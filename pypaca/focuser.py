import logging

import numpy as np

from . import AlpacaDevice, AlpacaDeviceError


##-------------------------------------------------------------------------
## Focuser Device
##-------------------------------------------------------------------------
class Focuser(AlpacaDevice):
    def __init__(self, **kwargs):
        self.property_names = ['absolute', 'maxincrement', 'maxstep',
                               'stepsize', 'tempcompavailable']
        super().__init__(**kwargs, device='focuser')

    def ismoving(self):
        return self.get('ismoving')['Value']

    def position(self):
        return self.get('position')['Value']

    def tempcomp(self):
        return self.get('tempcomp')['Value']

    def set_tempcomp(self, tempcomp):
        self.put('tempcomp', {'TempComp': tempcomp})

    def temperature(self):
        return self.get('temperature')['Value']

    def halt(self):
        self.put('halt', {})

    def move(self, position):
        self.put('move', {'Position': position})

