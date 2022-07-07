"""
Plot saturation surfaces in three-dimensions (with gamma-correction).

Caption: Saturated surfaces transformed into (x,y,Y) chromoluminance space.  In
the left panel, all colors contain at least one 0.0 for red, green, and/or blue
(before transformation).  In the right panel, all colors contain at least one
1.0 for red, green, and/or blue (before transformation).
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
from maths.plotting_series import (
    spectrum_locus_1931_2,
    gamut_triangle_vertices_srgb
)
from numpy import transpose, array
from maths.conversion_coefficients import COLOR_NAMES
from maths.coloration import three_dimensional_surface
# endregion

# region Plot Settings
INVERTED = False
SIZE = (8, 3.5)
FONT_SIZES = {
    'titles' : 14,
    'labels' : 12,
    'ticks' : 10,
    'legends' : 8
}
EXTENSION = 'svg'
RESOLUTION = 16
# endregion

# region Initialize Figure
figure = Figure(
    name = 'figure_13_3d_chromoluminance{0}'.format(
        '_inverted' if INVERTED else ''
    ),
    size = SIZE,
    inverted = INVERTED
)
figure.set_fonts(**FONT_SIZES)
low_panel = figure.add_panel(
    name = 'low',
    title = '',
    position = (0.06, 0, 0.44, 1),
    three_dimensional = True,
    x_label = r'$x$',
    x_lim = (-0.05, 1.05),
    y_label = r'$y$',
    y_lim = (-0.05, 1.05),
    z_label = r'$Y$',
    z_lim = (-0.05, 1.05)
)
low_panel.view_init(0, -135)
high_panel = figure.add_panel(
    name = 'high',
    title = '',
    position = (0.55, 0, 0.44, 1),
    three_dimensional = True,
    x_label = r'$x$',
    x_lim = (-0.05, 1.05),
    y_label = r'$y$',
    y_lim = (-0.05, 1.05),
    z_label = r'$Y$',
    z_lim = (-0.05, 1.05)
)
figure.change_panel_orientation(
    'high',
    vertical_sign = +1,
    left_axis = '-y'
)
for panel_name in figure.panels.keys():
    figure.change_panes(
        panel_name,
        x_pane_color = figure.grey_level(0.95),
        x_grid_color = figure.grey_level(0.75),
        y_pane_color = figure.grey_level(0.95),
        y_grid_color = figure.grey_level(0.75),
        z_pane_color = figure.grey_level(0.95),
        z_grid_color = figure.grey_level(0.75)
    )
# endregion

# region Reference Lines
for panel in figure.panels.values():
    panel.plot( # Defaults to z (or Y) = 0 plane
        list(datum['x'] for datum in spectrum_locus_1931_2),
        list(datum['y'] for datum in spectrum_locus_1931_2),
        color = figure.grey_level(0.5)
    )
    panel.plot(
        [spectrum_locus_1931_2[0]['x'], spectrum_locus_1931_2[-1]['x']],
        [spectrum_locus_1931_2[0]['y'], spectrum_locus_1931_2[-1]['y']],
        linestyle = ':',
        color = figure.grey_level(0.5)
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
        color = figure.grey_level(0.5)
    )
# endregion

# region Fill Colors
for color_name in COLOR_NAMES:
    for color_value, panel_name in [(0.0, 'low'), (1.0, 'high')]:
        coordinates, colors = three_dimensional_surface(
            RESOLUTION,
            color_name,
            color_value,
            apply_gamma_correction = True
        )
        figure.panels[panel_name].plot_surface(
            X = coordinates[0],
            Y = coordinates[1],
            Z = array(coordinates[2]),
            facecolors = colors,
            shade = False
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
