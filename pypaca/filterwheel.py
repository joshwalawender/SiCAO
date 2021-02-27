import logging

import numpy as np
from astropy.io import fits

from . import AlpacaDevice, AlpacaDeviceError



##-------------------------------------------------------------------------
## Filter Wheel Device
##-------------------------------------------------------------------------
class FilterWheel(AlpacaDevice):
    def __init__(self, **kwargs):
        self.property_names = ['focusoffsets', 'names']
        super().__init__(**kwargs, device='filterwheel')


    def position(self):
        pos = self.get('position')['Value']
        if pos == -1:
            name = 'moving'
        else:
            name = self.properties['names'][pos]
        self.log(f'Position Name = "{name}"')
        return pos, name


    def set_position(self, position):
        if type(position) == int:
            self.put('position', {'Position': position})
        elif position in self.properties['names']:
            posint = self.properties['names'].index(position)
            self.put('position', {'Position': posint})
