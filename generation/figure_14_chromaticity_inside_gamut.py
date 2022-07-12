"""
Plot chromaticity diagram coloring the interior of the display color gamut (with
gamma-correction applied).

Caption: Top-down view of the sRGB color gamut transformed into chromoluminance
space (here two-dimensional chromaticity) which effectively fills the display
color gamut with color.
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
    AXES_GREY_LEVEL, DOTTED_GREY_LEVEL, SL_GREY_LEVEL
)
from figure.figure import Figure
from numpy import arange
from maths.plotting_series import spectrum_locus_1931_2
from maths.coloration import chromaticity_inside_gamut
from matplotlib.collections import PathCollection
# endregion

# region Plot Settings
INVERTED = False
SIZE = (
    COLUMN_WIDTH,
    3.45
)
EXTENSION = 'pdf'
RESOLUTION = 16
# endregion

# region Initialize Figure
figure = Figure(
    name = 'figure_14_chromaticity_inside_gamut{0}'.format(
        '_inverted' if INVERTED else ''
    ),
    size = SIZE,
    inverted = INVERTED
)
figure.set_fonts(**FONT_SIZES)
panel = figure.add_panel(
    name = 'main',
    title = '',
    x_label = r'$x$',
    x_ticks = arange(0, 0.81, 0.1),
    x_lim = (-0.065, 0.865),
    y_label = r'$y$',
    y_ticks = arange(0, 0.81, 0.1),
    y_lim = (-0.065, 0.865)
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
    zorder = 0
)
panel.axvline(
    x = 0,
    linewidth = 2,
    color = figure.grey_level(AXES_GREY_LEVEL),
    zorder = 0
)
panel.plot(
    [0, 1],
    [1, 0],
    linestyle = ':',
    color = figure.grey_level(DOTTED_GREY_LEVEL),
    zorder = 0
)
panel.plot(
    list(datum['x'] for datum in spectrum_locus_1931_2),
    list(datum['y'] for datum in spectrum_locus_1931_2),
    solid_capstyle = 'round',
    color = figure.grey_level(SL_GREY_LEVEL),
    zorder = 2
)
panel.plot(
    [spectrum_locus_1931_2[0]['x'], spectrum_locus_1931_2[-1]['x']],
    [spectrum_locus_1931_2[0]['y'], spectrum_locus_1931_2[-1]['y']],
    solid_capstyle = 'round',
    linestyle = ':',
    color = figure.grey_level(SL_GREY_LEVEL),
    zorder = 1
)
# endregion

# region Fill Colors
paths, colors = chromaticity_inside_gamut(
    RESOLUTION,
    apply_gamma_correction = True
)
panel.add_collection(
    PathCollection(
        paths,
        facecolors = colors,
        edgecolors = colors,
        linewidth = 0.1,
        zorder = 3
    )
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
