"""
Generate values for table illustrating changes in color with arbitrary
manipulations of l-cone activation.

Caption: Varying the long-wavelength-sensitive cone activation (L column) while
holding the others constant and its effects on display color.
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
    if 'generation' not in folders:
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
from maths.color_conversion import (
    xyz_to_lms,
    rgb_to_xyz,
    xyz_to_rgb,
    lms_to_xyz
)
# endregion

# region Generate Values
start_color = (0.5, 0.5, 0.5)
start_cone_activation = xyz_to_lms(
    *rgb_to_xyz(
        *start_color
    ),
    use_2_degree = True
)
print('\nTable Values:')
for multiple in [0.85, 0.925, 1.0, 1.075, 1.15]:
    cone_activation = (
        multiple * start_cone_activation[0],
        *start_cone_activation[1:]
    )
    color = xyz_to_rgb(
        *lms_to_xyz(
            *cone_activation,
            use_2_degree = True
        )
    )
    print(
        'L = {0:0.4f}, M = {1:0.4f}, S = {2:0.4f}, R = {3:0.4f}, G = {4:0.4f}, B = {5:0.4f}'.format(
            *cone_activation,
            *color
        )
    )
# endregion
