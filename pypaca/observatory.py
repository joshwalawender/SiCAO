#!/usr/env/python

## Import General Tools
from pathlib import Path

from . import log
from . import devices

##-------------------------------------------------------------------------
## Image Configuration
##-------------------------------------------------------------------------
class ImageConf(object):
    """Object which describes a single image to acquire.
    
    Properties
    camera -- Which camera to use.
    filterwheel -- Which filter wheel to use.
    filter -- Which filter to use.
    exptime -- Exposure time in seconds.
    imtype -- Image type (IRAF like string)
    sequenceID -- ID of sequence to which this image belongs
    """
    def __init__(self, camera=None, filterwheel=None, filter=None,
                 exptime=None, imtype=None, sequenceID=None):
        self.camera = camera
        self.filterwheel = filterwheel
        self.filter = filter
        self.exptime = exptime
        self.imtype = imtype
        self.sequenceID=sequenceID


##-------------------------------------------------------------------------
## Sequence
##-------------------------------------------------------------------------
class Sequence(object):
    """Object which describes a sequence of images to acquire.
    
    Properties
    images -- List of ImageConf objects
    ditherparams -- 
    """
    



##-------------------------------------------------------------------------
## Observatory
##-------------------------------------------------------------------------
class observatory(object):
    def connect(self):
        pass
    
    def acquire_image(self, conf):
        """Acquire a single image with the given characteristics.
        """
        pass


if __name__ == '__main__':
    main()
