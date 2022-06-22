"""
Plotting various figures of chromaticity diagrams with colors filled in.

Figure Captions:
14 - Chromaticity diagram with the interior of the sRGB display gamut filled
with color.  The left panel shows a coarse color sampling with the edges of the
color patches visible; note that the three square surfaces from the right panel
of Figure 12 are here manipulated to fit within this triangle.  The right panel
shows a finer color sampling.
15 - Chromaticity diagrams with the interior of the spectrum locus (and display
gamut) filled with color.  The left panel shows a coarse color sampling with the
edges of the color patches visible.  The right panel shows a finer color
sampling.  Note the discontinuity, especially visible in the right panel,
between colors within and outside the sRGB display gamut.
16 - Chromaticity diagrams with (left) and without (right) gamma correction.
The gamma correction affects the way saturation approaches the edges of the
triangle, but the colors along the very edge are the same regardless of whether
gamma correction is applied, so the area outside the triangle is colored the
same regardless of whether the gamma correction step is applied.
17 - Profile of chromoluminance space with (left) and without (right) gamma
correction.  Note the intrusion of bright blue down the right side of the
profile in the right panel - there is clearly a luminance variation along the
horizontal where luminance (Y) is supposed to be constant.  The gamma corrected
(left) version of three-dimensional chromoluminance space is arguably more
correct.
18 - Chromaticity diagram filled with color based on custom primaries.  The
primary chromaticities were chosen to maximize the area of the triangle inside
the spectrum locus curve while also maintaining the hue angle / corresponding
wavelength of the primary colors (excluding pink, which has no corresponding
wavelength to maintain) derived from the sRGB primaries.
19 - Chromaticity diagram filled with color based on custom primaries.  The
primary chromaticities were chosen to tightly enclose the spectrum locus from
the outside while also maintaining the hue angle / corresponding wavelength of
the primary colors (excluding pink, which has no corresponding wavelength)
derived from the sRGB primaries.  Note filling this diagram with color only
requires one step - filling within the triangle - but with the added need to
unfill the region outside the spectrum locus.
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
SAVE_FIGURES = (
    True, # Figure 14 - Chromaticity inside gamut
    True, # Figure 15 - Chromaticity inside spectrum locus
    True, # Figure 16 - Chromaticity with and without gamma correction
    True, # Figure 17 - Chromoluminance with and without gamma correction
    True, # Figure 18 - Chromaticity with custom (inside SL) primaries
    True # Figure 19 - Chromaticity with custom (outside SL) primaries
)
INVERTED = False
SIZE = (16, 9)
FONT_SIZES = {
    'titles' : 16,
    'labels' : 14,
    'ticks' : 12,
    'legends' : 12
}
RESOLUTIONS = (8, 64) # Sparse and Fine settings
EXTENSION = 'svg'
# endregion

# region Imports
from csv import DictReader
from maths.rgb_cie_conversions import rgb_to_chromoluminance
from figure.figure import Figure
from numpy import linspace, transpose, array
from maths.saturated_color_paths import (
    chromaticity_within_gamut,
    chromaticity_outisde_gamut,
    three_dimensional_surface
)
from matplotlib.collections import PathCollection
# endregion

# region Constants
INSIDE_PRIMARIES_COEFFICIENTS = ( # Arbitrary Inside Primaries
    (0.7365, 0.0435, 0.1705),
    (0.3654, 0.5821, 0.0525),
    (0.0058, 0.0801, 1.0032)
)
OUTSIDE_PRIMARIES_COEFFICIENTS = ( # Arbitrary Outisde Primaries
    (0.8812, -0.0405, 0.1097),
    (0.3247, 0.7334, -0.0581),
    (-0.2237, 0.0807, 1.2320)
)
# endregion

# region Load in Data
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
        (
            float(row['x']),
            float(row['y'])
        )
        for row in DictReader(
            read_file,
            fieldnames = ['Wavelength', 'x', 'y', 'z'] # z is superfluous
        )
        if int(row['Wavelength']) < 700
    )
# endregion

# region Estimate sRGB Chromaticities (in CIE 1931)
srgb_primary_chromaticities = list(
    rgb_to_chromoluminance(
        red,
        green,
        blue
    )[0:2]
    for (red, green, blue) in [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 0, 0)]
)
# endregion

# region Figure 14 - Coloring inside the sRGB Display Gamut Triangle

if SAVE_FIGURES[0]:

    # region Initialize Figure
    figure = Figure(
        name = 'Color-Filled Chromaticity Diagram - sRGB Gamut Interior{0}'.format(
            ' (inverted)' if INVERTED else ''
        ),
        size = SIZE,
        inverted = INVERTED
    )
    figure.set_fonts(**FONT_SIZES)
    coarse_panel = figure.add_panel(
        name = 'coarse',
        title = '{0}\n{1}\n{2}'.format(
            r'CIE 1931 2$\degree$ Chromaticity Diagram',
            'Interior of sRGB Gamut Filled with Color',
            '(coarse resolution)'
        ),
        position = (0, 0, 0.5, 1),
        x_label = 'x',
        x_ticks = linspace(0, 0.8, 9),
        x_lim = (-0.065, 0.865),
        y_label = 'y',
        y_ticks = linspace(0, 0.8, 9),
        y_lim = (-0.065, 0.865)
    )
    fine_panel = figure.add_panel(
        name = 'fine',
        title = '{0}\n{1}\n{2}'.format(
            r'CIE 1931 2$\degree$ Chromaticity Diagram',
            'Interior of sRGB Gamut Filled with Color',
            '(fine resolution)'
        ),
        position = (0.5, 0, 0.5, 1),
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
            *transpose(spectrum_locus),
            color = figure.grey_level(0.25),
            zorder = 2
        )
        panel.plot(
            [spectrum_locus[0][0], spectrum_locus[-1][0]],
            [spectrum_locus[0][1], spectrum_locus[-1][1]],
            color = figure.grey_level(0.25),
            linestyle = ':',
            zorder = 2
        )
        panel.plot(
            *transpose(srgb_primary_chromaticities),
            color = figure.grey_level(0.25),
            zorder = 2
        )
    # endregion

    # region Color Fill
    paths, colors = chromaticity_within_gamut(
        resolution = RESOLUTIONS[0],
        gamma_correct = True
    )
    coarse_panel.add_collection(
        PathCollection(
            paths,
            facecolors = colors,
            edgecolors = (0.5, 0.5, 0.5),
            zorder = 1
        )
    )
    paths, colors = chromaticity_within_gamut(
        resolution = RESOLUTIONS[1],
        gamma_correct = True
    )
    fine_panel.add_collection(
        PathCollection(
            paths,
            facecolors = colors,
            edgecolors = colors,
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
    # endregion

# endregion

# region Figure 15 - Coloring inside of Spectrum Locus (and Display Gamut)

if SAVE_FIGURES[1]:

    # region Initialize Figure
    figure = Figure(
        name = 'Color-Filled Chromaticity Diagram{0}'.format(
            ' (inverted)' if INVERTED else ''
        ),
        size = SIZE,
        inverted = INVERTED
    )
    figure.set_fonts(**FONT_SIZES)
    coarse_panel = figure.add_panel(
        name = 'coarse',
        title = '{0}\n{1}\n{2}'.format(
            r'CIE 1931 2$\degree$ Chromaticity Diagram',
            'Interior Spectrum Locus Filled with Color',
            '(coarse resolution)'
        ),
        position = (0, 0, 0.5, 1),
        x_label = 'x',
        x_ticks = linspace(0, 0.8, 9),
        x_lim = (-0.065, 0.865),
        y_label = 'y',
        y_ticks = linspace(0, 0.8, 9),
        y_lim = (-0.065, 0.865)
    )
    fine_panel = figure.add_panel(
        name = 'fine',
        title = '{0}\n{1}\n{2}'.format(
            r'CIE 1931 2$\degree$ Chromaticity Diagram',
            'Interior of Spectrum Locus Filled with Color',
            '(fine resolution)'
        ),
        position = (0.5, 0, 0.5, 1),
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
            *transpose(spectrum_locus),
            color = figure.grey_level(0.25),
            zorder = 2
        )
        panel.plot(
            [spectrum_locus[0][0], spectrum_locus[-1][0]],
            [spectrum_locus[0][1], spectrum_locus[-1][1]],
            color = figure.grey_level(0.25),
            linestyle = ':',
            zorder = 2
        )
    # endregion

    # region Color Fill
    paths, colors = chromaticity_within_gamut(
        resolution = RESOLUTIONS[0],
        gamma_correct = True
    )
    coarse_panel.add_collection(
        PathCollection(
            paths,
            facecolors = colors,
            edgecolors = colors,
            zorder = 1
        )
    )
    paths, colors = chromaticity_outisde_gamut(
        resolution = RESOLUTIONS[0]
    )
    coarse_panel.add_collection(
        PathCollection(
            paths,
            facecolors = colors,
            edgecolors = (0.5, 0.5, 0.5),
            zorder = 1
        )
    )
    paths, colors = chromaticity_within_gamut(
        resolution = RESOLUTIONS[1],
        gamma_correct = True
    )
    fine_panel.add_collection(
        PathCollection(
            paths,
            facecolors = colors,
            edgecolors = colors,
            zorder = 1
        )
    )
    paths, colors = chromaticity_outisde_gamut(
        resolution = RESOLUTIONS[1]
    )
    fine_panel.add_collection(
        PathCollection(
            paths,
            facecolors = colors,
            edgecolors = colors,
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
    # endregion

# endregion

# region Figure 16 - Effect of Gamma Correction on Chromaticity

if SAVE_FIGURES[2]:

    # region Initialize Figure
    figure = Figure(
        name = 'Gamma Correction in Chromaticity{0}'.format(
            ' (inverted)' if INVERTED else ''
        ),
        size = SIZE,
        inverted = INVERTED
    )
    figure.set_fonts(**FONT_SIZES)
    yes_panel = figure.add_panel(
        name = 'yes',
        title = '{0}\n{1}\n{2}'.format(
            r'CIE 1931 2$\degree$ Chromaticity Diagram',
            'Interior Spectrum Locus Filled with Color',
            '(with gamma correction)'
        ),
        position = (0, 0, 0.5, 1),
        x_label = 'x',
        x_ticks = linspace(0, 0.8, 9),
        x_lim = (-0.065, 0.865),
        y_label = 'y',
        y_ticks = linspace(0, 0.8, 9),
        y_lim = (-0.065, 0.865)
    )
    no_panel = figure.add_panel(
        name = 'no',
        title = '{0}\n{1}\n{2}'.format(
            r'CIE 1931 2$\degree$ Chromaticity Diagram',
            'Interior of Spectrum Locus Filled with Color',
            '(without gamma correction)'
        ),
        position = (0.5, 0, 0.5, 1),
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
            *transpose(spectrum_locus),
            color = figure.grey_level(0.25),
            zorder = 2
        )
        panel.plot(
            [spectrum_locus[0][0], spectrum_locus[-1][0]],
            [spectrum_locus[0][1], spectrum_locus[-1][1]],
            color = figure.grey_level(0.25),
            linestyle = ':',
            zorder = 2
        )
    # endregion

    # region Color Fill
    paths, colors = chromaticity_within_gamut(
        resolution = RESOLUTIONS[1],
        gamma_correct = True
    )
    yes_panel.add_collection(
        PathCollection(
            paths,
            facecolors = colors,
            edgecolors = colors,
            zorder = 1
        )
    )
    paths, colors = chromaticity_within_gamut(
        resolution = RESOLUTIONS[1]
    )
    no_panel.add_collection(
        PathCollection(
            paths,
            facecolors = colors,
            edgecolors = colors,
            zorder = 1
        )
    )
    paths, colors = chromaticity_outisde_gamut(
        resolution = RESOLUTIONS[1]
    )
    for panel in figure.panels.values():
        panel.add_collection(
            PathCollection(
                paths,
                facecolors = colors,
                edgecolors = colors,
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
    # endregion

# endregion

# region Figure 17 - Effect of Gamma Correction on Chromoluminance

if SAVE_FIGURES[3]:

    # region Initialize Figure
    figure = Figure(
        name = 'Gamma Correction in Chromoluminance{0}'.format(
            ' (inverted)' if INVERTED else ''
        ),
        size = SIZE,
        inverted = INVERTED
    )
    figure.set_fonts(**FONT_SIZES)
    yes_panel = figure.add_panel(
        name = 'yes',
        title = 'Chromoluminance Profile with Gamma Correction',
        position = (0.025, 0, 0.475, 1),
        three_dimensional = True,
        x_label = 'x',
        x_lim = (-0.05, 1.05),
        y_label = 'y',
        y_lim = (-0.05, 1.05),
        z_label = 'Y',
        z_lim = (-0.05, 1.05)
    )
    no_panel = figure.add_panel(
        name = 'no',
        title = 'Chromoluminance Profile without Gamma Correction',
        position = (0.5, 0, 0.475, 1),
        three_dimensional = True,
        x_label = 'x',
        x_lim = (-0.05, 1.05),
        y_label = 'y',
        y_lim = (-0.05, 1.05),
        z_label = 'Y',
        z_lim = (-0.05, 1.05)
    )
    for panel_name, panel in figure.panels.items():
        panel.view_init(0, -145)
        figure.change_panes(
            panel_name,
            x_pane_color = figure.grey_level(0.95),
            x_grid_color = figure.grey_level(0.75),
            y_pane_color = figure.grey_level(0.95),
            y_grid_color = figure.grey_level(0.75),
            z_pane_color = figure.grey_level(0.95),
            z_grid_color = figure.grey_level(0.75)
        )
    # endregion

    # region Reference
    for panel in figure.panels.values():
        panel.plot3D(
            *transpose(spectrum_locus + [spectrum_locus[0]]), # z defaults to zeros
            color = figure.grey_level(0.5),
            linewidth = 2,
            zorder = 0
        )
        panel.plot3D(
            *transpose(srgb_primary_chromaticities), # z defaults to zeros
            color = figure.grey_level(0.5),
            zorder = 0
        )
    # endregion

    # region Plot Surfaces
    for color_value in [1, 0]:
        for color_index in range(3):
            if color_value == 1 and color_index == 0: continue
            coordinates, colors = three_dimensional_surface(
                color_index,
                1,
                color_value = color_value,
                resolution = RESOLUTIONS[1]
            )
            yes_panel.plot_surface(
                X = coordinates[0],
                Y = coordinates[1],
                Z = array(coordinates[2]),
                facecolors = colors,
                shade = False,
                zorder = 1
            )
            coordinates, colors = three_dimensional_surface(
                color_index,
                1,
                color_value = color_value,
                resolution = RESOLUTIONS[1],
                gamma_correct = False
            )
            no_panel.plot_surface(
                X = coordinates[0],
                Y = coordinates[1],
                Z = array(coordinates[2]),
                facecolors = colors,
                shade = False,
                zorder = 1
            )
    # endregion

    # region Save Figure
    figure.update()
    figure.save(
        path = 'images',
        name = figure.name,
        extension = EXTENSION
    )
    # endregion

# endregion

# region Figure 18 - Custom Primaries Inside Spectrum Locus

if SAVE_FIGURES[4]:

    # region Initialize Figure
    figure  = Figure(
        name = 'Chromatiticy with Custom Interior Primaries{0}'.format(
            ' (inverted)' if INVERTED else ''
        ),
        size = 2 * [SIZE[1]],
        inverted = INVERTED
    )
    figure.set_fonts(**FONT_SIZES)
    panel = figure.add_panel(
        name = 'main',
        title = 'Chromaticity Diagram with Custom Primaries\n(maximizing triangle area inside Spectrum Locus)',
        x_label = 'x',
        x_ticks = linspace(0, 0.8, 9),
        x_lim = (-0.065, 0.865),
        y_label = 'y',
        y_ticks = linspace(0, 0.8, 9),
        y_lim = (-0.065, 0.865)
    )
    panel.set_aspect(
        aspect = 'equal', # Make horizontal and vertical axes the same scale
        adjustable = 'box' # Change the plot area aspect ratio to achieve this
    )
    # endregion

    # region Reference
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
        *transpose(spectrum_locus),
        color = figure.grey_level(0.25),
        zorder = 2
    )
    panel.plot(
        [spectrum_locus[0][0], spectrum_locus[-1][0]],
        [spectrum_locus[0][1], spectrum_locus[-1][1]],
        color = figure.grey_level(0.25),
        linestyle = ':',
        zorder = 2
    )
    # endregion

    # region Color Fill
    paths, colors = chromaticity_within_gamut(
        resolution = RESOLUTIONS[1],
        coefficients = INSIDE_PRIMARIES_COEFFICIENTS
    )
    panel.add_collection(
        PathCollection(
            paths,
            facecolors = colors,
            edgecolors = colors,
            zorder = 1
        )
    )
    paths, colors = chromaticity_outisde_gamut(
        resolution = RESOLUTIONS[1],
        coefficients = INSIDE_PRIMARIES_COEFFICIENTS
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

    # region Trace Gamut
    panel.plot(
        *transpose(
            list(
                tuple(
                    INSIDE_PRIMARIES_COEFFICIENTS[coordinate_index][index]
                    / sum(
                        list(
                            INSIDE_PRIMARIES_COEFFICIENTS[function_index][index]
                            for function_index in range(3)
                        )
                    )
                    for coordinate_index in range(2)
                )
                for index in [0, 1, 2, 0]
            )
        ),
        color = (0.25, 0.25, 0.25),
        zorder = 2
    )
    # endregion

    # region Save Figure
    figure.update()
    figure.save(
        path = 'images',
        name = figure.name,
        extension = EXTENSION
    )
    # endregion

# endregion

# region Figure 19  - Custom Primaries Outside Spectrum Locus

if SAVE_FIGURES[5]:

    # region Initialize Figure
    figure = Figure(
        name = 'Chromaticity with Custom Exterior Primaries{0}'.format(
            ' (inverted)' if INVERTED else ''
        ),
        size = 2 * [SIZE[1]],
        inverted = INVERTED
    )
    figure.set_fonts(**FONT_SIZES)
    panel = figure.add_panel(
        name = 'main',
        title = 'Chromaticity Diagram with Custom Primaries\n(tightly enclosing the Spectrum Locus)',
        x_label = 'x',
        x_ticks = linspace(0, 0.8, 9),
        x_lim = (-0.165, 0.965),
        y_label = 'y',
        y_ticks = linspace(0, 0.8, 9),
        y_lim = (-0.165, 0.965)
    )
    panel.set_aspect(
        aspect = 'equal', # Make horizontal and vertical axes the same scale
        adjustable = 'box' # Change the plot area aspect ratio to achieve this
    )
    # endregion

    # region Reference
    panel.axhline(
        y = 0,
        linewidth = 2,
        color = figure.grey_level(0),
        zorder = 1
    )
    panel.axvline(
        x = 0,
        linewidth = 2,
        color = figure.grey_level(0),
        zorder = 1
    )
    panel.plot(
        [0, 1],
        [1, 0],
        linestyle = '--',
        color = figure.grey_level(0.5),
        zorder = 1
    )
    panel.plot(
        *transpose(spectrum_locus),
        color = figure.grey_level(0.25),
        zorder = 2
    )
    panel.plot(
        [spectrum_locus[0][0], spectrum_locus[-1][0]],
        [spectrum_locus[0][1], spectrum_locus[-1][1]],
        color = figure.grey_level(0.25),
        linestyle = ':',
        zorder = 2
    )
    # endregion

    # region Color Fill
    paths, colors = chromaticity_within_gamut(
        resolution = RESOLUTIONS[1],
        coefficients = OUTSIDE_PRIMARIES_COEFFICIENTS
    )
    panel.add_collection(
        PathCollection(
            paths,
            facecolors = colors,
            edgecolors = colors,
            zorder = -1
        )
    )
    panel.fill( # (Un)fill outside of spectrum locus (upper portion)
        *transpose(
            spectrum_locus
            + [(1.5, -0.5), (1.5, 1.5), (-0.5, 1.5), (-0.5, -0.5)]
            + [spectrum_locus[0]]
        ),
        color = figure.grey_level(1),
        zorder = 0
    )
    panel.fill( # (Un)fill outside of spectrum locus (lower portion)
        *transpose(
            list(
                spectrum_locus[index]
                for index in [0, -1]
            )
            + [(1.5, -0.5), (-0.5, -0.5)]
        ),
        color = figure.grey_level(1),
        zorder = 0
    )
    # endregion

    # region Trace Gamut
    panel.plot(
        *transpose(
            list(
                tuple(
                    OUTSIDE_PRIMARIES_COEFFICIENTS[coordinate_index][index]
                    / sum(
                        list(
                            OUTSIDE_PRIMARIES_COEFFICIENTS[function_index][index]
                            for function_index in range(3)
                        )
                    )
                    for coordinate_index in range(2)
                )
                for index in [0, 1, 2, 0]
            )
        ),
        color = (0.25, 0.25, 0.25),
        linestyle = ':',
        zorder = 2
    )
    # endregion

    # region Save Figure
    figure.update()
    figure.save(
        path = 'images',
        name = figure.name,
        extension = EXTENSION
    )
    # endregion

# endregion
