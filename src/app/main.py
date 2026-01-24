import asyncio
import sys
from psycopg_pool import AsyncConnectionPool
from rich.prompt import Prompt
from rich import print
from rich.markdown import Markdown
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, BaseMessage
from langgraph.graph.state import RunnableConfig, CompiledStateGraph

from langgraph.checkpoint.base import BaseCheckpointSaver

from app.config.config_env import Settings
from app.graph.builder.builder import BuiderGraph
from app.graph.context.context import Context
from app.graph.prompts.prompt import Supervisor

from app.graph.states.state import State
from app.graph.utils.verify_system_message import VerifySystemMessage
from app.model.sql_execute import SQLExecute
from app.graph.utils.checkpointer import PsqlCheckPointer
from app.graph.utils.lifespan import async_lifespan

from app.model.schema_inspetor import SchemaInspetor


async def run_project(
    checkpointer: BaseCheckpointSaver, pool: AsyncConnectionPool, thred_id: str
) -> None:
    graph: CompiledStateGraph[State, Context, State, State] = BuiderGraph().build_graph(
        checkpointer=checkpointer
    )  # grafo

    # BuiderGraph().graph_to_png(
    # graph=graph,
    # path=r"K:\Workspace\Python\agente_dados\architecture\graphs\grafo.png",
    # )
    schema_inspetor = SchemaInspetor(
        pool=pool
    )  # objeto da classe para carregar o schema

    sql_execute = SQLExecute(pool=pool)
    context: Context = Context(
        user_type="plus", schema_inspetor=schema_inspetor, sql_execute=sql_execute
    )  # envia o objeto para o contexto

    config = RunnableConfig(
        configurable={"thread_id": thred_id}
    )  # configuração de execução


    prompt: str = await Supervisor("default").defined_prompt()

    verify_system_message = await VerifySystemMessage().check_system_message(
            dsn=Settings().DATA_DSN, thread_id=thred_id
    )
    while True:
        user_input: str = Prompt.ask("[red]User: \n")  # Input do usuário
        human_message: HumanMessage = HumanMessage(user_input)  # Human Message

        if user_input.lower() in ["q", "quit", "exit", "bye"]:
            break
        
        if verify_system_message is False:
            current_message: list = [
                SystemMessage(prompt),
                human_message,
            ]  # mensagem atual
        else:
            current_message = []

        current_message.append(human_message)

        result = await graph.ainvoke(
            {"messages": current_message},
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
    async with (
        async_lifespan() as pool,
        PsqlCheckPointer(Settings().DATA_DSN).create() as checkpointer,
    ):
        await run_project(checkpointer, pool, thred_id='2')


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main=main())
