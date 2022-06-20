"""
Line path function returns a list of line segments and a list of associated
colors tracing a path around the display gamut in 2D chromaticity, 3D
chromoluminance, or 3D display space (RGB).
Plane function returns a list of matplotlib Paths (i.e. patches) and a list of
associated colors for a high saturation surface in 2D chromaticity space.
Surface function returns 2D arrays of coordinate triplets for i, j, and k
plotting axes and a 2D array of color triplets - either red, green, or blue must
be held constant at zero or one.
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
from typing import Optional, Tuple, List, Union
from numpy import ndarray, transpose, linspace
from rgb_cie_conversions import rgb_to_chromoluminance
from matplotlib.path import Path
# endregion

# region Constants
RESOLUTION = 16
# endregion

# region Function - Line Path around Saturation Gamut
def line_path(
    output_space : Optional[str] = None, # 'chromaticity' (default), 'chromoluminance', or 'display'
    resolution : Optional[int] = None, # Default RESOLUTION
    coefficients : Optional[ # Defaults to sRGB
        Union[
            List[Union[List[float], Tuple[float, float, float]]],
            Tuple[Union[List[float], Tuple[float, float, float]]],
            ndarray
        ]
    ] = None
) -> Tuple[
    List[ # Coordinate pairs (start, end), length = resolution + 5 * (resolution - 1)
        Union[
            Tuple[Tuple[float, float], Tuple[float, float]], # 2D
            Tuple[Tuple[float, float, float], Tuple[float, float, float]] # 3D
        ]
    ],
    List[Tuple[float, float, float]] # Colors, length = resolution + 5 * (resolution - 1)
    ]:

    # region Validate Arguments
    if output_space is None: output_space = 'chromaticity'
    assert isinstance(output_space, str)
    assert output_space in ['chromaticity', 'chromoluminance', 'display']
    if resolution is None: resolution = RESOLUTION
    assert isinstance(resolution, int)
    assert resolution >= 2
    if coefficients is not None:
        assert any(isinstance(coefficients, valid_type) for valid_type in [list, tuple, ndarray])
        if isinstance(coefficients, ndarray):
            assert len(coefficients.shape) == 2
            assert all(dimension == 3 for dimension in coefficients.shape)
        else:
            assert len(coefficients) == 3
            assert all(len(coefficient_row) == 3 for coefficient_row in coefficients)
        assert all(all(isinstance(value, float) for value in coefficient_row) for coefficient_row in coefficients)
    # endregion

    # region List Points Along Gamut
    rgb_points = transpose(
        [ # CCW from Red, excluding repeated first value from all but the first series
            [1.0] * resolution # Red: Red to Yellow
            + list(linspace(1, 0, resolution))[1:] # Red: Yellow to Green
            + [0.0] * (resolution - 1) # Red: Green to Cyan
            + [0.0] * (resolution - 1) # Red: Cyan to Blue
            + list(linspace(0, 1, resolution))[1:] # Red: Blue to Pink
            + [1.0] * (resolution - 1), # Red: Pink to Red
            list(linspace(0, 1, resolution)) # Green: Red to Yellow
            + [1.0] * (resolution - 1) # Green: Yellow to Green
            + [1.0] * (resolution - 1) # Green: Green to Cyan
            + list(linspace(1, 0, resolution))[1:] # Green: Cyan to Blue
            + [0.0] * (resolution - 1) # Green: Blue to Pink
            + [0.0] * (resolution - 1), # Green: Pink to Red
            [0.0] * resolution # Blue: Red to Yellow
            + [0.0] * (resolution - 1) # Blue: Yellow to Green
            + list(linspace(0, 1, resolution))[1:] # Blue: Green to Cyan
            + [1.0] * (resolution - 1) # Blue: Cyan to Blue
            + [1.0] * (resolution - 1) # Blue: Blue to Pink
            + list(linspace(1, 0, resolution))[1:] # Blue: Pink to Red
        ]
    ) # (R, G, B)
    rgb_points = list(
        (
            *triplet,
            *rgb_to_chromoluminance(
                *triplet,
                coefficients = coefficients
            )
        )
        for triplet in rgb_points
    ) # (R, G, B, x, y, Y)
    # endregion

    # region Build Return Lists
    coordinates = list(); colors = list()
    for first_index in range(len(rgb_points)):
        second_index = first_index + 1
        if second_index > len(rgb_points) - 1: second_index = 0
        coordinates.append(
            tuple(
                rgb_points[index][3:5]
                if output_space == 'chromaticity'
                else (
                    rgb_points[index][3:]
                    if output_space == 'chromoluminance'
                    else rgb_points[index][0:3]
                )
                for index in [first_index, second_index]
            )
        )
        colors.append(
            tuple(
                (
                    rgb_points[first_index][index]
                    + rgb_points[second_index][index]
                )
                / 2.0
                for index in range(3)
            )
        )
    # endregion

    # Return
    return coordinates, colors

# endregion

# region Function - Plane Patches Covering Saturation Gamut
def plane_paths(
    output_space : Optional[str] = None, # 'chromaticity' (default), 'chromoluminance', or 'display'
    resolution : Optional[int] = None, # Default RESOLUTION
    coefficients : Optional[ # Defaults to sRGB
        Union[
            List[Union[List[float], Tuple[float, float, float]]],
            Tuple[Union[List[float], Tuple[float, float, float]]],
            ndarray
        ]
    ] = None
) -> Tuple[
    List[Path], # Surface Patches, length = 3 * (resolution - 1) ** 2
    List[Tuple[float, float, float]] # Colors, length = 3 * (resolution - 1) ** 2
]:

    # region Validate Arguments
    if output_space is None: output_space = 'chromaticity'
    assert isinstance(output_space, str)
    assert output_space in ['chromaticity', 'chromoluminance', 'display']
    if resolution is None: resolution = RESOLUTION
    assert isinstance(resolution, int)
    assert resolution >= 2
    if coefficients is not None:
        assert any(isinstance(coefficients, valid_type) for valid_type in [list, tuple, ndarray])
        if isinstance(coefficients, ndarray):
            assert len(coefficients.shape) == 2
            assert all(dimension == 3 for dimension in coefficients.shape)
        else:
            assert len(coefficients) == 3
            assert all(len(coefficient_row) == 3 for coefficient_row in coefficients)
        assert all(all(isinstance(value, float) for value in coefficient_row) for coefficient_row in coefficients)
    # endregion

    # region Build Lists of Paths and Colors for Surface Patches
    color_values = linspace(0, 1, resolution)
    paths = list(); colors = list()
    for (fix_red, fix_green, fix_blue) in [(True, False, False), (False, True, False), (False, False, True)]:
        for second_index, second_value in enumerate(color_values):
            for third_index, third_value in enumerate(color_values):
                if second_index == 0 or third_index == 0: continue
                rgb_vertices = [
                    (
                        1.0 if fix_red else second_value,
                        1.0 if fix_green else (second_value if fix_red else third_value),
                        1.0 if fix_blue else third_value
                    ),
                    (
                        1.0 if fix_red else color_values[second_index - 1],
                        1.0 if fix_green else (color_values[second_index - 1] if fix_red else third_value),
                        1.0 if fix_blue else third_value
                    ),
                    (
                        1.0 if fix_red else color_values[second_index - 1],
                        1.0 if fix_green else (color_values[second_index - 1] if fix_red else color_values[third_index - 1]),
                        1.0 if fix_blue else color_values[third_index - 1]
                    ),
                    (
                        1.0 if fix_red else second_value,
                        1.0 if fix_green else (second_value if fix_red else color_values[third_index - 1]),
                        1.0 if fix_blue else color_values[third_index - 1]
                    ),
                    (
                        1.0 if fix_red else second_value,
                        1.0 if fix_green else (second_value if fix_red else third_value),
                        1.0 if fix_blue else third_value
                    )
                ]
                chromoluminance_vertices = list(
                    rgb_to_chromoluminance(
                        *rgb_vertice,
                        coefficients = coefficients
                    )
                    for rgb_vertice in rgb_vertices
                )
                paths.append(
                    Path(
                        list(
                            chromoluminance_vertice[0:2]
                            for chromoluminance_vertice in chromoluminance_vertices
                        )
                    )
                )
                colors.append(
                    (
                        1.0 if fix_red else (second_value + color_values[second_index - 1]) / 2.0,
                        1.0 if fix_green else (
                            (second_value + color_values[second_index - 1]) / 2.0
                            if fix_red else (third_value + color_values[third_index - 1]) / 2.0
                        ),
                        1.0 if fix_blue else (third_value + color_values[third_index - 1]) / 2.0
                    )
                )
    # endregion

    # Return
    return paths, colors

# endregion

# region Function - Surface Patches Covering a Single Saturation Surface


# endregion

# region Demonstration
if __name__ == '__main__':

    rgb_to_xyz = ( # Taken from CRT display
        (0.0455, 0.0369, 0.0282),
        (0.0256, 0.0708, 0.0184),
        (0.0023, 0.0106, 0.1484)
    )

    coordinates, colors = line_path(
        output_space = 'display',
        resolution = 4,
        coefficients = rgb_to_xyz
    )
    from pprint import pprint
    # pprint(coordinates); pprint(colors)
    from numpy import array
    print(array(coordinates).shape); print(array(colors).shape)

    paths, colors = plane_paths(
        output_space = 'display',
        resolution = 8,
        coefficients = None
    )
    print(array(paths).shape); print(array(colors).shape)
    print(3 * (8 - 1) * (8 - 1))


# endregion
