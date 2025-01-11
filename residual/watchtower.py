from collections.abc import Iterable
from itertools import count
from functools import singledispatchmethod
from typing import Union, TypeVar, Type

from watchtower.protein_sequence import ProteinSequence
from watchtower.services.base_class import Service

DEFAULT_PARAMS = {}
SERVICE_REGISTER = {}

class Watchtower:
    """
    In charge of loading in sequences and running services against them.
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

    SequenceInputType = Union[str, Iterable[str]]

    @singledispatchmethod
    def load_seqs(self,
                  __seqs: SequenceInputType,
                  /, *,
                  names: Iterable[str] | None = None,
                  overwrite: bool = True,
                  ) -> None:

        raise ValueError("Sequences must be given as a file path or an iterable of strings")

    @load_seqs.register
    def _(self,
          __seqs: str,
          /, *,
          names: Iterable[str] | None = None,
          overwrite: bool = True,
          ) -> None:

        """
        Import sequences from a fasta-formatted file.

        :param __seqs: path to file.
        :param overwrite: whether to replace any currently loaded sequences.
        """

        with open(__seqs, "r") as file:
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


    @load_seqs.register
    def _(self,
          __seqs: Iterable,
          /, *,
          names: Iterable[str] | None = None,
          overwrite: bool = True,
          ) -> None:

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
        for cls_name in SERVICE_REGISTER:
            print(cls_name)

S = TypeVar('S', bound=Type[Service])

def register_service(cls: S) -> S:
    SERVICE_REGISTER[cls.__name__] = cls
    return cls