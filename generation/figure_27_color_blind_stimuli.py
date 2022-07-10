"""
Example color-blind test stimuli for each cone type with accompanying
chromaticity diagram showing the distribution of chromaticities.

Caption: Example color-blind test stimuli for (from left-to-right) missing
long-, medium-, or short-wavelength sensitive cones (protanope, deuteranope, and
tritanope, respectively).  The object is to indicate the direction of the gap in
the embedded "C" shape.  Below each stimulus is a chromaticity diagram showing
the distribution of chromaticities in the stimulus (black fuzzy lines crossing
the white point).
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
from maths.conversion_coefficients import CONE_NAMES, COLOR_NAMES
from maths.color_blind import get_unique_colors
from maths.color_conversion import xyz_to_xyy, rgb_to_xyz
from figure.figure import Figure
from numpy import arange, transpose
from PIL import Image
from maths.plotting_series import (
    spectrum_locus_1931_2,
    gamut_triangle_vertices_srgb
)
from maths.coloration import chromaticity_inside_gamut
from matplotlib.collections import PathCollection
# endregion

# region Plot Settings
INVERTED = False
SIZE = (6.75, 4)
FONT_SIZES = {
    'titles' : 14,
    'labels' : 12,
    'ticks' : 10,
    'legends' : 7
}
EXTENSION = 'svg'
RESOLUTION = 16
MINIMUM_COUNT = 4 # May be helpful to clean distribution in case of (compression) artifacts
# endregion

# region Load Images and Get Distributions
images = dict()
distributions = dict()
for cone_name in CONE_NAMES:
    images[cone_name] = Image.open(
        'images/figure_27_{0}_stimulus.png'.format(
            cone_name[0].lower()
        )
    )
    unique_colors = get_unique_colors(images[cone_name])
    distributions[cone_name] = {
        xyz_to_xyy(
            *rgb_to_xyz(
                *list(
                    float(value / 255.0)
                    for value in unique_color
                )
            )
        )[0:2] : count
        for unique_color, count in unique_colors.items()
    }
# endregion

# region Initialize Figure
figure = Figure(
    name = 'figure_27_color_blind_stimuli{0}'.format(
        '_inverted' if INVERTED else ''
    ),
    size = SIZE,
    inverted = INVERTED
)
figure.set_fonts(**FONT_SIZES)
mid_point = 0.55
long_image_panel = figure.add_panel(
    name = 'long_image',
    title = '',
    position = (0 / 3, mid_point, 1 / 3, 1 - mid_point),
    x_label = '',
    x_ticks = [],
    y_label = '',
    y_ticks = []
)
long_chromaticity_panel = figure.add_panel(
    name = 'long_chromaticity',
    title = '',
    position = (0 / 3, 0, 1 / 3, mid_point),
    x_label = r'$x$',
    x_ticks = arange(0, 0.81, 0.2),
    x_lim = (-0.065, 0.865),
    y_label = r'$y$',
    y_ticks = arange(0, 0.81, 0.2),
    y_lim = (-0.065, 0.865)
)
medium_image_panel = figure.add_panel(
    name = 'medium_image',
    title = '',
    position = (1 / 3, mid_point, 1 / 3, 1 - mid_point),
    x_label = '',
    x_ticks = [],
    y_label = '',
    y_ticks = []
)
medium_chromaticity_panel = figure.add_panel(
    name = 'medium_chromaticity',
    title = '',
    position = (1 / 3, 0, 1 / 3, mid_point),
    x_label = r'$x$',
    x_ticks = arange(0, 0.81, 0.2),
    x_lim = (-0.065, 0.865),
    y_label = r'$y$',
    y_ticks = arange(0, 0.81, 0.2),
    y_lim = (-0.065, 0.865)
)
short_image_panel = figure.add_panel(
    name = 'short_image',
    title = '',
    position = (2 / 3, mid_point, 1 / 3, 1 - mid_point),
    x_label = '',
    x_ticks = [],
    y_label = '',
    y_ticks = []
)
short_chromaticity_panel = figure.add_panel(
    name = 'short_chromaticity',
    title = '',
    position = (2 / 3, 0, 1 / 3, mid_point),
    x_label = r'$x$',
    x_ticks = arange(0, 0.81, 0.2),
    x_lim = (-0.065, 0.865),
    y_label = r'$y$',
    y_ticks = arange(0, 0.81, 0.2),
    y_lim = (-0.065, 0.865)
)
for panel in figure.panels.values():
    panel.set_aspect(
        aspect = 'equal', # Make horizontal and vertical axes the same scale
        adjustable = 'box' # Change the plot area aspect ratio to achieve this
    )
# endregion

# region Load Images into Panels
for cone_name in CONE_NAMES:
    figure.panels['{0}_image'.format(cone_name.lower())].imshow(images[cone_name])
# endregion

# region Reference Lines
for panel_name, panel in figure.panels.items():
    if 'chromaticity' not in panel_name: continue
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
        list(datum['x'] for datum in spectrum_locus_1931_2),
        list(datum['y'] for datum in spectrum_locus_1931_2),
        solid_capstyle = 'round',
        color = figure.grey_level(0.5),
        zorder = 2
    )
    panel.plot(
        [spectrum_locus_1931_2[0]['x'], spectrum_locus_1931_2[-1]['x']],
        [spectrum_locus_1931_2[0]['y'], spectrum_locus_1931_2[-1]['y']],
        linestyle = ':',
        solid_capstyle = 'round',
        color = figure.grey_level(0.5),
        zorder = 1
    )
    panel.plot(
        *transpose(
            list(
                (
                    gamut_triangle_vertices_srgb[COLOR_NAMES[index]]['x'],
                    gamut_triangle_vertices_srgb[COLOR_NAMES[index]]['y']
                )
                for index in [0, 1, 2, 0]
            )
        ),
        color = figure.grey_level(0.75),
        zorder = 3
    )
# endregion

# region Color Fill
paths, colors = chromaticity_inside_gamut(RESOLUTION)
for panel_name, panel in figure.panels.items():
    if 'chromaticity' not in panel_name: continue
    panel.add_collection(
        PathCollection(
            paths,
            facecolors = colors,
            edgecolors = colors,
            linewidth = 0,
            zorder = 0
        )
    )
# endregion

# region Plot Distributions
for cone_name, cone_distribution in distributions.items():
    max_count = max(cone_distribution.values())
    for chromaticity, count in cone_distribution.items():
        if count < MINIMUM_COUNT: continue
        figure.panels['{0}_chromaticity'.format(cone_name.lower())].plot(
            *chromaticity,
            linestyle = 'none',
            marker = 'o',
            markersize = 1,
            markeredgecolor = 'none',
            markerfacecolor = (0, 0, 0, 0.125 + 0.875 * (count / max_count)),
            zorder = 1
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
