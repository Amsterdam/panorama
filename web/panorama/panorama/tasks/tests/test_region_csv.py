from ..detection import _region_csv


def test_region_csv():
    input = [
        [
            (2510, 2079),
            (2546, 2079),
            (2546, 2115),
            (2510, 2115),
            "cascade=default, scaleFactor=1.29, neighbours=7, zoom=1.41, time=100002ms",
        ],
        [
            (2508, 2079),
            (2545, 2079),
            (2545, 2116),
            (2508, 2116),
            "cascade=alt, scaleFactor=1.22, neighbours=5, zoom=1.41, time=100002ms",
        ],
        [
            (2508, 2079),
            (2543, 2079),
            (2543, 2114),
            (2508, 2114),
            "cascade=alt2, scaleFactor=1.22, neighbours=5, zoom=1.41, time=100002ms",
        ],
        [
            (2500, 2075),
            (2542, 2075),
            (2542, 2117),
            (2500, 2117),
            "cascade=profile_flip_correct, scaleFactor=1.11, neighbours=5, zoom=1.41, time=100002ms",
        ],
        [
            (2508, 2078),
            (2544, 2078),
            (2544, 2114),
            (2508, 2114),
            "cascade=alt_tree, scaleFactor=1.025, neighbours=2, zoom=1.41, time=100002ms",
        ],
        [
            (2511, 2079),
            (2547, 2079),
            (2547, 2115),
            (2511, 2115),
            "cascade=default, scaleFactor=1.29, neighbours=7, zoom=1.41, time=100002ms",
        ],
        [
            (2510, 2079),
            (2544, 2079),
            (2544, 2113),
            (2510, 2113),
            "cascade=alt, scaleFactor=1.22, neighbours=5, zoom=1.41, time=100002ms",
        ],
        [
            (2509, 2079),
            (2543, 2079),
            (2543, 2113),
            (2509, 2113),
            "cascade=alt2, scaleFactor=1.22, neighbours=5, zoom=1.41, time=100002ms",
        ],
        [
            (2502, 2075),
            (2543, 2075),
            (2543, 2116),
            (2502, 2116),
            "cascade=profile_flip_correct, scaleFactor=1.11, neighbours=5, zoom=1.41, time=100002ms",
        ],
        [
            (6664, 2108),
            (6682, 2108),
            (6682, 2126),
            (6664, 2126),
            "cascade=dlib, scaleFactor=1, neighbours=>-0.05, zoom=2, time=42150ms",
        ],
        [
            (6662, 2107),
            (6681, 2107),
            (6681, 2126),
            (6662, 2126),
            "cascade=dlib, scaleFactor=1, neighbours=>-0.05, zoom=1.83, time=42150ms",
        ],
        [
            (2513, 2083),
            (2541, 2083),
            (2541, 2111),
            (2513, 2111),
            "cascade=dlib, scaleFactor=1, neighbours=>-0.05, zoom=1.83, time=42150ms",
        ],
        [
            (2511, 2083),
            (2541, 2083),
            (2541, 2113),
            (2511, 2113),
            "cascade=dlib, scaleFactor=1, neighbours=>-0.05, zoom=1.68, time=42150ms",
        ],
        [
            (6662, 2104),
            (6683, 2104),
            (6683, 2125),
            (6662, 2125),
            "cascade=dlib, scaleFactor=1, neighbours=>-0.05, zoom=1.68, time=42150ms",
        ],
        [
            (2513, 2082),
            (2540, 2082),
            (2540, 2109),
            (2513, 2109),
            "cascade=dlib, scaleFactor=1, neighbours=>-0.05, zoom=1.54, time=42150ms",
        ],
    ]

    expect = """region_type,left_top_x,left_top_y,right_top_x,right_top_y,right_bottom_x,right_bottom_y,left_bottom_x,left_bottom_y,detected_by
N,2510,2079,2546,2079,2546,2115,2510,2115,"cascade=default, scaleFactor=1.29, neighbours=7, zoom=1.41, time=100002ms"
N,2508,2079,2545,2079,2545,2116,2508,2116,"cascade=alt, scaleFactor=1.22, neighbours=5, zoom=1.41, time=100002ms"
N,2508,2079,2543,2079,2543,2114,2508,2114,"cascade=alt2, scaleFactor=1.22, neighbours=5, zoom=1.41, time=100002ms"
N,2500,2075,2542,2075,2542,2117,2500,2117,"cascade=profile_flip_correct, scaleFactor=1.11, neighbours=5, zoom=1.41, time=100002ms"
N,2508,2078,2544,2078,2544,2114,2508,2114,"cascade=alt_tree, scaleFactor=1.025, neighbours=2, zoom=1.41, time=100002ms"
N,2511,2079,2547,2079,2547,2115,2511,2115,"cascade=default, scaleFactor=1.29, neighbours=7, zoom=1.41, time=100002ms"
N,2510,2079,2544,2079,2544,2113,2510,2113,"cascade=alt, scaleFactor=1.22, neighbours=5, zoom=1.41, time=100002ms"
N,2509,2079,2543,2079,2543,2113,2509,2113,"cascade=alt2, scaleFactor=1.22, neighbours=5, zoom=1.41, time=100002ms"
N,2502,2075,2543,2075,2543,2116,2502,2116,"cascade=profile_flip_correct, scaleFactor=1.11, neighbours=5, zoom=1.41, time=100002ms"
N,6664,2108,6682,2108,6682,2126,6664,2126,"cascade=dlib, scaleFactor=1, neighbours=>-0.05, zoom=2, time=42150ms"
N,6662,2107,6681,2107,6681,2126,6662,2126,"cascade=dlib, scaleFactor=1, neighbours=>-0.05, zoom=1.83, time=42150ms"
N,2513,2083,2541,2083,2541,2111,2513,2111,"cascade=dlib, scaleFactor=1, neighbours=>-0.05, zoom=1.83, time=42150ms"
N,2511,2083,2541,2083,2541,2113,2511,2113,"cascade=dlib, scaleFactor=1, neighbours=>-0.05, zoom=1.68, time=42150ms"
N,6662,2104,6683,2104,6683,2125,6662,2125,"cascade=dlib, scaleFactor=1, neighbours=>-0.05, zoom=1.68, time=42150ms"
N,2513,2082,2540,2082,2540,2109,2513,2109,"cascade=dlib, scaleFactor=1, neighbours=>-0.05, zoom=1.54, time=42150ms"
"""

    # splitlines takes care of the LF/CRLF thingy.
    assert _region_csv(input).splitlines() == expect.splitlines()
