from abc import ABC, abstractmethod
from typing import Any
from langchain_core.tools import Tool

class BaseToolClass(ABC):
    name:str
    description: str
    
    @abstractmethod
    def run(self, **kwargs) -> Any: ...

    
    def _wrapper(self, *args, **kwargs) -> Any:
        try:
            return self.run(**kwargs)
        except Exception as e:
            raise ValueError(f'Erro na tool {e}')

    def to_langchain(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            func=self._wrapper
        )