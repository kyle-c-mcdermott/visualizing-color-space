"""
Plotting Spectrum Loci for CIE 170-2 10-degree, CIE 170-2 2-degree, CIE 1964
10-degree, and CIE 1931 2-degree standards

Figure Caption:
8 - Spectrum Loci are plotted for the CIE 170-2 10-degree, CIE 170-2 2-degree,
CIE 1964 10-degree, and CIE 1931 2-degree standards.  Variations among these
standard chromaticity spaces should be compared to the individual observer
variability illustrated in Figure 2.  The chromaticities of standard illuminant
D65 are plotted for all but the CIE 170-2 2-degree standard.
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
SIZE = (9, 9)
FONT_SIZES = {
    'titles' : 16,
    'labels' : 14,
    'ticks' : 12,
    'legends' : 12
}
EXTENSION = 'svg'
# endregion

# region Imports
from csv import DictReader
from figure.figure import Figure
from numpy import linspace, transpose
# endregion

# region Constants
D65_CHROMATICITIES = {
    '170_2_10' : (0.3138, 0.3313), # estimating_d65_chromaticity.py
    '1964_10' : (0.31382, 0.33100), # Wikipedia
    '1931_2' : (0.31271, 0.32902) # Wikipedia
}
# endregion

# region Load in Data
"""
Tabulated spectrum locus coordinates for CIE 170-2 10-degree donloaded from:
http://www.cvrl.org/ciexyzpr.htm
Under 10-deg coordinates from 10-deg XYZ CMFs
using 1 nm Stepsize and csv Format
"""
with open(
    'cvrl/cc2012xyz10_1_5dp.csv',
    'r'
) as read_file:
    spectrum_locus_170_10_degree = list(
        {
            'Wavelength' : int(row['Wavelength']),
            'x' : float(row['x']),
            'y' : float(row['y'])
        }
        for row in DictReader(
            read_file,
            fieldnames = ['Wavelength', 'x', 'y', 'z'] # z is superfluous
        )
    )

"""
Tabulated spectrum locus coordinates for CIE 170-2 2-degree donloaded from:
http://www.cvrl.org/ciexyzpr.htm
Under 2-deg coordinates from 2-deg XYZ CMFs
using 1 nm Stepsize and csv Format
"""
with open(
    'cvrl/cc2012xyz2_1_5dp.csv',
    'r'
) as read_file:
    spectrum_locus_170_2_degree = list(
        {
            'Wavelength' : int(row['Wavelength']),
            'x' : float(row['x']),
            'y' : float(row['y'])
        }
        for row in DictReader(
            read_file,
            fieldnames = ['Wavelength', 'x', 'y', 'z'] # z is superfluous
        )
    )

"""
Tabulated spectrum locus coordinates for CIE 1964 10-degree downloaded from:
http://www.cvrl.org/cie.htm
Under Chromaticity Coordinates, CIE 1964 10-deg chromaticity xyz coordinates
using the second button "/W" with a solid (instead of dashed) line indicating
higher sampling resolution (1 nm)
"""
with open(
    'cvrl/cccie64_1.csv',
    'r'
) as read_file:
    spectrum_locus_1964_10_degree = list(
        {
            'Wavelength' : int(row['Wavelength']),
            'x' : float(row['x']),
            'y' : float(row['y'])
        }
        for row in DictReader(
            read_file,
            fieldnames = ['Wavelength', 'x', 'y', 'z'] # z is superfluous
        )
    )

"""
Tabulated spectrum locus coordinates for CIE 1931 2-degree downloaded from:
http://www.cvrl.org/cie.htm
Under Chromaticity Coordinates, CIE 1931 2-deg xyz chromaticity coordinates
using the second button "/W" with a solid (instead of dashed) line indicating
higher sampling resolution (1 nm)
"""
with open(
    'cvrl/cccie31_1.csv',
    'r'
) as read_file:
    spectrum_locus_1931_2_degree = list(
        {
            'Wavelength' : int(row['Wavelength']),
            'x' : float(row['x']),
            'y' : float(row['y'])
        }
        for row in DictReader(
            read_file,
            fieldnames = ['Wavelength', 'x', 'y', 'z'] # z is superfluous
        )
    )
# endregion

# region Figure 8 - Comparing Chromaticity Diagrams

# region Initialize Figure
figure = Figure(
    name = 'Comparison of CIE Standard Chromaticity Spaces{0}'.format(
        ' (inverted)' if INVERTED else ''
    ),
    size = SIZE,
    inverted = INVERTED
)
figure.set_fonts(**FONT_SIZES)
panel = figure.add_panel(
    name = 'main',
    title = 'Comparison of CIE Standard Chromaticity Spaces',
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
# endregion

# region Plot Spectrum Loci
legend_handles = list()
for (spectrum_locus, line_style, color, z_order) in [
    (spectrum_locus_170_10_degree, '-', (0, 0, 1), 4),
    (spectrum_locus_170_2_degree, '--', (0, 0, 0.75), 3),
    (spectrum_locus_1964_10_degree, ':', (0, 0.5, 0), 2),
    (spectrum_locus_1931_2_degree, '-.', (0.75, 0, 0), 1)
]:
    legend_handles.append(
        panel.plot(
            *transpose(
                list(
                    (
                        spectrum_locus[index]['x'],
                        spectrum_locus[index]['y']
                    )
                    for index in list(range(len(spectrum_locus))) + [0]
                )
            ),
            linestyle = line_style,
            color = color,
            zorder = z_order
        )[0]
    )
# endregion

# region Plot D65 for Select Standards
legend_handles.append(
    panel.plot(
        *D65_CHROMATICITIES['170_2_10'],
        linestyle = 'none',
        marker = 'o',
        markersize = 8,
        markeredgecolor = (0, 0, 1),
        markerfacecolor = 'none',
        zorder = 4
    )[0]
)
legend_handles.append(
    panel.plot(
        *D65_CHROMATICITIES['1964_10'],
        linestyle = 'none',
        marker = 'o',
        markersize = 12,
        markeredgecolor = (0, 0.5, 0),
        markerfacecolor = 'none',
        zorder = 2
    )[0]
)
legend_handles.append(
    panel.plot(
        *D65_CHROMATICITIES['1931_2'],
        linestyle = 'none',
        marker = 'o',
        markersize = 16,
        markeredgecolor = (0.75, 0, 0),
        markerfacecolor = 'none',
        zorder = 1
    )[0]
)
# endregion

# region Legend
panel.legend(
    legend_handles,
    [
        r'CIE 170-2 10$\degree$ Spectrum Locus',
        r'CIE 170-2 2$\degree$ Spectrum Locus',
        r'CIE 1964 10$\degree$ Spectrum Locus',
        r'CIE 1931 2$\degree$ Spectrum Locus',
        r'D65 Chromaticity in CIE 170-2 10$\degree$',
        r'D65 Chromaticity in CIE 1964 10$\degree$',
        r'D65 Chromaticity in CIE 1931 2$\degree$'
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
figure.close()
# endregion

# endregion
