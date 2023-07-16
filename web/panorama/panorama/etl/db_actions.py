import io
import logging

from django.core.management.color import no_style
from django.db import connection

from datasets.panoramas.models import Panorama
import panorama.objectstore_settings as settings
from panorama.etl.etl_settings import DUMP_FILENAME, INCREMENTS_CONTAINER
from panorama.object_store import ObjectStore

log = logging.getLogger(__name__)
objectstore = ObjectStore()


def _dump(filename, query, parameters=None):
    """Dumps the contents of the query, with parameters, in the objectstore

    :param filename: target filename
    :param query: query to output
    :param parameters: parameters that will be substituted in the query
    :return: None
    """
    output_stream = io.BytesIO()
    with connection.cursor() as cursor:
        # cursor.mogrify encodes parameters and outputs byte-array
        query_bytes = cursor.mogrify(query) if parameters is None else cursor.mogrify(query, parameters)
        copy_command = f"COPY ({query_bytes.decode()}) TO STDOUT"
        cursor.copy_expert(copy_command, output_stream)
    output_stream.seek(0)
    log.info(f"Writing DB dump: {INCREMENTS_CONTAINER}/{filename}")
    objectstore.put_into_panorama_store(
        INCREMENTS_CONTAINER, filename, output_stream, "binary/octet-stream", chunk_size=10_485_760)


def dump_mission(container, mission_path):
    """Dumps the panorama data of a mission to the objectstore:

        dump_mission("2016", "03/30/TMX315120208-0000023/")

    will create the file 2016/03/30/TMX315120208-0000023/increment.dump in the container 'increments'

    :param container: container (= year part of the path) to dump data from
    :param mission_path: mission path to dump
    :return: None
    """

    fields = [field.name for field in Panorama._meta.get_fields() if field.name != 'id']
    table_name = Panorama._meta.db_table

    base_query = f"SELECT {', '.join(fields)} FROM {table_name}"
    mission_where_clause = " WHERE SUBSTRING(pano_id from 1 for 20) = %s"
    mission_order_clause = " ORDER BY pano_id ASC"
    full_query = base_query+mission_where_clause+mission_order_clause

    mission_name = mission_path.split("/")[-2]
    filename = f"{container}/{mission_path}{DUMP_FILENAME}"

    _dump(filename, full_query, (mission_name,))


def dump_increment(increment_path):
    """Dumps current dataset (no filters/where-clause) to the given path.

    :param increment_path: the path the dataset needs to be dumped to
    :return: None
    """

    fields = [field.name for field in Panorama._meta.get_fields() if field.name != 'id']
    table_name = Panorama._meta.db_table

    query = f"SELECT {', '.join(fields)} FROM {table_name} ORDER BY pano_id ASC"
    filename = f"{increment_path}{DUMP_FILENAME}"

    _dump(filename, query)


def restore_increment(increment_path):
    """Restores the panorama data of a mission from the objectstore:

        restore_data("2016/03/30/TMX315120208-0000023/")

    will read the file `2016/03/30/TMX315120208-0000023/increment.dump` into the database

    :param increment_path: increment path to restore
    :return: None
    """

    fields = [field.name for field in Panorama._meta.get_fields() if field.name != 'id']
    table_name = Panorama._meta.db_table

    copy_command = f"COPY {table_name} ({', '.join(fields)}) FROM STDIN"
    log.info(f"Restoring from {INCREMENTS_CONTAINER}/{increment_path}{DUMP_FILENAME}")
    file = io.BytesIO(objectstore.get_panorama_store_object({'container': INCREMENTS_CONTAINER,
                                                             'name': f"{increment_path}{DUMP_FILENAME}"}))
    with connection.cursor() as cursor:
        cursor.copy_expert(copy_command, file)


def clear_database(model_list):
    """Clear the models from the database.

    :return: None
    """
    for model in model_list:
        model.objects.all().delete()


def reset_sequences(model_list):
    """Reset the sequence, so that after restore of the root increment, the id's start with 1

    :return: None
    """
    log.info("Resetting DB sequences")
    sequence_sql = connection.ops.sequence_reset_sql(no_style(), model_list)
    with connection.cursor() as cursor:
        for sql in sequence_sql:
            cursor.execute(sql)


def restore_all():
    """Rebuild the complete database from the root increment

    :return: None
    """
    log.info("Clearing database (panoramas_panorama table)")
    clear_database([Panorama])
    reset_sequences([Panorama])

    # restore root increment:
    log.info(f"Rebuilding database from root increment as user {settings.PANORAMA_OBJECTSTORE_USER}")
    restore_increment("")
