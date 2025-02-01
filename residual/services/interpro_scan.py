import asyncio
import aiohttp
from typing import Iterable

from loguru import logger

from residual.protein_sequence import ProteinSequence
from residual.services import ServiceBaseClass, register_service
from residual.utils import ExtendableUrl

@register_service
class InterProScan(ServiceBaseClass):

    base_url = ExtendableUrl('https://www.ebi.ac.uk/Tools/services/rest/iprscan5')
    max_jobs = 30

    def __init__(self, user_email: str):
        super().__init__()
        self.user_email = user_email

    def name(self) -> str:
        return 'ips5'

    async def _submit_sequence(self,
                               session: aiohttp.ClientSession,
                               seq: ProteinSequence,
                               ) -> str:

        """
        Sends request for a given sequence to the InterProScan API.

        :param seq: ProteinSequence to scan
        :return: id of successfully submitted job
        :raises: HTTPError if problem with retrieving the parameter names or sending the request.
        """

        payload = {
            'email': self.user_email,
            'title': seq.name,
            'goterms': True,
            'pathways': False,
            'stype': 'p',
            # 'appl': '',
            'sequence': seq.sequence,
        }

        url = self.base_url / 'run'
        async with session.post(str(url), data=payload) as res:
            res.raise_for_status()
            return await res.text()

    async def _retrieve_results(self,
                                session: aiohttp.ClientSession,
                                job_id: str,
                                check_delay: int = 1,
                                ) -> dict:

        """
        Fetch results for a job.

        :param job_id: id of the job, provided at time of submission.
        :param check_delay: how long in seconds to wait between checking job status.
        :return: dictionary containing json data.
        :raises: HTTPError if a problem with the status checking or data retrieval.
        :raises: ValueError if save filepath is not to a file ending '.json'.
        :raises: FileNotFoundError if save filepath is not valid.
        """

        url = self.base_url / 'status' / job_id

        while True:
            async with session.get(str(url)) as res:
                res.raise_for_status()
                status = await res.text()

            if status != 'FINISHED':
                await asyncio.sleep(check_delay)
            else:
                break

        url = self.base_url / 'result' / job_id / 'json'
        async with session.get(str(url)) as res:
            res.raise_for_status()
            return await res.json()


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


    async def _scan_sequence(self,
                             seq: ProteinSequence,
                             semaphore: asyncio.Semaphore,
                             session: aiohttp.ClientSession) -> None:

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
            job_id = await self._submit_sequence(session, seq)
            data = await self._retrieve_results(session, job_id)
            self._apply_data(seq, data)

        logger.info(f'{seq.name}: Scan finished.')

    async def _dispatch_jobs(self, sequences: Iterable[ProteinSequence]):

        semaphore = asyncio.Semaphore(self.max_jobs)

        async with aiohttp.ClientSession() as session:
            jobs = [self._scan_sequence(seq, semaphore, session) for seq in sequences]
            await asyncio.gather(*jobs)


    def run(self, inputs: Iterable[ProteinSequence]) -> list[ProteinSequence]:

        logger.info('Running InterProScan...')
        sequences = iter(inputs)
        asyncio.run(self._dispatch_jobs(sequences))

        logger.info('InterProScan run complete')
        return list(sequences)
