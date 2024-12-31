from watchtower.watchtower import Watchtower

def test_fasta_loading() -> None:

    wt = Watchtower()
    wt.load_seqs('data/tests/adh.fasta')

    assert len(wt.sequences) == 3
    assert wt.sequences['P00334'].sequence[:10] == 'MSFTLTNKNV'
    assert wt.sequences['P28469'].sequence[:10] == 'MSTAGKVIKC'
    assert wt.sequences['Q9QYY9'].sequence[:10] == 'MGTQGKVIKC'
