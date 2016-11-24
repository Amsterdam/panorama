WIDTH = 8000
X, Y = 0, 1


def intersection(point_left, point_right, width):
    part_left = width - point_left[X]
    part_right = point_right[X] - width
    intersect_y = point_left[Y] + int((point_right[Y] - point_left[Y]) * part_left / (part_left + part_right))
    return (width, intersect_y)


def wrap_around(regions, width=WIDTH):
    split_regions = []
    for (lt, rt, rb, lb, _) in regions:
        coordinates = [lt, rt, rb, lb]
        if all(p[X] >= width for p in coordinates):
            for idx, coordinate_set in enumerate(coordinates):
                coordinates[idx] = (coordinate_set[X] - width, coordinate_set[Y])

        if all(p[0] < width for p in coordinates):
            split_regions.append(coordinates)
        else:
            points_left, points_right = [], []
            for idx, _ in enumerate(coordinates):
                curr_coords = coordinates[idx]
                next_coords = coordinates[(idx+1) % len(coordinates)]

                if curr_coords[X] < width:
                    points_left.append(curr_coords)
                    if next_coords[X] >= width:
                        intersect_to = intersection(curr_coords, next_coords, width)
                        points_left.append(intersect_to)
                        points_right.append(intersect_to)
                else:
                    points_right.append(curr_coords)
                    if next_coords[X] < width:
                        intersect_back = intersection(next_coords, curr_coords, width)
                        points_left.append(intersect_back)
                        points_right.append(intersect_back)

            for idx, point in enumerate(points_right):
                points_right[idx] = (point[X] - width, point[Y])
            split_regions.extend([points_left, points_right])

    return split_regions
