"""
Figures illustrating blackbody radiation, the Planckian locus in CIE 1931 and
1960 chromaticity diagrams, isotherm lines and the estimation of correlated
color temperature.

Figure Captions:
22 - Blackbody radiation spectra and their chromaticities.  The left panel shows
blackbody spectra (in log scale) for a selection of temperatures in Kelvin.  The
right panel plots these temperatures along the Planckian Locus (running from
100 K to 1,000,000 K - marked as infinity as, in chromaticity space, it's close
enough).
23 - Chromaticity diagrams for the CIE 1931 (x, y) and CIE 1960 (u, v)
standards.  While the latter appears to be rotated, it is more accurately
squished and/or stretched; note that the spectrum locus approaches closest to
the vertical axis between 500 and 510 nm in both diagrams.  The Planckian locus,
and the sRGB display gamut, are illustrated for comparison.
24 - CIE 1960 chromaticity diagram with isotherm lines extending from selected
temperatures.  A selection of standard illuminants are also annotated and their
estimated correlated color temperature provided in the legend.
25 - Chromaticity diagrams for the CIE 1931 (x, y) and CIE 1960 (u, v) standards
with selected isotherm lines annotated.  The region in which correlated color
temperatures may be estimated is outlined.  Note that the length and
perpendicularity of isotherm lines is not preserved in CIE 1931 space -
correlated color temperature must be estimated in CIE 1960 space, regardless of
the color space ultimately being visualized or discussed.
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
    True, # Figure 22 - Planckian locus and blackbody spectra
    True, # Figure 23 - CIE 1931 vs 1960 chromaticity diagrams
    True, # Figure 24 - Isotherm lines close look
    True # Figure 25 - Isotherm lines in CIE 1931 and 1960
)
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
from numpy import arange, linspace, transpose
from csv import DictReader
from maths.correlated_color_temperature import (
    chromaticity_from_temperature,
    isotherm_endpoints_from_temperature,
    TEMPERATURES,
    radiant_emitance,
    temperature_chromaticities,
    xy_to_uv,
    correlated_color_temperature
)
from maths.rgb_cie_conversions import (
    rgb_to_chromoluminance,
    chromoluminance_to_rgb
)
from figure.figure import Figure
from maths.saturated_color_paths import (
    chromaticity_within_gamut,
    chromaticity_outside_gamut
)
from matplotlib.collections import PathCollection
from matplotlib.path import Path
# endregion

# region Constants
SELECTED_TEMPERATURES = [1000, 2000, 3000, 4000, 5000, 6000, 8000, 12000]
WAVELENGTH_BOUNDS = (365, 655)
WAVELENGTH_TICKS = [
    400,
    450,
    475
] + list(int(tick) for tick in arange(480, 601, 5)) + [
    610,
    625,
    650
]
WAVELENGTH_TICKS_UV = [
    400,
    450,
    475
] + list(int(tick) for tick in arange(480, 501, 5)) + list(int(tick) for tick in arange(510, 601, 10)) + [
    610,
    625,
    650
]

"""
From https://en.wikipedia.org/wiki/Standard_illuminant
"""
ILLUMINANTS_CHROMATICITY = {
    'A' : (0.44757, 0.40745), # Incandescent / Tungsten (~2856K)
    'D65' : (0.31271, 0.32902), # Daylight (~6504K)
    'E' : (1 / 3, 1 / 3), # Equal Energy (~5454K)
    'F3' : (0.40910, 0.39430) # White Fluorescent (~3450K)
}
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

# region Determine Select Temperature Chromaticities
chromaticities = dict()
for temperature in SELECTED_TEMPERATURES:
    chromaticities[temperature] = chromaticity_from_temperature(temperature)
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

# region Isotherm Lines
selected_endpoints = list()
for temperature in SELECTED_TEMPERATURES:
    selected_endpoints.append(
        isotherm_endpoints_from_temperature(temperature)
    )
endpoints = list()
for temperature in TEMPERATURES:
    endpoints.append(
        isotherm_endpoints_from_temperature(temperature)
    )
# endregion

# region Figure 22 - Planckian Locus and Blackbody Radiation

if SAVE_FIGURES[0]:

    # region Initialize Figure
    figure = Figure(
        name = 'Blackbody Radiation and Planckian Locus{0}'.format(
            ' (inverted)' if INVERTED else ''
        ),
        size = SIZE,
        inverted = INVERTED
    )
    figure.set_fonts(**FONT_SIZES)
    spectra_panel = figure.add_panel(
        name = 'spectra',
        title = 'Blackbody Radiation Spectra',
        position = (0, 0, 0.5, 1),
        x_label = 'Wavelength (nm)',
        x_lim = WAVELENGTH_BOUNDS,
        x_ticks = WAVELENGTH_TICKS,
        x_tick_labels = list(
            wavelength_tick if str(wavelength_tick)[-2:] in ['00', '50'] else ''
            for wavelength_tick in WAVELENGTH_TICKS
        ),
        y_label = r'Radiant Emitance ($\frac{W}{m^3}$)'
    )
    spectra_panel.set_yscale('log')
    chromaticity_panel = figure.add_panel(
        name = 'chromaticity',
        title = 'CIE 1931 Chromaticity Diagram\nwith Planckian Locus',
        position = (0.5, 0, 0.5, 1),
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
    # endregion

    # region Reference
    spectra_panel.axhline(
        y = 0,
        linewidth = 2,
        color = figure.grey_level(0),
        zorder = 0
    )
    chromaticity_panel.axhline(
        y = 0,
        linewidth = 2,
        color = figure.grey_level(0.75),
        zorder = 0
    )
    chromaticity_panel.axvline(
        x = 0,
        linewidth = 2,
        color = figure.grey_level(0.75),
        zorder = 0
    )
    chromaticity_panel.plot(
        [0, 1],
        [1, 0],
        linestyle = '--',
        color = figure.grey_level(0.75),
        zorder = 0
    )
    chromaticity_panel.plot(
        list(datum['x'] for datum in spectrum_locus),
        list(datum['y'] for datum in spectrum_locus),
        color = figure.grey_level(0.25),
        zorder = 2
    )
    chromaticity_panel.plot(
        [spectrum_locus[0]['x'], spectrum_locus[-1]['x']],
        [spectrum_locus[0]['y'], spectrum_locus[-1]['y']],
        color = figure.grey_level(0.25),
        linestyle = ':',
        zorder = 2
    )
    # endregion

    # region Color Fill
    paths, colors = chromaticity_within_gamut(
        resolution = RESOLUTION
    )
    chromaticity_panel.add_collection(
        PathCollection(
            paths,
            facecolors = colors,
            edgecolors = colors,
            zorder = 1
        )
    )
    paths, colors = chromaticity_outside_gamut(
        resolution = RESOLUTION
    )
    chromaticity_panel.add_collection(
        PathCollection(
            paths,
            facecolors = colors,
            edgecolors = colors,
            zorder = 1
        )
    )
    # endregion

    # region Wavelength Annotation
    figure.annotate_coordinates(
        name = 'chromaticity',
        coordinates = list(
            (
                datum['x'],
                datum['y']
            )
            for datum in spectrum_locus
            if datum['Wavelength'] in [WAVELENGTH_BOUNDS[0]] + WAVELENGTH_TICKS + [WAVELENGTH_BOUNDS[1]]
        ),
        coordinate_labels = [''] + WAVELENGTH_TICKS + [''],
        omit_endpoints = True,
        distance_proportion = 0.01,
        show_ticks = True,
        font_size = figure.font_sizes['legends'],
        font_color = figure.grey_level(0),
        tick_color = figure.grey_level(0),
        z_order = 3
    )
    # endregion

    # region Planckian Locus
    chromaticity_panel.plot(
        *transpose(
            list(
                temperature_chromaticity[0]
                for temperature_chromaticity in temperature_chromaticities
            )
        ),
        color = (0.25, 0.25, 0.25),
        linewidth = 2,
        zorder = 3
    )
    # endregion

    # region Blackbody Spectra and Temperature Chromaticities
    wavelengths = arange(
        WAVELENGTH_TICKS[0],
        WAVELENGTH_TICKS[-1] + 1,
        5
    )
    legend_handles = list()
    for temperature in SELECTED_TEMPERATURES:
        spectrum = list(
            (
                wavelength,
                radiant_emitance(
                    int(wavelength),
                    temperature
                )
            )
            for wavelength in wavelengths
        )
        spectra_panel.plot(
            *transpose(spectrum),
            color = figure.grey_level(0.25),
            zorder = 1
        )
        spectra_panel.annotate(
            text = '{0:,} K'.format(temperature),
            xy = (
                wavelengths[0] - 5,
                spectrum[0][1]
            ),
            xycoords = 'data',
            horizontalalignment = 'right',
            verticalalignment = 'top',
            fontsize = figure.font_sizes['legends'],
            color = figure.grey_level(0),
            zorder = 2
        )
        color = chromoluminance_to_rgb(
            *chromaticities[temperature][0],
            0.05 # Arbitrarily low
        )
        color = list(value / max(color) for value in color) # Saturate
        legend_handles.append(
            spectra_panel.plot( # Dummy series outside viewable range
                WAVELENGTH_BOUNDS[1] + 50,
                spectrum[-1][1],
                linestyle = 'none',
                marker = 'o',
                markersize = 8,
                markeredgecolor = 'none',
                markerfacecolor = color
            )[0]
        )
        chromaticity_panel.plot(
            *chromaticities[temperature][0],
            linestyle = 'none',
            marker = 'o',
            markersize = 8,
            markeredgecolor = (0.25, 0.25, 0.25),
            markerfacecolor = color,
            zorder = 4
        )
    spectra_panel.legend(
        reversed(legend_handles),
        reversed(list('{0:,} K'.format(temperature) for temperature in SELECTED_TEMPERATURES)),
        loc = 'lower right',
        facecolor = figure.grey_level(1)
    )
    # endregion

    # region Annotate Temperatures
    for temperature, chromaticity in chromaticities.items():
        chromaticity_panel.annotate(
            text = '{0:,} K'.format(temperature),
            xy = (
                chromaticity[0][0] - 0.005,
                chromaticity[0][1] + (-0.005 if temperature == 1000 else 0.005)
            ),
            xycoords = 'data',
            horizontalalignment= 'right',
            verticalalignment = 'top' if temperature == 1000 else 'bottom',
            fontsize = figure.font_sizes['legends'],
            color = (0.25, 0.25, 0.25),
            zorder = 5
        )
    chromaticity_panel.annotate(
        text = r'$\infty$',
        xy = (
            temperature_chromaticities[-1][0][0] - 0.005,
            temperature_chromaticities[-1][0][1] - 0.005
        ),
        xycoords = 'data',
        horizontalalignment = 'right',
        verticalalignment = 'top',
        fontsize = figure.font_sizes['legends'] + 4,
        color = (0.25, 0.25, 0.25),
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

# region Figure 23 - CIE 1931 and CIE 1960 Chromaticity Diagrams

if SAVE_FIGURES[1]:

    # region Initialize Figure
    figure = Figure(
        name = 'CIE 1931 and CIE 1960 Chromaticity Diagrams{0}'.format(
            ' (inverted)' if INVERTED else ''
        ),
        size = SIZE,
        inverted = INVERTED
    )
    figure.set_fonts(**FONT_SIZES)
    xy_panel = figure.add_panel(
        name = 'xy',
        title = 'CIE 1931 (x, y) Chromaticity Diagram',
        position = (0, 0, 0.5, 1),
        x_label = 'x',
        x_ticks = linspace(0, 0.8, 9),
        x_lim = (-0.065, 0.865),
        y_label = 'y',
        y_ticks = linspace(0, 0.8, 9),
        y_lim = (-0.065, 0.865)
    )
    uv_panel = figure.add_panel(
        name = 'uv',
        title = 'CIE 1960 (u, v) Chromaticity Diagram',
        position = (0.5, 0, 0.5, 1),
        x_label = 'u',
        x_ticks = linspace(0, 0.6, 7),
        x_lim = (-0.05, 0.7),
        y_label = 'v',
        y_ticks = linspace(0, 0.4, 5),
        y_lim = (-0.2, 0.55)
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
            color = figure.grey_level(0.75),
            zorder = 0
        )
        panel.axvline(
            x = 0,
            linewidth = 2,
            color = figure.grey_level(0.75),
            zorder = 0
        )
    xy_panel.plot(
        [0, 1],
        [1, 0],
        linestyle = '--',
        color = figure.grey_level(0.75),
        zorder = 0
    )
    uv_panel.plot(
        *transpose(list(xy_to_uv(x, y) for x, y in [(0.0, 1.0), (1.0, 0.0)])),
        linestyle = '--',
        color = figure.grey_level(0.75),
        zorder = 0
    )
    xy_panel.plot(
        list(datum['x'] for datum in spectrum_locus),
        list(datum['y'] for datum in spectrum_locus),
        color = figure.grey_level(0.25),
        zorder = 2
    )
    xy_panel.plot(
        [spectrum_locus[0]['x'], spectrum_locus[-1]['x']],
        [spectrum_locus[0]['y'], spectrum_locus[-1]['y']],
        color = figure.grey_level(0.25),
        linestyle = ':',
        zorder = 2
    )
    uv_panel.plot(
        *transpose(
            list(
                xy_to_uv(
                    datum['x'],
                    datum['y']
                )
                for datum in spectrum_locus
            )
        ),
        color = figure.grey_level(0.25),
        zorder = 2
    )
    uv_panel.plot(
        *transpose(
            list(
                xy_to_uv(
                    datum['x'],
                    datum['y']
                )
                for datum in [spectrum_locus[0], spectrum_locus[-1]]
            )
        ),
        color = figure.grey_level(0.25),
        linestyle = ':',
        zorder = 2
    )
    xy_panel.plot(
        *transpose(
            list(
                srgb_primary_chromaticities[index]
                for index in [0, 1, 2, 0]
            )
        ),
        color = (0.5, 0.5, 0.5),
        zorder = 3
    )
    uv_panel.plot(
        *transpose(
            list(
                xy_to_uv(*srgb_primary_chromaticities[index])
                for index in [0, 1, 2, 0]
            )
        ),
        color = (0.5, 0.5, 0.5),
        zorder = 3
    )
    # endregion

    # region Color Fill
    paths, colors = chromaticity_within_gamut(
        resolution = RESOLUTION
    )
    xy_panel.add_collection(
        PathCollection(
            paths,
            facecolors = colors,
            edgecolors = colors,
            zorder = 1
        )
    )
    uv_panel.add_collection(
        PathCollection(
            list(
                Path(
                    list(
                        xy_to_uv(*vertice)
                        for vertice in path.vertices
                    )
                )
                for path in paths
            ),
            facecolors = colors,
            edgecolors = colors,
            zorder = 1
        )
    )
    paths, colors = chromaticity_outside_gamut(
        resolution = RESOLUTION
    )
    xy_panel.add_collection(
        PathCollection(
            paths,
            facecolors = colors,
            edgecolors = colors,
            zorder = 1
        )
    )
    uv_panel.add_collection(
        PathCollection(
            list(
                Path(
                    list(
                        xy_to_uv(*vertice)
                        for vertice in path.vertices
                    )
                )
                for path in paths
            ),
            facecolors = colors,
            edgecolors = colors,
            zorder = 1
        )
    )
    # endregion

    # region Planckian Locus
    xy_panel.plot(
        *transpose(
            list(
                temperature_chromaticity[0]
                for temperature_chromaticity in temperature_chromaticities
            )
        ),
        color = (0.25, 0.25, 0.25),
        linewidth = 2,
        zorder = 4
    )
    uv_panel.plot(
        *transpose(
            list(
                temperature_chromaticity[1]
                for temperature_chromaticity in temperature_chromaticities
            )
        ),
        color = (0.25, 0.25, 0.25),
        linewidth = 2,
        zorder = 4
    )
    for chromaticity in chromaticities.values():
        xy_panel.plot(
            *chromaticity[0],
            linestyle = 'none',
            marker = 'o',
            markersize = 8,
            markeredgecolor = 'none',
            markerfacecolor = (0.25, 0.25, 0.25),
            zorder = 5
        )
        uv_panel.plot(
            *chromaticity[1],
            linestyle = 'none',
            marker = 'o',
            markersize = 8,
            markeredgecolor = 'none',
            markerfacecolor = (0.25, 0.25, 0.25),
            zorder = 5
        )
    # endregion

    # region Wavelength Annotations
    figure.annotate_coordinates(
        name = 'xy',
        coordinates = list(
            (
                datum['x'],
                datum['y']
            )
            for datum in spectrum_locus
            if datum['Wavelength'] in [WAVELENGTH_BOUNDS[0]] + WAVELENGTH_TICKS + [WAVELENGTH_BOUNDS[1]]
        ),
        coordinate_labels = [''] + WAVELENGTH_TICKS + [''],
        omit_endpoints = True,
        distance_proportion = 0.01,
        show_ticks = True,
        font_size = figure.font_sizes['legends'],
        font_color = figure.grey_level(0),
        tick_color = figure.grey_level(0),
        z_order = 3
    )
    figure.annotate_coordinates(
        name = 'uv',
        coordinates = list(
            xy_to_uv(datum['x'], datum['y'])
            for datum in spectrum_locus
            if datum['Wavelength'] in [WAVELENGTH_BOUNDS[0]] + WAVELENGTH_TICKS_UV + [WAVELENGTH_BOUNDS[1]]
        ),
        coordinate_labels = [''] + WAVELENGTH_TICKS_UV + [''],
        omit_endpoints = True,
        distance_proportion = 0.01,
        show_ticks = True,
        font_size = figure.font_sizes['legends'],
        font_color = figure.grey_level(0),
        tick_color = figure.grey_level(0),
        z_order = 3
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

# region Figure 24 - CIE 1960 Chromaticity Diagram with Isotherm Lines (zoomed)

if SAVE_FIGURES[2]:

    # region Initialize Figure
    figure = Figure(
        name = 'CIE 1960 Chromaticity Diagram with Isotherm Lines (zoomed){0}'.format(
            ' (inverted)' if INVERTED else ''
        ),
        size = SIZE,
        inverted = INVERTED
    )
    figure.set_fonts(**FONT_SIZES)
    panel = figure.add_panel(
        name = 'main',
        title = 'CIE 1960 Chromaticity Diagram with Isotherm Lines',
        x_label = 'u',
        x_lim = (0.075, 0.525),
        x_ticks = arange(0.1, 0.51, 0.05),
        x_margin = 0.0,
        y_label = 'v',
        y_lim = (0.2125, 0.4375),
        y_ticks = arange(0.225, 0.426, 0.025),
        y_margin = 0.0
    )
    panel.set_aspect(
        aspect = 'equal', # Make horizontal and vertical axes the same scale
        adjustable = 'box' # Change the plot area aspect ratio to achieve this
    )
    # endregion

    # region Reference
    panel.plot(
        *transpose(list(xy_to_uv(x, y) for x, y in [(0.0, 1.0), (1.0, 0.0)])),
        linestyle = '--',
        color = figure.grey_level(0.75),
        zorder = 0
    )
    panel.plot(
        *transpose(
            list(
                xy_to_uv(
                    datum['x'],
                    datum['y']
                )
                for datum in spectrum_locus
            )
        ),
        color = figure.grey_level(0.25),
        zorder = 2
    )
    panel.plot(
        *transpose(
            list(
                xy_to_uv(
                    datum['x'],
                    datum['y']
                )
                for datum in [spectrum_locus[0], spectrum_locus[-1]]
            )
        ),
        color = figure.grey_level(0.25),
        linestyle = ':',
        zorder = 2
    )
    # endregion

    # region Color Fill
    paths, colors = chromaticity_within_gamut(
        resolution = RESOLUTION
    )
    panel.add_collection(
        PathCollection(
            list(
                Path(
                    list(
                        xy_to_uv(*vertice)
                        for vertice in path.vertices
                    )
                )
                for path in paths
            ),
            facecolors = colors,
            edgecolors = colors,
            zorder = 1
        )
    )
    paths, colors = chromaticity_outside_gamut(
        resolution = RESOLUTION
    )
    panel.add_collection(
        PathCollection(
            list(
                Path(
                    list(
                        xy_to_uv(*vertice)
                        for vertice in path.vertices
                    )
                )
                for path in paths
            ),
            facecolors = colors,
            edgecolors = colors,
            zorder = 1
        )
    )
    # endregion

    # region Planckian Locus
    panel.plot(
        *transpose(
            list(
                temperature_chromaticity[1]
                for temperature_chromaticity in temperature_chromaticities
            )
        ),
        color = (0.25, 0.25, 0.25),
        linewidth = 2,
        zorder = 3
    )
    # endregion

    # region Isotherm Lines
    for temperature_index, temperature in enumerate(SELECTED_TEMPERATURES):
        panel.plot(
            [
                selected_endpoints[temperature_index][1][0][0],
                selected_endpoints[temperature_index][1][1][0]
            ],
            [
                selected_endpoints[temperature_index][1][0][1],
                selected_endpoints[temperature_index][1][1][1]
            ],
            color = (0.25, 0.25, 0.25),
            zorder = 4
        )
        panel.annotate(
            text = '{0:,} K'.format(temperature),
            xy = (
                selected_endpoints[temperature_index][1][1 if temperature < 3500 else 0][0]
                + (0.0 if temperature < 3500 else -0.001),
                selected_endpoints[temperature_index][1][1 if temperature < 3500 else 0][1]
                + (-0.001 if temperature < 3500 else 0.0)
            ),
            xycoords = 'data',
            horizontalalignment = 'center' if temperature < 3500 else 'right',
            verticalalignment = 'top' if temperature < 3500 else 'center',
            fontsize = figure.font_sizes['legends'],
            color = (0.25, 0.25, 0.25),
            zorder = 5
        )
    panel.annotate(
        text = r'$\infty$',
        xy = (
            temperature_chromaticities[-1][1][0] - 0.001,
            temperature_chromaticities[-1][1][1] - 0.001
        ),
        xycoords = 'data',
        horizontalalignment = 'center',
        verticalalignment = 'top',
        fontsize = figure.font_sizes['legends'] + 4,
        color = (0.25, 0.25, 0.25),
        zorder = 5
    )
    # endregion

    # region Standard Illuminants
    legend_handles = list(); legend_labels = list()
    for illuminant_name, illuminant_chromaticity in ILLUMINANTS_CHROMATICITY.items():
        color = chromoluminance_to_rgb(
            *illuminant_chromaticity,
            0.05 # Arbitrarily low
        )
        color = list(value / max(color) for value in color) # Saturate
        legend_handles.append(
            panel.plot(
                *xy_to_uv(*illuminant_chromaticity),
                linestyle = 'none',
                marker = 'o',
                markersize = 8,
                markeredgecolor = (0, 0, 0),
                markerfacecolor = color,
                zorder = 6
            )[0]
        )
        legend_labels.append(
            'Illuminant {0}: ~{1:,} K'.format(
                illuminant_name,
                int(correlated_color_temperature(*xy_to_uv(*illuminant_chromaticity))[0])
            )
        )
    panel.legend(
        legend_handles,
        legend_labels,
        loc = 'upper right',
        facecolor = figure.grey_level(1),
        markerfirst = False
    )
    illuminants_chromaticity_uv = {
        key : xy_to_uv(*value)
        for key, value in ILLUMINANTS_CHROMATICITY.items()
    }
    panel.annotate(
        text = 'A',
        xy = (
            illuminants_chromaticity_uv['A'][0],
            illuminants_chromaticity_uv['A'][1] + 0.0025
        ),
        xycoords = 'data',
        horizontalalignment = 'center',
        verticalalignment = 'bottom',
        fontsize = figure.font_sizes['legends'],
        color = (0, 0, 0),
        zorder = 5
    )
    panel.annotate(
        text = 'F3',
        xy = (
            illuminants_chromaticity_uv['F3'][0],
            illuminants_chromaticity_uv['F3'][1] + 0.0025
        ),
        xycoords = 'data',
        horizontalalignment = 'center',
        verticalalignment = 'bottom',
        fontsize = figure.font_sizes['legends'],
        color = (0, 0, 0),
        zorder = 5
    )
    panel.annotate(
        text = 'E',
        xy = (
            illuminants_chromaticity_uv['E'][0] + 0.0025,
            illuminants_chromaticity_uv['E'][1] - 0.0025
        ),
        xycoords = 'data',
        horizontalalignment = 'left',
        verticalalignment = 'top',
        fontsize = figure.font_sizes['legends'],
        color = (0, 0, 0),
        zorder = 5
    )
    panel.annotate(
        text = 'D65',
        xy = (
            illuminants_chromaticity_uv['D65'][0] - 0.0025,
            illuminants_chromaticity_uv['D65'][1]
        ),
        xycoords = 'data',
        horizontalalignment = 'right',
        verticalalignment = 'center',
        fontsize = figure.font_sizes['legends'],
        color = (0, 0, 0),
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

# region Figure 25 - CIE 1931 and CIE 1960 Chromaticity Diagrams with Isotherm Lines

if SAVE_FIGURES[3]:

    # region Initialize Figure
    figure = Figure(
        name = 'CIE 1931 and CIE 1960 Chromaticity Diagrams with Isotherm Lines{0}'.format(
            ' (inverted)' if INVERTED else ''
        ),
        size = SIZE,
        inverted = INVERTED
    )
    figure.set_fonts(**FONT_SIZES)
    xy_panel = figure.add_panel(
        name = 'xy',
        title = 'CIE 1931 (x, y) Chromaticity Diagram\nwith Isotherm Lines',
        position = (0, 0, 0.5, 1),
        x_label = 'x',
        x_ticks = linspace(0, 0.8, 9),
        x_lim = (-0.065, 0.865),
        y_label = 'y',
        y_ticks = linspace(0, 0.8, 9),
        y_lim = (-0.065, 0.865)
    )
    uv_panel = figure.add_panel(
        name = 'uv',
        title = 'CIE 1960 (u, v) Chromaticity Diagram\nwith Isotherm Lines',
        position = (0.5, 0, 0.5, 1),
        x_label = 'u',
        x_ticks = linspace(0, 0.6, 7),
        x_lim = (-0.05, 0.7),
        y_label = 'v',
        y_ticks = linspace(0, 0.4, 5),
        y_lim = (-0.2, 0.55)
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
    xy_panel.plot(
        [0, 1],
        [1, 0],
        linestyle = '--',
        color = figure.grey_level(0.5),
        zorder = 0
    )
    uv_panel.plot(
        *transpose(list(xy_to_uv(x, y) for x, y in [(0.0, 1.0), (1.0, 0.0)])),
        linestyle = '--',
        color = figure.grey_level(0.5),
        zorder = 0
    )
    xy_panel.plot(
        list(datum['x'] for datum in spectrum_locus),
        list(datum['y'] for datum in spectrum_locus),
        color = figure.grey_level(0.25),
        zorder = 2
    )
    xy_panel.plot(
        [spectrum_locus[0]['x'], spectrum_locus[-1]['x']],
        [spectrum_locus[0]['y'], spectrum_locus[-1]['y']],
        color = figure.grey_level(0.25),
        linestyle = ':',
        zorder = 2
    )
    uv_panel.plot(
        *transpose(
            list(
                xy_to_uv(
                    datum['x'],
                    datum['y']
                )
                for datum in spectrum_locus
            )
        ),
        color = figure.grey_level(0.25),
        zorder = 2
    )
    uv_panel.plot(
        *transpose(
            list(
                xy_to_uv(
                    datum['x'],
                    datum['y']
                )
                for datum in [spectrum_locus[0], spectrum_locus[-1]]
            )
        ),
        color = figure.grey_level(0.25),
        linestyle = ':',
        zorder = 2
    )
    # endregion

    # region Color Fill
    paths, colors = chromaticity_within_gamut(
        resolution = RESOLUTION
    )
    xy_panel.add_collection(
        PathCollection(
            paths,
            facecolors = colors,
            edgecolors = colors,
            zorder = 1
        )
    )
    uv_panel.add_collection(
        PathCollection(
            list(
                Path(
                    list(
                        xy_to_uv(*vertice)
                        for vertice in path.vertices
                    )
                )
                for path in paths
            ),
            facecolors = colors,
            edgecolors = colors,
            zorder = 1
        )
    )
    paths, colors = chromaticity_outside_gamut(
        resolution = RESOLUTION
    )
    xy_panel.add_collection(
        PathCollection(
            paths,
            facecolors = colors,
            edgecolors = colors,
            zorder = 1
        )
    )
    uv_panel.add_collection(
        PathCollection(
            list(
                Path(
                    list(
                        xy_to_uv(*vertice)
                        for vertice in path.vertices
                    )
                )
                for path in paths
            ),
            facecolors = colors,
            edgecolors = colors,
            zorder = 1
        )
    )
    # endregion

    # region Isotherm Region and Lines
    for temperature_index, temperature in enumerate(SELECTED_TEMPERATURES):
        xy_panel.plot(
            [
                selected_endpoints[temperature_index][0][0][0],
                selected_endpoints[temperature_index][0][1][0]
            ],
            [
                selected_endpoints[temperature_index][0][0][1],
                selected_endpoints[temperature_index][0][1][1]
            ],
            color = (0.25, 0.25, 0.25),
            zorder = 3
        )
        uv_panel.plot(
            [
                selected_endpoints[temperature_index][1][0][0],
                selected_endpoints[temperature_index][1][1][0]
            ],
            [
                selected_endpoints[temperature_index][1][0][1],
                selected_endpoints[temperature_index][1][1][1]
            ],
            color = (0.25, 0.25, 0.25),
            zorder = 3
        )
        xy_panel.annotate(
            text = '{0:,} K'.format(temperature),
            xy = (
                selected_endpoints[temperature_index][0][1 if temperature < 3500 else 0][0]
                + (0.0 if temperature < 3500 else -0.001),
                selected_endpoints[temperature_index][0][1 if temperature < 3500 else 0][1]
                + (-0.001 if temperature < 3500 else 0.0)
            ),
            xycoords = 'data',
            horizontalalignment = 'left' if temperature < 3500 else 'right',
            verticalalignment = 'top' if temperature < 3500 else 'center',
            fontsize = figure.font_sizes['legends'] - 2,
            color = (0.25, 0.25, 0.25),
            zorder = 5
        )
        uv_panel.annotate(
            text = '{0:,} K'.format(temperature),
            xy = (
                selected_endpoints[temperature_index][1][1 if temperature < 3500 else 0][0]
                + (0.0 if temperature < 3500 else -0.001),
                selected_endpoints[temperature_index][1][1 if temperature < 3500 else 0][1]
                + (-0.002 if temperature < 3500 else 0.0)
            ),
            xycoords = 'data',
            horizontalalignment = 'left' if temperature < 3500 else 'right',
            verticalalignment = 'top' if temperature < 3500 else 'center',
            fontsize = figure.font_sizes['legends'] - 2,
            color = (0.25, 0.25, 0.25),
            zorder = 5
        )
    xy_panel.annotate(
        text = r'$\infty$',
        xy = (
            temperature_chromaticities[-1][0][0] - 0.001,
            temperature_chromaticities[-1][0][1] - 0.001
        ),
        xycoords = 'data',
        horizontalalignment = 'center',
        verticalalignment = 'top',
        fontsize = figure.font_sizes['legends'] + 4,
        color = (0.25, 0.25, 0.25),
        zorder = 5
    )
    uv_panel.annotate(
        text = r'$\infty$',
        xy = (
            temperature_chromaticities[-1][1][0] - 0.001,
            temperature_chromaticities[-1][1][1] - 0.001
        ),
        xycoords = 'data',
        horizontalalignment = 'center',
        verticalalignment = 'top',
        fontsize = figure.font_sizes['legends'] + 4,
        color = (0.25, 0.25, 0.25),
        zorder = 5
    )
    xy_panel.plot(
        *transpose(
            list(
                temperature_chromaticity[0]
                for temperature_chromaticity in temperature_chromaticities
            )
        ),
        color = (0.25, 0.25, 0.25),
        linewidth = 2,
        zorder = 3
    )
    uv_panel.plot(
        *transpose(
            list(
                temperature_chromaticity[1]
                for temperature_chromaticity in temperature_chromaticities
            )
        ),
        color = (0.25, 0.25, 0.25),
        linewidth = 2,
        zorder = 3
    )
    xy_panel.plot(
        *transpose(
            list(
                endpoint[0][0]
                for endpoint in endpoints
            ) + list(
                reversed(
                    list(
                        endpoint[0][1]
                        for endpoint in endpoints
                    )
                )
            ) + [endpoints[0][0][0]]
        ),
        linewidth = 0.5,
        color = figure.grey_level(0.75),
        zorder = 4
    )
    uv_panel.plot(
        *transpose(
            list(
                endpoint[1][0]
                for endpoint in endpoints
            ) + list(
                reversed(
                    list(
                        endpoint[1][1]
                        for endpoint in endpoints
                    )
                )
            ) + [endpoints[0][1][0]]
        ),
        linewidth = 0.5,
        color = figure.grey_level(0.75),
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
