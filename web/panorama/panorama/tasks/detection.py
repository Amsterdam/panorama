import csv
import logging
import io

from datasets.panoramas.models import Panoramas
from panorama.object_store import ObjectStore

log = logging.getLogger(__name__)


def save_region_csv(panorama: Panoramas, regions: list, suffix: str):
    """
    Save detected regions to the objectstore.

    :param panorama: panorama that has been sent for detection
    :param regions: regions, as the usual five-tuples
    :param suffix: file basename suffix
    """
    object_store = ObjectStore()
    as_csv = _region_csv(regions)

    csv_name = f"results/{panorama.path}{panorama.filename[:-4]}/regions_{suffix}.csv"
    log.warning("saving {}".format(csv_name))

    object_store.put_into_datapunt_store(csv_name, as_csv, "text/csv")


def _region_csv(regions) -> bytes:
    """Produce CSV of regions as a bytes."""
    out = io.StringIO()
    w = csv.writer(out)

    w.writerow(
        [
            "region_type",
            "left_top_x",
            "left_top_y",
            "right_top_x",
            "right_top_y",
            "right_bottom_x",
            "right_bottom_y",
            "left_bottom_x",
            "left_bottom_y",
            "detected_by",
        ]
    )
    for region in regions:
        left_top, right_top, right_bottom, left_bottom = region[0:4]
        detected_by = region[4]

        # The first column, region_type, was meant to contain either "N" for
        # license plates or "G" for faces, but due to a bug has always contained
        # "N". We now hardcode it to "N" always. Don't use this field; the type
        # of region can be derived from the filename suffix, "_lp" for license
        # plates and "_f*" for faces.
        w.writerow(
            [
                "N",
                left_top[0],
                left_top[1],
                right_top[0],
                right_top[1],
                right_bottom[0],
                right_bottom[1],
                left_bottom[0],
                left_bottom[1],
                detected_by,
            ]
        )

    return out.getvalue()
