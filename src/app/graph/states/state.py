from typing import Annotated, Sequence, TypedDict
from langgraph.graph.message import BaseMessage, add_messages



class State(TypedDict):
    """
    Classe responsável por definir o State do grafo

    Attributes:
    messages:

    Args:
        messages (Annotated[Sequence[BaseMessage], add_messages]): Sequência de mensagens do tipo BaseMessage

    """

    messages: Annotated[Sequence[BaseMessage], add_messages]
