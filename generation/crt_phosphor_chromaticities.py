"""
Plotting the spectra and chromaticities for the three phosphors of a CRT display
and their combined output (white).

Figure Captions:
10 - Luminance spectra of the three phorphors of a CRT display measured with a
spectroradiometer (Photo Research PR 650, if memory serves).  In each panel the
summed spectrum representing white is also shown along with the individual
phosphor spectra.
11 - The products of the CRT white spectrum with each of the color matching
functions are shown on the left where the areas under each of the resulting
curves (shaded) are annotated.  On the right are plotted the chromaticity of
white as well as the three CRT phosphors.  The interior of the spectrum locus is
shaded except for the triangular region formed by the three display phosphors to
indicate the portion of the spectrum locus where chromaticities can be achieved
by mixing of the three phosphors.
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
from numpy.linalg import inv
# endregion

# region Contants
COLOR_NAMES = ['Red', 'Green', 'Blue']
FUNCTION_NAMES = ['X', 'Y', 'Z']
# endregion

# region Load in Data
"""
Tabulated CRT Spectra recorded with a Photo Research spectroradiometer (PR650?)
many years ago (monitor specifications not recorded)
"""
with open(
    'data/crt_phosphors.csv',
    'r'
) as read_file:
    phosphor_spectra = list(
        {
            'Wavelength' : int(row['Wavelength']),
            'Red' : float(row['Red']),
            'Green' : float(row['Green']),
            'Blue' : float(row['Blue'])
        }
        for row in DictReader(read_file)
    )

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

# endregion

# region Figure 10 - CRT Phorphor Spectra

# region Initialize Figure
figure = Figure(
    name = 'CRT Phosphor Spectra{0}'.format(
        ' (inverted)' if INVERTED else ''
    ),
    size = SIZE,
    inverted = INVERTED
)
figure.set_fonts(**FONT_SIZES)
red_panel = figure.add_panel(
    name = 'red',
    title = 'CRT Red Phosphor Spectrum',
    position = (0, 2 / 3, 1, 1 / 3),
    x_label = r'Wavelength $\lambda$ (nm)',
    x_lim = (370, 790),
    x_ticks = arange(400, 751, 50),
    y_label = r'Luminance $\frac{Cd}{m^2}$'
)
green_panel = figure.add_panel(
    name = 'green',
    title = 'CRT Green Phosphor Spectrum',
    position = (0, 1 / 3, 1, 1 / 3),
    x_label = r'Wavelength $\lambda$ (nm)',
    x_lim = (370, 790),
    x_ticks = arange(400, 751, 50),
    y_label = r'Luminance $\frac{Cd}{m^2}$'
)
blue_panel = figure.add_panel(
    name = 'blue',
    title = 'CRT Blue Phosphor Spectrum',
    position = (0, 0 / 3, 1, 1 / 3),
    x_label = r'Wavelength $\lambda$ (nm)',
    x_lim = (370, 790),
    x_ticks = arange(400, 751, 50),
    y_label = r'Luminance $\frac{Cd}{m^2}$'
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
# endregion

# region Plot Spectra
for color_index, color_name in enumerate(COLOR_NAMES):
    color = 3 * [0]; color[color_index] = 1
    legend_handles = list()
    legend_handles.append(
        figure.panels[color_name.lower()].plot(
            list(datum['Wavelength'] for datum in phosphor_spectra),
            list(datum[color_name] for datum in phosphor_spectra),
            linewidth = 2,
            color = color,
            zorder = 2
        )[0]
    )
    legend_handles.append(
        figure.panels[color_name.lower()].plot(
            list(datum['Wavelength'] for datum in phosphor_spectra),
            list(
                sum(
                    list(
                        datum[color_name_2]
                        for color_name_2 in COLOR_NAMES
                    )
                )
                for datum in phosphor_spectra
            ),
            color = figure.grey_level(0.75),
            zorder = 1
        )[0]
    )
    figure.panels[color_name.lower()].legend(
        legend_handles,
        [
            '{0} Spectrum'.format(color_name),
            'White Spectrum\n(sum of all three phorphors)'
        ],
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
# endregion

# endregion

# region Estimate CRT Chromaticities
products = {
    function_name : list(
        {
            'Wavelength' : cmf_datum['Wavelength'],
            'Product' : (
                cmf_datum[function_name]
                * list(
                    sum(
                        list(
                            spectra_datum[color_name]
                            for color_name in COLOR_NAMES
                        )
                    )
                    for spectra_datum in phosphor_spectra
                    if spectra_datum['Wavelength'] == cmf_datum['Wavelength']
                )[0]
            )
        }
        for cmf_datum in color_matching_functions
        if cmf_datum['Wavelength'] in list(datum['Wavelength'] for datum in phosphor_spectra)
    )
    for function_name in FUNCTION_NAMES
}
phosphor_chromaticities = {
    color_name : chromaticity_from_spectrum(
        list(
            (
                datum['Wavelength'],
                datum[color_name]
            )
            for datum in phosphor_spectra
        ),
        standard = '170_2_10_deg'
    )
    for color_name in COLOR_NAMES
}
white_chromaticity = chromaticity_from_spectrum(
    list(
        (
            datum['Wavelength'],
            sum(
                list(
                    datum[color_name]
                    for color_name in COLOR_NAMES
                )
            )
        )
        for datum in phosphor_spectra
    ),
    standard = '170_2_10_deg'
)
print('\nPhosphor Tristimulus Values:')
for function_index, function_name in enumerate(FUNCTION_NAMES):
    print(
        '{0}_R: {1:0.4f}, {0}_G: {2:0.4f}, {0}_B: {3:0.4f}'.format(
            function_name,
            *list(
                phosphor_chromaticities[color_name][0][function_index]
                for color_name in COLOR_NAMES
            )
        )
    )
inverse_transform = inv(
    list(
        list(
            phosphor_chromaticities[color_name][0][function_index]
            for color_name in COLOR_NAMES
        )
        for function_index in range(len(FUNCTION_NAMES))
    )
)
print('\nInverse Transformation Coefficients')
for color_index, color_name in enumerate(COLOR_NAMES):
    print(
        '{0}_X: {1:0.2f}, {0}_Y: {2:0.2f}, {0}_Z: {3:0.2f}'.format(
            color_name[0],
            *inverse_transform[color_index]
        )
    )
# from pprint import pprint; pprint(phosphor_chromaticities); pprint(white_chromaticity)

# endregion

# region Figure 11 - Estimating CRT White Chromaticity

# region Initialize Figure
figure = Figure(
    name = 'Estimating CRT White Chromaticity{0}'.format(
        ' (inverted)' if INVERTED else ''
    ),
    size = SIZE,
    inverted = INVERTED
)
figure.set_fonts(**FONT_SIZES)
x_panel = figure.add_panel(
    name = 'x',
    title = 'Product of CRT White Spectrum and X Function',
    position = (0, 2 / 3, 0.5, 1 / 3),
    x_label = r'Wavelength $\lambda$ (nm)',
    y_label = 'Product'
)
y_panel = figure.add_panel(
    name = 'y',
    title = 'Product of CRT White Spectrum and Y Function',
    position = (0, 1 / 3, 0.5, 1 / 3),
    x_label = r'Wavelength $\lambda$ (nm)',
    y_label = 'Product'
)
z_panel = figure.add_panel(
    name = 'z',
    title = 'Product of CRT White Spectrum and Z Function',
    position = (0, 0 / 3, 0.5, 1 / 3),
    x_label = r'Wavelength $\lambda$ (nm)',
    y_label = 'Product'
)
chromaticity_panel = figure.add_panel(
    name = 'chromaticity',
    title = 'Estimated Chromaticity of CRT Phosphors and White Spectra',
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

# region Plot Products and Chromaticities
for function_index, function_name in enumerate(FUNCTION_NAMES):
    figure.panels[function_name.lower()].fill(
        list(datum['Wavelength'] for datum in products[function_name])
        + [products[function_name][0]['Wavelength']],
        list(datum['Product'] for datum in products[function_name])
        + [products[function_name][0]['Product']],
        color = FILL_COLORS[function_index],
        zorder = 1
    )
    figure.panels[function_name.lower()].plot(
        list(datum['Wavelength'] for datum in products[function_name]),
        list(datum['Product'] for datum in products[function_name]),
        linewidth = 2,
        color = LINE_COLORS[function_index],
        zorder = 2
    )
legend_handles = list()
for color_index, color_name in enumerate(COLOR_NAMES):
    color = 3 * [0]; color[color_index] = 1
    legend_handles.append(
        chromaticity_panel.plot(
            *phosphor_chromaticities[color_name][1],
            linestyle = 'none',
            marker = 'o',
            markersize = 8,
            markeredgecolor = 'none',
            markerfacecolor = color,
            zorder = 2
        )[0]
    )
legend_handles.append(
    chromaticity_panel.plot(
        *white_chromaticity[1],
        linestyle = 'none',
        marker = 'o',
        markersize = 8,
        markerfacecolor = 'none',
        markeredgecolor = figure.grey_level(0.25),
        markeredgewidth = 2,
        zorder = 2
    )[0]
)
chromaticity_panel.legend(
    legend_handles,
    list(
        '{0} Phosphor ({1:0.3f}, {2:0.3f})'.format(
            color_name,
            *color_chromaticity[1]
        )
        for color_name, color_chromaticity in phosphor_chromaticities.items()
    )
    + [
        'White ({0:0.3f}, {1:0.3f})'.format(
            *white_chromaticity[1]
        )
    ],
    loc = 'upper right',
    facecolor = figure.grey_level(1)
)
# endregion

# region Annotation
x_panel.annotate(
    text = '{0}{1:0.4f}'.format(
        r'$X=\int \bar{R}(\lambda)\bar{X}(\lambda)d\lambda\approx$',
        white_chromaticity[0][0]
    ),
    xy = (
        x_panel.get_xlim()[1] - 0.05 * ptp(x_panel.get_xlim()),
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
    text = '{0}{1:0.4f}'.format(
        r'$Y=\int \bar{R}(\lambda)\bar{Y}(\lambda)d\lambda\approx$',
        white_chromaticity[0][1]
    ),
    xy = (
        y_panel.get_xlim()[1] - 0.05 * ptp(y_panel.get_xlim()),
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
    text = '{0}{1:0.4f}'.format(
        r'$Z=\int \bar{R}(\lambda)\bar{Z}(\lambda)d\lambda\approx$',
        white_chromaticity[0][2]
    ),
    xy = (
        z_panel.get_xlim()[1] - 0.05 * ptp(z_panel.get_xlim()),
        z_panel.get_ylim()[1] - 0.1 * ptp(z_panel.get_ylim())
    ),
    xycoords = 'data',
    horizontalalignment = 'right',
    verticalalignment = 'top',
    fontsize = figure.font_sizes['legends'],
    color = figure.grey_level(0),
    zorder = 3
)
# endregion

# region Shading of Chromaticity Diagram
chromaticity_panel.fill( # Fill outside of CRT gamut (upper portion)
    *transpose(
        list(
            phosphor_chromaticities[color_name][1]
            for color_name in COLOR_NAMES
        )
        + [(-0.5, -0.5), (-0.5, 1.5), (1.5, 1.5), (1.5, -0.5)]
        + [phosphor_chromaticities[COLOR_NAMES[0]][1]]
    ),
    color = figure.grey_level(0.9),
    zorder = -2
)
chromaticity_panel.fill( # Fill outside of CRT gamut (lower portion)
    *transpose(
        list(
            phosphor_chromaticities[COLOR_NAMES[color_index]][1]
            for color_index in [0, 2]
        )
        + [(-0.5, -0.5), (1.5, -0.5)]
        + [phosphor_chromaticities[COLOR_NAMES[0]][1]]
    ),
    color = figure.grey_level(0.9),
    zorder = -2
)
chromaticity_panel.fill( # (Un)fill outside of spectrum locus (upper portion)
    *transpose(
        spectrum_locus
        + [(1.5, -0.5), (1.5, 1.5), (-0.5, 1.5), (-0.5, -0.5)]
        + [spectrum_locus[0]]
    ),
    color = figure.grey_level(1),
    zorder = -1
)
chromaticity_panel.fill( # (Un)fill outside of spectrum locus (lower portion)
    *transpose(
        list(
            spectrum_locus[index]
            for index in [0, -1]
        )
        + [(1.5, -0.5), (-0.5, -0.5)]
    ),
    color = figure.grey_level(1),
    zorder = -1
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
