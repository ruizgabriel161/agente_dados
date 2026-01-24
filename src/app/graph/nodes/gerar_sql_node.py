import json
from typing import override
from app.config.config_env import Settings
from app.graph.context.context import Context
from app.graph.nodes.base_node import BaseNode
from langchain.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable


from app.graph.prompts.prompt import Supervisor
from app.graph.states.state import State

from rich import print
from rich.markdown import Markdown

from time import perf_counter


class GerarSQLNode(BaseNode):
    """
    Classe responsável por gerar o sql
    """

    def __init__(self, llm: Runnable):
        super().__init__(llm)
        self.llm: Runnable = llm

    @override
    async def node_process(self, state: State, *, context: Context) -> State:
        # ultima Humam message
        human_message: str = str(
            [m.content for m in state["messages"] if isinstance(m, HumanMessage)][-1]
        )

        schema = await context.schema_inspetor.get_schema(
            schema="dados", table="tb_colaboradores"
        )

        prompt: str = await Supervisor(agent="sql").defined_prompt(
            question=human_message, schema=schema
        )

        llm = self.llm.with_config(
            config={"configurable": {"temperature": 0, "model": Settings().MODEL}}
        )

        # print(Markdown("---"))
        # print("gerando query sql")
        # print(Markdown("---"))


        start = perf_counter()
        llm_response: BaseMessage = await llm.ainvoke(
            [SystemMessage(prompt), HumanMessage(human_message)]
        )

        elapsed = perf_counter() - start

        print(f'⏱️ Tempo de resposta da LLM: {elapsed:.3f}s')
        print(Markdown('---'))
        
        raw = llm_response.content

        if isinstance(raw, str):
            payload = json.loads(raw)
        elif isinstance(raw, list):
            payload = raw[0]
        elif isinstance(raw, dict):
            payload = raw
        else:
            raise TypeError(f"Formato inesperado do LLM: {type(raw)}")

        # print(type(payload), payload)
        # print(Markdown("---"))
        tool_message = AIMessage(
            content="",
            tool_calls=[{"id": "sql-1", "name": "query", "args": {"payload": payload}}],
        )

        return {"messages": list(state["messages"]) + [tool_message]}

    @override
    def name(self) -> str:
        return "gerar_sql_node"
