import os
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import pandas as pd

# Carrega variáveis de ambiente do .env na raiz do projeto
load_dotenv()

from .tools.python_executor_tool import PythonExecutorTool

# Constrói o caminho para o diretório de configuração de forma robusta
# Isso garante que ele funcione independentemente de onde o script é chamado
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config')

@CrewBase
class EdaCrew:
    """EdaCrew crew"""
    # CORREÇÃO: Caminhos para os arquivos YAML agora são absolutos
    agents_config = os.path.join(CONFIG_PATH, 'agents.yaml')
    tasks_config = os.path.join(CONFIG_PATH, 'tasks.yaml')
    
    def __init__(self, dataframe: pd.DataFrame):
        self.dataframe = dataframe
        self.llm = ChatOpenAI(model_name=os.getenv("MODEL", "gpt-4o-mini"), temperature=0.2)

    @agent
    def data_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['data_analyst'],
            # CORREÇÃO: A ferramenta é instanciada aqui com o DataFrame
            tools=[PythonExecutorTool(df=self.dataframe)],
            llm=self.llm,
            verbose=True
        )

    @agent
    def report_synthesizer(self) -> Agent:
        return Agent(
            config=self.agents_config['report_synthesizer'],
            llm=self.llm,
            verbose=True
        )

    @task
    def analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['analysis_task'],
            agent=self.data_analyst(),
        )

    @task
    def reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_task'],
            agent=self.report_synthesizer(),
            context=[self.analysis_task()]
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )