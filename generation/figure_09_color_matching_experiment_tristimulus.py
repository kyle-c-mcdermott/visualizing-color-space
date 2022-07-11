"""
Annotating the tristimulus values of the color matching experiment primaries and
a selected test light on the color matching functions.

Caption: CIE 170-2 10-degree color matching functions with the tristimulus
values of the experiment primaries and the 20,250 cm^-1 test light annotated
along the curves.
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
    TEXT_WIDTH, TEXT_HEIGHT,
    FONT_SIZES,
    WAVELENGTH_LABEL, WAVE_NUMBER_LABEL,
    AXES_GREY_LEVEL
)
from scipy.interpolate import interp1d
from maths.plotting_series import color_matching_functions_170_2_10
from maths.conversion_coefficients import (
    TRISTIMULUS_NAMES,
    COLOR_NAMES,
    EXPERIMENT_PRIMARIES
)
from numpy import arange, floor, ceil
from figure.figure import Figure
# endregion

# region Plot Settings
INVERTED = False
SIZE = (
    TEXT_WIDTH,
    TEXT_HEIGHT / 3
)
EXTENSION = 'pdf'
LINE_COLORS = (
    (0.8, 0, 0.8), # X
    (0.8, 0.5, 0), # Y
    (0, 0, 0.8) # Z
)
TEST_WAVE_NUMBER = 20250
# endregion

# region Determine Tristimulus Values
interpolators = {
    tristimulus_name : interp1d(
        list((10.0 ** 7.0) / datum['Wavelength'] for datum in color_matching_functions_170_2_10),
        list(datum[tristimulus_name] for datum in color_matching_functions_170_2_10),
        kind = 'quadratic'
    )
    for tristimulus_name in TRISTIMULUS_NAMES
}
primary_tristimulus_values = {
    COLOR_NAMES[primary_index] : {
        tristimulus_name : float(tristimulus_interpolator(primary_wave_number))
        for tristimulus_name, tristimulus_interpolator in interpolators.items()
    }
    for primary_index, primary_wave_number in enumerate(EXPERIMENT_PRIMARIES)
}
test_tristimulus_values = {
    tristimulus_name : float(tristimulus_interpolator(TEST_WAVE_NUMBER))
    for tristimulus_name, tristimulus_interpolator in interpolators.items()
}
print('\nPrimary Tristimulus Values:')
for color_name, color_values in primary_tristimulus_values.items():
    for tristimulus_name, tristimulus_value in color_values.items():
        print('{0} {1} = {2:0.3f}'.format(color_name, tristimulus_name, tristimulus_value))
print('\nTest Tristimulus Values:')
for tristimulus_name, tristimulus_value in test_tristimulus_values.items():
    print('{0} = {1:0.3f}'.format(tristimulus_name, tristimulus_value))
# endregion

# region Horizontal Axes Settings (Derived from Data)
wavelength_bounds = (360, 740)
wavelength_ticks = arange(375, 726, 25)
minimum_wave_number = int(ceil(((10.0 ** 7.0) / wavelength_bounds[1]) / 500) * 500)
maximum_wave_number = int(floor(((10.0 ** 7.0) / wavelength_bounds[0]) / 500) * 500)
wave_number_ticks = list(
    (10.0 ** 7.0) / wave_number
    for wave_number in arange(minimum_wave_number, maximum_wave_number + 1, 500)
)
wave_number_tick_labels = list(
    int(wave_number)
    if (
        int(wave_number / 1000) == wave_number / 1000
        and wave_number not in [22000, 24000, 26000]
    )
    else ''
    for wave_number in arange(minimum_wave_number, maximum_wave_number + 1, 500)
)
# endregion

# region Initialize Figure
figure = Figure(
    name = 'figure_09_color_matching_experiment_tristimulus{0}'.format(
        '_inverted' if INVERTED else ''
    ),
    size = SIZE,
    inverted = INVERTED
)
figure.set_fonts(**FONT_SIZES)
back_panel = figure.add_panel(
    name = 'back',
    title = '',
    x_label = WAVELENGTH_LABEL,
    x_lim = wavelength_bounds,
    x_margin = 0.0,
    x_ticks = wavelength_ticks,
    y_label = 'Value'
)
front_panel = figure.add_panel(
    name = 'front',
    title = '',
    x_label = WAVE_NUMBER_LABEL,
    x_lim = wavelength_bounds,
    x_ticks = wave_number_ticks,
    x_tick_labels = wave_number_tick_labels
)
front_panel.sharey(back_panel)
front_panel.xaxis.set_label_position('top')
front_panel.xaxis.tick_top()
# endregion

# region Reference Lines
back_panel.axhline(
    y = 0,
    linewidth = 2,
    color = figure.grey_level(AXES_GREY_LEVEL),
    zorder = 1
)
for primary_index, primary_wave_number in enumerate(EXPERIMENT_PRIMARIES):
    if not INVERTED:
        line_color = 3 * [0.75]; line_color[primary_index] = 1.0
    else:
        line_color = 3 * [0]; line_color[primary_index] = 0.25
    back_panel.axvline(
        x = (10.0 ** 7.0) / primary_wave_number,
        linestyle = ':',
        color = line_color,
        zorder = 0
    )
back_panel.axvline(
    x = (10.0 ** 7.0) / TEST_WAVE_NUMBER,
    linestyle = ':',
    color = figure.grey_level(0.75),
    zorder = 0
)
# endregion

# region Plot Color Matching Functions
legend_handles = list()
for tristimulus_index, tristimulus_name in enumerate(TRISTIMULUS_NAMES):
    legend_handles.append(
        back_panel.plot(
            list(
                datum['Wavelength']
                for datum in color_matching_functions_170_2_10
            ),
            list(
                datum[tristimulus_name]
                for datum in color_matching_functions_170_2_10
            ),
            color = LINE_COLORS[tristimulus_index],
            zorder = 2
        )[0]
    )
# endregion

# region Plot Legend
back_panel.legend(
    legend_handles,
    [
        r'$\bar{X}(\lambda)$',
        r'$\bar{Y}(\lambda)$',
        r'$\bar{Z}(\lambda)$'
    ],
    markerfirst = False,
    loc = 'upper right',
    facecolor = figure.grey_level(1)
)
# endregion

# region Plot and Annotate Tristimulus Values
annotation_text = {
    'Red' : {
        'X' : (r'$X_R$', +1, 'left'),
        'Y' : (r'$Y_R$', +1, 'left'),
        'Z' : (r'$Z_R$', -1, 'right')
    },
    'Green' : {
        'X' : (r'$X_G$', -1, 'right'),
        'Y' : (r'$Y_G$', -1, 'right'),
        'Z' : (r'$Z_G$', +1, 'left')
    },
    'Blue' : {
        'X' : (r'$X_B$', +1, 'left'),
        'Y' : (r'$Y_B$', -1, 'right'),
        'Z' : (r'$Z_B$', -1, 'right')
    }
}
for color_index, color_name in enumerate(COLOR_NAMES):
    marker_color = 3 * [0]; marker_color[color_index] = 0.8
    for tristimulus_name in TRISTIMULUS_NAMES:
        back_panel.plot(
            (10.0 ** 7.0) / EXPERIMENT_PRIMARIES[color_index],
            primary_tristimulus_values[color_name][tristimulus_name],
            linestyle = 'none',
            marker = 'o',
            markersize = 4,
            markeredgecolor = 'none',
            markerfacecolor = marker_color,
            zorder = 3
        )
        back_panel.annotate(
            text = annotation_text[color_name][tristimulus_name][0],
            xy = (
                (10.0 ** 7.0) / EXPERIMENT_PRIMARIES[color_index]
                + 2 * annotation_text[color_name][tristimulus_name][1],
                primary_tristimulus_values[color_name][tristimulus_name]
                + 0.01
            ),
            xycoords = 'data',
            horizontalalignment = annotation_text[color_name][tristimulus_name][2],
            verticalalignment = 'bottom',
            fontsize = figure.font_sizes['legends'],
            color = figure.grey_level(0),
            zorder = 4
        )
annotation_text = {
    'X' : (r'$X_{20,250cm^{-1}}$', -1, 'right'),
    'Y' : (r'$Y_{20,250cm^{-1}}$', -1, 'right'),
    'Z' : (r'$Z_{20,250cm^{-1}}$', +1, 'left')
}
for tristimulus_name in TRISTIMULUS_NAMES:
    back_panel.plot(
        (10.0 ** 7.0) / TEST_WAVE_NUMBER,
        test_tristimulus_values[tristimulus_name],
        linestyle = 'none',
        marker = 'o',
        markersize = 4,
        markeredgecolor = 'none',
        markerfacecolor = figure.grey_level(0),
        zorder = 3
    )
    back_panel.annotate(
        text = annotation_text[tristimulus_name][0],
        xy = (
            (10.0 ** 7.0) / TEST_WAVE_NUMBER
            + 2 * annotation_text[tristimulus_name][1],
            test_tristimulus_values[tristimulus_name]
            + 0.01
        ),
        xycoords = 'data',
        horizontalalignment = annotation_text[tristimulus_name][2],
        verticalalignment = 'bottom',
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
