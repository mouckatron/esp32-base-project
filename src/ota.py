
import hashlib
import logging
import machine
import os
import re
import socket
import ubinascii
import _thread
from time import sleep


class OTAServer():

    request_re = re.compile('(GET|HEAD|POST|PUT)\s+(\S+)\s+(HTTP)/([0-9.]+)')
    header_re = re.compile('([a-zA-Z-]+): (.*)')

    def __init__(self):
        self._log = logging.getLogger('OTA')
        self._log.setLevel(logging.DEBUG)
        self.__bound = False

    def start(self):
        self._log.info("Starting server")
        _thread.start_new_thread(self.run, ())

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while not self.__bound:
            # somtimes during a soft reset, we cannot rebind the socket, keep trying
            try:
                s.bind(('', 8080))
                self.__bound = True
            except OSError as e:
                self._log.error(str(e))
                sleep(2)

        self._log.info("Listening")
        s.listen(5)

        while True:
            conn, addr = s.accept()

            write_success = None

            mr = MessageReader(conn)
            header = mr.get_until(b'\r\n\r\n')

            request = self.parse_request(header)
            headers = self.parse_headers(header)

            self._log.debug(str(request))
            self._log.debug(str(headers))

            m = re.search(b'Content-Length: ([0-9]+)', header)

            if m:
                length = int(m.group(1))
                data = mr.get_bytes(length)

                write_success = self.write_file('{}'.format(request['path']),
                                                data,
                                                headers['X-filehash'])

                if write_success:
                    conn.send('HTTP/1.1 200 OK\r\nConnection: close\r\n')

            conn.close()

            if write_success:
                self._log.info("Resetting")
                machine.reset()
                self._log.debug("After reset...")


    def parse_request(self, headers):

        line = headers.split(b'\r\n')[0]
        parsed = OTAServer.request_re.match(line.decode('ascii'))

        return {
            'verb': parsed.group(1),
            'path': parsed.group(2),
            'version': parsed.group(4)
            }

    def parse_headers(self, headers):

        lines = headers.split(b'\r\n')
        headers = {}

        for line in lines:
            try:
                parsed = OTAServer.header_re.match(line.decode('ascii'))
            except RuntimeError:
                continue
            else:
                try:
                    headers[parsed.group(1)] = parsed.group(2)
                except AttributeError:
                    pass

        return headers

    def write_file(self, filename, data, filehash):

        try:
            os.mkdir('/tmp')
        except OSError:
            pass

        tmp_filename = '/tmp/{}'.format(basename(filename.lstrip('/')))

        self._log.debug("writing to temp file ".format(tmp_filename))
        with open(tmp_filename, 'wb') as f:
            f.write(ubinascii.a2b_base64(data))

        _filehash = ubinascii.hexlify(hashlib.sha1(open(tmp_filename, 'rb').read()).digest()).decode('ascii')

        self._log.debug("incoming filehash: {}".format(filehash))
        self._log.debug(" written filehash: {}".format(_filehash))
        if filehash == _filehash:
            self._log.info("hashes match, overwriting file")
            os.rename(tmp_filename, filename)
            return True


class MessageReader(object):
    def __init__(self,sock):
        self.sock = sock
        self.buffer = b''

    def get_until(self,what):
        while what not in self.buffer:
            if not self._fill():
                return b''
        offset = self.buffer.find(what) + len(what)
        data,self.buffer = self.buffer[:offset],self.buffer[offset:]
        return data

    def get_bytes(self,size):
        while len(self.buffer) < size:
            if not self._fill():
                return b''
        data,self.buffer = self.buffer[:size],self.buffer[size:]
        return data

    def _fill(self):
        data = self.sock.recv(1024)
        if not data:
            if self.buffer:
                raise MessageError('socket closed with incomplete message')
            return False
        self.buffer += data
        return True

def split(path):
    if path == "":
        return ("", "")
    r = path.rsplit("/", 1)
    if len(r) == 1:
        return ("", path)
    head = r[0] #.rstrip("/")
    if not head:
        head = "/"
    return (head, r[1])

def dirname(path):
    return split(path)[0]

def basename(path):
    return split(path)[1]
