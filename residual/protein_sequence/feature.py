from collections import namedtuple
from dataclasses import dataclass, field

GoTerm = namedtuple('goTerm', ['id', 'category', 'name'])

@dataclass
class Feature:
    service: str
    name: str
    locations: list[tuple[int, int]] | None = field(default_factory=list)
    go_terms: list = field(default_factory=list)
