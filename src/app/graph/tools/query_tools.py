from typing import Any, Dict
from langchain_core.tools import tool

from app.graph.context.context import Context
from langchain.tools import ToolRuntime

from rich import print
from rich.markdown import Markdown

from app.model.json_to_sql import JsonToSQL


@tool()
async def query(payload: Dict[str, Any], runtime: ToolRuntime[Context]) -> list[str] | str:
    """
    query Tool para executar o sql criado pela LLM

    Args:
        payload (Dict[str, Any]): payload json 
        table (Context): Context da aplicação.

    Raises:args
        ValueError: _description_

    Returns:
        list[str] | str: resultado da query.
    """

    context: Context = runtime.context

    json_to_sql = JsonToSQL(payload=payload)
    sql_query = json_to_sql.build_select()

    # print(">query_tool")
    # print(Markdown("---"))
    return await context.sql_execute.run(query=sql_query)
