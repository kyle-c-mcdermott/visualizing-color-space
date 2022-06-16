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

# Project folder
# from sys import path; path.append('../') # To access figure module

# region Settings

# endregion

# region Imports
from os import walk, chdir, getcwd
from os.path import dirname
from pandas import read_excel
from csv import DictWriter
from numpy import nanmean
from scipy.interpolate import interp1d

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
