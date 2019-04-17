#!/usr/env/python

## Import General Tools
import sys
import os
import argparse
import logging
import random
import time

import requests
import json

import numpy as np

##-------------------------------------------------------------------------
## Parse Command Line Arguments
##-------------------------------------------------------------------------
## create a parser object for understanding command-line arguments
p = argparse.ArgumentParser(description='''
''')
## add flags
p.add_argument("-v", "--verbose", dest="verbose",
    default=False, action="store_true",
    help="Be verbose! (default = False)")
## add options
# p.add_argument("--input", dest="input", type=str,
#     help="The input.")
## add arguments
# p.add_argument('argument', type=int,
#                help="A single argument")
# p.add_argument('allothers', nargs='*',
#                help="All other arguments")
args = p.parse_args()


##-------------------------------------------------------------------------
## Create logger object
##-------------------------------------------------------------------------
log = logging.getLogger('MyLogger')
log.setLevel(logging.DEBUG)
## Set up console output
LogConsoleHandler = logging.StreamHandler()
if args.verbose is True:
    LogConsoleHandler.setLevel(logging.DEBUG)
else:
    LogConsoleHandler.setLevel(logging.INFO)
LogFormat = logging.Formatter('%(asctime)s %(levelname)8s: %(message)s')
LogConsoleHandler.setFormatter(LogFormat)
log.addHandler(LogConsoleHandler)
## Set up file output
# LogFileName = None
# LogFileHandler = logging.FileHandler(LogFileName)
# LogFileHandler.setLevel(logging.DEBUG)
# LogFileHandler.setFormatter(LogFormat)
# log.addHandler(LogFileHandler)

class AlpacaError(Exception):
    pass

##-------------------------------------------------------------------------
## Abstract Alpaca Device
##-------------------------------------------------------------------------
class Device(object):
    def __init__(self, device, device_number=0, IP='127.0.0.1', port=11111,
                 ClientID=None, ClientTransactionID=0):
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
        j = json.loads(r.text)

        log.debug(f'  ClientTransactionID: {j["ClientTransactionID"]}')
        log.debug(f'  ServerTransactionID: {j["ServerTransactionID"]}')
        log.debug(f'  ErrorNumber: {j["ErrorNumber"]}')
        if j["ErrorNumber"] != 0:
            if type(j["ErrorMessage"]) == str:
                lines = j["ErrorMessage"].split('\n')
                log.error(f'  ErrorMessage: {lines[0]}')
                for v in lines[1:]:
                    log.error(f'                {v}')
            else:
                log.error(f'  ErrorMessage: {j["ErrorMessage"]}')

        if quiet is False:
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
            if type(j["ErrorMessage"]) == str:
                lines = j["ErrorMessage"].split('\n')
                log.error(f'  ErrorMessage: {lines[0]}')
                for v in lines[1:]:
                    log.error(f'                {v}')
            else:
                log.error(f'  ErrorMessage: {j["ErrorMessage"]}')
            raise AlpacaError

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
    def __init__(self, **args):
        Device.__init__(self, 'camera', **args)
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
                ready = self.imageready()
        if ready is True:
            log.info('Image ready for download')

    def ispulseguiding(self):
        return self.get('ispulseguiding', quiet=True)['Value']

    def lastexposureduration(self):
        return self.get('lastexposureduration', quiet=True)['Value']

    def lastexposuretime(self):
        return self.get('lastexposuretime', quiet=True)['Value']




    def startexposure(self, exptime, light=True):
        return self.put('startexposure', {'Duration': exptime, 'Light': light})

##-------------------------------------------------------------------------
## Command Line Test Program
##-------------------------------------------------------------------------
if __name__ == '__main__':
    IP = '10.0.1.103'
    port = 11111
    
#     t = Device('camera', IP=IP, port=port)
#     t.get('coolerpower')
#     t.get('ccdtemperature')
#     t.put('setccdtemperature', {'SetCCDTemperature': 5})
#     t.put('cooleron', {'CoolerOn': True})
#     sleep(10)
#     t.get('cooleron')
#     t.get('coolerpower')
#     t.get('ccdtemperature')

    c = Camera(IP=IP, port=port)
    c.electronsperadu()
    c.gain()
#     try:
#         c.startexposure(1, light=False)
#     except AlpacaError as e:
#         pass
#     else:
#         c.waitfor_imageready(exptime=1)
#         data = c.imagearray()
#     c.put('cooleron', {'CoolerOn': False})
#     c.coolerpower()
