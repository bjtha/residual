from collections.abc import Callable, Iterable

ALLOWED_SYMBOLS = set('ACDEFGHIKLMNPQRSTVWY')  # valid amino acid symbols

def validate_aa_sequence(seq: str) -> None:

    """
    Check if a given string qualifies as a protein sequence based on the characters present.

    :param seq: sequence as a contiguous string.
    :return: True if valid, False otherwise.
    """

    if disallowed := (set(seq) - ALLOWED_SYMBOLS):
        raise ValueError(f'Invalid sequence characters: {" ".join(str(i) for i in disallowed)}')


def url_maker(base_url: str):

    def join_url(*args) -> str:
        return '/'.join(str(item) for item in [base_url, *args])

    return join_url