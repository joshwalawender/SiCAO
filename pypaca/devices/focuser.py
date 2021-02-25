import random
import time

import requests
import json

import numpy as np

from . import Device, AlpacaDeviceError


##-------------------------------------------------------------------------
## Focuser Device
##-------------------------------------------------------------------------
class Focuser(Device):
    def __init__(self, IP, **args):
        Device.__init__(self, IP, **args, device='focuser')
        self.absolute = self.get('absolute')['Value']
        self.maxincrement = self.get('maxincrement')['Value']
        self.maxstep = self.get('maxstep')['Value']
        self.stepsize = self.get('stepsize')['Value']
        self.tempcompavailable = self.get('tempcompavailable')['Value']

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

