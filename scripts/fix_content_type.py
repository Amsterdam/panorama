# Sets the Content-Type for every .jpg in out Azure storage container to
# "image/jpeg".
#
# XXX This is slow. For large collections, run multiple instances concurrently.

import asyncio
from datetime import datetime
import os
import sys

from azure.storage.blob import ContentSettings
from azure.storage.blob.aio import BlobServiceClient


try:
    prefix = sys.argv[1]
except IndexError:
    print(f"usage: {sys.argv[0]} prefix", file=sys.stderr)
    sys.exit(2)

connstr = os.getenv("AZURE_CONNECTION_STRING")
if connstr is None:
    print(f"{sys.argv[0]}: AZURE_CONNECTION_STRING not set", file=sys.stderr)
    sys.exit(3)


cs = ContentSettings(content_type="image/jpeg")


async def main():
    async with BlobServiceClient.from_connection_string(connstr) as bsc:
        cc = bsc.get_container_client("panorama")

        changed, i = 0, 0
        async for page in cc.list_blobs(name_starts_with=prefix).by_page():
            tasks = []
            async for b in page:
                i += 1
                n = b["name"]
                if (
                    not n.endswith(".jpg")
                    or b["content_settings"]["content_type"] == "image/jpeg"
                ):
                    continue

                bc = cc.get_blob_client(n)
                tasks.append(bc.set_http_headers(cs))

            await asyncio.gather(*tasks)
            changed += len(tasks)
            print(prefix, i, changed, datetime.now())
            continue


asyncio.run(main())
