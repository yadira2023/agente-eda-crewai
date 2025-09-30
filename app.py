import streamlit as st
import pandas as pd
import os
import re
import sys
from contextlib import contextmanager, redirect_stdout
from io import StringIO
from dotenv import load_dotenv

# Adiciona o diretório 'src' ao path para permitir importações
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from nfagent.agent_manager import run_agent_analysis

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# --- Configuração da Página do Streamlit e Funções Auxiliares ---

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

# --- Sidebar para Configurações ---

with st.sidebar:
    st.header("Configurações")
    
    openai_api_key_from_env = os.getenv("OPENAI_API_KEY")
    current_openai_api_key = st.text_input(
        "OpenAI API Key", 
        type="password", 
        value=openai_api_key_from_env
    )
    if current_openai_api_key:
        os.environ["OPENAI_API_KEY"] = current_openai_api_key
    else:
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]
            
    st.markdown("---")
    
    uploaded_file = st.file_uploader("Faça upload do seu CSV de fraudes", type="csv")
    
    st.markdown("---")
    st.info("O agente usará o arquivo de fraude de cartão de crédito padrão se nenhum arquivo for enviado.")

# --- Lógica Principal de Carregamento de Dados ---

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
    else:
        st.warning(f"Arquivo padrão não encontrado em: '{default_path}'. Faça o upload de um CSV para continuar.")

# --- Gerenciamento do Histórico do Chat ---

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # Se a mensagem do histórico tiver uma imagem, exibe-a
        if "image" in message and message["image"] is not None and os.path.exists(message["image"]):
            st.image(message["image"])

# --- Interface de Input do Chat ---
st.info(
    "**Sugestões de Perguntas:**\n"
    "- Descreva o dataset e mostre as 5 primeiras linhas.\n"
    "- Qual a correlação entre V1, V2 e Amount? Gere um heatmap.\n"
    "- Crie um histograma para a variável 'Amount'.\n"
    "- Quais são os valores mínimo e máximo da coluna 'Time'?"
)

# Mantenha o chat_input simples e direto
if prompt := st.chat_input("Faça sua pergunta sobre o CSV aqui...", key="chat_input_widget"):

  
    if not os.getenv("OPENAI_API_KEY"):
        st.info("Por favor, insira sua chave da API da OpenAI na barra lateral para continuar.")
        st.stop()
    
    if df is None:
        st.error("Não há dados para analisar. Faça o upload de um arquivo CSV ou verifique o arquivo padrão.")
        st.stop()

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
                crew_output = run_agent_analysis(prompt, df)
                final_report = crew_output.raw
            except Exception as e:
                st.error(f"Ocorreu um erro durante a execução do agente: {e}")
                st.session_state.messages.append({"role": "assistant", "content": f"Erro: {e}", "image": None})
                st.stop()
        
        # <<< A LÓGICA DE EXIBIÇÃO ESTÁ AQUI DENTRO DO IF PROMPT >>>
        
        image_path = None
        report_text_only = final_report

        # Tenta encontrar a sintaxe de imagem Markdown no relatório
        match = re.search(r"!\[.*\]\((output/[^\)]+)\)", final_report)
        
        if match:
            image_path = match.group(1) # Extrai o caminho do arquivo
            # Remove a linha completa da imagem do relatório para evitar o ícone quebrado
            report_text_only = re.sub(r"!\[.*\]\((output/[^\)]+)\)\n?", "", final_report).strip()

        # Exibe APENAS O TEXTO do relatório no chat
        st.markdown(report_text_only)
        
        # Se um caminho de imagem foi encontrado e o arquivo existe, exibe a imagem com st.image()
        if image_path and os.path.exists(image_path):
            st.image(image_path, caption="Gráfico gerado pelo agente")
        elif image_path:
            st.warning(f"O agente mencionou um gráfico em '{image_path}', mas o arquivo não foi encontrado.")

        # Adiciona a resposta completa (texto e caminho da imagem) ao histórico
        st.session_state.messages.append({
            "role": "assistant", 
            "content": report_text_only, # Salva apenas o texto no histórico
            "image": image_path # Salva o caminho da imagem para recarregar a página
        })
