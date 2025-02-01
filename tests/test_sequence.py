import pytest
from residual.protein_sequence import *


def test_creation() -> None:

    seq = ProteinSequence(name='seq_1', sequence='MSFTLTNKNVIFVAGLGGIGLDTSKELLKRDL')

    assert seq.sequence == 'MSFTLTNKNVIFVAGLGGIGLDTSKELLKRDL'
    assert seq.name == 'seq_1'
    assert len(seq) == 32
    assert str(seq) == 'ProteinSequence(name=seq_1, sequence=MSFTLTNKNV...TSKELLKRDL)'

    copy_seq = ProteinSequence(name='seq_2', sequence='MSFTLTNKNVIFVAGLGGIGLDTSKELLKRDL')
    assert hash(seq) == hash(copy_seq)

def test_validation() -> None:

    with pytest.raises(ValueError):
        ProteinSequence(name='seq_2', sequence='NHVLQHAEPGNAQB')
        ProteinSequence(name='seq_3', sequence='NHVLQHAEPGNAQS\n')
        ProteinSequence(name='seq_4', sequence='nhvlqhaepgnaqs')
