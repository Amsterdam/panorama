WIDTH = 8000
X, Y = 0, 1
LEFT_TOP, RIGHT_TOP, RIGHT_BOTTOM, LEFT_BOTTOM = 0, 1, 2, 3


def intersection(point_left, point_right, width):
    part_left = width - point_left[X]
    part_right = point_right[X] - width
    intersect_y = point_left[Y] + int((point_right[Y] - point_left[Y]) * part_left / (part_left + part_right))
    return width, intersect_y


def wrap_around(regions, width=WIDTH):
    split_regions = []
    for (lt, rt, rb, lb, _) in regions:
        coordinates = [lt, rt, rb, lb]
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


def do_split_regions(regions):
    split_regions = []
    for region in regions:
        for split_region in wrap_around([((region['left_top_x'], region['left_top_y']),
                                         (region['right_top_x'], region['right_top_y']),
                                         (region['right_bottom_x'], region['right_bottom_y']),
                                         (region['left_bottom_x'],region['left_bottom_y']), '')]):
            split_regions.append({
                'left_top_x': split_region[LEFT_TOP][X],
                'left_top_y': split_region[LEFT_TOP][Y],
                'right_top_x': split_region[RIGHT_TOP][X],
                'right_top_y': split_region[RIGHT_TOP][Y],
                'right_bottom_x': split_region[RIGHT_BOTTOM][X],
                'right_bottom_y': split_region[RIGHT_BOTTOM][Y],
                'left_bottom_x': split_region[LEFT_BOTTOM][X],
                'left_bottom_y': split_region[LEFT_BOTTOM][Y]
            })

    return split_regions


def get_rectangle(region_dict):
    top = min(region_dict['left_top_y'], region_dict['right_top_y'])
    left = min(region_dict['left_top_x'], region_dict['left_bottom_x'])
    bottom = max(region_dict['left_bottom_y'], region_dict['right_bottom_y'])
    right = max(region_dict['right_top_x'], region_dict['right_bottom_x'])

    return (top, left), (bottom, right)


