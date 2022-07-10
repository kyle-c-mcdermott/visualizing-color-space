"""
Figure Module

The Figure class is effectively a container for a matplotlib.pyplot.figure.  The
.add_panel method creates a subplot with specific dimensions based on
proportions of the figure area.  When multiple panels have the same specified
edges, the .update() method will, while allowing needed space for
titles/labels/ticks, align the edges of the data areas of those panels.

Most methods streamline matplotlib.pyplot operations, while
.annotate_coordinates allows for the adding of text annotaitons to data series.
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
    if 'figure' not in folders:
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
from typing import Optional, Union, List, Tuple, Dict
from matplotlib import pyplot, transforms
from matplotlib.colors import to_rgb, to_rgba
from numpy import ndarray, mean, arctan2, ptp, pi, cos, sin
from matplotlib.axes import Axes
from warnings import warn
from uuid import uuid4
# endregion

# region Figure Class
class Figure(object):
    """
    Class for containing one matplotlib.pyplot.figure and its
    matplotlib.pyplot.axes
    """

    # region Initialization
    def __init__(
            self,
            name : Optional[Union[int, str]] = None,
            size : Optional[Union[List[Union[int, float]], Tuple[Union[int, float], ...]]] = None, # inches
            inverted : Optional[bool] = None,
            figure_color : Optional[Union[List[Union[int, float]], Tuple[Union[int, float], ...], str]] = None
    ):
        """
        Initialize object instance with optional name (or number), size in
        inches and background color
        """

        # region Pass Arguments into Properties
        if name is None: name = len(pyplot.get_fignums())
        self.__name = None
        self.name = name
        if size is None: size = (16.0, 9.0)
        self.__size = None
        self.size = size
        if inverted is None: inverted = False
        self.__inverted = None
        self.inverted = inverted
        if figure_color is None: figure_color = (1.0, 1.0, 1.0) if not inverted else (0.0, 0.0, 0.0)
        self.__figure_color = None
        self.figure_color = figure_color
        # endregion

        # region Initialize Figure
        self.figure = pyplot.figure(
            num = self.name,
            figsize = self.size,
            facecolor = self.figure_color
        )
        # endregion

        # region Initialize Panel Properties
        self.panels = dict()
        self.__nominal_positions = dict()
        self.__panel_colors = dict()
        self.__font_color = (0.0, 0.0, 0.0) if not inverted else (1.0, 1.0, 1.0)
        self.__font_sizes = None
        # endregion

    # endregion

    # region Properties
    @property
    def name(self) -> Union[int, str]:
        return self.__name

    @name.setter
    def name(
            self,
            name : Union[int, str]
    ) -> None:
        assert any(isinstance(name, valid_type) for valid_type in [int, str])
        if isinstance(name, str): assert len(name) > 0
        self.__name = name
        if hasattr(self, 'figure'): self.figure.canvas.manager.set_window_title(name)

    @property
    def size(self) -> Union[List[Union[int, float]], Tuple[Union[int, float], ...]]:
        return self.__size

    @size.setter
    def size(
            self,
            size : Union[List[Union[int, float]], Tuple[Union[int, float], ...]]
    ) -> None:
        assert any(isinstance(size, valid_type) for valid_type in [list, tuple])
        assert len(size) == 2
        assert all(any(isinstance(dimension, valid_type) for valid_type in [int, float]) for dimension in size)
        assert all(dimension > 0.0 for dimension in size)
        self.__size = size
        if hasattr(self, 'figure'): self.figure.set_size_inches(size, forward = True)

    @property
    def inverted(self) -> bool:
        return self.__inverted

    @inverted.setter
    def inverted(
        self,
        inverted : bool
    ) -> None:
        assert isinstance(inverted, bool)
        self.__inverted = inverted

    @property
    def figure_color(self) -> Tuple[float, float, float]:
        return self.__figure_color

    @figure_color.setter
    def figure_color(
            self,
            figure_color : Union[List[Union[int, float]], Tuple[Union[int, float], ...], str]
    ) -> None:
        assert any(isinstance(figure_color, valid_type) for valid_type in [list, tuple, str])
        if not isinstance(figure_color, str): # Treat as RGB tri-val in the interval [0, 1]
            assert len(figure_color) == 3
            assert all(any(isinstance(value, valid_type) for valid_type in [int, float]) for value in figure_color)
            assert all(0.0 <= value <= 1.0 for value in figure_color)
            if isinstance(figure_color, list): figure_color = tuple(figure_color)
        else: # Treat as hexadecimal 24-bit RGB string
            assert isinstance(figure_color, str)
            assert 6 <= len(figure_color) <= 7
            if '#' not in figure_color: figure_color = '#{0}'.format(figure_color)
            figure_color = to_rgb(figure_color)
        self.__figure_color = figure_color
        if hasattr(self, 'figure'): self.figure.set_facecolor(figure_color)

    @property
    def nominal_positions(self) -> Dict[Union[int, str], Tuple[float, ...]]:
        return self.__nominal_positions

    @property
    def panel_colors(self) -> Dict[Union[int, str], Tuple[float, ...]]:
        return self.__panel_colors

    @property
    def font_color(self) -> Tuple[float, ...]:
        return self.__font_color

    @property
    def font_sizes(self) -> Union[None, Dict[str, Union[int, float]]]:
        return self.__font_sizes
    # endregion

    # region Grey Level
    def grey_level(self, value : Optional[Union[int, float]] = None) -> Tuple[float, float, float]:
        """
        Return grey level color of value (default 1.0), inverting if necessary
        """

        # Validate Argument
        if value is None: value = 1.0
        assert any(isinstance(value, valid_type) for valid_type in [int, float])
        assert 0.0 <= value <= 1.0

        # Return
        return (value, value, value) if not self.inverted else (1.0 - value, 1.0 - value, 1.0 - value)

    # endregion

    # region Set Fonts
    def set_fonts(
            self,
            titles : Optional[Union[int, float]] = None,
            labels : Optional[Union[int, float]] = None,
            ticks : Optional[Union[int, float]] = None,
            legends : Optional[Union[int, float]] = None,
            color : Optional[Union[List[Union[int, float]], Tuple[Union[int, float], ...], str]] = None
    ) -> None:
        """Set font sizes and color"""

        # region Validate Arguments
        if titles is not None:
            assert any(isinstance(titles, valid_type) for valid_type in [int, float])
            assert titles > 0
        if labels is not None:
            assert any(isinstance(labels, valid_type) for valid_type in [int, float])
            assert labels > 0
        if ticks is not None:
            assert any(isinstance(ticks, valid_type) for valid_type in [int, float])
            assert ticks > 0
        if legends is not None:
            assert any(isinstance(legends, valid_type) for valid_type in [int, float])
            assert legends > 0
        if color is not None:
            assert any(isinstance(color, valid_type) for valid_type in [list, tuple, str])
            if not isinstance(color, str): # Treat as RGB tri-val in the interval [0, 1]
                assert len(color) == 3
                assert all(any(isinstance(value, valid_type) for valid_type in [int, float]) for value in color)
                assert all(0.0 <= value <= 1.0 for value in color)
                if isinstance(color, list): color = tuple(color)
            else: # Treat as hexadecimal 24-bit RGB string
                assert isinstance(color, str)
                assert 6 <= len(color) <= 7
                if '#' not in color: color = '#{0}'.format(color)
                color = to_rgb(color)
        # endregion

        # region Update Properties
        if any(argument is not None for argument in [titles, labels, ticks, legends]):
            font_sizes = dict()
            if titles is not None: font_sizes['titles'] = titles
            if labels is not None: font_sizes['labels'] = labels
            if ticks is not None: font_sizes['ticks'] = ticks
            if legends is not None: font_sizes['legends'] = legends
            self.__font_sizes = font_sizes
        if color is not None:
            self.__font_color = color
        else:
            self.__font_color = self.grey_level(0.0)
        # endregion

    # endregion

    # region Add Panel
    def add_panel(
            self,
            name : Optional[Union[int, str]] = None,
            title : Optional[str] = None, # name (default)
            position : Optional[Union[List[Union[int, float]], Tuple[Union[int, float], ...]]] = None, # (0, 0, 1, 1) (default)
            panel_color : Optional[Union[List[Union[int, float]], Tuple[Union[int, float], ...], str]] = None, # (1, 1, 1) (default)
            three_dimensional : Optional[bool] = None, # False (default)
            x_label : Optional[str] = None, # '' (default)
            y_label : Optional[str] = None, # '' (default)
            z_label : Optional[str] = None, # '' (default)
            x_scale : Optional[str] = None, # 'linear' (default), 'log', 'symlog', 'logit'
            y_scale : Optional[str] = None, # 'linear' (default), 'log', 'symlog', 'logit'
            z_scale : Optional[str] = None, # 'linear' (default), 'log', 'symlog', 'logit'
            x_margin : Optional[Union[int, float]] = None, # 0.1 (default)
            y_margin : Optional[Union[int, float]] = None, # 0.1 (default)
            z_margin : Optional[Union[int, float]] = None, # 0.1 (default)
            x_lim : Optional[Union[List[Union[int, float]], Tuple[Union[int, float], ...]]] = None,
            y_lim : Optional[Union[List[Union[int, float]], Tuple[Union[int, float], ...]]] = None,
            z_lim : Optional[Union[List[Union[int, float]], Tuple[Union[int, float], ...]]] = None,
            x_ticks : Optional[Union[ndarray, List[Union[int, float]], Tuple[Union[int, float], ...]]] = None,
            y_ticks : Optional[Union[ndarray, List[Union[int, float]], Tuple[Union[int, float], ...]]] = None,
            z_ticks : Optional[Union[ndarray, List[Union[int, float]], Tuple[Union[int, float], ...]]] = None,
            x_tick_labels : Optional[Union[ndarray, List[Union[int, float, str]], Tuple[Union[int, float, str], ...]]] = None,
            y_tick_labels : Optional[Union[ndarray, List[Union[int, float, str]], Tuple[Union[int, float, str], ...]]] = None,
            z_tick_labels : Optional[Union[ndarray, List[Union[int, float, str]], Tuple[Union[int, float, str], ...]]] = None,
            share_x_with : Optional[Union[int, str]] = None,
            share_y_with : Optional[Union[int, str]] = None
    ) -> Axes:
        """
        Add a panel (matplotlib.pyplot.axes) object to the figure with optional
        arguments within the figure.  Position gives left, top, width and height.
        """

        # region Validate Arguments
        if name is None: name = len(self.panels)
        assert any(isinstance(name, valid_type) for valid_type in [int, str])
        if isinstance(name, str): assert len(name) > 0
        assert name not in self.panels
        if title is not None:
            assert isinstance(title, str)
        else:
            title = name
        if position is None: position = (0.0, 0.0, 1.0, 1.0) # whole figure area
        assert any(isinstance(position, valid_type) for valid_type in [list, tuple])
        if isinstance(position, list): position = tuple(position)
        assert len(position) == 4
        assert all(any(isinstance(value, valid_type) for valid_type in [int, float]) for value in position)
        assert all(value > 0.0 for value in position[2:])
        if not all(isinstance(value, float) for value in position):
            position = tuple(
                float(value)
                for value in position
            )
        if panel_color is None:
            if not self.inverted:
                panel_color = (1.0, 1.0, 1.0, 0.0) # transparent (in case of shared axes)
            else:
                panel_color = (0.0, 0.0, 0.0, 0.0)
        assert any(isinstance(panel_color, valid_type) for valid_type in [list, tuple, str])
        if not isinstance(panel_color, str): # Treat as RGB(A) tri/quad-val in the interval [0, 1]
            assert 3 <= len(panel_color) <= 4
            assert all(any(isinstance(value, valid_type) for valid_type in [int, float]) for value in panel_color)
            assert all(0.0 <= value <= 1.0 for value in panel_color)
            if isinstance(panel_color, list): panel_color = tuple(panel_color)
        else: # Treat as hexadecimal string
            assert isinstance(panel_color, str)
            assert 6 <= len(panel_color) <= 9
            if 6 <= len(panel_color) == 7:
                if '#' not in panel_color: panel_color = '#{0}'.format(panel_color)
                panel_color = to_rgb(panel_color)
            else:
                if '#' not in panel_color: panel_color = '#{0}'.format(panel_color)
                panel_color = to_rgba(panel_color)
        if three_dimensional is not None:
            assert isinstance(three_dimensional, bool)
        else:
            three_dimensional = False
        if x_label is not None:
            assert isinstance(x_label, str)
        else:
            x_label = ''
        if y_label is not None:
            assert isinstance(y_label, str)
        else:
            y_label = ''
        if z_label is not None:
            assert isinstance(z_label, str)
            if not three_dimensional: warn('Z Axis Settings Ignored for rectilinear (default, 2D) axes')
        else:
            z_label = ''
        if x_scale is not None:
            assert isinstance(x_scale, str)
            assert x_scale in ['linear', 'log', 'symlog', 'logit']
        else:
            x_scale = 'linear'
        if y_scale is not None:
            assert isinstance(y_scale, str)
            assert y_scale in ['linear', 'log', 'symlog', 'logit']
        else:
            y_scale = 'linear'
        if z_scale is not None:
            assert isinstance(z_scale, str)
            assert z_scale in ['linear', 'log', 'symlog', 'logit']
            if not three_dimensional: warn('Z Axis Settings Ignored for rectilinear (default, 2D) axes')
        else:
            z_scale = 'linear'
        if x_margin is not None:
            assert any(isinstance(x_margin, valid_type) for valid_type in [int, float])
        else:
            x_margin = 0.1
        if y_margin is not None:
            assert any(isinstance(y_margin, valid_type) for valid_type in [int, float])
        else:
            y_margin = 0.1
        if z_margin is not None:
            assert any(isinstance(z_margin, valid_type) for valid_type in [int, float])
            if not three_dimensional: warn('Z Axis Settings Ignored for rectilinear (default, 2D) axes')
        else:
            z_margin = 0.1
        if x_lim is not None:
            assert any(isinstance(x_lim, valid_type) for valid_type in [list, tuple])
            assert len(x_lim) == 2
            assert all(any(isinstance(limit, valid_type) for valid_type in [int, float]) for limit in x_lim)
            assert x_lim[0] < x_lim[1]
        if y_lim is not None:
            assert any(isinstance(y_lim, valid_type) for valid_type in [list, tuple])
            assert len(y_lim) == 2
            assert all(any(isinstance(limit, valid_type) for valid_type in [int, float]) for limit in y_lim)
            assert y_lim[0] < y_lim[1]
        if z_lim is not None:
            assert any(isinstance(z_lim, valid_type) for valid_type in [list, tuple])
            assert len(z_lim) == 2
            assert all(any(isinstance(limit, valid_type) for valid_type in [int, float]) for limit in z_lim)
            assert z_lim[0] < z_lim[1]
            if not three_dimensional: warn('Z Axis Settings Ignored for rectilinear (default, 2D) axes')
        if x_ticks is not None:
            assert any(isinstance(x_ticks, valid_type) for valid_type in [ndarray, list, tuple])
            if isinstance(x_ticks, ndarray):
                assert len(x_ticks.shape) == 1
            else:
                assert all(any(isinstance(tick, valid_type) for valid_type in [int, float]) for tick in x_ticks)
        if y_ticks is not None:
            assert any(isinstance(y_ticks, valid_type) for valid_type in [ndarray, list, tuple])
            if isinstance(y_ticks, ndarray):
                assert len(y_ticks.shape) == 1
            else:
                assert all(any(isinstance(tick, valid_type) for valid_type in [int, float]) for tick in y_ticks)
        if z_ticks is not None:
            assert any(isinstance(z_ticks, valid_type) for valid_type in [ndarray, list, tuple])
            if isinstance(z_ticks, ndarray):
                assert len(z_ticks.shape) == 1
            else:
                assert all(any(isinstance(tick, valid_type) for valid_type in [int, float]) for tick in z_ticks)
            if not three_dimensional: warn('Z Axis Settings Ignored for rectilinear (default, 2D) axes')
        if x_tick_labels is not None:
            assert any(isinstance(x_tick_labels, valid_type) for valid_type in [ndarray, list, tuple])
            if isinstance(x_tick_labels, ndarray):
                assert len(x_tick_labels.shape) == 1
            else:
                assert all(
                    any(isinstance(tick, valid_type) for valid_type in [int, float, str])
                    for tick in x_tick_labels
                )
        if y_tick_labels is not None:
            assert any(isinstance(y_tick_labels, valid_type) for valid_type in [ndarray, list, tuple])
            if isinstance(y_tick_labels, ndarray):
                assert len(y_tick_labels.shape) == 1
            else:
                assert all(
                    any(isinstance(tick, valid_type) for valid_type in [int, float, str])
                    for tick in y_tick_labels
                )
        if z_tick_labels is not None:
            assert any(isinstance(z_tick_labels, valid_type) for valid_type in [ndarray, list, tuple])
            if isinstance(z_tick_labels, ndarray):
                assert len(z_tick_labels.shape) == 1
            else:
                assert all(
                    any(isinstance(tick, valid_type) for valid_type in [int, float, str])
                    for tick in z_tick_labels
                )
            if not three_dimensional: warn('Z Axis Settings Ignored for rectilinear (default, 2D) axes')
        if share_x_with is not None:
            assert any(isinstance(share_x_with, valid_type) for valid_type in [int, str])
            if isinstance(share_x_with, str): assert len(share_x_with) > 0
            assert share_x_with in self.panels
            share_x_with = self.panels[share_x_with]
        if share_y_with is not None:
            assert any(isinstance(share_y_with, valid_type) for valid_type in [int, str])
            if isinstance(share_y_with, str): assert len(share_y_with) > 0
            assert share_y_with in self.panels
            share_y_with = self.panels[share_y_with]
        # endregion

        # region Add Panel to Figure
        self.__nominal_positions[name] = position
        pyplot.figure(self.figure.number) # Set as current figure
        if not three_dimensional:
            self.panels[name] = pyplot.axes(
                position = position,
                facecolor = panel_color,
                autoscale_on = True,
                xmargin = x_margin,
                ymargin = y_margin,
                sharex = share_x_with, # Points to limits and ticks, but not label
                sharey = share_y_with, # Points to limits and ticks, but not label,
                xscale = x_scale,
                yscale = y_scale,
                label = str(uuid4())
            )
        else: # projection = '3d' allows z axis arguments to pass without exception
            self.panels[name] = pyplot.axes(
                projection = '3d',
                position = position,
                facecolor = panel_color,
                autoscale_on = True,
                xmargin = x_margin,
                ymargin = y_margin,
                zmargin = z_margin,
                sharex = share_x_with, # Points to limits and ticks, but not label
                sharey = share_y_with, # Points to limits and ticks, but not label,
                xscale = x_scale,
                yscale = y_scale,
                zscale = z_scale,
                label = str(uuid4())
            )
        self.__panel_colors[name] = panel_color
        # endregion

        # region Assign Attributes
        self.panels[name].set_title(title)
        self.panels[name].set_xlabel(x_label)
        self.panels[name].set_ylabel(y_label)
        if three_dimensional: self.panels[name].set_zlabel(z_label)
        if x_lim is not None: self.panels[name].set_xlim(x_lim)
        if y_lim is not None: self.panels[name].set_ylim(y_lim)
        if three_dimensional and z_lim is not None: self.panels[name].set_zlim(z_lim)
        if x_ticks is not None: self.panels[name].get_xaxis().set_ticks(x_ticks)
        if y_ticks is not None: self.panels[name].get_yaxis().set_ticks(y_ticks)
        if three_dimensional and z_ticks is not None: self.panels[name].get_zaxis().set_ticks(z_ticks)
        if x_tick_labels is not None: self.panels[name].get_xaxis().set_ticklabels(x_tick_labels)
        if y_tick_labels is not None: self.panels[name].get_yaxis().set_ticklabels(y_tick_labels)
        # endregion

        # Return
        return self.panels[name]

    # endregion

    # region Remove Panel
    def remove_panel(
            self,
            name : Union[int, str]
    ) -> bool:
        """Remove the named panel, if it exists, and return success or failure"""

        # Validate Arguments
        assert any(isinstance(name, valid_type) for valid_type in [int, str])
        if isinstance(name, str): assert len(name) > 0

        # Remove Panel (if it exists)
        if name not in self.panels: return False
        pyplot.figure(self.figure.number) # Set as current figure (is this necessary here?)
        self.panels[name].remove()
        self.panels.pop(name, None)
        self.__nominal_positions.pop(name, None)
        return True

    # endregion

    # region Change Panel Position
    def change_panel_position(
            self,
            name : Union[int, str],
            position : Union[List[Union[int, float]], Tuple[Union[int, float], ...]]
    ) -> Axes:
        """
        Change the position of an existing panel (can't use .setter with the
        dictionary nominal_positions)
        """

        # region Validate Arguments
        assert any(isinstance(name, valid_type) for valid_type in [int, str])
        if isinstance(name, str): assert len(name) > 0
        assert name in self.panels
        assert any(isinstance(position, valid_type) for valid_type in [list, tuple])
        if isinstance(position, list): position = tuple(position)
        assert len(position) == 4
        assert all(any(isinstance(value, valid_type) for valid_type in [int, float]) for value in position)
        assert all(value > 0.0 for value in position[2:])
        if not all(isinstance(value, float) for value in position):
            position = tuple(
                float(value)
                for value in position
            )
        # endregion

        # region Set and Return
        self.__nominal_positions[name] = position
        return self.panels[name]
        # endregion

    # endregion

    # region Change 3D Panel Orientation
    def change_panel_orientation(
        self,
        name : Union[int, str],
        vertical_sign : Optional[int] = None, # +1 (default) or -1 for increasing up or down, respectively
        left_axis : Optional[str] = None # '-x', '+x', '-y' or '+y' (sign is for values moving left to right)
    ) -> Axes:
        """
        Change the orientation of an existing 3D (verified) panel.
        Z will always be the vertical axis - set whether it is increasing upward
        (default) or downward.  The left axis (approaching from the left edge)
        can be X or Y and increasing or decreasing from left to right.  Right
        axis is determined by the above two choices.
        """

        # region Validate Arguments
        assert any(isinstance(name, valid_type) for valid_type in [int, str])
        if isinstance(name, str): assert len(name) > 0
        assert name in self.panels
        assert hasattr(self.panels[name], 'zaxis')
        if vertical_sign is not None:
            assert isinstance(vertical_sign, int)
            assert vertical_sign == -1 or vertical_sign == 1
        else:
            vertical_sign = 1
        if left_axis is not None:
            assert isinstance(left_axis, str)
            assert len(left_axis) == 2
            assert left_axis.lower() in ['-x', '+x', '-y', '+y']
        else:
            left_axis = '+y'
        # endregion

        # region Set Orientation
        base_elevation = 22.5 # 45 gives isometric view
        if vertical_sign == 1:
            if left_axis == '-x':
                self.panels[name].view_init(base_elevation, 45 - 270)
            elif left_axis == '+x':
                self.panels[name].view_init(base_elevation, 45 - 90)
            elif left_axis == '-y':
                self.panels[name].view_init(base_elevation, 45 - 180)
            else:
                self.panels[name].view_init(base_elevation, 45)
        else:
            if left_axis == '-x':
                self.panels[name].view_init(base_elevation - 180, 45)
            elif left_axis == '+x':
                self.panels[name].view_init(base_elevation - 180, 45 - 180)
            elif left_axis == '-y':
                self.panels[name].view_init(base_elevation - 180, 45 - 270)
            else:
                self.panels[name].view_init(base_elevation - 180, 45 - 90)
        return self.panels[name]
        # endregion

    # endregion

    # region Change Panel Color
    def change_panel_color(
            self,
            name : Union[int, str],
            panel_color : Union[List[Union[int, float]], Tuple[Union[int, float], ...], str]
    ) -> Axes:
        """
        Change the background color of an existing panel (can't use .setter with
        the dictionary panel_colors)
        """

        # region Validate Arguments
        assert any(isinstance(name, valid_type) for valid_type in [int, str])
        if isinstance(name, str): assert len(name) > 0
        assert name in self.panels
        assert any(isinstance(panel_color, valid_type) for valid_type in [list, tuple ,str])
        if not isinstance(panel_color, str):
            if isinstance(panel_color, list): panel_color = tuple(panel_color)
            assert len(panel_color) == 3
            assert all(any(isinstance(item, valid_type) for valid_type in [int, float]) for item in panel_color)
            assert all(0.0 <= item <= 1.0 for item in panel_color)
            if not all(isinstance(item, float) for item in panel_color):
                panel_color = tuple(
                    float(value)
                    for value in panel_color
                )
        else:
            assert isinstance(panel_color, str)
            assert 6 <= len(panel_color) <= 7
            if '#' not in panel_color: panel_color = '#{0}'.format(panel_color)
            panel_color = to_rgb(panel_color)
        # endregion

        # region Set and Return
        self.__panel_colors[name] = panel_color
        self.panels[name].set_facecolor(panel_color)
        return self.panels[name]
        # endregion

    # endregion

    # region Change 3D Panel Panes
    def change_panes(
        self,
        name : Union[int, str],
        x_pane_color : Optional[Union[List[Union[int, float]], Tuple[Union[int, float], ...], str]] = None, # (0, 0, 0, 0) (default)
        x_grid_line : Optional[str] = None, # '-' (default), '--', '-.', ':', ''
        x_grid_color : Optional[Union[List[Union[int, float]], Tuple[Union[int, float], ...], str]] = None, # (0.9, 0.9, 0.9) (default)
        y_pane_color : Optional[Union[List[Union[int, float]], Tuple[Union[int, float], ...], str]] = None, # (0, 0, 0, 0) (default)
        y_grid_line : Optional[str] = None, # '-' (default), '--', '-.', ':', ''
        y_grid_color : Optional[Union[List[Union[int, float]], Tuple[Union[int, float], ...], str]] = None, # (0.9, 0.9, 0.9) (default)
        z_pane_color : Optional[Union[List[Union[int, float]], Tuple[Union[int, float], ...], str]] = None, # (0, 0, 0, 0) (default)
        z_grid_line : Optional[str] = None, # '-' (default), '--', '-.', ':', ''
        z_grid_color : Optional[Union[List[Union[int, float]], Tuple[Union[int, float], ...], str]] = None # (0.9, 0.9, 0.9) (default)
    ) -> None:
        """Adjusts 3D panel pane colors and grid line properties by axis"""

        # region Validate Arguments
        assert any(isinstance(name, valid_type) for valid_type in [int, str])
        if isinstance(name, str): assert len(name) > 0
        assert name in self.panels
        assert hasattr(self.panels[name], 'zaxis')
        if x_pane_color is not None:
            assert any(isinstance(x_pane_color, valid_type) for valid_type in [list, tuple, str])
            if not isinstance(x_pane_color, str): # Treat as RGB(A) tri/quad-val in the interval [0, 1]
                assert 3 <= len(x_pane_color) <= 4
                assert all(any(isinstance(value, valid_type) for valid_type in [int, float]) for value in x_pane_color)
                assert all(0.0 <= value <= 1.0 for value in x_pane_color)
                if isinstance(x_pane_color, list): x_pane_color = tuple(x_pane_color)
            else: # Treat as hexadecimal string
                assert isinstance(x_pane_color, str)
                assert 6 <= len(x_pane_color) <= 9
                if 6 <= len(x_pane_color) <= 7:
                    if '#' not in x_pane_color: x_pane_color = '#{0}'.format(x_pane_color)
                    x_pane_color = to_rgb(x_pane_color)
                else:
                    if '#' not in x_pane_color: x_pane_color = '#{0}'.format(x_pane_color)
                    x_pane_color = to_rgba(x_pane_color)
        else:
            x_pane_color = (0.0, 0.0, 0.0, 0.0) # transparent
        if x_grid_line is None: x_grid_line = '-'
        assert isinstance(x_grid_line, str)
        assert x_grid_line in ['-', '--', '-.', ':', '']
        if x_grid_color is not None:
            assert any(isinstance(x_grid_color, valid_type) for valid_type in [list, tuple, str])
            if not isinstance(x_grid_color, str): # Treat as RGB tri-val in the interval [0, 1]
                assert len(x_grid_color) == 3
                assert all(any(isinstance(value, valid_type) for valid_type in [int, float]) for value in x_grid_color)
                assert all(0.0 <= value <= 1.0 for value in x_grid_color)
                if isinstance(x_grid_color, list): x_grid_color = tuple(x_grid_color)
            else: # Treat as hexadecimal 24-bit RGB string
                assert isinstance(x_grid_color, str)
                assert 6 <= len(x_grid_color) <= 7
                if '#' not in x_grid_color: x_grid_color = '#{0}'.format(x_grid_color)
                x_grid_color = to_rgb(x_grid_color)
        else:
            x_grid_color = (0.9, 0.9, 0.9)
        if y_pane_color is not None:
            assert any(isinstance(y_pane_color, valid_type) for valid_type in [list, tuple, str])
            if not isinstance(y_pane_color, str): # Treat as RGB(A) tri/quad-val in the interval [0, 1]
                assert 3 <= len(y_pane_color) <= 4
                assert all(any(isinstance(value, valid_type) for valid_type in [int, float]) for value in y_pane_color)
                assert all(0.0 <= value <= 1.0 for value in y_pane_color)
                if isinstance(y_pane_color, list): y_pane_color = tuple(y_pane_color)
            else: # Treat as hexadecimal string
                assert isinstance(y_pane_color, str)
                assert 6 <= len(y_pane_color) <= 9
                if 6 <= len(y_pane_color) <= 7:
                    if '#' not in y_pane_color: y_pane_color = '#{0}'.format(y_pane_color)
                    y_pane_color = to_rgb(y_pane_color)
                else:
                    if '#' not in y_pane_color: y_pane_color = '#{0}'.format(y_pane_color)
                    y_pane_color = to_rgba(y_pane_color)
        else:
            y_pane_color = (0.0, 0.0, 0.0, 0.0) # transparent
        if y_grid_line is None: y_grid_line = '-'
        assert isinstance(y_grid_line, str)
        assert y_grid_line in ['-', '--', '-.', ':', '']
        if y_grid_color is not None:
            assert any(isinstance(y_grid_color, valid_type) for valid_type in [list, tuple, str])
            if not isinstance(y_grid_color, str): # Treat as RGB tri-val in the interval [0, 1]
                assert len(y_grid_color) == 3
                assert all(any(isinstance(value, valid_type) for valid_type in [int, float]) for value in y_grid_color)
                assert all(0.0 <= value <= 1.0 for value in y_grid_color)
                if isinstance(y_grid_color, list): y_grid_color = tuple(y_grid_color)
            else: # Treat as hexadecimal 24-bit RGB string
                assert isinstance(y_grid_color, str)
                assert 6 <= len(y_grid_color) <= 7
                if '#' not in y_grid_color: y_grid_color = '#{0}'.format(y_grid_color)
        else:
            y_grid_color = (0.9, 0.9, 0.9)
        if z_pane_color is not None:
            assert any(isinstance(z_pane_color, valid_type) for valid_type in [list, tuple, str])
            if not isinstance(z_pane_color, str): # Treat as RGB(A) tri/quad-val in the interval [0, 1]
                assert 3 <= len(z_pane_color) <= 4
                assert all(any(isinstance(value, valid_type) for valid_type in [int, float]) for value in z_pane_color)
                assert all(0.0 <= value <= 1.0 for value in z_pane_color)
                if isinstance(z_pane_color, list): z_pane_color = tuple(z_pane_color)
            else: # Treat as hexadecimal string
                assert isinstance(z_pane_color, str)
                assert 6 <= len(z_pane_color) <= 9
                if 6 <= len(z_pane_color) <= 7:
                    if '#' not in z_pane_color: z_pane_color = '#{0}'.format(z_pane_color)
                    z_pane_color = to_rgb(z_pane_color)
                else:
                    if '#' not in z_pane_color: z_pane_color = '#{0}'.format(z_pane_color)
                    z_pane_color = to_rgba(z_pane_color)
        else:
            z_pane_color = (0.0, 0.0, 0.0, 0.0) # transparent
        if z_grid_line is None: z_grid_line = '-'
        assert isinstance(z_grid_line, str)
        assert z_grid_line in ['-', '--', '-.', ':', '']
        if z_grid_color is not None:
            assert any(isinstance(z_grid_color, valid_type) for valid_type in [list, tuple, str])
            if not isinstance(z_grid_color, str): # Treat as RGB tri-val in the interval [0, 1]
                assert len(z_grid_color) == 3
                assert all(any(isinstance(value, valid_type) for valid_type in [int, float]) for value in z_grid_color)
                assert all(0.0 <= value <= 1.0 for value in z_grid_color)
                if isinstance(z_grid_color, list): z_grid_color = tuple(z_grid_color)
            else: # Treat as hexadecimal 24-bit RGB string
                assert isinstance(z_grid_color, str)
                assert 6 <= len(z_grid_color) <= 7
                if '#' not in z_grid_color: z_grid_color = '#{0}'.format(z_grid_color)
        else:
            z_grid_color = (0.9, 0.9, 0.9)
        # endregion

        # region Set Properties
        self.panels[name].w_xaxis.set_pane_color(x_pane_color)
        self.panels[name].w_yaxis.set_pane_color(y_pane_color)
        self.panels[name].w_zaxis.set_pane_color(z_pane_color)
        self.panels[name].xaxis._axinfo['grid']['linestyle'] = x_grid_line
        self.panels[name].yaxis._axinfo['grid']['linestyle'] = y_grid_line
        self.panels[name].zaxis._axinfo['grid']['linestyle'] = z_grid_line
        self.panels[name].xaxis._axinfo['grid']['color'] = x_grid_color
        self.panels[name].yaxis._axinfo['grid']['color'] = y_grid_color
        self.panels[name].zaxis._axinfo['grid']['color'] = z_grid_color
        # endregion

    # endregion

    # region Annotate Coordinates
    def annotate_coordinates(
            self,
            name : Union[int, str],
            coordinates : Union[
                List[Union[List[Union[int, float]], Tuple[Union[int, float], ...]]],
                Tuple[Union[List[Union[int, float]], Tuple[Union[int, float], ...]], ...]
            ],
            coordinate_labels : Optional[
                Union[List[Union[int, float, str]], Tuple[Union[int, float, str], ...]]
            ] = None,
            omit_endpoints : Optional[bool] = None, # default False (since endpoints necessarily have different alignment rules)
            distance_proportion : Optional[float] = None, # default 0.05
            show_x : Optional[bool] = None, # default True, but unused if coordinate_labels is not None
            show_y : Optional[bool] = None, # default True, but unused if coordinate_labels is not None
            show_ticks : Optional[bool] = None, # default False
            font_size : Optional[Union[int, float]] = None, # default 10
            font_color : Optional[Union[List[Union[int, float]], Tuple[Union[int, float], ...], str]] = None,
            tick_color : Optional[Union[List[Union[int, float]], Tuple[Union[int, float], ...], str]] = None,
            z_order : Optional[int] = None
    ) -> None:
        """
        Annotate coordinates listed (points are not plotted here).  Annotations
        are placed away from the tip of the triangle formed by connecting to the
        neighboring two points (or away from an end-point). If the first and
        last coordinates match they won't be treated as end-points (using
        triangle rule instead).  Optionally hide the x or y coordinate.

        Does not work well if horizontal and vertical axes are not close in scale!
        """

        # region Validate Arguments
        assert any(isinstance(name, valid_type) for valid_type in [int, str])
        if isinstance(name, str): assert len(name) > 0
        assert name in self.panels
        assert any(isinstance(coordinates, valid_type) for valid_type in [list, tuple])
        assert all(
            any(isinstance(coordinate, valid_type) for valid_type in [list, tuple])
            for coordinate in coordinates
        )
        assert all(len(coordinate) == 2 for coordinate in coordinates)
        assert all(
            all(any(isinstance(value, valid_type) for valid_type in [int, float]) for value in coordinate)
            for coordinate in coordinates
        )
        if coordinate_labels is not None:
            assert any(isinstance(coordinate_labels, valid_type) for valid_type in [list, tuple])
            assert len(coordinate_labels) == len(coordinates)
            assert all(
                any(isinstance(coordinate_label, valid_type) for valid_type in [int, float, str])
                for coordinate_label in coordinate_labels
            )
        if omit_endpoints is None: omit_endpoints = False
        assert isinstance(omit_endpoints, bool)
        if distance_proportion is None: distance_proportion = 0.05
        assert isinstance(distance_proportion, float)
        assert -1.0 <= distance_proportion <= 1.0
        if show_x is None: show_x = True
        assert isinstance(show_x, bool)
        if show_y is None: show_y = True
        assert isinstance(show_y, bool)
        if show_ticks is None: show_ticks = False
        assert isinstance(show_ticks, bool)
        if font_size is None:
            if self.__font_sizes is None or 'legends' not in self.__font_sizes:
                font_size = 10
            else:
                font_size = self.__font_sizes['legends']
        assert any(isinstance(font_size, valid_type) for valid_type in [int, float])
        assert font_size > 0
        if font_color is None:
            font_color = self.grey_level(0.0)
        else:
            assert any(isinstance(font_color, valid_type) for valid_type in [list, tuple, str])
            if not isinstance(font_color, str):
                if isinstance(font_color, list): font_color = tuple(font_color)
                assert len(font_color) == 3
                assert all(any(isinstance(item, valid_type) for valid_type in [int, float]) for item in font_color)
                assert all(0.0 <= item <= 1.0 for item in font_color)
                if not all(isinstance(item, float) for item in font_color):
                    font_color = tuple(
                        float(value)
                        for value in font_color
                    )
            else:
                assert isinstance(font_color, str)
                assert 6 <= len(font_color) <= 7
                if '#' not in font_color: font_color = '#{0}'.format(font_color)
                font_color = to_rgb(font_color)
        if tick_color is None:
            tick_color = self.grey_level(0.0)
        else:
            assert any(isinstance(tick_color, valid_type) for valid_type in [list, tuple, str])
            if not isinstance(tick_color, str):
                if isinstance(tick_color, list): tick_color = tuple(tick_color)
                assert len(tick_color) == 3
                assert all(any(isinstance(item, valid_type) for valid_type in [int, float]) for item in tick_color)
                assert all(0.0 <= item <= 1.0 for item in tick_color)
                if not all(isinstance(item, float) for item in tick_color):
                    tick_color = tuple(
                        float(value)
                        for value in tick_color
                    )
            else:
                assert isinstance(tick_color, str)
                assert 6 <= len(tick_color) <= 7
                if '#' not in tick_color: tick_color = '#{0}'.format(tick_color)
                tick_color = to_rgb(tick_color)
        if z_order is None: z_order = 100
        assert isinstance(z_order, int)
        # endregion

        # Determine Center-of-Mass
        center = tuple(mean(coordinates, axis = 0))

        # region Determine Position
        def determine_position_middle(
                coordinate_triplet # Target coordinate in middle
        ) -> Tuple[float, Tuple[float, float]]:

            # Determine Angles
            angle_1 = arctan2(
                (coordinate_triplet[0][1] - coordinate_triplet[1][1]) / ptp(self.panels[name].get_ylim()),
                (coordinate_triplet[0][0] - coordinate_triplet[1][0]) / ptp(self.panels[name].get_xlim())
            )
            angle_2 = arctan2(
                (coordinate_triplet[2][1] - coordinate_triplet[1][1]) / ptp(self.panels[name].get_ylim()),
                (coordinate_triplet[2][0] - coordinate_triplet[1][0]) / ptp(self.panels[name].get_xlim())
            )

            # Set Angle to Use
            use_angle = float(mean([angle_1 + 2 * pi, angle_2 + 2 * pi])) - 2 * pi # Average in definite-positive space
            use_angle += pi # Point away
            if use_angle > pi: use_angle -= 2 * pi # Maintain interval [-pi, pi]

            # Check for Acute Angle between 1 and 2 (causes average to point away instead of in)
            if abs(use_angle - angle_1) < pi / 2 or abs(use_angle - angle_2) < pi / 2:
                use_angle += pi # Point away
                if use_angle > pi: use_angle -= 2 * pi # Maintain interval [-pi, pi]

            # If Contour is Locally Near-Flat Here
            if abs((angle_1 + 2 * pi) - (angle_2 + 2 * pi)) > (7 / 8) * pi:
                inward_angle = arctan2(
                    (center[1] - coordinate_triplet[1][1]) / ptp(self.panels[name].get_ylim()),
                    (center[0] - coordinate_triplet[1][0]) / ptp(self.panels[name].get_xlim())
                )
                difference_angle = (use_angle + 2 * pi) - (inward_angle + 2 * pi)
                if difference_angle < pi: difference_angle += 2 * pi
                if difference_angle > pi: difference_angle -= 2 * pi
                if abs(difference_angle) < pi / 2:
                    use_angle += pi # Point away
                    if use_angle > pi: use_angle -= 2 * pi # Keep within the interval [-pi, pi]

            # Return Angle and Position
            return (
                use_angle,
                (
                    coordinate_triplet[1][0]
                    + distance_proportion
                    * ptp(self.panels[name].get_xlim())
                    * cos(use_angle),
                    coordinate_triplet[1][1]
                    + distance_proportion
                    * ptp(self.panels[name].get_ylim())
                    * sin(use_angle)
                )
            )

        def determine_position_end(
                coordinate_pair # Target coordinate second
        ) -> Tuple[float, Tuple[float, float]]:

            # Determine Angle
            use_angle = arctan2(
                coordinate_pair[1][1] - coordinate_pair[0][1],
                coordinate_pair[1][0] - coordinate_pair[0][0]
            )

            # Return Angle and Position
            return (
                use_angle,
                (
                    coordinate_pair[1][0]
                    + distance_proportion
                    * ptp(self.panels[name].get_xlim())
                    * cos(use_angle),
                    coordinate_pair[1][1]
                    + distance_proportion
                    * ptp(self.panels[name].get_ylim())
                    * sin(use_angle)
                )
            )

        # endregion

        # region Determine String
        def determine_string(
                position_coordinate
        ) -> str:

            # Return String
            return '{0}{1}{2}{3}{4}'.format(
                '('
                if show_x and show_y
                else '',
                '{0:.3g}'.format(position_coordinate[0])
                if show_x
                else '',
                ' x '
                if show_x and show_y
                else '',
                '{0:.3g}'.format(position_coordinate[1])
                if show_y
                else '',
                ')'
                if show_x and show_y
                else ''
            )
        # endregion

        # region Loop through Coordinates
        for index, coordinate in enumerate(coordinates):
            if (
                omit_endpoints
                and (index == 0 or index == len(coordinates) - 1)
            ):
                continue

            # region Determine Position and Angle
            position = None
            angle = None
            if index == 0: # First value
                if len(coordinates) == 1: # Lone coordinate (place above)
                    position = (
                        coordinate[0],
                        coordinate[1] + distance_proportion * ptp(self.panels[name].get_ylim())
                    )
                    angle = pi / 2.0
                elif not all(coordinate[value_index] == coordinates[-1][value_index] for value_index in range(2)):
                    # Treat as end-point
                    angle, position = determine_position_end([coordinates[1], coordinate])
                else: # Treat as middle value
                    angle, position = determine_position_middle(
                        [
                            coordinates[-1],
                            coordinate,
                            coordinates[index + 1]
                        ]
                    )
            elif index < len(coordinates) - 1: # Middle values
                angle, position = determine_position_middle(
                    [
                        coordinates[index - 1],
                        coordinate,
                        coordinates[index + 1]
                    ]
                )
            else: # End value
                if not all(coordinate[value_index] == coordinates[0][value_index] for value_index in range(2)):
                    # Treat as end-point
                    angle, position = determine_position_end([coordinates[-2], coordinate])
                else: # Treat as middle value
                    pass # Already annotated at index == 0
            # endregion

            if position is not None and angle is not None:
                self.panels[name].annotate(
                    text = (
                        determine_string(coordinate)
                        if coordinate_labels is None
                        else coordinate_labels[index]
                    ),
                    xy = position,
                    xycoords = 'data',
                    horizontalalignment = (
                        'right'
                        if abs(angle) > pi * (5 / 8)
                        else (
                            'left'
                            if abs(angle) < pi * (3 / 8)
                            else 'center'
                        )
                    ),
                    verticalalignment = (
                        'top'
                        if -pi * (3 / 4) <= angle <= -pi * (1 / 4)
                        else (
                            'bottom'
                            if pi * (1 / 4) <= angle <= pi * (3 / 4)
                            else 'center'
                        )
                    ),
                    fontsize = font_size,
                    color = font_color,
                    zorder = z_order
                )
                if show_ticks:
                    self.panels[name].plot(
                        [coordinate[0], coordinate[0] + 0.75 * (position[0] - coordinate[0])],
                        [coordinate[1], coordinate[1] + 0.75 * (position[1] - coordinate[1])],
                        color = tick_color,
                        zorder = z_order - 1
                    )
        # endregion

    # endregion

    # region Update
    def update(
            self,
            buffer : Optional[int] = None
    ) -> None:
        """
        Arrange panels to maintain alignment of plot areas based on nominal
        positions
        """

        # region Validate Arguments
        if buffer is None: buffer = 10
        assert isinstance(buffer, int)
        assert buffer >= 0
        # endregion

        # region Fonts
        for panel in self.panels.values():
            panel.set_title(
                panel.get_title(),
                size = (
                    self.__font_sizes['titles']
                    if self.__font_sizes is not None and 'titles' in self.__font_sizes
                    else None
                ),
                color = self.__font_color
            )
            panel.set_xlabel(
                panel.get_xlabel(),
                size = (
                    self.__font_sizes['labels']
                    if self.__font_sizes is not None and 'labels' in self.__font_sizes
                    else None
                ),
                color = self.__font_color
            )
            panel.set_ylabel(
                panel.get_ylabel(),
                size = (
                    self.__font_sizes['labels']
                    if self.__font_sizes is not None and 'labels' in self.__font_sizes
                    else None
                ),
                color = self.__font_color
            )
            if hasattr(panel, 'w_zaxis'):
                panel.set_zlabel(
                    panel.get_zlabel(),
                    size = (
                        self.__font_sizes['labels']
                        if self.__font_sizes is not None and 'labels' in self.__font_sizes
                        else None
                    ),
                    color = self.__font_color
                )
            panel.tick_params(
                labelsize = (
                    self.__font_sizes['ticks']
                    if self.__font_sizes is not None and 'ticks' in self.__font_sizes
                    else None
                ),
                colors = self.__font_color
            )
            legend = panel.get_legend()
            if legend is not None:
                for text in legend.get_texts():
                    if (
                        self.__font_sizes is not None
                        and 'legends' in self.__font_sizes
                    ):
                        text.set_fontsize(self.__font_sizes['legends'])
                    text.set_color(self.__font_color)
        # endregion

        # region Fit Panels within Bounds
        pixel_size = self.figure.get_size_inches() * self.figure.dpi
        old_positions = {
            key : list(value)
            for key, value in self.nominal_positions.items()
        }
        new_positions = dict()
        for name, panel in self.panels.items():
            old_positions[name][2] = old_positions[name][0] + old_positions[name][2] # Width to Right
            old_positions[name][3] = old_positions[name][1] + old_positions[name][3] # Height to Top
            old_position_pixels = [ # Proportion to Pixels
                old_positions[name][0] * pixel_size[0],
                old_positions[name][1] * pixel_size[1],
                old_positions[name][2] * pixel_size[0],
                old_positions[name][3] * pixel_size[1]
            ]
            plot_area_pixels = panel.get_tightbbox(
                self.figure.canvas.get_renderer(),
                for_layout_only = True
            ).get_points()
            label = [
                (old_position_pixels[0] - plot_area_pixels[0][0] + buffer) * (1.0 / pixel_size[0]),
                (old_position_pixels[1] - plot_area_pixels[0][1] + buffer) * (1.0 / pixel_size[1]),
                (plot_area_pixels[1][0] - old_position_pixels[2] + buffer) * (1.0 / pixel_size[0]),
                (plot_area_pixels[1][1] - old_position_pixels[3] + buffer) * (1.0 / pixel_size[1])
            ]
            data_area = panel.get_position().get_points()
            new_positions[name] = [ # Reduce data area to accommodate labels within nominal position
                data_area[0][0] + label[0],
                data_area[0][1] + label[1],
                data_area[1][0] - label[2],
                data_area[1][1] - label[3]
            ]
        # endregion

        # region Align Shared Edges
        if len(self.panels) > 1:
            names = list(self.panels.keys())
            for index_first in range(len(names) - 1):
                for index_second in range(1, len(names)):
                    for index_edge in range(4):
                        if (
                            old_positions[names[index_first]][index_edge]
                            == old_positions[names[index_second]][index_edge]
                        ):
                            if index_edge <= 1: # Left, Bottom
                                inner = max(
                                    [
                                        new_positions[names[index_first]][index_edge],
                                        new_positions[names[index_second]][index_edge]
                                    ]
                                )
                            else: # Right, Top
                                inner = min(
                                    [
                                        new_positions[names[index_first]][index_edge],
                                        new_positions[names[index_second]][index_edge]
                                    ]
                                )
                            new_positions[names[index_first]][index_edge] = inner
                            new_positions[names[index_second]][index_edge] = inner
        # endregion

        # region Set
        for name in self.panels.keys():
            self.panels[name].set_position(
                transforms.Bbox(
                    [
                        [new_positions[name][0], new_positions[name][1]],
                        [new_positions[name][2], new_positions[name][3]]
                    ]
                )
            )
            if self.inverted:
                for spine in ['top', 'bottom', 'right', 'left']:
                    self.panels[name].spines[spine].set_edgecolor((1.0, 1.0, 1.0))
        # endregion

    # endregion

    # region Save
    def save(
            self,
            path : Optional[str] = None,
            name : Optional[Union[int, str]] = None,
            extension : Optional[str] = None
    ) -> None:
        """Save figure"""

        # region Validate Arguments
        if path is None: path = '.'
        assert isinstance(path, str)
        assert len(path) > 0
        if name is None: name = self.name
        assert isinstance(name, str)
        assert len(name) > 0
        if extension is None: extension = 'svg'
        assert isinstance(extension, str)
        assert len(extension) > 0
        # endregion

        # region Sanitize
        path = ''.join(
            character for character in path
            if character.isalnum() or character in (' ', '.', '_', '-', ',', '(', ')', '/', ':')
        ).rstrip()
        name = ''.join(
            character for character in str(name)
            if character.isalnum() or character in (' ', '.', '_', '-', ',', '(', ')')
        ).rstrip()
        file_name = '{0}/{1}.{2}'.format(path, name, extension)
        # endregion

        # region Save
        pyplot.figure(self.figure.number) # Set as current figure
        pyplot.savefig(
            file_name,
            facecolor = self.figure.get_facecolor(),
            edgecolor = 'none'
        )
        # endregion

    # endregion

    # region Close
    def close(self) -> None:
        """Close figure"""

        # Close
        pyplot.close(self.figure)
        self.figure = None

    # endregion

# endregion

# region Demonstration
if __name__ == '__main__':
    """
    Generates two images - one normal and one inverted - using the same script.
    Demonstrates creating both 2D and 3D panels and altering their appearance
    and the annotation of coordinates (in 2D).
    """

    extension = 'svg' # alter as desired (tested with png, svg, pdf, and jpg)

    # Loop - Once for Normal and Once for Inverted
    for inverted in [False, True]:

        # Initialize Figure
        demo_figure = Figure(
            name = 'Demonstration Figure{0}'.format(
                ' (inverted)' if inverted else ''
            ), # Used by default as file name when saving
            size = (16, 9), # Inches
            inverted = inverted
        )
        demo_figure.set_fonts(
            titles = 12,
            labels = 10,
            ticks = 8,
            legends = 12 # Used for annotations by default
        )

        # Create Panels (subplots)
        shared_back_panel = demo_figure.add_panel(
            name = 'shared_back',
            title = '', # So as not to appear behind shared_front
            position = (0, 0.5, 0.5, 0.5), # (left, bottom, width, height)
            panel_color = demo_figure.grey_level(0.8),
            x_label = '', # So as not to appear behind shared_front
            y_label = 'Shared Back Panel Y'
        )
        shared_front_panel = demo_figure.add_panel(
            name = 'shared_front',
            title = 'Shared X Panels',
            position = demo_figure.nominal_positions['shared_back'],
            panel_color = (0, 0, 0, 0), # transparent
            x_label = 'Shared X Axis',
            y_label = 'Shared Front Panel Y'
        )
        shared_front_panel.sharex(shared_back_panel)
        shared_front_panel.yaxis.set_label_position('right')
        shared_front_panel.yaxis.tick_right()
        annotated_coordinates_panel = demo_figure.add_panel(
            name = 'annotated_coordinates',
            title = 'Annotated Coordinates',
            position = (0, 0, 0.5, 0.5),
            x_label = 'horizontal',
            y_label = 'vertical'
        )
        three_dimensional_panel = demo_figure.add_panel(
            name = 'three_dimensional',
            title = '3D',
            position = (0.5, 0, 0.45, 1), # 3D subplots do not stay within their nominal bounds properly, depending on orientation
            three_dimensional = True,
            x_label = 'X',
            y_label = 'Y',
            z_label = 'Z'
        )

        # Change 3D Panel Properties
        demo_figure.change_panel_orientation(
            name=  'three_dimensional',
            vertical_sign = +1,
            left_axis = '+x'
        )
        demo_figure.change_panes(
            name = 'three_dimensional',
            x_pane_color = (0, 0, 0, 0), # transparent
            x_grid_line = '-',
            x_grid_color = demo_figure.grey_level(0.25),
            y_pane_color = (0, 0, 0, 0), # transparent
            y_grid_line = '--',
            y_grid_color = demo_figure.grey_level(0.5),
            z_pane_color = (0, 0, 0, 0), # transparent
            z_grid_line = ':',
            z_grid_color = demo_figure.grey_level(0.75)
        )

        # Plotting on Shared Panels
        """
        Note that, as both panels have been left to auto-scale on their own,
        both the red and blue series will have the same vertical extent, filling
        their available vertical space with the default margin of 0.1 (10%).
        Since the horizontal axis is shared, it accomodates both series.
        """
        shared_back_panel.plot(
            [-1, 0.5], # x values
            [0.25, 1.5], # y values
            linewidth = 2,
            color = 'red'
        )
        shared_front_panel.plot(
            [-0.75, 2],
            [1.25, 0.125],
            linewidth = 2,
            color = 'blue'
        )

        # Plotting with Annotated Coordinates
        # Single Point (Y coordinate annotated)
        annotated_coordinates_panel.plot(
            -0.75,
            3,
            marker = 'o',
            markersize = 5,
            markerfacecolor = demo_figure.grey_level(0),
            markeredgecolor = 'none',
            zorder = 1
        )
        demo_figure.annotate_coordinates(
            name = 'annotated_coordinates',
            coordinates = [(-0.75, 3)],
            show_x = False,
            z_order = 2
        )
        # Line Segment
        annotated_coordinates_panel.plot(
            [-0.7, -0.4],
            [1, 2],
            color = demo_figure.grey_level(0.125),
            zorder = 1
        )
        demo_figure.annotate_coordinates(
            name = 'annotated_coordinates',
            coordinates = [(-0.7, 1), (-0.4, 2)],
            distance_proportion = 0.025,
            z_order = 2
        )
        # Bent Line (includes intermediate point)
        annotated_coordinates_panel.plot(
            [-0.5, 0, 0.5],
            [-0.5, -1.5, -0.5],
            color = demo_figure.grey_level(0.25),
            zorder = 1
        )
        demo_figure.annotate_coordinates(
            name = 'annotated_coordinates',
            coordinates = [(-0.5, -0.5), (0, -1.5), (0.5, -0.5)],
            distance_proportion = 0.025,
            z_order = 2
        )
        # Closed Polygon
        annotated_coordinates_panel.plot(
            [0.1, 0.25, 0.75, 0.9, 0.1],
            [3.5, 1, 0.5, 3, 3.5],
            color = demo_figure.grey_level(0.5),
            zorder = 1
        )
        demo_figure.annotate_coordinates(
            name = 'annotated_coordinates',
            coordinates = [(0.1, 3.5), (0.25, 1), (0.75, 0.5), (0.9, 3), (0.1, 3.5)],
            coordinate_labels = ['i', 'j', 'k', 'l', 'm'],
            distance_proportion = 0.025,
            show_ticks = True,
            z_order = 2
        )

        # Plotting in 3D (series taken from matplotlib demo)
        from numpy import linspace
        theta = linspace(-4 * pi, 4 * pi, 128)
        z = linspace(-2, 2, len(theta))
        r = z ** 2 + 1
        x = r * sin(theta)
        y = r * cos(theta)
        three_dimensional_panel.plot(
            x,
            y,
            z,
            linewidth = 2,
            color = demo_figure.grey_level(0.125)
        )

        # Update (Positions) and Final Modifications
        demo_figure.update() # Primarily aligning subplots/panels
        # (.update() applies one font color to all decorations)
        shared_back_panel.yaxis.label.set_color('red')
        shared_back_panel.tick_params(
            axis = 'y',
            colors = 'red'
        )
        shared_front_panel.yaxis.label.set_color('blue')
        shared_front_panel.tick_params(
            axis = 'y',
            colors = 'blue'
        )

        # Save and Close
        demo_figure.save(extension = extension)
        demo_figure.close()

# endregion
