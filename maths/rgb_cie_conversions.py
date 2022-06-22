"""
Functions converting from display RGB to CIE 1931 2-Degree tristimulus values
and back.  Additional helper functions allow conversions to and from CIE 1931
2-Degree chromoluminance as well.  Linear transform coefficients for sRGB are
used by default (applying accompanying gamma correction), but custom linear
transformation coefficients can be passed (gamma correction will be treated as
undefined and skipped with custom coefficients).
Default sRGB coefficients and gamma correction taken from:
https://en.wikipedia.org/wiki/SRGB#Transformation
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
from numpy.linalg import inv
from typing import Union, Optional, List, Tuple
from numpy import ndarray, matmul, clip
from warnings import warn
# endregion

# region Constants
"""
Linear transformation coefficients for sRGB to CIE 1931 2-Degree tristimulus
values taken from:
https://en.wikipedia.org/wiki/SRGB#From_sRGB_to_CIE_XYZ
(Gamma correction is handled within the associated function, below)
"""
SRGB_TO_XYZ = (
    (0.4124, 0.3576, 0.1805), # X_R, X_G, X_B
    (0.2126, 0.7152, 0.0722), # Y_R, Y_G, Y_B
    (0.0193, 0.1192, 0.9505) # Z_R, Z_G, Z_B
)

"""
Linear transformation coefficients for CIE 1931 2-Degree tristimulus to sRGB
values taken from:
https://en.wikipedia.org/wiki/SRGB#From_CIE_XYZ_to_sRGB
(Gamma correction is handled within the associated function, below)
"""
XYZ_TO_SRGB = inv(SRGB_TO_XYZ) # Used to minimize rounding error going back and forth
# XYZ_TO_SRGB = (
#     (3.2406, -1.5372, -0.4986), # R_X, R_Y, R_Z
#     (-0.9689, 1.8758, 0.0415), # G_X, G_Y, G_Z
#     (0.0557, -0.2040, 1.0570) # B_X, B_Y, B_Z
# )

# endregion

# region Function - Convert sRGB to CIE 1931 2-Degree Tristimulus Values
def rgb_to_tristimulus(
    red : Union[int, float],
    green : Union[int, float],
    blue : Union[int, float],
    gamma_correct : Optional[bool] = None,
    coefficients : Optional[
        Union[
            List[Union[List[float], Tuple[float, float, float]]],
            Tuple[Union[List[float], Tuple[float, float, float]]],
            ndarray
        ]
    ] = None
) -> Tuple[float, float, float]: # (X, Y, Z)

    # region Validate Arguments
    assert any(isinstance(red, valid_type) for valid_type in [int, float])
    assert 0.0 <= red <= 1.0
    assert any(isinstance(green, valid_type) for valid_type in [int, float])
    assert 0.0 <= green <= 1.0
    assert any(isinstance(blue, valid_type) for valid_type in [int, float])
    assert 0.0 <= blue <= 1.0
    if gamma_correct is None: gamma_correct = False
    assert isinstance(gamma_correct, bool)
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

    # region Gamma Correction
    if gamma_correct:
        rgb_values = list(
            value / 12.92
            if value <= 0.04045
            else (
                (value + 0.055)
                / 1.055
            ) ** 2.4
            for value in [red, green, blue]
        ) if coefficients is None else (red, green, blue)
    else:
        rgb_values = (red, green, blue)
    # endregion

    # region Return Linear Transformation
    return tuple(
        matmul(
            SRGB_TO_XYZ if coefficients is None else coefficients,
            rgb_values
        )
    )
    # endregion

# endregion

# region Function - Convert sRGB to CIE 1931 2-Degree Chromoluminance
def rgb_to_chromoluminance(
    red : Union[int, float],
    green : Union[int, float],
    blue : Union[int, float],
    gamma_correct : Optional[bool] = None,
    coefficients : Optional[
        Union[
            List[Union[List[float], Tuple[float, float, float]]],
            Tuple[Union[List[float], Tuple[float, float, float]]],
            ndarray
        ]
    ] = None
) -> Tuple[float, float, float]: # (x, y, Y)

    # region Validate Arguments
    assert any(isinstance(red, valid_type) for valid_type in [int, float])
    assert 0.0 <= red <= 1.0
    assert any(isinstance(green, valid_type) for valid_type in [int, float])
    assert 0.0 <= green <= 1.0
    assert any(isinstance(blue, valid_type) for valid_type in [int, float])
    assert 0.0 <= blue <= 1.0
    if gamma_correct is None: gamma_correct = False
    assert isinstance(gamma_correct, bool)
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

    # region Convert and Return
    tristimulus_values = rgb_to_tristimulus(
        red,
        green,
        blue,
        gamma_correct = gamma_correct,
        coefficients = coefficients
    )
    if sum(tristimulus_values) == 0: # Black, special case
        white_tristimulus = rgb_to_tristimulus(
            1.0,
            1.0,
            1.0,
            gamma_correct = gamma_correct,
            coefficients = coefficients
        )
        return(
            white_tristimulus[0]
            / sum(white_tristimulus),
            white_tristimulus[1]
            / sum(white_tristimulus),
            0.0
        )
    else:
        return (
            tristimulus_values[0]
            / sum(tristimulus_values),
            tristimulus_values[1]
            / sum(tristimulus_values),
            tristimulus_values[1]
        )
    # endregion

# endregion

# region Function Convert CIE 1931 2-Degree Tristimulus Values to sRGB
def tristimulus_to_rgb(
    X : Union[int, float],
    Y : Union[int, float],
    Z : Union[int, float],
    gamma_correct : Optional[bool] = None,
    coefficients : Optional[
        Union[
            List[Union[List[float], Tuple[float, float, float]]],
            Tuple[Union[List[float], Tuple[float, float, float]]],
            ndarray
        ]
    ] = None
) -> Tuple[float, float, float]: # (R, G, B)

    # region Validate Arguments
    assert any(isinstance(X, valid_type) for valid_type in [int, float])
    assert 0.0 <= X
    assert any(isinstance(Y, valid_type) for valid_type in [int, float])
    assert 0.0 <= Y <= 1.0
    assert any(isinstance(Z, valid_type) for valid_type in [int, float])
    assert 0.0 <= Z
    if gamma_correct is None: gamma_correct = False
    assert isinstance(gamma_correct, bool)
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

    # region Apply Linear Transformation
    srgb_values = matmul(
        XYZ_TO_SRGB if coefficients is None else coefficients,
        (X, Y, Z)
    )
    # endregion

    # region Apply Clipping and Warn if Necessary
    clipped_srgb_values = clip(srgb_values, a_min = 0.0, a_max = 1.0)
    if not all(srgb_values[index] == clipped_srgb_values[index] for index in range(3)):
        warn('sRGB Values have been clipped and are not a valid conversion!')
    # endregion

    # region Return with Gamma Correction
    if gamma_correct:
        return tuple(
            12.92 * value
            if value <= (0.04045 / 12.92) # (0.0031308) Used to minimize rounding error going back and forth
            else 1.055 * (value ** (1.0 / 2.4)) - 0.055
            for value in clipped_srgb_values
        ) if coefficients is None else clipped_srgb_values
    else:
        return clipped_srgb_values
    # endregion

# endregion

# region Function - Convert CIE 1931 2-Degree Chromoluminance to sRGB
def chromoluminance_to_rgb(
    x : Union[int, float],
    y : Union[int, float],
    Y : Union[int, float],
    gamma_correct : Optional[bool] = None,
    coefficients : Optional[
        Union[
            List[Union[List[float], Tuple[float, float, float]]],
            Tuple[Union[List[float], Tuple[float, float, float]]],
            ndarray
        ]
    ] = None
) -> Tuple[float, float, float]: # (R, G, B)

    # region Validate Arguments
    assert any(isinstance(x, valid_type) for valid_type in [int, float])
    assert 0.0 <= x <= 1.0
    assert any(isinstance(y, valid_type) for valid_type in [int, float])
    assert 0.0 < y <= 1.0
    assert any(isinstance(Y, valid_type) for valid_type in [int, float])
    assert 0.0 <= Y <= 1.0
    if gamma_correct is None: gamma_correct = False
    assert isinstance(gamma_correct, bool)
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

    # region Convert and Return
    return tristimulus_to_rgb(
        Y * (x / y), # X
        Y,
        Y * ((1 - x - y) / y), # Z
        gamma_correct = gamma_correct,
        coefficients = coefficients
    )
    # endregion

# endregion

# region Demonstration
if __name__ == '__main__':

    red = 1.0
    green = 1.0
    blue = 1.0
    gamma_correct = True

    tristimulus_values = rgb_to_tristimulus(red, green, blue, gamma_correct = gamma_correct)
    chromoluminance_values = rgb_to_chromoluminance(red, green, blue, gamma_correct = gamma_correct)
    rgb_from_tristimulus = tristimulus_to_rgb(*tristimulus_values, gamma_correct = gamma_correct)
    rgb_from_chromoluminance = chromoluminance_to_rgb(*chromoluminance_values, gamma_correct = gamma_correct)

    print('\nOriginal RGB: ({0:0.2f}, {1:0.2f}, {2:0.2f})'.format(red, green, blue))
    print('Tristimulus Values: ({0:0.4f}, {1:0.4f}, {2:0.4f})'.format(*tristimulus_values))
    print('Chromoluminance Values: ({0:0.4f}, {1:0.4f}, {2:0.4f})'.format(*chromoluminance_values))
    print('RGB from Tristimulus:  ({0:0.2f}, {1:0.2f}, {2:0.2f})'.format(*rgb_from_tristimulus))
    print('RGB from Chromoluminance:  ({0:0.2f}, {1:0.2f}, {2:0.2f})\n'.format(*rgb_from_chromoluminance))

    print( # Invalid chromoluminance, outside of gamut, generates warning
        chromoluminance_to_rgb(
            0.01,
            0.01,
            0.5
        )
    )

    rgb_to_xyz = ( # Taken from CRT display
        (0.0455, 0.0369, 0.0282),
        (0.0256, 0.0708, 0.0184),
        (0.0023, 0.0106, 0.1484)
    )
    xyz_to_rgb = inv(rgb_to_xyz)
    tristimulus_values = rgb_to_tristimulus(red, green, blue, gamma_correct = gamma_correct, coefficients = rgb_to_xyz)
    chromoluminance_values = rgb_to_chromoluminance(red, green, blue, gamma_correct = gamma_correct, coefficients = rgb_to_xyz)
    rgb_from_tristimulus = tristimulus_to_rgb(*tristimulus_values, gamma_correct = gamma_correct, coefficients = xyz_to_rgb)
    rgb_from_chromoluminance = chromoluminance_to_rgb(*chromoluminance_values, gamma_correct = gamma_correct, coefficients = xyz_to_rgb)
    print('\nWith arbitrary linear transformation coefficients:')
    print('Tristimulus Values: ({0:0.4f}, {1:0.4f}, {2:0.4f})'.format(*tristimulus_values))
    print('Chromoluminance Values: ({0:0.4f}, {1:0.4f}, {2:0.4f})'.format(*chromoluminance_values))
    print('RGB from Tristimulus:  ({0:0.2f}, {1:0.2f}, {2:0.2f})'.format(*rgb_from_tristimulus))
    print('RGB from Chromoluminance:  ({0:0.2f}, {1:0.2f}, {2:0.2f})'.format(*rgb_from_chromoluminance))

# endregion
