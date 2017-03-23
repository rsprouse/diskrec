#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

# A simple stream-to-disk audio recorder.

import os
import win32file, win32pipe

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
        if os.name == 'nt':
            self.pipeout = win32file.CreateFile(
                pipename,
                win32file.GENERIC_WRITE | win32file.GENERIC_READ,
                0,
                None,
                win32file.OPEN_EXISTING,
                0,
                None
            )
     #       win32pipe.ConnectNamedPipe(self.pipeout, None)
        elif os.name == 'posix':
            self.pipeout = os.open(pipename, os.O_WRONLY)

    def write(self, msg):
        if os.name == 'nt':
            self._write_win(msg)
        elif os.name == 'posix':
            self._write_posix(msg)

    def _write_win(self, msg):
        res, j = win32file.WriteFile(self.pipeout, msg)

    def _write_posix(self, msg):
        os.write(self.pipeout, msg)

    def close(self):
        if os.name == 'nt':
            self._close_win()
        elif os.name == 'posix':
            self._close_posix()

    def _close_win(self):
        win32file.CloseHandle(self.pipeout)

    def _close_posix(self):
        os.close(self.pipeout)
