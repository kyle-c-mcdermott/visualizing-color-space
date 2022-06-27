"""
Useful functions with no other specific home.

intersection_of_two_segments() - Returns the intersection of two non-parallel
lines defined by the endpoints of two segments
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
from typing import Union, List, Tuple
from numpy import vstack, hstack, ones, cross
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
