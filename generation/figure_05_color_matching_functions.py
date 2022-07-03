"""
Color Matching Functions.

Caption:
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

# region Set Font
"""
Computer Modern fonts downloaded from:
https://www.fontsquirrel.com/fonts/computer-modern
and installed to the operating system
"""
from matplotlib import rc
rc('font', family = 'serif', serif = ['CMU Serif']) # Use Computer Modern to match LaTeX
rc('mathtext', fontset = 'cm') # Likewise for math text
rc('axes', unicode_minus = False) # Fixes negative values in axes ticks
# endregion

# region Imports
from figure.figure import Figure
from numpy import arange
from maths.conversion_coefficients import TRISTIMULUS_NAMES
from maths.plotting_series import color_matching_functions_170_2_10
# endregion

# region Plot Settings
INVERTED = False
SIZE = (4, 3)
FONT_SIZES = {
    'titles' : 14,
    'labels' : 12,
    'ticks' : 10,
    'legends' : 8
}
EXTENSION = 'svg'
# endregion

# region Initialize Figure
figure = Figure(
    name = 'figure_05_color_matching_functions{0}'.format(
        '_inverted' if INVERTED else ''
    ),
    size = SIZE,
    inverted = INVERTED
)
figure.set_fonts(**FONT_SIZES)
panel = figure.add_panel(
    name = 'main',
    title = '',
    x_label = r'Wavelength $\lambda$ ($nm$)',
    x_lim = (360, 740),
    x_margin = 0.0,
    x_ticks = arange(400, 701, 50),
    y_label = 'Value'
)
# endregion

# region Reference Lines
panel.axhline(
    y = 0,
    linewidth = 2,
    color = figure.grey_level(0.25),
    zorder = 0
)
panel.axhline(
    y = 1,
    linestyle = ':',
    color = figure.grey_level(0.75),
    zorder = 0
)
# endregion

# region Plot Color Matching Functions
legend_handles = list()
for tristimulus_index, tristimulus_name in enumerate(TRISTIMULUS_NAMES):
    line_color = (
        (0.8, 0, 0.8)
        if tristimulus_index == 0
        else (
            (0.8, 0.5, 0)
            if tristimulus_index == 1
            else (0, 0, 0.8)
        )
    )
    legend_handles.append(
        panel.plot(
            list(
                datum['Wavelength']
                for datum in color_matching_functions_170_2_10
            ),
            list(
                datum[tristimulus_name]
                for datum in color_matching_functions_170_2_10
            ),
            color = line_color,
            zorder = 1
        )[0]
    )
# endregion

# region Plot Legend
panel.legend(
    legend_handles,
    [
        r'$\bar{X}(\lambda)$',
        r'$\bar{Y}(\lambda)$',
        r'$\bar{Z}(\lambda)$'
    ],
    markerfirst = False,
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
