import os

# OBJECT_STORE SETTINGS

OBJECTSTORE_USER = os.getenv('OBJECTSTORE_USER', 'datapunt')
OBJECTSTORE_PASSWORD = os.getenv('OBJECTSTORE_PASSWORD', 'insecure')

AUTH_VERSION = '2.0'
AUTHURL = 'https://identity.stack.cloudvps.com/v2.0'

DATAPUNT_TENANT_NAME = 'BGE000081 Datapunt'
DATAPUNT_TENANT_ID = 'ffb7a5a57dd34cc49436abc510cad162'
PANORAMA_TENANT_NAME = 'BGE000081 Panorama'
PANORAMA_TENANT_ID = '3206eec333a04cc980799f75a593505a'

#   wait for new years to be uploaded:
#   when enabling this also views should be changed
#   in such a way that the only show Panoramas with status done
#   See taiga #599 API methods: alleen teurggeven geblurde panorama's (ook bij adjecencies)
#   replacing Panorama.objects. with Panorama.done. should do a lot. Maybe extra query shizzle is neede.
# PANORAMA_CONTAINERS = ['2016', '2017']
PANORAMA_CONTAINERS = ['2016']

DATAPUNT_CONTAINER = 'panorama'

REGION_NAME = 'NL'
