from typing import override
from app.graph.builder.base_builder import BaseBuider
from langgraph.graph.state import CompiledStateGraph
from langgraph.constants import END, START

from app.graph.context.context import Context
from app.graph.nodes.call_node import CallNode
from app.graph.nodes.gerar_sql_node import GerarSQLNode
from app.graph.nodes.router_node import RouterNode
from app.graph.nodes.tool_node import ToolsNode
from app.graph.states.state import State
from langgraph.checkpoint.base import BaseCheckpointSaver


class BuiderGraph(BaseBuider):
    """Classe responsável por buildar o grafo."""

    def __init__(self):
        super().__init__()

    @override
    def build_graph(
        self, checkpointer: BaseCheckpointSaver
    ) -> CompiledStateGraph[State, Context, State, State]:
        """
        Método para buildar o grafo

        Returns:
            CompiledStateGraph[State, Context, State, State]: Grafo compilado
        """

        call_node: CallNode = CallNode(llm=self.llm)
        router_node: RouterNode = RouterNode(llm=self.llm)
        tool_node: ToolsNode = ToolsNode()
        gerar_sql_node: GerarSQLNode = GerarSQLNode(llm=self.llm)

        # adiciona os nodes
        self.builder.add_node(router_node.name(), router_node.run)
        self.builder.add_node(tool_node.name(), tool_node.run)
        self.builder.add_node(call_node.name(), call_node.run)
        self.builder.add_node(gerar_sql_node.name(), gerar_sql_node.run)

        # adicionas as edges
        self.builder.add_conditional_edges(
            START, router_node.run, [gerar_sql_node.name(), call_node.name()]
        )
        self.builder.add_edge(gerar_sql_node.name(), tool_node.name())
        self.builder.add_edge(tool_node.name(), call_node.name())
        self.builder.add_edge(call_node.name(), END)

        graph: CompiledStateGraph[State, Context, State, State] = self.builder.compile(
            checkpointer=checkpointer
        )

        return graph
