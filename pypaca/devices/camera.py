import random
import time
from datetime import datetime
import requests
import json
import logging

import numpy as np
from astropy.io import fits


from . import AlpacaDevice, AlpacaDeviceError


##-------------------------------------------------------------------------
## AlpacaCamera Device
##-------------------------------------------------------------------------
class Camera(AlpacaDevice):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, device='camera')
        # Initialize Properties
        self.exptime = 0

        # Populate fixed header for all exposures
        self.fixed_header = fits.Header()
        self.fixed_header['BAYROFFX'] = (self.get('bayeroffsetx')['Value'],
                                         'Bayer Offset X')
        self.fixed_header['BAYROFFY'] = (self.get('bayeroffsety')['Value'],
                                         'Bayer Offset Y')
        self.fixed_header['FULLWELL'] = (self.get('fullwellcapacity')['Value'],
                                         'Full Well Capcity')
        self.fixed_header['PIXSIZEX'] = (self.get('pixelsizex')['Value'],
                                         'Pixel Size X')
        self.fixed_header['PIXSIZEY'] = (self.get('pixelsizey')['Value'],
                                         'Pixel Size Y')
        self.fixed_header['SENSNAME'] = (self.get('sensorname')['Value'],
                                         'Sensor Name')
        self.fixed_header['SENSTYPE'] = (self.get('sensortype')['Value'],
                                         'Sensor Type')
        self.fixed_header['EXPTIME'] = (self.exptime, 'Exposure Time (sec)')

        # Alpaca Capabilities
        self.canabort = self.get('canabortexposure')['Value']
        self.canasymmetricbin = self.get('canasymmetricbin')['Value']
        self.canfastread = self.get('canfastreadout')['Value']
        self.cangetcoolerpower = self.get('cangetcoolerpower')['Value']
        self.canpulseguide = self.get('canpulseguide')['Value']
        self.cansetccdtemperature = self.get('cansetccdtemperature')['Value']
        self.canstopexposure = self.get('canstopexposure')['Value']
        self.exposuremax = self.get('exposuremax')['Value']
        self.exposuremin = self.get('exposuremin')['Value']
        self.exposureresolution = self.get('exposureresolution')['Value']
        self.gainmax = self.get('gainmax')['Value']
        self.gainmin = self.get('gainmin')['Value']
        self.gains = self.get('gains')['Value']
        self.hasshutter = self.get('hasshutter')['Value']
        self.maxadu = self.get('maxadu')['Value']
        self.maxbinx = self.get('maxbinx')['Value']
        self.maxbiny = self.get('maxbiny')['Value']
        self.readoutmodes = self.get('readoutmodes')['Value']


    ##-------------------------------------------------------------------------
    ## Required Methods for ObservatoryControlSystem
    ##-------------------------------------------------------------------------
    def set_exptime(self, exptime):
        self.exptime = exptime
        self.fixed_header['EXPTIME'] = (self.exptime, 'Exposure Time (sec)')


    def _collect_preexposure_header(self):
        h = fits.Header()
        h['EXPBEGIN'] = (datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f'),
                         'UTC of Exposure Start')
        return h


    def _collect_postexposure_header(self):
        h = fits.Header()
        h['EXPEND'] = (datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f'),
                       'UTC of Exposure End')
        return h


    def expose(self, light=True):
        pre_header = self._collect_preexposure_header()
        self.startexposure(self.exptime, light=light)
        self.waitfor_imageready()
        post_header = self._collect_postexposure_header()
        data = self.imagearray()
        header = self.fixed_header + pre_header + post_header
        hdu = fits.PrimaryHDU(data=data, header=header)
        return fits.HDUList([hdu])


    def expose_dark(self):
        return self.expose(light=False)


    def set_window(self, inputstr):
        xstr, ystr = inputstr.split(',')
        x1, x2 = xstr.split(':')
        y1, y2 = ystr.split(':')
        self.detector.set_startx(int(x1))
        self.detector.set_starty(int(y1))
        self.detector.set_numx(int(x2)-int(x1))
        self.detector.set_numy(int(y2)-int(y1))

    ##-------------------------------------------------------------------------
    ## Alpaca Methods
    ##-------------------------------------------------------------------------
    def binning(self):
        binx = self.get('binx')['Value']
        biny = self.get('biny')['Value']
        return (binx, biny)

    def set_binning(self, binx, biny):
        self.put('binx', {'BinX': binx})
        self.put('biny', {'BinY': biny})

    def camerastate(self):
        return self.get('camerastate')['Value']

    def camerasize(self):
        sx = self.get('cameraxsize')['Value']
        sy = self.get('cameraysize')['Value']
        return (sx, sy)

    def ccdtemperature(self):
        return self.get('ccdtemperature')['Value']

    def cooleron(self):
        return self.get('cooleron')['Value']

    def set_cooleron(self, on=True):
        self.put('cooleron', {'CoolerOn': on})

    def coolerpower(self):
        if self.cangetcoolerpower is True:
            return self.get('coolerpower')['Value']

    def electronsperadu(self):
        return self.get('electronsperadu')['Value']

    def fastreadout(self):
        return self.get('fastreadout')['Value']

    def set_fastreadout(self, fast=True):
        self.put('fastreadout', {'FastReadout': fast})

    def gain(self):
        return self.get('gain')['Value']

    def set_gain(self, gain):
        self.put('gain', {'Gain': gain})

    def heatsinktemperature(self):
        return self.get('heatsinktemperature')['Value']

    def imagearray(self):
        self.log('Getting image data')
        data = np.array(self.get('imagearray', quiet=True)['Value'])
        self.log(f'Got data of shape {data.shape}')
        return data

    def imagearrayvariant(self):
        self.log('Getting image data')
        data = np.array(self.get('imagearrayvariant', quiet=True)['Value'])
        self.log(f'Got data of shape {data.shape}')
        return data

    def imageready(self):
        return self.get('imageready', quiet=True)['Value']

    def waitfor_imageready(self, sleep=1):
        ready = self.imageready()
        if ready is False:
            self.log('Waiting for image')
            while ready is False:
                time.sleep(sleep)
#                 self.percentcompleted()
                ready = self.imageready()
        if ready is True:
            self.log('Image ready for download', level=logging.DEBUG)

    def waitfor_and_getimage(self, sleep=1):
        ready = self.imageready()
        if ready is False:
            self.log('Waiting for image')
            while ready is False:
                time.sleep(sleep)
#                 self.percentcompleted()
                ready = self.imageready()
        if ready is True:
            self.log('Image ready for download')
            return self.imagearray()

    def ispulseguiding(self):
        return self.get('ispulseguiding', quiet=True)['Value']

    def lastexposureduration(self):
        return self.get('lastexposureduration', quiet=True)['Value']

    def lastexposurestarttime(self):
        return self.get('lastexposurestarttime', quiet=True)['Value']

    def numx(self):
        return self.get('numx')['Value']

    def numy(self):
        return self.get('numy')['Value']

    def set_numx(self, numx):
        self.put('numx', {'NumX': numx})

    def set_numy(self, numy):
        self.put('numy', {'NumY': numy})

    def percentcompleted(self):
        return self.get('percentcompleted')['Value']

    def readoutmode(self):
        return self.get('readoutmode')['Value']

    def set_readoutmode(self, readoutmode):
        self.put('readoutmode', {'ReadoutMode': readoutmode})

    def ccdsetpoint(self):
        return self.get('setccdtemperature')['Value']

    def set_ccdtemperature(self, setccdtemperature):
        self.put('setccdtemperature', {'SetCCDTemperature': setccdtemperature})

    def startx(self):
        return self.get('startx')['Value']

    def starty(self):
        return self.get('starty')['Value']

    def set_startx(self, startx):
        self.put('startx', {'StartX': startx})

    def set_starty(self, starty):
        self.put('starty', {'StartY': starty})

    def abortexposure(self):
        self.put('abortexposure', {})

    def pulseguide(self, direction, duration):
        # Direction of movement (0 = North, 1 = South, 2 = East, 3 = West)
        if type(direction) == str:
            numerical_directions = {'N': 0, 'S': 1, 'E': 2, 'W': 3}
            direction = numerical_directions[direction.upper()]
        elif type(direction) == int:
            pass
        else:
            return None
        self.put('pulseguide', {'Direction': direction, 'Duration': duration})

    def startexposure(self, exptime, light=True):
        return self.put('startexposure', {'Duration': exptime, 'Light': light})

    def stopexposure(self):
        return self.put('stopexposure', {})

