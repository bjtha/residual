import pytest

from watchtower.watchtower import Watchtower

def test_fasta_loading() -> None:

    wt = Watchtower()
    wt.load_seqs('data/tests/adh.fasta')

    assert len(wt.sequences) == 3
    assert wt.sequences['P00334'].sequence[:10] == 'MSFTLTNKNV'
    assert wt.sequences['P28469'].sequence[:10] == 'MSTAGKVIKC'
    assert wt.sequences['Q9QYY9'].sequence[:10] == 'MGTQGKVIKC'

def test_iterable_loading() -> None:
    wt = Watchtower()

    sequences = ['MSFTLTNKNV', 'MSTAGKVIKC', 'MGTQGKVIKC']

    with pytest.raises(ValueError):  # Check unequal name/sequence iterators are disallowed
        short_names = ['P00334', 'P28469']
        wt.load_seqs(sequences, names=short_names)

    names = ['P00334', 'P28469', 'Q9QYY9']
    wt.load_seqs(sequences, names=names) # With given names

    assert len(wt.sequences) == 3
    assert wt.sequences['P00334'].sequence[:10] == 'MSFTLTNKNV'
    assert wt.sequences['P28469'].sequence[:10] == 'MSTAGKVIKC'
    assert wt.sequences['Q9QYY9'].sequence[:10] == 'MGTQGKVIKC'

    wt.load_seqs(sequences) # With automatic names
    assert wt.sequences['sequence_003'].sequence[:10] == 'MGTQGKVIKC'