from collections import namedtuple
from dataclasses import dataclass, field

@dataclass
class Feature:
    service: str
    name: str
    locations: list[tuple[int, int]] | None = field(default=None)
    go_terms: list = field(default_factory=list)

GoTerm = namedtuple('goTerm', ['id', 'category', 'name'])