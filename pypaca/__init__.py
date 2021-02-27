import random
import requests
import json
import logging

import numpy as np


class AlpacaDeviceError(Exception): pass


##-------------------------------------------------------------------------
## Abstract Alpaca Device
##-------------------------------------------------------------------------
class AlpacaDevice(object):
    def __init__(self, IP='localhost', port=11111, device=None, device_number=0,
                 ClientID=None, ClientTransactionID=0, logger=None):
        alpaca_devices = ['switch', 'safetymonitor', 'dome', 'camera',
                          'observingconditions', 'filterwheel', 'focuser',
                          'rotator', 'telescope']
        if device not in alpaca_devices:
            raise AlpacaDeviceError(f'Device "{device}" not in standard Alpaca device list')
        self.device = device
        self.logger = logger
        self.log(f'Connecting to {device}', level=logging.INFO)
        if ClientID is None:
            self.clientID = int(random.random() * 65535)
        else:
            self.clientID = ClientID
        self.transactionID = ClientTransactionID
        self.IP = IP
        self.port = port
        self.device_number = device_number
        self.url = f"http://{IP}:{port}/api/v1/{self.device}/{self.device_number}/"
        self.log(f'URL: {self.url}', level=logging.DEBUG)

        self.core_proprty_names = ['name', 'description', 'supportedactions',
                                   'driverinfo', 'driverversion']
        self.properties = self.get_device_properties()
        self.log(f'Connected to {self.device}: "{self.properties["name"]}"',
                 level=logging.INFO)


    def get_device_properties(self):
        properties = {}
        if hasattr(self, 'property_names'):
            for pname in (self.core_proprty_names + self.property_names):
                properties[pname] = self.get(pname)['Value']
                self.log(f'{pname} = {properties[pname]}', level=logging.INFO)
        return properties


    def log(self, msg, level=logging.DEBUG):
        if self.logger: self.logger.log(level, f"{self.device:>15s}: {msg}")


    def get(self, command, quiet=False):
        self.log(f'GET {command}', level=logging.DEBUG)
        payload = {'ClientID': self.clientID,
                   'ClientTransactionID': self.transactionID,
                   }
        r = requests.get(self.url + command, data=payload)
        if r.status_code == 200:
            try:
                j = json.loads(r.text)
                self.log(f'  ClientTransactionID: {j["ClientTransactionID"]}', level=logging.DEBUG)
                self.log(f'  ServerTransactionID: {j["ServerTransactionID"]}', level=logging.DEBUG)
                self.log(f'  ErrorNumber: {j["ErrorNumber"]}', level=logging.DEBUG)
                if j["ErrorNumber"] != 0:
                    loglv = logging.WARNING if j["ErrorNumber"] != -2146233088 else logging.DEBUG
                    self.log(f'GET {command} failed.  ErrorNumber {j["ErrorNumber"]}', level=loglv)
                    if type(j["ErrorMessage"]) == str:
                        lines = j["ErrorMessage"].split('\n')
                        self.log(f'  ErrorMessage: {lines[0]}', level=loglv)
                        for v in lines[1:]:
                            self.log(f'                {v}', level=loglv)
                    else:
                        self.log(f'  ErrorMessage: {j["ErrorMessage"]}', level=loglv)

                if quiet is False and j["ErrorNumber"] == 0:
                    if type(j["Value"]) == str:
                        lines = j["Value"].split('\n')
                        self.log(f'GET {command}: {lines[0]}', level=logging.DEBUG)
                        for v in lines[1:]:
                            self.log(f'               {v}')
                    else:
                        self.log(f'GET {command}: {j["Value"]}', level=logging.DEBUG)

                self.transactionID += 1
                if self.transactionID > 4294967295:
                    self.transactionID -= 4294967295
                return j
            except json.JSONDecodeError as e:
                if self.log: self.log(f'GET {command} failed: {e.msg}')
                return {'Value': None,
                        'ErrorNumber': -1,
                        'ErrorMessage': e.msg,
                       }
        elif r.status_code == 400:
            self.log(f'400: Invalid request. "{self.url + command}"', level=logging.ERROR)
            self.log(f'  {r.text}', level=logging.ERROR)
            return {'Value': None}
        elif r.status_code == 500:
            self.log(f'500: Unexpected device error', level=logging.ERROR)
            self.log(f'  {r.text}', level=logging.ERROR)
            return {'Value': None}
        else:
            self.log(f'{r.status_code}: {r.text}', level=logging.ERROR)
            return {'Value': None}


    def put(self, command, contents):
        s = ', '.join([f'{key} = {contents[key]}' for key in contents.keys()])
        self.log(f'PUT {command}: {s}')

        default = {'ClientID': self.clientID,
                   'ClientTransactionID': self.transactionID,
                   }
        payload = {**default, **contents}
        r = requests.put(self.url + command, data=payload)
        j = json.loads(r.text)

        self.log(f'  ClientTransactionID: {j["ClientTransactionID"]}', level=logging.DEBUG)
        self.log(f'  ServerTransactionID: {j["ServerTransactionID"]}', level=logging.DEBUG)
        self.log(f'  ErrorNumber: {j["ErrorNumber"]}', level=logging.DEBUG)
        if j["ErrorNumber"] != 0:
            self.log(f'PUT {command}: {s} failed', level=logging.WARNING)
            if type(j["ErrorMessage"]) == str:
                lines = j["ErrorMessage"].split('\n')
                self.log(f'  ErrorMessage: {lines[0]}', level=logging.WARNING)
                for v in lines[1:]:
                    self.log(f'                {v}', level=logging.WARNING)
            else:
                self.log(f'  ErrorMessage: {j["ErrorMessage"]}', level=logging.WARNING)
            raise AlpacaDeviceError(j["ErrorMessage"])

        self.transactionID += 1
        if self.transactionID > 4294967295:
            self.transactionID -= 4294967295
        return j


    def get_connected(self):
        j = self.get('connected')
        return j['Value']


from .camera import Camera
from .filterwheel import FilterWheel
from .focuser import Focuser
from .telescope import Telescope
