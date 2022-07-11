"""
Various values intended to be used by all figures.
"""

# region Imports

# endregion

# region Constants Derived from LaTeX Document
"""
% Given thinned margins:
|usepackage[margin=1.75cm]{geometry}
% and (temprorarily) using layouts package to print measurements:
|usepackage{layouts}
% and using the multicol package:
|usepackage{multicol}

|printinunitsof{in}|prntlen{|textwidth} % leads to TEXT_WIDTH below
|printinunitsof{in}|prntlen{|textheight} # leads to TEXT_HEIGHT below

|begin{multicols}{2}
|printinunitsof{in}|prntlen{|linewidth} % leads to COLUMN_WIDTH below
|end{multicols}
"""
TEXT_WIDTH = 7.12344 # in inches
TEXT_HEIGHT = 9.62393 # in inches
COLUMN_WIDTH = 3.49252 # in inches
# endregion

# region Font Sizes
FONT_SIZES = {
    'titles' : 10,
    'labels' : 10,
    'ticks' : 8,
    'legends' : 8
}
# endregion

# region Axes Labels
WAVE_NUMBER_LABEL = r'Wave-Number ($cm^{-1}$)'
WAVELENGTH_LABEL = r'Wavelength $\lambda$ ($nm$)'
# endregion

# region Standard Series Appeareances
AXES_GREY_LEVEL = 0.25
DOTTED_GREY_LEVEL = 0.75
SL_GREY_LEVEL = 0.5

# endregion
