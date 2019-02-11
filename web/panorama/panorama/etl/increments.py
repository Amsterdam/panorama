import logging

from swiftclient import ClientException
import re

from panorama.etl.check_objectstore import is_increment_uptodate, increment_exists
from panorama.etl.db_actions import restore_increment, clear_database, dump_increment
from panorama.etl.etl_settings import DUMP_FILENAME, INCREMENTS_CONTAINER
from panorama.objectstore_settings import PANORAMA_CONTAINERS
from panorama.shared.object_store import ObjectStore

log = logging.getLogger(__name__)
objectstore = ObjectStore()


def _remove_stale_increment(container, path):
    """Remove an increment

        _remove_stale_increment('2015', '05/07')

    will remove the file: increments/2015/05/07/increment.dump from the objectstore

    :param container: the source container the increment is based on
    :param path: the path the increment is based on.
    :return: None
    """

    try:
        objectstore.panorama_conn.delete_object(INCREMENTS_CONTAINER, f"{container}/{path}{DUMP_FILENAME}")
    except ClientException:
        pass


def _is_mission(subdir):
    """Does the given subdir contain mission information (used to end recursion in `_check_and_process_recursively`

        _is_mission('05/07/') --> False
        _is_mission('05/07/TMX000002013-000030/' --> True

    :param subdir: the path of the subdir
    :return: True or False if the subdir is a mission dir or not
    """
    pattern = re.compile(r'\d\d/\d\d/\S\S\S\d\d\d\d\d\d\d\d\d\d\S\d\d\d\d\d\d/')
    return pattern.match(subdir)


def _check_and_process_recursively(source_container, path, increment, missions_to_rebuild):
    """Tests recursively if the directory is still up to date, recursion terminates when `_is_mission(subdir`
    returns True. Any mission-increment that is no longer up to date

    :param source_container: container to check: in panorama 'year'
    :param path: path to check recursively
    :param increment: restrict processing only to this increment
    :param missions_to_rebuild: a running List of missions that need to be rebuild
    :return: True if the subtree is still up date
    """

    log.info(f"Checking if path is still up to data: {source_container}/{path}")
    up_to_date = True
    subdirs = objectstore.get_subdirs(source_container, path)
    for subdir in subdirs:
        # process only if subdir is in parent/child tree of increment, if no increment is given process always
        do_process = increment is None or (f"{source_container}/{subdir}" in increment or
                                           increment in f"{source_container}/{subdir}")

        if do_process:
            # terminate at mission-dirs, or propagate recursion
            if _is_mission(subdir):
                log.info(f"Checking if path is still up to data: {source_container}/{subdir}")
                if not is_increment_uptodate(source_container, subdir):
                    _remove_stale_increment(source_container, subdir)
                    missions_to_rebuild.append((source_container, subdir))
                    up_to_date = False
                    log.info(f"    Not up to date: {source_container}/{subdir}")
            else:
                up_to_date = _check_and_process_recursively(source_container, subdir, increment,
                                                            missions_to_rebuild) and up_to_date

    if not up_to_date:
        log.info(f"    Not up to date: {source_container}/{path}")
        _remove_stale_increment(source_container, path)
    return up_to_date


def check_increments(increment=None):
    """Test all missions to see if the are still up to date, and if not, remove them recursively. Returning missions
    to (re)build

    :param increment: specific increment to check: `increment='2017/'`, or `increment='2017/04/'` etc.
    :return: tuple of Boolean (True if all increments where up to date, and False if any have been removed) and a List
    containing all missions to rebuild (a list of tuples consisting of container and mission directory
    """

    missions_to_rebuild = []
    up_to_dates = [_check_and_process_recursively(year, "", increment, missions_to_rebuild)
                   for year in PANORAMA_CONTAINERS]

    return all(up_to_dates), missions_to_rebuild


def rebuild_increments_recursively(path=""):
    """Re-construct the increments that have been deleted when checking for increments that were no longer up-to-date
    Assumes mission-level increments are present

    :return: None
    """

    subdirs = objectstore.get_subdirs(INCREMENTS_CONTAINER, path)

    for subdir in subdirs:
        if not increment_exists(subdir):
            rebuild_increments_recursively(subdir)

    clear_database()
    for subdir in subdirs:
        restore_increment(subdir)

    log.info(f"building increment in /{path}")
    dump_increment(path)
