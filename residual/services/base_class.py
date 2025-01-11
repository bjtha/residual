from abc import ABC, abstractmethod
from collections.abc import Iterable

from watchtower.protein_sequence import ProteinSequence

class Service(ABC):
    """
    Base class for a service provider.
    """

    def __init__(self):
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Name of the service
        :return:
        """

    @abstractmethod
    def run(self, inputs: Iterable[ProteinSequence]) -> list[ProteinSequence]:
        """
        Perform analysis on the given protein sequences and add the data to the objects.

        :param inputs: ProteinSequence instances to be analysed.
        :return:
        """