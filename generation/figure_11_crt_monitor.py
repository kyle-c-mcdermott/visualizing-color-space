"""
Plotting the phosphor spectra and monitor color gamut.

Caption: Red, green, and blue phosphor spectra measured from a CRT monitor.
Above each spectral line is also shown the summed spectrum of white (dashed
line).  The right panel plots the chromaticities (within the CIE 170-2 10-degree
standard) of the three phosphors and white; the triangle formed by the three
primaries is the monitor's color gamut.  All colors that can be shown by
combining the three phosphors at various intensities fall within the color gamut
triangle.
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
from maths.color_conversion import xyz_to_xyy
from maths.color_temperature import tristimulus_from_spectrum
from maths.chromaticity_conversion import STANDARD
from maths.plotting_series import (
    phosphor_spectra,
    spectrum_locus_1931_2
)
from maths.conversion_coefficients import COLOR_NAMES
from figure.figure import Figure
from numpy import arange, transpose
# endregion

# region Plot Settings
INVERTED = False
SIZE = (8, 4.5)
FONT_SIZES = {
    'titles' : 14,
    'labels' : 12,
    'ticks' : 10,
    'legends' : 8
}
EXTENSION = 'svg'
# endregion

# region Estimate Chromaticities from Spectra
phosphor_chromaticities = {
    color_name : xyz_to_xyy(
        *tristimulus_from_spectrum(
            list(
                (
                    datum['Wavelength'],
                    datum[color_name]
                )
                for datum in phosphor_spectra
            ),
            standard = STANDARD.CIE_170_2_10.value
        )
    )[0:2]
    for color_name in COLOR_NAMES
}
white_chromaticity = xyz_to_xyy(
    *tristimulus_from_spectrum(
        list(
            (
                datum['Wavelength'],
                sum(list(datum[color_name] for color_name in COLOR_NAMES))
            )
            for datum in phosphor_spectra
        ),
        standard = STANDARD.CIE_170_2_10.value
    )
)[0:2]
# endregion

# region Estimate and Print Tristimulus Values for CRT Phosphors
phosphor_tristimulus = {
    color_name : tristimulus_from_spectrum(
        list(
            (
                datum['Wavelength'],
                datum[color_name]
            )
            for datum in phosphor_spectra
        ),
        standard = STANDARD.CIE_170_2_10.value
    )
    for color_name in COLOR_NAMES
}
print('\nCRT Phosphor Tristimulus Values:')
for tristimulus_index in range(3):
    print(
        '{0:0.6f}, {1:0.6f}, {2:0.6f}'.format(
            *list(
                phosphor_tristimulus[color_name][tristimulus_index]
                for color_name in COLOR_NAMES
            )
        )
    )
# endregion

# region Initialize Figure
figure = Figure(
    name = 'figure_11_crt_monitor{0}'.format(
        '_inverted' if INVERTED else ''
    ),
    size = SIZE,
    inverted = INVERTED
)
figure.set_fonts(**FONT_SIZES)
mid_point = 0.439
red_panel = figure.add_panel(
    name = 'Red',
    title = '',
    position = (0, 2 / 3, mid_point, 1 / 3),
    x_label = r'Wavelength $\lambda$ ($nm$)',
    x_lim = (375, 725),
    x_margin = 0.0,
    y_label = 'Radiance',
    y_ticks = []
)
green_panel = figure.add_panel(
    name = 'Green',
    title = '',
    position = (0, 1 / 3, mid_point, 1 / 3),
    x_label = r'Wavelength $\lambda$ ($nm$)',
    x_lim = (375, 725),
    x_margin = 0.0,
    y_label = 'Radiance',
    y_ticks = []
)
blue_panel = figure.add_panel(
    name = 'Blue',
    title = '',
    position = (0, 0 / 3, mid_point, 1 / 3),
    x_label = r'Wavelength $\lambda$ ($nm$)',
    x_lim = (375, 725),
    x_margin = 0.0,
    y_label = 'Radiance',
    y_ticks = []
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
# endregion

# region Reference Lines
for panel in figure.panels.values():
    panel.axhline(
        y = 0,
        linewidth = 2,
        color = figure.grey_level(0.25),
        zorder = 1
    )
chromaticity_panel.axvline(
    x = 0,
    linewidth = 2,
    color = figure.grey_level(0.25),
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
    color = figure.grey_level(0.5),
    zorder = 3
)
chromaticity_panel.plot(
    [spectrum_locus_1931_2[0]['x'], spectrum_locus_1931_2[-1]['x']],
    [spectrum_locus_1931_2[0]['y'], spectrum_locus_1931_2[-1]['y']],
    linestyle = ':',
    color = figure.grey_level(0.5),
    zorder = 2
)
# endregion

# region Plot Spectra
for color_index, color_name in enumerate(COLOR_NAMES):
    legend_handles = list()
    legend_handles.append(
        figure.panels[color_name].plot(
            list(datum['Wavelength'] for datum in phosphor_spectra),
            list(
                sum(
                    list(
                        datum[phosphor_name]
                        for phosphor_name in COLOR_NAMES
                    )
                )
                for datum in phosphor_spectra
            ),
            color = figure.grey_level(0.5),
            linestyle = '--',
            zorder = 2
        )[0]
    )
    phosphor_color = 3 * [0]; phosphor_color[color_index] = 0.8
    legend_handles.append(
        figure.panels[color_name].plot(
            list(datum['Wavelength'] for datum in phosphor_spectra),
            list(datum[color_name] for datum in phosphor_spectra),
            color = phosphor_color,
            zorder = 3
        )[0]
    )
    figure.panels[color_name].legend(
        legend_handles,
        [
            'White (Sum)',
            '{0} Phosphor'.format(color_name)
        ],
        markerfirst = False,
        loc = 'upper right' if color_name == 'Blue' else 'upper left',
        facecolor = figure.grey_level(1)
    )
# endregion

# region Fill Chromaticity Region (within SL and outside gamut)
chromaticity_panel.fill( # Gets most of it
    *transpose(
        list(
            (
                datum['x'],
                datum['y']
            )
            for datum in spectrum_locus_1931_2
        )
        + [(spectrum_locus_1931_2[0]['x'], spectrum_locus_1931_2[0]['y'])]
        + list(
            phosphor_chromaticities[color_name]
            for color_name in COLOR_NAMES
        )
        + [(spectrum_locus_1931_2[-1]['x'], spectrum_locus_1931_2[-1]['y'])]
    ),
    color = figure.grey_level(0.9),
    zorder = 0
)
chromaticity_panel.fill( # The last bit at the bottom
    *transpose(
        [(spectrum_locus_1931_2[0]['x'], spectrum_locus_1931_2[0]['y'])]
        + list(
            phosphor_chromaticities[color_name]
            for color_name in ['Blue', 'Red']
        )
        + list(
            (
                spectrum_locus_1931_2[index]['x'],
                spectrum_locus_1931_2[index]['y']
            )
            for index in [-1, 0]
        )
    ),
    color = figure.grey_level(0.9),
    zorder = 0
)
# endregion

# region Plot Chromaticities
legend_handles = list()
for color_index, color_name in enumerate(COLOR_NAMES):
    marker_color = 3 * [0]; marker_color[color_index] = 0.8
    legend_handles.append(
        chromaticity_panel.plot(
            *phosphor_chromaticities[color_name],
            linestyle = 'none',
            marker = 'o',
            markersize = 4,
            markeredgecolor = 'none',
            markerfacecolor = marker_color,
            zorder = 4
        )[0]
    )
legend_handles.append(
    chromaticity_panel.plot(
        *white_chromaticity,
        linestyle = 'none',
        marker = 'o',
        markersize = 4,
        markeredgecolor = figure.grey_level(0.2),
        markerfacecolor = figure.grey_level(1),
        zorder = 4
    )[0]
)
chromaticity_panel.legend(
    legend_handles,
    list(
        '{0} Phosphor ({1:0.3f}, {2:0.3f})'.format(
            color_name,
            *phosphor_chromaticities[color_name]
        )
        for color_name in COLOR_NAMES
    )
    + ['White ({0:0.3f}, {1:0.3f})'.format(*white_chromaticity)],
    markerfirst = False,
    loc = 'upper right' if color_name == 'Blue' else 'upper left',
    facecolor = figure.grey_level(1)
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
