"""
A large CIE 1931 Chromaticity Diagram with all of the decorations.
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
    PAPER_WIDTH, PAPER_HEIGHT,
    FONT_SIZES
)
from maths.plotting_series import (
    spectrum_locus_1931_2,
    gamut_triangle_vertices_srgb
)
from numpy import arange, transpose, pi

from figure.figure import Figure
from maths.coloration import (
    chromaticity_outside_gamut,
    chromaticity_inside_gamut
)
from matplotlib.collections import PathCollection
from maths.color_temperature import (
    generate_temperature_series,
    isotherm_endpoints_from_temperature
)
from maths.color_conversion import uv_to_xy
from maths.functions import intersection_of_two_segments
from maths.conversion_coefficients import COLOR_NAMES
from maths.chromaticity_conversion import (
    COPUNCTAL_POINTS,
    chromaticity_rectangular_to_polar,
    D65_WHITE,
    chromaticity_polar_to_rectangular
)
# endregion

# region Plot Settings
INVERTED = False
SIZE = (
    PAPER_WIDTH,
    PAPER_HEIGHT
)
EXTENSION = 'pdf'
RESOLUTION = 16
TEMPERATURES = [2000, 3000, 4000, 5000, 7000, 10000, 20000]
# endregion

# region Constants
WAVELENGTH_TICKS = list(
    int(tick)
    for tick in [
        spectrum_locus_1931_2[0]['Wavelength']
    ] + [
        400,
        450
    ] + list(arange(475, 601, 5, dtype = int)) + [
        610,
        625,
        650
    ] + [
        spectrum_locus_1931_2[-1]['Wavelength']
    ]
)
# endregion

# region Initialize Figure
figure = Figure(
    name = 'figure_00_title_background{0}'.format(
        '_inverted' if INVERTED else ''
    ),
    size = SIZE,
    inverted = INVERTED
)
figure.set_fonts(**FONT_SIZES)
panel = figure.add_panel(
    name = 'main',
    title = '',
    position = (0.1, 0.1, 0.8, 0.7),
    x_label = '',
    x_ticks = [],
    x_lim = (-0.175, 0.975),
    y_label = '',
    y_ticks = [],
    y_lim = (-0.175, 0.975)
)
panel.set_aspect(
    aspect = 'equal', # Make horizontal and vertical axes the same scale
    adjustable = 'box' # Change the plot area aspect ratio to achieve this
)
panel.axis('off')
# endregion

# region Background Grid Lines
for x in arange(-0.1, 0.91, 0.1):
    panel.plot(
        2 * [x],
        [-0.125, 0.925],
        linewidth = 1 if x == 0.0 else 0.5,
        color = figure.grey_level(0.8 if x == 0.0 else 0.9),
        solid_capstyle = 'round',
        zorder = 0
    )
    for y in [-0.135, 0.935]:
        panel.annotate(
            text = '{0:0.1f}'.format(x),
            xy = (x, y),
            xycoords = 'data',
            horizontalalignment = 'center',
            verticalalignment = 'center',
            fontsize = figure.font_sizes['ticks'],
            color = figure.grey_level(0.7 if x == 0.0 else 0.8),
            zorder = 0
        )
for y in [-0.16, 0.96]:
    panel.annotate(
        text = r'$x$',
        xy = (0.4, y),
        xycoords = 'data',
        horizontalalignment = 'center',
        verticalalignment = 'center',
        fontsize = figure.font_sizes['labels'],
        color = figure.grey_level(0.6),
        zorder = 0
    )
for y in arange(-0.1, 0.91, 0.1):
    panel.plot(
        [-0.125, 0.925],
        2 * [y],
        linewidth = 1 if y == 0.0 else 0.5,
        color = figure.grey_level(0.8 if y == 0.0 else 0.9),
        solid_capstyle = 'round',
        zorder = 0
    )
    for x in [-0.145, 0.945]:
        panel.annotate(
            text = '{0:0.1f}'.format(y),
            xy = (x, y),
            xycoords = 'data',
            horizontalalignment = 'center',
            verticalalignment = 'center',
            fontsize = figure.font_sizes['ticks'],
            color = figure.grey_level(0.7 if y == 0.0 else 0.8),
            zorder = 0
        )
for x in [-0.174, 0.974]:
    panel.annotate(
        text = r'$y$',
        xy = (x, 0.4),
        xycoords = 'data',
        horizontalalignment = 'center',
        verticalalignment = 'center',
        fontsize = figure.font_sizes['labels'],
        color = figure.grey_level(0.6),
        zorder = 0
    )
panel.plot(
    [1.0 - 0.925, 0.925],
    [0.925, 1.0 - 0.925],
    linestyle = '--',
    color = figure.grey_level(0.8),
    solid_capstyle = 'round',
    dash_capstyle = 'round',
    zorder = 0
)
panel.annotate(
    text = r'$y+x=1$',
    xy = (
        0.925 + 0.01,
        1 - 0.925
    ),
    xycoords = 'data',
    horizontalalignment = 'left',
    verticalalignment = 'center',
    fontsize = figure.font_sizes['legends'],
    color = figure.grey_level(0.7),
    zorder = 0
)
# endregion

# region Fill Colors
paths, colors = chromaticity_outside_gamut(
    RESOLUTION * 6
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
paths, colors = chromaticity_inside_gamut(
    RESOLUTION
)
panel.add_collection(
    PathCollection(
        paths,
        facecolors = colors,
        edgecolors = colors,
        linewidth = 0.1,
        zorder = 2
    )
)
# endregion

# region sRGB Display Gamut
panel.plot(
    *transpose(
        list(
            (
                gamut_triangle_vertices_srgb[COLOR_NAMES[index]]['x'],
                gamut_triangle_vertices_srgb[COLOR_NAMES[index]]['y']
            )
            for index in [0, 1, 2, 0]
        )
    ),
    color = 3 * [0.75],
    solid_joinstyle = 'round',
    zorder = 4
)
# endregion

# region Planckian Locus and Isotherm Lines
_, pl_chromaticities = generate_temperature_series()
panel.plot(
    *transpose(pl_chromaticities),
    color = 3 * [0.6],
    solid_capstyle = 'round',
    zorder = 5
)
for temperature in TEMPERATURES:
    endpoints = isotherm_endpoints_from_temperature(temperature)
    endpoints = tuple(
        uv_to_xy(*endpoint)
        for endpoint in endpoints
    )
    endpoints = sorted(endpoints, key = lambda pair: pair[1])
    diagonal_intersection = intersection_of_two_segments(
        *endpoints,
        (0, 1),
        (1, 0)
    )
    if not (
        min([endpoints[0][0], endpoints[1][0]])
        <= diagonal_intersection[0]
        <= max([endpoints[0][0], endpoints[1][0]])
    ):
        panel.plot(
            *transpose(endpoints),
            color = 3 * [0.5],
            solid_capstyle = 'round',
            zorder = 5
        )
        panel.annotate(
            text = '{0:,}'.format(temperature),
            xy = (
                endpoints[1][0] - 0.001,
                endpoints[1][1] + 0.001
            ),
            xycoords = 'data',
            horizontalalignment = 'right',
            verticalalignment = 'bottom',
            fontsize = figure.font_sizes['legends'],
            color = 3 * [0.5],
            zorder = 5
        )
    else:
        panel.plot(
            [endpoints[0][0], diagonal_intersection[0]],
            [endpoints[0][1], diagonal_intersection[1]],
            color = 3 * [0.5],
            solid_capstyle = 'round',
            zorder = 5
        )
        panel.plot(
            [endpoints[1][0], diagonal_intersection[0]],
            [endpoints[1][1], diagonal_intersection[1]],
            color = figure.grey_level(0.9),
            linewidth = 0.5,
            solid_capstyle = 'round',
            zorder = 5
        )
        panel.annotate(
            text = '{0:,}'.format(temperature),
            xy = (
                endpoints[0][0] + 0.001,
                endpoints[0][1] - 0.001
            ),
            xycoords = 'data',
            horizontalalignment = 'left',
            verticalalignment = 'top',
            fontsize = figure.font_sizes['legends'],
            color = 3 * [0.5],
            zorder = 5
        )
panel.annotate(
    text = r'$\infty$',
    xy = (
        pl_chromaticities[-1][0] - 0.001,
        pl_chromaticities[-1][1] - 0.001
    ),
    xycoords = 'data',
    horizontalalignment = 'right',
    verticalalignment = 'top',
    fontsize = figure.font_sizes['labels'],
    color = 3 * [0.3],
    zorder = 5
)
# endregion

# region Spectrum Locus
panel.plot(
    list(datum['x'] for datum in spectrum_locus_1931_2),
    list(datum['y'] for datum in spectrum_locus_1931_2),
    color = figure.grey_level(0.6),
    solid_capstyle = 'round',
    zorder = 6
)
panel.plot(
    [spectrum_locus_1931_2[0]['x'], spectrum_locus_1931_2[-1]['x']],
    [spectrum_locus_1931_2[0]['y'], spectrum_locus_1931_2[-1]['y']],
    linestyle = '--',
    color = figure.grey_level(0.6),
    solid_capstyle = 'round',
    dash_capstyle = 'round',
    zorder = 6
)
figure.annotate_coordinates(
    name = 'main',
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
    font_size = figure.font_sizes['legends'],
    font_color = figure.grey_level(0.6),
    tick_color = figure.grey_level(0.6),
    z_order = 6
)
# endregion

# region Copunctal Point and Confusion Lines (3)
for cone_index, (cone_name, copunctal_point) in enumerate(COPUNCTAL_POINTS.items()):
    for angle in [-pi / 16, 0.0, pi / 16]:
        white_angle, white_radius = chromaticity_rectangular_to_polar(
            *D65_WHITE,
            center = cone_name
        )
        datum_point = chromaticity_polar_to_rectangular(
            white_angle + (angle if cone_index != 1 else angle / 2.0),
            white_radius,
            center = cone_name
        )
        sl_intersection = intersection_of_two_segments(
            copunctal_point,
            datum_point,
            (spectrum_locus_1931_2[0]['x'], spectrum_locus_1931_2[0]['y']),
            (spectrum_locus_1931_2[-1]['x'], spectrum_locus_1931_2[-1]['y'])
        )
        panel.plot(
            [copunctal_point[0], sl_intersection[0]],
            [copunctal_point[1], sl_intersection[1]],
            linewidth = 0.5,
            color = tuple(
                value if index != cone_index else (1.0 if not INVERTED else 0.5)
                for index, value in enumerate(figure.grey_level(0.7))
            ),
            solid_capstyle = 'round',
            zorder = 1
        )
        near_gamut_intersection = intersection_of_two_segments(
            copunctal_point,
            datum_point,
            (gamut_triangle_vertices_srgb['Red']['x'], gamut_triangle_vertices_srgb['Red']['y']),
            (gamut_triangle_vertices_srgb['Blue']['x'], gamut_triangle_vertices_srgb['Blue']['y'])
        )
        panel.plot(
            [sl_intersection[0], near_gamut_intersection[0]],
            [sl_intersection[1], near_gamut_intersection[1]],
            linewidth = 0.5,
            color = tuple(
                0.5 if index != cone_index else 1.0
                for index in range(3)
            ),
            solid_capstyle = 'round',
            zorder = 3
        )
        far_gamut_intersections = tuple(
            intersection_of_two_segments(
                copunctal_point,
                datum_point,
                (gamut_triangle_vertices_srgb['Green']['x'], gamut_triangle_vertices_srgb['Green']['y']),
                (gamut_triangle_vertices_srgb[second_primary]['x'], gamut_triangle_vertices_srgb[second_primary]['y'])
            )
            for second_primary in ['Blue', 'Red']
        )
        far_gamut_intersection = (
            far_gamut_intersections[0]
            if (
                gamut_triangle_vertices_srgb['Blue']['x']
                <= far_gamut_intersections[0][0]
                <= gamut_triangle_vertices_srgb['Green']['x']
            )
            else far_gamut_intersections[1]
        )
        for index, datum in enumerate(spectrum_locus_1931_2):
            if index == 0: continue
            sl_intersection = intersection_of_two_segments(
                copunctal_point,
                datum_point,
                (spectrum_locus_1931_2[index]['x'], spectrum_locus_1931_2[index]['y']),
                (spectrum_locus_1931_2[index - 1]['x'], spectrum_locus_1931_2[index - 1]['y'])
            )
            if (
                min([spectrum_locus_1931_2[index]['y'], spectrum_locus_1931_2[index - 1]['y']])
                <= sl_intersection[1]
                <= max([spectrum_locus_1931_2[index]['y'], spectrum_locus_1931_2[index - 1]['y']])
            ):
                break
        panel.plot(
            [far_gamut_intersection[0], sl_intersection[0]],
            [far_gamut_intersection[1], sl_intersection[1]],
            linewidth = 0.5,
            color = tuple(
                0.5 if index != cone_index else 1.0
                for index in range(3)
            ),
            solid_capstyle = 'round',
            zorder = 3
        )
    panel.plot(
        *copunctal_point,
        linestyle = 'none',
        marker = 'o',
        markersize = 4,
        markeredgecolor = 'none',
        markerfacecolor = tuple(
            value if index != cone_index else (1.0 if not INVERTED else 0.5)
            for index, value in enumerate(figure.grey_level(0.7))
        ),
        zorder = 3
    )
    panel.annotate(
        text = '{0}-cone Copunctal Point\n({1:0.3f}, {2:0.3f}){3}'.format(
            r'${0}$'.format(cone_name[0]),
            *copunctal_point,
            r' $\searrow$' if cone_index == 1 else ''
        ),
        xy = (
            copunctal_point[0]
            + (0.01 if cone_index == 0 else 0.03)
            if cone_index != 1
            else 0.925,
            copunctal_point[1]
            if cone_index != 1
            else 1 - 0.925 - 0.001
        ),
        xycoords = 'data',
        horizontalalignment = 'left' if cone_index != 1 else 'right',
        verticalalignment = 'center' if cone_index != 1 else 'top',
        fontsize = figure.font_sizes['legends'],
        color = tuple(
            value if index != cone_index else (1.0 if not INVERTED else 0.5)
            for index, value in enumerate(figure.grey_level(0.7))
        ),
        zorder = 3
    )
# endregion

# region Save Figure
figure.update(
    buffer = 0
)
figure.save(
    path = 'images',
    name = figure.name,
    extension = EXTENSION
)
figure.close()
# endregion
