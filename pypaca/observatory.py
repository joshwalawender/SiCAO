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
    dithersize -- Dither size (0 for no dither)
    """
    def __init__(self, images=None, dithersize=0):
        self.images = images
        self.dithersize = dithersize


##-------------------------------------------------------------------------
## Observatory
##-------------------------------------------------------------------------
class observatory(object):
    def connect_camera1(self, *args, **kwargs):
        """Camera1 is assumed to the main imaging camera."""
        self.camera1 = devices.Camera(*args, **kwargs)

    def connect_filterwheel1(self, *args, **kwargs):
        """FilterWheel1 is assumed to associated with the main imaging camera.
        """
        self.filterwheel1 = devices.FilterWheel(*args, **kwargs)

    def connect_focuser1(self, *args, **kwargs):
        """Focuser1 is assumed to the focuser for the main imaging camera."""
        self.focuser1 = devices.Focuser(*args, **kwargs)

    def connect_camera2(self, *args, **kwargs):
        """Camera2 is assumed to the guide camera."""
        self.camera2 = devices.Camera(*args, **kwargs)

    def connect_filterwheel2(self, *args, **kwargs):
        """FilterWheel2 is assumed to associated with the guide camera."""
        self.filterwheel1 = devices.FilterWheel(*args, **kwargs)

    def connect_focuser2(self, *args, **kwargs):
        """Focuser2 is assumed to the focuser for the guide camera."""
        self.focuser2 = devices.Focuser(*args, **kwargs)

    def connect_telescope(self, *args, **kwargs):
        """Telescope (mount) on which the other devices ride."""
        self.telescope = devices.Telescope(*args, **kwargs)

    def load_config(self, file):
        with open('test.yaml', 'r') as f:
            contents = f.read()
            self.config = yaml.safe_load(contents)

    def acquire_image(self, conf):
        """Acquire a single image with the given characteristics.
        """
        pass


if __name__ == '__main__':
    main()
