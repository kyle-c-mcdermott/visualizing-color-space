"""
Tabulated data loaded from files and other useful series for plotting.
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
from pandas import read_excel
from numpy import arange, transpose
from maths.conversion_coefficients import (
    COLOR_NAMES,
    CONE_NAMES,
    TRISTIMULUS_NAMES,
    SRGB_TO_XYZ_2,
    RGB_TO_XYZ_CRT_10,
    RGB_TO_XYZ_CUSTOM_INTERIOR,
    RGB_TO_XYZ_CUSTOM_EXTERIOR
)
from csv import DictReader
# endregion

# region Tabulated Data from the Colour & Vision Research Laboratory

# region Load - Color Matching Experiment Data (Individual Observer Settings)
"""
Stiles & Burch (1959) dataset page:
http://www.cvrl.org/stilesburch10_ind.htm
Dataset spreadsheet:
http://www.cvrl.org/database/data/sb_individual/SB10_corrected_indiv_CMFs.xls
"""
color_matching_experiment_individual_settings = read_excel(
    'cvrl/SB10_corrected_indiv_CMFs.xls',
    sheet_name = 'Corrected Data'
).drop(
    [0, 1, 2, 3, 4, 5] # Dropping header rows
).to_numpy(
    dtype = float
)
"""
In each row:
index 0 is wave-number in 1/cm
index 1 is wavelength in nm (unused, will convert from wave-number)
indices 2:5 are red, green, and blue primary settings for first observer
indices 5:8 are red, green, and blue primary settings for second observer
etc.
"""
color_matching_experiment_individual_settings = list(
    {
        'Wave-Number' : int(row[0]),
        'Wavelength' : (10.0 ** 7.0) / row[0], # Skipping their approximated values
        **{
            '{0:02.0f}-{1}'.format(
                observer_index,
                color_name
            ) : row[int(column_index + color_index)]
            for observer_index, column_index in enumerate(arange(2, len(row), 3))
            for color_index, color_name in enumerate(COLOR_NAMES)
        }
    }
    for row in color_matching_experiment_individual_settings
)
"""
In each row:
['Wave-Number'] is wave-number in 1/cm
['Wavelength'] is wavelength in nm
['XX-Red'] is observer XX red setting (XX from 00 to 52)
['XX-Green'] is observer XX green setting (XX from 00 to 52)
['XX-Blue'] is observer XX blue setting (XX from 00 to 52)
"""
# endregion

# region Load - Color Matching Experiment Data (Mean Settings)
"""
Tabulated mean data found here (see Stiles & Burch (1959) 10-deg, RGB CMFs -
use E/F button to download sbrgb10f.csv):
http://www.cvrl.org/stilesburch10_ind.htm
Description page:
http://www.cvrl.org/database/text/cmfs/sbrgb10.htm
"""
with open(
    'cvrl/sbrgb10f.csv',
    'r'
) as read_file:
    color_matching_experiment_mean_settings = list(
        {
            'Wave-Number' : int(row['Wave-Number']),
            'Wavelength' : (10.0 ** 7.0) / int(row['Wave-Number']),
            **{
                color_name : float(row[color_name])
                for color_name in COLOR_NAMES
            }
        }
        for row in DictReader(
            read_file,
            fieldnames = ['Wave-Number', 'Wavelength', *COLOR_NAMES]
        )
        if int(row['Wave-Number']) in list(datum['Wave-Number'] for datum in color_matching_experiment_individual_settings)
    )
"""
The tabulated data retrieved from CVRL have interpolated wave-numbers to fill
gaps where original stimulus sampling was more sparse.  Those extra,
interpolated rows are here being omitted.
"""
# endregion

# region Load - 10-Degree Cone Fundamentals
"""
Tabulated cone fundamentals downloaded from:
http://www.cvrl.org/cones.htm
Under "10-deg fundamentals based on the Stiles & Burch 10-deg CMFs" using
Energy (linear) Units, 1nm Stepsize and csv Format
"""
with open(
    'cvrl/linss10e_1.csv',
    'r'
) as read_file:
    cone_fundamentals_10 = list(
        {
            'Wavelength' : int(row['Wavelength']),
            **{
                cone_name : float(row[cone_name]) if len(row[cone_name]) > 0 else 0.0
                for cone_name in CONE_NAMES
            }
        }
        for row in DictReader(
            read_file,
            fieldnames = ['Wavelength', *CONE_NAMES]
        )
    )
# endregion

# region Load - Color Matching Functions - CIE 170-2 10-Degree
"""
Tabulated color matching functions downloaded from:
http://www.cvrl.org/ciexyzpr.htm
Under "10-deg XYZ CMFs transformed from the CIE (2006) 10-deg LMS cone fundamentals"
using 1 nm Stepsize and csv Format
"""
with open(
    'cvrl/lin2012xyz10e_1_7sf.csv',
    'r'
) as read_file:
    color_matching_functions_170_2_10 = list(
        {
            'Wavelength' : int(row['Wavelength']),
            **{
                tristimulus_name : float(row[tristimulus_name])
                for tristimulus_name in TRISTIMULUS_NAMES
            }
        }
        for row in DictReader(
            read_file,
            fieldnames = ['Wavelength', *TRISTIMULUS_NAMES]
        )
    )
# endregion

# region Load - Color Matching Functions - CIE 170-2 2-Degree
"""
Tabulated color matching functions for CIE 170-2 2-degree downloaded from:
http://www.cvrl.org/ciexyzpr.htm
Under "Colour matching functions", "2-deg XYZ CMFs transformed from the CIE
(2006) 2-deg LMS cone fundamentals" using 1 nm Stepsize and csv Format
"""
with open(
    'cvrl/lin2012xyz2e_1_7sf.csv',
    'r'
) as read_file:
    color_matching_functions_170_2_2 = list(
        {
            'Wavelength' : int(row['Wavelength']),
            **{
                tristimulus_name : float(row[tristimulus_name])
                for tristimulus_name in TRISTIMULUS_NAMES
            }
        }
        for row in DictReader(
            read_file,
            fieldnames = ['Wavelength', *TRISTIMULUS_NAMES]
        )
    )
# endregion

# region Load - Color Matching Functions - CIE 1964 10-Degree
"""
Tabulated color matching functions for CIE 1964 10-degree downloaded from:
http://www.cvrl.org/cie.htm
Under "Colour matching functions", "CIE 1964 10-deg, XYZ CMFs" using the second,
"/W" (solid line indiciating fine resolution as opposed to dotted line) button
"""
with open(
    'cvrl/ciexyz64_1.csv',
    'r'
) as read_file:
    color_matching_functions_1964_10 = list(
        {
            'Wavelength' : int(row['Wavelength']),
            **{
                tristimulus_name : float(row[tristimulus_name])
                for tristimulus_name in TRISTIMULUS_NAMES
            }
        }
        for row in DictReader(
            read_file,
            fieldnames = ['Wavelength', *TRISTIMULUS_NAMES]
        )
    )
# endregion

# region Load - Color Matching Functions - CIE 1931 2-Degree
"""
Tabulated color matching functions for CIE 1931 2-degree downloaded from:
http://www.cvrl.org/cie.htm
Under "Colour matching functions", "CIE 1931 2-deg, XYZ CMFs" using the second,
"/W" (solid line indiciating fine resolution as opposed to dotted line) button
"""
with open(
    'cvrl/ciexyz31_1.csv',
    'r'
) as read_file:
    color_matching_functions_1931_2 = list(
        {
            'Wavelength' : int(row['Wavelength']),
            **{
                tristimulus_name : float(row[tristimulus_name])
                for tristimulus_name in TRISTIMULUS_NAMES
            }
        }
        for row in DictReader(
            read_file,
            fieldnames = ['Wavelength', *TRISTIMULUS_NAMES]
        )
    )
# endregion

# region Load - CIE Standard Illuminant D65 Spectrum
"""
CIE Illuminant D65 Spectrum found on Older CIE Standards page:
http://www.cvrl.org/cie.htm
E/W button at the bottom of the page under CIE Illuminant D65
Attributed elsewhere to:
Judd, D. B., MacAdam, D. L., Wyszecki, G., Budde, H., Condit, H., Henderson, S.,
& Simonds, J. (1964). Spectral distribution of typical daylight as a function of
correlated color temperature. Josa, 54 (8), 1031-1040.
Note: from the appearance the values tabulated here appear to be interpolated
linearly from a more sparsely sampled source.
"""
with open(
    'cvrl/Illuminantd65.csv',
    'r'
) as read_file:
    d65_spectrum = list(
        {
            'Wavelength' : int(row['Wavelength']),
            'Energy' : float(row['Energy'])
        }
        for row in DictReader(
            read_file,
            fieldnames = ['Wavelength', 'Energy']
        )
    )
# endregion

# endregion

# region Estimated Spectrum Locus from Each CIE Standard Color Matching Functions
"""
The Spectrum Locus coordinates become less reliable as the color matching
function values approach zero - rounding issues can cause the path of the
spectrum locus to back-track which in turn causes problems with interpolation.
The estimated series here leave out wavelengths higher than a cutoff value -
determined by the slope of the associated hue angle changes swtiching signs -
that would be problematic for interpolation and would (if one zoomed in far
enough) be confusing when plotted.
"""
(
    spectrum_locus_170_2_10,
    spectrum_locus_170_2_2,
    spectrum_locus_1964_10,
    spectrum_locus_1931_2
) = tuple(
    list(
        {
            'Wavelength' : wavelength_datum['Wavelength'],
            'x' : (
                wavelength_datum['X']
                / sum(list(wavelength_datum[tristimulus_name] for tristimulus_name in TRISTIMULUS_NAMES))
            ),
            'y' : (
                wavelength_datum['Y']
                / sum(list(wavelength_datum[tristimulus_name] for tristimulus_name in TRISTIMULUS_NAMES))
            )
        }
        for wavelength_datum in color_matching_functions
        if wavelength_datum['Wavelength'] <= highest_wavelength
    )
    for color_matching_functions, highest_wavelength in [
        (color_matching_functions_170_2_10, 699),
        (color_matching_functions_170_2_2, 703),
        (color_matching_functions_1964_10, 701),
        (color_matching_functions_1931_2, 699)
    ]
)
# endregion

# region Load - Measured CRT Spectra
"""
Tabulated CRT Spectra recorded with a Photo Research spectroradiometer (PR650?)
many years ago (monitor specifications not recorded)
"""
with open(
    'data/crt_phosphors.csv',
    'r'
) as read_file:
    phosphor_spectra = list(
        {
            'Wavelength' : int(row['Wavelength']),
            **{
                color_name : float(row[color_name])
                for color_name in COLOR_NAMES
            }
        }
        for row in DictReader(read_file)
    )
# endregion

# region Gamut Triangle Chromaticities
(
    gamut_triangle_vertices_srgb,
    gamut_triangle_vertices_crt,
    gamut_triangle_vertices_interior,
    gamut_triangle_vertices_exterior
) = tuple(
    {
        color_name : {
            'x' : (
                transpose(coefficients)[color_index][0]
                / sum(transpose(coefficients)[color_index])
            ),
            'y' : (
                transpose(coefficients)[color_index][1]
                / sum(transpose(coefficients)[color_index])
            )
        }
        for color_index, color_name in enumerate(COLOR_NAMES)
    }
    for coefficients in [
        SRGB_TO_XYZ_2,
        RGB_TO_XYZ_CRT_10,
        RGB_TO_XYZ_CUSTOM_INTERIOR,
        RGB_TO_XYZ_CUSTOM_EXTERIOR
    ]
)
# endregion
