"""
Figure Package Unit Test

Can be run as script, or with unittest from console with:
python -m unittest figure_test

Successfully tested with:
matplotlib==3.4.2
numpy==1.21.1
"""

# region Imports
from unittest import TestCase, main
from figure import Figure
from numpy import array
from matplotlib.axes import Axes
# endregion

# region Test
class TestFigure(TestCase):
    """Test Figure Package"""

    # region Test Figure Initialization
    def test_figure_init(self):

        # Test name Assertions
        with self.assertRaises(AssertionError):
            Figure(name = 0.0) # Invalid type
        with self.assertRaises(AssertionError):
            Figure(name = '') # Invalid str length

        # Test size Assertions
        with self.assertRaises(AssertionError):
            Figure(size = 0) # Invalid type
        with self.assertRaises(AssertionError):
            Figure(size = 0.0) # Invalid type
        with self.assertRaises(AssertionError):
            Figure(size = '0') # Invalid type
        with self.assertRaises(AssertionError):
            Figure(size = [1, 1, 1]) # Invalid length
        with self.assertRaises(AssertionError):
            Figure(size = (1, 1, 1)) # Invalid length
        with self.assertRaises(AssertionError):
            Figure(size = ('1', '1')) # Invalid types
        with self.assertRaises(AssertionError):
            Figure(size = (0, 0)) # Must be greater than zero

        # Test inverted Assertions
        with self.assertRaises(AssertionError):
            Figure(inverted = 0) # Invalid type
        with self.assertRaises(AssertionError):
            Figure(inverted = 0.0) # Invalid type
        with self.assertRaises(AssertionError):
            Figure(inverted = 'False') # Invalid type

        # Test figure_color Assertions
        with self.assertRaises(AssertionError):
            Figure(figure_color = 0) # Invalid type
        with self.assertRaises(AssertionError):
            Figure(figure_color = 0.0) # Invalid type
        with self.assertRaises(AssertionError):
            Figure(figure_color = [1, 1, 1, 1]) # Invalid length
        with self.assertRaises(AssertionError):
            Figure(figure_color = (1, 1, 1, 1)) # Invalid length
        with self.assertRaises(AssertionError):
            Figure(figure_color = ('1', '1', '1')) # Invalid types
        with self.assertRaises(AssertionError):
            Figure(figure_color = (2, 2, 2)) # Invalid values
        # String assertions handled by hex_to_rgb()

    # endregion

    # region Test Grey Level
    def test_grey_level(self):

        # Initialize with defaults
        figure = Figure()

        # Test Argument Assertions
        with self.assertRaises(AssertionError):
            figure.grey_level('0') # Invalid type
        with self.assertRaises(AssertionError):
            figure.grey_level(2) # Invalid value

        # Test Return
        test_return = figure.grey_level(0.5)
        self.assertIsInstance(test_return, tuple)
        self.assertEqual(len(test_return), 3)
        for index, value in enumerate([0.5, 0.5, 0.5]):
            self.assertEqual(test_return[index], value)

        # Close
        figure.close()

    # endregion

    # region Test Setting Fonts
    def test_set_fonts(self):

        # Initialize with defaults
        figure = Figure()

        # Test titles Assertions
        with self.assertRaises(AssertionError):
            figure.set_fonts(titles = '1') # Invalid type
        with self.assertRaises(AssertionError):
            figure.set_fonts(titles = 0) # Invalid value

        # Test labels Assertions
        with self.assertRaises(AssertionError):
            figure.set_fonts(labels = '1') # Invalid type
        with self.assertRaises(AssertionError):
            figure.set_fonts(labels = 0) # Invalid value

        # Test ticks Assertions
        with self.assertRaises(AssertionError):
            figure.set_fonts(ticks = '1') # Invalid type
        with self.assertRaises(AssertionError):
            figure.set_fonts(ticks = 0) # Invalid value

        # Test legends Assertions
        with self.assertRaises(AssertionError):
            figure.set_fonts(legends = '1') # Invalid type
        with self.assertRaises(AssertionError):
            figure.set_fonts(legends = 0) # Invalid value

        # Test color Assertions
        with self.assertRaises(AssertionError):
            figure.set_fonts(color = 0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.set_fonts(color = 0.0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.set_fonts(color = [1, 1, 1, 1]) # Invalid length
        with self.assertRaises(AssertionError):
            figure.set_fonts(color = (1, 1, 1, 1)) # Invalid length
        with self.assertRaises(AssertionError):
            figure.set_fonts(color = ('1', '1', '1')) # Invalid types
        with self.assertRaises(AssertionError):
            figure.set_fonts(color = (2, 2, 2)) # Invalid values
        # String assertions handled by hex_to_rgb()

        # Close
        figure.close()

    # endregion

    # region Test Adding Panel
    def test_add_panel(self):

        # Initialize with defaults
        figure = Figure()

        # Test name Assertions
        with self.assertRaises(AssertionError):
            figure.add_panel(name = 0.0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(name = '') # Invalid str length

        # Test title Assertions
        with self.assertRaises(AssertionError):
            figure.add_panel(title = 0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(title = 0.0) # Invalid type

        # Test position Assertions
        with self.assertRaises(AssertionError):
            figure.add_panel(position = 0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(position = 0.0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(position = '0') # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(position = [0.0, 0.0, 1.0]) # Invalid length
        with self.assertRaises(AssertionError):
            figure.add_panel(position = (0.0, 0.0, 1.0)) # Invalid length
        with self.assertRaises(AssertionError):
            figure.add_panel(position = ('0.0', '0.0', '1.0', '1.0')) # Invalid types
        with self.assertRaises(AssertionError):
            figure.add_panel(position = (0.0, 0.0, 0.0, 0.0)) # Invalid values (indices 2 and 3)

        # Test panel_color Assertions
        with self.assertRaises(AssertionError):
            figure.add_panel(panel_color = 0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(panel_color = 0.0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(panel_color = [1, 1]) # Invalid length
        with self.assertRaises(AssertionError):
            figure.add_panel(panel_color = (1, 1)) # Invalid length
        with self.assertRaises(AssertionError):
            figure.add_panel(panel_color = ('1', '1', '1')) # Invalid types
        with self.assertRaises(AssertionError):
            figure.add_panel(panel_color = (2, 2, 2)) # Invalid values
        # String assertions handled by hex_to_rgb() / hex_to_rgba()

        # Test three_dimensional Assertions
        with self.assertRaises(AssertionError):
            figure.add_panel(three_dimensional = 0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(three_dimensional = 0.0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(three_dimensional = 'False') # Invalid type

        # Test x_label Assertions
        with self.assertRaises(AssertionError):
            figure.add_panel(x_label = 0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(x_label = 0.0) # Invalid type

        # Test y_label Assertions
        with self.assertRaises(AssertionError):
            figure.add_panel(y_label = 0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(y_label = 0.0) # Invalid type

        # Test z_label Assertions
        with self.assertRaises(AssertionError):
            figure.add_panel(z_label = 0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(z_label = 0.0) # Invalid type

        # Test x_scale Assertions
        with self.assertRaises(AssertionError):
            figure.add_panel(x_scale = 0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(x_scale = 0.0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(x_scale = 'invalid') # Invalid value

        # Test y_scale Assertions
        with self.assertRaises(AssertionError):
            figure.add_panel(y_scale = 0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(y_scale = 0.0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(y_scale = 'invalid') # Invalid value

        # Test z_scale Assertions
        with self.assertRaises(AssertionError):
            figure.add_panel(z_scale = 0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(z_scale = 0.0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(z_scale = 'invalid') # Invalid value

        # Test x_margin Assertions
        with self.assertRaises(AssertionError):
            figure.add_panel(x_margin = '0') # Invalid type

        # Test y_margin Assertions
        with self.assertRaises(AssertionError):
            figure.add_panel(y_margin = '0') # Invalid type

        # Test z_margin Assertions
        with self.assertRaises(AssertionError):
            figure.add_panel(z_margin = '0') # Invalid type

        # Test x_lim Assertions
        with self.assertRaises(AssertionError):
            figure.add_panel(x_lim = 0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(x_lim = 0.0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(x_lim = '0') # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(x_lim = [0, 1, 1]) # Invalid length
        with self.assertRaises(AssertionError):
            figure.add_panel(x_lim = (0, 1, 1)) # Invalid length
        with self.assertRaises(AssertionError):
            figure.add_panel(x_lim = ('0', '1')) # Invalid types
        with self.assertRaises(AssertionError):
            figure.add_panel(x_lim = (1, 0)) # Invalid order ([0] < [1])

        # Test y_lim Assertions
        with self.assertRaises(AssertionError):
            figure.add_panel(y_lim = 0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(y_lim = 0.0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(y_lim = '0') # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(y_lim = [0, 1, 1]) # Invalid length
        with self.assertRaises(AssertionError):
            figure.add_panel(y_lim = (0, 1, 1)) # Invalid length
        with self.assertRaises(AssertionError):
            figure.add_panel(y_lim = ('0', '1')) # Invalid types
        with self.assertRaises(AssertionError):
            figure.add_panel(y_lim = (1, 0)) # Invalid order ([0] < [1])

        # Test z_lim Assertions
        with self.assertRaises(AssertionError):
            figure.add_panel(z_lim = 0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(z_lim = 0.0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(z_lim = '0') # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(z_lim = [0, 1, 1]) # Invalid length
        with self.assertRaises(AssertionError):
            figure.add_panel(z_lim = (0, 1, 1)) # Invalid length
        with self.assertRaises(AssertionError):
            figure.add_panel(z_lim = ('0', '1')) # Invalid types
        with self.assertRaises(AssertionError):
            figure.add_panel(z_lim = (1, 0)) # Invalid order ([0] < [1])

        # Test x_ticks Assertions
        with self.assertRaises(AssertionError):
            figure.add_panel(x_ticks = 0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(x_ticks = 0.0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(x_ticks = '0') # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(x_ticks = ['0']) # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(x_ticks = ('0')) # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(x_ticks = array([[0, 1], [2, 3]])) # Invalid shape

        # Test y_ticks Assertions
        with self.assertRaises(AssertionError):
            figure.add_panel(y_ticks = 0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(y_ticks = 0.0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(y_ticks = '0') # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(y_ticks = ['0']) # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(y_ticks = ('0')) # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(y_ticks = array([[0, 1], [2, 3]])) # Invalid shape

        # Test z_ticks Assertions
        with self.assertRaises(AssertionError):
            figure.add_panel(z_ticks = 0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(z_ticks = 0.0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(z_ticks = '0') # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(z_ticks = ['0']) # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(z_ticks = ('0')) # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(z_ticks = array([[0, 1], [2, 3]])) # Invalid shape

        # Test x_tick_labels Assertions
        with self.assertRaises(AssertionError):
            figure.add_panel(x_tick_labels = 0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(x_tick_labels = 0.0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(x_tick_labels = '0') # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(x_tick_labels = array([[0, 1], [2, 3]])) # Invalid shape

        # Test y_tick_labels Assertions
        with self.assertRaises(AssertionError):
            figure.add_panel(y_tick_labels = 0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(y_tick_labels = 0.0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(y_tick_labels = '0') # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(y_tick_labels = array([[0, 1], [2, 3]])) # Invalid shape

        # Test z_tick_labels Assertions
        with self.assertRaises(AssertionError):
            figure.add_panel(z_tick_labels = 0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(z_tick_labels = 0.0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(z_tick_labels = '0') # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(z_tick_labels = array([[0, 1], [2, 3]])) # Invalid shape

        # Test share_x_with Assertions
        with self.assertRaises(AssertionError):
            figure.add_panel(share_x_with = 0.0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(share_x_with = '') # Invalid length
        with self.assertRaises(AssertionError):
            figure.add_panel(share_x_with = 'invalid') # Invalid str
        figure.add_panel(name = 'share_x_test')
        figure.add_panel(share_x_with = 'share_x_test')

        # Test share_y_with Assertions
        with self.assertRaises(AssertionError):
            figure.add_panel(share_y_with = 0.0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.add_panel(share_y_with = '') # Invalid length
        with self.assertRaises(AssertionError):
            figure.add_panel(share_y_with = 'invalid') # Invalid str
        figure.add_panel(name = 'share_y_test')
        figure.add_panel(share_y_with = 'share_y_test')

        # Test Return
        test_return = figure.add_panel()
        self.assertIsInstance(test_return, Axes)

        # Close
        figure.close()

    # endregion

    # region Test Removing Panel
    def test_remove_panel(self):

        # Initialize with defaults
        figure = Figure()

        # Test Argument Assertions
        with self.assertRaises(AssertionError):
            figure.remove_panel(name = 0.0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.remove_panel(name = '') # Invalid length

        # Test Return
        test_return = figure.remove_panel(name = 'False')
        self.assertIsInstance(test_return, bool)
        self.assertFalse(test_return)
        figure.add_panel(name = 'True')
        test_return = figure.remove_panel(name = 'True')
        self.assertIsInstance(test_return, bool)
        self.assertTrue(test_return)

        # Close
        figure.close()

    # endregion

    # region Test Changing Panel Position
    def test_change_panel_position(self):

        # Initialize with defaults
        figure = Figure()

        # Test name Assertions
        with self.assertRaises(AssertionError):
            figure.change_panel_position(
                name = 0.0, # Invalid type
                position = (0.0, 0.0, 1.0, 1.0)
            )
        with self.assertRaises(AssertionError):
            figure.change_panel_position(
                name = '', # Invalid length
                position = (0.0, 0.0, 1.0, 1.0)
            )
        with self.assertRaises(AssertionError):
            figure.change_panel_position(
                name = 'invalid', # Invalid string
                position = (0.0, 0.0, 1.0, 1.0)
            )

        # Test position Assertions
        figure.add_panel(name = 'test')
        with self.assertRaises(AssertionError):
            figure.change_panel_position(
                name = 'test',
                position = 0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.change_panel_position(
                name = 'test',
                position = 0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.change_panel_position(
                name = 'test',
                position = '0' # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.change_panel_position(
                name = 'test',
                position = [0.0, 0.0, 1.0] # Invalid length
            )
        with self.assertRaises(AssertionError):
            figure.change_panel_position(
                name = 'test',
                position = (0.0, 0.0, 1.0) # Invalid length
            )
        with self.assertRaises(AssertionError):
            figure.change_panel_position(
                name = 'test',
                position = ('0.0', '0.0', '1.0', '1.0') # Invalid types
            )
        with self.assertRaises(AssertionError):
            figure.change_panel_position(
                name = 'test',
                position = (0.0, 0.0, 0.0, 0.0) # Invalid values (indices 2 and 3)
            )

        # Test Return
        test_return = figure.change_panel_position(
            name = 'test',
            position = (0, 0, 1, 1)
        )
        self.assertIsInstance(test_return, Axes)

        # Close
        figure.close()

    # endregion

    # region Test Changing 3D Panel Orientation
    def test_change_panel_orientation(self):

        # Initialize with defaults
        figure = Figure()

        # Test name Assertions
        with self.assertRaises(AssertionError):
            figure.change_panel_orientation(
                name = 0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.change_panel_orientation(
                name = '' # Invalid length
            )
        with self.assertRaises(AssertionError):
            figure.change_panel_orientation(
                name = 'invalid' # Invalid string
            )
        figure.add_panel(name = '2D')
        with self.assertRaises(AssertionError):
            figure.change_panel_orientation(
                name = '2D' # Invalid panel type
            )

        # Test vertical_sign Assertions
        figure.add_panel(
            name = '3D',
            three_dimensional = True
        )
        with self.assertRaises(AssertionError):
            figure.change_panel_orientation(
                name = '3D',
                vertical_sign = 0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.change_panel_orientation(
                name = '3D',
                vertical_sign = '0' # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.change_panel_orientation(
                name = '3D',
                vertical_sign = 2 # Invalid value
            )

        # Test left_axis Assertions
        with self.assertRaises(AssertionError):
            figure.change_panel_orientation(
                name = '3D',
                left_axis = 0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.change_panel_orientation(
                name = '3D',
                left_axis = 0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.change_panel_orientation(
                name = '3D',
                left_axis = '' # Invalid length
            )
        with self.assertRaises(AssertionError):
            figure.change_panel_orientation(
                name = '3D',
                left_axis = '?a' # Invalid string
            )

        # Test Return
        test_return = figure.change_panel_orientation(name = '3D')
        self.assertIsInstance(test_return, Axes)

        # Close
        figure.close()

    # endregion

    # region Test Changing Panel Color
    def test_change_panel_color(self):

        # Initialize with defaults
        figure = Figure()

        # Test name Assertions
        with self.assertRaises(AssertionError):
            figure.change_panel_color(
                name = 0.0, # Invalid type
                panel_color = (0, 0, 0)
            )
        with self.assertRaises(AssertionError):
            figure.change_panel_color(
                name = '', # Invalid length
                panel_color = (0, 0, 0)
            )
        with self.assertRaises(AssertionError):
            figure.change_panel_color(
                name = 'invalid', # Invalid string
                panel_color = (0, 0, 0)
            )

        # Test panel_color Assertions
        figure.add_panel(name = 'test')
        with self.assertRaises(AssertionError):
            figure.change_panel_color(
                name = 'test',
                panel_color = 0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.change_panel_color(
                name = 'test',
                panel_color = 0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.change_panel_color(
                name = 'test',
                panel_color = [1, 1] # Invalid length
            )
        with self.assertRaises(AssertionError):
            figure.change_panel_color(
                name = 'test',
                panel_color = (1, 1) # Invalid length
            )
        with self.assertRaises(AssertionError):
            figure.change_panel_color(
                name = 'test',
                panel_color = ('1', '1', '1') # Invalid types
            )
        with self.assertRaises(AssertionError):
            figure.change_panel_color(
                name = 'test',
                panel_color = (2, 2, 2) # Invalid values
            )
        # String assertions handled by hex_to_rgb()

        # Test Return
        test_return = figure.change_panel_color(
            name = 'test',
            panel_color = (0, 0, 0)
        )
        self.assertIsInstance(test_return, Axes)

        # Close
        figure.close()

    # endregion

    # region Test Changing 3D Panel Panes
    def test_change_panes(self):

        # Initialize with defaults
        figure = Figure()

        # Test name Assertions
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = 0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '' # Invalid length
            )
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = 'invalid' # Invalid string
            )
        figure.add_panel(name = '2D')
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '2D' # Invalid panel type
            )

        # Test x_pane_color Assertions
        figure.add_panel(
            name = '3D',
            three_dimensional = True
        )
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                x_pane_color = 0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                x_pane_color = 0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                x_pane_color = [1, 1] # Invalid length
            )
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                x_pane_color = (1, 1) # Invalid length
            )
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                x_pane_color = ('1', '1', '1') # Invalid types
            )
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                x_pane_color = (2, 2, 2) # Invalid values
            )
        # String assertions handled by hex_to_rgb()

        # Test x_grid_line Assertions
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                x_grid_line = 0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                x_grid_line = 0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                x_grid_line = 'invalid' # Invalid string
            )

        # Test x_grid_color Assertions
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                x_grid_color = 0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                x_grid_color = 0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                x_grid_color = [1, 1] # Invalid length
            )
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                x_grid_color = (1, 1) # Invalid length
            )
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                x_grid_color = ('1', '1', '1') # Invalid types
            )
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                x_grid_color = (2, 2, 2) # Invalid values
            )
        # String assertions handled by hex_to_rgb()

        # Test y_pane_color Assertions
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                y_pane_color = 0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                y_pane_color = 0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                y_pane_color = [1, 1] # Invalid length
            )
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                y_pane_color = (1, 1) # Invalid length
            )
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                y_pane_color = ('1', '1', '1') # Invalid types
            )
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                y_pane_color = (2, 2, 2) # Invalid values
            )
        # String assertions handled by hex_to_rgb()

        # Test y_grid_line Assertions
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                y_grid_line = 0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                y_grid_line = 0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                y_grid_line = 'invalid' # Invalid string
            )

        # Test y_grid_color Assertions
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                y_grid_color = 0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                y_grid_color = 0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                y_grid_color = [1, 1] # Invalid length
            )
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                y_grid_color = (1, 1) # Invalid length
            )
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                y_grid_color = ('1', '1', '1') # Invalid types
            )
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                y_grid_color = (2, 2, 2) # Invalid values
            )
        # String assertions handled by hex_to_rgb()

        # Test z_pane_color Assertions
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                z_pane_color = 0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                z_pane_color = 0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                z_pane_color = [1, 1] # Invalid length
            )
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                z_pane_color = (1, 1) # Invalid length
            )
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                z_pane_color = ('1', '1', '1') # Invalid types
            )
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                z_pane_color = (2, 2, 2) # Invalid values
            )
        # String assertions handled by hex_to_rgb()

        # Test z_grid_line Assertions
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                z_grid_line = 0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                z_grid_line = 0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                z_grid_line = 'invalid' # Invalid string
            )

        # Test z_grid_color Assertions
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                z_grid_color = 0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                z_grid_color = 0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                z_grid_color = [1, 1] # Invalid length
            )
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                z_grid_color = (1, 1) # Invalid length
            )
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                z_grid_color = ('1', '1', '1') # Invalid types
            )
        with self.assertRaises(AssertionError):
            figure.change_panes(
                name = '3D',
                z_grid_color = (2, 2, 2) # Invalid values
            )
        # String assertions handled by hex_to_rgb()

        # Close
        figure.close()

    # endregion

    # region Test Annotating Coordinates
    def test_annotate_coordinates(self):

        # Initialize with defaults
        figure = Figure()

        # Test name Assertions
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 0.0, # Invalid type
                coordinates = ((0, 0), (1, 1))
            )
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = '', # Invalid length
                coordinates = ((0, 0), (1, 1))
            )
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 'invalid', # Invalid string
                coordinates = ((0, 0), (1, 1))
            )

        # Test coordinates Assertions
        figure.add_panel(name = 'test')
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 'test',
                coordinates = 0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 'test',
                coordinates = 0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 'test',
                coordinates = '0' # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 'test',
                coordinates = [0, 0] # Invalid types
            )
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 'test',
                coordinates = (0, 0) # Invalid types
            )
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 'test',
                coordinates = ((0, 0, 0), (1, 1, 1)) # Invalid lengths
            )
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 'test',
                coordinates = (('0', '0'), ('1', '1')) # Invalid types
            )

        # Test coordinate_labels Assertions
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 'test',
                coordinates = ((0, 0), (1, 1)),
                coordinate_labels = 0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 'test',
                coordinates = ((0, 0), (1, 1)),
                coordinate_labels = 0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 'test',
                coordinates = ((0, 0), (1, 1)),
                coordinate_labels = '0' # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 'test',
                coordinates = ((0, 0), (1, 1)),
                coordinate_labels = ['A', 'B', 'C'] # Invalid length
            )

        # Test omit_endpoints Assertions
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 'test',
                coordinates = ((0, 0), (1, 1)),
                omit_endpoints = 0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 'test',
                coordinates = ((0, 0), (1, 1)),
                omit_endpoints = 0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 'test',
                coordinates = ((0, 0), (1, 1)),
                omit_endpoints = 'False' # Invalid type
            )

        # Test distance_proportion Assertions
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 'test',
                coordinates = ((0, 0), (1, 1)),
                distance_proportion = 0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 'test',
                coordinates = ((0, 0), (1, 1)),
                distance_proportion = '0' # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 'test',
                coordinates = ((0, 0), (1, 1)),
                distance_proportion = 2.0 # Invalid value
            )

        # Test show_x Assertions
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 'test',
                coordinates = ((0, 0), (1, 1)),
                show_x = 0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 'test',
                coordinates = ((0, 0), (1, 1)),
                show_x = 0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 'test',
                coordinates = ((0, 0), (1, 1)),
                show_x = 'False' # Invalid type
            )

        # Test show_y Assertions
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 'test',
                coordinates = ((0, 0), (1, 1)),
                show_y = 0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 'test',
                coordinates = ((0, 0), (1, 1)),
                show_y = 0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 'test',
                coordinates = ((0, 0), (1, 1)),
                show_y = 'False' # Invalid type
            )

        # Test show_ticks Assertions
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 'test',
                coordinates = ((0, 0), (1, 1)),
                show_ticks = 0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 'test',
                coordinates = ((0, 0), (1, 1)),
                show_ticks = 0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 'test',
                coordinates = ((0, 0), (1, 1)),
                show_ticks = 'False' # Invalid type
            )

        # Test font_size Assertions
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 'test',
                coordinates = ((0, 0), (1, 1)),
                font_size = '0' # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 'test',
                coordinates = ((0, 0), (1, 1)),
                font_size = 0 # Invalid value
            )

        # Test font_color Assertions
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 'test',
                coordinates = ((0, 0), (1, 1)),
                font_color = 0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 'test',
                coordinates = ((0, 0), (1, 1)),
                font_color = 0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 'test',
                coordinates = ((0, 0), (1, 1)),
                font_color = [1, 1] # Invalid length
            )
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 'test',
                coordinates = ((0, 0), (1, 1)),
                font_color = (1, 1) # Invalid length
            )
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 'test',
                coordinates = ((0, 0), (1, 1)),
                font_color = ('1', '1', '1') # Invalid types
            )
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 'test',
                coordinates = ((0, 0), (1, 1)),
                font_color = (2, 2, 2) # Invalid values
            )
        # String assertions handled by hex_to_rgb()

        # Test tick_color Assertions
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 'test',
                coordinates = ((0, 0), (1, 1)),
                tick_color = 0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 'test',
                coordinates = ((0, 0), (1, 1)),
                tick_color = 0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 'test',
                coordinates = ((0, 0), (1, 1)),
                tick_color = [1, 1] # Invalid length
            )
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 'test',
                coordinates = ((0, 0), (1, 1)),
                tick_color = (1, 1) # Invalid length
            )
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 'test',
                coordinates = ((0, 0), (1, 1)),
                tick_color = ('1', '1', '1') # Invalid types
            )
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 'test',
                coordinates = ((0, 0), (1, 1)),
                tick_color = (2, 2, 2) # Invalid values
            )
        # String assertions handled by hex_to_rgb()

        # Test z_order Assertions
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 'test',
                coordinates = ((0, 0), (1, 1)),
                z_order = 0.0 # Invalid type
            )
        with self.assertRaises(AssertionError):
            figure.annotate_coordinates(
                name = 'test',
                coordinates = ((0, 0), (1, 1)),
                z_order = '0' # Invalid type
            )

        # Close
        figure.close()

    # endregion

    # region Test Updating Figure
    def test_update(self):

        # Initialize with defaults
        figure = Figure()

        # Test Argument Assertions
        with self.assertRaises(AssertionError):
            figure.update(buffer = 0.0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.update(buffer = '0') # Invalid type

        # Close
        figure.close()

    # endregion

    # region Test Saving Figure
    def test_save(self):

        # Initialize with defaults
        figure = Figure()

        # Test path Assertions
        with self.assertRaises(AssertionError):
            figure.save(path = 0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.save(path = 0.0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.save(path = '') # Invalid length

        # Test name Assertions
        with self.assertRaises(AssertionError):
            figure.save(name = 0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.save(name = 0.0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.save(name = '') # Invalid length

        # Test extension Assertions
        with self.assertRaises(AssertionError):
            figure.save(extension = 0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.save(extension = 0.0) # Invalid type
        with self.assertRaises(AssertionError):
            figure.save(extension = '') # Invalid length

        # Close
        figure.close()

    # endregion

# endregion

if __name__ == '__main__': main()
