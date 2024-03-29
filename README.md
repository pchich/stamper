Introduction:
stampfunct.py contains a function to be imported in whatever context is needed that creates stamp cutout jpegs centered around a given list of RA and DEC within a given fits file.

Installation:
Download both sky2xy tool and stampfunct.py.  Import the function "stamper" from stampfunct.py in a python script to make use of it. sky2xy is assumed to be in the working directory where the script will be run that is making the stamps (to change this, edit line 40 of stampfunct.py).

Details:
The function (called "stamper") takes four arguments: the string file name of the fits file you want to make stamps of, a list of lists of floats RA and DEC (decimal degrees) for that one file, (optional, assumed False if not given) a boolean that's True if the given coordinates are already in xy pixels or False if they need conversion to pixel coorinates, and (optional, names based off of fits file name if not given) a string to name this particular stamp (do no include the ".filetype").  The second argument could also be a list of xy pixel coordinates in the fits file if the third argument is provided True.

Executing the following commands before utilizing this script may be helpful in improving runtime by blocking display of ds9 while trying to save the jpeg files:
% export DISPLAY=:1
% Xvfb :1 -screen 0 1024x768x16 &
