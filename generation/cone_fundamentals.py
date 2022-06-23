"""
Plot Unscaled and Scaled Cone Fundamentals and the Color Matching Experiment
Settings from which they are derived.

Figure Captions:
3 - Mean experiment settings (faded, dashed) transformed into unscaled cone
fundamentals (bold, solid).  Open circles indicate the wave-numbers of the
experimental primary lights.  The nature of the coefficients used for this
transformation cause all three cone fundamentals to pass through a value of 1.0
at the wave-number corresponding to the "blue" primary (22,500 cm^-1) - the
absolute values of the peaks of the three cone fundamentals plotted here are
therefore arbitrary.  The relative shape and the wave-number corresponding to
the peak of each fundamental will be preserved through normalization.
4 - Normalized cone fundamentals conveying the shape of the sensitivity function
of each cone type across wavelengths of visible light.  In addition to all
curves peaking at 1.0, the order and relative shapes of the three curves are
altered as they are now plotted versus wavelength (in nanometers) instead of
wave-number (in centimeters^-1) (see top horizontal axis).  The peak
sensitivities of the three cone types here are approximately 569, 540, and 445
nm for the long-, medium-, and short-wavelength sensitive cones, respectively.
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
    'legends' : 8
}
LEFT_RIGHT_SCALE = 18 # Much less and auto-scale screws up the alignment
EXTENSION = 'svg'
WAVELENGTH_BOUNDS = (385, 720)
# endregion

# region Imports
from csv import DictReader
from figure.figure import Figure
from numpy import arange, ptp
# endregion

# region Constants
COLOR_NAMES = ['Red', 'Green', 'Blue']
CONE_NAMES = ['Long', 'Medium', 'Short']
COLOR_WAVE_NUMBERS = [15500, 19000, 22500]
# endregion

# region Load in Data
with open(
    'data/mean_observer_settings.csv',
    'r'
) as read_file:
    mean_data = list(
        {
            'Wave-Number' : int(row['Wave-Number']),
            **{
                color_name : float(row[color_name])
                for color_name in COLOR_NAMES
            }
        }
        for row in DictReader(read_file)
    )
with open(
    'data/unscaled_cone_fundamentals.csv',
    'r'
) as read_file:
    unscaled_cone_fundamentals = list(
        {
            'Wave-Number' : int(row['Wave-Number']),
            **{
                cone_name : float(row[cone_name])
                for cone_name in CONE_NAMES
            }
        }
        for row in DictReader(read_file)
    )
with open(
    'data/cone_fundamentals.csv',
    'r'
) as read_file:
    cone_fundamentals = list(
        {
            'Wavelength' : int(row['Wavelength']),
            **{
                cone_name : float(row[cone_name])
                for cone_name in CONE_NAMES
            }
        }
        for row in DictReader(read_file)
    )
# endregion

# region Figure 3 - Mean Experimental Settings and Unscaled Cone Fundamentals

# region Initialize Figure
figure = Figure(
    name = 'Unscaled Cone Fundamentals from Experiment Settings{0}'.format(
        ' (inverted)' if INVERTED else ''
    ),
    size = SIZE,
    inverted = INVERTED
)
figure.set_fonts(**FONT_SIZES)
settings_panel = figure.add_panel(
    name = 'settings',
    title = '',
    x_label = r'Wave-Number ($cm^{-1}$)',
    x_lim = (13750, 25750),
    x_ticks = arange(14000, 25001, 1000),
    x_tick_labels = list(
        '{0:,}'.format(tick)
        for tick in arange(14000, 25001, 1000)
    ),
    y_label = 'Setting (Intensity Relative to Test, dashed series)',
    y_lim = (-0.5, 3.5),
    y_ticks = arange(0, 3.1, 0.5)
)
fundamentals_panel = figure.add_panel(
    name = 'fundamentals',
    title = 'Experimental Settings Transformed into (Unscaled) Cone Fundamentals',
    y_label = 'Sensitivity (cone typs not scaled together, solid line series)',
    y_lim = ( # Maintain position of horizontal axis
        LEFT_RIGHT_SCALE
        * (
            settings_panel.get_ylim()[0]
            / ptp(settings_panel.get_ylim())
        ),
        LEFT_RIGHT_SCALE
        * (
            settings_panel.get_ylim()[1]
            / ptp(settings_panel.get_ylim())
        )
    ),
    y_ticks = list(arange(0, 15.1, 5)) + [1]
)
fundamentals_panel.sharex(settings_panel)
fundamentals_panel.yaxis.set_label_position('right')
fundamentals_panel.yaxis.tick_right()
# endregion

# region Reference
fundamentals_panel.axhline(
    y = 0,
    linewidth = 2,
    color = figure.grey_level(0),
    zorder = 0
)
fundamentals_panel.axhline(
    y = 1,
    color = figure.grey_level(0.5),
    zorder = 0
)
settings_panel.axhline(
    y = 1,
    color = figure.grey_level(0.5),
    linestyle = '--',
    zorder = 0
)
fundamentals_panel.plot(
    2 * [COLOR_WAVE_NUMBERS[2]],
    [
        1,
        ptp(fundamentals_panel.get_ylim()) / ptp(settings_panel.get_ylim())
    ], # Approximately lines up
    color = figure.grey_level(0.75),
    linestyle = ':',
    zorder = 0
)
# endregion

# region Plot Settings
legend_handles = list()
for color_index, color_name in enumerate(COLOR_NAMES):
    color = 3 * [0.125 if INVERTED else 0.75]
    color[color_index] = 0.25 if INVERTED else 1
    legend_handles.append(
        settings_panel.plot(
            list(datum['Wave-Number'] for datum in mean_data),
            list(datum[color_name] for datum in mean_data),
            color = color,
            linestyle = '--',
            zorder = 1
        )[0]
    )
    settings_panel.plot(
        COLOR_WAVE_NUMBERS[color_index],
        1,
        linestyle = 'none',
        marker = 'o',
        markersize = 8,
        markerfacecolor = 'none',
        markeredgecolor = color,
        markeredgewidth = 2,
        zorder = 2
    )
settings_panel.legend(
    legend_handles,
    [
        r'Mean Set Intensity of 15,500 $cm^{-1}$ (Red) Light',
        r'Mean Set Intensity of 19,000 $cm^{-1}$ (Green) Light',
        r'Mean Set Intensity of 22,500 $cm^{-1}$ (Blue) Light'
    ],
    loc = 'upper left',
    facecolor = figure.grey_level(1)
)
# endregion

# region Plot Unscaled Fundamentals
legend_handles = list()
for cone_index, cone_name in enumerate(CONE_NAMES):
    color = 3 * [0]; color[cone_index] = 1
    legend_handles.append(
        fundamentals_panel.plot(
            list(datum['Wave-Number'] for datum in unscaled_cone_fundamentals),
            list(datum[cone_name] for datum in unscaled_cone_fundamentals),
            color = color,
            linewidth = 2,
            zorder = 1
        )[0]
    )
fundamentals_panel.legend(
    legend_handles,
    list(
        'Unscaled {0}-Wavelength-Sensitive Cone Fundamental'.format(
            cone_name
        )
        for cone_name in CONE_NAMES
    ),
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

# region Figure 4 - Scaled (Normalized) Cone Fundamentals

# region Initialize Figure
figure = Figure(
    name = 'Normalized Cone Fundamentals{0}'.format(
        ' (inverted)' if INVERTED else ''
    ),
    size = SIZE,
    inverted = INVERTED
)
figure.set_fonts(**FONT_SIZES)
wave_number_panel = figure.add_panel(
    name = 'wave_number',
    title = 'Normalized Cone Fundamentals',
    x_label = r'Wave-Number ($cm^{-1}$)',
    x_lim = WAVELENGTH_BOUNDS,
    x_ticks = list(
        (10.0 ** 7.0) / tick
        for tick in arange(14000, 25001, 1000)
    ),
    x_tick_labels = list(
        '{0:,}'.format(tick)
        for tick in arange(14000, 25001, 1000)
    ),
    y_label = 'Normalized Cone Sensitivity'
)
wavelength_panel = figure.add_panel(
    name = 'wavelength',
    title = '',
    x_label = r'Wavelength $\lambda$ (nm)',
    x_lim = WAVELENGTH_BOUNDS,
    x_ticks = arange(400, 701, 25)
)
wavelength_panel.sharey(wave_number_panel)
wave_number_panel.xaxis.set_label_position('top'),
wave_number_panel.xaxis.tick_top()
# endregion

# region Reference
wavelength_panel.axhline(
    y = 0,
    linewidth = 2,
    color = figure.grey_level(0),
    zorder = 0
)
wavelength_panel.axhline(
    y = 1,
    linewidth = 2,
    color = figure.grey_level(0.5),
    zorder = 0
)
# endregion

# region Plot Fundamentals
legend_handles = list()
for cone_index, cone_name in enumerate(CONE_NAMES):
    color = 3 * [0]; color[cone_index] = 1
    legend_handles.append(
        wavelength_panel.plot(
            list(datum['Wavelength'] for datum in cone_fundamentals),
            list(datum[cone_name] for datum in cone_fundamentals),
            color = color,
            linewidth = 2,
            zorder = 1
        )[0]
    )
wavelength_panel.legend(
    legend_handles,
    list(
        '{0}-Wavelength-Sensitive Cone Fundamental'.format(cone_name)
        for cone_name in CONE_NAMES
    ),
    loc = 'right',
    facecolor = figure.grey_level(1)
)
# endregion

# region Annotate Peak Sensitivities
for cone_name in CONE_NAMES:
    peak_sensitivity = list(
        datum['Wavelength']
        for datum in cone_fundamentals
    )[
        list(
            datum[cone_name]
            for datum in cone_fundamentals
        ).index(1.0)
    ]
    wavelength_panel.annotate(
        text = '{0} nm\n({1} {2})'.format(
            peak_sensitivity,
            int((10.0 ** 7.0) / peak_sensitivity),
            r'$cm^{-1}$'
        ),
        xy = (peak_sensitivity, 1.025),
        xycoords = 'data',
        horizontalalignment = 'center',
        verticalalignment = 'bottom',
        fontsize = figure.font_sizes['legends'],
        color = figure.grey_level(0),
        zorder = 2
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
