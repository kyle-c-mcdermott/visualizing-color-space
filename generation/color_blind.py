"""
Figures showcasing color-blind stimuli and the analysis and filtering of images
to simulate color-blindness.

Figure Captions:
29 - Example color-blind testing stimuli for missing l-, m-, or s-cones (from
left to right).  Figures are composed of random dot fields where the task is to
identify the direction of the gap in the interior circle (which way is the C
facing?).  Dot luminances are randomized to eliminate luminance cues, while
colors are sampled from a linear distribution along a confusion line for the
designated cone passing through the chromaticity for white (shown in lower
panels).  Note that the background grey pixels account for the dot in the middle
of each distribution where the line segments on either side represent the
background and foreground distributions of colors.
30 - Series of color-blind testing stimuli with decreasing contrast from left to
right.  Stimuli for missing l-, m-, and s-cones are in each row from top to
bottom.  For these images there is no gap between background and foreground
color distributions as there were in Figure 29; this means that the same grey
chromaticity may appear in both the foreground and background distributions.
31 - (Filtered image series using constant (mean) distance from copunctal point)
32 - (Filtered image series using perpendicular line through white)
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
SAVE_FIGURES = (
    False, # Figure 29 - Color-blind stimuli with chromaticity diagrams
    False, # Figure 30 - Color-blind stimuli with decreasing contrast
    True, # Figure 31 - Filtered images with constant-distance
    False # Figure 32 - Filtered images with perpendicular line
)
INVERTED = False
SIZE = (16, 9)
FONT_SIZES = {
    'titles' : 16,
    'labels' : 14,
    'ticks' : 12,
    'legends' : 12
}
COUNT_MIN = 100
RESOLUTION = 32
EXTENSION = 'svg'
# endregion

# region Imports
from csv import DictReader
from maths.rgb_cie_conversions import rgb_to_chromoluminance
from maths.saturated_color_paths import chromaticity_within_gamut

from PIL import Image
from maths.color_blind_filters import get_unique_colors

from figure.figure import Figure
from numpy import linspace, transpose
from matplotlib.collections import PathCollection

# endregion

# region Constants

# endregion

# region Load CIE 1931 2-Degree Spectrum Locus
"""
Tabulated spectrum locus coordinates for CIE 1931 2-degree downloaded from:
http://www.cvrl.org/cie.htm
Under Chromaticity Coordinates, CIE 1931 2-deg xyz chromaticity coordinates
using the second button "/W" with a solid (instead of dashed) line indicating
higher sampling resolution (1 nm)
(Note that chromaticity values do not change beyond 699 nm, likely due to the
fact that rounding errors seem to cause the spectrum locus to start wandering
about back on itself based on chromaticities converted from the tabulated color
matching functions - the converted values were abandoned and 699 nm copied down
for the remainder of the series.)
"""
with open(
    'cvrl/cccie31_1.csv',
    'r'
) as read_file:
    spectrum_locus = list(
        {
            'Wavelength' : int(row['Wavelength']),
            'x' : float(row['x']),
            'y' : float(row['y'])
        }
        for row in DictReader(
            read_file,
            fieldnames = ['Wavelength', 'x', 'y', 'z'] # z is superfluous
        )
        if int(row['Wavelength']) < 700
    )
# endregion

# region Estimate sRGB Chromaticities (in CIE 1931)
srgb_primary_chromaticities = list(
    rgb_to_chromoluminance(
        red,
        green,
        blue
    )[0:2]
    for (red, green, blue) in [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 0, 0)]
)
# endregion

# region Load Images
sample_images = list(
    Image.open(
        'images/Color-Blind Stimulus - {0}-Cone Example.png'.format(
            cone_name
        )
    )
    for cone_name in ['L', 'M', 'S']
)
sample_images_unique_colors = list(
    get_unique_colors(sample_image)
    for sample_image in sample_images
)
contrast_images = list(
    list(
        Image.open(
            'images/Color-Blind Stimulus - {0}-Cone Contrast {1}.png'.format(
                cone_name,
                contrast_name
            )
        )
        for contrast_name in ['A', 'B', 'C', 'D']
    )
    for cone_name in ['L', 'M', 'S']
)
# endregion

# region Figure 29 - Color-Blind Stimuli with Chromaticity Diagrams

if SAVE_FIGURES[0]:

    # region Initialize Figure
    figure = Figure(
        name = 'Color-Blind Stimuli with Chromaticity{0}'.format(
            ' (inverted)' if INVERTED else ''
        ),
        size = (SIZE[0] * 0.85, SIZE[1]),
        inverted = INVERTED
    )
    figure.set_fonts(**FONT_SIZES)
    l_image_panel = figure.add_panel(
        name = 'l_image',
        title = 'Protanope Color-Blind Stimulus',
        position = (0 / 3, 0.55, 1 / 3, 0.45),
        x_label = '',
        x_ticks = [],
        y_label = '',
        y_ticks = []
    )
    l_chromaticity_panel = figure.add_panel(
        name = 'l_chromaticity',
        title = 'Protanope Color-Blind Stimulus\nChromaticity Distribution',
        position = (0 / 3, 0, 1 / 3, 0.55),
        x_label = 'x',
        x_ticks = linspace(0, 0.8, 9),
        x_lim = (-0.065, 0.865),
        y_label = 'y',
        y_ticks = linspace(0, 0.8, 9),
        y_lim = (-0.065, 0.865)
    )
    m_image_panel = figure.add_panel(
        name = 'm_image',
        title = 'Deuteranope Color-Blind Stimulus',
        position = (1 / 3, 0.55, 1 / 3, 0.45),
        x_label = '',
        x_ticks = [],
        y_label = '',
        y_ticks = []
    )
    m_chromaticity_panel = figure.add_panel(
        name = 'm_chromaticity',
        title = 'Deuteranope Color-Blind Stimulus\nChromaticity Distribution',
        position = (1 / 3, 0, 1 / 3, 0.55),
        x_label = 'x',
        x_ticks = linspace(0, 0.8, 9),
        x_lim = (-0.065, 0.865),
        y_label = 'y',
        y_ticks = linspace(0, 0.8, 9),
        y_lim = (-0.065, 0.865)
    )
    s_image_panel = figure.add_panel(
        name = 's_image',
        title = 'Tritanope Color-Blind Stimulus',
        position = (2 / 3, 0.55, 1 / 3, 0.45),
        x_label = '',
        x_ticks = [],
        y_label = '',
        y_ticks = []
    )
    s_chromaticity_panel = figure.add_panel(
        name = 's_chromaticity',
        title = 'Tritanope Color-Blind Stimulus\nChromaticity Distribution',
        position = (2 / 3, 0, 1 / 3, 0.55),
        x_label = 'x',
        x_ticks = linspace(0, 0.8, 9),
        x_lim = (-0.065, 0.865),
        y_label = 'y',
        y_ticks = linspace(0, 0.8, 9),
        y_lim = (-0.065, 0.865)
    )
    for panel_name, panel in figure.panels.items():
        if 'chromaticity' in panel_name:
            panel.set_aspect(
                aspect = 'equal',
                adjustable = 'box'
            )
    # endregion

    # region Load Images into Panels
    l_image_panel.imshow(sample_images[0])
    m_image_panel.imshow(sample_images[1])
    s_image_panel.imshow(sample_images[2])
    # endregion

    # region Reference
    for panel_name, panel in figure.panels.items():
        if 'chromaticity' not in panel_name: continue
        panel.axhline(
            y = 0,
            linewidth = 2,
            color = figure.grey_level(0),
            zorder = 0
        )
        panel.axvline(
            x = 0,
            linewidth = 2,
            color = figure.grey_level(0),
            zorder = 0
        )
        panel.plot(
            [0, 1],
            [1, 0],
            linestyle = '--',
            color = figure.grey_level(0.5),
            zorder = 0
        )
        panel.plot(
            list(datum['x'] for datum in spectrum_locus),
            list(datum['y'] for datum in spectrum_locus),
            color = figure.grey_level(0.25),
            zorder = 2
        )
        panel.plot(
            [spectrum_locus[0]['x'], spectrum_locus[-1]['x']],
            [spectrum_locus[0]['y'], spectrum_locus[-1]['y']],
            color = figure.grey_level(0.25),
            linestyle = ':',
            zorder = 2
        )
        panel.plot(
            *transpose(srgb_primary_chromaticities),
            color = figure.grey_level(0.25),
            zorder = 2
        )
    # endregion

    # region Color Fill
    paths, colors = chromaticity_within_gamut(
        resolution = RESOLUTION,
        gamma_correct = False
    )
    for panel_name, panel in figure.panels.items():
        if 'chromaticity' not in panel_name: continue
        panel.add_collection(
            PathCollection(
                paths,
                facecolors = colors,
                edgecolors = colors,
                zorder = 1
            )
        )
    # endregion

    # region Plot Unique Colors
    for cone_index, cone_name in enumerate(['l', 'm', 's']):
        max_count = max(sample_images_unique_colors[cone_index].values())
        for unique_color, count in sample_images_unique_colors[cone_index].items():
            if count < COUNT_MIN: continue
            figure.panels['{0}_chromaticity'.format(cone_name)].plot(
                *rgb_to_chromoluminance(
                    *list(
                        value / 255
                        for value in unique_color
                    ),
                    gamma_correct = False
                )[0:2],
                linestyle = 'none',
                marker = 'o',
                markersize = 2,
                markeredgecolor = 'none',
                markerfacecolor = (0, 0, 0, 0.125 + 0.875 * (count / max_count)),
                zorder = 3
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

# region Figure 30 - Color-Blind Stimuli with Decreasing Contrast

if SAVE_FIGURES[1]:

    # region Initialize Figure
    figure = Figure(
        name = 'Color-Blind Stimuli with Decreasing Contrast{0}'.format(
            ' (inverted)' if INVERTED else ''
        ),
        size = (SIZE[0] * 0.85, SIZE[1]),
        inverted = INVERTED
    )
    figure.set_fonts(**FONT_SIZES)
    l_a_panel = figure.add_panel(
        name = 'l_a',
        title = '',
        position = (0 / 4, 2 / 3, 1 / 4, 1 / 3),
        x_label = '',
        x_ticks = [],
        y_label = 'Protanope Stimuli',
        y_ticks = []
    )
    l_b_panel = figure.add_panel(
        name = 'l_b',
        title = '',
        position = (1 / 4, 2 / 3, 1 / 4, 1 / 3),
        x_label = '',
        x_ticks = [],
        y_label = '',
        y_ticks = []
    )
    l_c_panel = figure.add_panel(
        name = 'l_c',
        title = '',
        position = (2 / 4, 2 / 3, 1 / 4, 1 / 3),
        x_label = '',
        x_ticks = [],
        y_label = '',
        y_ticks = []
    )
    l_d_panel = figure.add_panel(
        name = 'l_d',
        title = '',
        position = (3 / 4, 2 / 3, 1 / 4, 1 / 3),
        x_label = '',
        x_ticks = [],
        y_label = '',
        y_ticks = []
    )
    m_a_panel = figure.add_panel(
        name = 'm_a',
        title = '',
        position = (0 / 4, 1 / 3, 1 / 4, 1 / 3),
        x_label = '',
        x_ticks = [],
        y_label = 'Deuteranope Stimuli',
        y_ticks = []
    )
    m_b_panel = figure.add_panel(
        name = 'm_b',
        title = '',
        position = (1 / 4, 1 / 3, 1 / 4, 1 / 3),
        x_label = '',
        x_ticks = [],
        y_label = '',
        y_ticks = []
    )
    m_c_panel = figure.add_panel(
        name = 'm_c',
        title = '',
        position = (2 / 4, 1 / 3, 1 / 4, 1 / 3),
        x_label = '',
        x_ticks = [],
        y_label = '',
        y_ticks = []
    )
    m_d_panel = figure.add_panel(
        name = 'm_d',
        title = '',
        position = (3 / 4, 1 / 3, 1 / 4, 1 / 3),
        x_label = '',
        x_ticks = [],
        y_label = '',
        y_ticks = []
    )
    s_a_panel = figure.add_panel(
        name = 's_a',
        title = '',
        position = (0 / 4, 0 / 3, 1 / 4, 1 / 3),
        x_label = '',
        x_ticks = [],
        y_label = 'Tritanope Stimuli',
        y_ticks = []
    )
    s_b_panel = figure.add_panel(
        name = 's_b',
        title = '',
        position = (1 / 4, 0 / 3, 1 / 4, 1 / 3),
        x_label = '',
        x_ticks = [],
        y_label = '',
        y_ticks = []
    )
    s_c_panel = figure.add_panel(
        name = 's_c',
        title = '',
        position = (2 / 4, 0 / 3, 1 / 4, 1 / 3),
        x_label = '',
        x_ticks = [],
        y_label = '',
        y_ticks = []
    )
    s_d_panel = figure.add_panel(
        name = 's_d',
        title = '',
        position = (3 / 4, 0 / 3, 1 / 4, 1 / 3),
        x_label = '',
        x_ticks = [],
        y_label = '',
        y_ticks = []
    )
    # endregion

    # region Load Images into Panels
    for cone_index, cone_name in enumerate(['l', 'm', 's']):
        for contrast_index, contrast_name in enumerate(['a', 'b', 'c', 'd']):
            figure.panels['{0}_{1}'.format(cone_name, contrast_name)].imshow(
                contrast_images[cone_index][contrast_index]
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

