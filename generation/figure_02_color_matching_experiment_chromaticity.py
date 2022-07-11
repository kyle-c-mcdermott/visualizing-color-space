"""
Individual observer and mean settings converted to experiment chromaticity.

Caption:  Individual (faded) and average (bold) settings converted to
experimental chromaticity.  Note that the settings between 19,000 cm^-1 (green)
and 22,500 cm^-1 (blue) where the red setting is negative extend up and left
relatively far, and that the individual variability here is also magnified.
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
from generation.constants import (
    COLUMN_WIDTH,
    FONT_SIZES,
    AXES_GREY_LEVEL, DOTTED_GREY_LEVEL
)
from figure.figure import Figure
from numpy import arange
from maths.plotting_series import (
    color_matching_experiment_individual_settings,
    color_matching_experiment_mean_settings
)
from maths.conversion_coefficients import COLOR_NAMES
# endregion

# region Plot Settings
INVERTED = False
SIZE = (
    COLUMN_WIDTH,
    2.9 # Adjusted down until plot area width was forced in
)
EXTENSION = 'pdf'
# endregion

# region Initialize Figure
figure = Figure(
    name = 'figure_02_color_matching_experiment_chromaticity{0}'.format(
        '_inverted' if INVERTED else ''
    ),
    size = SIZE,
    inverted = INVERTED
)
figure.set_fonts(**FONT_SIZES)
panel = figure.add_panel(
    name = 'main',
    title = '',
    x_label = r'$r$',
    x_ticks = arange(-6, 1.1, 1),
    y_label = r'$g$',
    y_ticks = arange(0, 5.1, 1)
)
panel.set_aspect(
    aspect = 'equal', # Make horizontal and vertical axes the same scale
    adjustable = 'box' # Change the plot area aspect ratio to achieve this
)
# endregion

# region Reference Lines
panel.axhline(
    y = 0,
    linewidth = 2,
    color = figure.grey_level(AXES_GREY_LEVEL),
    zorder = 1
)
panel.axhline(
    y = 1,
    linestyle = ':',
    color = figure.grey_level(DOTTED_GREY_LEVEL),
    zorder = 1
)
panel.axvline(
    x = 0,
    linewidth = 2,
    color = figure.grey_level(AXES_GREY_LEVEL),
    zorder = 1
)
panel.axvline(
    x = 1,
    linestyle = ':',
    color = figure.grey_level(DOTTED_GREY_LEVEL),
    zorder = 1
)
# endregion

# region Plot Individual Observer Settings
for observer_index in range(int(len(color_matching_experiment_individual_settings[0]) / 3.0)):
    panel.plot(
        list(
            datum['{0:02.0f}-Red'.format(observer_index)]
            / sum(
                list(
                    datum['{0:02.0f}-{1}'.format(observer_index, color_name)]
                    for color_name in COLOR_NAMES
                )
            )
            for datum in color_matching_experiment_individual_settings
        ),
        list(
            datum['{0:02.0f}-Green'.format(observer_index)]
            / sum(
                list(
                    datum['{0:02.0f}-{1}'.format(observer_index, color_name)]
                    for color_name in COLOR_NAMES
                )
            )
            for datum in color_matching_experiment_individual_settings
        ),
        color = figure.grey_level(0.9),
        zorder = 0
    )
# endregion

# region Plot Primary Coordinates
for x, y, color in [
    (1, 0, (1, 0, 0)),
    (0, 1, (0, 1, 0)),
    (0, 0, (0, 0, 1))
]:
    panel.plot(
        x,
        y,
        linestyle = 'none',
        marker = 'o',
        markersize = 8,
        markerfacecolor = 'none',
        markeredgecolor = color,
        zorder = 2
    )
# endregion

# region Plot Mean Observer Settings
panel.plot(
    list(
        datum['Red'] / sum(list(datum[color_name] for color_name in COLOR_NAMES))
        for datum in color_matching_experiment_mean_settings
    ),
    list(
        datum['Green'] / sum(list(datum[color_name] for color_name in COLOR_NAMES))
        for datum in color_matching_experiment_mean_settings
    ),
    color = figure.grey_level(0.2),
    marker = 'o',
    markersize = 4,
    markeredgecolor = 'none',
    markerfacecolor = figure.grey_level(0),
    zorder = 3
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
