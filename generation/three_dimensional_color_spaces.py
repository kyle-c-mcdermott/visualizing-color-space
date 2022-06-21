"""
Plotting RGB and Chromoluminance three-dimensional color spaces with saturation
surfaces.

Figure Cpations:
12 - Display red, green, and blue space plotted in three dimensions.  The left
panel shows the surface colors where at least one value is equal to zero, while
the right panel shows the surface colors where at least one value is equal to
one.  The entire display gamut is contained within the cube formed by these six
sides.  Note that red, green, and blue appear as three vertices, the
intermediate colors yellow, cyan, and pink are three more vertices, and the
final two vertices are black and white.
13 - Display red, green, and blue saturation surfaces converted to CIE 1931
2-Degree Chromoluminance ((x, y) chromaticity and Y for luminance).  The left
panel shows the display surface colors where at least one value is equal to
zero, while the right panel shows the display surface colors where at least one
value is equal to one.  Lines trace the missing edges corresponding to those in
the opposite panel, and reference lines on the Y = 0 plane show the spectrum
locus and triangular boundary of the display chromaticity gamut.
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
    'legends' : 12
}
RESOLUTION = 64
EXTENSION = 'svg'
# endregion

# region Imports
from csv import DictReader
from maths.rgb_cie_conversions import rgb_to_chromoluminance
from figure.figure import Figure
from maths.saturated_color_paths import three_dimensional_surface
from numpy import array, linspace, transpose
# endregion

# region Load in Data
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

# region Figure 12 - Saturation Surfaces in Display RGB Space

# region Initialize Figure
figure = Figure(
    name = 'Saturation Surfaces in RGB{0}'.format(
        ' (inverted)' if INVERTED else ''
    ),
    size = SIZE,
    inverted = INVERTED
)
figure.set_fonts(**FONT_SIZES)
low_panel = figure.add_panel(
    name = 'low',
    title = 'Low Saturation Surfaces in Display RGB\n(at least one value equals zero)',
    position = (0.025, 0, 0.475, 1),
    three_dimensional = True,
    x_label = 'Red',
    x_lim = (-0.05, 1.05),
    y_label = 'Green',
    y_lim = (-0.05, 1.05),
    z_label = 'Blue',
    z_lim = (-0.05, 1.05),
)
high_panel = figure.add_panel(
    name = 'high',
    title = 'High Saturation Surfaces in Display RGB\n(at least one value equals one)',
    position = (0.5, 0, 0.475, 1),
    three_dimensional = True,
    x_label = 'Red',
    x_lim = (-0.05, 1.05),
    y_label = 'Green',
    y_lim = (-0.05, 1.05),
    z_label = 'Blue',
    z_lim = (-0.05, 1.05),
)
for panel_name in figure.panels.keys():
    figure.change_panel_orientation(
        panel_name,
        vertical_sign = +1,
        left_axis = '+y'
    )
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

# region Plot Surfaces
for color_index in range(3):
    coordinates, colors = three_dimensional_surface(
        color_index,
        0,
        color_value = 0, # Low
        resolution = RESOLUTION
    )
    low_panel.plot_surface(
        X = coordinates[0],
        Y = coordinates[1],
        Z = array(coordinates[2]), # Only necessary for Z for some reason
        facecolors = colors,
        shade = False
    )
    coordinates, colors = three_dimensional_surface(
        color_index,
        0,
        color_value = 1, # High
        resolution = RESOLUTION
    )
    high_panel.plot_surface(
        X = coordinates[0],
        Y = coordinates[1],
        Z = array(coordinates[2]), # Only necessary for Z for some reason
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
# endregion

# endregion

# region Figure 13 - Saturation Surfaces in Chromoluminance Space

# region Initialize Figure
figure = Figure(
    name = 'Saturation Surfaces in Chromoluminance{0}'.format(
        ' (inverted)' if INVERTED else ''
    ),
    size = SIZE,
    inverted = INVERTED
)
figure.set_fonts(**FONT_SIZES)
low_panel = figure.add_panel(
    name = 'low',
    title = 'Low Saturation Surfaces in Chromoluminance\n(at least one RGB value equals zero)',
    position = (0.025, 0, 0.475, 1),
    three_dimensional = True,
    x_label = 'x',
    x_lim = (-0.05, 1.05),
    y_label = 'y',
    y_lim = (-0.05, 1.05),
    z_label = 'Y',
    z_lim = (-0.05, 1.05)
)
high_panel = figure.add_panel(
    name = 'high',
    title = 'High Saturation Surfaces in Chromoluminance\n(at least one RGB value equals one)',
    position = (0.5, 0, 0.475, 1),
    three_dimensional = True,
    x_label = 'x',
    x_lim = (-0.05, 1.05),
    y_label = 'y',
    y_lim = (-0.05, 1.05),
    z_label = 'Y',
    z_lim = (-0.05, 1.05)
)
for panel_name in figure.panels.keys():
    figure.change_panel_orientation(
        panel_name,
        vertical_sign = +1,
        left_axis = '-y'
    )
    figure.change_panes(
        panel_name,
        x_pane_color = figure.grey_level(0.95),
        x_grid_color = figure.grey_level(0.75),
        y_pane_color = figure.grey_level(0.95),
        y_grid_color = figure.grey_level(0.75),
        z_pane_color = figure.grey_level(0.95),
        z_grid_color = figure.grey_level(0.75)
    )
low_panel.view_init(0, -135)
# endregion

# region Reference
for panel in figure.panels.values():
    panel.plot3D(
        list(
            spectrum_locus[index]['x']
            for index in list(range(len(spectrum_locus))) + [0]
        ),
        list(
            spectrum_locus[index]['y']
            for index in list(range(len(spectrum_locus))) + [0]
        ), # z defaults to zeros
        color = figure.grey_level(0.5),
        linewidth = 2,
        zorder = 0
    )
    panel.plot3D(
        *transpose(srgb_primary_chromaticities), # z defaults to zeros
        color = figure.grey_level(0.5),
        zorder = 0
    )
# endregion

# region Plot Surfaces
for color_index in range(3):
    coordinates, colors = three_dimensional_surface(
        color_index,
        1,
        color_value = 0,
        resolution = RESOLUTION
    )
    low_panel.plot_surface(
        X = coordinates[0],
        Y = coordinates[1],
        Z = array(coordinates[2]),
        facecolors = colors,
        shade = False,
        zorder = 1
    )
    coordinates, colors = three_dimensional_surface(
        color_index,
        1,
        color_value = 1,
        resolution = RESOLUTION
    )
    high_panel.plot_surface(
        X = coordinates[0],
        Y = coordinates[1],
        Z = array(coordinates[2]),
        facecolors = colors,
        shade = False,
        zorder = 1
    )
# endregion

# region Plot Missing Edges
for color_index in range(3):
    colors = 3 * [1.0]
    xs = list(); ys = list(); zs = list()
    for value in linspace(0, 1, RESOLUTION):
        colors[color_index] = value
        x, y, Y = rgb_to_chromoluminance(*colors)
        xs.append(x); ys.append(y); zs.append(Y)
    low_panel.plot3D(
        xs,
        ys,
        zs,
        color = figure.grey_level(0.25),
        zorder = 2 # Doesn't seem to matter so much in 3D
    )
    colors = 3 * [0.0]
    xs = list(); ys = list(); zs = list()
    for value in linspace(0, 1, RESOLUTION):
        colors[color_index] = value
        x, y, Y = rgb_to_chromoluminance(*colors)
        xs.append(x); ys.append(y); zs.append(Y)
    high_panel.plot3D(
        xs,
        ys,
        zs,
        color = figure.grey_level(0.25),
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
# endregion

# endregion
