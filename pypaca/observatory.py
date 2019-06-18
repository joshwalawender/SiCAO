#!/usr/env/python

## Import General Tools
from pathlib import Path
import yaml

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
class Observatory(object):
    def __init__(self, configfile=None):

        # Initialize devices to None
        self.Camera1 = None      # main imaging camera
        self.FilterWheel1 = None # filter wheel for main imaging camera
        self.Focuser1 = None     # focuser for main imaging camera
        self.Camera2 = None      # guide camera
        self.FilterWheel2 = None # filter wheel for guide camera
        self.Focuser2 = None     # focuser for guide camera
        self.Telescope == None   # telescope (aka mount)

        # Load configuration
        if configfile is not None:
            self.load_config(configfile)
        else:
            self.load_config('~/git/pypaca/pypaca/test.yaml')

    def load_config(self, file):
        file = Path(file).expanduser()
        with open(file, 'r') as f:
            contents = f.read()
            self.config = yaml.safe_load(contents)

    def connect_to(self, device):
        """Generic connection method"""
        devtype = device[:-1] if device[-1] in ['1', '2'] else device
        setattr(self, device, getattr(devices, devtype)(**self.config[device]))

    def connect_all(self):
        """Connect to all devices"""
        for key, value in self.config:
            devtype = key[:-1] if key[-1] in ['1', '2'] else key
            if devtype in ['Camera', 'FilterWheel', 'Focuser', 'Telescope']:
                self.connect_to(key)

    def collect_metadata(self):
        """Collect metadata from connected devices.
        
        Telescope: RA, DEC, alt, az, airmass, name, focal length, aperture
        Camera1: exposure time
        FilterWheel1: filter
        Focuser1: position, temperature
        Camera2: exposure time
        FilterWheel2: filter
        Focuser2: position, temperature
        Observatory: config, sequence info, frame ID, obstype
        Other: UT time, software version
        """
        pass


if __name__ == '__main__':
    main()
