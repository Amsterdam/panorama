import logging
from openalpr.openalpr import Alpr

OPENALPR_DATA = "/usr/share/openalpr/runtime_data"
OPENALPR_CONF = "/etc/openalpr/openalpr.conf"
LICENSEPLATE_REGION = "eu"

log = logging.getLogger(__name__)


class OpenAlprError(Exception):
     def __init__(self, value):
         self.value = value

     def __str__(self):
         return repr(self.value)


class OpenAlpr:
    alpr = None

    def __enter__(self):
        if not self.alpr:
            self.alpr = Alpr(LICENSEPLATE_REGION, OPENALPR_CONF, OPENALPR_DATA)
            if not self.alpr.is_loaded():
                raise OpenAlprError("Error loading OpenALPR")
            else:
                log.info("Using OpenALPR {}".format(self.alpr.get_version()))

        return self.alpr

    def __exit__(self, type, value, traceback):
        # Keep alive in this project, self.alpr.unload() also ends python process
        pass