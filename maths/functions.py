"""
Useful functions with no other specific home.

intersection_of_two_segments() - Returns the intersection of two non-parallel
lines defined by the endpoints of two segments
conversion_matrix() - Returns a 3x3 matrix for linear transformation between
tristimulus values (X, Y, Z) and display color (R, G, B) based on primary
chromaticities and white chromoluminance
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
from typing import Union, List, Tuple, Optional
from numpy import vstack, hstack, ones, cross
from numpy.linalg import solve
# endregion

# region Function - Intersection of Two Line Segments
def intersection_of_two_segments(
    a1 : Union[List[Union[int, float]], Tuple[Union[int, float], Union[int, float]]], # 1st Point on Segment A
    a2 : Union[List[Union[int, float]], Tuple[Union[int, float], Union[int, float]]], # 2nd Point on Segment A
    b1 : Union[List[Union[int, float]], Tuple[Union[int, float], Union[int, float]]], # 1st Point on Segment B
    b2 : Union[List[Union[int, float]], Tuple[Union[int, float], Union[int, float]]] #  2nd Point on Segment B
) -> Tuple[float, float]: # Intersection Point (of infinitely extended lines), (inf, inf) if parallel
    """
    Adapted from https://stackoverflow.com/questions/3252194/numpy-and-line-intersections
    Elegantly handles both vertical lines (infinite slope) and parallel segments
    (returns (inf, inf)).
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

# region Function - Conversion Constant Matrix from Chromaticities
def conversion_matrix(
    red_chromaticity : Union[List[float], Tuple[float, float]],
    green_chromaticity : Union[List[float], Tuple[float, float]],
    blue_chromaticity : Union[List[float], Tuple[float, float]],
    white_chromaticity : Union[List[float], Tuple[float, float]],
    white_luminance : Optional[float] = None # default 1.0
) -> Tuple[
    Tuple[float, float, float], # X_R, X_G, X_B
    Tuple[float, float, float], # Y_R, Y_G, Y_B
    Tuple[float, float, float] # Z_R, Z_G, Z_B
]:
    """
    Using substitutions and linear algebra to solve first for the luminance of
    each primary and then for the other two tristimulus values for each primary.
    """

    # region Validate Arguments
    assert any(isinstance(red_chromaticity, valid_type) for valid_type in [list, tuple])
    assert len(red_chromaticity) == 2
    assert all(isinstance(value, float) for value in red_chromaticity)
    assert red_chromaticity[1] != 0.0
    assert any(isinstance(green_chromaticity, valid_type) for valid_type in [list, tuple])
    assert len(green_chromaticity) == 2
    assert all(isinstance(value, float) for value in green_chromaticity)
    assert green_chromaticity[1] != 0.0
    assert any(isinstance(blue_chromaticity, valid_type) for valid_type in [list, tuple])
    assert len(blue_chromaticity) == 2
    assert all(isinstance(value, float) for value in blue_chromaticity)
    assert blue_chromaticity[1] != 0.0
    assert any(isinstance(white_chromaticity, valid_type) for valid_type in [list, tuple])
    assert len(white_chromaticity) == 2
    assert all(isinstance(value, float) for value in white_chromaticity)
    assert white_chromaticity[1] != 0.0
    if white_luminance is None: white_luminance = 1.0
    assert isinstance(white_luminance, float)
    assert white_luminance > 0.0
    # endregion

    # region Solve for Primary Lumiannces (Ys)
    matrix = (
        ( # Sum of Xs (=Y(x/y))
            red_chromaticity[0] / red_chromaticity[1],
            green_chromaticity[0] / green_chromaticity[1],
            blue_chromaticity[0] / blue_chromaticity[1]
        ),
        (1.0, 1.0, 1.0), # Sum of Ys
        ( # Sum of Zs (=Y((1-x-y)/y)
            (1.0 - red_chromaticity[0] - red_chromaticity[1]) / red_chromaticity[1],
            (1.0 - green_chromaticity[0] - green_chromaticity[1]) / green_chromaticity[1],
            (1.0 - blue_chromaticity[0] - blue_chromaticity[1]) / blue_chromaticity[1]
        )
    )
    vector = (
        white_luminance * (white_chromaticity[0] / white_chromaticity[1]), # X_W
        white_luminance, # Y_W
        white_luminance * ((1.0 - white_chromaticity[0] - white_chromaticity[1]) / white_chromaticity[1]) # Z_W
    )
    primary_luminances = solve(matrix, vector)
    # endregion

    # region Generate Coefficients
    coefficients = (
        ( # Xs
            primary_luminances[0] * (red_chromaticity[0] / red_chromaticity[1]),
            primary_luminances[1] * (green_chromaticity[0] / green_chromaticity[1]),
            primary_luminances[2] * (blue_chromaticity[0] / blue_chromaticity[1])
        ),
        tuple(primary_luminances), # Ys
        ( # Zs
            primary_luminances[0] * ((1.0 - red_chromaticity[0] - red_chromaticity[1]) / red_chromaticity[1]),
            primary_luminances[1] * ((1.0 - green_chromaticity[0] - green_chromaticity[1]) / green_chromaticity[1]),
            primary_luminances[2] * ((1.0 - blue_chromaticity[0] - blue_chromaticity[1]) / blue_chromaticity[1])
        )
    )
    # endregion

    # Return
    return coefficients

# endregion
