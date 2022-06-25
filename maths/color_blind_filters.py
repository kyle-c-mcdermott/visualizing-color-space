"""
Functions for Analyzing and Filtering Images to eliminate chromatic variation
along confusion lines for a selected cone type.
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
from PIL import Image
from typing import Dict, Tuple
# endregion

# region Constants

# endregion

# region Function - Get Unique Colors from Image
def get_unique_colors(
    image : Image.Image
) -> Dict[Tuple[int, int, int], int]: # {(red, green, blue) : count}

    # Validate Argument
    assert isinstance(image, Image.Image)

    # Generate Dictionary of Unique 8-bit RGB Values with Counts (ignore alpha if present)
    pixels = image.load()
    uniques_count = dict()
    for col in range(image.width):
        for row in range(image.height):
            if pixels[col, row][0:3] not in uniques_count:
                uniques_count[pixels[col, row][0:3]] = 0
            uniques_count[pixels[col, row][0:3]] += 1

    # Return
    return uniques_count

# endregion



# region Demonstration
if __name__ == '__main__':

    image_file_name = 'images/Color-Blind Stimulus - S-Cone Example.png'

    # Load image and make 256 x 256 with correct mode
    with Image.open(image_file_name) as original_image:
        if original_image.mode == 'P': exit()
        resized_image = original_image.resize(
            (
                int(original_image.width * (256 / max(original_image.size))),
                int(original_image.height * (256 / max(original_image.size)))
            )
        )
    cropped_image = resized_image.crop(
        (
            int((resized_image.width - resized_image.height) / 2.0), # left
            0, # top
            resized_image.width - int((resized_image.width - resized_image.height) / 2.0) - 1, # right
            resized_image.height # bottom
        )
    )
    cropped_image.mode = 'RGB'

    # Get unique colors
    unique_colors = get_unique_colors(cropped_image)
    print(len(unique_colors))

# endregion
