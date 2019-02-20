import logging
from swiftclient import ClientException

from datasets.panoramas.models import EQUIRECTANGULAR_SUBPATH, FULL_IMAGE_NAME
from panorama.etl.etl_settings import DUMP_FILENAME, SOURCE_LISTING_NAME, INTERMEDIATE_LISTING_NAME, BLURRED_LISTING_NAME, \
    INCREMENTS_CONTAINER, INTERMEDIATE_CONTAINER
from panorama.shared.object_store import ObjectStore

panorama_images = {}
panorama_rendered = {}
panorama_blurred = {}

log = logging.getLogger(__name__)
objectstore = ObjectStore()


def panorama_image_file_exists(container, path, filename):
    """Check if the panorama  exists in container and path, directory listing is cached

    :param container: the objectstore container to look in
    :param path: the path the filename is at
    :param filename: the filename of the panorama
    :return: True or False depending on if the file is found
    """
    global panorama_images

    key = f"{container}/{path}"

    if key not in panorama_images:
        file_entries_in_source_dir = objectstore.get_panorama_store_objects(container, path)
        panorama_images[key] = [file['name'] for file in file_entries_in_source_dir]

    return f"{path}/{filename}" in panorama_images[key]


def panorama_rendered_file_exists(container, path, filename):
    """Check if the rendered panorama exists in the intermediate container

    :param container: the objectstore container the source for the rendered file is in
    :param path: the path the source panorama
    :param filename: the filename of the source panorama
    :return: True or False depending on if the file is found
    """
    global panorama_rendered

    key = f"{container}/{path}"

    if key not in panorama_rendered:
        file_entries_in_renderdir = objectstore.get_panorama_store_objects(INTERMEDIATE_CONTAINER, key)
        panorama_rendered[key] = [file['name'] for file in file_entries_in_renderdir]

    return f"{key}/{filename}" in panorama_rendered[key]


def panorama_blurred_file_exists(container, path, filename):
    """Check if the blurred panorama exists in the datapunt public - facing container

    :param container:  the panorama objectstore container the source for the rendered file is in
    :param path: the path the source panorama
    :param filename: the filename of the source panorama
    :return: True or False depending on if the file is found
    """
    global panorama_blurred

    key = f"{container}/{path}"

    if key not in panorama_blurred:
        file_entries_in_target_dir = objectstore.get_datapunt_store_objects(key)
        panorama_blurred[key] = [file['name'] for file in file_entries_in_target_dir]

    blurred_image = f"{key}/{filename[:-4]}{EQUIRECTANGULAR_SUBPATH}{FULL_IMAGE_NAME}"
    return blurred_image in panorama_blurred[key]


def _objlist_to_dirlisting(obj_list):
    """Takes a list of Objectstore object metadata and converts it into a simple
    directory listing.

    :param obj_list: list of Objectstore objects
    :return: multiline string, containing names and lastmodified of each Objectstore object per line
    """

    entries = [f"{entry['name']} {entry['last_modified']}" for entry in obj_list]
    return "\n".join(entries)


def _readsafe_object(metadata):
    """Takes metadata of an Objectstore object, a dict containing container en name of the object, and returns the
    string representation of the object, or an empty string if the file doesn't exist

    :param metadata: Objectstore object metadata
    :return: string conaining the contents of the Objectstore object
    """

    try:
        return objectstore.get_panorama_store_object(metadata).decode("utf-8")
    except ClientException:
        return ""


def _object_listings_for(container, path):
    """Creates string representations of directory listing, for panorama sources, intermediate and blurred files

    :param container: source container (year)
    :param path: source path
    :return: a tuple, of `source_listing, intermediate_listing, blurred_listing`
    """
    source_obj_list = objectstore.get_panorama_store_objects(container, path)
    source_listing = _objlist_to_dirlisting(source_obj_list)

    intermediate_obj_list = objectstore.get_panorama_store_objects(INTERMEDIATE_CONTAINER, f"{container}/{path}")
    intermediate_listing = _objlist_to_dirlisting(intermediate_obj_list)

    blurred_obj_list = objectstore.get_datapunt_store_objects(f"{container}/{path}")
    blurred_listing = _objlist_to_dirlisting([obj for obj in blurred_obj_list if "panorama_8000.jpg" in obj['name']])

    return source_listing, intermediate_listing, blurred_listing


def set_uptodate_info(container, path):
    """Update the information on the processed path (so the next time, when nothing changes, the `is_increment_uptodate`
    method will return if nothing changes

    :param container: the container (year)
    :param path: source path (path to mission
    :return: None
    """
    source_listing, intermediate_listing, blurred_listing = _object_listings_for(container, path)

    objectstore.put_into_panorama_store(INCREMENTS_CONTAINER, f"{container}/{path}{SOURCE_LISTING_NAME}",
                                        source_listing, "text/plain")

    objectstore.put_into_panorama_store(INCREMENTS_CONTAINER, f"{container}/{path}{INTERMEDIATE_LISTING_NAME}",
                                        intermediate_listing, "text/plain")

    objectstore.put_into_panorama_store(INCREMENTS_CONTAINER, f"{container}/{path}{BLURRED_LISTING_NAME}",
                                        blurred_listing, "text/plain")


def increment_exists(increment_path):
    """Check if an increment is present at the given path

    :param increment_path: the path to check for existince of increment
    :return: True or False, depending on if the path contains an increment
    """
    dirlist = objectstore.get_panorama_store_objects(INCREMENTS_CONTAINER, f"{increment_path}")
    return f"{increment_path}{DUMP_FILENAME}" in [obj['name'] for obj in dirlist]


def is_increment_uptodate(container, path):
    """For the deepest level in the nested incremental setup to be declared unchanged both the
    directory listing of the source, as that of the intermediate image set need to be unchanged

    :param container: source container to check (in panoramas: year)
    :param path: path of the leaf to test for unchanged
    :return: True or False
    """

    source_listing, intermediate_listing, blurred_listing = _object_listings_for(container, path)

    metadata = {'container': INCREMENTS_CONTAINER, 'name': f"{container}/{path}{SOURCE_LISTING_NAME}"}
    stored_source = _readsafe_object(metadata)

    metadata = {'container': INCREMENTS_CONTAINER, 'name': f"{container}/{path}{INTERMEDIATE_LISTING_NAME}"}
    stored_intermediate = _readsafe_object(metadata)

    metadata = {'container': INCREMENTS_CONTAINER, 'name': f"{container}/{path}{BLURRED_LISTING_NAME}"}
    stored_blurred = _readsafe_object(metadata)

    return source_listing == stored_source and \
           intermediate_listing == stored_intermediate and \
           blurred_listing == stored_blurred and \
           increment_exists(f"{container}/{path}")
