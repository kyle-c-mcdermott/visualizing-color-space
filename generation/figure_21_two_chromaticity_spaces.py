"""
CIE 1931 (x, y) and CIE 1960 (u, v) chromaticity with wavelengths annotated and
unadorned Planckian locus.

Caption: CIE 1931 (x, y) (left) and CIE 1960 (u, v) (right) chromaticity
diagrams.  The sRGB color gamut triangle is present in both diagrams along with
the Planckian locus.
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
    TEXT_WIDTH,
    FONT_SIZES,
    DOTTED_GREY_LEVEL, AXES_GREY_LEVEL, SL_GREY_LEVEL
)
from maths.plotting_series import (
    spectrum_locus_1931_2,
    gamut_triangle_vertices_srgb
)
from numpy import arange, transpose
from figure.figure import Figure
from maths.color_conversion import xy_to_uv
from maths.coloration import (
    chromaticity_outside_gamut,
    chromaticity_inside_gamut
)
from matplotlib.collections import PathCollection
from matplotlib.path import Path
from maths.conversion_coefficients import COLOR_NAMES
from maths.color_temperature import generate_temperature_series
# endregion

# region Plot Settings
INVERTED = False
SIZE = (
    TEXT_WIDTH,
    3.45
)
EXTENSION = 'pdf'
RESOLUTION = 16
# endregion

# region Constants
WAVELENGTH_TICKS = list(
    int(tick)
    for tick in [
        spectrum_locus_1931_2[0]['Wavelength']
    ] + [
        400,
        450
    ] + list(arange(475, 501, 5, dtype = int)) + list(arange(510, 611, 10)) + [
        625,
        650
    ] + [
        spectrum_locus_1931_2[-1]['Wavelength']
    ]
    if tick != 530
)
# endregion

# region Initialize Figure
figure = Figure(
    name = 'figure_21_two_chromaticity_spaces{0}'.format(
        '_inverted' if INVERTED else ''
    ),
    size = SIZE,
    inverted = INVERTED
)
figure.set_fonts(**FONT_SIZES)
xy_panel = figure.add_panel(
    name = 'xy',
    title = '',
    position = (0, 0, 0.5, 1),
    x_label = r'$x$',
    x_ticks = arange(0, 0.81, 0.1),
    x_lim = (-0.065, 0.865),
    y_label = r'$y$',
    y_ticks = arange(0, 0.81, 0.1),
    y_lim = (-0.065, 0.865)
)
uv_panel = figure.add_panel(
    name = 'uv',
    title = '',
    position = (0.5, 0, 0.5, 1),
    x_label = r'$u$',
    x_ticks = arange(0, 0.61, 0.1),
    x_lim = (-0.05, 0.7),
    y_label = r'$v$',
    y_ticks = arange(0, 0.41, 0.1),
    y_lim = (-0.2, 0.55)
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
        color = figure.grey_level(DOTTED_GREY_LEVEL),
        zorder = 1
    )
    panel.axvline(
        x = 0,
        linewidth = 2,
        color = figure.grey_level(DOTTED_GREY_LEVEL),
        zorder = 1
    )
xy_panel.plot(
    [0, 1],
    [1, 0],
    linestyle = ':',
    color = figure.grey_level(DOTTED_GREY_LEVEL),
    zorder = 1
)
uv_panel.plot(
    *transpose(list(xy_to_uv(x, y) for x, y in [(0.0, 1.0), (1.0, 0.0)])),
    linestyle = ':',
    color = figure.grey_level(DOTTED_GREY_LEVEL),
    zorder = 1
)
xy_panel.plot(
    list(datum['x'] for datum in spectrum_locus_1931_2),
    list(datum['y'] for datum in spectrum_locus_1931_2),
    solid_capstyle = 'round',
    color = figure.grey_level(AXES_GREY_LEVEL),
    zorder = 3
)
uv_panel.plot(
    *transpose(
        list(
            xy_to_uv(datum['x'], datum['y'])
            for datum in spectrum_locus_1931_2
        )
    ),
    solid_capstyle = 'round',
    color = figure.grey_level(AXES_GREY_LEVEL),
    zorder = 3
)
xy_panel.plot(
    [spectrum_locus_1931_2[0]['x'], spectrum_locus_1931_2[-1]['x']],
    [spectrum_locus_1931_2[0]['y'], spectrum_locus_1931_2[-1]['y']],
    solid_capstyle = 'round',
    color = figure.grey_level(AXES_GREY_LEVEL),
    linestyle = ':',
    zorder = 2
)
uv_panel.plot(
    *transpose(
        [
            xy_to_uv(spectrum_locus_1931_2[0]['x'], spectrum_locus_1931_2[0]['y']),
            xy_to_uv(spectrum_locus_1931_2[-1]['x'], spectrum_locus_1931_2[-1]['y'])
        ]
    ),
    solid_capstyle = 'round',
    color = figure.grey_level(AXES_GREY_LEVEL),
    linestyle = ':',
    zorder = 2
)
# endregion

# region Color Fill
paths, colors = chromaticity_outside_gamut(
    RESOLUTION * 6
)
xy_panel.add_collection(
    PathCollection(
        paths,
        facecolors = colors,
        edgecolors = colors,
        linewidth = 0.1,
        zorder = 0
    )
)
uv_panel.add_collection(
    PathCollection(
        list(
            Path(
                list(
                    xy_to_uv(*coordinate)
                    for coordinate in path.vertices
                )
            )
            for path in paths
        ),
        facecolors = colors,
        edgecolors = colors,
        linewidth = 0.1,
        zorder = 0
    )
)
paths, colors = chromaticity_inside_gamut(
    RESOLUTION
)
xy_panel.add_collection(
    PathCollection(
        paths,
        facecolors = colors,
        edgecolors = colors,
        linewidth = 0.1,
        zorder = 1
    )
)
uv_panel.add_collection(
    PathCollection(
        list(
            Path(
                list(
                    xy_to_uv(*coordinate)
                    for coordinate in path.vertices
                )
            )
            for path in paths
        ),
        facecolors = colors,
        edgecolors = colors,
        linewidth = 0.1,
        zorder = 1
    )
)
# endregion

# region Annotate Wavelengths
figure.annotate_coordinates(
    name = 'xy',
    coordinates = list(
        (
            datum['x'],
            datum['y']
        )
        for datum in spectrum_locus_1931_2
        if datum['Wavelength'] in WAVELENGTH_TICKS
    ),
    coordinate_labels = WAVELENGTH_TICKS,
    omit_endpoints = True,
    distance_proportion = 0.0075,
    show_ticks = True,
    font_size = figure.font_sizes['legends'] - 2,
    font_color = figure.grey_level(0),
    tick_color = figure.grey_level(AXES_GREY_LEVEL),
    z_order = 4
)
figure.annotate_coordinates(
    name = 'uv',
    coordinates = list(
        xy_to_uv(datum['x'], datum['y'])
        for datum in spectrum_locus_1931_2
        if datum['Wavelength'] in WAVELENGTH_TICKS
    ),
    coordinate_labels = WAVELENGTH_TICKS,
    omit_endpoints = True,
    distance_proportion = 0.0075,
    show_ticks = True,
    font_size = figure.font_sizes['legends'] - 2,
    font_color = figure.grey_level(0),
    tick_color = figure.grey_level(AXES_GREY_LEVEL),
    z_order = 4
)
# endregion

# region sRGB Color Gamut
xy_panel.plot(
    *transpose(
        list(
            (
                gamut_triangle_vertices_srgb[COLOR_NAMES[index]]['x'],
                gamut_triangle_vertices_srgb[COLOR_NAMES[index]]['y']
            )
            for index in [0, 1, 2, 0]
        )
    ),
    color = 3 * [SL_GREY_LEVEL],
    zorder = 2
)
uv_panel.plot(
    *transpose(
        list(
            xy_to_uv(
                gamut_triangle_vertices_srgb[COLOR_NAMES[index]]['x'],
                gamut_triangle_vertices_srgb[COLOR_NAMES[index]]['y']
            )
            for index in [0, 1, 2, 0]
        )
    ),
    color = 3 * [SL_GREY_LEVEL],
    zorder = 2
)
# endregion

# region Planckian Locus
pl_temperatures, pl_chromaticities = generate_temperature_series()
xy_panel.plot(
    *transpose(pl_chromaticities),
    solid_capstyle = 'round',
    color = 3 * [0.25],
    zorder = 3
)
xy_panel.annotate(
    text = r'$\infty$',
    xy = (
        pl_chromaticities[-1][0] - 0.005,
        pl_chromaticities[-1][1] - 0.005
    ),
    xycoords = 'data',
    horizontalalignment = 'right',
    verticalalignment = 'top',
    fontsize = figure.font_sizes['legends'],
    color = 3 * [0.25],
    zorder = 4
)
uv_panel.plot(
    *transpose(
        list(
            xy_to_uv(*chromaticity)
            for chromaticity in pl_chromaticities
        )
    ),
    solid_capstyle = 'round',
    color = 3 * [0.25],
    zorder = 3
)
uv_panel.annotate(
    text = r'$\infty$',
    xy = xy_to_uv(
        pl_chromaticities[-1][0] - 0.005,
        pl_chromaticities[-1][1] - 0.005
    ),
    xycoords = 'data',
    horizontalalignment = 'center',
    verticalalignment = 'top',
    fontsize = figure.font_sizes['legends'],
    color = 3 * [0.25],
    zorder = 4
)
# endregion

# region Save Figure
figure.update(
    buffer = 2
)
figure.save(
    path = 'images',
    name = figure.name,
    extension = EXTENSION
)
figure.close()
# endregion
