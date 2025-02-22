import json
import pytest

from residual.services.interpro_scan import *

@pytest.fixture
def _job_data() -> dict[str: dict]:
    data = {}
    for seq_name in ('P00334', 'P28469', 'Q9QYY9'):
        with open(f'data/tests/{seq_name}.json') as file:
            data[seq_name] = json.load(file)
    return data


@pytest.fixture
def _ipr_scan() -> InterProScan:
    return InterProScan(user_email='test@test.com')


def test_parse_match(_ipr_scan, _job_data) -> None:

    print('\n')
    result = _job_data['P00334']
    features = _ipr_scan.parser(result)
    for ft in features:
        print(ft)

