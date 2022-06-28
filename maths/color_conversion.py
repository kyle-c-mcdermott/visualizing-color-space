"""
Conversion functions between the various color spaces.  Largely employs linear
transformations using coefficients in conversion_coefficients.py.
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
from typing import Union, Optional, Tuple
from maths.conversion_coefficients import (
    RGB_TO_LMS_10, # rgb_to_lms()
    RGB_TO_UNSCALED_LMS_10, # rgb_to_lms()
    LMS_TO_RGB_10, # lms_to_rgb()
    UNSCALED_LMS_TO_RGB_10, # lms_to_rgb()
    LMS_TO_XYZ_2, # lms_to_xyz()
    LMS_TO_XYZ_10, # lms_to_xyz()
    XYZ_TO_LMS_2, # xyz_to_lms()
    XYZ_TO_LMS_10, # xyz_to_lms()
    XYZ_TO_RGB_CRT_10, # xyz_to_rgb()
    XYZ_TO_RGB_CUSTOM_INTERIOR, # xyz_to_rgb()
    XYZ_TO_RGB_CUSTOM_EXTERIOR, # xyz_to_rgb()
    XYZ_TO_SRGB_2, # xyz_to_rgb()
    RGB_TO_XYZ_CRT_10, # rgb_to_xyz()
    RGB_TO_XYZ_CUSTOM_INTERIOR, # rgb_to_xyz()
    RGB_TO_XYZ_CUSTOM_EXTERIOR, # rgb_to_xyz()
    SRGB_TO_XYZ_2 # rgb_to_xyz()
)
from numpy import matmul, around
from numpy.linalg import inv
from warnings import warn
# endregion

# region Constants
class DISPLAY(Enum):
    SRGB = 'srgb'
    CRT = 'crt'
    INTERIOR = 'interior'
    EXTERIOR = 'exterior'
# endregion

# region Between Experimental Primaries (RGB) and Cone Fundamentals (LMS)
def rgb_to_lms(
    red : Union[int, float],
    green : Union[int, float],
    blue : Union[int, float],
    normalize_fundamentals : Optional[bool] = None # default True
) -> Tuple[float, float, float]: # long, medium, short
    """
    Convert from experimental observer settings (Stiles & Burch 1959) to
    unscaled or scaled (normalized) cone fundamentals.
    Allowing int for arguments as there are foreseeable occasions where triplets
    like (1, 0, 0) may be requested
    """

    # Validate Arguments
    assert any(isinstance(red, valid_type) for valid_type in [int, float])
    assert any(isinstance(green, valid_type) for valid_type in [int, float])
    assert any(isinstance(blue, valid_type) for valid_type in [int, float])
    if normalize_fundamentals is None: normalize_fundamentals = True
    assert isinstance(normalize_fundamentals, bool)

    # Convert by Linear Transformation
    if normalize_fundamentals:
        lms = matmul(
            RGB_TO_LMS_10,
            (red, green, blue)
        )
    else:
        lms = matmul(
            RGB_TO_UNSCALED_LMS_10,
            (red, green, blue)
        )

    # Return
    return tuple(float(value) for value in lms)

def lms_to_rgb(
    long : float,
    medium : float,
    short : float,
    normalize_fundamentals : Optional[bool] = None # default True
) -> Tuple[float, float, float]: # red, green, blue
    """
    Convert from unscaled or scaled (normalized) cone fundamentals to
    experimental observer settings (Stiles & Burch 1959).  Included for
    completeness but not likely to see use.
    """

    # Validate Arguments
    assert isinstance(long, float)
    assert 0.0 <= long
    assert isinstance(medium, float)
    assert 0.0 <= medium
    assert isinstance(short, float)
    assert 0.0 <= short
    if normalize_fundamentals is None: normalize_fundamentals = True
    assert isinstance(normalize_fundamentals, bool)
    if normalize_fundamentals:
        assert long <= 1.0
        assert medium <= 1.0
        assert short <= 1.0

    # Convert by Linear Transformation
    if normalize_fundamentals:
        rgb = matmul(
            LMS_TO_RGB_10,
            (long, medium, short)
        )
    else:
        rgb = matmul(
            UNSCALED_LMS_TO_RGB_10,
            (long, medium, short)
        )

    # Return
    return tuple(float(value) for value in rgb)

# endregion

# region Between Cone Fundamentals (LMS) and Color Matching Functions (XYZ)
def lms_to_xyz(
    long : float,
    medium : float,
    short : float,
    use_2_degree : Optional[bool] = None # default True
) -> Tuple[float, float, float]: # X, Y, Z
    """
    Convert from cone fundamentals to color matching functions using either the
    CIE 1931 2-Degree Standard (see description in conversion_coefficients.py
    for LMS_TO_XYZ_2) (default) or the CIE 170-2 / 2012 10-Degree Standard (see
    description in conversion_coefficients.py for LMS_TO_XYZ_10).
    """

    # Validate Arguments
    assert isinstance(long, float)
    assert 0.0 <= long <= 1.0
    assert isinstance(medium, float)
    assert 0.0 <= medium <= 1.0
    assert isinstance(short, float)
    assert 0.0 <= short <= 1.0
    if use_2_degree is None: use_2_degree = True
    assert isinstance(use_2_degree, bool)

    # Convert by Linear Transformation
    if use_2_degree:
        xyz = matmul(
            LMS_TO_XYZ_2,
            (long, medium, short)
        )
    else:
        xyz = matmul(
            LMS_TO_XYZ_10,
            (long, medium, short)
        )

    # Return
    return tuple(float(value) for value in xyz)

def xyz_to_lms(
    X : float, # Using upper case as it is an important distinction among these functions
    Y : float,
    Z : float,
    use_2_degree : Optional[bool] = None # default True
) -> Tuple[float, float, float]: # long, medium, short
    """
    Convert from color matching functions to cone fundamentals using either the
    CIE 1931 2-Degree Standard (see description in conversion_coefficients.py
    for XYZ_TO_LMS_2) (default) or the CIE 170-2 / 2012 10-Degree Standard (see
    description in conversion_coefficients.py for XYZ_TO_LMS_10).
    """

    # Validate Arguments
    assert isinstance(X, float)
    assert 0.0 <= X
    assert isinstance(Y, float)
    assert 0.0 <= Y
    assert isinstance(Z, float)
    assert 0.0 <= Z
    if use_2_degree is None: use_2_degree = True
    assert isinstance(use_2_degree, bool)

    # Convert by Linear Transformation
    if use_2_degree:
        lms = matmul(
            XYZ_TO_LMS_2,
            (X, Y, Z)
        )
    else:
        lms = matmul(
            XYZ_TO_LMS_10,
            (X, Y, Z)
        )

    # Return
    return tuple(float(value) for value in lms)

# endregion

# region Between Color Matching Functions (XYZ) and Chromoluminance (xyY)
def xyz_to_xyy(
    X : float, # Using upper case as it is an important distinction among these functions
    Y : float,
    Z : float,
    display : Optional[str] = None # default srgb
) -> Tuple[float, float, float]: # x, y, Y
    """
    Straightfoward conversion from tristimulus values to chromoluminance.
    Display is used only to determine chromaticity for black (technically
    undefined, but set to white chromaticity for convenience)
    """

    # Validate Argumnets
    assert isinstance(X, float)
    assert 0.0 <= X
    assert isinstance(Y, float)
    assert 0.0 <= Y
    assert isinstance(Z, float)
    assert 0.0 <= Z
    if display is None: display = DISPLAY.SRGB.value
    assert isinstance(display, str)
    assert any(display == valid.value for valid in DISPLAY)

    # Select Coefficients
    if display == DISPLAY.CRT.value:
        coefficients = RGB_TO_XYZ_CRT_10
    elif display == DISPLAY.INTERIOR.value:
        coefficients = RGB_TO_XYZ_CUSTOM_INTERIOR
    elif display == DISPLAY.EXTERIOR.value:
        coefficients = RGB_TO_XYZ_CUSTOM_EXTERIOR
    else: # default sRGB
        coefficients = SRGB_TO_XYZ_2

    # Return
    return (
        (
            X / (X + Y + Z),
            Y / (X + Y + Z),
            Y
        )
        if X + Y + Z > 0.0
        else (
            sum(coefficients[0]) / sum(list(sum(row) for row in coefficients)),
            sum(coefficients[1]) / sum(list(sum(row) for row in coefficients)),
            0.0
        )
    )

def xyy_to_xyz(
    x : float,
    y : float,
    Y : float, # Using upper case as it is an important distinction among these functions
) -> Tuple[float, float, float]: # X, Y, Z
    """
    Straightforward conversion from chromoluminance to tristimulus values.
    """

    # Validate Arguments
    assert isinstance(x, float)
    assert 0.0 <= x <= 1.0
    assert isinstance(y, float)
    assert 0.0 < y <= 1.0
    assert isinstance(Y, float)
    assert 0.0 <= Y

    # Return
    return (
        Y * (x / y), # X
        Y,
        Y * ((1.0 - x - y) / y) # Z
    )

# endregion

# region Between Color Matching Functions (XYZ) and Display Colors (RGB)
def xyz_to_rgb(
    X : float, # Using upper case as it is an important distinction among these functions
    Y : float,
    Z : float,
    display : Optional[str] = None, # default srgb
    apply_gamma_correction : Optional[bool] = None, # default False
    suppress_warnings : Optional[bool] = None # default False
) -> Tuple[float, float, float]: # red, green, blue
    """
    Convert from color matching functions to display colors.
    display must come from the Display enum
    apply_gamma_correction = True only has effect when display = srgb
    suppress_warnings will ignore chromaticity outside gamut or luminance
    outside range (note that either one will cause invalid RGB values, but also
    both warnings might fail to trip if the chromaticity is inside the gamut and
    the luminance is between black and white, yet too dim or - more likely - too
    bright for the specific chromaticity)
    """

    # Validate Argumnets
    assert isinstance(X, float)
    assert isinstance(Y, float)
    assert isinstance(Z, float)
    if display is None: display = DISPLAY.SRGB.value
    assert isinstance(display, str)
    assert any(display == valid.value for valid in DISPLAY)
    if apply_gamma_correction is None: apply_gamma_correction = False
    assert isinstance(apply_gamma_correction, bool)
    if suppress_warnings is None: suppress_warnings = False
    assert isinstance(suppress_warnings, bool)

    # Select Coefficients
    if display == DISPLAY.CRT.value:
        coefficients = XYZ_TO_RGB_CRT_10
    elif display == DISPLAY.INTERIOR.value:
        coefficients = XYZ_TO_RGB_CUSTOM_INTERIOR
    elif display == DISPLAY.EXTERIOR.value:
        coefficients = XYZ_TO_RGB_CUSTOM_EXTERIOR
    else: # default sRGB
        coefficients = XYZ_TO_SRGB_2

    # More Validation (using exterior display primaries skips these)
    if all(coefficient >= 0.0 for coefficient in coefficients[0]):
        assert 0.0 <= X
    if all(coefficient >= 0.0 for coefficient in coefficients[1]):
        assert 0.0 <= Y
    if all(coefficient >= 0.0 for coefficient in coefficients[2]):
        assert 0.0 <= Z

    # (Check Validity of Coordinates within Origin Space)
    if not suppress_warnings:
        if apply_gamma_correction and display != DISPLAY.SRGB.value:
            warn('xyz_to_rgb() - Cannot Apply Gamma Correction when display is not sRGB!')
        if display != DISPLAY.EXTERIOR.value:
            x_r, y_r = xyz_to_xyy(*tuple(inv(coefficients)[index][0] for index in range(3)))[0:2]
            x_g, y_g = xyz_to_xyy(*tuple(inv(coefficients)[index][1] for index in range(3)))[0:2]
            x_b, y_b = xyz_to_xyy(*tuple(inv(coefficients)[index][2] for index in range(3)))[0:2]
            def is_inside(x, y):
                def area(x1, y1, x2, y2, x3, y3):
                    return abs(
                        (
                            x1 * (y2 - y3)
                            + x2 * (y3 - y1)
                            + x3 * (y1 - y2)
                        )
                        / 2.0
                    )
                a = area(x_r, y_r, x_g, y_g, x_b, y_b)
                a1 = area(x, y, x_g, y_g, x_b, y_b)
                a2 = area(x_r, y_r, x, y, x_b, y_b)
                a3 = area(x_r, y_r, x_g, y_g, x, y)
                return around(a, 6) == around(a1 + a2 + a3, 6)
            if not is_inside(*xyz_to_xyy(X, Y, Z)[0:2]):
                warn('xyz_to_rgb() - Chromaticity Outside Gamut!')
        else:
            warn('xyz_to_rgb() - Within Gamut Check Skipped for Exterior Primaries')
        if Y > sum(inv(coefficients)[1]):
            warn('xyz_to_rgb() - Luminance Higher than Maximum (white)!')

    # Convert by Linear Transformation
    rgb = matmul(
        coefficients,
        (X, Y, Z)
    )

    # (Apply Gamma Correction)
    """
    Gamma correction piecewise function taken from:
    https://en.wikipedia.org/wiki/SRGB
    """
    if display == DISPLAY.SRGB.value and apply_gamma_correction:
        rgb = tuple(
            12.92 * value
            if value <= (0.04045 / 12.92) # (0.0031308)
            else 1.055 * (value ** (1.0 / 2.4)) - 0.055
            for value in rgb
        )

    # (Check Validity of RGB Values)
    if not suppress_warnings:
        if any((value < 0.0 or value > 1.0) for value in rgb):
            warn('xyz_to_rgb() - Red, Green, and/or Blue Values Outside the Interval [0, 1]!')

    # Return
    return tuple(float(abs(around(value, 8))) for value in rgb)
    # abs() applied because otherwise sometimes returns -0.0 for saturated values

def rgb_to_xyz(
    red : Union[int, float],
    green : Union[int, float],
    blue : Union[int, float],
    display : Optional[str] = None, # default srgb
    apply_gamma_correction : Optional[bool] = None, # default False
    suppress_warnings : Optional[bool] = None # default False
) -> Tuple[float, float, float]: # X, Y, Z
    """
    Convert from display colors to color matching functions.
    display must come from the Display enum
    apply_gamma_correction = True only has effect when display = srgb
    Allowing int arguments as saturated values (0, or 1) are commonly requested
    """

    # Validate Arguments
    assert any(isinstance(red, valid_type) for valid_type in [int, float])
    assert 0.0 <= red <= 1.0
    assert any(isinstance(green, valid_type) for valid_type in [int, float])
    assert 0.0 <= green <= 1.0
    assert any(isinstance(blue, valid_type) for valid_type in [int, float])
    assert 0.0 <= blue <= 1.0
    if display is None: display = DISPLAY.SRGB.value
    assert isinstance(display, str)
    assert any(display == valid.value for valid in DISPLAY)
    if apply_gamma_correction is None: apply_gamma_correction = False
    assert isinstance(apply_gamma_correction, bool)
    if suppress_warnings is None: suppress_warnings = False
    assert isinstance(suppress_warnings, bool)
    if not suppress_warnings:
        if apply_gamma_correction and display != DISPLAY.SRGB.value:
            warn('rgb_to_xyz() - Cannot Apply Gamma Correction when display is not sRGB!')

    # Select Coefficients
    if display == DISPLAY.CRT.value:
        coefficients = RGB_TO_XYZ_CRT_10
    elif display == DISPLAY.INTERIOR.value:
        coefficients = RGB_TO_XYZ_CUSTOM_INTERIOR
    elif display == DISPLAY.EXTERIOR.value:
        coefficients = RGB_TO_XYZ_CUSTOM_EXTERIOR
    else: # default sRGB
        coefficients = SRGB_TO_XYZ_2

    # (Apply Gamma Correction)
    if display == DISPLAY.SRGB.value and apply_gamma_correction:
        red, green, blue = tuple(
            value / 12.92
            if value <= 0.04045
            else (
                (value + 0.055)
                / 1.055
            ) ** 2.4
            for value in (red, green, blue)
        )

    # Convert by Linear Transformation
    xyz = matmul(
        coefficients,
        (red, green, blue)
    )

    # Return
    return tuple(float(around(value, 8)) for value in xyz)

# endregion

# region Between CIE 1931 (x, y) Chromaticity and CIE 1960 (u, v) Chromaticity
def xy_to_uv(
    x : float,
    y : float
) -> Tuple[float, float]: # u, v
    """
    Using MacAdam's simplified expressions for conversion:
    https://en.wikipedia.org/wiki/CIE_1960_color_space
    """

    # Validate Arguments
    assert isinstance(x, float)
    assert 0.0 <= x <= 1.0
    assert isinstance(y, float)
    assert 0.0 < y <= 1.0

    # Convert and Return
    return(
        (4.0 * x)
        / (12.0 * y - 2.0 * x + 3),
        (6.0 * y)
        / (12.0 * y - 2.0 * x + 3)
    )

def uv_to_xy(
    u : float,
    v : float
) -> Tuple[float, float]: # x, y
    """
    Using MacAdam's simplified expressions for conversion:
    https://en.wikipedia.org/wiki/CIE_1960_color_space
    """

    # Validate Arguments
    assert isinstance(u, float)
    assert 0.0 <= u <= 1.0
    assert isinstance(v, float)
    assert 0.0 <= v <= 1.0

    # Convert and Return
    return (
        (3.0 * u)
        / (2.0 * u - 8.0 * v + 4),
        (2.0 * v)
        / (2.0 * u - 8.0 * v + 4)
    )

# endregion
