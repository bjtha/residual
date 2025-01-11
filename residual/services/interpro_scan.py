import asyncio
import json
import os
import requests
from time import sleep
from typing import Iterable
import xml.etree.ElementTree as ET

from loguru import logger

from residual.protein_sequence import ProteinSequence
from residual.services import ServiceBaseClass, register_service
from residual.utils import url_maker

@register_service
class InterProScan(ServiceBaseClass):

    base_url = 'https://www.ebi.ac.uk/Tools/services/rest/iprscan5'
    max_jobs = 2

    def __init__(self, user_email: str):
        super().__init__()

        self.user_email = user_email
        self.make_url = url_maker(self.base_url)

    def name(self) -> str:
        return 'ips5'

    def _submit_sequence(self, seq: ProteinSequence, **params) -> str:

        """
        Sends request for a given sequence to the InterProScan API.

        :param seq: ProteinSequence to scan
        :param params: keyword parameters defining options for the run. If not specified, defaults apply.
        :return: id of successfully submitted job
        :raises: HTTPError if problem with retrieving the parameter names or sending the request.
        """

        payload = {
            'email': self.user_email,
            'title': seq.name,
            'goterms': True,
            'pathways': False,
            'stype': 'p',
            'appl': None,
            'sequence': seq.sequence,
        }

        # Update payload with user-defined options if they are accepted by the API
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

    async def _retrieve_results(self,
                          job_id: str,
                          check_delay: int = 5,
                          save_file: str | None = None,
                          ) -> dict:

        """
        Fetch results for a job.

        :param job_id: id of the job, provided at time of submission.
        :param check_delay: how long in seconds to wait between checking job status.
        :param save_file: location to save retrieved json data. If None, does not save.
        :return: dictionary containing json data.
        :raises: HTTPError if a problem with the status checking or data retrieval.
        :raises: ValueError if save filepath is not to a file ending '.json'.
        :raises: FileNotFoundError if save filepath is not valid.
        """

        url = self.make_url('status', job_id)

        while True:
            res = requests.get(url)
            res.raise_for_status()
            status = res.text

            if status != 'FINISHED':
                await asyncio.sleep(check_delay)
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


    async def _scan_sequence(self, seq: ProteinSequence, semaphore: asyncio.Semaphore) -> None:

        """
        Query the InterProScan with a sequence, collect the results and write the data
        to the sequence object.

        :param seq: ProteinSequence to be scanned.
        :param semaphore:
        :return:
        """

        logger.info(f'{seq.name}: Waiting for semaphore...')

        async with semaphore:
            logger.info(f'{seq.name}: Scanning now...')
            job_id = self._submit_sequence(seq)
            data = await self._retrieve_results(job_id)
            self._apply_data(seq, data)

        logger.info(f'{seq.name}: Scan finished.')

    async def _dispatch_jobs(self, sequences: Iterable[ProteinSequence]):

        """
        :param sequences:
        :return:
        """

        semaphore = asyncio.Semaphore(self.max_jobs)

        jobs = []

        for seq in sequences:
            logger.info(f'Creating task for {seq.name}')
            jobs.append(asyncio.create_task(self._scan_sequence(seq, semaphore)))

        await asyncio.gather(*jobs)


    def run(self, inputs: Iterable[ProteinSequence]) -> list[ProteinSequence]:

        logger.info('Running InterProScan...')
        sequences = iter(inputs)
        asyncio.run(self._dispatch_jobs(sequences))

        logger.info('InterProScan run complete')
        return list(sequences)

if __name__ == '__main__':
    ips = InterProScan(os.environ['USER_EMAIL'])

    test_seq = ProteinSequence(name='P00334', sequence=
    'MSFTLTNKNVIFVAGLGGIGLDTSKELLKRDLKNLVILDRIENPAAIAELKAINPKVTVT'
    'FYPYDVTVPIAETTKLLKTIFAQLKTVDVLINGAGILDDHQIERTIAVNYTGLVNTTTAI'
    'LDFWDKRKGGPGGIICNIGSVTGFNAIYQVPVYSGTKAAVVNFTSSLAKLAPITGVTAYT'
    'VNPGITRTTLVHKFNSWLDVEPQVAEKLLAHPTQPSLACAENFVKAIELNQNGAIWKLDL'
    'GTLEAIQWTKHWDSGI'
                          )

