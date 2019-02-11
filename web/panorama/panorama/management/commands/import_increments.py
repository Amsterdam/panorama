import logging
import re
from django.core.management import BaseCommand

from panorama.etl.batch_import import rebuild_mission, import_mission_metadata
from panorama.etl.check_objectstore import set_uptodate_info
from panorama.etl.db_actions import dump_mission  # , write_increments, restore_data
from panorama.etl.increments import check_increments

log = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('increment', type=str, help="The increment to import (examples: '2016', '2016/01/', "
                                                        "'2017/02/03/' or even '2017/05/04/TMX000321015-00030/)")

    @staticmethod
    def _check_increment(increment):
        increment_in = increment

        if increment[:1] == "/":
            increment = increment[1:]

        if increment[-1:] != "/":
            increment = increment + "/"

        if not any([
            re.match(r'\d\d\d\d/', increment),
            re.match(r'\d\d\d\d/\d\d/', increment),
            re.match(r'\d\d\d\d/\d\d/\d\d/', increment),
            re.match(r'\d\d\d\d/\d\d/\d\d/\S\S\S\d\d\d\d\d\d\d\d\d\d\S\d\d\d\d\d\d/', increment),
        ]):
            raise Exception(f"Increment '{increment_in}' is not a valid incremental pattern")

        return increment

    def handle(self, *args, **options):
        increment = self._check_increment(options['increment']) if 'increment' in options else None

        up_to_date, missions_to_rebuild = check_increments(increment=increment)
        if up_to_date:
            log.info("Everything still up to date")
            return

        import_mission_metadata()
        for container, mission_path in missions_to_rebuild:
            rebuild_mission(container, mission_path)
            dump_mission(container, mission_path)
            set_uptodate_info(container, mission_path)
