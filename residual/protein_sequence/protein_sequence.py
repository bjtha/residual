from itertools import chain
from collections.abc import Iterable, Sized

from residual.protein_sequence.feature import Feature

class ProteinSequence:

    """
    Holds the sequence and accumulated analysis data.
    """

    ALLOWED_SYMBOLS = set('ACDEFGHIKLMNPQRSTVWY')  # Valid amino acid symbols

    def __init__(self, name: str, sequence: str):
        self.name = name
        self.sequence = sequence
        self.features: list[Feature | None] = []

    def __len__(self):
        return len(self.sequence)

    def __repr__(self):
        seq_rep = self.sequence if len(self) <= 20 else self.sequence[:10] + '...' + self.sequence[-10:]
        return f'ProteinSequence(name={self.name}, sequence={seq_rep})'

    def __hash__(self):
        return hash(self.sequence)

    @property
    def sequence(self):
        return self._sequence

    @sequence.setter
    def sequence(self, value: str):
        if disallowed := (set(value) - self.ALLOWED_SYMBOLS):
            raise ValueError(f'Invalid sequence characters: {" ".join(str(i) for i in disallowed)}')
        self._sequence = value

    def features_as_lines(self) -> list[str]:

        empty = [('', '', '')]  # Insert an empty row between each feature.
        rows = list(chain(*(ft.into_rows() + empty for ft in self.features)))

        padding = 2
        widths = [self._get_max_length(col, minimum=25) + padding for col in zip(*rows)]
        row_layout = self._get_row_layout(*widths)

        lines = [row_layout.format('Name', 'Locations', 'GO Terms'), '-' * sum(widths)]  # Headers
        lines += [row_layout.format(*row) for row in rows]  # Data

        return lines

    @staticmethod
    def _get_max_length(items: Iterable[Sized], minimum: int):
        return max(max(map(len, items)), minimum)

    @staticmethod
    def _get_row_layout(*sizes: int):
        cells = ['{:<w}'.replace('w', str(size)) for size in sizes]
        return ''.join(cells)
