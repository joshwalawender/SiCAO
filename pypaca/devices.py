#!/usr/env/python
import random
import time

import requests
import json

import numpy as np

from . import log

##-------------------------------------------------------------------------
## Abstract Alpaca Device
##-------------------------------------------------------------------------
class Device(object):
    def __init__(self, IP, port=11111, device=None, device_number=0,
                 ClientID=None, ClientTransactionID=0):
        alpaca_devices = ['switch', 'safetymonitor', 'dome', 'camera',
                          'observingconditions', 'filterwheel', 'focuser',
                          'rotator', 'telescope']
        if device not in alpaca_devices:
            raise AlpacaError(f'Device "{device}" not in standard Alpaca device list')
        if ClientID is None:
            self.clientID = int(random.random() * 65535)
        else:
            self.clientID = ClientID
        self.transactionID = ClientTransactionID
        self.device = device
        self.IP = IP
        self.port = port
        self.device_number = device_number
        self.url = f"http://{IP}:{port}/api/v1/{self.device}/{self.device_number}/"
        self.name = self.get_name()
        self.description = self.get_description()
        self.driverinfo = self.get_driverinfo()
        self.driverversion = self.get_driverversion()
        self.supportedactions = self.get_supportedactions()


    def get(self, command, quiet=False):
        log.debug(f'GET {command}')
        payload = {'ClientID': self.clientID,
                   'ClientTransactionID': self.transactionID,
                   }
        r = requests.get(self.url + command, data=payload)
        if r.status_code == 200:
            try:
                j = json.loads(r.text)
                log.debug(f'  ClientTransactionID: {j["ClientTransactionID"]}')
                log.debug(f'  ServerTransactionID: {j["ServerTransactionID"]}')
                log.debug(f'  ErrorNumber: {j["ErrorNumber"]}')
                if j["ErrorNumber"] != 0:
                    log.warning(f'GET {command} failed')
                    if type(j["ErrorMessage"]) == str:
                        lines = j["ErrorMessage"].split('\n')
                        log.warning(f'  ErrorMessage: {lines[0]}')
                        for v in lines[1:]:
                            log.warning(f'                {v}')
                    else:
                        log.warning(f'  ErrorMessage: {j["ErrorMessage"]}')

                if quiet is False and j["ErrorNumber"] == 0:
                    if type(j["Value"]) == str:
                        lines = j["Value"].split('\n')
                        log.info(f'GET {command}: {lines[0]}')
                        for v in lines[1:]:
                            log.info(f'               {v}')
                    else:
                        log.info(f'GET {command}: {j["Value"]}')

                self.transactionID += 1
                if self.transactionID > 4294967295:
                    self.transactionID -= 4294967295
                return j
            except json.JSONDecodeError as e:
                log.error(f'GET {command} failed: {e.msg}')
                return {'Value': None,
                        'ErrorNumber': -1,
                        'ErrorMessage': e.msg,
                       }
        elif r.status_code == 400:
            log.error(f'400: Invalid request. "{self.url + command}"')
            log.error(f'  {r.text}')
            return {'Value': None}
        elif r.status_code == 500:
            log.error(f'500: Unexpected device error')
            log.error(f'  {r.text}')
            return {'Value': None}
        else:
            log.error(f'{r.status_code}: {r.text}')
            return {'Value': None}


    def put(self, command, contents):
        s = ', '.join([f'{key} = {contents[key]}' for key in contents.keys()])
        log.info(f'PUT {command}: {s}')

        default = {'ClientID': self.clientID,
                   'ClientTransactionID': self.transactionID,
                   }
        payload = {**default, **contents}
        r = requests.put(self.url + command, data=payload)
        j = json.loads(r.text)

        log.debug(f'  ClientTransactionID: {j["ClientTransactionID"]}')
        log.debug(f'  ServerTransactionID: {j["ServerTransactionID"]}')
        log.debug(f'  ErrorNumber: {j["ErrorNumber"]}')
        if j["ErrorNumber"] != 0:
            log.warning(f'PUT {command}: {s} failed')
            if type(j["ErrorMessage"]) == str:
                lines = j["ErrorMessage"].split('\n')
                log.warning(f'  ErrorMessage: {lines[0]}')
                for v in lines[1:]:
                    log.warning(f'                {v}')
            else:
                log.warning(f'  ErrorMessage: {j["ErrorMessage"]}')
            raise AlpacaError(j["ErrorMessage"])

        self.transactionID += 1
        if self.transactionID > 4294967295:
            self.transactionID -= 4294967295
        return j


    def get_connected(self):
        j = self.get('connected')
        return j['Value']


    def get_description(self):
        j = self.get('description')
        return j['Value']


    def get_driverinfo(self):
        j = self.get('driverinfo')
        return j['Value']


    def get_driverversion(self):
        j = self.get('driverversion')
        return j['Value']


    def get_name(self):
        j = self.get('name')
        return j['Value']


    def get_supportedactions(self):
        j = self.get('supportedactions')
        return j['Value']


##-------------------------------------------------------------------------
## Camera Device
##-------------------------------------------------------------------------
class Camera(Device):
    def __init__(self, IP, **args):
        Device.__init__(self, IP, **args, device='camera')
        self.bayeroffsetx = self.get('bayeroffsetx')['Value']
        self.bayeroffsety = self.get('bayeroffsety')['Value']
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
        self.fullwellcapacity = self.get('fullwellcapacity')['Value']
        self.gainmax = self.get('gainmax')['Value']
        self.gainmin = self.get('gainmin')['Value']
        self.gains = self.get('gains')['Value']
        self.hasshutter = self.get('hasshutter')['Value']
        self.maxadu = self.get('maxadu')['Value']
        self.maxbinx = self.get('maxbinx')['Value']
        self.maxbiny = self.get('maxbiny')['Value']
        self.pixelsizex = self.get('pixelsizex')['Value']
        self.pixelsizey = self.get('pixelsizey')['Value']
        self.readoutmodes = self.get('readoutmodes')['Value']
        self.sensorname = self.get('sensorname')['Value']
        self.sensortype = self.get('sensortype')['Value']

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
        log.info('Getting image data')
        data = np.array(self.get('imagearray', quiet=True)['Value'])
        log.info(f'Got data of shape {data.shape}')
        return data

    def imagearrayvariant(self):
        log.info('Getting image data')
        data = np.array(self.get('imagearrayvariant', quiet=True)['Value'])
        log.info(f'Got data of shape {data.shape}')
        return data

    def imageready(self):
        return self.get('imageready', quiet=True)['Value']

    def waitfor_imageready(self, exptime=1, sleep=1):
        ready = self.imageready()
        if ready is False:
            log.info('Waiting for image')
            while ready is False:
                time.sleep(sleep)
                self.percentcompleted()
                ready = self.imageready()
        if ready is True:
            log.info('Image ready for download')

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
        self.put('position', {'Position': position})


##-------------------------------------------------------------------------
## Telescope Device
##-------------------------------------------------------------------------
class Telescope(Device):
    def __init__(self, IP, **args):
        Device.__init__(self, IP, **args, device='telescope')
        self.alignmentmode = self.get('alignmentmode')['Value']
        self.aperturearea = self.get('aperturearea')['Value']
        self.aperturediameter = self.get('aperturediameter')['Value']
        self.canfindhome = self.get('canfindhome')['Value']
        self.canpark = self.get('canpark')['Value']
        self.canpulseguide = self.get('canpulseguide')['Value']
        self.cansetdeclinationrate = self.get('cansetdeclinationrate')['Value']
        self.cansetguiderates = self.get('cansetguiderates')['Value']
        self.cansetpark = self.get('cansetpark')['Value']
        self.cansetpierside = self.get('cansetpierside')['Value']
        self.cansetrightascensionrate = self.get('cansetrightascensionrate')['Value']
        self.cansettracking = self.get('cansettracking')['Value']
        self.canslew = self.get('canslew')['Value']
        self.canslewaltaz = self.get('canslewaltaz')['Value']
        self.canslewaltazasync = self.get('canslewaltazasync')['Value']
        self.canslewasync = self.get('canslewasync')['Value']
        self.cansync = self.get('cansync')['Value']
        self.cansyncaltaz = self.get('cansyncaltaz')['Value']
        self.equatorialsystem = self.get('equatorialsystem')['Value']
        self.focallength = self.get('focallength')['Value']
        self.trackingrates = self.get('trackingrates')['Value']
        self.axisrates = self.get('axisrates')['Value']
        self.canmoveaxis = self.get('canmoveaxis')['Value']

    def altitude(self):
        return self.get('altitude')['Value']

    def athome(self):
        return self.get('athome')['Value']

    def atpark(self):
        return self.get('atpark')['Value']

    def azimuth(self):
        return self.get('azimuth')['Value']

    def declination(self):
        return self.get('declination')['Value']

    def declinationrate(self):
        return self.get('declinationrate')['Value']

    def set_declinationrate(self, declinationrate):
        self.put('declinationrate', {'DeclinationRate': declinationrate})

    def doesrefraction(self):
        return self.get('doesrefraction')['Value']

    def set_doesrefraction(self, doesrefraction):
        self.put('doesrefraction', {'DoesRefraction': doesrefraction})

    def guideratedeclination(self):
        return self.get('guideratedeclination')['Value']

    def set_guideratedeclination(self, guideratedeclination):
        self.put('guideratedeclination', {'GuideRateDeclination': guideratedeclination})

    def guideraterightascension(self):
        return self.get('guideraterightascension')['Value']

    def set_guideraterightascension(self, guideraterightascension):
        self.put('guideraterightascension', {'GuideRateRightAscension': guideraterightascension})

    def ispulseguiding(self):
        return self.get('ispulseguiding')['Value']

    def rightascension(self):
        return self.get('rightascension')['Value']

    def rightascensionrate(self):
        return self.get('rightascensionrate')['Value']

    def set_rightascensionrate(self, rightascensionrate):
        self.put('rightascensionrate', {'RightAscensionRate': rightascensionrate})

    def sideofpier(self):
        return self.get('sideofpier')['Value']

    def set_sideofpier(self, sideofpier):
        self.put('sideofpier', {'SideOfPier': sideofpier})

    def siderealtime(self):
        return self.get('siderealtime')['Value']

    def siteelevation(self):
        return self.get('siteelevation')['Value']

    def set_siteelevation(self, siteelevation):
        self.put('siteelevation', {'SiteElevation': siteelevation})

    def sitelatitude(self):
        return self.get('sitelatitude')['Value']

    def set_sitelatitude(self, sitelatitude):
        self.put('sitelatitude', {'SiteLatitude': sitelatitude})

    def sitelongitude(self):
        return self.get('sitelongitude')['Value']

    def set_sitelongitude(self, sitelongitude):
        self.put('sitelongitude', {'SiteLongitude': sitelongitude})

    def slewing(self):
        return self.get('slewing')['Value']

    def slewsettletime(self):
        return self.get('slewsettletime')['Value']

    def set_slewsettletime(self, slewsettletime):
        self.put('slewsettletime', {'SlewSettleTime': slewsettletime})

    def targetdeclination(self):
        return self.get('targetdeclination')['Value']

    def set_targetdeclination(self, targetdeclination):
        self.put('targetdeclination', {'TargetDeclination': targetdeclination})

    def targetrightascension(self):
        return self.get('targetrightascension')['Value']

    def set_targetrightascension(self, targetrightascension):
        self.put('targetrightascension', {'TargetRightAscension': targetrightascension})

    def tracking(self):
        return self.get('tracking')['Value']

    def set_tracking(self, tracking):
        self.put('tracking', {'Tracking': tracking})

    def trackingrate(self):
        return self.get('trackingrate')['Value']

    def set_trackingrate(self, trackingrate):
        self.put('trackingrate', {'TrackingRate': trackingrate})

    def utcdate(self):
        return self.get('utcdate')['Value']

    def set_utcdate(self, utcdate):
        self.put('utcdate', {'UTCDate': utcdate})

    def abortslew(self):
        self.put('abortslew', {})

    def destinationsideofpier(self):
        return self.get('destinationsideofpier')['Value']

    def findhome(self):
        self.put('findhome', {})

    def moveaxis(self, moveaxis):
        self.put('moveaxis', {'MoveAxis': moveaxis})

    def park(self):
        self.put('park', {})

    def pulseguide(self, direction, duration):
        self.put('pulseguide', {'Direction': direction, 'Duration': duration})

    def setpark(self):
        self.put('setpark', {})

    def slewtoaltaz(self, alt, az):
        self.put('slewtoaltaz', {'Azimuth': az, 'Altitude': alt})

    def slewtoaltazasync(self, alt, az):
        self.put('slewtoaltazasync', {'Azimuth': az, 'Altitude': alt})

    def slewtocoordinates(self, RA, dec):
        self.put('slewtocoordinates', {'RightAscension': RA, 'Declination': dec})

    def slewtocoordinatesasync(self, RA, dec):
        self.put('slewtocoordinatesasync', {'RightAscension': RA, 'Declination': dec})

    def slewtotarget(self):
        self.put('slewtotarget', {})

    def slewtotargetasync(self):
        self.put('slewtotargetasync', {})

    def synctoaltaz(self, alt, az):
        self.put('synctoaltaz', {'Azimuth': az, 'Altitude': alt})

    def synctocoordinates(self, RA, dec):
        self.put('synctocoordinates', {'RightAscension': RA, 'Declination': dec})

    def synctotarget(self):
        self.put('synctotarget', {})

    def unpark(self):
        self.put('unpark', {})






##-------------------------------------------------------------------------
## Command Line Test Program
##-------------------------------------------------------------------------
if __name__ == '__main__':
    IP = '10.0.1.104'
    port = 11111

    # c = Camera(IP=IP, port=port)
    # c.electronsperadu()
    # c.gain()
    # try:
    #     c.startexposure(1, light=False)
    # except AlpacaError as e:
    #     pass
    # else:
    #     c.waitfor_imageready(exptime=1)
    #     data = c.imagearray()
    # c.lastexposureduration()
    # c.lastexposurestarttime()
    # c.coolerpower()


#     f = Focuser(IP=IP, port=port)
#     f.ismoving()
#     f.position()
#     f.tempcomp()
#     f.temperature()

    t = Telescope(IP=IP, port=port)
