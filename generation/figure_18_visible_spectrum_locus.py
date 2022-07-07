"""
A filled-color chromaticity diagram with annotated wavelengths along the
spectrum locus and a vertical band showing the visible spectrum colors derived
from the colors in the chromaticity diagram.

Caption: Color-filled chromaticity diagram with annotated wavelengths.  The
vertical strip to the right shows the colors along the spectrum locus.  Named
colors are annotated along with the closest whole wavelength match; these are
the points where the saturated colors have only 0 or 1 in them (e.g. (1, 0, 1)
for yellow).
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
from maths.plotting_series import spectrum_locus_1931_2
from numpy import arange, ptp
from maths.coloration import (
    visible_spectrum,
    chromaticity_outside_gamut,
    chromaticity_inside_gamut
)
from figure.figure import Figure
from matplotlib.collections import PathCollection
# endregion

# region Plot Settings
INVERTED = False
SIZE = (6.5, 4)
FONT_SIZES = {
    'titles' : 14,
    'labels' : 12,
    'ticks' : 10,
    'legends' : 7
}
EXTENSION = 'svg'
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
    ] + list(arange(475, 601, 5, dtype = int)) + [
        610,
        625,
        650
    ] + [
        spectrum_locus_1931_2[-1]['Wavelength']
    ]
)
# endregion

# region Best Wavelengths for Named Colors
named_colors = {
    'Red' : (1.0, 0.0, 0.0),
    'Yellow' : (1.0, 1.0, 0.0),
    'Green' : (0.0, 1.0, 0.0),
    'Cyan' : (0.0, 1.0, 1.0),
    'Blue' : (0.0, 0.0, 1.0)
}
spectrum_paths, spectrum_colors = visible_spectrum(
    int(ptp(WAVELENGTH_TICKS)) + 1,
    0,
    WAVELENGTH_TICKS[0],
    1,
    int(ptp(WAVELENGTH_TICKS)),
    WAVELENGTH_TICKS[0],
    WAVELENGTH_TICKS[-1],
    vertical = True
)
best_wavelengths = {key : None for key in named_colors.keys()}
for wavelength_index, wavelength in enumerate(
    arange(WAVELENGTH_TICKS[0], WAVELENGTH_TICKS[-1] + 0.1, 1)
):
    for color_name, named_color in named_colors.items():
        error = sum(
            list(
                (
                    named_color[color_index]
                    - spectrum_colors[wavelength_index][color_index]
                ) ** 2.0
                for color_index in range(3)
            )
        )
        if best_wavelengths[color_name] is None or best_wavelengths[color_name][1] > error:
            best_wavelengths[color_name] = (wavelength, error)
# endregion

# region Initialize Figure
figure = Figure(
    name = 'figure_18_visible_spectrum_locus{0}'.format(
        '_inverted' if INVERTED else ''
    ),
    size = SIZE,
    inverted = INVERTED
)
figure.set_fonts(**FONT_SIZES)
mid_point = 0.65
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
spectrum_panel_back = figure.add_panel(
    name = 'spectrum_back',
    title = '',
    position = (mid_point, 0, 1 - mid_point, 1),
    x_lim = (0, 1),
    x_margin = 0.0,
    x_ticks = [],
    y_label = r'Wavelength $\lambda$ ($nm$)',
    y_lim = (
        WAVELENGTH_TICKS[0],
        WAVELENGTH_TICKS[-1]
    ),
    y_margin = 0.0,
    y_ticks = WAVELENGTH_TICKS[1:-1],
    y_tick_labels = list(
        wavelength_tick
        if int(wavelength_tick / 25) == wavelength_tick / 25
        else ''
        for wavelength_tick in WAVELENGTH_TICKS[1:-1]
    )
)
spectrum_panel_front = figure.add_panel(
    name = 'spectrum_front',
    title = '',
    position = (mid_point, 0, 1 - mid_point, 1),
    y_lim = (
        WAVELENGTH_TICKS[0],
        WAVELENGTH_TICKS[-1]
    ),
    y_margin = 0.0,
    y_ticks = list(best_wavelength[0] for best_wavelength in best_wavelengths.values()),
    y_tick_labels = list(
        '{0} ({1:0.0f}{2})'.format(
            color_name,
            best_wavelength[0],
            r'$nm$'
        )
        for color_name, best_wavelength in best_wavelengths.items()
    )
)
spectrum_panel_front.sharex(spectrum_panel_back)
spectrum_panel_front.yaxis.set_label_position('right')
spectrum_panel_front.yaxis.tick_right()
# endregion

# region Reference Lines
chromaticity_panel.axhline(
    y = 0,
    linewidth = 2,
    color = figure.grey_level(0.75),
    zorder = 1
)
chromaticity_panel.axvline(
    x = 0,
    linewidth = 2,
    color = figure.grey_level(0.75),
    zorder = 1
)
chromaticity_panel.plot(
    [0, 1],
    [1, 0],
    linestyle = ':',
    color = figure.grey_level(0.75),
    zorder = 1
)
chromaticity_panel.plot(
    list(datum['x'] for datum in spectrum_locus_1931_2),
    list(datum['y'] for datum in spectrum_locus_1931_2),
    solid_capstyle = 'round',
    color = figure.grey_level(0.25),
    zorder = 3
)
chromaticity_panel.plot(
    [spectrum_locus_1931_2[0]['x'], spectrum_locus_1931_2[-1]['x']],
    [spectrum_locus_1931_2[0]['y'], spectrum_locus_1931_2[-1]['y']],
    solid_capstyle = 'round',
    color = figure.grey_level(0.25),
    linestyle = ':',
    zorder = 2
)
# endregion

# region Fill Colors
paths, colors = chromaticity_outside_gamut(
    RESOLUTION * 6
)
chromaticity_panel.add_collection(
    PathCollection(
        paths,
        facecolors = colors,
        edgecolors = colors,
        linewidth = 0,
        zorder = 0
    )
)
paths, colors = chromaticity_inside_gamut(
    RESOLUTION
)
chromaticity_panel.add_collection(
    PathCollection(
        paths,
        facecolors = colors,
        edgecolors = colors,
        linewidth = 0,
        zorder = 1
    )
)
paths, colors = visible_spectrum(
    RESOLUTION * 6,
    0,
    WAVELENGTH_TICKS[0],
    1,
    int(ptp(WAVELENGTH_TICKS)),
    WAVELENGTH_TICKS[0],
    WAVELENGTH_TICKS[-1],
    vertical = True
)
spectrum_panel_back.add_collection(
    PathCollection(
        paths,
        facecolors = colors,
        edgecolors = colors,
        linewidth = 0,
        zorder = 0
    )
)
# endregion

# region Annotate Wavelengths
figure.annotate_coordinates(
    name = 'chromaticity',
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
    font_color = figure.grey_level(0),
    tick_color = figure.grey_level(0.25),
    z_order = 4
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
