"""
Generates a color-blind stimulus image composed of randomly placed, sized, and
colored circles.  The (partially) hidden figure is a C shape pointing up, right,
down, or left.  The chromaticity of each circle is randomly chosen from either
side of a linear distribution - background circle chromaticities are taken from
one side and foreground (hidden figure) circle chromaticities are taken from the
other.  Luminance is randomized to prevent luminance cues being used to find the
figure.
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

# region Imports
from numpy import linspace, arctan2, pi, ptp, cos, sin, transpose
from numpy.random import rand
from pprint import pprint
from maths.rgb_cie_conversions import (
    rgb_to_chromoluminance,
    chromoluminance_to_rgb
)
from maths.color_blindness import intersection_two_segments
from figure.figure import Figure
from matplotlib.spines import Spine
# endregion

# region Settings
FIELD_RADIUS = 1.0
INITIAL_COUNT = 2 ** 14
SIZES = list(linspace(0.04, 0.01, 8) * FIELD_RADIUS)
GAP_SIZE = 0.01
STIMULUS_GAP_DIRECTIONS = {
    'Up' : pi / 2,
    'Right' : 0.0,
    'Down' : -pi / 2,
    'Left' : pi
}
STIMULUS_GAP_NAME = 'Left'
STIMULUS_GAP_DIRECTION = STIMULUS_GAP_DIRECTIONS[STIMULUS_GAP_NAME]
STIMULUS_GAP_WIDTH = pi / 6 # Radians
MIDDLE_COLORS = {
    'Grey' : (0.5, 0.5, 0.5),
    'Yellow' : (0.5, 0.5, 0.25),
    'Cyan' : (0.25, 0.5, 0.5),
    'Pink' : (0.5, 0.25, 0.5)
}
MIDDLE_COLOR_NAME = 'Grey'
MIDDLE_COLOR = MIDDLE_COLORS[MIDDLE_COLOR_NAME]
CONE_TYPE = 'S'
STIMULUS_CHROMATIC_SIGN = +1 # +/-1, will flip colors of foreground and background
CHROMATIC_DISTANCE_PROPORTION_BOUNDS = (0.0, 0.6) # Proportion of maximum distance, within gamut, on either side of distribution
MAXIMUM_ALLOWED_LUMINANCE = 0.4
LUMINANCE_SATURATION_PROPORTION_BOUNDS = (0.75, 0.95) # Proportion (of saturation) range for luminance variation
FIGURE_BACKGROUNDS = {
    'Black' : (0, 0, 0),
    'White' : (1, 1, 1),
    'Mean' : None # Estimated later
}
FIGURE_BACKGROUND_NAME = 'Mean'
FIGURE_TITLE = 'Color-Blind Stimulus - {0}-Cone Variation around {1} pointing {2} on {3}'.format(
    CONE_TYPE,
    MIDDLE_COLOR_NAME,
    STIMULUS_GAP_NAME,
    FIGURE_BACKGROUND_NAME
)
FIGURE_SIZE = (9, 9)
EXTENSION = 'png'
# endregion

# region Constants
COPUNCTAL_POINTS = {
    'L' : (0.746, 0.254),
    'M' : (1.400, -0.400),
    'S' : (0.175, 0.000)
}
# endregion

# region Determine Properties of Circles

# region Generate Random (possibly overlapping) Positions
positions = list( # Positions within square field
    (
        float(-FIELD_RADIUS + 2.0 * rand() * FIELD_RADIUS),
        float(-FIELD_RADIUS + 2.0 * rand() * FIELD_RADIUS)
    )
    for index in range(INITIAL_COUNT)
) # (x, y)
positions = list(
    (
        *position,
        (position[0] ** 2.0 + position[1] ** 2.0) ** 0.5,
        arctan2(position[1], position[0])
    )
    for position in positions
) # (x, y, distance, angle)
positions = list( # Using distance discard circles outside circular field area
    position
    for position in positions
    if position[2] <= FIELD_RADIUS
) # (x, y, distance, angle)
# endregion

# region Place Circles in Field
counts = list()
circles = list()
for size in SIZES:
    to_pop = list()
    for index, position in enumerate(positions):

        # Deny if Crosses Outer Border
        if position[2] + size > FIELD_RADIUS: continue

        # Deny if Stradles Stimulus Borders
        if (
            position[2] - size <= (1 / 3) * FIELD_RADIUS
            and position[2] + size >= (1 / 3) * FIELD_RADIUS
        ): continue
        if (
            position[2] - size <= (2 / 3) * FIELD_RADIUS
            and position[2] + size >= (2 / 3) * FIELD_RADIUS
        ): continue

        # Place
        if len(circles) == 0:
            circles.append(
                (
                    *position,
                    size
                )
            ) # (x, y, distance, angle, size)
            to_pop.append(index)
        else:
            place = True
            for circle in circles:
                if (
                    (position[0] - circle[0]) ** 2.0
                    + (position[1] - circle[1]) ** 2.0
                ) ** 0.5 < (
                    size
                    + circle[4]
                    + GAP_SIZE
                ):
                    place = False
                    break
            if place:
                circles.append(
                    (
                        *position,
                        size
                    )
                ) # (x, y, distance, angle, size)
                to_pop.append(index)
    if len(to_pop) > 0:
        for index in reversed(to_pop):
            positions.pop(index)
    counts.append((size, len(to_pop)))
print('\nCircle count by size:'); pprint(counts)

# endregion

# region Determine Colors

# Determine Chromaticity Distribution
middle_chromaticity = rgb_to_chromoluminance(
    *MIDDLE_COLOR,
    gamma_correct = False
)
middle_polar = ( # from selected copunctal point
    arctan2(
        middle_chromaticity[1] - COPUNCTAL_POINTS[CONE_TYPE][1],
        middle_chromaticity[0] - COPUNCTAL_POINTS[CONE_TYPE][0]
    ),
    (
        (middle_chromaticity[0] - COPUNCTAL_POINTS[CONE_TYPE][0]) ** 2.0
        + (middle_chromaticity[1] - COPUNCTAL_POINTS[CONE_TYPE][1]) ** 2.0
    ) ** 0.5
) # (angle, distance)
gamut_segments = [
    (
        rgb_to_chromoluminance(1.0, 0.0, 0.0)[0:2], # Red
        rgb_to_chromoluminance(0.0, 1.0, 0.0)[0:2] # to Green
    ),
    (
        rgb_to_chromoluminance(0.0, 1.0, 0.0)[0:2], # Green
        rgb_to_chromoluminance(0.0, 0.0, 1.0)[0:2] # to Blue
    ),
    (
        rgb_to_chromoluminance(0.0, 0.0, 1.0)[0:2], # Blue
        rgb_to_chromoluminance(1.0, 0.0, 0.0)[0:2] # to Red
    )
]
confusion_line_intersections = (
    intersection_two_segments(
        COPUNCTAL_POINTS[CONE_TYPE],
        middle_chromaticity[0:2],
        *gamut_segments[2]
    ),
    intersection_two_segments(
        COPUNCTAL_POINTS[CONE_TYPE],
        middle_chromaticity[0:2],
        *gamut_segments[0 if CONE_TYPE == 'S' else 1]
    )
)
maximum_distance = min(
    list(
        (
            (middle_chromaticity[0] - confusion_line_intersection[0]) ** 2.0
            + (middle_chromaticity[1] - confusion_line_intersection[1]) ** 2.0
        ) ** 0.5
        for confusion_line_intersection in confusion_line_intersections
    )
)

# Determine whether Circle is Foreground or Background
circles = list(
    (
        *circle,
        (
            (1 / 3) * FIELD_RADIUS < circle[2] < (2 / 3) * FIELD_RADIUS
            and (
                (
                    circle[3] < STIMULUS_GAP_DIRECTION - STIMULUS_GAP_WIDTH
                    or circle[3] > STIMULUS_GAP_DIRECTION + STIMULUS_GAP_WIDTH
                ) if STIMULUS_GAP_DIRECTION != pi else (
                    circle[3] < pi - STIMULUS_GAP_WIDTH
                    and circle[3] > -pi + STIMULUS_GAP_WIDTH
                )
            )
        )
    )
    for circle in circles
) # (x, y, distance, angle, size, in-stimulus)

# Determine Maximum Luminance
chromaticity_bounds = (
    (
        COPUNCTAL_POINTS[CONE_TYPE][0]
        + (
            middle_polar[1]
            - maximum_distance
            * CHROMATIC_DISTANCE_PROPORTION_BOUNDS[1]
        )
        * cos(middle_polar[0]),
        COPUNCTAL_POINTS[CONE_TYPE][1]
        + (
            middle_polar[1]
            - maximum_distance
            * CHROMATIC_DISTANCE_PROPORTION_BOUNDS[1]
        )
        * sin(middle_polar[0])
    ),
    (
        COPUNCTAL_POINTS[CONE_TYPE][0]
        + (
            middle_polar[1]
            + maximum_distance
            * CHROMATIC_DISTANCE_PROPORTION_BOUNDS[1]
        )
        * cos(middle_polar[0]),
        COPUNCTAL_POINTS[CONE_TYPE][1]
        + (
            middle_polar[1]
            + maximum_distance
            * CHROMATIC_DISTANCE_PROPORTION_BOUNDS[1]
        )
        * sin(middle_polar[0])
    )
)
color_bounds = tuple(
    chromoluminance_to_rgb(
        *chromaticity_bound,
        0.05, # Arbitrarily low
        gamma_correct = False
    )
    for chromaticity_bound in chromaticity_bounds
)
saturated_color_bounds = tuple(
    tuple(value / max(color_bound) for value in color_bound)
    for color_bound in color_bounds
)
luminance_bounds = list(
    rgb_to_chromoluminance(
        *saturated_color_bound,
        gamma_correct = False
    )[2]
    for saturated_color_bound in saturated_color_bounds
)
maximum_luminance = min(luminance_bounds + [MAXIMUM_ALLOWED_LUMINANCE])
print(
    '\nMaximum Luminance: {0:0.3f} / ({1:0.3f})'.format(
        maximum_luminance,
        MAXIMUM_ALLOWED_LUMINANCE
    )
)

# Set Colors
FIGURE_BACKGROUNDS['Mean'] = chromoluminance_to_rgb(
    *middle_chromaticity[0:2],
    maximum_luminance * (
        sum(LUMINANCE_SATURATION_PROPORTION_BOUNDS) / 2.0
    ),
    gamma_correct = False
)
circle_colors = list()
for circle in circles:
    distance = (
        middle_polar[1]
        + (STIMULUS_CHROMATIC_SIGN if circle[5] else -STIMULUS_CHROMATIC_SIGN)
        * maximum_distance
        * (
            CHROMATIC_DISTANCE_PROPORTION_BOUNDS[0]
            + rand() * ptp(CHROMATIC_DISTANCE_PROPORTION_BOUNDS)
        )
    )
    chromaticity = (
        COPUNCTAL_POINTS[CONE_TYPE][0] + distance * cos(middle_polar[0]),
        COPUNCTAL_POINTS[CONE_TYPE][1] + distance * sin(middle_polar[0])
    )
    color = chromoluminance_to_rgb(
        *chromaticity,
        maximum_luminance * (
            LUMINANCE_SATURATION_PROPORTION_BOUNDS[0]
            + rand() * ptp(LUMINANCE_SATURATION_PROPORTION_BOUNDS)
        ),
        gamma_correct = False
    )
    circle_colors.append(color)

# endregion

# endregion

# region Build and Save Image

# region Initialize Figure
figure = Figure(
    name = FIGURE_TITLE,
    size = FIGURE_SIZE,
    figure_color = FIGURE_BACKGROUNDS[FIGURE_BACKGROUND_NAME]
)
panel = figure.add_panel(
    name = 'main',
    title = '',
    panel_color = FIGURE_BACKGROUNDS[FIGURE_BACKGROUND_NAME],
    x_label = '',
    x_ticks = [],
    x_lim = (-1.05 * FIELD_RADIUS, 1.05 * FIELD_RADIUS),
    y_label = '',
    y_ticks = [],
    y_lim = (-1.05 * FIELD_RADIUS, 1.05 * FIELD_RADIUS)
)
for child in panel.get_children(): # Remove border
    if isinstance(child, Spine):
        child.set_color(FIGURE_BACKGROUNDS[FIGURE_BACKGROUND_NAME])
# endregion

# region Fill Circles
angles = linspace(-pi, pi, 128)
for index, circle in enumerate(circles):
    panel.fill(
        *transpose(
            list(
                (
                    circle[0] + circle[4] * cos(angle),
                    circle[1] + circle[4] * sin(angle)
                )
                for angle in angles
            )
        ),
        color = circle_colors[index],
        edgecolor = 'none'
    )
# endregion

# region Save
figure.update(
    buffer = 0
)
figure.save(
    path = 'images',
    name = figure.name,
    extension = EXTENSION
)
figure.close()
# endregion

# endregion
