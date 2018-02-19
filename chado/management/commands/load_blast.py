"""Load FASTA file."""

from Bio.Blast import NCBIXML
from chado.loaders.common import FileValidator
from chado.loaders.exceptions import ImportingError
from chado.loaders.similarity import SimilarityLoader
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.core.management.base import BaseCommand, CommandError
import os
from tqdm import tqdm


class Command(BaseCommand):
    """Load FASTA file."""

    help = 'Load FASTA file'

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--file", help="BLAST File", required=True,
                            type=str)
        parser.add_argument("--so_query", help="Query Sequence Ontology term. "
                            "eg. assembly, mRNA, CDS, polypeptide",
                            required=True, type=str)
        parser.add_argument("--so_subject", help="Subject Sequence Ontology "
                            "term. eg. assembly, mRNA, CDS, polypeptide",
                            required=True, type=str)
        parser.add_argument("--program", help="Program", required=True,
                            type=str)
        parser.add_argument("--programversion", help="Program version",
                            required=True, type=str)
        parser.add_argument("--name", help="Name",
                            required=False, type=str)
        parser.add_argument("--description", help="Description",
                            required=False, type=str)
        parser.add_argument("--algorithm", help="Algorithm",
                            required=False, type=str)
        parser.add_argument("--cpu", help="Number of threads", default=1,
                            type=int)

    def handle(self,
               file: str,
               so_query: str,
               so_subject: str,
               program: str,
               programversion: str,
               name: str=None,
               description: str=None,
               algorithm: str=None,
               cpu: int=1,
               verbosity: int=1,
               **options):
        """Execute the main function."""
        if verbosity > 0:
            self.stdout.write('Preprocessing')

        try:
            FileValidator().validate(file)
        except ImportingError as e:
            raise CommandError(e)

        filename = os.path.basename(file)

        try:
            blast_file = SimilarityLoader(
                    filename=filename,
                    so_query=so_query,
                    so_subject=so_subject,
                    algorithm=algorithm,
                    name=name,
                    description=description,
                    program=program,
                    programversion=programversion)
        except ImportingError as e:
            raise CommandError(e)

        try:
            blast_records = NCBIXML.parse(open(file))
        except ValueError as e:
            return CommandError(e)

        pool = ThreadPoolExecutor(max_workers=cpu)
        tasks = list()
        for record in blast_records:
            if len(record.alignments) > 0:
                tasks.append(pool.submit(blast_file.store_bio_blast_record,
                                         record))
        if verbosity > 0:
            self.stdout.write('Loading')
        for task in tqdm(as_completed(tasks), total=len(tasks)):
            try:
                task.result()
            except ImportingError as e:
                raise CommandError(e)

        self.stdout.write(self.style.SUCCESS('Done'))