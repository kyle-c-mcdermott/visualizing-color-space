"""
Confusion lines and copunctal points for all three cone types with color bands
showing colors from the confusion lines.

Caption: Select confusion lines converging on annotated copunctal points for
(from left-to-right) the long-, medium-, and short-wavelength sensitive cones
(protanope, deuteranope, and tritanope, respectively).  Horizontal bands of
color each show a range of saturated colors whose chromaticities would be
indistinguishable to someone missing that cone (though being saturated colors,
luminance variation would be detectable).
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
    AXES_GREY_LEVEL, DOTTED_GREY_LEVEL, SL_GREY_LEVEL
)
from maths.plotting_series import gamut_triangle_vertices_srgb
from maths.color_conversion import (
    rgb_to_xyz,
    xyz_to_lms,
    xyz_to_xyy,
    lms_to_xyz,
    xyz_to_rgb,
    xyy_to_xyz
)
from maths.conversion_coefficients import CONE_NAMES, COLOR_NAMES
from maths.functions import intersection_of_two_segments
from numpy import mean, linspace, arange, transpose
from matplotlib.path import Path
from figure.figure import Figure
from maths.plotting_series import (
    spectrum_locus_1931_2,
    gamut_triangle_vertices_srgb
)
from maths.coloration import chromaticity_inside_gamut
from matplotlib.collections import PathCollection
# endregion

# region Plot Settings
INVERTED = False
SIZE = (
    TEXT_WIDTH,
    2.4
)
EXTENSION = 'pdf'
RESOLUTION = 16
# endregion

# region Constants
BAND_ENDPOINTS = (
    ((0.3, 0.800), (0.625, 0.800)),
    ((0.4, 0.725), (0.725, 0.725)),
    ((0.5, 0.650), (0.825, 0.650))
)
BAND_HEIGHT = 0.05
BAND_CHROMATICITY_MARGIN = 0.01
# endregion

# region Confusion Line Segments within Display Color Gamut
named_colors = {
    'grey' : (0.5, 0.5, 0.5),
    'yellow' : (0.5, 0.5, 0.125),
    'cyan' : (0.125, 0.5, 0.5),
    'pink' : (0.5, 0.125, 0.5)
}
cones_intersections = dict()
for cone_name, start_colors, first_edge, second_edge in [
    (
        'Long',
        ('yellow', 'grey', 'pink'),
        tuple(
            tuple(
                gamut_triangle_vertices_srgb[color_name][coordinate]
                for coordinate in ['x', 'y']
            )
            for color_name in ['Green', 'Blue']
        ),
        tuple(
            tuple(
                gamut_triangle_vertices_srgb[color_name][coordinate]
                for coordinate in ['x', 'y']
            )
            for color_name in ['Red', 'Blue']
        )
    ),
    (
        'Medium',
        ('yellow', 'grey', 'pink'),
        tuple(
            tuple(
                gamut_triangle_vertices_srgb[color_name][coordinate]
                for coordinate in ['x', 'y']
            )
            for color_name in ['Green', 'Blue']
        ),
        tuple(
            tuple(
                gamut_triangle_vertices_srgb[color_name][coordinate]
                for coordinate in ['x', 'y']
            )
            for color_name in ['Red', 'Blue']
        )
    ),
    (
        'Short',
        ('cyan', 'grey', 'pink'),
        tuple(
            tuple(
                gamut_triangle_vertices_srgb[color_name][coordinate]
                for coordinate in ['x', 'y']
            )
            for color_name in ['Red', 'Blue']
        ),
        tuple(
            tuple(
                gamut_triangle_vertices_srgb[color_name][coordinate]
                for coordinate in ['x', 'y']
            )
            for color_name in ['Red', 'Green']
        )
    )
]:
    cones_intersections[cone_name] = list()
    for start_color in start_colors:
        start_tristimulus = rgb_to_xyz(*named_colors[start_color])
        start_cone_activation = xyz_to_lms(
            *start_tristimulus,
            use_2_degree = True
        )
        end_cone_activation = list(
            start_cone_activation[index] + (
                0.05
                if index == CONE_NAMES.index(cone_name)
                else 0.0
            )
            for index in range(len(CONE_NAMES))
        )
        intersections = list()
        for edge in (first_edge, second_edge):
            intersections.append(
                intersection_of_two_segments(
                    xyz_to_xyy(*start_tristimulus)[0:2],
                    xyz_to_xyy(
                        *lms_to_xyz(
                            *end_cone_activation,
                            use_2_degree = True
                        )
                    )[0:2],
                    edge[0],
                    edge[1]
                )
            )
        cones_intersections[cone_name].append(intersections)
# endregion

# region Estimate Copunctal Points
copunctal_points = dict()
for cone_name, cone_intersections in cones_intersections.items():
    copunctal_estimates = list()
    for line_index, line_segment in enumerate(cone_intersections):
        if line_index == 0: continue
        copunctal_estimates.append(
            intersection_of_two_segments(
                line_segment[0],
                line_segment[1],
                cone_intersections[line_index - 1][0],
                cone_intersections[line_index - 1][1]
            )
        )
    copunctal_points[cone_name] = tuple(mean(copunctal_estimates, axis = 0))
# endregion

# region Paths and Colors for Sample Bands
cones_color_bands = dict()
for cone_name, cone_intersections in cones_intersections.items():
    cones_color_bands[cone_name] = list()
    for line_index, line_segment in enumerate(cone_intersections):
        xs = linspace(
            BAND_ENDPOINTS[line_index][0][0],
            BAND_ENDPOINTS[line_index][1][0],
            RESOLUTION + 1
        )
        paths = list(); colors = list()
        for value_index, value in enumerate(
            linspace(
                BAND_CHROMATICITY_MARGIN,
                1 - BAND_CHROMATICITY_MARGIN,
                RESOLUTION
            )
        ):
            paths.append(
                Path(
                    [
                        (
                            xs[value_index],
                            BAND_ENDPOINTS[line_index][0][1] - BAND_HEIGHT / 2.0
                        ),
                        (
                            xs[value_index + 1],
                            BAND_ENDPOINTS[line_index][0][1] - BAND_HEIGHT / 2.0
                        ),
                        (
                            xs[value_index + 1],
                            BAND_ENDPOINTS[line_index][0][1] + BAND_HEIGHT / 2.0
                        ),
                        (
                            xs[value_index],
                            BAND_ENDPOINTS[line_index][0][1] + BAND_HEIGHT / 2.0
                        ),
                        (
                            xs[value_index],
                            BAND_ENDPOINTS[line_index][0][1] - BAND_HEIGHT / 2.0
                        )
                    ]
                )
            )
            chromaticity = list(
                line_segment[0][index]
                + value * (
                    line_segment[1][index]
                    - line_segment[0][index]
                )
                for index in range(2)
            )
            color = xyz_to_rgb(
                *xyy_to_xyz(
                    *chromaticity,
                    0.05 # arbitrarily low
                )
            )
            colors.append(
                list(color_value / max(color) for color_value in color) # saturate
            )
        cones_color_bands[cone_name].append((paths, colors))
# endregion

# region Initialize Figure
figure = Figure(
    name = 'figure_26_copunctal_points{0}'.format(
        '_inverted' if INVERTED else ''
    ),
    size = SIZE,
    inverted = INVERTED
)
figure.set_fonts(**FONT_SIZES)
long_panel = figure.add_panel(
    name = 'Long',
    title = '',
    position = (0 / 3, 0, 1 / 3, 1),
    x_label = r'$x$',
    x_ticks = arange(0, 0.81, 0.2),
    x_lim = (-0.065, 0.865),
    y_label = r'$y$',
    y_ticks = arange(0, 0.81, 0.2),
    y_lim = (-0.065, 0.865)
)
medium_panel = figure.add_panel(
    name = 'Medium',
    title = '',
    position = (1 / 3, 0, 1 / 3, 1),
    x_label = r'$x$',
    x_ticks = arange(0, 0.81, 0.2),
    x_lim = (-0.065, 0.865),
    y_label = r'$y$',
    y_ticks = arange(0, 0.81, 0.2),
    y_lim = (-0.065, 0.865)
)
short_panel = figure.add_panel(
    name = 'Short',
    title = '',
    position = (2 / 3, 0, 1 / 3, 1),
    x_label = r'$x$',
    x_ticks = arange(0, 0.81, 0.2),
    x_lim = (-0.065, 0.865),
    y_label = r'$y$',
    y_ticks = arange(0, 0.81, 0.2),
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
        zorder = 3
    )
# endregion

# region Color Fill
paths, colors = chromaticity_inside_gamut(RESOLUTION)
for cone_name, cone_color_bands in cones_color_bands.items():
    figure.panels[cone_name].add_collection(
        PathCollection(
            paths,
            facecolors = colors,
            edgecolors = colors,
            linewidth = 0.1,
            zorder = 1
        )
    )
    for cone_color_band in cone_color_bands:
        figure.panels[cone_name].add_collection(
            PathCollection(
                cone_color_band[0],
                facecolors = cone_color_band[1],
                edgecolors = cone_color_band[1],
                linewidth = 0.1,
                zorder = 0
            )
        )
# endregion

# region Confusion Lines
for cone_name, cone_intersections in cones_intersections.items():
    for cone_intersection in cone_intersections:
        figure.panels[cone_name].plot(
            *transpose(cone_intersection),
            solid_capstyle = 'round',
            color = figure.grey_level(1),
            zorder = 2
        )
        for coordinate in cone_intersection:
            figure.panels[cone_name].plot(
                [copunctal_points[cone_name][0], coordinate[0]],
                [copunctal_points[cone_name][1], coordinate[1]],
                solid_capstyle = 'round',
                color = figure.grey_level(0),
                zorder = 0
            )
# endregion

# region Annotate Copunctal Points
for cone_name, h_offset, v_offset, h_align, v_align in [
    ('Long', -0.04, -0.06, 'center', 'top'),
    ('Medium', 0.0, 0.0, 'right', 'center'),
    ('Short', 0.0, -0.01, 'center', 'top')
]:
    annotation_point = (
        copunctal_points[cone_name]
        if cone_name != 'Medium'
        else (0.675, -0.035)
    )
    figure.panels[cone_name].annotate(
        text = '({0:0.3f}, {1:0.3f}{2})'.format(
            *copunctal_points[cone_name],
            r' $\searrow$' if cone_name == 'Medium' else ''
        ),
        xy = (
            annotation_point[0] + h_offset,
            annotation_point[1] + v_offset
        ),
        xycoords = 'data',
        horizontalalignment = h_align,
        verticalalignment = v_align,
        fontsize = figure.font_sizes['legends'],
        color = figure.grey_level(0),
        zorder = 3
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
