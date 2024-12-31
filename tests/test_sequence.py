import pytest
from watchtower.protein_sequence import ProteinSequence

def test_validation() -> None:

    ProteinSequence(name='seq_1', sequence='NHVLQHAEPGNAQS')

    with pytest.raises(ValueError):
        ProteinSequence(name='seq_2', sequence='NHVLQHAEPGNAQB')
        ProteinSequence(name='seq_3', sequence='NHVLQHAEPGNAQS\n')
        ProteinSequence(name='seq_4', sequence='nhvlqhaepgnaqs')
