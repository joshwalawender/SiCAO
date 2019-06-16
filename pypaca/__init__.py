verbose = True

##-------------------------------------------------------------------------
## Create logger object
##-------------------------------------------------------------------------
import logging
log = logging.getLogger('MyLogger')
log.setLevel(logging.DEBUG)
## Set up console output
LogConsoleHandler = logging.StreamHandler()
if verbose is True:
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


##-------------------------------------------------------------------------
## AlpacaError
##-------------------------------------------------------------------------
class AlpacaError(Exception):
    pass

from . import devices
