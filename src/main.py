import setup

import etc
import machine
import ota
import logging

# Logging
logging.getLogger('').setLevel(logging.INFO)

# OTA
otaserver = ota.OTAServer()
otaserver.start()
