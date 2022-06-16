"""
Plot the individual and mean color matching settings from observers in Stiles &
Burch (1959) expeirment.

Tabulated data are taken from the Color & Vision Reserach Laboratory website
(http://www.cvrl.org/)

Figure Caption:
Raw (faded) and mean (bold) settings of red, green, and blue primary light
intensitites relative to test light intensity.  Test light wave-numbers are
indicated by black dots along the bottom - note that the red, green, and blue
primaries (at 15,500, 19,000, and 22,500 cm^-1, respecitvely) are indicated by
open circles.  Lack of variation in individual settings at the primary wave-
numbers indicate that settings were not recorded for these lights (the match is
presumed, however real settings would show some variability due to observer
error).  Negative intensity settings indicate that the primary light was added
to the test side of the bipartite stimulus instead of the match side.  Setting
intensitites drop towards zero at the extermes, indicating that the test lights
at these extremes were perceived to be much dimmer than those towards the middle
of the visible spectrum - note also that sampling is more sparse towards the
extremes.
"""

# Project folder
from sys import path; path.append('../') # To access figure module

# region Settings
INVERTED = False
SIZE = (16, 9)
FONT_SIZES = {
    'titles' : 16,
    'labels' : 14,
    'ticks' : 12,
    'legends' : 8
}
EXTENSION = 'svg'
# endregion

# region Imports
from os import walk, chdir, getcwd
from os.path import dirname
from csv import DictReader
from figure.figure import Figure
from numpy import arange
# endregion

# region Constants
COLOR_NAMES = ['Red', 'Green', 'Blue']
COLOR_WAVE_NUMBERS = [15500, 19000, 22500]
# endregion

# region (Ensure Correct Working Directory)
folders = list()
while True:
    for root, dirs, files in walk('.'):
        folders += list(name for name in dirs)
    if 'cvrl' not in folders:
        chdir(dirname(getcwd())) # Move up one
    else:
        break
# endregion

# region Load in Data
with open(
    'data/individual_observer_settings.csv',
    'r'
) as read_file:
    individual_data = list(
        {
            key : float(value)
            for key, value in row.items()
        }
        for row in DictReader(
            read_file
        )
    )
with open(
    'data/mean_observer_settings.csv',
    'r'
) as read_file:
    mean_data = list(
        {
            key : float(value)
            for key, value in row.items()
        }
        for row in DictReader(
            read_file
        )
    )
mean_maxima = {
    color_name : max(
        list(
            mean_datum[color_name]
            for mean_datum in mean_data
        )
    )
    for color_name in COLOR_NAMES
}
# endregion

# region Initialize Figure
figure = Figure(
    name = 'Color Matching Expeirment Data{0}'.format(
        ' (inverted)' if INVERTED else ''
    ),
    size = SIZE,
    inverted = INVERTED
)
figure.set_fonts(**FONT_SIZES)
background_panel = figure.add_panel(
    name = 'background',
    title = '',
    x_label = r'Wave-Number ($cm^{-1}$)',
    x_lim = (13750, 25750),
    x_ticks = arange(14000, 25001, 1000),
    x_tick_labels = list(
        '{0:,}'.format(tick)
        for tick in arange(14000, 25001, 1000)
    ),
    y_lim = (-1.5, 4),
    y_ticks = [-0.5, 0.5],
    y_tick_labels = ['Test Side', 'Match Side']
)
foreground_panel = figure.add_panel(
    name = 'foreground',
    title = 'Stiles & Burch (1959) Color Matching Experiment',
    y_label = 'Setting (Intensity Relative to Test)',
    y_lim = (-1.5, 4),
    y_ticks = arange(-1, 3.6, 0.5)
)
foreground_panel.sharex(background_panel)
background_panel.yaxis.set_label_position('right')
background_panel.yaxis.tick_right()
# endregion

# region Reference
foreground_panel.axhline(
    y = 0,
    linewidth = 2,
    color = figure.grey_level(0),
    zorder = 0
)
for y in [-1, 1]:
    foreground_panel.axhline(
        y = y,
        color = figure.grey_level(0.75),
        zorder = 0
    )
for x in COLOR_WAVE_NUMBERS:
    foreground_panel.axvline(
        x = x,
        color = figure.grey_level(0.95),
        zorder = 0
    )
# endregion

# region Plot Individual Data
for color_index, color_name in enumerate(COLOR_NAMES):
    relevant_keys = list(
        key
        for key in individual_data[0].keys()
        if color_name in key
    )
    color = 3 * [0 if INVERTED else (0.75 if color_index == 1 else 0.875)]
    color[color_index] = (0.5 if color_index == 2 else 0.25) if INVERTED else 1
    for relevant_key in relevant_keys:
        foreground_panel.plot(
            list(datum['Wave-Number'] for datum in individual_data),
            list(datum[relevant_key] for datum in individual_data),
            linewidth = 0.5,
            color = color,
            zorder = 1
        )
# endregion

# region Plot Mean Data
for wave_number_index in range(len(mean_data)):
    if wave_number_index == 0: continue
    if any(
        mean_data[index]['Wave-Number'] in COLOR_WAVE_NUMBERS
        for index in [wave_number_index - 1, wave_number_index]
    ):
        line_style = ':'
    else:
        line_style = '-'
    for color_index, color_name in enumerate(COLOR_NAMES):
        intensity = 0.5 * (
            max(
                [
                    abs(mean_data[wave_number_index - 1][color_name]),
                    abs(mean_data[wave_number_index][color_name])
                ]
            )
            / mean_maxima[color_name]
        )
        signs = list(
            1 if color_index == index else -1
            for index in range(3)
        )
        series_handle = foreground_panel.plot(
            [mean_data[wave_number_index - 1]['Wave-Number'], mean_data[wave_number_index]['Wave-Number']],
            [mean_data[wave_number_index - 1][color_name], mean_data[wave_number_index][color_name]],
            linewidth = 2,
            linestyle = line_style,
            color = list(
                0.5 + sign * intensity
                for sign in signs
            ),
            zorder = 2
        )
foreground_panel.legend(
    [ # Using dummy series
        foreground_panel.plot(0, 0, color = 'red', linewidth = 2)[0],
        foreground_panel.plot(0, 0, color = 'green', linewidth = 2)[0],
        foreground_panel.plot(0, 0, color = 'blue', linewidth = 2)[0]
    ],
    [
        r'Mean Set Intensity of 15,500 $cm^{-1}$ (Red) Light',
        r'Mean Set Intensity of 19,000 $cm^{-1}$ (Green) Light',
        r'Mean Set Intensity of 22,500 $cm^{-1}$ (Blue) Light'
    ],
    loc = 'upper right',
    facecolor = figure.grey_level(1)
)
# endregion

# region Plot Test Wave-Numbers
sign = +1
for mean_datum in mean_data:
    if mean_datum['Wave-Number'] not in COLOR_WAVE_NUMBERS:
        foreground_panel.plot(
            mean_datum['Wave-Number'],
            -1,
            linestyle = 'none',
            marker = 'o',
            markersize = 8,
            markeredgecolor = 'none',
            markerfacecolor = figure.grey_level(0),
            zorder = 2
        )
    else:
        color = [0] * 3
        for color_index, color_wave_number in enumerate(COLOR_WAVE_NUMBERS):
            if mean_datum['Wave-Number'] == color_wave_number:
                color[color_index] = 1
                foreground_panel.plot(
                    mean_datum['Wave-Number'],
                    -1,
                    linestyle = 'none',
                    marker = 'o',
                    markersize = 8,
                    markerfacecolor = 'none',
                    markeredgecolor = color,
                    markeredgewidth = 2,
                    zorder = 2
                )
    foreground_panel.annotate(
        text = '{0:,}'.format(int(mean_datum['Wave-Number'])),
        xy = (
            mean_datum['Wave-Number'],
            -1 + sign * 0.1
        ),
        xycoords = 'data',
        horizontalalignment = 'center',
        verticalalignment = 'bottom' if sign > 0 else 'top',
        fontsize = figure.font_sizes['legends'],
        zorder = 3
    )
    sign *= -1
# endregion

# region Save Figure
figure.update()
figure.save(
    path = 'images',
    name = figure.name,
    extension = EXTENSION
)
# endregion
