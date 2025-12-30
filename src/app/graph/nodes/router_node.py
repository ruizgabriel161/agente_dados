from typing import Any, override, Literal
from app.graph.nodes.base_node import BaseNode
from app.graph.prompts.prompt import Supervisor
from app.graph.states.state import State
from rich import print
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

import re
import unicodedata


class RouterNode(BaseNode):
    """
    Classe Router para ser uma conditional edge
    """

    def __init__(self, llm=None):
        super().__init__(llm)

    def router(self, state: State) -> Literal["gerar_sql_node", "call_node"]:
        """
        router Método para decidir qual caminho a LLM percorrerá. Condicional edge

        Args:
        state (State): Estado do Grafo

        Returns:
            Literal["gerar_sql_node", "call_node"] - caminho escolhido
        """
        human_message: str | Any = next(
            m.content
            for m in reversed(state["messages"])
            if isinstance(m, HumanMessage)
        )  # busca a ultima human_message

        # padroniza o human_message
        human_message = self.normalize_input(human_message)

        schema = state.get("schema")

        if schema:
            if any(col for col in self.extract_columns(schema=schema)):
                return "gerar_sql_node"

        word_list_sql = [
            "listar",
            "traga",
            "mostre",
            "consulta",
            "tabela",
            "diga",
            "fale",
        ]

        if any(w for w in word_list_sql):
            return "gerar_sql_node"

        word_list_chat = ["explique", "o que é", "como funciona", "conceito"]

        if any(c for c in word_list_chat):
            return "call_node"

        prompt: str = Supervisor("decisao").defined_prompt(question=str(human_message))
        decision: AIMessage = self.llm.invoke(
            [SystemMessage(prompt), HumanMessage(human_message)]
        )
        content: str = str(decision.content)
        content = content.strip().upper()

        if state.get("sql_executed") or "CHAT" in content:
            print("call_node")
        elif "SQL" in content:
            print("gerar_sql_node")
        else:
            print("call_node")

        if state.get("sql_executed") or "CHAT" in content:
            return "call_node"
        elif "SQL" in content:
            return "gerar_sql_node"
        else:
            return "call_node"

    def extract_columns(self, schema: str) -> set[str]:
        """
        extract_columns Metodo responsável por extrair as colunas so schema

        Args:
            schema (str): schema da tabela

        Returns:
            set[str]: colunas retornadas
        """
        return {
            match.group(1).lower()
            for match in re.finditer(r"-\s*([A-Za-z0-9_%]+)\s*\(", schema)
        }

    def normalize_input(self, input: str) -> str:
        """
        normalize_input Padronizar palavra removendo os acentos e colocando em minusculo

        Args:
            input (str): texto para ser normalizado

        Returns:
            str: retorna o texto tratado
        """
        input = input.lower()
        input = unicodedata.normalize("NFKD", input)
        return "".join(c for c in input if not unicodedata.combining(c))

    @override
    def node_process(self, state: State) -> State:
        return state

    @override
    def name(
        self,
    ):
        return "router"
