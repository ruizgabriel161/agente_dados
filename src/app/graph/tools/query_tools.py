from langchain_core.tools import tool
from app.graph.tools.sql_tool import SQLBot

sqlbot = SQLBot()

@tool
def query(query: str, table: str = "dados") -> str:
    '''
    query Tool para executar o sql criado pela LLM

    Args:
        query (str): query SQL
        table (str, optional): Tabela onde será executada a query. Defaults to "dados".

    Returns:
        str: resultado da query
    '''    
    if not sqlbot.table_exists(table):
        sqlbot.load_excel(
            name=table,
            path="data/raw/teste.xlsx"
        )

    return sqlbot.run(query)
