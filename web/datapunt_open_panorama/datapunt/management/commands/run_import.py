import sys

from django.core.management import BaseCommand, call_command

import datasets.panoramas.batch


class Command(BaseCommand):

    ordered = ['panorama']

    imports = dict(
        panorama=[datasets.panoramas.batch.ImportPanoramaJob],
    )

    def add_arguments(self, parser):
        parser.add_argument(
            'dataset',
            nargs='*',
            default=self.ordered,
            help="Dataset to import, choose from {}".format(
                ', '.join(self.imports.keys())))

    def handle(self, *args, **options):
        dataset = options['dataset']

        for ds in dataset:
            if ds not in self.imports.keys():
                self.stderr.write("Unkown dataset: {}".format(ds))
                sys.exit(1)

        sets = [ds for ds in self.ordered if ds in dataset]     # enforce order

        self.stdout.write("Importing {}".format(", ".join(sets)))

        for ds in sets:

            for job_class in self.imports[ds]:
                job_class().process()

            #call_command('create_geo_tables')
