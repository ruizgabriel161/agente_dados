from app.graph.context.context import Context
from app.graph.nodes.base_node import BaseNode
from typing import override
from app.graph.states.state import State
from langgraph.prebuilt import ToolNode
from langchain_core.runnables import Runnable
from app.graph.tools.query_tools import query
from rich import print
from rich.markdown import Markdown

class ToolsNode(BaseNode):
    def __init__(self, llm=None):
        super().__init__(llm)
        self._tool_node: Runnable = ToolNode(tools=[query])

    @override
    async def node_process(self, state: State, *,context:Context | None) -> State:

        # print('>tool_node')
        # print(Markdown('---'))
        result = await self._tool_node.ainvoke(state)

        # print(f'{result["messages"][0].content}')
        # print(Markdown('---'))

        messages = result.get('messages', [])

        if not messages:
            return state

        tool_message = result["messages"][0]

        new_messages = list(state['messages'])
        new_messages.append(tool_message)

        # print(new_messages)
        # merge explícito para agradar o Pyright
        return State(
            messages=new_messages
        )

    @override
    def name(self):
        return "tools"
