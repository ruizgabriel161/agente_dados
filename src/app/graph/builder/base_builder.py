from abc import ABC, abstractmethod
from langgraph.graph.state import CompiledStateGraph, StateGraph
from app.graph.context.context import Context
from app.graph.states.state import State
from app.graph.utils.load_llm import LoadLLM

from rich import print
from rich.markdown import Markdown

class BaseBuider(ABC):
    """Classe responsável por abstrair o buider"""

    def __init__(self):
        """
        Inicializa a classe e defini o buider e tipa o graph
        """
        self.builder: StateGraph[State, Context, State, State] = StateGraph(
            state_schema=State,
            context_schema=Context,
            input_schema=State,
            output_schema=State,
        )
        print('[green]Carregando LLM')
        self.llm = LoadLLM().init_llm()
        print('[green]LLM Carregada')
        print(Markdown('---'))

    @abstractmethod
    def build_graph() -> CompiledStateGraph[State, Context, State, State]: ...

    def graph_to_png(
        self, graph: CompiledStateGraph[State, Context, State, State], path: str
    ) -> None:
        """
        Método responsável por salvar o grafico em png

        Args:
            path (str): Caminho do arquivo a ser salvo

        Raises:
            ValueError: Erro caso a variavel não tenha sido definida
        """

        graph.get_graph().draw_mermaid_png(output_file_path=path)
