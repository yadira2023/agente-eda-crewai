import os
import sys
from crew import EdaCrew
from tools.data_manager import data_manager

def run():
    """
    Função principal que carrega os dados e executa a crew com interação do usuário.
    """
    os.makedirs("output", exist_ok=True)

    # CORREÇÃO: Define o caminho para o arquivo CSV local
    # O caminho é relativo à raiz do projeto, de onde o script é executado.
    local_csv_path = "dataset/creditcard.csv"
    
    # Carrega os dados a partir do arquivo local
    print("Iniciando o carregamento do DataFrame local...")
    load_status = data_manager.load_dataframe_from_local_csv(filepath=local_csv_path)
    
    if "Erro" in load_status:
        print("Falha ao carregar o DataFrame. Verifique o caminho do arquivo e encerre a execução.", file=sys.stderr)
        sys.exit(1)

    # Interação com o usuário
    while True:
        question = input("\nDigite sua pergunta sobre os dados (ou 'sair' para terminar): ")
        if question.lower() in ['sair', 'exit', 'quit']:
            break

        inputs = {'question': question}
        
        print(f"\nIniciando a crew com a pergunta: '{question}'")
        crew_result = EdaCrew().crew().kickoff(inputs=inputs)
        
        print("\n\n########################")
        print("## Relatório Final")
        print("########################\n")
        print(crew_result)

# Funções placeholder para corresponder ao pyproject.toml
def train():
    print("Funcionalidade 'train' não implementada.")

def replay():
    print("Funcionalidade 'replay' não implementada.")

def test():
    print("Funcionalidade 'test' não implementada.")

if __name__ == "__main__":
    run()