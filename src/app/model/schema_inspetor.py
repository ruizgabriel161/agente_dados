from typing import Any
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool


class SchemaInspetor:
    """Classe responsável por trabalhar com schema de dados dew consulta"""

    def __init__(self, pool: AsyncConnectionPool):
        self.pool: AsyncConnectionPool = pool

    async def get_schema(self, schema: str, table: str) -> str:
        sql = """
            SELECT
                column_name,
                data_type,
                is_nullable
            FROM information_schema.columns
            WHERE 
                table_schema = %s
                AND table_name = %s
            ORDER BY ordinal_position

            """
        async with (
            self.pool.connection() as con,
            con.cursor(row_factory=dict_row) as cur,
        ):
            await cur.execute(sql, (schema, table))
            rows: list[dict[str, Any]] = await cur.fetchall()
        return self._rows_to_markdown(rows=rows)
        
    def _rows_to_markdown(self, rows: list[dict[str, Any]], max_rows: int | None = None) -> str:
        if not rows:
            return "Nenhum registro retornado."

        if max_rows:
            rows = rows[:max_rows]

        headers = rows[0].keys()

        lines = []
        lines.append(" | ".join(headers))
        lines.append(" | ".join("---" for _ in headers))

        for row in rows:
            lines.append(" | ".join(str(row.get(h, "")) for h in headers))

        return "\n".join(lines)