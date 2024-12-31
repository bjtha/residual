from collections.abc import Iterable
from functools import singledispatchmethod
from typing import Union

from watchtower.protein_sequence import ProteinSequence

DEFAULT_PARAMS = {}

class Watchtower:
    """
    In charge of running services against the given sequences and outputting the final result
    """

    def __init__(self, params: dict = None) -> None:

        self.sequences = dict()
        self.output = 'normal'

        if params is None:
            params = DEFAULT_PARAMS

        self.configure(**params)

    def configure(self, **kwargs) -> None:
        for key, value in kwargs.items():

            if not hasattr(self, key):
                raise AttributeError(f'{key} is not a configureable property of {self.__class__.__name__}')

            setattr(self, key, value)

    SequenceInputType = Union[str, Iterable]

    @singledispatchmethod
    def load_seqs(self, __seqs: SequenceInputType, /):
        raise ValueError("Sequences must be given as a file path or an iterable of strings")

    @load_seqs.register
    def _(self, seqs: str) -> None:

        """
        Import sequences from a fasta-formatted file.

        :param seqs: path to file.
        """

        with open(seqs, "r") as file:
            lines = [line.strip() for line in file.readlines()][::-1]

        seq_lines = []

        for line in lines:
            if line.startswith('>'):
                name = line.lstrip('>')
                sequence = ''.join(seq_lines)
                self.sequences[name] = ProteinSequence(name, sequence)
                seq_lines = []

            else:
                seq_lines.insert(0, line)


    @load_seqs.register
    def _(self, seqs: Iterable):
        print('Attempting to load sequences from an iterable...')


if __name__ == '__main__':

    watch = Watchtower()
    watch.load_seqs("filepath")
    watch.load_seqs(['A', 'B', 'C'])
    watch.load_seqs(str(i) for i in range(5))