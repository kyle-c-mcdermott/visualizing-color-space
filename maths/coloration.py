"""
Functions for building paths/coordinates and colors for filling plotting areas
with color.
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
from matplotlib.path import Path
from numpy import linspace, pi, cos, sin, ptp
from maths.color_conversion import (
    DISPLAY,
    xyz_to_xyy,
    rgb_to_xyz,
    xyz_to_rgb,
    xyy_to_xyz
)
from maths.chromaticity_conversion import (
    STANDARD,
    angle_bounds_170_2_10,
    wavelength_from_hue_angle_170_2_10,
    chromaticity_from_wavelength_170_2_10,
    wavelength_bounds_170_2_10,
    hue_angle_from_wavelength_170_2_10,
    angle_bounds_170_2_2,
    wavelength_from_hue_angle_170_2_2,
    chromaticity_from_wavelength_170_2_2,
    wavelength_bounds_170_2_2,
    hue_angle_from_wavelength_170_2_2,
    angle_bounds_1964_10,
    wavelength_from_hue_angle_1964_10,
    chromaticity_from_wavelength_1964_10,
    wavelength_bounds_1964_10,
    hue_angle_from_wavelength_1964_10,
    angle_bounds_1931_2,
    wavelength_from_hue_angle_1931_2,
    chromaticity_from_wavelength_1931_2,
    wavelength_bounds_1931_2,
    hue_angle_from_wavelength_1931_2
)
from maths.functions import intersection_of_two_segments
from maths.plotting_series import (
    spectrum_locus_170_2_10,
    spectrum_locus_170_2_2,
    spectrum_locus_1964_10,
    spectrum_locus_1931_2
)
from maths.conversion_coefficients import COLOR_NAMES
# endregion

# region Chromaticity inside Gamut
def chromaticity_inside_gamut(
    resolution : int,
    display : Optional[str] = None, # default srgb
    apply_gamma_correction : Optional[bool] = None # default False
) -> Tuple[List[Path], List[Tuple[float, float, float]]]:
    """
    Returns a list of paths and a list of colors
    (length = 3 * (resolution - 1) ** 2) filling the display color gamut
    triangle based on display with saturated colors (at least one of red, green,
    and/or blue equal to one)
    """

    # region Validate Arguments
    assert isinstance(resolution, int)
    assert resolution >= 2
    if display is None: display = DISPLAY.SRGB.value
    assert isinstance(display, str)
    assert any(display == valid.value for valid in DISPLAY)
    if apply_gamma_correction is None: apply_gamma_correction = False
    assert isinstance(apply_gamma_correction, bool)
    # endregion

    # region Build Lists
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
                    xyz_to_xyy(
                        *rgb_to_xyz(
                            *rgb_vertex,
                            display = display,
                            apply_gamma_correction = apply_gamma_correction
                        ),
                        display = display
                    )
                    for rgb_vertex in rgb_vertices
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

# region Chromaticity outside Gamut
def chromaticity_outside_gamut(
    resolution : int,
    display : Optional[str] = None, # default srgb
    standard : Optional[str] = None # default CIE 1931
) -> Tuple[List[Path], List[Tuple[float, float, float]]]:
    """
    Returns a list of paths and a list of colors (length = resolution) filling
    the region inside the spectrum locus based on the most saturated color for
    each angle around white.
    """

    # region Validate Arguments
    assert isinstance(resolution, int)
    assert resolution >= 8
    if display is None: display = DISPLAY.SRGB.value
    assert isinstance(display, str)
    assert any(display == valid.value for valid in DISPLAY)
    assert display != DISPLAY.EXTERIOR.value
    if standard is None: standard = STANDARD.CIE_1931_2.value
    assert isinstance(standard, str)
    assert any(standard == valid.value for valid in STANDARD)
    # endregion

    # region Choose Based on Standard
    if standard == STANDARD.CIE_170_2_10.value:
        angle_bounds = angle_bounds_170_2_10
        wavelength_from_hue_angle = wavelength_from_hue_angle_170_2_10
        chromaticity_from_wavelength = chromaticity_from_wavelength_170_2_10
        spectrum_locus = spectrum_locus_170_2_10
    elif standard == STANDARD.CIE_170_2_2.value:
        angle_bounds = angle_bounds_170_2_2
        wavelength_from_hue_angle = wavelength_from_hue_angle_170_2_2
        chromaticity_from_wavelength = chromaticity_from_wavelength_170_2_2
        spectrum_locus = spectrum_locus_170_2_2
    elif standard == STANDARD.CIE_1964_10.value:
        angle_bounds = angle_bounds_1964_10
        wavelength_from_hue_angle = wavelength_from_hue_angle_1964_10
        chromaticity_from_wavelength = chromaticity_from_wavelength_1964_10
        spectrum_locus = spectrum_locus_1964_10
    else:
        angle_bounds = angle_bounds_1931_2
        wavelength_from_hue_angle = wavelength_from_hue_angle_1931_2
        chromaticity_from_wavelength = chromaticity_from_wavelength_1931_2
        spectrum_locus = spectrum_locus_1931_2
    # endregion

    # region Determine Colors
    white_chromaticity = xyz_to_xyy(
        *rgb_to_xyz(
            1.0, 1.0, 1.0,
            display = display
        ),
        display = display
    )[0:2]
    cyan_chromaticity = xyz_to_xyy(
        *rgb_to_xyz(
            0.0, 1.0, 1.0,
            display = display
        ),
        display = display
    )[0:2]
    safe_distance = 0.75 * ( # Cyan being nearest intermediate saturated color to white
        (white_chromaticity[0] - cyan_chromaticity[0]) ** 2.0
        + (white_chromaticity[1] - cyan_chromaticity[1]) ** 2.0
    ) ** 0.5
    safe_luminance = xyz_to_xyy(
        *rgb_to_xyz(
            0.0, 0.0, 1.0, # Blue having the lowest luminance of the three
            display = display
        ),
        display = display
    )[2]
    angles = linspace(
        0.0 - (5.0 / 2.0) * pi,
        2.0 * pi * (1 - (1 / resolution)) - (5.0 / 2.0) * pi,
        resolution
    )
    colors = list(
        xyz_to_rgb(
            *xyy_to_xyz(
                white_chromaticity[0] + safe_distance * cos(angle),
                white_chromaticity[1] + safe_distance * sin(angle),
                safe_luminance
            ),
            display = display
        )
        for angle in angles
    )
    colors = list(
        tuple(
            (value - min(color)) / ptp(color) # Set min to 0 and max to 1 maintaining ratio of distances to middle value
            for value in color
        )
        for color in colors
    )
    # endregion

    # region Determine Paths
    angles = list( # Offset by half width
        angle - pi / resolution
        for angle in angles
    )
    endpoints = list()
    for angle in angles:
        if angle_bounds[0] <= angle <= angle_bounds[1]: # Intersects spectrum locus
            endpoints.append(
                tuple(
                    float(
                        chromaticity_from_wavelength[coordinate](
                            wavelength_from_hue_angle(angle)
                        )
                    )
                    for coordinate in ['x', 'y']
                )
            )
        else: # Intersects line between spectrum locus endpoints
            endpoints.append(
                intersection_of_two_segments(
                    white_chromaticity,
                    (
                        white_chromaticity[0] + 1.0 * cos(angle),
                        white_chromaticity[1] + 1.0 * sin(angle)
                    ),
                    (spectrum_locus[0]['x'], spectrum_locus[0]['y']),
                    (spectrum_locus[-1]['x'], spectrum_locus[-1]['y'])
                )
            )
    paths = list()
    for first_index in range(resolution):
        second_index = first_index + 1
        if second_index >= resolution: second_index = 0
        paths.append(
            Path(
                [
                    white_chromaticity,
                    endpoints[first_index],
                    endpoints[second_index],
                    white_chromaticity
                ]
            )
        )
    # endregion

    # Return
    return paths, colors

# endregion

# region Three-Dimensional Surface
def three_dimensional_surface(
    resolution : int,
    color_name : str,
    color_value : Union[int, float],
    plot_rgb : Optional[bool] = None, # default False
    display : Optional[str] = None, # default srgb
    apply_gamma_correction : Optional[bool] = None # default False
) -> Tuple[
    Tuple[List[List[float]], List[List[float]], List[List[float]]],
    List[List[Tuple[float, float, float]]]
]:
    """
    Returns a tuple of three two-dimenaional arrays (lists of lists) of
    coordinate values for the three plotting dimensions and a corresponding list
    of lists of colors (shape = (resolution, resolution)) for a saturation
    surface where color_name is held constant at color_value.
    """

    # region Validate Arguments
    assert isinstance(resolution, int)
    assert resolution >= 2
    assert isinstance(color_name, str)
    color_name = color_name.lower().title()
    assert color_name in COLOR_NAMES
    assert any(isinstance(color_value, valid_type) for valid_type in [int, float])
    assert 0.0 <= color_value <= 1.0
    if plot_rgb is None: plot_rgb = False
    assert isinstance(plot_rgb, bool)
    if display is None: display = DISPLAY.SRGB.value
    assert isinstance(display, str)
    assert any(display == valid.value for valid in DISPLAY)
    if apply_gamma_correction is None: apply_gamma_correction = False
    assert isinstance(apply_gamma_correction, bool)
    # endregion

    # region Build Lists
    color_index = COLOR_NAMES.index(color_name)
    first_index = 1 if color_index == 0 else 0
    second_index = 2 if color_index != 2 else 1
    triplet = 3 * [0.0]
    triplet[color_index] = float(color_value)
    xs = list(); ys = list(); zs = list(); colors = list()
    for first_value in linspace(0, 1, resolution):
        row_xs = list(); row_ys = list(); row_zs = list(); row_colors = list()
        for second_value in linspace(0, 1, resolution):
            triplet[first_index] = first_value
            triplet[second_index] = second_value
            if plot_rgb:
                use_values = triplet
            else:
                use_values = xyz_to_xyy(
                    *rgb_to_xyz(
                        *triplet,
                        display = display,
                        apply_gamma_correction = apply_gamma_correction
                    ),
                    display = display
                )
            row_xs.append(use_values[0])
            row_ys.append(use_values[1])
            row_zs.append(use_values[2])
            row_colors.append(tuple(value for value in triplet)) # Weird reference issue just appending triplet
        xs.append(row_xs); ys.append(row_ys); zs.append(row_zs)
        colors.append(row_colors)
    # endregion

    # Return
    return (xs, ys, zs), colors

# endregion

# region Visible Spectrum
def visible_spectrum(
    resolution : int,
    left : Union[int, float],
    bottom : Union[int, float],
    width : Union[int, float],
    height : Union[int, float],
    minimum_wavelength : Union[int, float],
    maximum_wavelength : Union[int, float],
    vertical : Optional[bool] = None, # default False (horizontal)
    display : Optional[str] = None, # default srgb
    standard : Optional[str] = None # default CIE 1931
) -> Tuple[List[Path], List[Tuple[float, float, float]]]:
    """
    Returns a list of paths and a list of colors (length = resolution) filling
    the region specified by left/bottom/width/height and providing saturated
    colors based on the hue angle for each wavelength within the given range.
    Negative width or height (depending on vertical),
    or minimum_wavelength > maximum_wavelength, will reverse the direction.
    """

    # region Validate Arguments
    assert isinstance(resolution, int)
    assert resolution >= 8
    assert any(isinstance(left, valid_type) for valid_type in [int, float])
    assert any(isinstance(bottom, valid_type) for valid_type in [int, float])
    assert any(isinstance(width, valid_type) for valid_type in [int, float])
    assert width != 0.0
    assert any(isinstance(height, valid_type) for valid_type in [int, float])
    assert height != 0.0
    assert any(isinstance(minimum_wavelength, valid_type) for valid_type in [int, float])
    assert any(isinstance(maximum_wavelength, valid_type) for valid_type in [int, float])
    if vertical is None: vertical = False
    assert isinstance(vertical, bool)
    if display is None: display = DISPLAY.SRGB.value
    assert isinstance(display, str)
    assert any(display == valid.value for valid in DISPLAY)
    assert display != DISPLAY.EXTERIOR.value
    if standard is None: standard = STANDARD.CIE_1931_2.value
    assert isinstance(standard, str)
    assert any(standard == valid.value for valid in STANDARD)
    # endregion

    # region Choose Based on Standard
    if standard == STANDARD.CIE_170_2_10.value:
        wavelength_bounds = wavelength_bounds_170_2_10
        hue_angle_from_wavelength = hue_angle_from_wavelength_170_2_10
    elif standard == STANDARD.CIE_170_2_2.value:
        wavelength_bounds = wavelength_bounds_170_2_2
        hue_angle_from_wavelength = hue_angle_from_wavelength_170_2_2
    elif standard == STANDARD.CIE_1964_10.value:
        wavelength_bounds = wavelength_bounds_1964_10
        hue_angle_from_wavelength = hue_angle_from_wavelength_1964_10
    else:
        wavelength_bounds = wavelength_bounds_1931_2
        hue_angle_from_wavelength = hue_angle_from_wavelength_1931_2
    # endregion

    # More Validation
    assert wavelength_bounds[0] <= minimum_wavelength <= wavelength_bounds[1]
    assert wavelength_bounds[0] <= maximum_wavelength <= wavelength_bounds[1]

    # region Determine Colors
    wavelengths = linspace(
        minimum_wavelength,
        maximum_wavelength,
        resolution + 1
    )[0:-1]
    angles = list(
        float(hue_angle_from_wavelength(wavelength))
        for wavelength in wavelengths
    )
    white_chromaticity = xyz_to_xyy(
        *rgb_to_xyz(
            1.0, 1.0, 1.0,
            display = display
        ),
        display = display
    )[0:2]
    cyan_chromaticity = xyz_to_xyy(
        *rgb_to_xyz(
            0.0, 1.0, 1.0,
            display = display
        ),
        display = display
    )[0:2]
    safe_distance = 0.75 * ( # Cyan being nearest intermediate saturated color to white
        (white_chromaticity[0] - cyan_chromaticity[0]) ** 2.0
        + (white_chromaticity[1] - cyan_chromaticity[1]) ** 2.0
    ) ** 0.5
    safe_luminance = xyz_to_xyy(
        *rgb_to_xyz(
            0.0, 0.0, 1.0, # Blue having the lowest luminance of the three
            display = display
        ),
        display = display
    )[2]
    colors = list(
        xyz_to_rgb(
            *xyy_to_xyz(
                white_chromaticity[0] + safe_distance * cos(angle),
                white_chromaticity[1] + safe_distance * sin(angle),
                safe_luminance
            ),
            display = display
        )
        for angle in angles
    )
    colors = list(
        tuple(
            (value - min(color)) / ptp(color) # Set min to 0 and max to 1 maintaining ratio of distances to middle value
            for value in color
        )
        for color in colors
    )
    # endregion

    # region Determine Paths
    paths = list(
        Path(
            [
                (
                    left + ((index / resolution) * width if not vertical else 0.0),
                    bottom + ((index / resolution) * height if vertical else 0.0)
                ),
                (
                    left + ((index / resolution) * width if not vertical else 0.0),
                    bottom + (((index + 1) / resolution) * height if vertical else height)
                ),
                (
                    left + (((index + 1) / resolution) * width if not vertical else width),
                    bottom + (((index + 1) / resolution) * height if vertical else height)
                ),
                (
                    left + (((index + 1) / resolution) * width if not vertical else width),
                    bottom + ((index / resolution) * height if vertical else 0.0)
                ),
                (
                    left + ((index / resolution) * width if not vertical else 0.0),
                    bottom + ((index / resolution) * height if vertical else 0.0)
                )
            ]
        )
        for index in range(resolution)
    )
    # endregion

    # Return
    return paths, colors

# endregion
