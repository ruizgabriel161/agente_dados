import asyncio
import sys
from rich.prompt import Prompt
from rich import print
from rich.markdown import Markdown
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, BaseMessage
from langgraph.graph.state import RunnableConfig, CompiledStateGraph

from langgraph.checkpoint.base import BaseCheckpointSaver

from app.config.config_env import Settings
from app.graph.build.buider import BuiderGraph
from app.graph.context.context import Context
from app.graph.prompts.prompt import Supervisor

from app.graph.states.state import State
from app.graph.tools.sql_tool import SQLBot
from app.graph.utils.checkpointer import PsqlCheckPointer
from app.graph.utils.lifespan import async_lifespan


async def run_project(checkpointer:BaseCheckpointSaver) -> None:

    graph: CompiledStateGraph[State, Context, State, State] = BuiderGraph().build_graph(
        checkpointer=checkpointer
    )  # grafo

    BuiderGraph().graph_to_png(
        graph=graph,
        path=r"K:\Workspace\Python\agente_dados\architecture\graphs\grafo.png",
    )

    context: Context = Context(user_type="plus")
    config = RunnableConfig(configurable={"thread_id": 1})  # configuração de execução
    first_message: bool = True  # booleano de controle do laço
    prompt: str = Supervisor("default").defined_prompt()
    sqlbot: SQLBot = SQLBot()  # Objeto do SQLBot
    schema: str = sqlbot.ensure_table(
        name="GC_RPAO", path="data/raw/teste.xlsx"
    )  # Schema dos dados

    while True:
        user_input: str = Prompt.ask("[red]User: \n")  # Input do usuário
        human_message: HumanMessage = HumanMessage(user_input)  # Human Message

        if user_input in ["q", "quit", "exit", "bye"]:
            break

        if first_message:
            current_message: list = [
                SystemMessage(prompt),
                human_message,
            ]  # mensagem atual
            first_message = False

        current_message.append(human_message)

        result = await graph.ainvoke(
            {"messages": current_message, "sql_executed": False, "schema": schema},
            config=config,
            context=context,
        )

        response: BaseMessage = result["messages"][-1]

        model_name = ""
        if isinstance(response, AIMessage):
            model_name = response.response_metadata.get("model", "modelo desconhecido")

        print(f"[#FFD700]Klicinha ({model_name}): \n[/#FFD700]")

        print(Markdown(result["messages"][-1].text))
    # printa todo o historico do state quando encerrar o programa
    print(await graph.aget_state(config=config))

async def main() -> None:
    async with async_lifespan(), PsqlCheckPointer(Settings().DATA_DSN).create() as checkpointer:
        await run_project(checkpointer)


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(
            asyncio.WindowsSelectorEventLoopPolicy()
        )
    asyncio.run(main=main())
