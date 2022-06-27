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
from maths.functions import intersection_of_two_segments
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
            self.assertEqual(test_return[index], value)

    # endregion

# endregion

if __name__ == '__main__': main()
