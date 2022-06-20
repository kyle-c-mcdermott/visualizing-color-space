"""
Function returns tristimulus values and chromaticity coordinates estimated from
the input spectrum.  An optional argument specifies the CIE standard to be used
(defaults to CIE 1931 2-Degree).  Interpolation is used to get color matching
function values corresponding to the wavelengths/wave-numbers of the input
spectrum.  Extrapolation beyond the range of either the color matching functions
or the input spectrum are avoided.
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
from csv import DictReader
from typing import Union, List, Tuple, Optional
from numpy import ndarray, transpose, trapz
from scipy.interpolate import interp1d
# endregion

# region Constants
FUNCTION_NAMES = ['X', 'Y', 'Z']
# endregion

# region Load Color Matching Functions
color_matching_functions = dict()
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
    color_matching_functions['1931'] = list(
        {
            'Wavelength' : int(row['Wavelength']),
            'X' : float(row['X']),
            'Y' : float(row['Y']),
            'Z' : float(row['Z'])
        }
        for row in DictReader(
            read_file,
            fieldnames = ['Wavelength', 'X', 'Y', 'Z']
        )
    )

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
    color_matching_functions['1964'] = list(
        {
            'Wavelength' : int(row['Wavelength']),
            'X' : float(row['X']),
            'Y' : float(row['Y']),
            'Z' : float(row['Z'])
        }
        for row in DictReader(
            read_file,
            fieldnames = ['Wavelength', 'X', 'Y', 'Z']
        )
    )

"""
Tabulated color matching functions for CIE 170-2 2-degree downloaded from:
http://www.cvrl.org/ciexyzpr.htm
Under "Colour matching functions", "2-deg XYZ CMFs transformed from the CIE
(2006) 2-deg LMS cone fundamentals" using 1 nm Stepsize and csv Format
"""
with open(
    'cvrl/lin2012xyz10e_1_7sf.csv',
    'r'
) as read_file:
    color_matching_functions['170_2_2_deg'] = list(
        {
            'Wavelength' : int(row['Wavelength']),
            'X' : float(row['X']),
            'Y' : float(row['Y']),
            'Z' : float(row['Z'])
        }
        for row in DictReader(
            read_file,
            fieldnames = ['Wavelength', 'X', 'Y', 'Z']
        )
    )

"""
Tabulated color matching functions for CIE 170-2 10-degree downloaded from:
http://www.cvrl.org/ciexyzpr.htm
Under "Colour matching functions", "10-deg XYZ CMFs transformed from the CIE
(2006) 2-deg LMS cone fundamentals" using 1 nm Stepsize and csv Format
"""
with open(
    'cvrl/lin2012xyz10e_1_7sf.csv',
    'r'
) as read_file:
    color_matching_functions['170_2_10_deg'] = list(
        {
            'Wavelength' : int(row['Wavelength']),
            'X' : float(row['X']),
            'Y' : float(row['Y']),
            'Z' : float(row['Z'])
        }
        for row in DictReader(
            read_file,
            fieldnames = ['Wavelength', 'X', 'Y', 'Z']
        )
    )

# endregion

# region Function
def chromaticity_from_spectrum(
    spectrum : Union[ # A list/tuple of list/tuple pairs
        List[Union[List[Union[int, float]], Tuple[Union[int, float], ...]]],
        Tuple[Union[List[Union[int, float]], Tuple[Union[int, float], ...]], ...],
        ndarray
    ],
    color_unit : Optional[str] = None, # default "wavelength", "wave-number" allowed
    standard : Optional[str] = None # default "1931", "1964", "170_2_10_deg", and "170_2_2_deg" allowed
) -> Tuple[Tuple[float, float, float], Tuple[float, float]]: # ((X, Y, Z), (x, y))

    # region Validate Arguments
    assert any(isinstance(spectrum, valid_type) for valid_type in [list, tuple, ndarray])
    if isinstance(spectrum, ndarray):
        assert len(spectrum.shape) == 2
        assert any(dimension == 2 for dimension in spectrum.shape)
        if spectrum.shape[1] != 2: spectrum = transpose(spectrum)
    else:
        assert len(spectrum) > 0
        assert all(len(pair) == 2 for pair in spectrum)
    assert all(
        all(
            any(
                isinstance(value, valid_type)
                for valid_type in [int, float]
            )
            for value in pair
        )
        for pair in spectrum
    )
    assert all(all(value >= 0.0 for value in pair) for pair in spectrum)
    assert len(set(transpose(spectrum)[0])) == len(spectrum) # No repeated colors
    if color_unit is None: color_unit = 'wavelength'
    assert isinstance(color_unit, str)
    assert len(color_unit) > 0
    assert color_unit in ['wavelength', 'wave-number']
    if standard is None: standard = '1931'
    assert isinstance(standard, str)
    assert len(standard) > 0
    assert standard in ['1931', '1964', '170_2_10_deg', '170_2_2_deg']
    # endregion

    # region (Convert to Wavelength)
    if color_unit != 'wavelength':
        spectrum = list(
            (
                (10.0 ** 7.0) / pair[0],
                pair[1]
            )
            for pair in spectrum
        )
    # endregion

    # region (Sort and Clip Spectrum)
    spectrum = sorted(spectrum, key = lambda pair: pair[0])
    if (
        spectrum[0][0] < color_matching_functions[standard][0]['Wavelength']
        or spectrum[-1][0] > color_matching_functions[standard][-1]['Wavelength']
    ):
        spectrum = list(
            pair
            for pair in spectrum
            if (
                color_matching_functions[standard][0]['Wavelength']
                <= pair[0]
                <= color_matching_functions[standard][-1]['Wavelength']
            )
        )
    # endregion

    # region (Interpolate Color Matching Functions)
    if all(
        pair[0] in list(
            datum['Wavelength']
            for datum in color_matching_functions[standard]
        )
        for pair in spectrum
    ):
        use_cmf = list(
            datum
            for datum in color_matching_functions[standard]
            if datum['Wavelength'] in transpose(spectrum)[0]
        )
    else:
        interpolators = {
            function_name : interp1d(
                list(datum['Wavelength'] for datum in color_matching_functions[standard]),
                list(datum[function_name] for datum in color_matching_functions[standard])
            )
            for function_name in FUNCTION_NAMES
        }
        use_cmf = list(
            {
                'Wavelength' : pair[0],
                **{
                    function_name : float(function_interpolator(pair[0]))
                    for function_name, function_interpolator in interpolators.items()
                }
            }
            for pair in spectrum
        )
    # endregion

    # region Integrate Product
    tristimulus_values = {
        function_name : trapz(
            list(
                pair[1] * use_cmf[pair_index][function_name]
                for pair_index, pair in enumerate(spectrum)
            ),
            x = transpose(spectrum)[0]
        )
        for function_name in FUNCTION_NAMES
    }
    # endregion

    # region Return
    return (
        (
            tristimulus_values['X'],
            tristimulus_values['Y'],
            tristimulus_values['Z']
        ),
        (
            tristimulus_values['X']
            / (
                tristimulus_values['X']
                + tristimulus_values['Y']
                + tristimulus_values['Z']
            ),
            tristimulus_values['Y']
            / (
                tristimulus_values['X']
                + tristimulus_values['Y']
                + tristimulus_values['Z']
            )
        )
    )
    # endregion

# endregion

# region Demonstration
if __name__ == '__main__':
    with open(
        'cvrl/Illuminantd65.csv',
        'r'
    ) as read_file:
        d65_spectrum = list(
            (
                int(row['Wavelength']),
                float(row['Energy'])
            )
            for row in DictReader(
                read_file,
                fieldnames = ['Wavelength', 'Energy']
            )
        )
    d65_chromaticity = chromaticity_from_spectrum(
        d65_spectrum,
        standard = '170_2_2_deg'
    )
    print(
        '\nD65 Tristimulus Values (170-2 2-deg):\nX = {0:0.0f}\nY = {1:0.0f}\nZ = {2:0.0f}'.format(
            *d65_chromaticity[0]
        )
    )
    print(
        'D65 Chromaticity (170-2 2-deg) = ({0:0.4f}, {1:0.4f})'.format(
            *d65_chromaticity[1]
        )
    )
# endregion
