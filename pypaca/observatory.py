#!/usr/env/python

## Import General Tools
from pathlib import Path
import yaml
import datetime
from time import sleep

import numpy as np
from astropy.io import fits
from astropy.table import Table

from . import log, devices, AlpacaError, ObservatoryError


##-------------------------------------------------------------------------
## Sequence
##-------------------------------------------------------------------------
class Sequence(object):
    """Example Sequence Table:
    t = Table(names=('imtype', 'exptime', 'filter', 'nexp', 'bin'),
              dtype=('a20', 'f4', 'a20', 'i4', 'a3'))
    t.add_row(['light', 120, 'R', 5, '1x1'])
    t.add_row(['light', 120, 'G', 5, '1x1'])
    t.add_row(['light', 120, 'B', 5, '1x1'])
    t.add_row(['light', 120, 'L', 15, '1x1'])
    t.write('ExampleSequence.txt', format='ascii.fixed_width_two_line')
    """
    def read(self, file):
        file = Path(file).expanduser()
        with open(file, 'r') as f:
            info = yaml.safe_load(f.read())

        for key in info.keys():
            if key == 'table':
                self.table = Table.read(info['table'],
                                        format='ascii.fixed_width_two_line')
            else:
                setattr(self, key, info[key])




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
        self.Telescope = None   # telescope (aka mount)

        self.imtypes_light = ['light', 'twiflat', 'sky', 'domeflat']
        self.imtypes_dark = ['bias', 'dark']
        self.imtypes = self.imtypes_light.extend(self.imtypes_dark)

        self.targname = ''

        # Load configuration
        if configfile is not None:
            self.load_config(configfile)
        else:
            self.load_config('~/git/pypaca/pypaca/test.yaml')

    def is_light(self, imtype):
        if imtype.lower() in self.imtypes_light:
            return True
        elif imtype.lower() in self.imtypes_dark:
            return False
        else:
            raise ObservatoryError(f"{imtype} is not a valid image type")

    def load_config(self, file):
        file = Path(file).expanduser()
        with open(file, 'r') as f:
            contents = f.read()
            config = yaml.safe_load(contents)
        self.devices = config['Devices']
        self.options = config['Options']

    def connect_to(self, device):
        """Generic connection method"""
        devtype = device[:-1] if device[-1] in ['1', '2'] else device
        setattr(self, device, getattr(devices, devtype)(**self.devices[device]))

    def connect_all(self):
        """Connect to all devices"""
        for key in self.devices.keys():
            devtype = key[:-1] if key[-1] in ['1', '2'] else key
            if devtype in ['Camera', 'FilterWheel', 'Focuser', 'Telescope']:
                self.connect_to(key)

    def collect_metadata(self, pre=False):
        """Collect metadata from connected devices.
        
        Telescope: RA, DEC, alt, az, airmass, name, focal length, aperture
        Camera1: exposure time
        FilterWheel1: filter
        Focuser1: position, temperature
        Observatory: config, sequence info, frame ID, obstype
        Other: UT time, software version
        """
        h = fits.Header()
        now = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')
        if pre is True:
            log.info('Collecting pre-exposure metadata')
            # General
            h.set('UT1', value=now,
                  comment='Computer UT at start of exposure')
            h.set('TARGNAME', value=self.targname,
                  comment='Target name')
            # Telescope
            h.set('ALT0', value=self.Telescope.altitude(),
                  comment='Telescope altitude (deg) at start of exposure')
            h.set('AZ0', value=self.Telescope.azimuth(),
                  comment='Telescope azimuth (deg) at start of exposure')
            h.set('DEC0', value=self.Telescope.declination(),
                  comment='Telescope DEC (deg) at start of exposure')
            h.set('DECRATE0', value=self.Telescope.declinationrate(),
                  comment='Telescope DEC rate (unit?) at start of exposure')
            h.set('RA0', value=self.Telescope.rightascension(),
                  comment='Telescope RA (hours) at start of exposure')
            h.set('RARATE0', value=self.Telescope.rightascensionrate(),
                  comment='Telescope RA rate (unit?) at start of exposure')
            h.set('LST0', value=self.Telescope.siderealtime(),
                  comment='Sidereal time (hours) at start of exposure')
            h.set('TARGDEC0', value=self.Telescope.targetdeclination(),
                  comment='Target DEC (deg) at start of exposure')
            h.set('TARGRA0', value=self.Telescope.targetrightascension(),
                  comment='Target RA (hours) at start of exposure')
            h.set('TELUT0', value=self.Telescope.utcdate(),
                  comment='Telescope UT at start of exposure')
        if pre is False:
            log.info('Collecting post-exposure metadata')
            # General
            h.set('UT', value=now,
                  comment='Computer UT at end of exposure')
            # Telescope
            h.set('TELNAME', value=self.Telescope.name,
                  comment='Telescope name from driver')
            h.set('TELINFO', value=self.Telescope.description)
            h.set('TELDRIVR', value=self.Telescope.driverversion,
                  comment='Telescope driver version')
            h.set('ALT', value=self.Telescope.altitude(),
                  comment='Telescope altitude (deg) at end of exposure')
            h.set('AZ', value=self.Telescope.azimuth(),
                  comment='Telescope azimuth (deg) at end of exposure')
            h.set('DEC', value=self.Telescope.declination(),
                  comment='Telescope DEC (deg) at end of exposure')
            h.set('DECRATE', value=self.Telescope.declinationrate(),
                  comment='Telescope DEC rate (unit?) at end of exposure')
            h.set('RA', value=self.Telescope.rightascension(),
                  comment='Telescope RA (hours) at end of exposure')
            h.set('RARATE', value=self.Telescope.rightascensionrate(),
                  comment='Telescope RA rate (unit?) at end of exposure')
            h.set('PIERSIDE', value=self.Telescope.sideofpier(),
                  comment='Pier side reported by telescope')
            h.set('LST', value=self.Telescope.siderealtime(),
                  comment='Sidereal time (hours) at end of exposure')
            h.set('SITE_EL', value=self.Telescope.siteelevation(),
                  comment='Site elevation (unit?)')
            h.set('SITE_LAT', value=self.Telescope.sitelatitude(),
                  comment='Site latitude')
            h.set('SITE_LON', value=self.Telescope.sitelongitude(),
                  comment='Site longitude')
            h.set('TARGDEC', value=self.Telescope.targetdeclination(),
                  comment='Target DEC (deg) at end of exposure')
            h.set('TARGRA', value=self.Telescope.targetrightascension(),
                  comment='Target RA (hours) at end of exposure')
            h.set('TRACKING', value=self.Telescope.tracking(),
                  comment='Tracking status')
            h.set('TRACRATE', value=self.Telescope.trackingrate(),
                  comment='Tracking rate (units?)')
            h.set('TELUT', value=self.Telescope.utcdate(),
                  comment='Telescope UT at end of exposure')
            # Camera1
            h.set('CAMNAME', value=self.Camera1.name,
                  comment='Camera name from driver')
            h.set('CAMINFO', value=self.Camera1.description)
            h.set('CAMDRIVR', value=self.Camera1.driverversion,
                  comment='Camera driver version')
            h.set('BAYEROX', value=self.Camera1.bayeroffsetx,
                  comment='Bayer offset X')
            h.set('BAYEROY', value=self.Camera1.bayeroffsety,
                  comment='Bayer offset Y')
            h.set('PIXSIZEX', value=self.Camera1.pixelsizex,
                  comment='Pixel size (microns) in X direction')
            h.set('PIXSIZEY', value=self.Camera1.pixelsizey,
                  comment='Pixel size (microns) in Y direction')
            h.set('CCDNAME', value=self.Camera1.sensorname,
                  comment='Sensor name from driver')
            h.set('CCDTYPE', value=self.Camera1.sensortype,
                  comment='CCD type from driver')
            binx, biny = self.Camera1.binning()
            h.set('BINX', value=binx, comment='X Binning')
            h.set('BINY', value=biny, comment='Y Binning')
            h.set('BINNING', value=f'{binx}, {biny}', comment='Binning')
            h.set('DETSIZE', value=str(self.Camera1.camerasize()),
                  comment='Size of detector in pixels')
            h.set('DETTEMP', value=self.Camera1.ccdtemperature(),
                  comment='Detector temperature (degrees C)')
            h.set('DETSETP', value=self.Camera1.ccdsetpoint(),
                  comment='Detector set point (degrees C)')
            h.set('COOLON', value=self.Camera1.cooleron(),
                  comment='Detector cooler on?')
            h.set('COOLPWR', value=self.Camera1.coolerpower(),
                  comment='Cooler power ouput (%)')
            h.set('EPERADU', value=self.Camera1.electronsperadu(),
                  comment='Gain in electrons per adu')
            h.set('GAIN', value=self.Camera1.gain(),
                  comment='Gain in camera units (db?)')
            h.set('EXPTIME', value=self.Camera1.lastexposureduration(),
                  comment='Exposure duration (seconds)')
            h.set('EXPSTART', value=self.Camera1.lastexposurestarttime(),
                  comment='Start time of last exposure')
            h.set('NUMX', value=self.Camera1.numx(),
                  comment='Window size (pixels) in X')
            h.set('NUMY', value=self.Camera1.numy(),
                  comment='Window size (pixels) in Y')
            h.set('STARTX', value=self.Camera1.startx(),
                  comment='Starting X pixel of window')
            h.set('STARTY', value=self.Camera1.starty(),
                  comment='Starting Y pixel of window')
            # Filter Wheel1
            h.set('FWNAME', value=self.FilterWheel1.name,
                  comment='Filter wheel name from driver')
            h.set('FWINFO', value=self.FilterWheel1.description)
            h.set('FWDRIVR', value=self.FilterWheel1.driverversion,
                  comment='Filter wheel driver version')
            pos, name = self.FilterWheel1.position()
            h.set('FILTER', value=name, comment='Filter name')
            h.set('FILTPOS', value=pos, comment='Filter position')
            # Focuser1
            h.set('FOCNAME', value=self.Focuser1.name,
                  comment='Focuser name from driver')
            h.set('FOCINFO', value=self.Focuser1.description)
            h.set('FOCDRIVR', value=self.Focuser1.driverversion,
                  comment='Focuser driver version')
            h.set('FOCUSPOS', value=self.Focuser1.position(),
                  comment='Focuser position')
            h.set('TEMPCOMP', value=self.Focuser1.tempcomp(),
                  comment='Temperature compensation active?')
            h.set('FOCTEMP', value=self.Focuser1.temperature(),
                  comment='Focuser temperature (degrees C)')
        return h

    def expose(self, exptime=0, filter='L', imtype='light',
               filename=None):
        """Method to take an exposure with the specified parameters and write
        a FITS file.
        """
        if self.is_light(imtype) is False\
           and self.options['filter_as_dark'] is not None:
            # Override filter if imtype specifies dark
            self.FilterWheel1.set_position(self.options['filter_as_dark'])
        else:
            # Set filter
            self.FilterWheel1.set_position(filter)
        h = self.collect_metadata(pre=True)
        h.set('IMTYPE', imtype, 'Image Type')
        log.info(f'Starting {exptime} second exposure')
        self.Camera1.startexposure(exptime, light=self.is_light(imtype))
        if exptime > 1:
            sleep(exptime-1)
        data = self.Camera1.waitfor_and_getimage()
        h += self.collect_metadata()
        if data.shape[0] > data.shape[1]:
            # Rotate data to long edge horizontal for display if needed
            data = np.rot90(data)
        hdu = fits.PrimaryHDU(data=data, header=h)
        if filename is None:
            return hdu
        try:
            fp = Path(filename).expanduser()
            log.info(f'Writing file to {fp}')
            hdu.writeto(fp)
        except:
            log.error(f'Failed to write file to {fp}')
        finally:
            return hdu


if __name__ == '__main__':
    main()
