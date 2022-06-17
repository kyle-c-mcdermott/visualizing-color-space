"""
Derives the CIE 170-2 10-Degree Standard Observer Color Matching Functions
(derived from the CIE 2006 physiologically-relevant Cone Fundamentals, also
here derived, and also called the CIE 2012 physiologically-relevant Color
Matching Functions) from the original (corrected) Stiles & Burch 1959 color
matching experiment data from 49 observers (53 observations - some observers
doubled across two experimental conditions).

Tabulated data and coefficients are taken from the Color & Vision Research
Laboratory website (http://www.cvrl.org/)
"""

# Project folder (to access other modules from project or sub-folder)
from sys import path; path.append('.'); path.append('../')

# region Settings

# endregion

# region Imports
from os import walk, chdir, getcwd
from os.path import dirname
from pandas import read_excel
from csv import DictWriter, DictReader
from numpy import nanmean, around, std, matmul, arange
from scipy.interpolate import interp1d
from numpy.linalg import inv

from pprint import pprint
# endregion

# region (Ensure Correct Working Directory)
folders = list()
while True:
    for root, dirs, files in walk('.'):
        folders += list(name for name in dirs)
    if 'cvrl' not in folders:
        chdir(dirname(getcwd())) # Move up one
    else:
        break
# endregion

# region Constants
COLOR_NAMES = ['Red', 'Green', 'Blue']
CONE_NAMES = ['Long', 'Medium', 'Short']

"""
10-Degree Cone Fundamentals Conversion Coefficients Detailed here:
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
RGB_TO_UNSCALED_LMS = [
    [2.846201, 11.092490, 1.000000], # L_R/L_B, L_G/L_B, L_B/L_B (= 1.0)
    [0.168926, 8.265895, 1.000000], # M_R/M_B, M_G/M_B, M_B/M_B (= 1.0)
    [0.000000, 0.010600, 1.000000] # S_R/S_B (= 0.0), S_G/S_B, S_B/S_B (= 1.0)
]

# endregion

# region Load in Color Matching Experiment Data
"""
Stiles & Burch (1959) dataset page:
http://www.cvrl.org/stilesburch10_ind.htm
Dataset spreadsheet:
http://www.cvrl.org/database/data/sb_individual/SB10_corrected_indiv_CMFs.xls
stored as SB10_corrected_indiv_CMFs.xls in /cvrl folder
"""
individual_data = read_excel(
    'cvrl/SB10_corrected_indiv_CMFs.xls',
    sheet_name = 'Corrected Data'
).drop(
    [0, 1, 2, 3, 4, 5] # Dropping header rows
).to_numpy(
    dtype = float
).transpose() # Swapping axes
"""
individual_data[0] is wave-number in 1/cm
individual_data[1] is wavelength in nm (unused, will convert from wave-number)
individual_data[2:5] is red, green, and blue primary settings for first observer
individual_data[5:8] is red, green, and blue primary settings for second observer
etc.
"""
# endregion

# region Save Color Matching Experiment Data for Use in Plotting
individual_data = list(
    {
        'Wave-Number' : int(individual_data[0][wave_number_index]),
        **{
            '{0:02}-{1}'.format(
                observer_index + 1,
                color_name
            ) : individual_data[2 + (observer_index * 3) + color_index][wave_number_index]
            for observer_index in range(int((individual_data.shape[0] - 2) / 3))
            for color_index, color_name in enumerate(COLOR_NAMES)
        }
    }
    for wave_number_index in range(individual_data.shape[1])
)
with open(
    'data/individual_observer_settings.csv',
    'w',
    newline = ''
) as write_file:
    writer = DictWriter(
        write_file,
        fieldnames = individual_data[0].keys()
    )
    writer.writeheader()
    writer.writerows(individual_data)
# endregion

# region Average Setting Values across All Observers and Save
mean_data = list(
    {
        'Wave-Number' : individual_data[wave_number_index]['Wave-Number'],
        **{
            color_name : nanmean(
                list(
                    value
                    for key, value in individual_data[wave_number_index].items()
                    if color_name in key
                )
            )
            for color_name in COLOR_NAMES
        }
    }
    for wave_number_index in range(len(individual_data))
)
with open(
    'data/mean_observer_settings.csv',
    'w',
    newline = ''
) as write_file:
    writer = DictWriter(
        write_file,
        fieldnames = mean_data[0].keys()
    )
    writer.writeheader()
    writer.writerows(mean_data)
# endregion

# region Verify Averages
"""
Tabulated means downloaded from:
http://www.cvrl.org/stilesburch10_ind.htm
Using the "E/F" button under "Stiles & Burch (1959)10-deg, RGB CMFs"
"""
with open(
    'cvrl/sbrgb10f.csv',
    'r'
) as read_file:
    verification_mean_data = list( # Will leave out extra interpolated rows
        {
            'Wave-Number' : int(row['Wave-Number']),
            'Red' : float(row['Red']),
            'Green' : float(row['Green']),
            'Blue' : float(row['Blue'])
        }
        for row in DictReader(
            read_file,
            fieldnames = ['Wave-Number', 'Wavelength', 'Red', 'Green', 'Blue']
        )
        if int(row['Wave-Number']) in list(mean_datum['Wave-Number'] for mean_datum in mean_data)
    )
errors = list(
    abs(
        around(mean_datum[color_name], 4)
        - verification_mean_data[datum_index][color_name]
    )
    for datum_index, mean_datum in enumerate(mean_data)
    for color_name in COLOR_NAMES
)
print('\nMean Experiment Settings Verification:')
print('Mean Error: {0:0.4f}'.format(nanmean(errors)).rjust(32))
print('Max Error: {0:0.4f}'.format(max(errors)).rjust(32))
print('Error Standard Deviation: {0:0.4f}'.format(std(errors)))
"""
The largest discrepancy is around 17,000 cm^-1 in the mean Red settings.  This
may be a transcription issue since the tabulated values from CVRL seem to be
unusually rounded in this part of the table (perhaps the latter digits were
illegible?).
"""
# endregion

# region Transform Mean Settings into Unscaled Cone Fundamentals and Save
unscaled_cone_fundamentals = list(
    {
        'Wave-Number' : mean_datum['Wave-Number'],
        **{
            CONE_NAMES[value_index] : max([0.0, value]) # Some slightly negative values appear, here clipped
            for value_index, value in enumerate(
                matmul(
                    RGB_TO_UNSCALED_LMS,
                    list(
                        mean_datum[color_name]
                        for color_name in COLOR_NAMES
                    )
                )
            )
        }
    }
    for mean_datum in mean_data
)
with open(
    'data/unscaled_cone_fundamentals.csv',
    'w',
    newline = ''
) as write_file:
    writer = DictWriter(
        write_file,
        fieldnames = unscaled_cone_fundamentals[0].keys()
    )
    writer.writeheader()
    writer.writerows(unscaled_cone_fundamentals)
# endregion

# region Estimate Normalization Constants for Cone Fundamentals
"""
CVRL share tabulated data for the scaled cone fundamentals here:
http://www.cvrl.org/cones.htm
Under "10-deg fundamentals based on the Stiles & Burch 10-deg CMFs" with units
set to "Energy (linear)" the three files are linss10e_5.csv (5nm wavelength
steps), linss10e_1.csv (1nm wavelength steps), and linss10e_fine.csv (0.1nm
steps).  In the sparsest sampling (5nm) not all cone sensitivity series peak at
exactly 1.0, therefore we will interpolate at 1nm intervals to determine the
constants k and then verify the scaled cone fundamentals with their data with
the same 1nm sampling.
"""

# Convert Wave-Number to Wavelength
unscaled_cone_fundamentals = list(
    {
        'Wavelength' : (10.0 ** 7.0) / datum['Wave-Number'],
        **{
            cone_name : datum[cone_name]
            for cone_name in CONE_NAMES
        }
    }
    for datum in unscaled_cone_fundamentals
)

# Build Interpolators
unscaled_cone_interpolators = {
    cone_name : interp1d(
        list(datum['Wavelength'] for datum in unscaled_cone_fundamentals),
        list(datum[cone_name] for datum in unscaled_cone_fundamentals),
        kind = 'quadratic' # This may bump up the maximum value slightly, so interpolation is done before normalization
    )
    for cone_name in CONE_NAMES
}

# Sample at 1 nm Steps within Valid Range (no extrapolation)
unscaled_cone_fundamentals = list(
    {
        'Wavelength' : int(wavelength),
        **{
            cone_name : max([0.0, float(cone_interpolator(int(wavelength)))]) # Interpolation causes some dips below zero
            for cone_name, cone_interpolator in unscaled_cone_interpolators.items()
        }
    }
    for wavelength in arange(
        int(unscaled_cone_fundamentals[0]['Wavelength']) + 1, # rounding up
        int(unscaled_cone_fundamentals[-1]['Wavelength']) + 0.1,
        1
    ) # Yields the interval [393, 714]
)

# Determine Normalization Constants k
constants_k = {
    cone_name : max(
        list(datum[cone_name] for datum in unscaled_cone_fundamentals)
    )
    for cone_name in CONE_NAMES
}
print('\nNormalization Constants k:')
for cone_name, cone_constant in constants_k.items():
    print('{0}: {1}'.format(cone_name.rjust(6), str(around(cone_constant, 6)).rjust(9)))

# endregion

# region Normalize Cone Fundamentals and Save
cone_fundamentals = list(
    {
        'Wavelength' : datum['Wavelength'],
        **{
            cone_name : datum[cone_name] / constants_k[cone_name]
            for cone_name in CONE_NAMES
        }
    }
    for datum in unscaled_cone_fundamentals
)
with open(
    'data/cone_fundamentals.csv',
    'w',
    newline = ''
) as write_file:
    writer = DictWriter(
        write_file,
        fieldnames = cone_fundamentals[0].keys()
    )
    writer.writeheader()
    writer.writerows(cone_fundamentals)
# endregion

# region Verify Cone Fundamentals
"""
Tabulated means downloaded from:
http://www.cvrl.org/cones.htm
Under "10-deg fundamentals based on the Stiles & Burch 10-deg CMFs" using
Energy (linear) Units, 1nm Stepsize and csv Format
"""
with open(
    'cvrl/linss10e_1.csv',
    'r'
) as read_file:
    verification_fundamentals = list( # Will leave out extra extrapolated rows
        {
            'Wavelength' : int(row['Wavelength']),
            'Long' : float(row['Long']),
            'Medium' : float(row['Medium']),
            'Short' : float(row['Short']) if len(row['Short']) > 0 else 0.0
        }
        for row in DictReader(
            read_file,
            fieldnames = ['Wavelength', 'Long', 'Medium', 'Short']
        )
        if int(row['Wavelength']) in list(datum['Wavelength'] for datum in cone_fundamentals)
    )
errors = list(
    abs(
        around(datum[cone_name], 6)
        - verification_fundamentals[datum_index][cone_name]
    )
    for datum_index, datum in enumerate(cone_fundamentals)
    for cone_name in CONE_NAMES
)
print('\nScaled Cone Fundamentals Verification:')
print('Mean Error: {0:0.4f}'.format(nanmean(errors)).rjust(32))
print('Max Error: {0:0.4f}'.format(max(errors)).rjust(32))
print('Error Standard Deviation: {0:0.4f}'.format(std(errors)))
"""
The largest discrepancy is around 450 and 460 in the short cone sensitivity
series - cause unknown (not quite 2% error)
"""
# endregion

# region Factor Normalization Constants and Print/Save New Transform Coefficients
rgb_to_scaled_lms = list(
    list(
        value / constants_k[CONE_NAMES[cone_index]]
        for value in row
    )
    for cone_index, row in enumerate(RGB_TO_UNSCALED_LMS)
)
scaled_lms_to_rgb = inv(rgb_to_scaled_lms)
print('\nLinear Transform Coefficients RGB to Scaled LMS:')
for cone_index, cone_name in enumerate(CONE_NAMES):
    print(
        '{0}_R: {1:0.6f}, {0}_G: {2:0.6f}, {0}_B: {3:0.6f}'.format(
            cone_name[0],
            *rgb_to_scaled_lms[cone_index]
        )
    )
print('\nLinear Transform Coefficients Scaled LMS to RGB:')
for color_index, color_name in enumerate(COLOR_NAMES):
    print(
        '{0}_L: {1:0.6f}, {0}_M: {2:0.6f}, {0}_S: {3:0.6f}'.format(
            color_name[0],
            *scaled_lms_to_rgb[color_index]
        )
    )
with open(
    'data/rgb_to_scaled_fundamentals.csv',
    'w',
    newline = ''
) as write_file:
    writer = DictWriter(
        write_file,
        fieldnames = COLOR_NAMES
    )
    writer.writeheader()
    writer.writerows(
        list(
            {
                color_name : row[color_index]
                for color_index, color_name in enumerate(COLOR_NAMES)
            }
            for row in rgb_to_scaled_lms
        )
    )
# endregion
