"""
Plot chromaticity diagram coloring the exterior of the display color gamut.
Shows radial coloration in isolation, and with interior coloration on top.

Caption: Filling in colors outside of the color gamut triangle (but within the
CIE 1931 2-degree spectrum locus).  The method applied does not vary in color
saturation (see left panel where the central point is not white), but the
top-down view of high-saturation surfaces can be placed on top (see right
panel).  Note that the colors within the triangle in the right panel are less
saturated than the colored region outside the triangle creating a discontinuity
(i.e. the triangle edges are apparent).
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
from maths.plotting_series import spectrum_locus_1931_2
from maths.coloration import (
    chromaticity_inside_gamut,
    chromaticity_outside_gamut
)
from matplotlib.collections import PathCollection
# endregion

# region Plot Settings
INVERTED = False
SIZE = (8, 4)
FONT_SIZES = {
    'titles' : 14,
    'labels' : 12,
    'ticks' : 10,
    'legends' : 8
}
EXTENSION = 'svg'
RESOLUTION = 16
# endregion

# region Initialize Figure
figure = Figure(
    name = 'figure_15_chromaticity_outside_gamut{0}'.format(
        '_inverted' if INVERTED else ''
    ),
    size = SIZE,
    inverted = INVERTED
)
figure.set_fonts(**FONT_SIZES)
left_panel = figure.add_panel(
    name = 'left',
    title = '',
    position = (0, 0, 0.5, 1),
    x_label = 'x',
    x_ticks = arange(0, 0.81, 0.1),
    x_lim = (-0.065, 0.865),
    y_label = 'y',
    y_ticks = arange(0, 0.81, 0.1),
    y_lim = (-0.065, 0.865)
)
right_panel = figure.add_panel(
    name = 'right',
    title = '',
    position = (0.5, 0, 0.5, 1),
    x_label = 'x',
    x_ticks = arange(0, 0.81, 0.1),
    x_lim = (-0.065, 0.865),
    y_label = 'y',
    y_ticks = arange(0, 0.81, 0.1),
    y_lim = (-0.065, 0.865)
)
for panel in figure.panels.values():
    panel.set_aspect(
        aspect = 'equal', # Make horizontal and vertical axes the same scale
        adjustable = 'box' # Change the plot area aspect ratio to achieve this
    )
# endregion

# region Reference Lines
for panel in figure.panels.values():
    panel.axhline(
        y = 0,
        linewidth = 2,
        color = figure.grey_level(0.25),
        zorder = 1
    )
    panel.axvline(
        x = 0,
        linewidth = 2,
        color = figure.grey_level(0.25),
        zorder = 1
    )
    panel.plot(
        [0, 1],
        [1, 0],
        linestyle = ':',
        color = figure.grey_level(0.75),
        zorder = 1
    )
    panel.plot(
        list(datum['x'] for datum in spectrum_locus_1931_2),
        list(datum['y'] for datum in spectrum_locus_1931_2),
        color = figure.grey_level(0.5),
        zorder = 3
    )
    panel.plot(
        [spectrum_locus_1931_2[0]['x'], spectrum_locus_1931_2[-1]['x']],
        [spectrum_locus_1931_2[0]['y'], spectrum_locus_1931_2[-1]['y']],
        linestyle = ':',
        color = figure.grey_level(0.5),
        zorder = 2
    )
# endregion

# region Fill Colors
paths, colors = chromaticity_outside_gamut(
    RESOLUTION * 6
)
for panel in figure.panels.values():
    panel.add_collection(
        PathCollection(
            paths,
            facecolors = colors,
            edgecolors = colors,
            linewidth = 0,
            zorder = 0
        )
    )
paths, colors = chromaticity_inside_gamut(
    RESOLUTION,
    apply_gamma_correction = True
)
right_panel.add_collection(
    PathCollection(
        paths,
        facecolors = colors,
        edgecolors = colors,
        linewidth = 0,
        zorder = 1
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
