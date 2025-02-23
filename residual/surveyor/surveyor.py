from collections.abc import Iterable
from itertools import count

from loguru import logger

from residual.protein_sequence import ProteinSequence, SequenceDisplay
from residual.services.base_class import service_registry

class Surveyor:
    """Loads protein sequences, runs services against them and writes out the result."""

    def __init__(self, user_email: str) -> None:
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
        :param overwrite: whether to replace any currently loaded sequences, default = True.
        """

        with open(__file, "r") as file:
            lines = [line.strip() for line in file.readlines()][::-1]
            # Reading file in reverse, so names are encountered after the sequence, makes it easier to
            # tell when the final sequence has ended.

        if overwrite:
            self.sequences = {}

        seq_lines = []

        for line in lines:
            if line.startswith('>'):
                name = line.lstrip('>')
                sequence = ''.join(seq_lines)
                try:
                    self.sequences[name] = ProteinSequence(name, sequence)
                except ValueError as e:
                    logger.error(f'Error parsing {name}: {e}')
                    continue
                finally:
                    seq_lines = []
            else:
                seq_lines.insert(0, line)

        logger.info(f'{len(self.sequences)} total sequences loaded.')


    def load_strings(self,
                     __seqs: Iterable[str],
                     /, *,
                     names: Iterable[str] | None = None,
                     overwrite: bool = True,
                     ) -> None:

        """
        Loads sequences directly from strings.

        :param __seqs: iterable of sequence strings.
        :param names: names to give the sequences. If defined, there must be an equal number of names
                      and sequences. Otherwise, names default to sequence_001, sequence_002 etc.
        :param overwrite: whether to clear currently loaded sequences first, default = True.
        """

        if overwrite:
            self.sequences = {}

        if names:
            try:
                name_seq_pairs = list(zip(names, __seqs, strict=True))
            except ValueError:
                logger.error('Number of names and sequences must be equal.')
                return
        else:
            name_seq_pairs = zip((f'sequence_{i:03}' for i in count(1)), __seqs)

        for name, sequence in name_seq_pairs:
            try:
                self.sequences[name] = ProteinSequence(name, sequence)
            except ValueError as e:
                logger.error(f'Error parsing {name}: {e}')

        print(f'{len(self.sequences)} total sequences loaded.')

    def write_out(self, filename: str) -> None:
        with open(filename, 'w') as file:
            for seq in self.sequences.values():
                display = SequenceDisplay(seq)
                file.write(display())
                file.write('\n')

    def run(self, outfile: str) -> None:
        for name, service_cls in service_registry.items():
            service = service_cls(self.user_email)
            service.run(self.sequences.values())
        self.write_out(filename=outfile)