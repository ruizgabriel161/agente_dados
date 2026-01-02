
from dataclasses import dataclass
from typing import Literal


@dataclass(kw_only=True, frozen=True,repr=True,slots=True)
class Context:
    """Classe de contexto."""
    user_type: Literal['plus', 'enterprise'] = 'plus'
    