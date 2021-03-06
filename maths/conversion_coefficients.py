"""
Coefficients for linear transformations and corresponding name tuplets for
labelling.  All coefficient variable names appended with _10 or _2 to indicate
a 10- or 2-degree stimulus, respectively.  The 10-degree coefficients are
generally used in derivations from experimental data, through cone fundamentals
to color matching functions.  The 2-degree coefficients are generally used for
coloring figures and generating color-blind stimuli or filtering images to
simulate color blindness (i.e. working with images).
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
    if 'maths' not in folders:
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
from numpy.linalg import inv
# endregion

# region Names
COLOR_NAMES = ('Red', 'Green', 'Blue') # for experimental or display primaries
CONE_NAMES = ('Long', 'Medium', 'Short') # for cone fundamentals and color-blindness
TRISTIMULUS_NAMES = ('X', 'Y', 'Z') # for color matching functions
EXPERIMENT_PRIMARIES = [15500, 19000, 22500] # Wave-numbers in cm^-1
# endregion

# region Coefficients

# region Between Experimental Primaries (RGB) and Cone Fundamentals (LMS)
"""
10-Degree Cone Fundamentals Conversion Coefficients detailed here:
http://www.cvrl.org/database/text/cones/ss10.htm
S_G/S_B is taken from Stockman, Sharpe & Fach (1999)
PDF avaiable here:
https://www.sciencedirect.com/science/article/pii/S0042698998002259
Remaining coefficients taken from Stockman & Sharpe (2000)
PDF available here:
https://www.sciencedirect.com/science/article/pii/S0042698900000213
These coefficients produce, l-, m-, and s-cone sensitivities that are
arbitrarily scaled to one another, requiring a subsequent normalization step.
"""
RGB_TO_UNSCALED_LMS_10 = (
    (2.846201, 11.092490, 1.000000), # L_R/L_B, L_G/L_B, L_B/L_B (= 1.0)
    (0.168926, 8.265895, 1.000000), # M_R/M_B, M_G/M_B, M_B/M_B (= 1.0)
    (0.000000, 0.010600, 1.000000) # S_R/S_B (= 0.0), S_G/S_B, S_B/S_B (= 1.0)
)
UNSCALED_LMS_TO_RGB_10 = inv(RGB_TO_UNSCALED_LMS_10)

"""
After quadratic spline interpolation in 1 nm steps, scaling constants were
applied to give each cone fundamental a maximum value of 1.0.
"""
RGB_TO_LMS_10 = (
    (0.191904, 0.747907, 0.067425), # L_R, L_G, L_B
    (0.019201, 0.939552, 0.113666), # M_R, M_G, M_B
    (0.000000, 0.010589, 0.998992) # S_R, S_G, S_B
)
LMS_TO_RGB_10 = inv(RGB_TO_LMS_10)
# endregion

# region Between Cone Fundamentals (LMS) and Color Matching Functions (XYZ)
"""
10-Degree Color Matching Function Conversion Coefficients detailed here:
http://www.cvrl.org/database/text/cienewxyz/cie2012xyz10.htm
Y_L and Y_M taken from Sharpe et al (2011)
PDF available here:
http://www.cvrl.org/people/Stockman/pubs/2011%20Vstar%20correction%20SSJJ.pdf
Z_S simply scales the s-cone cone fundamental to have the same integral (1.0) as
the Y color matching function; said coefficient is in Stockman, Sharpe & Fach (1999)
The X coefficients are credited to Jan Henrik Wold but there is no citation given.
"""
LMS_TO_XYZ_10 = (
    (1.939864, -1.346644, 0.430449), # X_L, X_M, X_S
    (0.692839, 0.349676, 0.000000), # Y_L, Y_M, Y_S
    (0.000000, 0.000000, 2.146879) # Z_L, Z_M, Z_S
)
XYZ_TO_LMS_10 = inv(LMS_TO_XYZ_10)

"""
2-Degree Color Matching Function Conversion Coefficients detailed here:
http://www.cvrl.org/database/text/cones/sp.htm
Judd (1951) and then Vos (1978) made revisions to CIE 1931 2-Degree CMFs
Smith & Pokorny (1975) and then Wyszecki & Stiles (1982) modified the cone
fundamentals accordingly
"""
XYZ_TO_LMS_2 = (
    (0.15514, 0.54312, -0.03286), # L_X, L_Y, L_Z
    (-0.15514, 0.45684, 0.03286), # M_X, M_Y, M_Z
    (0.00000, 0.00000, 0.00801) # S_X, S_Y, S_Z
)
LMS_TO_XYZ_2 = inv(XYZ_TO_LMS_2)
# endregion

# region Between Color Matching Functions (XYZ) and Display Colors (RGB)
"""
Linear transformation coefficients for sRGB to CIE 1931 2-Degree tristimulus
values taken from:
https://en.wikipedia.org/wiki/SRGB
(Optional gamma correction is handled within the associated conversion function)
"""
SRGB_TO_XYZ_2 = (
    (0.4124, 0.3576, 0.1805), # X_R, X_G, X_B
    (0.2126, 0.7152, 0.0722), # Y_R, Y_G, Y_B
    (0.0193, 0.1192, 0.9505) # Z_R, Z_G, Z_B
)
XYZ_TO_SRGB_2 = inv(SRGB_TO_XYZ_2)

"""
Primaries derived from measured spectra from a CRT display
"""
RGB_TO_XYZ_CRT_10 = ( # Not a CIE standard, but estimated using 10-degree CMFs
    (0.0455, 0.0369, 0.0282), # X_R, X_G, X_B
    (0.0256, 0.0708, 0.0184), # Y_R, Y_G, Y_B
    (0.0023, 0.0106, 0.1484) # Z_R, Z_G, Z_B
)
XYZ_TO_RGB_CRT_10 = inv(RGB_TO_XYZ_CRT_10)

"""
Custom primaries designed to maximize the area of the gamut triangle inside the
CIE 1931 2-degree spectrum locus while maintaining D65 white and hue angles
(around white) for red, yellow, cyan, and blue (but not green or pink)
"""
RGB_TO_XYZ_CUSTOM_INTERIOR = ( # Not a CIE standard, no stimulus size indication
    (0.7365, 0.0435, 0.1705), # X_R, X_G, X_B
    (0.3654, 0.5821, 0.0525), # Y_R, Y_G, Y_B
    (0.0058, 0.0801, 1.0032) # Z_R, Z_G, Z_B
)
XYZ_TO_RGB_CUSTOM_INTERIOR = inv(RGB_TO_XYZ_CUSTOM_INTERIOR)

"""
Custom primaries designed to tightly enclose the CIE 1931 2-degree spectrum
while maintaining D65 white and hue angles (around white) for red, yellow, cyan,
and blue (but not green or pink)
"""
RGB_TO_XYZ_CUSTOM_EXTERIOR = ( # Not a CIE standard, no stimulus size indication
    (0.8812, -0.0405, 0.1097), # X_R, X_G, X_B
    (0.3247, 0.7334, -0.0581), # Y_R, Y_G, Y_B
    (-0.2237, 0.0807, 1.2320) # Z_R, Z_G, Z_B
)
XYZ_TO_RGB_CUSTOM_EXTERIOR = inv(RGB_TO_XYZ_CUSTOM_EXTERIOR)
# endregion

# endregion
