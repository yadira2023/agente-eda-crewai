import streamlit as st
import pandas as pd
import os
import re
import sys
from contextlib import contextmanager, redirect_stdout
from io import StringIO
from dotenv import load_dotenv

# Adiciona o diretório 'src' ao path para permitir importações no ambiente de deploy
# MANTENHA ESTA LINHA POR ENQUANTO, CASO HAJA PROBLEMAS COM A IMPORTAÇÃO DE 'src'
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src'))) 

from src.nfagent.agent_manager import run_agent_analysis

# Carrega as variáveis de ambiente (mantido para o modelo MODEL, mas não para a chave)
load_dotenv()

# --- Configuração da Página e Funções Auxiliares (SEM ALTERAÇÕES) ---

st.set_page_config(page_title="Agente de Análise de Dados", layout="wide")
st.title("🤖 Agente de Análise de Dados")
st.caption("Faça perguntas sobre seu arquivo CSV e obtenha análises, gráficos e conclusões.")

# Classe para capturar o log verbose do CrewAI em tempo real
class StreamlitLogStream(StringIO):
    def __init__(self, container):
        super().__init__()
        self.container = container
        self.buffer = ""

    def write(self, s):
        self.buffer += s
        clean_buffer = re.sub(r'\x1b\[[0-9;]*[mK]', '', self.buffer)
        self.container.markdown(f"```log\n{clean_buffer}\n```")

    def flush(self):
        pass

@contextmanager
def st_capture_stdout(container):
    """Context manager para capturar stdout e exibir em um container Streamlit."""
    log_stream = StreamlitLogStream(container)
    old_stdout = sys.stdout
    sys.stdout = log_stream
    try:
        yield
    finally:
        sys.stdout = old_stdout

# Função para carregar CSV, com cache para performance
@st.cache_data
def load_csv(uploaded_file):
    if uploaded_file is not None:
        try:
            return pd.read_csv(uploaded_file)
        except Exception as e:
            st.error(f"Erro ao carregar o arquivo: {e}. Verifique o formato ou encoding.")
            return None
    return None

# --- Sidebar para Configurações (ALTERADO PARA CHAVE DO USUÁRIO + BOTÃO) ---

with st.sidebar:
    st.header("Configuração")
    
    # Input da chave da API da OpenAI - NÃO É PRÉ-PREENCHIDA
    openai_api_key_input = st.text_input(
        "Insira sua Chave da API OpenAI", 
        type="password", 
        key="api_key_input_sidebar"
    )
    st.markdown("---")
    
    # Upload de arquivo CSV
    st.subheader("Escolha um arquivo CSV")
    uploaded_file = st.file_uploader("Drag and drop file here", type="csv")
    
    st.markdown("---")
    
    # O Botão que inicia a configuração e habilita o agente
    start_button = st.button("Iniciar Agente", key="start_agent_button") 
    
    # Nota sobre o dataset padrão (opcional)
    st.caption("O agente usará o arquivo padrão se nenhum upload for feito.")

# --- Gerenciamento de Estado do Agente ---

# Inicializa o estado do agente (se a chave e os dados foram validados)
if "agent_initialized" not in st.session_state:
    st.session_state.agent_initialized = False

# Lógica para carregar o DataFrame (fora do botão, pois o Streamlit precisa do DF em cada rerun)
df = None
if uploaded_file is not None:
    df = load_csv(uploaded_file)
else:
    default_path = "src/nfagent/dataset/creditcard.csv"
    if os.path.exists(default_path):
        try:
            df = pd.read_csv(default_path)
        except Exception as e:
            st.error(f"Erro ao carregar o arquivo padrão em '{default_path}': {e}.")
            df = None
    # NOTA: Não mostramos a mensagem de Warning se o arquivo padrão não existir, pois 
    # o st.info abaixo já fará a mesma coisa.

# --- Lógica de Validação e Início do Agente ---

if start_button:
    if not openai_api_key_input:
        st.error("ERRO DE CONFIGURAÇÃO: Por favor, insira sua chave da API da OpenAI.")
        st.session_state.agent_initialized = False
    elif df is None:
        st.error("ERRO DE CONFIGURAÇÃO: Não há dados para analisar. Por favor, carregue um arquivo CSV.")
        st.session_state.agent_initialized = False
    else:
        # Tudo OK! Configura a variável de ambiente com a chave do usuário
        os.environ["OPENAI_API_KEY"] = openai_api_key_input
        st.session_state.agent_initialized = True
        st.success("Agente configurado e dados carregados! Você pode começar a perguntar abaixo.")
        # Opcional: Redireciona o foco para o corpo principal para o usuário não ficar confuso
        st.balloons()


# --- Exibição do Status e Chat ---

if not st.session_state.agent_initialized:
    # Mostra mensagem de status na área principal
    st.info("Aguardando configuração. Insira a chave da API, carregue seu CSV e clique em 'Iniciar Agente'.")
    st.stop()


# --- Gerenciamento do Histórico do Chat ---

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "image" in message and message["image"] is not None and os.path.exists(message["image"]):
            st.image(message["image"])

# --- Interface de Input do Chat (Habilitada Apenas Se Inicializado) ---

if prompt := st.chat_input("Ex: 'Descreva os dados' ou 'Gere um gráfico de barras'", key="chat_input_widget"):
    
    # NOTA: Não precisamos mais do os.getenv() ou st.stop() aqui, pois o botão de início
    # já garantiu que a chave está em os.environ e que o DF não é None.
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        st.info("Analisando os dados... O processo pode levar alguns instantes.")
        
        thinking_container = st.expander("Ver o processo de pensamento do agente")
        log_container = thinking_container.empty()

        final_report = None
        with st_capture_stdout(log_container):
            try:
                # O CrewAI agora usará a chave definida em os.environ pelo botão 'Iniciar Agente'
                crew_output = run_agent_analysis(prompt, df)
                final_report = crew_output.raw
            except Exception as e:
                st.error(f"Ocorreu um erro durante a execução do agente: {e}")
                st.session_state.messages.append({"role": "assistant", "content": f"Erro: {e}", "image": None})
                st.stop()
        
        image_path = None
        report_text_only = final_report

        # Tenta encontrar a sintaxe de imagem Markdown no relatório
        match = re.search(r"!\[.*\]\((output/[^\)]+)\)", final_report)
        
        if match:
            image_path = match.group(1)
            report_text_only = re.sub(r"!\[.*\]\((output/[^\)]+)\)\n?", "", final_report).strip()

        st.markdown(report_text_only)
        
        if image_path and os.path.exists(image_path):
            st.image(image_path, caption="Gráfico gerado pelo agente")
        elif image_path:
            st.warning(f"O agente mencionou um gráfico em '{image_path}', mas o arquivo não foi encontrado.")

        st.session_state.messages.append({
            "role": "assistant", 
            "content": report_text_only,
            "image": image_path
        })
