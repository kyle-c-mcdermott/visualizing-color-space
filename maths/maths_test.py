"""
Maths Package Unit Test

Can be run as script, or with unittest from console with:
python -m unittest maths_test
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
from unittest import TestCase, main
from maths.functions import (
    intersection_of_two_segments,
    conversion_matrix
)
from maths.color_conversion import (
    rgb_to_lms,
    lms_to_rgb,
    lms_to_xyz,
    xyz_to_lms,
    xyz_to_xyy,
    DISPLAY,
    xyy_to_xyz,
    xyz_to_rgb,
    rgb_to_xyz,
    xy_to_uv,
    uv_to_xy
)
from maths.chromaticity_conversion import (
    wavelength_to_chromaticity,
    STANDARD,
    wavelength_to_hue_angle,
    hue_angle_to_wavelength,
    chromaticity_rectangular_to_polar,
    CENTER,
    chromaticity_polar_to_rectangular
)
from numpy import pi
from maths.color_temperature import (
    tristimulus_from_spectrum,
    radiant_emitance,
    spectrum_from_temperature,
    isotherm_endpoints_from_temperature,
    correlated_color_temperature_from_chromaticity,
    generate_temperature_series
)
from maths.plotting_series import color_matching_functions_1931_2
from maths.color_blind import (
    get_unique_colors,
    filter_image
)
from PIL import Image
# endregion

# region Test
class TestMaths(TestCase):
    """Test Maths Package"""

    # region Test functions.intersection_of_two_segments
    def test_functions_intersection_of_two_segments(self):

        # Valid Arguments
        valid_a1 = (0.0, 0.0)
        valid_a2 = (1.0, 1.0)
        valid_b1 = (0.0, 1.0)
        valid_b2 = (1.0, 0.0)

        # Test a1 Assertions
        with self.assertRaises(AssertionError):
            intersection_of_two_segments(
                0, # Invalid type
                valid_a2,
                valid_b1,
                valid_b2
            )
        with self.assertRaises(AssertionError):
            intersection_of_two_segments(
                0.0, # Invalid type
                valid_a2,
                valid_b1,
                valid_b2
            )
        with self.assertRaises(AssertionError):
            intersection_of_two_segments(
                '0', # Invalid type
                valid_a2,
                valid_b1,
                valid_b2
            )
        with self.assertRaises(AssertionError):
            intersection_of_two_segments(
                (0, 1, 2), # Invalid length
                valid_a2,
                valid_b1,
                valid_b2
            )
        with self.assertRaises(AssertionError):
            intersection_of_two_segments(
                ('0', '1'), # Invalid types
                valid_a2,
                valid_b1,
                valid_b2
            )

        # Test a2 Assertions
        with self.assertRaises(AssertionError):
            intersection_of_two_segments(
                valid_a1,
                0, # Invalid type
                valid_b1,
                valid_b2
            )
        with self.assertRaises(AssertionError):
            intersection_of_two_segments(
                valid_a1,
                0.0, # Invalid type
                valid_b1,
                valid_b2
            )
        with self.assertRaises(AssertionError):
            intersection_of_two_segments(
                valid_a1,
                '0', # Invalid type
                valid_b1,
                valid_b2
            )
        with self.assertRaises(AssertionError):
            intersection_of_two_segments(
                valid_a1,
                (0, 1, 2), # Invalid length
                valid_b1,
                valid_b2
            )
        with self.assertRaises(AssertionError):
            intersection_of_two_segments(
                valid_a1,
                ('0', '1'), # Invalid types
                valid_b1,
                valid_b2
            )

        # Test b1 Assertions
        with self.assertRaises(AssertionError):
            intersection_of_two_segments(
                valid_a1,
                valid_a2,
                0, # Invalid type
                valid_b2
            )
        with self.assertRaises(AssertionError):
            intersection_of_two_segments(
                valid_a1,
                valid_a2,
                0.0, # Invalid type
                valid_b2
            )
        with self.assertRaises(AssertionError):
            intersection_of_two_segments(
                valid_a1,
                valid_a2,
                '0', # Invalid type
                valid_b2
            )
        with self.assertRaises(AssertionError):
            intersection_of_two_segments(
                valid_a1,
                valid_a2,
                (0, 1, 2), # Invalid length
                valid_b2
            )
        with self.assertRaises(AssertionError):
            intersection_of_two_segments(
                valid_a1,
                valid_a2,
                ('0', '1'), # Invalid types
                valid_b2
            )

        # Test b2 Assertions
        with self.assertRaises(AssertionError):
            intersection_of_two_segments(
                valid_a1,
                valid_a2,
                valid_b1,
                0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            intersection_of_two_segments(
                valid_a1,
                valid_a2,
                valid_b1,
                0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            intersection_of_two_segments(
                valid_a1,
                valid_a2,
                valid_b1,
                '0' # Invalid type
            )
        with self.assertRaises(AssertionError):
            intersection_of_two_segments(
                valid_a1,
                valid_a2,
                valid_b1,
                (0, 1, 2) # Invalid length
            )
        with self.assertRaises(AssertionError):
            intersection_of_two_segments(
                valid_a1,
                valid_a2,
                valid_b1,
                ('0', '1') # Invalid types
            )

        # Test Return (non-parallel)
        test_return = intersection_of_two_segments(
            valid_a1,
            valid_a2,
            valid_b1,
            valid_b2
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 2)
        for index, value in enumerate([0.5, 0.5]):
            self.assertIsInstance(test_return[index], float)
            self.assertEqual(test_return[index], value)

        # Test Return (parallel / collinear)
        test_return = intersection_of_two_segments(
            valid_a1,
            valid_a2,
            valid_a1,
            valid_a2
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 2)
        for index, value in enumerate([float('inf'), float('inf')]):
            self.assertIsInstance(test_return[index], float)
            self.assertEqual(test_return[index], value)

    # endregion

    # region Test functions.conversion_matrix
    def test_functions_conversion_matrix(self):

        # Valid Arguments
        valid_red_chromaticity = (0.6400, 0.3000)
        valid_green_chromaticity = (0.3000, 0.6000)
        valid_blue_chromaticity = (0.1500, 0.0600)
        valid_white_chromaticity = (0.3127, 0.3290)

        # Test red_chromaticity Assertions
        with self.assertRaises(AssertionError):
            conversion_matrix(
                0, # Invalid type
                valid_green_chromaticity,
                valid_blue_chromaticity,
                valid_white_chromaticity
            )
        with self.assertRaises(AssertionError):
            conversion_matrix(
                0.0, # Invalid type
                valid_green_chromaticity,
                valid_blue_chromaticity,
                valid_white_chromaticity
            )
        with self.assertRaises(AssertionError):
            conversion_matrix(
                '0', # Invalid type
                valid_green_chromaticity,
                valid_blue_chromaticity,
                valid_white_chromaticity
            )
        with self.assertRaises(AssertionError):
            conversion_matrix(
                (0.0, 1.0, 2.0), # Invalid length
                valid_green_chromaticity,
                valid_blue_chromaticity,
                valid_white_chromaticity
            )
        with self.assertRaises(AssertionError):
            conversion_matrix(
                ('0', '1'), # Invalid types
                valid_green_chromaticity,
                valid_blue_chromaticity,
                valid_white_chromaticity
            )
        with self.assertRaises(AssertionError):
            conversion_matrix(
                (0.3, 0.0), # Invalid value
                valid_green_chromaticity,
                valid_blue_chromaticity,
                valid_white_chromaticity
            )

        # Test green_chromaticity Assertions
        with self.assertRaises(AssertionError):
            conversion_matrix(
                valid_red_chromaticity,
                0, # Invalid type
                valid_blue_chromaticity,
                valid_white_chromaticity
            )
        with self.assertRaises(AssertionError):
            conversion_matrix(
                valid_red_chromaticity,
                0.0, # Invalid type
                valid_blue_chromaticity,
                valid_white_chromaticity
            )
        with self.assertRaises(AssertionError):
            conversion_matrix(
                valid_red_chromaticity,
                '0', # Invalid type
                valid_blue_chromaticity,
                valid_white_chromaticity
            )
        with self.assertRaises(AssertionError):
            conversion_matrix(
                valid_red_chromaticity,
                (0.0, 1.0, 2.0), # Invalid length
                valid_blue_chromaticity,
                valid_white_chromaticity
            )
        with self.assertRaises(AssertionError):
            conversion_matrix(
                valid_red_chromaticity,
                ('0', '1'), # Invalid types
                valid_blue_chromaticity,
                valid_white_chromaticity
            )
        with self.assertRaises(AssertionError):
            conversion_matrix(
                valid_red_chromaticity,
                (0.3, 0.0), # Invalid value
                valid_blue_chromaticity,
                valid_white_chromaticity
            )

        # Test blue_chromaticity Assertions
        with self.assertRaises(AssertionError):
            conversion_matrix(
                valid_red_chromaticity,
                valid_green_chromaticity,
                0, # Invalid type
                valid_white_chromaticity
            )
        with self.assertRaises(AssertionError):
            conversion_matrix(
                valid_red_chromaticity,
                valid_green_chromaticity,
                0.0, # Invalid type
                valid_white_chromaticity
            )
        with self.assertRaises(AssertionError):
            conversion_matrix(
                valid_red_chromaticity,
                valid_green_chromaticity,
                '0', # Invalid type
                valid_white_chromaticity
            )
        with self.assertRaises(AssertionError):
            conversion_matrix(
                valid_red_chromaticity,
                valid_green_chromaticity,
                (0.0, 1.0, 2.0), # Invalid length
                valid_white_chromaticity
            )
        with self.assertRaises(AssertionError):
            conversion_matrix(
                valid_red_chromaticity,
                valid_green_chromaticity,
                ('0', '1'), # Invalid types
                valid_white_chromaticity
            )
        with self.assertRaises(AssertionError):
            conversion_matrix(
                valid_red_chromaticity,
                valid_green_chromaticity,
                (0.3, 0.0), # Invalid value
                valid_white_chromaticity
            )

        # Test white_chromaticity Assertions
        with self.assertRaises(AssertionError):
            conversion_matrix(
                valid_red_chromaticity,
                valid_green_chromaticity,
                valid_blue_chromaticity,
                0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            conversion_matrix(
                valid_red_chromaticity,
                valid_green_chromaticity,
                valid_blue_chromaticity,
                0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            conversion_matrix(
                valid_red_chromaticity,
                valid_green_chromaticity,
                valid_blue_chromaticity,
                '0' # Invalid type
            )
        with self.assertRaises(AssertionError):
            conversion_matrix(
                valid_red_chromaticity,
                valid_green_chromaticity,
                valid_blue_chromaticity,
                (0.0, 1.0, 2.0) # Invalid length
            )
        with self.assertRaises(AssertionError):
            conversion_matrix(
                valid_red_chromaticity,
                valid_green_chromaticity,
                valid_blue_chromaticity,
                ('0', '1') # Invalid types
            )
        with self.assertRaises(AssertionError):
            conversion_matrix(
                valid_red_chromaticity,
                valid_green_chromaticity,
                valid_blue_chromaticity,
                (0.3, 0.0) # Invalid value
            )

        # Test white_luminance Assertions
        with self.assertRaises(AssertionError):
            conversion_matrix(
                valid_red_chromaticity,
                valid_green_chromaticity,
                valid_blue_chromaticity,
                valid_white_chromaticity,
                0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            conversion_matrix(
                valid_red_chromaticity,
                valid_green_chromaticity,
                valid_blue_chromaticity,
                valid_white_chromaticity,
                '0' # Invalid type
            )
        with self.assertRaises(AssertionError):
            conversion_matrix(
                valid_red_chromaticity,
                valid_green_chromaticity,
                valid_blue_chromaticity,
                valid_white_chromaticity,
                -1.0 # Invalid value
            )

        # Test Return
        test_return = conversion_matrix(
            valid_red_chromaticity,
            valid_green_chromaticity,
            valid_blue_chromaticity,
            valid_white_chromaticity
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 3)
        for index_1, values in enumerate(
            (
                (0.4042728701465506, 0.3700149183479725, 0.17616813855714844),
                (0.18950290788119561, 0.740029836695945, 0.07046725542285938),
                (0.03790058157623913, 0.12333830611599081, 0.9278188630676486)
            )
        ):
            self.assertIsInstance(test_return[index_1], tuple)
            self.assertEqual(len(test_return[index_1]), 3)
            for index_2, value in enumerate(values):
                self.assertIsInstance(test_return[index_1][index_2], float)
                self.assertAlmostEqual(test_return[index_1][index_2], value)
        test_return = conversion_matrix(
            (0.620, 0.349),
            (0.312, 0.599),
            (0.144, 0.094),
            (0.286, 0.297),
            white_luminance = 0.1148
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 3)
        for index_1, values in enumerate(
            (
                (0.04562251477687339, 0.036885130826335655, 0.028040502544939106),
                (0.025681060737304535, 0.070814722323638, 0.018304216939057472),
                (0.0022811257388436717, 0.010521720011358565, 0.1483809926336361)
            )
        ):
            self.assertIsInstance(test_return[index_1], tuple)
            self.assertEqual(len(test_return[index_1]), 3)
            for index_2, value in enumerate(values):
                self.assertIsInstance(test_return[index_1][index_2], float)
                self.assertAlmostEqual(test_return[index_1][index_2], value)

    # endregion

    # region Test color_conversion.rgb_to_lms
    def test_color_conversion_rgb_to_lms(self):

        # Valid Arguments
        valid_red = 0.5
        valid_green = 0.5
        valid_blue = 0.5

        # Test red Assertions
        with self.assertRaises(AssertionError):
            rgb_to_lms(
                '0', # Invalid type
                valid_green,
                valid_blue
            )

        # Test green Assertions
        with self.assertRaises(AssertionError):
            rgb_to_lms(
                valid_red,
                '0', # Invalid type
                valid_blue
            )

        # Test blue Assertions
        with self.assertRaises(AssertionError):
            rgb_to_lms(
                valid_red,
                valid_green,
                '0' # Invalid type
            )

        # Test normalize_fundamentals Assertions
        with self.assertRaises(AssertionError):
            rgb_to_lms(
                valid_red,
                valid_green,
                valid_blue,
                normalize_fundamentals = 0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            rgb_to_lms(
                valid_red,
                valid_green,
                valid_blue,
                normalize_fundamentals = 0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            rgb_to_lms(
                valid_red,
                valid_green,
                valid_blue,
                normalize_fundamentals = '0' # Invalid type
            )

        # Test Return
        test_return = rgb_to_lms(
            1.0,
            0.0,
            0.0
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 3)
        for index, value in enumerate([0.191888, 0.019219, 0.0]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)
        test_return = rgb_to_lms(
            1.0,
            0.0,
            0.0,
            normalize_fundamentals = False
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 3)
        for index, value in enumerate([2.846201, 0.168926, 0.0]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)

    # endregion

    # region Test color_conversion.lms_to_rgb
    def test_color_conversion_lms_to_rgb(self):

        # Valid Arguments
        valid_long = 0.5
        valid_medium = 0.5
        valid_short = 0.5

        # Test long Assertions
        with self.assertRaises(AssertionError):
            lms_to_rgb(
                0, # Invalid type
                valid_medium,
                valid_short
            )
        with self.assertRaises(AssertionError):
            lms_to_rgb(
                '0', # Invalid type
                valid_medium,
                valid_short
            )
        with self.assertRaises(AssertionError):
            lms_to_rgb(
                -0.1, # Invalid value
                valid_medium,
                valid_short
            )

        # Test medium Assertions
        with self.assertRaises(AssertionError):
            lms_to_rgb(
                valid_long,
                0, # Invalid type
                valid_short
            )
        with self.assertRaises(AssertionError):
            lms_to_rgb(
                valid_long,
                '0', # Invalid type
                valid_short
            )
        with self.assertRaises(AssertionError):
            lms_to_rgb(
                valid_long,
                -0.1, # Invalid value
                valid_short
            )

        # Test short Assertions
        with self.assertRaises(AssertionError):
            lms_to_rgb(
                valid_long,
                valid_medium,
                0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            lms_to_rgb(
                valid_long,
                valid_medium,
                '0' # Invalid type
            )
        with self.assertRaises(AssertionError):
            lms_to_rgb(
                valid_long,
                valid_medium,
                -0.1 # Invalid value
            )

        # Test normalize_fundamentals Assertions
        with self.assertRaises(AssertionError):
            lms_to_rgb(
                valid_long,
                valid_medium,
                valid_short,
                normalize_fundamentals = 0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            lms_to_rgb(
                valid_long,
                valid_medium,
                valid_short,
                normalize_fundamentals = 0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            lms_to_rgb(
                valid_long,
                valid_medium,
                valid_short,
                normalize_fundamentals = '0' # Invalid type
            )

        # Test Return
        test_return = lms_to_rgb(
            0.2,
            0.4,
            0.2
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 3)
        for index, value in enumerate([-0.6431246874633334, 0.41480164505858064, 0.1957928622122068]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)
        test_return = lms_to_rgb(
            3.5,
            3.5,
            0.5,
            normalize_fundamentals = False
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 3)
        for index, value in enumerate([-0.39214312026556863, 0.37142744974395, 0.4960628690327141]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)

    # endregion

    # region Test color_conversion.lms_to_xyz
    def test_color_conversion_lms_to_xyz(self):

        # Valid Arguments
        valid_long = 0.5
        valid_medium = 0.5
        valid_short = 0.5

        # Test long Assertions
        with self.assertRaises(AssertionError):
            lms_to_xyz(
                0, # Invalid type
                valid_medium,
                valid_short
            )
        with self.assertRaises(AssertionError):
            lms_to_xyz(
                '0', # Invalid type
                valid_medium,
                valid_short
            )
        with self.assertRaises(AssertionError):
            lms_to_xyz(
                -0.1, # Invalid value
                valid_medium,
                valid_short
            )

        # Test medium Assertions
        with self.assertRaises(AssertionError):
            lms_to_xyz(
                valid_long,
                0, # Invalid type
                valid_short
            )
        with self.assertRaises(AssertionError):
            lms_to_xyz(
                valid_long,
                '0', # Invalid type
                valid_short
            )
        with self.assertRaises(AssertionError):
            lms_to_xyz(
                valid_long,
                -0.1, # Invalid value
                valid_short
            )

        # Test short Assertions
        with self.assertRaises(AssertionError):
            lms_to_xyz(
                valid_long,
                valid_medium,
                0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            lms_to_xyz(
                valid_long,
                valid_medium,
                '0' # Invalid type
            )
        with self.assertRaises(AssertionError):
            lms_to_xyz(
                valid_long,
                valid_medium,
                -0.1 # Invalid value
            )

        # Test use_2_degree Assertions
        with self.assertRaises(AssertionError):
            lms_to_xyz(
                valid_long,
                valid_medium,
                valid_short,
                use_2_degree = 0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            lms_to_xyz(
                valid_long,
                valid_medium,
                valid_short,
                use_2_degree = 0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            lms_to_xyz(
                valid_long,
                valid_medium,
                valid_short,
                use_2_degree = '0' # Invalid type
            )

        # Test Return
        test_return = lms_to_xyz(
            0.2,
            0.4,
            0.4
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 3)
        for index, value in enumerate([0.23513200000000004, 0.164852, 0.0032040000000000003]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)
        test_return = lms_to_xyz(
            0.2,
            0.4,
            0.4,
            use_2_degree = False
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 3)
        for index, value in enumerate([0.021495189999999997, 0.278438132, 0.8587517800000001]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)

    # endregion

    # region Test color_conversion.xyz_to_lms
    def test_color_conversion_xyz_to_lms(self):

        # Valid Arguments
        valid_X = 0.5
        valid_Y = 0.5
        valid_Z = 0.5

        # Test X Assertions
        with self.assertRaises(AssertionError):
            xyz_to_lms(
                0, # Invalid type
                valid_Y,
                valid_Z
            )
        with self.assertRaises(AssertionError):
            xyz_to_lms(
                '0', # Invalid type
                valid_Y,
                valid_Z
            )
        with self.assertRaises(AssertionError):
            xyz_to_lms(
                -0.1, # Invalid value
                valid_Y,
                valid_Z
            )

        # Test Y Assertions
        with self.assertRaises(AssertionError):
            xyz_to_lms(
                valid_X,
                0, # Invalid type
                valid_Z
            )
        with self.assertRaises(AssertionError):
            xyz_to_lms(
                valid_X,
                '0', # Invalid type
                valid_Z
            )
        with self.assertRaises(AssertionError):
            xyz_to_lms(
                valid_X,
                -0.1, # Invalid value
                valid_Z
            )

        # Test Z Assertions
        with self.assertRaises(AssertionError):
            xyz_to_lms(
                valid_X,
                valid_Y,
                0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            xyz_to_lms(
                valid_X,
                valid_Y,
                '0' # Invalid type
            )
        with self.assertRaises(AssertionError):
            xyz_to_lms(
                valid_X,
                valid_Y,
                -0.1 # Invalid value
            )

        # Test use_2_degree Assertions
        with self.assertRaises(AssertionError):
            xyz_to_lms(
                valid_X,
                valid_Y,
                valid_Z,
                use_2_degree = 0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            xyz_to_lms(
                valid_X,
                valid_Y,
                valid_Z,
                use_2_degree = 0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            xyz_to_lms(
                valid_X,
                valid_Y,
                valid_Z,
                use_2_degree = '0' # Invalid type
            )

        # Test Return
        test_return = xyz_to_lms(
            0.2,
            0.1,
            0.0
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 3)
        for index, value in enumerate([0.2388647821277039, 0.3000120004800192, 0.0]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)
        test_return = xyz_to_lms(
            0.4,
            0.1,
            2.1,
            use_2_degree = False
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 3)
        for index, value in enumerate([0.07900529274194415, 0.12944002280819375, 0.9781639113458372]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)

    # endregion

    # region Test color_conversion.xyz_to_xyy
    def test_color_conversion_xyz_to_xyy(self):

        # Valid Arguments
        valid_X = 0.5
        valid_Y = 0.5
        valid_Z = 0.5

        # Test X Assertions
        with self.assertRaises(AssertionError):
            xyz_to_xyy(
                0, # Invalid type
                valid_Y,
                valid_Z
            )
        with self.assertRaises(AssertionError):
            xyz_to_xyy(
                '0', # Invalid type
                valid_Y,
                valid_Z
            )
        with self.assertRaises(AssertionError):
            xyz_to_xyy(
                -0.1, # Invalid value
                valid_Y,
                valid_Z
            )

        # Test Y Assertions
        with self.assertRaises(AssertionError):
            xyz_to_xyy(
                valid_X,
                0, # Invalid type
                valid_Z
            )
        with self.assertRaises(AssertionError):
            xyz_to_xyy(
                valid_X,
                '0', # Invalid type
                valid_Z
            )
        with self.assertRaises(AssertionError):
            xyz_to_xyy(
                valid_X,
                -0.1, # Invalid value
                valid_Z
            )

        # Test Z Assertions
        with self.assertRaises(AssertionError):
            xyz_to_xyy(
                valid_X,
                valid_Y,
                0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            xyz_to_xyy(
                valid_X,
                valid_Y,
                '0' # Invalid type
            )
        with self.assertRaises(AssertionError):
            xyz_to_xyy(
                valid_X,
                valid_Y,
                -0.1 # Invalid value
            )

        # Test display Assertions
        with self.assertRaises(AssertionError):
            xyz_to_xyy(
                valid_X,
                valid_Y,
                valid_Z,
                display = 0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            xyz_to_xyy(
                valid_X,
                valid_Y,
                valid_Z,
                display = 0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            xyz_to_xyy(
                valid_X,
                valid_Y,
                valid_Z,
                display = 'invalid' # Invalid value
            )

        # Test Return
        test_return = xyz_to_xyy(
            0.5,
            0.5,
            0.5
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 3)
        for index, value in enumerate([0.3333333333333333, 0.3333333333333333, 0.5]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)
        test_return = xyz_to_xyy(
            0.0,
            0.0,
            0.0,
            display = DISPLAY.SRGB.value
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 3)
        for index, value in enumerate([0.3127159072215825, 0.3290014805066623, 0.0]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)
        test_return = xyz_to_xyy(
            0.0,
            0.0,
            0.0,
            display = DISPLAY.CRT.value
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 3)
        for index, value in enumerate([0.2860098267390742, 0.2968709594000517, 0.0]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)
        test_return = xyz_to_xyy(
            0.0,
            0.0,
            0.0,
            display = DISPLAY.INTERIOR.value
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 3)
        for index, value in enumerate([0.31270561916041584, 0.3289906566653507, 0.0]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)
        test_return = xyz_to_xyy(
            0.0,
            0.0,
            0.0,
            display = DISPLAY.EXTERIOR.value
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 3)
        for index, value in enumerate([0.31269329472922286, 0.32901230506020923, 0.0]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)

    # endregion

    # region Test color_conversion.xyy_to_xyz
    def test_color_conversion_xyy_to_xyz(self):

        # Valid Arguments
        valid_x = 0.3
        valid_y = 0.3
        valid_Y = 0.5

        # Test x Assertions
        with self.assertRaises(AssertionError):
            xyy_to_xyz(
                0, # Invalid type
                valid_y,
                valid_Y
            )
        with self.assertRaises(AssertionError):
            xyy_to_xyz(
                '0', # Invalid type
                valid_y,
                valid_Y
            )
        with self.assertRaises(AssertionError):
            xyy_to_xyz(
                -0.1, # Invalid value
                valid_y,
                valid_Y
            )

        # Test y Assertions
        with self.assertRaises(AssertionError):
            xyy_to_xyz(
                valid_x,
                0, # Invalid type
                valid_Y
            )
        with self.assertRaises(AssertionError):
            xyy_to_xyz(
                valid_x,
                '0', # Invalid type
                valid_Y
            )
        with self.assertRaises(AssertionError):
            xyy_to_xyz(
                valid_x,
                -0.1, # Invalid value
                valid_Y
            )

        # Test Y Assertions
        with self.assertRaises(AssertionError):
            xyy_to_xyz(
                valid_x,
                valid_y,
                0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            xyy_to_xyz(
                valid_x,
                valid_y,
                '0' # Invalid type
            )
        with self.assertRaises(AssertionError):
            xyy_to_xyz(
                valid_x,
                valid_y,
                -0.1 # Invalid value
            )

        # Test Return
        test_return = xyy_to_xyz(
            valid_x,
            valid_y,
            valid_Y
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 3)
        for index, value in enumerate([0.5, 0.5, 0.6666666666666666]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)

    # endregion

    # region Test color_conversion.xyz_to_rgb
    def test_color_conversion_xyz_to_rgb(self):

        # Valid Arguments
        valid_X = 0.5
        valid_Y = 0.5
        valid_Z = 0.5

        # Test X Assertions
        with self.assertRaises(AssertionError):
            xyz_to_rgb(
                0, # Invalid type
                valid_Y,
                valid_Z
            )
        with self.assertRaises(AssertionError):
            xyz_to_rgb(
                '0', # Invalid type
                valid_Y,
                valid_Z
            )
        with self.assertRaises(AssertionError):
            xyz_to_rgb(
                -0.1, # Invalid value
                valid_Y,
                valid_Z
            )

        # Test Y Assertions
        with self.assertRaises(AssertionError):
            xyz_to_rgb(
                valid_X,
                0, # Invalid type
                valid_Z
            )
        with self.assertRaises(AssertionError):
            xyz_to_rgb(
                valid_X,
                '0', # Invalid type
                valid_Z
            )
        with self.assertRaises(AssertionError):
            xyz_to_rgb(
                valid_X,
                -0.1, # Invalid value
                valid_Z
            )

        # Test Z Assertions
        with self.assertRaises(AssertionError):
            xyz_to_rgb(
                valid_X,
                valid_Y,
                0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            xyz_to_rgb(
                valid_X,
                valid_Y,
                '0' # Invalid type
            )
        with self.assertRaises(AssertionError):
            xyz_to_rgb(
                valid_X,
                valid_Y,
                -0.1 # Invalid value
            )

        # Test display Assertions
        with self.assertRaises(AssertionError):
            xyz_to_rgb(
                valid_X,
                valid_Y,
                valid_Z,
                display = 0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            xyz_to_rgb(
                valid_X,
                valid_Y,
                valid_Z,
                display = 0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            xyz_to_rgb(
                valid_X,
                valid_Y,
                valid_Z,
                display = 'invalid' # Invalid value
            )

        # Test apply_gamma_correction Assertions
        with self.assertRaises(AssertionError):
            xyz_to_rgb(
                valid_X,
                valid_Y,
                valid_Z,
                apply_gamma_correction = 0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            xyz_to_rgb(
                valid_X,
                valid_Y,
                valid_Z,
                apply_gamma_correction = 0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            xyz_to_rgb(
                valid_X,
                valid_Y,
                valid_Z,
                apply_gamma_correction = '0' # Invalid type
            )

        # Test suppress_warnings Assertions
        with self.assertRaises(AssertionError):
            xyz_to_rgb(
                valid_X,
                valid_Y,
                valid_Z,
                suppress_warnings = 0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            xyz_to_rgb(
                valid_X,
                valid_Y,
                valid_Z,
                suppress_warnings = 0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            xyz_to_rgb(
                valid_X,
                valid_Y,
                valid_Z,
                suppress_warnings = '0' # Invalid type
            )

        # Test Return
        test_return = xyz_to_rgb(
            0.5,
            0.5,
            0.5
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 3)
        for index, value in enumerate([0.60239445, 0.47417143, 0.45434251]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)
        test_return = xyz_to_rgb(
            0.05,
            0.05,
            0.05,
            display = DISPLAY.CRT.value
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 3)
        for index, value in enumerate([0.57206619, 0.42193973, 0.29792242]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)
        test_return = xyz_to_rgb(
            0.5,
            0.5,
            0.5,
            display = DISPLAY.INTERIOR.value
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 3)
        for index, value in enumerate([0.54493369, 0.47564714, 0.45727676]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)
        test_return = xyz_to_rgb(
            0.5,
            0.5,
            0.5,
            display = DISPLAY.EXTERIOR.value,
            suppress_warnings = True
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 3)
        for index, value in enumerate([0.5310673, 0.48391441, 0.47057456]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)
        test_return = xyz_to_rgb(
            0.5,
            0.5,
            0.5,
            apply_gamma_correction = True
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 3)
        for index, value in enumerate([0.79915403, 0.71808196, 0.70444361]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)

        # Test Warnings
        with self.assertWarns(UserWarning):
            xyz_to_rgb( # Cannot apply gamma correction when display is not sRGB
                0.5,
                0.5,
                0.5,
                display = DISPLAY.INTERIOR.value,
                apply_gamma_correction = True
            )
        with self.assertWarns(UserWarning):
            xyz_to_rgb( # Chromaticity outside gamut
                1.0,
                1.0,
                0.0
            )
        with self.assertWarns(UserWarning):
            xyz_to_rgb( # Luminance too high
                1.0,
                1.1,
                1.0
            )
        with self.assertWarns(UserWarning):
            xyz_to_rgb( # Within gamut check skipped for exterior primaries
                0.5,
                0.5,
                0.5,
                display = DISPLAY.EXTERIOR.value
            )
        with self.assertWarns(UserWarning):
            xyz_to_rgb( # RGB out of bounds (without any previous warnings)
                1.0,
                1.0,
                1.0
            )

    # endregion

    # region Test color_conversion.rgb_to_xyz
    def test_color_conversion_rgb_to_xyz(self):

        # Valid Arguments
        valid_red = 0.5
        valid_green = 0.5
        valid_blue = 0.5

        # Test red Assertions
        with self.assertRaises(AssertionError):
            rgb_to_xyz(
                '0', # Invalid type
                valid_green,
                valid_blue
            )
        with self.assertRaises(AssertionError):
            rgb_to_xyz(
                -0.1, # Invalid value
                valid_green,
                valid_blue
            )

        # Test green Assertions
        with self.assertRaises(AssertionError):
            rgb_to_xyz(
                valid_red,
                '0', # Invalid type
                valid_blue
            )
        with self.assertRaises(AssertionError):
            rgb_to_xyz(
                valid_red,
                -0.1, # Invalid value
                valid_blue
            )

        # Test green Assertions
        with self.assertRaises(AssertionError):
            rgb_to_xyz(
                valid_red,
                valid_green,
                '0' # Invalid type
            )
        with self.assertRaises(AssertionError):
            rgb_to_xyz(
                valid_red,
                valid_green,
                -0.1 # Invalid value
            )

        # Test display Assertions
        with self.assertRaises(AssertionError):
            rgb_to_xyz(
                valid_red,
                valid_green,
                valid_blue,
                display = 0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            rgb_to_xyz(
                valid_red,
                valid_green,
                valid_blue,
                display = 0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            rgb_to_xyz(
                valid_red,
                valid_green,
                valid_blue,
                display = 'invalid' # Invalid value
            )

        # Test apply_gamma_correction Assertions
        with self.assertRaises(AssertionError):
            rgb_to_xyz(
                valid_red,
                valid_green,
                valid_blue,
                apply_gamma_correction = 0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            rgb_to_xyz(
                valid_red,
                valid_green,
                valid_blue,
                apply_gamma_correction = 0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            rgb_to_xyz(
                valid_red,
                valid_green,
                valid_blue,
                apply_gamma_correction = '0' # Invalid type
            )

        # Test Return
        test_return = rgb_to_xyz(
            0.5,
            0.5,
            0.5
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 3)
        for index, value in enumerate([0.47525, 0.5, 0.5445]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)
        test_return = rgb_to_xyz(
            0.5,
            0.5,
            0.5,
            display = DISPLAY.CRT.value
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 3)
        for index, value in enumerate([0.0553, 0.0574, 0.08065]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)
        test_return = rgb_to_xyz(
            0.5,
            0.5,
            0.5,
            display = DISPLAY.INTERIOR.value
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 3)
        for index, value in enumerate([0.47525, 0.5, 0.54455]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)
        test_return = rgb_to_xyz(
            0.5,
            0.5,
            0.5,
            display = DISPLAY.EXTERIOR.value
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 3)
        for index, value in enumerate([0.4752, 0.5, 0.5445]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)
        test_return = rgb_to_xyz(
            0.5,
            0.5,
            0.5,
            apply_gamma_correction = True
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 3)
        for index, value in enumerate([0.2034461, 0.21404114, 0.2330908]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)

        # Test Warnings
        with self.assertWarns(UserWarning):
            rgb_to_xyz( # Cannot apply gamma correction when display is not sRGB
                0.5,
                0.5,
                0.5,
                display = DISPLAY.INTERIOR.value,
                apply_gamma_correction = True
            )

    # endregion

    # region Test color_conversion.xy_to_uv
    def test_color_conversion_xy_to_uv(self):

        # Valid Arguments
        valid_x = 0.3
        valid_y = 0.3

        # Test x Assertions
        with self.assertRaises(AssertionError):
            xy_to_uv(
                0, # Invalid type
                valid_y
            )
        with self.assertRaises(AssertionError):
            xy_to_uv(
                '0', # Invalid type
                valid_y
            )
        with self.assertRaises(AssertionError):
            xy_to_uv(
                -0.1, # Invalid value
                valid_y
            )

        # Test y Assertions
        with self.assertRaises(AssertionError):
            xy_to_uv(
                valid_x,
                0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            xy_to_uv(
                valid_x,
                '0' # Invalid type
            )
        with self.assertRaises(AssertionError):
            xy_to_uv(
                valid_x,
                -0.1 # Invalid value
            )

        # Test Return
        test_return = xy_to_uv(
            valid_x,
            valid_y
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 2)
        for index, value in enumerate([0.19999999999999998, 0.3]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)

    # endregion

    # region Test color_conversion.uv_to_xy
    def test_color_conversion_uv_to_xy(self):

        # Valid Arguments
        valid_u = 0.2
        valid_v = 0.3

        # Test u Assertions
        with self.assertRaises(AssertionError):
            uv_to_xy(
                0, # Invalid type
                valid_v
            )
        with self.assertRaises(AssertionError):
            uv_to_xy(
                '0', # Invalid type
                valid_v
            )
        with self.assertRaises(AssertionError):
            uv_to_xy(
                -0.1, # Invalid value
                valid_v
            )

        # Test v Assertions
        with self.assertRaises(AssertionError):
            uv_to_xy(
                valid_u,
                0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            uv_to_xy(
                valid_u,
                '0' # Invalid type
            )
        with self.assertRaises(AssertionError):
            uv_to_xy(
                valid_u,
                -0.1 # Invalid value
            )

        # Test Return
        test_return = uv_to_xy(
            valid_u,
            valid_v
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 2)
        for index, value in enumerate([0.30000000000000004, 0.3]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)

    # endregion

    # region Test chromaticity_conversion.wavelength_to_chromaticity
    def test_chromaticity_conversion_wavelength_to_chromaticity(self):

        # Valid Arguments
        valid_wavelength = 550

        # Test wavelength Assertions
        with self.assertRaises(AssertionError):
            wavelength_to_chromaticity(
                '550' # Invalid type
            )
        with self.assertRaises(AssertionError):
            wavelength_to_chromaticity(
                250 # Invalid value
            )

        # Test standard Assertions
        with self.assertRaises(AssertionError):
            wavelength_to_chromaticity(
                valid_wavelength,
                standard = 0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            wavelength_to_chromaticity(
                valid_wavelength,
                standard = 0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            wavelength_to_chromaticity(
                valid_wavelength,
                standard = 'invalid' # Invalid value
            )

        # Test Return
        test_return = wavelength_to_chromaticity(
            valid_wavelength
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 2)
        for index, value in enumerate([0.3016037993957512, 0.6923077623715743]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)
        test_return = wavelength_to_chromaticity(
            valid_wavelength,
            standard = STANDARD.CIE_170_2_10.value
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 2)
        for index, value in enumerate([0.3511403518094706, 0.6473414565509334]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)
        test_return = wavelength_to_chromaticity(
            valid_wavelength,
            standard = STANDARD.CIE_170_2_2.value
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 2)
        for index, value in enumerate([0.31161427083871945, 0.6857576592280564]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)
        test_return = wavelength_to_chromaticity(
            valid_wavelength,
            standard = STANDARD.CIE_1964_10.value
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 2)
        for index, value in enumerate([0.3472959375972994, 0.6500899660783639]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)

    # endregion

    # region Test chromaticity_conversion.wavelength_to_hue_angle
    def test_chromaticity_conversion_wavelength_to_hue_angle(self):

        # Valid Arguments
        valid_wavelength = 550

        # Test wavelength Assertions
        with self.assertRaises(AssertionError):
            wavelength_to_hue_angle(
                '550' # Invalid type
            )
        with self.assertRaises(AssertionError):
            wavelength_to_hue_angle(
                250 # Invalid value
            )

        # Test standard Assertions
        with self.assertRaises(AssertionError):
            wavelength_to_hue_angle(
                valid_wavelength,
                standard = 0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            wavelength_to_hue_angle(
                valid_wavelength,
                standard = 0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            wavelength_to_hue_angle(
                valid_wavelength,
                standard = 'invalid' # Invalid value
            )

        # Test Return
        test_return = wavelength_to_hue_angle(
            valid_wavelength
        )
        self.assertIsInstance(test_return, float)
        self.assertAlmostEqual(test_return, -4.681812452611317)
        test_return = wavelength_to_hue_angle(
            valid_wavelength,
            standard = STANDARD.CIE_170_2_10.value
        )
        self.assertIsInstance(test_return, float)
        self.assertAlmostEqual(test_return, -4.832510418547499)
        test_return = wavelength_to_hue_angle(
            valid_wavelength,
            standard = STANDARD.CIE_170_2_2.value
        )
        self.assertIsInstance(test_return, float)
        self.assertAlmostEqual(test_return, -4.709301065032081)
        test_return = wavelength_to_hue_angle(
            valid_wavelength,
            standard = STANDARD.CIE_1964_10.value
        )
        self.assertIsInstance(test_return, float)
        self.assertAlmostEqual(test_return, -4.819671747185267)

    # endregion

    # region Test chromaticity_conversion.hue_angle_to_wavelength
    def test_chromaticity_conversion_hue_angle_to_wavelength(self):

        # Valid Arguments
        valid_angle = -pi

        # Test angle Assertions
        with self.assertRaises(AssertionError):
            hue_angle_to_wavelength(
                0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            hue_angle_to_wavelength(
                '0' # Invalid type
            )
        with self.assertRaises(AssertionError):
            hue_angle_to_wavelength(
                -0.51 * pi # Invalid value
            )

        # Test standard Assertions
        with self.assertRaises(AssertionError):
            hue_angle_to_wavelength(
                valid_angle,
                standard = 0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            hue_angle_to_wavelength(
                valid_angle,
                standard = 0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            hue_angle_to_wavelength(
                valid_angle,
                standard = 'invalid' # Invalid value
            )

        # Test suppress_warnings Assertions
        with self.assertRaises(AssertionError):
            hue_angle_to_wavelength(
                valid_angle,
                suppress_warnings = 0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            hue_angle_to_wavelength(
                valid_angle,
                suppress_warnings = 0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            hue_angle_to_wavelength(
                valid_angle,
                suppress_warnings = '0' # Invalid type
            )

        # Test Return
        test_return = hue_angle_to_wavelength(
            valid_angle
        )
        self.assertIsInstance(test_return, float)
        self.assertAlmostEqual(test_return, 491.52904608864185)
        test_return = hue_angle_to_wavelength(
            valid_angle,
            standard = STANDARD.CIE_170_2_10.value
        )
        self.assertIsInstance(test_return, float)
        self.assertAlmostEqual(test_return, 484.31854444518814)
        test_return = hue_angle_to_wavelength(
            valid_angle,
            standard = STANDARD.CIE_170_2_2.value
        )
        self.assertIsInstance(test_return, float)
        self.assertAlmostEqual(test_return, 488.78592569840157)
        test_return = hue_angle_to_wavelength(
            valid_angle,
            standard = STANDARD.CIE_1964_10.value
        )
        self.assertIsInstance(test_return, float)
        self.assertAlmostEqual(test_return, 485.06676341128315)

        # Test Warnings
        with self.assertWarns(UserWarning):
            hue_angle_to_wavelength(
                -3.0 * pi
            )

    # endregion

    # region Test chromaticity_conversion.chromaticity_rectangular_to_polar
    def test_chromaticity_conversion_chromaticity_rectangular_to_polar(self):

        # Valid Arguments
        valid_x = 0.3
        valid_y = 0.3

        # Test x Assertions
        with self.assertRaises(AssertionError):
            chromaticity_rectangular_to_polar(
                0, # Invalid type
                valid_y
            )
        with self.assertRaises(AssertionError):
            chromaticity_rectangular_to_polar(
                '0', # Invalid type
                valid_y
            )
        with self.assertRaises(AssertionError):
            chromaticity_rectangular_to_polar(
                -1.0, # Invalid value
                valid_y
            )

        # Test y Assertions
        with self.assertRaises(AssertionError):
            chromaticity_rectangular_to_polar(
                valid_x,
                0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            chromaticity_rectangular_to_polar(
                valid_x,
                '0' # Invalid type
            )
        with self.assertRaises(AssertionError):
            chromaticity_rectangular_to_polar(
                valid_x,
                -1.0 # Invalid value
            )

        # Test center Assertions
        with self.assertRaises(AssertionError):
            chromaticity_rectangular_to_polar(
                valid_x,
                valid_y,
                center = 0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            chromaticity_rectangular_to_polar(
                valid_x,
                valid_y,
                center = 0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            chromaticity_rectangular_to_polar(
                valid_x,
                valid_y,
                center = 'invalid' # Invalid value
            )

        # Test Return
        test_return = chromaticity_rectangular_to_polar(
            valid_x,
            valid_y
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 2)
        for index, value in enumerate([-1.9840098855044832, 0.031666704407724636]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)
        test_return = chromaticity_rectangular_to_polar(
            valid_x,
            valid_y,
            center = CENTER.LONG.value
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 2)
        for index, value in enumerate([-3.2443682645700243, 0.44836592198783354]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)
        test_return = chromaticity_rectangular_to_polar(
            valid_x,
            valid_y,
            center = CENTER.MEDIUM.value
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 2)
        for index, value in enumerate([-3.7083218711132995, 1.3038404810405297]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)
        test_return = chromaticity_rectangular_to_polar(
            valid_x,
            valid_y,
            center = CENTER.SHORT.value
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 2)
        for index, value in enumerate([-5.1071801000844514, 0.325]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)

    # endregion

    # region Test chromaticity_conversion.chromaticity_polar_to_rectangular
    def test_chromaticity_conversion_chromaticity_polar_to_rectangular(self):

        # Valid Arguments
        valid_angle = -pi
        valid_radius = 0.05

        # Test angle Assertions
        with self.assertRaises(AssertionError):
            chromaticity_polar_to_rectangular(
                0, # Invalid type
                valid_radius
            )
        with self.assertRaises(AssertionError):
            chromaticity_polar_to_rectangular(
                '0', # Invalid type
                valid_radius
            )

        # Test radius Assertions
        with self.assertRaises(AssertionError):
            chromaticity_polar_to_rectangular(
                valid_angle,
                0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            chromaticity_polar_to_rectangular(
                valid_angle,
                '0' # Invalid type
            )

        # Test center Assertions
        with self.assertRaises(AssertionError):
            chromaticity_polar_to_rectangular(
                valid_angle,
                valid_radius,
                center = 0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            chromaticity_polar_to_rectangular(
                valid_angle,
                valid_radius,
                center = 0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            chromaticity_polar_to_rectangular(
                valid_angle,
                valid_radius,
                center = 'invalid' # Invalid value
            )

        # Test Return
        test_return = chromaticity_polar_to_rectangular(
            valid_angle,
            valid_radius
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 2)
        for index, value in enumerate([0.2627159072215825, 0.3290014805066623]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)
        test_return = chromaticity_polar_to_rectangular(
            -pi,
            0.4,
            center = CENTER.LONG.value
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 2)
        for index, value in enumerate([0.346, 0.25399999999999995]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)
        test_return = chromaticity_polar_to_rectangular(
            -3.7,
            1.3,
            center = CENTER.MEDIUM.value
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 2)
        for index, value in enumerate([0.2974699587764693, 0.28878698318104146]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)
        test_return = chromaticity_polar_to_rectangular(
            -5.1,
            0.3,
            center = CENTER.SHORT.value
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 2)
        for index, value in enumerate([0.28839332281389407, 0.27774440469831974]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)

    # endregion

    # region Test color_temperature.tristimulus_from_spectrum
    def test_color_temperature_tristimulus_from_spectrum(self):

        # Valid Arguments
        valid_spectrum = [
            (450, 1),
            (550, 1)
        ]

        # Test spectrum Assertions
        with self.assertRaises(AssertionError):
            tristimulus_from_spectrum(
                0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            tristimulus_from_spectrum(
                0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            tristimulus_from_spectrum(
                '0' # Invalid type
            )
        with self.assertRaises(AssertionError):
            tristimulus_from_spectrum(
                (1, 1) # Invalid type
            )
        with self.assertRaises(AssertionError):
            tristimulus_from_spectrum(
                [1.0] # Invalid length
            )
        with self.assertRaises(AssertionError):
            tristimulus_from_spectrum(
                ['1', '1'] # Invalid types
            )
        with self.assertRaises(AssertionError):
            tristimulus_from_spectrum(
                [('1', '1'), ('1', '1')] # Invalid types
            )
        with self.assertRaises(AssertionError):
            tristimulus_from_spectrum(
                [(1, 1, 1), (2, 2, 2)] # Invalid lengths
            )
        with self.assertRaises(AssertionError):
            tristimulus_from_spectrum(
                [-1.0, -1.0] # Invalid values
            )
        with self.assertRaises(AssertionError):
            tristimulus_from_spectrum(
                [(0.0, -1.0), (1.0, -1.0)] # Invalid values
            )
        with self.assertRaises(AssertionError):
            tristimulus_from_spectrum(
                [(1.0, -1.0), (2.0, -1.0)] # Invalid values
            )
        with self.assertRaises(AssertionError):
            tristimulus_from_spectrum(
                [(1.0, 1.0), (1.0, 1.0)] # Invalid (repeating) values (in first index)
            )

        # Test standard Assertions
        with self.assertRaises(AssertionError):
            tristimulus_from_spectrum(
                valid_spectrum,
                standard = 0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            tristimulus_from_spectrum(
                valid_spectrum,
                standard = 0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            tristimulus_from_spectrum(
                valid_spectrum,
                standard = 'invalid' # Invalid value
            )

        # Test Return
        test_return = tristimulus_from_spectrum(
            valid_spectrum
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 3)
        for index, value in enumerate([0.38482495, 0.5164750499999999, 0.8904299995]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)
        test_return = tristimulus_from_spectrum(
            valid_spectrum,
            standard = STANDARD.CIE_170_2_10.value
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 3)
        for index, value in enumerate([0.46531545, 0.5473265, 1.065293789]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)
        test_return = tristimulus_from_spectrum(
            valid_spectrum,
            standard = STANDARD.CIE_170_2_2.value
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 3)
        for index, value in enumerate([0.38594215, 0.52687316, 0.9261676455000001]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)
        test_return = tristimulus_from_spectrum(
            valid_spectrum,
            standard = STANDARD.CIE_1964_10.value
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 3)
        for index, value in enumerate([0.450264, 0.5406085, 0.999394]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)
        spectrum = list(
            (
                datum['Wavelength'],
                1.0
            )
            for datum in color_matching_functions_1931_2
            if datum['Wavelength'] > 450
        )
        test_return = tristimulus_from_spectrum(
            spectrum # Testing omission of wavelengths
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 3)
        for index, value in enumerate([96.5168590442245, 106.23936400800198, 55.385171360635994]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)
        spectrum += [(450.5, spectrum[0][1])]
        test_return = tristimulus_from_spectrum(
            spectrum # Testing interpolation
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 3)
        for index, value in enumerate([96.8508073192245, 106.27874901050198, 57.154393035636]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)
        spectrum += [(900, spectrum[-1][1])]
        test_return = tristimulus_from_spectrum(
            spectrum # Testing clipping
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 3)
        for index, value in enumerate([96.8508073192245, 106.27874901050198, 57.154393035636]):
            self.assertIsInstance(test_return[index], float)
            self.assertAlmostEqual(test_return[index], value)

    # endregion

    # region Test color_temperature.radiant_emitance
    def test_color_temperature_radiant_emitance(self):

        # Valid Arguments
        valid_wavelength = 550
        valid_temperature = 3000

        # Test wavelength Assertions
        with self.assertRaises(AssertionError):
            radiant_emitance(
                '0', # Invalid type
                valid_temperature
            )
        with self.assertRaises(AssertionError):
            radiant_emitance(
                -1, # Invalid type
                valid_temperature
            )

        # Test temperature Assertions
        with self.assertRaises(AssertionError):
            radiant_emitance(
                valid_wavelength,
                '0' # Invalid type
            )
        with self.assertRaises(AssertionError):
            radiant_emitance(
                valid_wavelength,
                -1 # Invalid type
            )

        # Test Return
        test_return = radiant_emitance(
            valid_wavelength,
            valid_temperature
        )
        self.assertIsInstance(test_return, float)
        self.assertAlmostEqual(test_return, 1214360870680.4893)

    # endregion

    # region Test color_temperature.spectrum_from_temperature
    def test_color_temperature_spectrum_from_temperature(self):

        # Valid Arguments
        valid_temperature = 3000

        # Test temperature Assertions
        with self.assertRaises(AssertionError):
            spectrum_from_temperature(
                '0' # Invalid type
            )
        with self.assertRaises(AssertionError):
            spectrum_from_temperature(
                -1.0 # Invalid value
            )

        # Test standard Assertions
        with self.assertRaises(AssertionError):
            spectrum_from_temperature(
                valid_temperature,
                standard = 0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            spectrum_from_temperature(
                valid_temperature,
                standard = 0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            spectrum_from_temperature(
                valid_temperature,
                standard = 'invalid' # Invalid value
            )

        # Test Return
        test_return = spectrum_from_temperature(
            valid_temperature
        )
        self.assertIsInstance(test_return, list)
        for test_value in test_return:
            self.assertIsInstance(test_value, float)
        for index, value in [(0, 101365669845.23505), (-1, 2948380262101.136)]:
            self.assertAlmostEqual(test_return[index], value)
        test_return = spectrum_from_temperature(
            valid_temperature,
            standard = STANDARD.CIE_170_2_10.value
        )
        self.assertIsInstance(test_return, list)
        for test_value in test_return:
            self.assertIsInstance(test_value, float)
        for index, value in [(0, 189292552636.88422), (-1, 2948380262101.136)]:
            self.assertAlmostEqual(test_return[index], value)
        test_return = spectrum_from_temperature(
            valid_temperature,
            standard = STANDARD.CIE_170_2_2.value
        )
        self.assertIsInstance(test_return, list)
        for test_value in test_return:
            self.assertIsInstance(test_value, float)
        for index, value in [(0, 189292552636.88422), (-1, 2948380262101.136)]:
            self.assertAlmostEqual(test_return[index], value)
        test_return = spectrum_from_temperature(
            valid_temperature,
            standard = STANDARD.CIE_1964_10.value
        )
        self.assertIsInstance(test_return, list)
        for test_value in test_return:
            self.assertIsInstance(test_value, float)
        for index, value in [(0, 101365669845.23505), (-1, 2948380262101.136)]:
            self.assertAlmostEqual(test_return[index], value)

    # endregion

    # region Test color_temperature.isotherm_endpoints_from_temperature
    def test_color_temperature_isotherm_endpoints_from_temperature(self):

        # Valid Arguments
        valid_temperature = 3000

        # Test temperature Assertions
        with self.assertRaises(AssertionError):
            isotherm_endpoints_from_temperature(
                '0' # Invalid type
            )
        with self.assertRaises(AssertionError):
            isotherm_endpoints_from_temperature(
                -1.0 # Invalid value
            )

        # Test Return
        test_return = isotherm_endpoints_from_temperature(valid_temperature)
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 2)
        for test_pair in test_return:
            self.assertIsInstance(test_pair, tuple)
            self.assertEqual(len(test_pair), 2)
            for test_value in test_pair:
                self.assertIsInstance(test_value, float)
        for index, value in enumerate([0.23278161951970855, 0.3943184107415542]):
            self.assertAlmostEqual(test_return[0][index], value)

    # endregion

    # region Test color_temperature.correlated_color_temperature_from_chromaticity
    def test_color_temperature_correlated_color_temperature_from_chromaticity(self):

        # Valid Arguments
        valid_u, valid_v = xy_to_uv(0.31271, 0.32902)

        # Test u Assertions
        with self.assertRaises(AssertionError):
            correlated_color_temperature_from_chromaticity(
                0, # Invalid type
                valid_v
            )
        with self.assertRaises(AssertionError):
            correlated_color_temperature_from_chromaticity(
                '0', # Invalid type
                valid_v
            )
        with self.assertRaises(AssertionError):
            correlated_color_temperature_from_chromaticity(
                -0.1, # Invalid value
                valid_v
            )

        # Test v Assertions
        with self.assertRaises(AssertionError):
            correlated_color_temperature_from_chromaticity(
                valid_u,
                0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            correlated_color_temperature_from_chromaticity(
                valid_u,
                '0' # Invalid type
            )
        with self.assertRaises(AssertionError):
            correlated_color_temperature_from_chromaticity(
                valid_u,
                -0.1 # Invalid value
            )

        # Test Return
        test_return = correlated_color_temperature_from_chromaticity(
            valid_u,
            valid_v
        )
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 3)
        self.assertIsInstance(test_return[0], int)
        self.assertEqual(test_return[0], 6504)
        self.assertIsInstance(test_return[1], float)
        self.assertAlmostEqual(test_return[1], 0.003212310635578674)
        self.assertIsInstance(test_return[2], bool)
        self.assertTrue(test_return[2])

    # endregion

    # region Test color_temperature.generate_temperature_series
    def test_color_temperature_generate_temperature_series(self):

        # Valid Arguments
        valid_minimum_temperature = 10 ** 3
        valid_maximum_tmperature = 10 ** 7
        valid_chromaticity_distance_step = 0.01

        # Test minimum_temperature Assertions
        with self.assertRaises(AssertionError):
            generate_temperature_series(
                minimum_temperature = '0' # Invalid type
            )
        with self.assertRaises(AssertionError):
            generate_temperature_series(
                minimum_temperature = 0 # Invalid value
            )

        # Test maximum_temperature Assertions
        with self.assertRaises(AssertionError):
            generate_temperature_series(
                maximum_temperature = '0' # Invalid type
            )
        with self.assertRaises(AssertionError):
            generate_temperature_series(
                maximum_temperature = 0 # Invalid value
            )
        with self.assertRaises(AssertionError):
            generate_temperature_series(
                maximum_temperature = 10 # Invalid value (less than default minimum)
            )

        # Test chromaticity_distance_step Assertions
        with self.assertRaises(AssertionError):
            generate_temperature_series(
                chromaticity_distance_step = 0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            generate_temperature_series(
                chromaticity_distance_step = '0' # Invalid type
            )
        with self.assertRaises(AssertionError):
            generate_temperature_series(
                chromaticity_distance_step = 0.0 # Invalid value
            )

        # Test Return
        test_return = generate_temperature_series(
            minimum_temperature = valid_minimum_temperature,
            maximum_temperature = valid_maximum_tmperature,
            chromaticity_distance_step = valid_chromaticity_distance_step
        )
        self.assertIsInstance(test_return, tuple)
        self.assertIsInstance(test_return[0], list)
        self.assertEqual(len(test_return[0]), 24)
        for test_value in test_return[0]:
            self.assertIsInstance(test_value, int)
        self.assertEqual(test_return[0][-1], 10000129200)

        self.assertIsInstance(test_return[1], list)
        self.assertEqual(len(test_return[1]), 24)
        for test_pair in test_return[1]:
            self.assertIsInstance(test_pair, tuple)
            self.assertEqual(len(test_pair), 2)
            for test_value in test_pair:
                self.assertIsInstance(test_value, float)
        for index, value in enumerate([0.23987727982643164, 0.23403837880105186]):
            self.assertAlmostEqual(test_return[1][-1][index], value)

    # endregion

    # region Test color_blind.get_unique_colors
    def test_color_blind_get_unique_colors(self):

        # Test image Assertions
        with self.assertRaises(AssertionError):
            get_unique_colors(
                0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            get_unique_colors(
                0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            get_unique_colors(
                '0' # Invalid type
            )

        # Test Return
        test_return = get_unique_colors(
            Image.new('RGB', (2, 2), color = (128, 128, 128))
        )
        self.assertIsInstance(test_return, dict)
        self.assertEqual(len(test_return), 1)
        self.assertIn((128, 128, 128), test_return)
        self.assertEqual(test_return[(128, 128, 128)], 4)

    # endregion

    # region Test color_blind.filter_image
    def test_color_blind_filter_image(self):

        # Valid Arguments
        valid_image = Image.new('RGB', (2, 2), color = (128, 128, 128))
        valid_cone = 'long'

        # Test image Assertions
        with self.assertRaises(AssertionError):
            filter_image(
                0, # Invalid type
                valid_cone
            )
        with self.assertRaises(AssertionError):
            filter_image(
                0.0, # Invalid type
                valid_cone
            )
        with self.assertRaises(AssertionError):
            filter_image(
                '0', # Invalid type
                valid_cone
            )

        # Test cone Assertions
        with self.assertRaises(AssertionError):
            filter_image(
                valid_image,
                0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            filter_image(
                valid_image,
                0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            filter_image(
                valid_image,
                'invalid' # Invalid value
            )

        # Test Return
        pixels = valid_image.load()
        pixels[0, 0] = (192, 64, 64)
        pixels[1, 0] = (64, 192, 64)
        pixels[0, 1] = (64, 64, 192)
        test_return = filter_image(
            valid_image,
            'long'
        )
        self.assertIsInstance(test_return, Image.Image)
        pixels = test_return.load()
        for index, value in enumerate([89, 93, 76]):
            self.assertEqual(pixels[0, 0][index], value)
        test_return = filter_image(
            valid_image,
            'medium'
        )
        self.assertIsInstance(test_return, Image.Image)
        pixels = test_return.load()
        for index, value in enumerate([102, 91, 57]):
            self.assertEqual(pixels[0, 0][index], value)
        test_return = filter_image(
            valid_image,
            'short'
        )
        self.assertIsInstance(test_return, Image.Image)
        pixels = test_return.load()
        for index, value in enumerate([197, 59, 95]):
            self.assertEqual(pixels[0, 0][index], value)

    # endregion

# endregion

if __name__ == '__main__': main()
