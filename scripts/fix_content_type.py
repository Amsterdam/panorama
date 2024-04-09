# Sets the Content-Type for every .jpg in out Azure storage container to
# "image/jpeg".
#
# XXX This is slow. For large collections, run multiple instances concurrently.

from datetime import datetime
import os
import sys

from azure.storage.blob import BlobServiceClient, ContentSettings


try:
    prefix = sys.argv[1]
except IndexError:
    print(f"usage: {sys.argv[0]} prefix", file=sys.stderr)
    sys.exit(2)

connstr = os.getenv("AZURE_CONNECTION_STRING")
if connstr is None:
    print(f"{sys.argv[0]}: AZURE_CONNECTION_STRING not set", file=sys.stderr)
    sys.exit(3)

bsc = bsc = BlobServiceClient.from_connection_string(connstr)
cc = bsc.get_container_client("panorama")
cs = ContentSettings(content_type="image/jpeg")

changed = 0
for i, b in enumerate(cc.list_blobs(name_starts_with=prefix)):
    n = b["name"]
    if i % 1000 == 0:
        print(i, changed, datetime.now(), n)
    if not n.endswith(".jpg") or b["content_settings"]["content_type"] == "image/jpeg":
        continue

    bc = cc.get_blob_client(n)
    bc.set_http_headers(ContentSettings(content_type="image/jpeg"))
    changed += 1
