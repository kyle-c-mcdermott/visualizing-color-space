"""
Functions for building blackbody spectra for a given temperature and for
estimating correlated color temperature for a given chromaticity.  Included also
are helper functions for plotting.
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
from scipy.constants import pi, Planck, speed_of_light, Boltzmann
from typing import Union, List, Tuple, Optional
from numpy import transpose, trapz, exp, arctan2, cos, sin, pi, arange
from maths.chromaticity_conversion import STANDARD
from maths.plotting_series import (
    color_matching_functions_170_2_10,
    color_matching_functions_170_2_2,
    color_matching_functions_1964_10,
    color_matching_functions_1931_2
)
from scipy.interpolate import interp1d
from maths.conversion_coefficients import TRISTIMULUS_NAMES
from maths.color_conversion import xy_to_uv, xyz_to_xyy
from scipy.optimize import fmin
# endregion

# region Constants
"""
Planck's Law equation and necessary constants defined:
https://en.wikipedia.org/wiki/Planckian_locus#The_Planckian_locus_in_the_XYZ_color_space
"""
RADIATION_CONSTANTS = (
    2.0 * pi * Planck * (speed_of_light ** 2.0),
    (Planck * speed_of_light) / Boltzmann
)
# endregion

# region Tristimulus from Spectrum
def tristimulus_from_spectrum(
    spectrum : Union[
        List[Union[int, float]], # Intensity only, assumes wavelengths match those of the CMF of chosen standard
        List[Union[List[Union[int, float]], Tuple[Union[int, float], Union[int, float]]]] # Wavelength-Intenstiy Pairs
    ],
    standard : Optional[str] = None # default 1931_2
) -> Tuple[float, float, float]: # X, Y, Z
    """
    Applies the color matching functions to the input spectrum and returns the
    integrated product for each function.  If spectrum consists of a single
    column the wavelengths are assumed to match those of the optionally chosen
    color matching function.  Spectrum is trimmed if any wavelengths exceed the
    range of the color matching functions.  Interpolation is used when necessary.
    """

    # region Validate Arguments
    assert isinstance(spectrum, list)
    assert len(spectrum) > 1
    assert all(any(isinstance(datum, valid_type) for valid_type in [int, float, list, tuple])for datum in spectrum)
    if any(isinstance(spectrum[0], value_type) for value_type in [int, float]):
        assert all(value >= 0.0 for value in spectrum)
    else:
        assert all(len(pair) == 2 for pair in spectrum)
        assert all(all(any(isinstance(value, valid_type) for valid_type in [int, float]) for value in pair) for pair in spectrum)
        assert all(pair[0] > 0.0 for pair in spectrum)
        assert all(pair[1] >= 0.0 for pair in spectrum)
        assert len(spectrum) == len(set(transpose(spectrum)[0])) # No repeating wavelengths
    if standard is None: standard = STANDARD.CIE_1931_2.value
    assert isinstance(standard, str)
    assert any(standard == valid.value for valid in STANDARD)
    # endregion

    # region Select Standard
    if standard == STANDARD.CIE_170_2_10.value:
        color_matching_functions = color_matching_functions_170_2_10
    elif standard == STANDARD.CIE_170_2_2.value:
        color_matching_functions = color_matching_functions_170_2_2
    elif standard == STANDARD.CIE_1964_10.value:
        color_matching_functions = color_matching_functions_1964_10
    else:
        color_matching_functions = color_matching_functions_1931_2
    # endregion

    # More Assertions
    if any(isinstance(spectrum[0], value_type) for value_type in [int, float]):
        assert len(spectrum) == len(color_matching_functions)

    # region (Sort and Clip Spectrum)
    if any(isinstance(spectrum[0], pair_type) for pair_type in [list, tuple]):
        spectrum = sorted(spectrum, key = lambda pair: pair[0])
        if (
            spectrum[0][0] < color_matching_functions[0]['Wavelength']
            or spectrum[-1][0] > color_matching_functions[0]['Wavelength']
        ):
            spectrum = list(
                pair
                for pair in spectrum
                if (
                    color_matching_functions[0]['Wavelength']
                    <= pair[0]
                    <= color_matching_functions[-1]['Wavelength']
                )
            )
    # endregion

    # region Line Up Wavelengths in Color Matching Functions to Spectrum
    if any(isinstance(spectrum[0], pair_type) for pair_type in [list, tuple]):
        if all(
            pair[0] in list(datum['Wavelength'] for datum in color_matching_functions)
            for pair in spectrum
        ): # Omit any extra wavelengths in color matching functions that aren't in spectrum
            color_matching_functions = list(
                datum
                for datum in color_matching_functions
                if datum['Wavelength'] in transpose(spectrum)[0]
            )
        else: # Generate new, interpolated color matching functions for spectrum wavelengths
            interpolators = {
                tristimulus_name : interp1d(
                    list(datum['Wavelength'] for datum in color_matching_functions),
                    list(datum[tristimulus_name] for datum in color_matching_functions)
                )
                for tristimulus_name in TRISTIMULUS_NAMES
            }
            color_matching_functions = list(
                {
                    'Wavelength' : pair[0],
                    **{
                        function_name : float(interpolator(pair[0]))
                        for function_name, interpolator in interpolators.items()
                    }
                }
                for pair in spectrum
            )
    # endregion

    # region Integrate Products
    tristimulus_values = tuple(
        float(
            trapz(
                list(
                    (
                        datum
                        if any(isinstance(datum, value_type) for value_type in [int, float])
                        else datum[1]
                    )
                    * color_matching_functions[datum_index][tristimulus_name]
                    for datum_index, datum in enumerate(spectrum)
                )
            )
        )
        for tristimulus_name in TRISTIMULUS_NAMES
    )
    # endregion

    # Return
    return tristimulus_values

# endregion

# region Radiant Emitance from Temperature
def radiant_emitance(
    wavelength : Union[int, float], # (nm)
    temperature : Union[int, float] # (K)
) -> float: # emitance
    """Apply Planck's Law"""

    # Validate Arguments
    assert any(isinstance(wavelength, valid_type) for valid_type in [int, float])
    assert wavelength > 0.0
    assert any(isinstance(temperature, valid_type) for valid_type in [int, float])
    assert temperature > 0.0

    # Scale Wavelength and Apply Planck's Law
    wavelength *= (10.0 ** -9.0) # (nm to m)
    return float(
        (
            RADIATION_CONSTANTS[0]
            / (wavelength ** 5.0)
        )
        * (
            1.0
            / (
                exp(
                    RADIATION_CONSTANTS[1]
                    / (wavelength * temperature)
                )
                - 1.0
            )
        )
    )

# endregion

# region Spectrum from Temperature
def spectrum_from_temperature(
    temperature : Union[int, float], # (K)
    standard : Optional[str] = None # default 1931_2
) -> List[float]: # [emitances]
    """
    Generate a spectrum of radiant emitances for the tabulated wavelengths in
    the color matching functions of the optionally specified CIE standard.
    (Wavelengths specified this way to avoid the necessity of interpolation)
    """

    # Validate Arguments
    assert any(isinstance(temperature, valid_type) for valid_type in [int, float])
    assert temperature > 0.0
    if standard is None: standard = STANDARD.CIE_1931_2.value
    assert isinstance(standard, str)
    assert any(standard == valid.value for valid in STANDARD)

    # Select Standard
    if standard == STANDARD.CIE_170_2_10.value:
        color_matching_functions = color_matching_functions_170_2_10
    elif standard == STANDARD.CIE_170_2_2.value:
        color_matching_functions = color_matching_functions_170_2_2
    elif standard == STANDARD.CIE_1964_10.value:
        color_matching_functions = color_matching_functions_1964_10
    else:
        color_matching_functions = color_matching_functions_1931_2

    # Generate Spectrum
    spectrum = list(
        radiant_emitance(
            wavelength,
            temperature
        )
        for wavelength in sorted(list(datum['Wavelength'] for datum in color_matching_functions))
    )

    # Return
    return spectrum

# endregion

# region Isotherm Endpoints from Temperature
def isotherm_endpoints_from_temperature(
    temperature : Union[int, float] # (K)
) -> Tuple[Tuple[float, float], Tuple[float, float]]: # ((u1, v1), (u2, v2))
    """
    Determine local angle of Planckian locus in (u, v) chromaticity space around
    the desired temperature, then go out 0.05 in either direction perpendicular.
    """

    # Validate Arguments
    assert any(isinstance(temperature, valid_type) for valid_type in [int, float])
    assert temperature > 0.0

    # Get Local Chromaticities
    chromaticities = list(
        xy_to_uv(
            *xyz_to_xyy(
                *tristimulus_from_spectrum(
                    spectrum_from_temperature(
                        max([100, temperature + offset]) # Stay well above zero
                    )
                )
            )[0:2]
        )
        for offset in [-100, 0, 100]
    )

    # Get Local Angle
    angle = arctan2(
        chromaticities[2][1] - chromaticities[0][1], # delta-y
        chromaticities[2][0] - chromaticities[0][0] # delta-x
    )

    # Get Endpoints
    endpoints = tuple(
        (
            float(chromaticities[1][0] + 0.05 * cos(angle + rotation)),
            float(chromaticities[1][1] + 0.05 * sin(angle + rotation))
        )
        for rotation in [-pi / 2.0, pi / 2.0]
    )

    # Return
    return endpoints

# endregion

# region Correlated Color Temperature from (u, v) Chromaticity
def correlated_color_temperature_from_chromaticity(
    u : float,
    v : float
) -> Tuple[int, float, bool]: # temperature, distance, valid
    """
    Determine the nearest color temperature chromaticity to the specified
    coordinates using fmin().
    """

    # Validate Arguments
    assert isinstance(u, float)
    assert 0.0 <= u <= 1.0
    assert isinstance(v, float)
    assert 0.0 <= v <= 1.0

    # region Function - Distance to Temperature
    def distance_to_temperature(temperature, u, v):
        chromaticity = xy_to_uv(
            *xyz_to_xyy(
                *tristimulus_from_spectrum(
                    spectrum_from_temperature(
                        int(temperature)
                    )
                )
            )[0:2]
        )
        return (
            (u - chromaticity[0]) ** 2.0
            + (v - chromaticity[1]) ** 2.0
        ) ** 0.5
    # endregion

    # Solve by Minimum Distance
    solution = fmin(
        func = distance_to_temperature,
        x0 = 6000,
        args = (u, v),
        full_output = True, # to get best distance
        disp = False # to omit console message
    )
    temperature = int(solution[0])
    distance = float(solution[1])

    # Return
    return (
        temperature,
        distance,
        distance <= 0.05 and temperature < 10 ** 10
    )

# endregion

# region Generate Evenly Spaced Temperature Series
def generate_temperature_series(
    minimum_temperature : Optional[Union[int, float]] = None, # (K)
    maximum_temperature : Optional[Union[int, float]] = None, # (K)
    chromaticity_distance_step : Optional[float] = None # (x, y) Chromatictiy
) -> Tuple[List[int], List[Tuple[float, float]]]: # [temperatures] (K) and [chromaticities] (x, y)
    """
    Generate a seris of temperatures from minimum to maximum with a minimum
    chromaticity difference between temperatures.  The aim is to have
    chromaticity differences not too much greater than the step size.
    (Default values result in a list of 69 temperatures)
    """

    # region Validate Arguments
    if minimum_temperature is None: minimum_temperature = 10 ** 2
    assert any(isinstance(minimum_temperature, valid_type) for valid_type in [int, float])
    assert minimum_temperature > 0.0
    if maximum_temperature is None: maximum_temperature = 10 ** 10
    assert any(isinstance(maximum_temperature, valid_type) for valid_type in [int, float])
    assert maximum_temperature > 0.0
    assert maximum_temperature > minimum_temperature
    if chromaticity_distance_step is None: chromaticity_distance_step = 0.0025
    assert isinstance(chromaticity_distance_step, float)
    assert 0.0 < chromaticity_distance_step < 0.5
    # endregion

    # region Build Temperature Series
    temperatures = [int(minimum_temperature)]
    chromaticities = [
        xyz_to_xyy(
            *tristimulus_from_spectrum(
                spectrum_from_temperature(
                    temperatures[-1]
                )
            )
        )[0:2]
    ]
    while temperatures[-1] < maximum_temperature:
        for power in arange(1, 10.1, 1):
            chromaticity = xyz_to_xyy(
                *tristimulus_from_spectrum(
                    spectrum_from_temperature(
                        temperatures[-1] + 10.0 ** power
                    )
                )
            )[0:2]
            if (
                (chromaticity[0] - chromaticities[-1][0]) ** 2.0
                + (chromaticity[1] - chromaticities[-1][1]) ** 2.0
            ) ** 0.5 > chromaticity_distance_step or power == 10:
                temperatures.append(
                    int(temperatures[-1] + 10.0 ** power)
                )
                chromaticities.append(
                    chromaticity
                )
                break
    # endregion

    # Return
    return temperatures, chromaticities

# endregion
