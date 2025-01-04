import json
import os
import requests
from time import sleep, time
from typing import Iterable
import xml.etree.ElementTree as ET

from watchtower.protein_sequence import ProteinSequence
from watchtower.services.base_class import Service
from watchtower.utils import url_maker

USER_EMAIL = os.getenv('USER_EMAIL')

class InterProScan(Service):

    base_url = 'https://www.ebi.ac.uk/Tools/services/rest/iprscan5'

    def __init__(self, user_email: str):
        super().__init__()

        self.user_email = user_email
        self.make_url = url_maker(self.base_url)

    def name(self) -> str:
        return 'ips5'

    def run(self, inputs: Iterable[ProteinSequence]) -> list[ProteinSequence]:

        sequences = iter(inputs)

        # Set up a dictionary for sequence-job mapping

        # Establish the max number of concurrent

        # i = 0
        # j = max_jobs

        # while done < len(sequences):
            # for sequence in sequences[i:j]:
                # send sequences for analysis
                # collect job_id, map it to the sequence object ( {job_id: ProteinSequence} )
            # for job_id in the mapping:
                # wait for the job is complete
                # assign the results to a results dictionary
                # increment the 'done' counter
            # set up the next bracket by updating i and j

        data = {self.name: {}}

        for sequence in inputs:
            sequence.metadata.update(data)

        return list(inputs)

    def _submit_sequence(self, seq: ProteinSequence, **params) -> str:

        """
        Sends request for a given sequence to the InterProScan API.

        :param seq: ProteinSequence to scan
        :param params: keyword parameters defining options for the run. If not specified, defaults apply.
        :return: id of successfully submitted job
        :raises: HTTPError if problem with retrieving the parameter names or sending the request.
        """

        payload = {
            'email': USER_EMAIL,
            'title': seq.name,
            'goterms': True,
            'pathways': False,
            'stype': 'p',
            'appl': None,
            'sequence': seq.sequence,
        }

        # Update with user-defined options to the payload if they are accepted by the API
        if params:
            res = requests.get(url=self.make_url('parameters'))
            res.raise_for_status()
            available_parameters = [param.text for param in ET.fromstring(res.text)]  # Parsed xml result

            for key, value in params.items():
                if key in available_parameters:
                    payload[key] = value

        res = requests.post(url=self.make_url('run'),
                            data=payload)
        res.raise_for_status()

        return res.text

    def _retrieve_results(self,
                          job_id: str,
                          check_delay: int = 10,
                          save_file: str | None = None,
                          verbose: bool = False,
                          ) -> dict:

        """
        Fetch results for a job.

        :param job_id: id of the job, provided at time of submission.
        :param check_delay: how long in seconds to wait between checking job status.
        :param save_file: location to save retrieved json data. If None, does not save.
        :param verbose: whether to print status updates while in checking loop.
        :return: dictionary containing json data.
        :raises: HTTPError if a problem with the status checking or data retrieval.
        :raises: ValueError if save filepath is not to a file ending '.json'
        :raises: FileNotFoundError if save filepath is not valid
        """

        url = self.make_url('status', job_id)

        start = time()
        check_count = 0
        status_string = ''
        while True:
            res = requests.get(url)
            check_count += 1
            res.raise_for_status()
            status = res.text

            if verbose:
                print('\r' + ' '*len(status_string), end='')
                elapsed = round(time()-start, 1)
                status_string = str(check_count).ljust(5) + f'ELAPSED: {elapsed} s'.ljust(18) + status
                print('\r' + status_string, end='')

            if status != 'FINISHED':
                sleep(check_delay)
            else:
                break

        url = self.make_url('result', job_id, 'json')
        res = requests.get(url)
        res.raise_for_status()

        if save_file:
            if not save_file.endswith('.json'):
                raise ValueError('Must save data to a .json file.')

            with open(save_file, "w") as file:
                file.write(res.text)

        result_data = json.loads(res.text)

        return result_data

    def _apply_data(self, seq: ProteinSequence, data: dict) -> None:

        """
        Extract desired data from the API result and add to the ProteinSequence.

        :param seq: original ProteinSequences
        :param data: result from scan
        :return:
        """

        matches = [match for match in data['results'][0]['matches'] if match['signature']['entry'] is not None]

        result = {}
        for match in matches:
            ipr_name = match['signature']['entry']['accession']
            description = match['signature']['entry']['description']

            go_terms = {}
            for match_go in match['signature']['entry']['goXRefs']:
                go_terms[match_go['id']] = {
                    'name': match_go['name'],
                    'category': match_go['category']
                }

            locations = []
            for match_loc in match['locations']:
                locations.append(
                    (match_loc['start'], match_loc['end'])
                )

            result[ipr_name] = {'description': description,
                                'go_terms': go_terms,
                                'locations': locations,}

        seq.metadata[self.name()] = result


if __name__ == '__main__':
    ips = InterProScan(USER_EMAIL)

    test_seq = ProteinSequence(name='P00334', sequence=
    'MSFTLTNKNVIFVAGLGGIGLDTSKELLKRDLKNLVILDRIENPAAIAELKAINPKVTVT'
    'FYPYDVTVPIAETTKLLKTIFAQLKTVDVLINGAGILDDHQIERTIAVNYTGLVNTTTAI'
    'LDFWDKRKGGPGGIICNIGSVTGFNAIYQVPVYSGTKAAVVNFTSSLAKLAPITGVTAYT'
    'VNPGITRTTLVHKFNSWLDVEPQVAEKLLAHPTQPSLACAENFVKAIELNQNGAIWKLDL'
    'GTLEAIQWTKHWDSGI'
                          )

    job = ips._submit_sequence(test_seq)
    job_data = ips._retrieve_results(job, verbose=True, save_file='./job_data.json')
    ips._apply_data(test_seq, job_data)

    print(test_seq.metadata)