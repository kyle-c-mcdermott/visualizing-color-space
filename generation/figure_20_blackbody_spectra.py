"""
Blackbody radiation spectra and (x, y) chromaticity diagram.

Caption: Blackbody spectra for selected temperatures and their chromaticities
plotted along the Planckian locus in CIE 1931 2-degree (x, y) chromaticity
space.  Note that the Planckian locus is not actually drawn out to infinity -
it ends at 10^10 here - but chromaticity changes become infinitesimal as
temperatures become infinite.
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
from maths.plotting_series import (
    spectrum_locus_1931_2,
    color_matching_functions_1931_2
)
from numpy import arange, transpose
from figure.figure import Figure
from maths.color_temperature import (
    spectrum_from_temperature,
    tristimulus_from_spectrum,
    generate_temperature_series
)
from maths.color_conversion import xyz_to_xyy, xyy_to_xyz, xyz_to_rgb
from maths.coloration import (
    chromaticity_outside_gamut,
    chromaticity_inside_gamut
)
from matplotlib.collections import PathCollection
# endregion

# region Plot Settings
INVERTED = False
SIZE = (8, 4)
FONT_SIZES = {
    'titles' : 14,
    'labels' : 12,
    'ticks' : 10,
    'legends' : 7
}
EXTENSION = 'svg'
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
    name = 'figure_20_blackbody_spectra{0}'.format(
        '_inverted' if INVERTED else ''
    ),
    size = SIZE,
    inverted = INVERTED
)
figure.set_fonts(**FONT_SIZES)
mid_point = 0.5
spectra_panel = figure.add_panel(
    name = 'spectra',
    title = '',
    position = (0, 0, mid_point, 1),
    x_label = r'Wavelength $\lambda$ ($nm$)',
    x_lim = (
        WAVELENGTH_TICKS[0],
        WAVELENGTH_TICKS[-1]
    ),
    x_margin = 0.0,
    x_ticks = WAVELENGTH_TICKS,
    x_tick_labels = list(
        wavelength_tick
        if int(wavelength_tick / 50) == wavelength_tick / 50
        else ''
        for wavelength_tick in WAVELENGTH_TICKS
    ),
    y_label = r'Radiant Emitance ($\frac{W}{m^3}$)'
)
chromaticity_panel = figure.add_panel(
    name = 'chromaticity',
    title = '',
    position = (mid_point, 0, 1 - mid_point, 1),
    x_label = 'x',
    x_ticks = arange(0, 0.81, 0.1),
    x_lim = (-0.065, 0.865),
    y_label = 'y',
    y_ticks = arange(0, 0.81, 0.1),
    y_lim = (-0.065, 0.865)
)
chromaticity_panel.set_aspect(
    aspect = 'equal', # Make horizontal and vertical axes the same scale
    adjustable = 'box' # Change the plot area aspect ratio to achieve this
)
spectra_panel.set_yscale('log')
# endregion

# region Reference Lines
spectra_panel.axhline(
    y = 0,
    linewidth = 2,
    color = figure.grey_level(0.25),
    zorder = 0
)
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
    linestyle = '--',
    color = figure.grey_level(0.75),
    zorder = 1
)
chromaticity_panel.plot(
    list(datum['x'] for datum in spectrum_locus_1931_2),
    list(datum['y'] for datum in spectrum_locus_1931_2),
    color = figure.grey_level(0.25),
    zorder = 3
)
chromaticity_panel.plot(
    [spectrum_locus_1931_2[0]['x'], spectrum_locus_1931_2[-1]['x']],
    [spectrum_locus_1931_2[0]['y'], spectrum_locus_1931_2[-1]['y']],
    color = figure.grey_level(0.25),
    linestyle = ':',
    zorder = 2
)
# endregion

# region Blackbody Spectra
selected_temperatures = dict()
legend_handles = list()
for temperature in reversed(TEMPERATURES):
    spectrum = spectrum_from_temperature(temperature)
    tristimulus = tristimulus_from_spectrum(spectrum)
    chromaticity = xyz_to_xyy(*tristimulus)[0:2]
    color = xyz_to_rgb(
        *xyy_to_xyz(
            *chromaticity,
            0.05 # arbitrarily low
        )
    )
    color = tuple(value / max(color) for value in color)
    selected_temperatures[temperature] = {
        'chromaticity' : chromaticity,
        'color' : color
    }
    legend_handles.append(
        spectra_panel.plot(
            list(datum['Wavelength'] for datum in color_matching_functions_1931_2),
            spectrum,
            color = color,
            zorder = 1
        )[0]
    )
spectra_panel.legend(
    legend_handles,
    list(
        '{0:,}{1}'.format(
            temperature,
            r'$K$'
        )
        for temperature in reversed(TEMPERATURES)
    ),
    markerfirst = False,
    loc = 'lower right',
    facecolor = figure.grey_level(1)
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

# region Planckian Locus
pl_temperatures, pl_chromaticities = generate_temperature_series()
chromaticity_panel.plot(
    *transpose(pl_chromaticities),
    color = 3 * [0.25],
    zorder = 4
)
for temperature, appearance in selected_temperatures.items():
    chromaticity_panel.plot(
        *appearance['chromaticity'],
        linestyle = 'none',
        marker = 'o',
        markersize = 4,
        markeredgecolor = 3 * [0.25],
        markerfacecolor = appearance['color'],
        zorder = 5
    )
    chromaticity_panel.annotate(
        text = '{0:,}{1}'.format(temperature, r'$K$'),
        xy = (
            appearance['chromaticity'][0] - 0.005,
            appearance['chromaticity'][1] + 0.005
        ),
        xycoords = 'data',
        horizontalalignment = 'right',
        verticalalignment = 'bottom',
        fontsize = figure.font_sizes['legends'],
        color = 3 * [0.25],
        zorder = 6
    )
chromaticity_panel.annotate(
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
    zorder = 6
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
