"""
CIE 1931 (x, y) chromaticity with isotherm lines and standard illuminants.

Caption: CIE 1931 (x, y) chromaticity showing the same isotherm lines and
standard illuminants as in Figure X.  Note that isotherm lines are not
perpendicular to the Planckian locus and have varying lengths.
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
from numpy import arange, transpose
from maths.plotting_series import spectrum_locus_1931_2
from maths.coloration import (
    chromaticity_outside_gamut,
    chromaticity_inside_gamut
)
from matplotlib.collections import PathCollection
from maths.color_temperature import (
    generate_temperature_series,
    isotherm_endpoints_from_temperature
)
from maths.color_conversion import uv_to_xy, xyz_to_rgb, xyy_to_xyz
# endregion

# region Plot Settings
INVERTED = False
SIZE = (
    COLUMN_WIDTH,
    3.45
)
EXTENSION = 'pdf'
RESOLUTION = 16
TEMPERATURES = [2000, 3000, 4000, 5000, 7000, 10000, 20000]
# endregion

# region Constants
"""
From https://en.wikipedia.org/wiki/Standard_illuminant
"""
ILLUMINANTS_CHROMATICITY = { # (x, y)
    r'$A$' : (0.44757, 0.40745), # Incandescent / Tungsten (~2856K)
    r'$D65$' : (0.31271, 0.32902), # Daylight (~6504K)
    r'$E$' : (1 / 3, 1 / 3), # Equal Energy (~5454K)
    r'$F3$' : (0.40910, 0.39430) # White Fluorescent (~3450K)
}
# endregion

# region Initialize Figure
figure = Figure(
    name = 'figure_23_cie_1931_isotherm{0}'.format(
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
    zorder = 1
)
panel.axvline(
    x = 0,
    linewidth = 2,
    color = figure.grey_level(AXES_GREY_LEVEL),
    zorder = 1
)
panel.plot(
    [0, 1],
    [1, 0],
    linestyle = ':',
    color = figure.grey_level(DOTTED_GREY_LEVEL),
    zorder = 1
)
panel.plot(
    list(datum['x'] for datum in spectrum_locus_1931_2),
    list(datum['y'] for datum in spectrum_locus_1931_2),
    solid_capstyle = 'round',
    color = figure.grey_level(SL_GREY_LEVEL),
    zorder = 3
)
panel.plot(
    [spectrum_locus_1931_2[0]['x'], spectrum_locus_1931_2[-1]['x']],
    [spectrum_locus_1931_2[0]['y'], spectrum_locus_1931_2[-1]['y']],
    linestyle = ':',
    solid_capstyle = 'round',
    color = figure.grey_level(SL_GREY_LEVEL),
    zorder = 2
)
# endregion

# region Color Fill
paths, colors = chromaticity_outside_gamut(
    RESOLUTION * 6
)
panel.add_collection(
    PathCollection(
        paths,
        facecolors = colors,
        edgecolors = colors,
        linewidth = 0.1,
        zorder = 0
    )
)
paths, colors = chromaticity_inside_gamut(
    RESOLUTION
)
panel.add_collection(
    PathCollection(
        paths,
        facecolors = colors,
        edgecolors = colors,
        linewidth = 0.1,
        zorder = 1
    )
)
# endregion

# region Planckian Locus
pl_temperatures, pl_chromaticities = generate_temperature_series()
panel.plot(
    *transpose(pl_chromaticities),
    solid_capstyle = 'round',
    color = 3 * [0.25],
    zorder = 4
)
# endregion

# region Isotherm Lines
for temperature in TEMPERATURES:
    endpoints = isotherm_endpoints_from_temperature(temperature)
    panel.plot(
        *transpose(
            list(
                uv_to_xy(*endpoint)
                for endpoint in endpoints
            )
        ),
        solid_capstyle = 'round',
        color = 3 * [0.25],
        zorder = 5
    )
# endregion

# region Standard Illuminants
for illuminant_chromaticity in ILLUMINANTS_CHROMATICITY.values():
    color = xyz_to_rgb(
        *xyy_to_xyz(
            *illuminant_chromaticity,
            0.05 # arbitrarily low
        )
    )
    color = list(value / max(color) for value in color) # saturate
    panel.plot(
        *illuminant_chromaticity,
        linestyle = 'none',
        marker = 'o',
        markersize = 4,
        markeredgecolor = 3 * [0],
        markerfacecolor = color,
        zorder = 6
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
