import random
import requests
import json

import numpy as np


class AlpacaDeviceError(Exception):
    pass


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
            raise AlpacaDeviceError(f'Device "{device}" not in standard Alpaca device list')
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
            raise AlpacaDeviceError(j["ErrorMessage"])

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


