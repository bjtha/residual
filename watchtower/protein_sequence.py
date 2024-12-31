from dataclasses import dataclass, field

@dataclass
class ProteinSequence:

    """
    Holds the sequence and accumulated analysis data.
    """

    name: str
    sequence: str
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:

        sequence = set(self.sequence)
        allowed = set('ACDEFGHIKLMNPQRSTVWY')  # Valid amino acid symbols

        if disallowed := (sequence - allowed):
            raise ValueError(f'Invalid sequence characters: {" ".join(str(i) for i in disallowed)}')
