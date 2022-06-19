"""
Figure illustrating the determination of trivalues for color matching experiment
primaries and an example test light and the resulting mixture for either side of
the experiment stimulus - converting summed trivalues into plotted
chromaticities.

Figure Caption:
9 - The left panel plots the three color matching functions and annotations show
the X, Y, and Z values for each of the three experimental primaries and the
selected test light at 20,250 cm^-1.  These values represent each light at an
intensity of 1.0 using the experiment's relative scale.  The test light is taken
as having an intensity of 1.0, while the primary intensities are the absolute
value of their mean setting value (with negative values being on the test side
instead of the match side).  The right panel plots the chromaticities of the
primaries and the selected test light along with the chromaticity of the
stimulus resulting from the mix of green and blue (on the match side) and red
and the test light (on the test side).  The mixed chromaticity necessarily falls
on a straight line between the two lights being mixed on either side of the
bipartite stimulus.
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
TEST_LIGHT_INDEX = 11 # 20,250 cm^-1 (~494 nm) - large negative Red setting
COLORS = (
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
EXTENSION = 'svg'
# endregion

# region Imports
from csv import DictReader
from figure.figure import Figure
from scipy.interpolate import interp1d
from numpy import arange, linspace, transpose, ptp
# endregion

# region Constants
FUNCTION_NAMES = ['X', 'Y', 'Z']
COLOR_NAMES = ['Red', 'Green', 'Blue']
# endregion

# region Load in Data
with open(
    'data/color_matching_functions.csv',
    'r'
) as read_file:
    color_matching_functions = list(
        {
            'Wavelength' : int(row['Wavelength']),
            **{
                function_name : float(row[function_name])
                for function_name in FUNCTION_NAMES
            }
        }
        for row in DictReader(read_file)
    )
spectrum_locus = list(
    (
        datum['X'] / (datum['X'] + datum['Y'] + datum['Z']),
        datum['Y'] / (datum['X'] + datum['Y'] + datum['Z'])
    )
    for datum in color_matching_functions
)
with open(
    'data/mean_observer_settings.csv',
    'r'
) as read_file:
    mean_data = list(
        {
            'Wave-Number' : int(row['Wave-Number']),
            'Wavelength' : (10.0 ** 7.0) / float(row['Wave-Number']),
            'Red' : float(row['Red']),
            'Green' : float(row['Green']),
            'Blue' : float(row['Blue'])
        }
        for row in DictReader(read_file)
    )
primary_wavelengths = {
    color_name : list(
        datum['Wavelength']
        for datum in mean_data
        if datum[color_name] == 1.0 and all(
            datum[other_name] == 0.0
            for other_name in COLOR_NAMES
            if other_name != color_name
        )
    )[0]
    for color_name in COLOR_NAMES
}
test_wavelengths = list(
    datum['Wavelength']
    for datum in mean_data
    if (
        datum['Wavelength'] not in primary_wavelengths.values()
        and (
            color_matching_functions[0]['Wavelength']
            <= datum['Wavelength']
            <= color_matching_functions[-1]['Wavelength']
        )
    )
)
test_mean_setting = list(
    {
        color_name : datum[color_name]
        for color_name in COLOR_NAMES
    }
    for datum in mean_data
    if datum['Wavelength'] == test_wavelengths[TEST_LIGHT_INDEX]
)[0]
# endregion

# region Interpoloate Trivalues for Experiment Lights
cmf_interpolators = {
    function_name : interp1d(
        list(datum['Wavelength'] for datum in color_matching_functions),
        list(datum[function_name] for datum in color_matching_functions),
        kind = 'quadratic'
    )
    for function_name in FUNCTION_NAMES
}
primary_trivalues = {
    primary_name : {
        interpolator_name : float(interpolator(primary_wavelength))
        for interpolator_name, interpolator in cmf_interpolators.items()
    }
    for primary_name, primary_wavelength in primary_wavelengths.items()
}
test_trivalues = list(
    {
        interpolator_name : float(interpolator(test_wavelength))
        for interpolator_name, interpolator in cmf_interpolators.items()
    }
    for test_wavelength in test_wavelengths
)
# endregion

# region Color Mixing
summed_trivalues = list() # Match side / positive settings
for function_name in FUNCTION_NAMES:
    summed_trivalues.append(
        sum(
            list(
                test_mean_setting[primary_name]
                * primary_trivalue[function_name]
                for primary_name, primary_trivalue in primary_trivalues.items()
                if test_mean_setting[primary_name] >= 0.0 # on match side
            )
        )
    )
match_chromaticity = (
    summed_trivalues[0] / sum(summed_trivalues),
    summed_trivalues[1] / sum(summed_trivalues)
)
# endregion

# region Figure 9 - Color Mixing: Experiment Chromaticities

# region Initialize Figure
figure = Figure(
    name = 'Color Mixing - Experiment Chromaticities{0}'.format(
        ' (inverted)' if INVERTED else ''
    ),
    size = SIZE,
    inverted = INVERTED
)
figure.set_fonts(**FONT_SIZES)
cmf_panel = figure.add_panel(
    name = 'cmf',
    title = 'Experiment Light Trivalues from Color Matching Functions',
    position = (0, 0, 0.5, 1),
    x_label = r'Wavelength $\lambda$ (nm)',
    x_lim = (380, 730),
    x_ticks = arange(400, 701, 25),
    y_label = 'Value',
    y_lim = (-0.125, 2.25)
)
chromaticity_panel = figure.add_panel(
    name = 'chromaticity',
    title = 'Experiment Lights Chromaticities',
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
    linestyle = ':',
    color = figure.grey_level(0.25),
    zorder = 1
)
# endregion

# region Plot Color Matching Functions
legend_handles = list()
for function_index, function_name in enumerate(FUNCTION_NAMES):
    legend_handles.append(
        cmf_panel.plot(
            list(datum['Wavelength'] for datum in color_matching_functions),
            list(datum[function_name] for datum in color_matching_functions),
            color = COLORS[function_index],
            zorder = 2
        )[0]
    )
# endregion

# region Plot Lights (Dirac Delta) Spectra
for (color_name, color) in [
    ('Red', (1, 0, 0)),
    ('Green', (0, 1, 0)),
    ('Blue', (0, 0, 1))
]:
    legend_handles.append( # Dummy series for legend
        cmf_panel.plot(
            [0, 0],
            [1, 1],
            color = color,
            marker = 'o',
            markersize = 8,
            markeredgecolor = 'none',
            markerfacecolor = color
        )[0]
    )
    max_value = 0.0
    for function_name in FUNCTION_NAMES:
        cmf_panel.plot(
            primary_wavelengths[color_name],
            primary_trivalues[color_name][function_name],
            linestyle = 'none',
            marker = 'o',
            markersize = 8,
            markeredgecolor = 'none',
            markerfacecolor = color,
            zorder = 3
        )
        cmf_panel.annotate(
            text = '{0}{1}{2:0.3f}'.format(
                function_name,
                r'$\approx$',
                primary_trivalues[color_name][function_name]
            ),
            xy = (
                primary_wavelengths[color_name] + (-1 if color_name == 'Blue' else 1) * 4,
                primary_trivalues[color_name][function_name] + 0.0125
            ),
            xycoords = 'data',
            horizontalalignment = 'right' if color_name == 'Blue' else 'left',
            verticalalignment = 'bottom',
            fontsize = figure.font_sizes['legends'],
            color = figure.grey_level(0),
            zorder = 4
        )
        if max_value < primary_trivalues[color_name][function_name]:
            max_value = primary_trivalues[color_name][function_name]
    cmf_panel.plot(
        2 * [primary_wavelengths[color_name]],
        [0.0, max_value],
        color = color,
        zorder = 1
    )
legend_handles.append( # Dummy series for legend
    cmf_panel.plot(
        [0, 0],
        [1, 1],
        color = figure.grey_level(0.25),
        marker = 'o',
        markersize = 8,
        markeredgecolor = 'none',
        markerfacecolor = figure.grey_level(0.25)
    )[0]
)
for function_name in FUNCTION_NAMES:
    cmf_panel.plot(
        test_wavelengths[TEST_LIGHT_INDEX],
        test_trivalues[TEST_LIGHT_INDEX][function_name],
        linestyle = 'none',
        marker = 'o',
        markersize = 8,
        markeredgecolor = 'none',
        markerfacecolor = figure.grey_level(0.25),
        zorder = 3
    )
    cmf_panel.annotate(
        text = '{0}{1}{2:0.3f}'.format(
            function_name,
            r'$\approx$',
            test_trivalues[TEST_LIGHT_INDEX][function_name]
        ),
        xy = (
            test_wavelengths[TEST_LIGHT_INDEX] - 4,
            test_trivalues[TEST_LIGHT_INDEX][function_name] + 0.0125
        ),
        xycoords = 'data',
        horizontalalignment = 'right',
        verticalalignment = 'bottom',
        fontsize = figure.font_sizes['legends'],
        color = figure.grey_level(0),
        zorder = 4
    )
cmf_panel.plot(
    2 * [test_wavelengths[TEST_LIGHT_INDEX]],
    [0.0, max(test_trivalues[TEST_LIGHT_INDEX].values())],
    color = figure.grey_level(0.25),
    zorder = 1
)
# endregion

# region Color Matching Functions Legend
cmf_panel.legend(
    legend_handles,
    list(
        'Color Matching Function {0}'.format(function_name)
        for function_name in FUNCTION_NAMES
    ) + list(
        '{0} Primary Trivalues\n{1:0.1f} nm ({2:,} {3})'.format(
            color_name,
            primary_wavelengths[color_name],
            int((10.0 ** 7.0) / primary_wavelengths[color_name]),
            r'$cm^{-1}$'
        )
        for color_name in COLOR_NAMES
    ) + [
        'Test Light Trivalues\n{0:0.1f} nm ({1:,} {2})'.format(
            test_wavelengths[TEST_LIGHT_INDEX],
            int((10.0 ** 7.0) / test_wavelengths[TEST_LIGHT_INDEX]),
            r'$cm^{-1}$'
        )
    ],
    loc = 'upper right',
    facecolor = figure.grey_level(1)
)
# endregion

# region Plot Lights Chromaticities
legend_handles = list()
for (color_name, color) in [
    ('Red', (1, 0, 0)),
    ('Green', (0, 1, 0)),
    ('Blue', (0, 0, 1))
]:
    legend_handles.append(
        chromaticity_panel.plot(
            primary_trivalues[color_name]['X'] / sum(primary_trivalues[color_name].values()),
            primary_trivalues[color_name]['Y'] / sum(primary_trivalues[color_name].values()),
            linestyle = 'none',
            marker = 'o',
            markersize = 8,
            markeredgecolor = 'none',
            markerfacecolor = color,
            zorder = 2
        )[0]
    )
    chromaticity_panel.plot(
        [
            match_chromaticity[0],
            primary_trivalues[color_name]['X'] / sum(primary_trivalues[color_name].values())
        ],
        [
            match_chromaticity[1],
            primary_trivalues[color_name]['Y'] / sum(primary_trivalues[color_name].values())
        ],
        linewidth = 0.5,
        color = color,
        zorder = 2
    )
for test_index, test_trival in enumerate(test_trivalues):
    if test_index == TEST_LIGHT_INDEX: continue
    chromaticity_panel.plot(
        test_trival['X'] / sum(test_trival.values()),
        test_trival['Y'] / sum(test_trival.values()),
        linestyle = 'none',
        marker = 'o',
        markersize = 4,
        markeredgecolor = 'none',
        markerfacecolor = figure.grey_level(0.5),
        zorder = 2
    )
legend_handles.append(
    chromaticity_panel.plot(
        test_trivalues[TEST_LIGHT_INDEX]['X'] / sum(test_trivalues[TEST_LIGHT_INDEX].values()),
        test_trivalues[TEST_LIGHT_INDEX]['Y'] / sum(test_trivalues[TEST_LIGHT_INDEX].values()),
        linestyle = 'none',
        marker = 'o',
        markersize = 8,
        markeredgecolor = 'none',
        markerfacecolor = figure.grey_level(0.25),
        zorder = 2
    )[0]
)
chromaticity_panel.plot(
    [
        match_chromaticity[0],
        test_trivalues[TEST_LIGHT_INDEX]['X'] / sum(test_trivalues[TEST_LIGHT_INDEX].values())
    ],
    [
        match_chromaticity[1],
        test_trivalues[TEST_LIGHT_INDEX]['Y'] / sum(test_trivalues[TEST_LIGHT_INDEX].values())
    ],
    linewidth = 0.5,
    color = figure.grey_level(0.25),
    zorder = 2
)
legend_handles.append(
    chromaticity_panel.plot(
        *match_chromaticity,
        linestyle = 'none',
        marker = 'o',
        markersize = 8,
        markerfacecolor = 'none',
        markeredgecolor = figure.grey_level(0),
        markeredgewidth = 2,
        zorder = 3
    )[0]
)
chromaticity_panel.legend(
    legend_handles,
    list(
        '{0} ({1:0.3f}, {2:0.3f})'.format(
            color_name,
            color_trivalues['X'] / sum(color_trivalues.values()),
            color_trivalues['Y'] / sum(color_trivalues.values())
        )
        for color_name, color_trivalues in primary_trivalues.items()
    ) + [
        'Test ({0:0.3f}, {1:0.3f})'.format(
            test_trivalues[TEST_LIGHT_INDEX]['X'] / sum(test_trivalues[TEST_LIGHT_INDEX].values()),
            test_trivalues[TEST_LIGHT_INDEX]['Y'] / sum(test_trivalues[TEST_LIGHT_INDEX].values())
        ),
        'Match ({0:0.3f}, {1:0.3f})'.format(*match_chromaticity)
    ],
    loc = 'upper right',
    facecolor = figure.grey_level(1)
)
# endregion

# region Annotations
chromaticity_panel.annotate(
    text = '{0:0.1f} nm\n{1} Side'.format(
        primary_wavelengths['Red'],
        'Match' if test_mean_setting['Red'] >= 0.0 else 'Test'
    ),
    xy = (
        primary_trivalues['Red']['X'] / sum(primary_trivalues['Red'].values()) + 0.002,
        primary_trivalues['Red']['Y'] / sum(primary_trivalues['Red'].values()) + 0.002
    ),
    xycoords = 'data',
    horizontalalignment = 'left',
    verticalalignment = 'bottom',
    fontsize = figure.font_sizes['legends'],
    color = figure.grey_level(0),
    zorder = 5
)
chromaticity_panel.annotate(
    text = '{0:0.1f} nm\n{1} Side'.format(
        primary_wavelengths['Green'],
        'Match' if test_mean_setting['Green'] >= 0.0 else 'Test'
    ),
    xy = (
        primary_trivalues['Green']['X'] / sum(primary_trivalues['Green'].values()) + 0.02,
        primary_trivalues['Green']['Y'] / sum(primary_trivalues['Green'].values()) + 0.002
    ),
    xycoords = 'data',
    horizontalalignment = 'left',
    verticalalignment = 'bottom',
    fontsize = figure.font_sizes['legends'],
    color = figure.grey_level(0),
    zorder = 5
)
chromaticity_panel.annotate(
    text = '{0:0.1f} nm\n{1} Side'.format(
        primary_wavelengths['Blue'],
        'Match' if test_mean_setting['Blue'] >= 0.0 else 'Test'
    ),
    xy = (
        primary_trivalues['Blue']['X'] / sum(primary_trivalues['Blue'].values()) - 0.01,
        primary_trivalues['Blue']['Y'] / sum(primary_trivalues['Blue'].values()) + 0.015
    ),
    xycoords = 'data',
    horizontalalignment = 'right',
    verticalalignment = 'top',
    fontsize = figure.font_sizes['legends'],
    color = figure.grey_level(0),
    zorder = 5
)
chromaticity_panel.annotate(
    text = '{0:0.1f} nm'.format(test_wavelengths[TEST_LIGHT_INDEX]),
    xy = (
        test_trivalues[TEST_LIGHT_INDEX]['X'] / sum(test_trivalues[TEST_LIGHT_INDEX].values()) + 0.002,
        test_trivalues[TEST_LIGHT_INDEX]['Y'] / sum(test_trivalues[TEST_LIGHT_INDEX].values()) + 0.002
    ),
    xycoords = 'data',
    horizontalalignment = 'left',
    verticalalignment = 'bottom',
    fontsize = figure.font_sizes['legends'],
    color = figure.grey_level(0),
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
# endregion

# endregion
