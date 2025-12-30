from app.graph.tools.base_tools import BaseToolClass
from pandas import read_excel, DataFrame
from duckdb import DuckDBPyConnection, connect


class SQLBot(BaseToolClass):
    name: str = "query"
    description: str = "executar a query do duckdb"
    _con: DuckDBPyConnection | None = None

    def __init__(self):
        if SQLBot._con is None:
            SQLBot._con = connect(database=":memory:")
        self.con = SQLBot._con

    def table_exists(self, name: str) -> bool:
        query = """
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name  = ?
            """
        result = self.con.execute(query, [name]).fetchone()
        return result is not None and result[0] > 0

    def get_schema(self, table_name: str) -> str:
        query = """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = ?
        ORDER BY ordinal_position
        """
        rows = self.con.execute(query, [table_name]).fetchall()

        return "\n".join(f"- {col} ({dtype})" for col, dtype in rows)

    def run(self, query: str) -> str:

        try:
            return self.con.execute(query=query).df().to_string()
        except Exception as e:
            return f'Não foi possível executar a query: {query}\n Erro: {e}'
        

    def load_excel(self, name: str, path: str) -> DuckDBPyConnection:
        df = read_excel(path)
        return self.con.register(name, df)

    def ensure_table(self, name: str, path: str) -> str:
        if not self.table_exists(name):
            self.load_excel(name=name, path=path)
        return self.get_schema(name)
