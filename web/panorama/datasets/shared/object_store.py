import logging

from swiftclient.client import Connection
from django.conf import settings

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
log = logging.getLogger(__name__)


class ObjectStore():
    datapunt_conn = Connection(authurl=settings.AUTHURL,
                               user=settings.OBJECTSTORE_USER,
                               key=settings.OBJECTSTORE_PASSWORD,
                               tenant_name=settings.DATAPUNT_TENANT_NAME,
                               auth_version=settings.AUTH_VERSION,
                               os_options={'tenant_id': settings.DATAPUNT_TENANT_ID,
                                           'region_name': settings.REGION_NAME})
    panorama_conn = Connection(authurl=settings.AUTHURL,
                               user=settings.OBJECTSTORE_USER,
                               key=settings.OBJECTSTORE_PASSWORD,
                               tenant_name=settings.PANORAMA_TENANT_NAME,
                               auth_version=settings.AUTH_VERSION,
                               os_options={'tenant_id': settings.PANORAMA_TENANT_ID,
                                           'region_name': settings.REGION_NAME})

    def get_panorama_store_object(self, object_meta_data):
        return self.panorama_conn.get_object(object_meta_data['container'], object_meta_data['name'])[1]

    def get_panorama_store_objects(self, container, path):
        return self.panorama_conn.get_container(container, prefix=path)[1]

    def get_datapunt_store_objects(self, path):
        return self.datapunt_conn.get_container(settings.DATAPUNT_CONTAINER, prefix=path)[1]

    def get_csvs(self, csv_identifier):
        csvs = []
        for container in settings.PANORAMA_CONTAINERS:
            for month in self._get_subdirs(container, ''):
                for day in self._get_subdirs(container, month):
                    for trajectory in self._get_subdirs(container, day):
                        csvs.extend(self._get_csv_type(container, trajectory, csv_identifier))
        return csvs

    def _get_subdirs(self, container, path):
        _, objects_from_store = self.panorama_conn.get_container(container, delimiter='/', prefix=path)
        return [store_object['subdir'] for store_object in objects_from_store if 'subdir' in store_object]

    def _get_csv_type(self, container, path, csv_identifier):
        _, csvs = self.panorama_conn.get_container(container, delimiter='/', prefix=path+csv_identifier)
        for csv_object in csvs:
            csv_object['container'] = container
        return csvs

    def put_into_datapunt_store(self, object_name, object_content, content_type):
        self.datapunt_conn.put_object(settings.DATAPUNT_CONTAINER,
                                      object_name,
                                      contents=object_content,
                                      content_type=content_type)

