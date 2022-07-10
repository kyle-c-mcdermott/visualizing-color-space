"""
Example color-blind test stimuli of decreasing chromatic contrast.

Caption: Color-blind test stimuli with decreasing contrast from left-to-right.
The distributions of chromaticities in the sample stimuli are taken from (from
top-to-bottom) long-, medium-, and short-wavelength-sensitive confusion lines.
These stimuli are not calibrated - the reader should not take an ability or
inability to perform the associated discrimination task here as an indication of
whether or not they may be color-blind.
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
from maths.conversion_coefficients import CONE_NAMES
from PIL import Image
from figure.figure import Figure
# endregion

# region Plot Settings
INVERTED = False
SIZE = (5.3, 4)
FONT_SIZES = {
    'titles' : 14,
    'labels' : 12,
    'ticks' : 10,
    'legends' : 7
}
EXTENSION = 'svg'
# endregion

# region Load Images
images = dict()
for cone_name in CONE_NAMES:
    images[cone_name] = list()
    for index in range(4):
        images[cone_name].append(
            Image.open(
                'images/figure_28_{0}_{1}.png'.format(
                    cone_name[0].lower(),
                    index
                )
            )
        )
# endregion

# region Initialize Figure
figure = Figure(
    name = 'figure_28_color_blind_stimuli_contrast{0}'.format(
        '_inverted' if INVERTED else ''
    ),
    size = SIZE,
    inverted = INVERTED
)
figure.set_fonts(**FONT_SIZES)
for cone_index, cone_name in enumerate(CONE_NAMES):
    for contrast_index in range(4):
        figure.add_panel(
            name = '{0}_{1}'.format(cone_name, contrast_index),
            title = '',
            position = (
                contrast_index / 4,
                (2 - cone_index) / 3,
                1 / 4,
                1 / 3
            ),
            x_label = '',
            x_ticks = [],
            y_label = '',
            y_ticks = []
        )
for panel in figure.panels.values():
    panel.set_aspect(
        aspect = 'equal', # Make horizontal and vertical axes the same scale
        adjustable = 'box' # Change the plot area aspect ratio to achieve this
    )
# endregion

# region Load Images into Panels
for cone_name in CONE_NAMES:
    for index in range(4):
        figure.panels['{0}_{1}'.format(cone_name, index)].imshow(
            images[cone_name][index]
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
