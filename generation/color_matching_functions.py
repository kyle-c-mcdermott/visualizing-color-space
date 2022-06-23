"""
Plot the Color Matching Functions.

Figure Caption:
5 - Color Matching Functions for the 10-degree stimulus.  The Y function is the
luminous efficiency function scaled to peak at 1.  The Z function is the s-cone
fundamental scaled to have the same area as Y.  X is constrained to be as close
to the CIE 1964 standard while having all positive values and the same area as
the other two functions.
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

# region Settings
INVERTED = False
SIZE = (16, 9)
FONT_SIZES = {
    'titles' : 16,
    'labels' : 14,
    'ticks' : 12,
    'legends' : 8
}
WAVELENGTH_BOUNDS = (385, 720)
COLORS = (
    (0.75, 0, 0.75), # X
    (1, 0.5, 0), # Y
    (0, 0, 1) # Z
)
EXTENSION = 'svg'
# endregion

# region Imports
from csv import DictReader
from figure.figure import Figure
from numpy import arange
# endregion

# region Constants
FUNCTION_NAMES = ['X', 'Y', 'Z']
# endregion

# region Load in Data
with open(
    'data/color_matching_functions.csv',
    'r'
) as read_file:
    color_matching_functions = list(
        {
            'Wavelength' : int(row['Wavelength']),
            **{
                function_name : float(row[function_name])
                for function_name in FUNCTION_NAMES
            }
        }
        for row in DictReader(read_file)
    )
# endregion

# region Figure 5 - Color Matching Functions

# region Initialize Figure
figure = Figure(
    name = 'Color Matching Functions{0}'.format(
        ' (inverted)' if INVERTED else ''
    ),
    size = SIZE,
    inverted = INVERTED
)
figure.set_fonts(**FONT_SIZES)
panel = figure.add_panel(
    name = 'main',
    title = r'CIE 170-2 10$\degree$ Color Matching Functions',
    x_label = r'Wavelength $\lambda$ (nm)',
    x_lim = WAVELENGTH_BOUNDS,
    x_ticks = arange(400, 701, 25),
    y_label = 'Function Value (Y arbitrarily set to peak at 1.0)'
)
# endregion

# region Reference
panel.axhline(
    y = 0,
    linewidth = 2,
    color = figure.grey_level(0),
    zorder = 0
)
panel.axhline(
    y = 1,
    linewidth = 2,
    color = figure.grey_level(0.75),
    zorder = 0
)
# endregion

# region Plot Color Matching Functions
legend_handles = list()
for function_index, function_name in enumerate(FUNCTION_NAMES):
    legend_handles.append(
        panel.plot(
            list(datum['Wavelength'] for datum in color_matching_functions),
            list(datum[function_name] for datum in color_matching_functions),
            color = COLORS[function_index],
            linewidth = 2,
            zorder = 1
        )[0]
    )
panel.legend(
    legend_handles,
    list(
        'Color Matching Function {0}'.format(function_name)
        for function_name in FUNCTION_NAMES
    ),
    loc = 'upper right',
    facecolor = figure.grey_level(1)
)
# endregion

# region Save Figure
figure.update()
figure.save(
    path = 'images',
    name = figure.name,
    extension = EXTENSION
)
figure.close()
# endregion

# endregion
