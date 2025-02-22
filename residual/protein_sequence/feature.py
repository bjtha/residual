from collections import namedtuple
from dataclasses import dataclass, field
from itertools import zip_longest

GoTerm = namedtuple('goTerm', ['id', 'category', 'name'])

@dataclass
class Feature:
    service: str
    name: str
    locations: list[tuple[int, int]] | None = field(default_factory=list)
    go_terms: list = field(default_factory=list)

    def into_columns(self):
        columns = zip(*zip_longest([self.name],
                                  [f'{start}-{end}' for start, end in self.locations],
                                  [f'{id_} ({category}) {name}' for id_, category, name in self.go_terms],
                                  fillvalue=''))
        return list(columns)

    def into_rows(self):
        rows = zip_longest([self.name],
                           [f'{start}-{end}' for start, end in self.locations],
                           [f'{id_} ({category}) {name}' for id_, category, name in self.go_terms],
                           fillvalue='')
        return list(rows)
