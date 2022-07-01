"""
Individual observer and mean red, green, and blue setting values plotted versus
wave-number in cm^-1 (with top horizontal axis giving wavelength in nm)

Caption: Individual (faded) and average (bold) settings of the red, green, and
blue primary lights relative to the test light intensity plotted across all test
light wave-numbers.  Positive settings indicate primary lights added together on
the "match" side of the stimulus.  Negative settings indicate primary lights
instead added to the "test" side of the stimulus along with the test light.
Where horizontal and vertical dotted lines cross, no settings were recorded
(note there is zero individual variability at these points); instead it was
presumed that each primary would exactly match itself in isolation.  Note that
the step size between test lights is larger below 16,000 cm^-1 and above 21,500
cm^-1.
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
    color_matching_experiment_mean_settings,
    color_matching_experiment_individual_settings
)
from numpy import arange, ceil, floor
from figure.figure import Figure
from maths.conversion_coefficients import COLOR_NAMES
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

# region Constants
COLOR_WAVE_NUMBERS = [15500, 19000, 22500]
# endregion

# region Horizontal Axes Settings (Derived from Data)
minimum_wave_number = min(list(datum['Wave-Number'] for datum in color_matching_experiment_mean_settings))
maximum_wave_number = max(list(datum['Wave-Number'] for datum in color_matching_experiment_mean_settings))
wave_number_ticks = arange(minimum_wave_number, maximum_wave_number + 1, 500)
wave_number_bounds = (minimum_wave_number - 250, maximum_wave_number + 250)
minimum_wavelength = ceil(((10.0 ** 7.0) / maximum_wave_number) / 100.0) * 100.0
maximum_wavelength = floor(((10.0 ** 7.0) / minimum_wave_number) / 100.0) * 100.0
wavelength_ticks = arange(minimum_wavelength, maximum_wavelength + 1, 25)
# endregion

# region Initialize Figure
figure = Figure(
    name = 'figure_01_color_matching_experiment_data{0}'.format(
        '_inverted' if INVERTED else ''
    ),
    size = SIZE,
    inverted = INVERTED
)
back_panel = figure.add_panel(
    name = 'back',
    title = '',
    x_label = r'Wave-Number ($cm^{-1}$)',
    x_lim = wave_number_bounds,
    x_margin = 0.0,
    x_ticks = wave_number_ticks,
    x_tick_labels = list(
        '{0:,}'.format(wave_number_tick)
        if index / 2 == int(index / 2)
        else ''.format(wave_number_tick)
        for index, wave_number_tick in enumerate(wave_number_ticks)
    ),
    y_label = 'Setting\n(relative to test intensity)',
    y_lim = (-0.75, 4.25),
    y_margin = 0.0,
    y_ticks = arange(-0.5, 4.1, 0.5),
    y_tick_labels = list(
        int(y_tick) if int(y_tick) == y_tick else ''
        for y_tick in arange(-0.5, 4.1, 0.5)
    )
)
front_panel = figure.add_panel(
    name = 'front',
    title = '',
    x_label = r'Wavelength ($nm$)',
    x_lim = wave_number_bounds,
    x_margin = 0.0,
    x_ticks = list((10.0 ** 7.0) / x_tick for x_tick in wavelength_ticks),
    x_tick_labels = list(int(wavelength_tick) for wavelength_tick in wavelength_ticks)
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
for color_index, color_wave_number in enumerate(COLOR_WAVE_NUMBERS):
    if not INVERTED:
        line_color = 3 * [0.75]; line_color[color_index] = 1.0
    else:
        line_color = 3 * [0]; line_color[color_index] = 0.25
    back_panel.axvline(
        x = color_wave_number,
        linestyle = ':',
        color = line_color,
        zorder = 1
    )
# endregion

# region Plot Individual Observer Settings
for color_index, color_name in enumerate(COLOR_NAMES):
    if not INVERTED:
        line_color = 3 * [0.9]; line_color[color_index] = 1.0
    else:
        line_color = 3 * [0.0]; line_color[color_index] = 0.15
    for observer_index in range(int(len(color_matching_experiment_individual_settings[0]) / 3.0)):
        back_panel.plot(
            list(
                datum['Wave-Number']
                for datum in color_matching_experiment_individual_settings
            ),
            list(
                datum['{0:02.0f}-{1}'.format(observer_index, color_name)]
                for datum in color_matching_experiment_individual_settings
            ),
            color = line_color,
            zorder = 0
        )
# endregion

# region Plot Mean Observer Settings
legend_handles = list()
for color_index, color_name in enumerate(COLOR_NAMES):
    line_color = 3 * [0.0]; line_color[color_index] = 0.8
    marker_color = 3 * [0.0]; marker_color[color_index] = 1.0
    legend_handles.append(
        back_panel.plot(
            list(
                datum['Wave-Number']
                for datum in color_matching_experiment_mean_settings
            ),
            list(
                datum[color_name]
                for datum in color_matching_experiment_mean_settings
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
        'Mean {0} Setting ({1:,} {2} or {3}{4:0.2f} {5})'.format(
            color_name,
            COLOR_WAVE_NUMBERS[color_index],
            r'$cm^{-1}$',
            r'$\approx$',
            (10.0 ** 7.0) / COLOR_WAVE_NUMBERS[color_index],
            r'$nm$'
        )
        for color_index, color_name in enumerate(COLOR_NAMES)
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
