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

def test_feature_display() -> None:
    feature1 = Feature(service='Service',
                       name='Signature A',
                       locations=[(1, 10), (50, 60)],
                       go_terms=[GoTerm('GO:0000001', 'BIOLOGICAL PROCESS', 'Replication')])
    feature2 = Feature(service='Service',
                       name='Signature B',
                       go_terms=[GoTerm('GO:0000200', 'MOLECULAR FUNCTION', 'Enzyme activity'),
                                 GoTerm('GO:0000201', 'MOLECULAR FUNCTION', 'Cofactor binding')])
    feature3 = Feature(service='Service',
                       name='Signature C',
                       locations=[(5, 30), (40, 50), (70, 85)])

    seq = ProteinSequence(name='seq_1', sequence='MSFTLTNKNVIFVAGLGGIGLDTSKELLKRDL')
    seq.features = [feature1, feature2, feature3]

    print('\n')
    for line in seq.features_as_lines():
        print(line)