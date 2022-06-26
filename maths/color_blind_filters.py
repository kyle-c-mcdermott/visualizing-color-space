"""
Functions for Analyzing and Filtering Images to eliminate chromatic variation
along confusion lines for a selected cone type.
"""

# region (Ensuring Access to Directories and Modules)
"""
If the script is not run from the project folder (highest level in repository),
but instead (presumably) from the folder containing this script, the current
working directory is moved up until a known sub-folder name is visible.
"""
from os import walk, chdir, getcwd
from os.path import dirname
folders = list()
while True:
    for root, dirs, files in walk('.'):
        folders += list(name for name in dirs)
    if 'maths' not in folders:
        chdir(dirname(getcwd())) # Move up one
    else:
        break
"""
Adding the (now updated) current working directory to the path so that imports
from the repository will work.
"""
from sys import path; path.append('.')
# endregion

# region Imports
from maths.rgb_cie_conversions import (
    rgb_to_chromoluminance,
    chromoluminance_to_rgb
)
from numpy import arctan2, pi, cos, sin
from PIL import Image
from typing import Dict, Tuple
from maths.color_blindness import intersection_two_segments
from scipy.optimize import fminbound
# endregion

# region Constants
CONE_TYPES = ['L', 'M', 'S']
COPUNCTAL_POINTS = {
    'L' : (0.746, 0.254),
    'M' : (1.400, -0.400),
    'S' : (0.175, 0.000)
}
# endregion

# region Get Gamut Triangle Edge Segments
gamut_segments = [
    (
        rgb_to_chromoluminance(1.0, 0.0, 0.0)[0:2], # Red
        rgb_to_chromoluminance(0.0, 1.0, 0.0)[0:2] # to Green
    ),
    (
        rgb_to_chromoluminance(0.0, 1.0, 0.0)[0:2], # Green
        rgb_to_chromoluminance(0.0, 0.0, 1.0)[0:2] # to Blue
    ),
    (
        rgb_to_chromoluminance(1.0, 0.0, 0.0)[0:2], # to Red
        rgb_to_chromoluminance(0.0, 0.0, 1.0)[0:2] # Blue
    )
]
# endregion

# region Estimate Angle Limits for Confusion Lines Passing through Gamut Edges
angle_limits = dict()
for cone_type in CONE_TYPES:
    angle_limits[cone_type] = list()
    for gamut_edge_index in range(3):
        angles = (
            arctan2(
                gamut_segments[gamut_edge_index][index][1] - COPUNCTAL_POINTS[cone_type][1], # delta-y
                gamut_segments[gamut_edge_index][index][0] - COPUNCTAL_POINTS[cone_type][0] # delta-x
            ) - pi / 2.0
            for index in range(2)
        )
        angles = list(
            angle
            if -pi <= angle <= pi
            else angle + 2.0 * pi
            for angle in angles
        )
        angle_limits[cone_type].append(sorted(angles))
# endregion

# region Function - Get Unique Colors from Image
def get_unique_colors(
    image : Image.Image
) -> Dict[Tuple[int, int, int], int]: # {(red, green, blue) : count}

    # Validate Argument
    assert isinstance(image, Image.Image)

    # Generate Dictionary of Unique 8-bit RGB Values with Counts (ignore alpha if present)
    pixels = image.load()
    uniques_count = dict()
    for col in range(image.width):
        for row in range(image.height):
            if pixels[col, row][0:3] not in uniques_count:
                uniques_count[pixels[col, row][0:3]] = 0
            uniques_count[pixels[col, row][0:3]] += 1

    # Return
    return uniques_count

# endregion

# region Function - Collpase to Mean Copunctal Distance
def distance_arc_to_gamut_edge(
    angle : float,
    cone_type : str,
    gamut_edge_index : int,
    radius : float
) -> float:
    """
    Determine distance between the point (defined by copunctal point, angle and
    radius) and the intersection of the indicated gamut triangle edge with the
    line defined by the copunctal point and angle.  Will be minimized with
    fmin() in determining the minimum/maximum angles for the arc contained by
    the gamut triangle.
    """

    # Validate Arguments
    assert isinstance(angle, float)
    assert -pi <= angle <= pi
    assert isinstance(cone_type, str)
    assert len(cone_type) == 1
    assert cone_type in CONE_TYPES
    assert isinstance(gamut_edge_index, int)
    assert 0 <= gamut_edge_index <= 2
    assert isinstance(radius, float)
    assert radius > 0.0

    # Get Point Coordinate
    point_coordinate = ( # Rotating zero angle to vertical to avoid jump from -pi to pi in area of interest
        COPUNCTAL_POINTS[cone_type][0] + radius * cos(angle + pi / 2),
        COPUNCTAL_POINTS[cone_type][1] + radius * sin(angle + pi / 2)
    )

    # Get Intersection Coordinate
    intersection_coordinate = intersection_two_segments(
        COPUNCTAL_POINTS[cone_type],
        point_coordinate,
        *gamut_segments[gamut_edge_index]
    )

    # Return Distance
    return (
        (point_coordinate[0] - intersection_coordinate[0]) ** 2.0
        + (point_coordinate[1] - intersection_coordinate[1]) ** 2.0
    ) ** 0.5

def collapse_to_mean_copunctal_distance(
    image : Image.Image,
    cone_type : str
) -> Image.Image:

    # region Validate Arguments
    assert isinstance(image, Image.Image)
    assert isinstance(cone_type, str)
    assert len(cone_type) == 1
    assert cone_type in CONE_TYPES
    # endregion

    # region Estimate Mean Chromaticity
    unique_colors = get_unique_colors(image)
    sum = {key : 0.0 for key in ['x', 'y', 'count']}
    for unique_color, color_count in unique_colors.items():
        chromaticity = rgb_to_chromoluminance(
            *list(
                value / 255.0
                for value in unique_color
            ),
            gamma_correct = False
        )
        sum['x'] += color_count * chromaticity[0]
        sum['y'] += color_count * chromaticity[1]
        sum['count'] += color_count
    mean_chromaticity = (
        sum['x'] / sum['count'],
        sum['y'] / sum['count']
    )
    # endregion

    # region Estimate Gamut Edge Intersection Angles and Set Angle Bounds
    mean_chromaticity_distance = (
        (mean_chromaticity[0] - COPUNCTAL_POINTS[cone_type][0]) ** 2.0
        + (mean_chromaticity[1] - COPUNCTAL_POINTS[cone_type][1]) ** 2.0
    ) ** 0.5
    gamut_edge_angles = list(
        fminbound(
            func = distance_arc_to_gamut_edge,
            x1 = angle_limits[cone_type][edge_index][0],
            x2 = angle_limits[cone_type][edge_index][1],
            args = (
                cone_type,
                edge_index,
                mean_chromaticity_distance
            )
        )
        for edge_index in range(3)
    )
    angle_bounds = (
        min(gamut_edge_angles) + (pi / 90.0), # 2 degree buffer
        max(gamut_edge_angles) - (pi / 90.0) # 2 degree buffer
    )
    # endregion

    # region Alter Unique Colors to Constant Radial Distance from Copunctal Point
    collapsed_colors = dict()
    for unique_color, color_count in unique_colors.items():
        chromoluminance = rgb_to_chromoluminance(
            *list(
                value / 255.0
                for value in unique_color
            ),
            gamma_correct = False
        )
        angle = arctan2(
            chromoluminance[1] - COPUNCTAL_POINTS[cone_type][1], # delta-y
            chromoluminance[0] - COPUNCTAL_POINTS[cone_type][0] # delta-x
        ) - pi / 2.0
        if angle < -pi: angle += 2.0 * pi
        if angle > pi: angle -= 2.0 * pi
        if angle < angle_bounds[0]: angle = angle_bounds[0]
        if angle > angle_bounds[1]: angle = angle_bounds[1]
        collapsed_colors[unique_color] = tuple(
            int(value * 255)
            for value in chromoluminance_to_rgb(
                COPUNCTAL_POINTS[cone_type][0]
                + mean_chromaticity_distance
                * cos(angle + pi / 2.0),
                COPUNCTAL_POINTS[cone_type][1]
                + mean_chromaticity_distance
                * sin(angle + pi / 2.0),
                chromoluminance[2],
                gamma_correct = False
            )
        )
    # endregion

    # region Build New Image and Return
    new_image = Image.new('RGB', image.size, (0, 0, 0))
    pixels = image.load(); new_pixels = new_image.load()
    for col in range(image.width):
        for row in range(image.height):
            new_pixels[col, row] = collapsed_colors[pixels[col, row][0:3]]
    return new_image
    # endregion

# endregion

# region Demonstration
if __name__ == '__main__':

    image_file_name = 'images/flower-field-250016_1280.jpg'

    # Load image and make 256 x 256 with correct mode
    with Image.open(image_file_name) as original_image:
        if original_image.mode == 'P': exit()
        resized_image = original_image.resize(
            (
                int(original_image.width * (256 / max(original_image.size))),
                int(original_image.height * (256 / max(original_image.size)))
            )
        )
    cropped_image = resized_image.crop(
        (
            int((resized_image.width - resized_image.height) / 2.0), # left
            0, # top
            resized_image.width - int((resized_image.width - resized_image.height) / 2.0) - 1, # right
            resized_image.height # bottom
        )
    )
    cropped_image.mode = 'RGB'

    # Get unique colors
    unique_colors = get_unique_colors(cropped_image)
    print(
        '\nNumber of Unique Colors: {0}'.format(
            len(unique_colors)
        )
    )

    # Filter - Collapse to Mean Copunctal Distance
    filtered_image = collapse_to_mean_copunctal_distance(cropped_image, 'S')
    filtered_image.save('images/temp.png')

# endregion
