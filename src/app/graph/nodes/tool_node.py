from app.graph.nodes.base_node import BaseNode
from typing import override
from app.graph.states.state import State
from langgraph.prebuilt import ToolNode
from langchain_core.runnables import Runnable
from app.graph.tools.query_tools import query


class ToolsNode(BaseNode):
    def __init__(self, llm=None):
        super().__init__(llm)
        self._tool_node: Runnable = ToolNode(tools=[query])

    @override
    def node_process(self, state: State) -> State:

        return self._tool_node.invoke(input=state)

    @override
    def name(self):
        return "tools"
