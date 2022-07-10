"""
(Normalized) cone fundamentals, smoothed by quadratic spline interpoloation to
1nm wavelength steps.

Caption:  Normalized, smoothed cone fundamentals.  The approximate peak of each
cone's sensitivity curve is annotated.
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
from figure.figure import Figure
from numpy import arange
from maths.conversion_coefficients import CONE_NAMES
from maths.plotting_series import cone_fundamentals_10
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

# region Intitialize Figure
figure = Figure(
    name = 'figure_04_cone_fundamentals{0}'.format(
        '_inverted' if INVERTED else ''
    ),
    size = SIZE,
    inverted = INVERTED
)
figure.set_fonts(**FONT_SIZES)
panel = figure.add_panel(
    name = 'main',
    title = '',
    x_label = r'Wavelength $\lambda$ ($nm$)',
    x_lim = (360, 740),
    x_margin = 0.0,
    x_ticks = arange(375, 726, 25),
    y_label = 'Cone Sensitivity\n(normalized proportion)'
)
# endregion

# region Reference Lines
panel.axhline(
    y = 0,
    linewidth = 2,
    color = figure.grey_level(0.25),
    zorder = 0
)
panel.axhline(
    y = 1,
    linestyle = ':',
    color = figure.grey_level(0.75),
    zorder = 0
)
# endregion

# region Plot (Normalized) Cone Fundamentals (CVRL Tabulated Values)
legend_handles = list()
for cone_index, cone_name in enumerate(CONE_NAMES):
    line_color = 3 * [0.0]; line_color[cone_index] = 0.8
    marker_color = 3 * [0.0]; marker_color[cone_index] = 1.0
    legend_handles.append(
        panel.plot(
            list(
                datum['Wavelength']
                for datum in cone_fundamentals_10
            ),
            list(
                datum[cone_name]
                for datum in cone_fundamentals_10
            ),
            color = line_color,
            zorder = 1
        )[0]
    )
# endregion

# region Plot Legend
panel.legend(
    legend_handles,
    list(
        '{0}-Cone Sensitivity {1}'.format(
            cone_name,
            r'$\bar{L}(\lambda)$'
            if cone_name == 'Long'
            else (
                r'$\bar{M}(\lambda)$'
                if cone_name == 'Medium'
                else r'$\bar{S}(\lambda)$'
            )
        )
        for cone_name in CONE_NAMES
    ),
    markerfirst = False,
    loc = 'upper right',
    facecolor = figure.grey_level(1)
)
# endregion

# region Annotations
for cone_index, cone_wavelength in enumerate([569, 541, 445]):
    panel.annotate(
        text = '{0}-Cone Peak\n{1}{2}{3}'.format(
            CONE_NAMES[cone_index],
            r'$\approx$',
            cone_wavelength,
            r'$nm$'
        ),
        xy = (
            cone_wavelength,
            1.01
        ),
        xycoords = 'data',
        horizontalalignment = (
            'left'
            if cone_index == 0
            else (
                'right'
                if cone_index == 1
                else 'center'
            )
        ),
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
