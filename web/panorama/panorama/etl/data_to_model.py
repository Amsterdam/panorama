from datetime import datetime
import logging

from django.contrib.gis.geos import Point

from datasets.panoramas.models import Mission, Panorama
from panorama.etl.check_objectstore import panorama_image_file_exists, panorama_blurred_file_exists, \
    panorama_rendered_file_exists
from panorama.etl.date_util import _convert_gps_time

EMPTY_FALLBACK_YEAR = 2000
log = logging.getLogger(__name__)


def process_mission_row(headers, row, _):
    """Process a row of a csv into a Mission model
    
    :param headers: a List containing the header-data
    :param row: a List containing data entries for an instance of Mission
    :param _: ignored csv_file info
    :return: None if no data was given, otherwise a hydrated instance of Mission model
    """
    if not row:
        return None

    data = dict(zip(headers, row))

    date_format = '%d-%m-%Y'
    mission_date = datetime.strptime(data['datum'], date_format).date()
    mission_year = data['woz-jaargang'] if 'woz-jaargang' in data else None
    if mission_year is None or mission_year is "":
        mission_year = mission_date.year

    return Mission(
        name=data['Missienaam'],
        surface_type=data['water/land'][:1].upper(),
        mission_distance=data['rijafstand'],
        mission_type=data['missietype'],
        mission_year=mission_year,
        date=mission_date,
        neighbourhood=data['Gebied']
    )


def _create_panorama_tags(mission, mission_year):
    """Create (Amsterdam-specific) tags based on the (Amsterdam-specific :-) mission metadata

    :param mission: the Mission object
    :param mission_year: the mission-year (might be different from mission.year
    :return: a List of tags
    """
    tags = []

    if mission.mission_type:
        tags.append('mission-'+mission.mission_type)

    tags.append('mission-'+str(mission_year))

    if mission.surface_type == 'L':
        tags.append('surface-land')
    elif mission.surface_type == 'W':
        tags.append('surface-water')

    if mission.mission_distance:
        tags.append('mission-distance-'+str(mission.mission_distance))

    return tags


def _get_mission(filename):
    """Gets the mission that contains the metadata for the panorama

    :param filename: location of the panorama, mission_name is part of the path to the panorama
    :return: a persisted Mission, or a transcient dummy Mission, if none is found for the mission_name
    """
    mission_name = filename.split('/')[-2]
    try:
        return Mission.objects.filter(name=mission_name)[0]
    except IndexError:
        log.error(f"Mission {mission_name} does not exist, using dummy mission")
        return Mission(
            name=mission_name,
            surface_type='L',
            mission_type='bi',
            mission_distance=5,
            date="2015-1-1",
            neighbourhood='AUTOMATICALLY CREATED',
            mission_year=EMPTY_FALLBACK_YEAR
        )


def process_panorama_row(headers, row, csv_file):
    """Process a single row in the panorama photos metadata csv

    :param headers: a List containing the header-data
    :param row: a List containing data entries for an instance of Panorama
    :param csv_file: csv_file info (used to guess mission_name)
    :return: None if instance cannot be constructed, otherwise a hydrated instance of Panorama model
    """
    if not row:
        return None

    data = dict(zip(headers, row))

    mission = _get_mission(csv_file['name'])

    container = csv_file['container']
    path = "/".join(csv_file['name'].split("/")[:-1])

    try:
        base_filename = data['panorama_file_name']
    except KeyError:
        return None

    filename = f"{base_filename}.jpg"

    # check if panorama file exists
    if not panorama_image_file_exists(container, path, filename):
        log.error(f"MISSING Panorama: {container}/{path}/{filename}")
        return None

    # determine panorama_status based on presence of images
    panorama_status = Panorama.STATUS.to_be_rendered
    if panorama_blurred_file_exists(container, path, filename):
        panorama_status = Panorama.STATUS.done
    elif panorama_rendered_file_exists(container, path, filename):
        panorama_status = Panorama.STATUS.rendered

    # Creating unique id from mission name and base filename
    pano_id = f"{mission.name}_{base_filename}"

    pano_timestamp = _convert_gps_time(data['gps_seconds[s]'])
    mission_year = pano_timestamp.year if mission.mission_year == EMPTY_FALLBACK_YEAR else mission.mission_year
    tags = _create_panorama_tags(mission, mission_year)

    return Panorama(
        pano_id=pano_id,
        status=panorama_status,
        timestamp=pano_timestamp,
        filename=filename,
        path=f"{container}/{path}",
        mission_type=mission.mission_type,
        surface_type=mission.surface_type,
        mission_year=mission_year,
        mission_distance=mission.mission_distance,
        tags=tags,
        geolocation=Point(
            float(data['longitude[deg]']),
            float(data['latitude[deg]']),
            float(data['altitude_ellipsoidal[m]'])
        ),
        roll=float(data['roll[deg]']),
        pitch=float(data['pitch[deg]']),
        heading=float(data['heading[deg]']),
    )
