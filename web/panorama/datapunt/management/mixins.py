import logging
import time

from django.db import connection

log = logging.getLogger(__name__)


class _wait_for_panorama_table:
    def __enter__(self):
        while True:
            log.warn("waiting for panoramas table...")
            time.sleep(10)
            if self.is_panorama_table_present is True:
                log.warn("done... waiting for panoramas table")
                break

    def __exit__(self, type, value, traceback):
        pass

    @property
    def is_panorama_table_present(self):
        try:
            with connection.cursor() as cursor:
                cursor.execute("select * from information_schema.tables where table_name=%s", ('panoramas_panorama',))
                return bool(cursor.rowcount)
        except Exception as e:
            log.error(e)
        return False


class PanoramaTableAware:
    def panorama_table_present(self):
        return _wait_for_panorama_table()

