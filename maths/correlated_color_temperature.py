"""
Functions for building blackbody spectra for a given temperature and for
estimating correlated color temperature for a given chromaticity.
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
from numpy import arange, linspace, exp, arctan2, cos, sin, pi, ndarray
from typing import Union, Tuple, List
from maths.chromaticity_from_spectrum import chromaticity_from_spectrum
from scipy.interpolate import interp1d
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

WAVELENGTHS = list(arange(360, 830.1, 1)) # Based on tabulated CIE 1931 Color Matching Functions
TEMPERATURES = (
    list(linspace(100, 1990, 16))
    + list(linspace(2000, 3900, 16))
    + list(linspace(4000, 7900, 16))
    + list(linspace(8000, 99000, 8))
    + list(linspace(100000, 1000000, 8))
)
# endregion

# region Function - Planck's Law
def radiant_emitance(
    wavelength : Union[int, float], # (nm)
    temperature : Union[int, float] # (K)
) -> float: # (W/m^3)

    # Validate Arguments
    assert any(isinstance(wavelength, valid_type) for valid_type in [int, float])
    assert any(isinstance(temperature, valid_type) for valid_type in [int, float])
    assert temperature > 0

    # Scale Wavelength and Apply Planck's Law
    wavelength *= (10.0 ** -9.0) # (nm to m)
    return (
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

# region Functions - Conversions between CIE 1931 (x, y) and CIE 1960 (u, v)
"""
Using MacAdam's simplified expressions for conversion:
https://en.wikipedia.org/wiki/CIE_1960_color_space
"""
def xy_to_uv(
    x : float,
    y : float
) -> Tuple[float, float]: # (u, v)
    assert isinstance(x, float); assert 0.0 <= x <= 1.0
    assert isinstance(y, float); assert 0.0 <= y <= 1.0
    return (
        (4.0 * x)
        / (12.0 * y - 2.0 * x + 3),
        (6.0 * y)
        / (12.0 * y - 2.0 * x + 3)
    )
def uv_to_xy(
    u : float,
    v : float
) -> Tuple[float, float]: # (x, y)
    assert isinstance(u, float); assert 0.0 <= u <= 1.0
    assert isinstance(v, float); assert 0.0 <= v <= 1.0
    return (
        (3.0 * u)
        / (2.0 * u - 8.0 * v + 4),
        (2.0 * v)
        / (2.0 * u - 8.0 * v + 4)
    )
# endregion

# region Function - Chromaticity from Temperature
def chromaticity_from_temperature(
    temperature : Union[int, float] # (K)
) -> Tuple[Tuple[float, float], Tuple[float, float]]: # ((x, y), (u, v))

    # Validate Argument
    assert any(isinstance(temperature, valid_type) for valid_type in [int, float])
    assert temperature > 0

    # Build Spectrum and Estimate CIE 1931 tristimulus values and chromaticity
    spectrum = list(
        (
            wavelength,
            radiant_emitance(
                wavelength,
                temperature
            )
        )
        for wavelength in WAVELENGTHS
    )
    chromaticity = chromaticity_from_spectrum(spectrum)

    # Convert to CIE 1960 and Return
    u, v = xy_to_uv(*chromaticity[1])
    return chromaticity[1], (u, v)

# endregion

# region Build Interpolator for Spectrum Locus
temperature_chromaticities = list(
    chromaticity_from_temperature(temperature)
    for temperature in TEMPERATURES
)
uv_chromaticity_from_temperature = tuple(
    interp1d(
        TEMPERATURES,
        list(
            chromaticity[1][index]
            for chromaticity in temperature_chromaticities
        ),
        bounds_error = False,
        fill_value = (
            temperature_chromaticities[0][1][index],
            temperature_chromaticities[-1][1][index]
        )
    )
    for index in range(2)
)
# endregion

# region Function - Isotherm Endpoints from Temperature
def isotherm_endpoints_from_temperature(
    temperature : Union[int, float] # (K)
) -> Tuple[
    Tuple[Tuple[float, float], Tuple[float, float]], # ((x1, y1), (x2, y2))
    Tuple[Tuple[float, float], Tuple[float, float]] # ((u1, v1), (u2, v2))
]:

    # Validate Argument
    assert any(isinstance(temperature, valid_type) for valid_type in [int, float])
    assert temperature > 0

    # Determine Local Angle from Nearby Temperatures
    nearby_temperatures = (
        max([TEMPERATURES[0], temperature - 100]),
        temperature,
        min([temperature + 100, TEMPERATURES[-1]])
    )
    nearby_chromaticities = tuple(
        tuple(
            float(interpolator(nearby_temperature))
            for interpolator in uv_chromaticity_from_temperature
        )
        for nearby_temperature in nearby_temperatures
    )
    angle = arctan2(
        nearby_chromaticities[2][1] - nearby_chromaticities[0][1], # delta-y
        nearby_chromaticities[2][0] - nearby_chromaticities[0][0] # delta-x
    )

    # Determine Endpoint Chromaticities in (u, v) Space
    uv_chromaticities = tuple(
        (
            nearby_chromaticities[1][0] + 0.05 * cos(angle + rotation),
            nearby_chromaticities[1][1] + 0.05 * sin(angle + rotation)
        )
        for rotation in [-pi / 2.0, pi / 2.0]
    )

    # Return
    return (
        tuple(
            uv_to_xy(*uv_chromaticity)
            for uv_chromaticity in uv_chromaticities
        ),
        uv_chromaticities
    )

# endregion

# region Functions - Correlated Color Temperature
def distance_to_temperature(
    temperature : Union[int, float, ndarray], # (K) - ndarray for fmin()
    u : float,
    v : float
) -> float: # distance in (u, v) space

    # Validate Arguments
    assert any(isinstance(temperature, valid_type) for valid_type in [int, float, ndarray])
    assert temperature > 0
    assert isinstance(u, float)
    assert 0.0 <= u <= 1.0
    assert isinstance(v, float)
    assert 0.0 <= v <= 1.0

    # Determine Chromaticity for Temperature
    temperature_chromaticity = tuple(
        float(interpolator(temperature))
        for interpolator in uv_chromaticity_from_temperature
    )

    # Estimate and Return Distance
    return (
        (temperature_chromaticity[0] - u) ** 2.0
        + (temperature_chromaticity[1] - v) ** 2.0
    ) ** 0.5

def correlated_color_temperature(
    u : float,
    v : float
) -> Tuple[float, float, bool]: # (Temperature, Distance, Valid)

    # Validate Arguments
    assert isinstance(u, float)
    assert 0.0 <= u <= 1.0
    assert isinstance(v, float)
    assert 0.0 <= v <= 1.0

    # Solve by Minimum Distance
    solution = fmin(
        func = distance_to_temperature,
        x0 = 6000,
        args = (u, v),
        full_output = True, # to get best distance
        disp = False # to omit console message
    )
    temperature = int(solution[0])
    distance = solution[1]

    # Return
    return (
        temperature,
        distance,
        TEMPERATURES[0] <= temperature <= TEMPERATURES[-1] and distance <= 0.05
    )

# endregion

# region Demonstration
if __name__ == '__main__':

    chromaticity_6500 = chromaticity_from_temperature(6500)
    print(
        '\n{0}\n{1}\n{2}'.format(
            'Chromaticity of 6,500 K:',
            'CIE 1931 - ({0:0.4f}, {1:0.4f})'.format(
                *chromaticity_6500[0]
            ),
            'CIE 1960 - ({0:0.4f}, {1:0.4f})'.format(
                *chromaticity_6500[1]
            )
        )
    )

    isotherm_endpoints = isotherm_endpoints_from_temperature(6500)
    print(
        '\n{0}\n{1}\n{2}'.format(
            'Isotherm Endpoints for 6,500 K:',
            'CIE 1931 - ({0:0.4f}, {1:0.4f}) to ({2:0.4f}, {3:0.4f})'.format(
                *isotherm_endpoints[0][0],
                *isotherm_endpoints[0][1]
            ),
            'CIE 1960 - ({0:0.4f}, {1:0.4f}) to ({2:0.4f}, {3:0.4f})'.format(
                *isotherm_endpoints[1][0],
                *isotherm_endpoints[1][1]
            )
        )
    )

    d65_temperature = correlated_color_temperature(
        *xy_to_uv(0.31271, 0.32902) # D65
    )
    print(
        '\n{0}\n{1}'.format(
            'Estimated Correlated Color Temperature for D65',
            '~{0:,} K (distance = {1:0.4f} and {2}within temperature range, {3}valid)'.format(
                d65_temperature[0],
                d65_temperature[1],
                '' if TEMPERATURES[0] <= d65_temperature[0] <= TEMPERATURES[-1] else 'not ',
                '' if d65_temperature[2] else 'in'
            )
        )
    )

# endregion
