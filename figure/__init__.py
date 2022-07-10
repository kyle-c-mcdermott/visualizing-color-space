"""
Figure Package

The figure.py script is essentially a wrapper for matplotlib.pyplot.
Subplots (herein called panels) are constrcuted to align their data area
boundaries based on nominal positions defined within the figure area - the
purpose is to streamline such alignment in the face of differences among panels
in the size of titles and axes annotations (labels, ticks).

Additional functions are provided for streamlining common manipulations.  A
function for text annotation of a series of plotted values is also included.
"""