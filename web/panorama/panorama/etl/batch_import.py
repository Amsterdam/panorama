import logging
import csv

from datasets.panoramas.models import Mission
from datasets.panoramas.v1.models import Panorama
from panorama.etl.data_to_model import process_mission_row, process_panorama_row
from panorama.etl.etl_settings import BATCH_SIZE
from panorama.shared.object_store import ObjectStore

log = logging.getLogger(__name__)
objectstore = ObjectStore()


def process_csv(csv_file, generate_model):
    """Method to split a csv_file in header and rows, and call the process_row method to generate objects.

    :param csv_file: the objectstore metadata info dict for the csv_file to process
    :param generate_model: a method to call back to, taking headers, row and the dict of csv_file info as arguments,
    and producing an object to persist
    :return: a list of objects per row in csv_file, as created by the process_row method
    """
    csv_binary = objectstore.get_panorama_store_object(csv_file)
    csv_file_iterator = iter(csv_binary.decode("utf-8").split('\n'))

    rows = csv.reader(csv_file_iterator,
                      delimiter='\t',
                      quotechar=None,
                      quoting=csv.QUOTE_NONE)

    # first row is headers
    headers = next(rows)

    # subsequent rows contain objects to generate models from, with the given method
    models = [generate_model(headers, row, csv_file) for row in rows]

    # return, removing None-values
    return filter(None, models)


def import_mission_metadata():
    """Get all missiegegevens.csv files and load the mission metadata into the database

    :return: None
    """
    for csv_file in objectstore.get_containerroot_csvs('missiegegevens'):
        log.info(f"READING missions: {csv_file['name']}")
        Mission.objects.bulk_create(
            process_csv(csv_file, process_mission_row),
            batch_size=BATCH_SIZE
        )


def rebuild_mission(container, mission_path):
    """Load the data associated with the given mission into the database

    :param mission: a tuple of container and mission_path to import
    :return: None
    """

    panorama_csvs = objectstore.get_csv_type(container, mission_path, "panorama")
    for csv_file in panorama_csvs:
        log.info(f"READING panoramas: {csv_file['name']}")
        Panorama.objects.bulk_create(
            process_csv(csv_file, process_panorama_row),
            batch_size=BATCH_SIZE
        )

    # trajectory_csvs = objectstore.get_csv_type(container, mission_path, "trajectory")
    # for csv_file in trajectory_csvs:
    #     log.info(f"READING trajectories: {csv_file['name']}")
    #     Trajectory.objects.bulk_create(
    #         process_csv(csv_file, process_trajectory_row),
    #         batch_size=BATCH_SIZE
    #     )
