import sys
import asyncio

from langchain_core.messages import SystemMessage
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph.state import RunnableConfig

from app.config.config_env import Settings

from rich import print


class VerifySystemMessage:
    """
    Classe Responsável por verificar se há SystemMessage no checkpoint
    """

    def __init__(self): ...

    async def check_system_message(self, dsn: str, thread_id: str) -> bool:
        async with AsyncPostgresSaver.from_conn_string(dsn) as saver:
            config = RunnableConfig(configurable={"thread_id": thread_id})
            checkpoint = await saver.aget(config=config)
        if not checkpoint:
            return False
        messages = checkpoint.get("channel_values", {}).get("messages", [])


        return any(isinstance(msg,SystemMessage) for msg in messages)
