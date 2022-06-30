"""
Functions for visualizing the distribution of chromaticities in an image and for
filtering that image to mimic the loss of chromatic discrimination ability from
missing one of the three cone photoreceptor types.
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
from enum import Enum
from PIL import Image
from typing import Dict, Tuple
from maths.chromaticity_conversion import COPUNCTAL_POINTS
from maths.color_conversion import (
    xyz_to_xyy,
    rgb_to_xyz,
    xyz_to_rgb,
    xyy_to_xyz
)
from numpy import cos, sin, pi, arctan2
from maths.functions import intersection_of_two_segments
from maths.plotting_series import gamut_triangle_vertices_srgb
from scipy.optimize import fminbound
# endregion

# region Constants
class CONE(Enum):
    LONG = 'long'
    MEDIUM = 'medium'
    SHORT = 'short'
# endregion

# region Get Unique Colors from Images (with Counts)
def get_unique_colors(
    image : Image.Image
) -> Dict[Tuple[int, int, int], int]: # {(red, green, blue) : count}
    """
    Build a dictionary where the RGB color (in the interval [0, 255]) is the key
    and the number of pixels in the image with that color is the value.
    """

    # Validate Arguments
    assert isinstance(image, Image.Image)

    # Build Dictionary
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

# region Filter Image
def filter_image(
    image : Image.Image,
    cone : str
) -> Image.Image:
    """
    Adjust the chromaticity of colors in the image to have a constant distance
    from the associated copunctal point (determined by cone type) equal to the
    mean distance of the chromaticities in the original image (somewhat
    preserving the mean color of the image).
    """

    # Validate Arguments
    assert isinstance(image, Image.Image)
    assert isinstance(cone, str)
    assert any(cone == valid.value for valid in CONE)

    # Select Copunctal Point
    copunctal_point = COPUNCTAL_POINTS[cone]

    # region Estimate Mean Chromaticity and its Distance from Copuncatl Point
    original_unique_colors = get_unique_colors(image)
    original_chromoluminances = dict()
    sum = {key : 0.0 for key in ['x', 'y', 'count']}
    for unique_color, color_count in original_unique_colors.items():
        chromoluminance = xyz_to_xyy(
            *rgb_to_xyz(
                *list(
                    value / 255.0
                    for value in unique_color
                )
            )
        )
        original_chromoluminances[unique_color] = chromoluminance
        sum['x'] += color_count * chromoluminance[0]
        sum['y'] += color_count * chromoluminance[1]
        sum['count'] += color_count
    mean_chromaticity = (
        sum['x'] / sum['count'],
        sum['y'] / sum['count']
    )
    mean_chromaticity_distance = (
        (mean_chromaticity[0] - copunctal_point[0]) ** 2.0
        + (mean_chromaticity[1] - copunctal_point[1]) ** 2.0
    ) ** 0.5
    # endregion

    # region Function - Distance to Gamut Edge
    def distance_to_edge(angle, gamut_vertex_1, gamut_vertex_2):
        """
        Determine the intersection of the confusion line defined by angle and
        copunctal_point with the indicated gamut edge.  Meausre the distance
        from that intersection to a point along the confusion line
        mean_chromaticity_distance away from the copunctal point.  Aim is to
        minimize this distance to determine the appropriate angle for the arc
        with mean_chromaticity_distance to intersect the gamut edge.
        """
        coordinate = (
            copunctal_point[0] + mean_chromaticity_distance * cos(angle),
            copunctal_point[1] + mean_chromaticity_distance * sin(angle)
        )
        intersection = intersection_of_two_segments(
            copunctal_point,
            coordinate,
            gamut_vertex_1,
            gamut_vertex_2
        )
        return (
            (coordinate[0] - intersection[0]) ** 2.0
            + (coordinate[1] - intersection[1]) ** 2.0
        ) ** 0.5
    # endregion

    # region Determine Angle Boundaries for Distribution Arc
    gamut_triangle_angles = {
        color_name : arctan2(
            color_coordinate['y'] - copunctal_point[1], # delta-y
            color_coordinate['x'] - copunctal_point[0] # delta-x
        ) if arctan2(
            color_coordinate['y'] - copunctal_point[1], # delta-y
            color_coordinate['x'] - copunctal_point[0] # delta-x
        ) <= -pi / 2.0 else arctan2(
            color_coordinate['y'] - copunctal_point[1], # delta-y
            color_coordinate['x'] - copunctal_point[0] # delta-x
        ) - 2.0 * pi
        for color_name, color_coordinate in gamut_triangle_vertices_srgb.items()
    }
    gamut_edge_angles = list(
        fminbound(
            func = distance_to_edge,
            x1 = min(
                [
                    gamut_triangle_angles[color_name_1],
                    gamut_triangle_angles[color_name_2]
                ]
            ),
            x2 = max(
                [
                    gamut_triangle_angles[color_name_1],
                    gamut_triangle_angles[color_name_2]
                ]
            ),
            args = (
                tuple(gamut_triangle_vertices_srgb[color_name_1][coord] for coord in ['x', 'y']),
                tuple(gamut_triangle_vertices_srgb[color_name_2][coord] for coord in ['x', 'y']),
            )
        )
        for color_name_1, color_name_2 in [
            ('Red', 'Green'),
            ('Green', 'Blue'),
            ('Blue', 'Red')
        ]
    )
    angle_bounds = (
        min(gamut_edge_angles) + (pi / 90.0), # 2 degree buffer
        max(gamut_edge_angles) - (pi / 90.0) # 2 degree buffer
    )
    # endregion

    # region Set New Colors
    changed_colors = dict()
    for unique_color, original_chromoluminance in original_chromoluminances.items():
        angle = ( # Force range between -5pi/2 to -pi/2
            arctan2(
                original_chromoluminance[1] - copunctal_point[1], # delta-y
                original_chromoluminance[0] - copunctal_point[0] # delta-x
            ) if
            arctan2(
                original_chromoluminance[1] - copunctal_point[1], # delta-y
                original_chromoluminance[0] - copunctal_point[0] # delta-x
            ) <= -pi / 2.0 else
            arctan2(
                original_chromoluminance[1] - copunctal_point[1], # delta-y
                original_chromoluminance[0] - copunctal_point[0] # delta-x
            ) - 2.0 * pi
        )
        if angle < angle_bounds[0]: angle = angle_bounds[0]
        if angle > angle_bounds[1]: angle = angle_bounds[1]
        valid_rgb = False
        use_luminance = original_chromoluminance[2]
        while not valid_rgb:
            new_color = xyz_to_rgb(
                *xyy_to_xyz(
                    copunctal_point[0] + mean_chromaticity_distance * cos(angle),
                    copunctal_point[1] + mean_chromaticity_distance * sin(angle),
                    use_luminance
                ),
                suppress_warnings = True
            )
            if all(0.0 <= value <= 1.0 for value in new_color):
                valid_rgb = True
            else:
                use_luminance *= 0.95
        changed_colors[unique_color] = tuple(
            int(value * 255.0)
            for value in new_color
        )
    # endregion

    # Build New Image
    new_image = Image.new('RGB', image.size, (0, 0, 0))
    pixels = image.load(); new_pixels = new_image.load()
    for col in range(image.width):
        for row in range(image.height):
            new_pixels[col, row] = changed_colors[pixels[col, row][0:3]]

    # Return
    return new_image

# endregion
