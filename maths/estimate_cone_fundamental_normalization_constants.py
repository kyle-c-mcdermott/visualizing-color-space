"""
Using conversion coefficients reported by Stockman, Sharpe, & Fach (1999) and
Stockman & Sharpe (2000), transform color matching experiment mean settings into
unnormalized cone fundamentals.  Using quadratic spline interpolation, smooth
and determine the peaks of the unnormalized sensitivities (to the nearest whole
nanometer of wavelength).  Apply the normalized linear transformation and
compare the resulting series to the tabulated data from CVRL.

Errors persist despite different methods of interpolation or samling density.
It is suspected that there may be some transcription errors in the tabulated
data online (oddly rounded values in some places) that may be responsible for
the largest errors, however the source of the general mismatch is unknown.
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
from maths.plotting_series import (
    color_matching_experiment_mean_settings,
    cone_fundamentals_10
)
from maths.color_conversion import rgb_to_lms
from maths.conversion_coefficients import (
    COLOR_NAMES,
    CONE_NAMES,
    RGB_TO_UNSCALED_LMS_10
)
from scipy.interpolate import interp1d
from numpy import mean, std
# endregion

# region Transform Mean Settings into Unnormalized Cone Fundamentals
unnormalized_cone_fundamentals = list()
for datum in color_matching_experiment_mean_settings:
    cone_fundamentals = rgb_to_lms(
        *list(
            datum[color_name]
            for color_name in COLOR_NAMES
        ),
        normalize_fundamentals = False
    )
    unnormalized_cone_fundamentals.append(
        {
            'Wavelength' : datum['Wavelength'],
            **{
                cone_name : cone_fundamentals[cone_index]
                for cone_index, cone_name in enumerate(CONE_NAMES)
            }
        }
    )
# endregion

# region Build Interpolators and Determine Wavelengths of Peaks
unnormalized_interpolators = {
    cone_name : interp1d(
        list(datum['Wavelength'] for datum in unnormalized_cone_fundamentals),
        list(datum[cone_name] for datum in unnormalized_cone_fundamentals),
        kind = 'quadratic'
    )
    for cone_name in CONE_NAMES
}
interpolated_unnormalized_cone_fundamentals = list(
    {
        'Wavelength' : wavelength,
        **{
            cone_name : float(cone_interpolator(wavelength))
            for cone_name, cone_interpolator in unnormalized_interpolators.items()
        }
    }
    for wavelength in list(
        datum['Wavelength']
        for datum in cone_fundamentals_10
        if (
            color_matching_experiment_mean_settings[0]['Wavelength']
            <= datum['Wavelength']
            <= color_matching_experiment_mean_settings[-1]['Wavelength']
        )
    )
)
unnormalized_maxima = {
    cone_name : max(
        list(datum[cone_name] for datum in interpolated_unnormalized_cone_fundamentals)
    )
    for cone_name in CONE_NAMES
}
peak_wavelengths = {
    cone_name : list(
        datum['Wavelength'] for datum in interpolated_unnormalized_cone_fundamentals
        if datum[cone_name] == unnormalized_maxima[cone_name]
    )[0]
    for cone_name in CONE_NAMES
}
print('\nNormalization Constants k:')
for cone_name, cone_maximum in unnormalized_maxima.items():
    print(
        'k ({0}) = {1:0.6f} (at {2:0.0f} nm)'.format(
            cone_name,
            cone_maximum,
            peak_wavelengths[cone_name]
        )
    )
# endregion

# region Factor and Print out Linear Transformation Coefficients
print('\nNormalized Cone Fundamentals Linear Transformation Coefficients:')
for cone_index, row in enumerate(RGB_TO_UNSCALED_LMS_10):
    print(
        '{0:0.6f}, {1:0.6f}, {2:0.6f}'.format(
            *list(
                column_value / unnormalized_maxima[CONE_NAMES[cone_index]]
                for column_value in row
            )
        )
    )
# endregion

# region Transform Mean Settings into Normalized Cone Fundamentals
"""
The above derived constants are built into rgb_to_lms() already
"""
normalized_cone_fundamentals = list()
for datum in color_matching_experiment_mean_settings:
    cone_fundamentals = rgb_to_lms(
        *list(
            datum[color_name]
            for color_name in COLOR_NAMES
        ),
        normalize_fundamentals = True
    )
    normalized_cone_fundamentals.append(
        {
            'Wavelength' : datum['Wavelength'],
            **{
                cone_name : cone_fundamentals[cone_index]
                for cone_index, cone_name in enumerate(CONE_NAMES)
            }
        }
    )
# endregion

# region Build Interpolators
normalized_interpolators = {
    cone_name : interp1d(
        list(datum['Wavelength'] for datum in normalized_cone_fundamentals),
        list(datum[cone_name] for datum in normalized_cone_fundamentals),
        kind = 'quadratic'
    )
    for cone_name in CONE_NAMES
}
# endregion

# region Report on Error Relative to CVRL Tabulated Data
errors = {
    cone_name : list(
        datum[cone_name] - normalized_interpolators[cone_name](datum['Wavelength'])
        for datum in cone_fundamentals_10
        if (
            color_matching_experiment_mean_settings[0]['Wavelength']
            <= datum['Wavelength']
            <= color_matching_experiment_mean_settings[-1]['Wavelength']
        )
    )
    for cone_name in CONE_NAMES
}
print('\nError Report:')
for cone_name, cone_errors in errors.items():
    print(
        '{0} Cone Mean Error {1:0.4f} (+/-{2:0.4f}) in the interval [{3:0.4f}, {4:0.4f}]'.format(
            cone_name,
            mean(cone_errors),
            std(cone_errors),
            min(cone_errors),
            max(cone_errors)
        )
    )
print('(Note normalized sensitivites are in the interval [0, 1] - all errors less than 2%)')
# endregion
