
"""
Paul Chichura, 6/20/16

stamp module to be imported in whatever context is needed. function takes four
arguments: the string name of the fits file you want to stamp, a list of lists
of floats RA and DEC for that one file, (optional, assumed False if not given)
a boolean that's True if the given coordinates are already in xy pixels or
False if they need conversion, and (optional, names based off of fits file name
if not given) a string to name this particular stamp (do no include the
".filetype")

~*Remember to install sky2xy tool into the working directory or change ln 40*~

Useful: executing the following commands before utilizing this script should
improve runtime by blocking display of ds9 while trying to save the jpeg files:
% export DISPLAY=:1
% Xvfb :1 -screen 0 1024x768x16 &
"""

#define function, filename string name of file, skycoords list of lists RA,DEC
#isPixel is a Boolean that's True if skycoords are already converted to pixels
#name is an optional string for the filename (minus the .filetype) for stamps
def stamper(fitsfile, skycoords, isPixel=False, name='null'):

    import pyfits
    import os
    import subprocess
    import numpy as np

    #convert sky coordinate system into pixel coordinates
    hdulist = pyfits.open(fitsfile)
    xycoords = []
    if isPixel:
        #if pixel coordinates are given, bypasses coord conversion
        xycoords = skycoords
    else:
        #use sky2xy tool to convert to xy coordinates for each coordinate
        for i in range(len(skycoords)):
            proc = subprocess.Popen(["./sky2xy", fitsfile,
                str(skycoords[i][0]), str(skycoords[i][1])],
                stdout=subprocess.PIPE)
            result = proc.stdout.read()
            result = result.split()
            xycoords.append( [ int(float(result[4])), int(float(result[5])) ] )

    #get data object from the hdu
    scidata = hdulist[0].data
    wgtdata = hdulist[1].data

    #specify radius of stamp
    radius = 45

    #iterate through each coordinate we need to stamp
    for point in range(len(xycoords)):
        #placeholder variables for pixel indexes of corners of stamps
        xstart = 0
        xstop = 0
        ystart = 0
        ystop = 0
        
        #placeholder variables for pixel indeces of blank image to be filled
        stampxstart = 0
        stampxstop = radius*2
        stampystart = 0
        stampystop = radius*2
        
        #determine file names
        if name=='null': #if no specified filename
            filename = (fitsfile[:-5] + "_stamp_X" + str(xycoords[point][0]) +
                "_Y" + str(xycoords[point][1]) + ".fits")
            basename = filename.split("/")
            filename = basename[-1]
            jpegfilename = filename[:-5] + ".jpeg"
        else: #if a name was specified
            if len(xycoords) == 1: #if only one coordinate given
                filename = name + ".fits"
                jpegfilename = name + ".jpeg"
            else: #if multiple coordinates are given
                filename = (name + "_X" + str(xycoords[point][0]) + "_Y" + 
                    str(xycoords[point][1]) + ".fits")
                jpegfilename = filename[:-5] + ".jpeg"
        
        #make blank data arrays
        scistamp = np.full((radius*2,radius*2), .5)
        wgtstamp = np.full((radius*2,radius*2), .5)
        
        #NB: xy origin is in the bottom left of the fits file
        #check if coord is too close to bottom edge   
        if xycoords[point][1] - radius < 0:
            ystart = 0
            ystop = xycoords[point][1] + radius
            stampystart = radius*2 - ystop
            stampystop = radius*2
        #check if coord is too close to top edge
        elif xycoords[point][1] + radius >= len(scidata):
            ystop = len(scidata) - 1
            ystart = xycoords[point][1] - radius
            stampystart = 0
            stampystop = ystop - ystart
        #else y coordinates centered around the point
        else:
            ystart = xycoords[point][1] - radius
            ystop = ystart + radius * 2        
        
        #check if coord is too close to left edge
        if xycoords[point][0] - radius < 0:
            xstart = 0
            xstop = xycoords[point][0] + radius
            stampxstart = radius*2 - xstop
            stampxstop = radius*2
        #check if coord is too close to right edge
        elif xycoords[point][0] + radius >= len(scidata[0]):
            xstop = len(scidata[0]) - 1
            xstart = xycoords[point][0] - radius
            stampxstart = 0
            stampxstop = xstop - xstart
        #else x coordinates centered around the point
        else:
            xstart = xycoords[point][0] - radius
            xstop = xstart + radius * 2    
        
        #get the stamp
        scistamp[stampystart:stampystop, stampxstart:stampxstop] = scidata[ystart:ystop, xstart:xstop]
        wgtstamp[stampystart:stampystop, stampxstart:stampxstop] = wgtdata[ystart:ystop, xstart:xstop]
        
        #save the stamp
        #create a PrimaryHDU object to encapsulate the data
        scihdu = pyfits.PrimaryHDU(scistamp)
        wgthdu = pyfits.ImageHDU(wgtstamp)
        hlist = pyfits.HDUList([scihdu, wgthdu])
        
        #write and save to new fits file
        os.system("rm " + filename + " -f")
        hlist.writeto(filename)
        
        #save the fits file as a jpeg image file
        os.system("ds9 " + filename + " -scale mode zscale -zoom to fit " +
            "-saveimage jpeg " + jpegfilename + " -exit")
            