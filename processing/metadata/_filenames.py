import os.path


def strip_filename(path: str) -> str:
    """Extracts the important parts of a panorama filename.

    The input path should be the (relative or absolute) path to an input
    panorama, ending in <year>/<month>/<day>/<mission>/<filename>. The return
    value is that part of the filename with ".jpg" stripped off, so that it
    can be used as the directory name for the output of our processing pipeline.

    >>> strip_filename("foo/bar/2023/01/12/TMX7316010203-002929/pano_0001_000025.jpg")
    '2023/01/12/TMX7316010203-002929/pano_0001_000025'

    Paths are validated:

    >>> strip_filename("foo/bar/2023/01/12/TMX7316010203-002929/pano_0001_000025")
    Traceback (most recent call last):
    ValueError: expected a filename ending in .jpg, got 'foo/bar/2023/01/12/TMX7316010203-002929/pano_0001_000025'
    >>> strip_filename("TMX7316010203-002929/pano_0001_000025.jpg")
    Traceback (most recent call last):
    ValueError: unexpected path 'TMX7316010203-002929/pano_0001_000025.jpg'
    """
    dirname, filename = os.path.split(path)
    filename, jpg = os.path.splitext(filename)
    if jpg.lower() != ".jpg":
        raise ValueError(f"expected a filename ending in .jpg, got {path!r}")

    dirname, mission = os.path.split(dirname)
    dirname, day = os.path.split(dirname)
    dirname, month = os.path.split(dirname)
    dirname, year = os.path.split(dirname)
    if not all([day, dirname, filename, month, mission, year]):
        raise ValueError(f"unexpected path {path!r}")

    return os.path.join(year, month, day, mission, filename)
