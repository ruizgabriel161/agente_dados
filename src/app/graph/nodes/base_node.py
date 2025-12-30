from abc import ABC, abstractmethod
from app.graph.states.state import State
from langchain_core.runnables import Runnable


class BaseNode(ABC):
    """
    Classe responsável por abstrair os nodes
    """

    def __init__(self, llm: Runnable | None = None):
        self.llm = llm
        

    def run(self, state: State) -> State | str:
        """
        Método responsável por executar o node e garantir que ele esteja funcionando

        Args:
            state (State): State grafo

        Raises:
            e: Possiveis erros

        Returns:
            State: Retorna um novo State
        """
        self.__validade_state(state=state)

        try:
            output = self.node_process(state)
        except Exception as e:
            raise e

        return output

    @abstractmethod
    def node_process(self, state: State) -> State: ...

    @abstractmethod
    def name(self) -> str: ...

    def __validade_state(self, state: State) -> None:
        """
        Método privado para verificar se o State passado no argumento contem as condições validas

        Args:
            state (State): Stado do grafo

        Raises:
            ValueError: Erro de tipagem do State
            ValueError: erro nas chaves do grafo
        """
        if not isinstance(state, dict):
            raise ValueError("State invalido, não é um typedict")
        if "messages" not in state:
            raise ValueError("Não há um chave messages no state")
