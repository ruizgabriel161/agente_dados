from typing import Any, Sequence, Tuple
from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row
from psycopg.sql import Composed
from rich import print
from rich.markdown import Markdown


class SQLExecute:
    def __init__(self, pool: AsyncConnectionPool):
        self.pool = pool

    async def run(self, query: Tuple[Composed, list[Any]]) -> str:
        sql_query, params = query

        # print(f'{sql_query=}')
        # print(f'{params=}')
        # print(Markdown("---"))
        # print("executando query")
        # print(Markdown("---"))
        async with (
            self.pool.connection() as con,
            con.cursor(row_factory=dict_row) as cur,
        ):
            await cur.execute(query=sql_query, params=params)
            if cur.description is None:
                return "Query executada com sucesso"
            rows: list[dict[str, Any]] = await cur.fetchall()
        if not rows:
            return "Nenhum registro encontrado"
        return self._format_for_llm(rows=rows)
    
    @staticmethod
    def _format_for_llm(rows: Sequence[dict[str, Any]]) -> str:
        if not rows:
            return "Nenhum registro encontrado"

        headers = rows[0].keys()

        lines = [
            " | ".join(headers),
            " | ".join("---" for _ in headers),
        ]

        for row in rows:
            lines.append(" | ".join(map(str, row.values())))

        return "\n".join(lines)

