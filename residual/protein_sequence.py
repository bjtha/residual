from dataclasses import dataclass, field

ALLOWED_SYMBOLS = set('ACDEFGHIKLMNPQRSTVWY')  # Valid amino acid symbols


@dataclass
class ProteinSequence:

    """
    Holds the sequence and accumulated analysis data.
    """

    name: str
    sequence: str
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.validate_aa_sequence(self.sequence)

    @staticmethod
    def validate_aa_sequence(seq: str) -> None:
        """
        Check if a given string qualifies as a protein sequence based on the characters present.

        :param seq: sequence as a contiguous string.
        :return: True if valid, False otherwise.
        """

        if disallowed := (set(seq) - ALLOWED_SYMBOLS):
            raise ValueError(f'Invalid sequence characters: {" ".join(str(i) for i in disallowed)}')