import random
import time

import requests
import json

import numpy as np

from . import Device, AlpacaDeviceError



##-------------------------------------------------------------------------
## Filter Wheel Device
##-------------------------------------------------------------------------
class FilterWheel(Device):
    def __init__(self, IP, **args):
        Device.__init__(self, IP, **args, device='filterwheel')
        self.focusoffsets = self.get('focusoffsets')['Value']
        self.names = self.get('names')['Value']

    def position(self):
        pos = self.get('position')['Value']
        if pos == -1:
            name = 'moving'
        else:
            name = self.names[pos]
        log.info(f'Position Name = "{name}"')
        return pos, name

    def set_position(self, position):
        if type(position) == int:
            self.put('position', {'Position': position})
        elif position in self.names:
            posint = self.names.index(position)
            self.put('position', {'Position': posint})

