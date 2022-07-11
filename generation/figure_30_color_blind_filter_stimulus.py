"""
Filtering a color-blind test stimulus to mimic the effects of color-blindness,
with filtered images and chromatic distributions.

Caption: A color-blind test stimulus (protanope) filtered to remove chromatic
differences to which an observer with a missing cone type would not be
sensitive.  From left-to-right are the original image, a protanope filtered
image, a deuteranope filtered image, and a tritanope filtered image.  Below each
image is a chromaticity diagram showing the distribution of chromaticities in
the image.  Note that in the second image from the left (filtered to mimic the
chromatic discriminability of a protanope) the "C" figure is invisible (the
distribution is a more-or-less uniform point).
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
    TEXT_WIDTH,
    FONT_SIZES,
    AXES_GREY_LEVEL, DOTTED_GREY_LEVEL, SL_GREY_LEVEL
)
from PIL import Image
from maths.color_conversion import xyz_to_xyy, rgb_to_xyz
from maths.color_blind import get_unique_colors, filter_image, CONE
from figure.figure import Figure
from numpy import arange, transpose
from maths.plotting_series import (
    spectrum_locus_1931_2,
    gamut_triangle_vertices_srgb
)
from maths.conversion_coefficients import COLOR_NAMES
from maths.coloration import chromaticity_inside_gamut
from matplotlib.collections import PathCollection
# endregion

# region Plot Settings
INVERTED = False
SIZE = (
    TEXT_WIDTH,
    3.1
)
EXTENSION = 'pdf'
RESOLUTION = 16
MINIMUM_COUNT = 8 # May be helpful to clean distribution in case of (compression) artifacts
# endregion

# region Load and Filter Image and Get Distributions
original_image = Image.open('images/figure_30_stimulus.png')
original_chromaticities = {
    xyz_to_xyy(
        *rgb_to_xyz(
            *list(
                float(value / 255.0)
                for value in unique_color
            )
        )
    )[0:2] : count
    for unique_color, count in get_unique_colors(original_image).items()
}
filtered_images = {
    cone_type.value : filter_image(
        original_image,
        cone_type.value
    )
    for cone_type in CONE
}
filtered_chromaticities = {
    cone_name : {
        xyz_to_xyy(
            *rgb_to_xyz(
                *list(
                    float(value / 255.0)
                    for value in unique_color
                )
            )
        )[0:2] : count
        for unique_color, count in get_unique_colors(cone_image).items()
    }
    for cone_name, cone_image in filtered_images.items()
}
# endregion

# region Initialize Figure
figure = Figure(
    name = 'figure_30_color_blind_filter_stimulus{0}'.format(
        '_inverted' if INVERTED else ''
    ),
    size = SIZE,
    inverted = INVERTED
)
figure.set_fonts(**FONT_SIZES)
mid_point = 0.55
original_image_panel = figure.add_panel(
    name = 'original_image',
    title = '',
    position = (0 / 4, mid_point, 1 / 4, 1 - mid_point),
    x_label = '',
    x_ticks = [],
    y_label = '',
    y_ticks = []
)
original_chromaticity_panel = figure.add_panel(
    name = 'original_chromaticity',
    title = '',
    position = (0 / 4, 0, 1 / 4, mid_point),
    x_label = r'$x$',
    x_ticks = arange(0, 0.81, 0.2),
    x_lim = (-0.065, 0.865),
    y_label = r'$y$',
    y_ticks = arange(0, 0.81, 0.2),
    y_lim = (-0.065, 0.865)
)
long_image_panel = figure.add_panel(
    name = 'long_image',
    title = '',
    position = (1 / 4, mid_point, 1 / 4, 1 - mid_point),
    x_label = '',
    x_ticks = [],
    y_label = '',
    y_ticks = []
)
long_chromaticity_panel = figure.add_panel(
    name = 'long_chromaticity',
    title = '',
    position = (1 / 4, 0, 1 / 4, mid_point),
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
    position = (2 / 4, mid_point, 1 / 4, 1 - mid_point),
    x_label = '',
    x_ticks = [],
    y_label = '',
    y_ticks = []
)
medium_chromaticity_panel = figure.add_panel(
    name = 'medium_chromaticity',
    title = '',
    position = (2 / 4, 0, 1 / 4, mid_point),
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
    position = (3 / 4, mid_point, 1 / 4, 1 - mid_point),
    x_label = '',
    x_ticks = [],
    y_label = '',
    y_ticks = []
)
short_chromaticity_panel = figure.add_panel(
    name = 'short_chromaticity',
    title = '',
    position = (3 / 4, 0, 1 / 4, mid_point),
    x_label = r'$x$',
    x_ticks = arange(0, 0.81, 0.2),
    x_lim = (-0.065, 0.865),
    y_label = r'$y$',
    y_ticks = arange(0, 0.81, 0.2),
    y_lim = (-0.065, 0.865)
)
for panel_name, panel in figure.panels.items():
    if 'chromaticity' not in panel_name: continue
    panel.set_aspect(
        aspect = 'equal', # Make horizontal and vertical axes the same scale
        adjustable = 'box' # Change the plot area aspect ratio to achieve this
    )
# endregion

# region Load Images into Panels
original_image_panel.imshow(original_image)
for cone_name, cone_image in filtered_images.items():
    figure.panels['{0}_image'.format(cone_name.lower())].imshow(cone_image)
# endregion

# region Reference Lines
for panel_name, panel in figure.panels.items():
    if 'chromaticity' not in panel_name: continue
    panel.axhline(
        y = 0,
        linewidth = 2,
        color = figure.grey_level(AXES_GREY_LEVEL),
        zorder = 0
    )
    panel.axvline(
        x = 0,
        linewidth = 2,
        color = figure.grey_level(AXES_GREY_LEVEL),
        zorder = 0
    )
    panel.plot(
        [0, 1],
        [1, 0],
        linestyle = ':',
        color = figure.grey_level(DOTTED_GREY_LEVEL),
        zorder = 0
    )
    panel.plot(
        list(datum['x'] for datum in spectrum_locus_1931_2),
        list(datum['y'] for datum in spectrum_locus_1931_2),
        solid_capstyle = 'round',
        color = figure.grey_level(SL_GREY_LEVEL),
        zorder = 2
    )
    panel.plot(
        [spectrum_locus_1931_2[0]['x'], spectrum_locus_1931_2[-1]['x']],
        [spectrum_locus_1931_2[0]['y'], spectrum_locus_1931_2[-1]['y']],
        linestyle = ':',
        solid_capstyle = 'round',
        color = figure.grey_level(SL_GREY_LEVEL),
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
        color = figure.grey_level(DOTTED_GREY_LEVEL),
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
            linewidth = 0.1,
            zorder = 0
        )
    )
# endregion

# region Plot Distributions
for panel, distribution in [
    (original_chromaticity_panel, original_chromaticities),
    (long_chromaticity_panel, filtered_chromaticities['long']),
    (medium_chromaticity_panel, filtered_chromaticities['medium']),
    (short_chromaticity_panel, filtered_chromaticities['short'])
]:
    max_count = max(distribution.values())
    for chromaticity, count in distribution.items():
        if count < MINIMUM_COUNT: continue
        panel.plot(
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
figure.update(
    buffer = 2
)
figure.save(
    path = 'images',
    name = figure.name,
    extension = EXTENSION
)
figure.close()
# endregion
