from typing import Any, override, Literal
from app.graph.context.context import Context
from app.graph.nodes.base_node import BaseNode
from app.graph.prompts.prompt import Supervisor
from app.graph.states.state import State
from rich import print
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import Runnable

import re
import unicodedata


class RouterNode(BaseNode):
    """
    Classe Router para ser uma conditional edge
    """

    def __init__(self, llm: Runnable):
        super().__init__(llm)
        self.llm: Runnable = llm

    async def router(self, state: State, context: Context) -> Literal["gerar_sql_node", "call_node"]:
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

        schema = await context.schema_inspetor.get_schema(
            schema="dados", table="tb_colaboradores"
        )

        teste = self.extract_columns(schema=schema)

        print(teste)


        if schema:
            if any(col for col in self.extract_columns(schema=schema)):
                print('>teste')
                return "gerar_sql_node"
            
        word_list_chat = [
            "explique",
            "o que é",
            "como funciona",
            "conceito",
            "meu nome é",
        ]

        if any(c in human_message for c in word_list_chat):
            print('entrou no call_node')
            return "call_node"

        word_list_sql = [
            "listar",
            "traga",
            "mostre",
            "consulta",
            "tabela",
            "diga",
            "fale",
        ]

        if any(w in human_message for w in word_list_sql):
            return "gerar_sql_node"


        prompt: str = await Supervisor("decisao").defined_prompt(question=str(human_message))
        decision: AIMessage = self.llm.invoke(
            [SystemMessage(prompt), HumanMessage(human_message)]
        )
        content: str = str(decision.content)
        content = content.strip().upper()

        print(f"Decisão = {content}")

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
            line.split("|")[0].strip().lower()
            for line in schema.splitlines()
            if line.strip()  # ignora linhas vazias
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
    async def node_process(self, state: State, context: Context) -> State | str:
        decision = await self.router(state, context=context)
        return decision 

    @override
    def name(
        self,
    ):
        return "router"
