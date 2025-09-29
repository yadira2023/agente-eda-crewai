import io
import sys
import os
from typing import Type, Any
import pandas as pd
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# O data_manager não é mais necessário para passar o DataFrame para esta ferramenta
# from .data_manager import data_manager

class PythonCodeExecutorInput(BaseModel):
    code: str = Field(..., description="O código Python a ser executado para analisar o DataFrame 'df'.")

class PythonExecutorTool(BaseTool):
    name: str = "Python Code Executor"
    description: str = (
        "Executa código Python para análise de dados em um DataFrame do pandas chamado 'df'. "
        "Use esta ferramenta para realizar qualquer cálculo, análise ou visualização de dados. "
        "O código deve usar a variável 'df' que já está carregada. "
        "Para gráficos, salve-os em um arquivo DENTRO DO DIRETÓRIO 'output/' (ex: 'plt.savefig(\"output/plot.png\")') "
        "e retorne o caminho do arquivo. O output de 'print()' será capturado e retornado."
    )
    args_schema: Type[BaseModel] = PythonCodeExecutorInput
    # CORREÇÃO: Adiciona um campo para armazenar o DataFrame
    df: pd.DataFrame = Field(None, exclude=True)

    def _run(self, code: str) -> str:
        if self.df is None:
            return "Erro Crítico: O DataFrame não foi fornecido para a ferramenta de execução."

        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()
        
        local_namespace = {
            'df': self.df, 'pd': pd, 'np': np, 'plt': plt, 'sns': sns,
            'stats': stats, 'KMeans': KMeans, 'StandardScaler': StandardScaler
        }
        
        output_log = ""
        try:
            plt.close('all')
            exec(code, {}, local_namespace)
            # A única coisa que a ferramenta faz é capturar o que foi impresso.
            output_log = captured_output.getvalue()
        except Exception as e:
            output_log = f"Erro ao executar o código: {e}"
        finally:
            sys.stdout = old_stdout
        
        return output_log if output_log else "Código executado sem output de texto."