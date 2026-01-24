
from dataclasses import dataclass
from typing import Literal

from app.model.schema_inspetor import SchemaInspetor
from app.model.sql_execute import SQLExecute


@dataclass(kw_only=True, frozen=True,repr=True,slots=True)
class Context:
    """Classe de contexto."""
    user_type: Literal['plus', 'enterprise'] = 'plus'
    schema_inspetor: SchemaInspetor
    sql_execute: SQLExecute