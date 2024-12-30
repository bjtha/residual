from collections.abc import Iterable
from functools import singledispatchmethod

DEFAULT_PARAMS = {}

class Watchtower:
    """
    In charge of running services against the given sequences and outputting the final result
    """

    def __init__(self, params: dict = None) -> None:

        self.output = 'normal'

        if params is None:
            params = DEFAULT_PARAMS

        self.configure(**params)

    def configure(self, **kwargs) -> None:
        for key, value in kwargs.items():

            if not hasattr(self, key):
                raise AttributeError(f'{key} is not a configureable property of {self.__class__.__name__}')

            setattr(self, key, value)

    @singledispatchmethod
    def load_seqs(self, seqs):
        raise ValueError("Sequences must be given as a file path or an iterable of strings")

    @load_seqs.register
    def _(self, seqs: str):
        print('Attempting to load sequences from a filepath...')

    @load_seqs.register
    def _(self, seqs: Iterable):
        print('Attempting to load sequences from an iterable...')


if __name__ == '__main__':

    watch = Watchtower()
    watch.load_seqs("filepath")
    watch.load_seqs(['A', 'B', 'C'])
    watch.load_seqs(str(i) for i in range(5))