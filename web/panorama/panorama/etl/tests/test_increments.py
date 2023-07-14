from panorama.etl.increments import _is_mission


def test_is_mission():
    assert _is_mission("05/07/TMX7316010203-002369/")
    assert not _is_mission("05/07/")
    assert not _is_mission("05/07/TMX7316010203-002369")
