"""
Plotting color matching experiment primaries and selected test light
chromaticities along with match/test chromaticity at the intersection of lines
joining lights from the match and test sides of the stimulus.

Caption: Chromaticities of the experimental primaries and the 20,250 cm^-1 test
light.  The green and blue primaries on the match side of the stimulus, and the
test light and red primary on the test side of the stimulus, are mixed in
proportions to find the chromaticity where the lines joining each pair
intersect.
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
from maths.plotting_series import spectrum_locus_170_2_10
# endregion

# region Plot Settings
INVERTED = False
SIZE = (4, 3.2)
FONT_SIZES = {
    'titles' : 14,
    'labels' : 12,
    'ticks' : 10,
    'legends' : 8
}
EXTENSION = 'svg'
# endregion

# region Initialize Figure
figure = Figure(
    name = 'figure_10_color_matching_experiment_mixing{0}'.format(
        '_inverted' if INVERTED else ''
    ),
    size = SIZE,
    inverted = INVERTED
)
figure.set_fonts(**FONT_SIZES)
panel = figure.add_panel(
    name = 'main',
    title = '',
    x_label = 'x',
    x_ticks = arange(0, 0.81, 0.1),
    x_lim = (-0.065, 0.865),
    y_label = 'y',
    y_ticks = arange(0, 0.81, 0.1),
    y_lim = (-0.065, 0.865)
)
panel.set_aspect(
    aspect = 'equal', # Make horizontal and vertical axes the same scale
    adjustable = 'box' # Change the plot area aspect ratio to achieve this
)
# endregion

# region Reference Lines
panel.axhline(
    y = 0,
    linewidth = 2,
    color = figure.grey_level(0.25),
    zorder = 0
)
panel.axvline(
    x = 0,
    linewidth = 2,
    color = figure.grey_level(0.25),
    zorder = 0
)
panel.plot(
    [0, 1],
    [1, 0],
    linestyle = ':',
    color = figure.grey_level(0.75),
    zorder = 0
)
panel.plot(
    list(datum['x'] for datum in spectrum_locus_170_2_10),
    list(datum['y'] for datum in spectrum_locus_170_2_10),
    color = figure.grey_level(0.5),
    zorder = 2
)
panel.plot(
    [spectrum_locus_170_2_10[0]['x'], spectrum_locus_170_2_10[-1]['x']],
    [spectrum_locus_170_2_10[0]['y'], spectrum_locus_170_2_10[-1]['y']],
    linestyle = ':',
    color = figure.grey_level(0.5),
    zorder = 1
)
# endregion

# region Plot Lights with Lines Connecting to Matching Chromaticity
match_chromaticity = (0.1705, 0.494)
legend_handles = list()
for chromaticity, color in [
    ((0.713, 0.287), (0.8, 0, 0)), # Red
    ((0.180, 0.799), (0, 0.8, 0)), # Green
    ((0.154, 0.033), (0, 0, 0.8)), # Blue
    ((0.007, 0.559), figure.grey_level(0.2)) # Test
]:
    legend_handles.append(
        panel.plot(
            *chromaticity,
            linestyle = 'none',
            marker = 'o',
            markersize = 4,
            markeredgecolor = 'none',
            markerfacecolor = color,
            zorder = 4
        )[0]
    )
    panel.plot(
        [chromaticity[0], match_chromaticity[0]],
        [chromaticity[1], match_chromaticity[1]],
        linestyle = '--',
        color = color,
        zorder = 3
    )
legend_handles.append(
    panel.plot(
        *match_chromaticity,
        linestyle = 'none',
        marker = 'o',
        markersize = 4,
        markerfacecolor = figure.grey_level(1),
        markeredgecolor = figure.grey_level(0.2),
        zorder = 4
    )[0]
)
# endregion

# region Plot Legend
panel.legend(
    legend_handles,
    [
        'Red Primary',
        'Green Primary',
        'Blue Primary',
        'Test Light',
        'Match'
    ],
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
