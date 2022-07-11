"""
Plotting the (x, y) chromaticity space with spectrum loci of four different CIE
standards along with the chromaticity of D65.

Caption: Spectrum loci and D65 chromaticities for the CIE 170-2 10-degree and
2-degree, 1964 10-degree, and 1931 2-degree standards.  The chromaticity
coordinates for D65 are given in the legend.
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
    COLUMN_WIDTH,
    FONT_SIZES,
    AXES_GREY_LEVEL, DOTTED_GREY_LEVEL
)
from maths.chromaticity_conversion import STANDARD, xyz_to_xyy
from maths.color_temperature import tristimulus_from_spectrum
from maths.plotting_series import (
    d65_spectrum,
    spectrum_locus_170_2_10,
    spectrum_locus_170_2_2,
    spectrum_locus_1964_10,
    spectrum_locus_1931_2
)
from figure.figure import Figure
from numpy import arange
# endregion

# region Plot Settings
INVERTED = False
SIZE = (
    COLUMN_WIDTH,
    3.45
)
EXTENSION = 'pdf'
COLORS = {
    STANDARD.CIE_170_2_10.value : (0.2, 0.2, 0.8),
    STANDARD.CIE_170_2_2.value : (0.2, 0.8, 0.2),
    STANDARD.CIE_1964_10.value : (0.8, 0.2, 0.2),
    STANDARD.CIE_1931_2.value : 3 * [0.8 if INVERTED else 0.2]
}
LINE_STYLES = {
    STANDARD.CIE_170_2_10.value : '--',
    STANDARD.CIE_170_2_2.value : '-.',
    STANDARD.CIE_1964_10.value : ':',
    STANDARD.CIE_1931_2.value : '-'
}
MARKER_SIZES = {
    STANDARD.CIE_170_2_10.value : 4,
    STANDARD.CIE_170_2_2.value : 5.5,
    STANDARD.CIE_1964_10.value : 7,
    STANDARD.CIE_1931_2.value : 8.5
}
# endregion

# region Estimate D65 Chromaticity for Each Standard
d65_chromaticities = {
    standard.value : xyz_to_xyy(
        *tristimulus_from_spectrum(
            list(
                (
                    datum['Wavelength'],
                    datum['Energy']
                )
                for datum in d65_spectrum
            ),
            standard = standard.value
        )
    )[0:2]
    for standard in STANDARD
}
# endregion

# region Initialize Figure
figure = Figure(
    name = 'figure_08_chromaticity_spaces{0}'.format(
        '_inverted' if INVERTED else ''
    ),
    size = SIZE,
    inverted = INVERTED
)
figure.set_fonts(**FONT_SIZES)
panel = figure.add_panel(
    name = 'main',
    title = '',
    x_label = r'$x$',
    x_ticks = arange(0, 0.81, 0.1),
    x_lim = (-0.065, 0.865),
    y_label = r'$y$',
    y_ticks = arange(0, 0.81, 0.1),
    y_lim = (-0.065, 0.865)
)
panel.set_aspect(
    aspect = 'equal', # Make horizontal and vertical axes the same scale
    adjustable = 'box' # Change the plot area aspect ratio to achieve this
)
# endregion

# region Reference Lines
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
    zorder = 1
)
# endregion

# region Plot Spectrum Loci and D65 Chromaticities
legend_handles = list()
for standard, spectrum_locus in [
    (STANDARD.CIE_170_2_10.value, spectrum_locus_170_2_10),
    (STANDARD.CIE_170_2_2.value, spectrum_locus_170_2_2),
    (STANDARD.CIE_1964_10.value, spectrum_locus_1964_10),
    (STANDARD.CIE_1931_2.value, spectrum_locus_1931_2)
]:
    legend_handles.append(
        panel.plot(
            list(datum['x'] for datum in spectrum_locus),
            list(datum['y'] for datum in spectrum_locus),
            color = COLORS[standard],
            linestyle = LINE_STYLES[standard],
            zorder = 1
        )[0]
    )
    panel.plot(
        [spectrum_locus[0]['x'], spectrum_locus[-1]['x']],
        [spectrum_locus[0]['y'], spectrum_locus[-1]['y']],
        color = COLORS[standard],
        linestyle = LINE_STYLES[standard],
        zorder = 1
    )
    panel.plot(
        *d65_chromaticities[standard],
        linestyle = 'none',
        marker = 'o',
        markersize = MARKER_SIZES[standard],
        markerfacecolor = 'none',
        markeredgecolor = COLORS[standard],
        zorder = 2
    )
# endregion

# region Plot Legend
panel.legend(
    legend_handles,
    list(
        '{0}{1}\n({2:0.4f}, {3:0.4f})'.format(
            standard_string,
            r'$^\circ$',
            *d65_chromaticities[standard]
        )
        for standard, standard_string in [
            (STANDARD.CIE_170_2_10.value, 'CIE 170-2 10'),
            (STANDARD.CIE_170_2_2.value, 'CIE 170-2 2'),
            (STANDARD.CIE_1964_10.value, 'CIE 1964 10'),
            (STANDARD.CIE_1931_2.value, 'CIE 1931 2')
        ]
    ),
    markerfirst = False,
    loc = 'upper right',
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
