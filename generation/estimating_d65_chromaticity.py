"""
Plotting the D65 Spectrum and illustrating how to use the color matching
functions to estimate trivalues (X, Y, Z) and chromaticity (x, y).

Figure Captions:
6 - Energy spectrum of the standard CIE Illuminant D65 (daylight, with a
correlated color temperature of roughly 6500K - that will be demonstrated later).
7 - The products of the D65 spectrum from Figure 6 with each of the color
matching functions from Figure 5 are shown on the left where the area under each
of the resulting curves (shaded) are annotated.  On the right, the trivalues X,
Y, and Z are converted to chromaticity (x, y) and plotted.  The resulting
chromaticity coordinates are reasonably close to those listed for the CIE 1964
10-degree diagram (of which the presented CIE 170-2 10-degree diagram is a
modification).
https://en.wikipedia.org/wiki/Standard_illuminant#White_points_of_standard_illuminants
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
    'legends' : 12
}
EXTENSION = 'svg'
LINE_COLORS = (
    (0.75, 0, 0.75), # X
    (1, 0.5, 0), # Y
    (0, 0, 1) # Z
)
FILL_COLORS = (
    (
        (0.5, 0, 0.5),
        (0.75, 0.25, 0),
        (0, 0, 0.5)
    )
    if INVERTED else (
        (1, 0.5, 1),
        (1, 0.75, 0.5),
        (0.5, 0.5, 1)
    )
)
# endregion

# region Imports
from csv import DictReader
from figure.figure import Figure
from numpy import arange, linspace, transpose, ptp
from maths.chromaticity_from_spectrum import chromaticity_from_spectrum
# endregion

# region Constants
FUNCTION_NAMES = ['X', 'Y', 'Z']
# endregion

# region Load in Data
"""
Tabulated color matching functions downloaded from:
http://www.cvrl.org/ciexyzpr.htm
Under "10-deg XYZ CMFs transformed from the CIE (2006) 10-deg LMS cone fundamentals"
using 1 nm Stepsize and csv Format
Here using CVRL's tabulated data instead of my own estimates because the CVRL
table has a slightly wider range of wavelengths (likely from extrapolation, but
the chromaticity estimate may be more accurate from the wider functions).
"""
with open(
    'cvrl/lin2012xyz10e_1_7sf.csv',
    'r'
) as read_file:
    color_matching_functions = list(
        {
            'Wavelength' : int(row['Wavelength']),
            'X' : float(row['X']),
            'Y' : float(row['Y']),
            'Z' : float(row['Z'])
        }
        for row in DictReader(
            read_file,
            fieldnames = ['Wavelength', 'X', 'Y', 'Z']
        )
    )
spectrum_locus = list(
    (
        datum['X'] / (datum['X'] + datum['Y'] + datum['Z']),
        datum['Y'] / (datum['X'] + datum['Y'] + datum['Z'])
    )
    for datum in color_matching_functions
)

"""
CIE Illuminant D65 Spectrum found on Older CIE Standards page:
http://www.cvrl.org/cie.htm
E/W button at the bottom of the page under CIE Illuminant D65
(no citation given)
Note: from the appearance the values tabulated here appear to be interpolated
linearly from a more sparsely sampled source.
"""
with open(
    'cvrl/Illuminantd65.csv',
    'r'
) as read_file:
    d65_spectrum = list( # Will leave out wavelengths not in the tabulated CMFs
        {
            'Wavelength' : int(row['Wavelength']),
            'Energy' : float(row['Energy'])
        }
        for row in DictReader(
            read_file,
            fieldnames = ['Wavelength', 'Energy']
        )
        if int(row['Wavelength']) in list(datum['Wavelength'] for datum in color_matching_functions)
    )
# endregion

# region Figure 6 - Illuminant D65 Spectrum

# region Initialize Figure
figure = Figure(
    name = 'D65 Spectrum{0}'.format(
        ' (inverted)' if INVERTED else ''
    ),
    size = SIZE,
    inverted = INVERTED
)
figure.set_fonts(**FONT_SIZES)
panel = figure.add_panel(
    name = 'main',
    title = 'CIE Standard Illuminant D65 Energy Spectrum',
    x_label = r'Wavelength $\lambda$ (nm)',
    x_lim = (385, 835),
    x_ticks = arange(400, 801, 50),
    y_label = 'Energy'
)
# endregion

# region Reference
panel.axhline(
    y = 0,
    linewidth = 2,
    color = figure.grey_level(0),
    zorder = 0
)
# endregion

# region Plot Spectrum
panel.plot(
    list(datum['Wavelength'] for datum in d65_spectrum),
    list(datum['Energy'] for datum in d65_spectrum),
    linewidth = 2,
    color = figure.grey_level(0.25),
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

# region Estimate D65 Chromaticity
products = {
    function_name : list(
        d65_spectrum[datum_index]['Energy'] * datum[function_name]
        for datum_index, datum in enumerate(color_matching_functions)
    )
    for function_name in FUNCTION_NAMES
}
d65_chromaticity = chromaticity_from_spectrum(
    list(
        (
            datum['Wavelength'],
            datum['Energy']
        )
        for datum in d65_spectrum
    ),
    standard = '170_2_10_deg'
)
# endregion

# region Figure 7 - Estimating D65 Chromaticity

# region Initialize Figure
figure = Figure(
    name = 'Estimating D65 Chromaticity{0}'.format(
        ' (inverted)' if INVERTED else ''
    ),
    size = SIZE,
    inverted = INVERTED
)
figure.set_fonts(**FONT_SIZES)
x_panel = figure.add_panel(
    name = 'x',
    title = 'Product of D65 Spectrum and X Function',
    position = (0, 2 / 3, 0.5, 1 / 3),
    x_label = r'Wavelength $\lambda$ (nm)',
    x_lim = (385, 835),
    x_ticks = arange(400, 801, 50),
    y_label = 'Product'
)
y_panel = figure.add_panel(
    name = 'y',
    title = 'Product of D65 Spectrum and Y Function',
    position = (0, 1 / 3, 0.5, 1 / 3),
    x_label = r'Wavelength $\lambda$ (nm)',
    x_lim = (385, 835),
    x_ticks = arange(400, 801, 50),
    y_label = 'Product'
)
z_panel = figure.add_panel(
    name = 'z',
    title = 'Product of D65 Spectrum and Z Function',
    position = (0, 0 / 3, 0.5, 1 / 3),
    x_label = r'Wavelength $\lambda$ (nm)',
    x_lim = (385, 835),
    x_ticks = arange(400, 801, 50),
    y_label = 'Product'
)
chromaticity_panel = figure.add_panel(
    name = 'chromaticity',
    title = 'Estimated Chromaticity of D65',
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
for panel in figure.panels.values():
    panel.axhline(
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
chromaticity_panel.plot(
    *transpose(spectrum_locus),
    color = figure.grey_level(0.25),
    zorder = 1
)
chromaticity_panel.plot(
    [spectrum_locus[0][0], spectrum_locus[-1][0]],
    [spectrum_locus[0][1], spectrum_locus[-1][1]],
    color = figure.grey_level(0.25),
    linestyle = ':',
    zorder = 1
)
# endregion

# region Plot Products and Chromaticity
for function_index, function_name in enumerate(FUNCTION_NAMES):
    figure.panels[function_name.lower()].fill(
        list(datum['Wavelength'] for datum in color_matching_functions)
        + [color_matching_functions[0]['Wavelength']],
        products[function_name] + [products[function_name][0]],
        color = FILL_COLORS[function_index],
        zorder = 1
    )
    figure.panels[function_name.lower()].plot(
        list(datum['Wavelength'] for datum in color_matching_functions),
        list(products[function_name]),
        linewidth = 2,
        color = LINE_COLORS[function_index],
        zorder = 2
    )
chromaticity_panel.plot(
    *d65_chromaticity[1],
    linestyle = 'none',
    marker = 'o',
    markersize = 8,
    markeredgecolor = 'none',
    markerfacecolor = figure.grey_level(0),
    zorder = 2
)
# endregion

# region Annotations
x_panel.annotate(
    text = '{0}{1:0.0f}'.format(
        r'$X=\int \bar{R}(\lambda)\bar{X}(\lambda)d\lambda\approx$',
        d65_chromaticity[0][0]
    ),
    xy = (
        x_panel.get_xlim()[1] - 0.1 * ptp(x_panel.get_xlim()),
        x_panel.get_ylim()[1] - 0.1 * ptp(x_panel.get_ylim())
    ),
    xycoords = 'data',
    horizontalalignment = 'right',
    verticalalignment = 'top',
    fontsize = figure.font_sizes['legends'],
    color = figure.grey_level(0),
    zorder = 3
)
y_panel.annotate(
    text = '{0}{1:0.0f}'.format(
        r'$Y=\int \bar{R}(\lambda)\bar{Y}(\lambda)d\lambda\approx$',
        d65_chromaticity[0][1]
    ),
    xy = (
        y_panel.get_xlim()[1] - 0.1 * ptp(y_panel.get_xlim()),
        y_panel.get_ylim()[1] - 0.1 * ptp(y_panel.get_ylim())
    ),
    xycoords = 'data',
    horizontalalignment = 'right',
    verticalalignment = 'top',
    fontsize = figure.font_sizes['legends'],
    color = figure.grey_level(0),
    zorder = 3
)
z_panel.annotate(
    text = '{0}{1:0.0f}'.format(
        r'$Z=\int \bar{R}(\lambda)\bar{Z}(\lambda)d\lambda\approx$',
        d65_chromaticity[0][2]
    ),
    xy = (
        z_panel.get_xlim()[1] - 0.1 * ptp(z_panel.get_xlim()),
        z_panel.get_ylim()[1] - 0.1 * ptp(z_panel.get_ylim())
    ),
    xycoords = 'data',
    horizontalalignment = 'right',
    verticalalignment = 'top',
    fontsize = figure.font_sizes['legends'],
    color = figure.grey_level(0),
    zorder = 3
)
chromaticity_panel.annotate(
    text = 'D65',
    xy = (
        d65_chromaticity[1][0] + 0.01,
        d65_chromaticity[1][1] + 0.01
    ),
    xycoords = 'data',
    horizontalalignment = 'left',
    verticalalignment = 'bottom',
    fontsize = figure.font_sizes['legends'],
    color = figure.grey_level(0),
    zorder = 3
)
chromaticity_panel.annotate(
    text = '{0}{1:0.4f}\n\n{2}{3:0.4f}'.format(
        r'$x=\frac{X}{X+Y+Z}\approx$',
        d65_chromaticity[1][0],
        r'$y=\frac{Y}{X+Y+Z}\approx$',
        d65_chromaticity[1][1]
    ),
    xy = (
        chromaticity_panel.get_xlim()[1] - 0.1 * ptp(chromaticity_panel.get_xlim()),
        chromaticity_panel.get_ylim()[1] - 0.1 * ptp(chromaticity_panel.get_ylim())
    ),
    xycoords = 'data',
    horizontalalignment = 'right',
    verticalalignment = 'top',
    fontsize = figure.font_sizes['legends'],
    color = figure.grey_level(0),
    zorder = 3
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
