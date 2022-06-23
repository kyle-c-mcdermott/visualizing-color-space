"""
Four functions each provide a list of coordinates for plotting and a list of
corresponding colors.  Depending upon the nature of the plotting area (two-
dimensional or three-dimensional), the coordinates may be returned as matplotlib
Paths or as a two-dimensional numpy array of coordinate positions for x, y and z.
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
from csv import DictReader
from typing import Optional, Union, List, Tuple
from numpy import arctan2, pi, transpose, clip, ndarray, linspace
from scipy.interpolate import interp1d
from maths.rgb_cie_conversions import rgb_to_chromoluminance
from matplotlib.path import Path
# endregion

# region Constants
RESOLUTION = 16

"""
Linear transformation coefficients for sRGB to CIE 1931 2-Degree tristimulus
values taken from:
https://en.wikipedia.org/wiki/SRGB#From_sRGB_to_CIE_XYZ
Used here only to determine white point with default coefficients (gamma
correction handled during conversion by other functions)
"""
SRGB_TO_XYZ = (
    (0.4124, 0.3576, 0.1805), # X_R, X_G, X_B
    (0.2126, 0.7152, 0.0722), # Y_R, Y_G, Y_B
    (0.0193, 0.1192, 0.9505) # Z_R, Z_G, Z_B
)
# endregion

# region Load CIE 1931 2-Degree Spectrum Locus
"""
Tabulated spectrum locus coordinates for CIE 1931 2-degree downloaded from:
http://www.cvrl.org/cie.htm
Under Chromaticity Coordinates, CIE 1931 2-deg xyz chromaticity coordinates
using the second button "/W" with a solid (instead of dashed) line indicating
higher sampling resolution (1 nm)
(Note that chromaticity values do not change beyond 699 nm, likely due to the
fact that rounding errors seem to cause the spectrum locus to start wandering
about back on itself based on chromaticities converted from the tabulated color
matching functions - the converted values were abandoned and 699 nm copied down
for the remainder of the series.)
"""
with open(
    'cvrl/cccie31_1.csv',
    'r'
) as read_file:
    spectrum_locus = list(
        {
            'Wavelength' : int(row['Wavelength']),
            'x' : float(row['x']),
            'y' : float(row['y'])
        }
        for row in DictReader(
            read_file,
            fieldnames = ['Wavelength', 'x', 'y', 'z'] # z is superfluous
        )
        if int(row['Wavelength']) < 700
    )
# endregion

# region Function - Gamut Series (used by other functions)
def gamut_series(
    resolution : Optional[int] = None,
    coefficients : Optional[
        Union[
            List[Union[List[float], Tuple[float, float, float]]],
            Tuple[Union[List[float], Tuple[float, float, float]]],
            ndarray
        ]
    ] = None
) -> List[Tuple[float, float, float, float, float, float, float, Union[float, None]]]:
    """
    Traces a line starting at red, passing through green and blue and returning
    just short of red along the gamut triangle.  Returns a list
    (N = resolution + 5 * (resolution - 1)) of the following values:
        Red, Green, and Blue values (display RGB)
        x, y, and Y chromoluminance (CIE 1931 2-Degree assumed)
        Hue angle from white point (D65 default)
        Interpolated wavelength based on hue angle (within valid range)
    """

    # region Validate Arguments
    if resolution is None: resolution = RESOLUTION
    assert isinstance(resolution, int)
    assert resolution >= 2
    if coefficients is None: coefficients = SRGB_TO_XYZ
    assert any(isinstance(coefficients, valid_type) for valid_type in [list, tuple, ndarray])
    if isinstance(coefficients, ndarray):
        assert len(coefficients.shape) == 2
        assert all(dimension == 3 for dimension in coefficients.shape)
    else:
        assert len(coefficients) == 3
        assert all(len(coefficient_row) == 3 for coefficient_row in coefficients)
    assert all(all(isinstance(value, float) for value in coefficient_row) for coefficient_row in coefficients)
    # endregion

    # region Determine White
    white_tristimulus = list(sum(row) for row in coefficients)
    white_chromaticity = (
        white_tristimulus[0] / sum(white_tristimulus),
        white_tristimulus[1] / sum(white_tristimulus)
    )
    # endregion

    # region Build Interpolation for Wavelength Hue Angles
    spectrum_locus_hues = sorted(
        list(
            (
                arctan2(
                    datum['y'] - white_chromaticity[1], # delta-y
                    datum['x'] - white_chromaticity[0] # delta-x
                )
                if arctan2(
                    datum['y'] - white_chromaticity[1], # delta-y
                    datum['x'] - white_chromaticity[0] # delta-x
                ) > -pi / 2 # Avoids jump in angle series
                else arctan2(
                    datum['y'] - white_chromaticity[1], # delta-y
                    datum['x'] - white_chromaticity[0] # delta-x
                ) + 2 * pi,
                datum['Wavelength']
            )
            for datum in spectrum_locus
        ),
        key = lambda pair: pair[0]
    )
    hue_bounds = (
        min(transpose(spectrum_locus_hues)[0]),
        max(transpose(spectrum_locus_hues)[0])
    )
    wavelength_from_angle = interp1d(
        *transpose(spectrum_locus_hues),
        kind = 'quadratic'
    )
    # endregion

    # region Build Output Series
    output_series = transpose(
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
    )[0:-2] # (R, G, B) (remove last, repeated red coordinate)
    output_series = list(
        (
            *triplet,
            *rgb_to_chromoluminance(*triplet, coefficients = coefficients)
        )
        for triplet in output_series
    ) # (R, G, B, x, y, Y)
    output_series = list(
        (
            *sextuplet,
            arctan2(
                sextuplet[4] - white_chromaticity[1], # delta-y
                sextuplet[3] - white_chromaticity[0] # delta-x
            )
            if arctan2(
                sextuplet[4] - white_chromaticity[1], # delta-y
                sextuplet[3] - white_chromaticity[0] # delta-x
            ) > -pi / 2
            else arctan2(
                sextuplet[4] - white_chromaticity[1], # delta-y
                sextuplet[3] - white_chromaticity[0] # delta-x
            ) + 2 * pi
        )
        for sextuplet in output_series
    ) # (R, G, B, x, y, Y, hue-angle)
    output_series = list(
        (
            *septuplet,
            float(wavelength_from_angle(septuplet[-1]))
            if hue_bounds[0] <= septuplet[-1] <= hue_bounds[1]
            else None # Won't be used for visible spectrum
        )
        for septuplet in output_series
    ) # (R, G, B, x, y, Y, hue-angle, wavelength)
    # endregion

    # Return
    return output_series

# endregion

# region Function - Visible Spectrum Band
def visible_spectrum(
    left : Union[int, float],
    bottom : Union[int, float],
    width : Union[int, float],
    height : Union[int, float],
    min_wavelength : Union[int, float],
    max_wavelength : Union[int, float],
    resolution : Optional[int] = None, # default RESOLUTION
    power : Optional[float] = None, # default 0 (no fading)
    vertical : Optional[bool] = None, # default False (horizontal)
    coefficients : Optional[ # default sRGB
        Union[
            List[Union[List[float], Tuple[float, float, float]]],
            Tuple[Union[List[float], Tuple[float, float, float]]],
            ndarray
        ]
    ] = None
) -> Tuple[List[Path], List[Tuple[float, float, float]]]:
    """
    Returns a list of paths and a list of colors (N = resolution) filling a band
    (default horizontal) specified by the first four arguments.  Goes from low
    wavelengths (blue) to high wavelengths (red) from left/bottom to
    width/height; use negative width or height to reverse direction.
    Wavelengths beyond the valid range will simply be copied from the minimum or
    maximum valid value (can also reverse direction by swapping min/max
    wavelengths).  A value for power greater that zero will cause the spectrum
    to darken towards red and blue - higher power means more darkening.
    """

    # region Validate Arguments
    assert any(isinstance(left, valid_type) for valid_type in [int, float])
    assert any(isinstance(bottom, valid_type) for valid_type in [int, float])
    assert any(isinstance(width, valid_type) for valid_type in [int, float])
    assert any(isinstance(height, valid_type) for valid_type in [int, float])
    assert any(isinstance(min_wavelength, valid_type) for valid_type in [int, float])
    assert 300 < min_wavelength < 900 # arbitrary, but reasonable limits
    assert any(isinstance(max_wavelength, valid_type) for valid_type in [int, float])
    assert 300 < max_wavelength < 900 # arbitrary, but reasonable limits
    if resolution is None: resolution = RESOLUTION
    assert isinstance(resolution, int)
    assert resolution >= 2
    if power is None: power = 0.0
    assert isinstance(power, float)
    assert power >= 0.0
    if vertical is None: vertical = False
    assert isinstance(vertical, bool)
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

    # region Build List of Paths
    output_paths = list(
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

    # region Get Saturated Values Series and Build Interpolators
    saturated_values = gamut_series(
        resolution = resolution,
        coefficients = coefficients
    ) # (R, G, B, x, y, Y, hue-angle, wavelength)
    wavelength_bounds = (
        min(list(octuplet[-1] for octuplet in saturated_values if octuplet[-1] is not None)),
        max(list(octuplet[-1] for octuplet in saturated_values if octuplet[-1] is not None))
    )
    rgb_from_wavelength = list(
        interp1d(
            list(datum[-1] for datum in saturated_values if datum[-1] is not None),
            list(datum[index] for datum in saturated_values if datum[-1] is not None),
            kind = 'quadratic'
        )
        for index in range(3)
    )
    normalized_Y = list(
        (
            octuplet[-1],
            octuplet[5] / max(list(datum[5] for datum in saturated_values if datum[-1] is not None))
        )
        for octuplet in saturated_values
        if octuplet[-1] is not None
    ) # (wavelength, noramlized-Y)
    normalized_Y_from_wavelength = interp1d(
        *transpose(normalized_Y),
        kind = 'quadratic'
    )
    # endregion

    # region Build List of Colors
    wavelengths = clip(
        list(
            min_wavelength + (index / (resolution - 1)) * (max_wavelength - min_wavelength)
            for index in range(resolution)
        ),
        a_min = wavelength_bounds[0],
        a_max = wavelength_bounds[1]
    )
    output_colors = list(
        list(
            clip(
                float(interpolator(wavelength))
                * float(normalized_Y_from_wavelength(wavelength)) **  power,
                a_min = 0.0,
                a_max = 1.0
            )
            for interpolator in rgb_from_wavelength
        )
        for wavelength in wavelengths
    )
    # endregion

    return output_paths, output_colors

# endregion

# region Function - Chromaticity within Gamut
def chromaticity_within_gamut(
    resolution : Optional[int] = None, # default RESOLUTION
    gamma_correct : Optional[bool] = None,
    coefficients : Optional[ # default sRGB
        Union[
            List[Union[List[float], Tuple[float, float, float]]],
            Tuple[Union[List[float], Tuple[float, float, float]]],
            ndarray
        ]
    ] = None
) -> Tuple[List[Path], List[Tuple[float, float, float]]]:
    """
    Returns a list of paths and a list of colors (N = 3 * (resolution - 1) ** 2)
    filling the triangular gamut space within the chromaticity coordinates
    derived from coefficients with saturated colors (at least one of red, green,
    and/or blue is equal to one)
    """

    # region Validate Arguments
    if resolution is None: resolution = RESOLUTION
    assert isinstance(resolution, int)
    assert resolution >= 2
    if gamma_correct is None: gamma_correct = False
    assert isinstance(gamma_correct, bool)
    if coefficients is not None: # Can otherwise be passed as None
        assert any(isinstance(coefficients, valid_type) for valid_type in [list, tuple, ndarray])
        if isinstance(coefficients, ndarray):
            assert len(coefficients.shape) == 2
            assert all(dimension == 3 for dimension in coefficients.shape)
        else:
            assert len(coefficients) == 3
            assert all(len(coefficient_row) == 3 for coefficient_row in coefficients)
        assert all(all(isinstance(value, float) for value in coefficient_row) for coefficient_row in coefficients)
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
                    rgb_to_chromoluminance(
                        *rgb_vertice,
                        gamma_correct = gamma_correct,
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

# region Function - Chromaticity outside Gamut (but inside Spectrum Locus)
def chromaticity_outside_gamut(
    resolution : Optional[int] = None, # default RESOLUTION
    coefficients : Optional[ # default sRGB
        Union[
            List[Union[List[float], Tuple[float, float, float]]],
            Tuple[Union[List[float], Tuple[float, float, float]]],
            ndarray
        ]
    ] = None
) -> Tuple[List[Path], List[Tuple[float, float, float]]]:
    """
    Returns a list of paths a dn a list of colors
    (N = resolution + 5 * (resolution - 1)) filling the area outside the
    triangular gamut space defined by the chromaticity coordinates defined by
    the coefficients with saturated colors (at least one of red, green, and/or
    blue is equal to one) and inside the spectrum locus.  If the coefficients
    define chromaticities beyond the spectrum locus (i.e. "impossible" values)
    then the filled in area will still be between the gamut triangle and
    spectrum locus.
    """

    # region Validate Arguments
    if resolution is None: resolution = RESOLUTION
    assert isinstance(resolution, int)
    assert resolution >= 2
    if coefficients is None: coefficients = SRGB_TO_XYZ
    assert any(isinstance(coefficients, valid_type) for valid_type in [list, tuple, ndarray])
    if isinstance(coefficients, ndarray):
        assert len(coefficients.shape) == 2
        assert all(dimension == 3 for dimension in coefficients.shape)
    else:
        assert len(coefficients) == 3
        assert all(len(coefficient_row) == 3 for coefficient_row in coefficients)
    assert all(all(isinstance(value, float) for value in coefficient_row) for coefficient_row in coefficients)
    # endregion

    # region Determine White
    white_tristimulus = list(sum(row) for row in coefficients)
    white_chromaticity = (
        white_tristimulus[0] / sum(white_tristimulus),
        white_tristimulus[1] / sum(white_tristimulus)
    )
    # endregion

    # region Get Saturated Values Series and Build Interpolators
    saturated_values = gamut_series(
        resolution = resolution,
        coefficients = coefficients
    ) # (R, G, B, x, y, Y, hue-angle, wavelength)
    spectrum_locus_hue_angles = list(
        (
            datum['x'],
            datum['y'],
            arctan2(
                datum['y'] - white_chromaticity[1], # delta-y
                datum['x'] - white_chromaticity[0] # delta-x
            )
            if arctan2(
                datum['y'] - white_chromaticity[1], # delta-y
                datum['x'] - white_chromaticity[0] # delta-x
            ) > -pi / 2 # Avoids jump in angle series
            else arctan2(
                datum['y'] - white_chromaticity[1], # delta-y
                datum['x'] - white_chromaticity[0] # delta-x
            ) + 2 * pi
        )
        for datum in spectrum_locus
    ) # (x, y, hue-angle)
    spectrum_locus_hue_angles = list(
        (
            datum[0],
            datum[1],
            datum[2] - 2 * pi
        )
        for datum in spectrum_locus_hue_angles[:4]
    ) + spectrum_locus_hue_angles + list(
        (
            datum[0],
            datum[1],
            datum[2] + 2 * pi
        )
        for datum in spectrum_locus_hue_angles[-4:]
    ) # (x, y, hue-angle) - insuring closed series
    spectrum_locus_chromaticity_from_angle = list(
        interp1d(
            transpose(spectrum_locus_hue_angles)[2],
            transpose(spectrum_locus_hue_angles)[index]
        )
        for index in range(2)
    )
    saturated_values = list(
        (
            *octuplet,
            *list(
                float(interpolator(octuplet[6]))
                for interpolator in spectrum_locus_chromaticity_from_angle
            )
        )
        for octuplet in saturated_values
    ) # (R, G, B, x, y, Y, hue-angle, wavelength, x-SL-intercept, y-SL-intercept)
    # endregion

    # region Build Lists
    paths = list(); colors = list()
    for first_index in range(len(saturated_values)):
        second_index = first_index + 1
        if second_index > len(saturated_values) - 1: second_index = 0
        paths.append(
            Path(
                [
                    (
                        saturated_values[first_index][3], # x
                        saturated_values[first_index][4] # y
                    ),
                    (
                        saturated_values[first_index][8], # x-SL-intercept
                        saturated_values[first_index][9] # y-SL-intercept
                    ),
                    (
                        saturated_values[second_index][8], # x-SL-intercept
                        saturated_values[second_index][9] # y-SL-intercept
                    ),
                    (
                        saturated_values[second_index][3], # x
                        saturated_values[second_index][4] # y
                    ),
                    (
                        saturated_values[first_index][3], # x
                        saturated_values[first_index][4] # y
                    )
                ]
            )
        )
        colors.append(
            list(
                (
                    saturated_values[first_index][index]
                    + saturated_values[second_index][index]
                )
                / 2.0
                for index in range(3)
            )
        )
    # endregion

    # Return
    return paths, colors

# endregion

# region Function - Three-Dimensional Surface
def three_dimensional_surface(
    color_index : int, # Red = 0, Green = 1, Blue = 2
    space_index : int, # RGB = 0, Chromoluminance = 1
    color_value : Optional[int] = None, # default 1
    resolution : Optional[int] = None, # default RESOLUTION
    gamma_correct : Optional[bool] = None,
    coefficients : Optional[ # default sRGB / CIE 1931
        Union[
            List[Union[List[float], Tuple[float, float, float]]],
            Tuple[Union[List[float], Tuple[float, float, float]]],
            ndarray
        ]
    ] = None
) -> Tuple[
    Tuple[List[List[float]], List[List[float]], List[List[float]]],
    List[List[Tuple[float, float, float]]]
]:
    """
    Returns a tuple of three two-dimensional arrays (lists of lists) of
    coorindate values for plot_x, plot_y, and plot_z (not to be confused with
    chromaticity coordintaes) and a similar array of colors
    (N = resolution ** 2) for one of six possible saturation surfaces based on
    the combination of color (red, green, or blue) and fixed value (0 or 1) in
    the specified space (sRGB cube or chromoluminance - default CIE 1931)
    """

    # region Validate Arguments
    assert isinstance(color_index, int)
    assert 0 <= color_index <= 2 # 0 = Red, 1 = Green, 2 = Blue
    assert isinstance(space_index, int)
    assert 0 <= space_index <= 1 # 0 = RGB, 1 = Chromoluminance
    if color_value is None: color_value = 1
    assert isinstance(color_value, int)
    assert 0 <= color_value <= 1 # 0 = Transitions to White, 1 = Transitions to Black
    if resolution is None: resolution = RESOLUTION
    assert isinstance(resolution, int)
    assert resolution >= 2
    if gamma_correct is None: gamma_correct = True
    assert isinstance(gamma_correct, bool)
    if coefficients is not None: # Can otherwise be passed as None
        assert any(isinstance(coefficients, valid_type) for valid_type in [list, tuple, ndarray])
        if isinstance(coefficients, ndarray):
            assert len(coefficients.shape) == 2
            assert all(dimension == 3 for dimension in coefficients.shape)
        else:
            assert len(coefficients) == 3
            assert all(len(coefficient_row) == 3 for coefficient_row in coefficients)
        assert all(all(isinstance(value, float) for value in coefficient_row) for coefficient_row in coefficients)
    # endregion

    # region Build Lists
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
            if space_index == 0:
                use_values = triplet
            else:
                use_values = rgb_to_chromoluminance(
                    *triplet,
                    gamma_correct = gamma_correct,
                    coefficients = coefficients
                )
            row_xs.append(use_values[0])
            row_ys.append(use_values[1])
            row_zs.append(use_values[2])
            row_colors.append(tuple(value for value in triplet)) # Weird reference issue just appending triplet
        xs.append(row_xs); ys.append(row_ys); zs.append(row_zs)
        colors.append(row_colors)
    # endregion

    return (xs, ys, zs), colors

# endregion

# region Demonstration
if __name__ == '__main__':
    """Uncomment as desired"""

    # rgb_to_xyz = ( # Measured from CRT display
    #     (0.0455, 0.0369, 0.0282),
    #     (0.0256, 0.0708, 0.0184),
    #     (0.0023, 0.0106, 0.1484)
    # )
    # rgb_to_xyz = ( # Arbitrary Outisde Primaries
    #     (0.8812, -0.0405, 0.1097),
    #     (0.3247, 0.7334, -0.0581),
    #     (-0.2237, 0.0807, 1.2320)
    # )

    # from figure.figure import Figure
    # from matplotlib.collections import PathCollection
    # from numpy import array

    # region visible_spectrum
    # figure = Figure(
    #     name = 'Demonstration - saturated_color_paths visible_spectrum',
    #     size = (16, 9),
    #     inverted = True
    # )
    # panel = figure.add_panel(
    #     name = 'main',
    #     title = 'Demonstration - saturated_color_paths.visible_spectrum',
    #     x_lim = (0, 1),
    #     y_lim = (0, 1)
    # )
    # paths, colors = visible_spectrum(
    #     0.1, 0.85, 0.8, 0.1,
    #     400, 650,
    #     resolution = 128
    # )
    # panel.add_collection(
    #     PathCollection(
    #         paths,
    #         facecolors = colors,
    #         edgecolors = colors,
    #         zorder = 0
    #     )
    # )
    # paths, colors = visible_spectrum(
    #     0.1, 0.75, 0.8, 0.1,
    #     450, 600,
    #     resolution = 256,
    #     power = 1.0
    # )
    # panel.add_collection(
    #     PathCollection(
    #         paths,
    #         facecolors = colors,
    #         edgecolors = colors,
    #         zorder = 0
    #     )
    # )
    # paths, colors = visible_spectrum(
    #     0.1, 0.65, 0.8, 0.1,
    #     625, 425,
    #     resolution = 512,
    #     power = 0.5
    # )
    # panel.add_collection(
    #     PathCollection(
    #         paths,
    #         facecolors = colors,
    #         edgecolors = colors,
    #         zorder = 0
    #     )
    # )
    # paths, colors = visible_spectrum(
    #     0.1, 0.1, 0.1, 0.5,
    #     390, 830,
    #     resolution = 256,
    #     power = 0.0,
    #     vertical = True
    # )
    # panel.add_collection(
    #     PathCollection(
    #         paths,
    #         facecolors = colors,
    #         edgecolors = colors,
    #         zorder = 0
    #     )
    # )
    # paths, colors = visible_spectrum(
    #     0.25, 0.1, 0.1, 0.5,
    #     540, 590,
    #     resolution = 256,
    #     power = 2.0,
    #     vertical = True
    # )
    # panel.add_collection(
    #     PathCollection(
    #         paths,
    #         facecolors = colors,
    #         edgecolors = colors,
    #         zorder = 0
    #     )
    # )
    # paths, colors = visible_spectrum(
    #     0.4, 0.1, 0.1, 0.5,
    #     525, 475,
    #     resolution = 256,
    #     power = 2.0,
    #     vertical = True
    # )
    # panel.add_collection(
    #     PathCollection(
    #         paths,
    #         facecolors = colors,
    #         edgecolors = colors,
    #         zorder = 0
    #     )
    # )
    # figure.update()
    # figure.save(
    #     path = 'images',
    #     name = figure.name,
    #     extension = 'svg'
    # )
    # figure.close()
    # endregion

    # region chromaticity_within_gamut
    # figure = Figure(
    #     name = 'Demonstration - saturated_color_paths chromaticity_within_gamut',
    #     size = (16, 9),
    #     inverted = True
    # )
    # srgb_panel = figure.add_panel(
    #     name = 'srgb',
    #     title = 'Demonstration - saturated_color_paths.chromaticity_within_gamut\nsRGB',
    #     position = (0, 0, 0.5, 1),
    #     x_label = 'x',
    #     x_ticks = linspace(0, 0.8, 9),
    #     x_lim = (-0.065, 0.865),
    #     y_label = 'y',
    #     y_ticks = linspace(0, 0.8, 9),
    #     y_lim = (-0.065, 0.865)
    # )
    # custom_panel = figure.add_panel(
    #     name = 'custom',
    #     title = 'Demonstration - saturated_color_paths.chromaticity_within_gamut\ncustom',
    #     position = (0.5, 0, 0.5, 1),
    #     x_label = 'x',
    #     x_ticks = linspace(0, 0.8, 9),
    #     x_lim = (-0.065, 0.865),
    #     y_label = 'y',
    #     y_ticks = linspace(0, 0.8, 9),
    #     y_lim = (-0.065, 0.865)
    # )
    # for panel in figure.panels.values():
    #     panel.set_aspect(
    #         aspect = 'equal', # Make horizontal and vertical axes the same scale
    #         adjustable = 'box' # Change the plot area aspect ratio to achieve this
    #     )
    #     panel.plot(
    #         list(datum['x'] for datum in spectrum_locus),
    #         list(datum['y'] for datum in spectrum_locus),
    #         color = figure.grey_level(0.75),
    #         zorder = 1
    #     )
    # paths, colors = chromaticity_within_gamut()
    # srgb_panel.add_collection(
    #     PathCollection(
    #         paths,
    #         facecolors = colors,
    #         edgecolors = colors,
    #         zorder = 0
    #     )
    # )
    # paths, colors = chromaticity_within_gamut(
    #     resolution = 64,
    #     coefficients = rgb_to_xyz
    # )
    # custom_panel.add_collection(
    #     PathCollection(
    #         paths,
    #         facecolors = colors,
    #         edgecolors = colors,
    #         zorder = 0
    #     )
    # )
    # figure.update()
    # figure.save(
    #     path = 'images',
    #     name = figure.name,
    #     extension = 'svg'
    # )
    # figure.close()
    # endregion

    # region chromaticity_outside_gamut
    # figure = Figure(
    #     name = 'Demonstration - saturated_color_paths chromaticity_outside_gamut',
    #     size = (16, 9),
    #     inverted = True
    # )
    # srgb_panel = figure.add_panel(
    #     name = 'srgb',
    #     title = 'Demonstration - saturated_color_paths.chromaticity_within_gamut\nsRGB',
    #     position = (0, 0, 0.5, 1),
    #     x_label = 'x',
    #     x_ticks = linspace(0, 0.8, 9),
    #     x_lim = (-0.065, 0.865),
    #     y_label = 'y',
    #     y_ticks = linspace(0, 0.8, 9),
    #     y_lim = (-0.065, 0.865)
    # )
    # custom_panel = figure.add_panel(
    #     name = 'custom',
    #     title = 'Demonstration - saturated_color_paths.chromaticity_within_gamut\ncustom',
    #     position = (0.5, 0, 0.5, 1),
    #     x_label = 'x',
    #     x_ticks = linspace(0, 0.8, 9),
    #     x_lim = (-0.065, 0.865),
    #     y_label = 'y',
    #     y_ticks = linspace(0, 0.8, 9),
    #     y_lim = (-0.065, 0.865)
    # )
    # for panel in figure.panels.values():
    #     panel.set_aspect(
    #         aspect = 'equal', # Make horizontal and vertical axes the same scale
    #         adjustable = 'box' # Change the plot area aspect ratio to achieve this
    #     )
    # paths, colors = chromaticity_outside_gamut()
    # srgb_panel.add_collection(
    #     PathCollection(
    #         paths,
    #         facecolors = colors,
    #         edgecolors = colors,
    #         zorder = 0
    #     )
    # )
    # paths, colors = chromaticity_outside_gamut(
    #     resolution = 64,
    #     coefficients = rgb_to_xyz
    # )
    # custom_panel.add_collection(
    #     PathCollection(
    #         paths,
    #         facecolors = colors,
    #         edgecolors = colors,
    #         zorder = 0
    #     )
    # )
    # figure.update()
    # figure.save(
    #     path = 'images',
    #     name = figure.name,
    #     extension = 'svg'
    # )
    # figure.close()
    # endregion

    # region three_dimensional_surface
    # figure = Figure(
    #     name = 'Demonstration - saturated_color_paths three_dimensional_surface',
    #     size = (16, 9),
    #     inverted = True
    # )
    # rgb_high_panel = figure.add_panel(
    #     name = 'rgb_high',
    #     title = 'Demonstration - saturated_color_paths.three_dimensional_surface\nRGB 1-Surface',
    #     position = (0, 0.5, 0.5, 0.5),
    #     three_dimensional = True
    # )
    # xyY_high_panel = figure.add_panel(
    #     name = 'xyY_high',
    #     title = 'Demonstration - saturated_color_paths.three_dimensional_surface\nxyY 1-Surface',
    #     position = (0, 0, 0.5, 0.5),
    #     three_dimensional = True
    # )
    # rgb_low_panel = figure.add_panel(
    #     name = 'rgb_low',
    #     title = 'Demonstration - saturated_color_paths.three_dimensional_surface\nRGB 0-Surface',
    #     position = (0.5, 0.5, 0.5, 0.5),
    #     three_dimensional = True
    # )
    # xyY_low_panel = figure.add_panel(
    #     name = 'xyY_low',
    #     title = 'Demonstration - saturated_color_paths.three_dimensional_surface\nxyY 0-Surface',
    #     position = (0.5, 0, 0.5, 0.5),
    #     three_dimensional = True
    # )
    # for panel_name in figure.panels.keys():
    #     figure.change_panel_orientation(
    #         panel_name,
    #         vertical_sign = +1,
    #         left_axis = '+y' if 'rgb' in panel_name else '-y'
    #     )
    # xyY_low_panel.view_init(0, -135)
    # for color_index in range(3):
    #     coordinates, colors = three_dimensional_surface(
    #         color_index = color_index,
    #         space_index = 0
    #     )
    #     rgb_high_panel.plot_surface(
    #         X = coordinates[0],
    #         Y = coordinates[1],
    #         Z = array(coordinates[2]),
    #         facecolors = colors,
    #         shade = False
    #     )
    #     coordinates, colors = three_dimensional_surface(
    #         color_index = color_index,
    #         space_index = 0,
    #         color_value = 0,
    #         resolution = 32
    #     )
    #     rgb_low_panel.plot_surface(
    #         X = coordinates[0],
    #         Y = coordinates[1],
    #         Z = array(coordinates[2]),
    #         facecolors = colors,
    #         shade = False
    #     )
    #     coordinates, colors = three_dimensional_surface(
    #         color_index = color_index,
    #         space_index = 1,
    #         resolution = 64
    #     )
    #     xyY_high_panel.plot_surface(
    #         X = coordinates[0],
    #         Y = coordinates[1],
    #         Z = array(coordinates[2]),
    #         facecolors = colors,
    #         shade = False
    #     )
    #     coordinates, colors = three_dimensional_surface(
    #         color_index = color_index,
    #         space_index = 1,
    #         color_value = 0,
    #         resolution = 128
    #     )
    #     xyY_low_panel.plot_surface(
    #         X = coordinates[0],
    #         Y = coordinates[1],
    #         Z = array(coordinates[2]),
    #         facecolors = colors,
    #         shade = False
    #     )
    # figure.update()
    # figure.save(
    #     path = 'images',
    #     name = figure.name,
    #     extension = 'svg'
    # )
    # figure.close()
    # endregion

# endregion
