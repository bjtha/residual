import pytest

from residual.surveyor import *

def test_fasta_loading() -> None:

    sv = Surveyor()
    sv.load_fasta('data/tests/adh.fasta')

    assert len(sv.sequences) == 3
    assert sv.sequences['P00334'].sequence[:10] == 'MSFTLTNKNV'
    assert sv.sequences['P28469'].sequence[:10] == 'MSTAGKVIKC'
    assert sv.sequences['Q9QYY9'].sequence[:10] == 'MGTQGKVIKC'

def test_iterable_loading() -> None:
    sv = Surveyor()

    sequences = ['MSFTLTNKNV', 'MSTAGKVIKC', 'MGTQGKVIKC']

    with pytest.raises(ValueError):  # Check unequal name/sequence iterators are disallowed
        short_names = ['P00334', 'P28469']
        sv.load_strings(sequences, names=short_names)

    names = ['P00334', 'P28469', 'Q9QYY9']
    sv.load_strings(sequences, names=names) # With given names

    assert len(sv.sequences) == 3
    assert sv.sequences['P00334'].sequence == 'MSFTLTNKNV'
    assert sv.sequences['P28469'].sequence == 'MSTAGKVIKC'
    assert sv.sequences['Q9QYY9'].sequence == 'MGTQGKVIKC'

    sv.load_strings(sequences) # With automatic names
    assert sv.sequences['sequence_003'].sequence == 'MGTQGKVIKC'

def test_register_service() -> None:

    @Surveyor.register_service
    class TestService(ServiceBaseClass):
        def run(self, inputs: Iterable[ProteinSequence]):
            ...

    assert Surveyor.service_register == {'TestService': TestService}