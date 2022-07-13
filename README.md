# visualizing-color-space
Figure Generation and Useful Functions Associated with the [Visualizing Color Space Document](https://drive.google.com/drive/folders/1jPUTIYndDIz3u3UEHpQn7Y6sarJDSm_q?usp=sharing).  The **generation** folder should be the starting point for exploration - each figure script therein imports from **figure** and **maths**.  **maths/plotting_series.py** is the main injestion point for the tabulated data contained in **cvrl** and **data**.  The document itself is a LaTeX document (built in [Overleaf](https://www.overleaf.com/read/grwgzthdfpgb)) intended to be built from a workspace containing the **tex** and **images** folders.
## Folders
- **figure** contains the figure module which wraps around various matplotlib functionality
- **cvrl** contains tabulated data and coefficients taken from the Color & Vision Research Laboratory [website](http://www.cvrl.org)
- **data** contains tabulated data curated by the author
- **maths** contains scripts used to perform the derivations presented in the Visualizing Color Space document - various functions are related to either/both derivations and figure generation
- **generation** contains scripts for generating the figures in the Visualizing Color Space document
- **images** contains generated figure images in pdf format with relatively low resolution (higher resolution images in multiple formats are available [here](https://drive.google.com/drive/folders/1W4yqJu7mcu4SLyxMzZr2CoseSl0dLA23?usp=sharing))
- **tex** contains the LaTeX project of the document