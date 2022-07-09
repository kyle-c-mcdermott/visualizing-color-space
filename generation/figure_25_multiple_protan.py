"""
Chromaticity and chromoluminance plots of multiple, extended protanope confusion
lines.

Caption: Multiple protanope (missing long-wavelength-sensitive cone) confusion
lines plotted in chromaticity (left) and chromoluminance (right).  The point
where the chromaticity lines intersect - the copunctal point - is annotated in
the left panel.  Note that in chromoluminance space the confusion line paths
approach infinite luminance asymptotically as chromaticity goes toward the
copunctal point.
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
from maths.color_conversion import (
    xyz_to_lms,
    rgb_to_xyz,
    xyz_to_xyy,
    lms_to_xyz
)
from maths.functions import intersection_of_two_segments
from numpy import mean, arange, transpose, linspace
from figure.figure import Figure
from maths.plotting_series import (
    spectrum_locus_1931_2,
    gamut_triangle_vertices_srgb
)
from maths.conversion_coefficients import COLOR_NAMES
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
RESOLUTION = 64 # for 3D reference curves only
# endregion

# region Constants
ACTIVATION_STEP = 0.01 # Determines resolution and extent of series within the spectrum locus
# endregion

# region Generate Plotting Series
start_colors = (
    (0.5, 0.5, 0.25),
    (0.5, 0.5, 0.5),
    (0.5, 0.25, 0.5)
)
chromoluminances = list()
for start_color in start_colors:
    start_tristimulus = rgb_to_xyz(*start_color)
    start_cone_activation = xyz_to_lms(
        *start_tristimulus,
        use_2_degree = True
    )
    chromoluminance = xyz_to_xyy(*start_tristimulus)
    cone_activation = list(float(value) for value in start_cone_activation)
    row_chromoluminances = list()
    while 0.0 <= chromoluminance[0] <= 0.65: # Move down in l-cone activation
        row_chromoluminances.append(chromoluminance)
        cone_activation[0] -= ACTIVATION_STEP
        tristimulus = lms_to_xyz(
            *cone_activation,
            use_2_degree = True
        )
        if tristimulus[0] < 0.1: break
        chromoluminance = xyz_to_xyy(*tristimulus)
    chromoluminance = xyz_to_xyy(*start_tristimulus)
    cone_activation = list(float(value) for value in start_cone_activation)
    while 0.0 <= chromoluminance[0] <= 0.65: # Move up in l-cone activation
        row_chromoluminances.append(chromoluminance)
        cone_activation[0] += ACTIVATION_STEP
        if cone_activation[0] > 1.0: break
        tristimulus = lms_to_xyz(
            *cone_activation,
            use_2_degree = True
        )
        chromoluminance = xyz_to_xyy(*tristimulus)
    chromoluminances.append(
        sorted(
            row_chromoluminances,
            key = lambda triplet: triplet[0]
        )
    )
# endregion

# region Estimate Protanope Copunctal Point
intersections = list()
for index, row_chromoluminances in enumerate(chromoluminances):
    if index == 0: continue
    intersections.append(
        intersection_of_two_segments(
            row_chromoluminances[0][0:2],
            row_chromoluminances[-1][0:2],
            chromoluminances[index - 1][0][0:2],
            chromoluminances[index - 1][-1][0:2]
        )
    )
copunctal_point = tuple(mean(intersections, axis = 0))
# endregion

# region Initialize Figure
figure = Figure(
    name = 'figure_25_multiple_protan{0}'.format(
        '_inverted' if INVERTED else ''
    ),
    size = SIZE,
    inverted = INVERTED
)
figure.set_fonts(**FONT_SIZES)
mid_point = 0.51
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
    color = figure.grey_level(0.25),
    zorder = 0
)
chromaticity_panel.axvline(
    x = 0,
    linewidth = 2,
    color = figure.grey_level(0.25),
    zorder = 0
)
chromaticity_panel.plot(
    [0, 1],
    [1, 0],
    linestyle = ':',
    color = figure.grey_level(0.75),
    zorder = 0
)
for panel in figure.panels.values():
    panel.plot(
        list(datum['x'] for datum in spectrum_locus_1931_2),
        list(datum['y'] for datum in spectrum_locus_1931_2),
        solid_capstyle = 'round',
        color = figure.grey_level(0.5),
        zorder = 2
    )
    panel.plot(
        [spectrum_locus_1931_2[0]['x'], spectrum_locus_1931_2[-1]['x']],
        [spectrum_locus_1931_2[0]['y'], spectrum_locus_1931_2[-1]['y']],
        linestyle = ':',
        solid_capstyle = 'round',
        color = figure.grey_level(0.5),
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
        color = figure.grey_level(0.75),
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
                color = figure.grey_level(0.75),
                zorder = 2
            )
# endregion

# region Plot Protan Lines Series
for row_chromoluminances in chromoluminances:
    chromaticity_panel.plot(
        *transpose(
            list(
                chromoluminance[0:2]
                for chromoluminance in row_chromoluminances
            )
        ),
        solid_capstyle = 'round',
        color = figure.grey_level(0),
        zorder = 3
    )
    chromoluminance_panel.plot3D(
        *transpose(row_chromoluminances),
        solid_capstyle = 'round',
        color = figure.grey_level(0),
        zorder = 3
    )
# endregion

# region Plot and Annotate Copunctal Point
chromaticity_panel.plot(
    *copunctal_point,
    linestyle = 'none',
    marker = 'o',
    markersize = 4,
    markeredgecolor = figure.grey_level(0),
    markerfacecolor = 'none',
    zorder = 4
)
chromaticity_panel.annotate(
    text = '({0:0.3f}, {1:0.3f})'.format(*copunctal_point),
    xy = (
        copunctal_point[0] + 0.025,
        copunctal_point[1] - 0.015
    ),
    xycoords = 'data',
    horizontalalignment = 'center',
    verticalalignment = 'top',
    fontsize = figure.font_sizes['legends'],
    color = figure.grey_level(0),
    zorder = 5
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
