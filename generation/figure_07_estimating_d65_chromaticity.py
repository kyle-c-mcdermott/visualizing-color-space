"""
Plotting the product of the color matching functions and the D65 spectrum and
the resulting chromaticity coordinate.

Caption: Illustration of the estimation of chromaticity from a spectrum.  The
three left panels show the products of the three color matching functions with
the D65 spectrum.  The area shaded under each resulting curve is annotated
within each panel by applying equation X.  The right panel shows the resulting
chromaticity coordinate (x, y).
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
    d65_spectrum,
    color_matching_functions_170_2_10,
    spectrum_locus_170_2_10
)
from maths.conversion_coefficients import TRISTIMULUS_NAMES
from maths.color_temperature import tristimulus_from_spectrum
from maths.chromaticity_conversion import STANDARD, xyz_to_xyy
from figure.figure import Figure
from numpy import arange, transpose, ptp
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
LINE_COLORS = (
    (0.8, 0, 0.8), # X
    (0.8, 0.5, 0), # Y
    (0, 0, 0.8) # Z
)
FILL_COLORS = (
    (
        (0.5, 0, 0.5), # X
        (0.75, 0.25, 0), # Y
        (0, 0, 0.5)
    )
    if INVERTED else (
        (1, 0.5, 1), # X
        (1, 0.75, 0.5), # Y
        (0.5, 0.5, 1) # Z
    )
)
# endregion

# region Multiply Color Matching Functions by Spectrum
d65_spectrum_by_wavelength = {
    datum['Wavelength'] : datum['Energy']
    for datum in d65_spectrum
}
color_matching_functions_by_wavelength = {
    datum['Wavelength'] : {
        tristimulus_name : datum[tristimulus_name]
        for tristimulus_name in TRISTIMULUS_NAMES
    }
    for datum in color_matching_functions_170_2_10
}
product_series = {
    tristimulus_name : list(
        (
            wavelength,
            (
                d65_spectrum_by_wavelength[wavelength]
                * color_matching_functions_by_wavelength[wavelength][tristimulus_name]
            )
        )
        for wavelength in color_matching_functions_by_wavelength.keys()
        if wavelength in d65_spectrum_by_wavelength
    )
    for tristimulus_name in TRISTIMULUS_NAMES
}
# endregion

# region Estimate D65 Chromaticity
tristimulus_values = tristimulus_from_spectrum( # Effectively completes what's above
    list(
        (
            datum['Wavelength'],
            datum['Energy']
        )
        for datum in d65_spectrum
    ),
    standard = STANDARD.CIE_170_2_10.value
)
chromaticity = xyz_to_xyy(*tristimulus_values)[0:2]
# endregion

# region Initialize Figure
figure = Figure(
    name = 'figure_07_estimating_d65_chromaticity{0}'.format(
        '_inverted' if INVERTED else ''
    ),
    size = SIZE,
    inverted = INVERTED
)
figure.set_fonts(**FONT_SIZES)
mid_point = 0.435
x_panel = figure.add_panel(
    name = 'X',
    title = '',
    position = (0, 2 / 3, mid_point, 1 / 3),
    x_label = r'Wavelength $\lambda$ ($nm$)',
    x_lim = (375, 725),
    x_margin = 0.0,
    y_label = 'Product',
    y_ticks = []
)
y_panel = figure.add_panel(
    name = 'Y',
    title = '',
    position = (0, 1 / 3, mid_point, 1 / 3),
    x_label = r'Wavelength $\lambda$ ($nm$)',
    x_lim = (375, 725),
    x_margin = 0.0,
    y_label = 'Product',
    y_ticks = []
)
z_panel = figure.add_panel(
    name = 'Z',
    title = '',
    position = (0, 0 / 3, mid_point, 1 / 3),
    x_label = r'Wavelength $\lambda$ ($nm$)',
    x_lim = (375, 725),
    x_margin = 0.0,
    y_label = 'Product',
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
# endregion

# region Plot and Fill Product Series
for tristimulus_index, tristimulus_name in enumerate(TRISTIMULUS_NAMES):
    figure.panels[tristimulus_name].fill(
        *transpose(
            product_series[tristimulus_name]
            + [product_series[tristimulus_name][0]]
        ),
        color = FILL_COLORS[tristimulus_index],
        zorder = 0
    )
    figure.panels[tristimulus_name].plot(
        *transpose(product_series[tristimulus_name]),
        color = LINE_COLORS[tristimulus_index],
        zorder = 2
    )
# endregion

# region Plot Spectrum Locus and D65 Chromaticity Coordinate
chromaticity_panel.plot(
    list(datum['x'] for datum in spectrum_locus_170_2_10),
    list(datum['y'] for datum in spectrum_locus_170_2_10),
    color = figure.grey_level(0.5),
    zorder = 3
)
chromaticity_panel.plot(
    [spectrum_locus_170_2_10[0]['x'], spectrum_locus_170_2_10[-1]['x']],
    [spectrum_locus_170_2_10[0]['y'], spectrum_locus_170_2_10[-1]['y']],
    linestyle = ':',
    color = figure.grey_level(0.5),
    zorder = 2
)
chromaticity_panel.plot(
    *chromaticity,
    linestyle = 'none',
    marker = 'o',
    markersize = 4,
    markeredgecolor = 'none',
    markerfacecolor = figure.grey_level(0),
    zorder = 3
)
# endregion

# region Annotations
annotation_text = [
    '{0}{1:0.0f}'.format(
        r'$X_{D65}=\int \bar{R}_{D65}(\lambda)\bar{X}(\lambda)d\lambda\approx$',
        tristimulus_values[0]
    ),
    '{0}{1:0.0f}'.format(
        r'$Y_{D65}=\int \bar{R}_{D65}(\lambda)\bar{Y}(\lambda)d\lambda\approx$',
        tristimulus_values[1]
    ),
    '{0}{1:0.0f}'.format(
        r'$Z_{D65}=\int \bar{R}_{D65}(\lambda)\bar{Z}(\lambda)d\lambda\approx$',
        tristimulus_values[2]
    )
]
for tristimulus_index, tristimulus_name in enumerate(TRISTIMULUS_NAMES):
    figure.panels[tristimulus_name].annotate(
        text = annotation_text[tristimulus_index],
        xy = (
            figure.panels[tristimulus_name].get_xlim()[1]
            - 0.05 * ptp(figure.panels[tristimulus_name].get_xlim()),
            figure.panels[tristimulus_name].get_ylim()[1]
            - 0.05 * ptp(figure.panels[tristimulus_name].get_ylim())
        ),
        xycoords = 'data',
        horizontalalignment = 'right',
        verticalalignment = 'top',
        fontsize = figure.font_sizes['legends'],
        color = figure.grey_level(0),
        zorder = 3
    )
chromaticity_panel.annotate(
    text = '{0}\n({1:0.4f}, {2:0.4f})'.format(
        r'$D65$',
        *chromaticity
    ),
    xy = (
        chromaticity[0],
        chromaticity[1] - 0.02
    ),
    xycoords = 'data',
    horizontalalignment = 'center',
    verticalalignment = 'top',
    fontsize = figure.font_sizes['legends'],
    color = figure.grey_level(0),
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
