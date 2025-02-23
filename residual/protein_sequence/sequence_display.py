from itertools import chain, zip_longest, batched
from typing import Iterable, Sized

from residual.protein_sequence import ProteinSequence, Feature, GoTerm

class SequenceDisplay:

    def __init__(self, __seq: ProteinSequence, /):
        self.seq = __seq

    def feature_into_rows(self, ft: Feature):
        columns = []
        for prop, value in vars(ft).items():  # For each property in the feature...
            if parser := getattr(self, f'_parse_{prop}', None):  # ...get the respective parser, if defined
                columns.append(parser(value))
        rows = zip_longest(*columns, fillvalue='')  # Rearrange columns into rows with blank cells.
        return list(rows)

    @staticmethod
    def _parse_service(service: str):
        return [service]

    @staticmethod
    def _parse_name(name: str):
        return [name]

    @staticmethod
    def _parse_locations(locations: list[tuple[int]]):
        return [f'{start}-{end}' for start, end in locations]

    @staticmethod
    def _parse_go_terms(go_terms: GoTerm):
        return [f'{id_} ({category}) {name}' for id_, category, name in go_terms]

    @staticmethod
    def _get_max_length(items: Iterable[Sized], minimum: int):
        return max(max(map(len, items)), minimum)

    @staticmethod
    def _get_row_layout(sizes: Iterable[int]):
        cells = ['{:<w}'.replace('w', str(size)) for size in sizes]
        return ''.join(cells)

    def tabulate_features(self, features: Iterable[Feature]) -> list[str]:

        features = sorted(features, key=lambda f: f.locations[0][0] if f.locations else 0)

        # Sample features to determine headers and columns before tabulating.
        first_feature = features[0]
        first_row = self.feature_into_rows(first_feature)[0]
        empty = [['' for _ in first_row]]

        # Get the features as rows, adding an empty row after each for readability.
        rows = list(chain(*(self.feature_into_rows(ft) + empty for ft in features)))

        # Make a template row layout, with column widths to accommodate the longest cells.
        padding = 2
        widths = [self._get_max_length(col, minimum=15) + padding for col in zip(*rows)]
        row_layout = self._get_row_layout(widths)

        headers = [row_layout.format(*[prop.capitalize() for prop in vars(first_feature)])]
        divider = ['-' * sum(widths)]
        data = [row_layout.format(*row) for row in rows]
        return headers + divider + data

    def __str__(self):
        seq_lines: list[str] = [''.join(batch) for batch in batched(self.seq.sequence, 80)]
        feature_lines: list[str] = self.tabulate_features(self.seq.features) if self.seq.features else []
        return f">{self.seq.name}\n{'\n'.join(seq_lines)}\n\n{'\n'.join(feature_lines)}"

    def __call__(self):
        return str(self)