#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

# A simple stream-to-disk audio recorder.

import os
import subprocess
from diskrec.streamer import DiskStreamer

if os.name == 'nt':
    import win32file, win32pipe
    pipename = r'\\.\pipe\diskrec'
elif os.name == 'posix':
    pipename = '/tmp/diskrec.pipe'
else:
    raise 'DiskrecServer not implemented for {}'.format(os.name)

class DiskrecServer(object):
    '''A server for receiving requests to make direct-to-disk recordings.'''
    def __init__(self):
        self.buffersize = 4096
        self.streamer = None
        if os.name == 'nt':
            self._open_win()
        elif os.name == 'posix'
            self._open_posix()

    def listen(self):
        '''Listen for messages and act accordingly.'''
        while True:
            if os.name == 'nt':
                msg = self._read_win()
            elif os.name == 'posix'
                msg = self._read_posix()
            if msg.startswith('STARTREC '):
                nchan, fname = msg.replace('STARTREC ', '').split()
                self.streamer = DiskStreamer(fname, channels=int(nchan))
                self.streamer.start_stream()
            elif msg == 'STOPREC':
                self.streamer.stop_stream()
                self.streamer.close()
            elif msg == 'TERMINATE':
                self.close()
                break

    def _open_win(self):
        '''Open the pipe on a Windows system.'''
        try:
            self.handle = win32pipe.CreateNamedPipe(
                pipename,
                openmode,
                pipemode,
                maxinstances,
                self.buffersize,
                self.buffersize,
                defaulttimeout,
                securityattrib,
            )

    def _open_posix(self):
        '''Open the pipe on a posix system.'''
        try:
            os.mkfifo(pipe_name)
        except FileExistsError:
            pass
        self.pipein = open(pipe_name, os.O_RDONLY)

    def _read_win(self):
        resp = win32file.ReadFile(self.pipein, self.buffersize)

    def close(self):
        close(self.pipein)
