"""
Illustrating the plotting of color versus wavelength of light.

Figure Captions:
20 - Chromaticity diagram annotated with wavelengths along the spectrum locus.
The corresponding colors from the coloration methods described above using the
sRGB primaries where they reach the spectrum locus (based on hue angle outward
from white point - D65) are illustrated in the vertical strip to the right.  The
approximate wavelength of named colors are given.  Note the uneven spacing of
wavelengths along the spectrum locus, emphasized by the same tick locations on
the linear-wavelength scale of the vertical strip.
21 - (Horizontal spectra - with red, green, and blue values - from sRGB conversion and approximating functions)
"""

# TODO: Come up with simplified, piecewise functions for red, green, and blue

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
INVERTED = True
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
from numpy import arange, ptp, linspace
from csv import DictReader
from maths.saturated_color_paths import (
    visible_spectrum,
    chromaticity_within_gamut,
    chromaticity_outisde_gamut
)
from figure.figure import Figure
from matplotlib.collections import PathCollection
# endregion

# region Constants
WAVELENGTH_BOUNDS = [370, 680]
WAVELENGTH_TICKS = [
    400,
    450,
    475
] + list(int(tick) for tick in arange(480, 601, 5)) + [
    610,
    625,
    650
]
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
"""
The effective limits of wavelength where RGB values can vary is roughly in the
interval [370, 680] when using sRGB and CIE 1931 standards
"""
# endregion

# region Estimate Named Color Wavelengths
paths, colors = visible_spectrum(
    0, 1, 0, 1,
    *WAVELENGTH_BOUNDS,
    resolution = int(ptp(WAVELENGTH_BOUNDS)) + 1
)
named_colors = {
    'Red' : (1.0, 0.0, 0.0),
    'Yellow' : (1.0, 1.0, 0.0),
    'Green' : (0.0, 1.0, 0.0),
    'Cyan' : (0.0, 1.0, 1.0),
    'Blue' : (0.0, 0.0, 1.0)
}
best_wavelengths = {key : None for key in named_colors.keys()}
for wavelength_index, wavelength in enumerate(
    arange(WAVELENGTH_BOUNDS[0], WAVELENGTH_BOUNDS[1] + 0.1, 1)
):
    for color_name, named_color in named_colors.items():
        error = sum(
            list(
                (
                    named_color[color_index]
                    - colors[wavelength_index][color_index]
                ) ** 2.0
                for color_index in range(3)
            )
        )
        if best_wavelengths[color_name] is None or best_wavelengths[color_name][1] > error:
            best_wavelengths[color_name] = (wavelength, error)
# endregion

# region Figure 20 - Wavelength Annotated Chromaticity Diagram and Vertical Color Spectrum

# region Initialize Figure
figure = Figure(
    name = 'Color Spectrum from Hue Angle{0}'.format(
        ' (inverted)' if INVERTED else ''
    ),
    size = (SIZE[1] * 1.25, SIZE[1]),
    inverted = INVERTED
)
figure.set_fonts(**FONT_SIZES)
chromaticity_panel = figure.add_panel(
    name = 'chromaticity',
    title = '{0}\n{1}'.format(
        r'CIE 1931 2$\degree$ Chromaticity Diagram',
        '(with annotated wavelengths)'
    ),
    position = (0, 0, 3 / 4, 1),
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
spectrum_panel_back = figure.add_panel(
    name = 'spectrum_back',
    title = 'Visible Spectrum Derived\nfrom Chromatic Angles\naround White',
    position = (3 / 4, 0, 1 / 4, 1),
    x_lim = (0, 1),
    x_ticks = [],
    x_margin = 0.0,
    y_label = 'Wavelength (nm)',
    y_lim = WAVELENGTH_BOUNDS,
    y_ticks = WAVELENGTH_TICKS,
    y_tick_labels = list(
        wavelength_tick
        if str(wavelength_tick)[-1] != '5'
        else ''
        for wavelength_tick in WAVELENGTH_TICKS
    ),
    y_margin = 0.0
)
spectrum_panel_front = figure.add_panel(
    name = 'spectrum_front',
    title = '',
    position = (3 / 4, 0, 1 / 4, 1),
    y_lim = WAVELENGTH_BOUNDS,
    y_ticks = list(best_wavelength[0] for best_wavelength in best_wavelengths.values()),
    y_tick_labels = list(
        '{0}\n{1:0.0f} nm'.format(
            color_name,
            best_wavelength[0]
        )
        for color_name, best_wavelength in best_wavelengths.items()
    ),
    y_margin = 0.0
)
spectrum_panel_front.sharex(spectrum_panel_back)
spectrum_panel_front.yaxis.set_label_position('right')
spectrum_panel_front.yaxis.tick_right()
# endregion

# region Reference
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
paths, colors = chromaticity_outisde_gamut(
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
paths, colors = visible_spectrum(
    0,
    WAVELENGTH_BOUNDS[0],
    1,
    int(ptp(WAVELENGTH_BOUNDS)),
    *WAVELENGTH_BOUNDS,
    resolution = RESOLUTION * 8,
    vertical = True
)
spectrum_panel_back.add_collection(
    PathCollection(
        paths,
        facecolors = colors,
        edgecolors = colors,
        zorder = 0
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

# region Save Figure
figure.update()
figure.save(
    path = 'images',
    name = figure.name,
    extension = EXTENSION
)
# endregion

# endregion

# region Figure 21 - Spectrum Color RGB Series

# region Initialize Figure
figure = Figure(
    name = 'Color Spectrum RGB Functions{0}'.format(
        ' (inverted)' if INVERTED else ''
    ),
    size = SIZE,
    inverted = INVERTED
)
figure.set_fonts(**FONT_SIZES)
spectra_panel = figure.add_panel(
    name = 'spectra',
    title = 'Visible Spectra Derived from\nChromatic Angles and Simplifying Functions',
    position = (0, 2 / 3, 1, 1 / 3),
    x_label = 'Wavelength (nm)',
    x_lim = WAVELENGTH_BOUNDS,
    x_margin = 0.0,
    x_ticks = arange(
        375,
        676,
        25
    ),
    y_lim = (0, 1),
    y_margin = 0.0,
    y_ticks = (0.25, 0.75),
    y_tick_labels = [
        'from\nChromaticity',
        'Simplified'
    ]
)
rgb_panel = figure.add_panel(
    name = 'rgb',
    title = 'Red, Green, and Blue Values of Visible Spectrum',
    position = (0, 0, 1, 2 / 3),
    x_label = 'Wavelength (nm)',
    x_lim = WAVELENGTH_BOUNDS,
    x_margin = 0.0,
    x_ticks = arange(
        375,
        676,
        25
    ),
    y_label = 'Color Value',
    y_ticks = linspace(0, 1, 5)
)
# endregion

# region Reference
for y in [0, 1]:
    rgb_panel.axhline(
        y = y,
        linewidth = 2,
        color = figure.grey_level(0),
        zorder = 0
    )
# endregion

# region Color Fill and Value Plotting
paths, colors = visible_spectrum(
    WAVELENGTH_BOUNDS[0],
    0,
    int(ptp(WAVELENGTH_BOUNDS)),
    0.5,
    *WAVELENGTH_BOUNDS,
    resolution = RESOLUTION * 8
)
spectra_panel.add_collection(
    PathCollection(
        paths,
        facecolors = colors,
        edgecolors = colors,
        zorder = 0
    )
)
for color_index in range(3):
    color = 3 * [0.0]; color[color_index] = 1.0
    rgb_panel.plot(
        linspace(*WAVELENGTH_BOUNDS, RESOLUTION * 8),
        list(datum[color_index] for datum in colors),
        linewidth = 2,
        color = color,
        zorder = 1
    )
# endregion

# region Annotations
for color_name, best_wavelength in best_wavelengths.items():
    rgb_panel.plot(
        2 * [best_wavelength[0]],
        [0, 1],
        linestyle = ':',
        linewidth = 0.5,
        color = named_colors[color_name],
        zorder = -1
    )
    rgb_panel.annotate(
        text = '{0}\n{1:0.0f} nm'.format(
            color_name,
            best_wavelength[0]
        ),
        xy = (
            best_wavelength[0],
            (0.0 if color_name in ['Red', 'Green', 'Blue'] else 1.0)
            + (-0.01 if color_name in ['Red', 'Green', 'Blue'] else 0.01)
        ),
        xycoords = 'data',
        horizontalalignment = 'center',
        verticalalignment = 'top' if color_name in ['Red', 'Green', 'Blue'] else 'bottom',
        fontsize = figure.font_sizes['legends'],
        color = figure.grey_level(0),
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
