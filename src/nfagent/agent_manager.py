import pandas as pd
from .crew import EdaCrew
#from .tools.data_manager import data_manager

def run_agent_analysis(question: str, dataframe: pd.DataFrame) -> str:
    """
    Carrega um DataFrame no gerenciador de dados e executa a crew de análise
    para uma única pergunta.

    Args:
        question (str): A pergunta do usuário.
        dataframe (pd.DataFrame): O DataFrame carregado para análise.

    Returns:
        str: O resultado final (relatório em Markdown) da crew.
    """
    # Define o DataFrame no gerenciador de dados global
    # para que as ferramentas do agente possam acessá-lo.
    inputs = {'question': question}
    
    print(f"\n[Agent Manager] Iniciando a crew com a pergunta: '{question}'")
    
    # CORREÇÃO: Passa o DataFrame diretamente para o construtor da EdaCrew
    crew_instance = EdaCrew(dataframe=dataframe).crew()
    crew_result = crew_instance.kickoff(inputs=inputs)
    
    return crew_result