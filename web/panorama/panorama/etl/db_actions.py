import io
import logging

from django.core.management.color import no_style
from django.db import connection
# from django.db.models.functions import ExtractYear, ExtractMonth, ExtractDay, Substr

from datasets.panoramas.v1.models import Panorama
from panorama.etl.etl_settings import DUMP_FILENAME, INCREMENTS_CONTAINER
from panorama.shared.object_store import ObjectStore

log = logging.getLogger(__name__)
objectstore = ObjectStore()


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
    mission_name = mission_path.split("/")[-2]

    mission_order_clause = " ORDER BY pano_id ASC"

    with connection.cursor() as cursor:
        # create the query, with proper escaping (mogrify returns bytes, decode to string):
        complete_query = cursor.mogrify(base_query+mission_where_clause+mission_order_clause, (mission_name,)).decode()
        # create the custom copy command
        copy_command = f"COPY ({complete_query}) TO STDOUT WITH (FORMAT binary)"

        outputstream = io.BytesIO()

        cursor.copy_expert(copy_command, outputstream)
        objectstore.put_into_panorama_store(INCREMENTS_CONTAINER,
                                            f"{container}/{mission_path}{DUMP_FILENAME}",
                                            outputstream.getvalue(),
                                            "binary/octet-stream")


def dump_increment(increment_path):
    """Dumps current dataset (no filters/where-clause) to the given path.

    :param increment_path: the path the dataset needs to be dumped to
    :return: None
    """

    fields = [field.name for field in Panorama._meta.get_fields() if field.name != 'id']
    table_name = Panorama._meta.db_table

    base_query = f"SELECT {', '.join(fields)} FROM {table_name}"
    order_clause = " ORDER BY pano_id ASC"

    with connection.cursor() as cursor:
        # create the custom copy command
        copy_command = f"COPY ({base_query+order_clause}) TO STDOUT WITH (FORMAT binary)"

        outputstream = io.BytesIO()

        cursor.copy_expert(copy_command, outputstream)
        objectstore.put_into_panorama_store(INCREMENTS_CONTAINER,
                                            f"{increment_path}{DUMP_FILENAME}",
                                            outputstream.getvalue(),
                                            "binary/octet-stream")


def restore_increment(increment_path):
    """Restores the panorama data of a mission from the objectstore:

        restore_data("2016/03/30/TMX315120208-0000023/")

    will read the file `2016/03/30/TMX315120208-0000023/increment.dump` into the database

    :param increment_path: increment path to restore
    :return: None
    """

    fields = [field.name for field in Panorama._meta.get_fields() if field.name != 'id']
    table_name = Panorama._meta.db_table

    copy_command = f"COPY {table_name} ({', '.join(fields)}) FROM  STDIN (FORMAT binary)"
    file = io.BytesIO(objectstore.get_panorama_store_object({'container': INCREMENTS_CONTAINER,
                                                             'name': f"{increment_path}{DUMP_FILENAME}"}))
    with connection.cursor() as cursor:
        cursor.copy_expert(copy_command, file)


def clear_database():
    """Clear the models from the database

    :return: None
    """
    Panorama.objects.all().delete()


def reset_sequences():
    """Reset the sequence, so that after restore of the root increment, the id's start with 1

    :return: None
    """
    sequence_sql = connection.ops.sequence_reset_sql(no_style(), [Panorama])
    with connection.cursor() as cursor:
        for sql in sequence_sql:
            cursor.execute(sql)


def restore_all():
    """Rebuild the complete database from the root increment

    :return: None
    """
    clear_database()
    reset_sequences()

    # restore root increment:
    restore_increment("")
