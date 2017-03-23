#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

# A simple stream-to-disk audio recorder.

import os

if os.name == 'nt':
    import win32file
    pipename = r'\\.\pipe\diskrec'
elif os.name == 'posix':
    pipename = '/tmp/diskrec.pipe'
else:
    raise 'DiskrecClient not implemented for {}'.format(os.name)

class DiskrecClient(object):
    '''A class for communicating with a DiskrecServer.'''
    def __init__(self):
        self.pipeout = os.open(pipename, os.O_WRONLY)

    def write(self, msg):
        os.write(self.pipeout, msg)

    def close(self):
        close(self.pipeout)
