from urllib.parse import urlparse

from django.contrib.sites.models import Site
from django.core.management import BaseCommand


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('base_uri', help='Base URI for the API, such as https://somesite.com/api/')

    def handle(self, *args, **options):
        base = options['base_uri']
        assert base

        # ensure base ends with '/'
        if not base.endswith('/'):
            base += '/'

        # parse out domain
        parsed = urlparse(base)
        domain = parsed.netloc
        assert domain

        # ensure the API Domain site contains base
        Site.objects.update_or_create(name='API Domain', defaults=dict(
            domain=base
        ))

        # ensure the admin Domain contains domain
        Site.objects.update_or_create(name='Admin domain', defaults=dict(
            domain=domain
        ))
