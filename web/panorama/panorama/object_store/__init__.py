import logging
from swiftclient import client
from swiftclient.exceptions import ClientException
import panorama.objectstore_settings as settings

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("swiftclient").setLevel(logging.WARNING)

log = logging.getLogger(__name__)


class ObjectStore:
    RESP_LIMIT = 10000  # serverside limit of the response
    datapunt_conn = None
    panorama_conn = None

    def __init__(self):
        base_options = {'region_name': settings.REGION_NAME}
        if settings.RUNNING_OS_INTERNALLY:
            base_options['endpoint_type'] = 'internalURL'

        self.datapunt_conn = client.Connection(authurl=settings.AUTHURL,
                                               user=settings.DATAPUNT_OBJECTSTORE_USER,
                                               key=settings.DATAPUNT_OBJECTSTORE_PASSWORD,
                                               tenant_name=settings.DATAPUNT_TENANT_NAME,
                                               auth_version=settings.AUTH_VERSION,
                                               os_options={'tenant_id': settings.DATAPUNT_TENANT_ID, **base_options})
        self.panorama_conn = client.Connection(authurl=settings.AUTHURL,
                                               user=settings.PANORAMA_OBJECTSTORE_USER,
                                               key=settings.PANORAMA_OBJECTSTORE_PASSWORD,
                                               tenant_name=settings.PANORAMA_TENANT_NAME,
                                               auth_version=settings.AUTH_VERSION,
                                               os_options={'tenant_id': settings.PANORAMA_TENANT_ID, **base_options})

    def get_panorama_store_object(self, object_meta_data):
        try:
            return self.panorama_conn.get_object(
                object_meta_data['container'], object_meta_data['name'])[1]
        except ClientException as exc:
            log.error(exc)
            log.error(
                'User: %s (%s)', settings.PANORAMA_OBJECTSTORE_USER, settings.PANORAMA_TENANT_NAME)
            raise

    def get_panorama_store_objects(self, container, path):
        return self._get_full_container_list(self.panorama_conn, container, [], prefix=path)

    def get_datapunt_store_objects(self, path):
        return self._get_full_container_list(self.datapunt_conn, settings.DATAPUNT_CONTAINER, [], prefix=path)

    def get_datapunt_store_object(self, path):
        return self.datapunt_conn.get_object(settings.DATAPUNT_CONTAINER, path)[1]

    def _get_full_container_list(self, conn, container, seed, **kwargs):
        kwargs['limit'] = self.RESP_LIMIT
        if len(seed):
            if 'subdir' in seed[1]:
                kwargs['marker'] = seed[-1]['subdir']
            else:
                kwargs['marker'] = seed[-1]['name']

        try:
            _, page = conn.get_container(container, **kwargs)
        except ClientException as exc:
            log.error(exc)
            log.error('container: %s', container)
            raise
        seed.extend(page)
        return seed if len(page) < self.RESP_LIMIT else \
               self._get_full_container_list(conn, container, seed, **kwargs)

    def get_csvs(self, csv_identifier):
        csvs = []
        for container in settings.PANORAMA_CONTAINERS:
            for month in self.get_subdirs(container, ''):
                for day in self.get_subdirs(container, month):
                    for trajectory in self.get_subdirs(container, day):
                        csvs.extend(self.get_csv_type(container, trajectory, csv_identifier))
        return csvs

    def get_subdirs(self, container, path):
        objects_from_store = self._get_full_container_list(self.panorama_conn,
                                                           container,
                                                           [],
                                                           delimiter='/',
                                                           prefix=path)
        return [store_object['subdir'] for store_object in objects_from_store if 'subdir' in store_object]

    def get_detection_csvs(self, day):
        csvs = []
        log.info('day: %s', day)
        for trajectory in self.get_datapunt_subdirs(day):
            for panorama in self.get_datapunt_subdirs(trajectory):
                csvs.extend(self._get_datapunt_csv_type(panorama, 'region'))
        return csvs

    def get_datapunt_subdirs(self, path):
        objects_from_store = self._get_full_container_list(self.datapunt_conn,
                                                           settings.DATAPUNT_CONTAINER,
                                                           [],
                                                           delimiter='/',
                                                           prefix=path)
        return [store_object['subdir'] for store_object in objects_from_store if 'subdir' in store_object]

    def get_csv_type(self, container, path, csv_identifier):
        csvs = self._get_full_container_list(self.panorama_conn,
                                             container,
                                             [],
                                             delimiter='/',
                                             prefix=path+csv_identifier)
        for csv_object in csvs:
            csv_object['container'] = container
        return csvs

    def _get_datapunt_csv_type(self, path, csv_identifier):
        csvs = self._get_full_container_list(self.datapunt_conn,
                                             settings.DATAPUNT_CONTAINER,
                                             [],
                                             delimiter='/',
                                             prefix=path+csv_identifier)
        return csvs

    def put_into_datapunt_store(self, object_name, object_content, content_type):
        try:
            self.datapunt_conn.put_object(settings.DATAPUNT_CONTAINER,
                                        object_name,
                                        contents=object_content,
                                        content_type=content_type)
        except ClientException as exc:
            log.error(exc)
            log.error(
                'User: %s (%s)', settings.DATAPUNT_OBJECTSTORE_USER, settings.DATAPUNT_TENANT_NAME)
            raise

    def put_into_panorama_store(self, container, object_name, object_content, content_type, chunk_size=None):
        try:
            response_dict = {}
            self.panorama_conn.put_object(container,
                                        object_name,
                                        contents=object_content,
                                        content_type=content_type,
                                        chunk_size=chunk_size,
                                        response_dict=response_dict)
        except ClientException as exc:
            log.error(exc)
            log.error(
                'User: %s (%s)', settings.PANORAMA_OBJECTSTORE_USER, settings.PANORAMA_TENANT_NAME)
            for key, value in response_dict.items():
                log.error(f"{key}: {value}")
            raise
        except (ConnectionError, OSError) as exc:
            log.error(exc)
            raise

    def get_containerroot_csvs(self, csv_identifier):
        csvs = []
        for container in settings.PANORAMA_CONTAINERS:
            csvs.extend(self.get_csv_type(container, '', csv_identifier))
        return csvs
