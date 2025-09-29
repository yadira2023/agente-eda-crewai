import pandas as pd
import os

class DataFrameManager:
    _instance = None
    df = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataFrameManager, cls).__new__(cls)
            cls.df = None
        return cls._instance

    def load_dataframe_from_local_csv(self, filepath: str):
        """
        Carrega um DataFrame a partir de um caminho de arquivo CSV local.
        """
        if self.df is not None and not isinstance(self.df, str):
            return "DataFrame já está carregado."
        
        try:
            print(f"Carregando CSV local de: {filepath}")
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"O arquivo não foi encontrado no caminho especificado: {filepath}")
            
            self.df = pd.read_csv(filepath)
            info = f"Dataset carregado com sucesso. Shape: {self.df.shape}"
            print(info)
            return info
        except Exception as e:
            self.df = "Erro"
            error_msg = f"Erro ao carregar o CSV local: {e}"
            print(error_msg, flush=True)
            return error_msg

    def get_df(self):
        return self.df

data_manager = DataFrameManager()