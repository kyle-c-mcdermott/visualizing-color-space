"""
CIE 1960 (u, v) chromaticity zoomed in on Planckian locus with isotherm lines
and standard illuminants.

Caption: CIE 1960 (u, v) chromaticity (zoomed in) showing isotherm lines for
selected temperatures along the Planckian locus and standard illuminants A, D65,
E, and F3.
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
from numpy import arange, transpose
from maths.color_conversion import xy_to_uv, xyz_to_rgb, xyy_to_xyz
from maths.plotting_series import spectrum_locus_1931_2
from maths.coloration import (
    chromaticity_outside_gamut,
    chromaticity_inside_gamut
)
from matplotlib.collections import PathCollection
from matplotlib.path import Path
from maths.color_temperature import (
    generate_temperature_series,
    isotherm_endpoints_from_temperature,
    correlated_color_temperature_from_chromaticity
)
# endregion

# region Plot Settings
INVERTED = False
SIZE = (8, 4)
FONT_SIZES = {
    'titles' : 14,
    'labels' : 12,
    'ticks' : 10,
    'legends' : 8
}
EXTENSION = 'svg'
RESOLUTION = 16
TEMPERATURES = [2000, 3000, 4000, 5000, 7000, 10000, 20000]
# endregion

# region Constants
"""
From https://en.wikipedia.org/wiki/Standard_illuminant
"""
ILLUMINANTS_CHROMATICITY = { # (x, y)
    r'$A$' : (0.44757, 0.40745), # Incandescent / Tungsten (~2856K)
    r'$D65$' : (0.31271, 0.32902), # Daylight (~6504K)
    r'$E$' : (1 / 3, 1 / 3), # Equal Energy (~5454K)
    r'$F3$' : (0.40910, 0.39430) # White Fluorescent (~3450K)
}
ILLUMINANTS_POSITIONS = { # (u-offset, v-offset, horizontal-align., vertical-align.)
    r'$A$' : (0.0, 0.0035, 'center', 'bottom'),
    r'$D65$' : (0.0, 0.0035, 'center', 'bottom'),
    r'$E$' : (0.0, -0.005, 'center', 'top'),
    r'$F3$' : (0.0, 0.0035, 'center', 'bottom')
}
# endregion

# region Initialize Figure
figure = Figure(
    name = 'figure_22_isotherm_lines_zoom{0}'.format(
        '_inverted' if INVERTED else ''
    ),
    size = SIZE,
    inverted = INVERTED
)
figure.set_fonts(**FONT_SIZES)
panel = figure.add_panel(
    name = 'main',
    title = '',
    x_label = r'$u$',
    x_lim = (0.075, 0.525),
    x_ticks = arange(0.1, 0.51, 0.05),
    x_margin = 0.0,
    y_label = r'$v$',
    y_lim = (0.2125, 0.4375),
    y_ticks = arange(0.225, 0.426, 0.025),
    y_margin = 0.0
)
panel.set_aspect(
    aspect = 'equal', # Make horizontal and vertical axes the same scale
    adjustable = 'box' # Change the plot area aspect ratio to achieve this
)
# endregion

# region Reference Lines
panel.plot(
    *transpose(list(xy_to_uv(x, y) for x, y in [(0.0, 1.0), (1.0, 0.0)])),
    linestyle = ':',
    color = figure.grey_level(0.75),
    zorder = 1
)
panel.plot(
    *transpose(
        list(
            xy_to_uv(datum['x'], datum['y'])
            for datum in spectrum_locus_1931_2
        )
    ),
    color = figure.grey_level(0.5),
    zorder = 2
)
panel.plot(
    *transpose(
        [
            xy_to_uv(spectrum_locus_1931_2[0]['x'], spectrum_locus_1931_2[0]['y']),
            xy_to_uv(spectrum_locus_1931_2[-1]['x'], spectrum_locus_1931_2[-1]['y'])
        ]
    ),
    color = figure.grey_level(0.5),
    linestyle = ':',
    zorder = 2
)
# endregion

# region Color Fill
paths, colors = chromaticity_outside_gamut(
    RESOLUTION * 6
)
panel.add_collection(
    PathCollection(
        list(
            Path(
                list(
                    xy_to_uv(*coordinate)
                    for coordinate in path.vertices
                )
            )
            for path in paths
        ),
        facecolors = colors,
        edgecolors = colors,
        linewidth = 0,
        zorder = 0
    )
)
paths, colors = chromaticity_inside_gamut(
    RESOLUTION
)
panel.add_collection(
    PathCollection(
        list(
            Path(
                list(
                    xy_to_uv(*coordinate)
                    for coordinate in path.vertices
                )
            )
            for path in paths
        ),
        facecolors = colors,
        edgecolors = colors,
        linewidth = 0,
        zorder = 1
    )
)
# endregion

# region Planckian Locus
pl_temperatures, pl_chromaticities = generate_temperature_series()
panel.plot(
    *transpose(
        list(
            xy_to_uv(*chromaticity)
            for chromaticity in pl_chromaticities
        )
    ),
    solid_capstyle = 'round',
    color = 3 * [0.25],
    zorder = 3
)
panel.annotate(
    text = r'$\infty$',
    xy = xy_to_uv(
        pl_chromaticities[-1][0] - 0.005,
        pl_chromaticities[-1][1] - 0.005
    ),
    xycoords = 'data',
    horizontalalignment = 'center',
    verticalalignment = 'top',
    fontsize = figure.font_sizes['legends'],
    color = 3 * [0.25],
    zorder = 3
)
# endregion

# region Isotherm Lines
for temperature in TEMPERATURES:
    endpoints = isotherm_endpoints_from_temperature(temperature)
    panel.plot(
        *transpose(endpoints),
        solid_capstyle = 'round',
        color = 3 * [0.25],
        zorder = 4
    )
    panel.annotate(
        text = '{0:,}{1}'.format(temperature, r'$K$'),
        xy = (
            endpoints[1 if temperature < 3500 else 0][0]
            + (0.0 if temperature < 3500 else -0.001),
            endpoints[1 if temperature < 3500 else 0][1]
            + (-0.001 if temperature < 3500 else 0.0)
        ),
        xycoords = 'data',
        horizontalalignment = 'center' if temperature < 3500 else 'right',
        verticalalignment = 'top' if temperature < 3500 else 'center',
        fontsize = figure.font_sizes['legends'],
        color = 3 * [0.25],
        zorder = 5
    )
# endregion

# region Standard Illuminants
legend_handles = list()
for illuminant_name, illuminant_chromaticity in ILLUMINANTS_CHROMATICITY.items():
    color = xyz_to_rgb(
        *xyy_to_xyz(
            *illuminant_chromaticity,
            0.05 # arbitrarily low
        )
    )
    color = list(value / max(color) for value in color) # saturate
    legend_handles.append(
        panel.plot(
            *xy_to_uv(*illuminant_chromaticity),
            linestyle = 'none',
            marker = 'o',
            markersize = 8,
            markeredgecolor = 3 * [0],
            markerfacecolor = color,
            zorder = 5
        )[0]
    )
    panel.annotate(
        text = illuminant_name,
        xy = (
            xy_to_uv(*illuminant_chromaticity)[0]
            + ILLUMINANTS_POSITIONS[illuminant_name][0],
            xy_to_uv(*illuminant_chromaticity)[1]
            + ILLUMINANTS_POSITIONS[illuminant_name][1]
        ),
        xycoords = 'data',
        horizontalalignment = ILLUMINANTS_POSITIONS[illuminant_name][2],
        verticalalignment = ILLUMINANTS_POSITIONS[illuminant_name][3],
        fontsize = figure.font_sizes['legends'],
        color = 3 * [0],
        zorder = 6
    )
panel.legend(
    legend_handles,
    list(
        'Illuminant {0}: {1}{2:,}{3}'.format(
            illuminant_name,
            r'$\approx$',
            correlated_color_temperature_from_chromaticity(
                *xy_to_uv(*illuminant_chromaticity)
            )[0],
            r'$K$'
        )
        for illuminant_name, illuminant_chromaticity in ILLUMINANTS_CHROMATICITY.items()
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
