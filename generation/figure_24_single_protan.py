"""
Chromaticity and chromoluminance plots of a selection of colors along a single
protanope confusion line.

Caption: The colors from Table X are plotted in chromaticity space (left) and
chromoluminance space (right).  While the changes in long-wavelength-sensitive
cone activation result in a straight line path in chromaticity, there are also
changes in luminance that follow a slightly curved path.
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
    TEXT_WIDTH, TEXT_HEIGHT,
    FONT_SIZES,
    AXES_GREY_LEVEL, DOTTED_GREY_LEVEL, SL_GREY_LEVEL
)
from maths.color_conversion import (
    xyz_to_lms,
    rgb_to_xyz,
    xyz_to_rgb,
    lms_to_xyz,
    xyz_to_xyy
)
from figure.figure import Figure
from numpy import arange, transpose, linspace
from maths.plotting_series import (
    spectrum_locus_1931_2,
    gamut_triangle_vertices_srgb
)
from maths.conversion_coefficients import COLOR_NAMES
# endregion

# region Plot Settings
INVERTED = False
SIZE = (
    TEXT_WIDTH,
    TEXT_HEIGHT / 3
)
EXTENSION = 'pdf'
RESOLUTION = 64
# endregion

# region Generate Plotting Series
start_color = (0.5, 0.5, 0.5)
start_cone_activation = xyz_to_lms(
    *rgb_to_xyz(
        *start_color
    ),
    use_2_degree = True
)
colors = list()
chromoluminances = list()
for multiple in [0.85, 0.925, 1.0, 1.075, 1.15]:
    cone_activation = (
        multiple * start_cone_activation[0],
        *start_cone_activation[1:]
    )
    colors.append(
        xyz_to_rgb(
            *lms_to_xyz(
                *cone_activation,
                use_2_degree = True
            )
        )
    )
    chromoluminances.append(
        xyz_to_xyy(
            *lms_to_xyz(
                *cone_activation,
                use_2_degree = True
            )
        )
    )
# endregion

# region Initialize Figure
figure = Figure(
    name = 'figure_24_single_protan{0}'.format(
        '_inverted' if INVERTED else ''
    ),
    size = SIZE,
    inverted = INVERTED
)
figure.set_fonts(**FONT_SIZES)
mid_point = 0.46
chromaticity_panel = figure.add_panel(
    name = 'chromaticity',
    title = '',
    position = (0, 0, mid_point, 1),
    x_label = r'$x$',
    x_ticks = arange(0, 0.81, 0.1),
    x_lim = (-0.065, 0.865),
    y_label = r'$y$',
    y_ticks = arange(0, 0.81, 0.1),
    y_lim = (-0.065, 0.865)
)
chromaticity_panel.set_aspect(
    aspect = 'equal', # Make horizontal and vertical axes the same scale
    adjustable = 'box' # Change the plot area aspect ratio to achieve this
)
chromoluminance_panel = figure.add_panel(
    name = 'chromoluminance',
    title = '',
    position = (mid_point + 0.03, 0, 1 - mid_point - 0.03, 1),
    three_dimensional = True,
    x_label = r'$x$',
    x_lim = (-0.05, 1.05),
    y_label = r'$y$',
    y_lim = (-0.05, 1.05),
    z_label = r'$Y$',
    z_lim = (-0.05, 1.05)
)
chromoluminance_panel.view_init(0, -135)
figure.change_panes(
    'chromoluminance',
    x_pane_color = figure.grey_level(0.95),
    x_grid_color = figure.grey_level(0.75),
    y_pane_color = figure.grey_level(0.95),
    y_grid_color = figure.grey_level(0.75),
    z_pane_color = figure.grey_level(0.95),
    z_grid_color = figure.grey_level(0.75)
)
# endregion

# region Reference Lines
chromaticity_panel.axhline(
    y = 0,
    linewidth = 2,
    color = figure.grey_level(AXES_GREY_LEVEL),
    zorder = 0
)
chromaticity_panel.axvline(
    x = 0,
    linewidth = 2,
    color = figure.grey_level(AXES_GREY_LEVEL),
    zorder = 0
)
chromaticity_panel.plot(
    [0, 1],
    [1, 0],
    linestyle = ':',
    color = figure.grey_level(DOTTED_GREY_LEVEL),
    zorder = 0
)
for panel in figure.panels.values():
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
        linestyle = ':',
        solid_capstyle = 'round',
        color = figure.grey_level(SL_GREY_LEVEL),
        zorder = 1
    )
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
        color = figure.grey_level(DOTTED_GREY_LEVEL),
        zorder = 1
    )
color = 3 * [0.0]
for color_index in range(3):
    second_index = 1 if color_index == 0 else 0
    third_index = 1 if color_index == 2 else 2
    for second_value in range(2):
        for third_value in range(2):
            xs = list(); ys = list(); zs = list()
            for value in linspace(0, 1, RESOLUTION):
                color[color_index] = value
                color[second_index] = second_value
                color[third_index] = third_value
                x, y, Y = xyz_to_xyy(*rgb_to_xyz(*color))
                xs.append(x); ys.append(y); zs.append(Y)
            chromoluminance_panel.plot3D(
                xs,
                ys,
                zs,
                color = figure.grey_level(DOTTED_GREY_LEVEL),
                zorder = 2
            )
# endregion

# region Plot Protan Line Series
chromaticity_panel.plot(
    *transpose(
        list(
            chromoluminance[0:2]
            for chromoluminance in chromoluminances
        )
    ),
    color = figure.grey_level(0),
    zorder = 3
)
chromoluminance_panel.plot3D(
    *transpose(chromoluminances),
    color = figure.grey_level(0),
    zorder = 3
)
for index, color in enumerate(colors):
    chromaticity_panel.plot(
        *chromoluminances[index][0:2],
        linestyle = 'none',
        marker = 'o',
        markersize = 4,
        markeredgecolor = 'none',
        markerfacecolor = color,
        zorder = 4
    )
    chromoluminance_panel.plot(
        *chromoluminances[index],
        linestyle = 'none',
        marker = 'o',
        markersize = 4,
        markeredgecolor = 'none',
        markerfacecolor = color,
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
