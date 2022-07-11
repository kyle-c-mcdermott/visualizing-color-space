"""
Visible spectrum bands with their corresponding red, green, and blue values
plotted.

Caption: Visible spectrum bands and the corresponding red, green, and blue
values as functions of wavelengths.  The saturated spectrum is the same as that
presented in Figure X (with the more extreme wavelengths cropped out).  The
smoothed spectrum was constructed with an arbitrary method that preserves the
hue angle for each wavelength but otherwise smooths out the resulting functions
for red, green, and blue (note that green and blue cross at the same cyan
wavelength, and green and red cross at the same yellow wavelength, for both
series).
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
    TEXT_WIDTH, TEXT_HEIGHT,
    FONT_SIZES,
    WAVELENGTH_LABEL
)
from numpy import arange, ptp, arctan2, exp, log, linspace, cos, sin
from maths.coloration import visible_spectrum
from maths.color_conversion import (
    xyz_to_xyy,
    rgb_to_xyz,
    xyz_to_rgb,
    xyy_to_xyz
)
from figure.figure import Figure
from matplotlib.collections import PathCollection
# endregion

# region Plot Settings
INVERTED = False
SIZE = (
    TEXT_WIDTH,
    TEXT_HEIGHT / 3
)
EXTENSION = 'pdf'
RESOLUTION = 64
# endregion

# region Constants
WAVELENGTH_TICKS = list(
    int(tick)
    for tick in [
        450
    ] + list(arange(475, 601, 5, dtype = int)) + [
        610,
        625,
        650
    ]
)
WHITE = (0.31271, 0.32902) # D65
# endregion

# region Modify Color Series
spectrum_paths, spectrum_colors = visible_spectrum(
    RESOLUTION,
    WAVELENGTH_TICKS[0],
    0.5,
    int(ptp(WAVELENGTH_TICKS)),
    0.5,
    WAVELENGTH_TICKS[0],
    WAVELENGTH_TICKS[-1]
)
smoothed_paths, _ = visible_spectrum(
    RESOLUTION,
    WAVELENGTH_TICKS[0],
    0,
    int(ptp(WAVELENGTH_TICKS)),
    0.5,
    WAVELENGTH_TICKS[0],
    WAVELENGTH_TICKS[-1]
)
spectrum_chromoluminances = list(
    xyz_to_xyy(
        *rgb_to_xyz(
            *color
        )
    )
    for color in spectrum_colors
)
angles = list( # Will preserve angle
    arctan2(
        chromoluminance[1] - WHITE[1], # delta-y
        chromoluminance[0] - WHITE[0] # delta-x
    )
    for chromoluminance in spectrum_chromoluminances
)
def gaussian(x, min, max, center, width):
    return (
        min
        + (max - min)
        * exp(
            (4.0 * log(0.5) * (center - x) ** 2.0)
            / (width ** 2.0)
        )
    )
"""
The method for obtaining the Gaussian parameters was essentially to plot the
radius from white vs. wavelength and construct a Gaussian (pointing down) just
below that (ensuring requested radii are inside the color gamut) and likewise
plotting luminance Y vs. wavelength and constructing a Gaussian just below that
(ensuring requested luminances are below the maximum).  Thus chromatic contrast
and luminance both follow Gaussian curves - smoothing out the original chromatic
contrast and luminance resulting from the saturated colors.
"""
wavelengths = linspace(
    WAVELENGTH_TICKS[0],
    WAVELENGTH_TICKS[-1],
    RESOLUTION
)
smoothed_colors = list(
    xyz_to_rgb(
        *xyy_to_xyz(
            WHITE[0] + gaussian(wavelength, 0.205, 0.08, 497, 75) * cos(angles[wavelength_index]),
            WHITE[1] + gaussian(wavelength, 0.205, 0.08, 497, 75) * sin(angles[wavelength_index]),
            gaussian(wavelength, 0.05, 0.72, 553, 75)
        )
    )
    for wavelength_index, wavelength in enumerate(wavelengths)
)
# endregion

# region Initialize Figure
figure = Figure(
    name = 'figure_19_visible_spectrum_functions{0}'.format(
        '_inverted' if INVERTED else ''
    ),
    size = SIZE,
    inverted = INVERTED
)
figure.set_fonts(**FONT_SIZES)
mid_point = 0.6
spectra_panel = figure.add_panel(
    name = 'spectra',
    title = '',
    position = (0, mid_point, 1, 1 - mid_point),
    x_label = WAVELENGTH_LABEL,
    x_lim = (
        WAVELENGTH_TICKS[0],
        WAVELENGTH_TICKS[-1]
    ),
    x_margin = 0.0,
    x_ticks = WAVELENGTH_TICKS[1:-1],
    x_tick_labels = list(
        wavelength_tick
        if int(wavelength_tick / 25) == wavelength_tick / 25
        else ''
        for wavelength_tick in WAVELENGTH_TICKS[1:-1]
    ),
    y_label = '',
    y_lim = (0, 1),
    y_margin = 0.0,
    y_ticks = [0.25, 0.75],
    y_tick_labels = ['Smoothed', 'Saturated']
)
functions_panel = figure.add_panel(
    name = 'functions',
    title = '',
    position = (0, 0, 1, mid_point),
    x_label = WAVELENGTH_LABEL,
    x_lim = (
        WAVELENGTH_TICKS[0],
        WAVELENGTH_TICKS[-1]
    ),
    x_margin = 0.0,
    x_ticks = WAVELENGTH_TICKS[1:-1],
    x_tick_labels = list(
        wavelength_tick
        if int(wavelength_tick / 25) == wavelength_tick / 25
        else ''
        for wavelength_tick in WAVELENGTH_TICKS[1:-1]
    ),
    y_label = 'Color Value'
)
# endregion

# region Color Fill
spectra_panel.add_collection(
    PathCollection(
        spectrum_paths,
        facecolors = spectrum_colors,
        edgecolors = spectrum_colors,
        linewidth = 0.1
    )
)
spectra_panel.add_collection(
    PathCollection(
        smoothed_paths,
        facecolors = smoothed_colors,
        edgecolors = smoothed_colors,
        linewidth = 0.1
    )
)
# endregion

# region Plot Red, Green, and Blue
legend_handles = list()
for color_index in range(3):
    color = 3 * [0.0]; color[color_index] = 1.0
    legend_handles.append(
        functions_panel.plot(
            wavelengths,
            list(spectrum_color[color_index] for spectrum_color in spectrum_colors),
            color = color,
            zorder = 1
        )[0]
    )
    legend_handles.append(
        functions_panel.plot(
            wavelengths,
            list(smoothed_color[color_index] for smoothed_color in smoothed_colors),
            color = color,
            linestyle = '--',
            zorder = 0
        )[0]
    )
# endregion

# region Plot Legend
functions_panel.legend(
    legend_handles,
    list(
        '{0} {1}'.format(
            function_type,
            color_name
        )
        for color_name in ['Red', 'Green', 'Blue']
        for function_type in ['Saturated', 'Smoothed']
    ),
    markerfirst = False,
    loc = 'upper right',
    facecolor = figure.grey_level(1)
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
