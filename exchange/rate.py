from dataclasses import dataclass
import functools

@dataclass(frozen=True)
class ExchangeRate:
    origin: str
    target: str
    rate: float

