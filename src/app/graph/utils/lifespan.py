from contextlib import asynccontextmanager
from typing import AsyncIterator
from psycopg_pool import AsyncConnectionPool
from psycopg.rows import TupleRow
from psycopg import AsyncConnection
from app.config.config_env import Settings
from rich import print
from rich.markdown import Markdown


@asynccontextmanager
async def async_lifespan() -> AsyncIterator[
    AsyncConnectionPool[AsyncConnection[TupleRow]]
]:
    pool = AsyncConnectionPool[AsyncConnection[TupleRow]](
        conninfo=Settings().DATA_DSN,
        min_size=2,
        max_size=10,
        timeout=10,
    )
    print('Abrindo conexão com banco de dados')
    print(Markdown('---'))
    async with pool:
        yield pool
