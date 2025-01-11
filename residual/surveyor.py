from collections.abc import Iterable
from itertools import count

from residual.protein_sequence import ProteinSequence
from residual.services.loader import load_services
from residual.services.base_class import service_registry

class Surveyor:
    """Loads protein sequences and runs services against them."""

    def __init__(self, user_email: str) -> None:
        load_services()
        self.user_email = user_email
        self.sequences: dict[str: ProteinSequence] = dict()

    def load_fasta(self,
                   __file: str,
                   /, *,
                   overwrite: bool = True,
                   ) -> None:

        """
        Import sequences from a fasta-formatted file.

        :param __file: path to file.
        :param overwrite: whether to replace any currently loaded sequences.
        """

        with open(__file, "r") as file:
            lines = [line.strip() for line in file.readlines()][::-1]

        if overwrite:
            self.sequences = {}

        seq_lines = []

        for line in lines:
            if line.startswith('>'):
                name = line.lstrip('>')
                sequence = ''.join(seq_lines)
                self.sequences[name] = ProteinSequence(name, sequence)
                seq_lines = []

            else:
                seq_lines.insert(0, line)

        print(f'{len(self.sequences)} total sequences loaded.')


    def load_strings(self,
                     __seqs: Iterable[str],
                     /, *,
                     names: Iterable[str] | None = None,
                     overwrite: bool = True,
                     ) -> None:

        """
        Loads sequences directly from strings.

        :param __seqs: iterable of sequence strings.
        :param names: names to give the sequences. If defined, must be an equal number of names
        and sequences. Otherwise, names default to sequence_001, sequence_002 etc.
        :param overwrite: whether to clear currently loaded sequences first.
        :raises ValueError: if unequal number of names and sequences are given.
        """

        if overwrite:
            self.sequences = {}

        if names:
            try:
                name_seq_pairs = list(zip(names, __seqs, strict=True))
            except ValueError:
                raise ValueError('Number of names and sequences must be equal.')
        else:
            name_seq_pairs = zip((f'sequence_{i:03}' for i in count(1)), __seqs)

        for name, sequence in name_seq_pairs:
            self.sequences[name] = ProteinSequence(name, sequence)

        print(f'{len(self.sequences)} total sequences loaded.')


    def run(self) -> None:

        for name, service_cls in service_registry.items():
            service = service_cls(self.user_email)
            service.run(self.sequences.values())