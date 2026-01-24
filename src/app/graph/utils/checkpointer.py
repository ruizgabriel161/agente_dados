from contextlib import asynccontextmanager
from typing import AsyncGenerator, Protocol, TypeVar
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver


T_co = TypeVar("T_co", covariant=True)


class AsyncCheckPointer(Protocol[T_co]):
    def create(self) -> AsyncGenerator[T_co]: ...


class InMemoryCheckPointer:
    @asynccontextmanager
    async def create(self):
        yield InMemorySaver()


class PsqlCheckPointer:
    def __init__(self, dsn: str):
        self.dsn: str = dsn
        pass

    @asynccontextmanager
    async def create(self) -> AsyncGenerator[AsyncPostgresSaver, None]:
        async with AsyncPostgresSaver.from_conn_string(
            self.dsn
        ) as checkpointer:
            await checkpointer.setup()
            yield checkpointer
