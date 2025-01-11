from dataclasses import dataclass, field

from watchtower.utils import validate_aa_sequence

@dataclass
class ProteinSequence:

    """
    Holds the sequence and accumulated analysis data.
    """

    name: str
    sequence: str
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        validate_aa_sequence(self.sequence)
