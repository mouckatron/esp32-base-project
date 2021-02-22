#! /usr/bin/env python3

import base64
import binascii
import hashlib
import requests

FILE = '../src/ota.py'

sha1hash = binascii.hexlify(hashlib.sha1(open(FILE, 'rb').read()).digest())

print(sha1hash)

files = base64.b64encode(open(FILE, 'rb').read())


requests.put('http://192.168.0.153:8080/ota.py',
             headers = {'X-filehash': sha1hash},
             data=files)
