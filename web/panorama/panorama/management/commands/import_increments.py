import logging
import os
import re
import sys

from django.core.management import BaseCommand

from datasets.panoramas.models import Panoramas
from panorama.etl.batch_import import rebuild_mission, import_mission_metadata
from panorama.etl.check_objectstore import set_uptodate_info
from panorama.etl.db_actions import dump_mission, restore_all
from panorama.etl.increments import check_increments, rebuild_increments_recursively

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """Command to work with incremental updates.

        manage.py import_increments

    Default behaviour, scan all increments for changes and presence, (re)build new, missing or out of date increments
    and do a full rebuild of the database.

        manage.py import_increments -r

    This will rebuild all increments, including existing and up-to-date ones. And then do a full rebuild of the database

        manage.py import_increments --increment /2016/03

    This will scan only increments in /2016/03 and only rebuild increments in this tree if they are missing or out of
    date. Because this doesn't check other increments, the database is not fully rebuilt, and exit code will be <> 0
    to make sure the database isn't used.

        manage.py import_increments -f --increment /2016/03

    As above, but at the end the database is fully rebuilt, if successful exit code will be 0. This depends on other
    increments being present and up to date. Because default behaviour without increment is a full rebuild of the
    database anyway, the flag `-f` only makes sense in combination with an increment.

    Example use (in 2019):

        manage.py import_increments --increment /2016/
        manage.py import_increments --increment /2017/
        manage.py import_increments --increment /2018/

    This will make sure every historical increment is built and saved. After that one can perform a daily run of:

        manage.py import_increments -f --increment /2019/

    Every new dataset in 2019 will be automatically checked and increments will be made for that, and the database
    will be built from historical increments and new increments.

    If a historical mission has been added, or historical data has been changed, the increments can be (re)built:

        manage.py import_increments --increment /2018/06/08/TMX612010203-000782/

    this will also propagate changes to increments /2018/06/08, /2018/06/, /2018 and the root-increment (basically the
    complete dataset).

    If the data-model has been changed, voiding all increments (in 2019):

        manage.py import_increments -r --increment /2016/
        manage.py import_increments -r --increment /2017/
        manage.py import_increments -r --increment /2018/
        manage.py import_increments -r --increment /2018/
        manage.py import_increments -rf --increment /2019/

    """

    def add_arguments(self, parser):
        parser.add_argument('--increment', type=str, help="Builds increment to import (examples: '2016', '2016/01/', "
                                                          "'2017/02/03/' or even '2017/05/04/TMX000321015-000030/). "
                                                          "Will abort full restore - because it doesn't check other "
                                                          "increments for existence or up-to-date-ness. \n"
                                                          "REMARK: this will lead to an incomplete database. and an "
                                                          "exit code <> 0, so that integration and CI/CD don't mistake "
                                                          "the result as a usable database. This behaviour can be "
                                                          "overriden by adding the `-f` flag. Caveat: if other "
                                                          "increments are missing or out of date, this will lead to an "
                                                          "incomplete or out of date database")
        parser.add_argument('-r', action='store_true', help="Re-build. Always rebuild increments even if they are "
                                                            "up to date.")
        parser.add_argument('-f', action='store_true', help="Force import. Use in combination with "
                                                            "`--increment INCREMENT` to do a full import. TAKE CARE! "
                                                            "This will leave the database incomplete/out of "
                                                            "date if any increment outside the given increment is "
                                                            "missing or out of date.")

    @staticmethod
    def _check_increment_arg(increment):
        if increment is None:
            return

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

    @staticmethod
    def _set_env_for_swarm_start():
        to_process_count = Panoramas.objects.count() - Panoramas.done.count()
        if to_process_count > 2000:
            os.environ["START_SWARM"] = "1"
            os.environ["PANOS_TO_PROCESS"] = str(to_process_count)

    def handle(self, *args, **options):
        force_rebuild = options['r']
        force_import = options['f']
        increment = self._check_increment_arg(options['increment']) if 'increment' in options else None

        _, missions_to_rebuild = check_increments(increment=increment, force_rebuild=force_rebuild)

        import_mission_metadata()
        for container, mission_path in missions_to_rebuild:
            rebuild_mission(container, mission_path)
            dump_mission(container, mission_path)
            set_uptodate_info(container, mission_path)

        rebuild_increments_recursively()
        if increment is None or force_import:
            restore_all()
            self._set_env_for_swarm_start()
        else:
            # make sure exit is not treated as a signal that the database is usable.
            sys.exit(42)
