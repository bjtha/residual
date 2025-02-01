from dataclasses import dataclass, field

from residual.protein_sequence.descriptors import AminoAcidSequence


class ProteinSequence:

    """
    Holds the sequence and accumulated analysis data.
    """

    sequence = AminoAcidSequence()

    def __init__(self, name: str, sequence: str):
        self.name = name
        self.sequence = sequence
        self.metadata = dict()

    def __len__(self):
        return len(self.sequence)

    def __repr__(self):
        seq_rep = self.sequence if len(self) <= 20 else self.sequence[:10] + '...' + self.sequence[-10:]
        return f'ProteinSequence(name={self.name}, sequence={seq_rep})'

    def __hash__(self):
        return hash(self.sequence)