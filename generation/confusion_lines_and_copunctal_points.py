"""
Figures illustrating confusion lines and copunctal points for the three types of
missing-cone color-blindness.

Figure Captions:
26 - A series of chromaticity / chromoluminance values derived from varying
l-cone activation in either direction away from a middle grey display value (see
Table 1 above).  The left panel shows the (top-down view) of chromaticity where
the points fall along a straight line - one of the protanope confusion lines.
The right panel shows the same values plotted in three-dimensional
chromoluminance space.  Note that the luminance is not constant, nor does it
vary along a straight line.
27 - Multiple protanope confusion lines plotted in chromaticity and
chromoluminance spaces.  In the left panel, straight lines converge on a single
point (the copunctal point) for the long-wavelength-sensitive cone.  In the
right panel the paths do not follow straight lines but do asymptotically go
towards the appropriate chromaticity (presumably at infinite luminance).
28 - Confusion lines for protanope, deuteranope, and protanope color-blindness
(missing L, M, and S cones, respectively).  The copunctal points where confusion
lines converge is given in the title for each panel.  In each panel are three
bands of color in the upper right corresponding to the paths the confusion lines
take through the display gamut.
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

# region Settings
INVERTED = False
SIZE = (16, 9)
FONT_SIZES = {
    'titles' : 16,
    'labels' : 14,
    'ticks' : 12,
    'legends' : 10
}
RESOLUTION = 32
EXTENSION = 'svg'
# endregion

# region Imports
from csv import DictReader
from maths.color_blindness import (
    rgb_to_lms,
    lms_to_rgb,
    lms_to_xyz,
    intersection_two_segments
)
from maths.rgb_cie_conversions import (
    rgb_to_chromoluminance,
    chromoluminance_to_rgb
)
from numpy import mean, linspace, transpose
from matplotlib.path import Path
from figure.figure import Figure
from maths.saturated_color_paths import chromaticity_within_gamut
from matplotlib.collections import PathCollection
# endregion

# region Constants
ACTIVATION_STEP = 0.01
# endregion

# region Load CIE 1931 2-Degree Spectrum Locus
"""
Tabulated spectrum locus coordinates for CIE 1931 2-degree downloaded from:
http://www.cvrl.org/cie.htm
Under Chromaticity Coordinates, CIE 1931 2-deg xyz chromaticity coordinates
using the second button "/W" with a solid (instead of dashed) line indicating
higher sampling resolution (1 nm)
(Note that chromaticity values do not change beyond 699 nm, likely due to the
fact that rounding errors seem to cause the spectrum locus to start wandering
about back on itself based on chromaticities converted from the tabulated color
matching functions - the converted values were abandoned and 699 nm copied down
for the remainder of the series.)
"""
with open(
    'cvrl/cccie31_1.csv',
    'r'
) as read_file:
    spectrum_locus = list(
        {
            'Wavelength' : int(row['Wavelength']),
            'x' : float(row['x']),
            'y' : float(row['y'])
        }
        for row in DictReader(
            read_file,
            fieldnames = ['Wavelength', 'x', 'y', 'z'] # z is superfluous
        )
        if int(row['Wavelength']) < 700
    )
# endregion

# region Chomoluminance of Selected Points from Middle Grey with L-Cone Variations
middle_grey_activation = rgb_to_lms(0.5, 0.5, 0.5)
select_l_cone_colors = list()
select_l_cone_chromoluminances = list()
for multiple in [0.85, 0.925, 1.0, 1.075, 1.15]:
    lms = list(
        middle_grey_activation[index] * multiple
        if index == 0
        else middle_grey_activation[index]
        for index in range(3)
    )
    rgb = lms_to_rgb(*lms)
    select_l_cone_colors.append(rgb)
    select_l_cone_chromoluminances.append(
        rgb_to_chromoluminance(
            *rgb,
            gamma_correct = True
        )
    )
# endregion

# region Extended Confusion Lines for L Cone / Protanope
l_cone_confusion_lines = list()
for color in [(0.5, 0.5, 0.5), (0.5, 0.5, 0.25), (0.5, 0.25, 0.5)]:
    starting_lms = rgb_to_lms(*color)
    starting_tristimulus_values = lms_to_xyz(*starting_lms)
    chromoluminance = (
        starting_tristimulus_values[0] / sum(starting_tristimulus_values),
        starting_tristimulus_values[1] / sum(starting_tristimulus_values),
        starting_tristimulus_values[1]
    )
    lms = list(float(value) for value in starting_lms)
    confusion_line_chromoluminances = list()
    while 0.0 <= chromoluminance[0] <= 0.65:
        confusion_line_chromoluminances.append(chromoluminance)
        lms[0] -= ACTIVATION_STEP
        tristimulus_values = lms_to_xyz(*lms)
        chromoluminance = (
            tristimulus_values[0] / sum(tristimulus_values),
            tristimulus_values[1] / sum(tristimulus_values),
            tristimulus_values[1]
        )
    chromoluminance = (
        starting_tristimulus_values[0] / sum(starting_tristimulus_values),
        starting_tristimulus_values[1] / sum(starting_tristimulus_values),
        starting_tristimulus_values[1]
    )
    lms = list(float(value) for value in starting_lms)
    while 0.0 <= chromoluminance[0] <= 0.65:
        lms[0] += ACTIVATION_STEP
        tristimulus_values = lms_to_xyz(*lms)
        chromoluminance = (
            tristimulus_values[0] / sum(tristimulus_values),
            tristimulus_values[1] / sum(tristimulus_values),
            tristimulus_values[1]
        )
        if 0.0 <= chromoluminance[0] <= 0.65:
            confusion_line_chromoluminances.append(chromoluminance)
    confusion_line_chromoluminances.sort(
        key = lambda triplet: triplet[0]
    )
    l_cone_confusion_lines.append(confusion_line_chromoluminances)
# endregion

# region Colorized Confusion Line Series and Copunctal Points
gamut_segments = [
    (
        rgb_to_chromoluminance(1.0, 0.0, 0.0)[0:2], # Red
        rgb_to_chromoluminance(0.0, 1.0, 0.0)[0:2] # to Green
    ),
    (
        rgb_to_chromoluminance(0.0, 1.0, 0.0)[0:2], # Green
        rgb_to_chromoluminance(0.0, 0.0, 1.0)[0:2] # to Blue
    ),
    (
        rgb_to_chromoluminance(0.0, 0.0, 1.0)[0:2], # Blue
        rgb_to_chromoluminance(1.0, 0.0, 0.0)[0:2] # to Red
    )
]
copunctal_points = list()
cones_gamut_intersections = list()
for cone_index, starting_colors in [
    (0, [(0.5, 0.5, 0.25), (0.5, 0.5, 0.5), (0.5, 0.25, 0.5)]), # L-Cone: Yellow, White, Pink
    (1, [(0.5, 0.5, 0.25), (0.5, 0.5, 0.5), (0.5, 0.25, 0.5)]), # M-Cone: Yellow, White, Pink
    (2, [(0.25, 0.5, 0.5), (0.5, 0.5, 0.5), (0.5, 0.25, 0.5)]) # S-Cone: Cyan, White, Pink
]:
    segments_chromaticities = list()
    cone_gamut_intersection = list()
    for starting_color in starting_colors:
        starting_lms = rgb_to_lms(*starting_color)
        ending_lms = list(
            starting_lms[index] - 0.1 if index == cone_index else 0.0
            for index in range(len(starting_lms))
        )
        tristimulus_endpoints = list(
            lms_to_xyz(*lms)
            for lms in [starting_lms, ending_lms]
        )
        segments_chromaticities.append(
            list(
                (
                    tristimulus_endpoint[0] / sum(tristimulus_endpoint),
                    tristimulus_endpoint[1] / sum(tristimulus_endpoint)
                )
                for tristimulus_endpoint in tristimulus_endpoints
            )
        )
        cone_gamut_intersection.append(
            (
                intersection_two_segments(
                    *segments_chromaticities[-1],
                    *gamut_segments[2 if cone_index == 2 else 1]
                ),
                intersection_two_segments(
                    *segments_chromaticities[-1],
                    *gamut_segments[0 if cone_index == 2 else 2]
                )
            )
        )
    cones_gamut_intersections.append(cone_gamut_intersection)
    copunctal_point_estimates = list()
    for index, segment_chromaticities in enumerate(segments_chromaticities):
        if index == 0: continue
        copunctal_point_estimates.append(
            intersection_two_segments(
                segments_chromaticities[0][0],
                segments_chromaticities[0][1],
                segment_chromaticities[0],
                segment_chromaticities[1]
            )
        )
    copunctal_points.append(tuple(mean(copunctal_point_estimates, axis = 0)))
band_endpoints = (
    ((0.3, 0.825), (0.65, 0.825)),
    ((0.4, 0.750), (0.75, 0.750)),
    ((0.5, 0.675), (0.85, 0.675))
)
band_height = 0.05
cones_color_bands = list()
for cone_gamut_intersections in cones_gamut_intersections:
    cone_color_bands = list()
    for color_index, color_band_intersections in enumerate(cone_gamut_intersections):
        xs = linspace(
            band_endpoints[color_index][0][0],
            band_endpoints[color_index][1][0],
            RESOLUTION + 1
        )
        paths = list(); colors = list()
        for value_index, value in enumerate(linspace(0, 1, RESOLUTION)):
            paths.append(
                Path(
                    [
                        (
                            xs[value_index],
                            band_endpoints[color_index][0][1] - band_height / 2.0
                        ),
                        (
                            xs[value_index + 1],
                            band_endpoints[color_index][0][1] - band_height / 2.0
                        ),
                        (
                            xs[value_index + 1],
                            band_endpoints[color_index][0][1] + band_height / 2.0
                        ),
                        (
                            xs[value_index],
                            band_endpoints[color_index][0][1] + band_height / 2.0
                        ),
                        (
                            xs[value_index],
                            band_endpoints[color_index][0][1] - band_height / 2.0
                        )
                    ]
                )
            )
            chromaticity = list(
                color_band_intersections[0][index]
                + value * (
                    color_band_intersections[1][index]
                    - color_band_intersections[0][index]
                )
                for index in range(2)
            )
            color = chromoluminance_to_rgb(*chromaticity, 0.05) # Arbitrarily low Y
            color = list(rgb_value / max(color) for rgb_value in color) # Saturate
            colors.append(color)
        cone_color_bands.append((paths, colors))
    cones_color_bands.append(cone_color_bands)
# endregion

# region Figure 26 - Protanope Confusion Line with Annotated Points

# region Initialize Figure
figure = Figure(
    name = 'Protanope Confusion Line from Point Series{0}'.format(
        ' (inverted)' if INVERTED else ''
    ),
    size = SIZE,
    inverted = INVERTED
)
figure.set_fonts(**FONT_SIZES)
chromaticity_panel = figure.add_panel(
    name = 'chromaticity',
    title = 'Protanope Confusion Line from Tabulated Coordinates\nChromaticity (x, y)',
    position = (0, 0, 0.5, 1),
    x_label = 'x',
    x_ticks = linspace(0, 0.8, 9),
    x_lim = (-0.065, 0.865),
    y_label = 'y',
    y_ticks = linspace(0, 0.8, 9),
    y_lim = (-0.065, 0.865)
)
chromaticity_panel.set_aspect(
    aspect = 'equal', # Make horizontal and vertical axes the same scale
    adjustable = 'box' # Change the plot area aspect ratio to achieve this
)
chromoluminance_panel = figure.add_panel(
    name = 'chromoluminance',
    title = 'Protanope Confusion Line from Tabulated Coordinates\nChromoluminance (x, y, Y)',
    position = (0.5, 0, 0.5, 1),
    three_dimensional = True,
    x_label = 'x',
    x_lim = (-0.05, 1.05),
    y_label = 'y',
    y_lim = (-0.05, 1.05),
    z_label = 'Y',
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

# region Reference
chromaticity_panel.axhline(
    y = 0,
    linewidth = 2,
    color = figure.grey_level(0),
    zorder = 0
)
chromaticity_panel.axvline(
    x = 0,
    linewidth = 2,
    color = figure.grey_level(0),
    zorder = 0
)
chromaticity_panel.plot(
    [0, 1],
    [1, 0],
    linestyle = '--',
    color = figure.grey_level(0.5),
    zorder = 0
)
for panel in figure.panels.values():
    panel.plot(
        list(datum['x'] for datum in spectrum_locus),
        list(datum['y'] for datum in spectrum_locus),
        color = figure.grey_level(0.25),
        zorder = 1
    )
    panel.plot(
        [spectrum_locus[0]['x'], spectrum_locus[-1]['x']],
        [spectrum_locus[0]['y'], spectrum_locus[-1]['y']],
        color = figure.grey_level(0.25),
        linestyle = ':',
        zorder = 1
    )
    panel.plot(
        *transpose(
            list(
                rgb_to_chromoluminance(*color)[0:2]
                for color in [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 0, 0)]
            )
        ),
        color = figure.grey_level(0.75),
        zorder = 2
    )
color = 3 * [0.0]
for color_index in range(3):
    second_index = 0
    if color_index == 0: second_index = 1
    third_index = 2
    if color_index == 2: third_index = 1
    for second_value in range(2):
        for third_value in range(2):
            xs = list(); ys = list(); zs = list()
            for value in linspace(0, 1, RESOLUTION):
                color[color_index] = value
                color[second_index] = second_value
                color[third_index] = third_value
                x, y, Y = rgb_to_chromoluminance(*color)
                xs.append(x); ys.append(y); zs.append(Y)
            chromoluminance_panel.plot3D(
                xs,
                ys,
                zs,
                color = figure.grey_level(0.75),
                zorder = 2
            )
# endregion

# region Plot Selected Coordinates along Protanope Confusion Line
chromaticity_panel.plot(
    *transpose(
        list(
            chromoluminance[0:2]
            for chromoluminance in select_l_cone_chromoluminances
        )
    ),
    color = figure.grey_level(0),
    linewidth = 2,
    zorder = 3
)
chromoluminance_panel.plot3D(
    *transpose(select_l_cone_chromoluminances),
    color = figure.grey_level(0),
    linewidth = 2,
    zorder = 3
)
for index, color in enumerate(select_l_cone_colors):
    chromaticity_panel.plot(
        *select_l_cone_chromoluminances[index][0:2],
        linestyle = 'none',
        marker = 'o',
        markersize = 6,
        markeredgecolor = 'none',
        markerfacecolor = color,
        zorder = 4
    )
    chromoluminance_panel.plot(
        *select_l_cone_chromoluminances[index],
        linestyle = 'none',
        marker = 'o',
        markersize = 6,
        markeredgecolor = 'none',
        markerfacecolor = color,
        zorder = 4
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

# endregion

# region Figure 27 - Multiple, Extended Protanope Confusion Lines

# region Initialize Figure
figure = Figure(
    name = 'Extended Protanope Confusion Lines{0}'.format(
        ' (inverted)' if INVERTED else ''
    ),
    size = SIZE,
    inverted = INVERTED
)
figure.set_fonts(**FONT_SIZES)
chromaticity_panel = figure.add_panel(
    name = 'chromaticity',
    title = 'Extended Protanope Confusion Lines\nChromaticity (x, y)',
    position = (0, 0, 0.5, 1),
    x_label = 'x',
    x_ticks = linspace(0, 0.8, 9),
    x_lim = (-0.065, 0.865),
    y_label = 'y',
    y_ticks = linspace(0, 0.8, 9),
    y_lim = (-0.065, 0.865)
)
chromaticity_panel.set_aspect(
    aspect = 'equal', # Make horizontal and vertical axes the same scale
    adjustable = 'box' # Change the plot area aspect ratio to achieve this
)
chromoluminance_panel = figure.add_panel(
    name = 'chromoluminance',
    title = 'Extended Protanope Confusion Lines\nChromoluminance (x, y, Y)',
    position = (0.5, 0, 0.5, 1),
    three_dimensional = True,
    x_label = 'x',
    x_lim = (-0.05, 1.05),
    y_label = 'y',
    y_lim = (-0.05, 1.05),
    z_label = 'Y',
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

# region Reference
chromaticity_panel.axhline(
    y = 0,
    linewidth = 2,
    color = figure.grey_level(0),
    zorder = 0
)
chromaticity_panel.axvline(
    x = 0,
    linewidth = 2,
    color = figure.grey_level(0),
    zorder = 0
)
chromaticity_panel.plot(
    [0, 1],
    [1, 0],
    linestyle = '--',
    color = figure.grey_level(0.5),
    zorder = 0
)
for panel in figure.panels.values():
    panel.plot(
        list(datum['x'] for datum in spectrum_locus),
        list(datum['y'] for datum in spectrum_locus),
        color = figure.grey_level(0.25),
        zorder = 1
    )
    panel.plot(
        [spectrum_locus[0]['x'], spectrum_locus[-1]['x']],
        [spectrum_locus[0]['y'], spectrum_locus[-1]['y']],
        color = figure.grey_level(0.25),
        linestyle = ':',
        zorder = 1
    )
    panel.plot(
        *transpose(
            list(
                rgb_to_chromoluminance(*color)[0:2]
                for color in [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 0, 0)]
            )
        ),
        color = figure.grey_level(0.75),
        zorder = 2
    )
color = 3 * [0.0]
for color_index in range(3):
    second_index = 0
    if color_index == 0: second_index = 1
    third_index = 2
    if color_index == 2: third_index = 1
    for second_value in range(2):
        for third_value in range(2):
            xs = list(); ys = list(); zs = list()
            for value in linspace(0, 1, RESOLUTION):
                color[color_index] = value
                color[second_index] = second_value
                color[third_index] = third_value
                x, y, Y = rgb_to_chromoluminance(*color)
                xs.append(x); ys.append(y); zs.append(Y)
            chromoluminance_panel.plot3D(
                xs,
                ys,
                zs,
                color = figure.grey_level(0.75),
                zorder = 2
            )
# endregion

# region Plot Extended Confusion Lines
for l_cone_confusion_line in l_cone_confusion_lines:
    chromaticity_panel.plot(
        *transpose(
            list(
                chromoluminance[0:2]
                for chromoluminance in l_cone_confusion_line
            )
        ),
        color = figure.grey_level(0),
        linewidth = 2,
        zorder = 3
    )
    chromoluminance_panel.plot3D(
        *transpose(l_cone_confusion_line),
        color = figure.grey_level(0),
        linewidth = 2,
        zorder = 3
    )
# endregion

# region Copunctal Point
chromaticity_panel.plot(
    *copunctal_points[0],
    linestyle = 'none',
    marker = 'o',
    markersize = 8,
    markerfacecolor = 'none',
    markeredgecolor = figure.grey_level(0),
    markeredgewidth = 2,
    zorder = 4
)
chromaticity_panel.annotate(
    text = '({0:0.3f}, {1:0.3f})'.format(
        *copunctal_points[0]
    ),
    xy = (
        copunctal_points[0][0] - 0.02,
        copunctal_points[0][1] + 0.02
    ),
    xycoords = 'data',
    horizontalalignment = 'left',
    verticalalignment = 'bottom',
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

# endregion

# region Figure 28 - Colored Confusion Line Bands for All Three Cones

# region Initialize Figure
figure = Figure(
    name = 'Confusion Lines and Copunctal Points{0}'.format(
        ' (inverted)' if INVERTED else ''
    ),
    size = (SIZE[1] * 3 / 1.5, SIZE[1] / 1.5),
    inverted = INVERTED
)
figure.set_fonts(**FONT_SIZES)
l_panel = figure.add_panel(
    name = 'l',
    title = 'Protanope Confusion Lines\nCopunctal Point = ({0:0.3f}, {1:0.3f})'.format(
        *copunctal_points[0]
    ),
    position = (0 / 3, 0, 1 / 3, 1),
    x_label = 'x',
    x_ticks = linspace(0, 0.8, 9),
    x_lim = (-0.065, 0.865),
    y_label = 'y',
    y_ticks = linspace(0, 0.8, 9),
    y_lim = (-0.065, 0.865)
)
m_panel = figure.add_panel(
    name = 'm',
    title = 'Deuteranope Confusion Lines\nCopunctal Point = ({0:0.3f}, {1:0.3f})'.format(
        *copunctal_points[1]
    ),
    position = (1 / 3, 0, 1 / 3, 1),
    x_label = 'x',
    x_ticks = linspace(0, 0.8, 9),
    x_lim = (-0.065, 0.865),
    y_label = 'y',
    y_ticks = linspace(0, 0.8, 9),
    y_lim = (-0.065, 0.865)
)
s_panel = figure.add_panel(
    name = 's',
    title = 'Tritanope Confusion Lines\nCopunctal Point = ({0:0.3f}, {1:0.3f})'.format(
        *copunctal_points[2]
    ),
    position = (2 / 3, 0, 1 / 3, 1),
    x_label = 'x',
    x_ticks = linspace(0, 0.8, 9),
    x_lim = (-0.065, 0.865),
    y_label = 'y',
    y_ticks = linspace(0, 0.8, 9),
    y_lim = (-0.065, 0.865)
)
for panel in figure.panels.values():
    panel.set_aspect(
        aspect = 'equal', # Make horizontal and vertical axes the same scale
        adjustable = 'box' # Change the plot area aspect ratio to achieve this
    )
# endregion

# region Reference
for panel in figure.panels.values():
    panel.axhline(
        y = 0,
        linewidth = 2,
        color = figure.grey_level(0),
        zorder = 0
    )
    panel.axvline(
        x = 0,
        linewidth = 2,
        color = figure.grey_level(0),
        zorder = 0
    )
    panel.plot(
        [0, 1],
        [1, 0],
        linestyle = '--',
        color = figure.grey_level(0.5),
        zorder = 0
    )
    panel.plot(
        list(datum['x'] for datum in spectrum_locus),
        list(datum['y'] for datum in spectrum_locus),
        color = figure.grey_level(0.25),
        zorder = 2
    )
    panel.plot(
        [spectrum_locus[0]['x'], spectrum_locus[-1]['x']],
        [spectrum_locus[0]['y'], spectrum_locus[-1]['y']],
        color = figure.grey_level(0.25),
        linestyle = ':',
        zorder = 2
    )
# endregion

# region Color Fill
for panel in figure.panels.values():
    paths, colors = chromaticity_within_gamut(
        resolution = RESOLUTION,
        gamma_correct = False
    )
    panel.add_collection(
        PathCollection(
            paths,
            facecolors = colors,
            edgecolors = colors,
            zorder = 1
        )
    )
# endregion

# region Confusion Lines
for cone_index, cone_type in enumerate(['l', 'm', 's']):
    for intersections in cones_gamut_intersections[cone_index]:
        figure.panels[cone_type].plot(
            [intersections[0][0], copunctal_points[cone_index][0]],
            [intersections[0][1], copunctal_points[cone_index][1]],
            color = (0.5, 0.5, 0.5),
            zorder = 3
        )
        figure.panels[cone_type].plot(
            *transpose(intersections),
            linewidth = 2,
            color = figure.grey_level(1),
            zorder = 4
        )
# endregion

# region Color Bands
for cone_index, cone_type in enumerate(['l', 'm', 's']):
    for color_band in cones_color_bands[cone_index]:
        figure.panels[cone_type].add_collection(
            PathCollection(
                color_band[0],
                facecolors = color_band[1],
                edgecolors = color_band[1],
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

# endregion
