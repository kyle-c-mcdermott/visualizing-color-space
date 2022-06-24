"""
Functions for deriving copunctal points from color-blindness confusion lines.
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
from typing import Union, Tuple, List
from numpy import matmul, vstack, hstack, ones, cross
from maths.rgb_cie_conversions import (
    rgb_to_tristimulus,
    tristimulus_to_rgb
)

# endregion

# region Constants
"""
10-Degree Color Matching Function Conversion Coefficients detailed here:
http://www.cvrl.org/database/text/cienewxyz/cie2012xyz10.htm
Y_L and Y_M taken from Sharpe et al (2011)
PDF available here:
http://www.cvrl.org/people/Stockman/pubs/2011%20Vstar%20correction%20SSJJ.pdf
Z_S simply scales the s-cone cone fundamental to have the same integral (1.0) as
the Y color matching function; said coefficient is in Stockman, Sharpe & Fach (1999)
The X coefficients are credited to Jan Henrik Wold but there is no citation given.
"""
# LMS_TO_XYZ = [
#     [1.93986443, -1.34664359, 0.43044935], # X_L, X_M, X_S
#     [0.69283932, 0.34967567, 0.00000000], # Y_L, Y_M, Y_S
#     [0.00000000, 0.00000000, 2.14687945] # Z_L, Z_M, Z_S
# ]
# XYZ_TO_LMS = inv(LMS_TO_XYZ)


# 2-Degree Observer Conversion Matrix for XYZ to LMS (Smith & Pokorny 1975)
# http://www.cvrl.org/database/text/cones/sp.htm
XYZ_TO_LMS = [
    [00.15514, 0.54312, -0.03286],
    [-0.15514, 0.45684, 00.03286],
    [00.00000, 0.00000, 00.00801]
]
LMS_TO_XYZ = inv(XYZ_TO_LMS)
# endregion

# region Functions - Conversions between Cone Activation and Tristimulus Values
def xyz_to_lms(
    X : float,
    Y : float,
    Z : float
) -> Tuple[float, float, float]:

    # Validate Arguments
    """
    We will not here enforce that tristimulus values be positive because we want
    to be able to perform conversions outside of the spectrum locus while
    plotting confusion lines out to the copunctal points.
    """
    assert isinstance(X, float)
    assert isinstance(Y, float)
    assert isinstance(Z, float)

    # Convert
    cone_activations = matmul(
        XYZ_TO_LMS,
        (X, Y, Z)
    )

    # Return
    return tuple(float(value) for value in cone_activations)

def lms_to_xyz(
    L : float,
    M : float,
    S : float
) -> Tuple[float, float, float]:

    # Validate Arguments
    """
    We will not here enforce that cone activation values be positive because we
    want to be able to perform conversions outside of the spectrum locus while
    plotting confusion lines out to the copunctal points.
    """
    assert isinstance(L, float)
    assert isinstance(M, float)
    assert isinstance(S, float)

    # Convert
    tristimulus_values = matmul(
        LMS_TO_XYZ,
        (L, M, S)
    )

    # Return
    return tuple(float(value) for value in tristimulus_values)

# endregion

# region Functions - Conversions between Cone Activations and sRGB
def rgb_to_lms(
    red : Union[int, float],
    green : Union[int, float],
    blue : Union[int, float]
) -> Tuple[float, float, float]:

    # Validate Arguments
    assert any(isinstance(red, valid_type) for valid_type in [int, float])
    assert 0.0 <= red <= 1.0
    assert any(isinstance(green, valid_type) for valid_type in [int, float])
    assert 0.0 <= green <= 1.0
    assert any(isinstance(blue, valid_type) for valid_type in [int, float])
    assert 0.0 <= blue <= 1.0

    # Convert to XYZ
    tristimulus_values = rgb_to_tristimulus(
        red,
        green,
        blue,
        gamma_correct = True
    )

    # Convert to LMS
    cone_activations = xyz_to_lms(*tristimulus_values)

    # Return
    return tuple(float(value) for value in cone_activations)

def lms_to_rgb(
    L : float,
    M : float,
    S : float
) -> Tuple[float, float, float]:

    # Validate Arguments
    assert isinstance(L, float)
    assert 0.0 <= L
    assert isinstance(M, float)
    assert 0.0 <= M
    assert isinstance(S, float)
    assert 0.0 <= S

    # Convert to XYZ
    tristimulus_values = lms_to_xyz(L, M, S)

    # Convert to RGB
    rgb = tristimulus_to_rgb(
        *tristimulus_values,
        gamma_correct = True
    )

    # Return
    return rgb

# endregion

# region Function - Intersection of Two Line Segments
def intersection_two_segments(
    a1 : Union[List[Union[int, float]], Tuple[Union[int, float], Union[int, float]]], # 1st Point on Segment A
    a2 : Union[List[Union[int, float]], Tuple[Union[int, float], Union[int, float]]], # 2nd Point on Segment A
    b1 : Union[List[Union[int, float]], Tuple[Union[int, float], Union[int, float]]], # 1st Point on Segment B
    b2 : Union[List[Union[int, float]], Tuple[Union[int, float], Union[int, float]]] #  2nd Point on Segment B
) -> Tuple[float, float]: # Intersection Point (of infinitely extended lines), (inf, inf) if parallel
    """
    Adapted from https://stackoverflow.com/questions/3252194/numpy-and-line-intersections
    Elegantly handles both vertical lines (infinite slope) and parallel segments.
    """

    # region Validate Arguments
    assert any(isinstance(a1, valid_type) for valid_type in [list, tuple])
    assert len(a1) == 2
    assert all(any(isinstance(value, valid_type) for valid_type in [int, float]) for value in a1)
    assert any(isinstance(a2, valid_type) for valid_type in [list, tuple])
    assert len(a2) == 2
    assert all(any(isinstance(value, valid_type) for valid_type in [int, float]) for value in a2)
    assert any(isinstance(b1, valid_type) for valid_type in [list, tuple])
    assert len(b1) == 2
    assert all(any(isinstance(value, valid_type) for valid_type in [int, float]) for value in b1)
    assert any(isinstance(b2, valid_type) for valid_type in [list, tuple])
    assert len(b2) == 2
    assert all(any(isinstance(value, valid_type) for valid_type in [int, float]) for value in b2)
    # endregion

    # region Estimate and Return Intersection
    stacked = vstack([a1, a2, b1, b2]) # Puts four coordinates in a vertical stack
    homogeneous = hstack((stacked, ones((4, 1)))) # Converts coordinate pairs to triplets each ending with a 1
    first_line = cross(homogeneous[0], homogeneous[1]) # Linear equation from Segment A
    second_line = cross(homogeneous[2], homogeneous[3]) # Linear equation from Segment B
    x, y, z = cross(first_line, second_line) # Intersection point
    if z == 0:
        return float('inf'), float('inf') # parallel
    else:
        return x / z, y / z
    # endregion

# endregion


# region Demonstration
if __name__ == '__main__':

    from maths.rgb_cie_conversions import rgb_to_chromoluminance

    middle_grey_activation = rgb_to_lms(0.5, 0.5, 0.5)
    print(
        '\nMiddle Grey Cone Activations:\nL: {0:0.4f}\nM: {1:0.4f}\nS: {2:0.4f}'.format(
            *middle_grey_activation
        )
    )
    verify_conversion = lms_to_rgb(*middle_grey_activation)
    print(
        'Verified Conversion: ({0:0.4f}, {1:0.4f}, {2:0.4f})'.format(
            *verify_conversion
        )
    )

    for cone_index, cone_type in enumerate(['L', 'M', 'S']):
        print('\n{0} Cone Series:'.format(cone_type))
        for multiple in [0.85, 0.925, 1.0, 1.075, 1.15]:
            lms = list(
                middle_grey_activation[index] * multiple
                if index == cone_index
                else middle_grey_activation[index]
                for index in range(3)
            )
            rgb = lms_to_rgb(*lms)
            tristimulus = rgb_to_tristimulus(
                *rgb,
                gamma_correct = True
            )
            chromoluminance = rgb_to_chromoluminance(
                *rgb,
                gamma_correct = True
            )
            print(
                '{0:0.3f} * {1}: (L, M, S): ({2:0.4f}, {3:0.4f}, {4:0.4f}), (X, Y, Z): ({5:0.4f}, {6:0.4f}, {7:0.4f}), (x, y): ({8:0.4f}, {9:0.4f}), (R, G, B): ({10:0.3f}, {11:0.3f}, {12:0.3f}), Hex: {13}'.format(
                    multiple,
                    cone_type,
                    *lms,
                    *tristimulus,
                    *chromoluminance[0:2],
                    *rgb,
                    '%02x%02x%02x' % tuple(int(value * 255.0) for value in rgb)
                )
            )





# endregion
