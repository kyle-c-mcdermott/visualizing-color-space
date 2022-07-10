# visualizing-color-space/maths
This folder contains modules with various useful functions used in deriving the
color matching functions and generating figures.
## Modules and Dependencies
- **functions.py** does not import from any other module herein
    - **intersection_of_two_segments()** does what it says
    - **conversion_matrix()** builds a 3x3 matrix of coefficients for converting
    from RGB to XYZ based on the chromaticities of red, green, and blue
    primaries and white chromaticity and luminance
- **conversion_coefficients.py** does not import from any other module herein
    - Contains constants giving name labels for colors, cones, and tristimulus
    values and the wave-numbers of the Stiles & Burch (1959) experimental
    primaries
    - Contains various 3x3 matrices of coefficients for linear transformations
- **plotting_series.py** imports from **conversion_coefficients.py**
    - Contains various series for plotting, including: color matching experiment
    data, cone fundamentals, color matching functions, spectrum loci, light
    spectra and disply color gamut chromaticity coordinates
- **color_conversion.py** imports from **conversion_coefficients.py**
    - Contains DISPLAY enum
    - **rgb_to_lms()** and **lms_to_rgb()** convert between experiment settings
    and (optionally normalized) cone activation
    - **lms_to_xyz()** and **xyz_to_lms()** convert between cone activation and
    tristimulus values
    - **xyz_to_xyy()** and **xyy_to_xyz()** convert between tristimulus values
    and chromoluminance
    - **xyz_to_rgb()** and **rgb_to_xyz()** convert between tristimulus values
    and display red/green/blue
    - **xy_to_uv()** and **uv_to_xy()** convert between CIE 1931 and CIE 1960
    chromaticity coordinates
- **chromaticity_conversion.py** imports from **plotting_series.py** and
**color_conversion.py**
    - Contains STANDARD and CENTER enums and estimated chromaticity coordinates
    for the copunctal points
    - Contains interpolators for: chromaticity from wavelength, hue angle from
    wavelength, and wavelength from hue angle
    - **wavelength_to_chromaticity()** utilizes interpolation to derive
    chromaticity from wavelength
    - **wavelength_to_hue_angle()** utilizes interpolation to derive hue angle
    (around D65) from wavelength
    - **hue_angle_to_wavelength()** utilizes interpolation to derive wavelength
    from hue angle (around D65)
    - **chromaticity_rectangular_to_polar()** does the expected coordinate
    transformation
    - **chromaticity_polar_to_rectangular()** does the expected coordinate
    transformation
- **color_temperature.py** imports from **conversion_coefficients.py**,
**plotting_series.py**, **color_conversion.py**, and
**chromaticity_conversion.py**
    - **tristimulus_from_spectrum()** derives tristimulus values from a spectrum
    (using color matching functions)
    - **radiant_emitance()** gives the blackbody radiation emitance for a given
    wavelength and temperature
    - **spectrum_from_temperature()** uses the above to build a spectrum across
    many wavelengths for a given temperature
    - **isotherm_endpoints_from_temperature()** is used for plotting isotherm
    lines for a given temperature
    - **correlated_color_temperature_from_chromaticity()** estimates the
    correlated color temperature for a given (u, v) chromaticity
    - **generate_temperature_series()** is used for plotting the Planckian locus
- **color_blind.py** imports from **functions.py**, **plotting_series.py**,
**color_conversion.py**, and **chromaticity_conversion.py**
    - Contains the CONE enum
    - **get_unique_colors()** gets all unique color values from an image along
    with a pixel count for each
    - **filter_image()** returns a filtered version of the input image to
    simulate missing the specified cone type
- **coloration.py** imports from **conversion_coefficients.py**,
**plotting_series.py**, **color_conversion.py**, and
**chromaticity_conversion.py**
    - **chromaticity_inside_gamut()** is used to color a chromaticity diagram
    within the display color gamut triangle
    - **chromaticity_outside_gamut()** is used to color a chromaticity diagram
    within the spectrum locus (ideally *behind* the coloring within the
    display color gamut triangle)
    - **three_dimensional_surface()** is used to plot 3D colored surfaces in
    either RGB or chromoluminance space
    - **visible_spectrum()** is used to plot a band of color corresponding to
    the visible spectrum
- **estimate_cone_fundamental_normalization_constants.py** imports from
**conversion_coefficients.py**, **plotting_series.py**, and
**color_conversion.py** and prints out to the console
- **maths_test.py** contains unit tests for all modules herein