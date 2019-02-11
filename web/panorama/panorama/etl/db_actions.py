import io

from django.db import connection
# from django.db.models.functions import ExtractYear, ExtractMonth, ExtractDay, Substr

from datasets.panoramas.models import Panorama
from panorama.etl.check_objectstore import INCREMENTS_CONTAINER
from panorama.shared.object_store import ObjectStore

DUMP_FILENAME = "increment.dump"
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


def restore_data(container, mission_path):
    """Restores the panorama data of a mission from the objectstore:

        restore_data("2016", "03/30/TMX315120208-0000023/")

    will read the file 2016/03/30/TMX315120208-0000023/increment.dump into the database

    :param container: container (= year part of the path) to choose data from
    :param mission_path: mission path to dump
    :return: None
    """
    fields = [field.name for field in Panorama._meta.get_fields() if field.name != 'id']
    table_name = Panorama._meta.db_table

    copy_command = f"COPY {table_name} ({', '.join(fields)}) FROM  STDIN (FORMAT binary)"
    file = io.BytesIO(objectstore.get_panorama_store_object({'container': INCREMENTS_CONTAINER,
                                                             'name': f"{container}/{mission_path}{DUMP_FILENAME}"}))
    with connection.cursor() as cursor:
        cursor.copy_expert(copy_command, file)


# def write_increments():
#
#     nested_increments = [
#         {'year': ExtractYear('timestamp')},
#         {'month': ExtractMonth('timestamp')},
#         {'day': ExtractDay('timestamp')},
#         {'mission': Substr('pano_id', 1, 20)},
#     ]
#
#     for i in range(1, len(nested_increments)+1):
#         annotate = {k: v for item in nested_increments[0:i] for k, v in item.items()}
#         values = [k for item in nested_increments[0:i] for k, _ in item.items()]
#
#         queryset = Panorama.objects.annotate(**annotate).order_by(*values).values(*values).distinct()
#
#         for p in queryset:
#             nested_parts = [str(p[field]) for field in values]
#             filename = "_".join(nested_parts)
#             print(f"filename: {filename}.dump")
#
#             filters = {field: p[field] for field in values}
#             fields = [field.name for field in Panorama._meta.get_fields() if field.name != 'id']
#
#             dataset = Panorama.objects.annotate(**annotate).filter(**filters).values(*fields).all()
#
#             print(f"sql: {dataset.query}")
