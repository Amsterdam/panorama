from django.core.management import call_command
from django.test import TestCase


class CommandsTestCase(TestCase):
    def test_add_region_runs_when_called_twice(self):
        args = ['--pano_id', 'TMX7316060226-000030_pano_0008_000650', '--type', 'G', '--coords', '1250,1990,1280,2010']
        call_command('add_region', *args)
        call_command('add_region', *args)
