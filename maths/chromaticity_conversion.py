"""
Conversion functions within (x, y) chromaticity space dealing with conversions
between wavelength and chromaticity coordinates in rectangular and polar (around
white) spaces and conversions between rectangular and polar coordinates centered
around the color-blind copunctal points.
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
from maths.color_conversion import rgb_to_xyz, xyz_to_xyy
from enum import Enum
from maths.plotting_series import (
    spectrum_locus_170_2_10,
    spectrum_locus_170_2_2,
    spectrum_locus_1964_10,
    spectrum_locus_1931_2
)
from numpy import arctan2, pi, cos, sin
from scipy.interpolate import interp1d
from typing import Union, Optional, Tuple
from warnings import warn
# endregion

# region Constants
D65_WHITE = xyz_to_xyy(*rgb_to_xyz(1.0, 1.0, 1.0))[0:2]
class STANDARD(Enum):
    CIE_170_2_10 = '170_2_10'
    CIE_170_2_2 = '170_2_2'
    CIE_1964_10 = '1964_10'
    CIE_1931_2 = '1931_2'
class CENTER(Enum):
    D65 = 'd65'
    LONG = 'long'
    MEDIUM = 'medium'
    SHORT = 'short'
COPUNCTAL_POINTS = { # Approximated from own calculations
    CENTER.LONG.value : (0.746, 0.254),
    CENTER.MEDIUM.value : (1.400, -0.400),
    CENTER.SHORT.value : (0.175, 0.000)
}
# endregion

# region Build Series for Interpolation
"""
Using arctan2(), the hue angles jump from -pi to pi at around 485 nm, so for
interpolation any hue angle greater than -pi / 2 is shifted down by -2 pi.  The
resulting range of hue angles is roughly in the interval [-2.1 pi, -0.7 pi].
"""
(
    spectrum_locus_angles_170_2_10,
    spectrum_locus_angles_170_2_2,
    spectrum_locus_angles_1964_10,
    spectrum_locus_angles_1931_2
) = tuple(
    list(
        arctan2(
            datum['y'] - D65_WHITE[1], # delta-y
            datum['x'] - D65_WHITE[0]
        ) if arctan2(
            datum['y'] - D65_WHITE[1], # delta-y
            datum['x'] - D65_WHITE[0]
        ) < -pi / 2 else arctan2(
            datum['y'] - D65_WHITE[1], # delta-y
            datum['x'] - D65_WHITE[0]
        ) - 2 * pi
        for datum in spectrum_locus
    )
    for spectrum_locus in [
        spectrum_locus_170_2_10,
        spectrum_locus_170_2_2,
        spectrum_locus_1964_10,
        spectrum_locus_1931_2
    ]
)
# endregion

# region Get Interpolation Bounds
(
    angle_bounds_170_2_10,
    angle_bounds_170_2_2,
    angle_bounds_1964_10,
    angle_bounds_1931_2
) = tuple(
    (
        min(spectrum_locus_angles),
        max(spectrum_locus_angles)
    )
    for spectrum_locus_angles in [
        spectrum_locus_angles_170_2_10,
        spectrum_locus_angles_170_2_2,
        spectrum_locus_angles_1964_10,
        spectrum_locus_angles_1931_2
    ]
)
(
    wavelength_bounds_170_2_10,
    wavelength_bounds_170_2_2,
    wavelength_bounds_1964_10,
    wavelength_bounds_1931_2
) = tuple(
    (
        min(list(datum['Wavelength'] for datum in spectrum_locus)),
        max(list(datum['Wavelength'] for datum in spectrum_locus))
    )
    for spectrum_locus in [
        spectrum_locus_170_2_10,
        spectrum_locus_170_2_2,
        spectrum_locus_1964_10,
        spectrum_locus_1931_2
    ]
)
# endregion

# region Build Interpolators

# region Determine x and y from Wavelength
(
    chromaticity_from_wavelength_170_2_10,
    chromaticity_from_wavelength_170_2_2,
    chromaticity_from_wavelength_1964_10,
    chromaticity_from_wavelength_1931_2
) = tuple(
    {
        coordinate : interp1d(
            list(datum['Wavelength'] for datum in spectrum_locus),
            list(datum[coordinate] for datum in spectrum_locus),
            kind = 'quadratic'
        )
        for coordinate in ['x', 'y']
    }
    for spectrum_locus in [
        spectrum_locus_170_2_10,
        spectrum_locus_170_2_2,
        spectrum_locus_1964_10,
        spectrum_locus_1931_2
    ]
)
# endregion

# region Determine Hue Angle around D65 from Wavelength and Vice Versa
(
    hue_angle_from_wavelength_170_2_10,
    hue_angle_from_wavelength_170_2_2,
    hue_angle_from_wavelength_1964_10,
    hue_angle_from_wavelength_1931_2
) = tuple(
    interp1d(
        list(datum['Wavelength'] for datum in spectrum_locus),
        spectrum_locus_angles,
        kind = 'quadratic'
    )
    for spectrum_locus, spectrum_locus_angles in [
        (spectrum_locus_170_2_10, spectrum_locus_angles_170_2_10),
        (spectrum_locus_170_2_2, spectrum_locus_angles_170_2_2),
        (spectrum_locus_1964_10, spectrum_locus_angles_1964_10),
        (spectrum_locus_1931_2, spectrum_locus_angles_1931_2)
    ]
)
(
    wavelength_from_hue_angle_170_2_10,
    wavelength_from_hue_angle_170_2_2,
    wavelength_from_hue_angle_1964_10,
    wavelength_from_hue_angle_1931_2
) = tuple(
    interp1d(
        spectrum_locus_angles,
        list(datum['Wavelength'] for datum in spectrum_locus),
        kind = 'quadratic'
    )
    for spectrum_locus, spectrum_locus_angles in [
        (spectrum_locus_170_2_10, spectrum_locus_angles_170_2_10),
        (spectrum_locus_170_2_2, spectrum_locus_angles_170_2_2),
        (spectrum_locus_1964_10, spectrum_locus_angles_1964_10),
        (spectrum_locus_1931_2, spectrum_locus_angles_1931_2)
    ]
)
# endregion

# endregion

# region Conversion Functions

# region Conversion from Wavelength to Chromaticity
def wavelength_to_chromaticity(
    wavelength : Union[int, float],
    standard : Optional[str] = None # default 1931_2
) -> Tuple[float, float]: # x, y
    """
    Use interpolation to convert from wavelength (nm) to (rectangular)
    chromaticity coordinates for the optionally specified CIE standard
    """

    # Validate Arguments
    assert any(isinstance(wavelength, valid_type) for valid_type in [int, float])
    if standard is None: standard = STANDARD.CIE_1931_2.value
    assert isinstance(standard, str)
    assert any(standard == valid.value for valid in STANDARD)

    # Select Standard
    if standard == STANDARD.CIE_170_2_10.value:
        interpolators = chromaticity_from_wavelength_170_2_10
        wavelength_bounds = wavelength_bounds_170_2_10
    elif standard == STANDARD.CIE_170_2_2.value:
        interpolators = chromaticity_from_wavelength_170_2_2
        wavelength_bounds = wavelength_bounds_170_2_2
    elif standard == STANDARD.CIE_1964_10.value:
        interpolators = chromaticity_from_wavelength_1964_10
        wavelength_bounds = wavelength_bounds_1964_10
    else:
        interpolators = chromaticity_from_wavelength_1931_2
        wavelength_bounds = wavelength_bounds_1931_2

    # More Validation
    assert wavelength_bounds[0] <= wavelength <= wavelength_bounds[1]

    # Interpolate
    x, y = tuple(
        float(interpolators[coordinate](wavelength))
        for coordinate in ['x', 'y']
    )

    # Return
    return x, y

# endregion

# region Conversions between Hue Angle and Wavelength
def wavelength_to_hue_angle(
    wavelength : Union[int, float],
    standard : Optional[str] = None, # default 1931_2
) -> float: # angle
    """
    Use interpolation to convert from wavelength to hue angle (around D65) for
    the optionally specified CIE standard
    """

    # Validate Arguments
    assert any(isinstance(wavelength, valid_type) for valid_type in [int, float])
    if standard is None: standard = STANDARD.CIE_1931_2.value
    assert isinstance(standard, str)
    assert any(standard == valid.value for valid in STANDARD)

    # Select Standard
    if standard == STANDARD.CIE_170_2_10.value:
        interpolator = hue_angle_from_wavelength_170_2_10
        wavelength_bounds = wavelength_bounds_170_2_10
    elif standard == STANDARD.CIE_170_2_2.value:
        interpolator = hue_angle_from_wavelength_170_2_2
        wavelength_bounds = wavelength_bounds_170_2_2
    elif standard == STANDARD.CIE_1964_10.value:
        interpolator = hue_angle_from_wavelength_1964_10
        wavelength_bounds = wavelength_bounds_1964_10
    else:
        interpolator = hue_angle_from_wavelength_1931_2
        wavelength_bounds = wavelength_bounds_1931_2

    # More Validation
    assert wavelength_bounds[0] <= wavelength <= wavelength_bounds[1]

    # Interpolate
    angle = float(interpolator(wavelength))

    # Return
    return angle

def hue_angle_to_wavelength(
    angle : float,
    standard : Optional[str] = None, # default 1931_2
    suppress_warnings : Optional[bool] = None # default False
) -> float: # wavelength
    """
    Use interpolation to convert from hue angle (around D65) to wavelength for
    the optionally specified standard
    """

    # Validate Arguments
    assert isinstance(angle, float)
    if standard is None: standard = STANDARD.CIE_1931_2.value
    assert isinstance(standard, str)
    assert any(standard == valid.value for valid in STANDARD)
    if suppress_warnings is None: suppress_warnings = False
    assert isinstance(suppress_warnings, bool)

    # Select Standard
    if standard == STANDARD.CIE_170_2_10.value:
        interpolator = wavelength_from_hue_angle_170_2_10
        angle_bounds = angle_bounds_170_2_10
    elif standard == STANDARD.CIE_170_2_2.value:
        interpolator = wavelength_from_hue_angle_170_2_2
        angle_bounds = angle_bounds_170_2_2
    elif standard == STANDARD.CIE_1964_10.value:
        interpolator = wavelength_from_hue_angle_1964_10
        angle_bounds = angle_bounds_1964_10
    else:
        interpolator = wavelength_from_hue_angle_1931_2
        angle_bounds = angle_bounds_1931_2

    # (Wrap Angle)
    if (-(5.0 / 2.0) * pi > angle or angle >= -pi / 2.0):
        if not suppress_warnings:
            warn('hue_angle_to_wavelength() - Angle Outside Bounds Will Be Wrapped')
        while angle < -(5.0 / 2.0) * pi:
            angle += 2.0 * pi
        while angle >= -pi / 2.0:
            angle -= 2.0 * pi

    # More Assertions
    assert angle_bounds[0] <= angle <= angle_bounds[1]

    # Interpolate
    wavelength = float(interpolator(angle))

    # Return
    return wavelength

# endregion

# region Conversions between Rectangular and Polar Coordinates in CIE 1931
"""
The same issue applies using arctan2() here, and the same rule subtracting 2 pi
from any angle greater than -pi / 2 works for the three copunctal points.  A
jump of 2 pi at some point revolving around white is unavoidable, and it may as
well be from -pi / 2 to -5pi / 2 instead of from -pi to pi (this won't be
encountered in any of the planned calculations presented).
"""
def chromaticity_rectangular_to_polar(
    x : float,
    y : float,
    center : Optional[str] = None # default d65
) -> Tuple[float, float]: # angle, radius
    """
    Trigonometric conversion from rectangular to polar coordinates with the
    optionally specified center of rotation
    """

    # Validate Arguments
    assert isinstance(x, float)
    assert 0.0 <= x <= 1.0
    assert isinstance(y, float)
    assert 0.0 < y <= 1.0
    if center is None: center = CENTER.D65.value
    assert isinstance(center, str)
    assert any(center == valid.value for valid in CENTER)

    # Select Center
    if center == CENTER.LONG.value:
        center = COPUNCTAL_POINTS['long']
    elif center == CENTER.MEDIUM.value:
        center = COPUNCTAL_POINTS['medium']
    elif center == CENTER.SHORT.value:
        center = COPUNCTAL_POINTS['short']
    else:
        center = D65_WHITE

    # Convert
    angle = float(
        arctan2(
            y - center[1], # delta-y
            x - center[0] # delta-x
        ) if arctan2(
            y - center[1], # delta-y
            x - center[0] # delta-x
        ) < -pi / 2.0 else arctan2(
            y - center[1], # delta-y
            x - center[0] # delta-x
        ) - 2.0 * pi
    )
    radius = (
        (x - center[0]) ** 2.0 # delta-x
        + (y - center[1]) ** 2.0 # delta-y
    ) ** 0.5

    # Return
    return angle, radius

def chromaticity_polar_to_rectangular(
    angle : float,
    radius : float,
    center : Optional[str] = None # default d65
) -> Tuple[float, float]: # x, y
    """
    Trigonometric conversion from polar to rectangular coordinates with the
    optionally specified center of rotation
    """

    # Validate Arguments
    assert isinstance(angle, float)
    assert isinstance(radius, float)
    if center is None: center = CENTER.D65.value
    assert isinstance(center, str)
    assert any(center == valid.value for valid in CENTER)

    # Select Center
    if center == CENTER.LONG.value:
        center = COPUNCTAL_POINTS['long']
    elif center == CENTER.MEDIUM.value:
        center = COPUNCTAL_POINTS['medium']
    elif center == CENTER.SHORT.value:
        center = COPUNCTAL_POINTS['short']
    else:
        center = D65_WHITE

    # Convert
    x = float(center[0] + radius * cos(angle))
    y = float(center[1] + radius * sin(angle))

    # Return
    return x, y

# endregion

# endregion
