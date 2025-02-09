import asyncio

import aiohttp
from typing import Iterable

from loguru import logger

from residual.protein_sequence import ProteinSequence, Feature, GoTerm
from residual.services import ServiceBaseClass, register_service
from residual.utils import RequestResult

@register_service
class InterProScan(ServiceBaseClass):

    base_url = 'https://www.ebi.ac.uk/Tools/services/rest/iprscan5/'
    max_jobs = 30

    def __init__(self, user_email: str):
        super().__init__()
        self.user_email = user_email

    def name(self) -> str:
        return 'ips5'

    async def _submit_sequence(self,
                               session: aiohttp.ClientSession,
                               seq: ProteinSequence,
                               ) -> (RequestResult, str):

        """
        Sends request for a given sequence to the InterProScan API.
        """

        payload = {
            'email': self.user_email,
            'title': seq.name,
            'goterms': True,
            'pathways': False,
            'stype': 'p',
            'sequence': seq.sequence,
        }

        retries = 3
        for attempt in range(1, retries+1):
            try:
                async with session.post('run', data=payload) as res:
                    res.raise_for_status()
                    job_id = await res.text()
                    return RequestResult.SUCCESS, job_id

            except aiohttp.ClientResponseError as e:
                logger.error(f'HTTP Error {e.status}: {e.message} (Attempt {attempt} of {retries})')
                if e.status >= 500:  # Server-side error
                    await asyncio.sleep(2**attempt)
                    continue
                else:  # Client-side error
                    break

        return RequestResult.FAILURE, ''

    async def _retrieve_results(self,
                                session: aiohttp.ClientSession,
                                job_id: str,
                                check_delay: int = 1,
                                ) -> (RequestResult, dict):

        """
        Fetch results for a job.

        :param job_id: id of the job, provided at submission.
        :param check_delay: how long in seconds to wait between checking job status.
        :return: dictionary containing json data.
        :raises: HTTPError if a problem with the status checking or data retrieval.
        :raises: ValueError if save filepath is not to a file ending '.json'.
        :raises: FileNotFoundError if save filepath is not valid.
        """

        while True:
            try:
                async with session.get(f'status/{job_id}') as res:
                    res.raise_for_status()
                    status = await res.text()
            except aiohttp.ClientResponseError as e:
                logger.error(f'HTTP Error {e.status}: {e.message}')
                return RequestResult.FAILURE, {}

            if status != 'FINISHED':
                await asyncio.sleep(check_delay)
            else:
                break

        async with session.get(f'result/{job_id}/json') as res:
            res.raise_for_status()
            job_data = await res.json()
            return RequestResult.SUCCESS, job_data

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

            result, job_id = await self._submit_sequence(session, seq)
            if result == RequestResult.FAILURE:
                return

            result, data = await self._retrieve_results(session, job_id)
            if result == RequestResult.FAILURE:
                return

            seq.features += parse_iprscan_data(data)

        logger.info(f'{seq.name}: Scan finished.')

    async def _dispatch_jobs(self, sequences: Iterable[ProteinSequence]):

        semaphore = asyncio.Semaphore(self.max_jobs)

        async with aiohttp.ClientSession(base_url=self.base_url) as session:
            jobs = [self._scan_sequence(seq, semaphore, session) for seq in sequences]
            await asyncio.gather(*jobs)


    def run(self, inputs: Iterable[ProteinSequence]) -> list[ProteinSequence]:

        logger.info('Running InterProScan...')
        sequences = iter(inputs)
        asyncio.run(self._dispatch_jobs(sequences))

        logger.info('InterProScan run complete')
        return list(sequences)


def compose_name(data: dict) -> str | None:
    """Forms feature name from data; returns None if not enough information to give a meaningful name."""

    accession = data.get('accession')
    elements = [e for e in map(data.get, ('description', 'name')) if e not in (None, accession)]
    return elements[0] if elements else None


def collect_go_terms(data: dict) -> list[GoTerm | None]:
    go_terms = []
    if go_refs := data.get('goXRefs'):
        for ref in go_refs:
            if 'databaseName' in ref: ref.pop('databaseName')
            go_terms.append(GoTerm(**ref))
    return go_terms


def parse_match(match: dict) -> Feature | None:
    """Parses a single InterProScan match into a feature. Collects all GO terms and locations into the feature,
    but prefers descriptions given by the IPR database entry over signature descriptions."""

    go_terms = collect_go_terms(match)
    locations = [(loc['start'], loc['end']) for loc in match['locations']]

    signature = match['signature']
    name = compose_name(signature)

    if entry := signature.get('entry'):  # Replace signature-level description with entry if one's available.
        name = compose_name(entry) or name
        go_terms += collect_go_terms(entry)

    return Feature('iprscan5', name, locations, go_terms) if name else None


def parse_iprscan_data(data: dict) -> list[Feature]:
    """Parses response from an InterProScan job into a list of Features."""

    return [ft for ft in map(parse_match, data['results'][0]['matches']) if ft is not None]