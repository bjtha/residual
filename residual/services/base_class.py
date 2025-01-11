from abc import ABC, abstractmethod
from collections.abc import Iterable

from residual.protein_sequence import ProteinSequence

service_registry = {}

def register_service(cls):
    """Decorator for services to have them automatically detected by the Surveyor."""
    service_registry[cls.__name__] = cls
    return cls

class ServiceBaseClass(ABC):
    """Base class for a service provider."""

    def __init__(self):
        ...

    @abstractmethod
    def run(self, inputs: Iterable[ProteinSequence]) -> list[ProteinSequence]:
        """
        Perform analysis on the given protein sequences and add the data to the objects.

        :param inputs: ProteinSequence instances to be analysed.
        :return:
        """