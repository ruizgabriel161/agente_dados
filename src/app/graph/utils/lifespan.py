from contextlib import asynccontextmanager
from typing import  AsyncGenerator


@asynccontextmanager
async def async_lifespan() -> AsyncGenerator[None]:
    print("async Abri")
    yield
    print("async fechei")
