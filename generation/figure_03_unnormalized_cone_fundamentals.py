"""
Unnormalized cone fundamentals transformed from the color matching experiment
mean settings.

Caption: Unnormalized cone fundamentals transformed from color matching
experiment mean settings using equation X.  Dashed vertical lines indicate the
wavelengths of the experimental primary lights; note that all three fundamentals
pass through $1.0$ at the wavelength corresponding to the experimental blue
primary.
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
from maths.plotting_series import color_matching_experiment_mean_settings
from maths.color_conversion import rgb_to_lms
from maths.conversion_coefficients import (
    COLOR_NAMES,
    CONE_NAMES,
    EXPERIMENT_PRIMARIES
)
from numpy import arange, ceil, floor
from figure.figure import Figure
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

# region Transform Mean Settings into Unnormalized Cone Fundamentals
unnormalized_cone_fundamentals = list()
for datum in color_matching_experiment_mean_settings:
    cone_fundamentals = rgb_to_lms(
        *list(
            datum[color_name]
            for color_name in COLOR_NAMES
        ),
        normalize_fundamentals = False
    )
    unnormalized_cone_fundamentals.append(
        {
            'Wavelength' : datum['Wavelength'],
            **{
                cone_name : cone_fundamentals[cone_index]
                for cone_index, cone_name in enumerate(CONE_NAMES)
            }
        }
    )
# endregion

# region Horizontal Axes Settings (Derived from Data)
minimum_wave_number = min(list(datum['Wave-Number'] for datum in color_matching_experiment_mean_settings))
maximum_wave_number = max(list(datum['Wave-Number'] for datum in color_matching_experiment_mean_settings))
wave_number_ticks = arange(minimum_wave_number, maximum_wave_number + 1, 500)
minimum_wavelength = ceil(((10.0 ** 7.0) / maximum_wave_number) / 100.0) * 100.0
maximum_wavelength = floor(((10.0 ** 7.0) / minimum_wave_number) / 100.0) * 100.0
wavelength_ticks = arange(minimum_wavelength, maximum_wavelength + 1, 25)
wavelength_bounds = (
    (10.0 ** 7.0) / (maximum_wave_number + 250),
    (10.0 ** 7.0) / (minimum_wave_number - 250)
)
# endregion

# region Initialize Figure
figure = Figure(
    name = 'figure_03_unnormalized_cone_fundamentals{0}'.format(
        '_inverted' if INVERTED else ''
    ),
    size = SIZE,
    inverted = INVERTED
)
figure.set_fonts(**FONT_SIZES)
back_panel = figure.add_panel(
    name = 'back',
    title = '',
    x_label = r'Wavelength $\lambda$ ($nm$)',
    x_lim = wavelength_bounds,
    x_margin = 0.0,
    x_ticks = wavelength_ticks,
    y_label = 'Unnormalized Cone Sensitivity'
)
front_panel = figure.add_panel(
    name = 'front',
    title = '',
    x_label = r'Wave-Number ($cm^{-1}$)',
    x_lim = wavelength_bounds,
    x_margin = 0.0,
    x_ticks = list((10.0 ** 7.0) / x_tick for x_tick in wave_number_ticks),
    x_tick_labels = list(
        '{0:,}'.format(wave_number_tick)
        if index / 2 == int(index / 2) and wave_number_tick != 24000
        else ''
        for index, wave_number_tick in enumerate(wave_number_ticks)
    )
)
front_panel.sharey(back_panel)
front_panel.xaxis.set_label_position('top')
front_panel.xaxis.tick_top()
# endregion

# region Reference Lines
back_panel.axhline(
    y = 0,
    linewidth = 2,
    color = figure.grey_level(0.25),
    zorder = 1
)
back_panel.axhline(
    y = 1,
    linestyle = ':',
    color = figure.grey_level(0.75),
    zorder = 1
)
for color_index, color_wave_number in enumerate(EXPERIMENT_PRIMARIES):
    if not INVERTED:
        line_color = 3 * [0.75]; line_color[color_index] = 1.0
    else:
        line_color = 3 * [0]; line_color[color_index] = 0.25
    back_panel.axvline(
        x = (10.0 ** 7.0) / color_wave_number,
        linestyle = ':',
        color = line_color,
        zorder = 0
    )
# endregion

# region Plot Unnormalized Cone Fundamentals
legend_handles = list()
for cone_index, cone_name in enumerate(CONE_NAMES):
    line_color = 3 * [0.0]; line_color[cone_index] = 0.8
    marker_color = 3 * [0.0]; marker_color[cone_index] = 1.0
    legend_handles.append(
        back_panel.plot(
            list(
                datum['Wavelength']
                for datum in unnormalized_cone_fundamentals
            ),
            list(
                datum[cone_name]
                for datum in unnormalized_cone_fundamentals
            ),
            color = line_color,
            marker = 'o',
            markersize = 4,
            markeredgecolor = 'none',
            markerfacecolor = marker_color,
            zorder = 2
        )[0]
    )
# endregion

# region Plot Legend
back_panel.legend(
    legend_handles,
    list(
        'Unnormalized {0}-Cone Sensitivity {1}'.format(
            cone_name,
            r'$k_L\bar{L}(\lambda)$'
            if cone_name == 'Long'
            else (
                r'$k_M\bar{M}(\lambda)$'
                if cone_name == 'Medium'
                else r'$k_S\bar{S}(\lambda)$'
            )
        )
        for cone_name in CONE_NAMES
    ),
    markerfirst = False,
    loc = 'upper left',
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
