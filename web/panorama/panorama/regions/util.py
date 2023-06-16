WIDTH = 8000
X, Y = 0, 1
LEFT_TOP, RIGHT_TOP, RIGHT_BOTTOM, LEFT_BOTTOM = 0, 1, 2, 3


def _intersection_height(point_left, point_right, width):
    """
    Given a point inside an image and a point to the right of it,
    return the height where the line segment between the two points
    crosses the border of the image.

    :param point_left: x, y coordinates for the point left of the border
    :param point_right: x, y coordinates for the point right of the border
    :param width: width of the image
    :return: y coordinate where the line from left to right intersects with the border
    """
    part_left = width - point_left[X]
    part_right = point_right[X] - width
    return point_left[Y] + int((point_right[Y] - point_left[Y]) * part_left / (part_left + part_right))


def wrap_around(regions, width=WIDTH):
    """
    Split regions that intersect with the border of the image into a region left to the
    right border, and right to the left border (all within image).

    :param regions: array of coordinate-sets (left-top, right-top, right-bottom, leftbottom, description)
    :param width: width of the image
    :return: set of split regions
    """
    split_regions = []
    for (lt, rt, rb, lb, _) in regions:
        coordinates = [lt, rt, rb, lb]

        if any(p[X] < 0 for p in coordinates):
            for idx, coordinate_set in enumerate(coordinates):
                coordinates[idx] = (coordinate_set[X] + width, coordinate_set[Y])

        if all(p[X] >= width for p in coordinates):
            for idx, coordinate_set in enumerate(coordinates):
                coordinates[idx] = (coordinate_set[X] - width, coordinate_set[Y])
            split_regions.append(coordinates)
        elif all(p[X] <= width for p in coordinates):
            split_regions.append(coordinates)
        else:
            points_left, points_right = [], []
            for idx, curr_coords in enumerate(coordinates):
                next_coords = coordinates[(idx+1) % len(coordinates)]

                if curr_coords[X] == width:
                    if idx == LEFT_TOP or idx == LEFT_BOTTOM:
                        points_left.append(curr_coords)
                    else:
                        points_right.append(curr_coords)
                    if next_coords[X] != width:
                        points_left.append(curr_coords)
                        points_right.append(curr_coords)
                elif curr_coords[X] < width:
                    points_left.append(curr_coords)
                    if next_coords[X] > width:
                        intersect_to = (width, _intersection_height(curr_coords, next_coords, width))
                        points_right.append(intersect_to)
                        if idx == RIGHT_TOP:
                            points_right.append(intersect_to)
                        else:
                            points_left.append(intersect_to)
                else:
                    points_right.append(curr_coords)
                    if next_coords[X] < width:
                        intersect_back = (width, _intersection_height(next_coords, curr_coords, width))
                        points_left.append(intersect_back)
                        if idx == LEFT_BOTTOM:
                            points_left.append(intersect_back)
                        else:
                            points_right.append(intersect_back)
            for idx, point in enumerate(points_right):
                points_right[idx] = (point[X] - width, point[Y])
            split_regions.extend([points_left, points_right])

    return split_regions
