import logging

import numpy as np
from astropy.io import fits

from . import AlpacaDevice, AlpacaDeviceError


##-------------------------------------------------------------------------
## Telescope Device
##-------------------------------------------------------------------------
class Telescope(AlpacaDevice):
    def __init__(self, **kwargs):
        self.property_names = ['alignmentmode',
                               'canfindhome', 'canpark', 'canpulseguide',
                               'cansetdeclinationrate', 'cansetguiderates',
                               'cansetpark', 'cansetpierside',
                               'cansetrightascensionrate', 'cansettracking',
                               'canslew', 'canslewaltaz', 'canslewaltazasync',
                               'canslewasync', 'cansync', 'cansyncaltaz',
                               'equatorialsystem', 'trackingrates',
                               ]
        super().__init__(**kwargs, device='telescope')


    ##-------------------------------------------------------------------------
    ## Required Methods for ObservatoryControlSystem
    ##-------------------------------------------------------------------------
    def slew(self, coord):
        self.log(f"Slewing to {coord.to_string('hmsdms', sep=':', precision=1)}",
                 level=logging.INFO)
        self.slewtocoordinates(coord.ra.deg/15, coord.dec.deg)


    def collect_header_metadata(self):
        h = fits.Header()
        h['TELNAME'] = (self.properties['name'],
                        'Telescope Name')
        h['TELDVRSN'] = (self.properties['driverversion'],
                         'Telescope Driver Version')
        h['ALT'] = (self.altitude(), 'Altitude (deg)')
        h['AZ'] = (self.azimuth(), 'Azimuth (deg)')
        if h['ALT'] > 0:
            h['AIRMASS'] = (( np.sin( (h['ALT'] + 244/(165+47*h['ALT']))*np.pi/180 ) )**-1,
                            'Airmass (Pickering, 2002 formula)')
        else:
            h['AIRMASS'] = (100, 'Airmass (low elevation)')
        h['RA'] = (self.rightascension(), 'Right Ascension (hours)')
        h['DEC'] = (self.declination(), 'Declination (deg)')
        h['RARATE'] = (self.rightascensionrate(), 'Right Ascension Trim Rate')
        h['DECRATE'] = (self.declinationrate(), 'Declination Trim Rate')
        h['PIERSIDE'] = (self.sideofpier(), 'Side of Pier')
        h['TRACKING'] = (self.tracking(), 'Tracking')
        return h


    ##-------------------------------------------------------------------------
    ## Alpaca Methods
    ##-------------------------------------------------------------------------
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
        self.log('Parking telescope')
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
        self.log('Unparking telescope')
        self.put('unpark', {})


