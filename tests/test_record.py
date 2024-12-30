import pytest
from watchtower.sequence_record import SequenceRecord

def test_validation() -> None:

    SequenceRecord(name='seq_1', sequence='NHVLQHAEPGNAQS')

    with pytest.raises(ValueError):
        SequenceRecord(name='seq_2', sequence='NHVLQHAEPGNAQB')
        SequenceRecord(name='seq_3', sequence='NHVLQHAEPGNAQS\n')
        SequenceRecord(name='seq_4', sequence='nhvlqhaepgnaqs')
