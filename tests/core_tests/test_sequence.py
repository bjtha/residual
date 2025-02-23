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

def test_feature_into_rows() -> None:
    feature1 = Feature(service='Service 1',
                       name='Signature A',
                       locations=[(1, 10), (50, 60)],
                       go_terms=[GoTerm('GO:0000001', 'BIOLOGICAL PROCESS', 'Replication')])
    display = SequenceDisplay(ProteinSequence(name='seq_1', sequence=''))
    feature1_as_rows = [('Service 1', 'Signature A', '1-10', 'GO:0000001 (BIOLOGICAL PROCESS) Replication'),
                        ('', '', '50-60', '')]
    assert display.feature_into_rows(feature1) == feature1_as_rows