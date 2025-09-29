# Agente Autônomo para Análise Exploratória de Dados (EDA)

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35.0-red?logo=streamlit)](https://streamlit.io/)
[![CrewAI](https://img.shields.io/badge/CrewAI-0.30.11-orange)](https://www.crewai.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📖 Descrição

Este projeto implementa uma equipe de agentes autônomos construída com a framework **CrewAI** para realizar Análise Exploratória de Dados (EDA) em qualquer conjunto de dados CSV. A aplicação possui uma interface web interativa criada com **Streamlit**, permitindo que usuários façam perguntas em linguagem natural sobre seus dados e recebam respostas em formato de texto e visualizações gráficas.

O agente é capaz de:
-   Interpretar perguntas abertas sobre o dataset.
-   Gerar e executar código Python (usando Pandas, Matplotlib e Seaborn) dinamicamente.
-   Fornecer análises descritivas, estatísticas, contagens e correlações.
-   Criar e exibir gráficos como histogramas, gráficos de barras e heatmaps.
-   Apresentar os resultados em uma interface de chat amigável.

Por padrão, o projeto vem configurado para usar o dataset de [Detecção de Fraude de Cartão de Crédito do Kaggle](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud), mas permite o upload de qualquer outro arquivo CSV.

## 🚀 Funcionalidades

-   **Interface de Chat Interativa:** Converse com o agente de dados.
-   **Upload de CSV:** Analise seu próprio arquivo de dados.
-   **Visualização em Tempo Real:** Acompanhe o "processo de pensamento" do agente enquanto ele trabalha.
-   **Geração de Gráficos:** Obtenha visualizações dos seus dados salvas automaticamente na pasta `output/` e exibidas no chat.
-   **Configuração Segura:** Suas chaves de API são gerenciadas através de um arquivo `.env` e nunca são expostas.

## ⚙️ Pré-requisitos

Antes de começar, certifique-se de que você tem o seguinte instalado:
-   **Python 3.10 ou superior**.
-   **Git** (opcional, se for clonar de um repositório).
-   Um gerenciador de pacotes como `pip` (geralmente vem com o Python).

## 🛠️ Guia de Instalação e Execução no VS Code

Siga estes passos para configurar e executar o projeto em sua máquina local usando o Visual Studio Code.

### 1. Abrir o Projeto no VS Code

1.  Abra o VS Code.
2.  Vá em `File > Open Folder...` (ou `Arquivo > Abrir Pasta...`).
3.  Selecione a pasta raiz do projeto (`AGENTEI2A2/`).

### 2. Configurar o Ambiente Virtual e Instalar Dependências

1.  **Abra o Terminal Integrado:** Use o atalho `Ctrl + Shift + '` (ou vá em `View > Terminal`).
2.  **Crie o Ambiente Virtual:** Digite o seguinte comando no terminal:
    ```bash
    python -m venv .venv
    ```3.  **Ative o Ambiente Virtual:**
    *   **No Windows (PowerShell):**
        ```bash
        .\.venv\Scripts\activate
        ```
    *   **No macOS / Linux:**
        ```bash
        source ./.venv/bin/activate
        ```
    > Após a ativação, você verá `(.venv)` no início do seu prompt do terminal.
4.  **Instale as Bibliotecas Necessárias:** Com o ambiente ativado, instale todas as dependências a partir do arquivo `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```

### 3. Configurar a Chave da API da OpenAI

Este projeto utiliza um modelo de linguagem da OpenAI (como GPT-4o-mini) para alimentar os agentes. Você precisará de uma chave de API válida.

1.  **Crie um arquivo `.env`** na raiz do projeto (no mesmo nível do `app.py`).
2.  Adicione sua chave de API e o modelo desejado ao arquivo, no seguinte formato:

    ```env
    # AGENTEI2A2/.env
    OPENAI_API_KEY="sk-sua-chave-secreta-aqui"
    MODEL="gpt-4o-mini"
    ```
    > **Nota de Segurança:** O arquivo `.env` já está incluído no `.gitignore` para evitar que sua chave secreta seja acidentalmente enviada para um repositório.

### 4. Preparar o Dataset e a Pasta de Saída

1.  **Pasta de Saída:** Crie uma pasta chamada `output` na raiz do projeto. É aqui que os gráficos gerados pelo agente serão salvos.
2.  **(Opcional) Dataset Padrão:** Para usar a aplicação sem precisar fazer upload de um arquivo a cada vez:
    *   **Acesse a página do dataset no Kaggle:** [Credit Card Fraud Detection](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud).
    *   Baixe o arquivo `creditcardfraud.zip` e descompacte-o para obter `creditcard.csv`.
    *   Mova o arquivo `creditcard.csv` para a pasta `src/nfagent/dataset/`. Se essas pastas não existirem, crie-as.

### 5. Executar a Aplicação Streamlit

Com tudo configurado, inicie a aplicação com o seguinte comando no terminal do VS Code (com o ambiente virtual ainda ativado):
```bash
streamlit run app.py
```

Seu navegador padrão deve abrir automaticamente no endereço `http://localhost:8501`.

## 💬 Como Usar

1.  A aplicação será aberta no seu navegador.
2.  Sua **Chave da API da OpenAI** será carregada automaticamente a partir do arquivo `.env` e preenchida na barra lateral.
3.  **Escolha seu Dataset:**
    *   Para usar o dataset padrão (se você o configurou), não faça nada.
    *   Para analisar seu próprio arquivo, clique em "Browse files" na barra lateral e selecione o arquivo CSV.
4.  **Faça sua Pergunta:** Digite sua pergunta na caixa de chat na parte inferior da página e pressione Enter.

### Exemplos de Perguntas

-   `Sobre o que é o dataset? Mostre as primeiras 5 linhas.`
-   `Qual a correlação entre V1, V2 e Amount? Gere um heatmap.`
-   `Mostre a distribuição da variável 'Amount' com um histograma.`
-   `Com base nas análises, quais são as 3 principais conclusões que você pode tirar sobre este dataset?`

O agente irá processar sua solicitação, e você poderá acompanhar seu progresso na seção "Ver o processo de pensamento do agente". A resposta final, incluindo texto e gráficos, será exibida na janela de chat.

## 📄 Licença

Este projeto está sob a licença MIT.
