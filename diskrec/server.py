#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

# A simple stream-to-disk audio recorder.

import os
import threading
from diskrec.streamer import DiskStreamer

if os.name == 'nt':
    import win32file, win32pipe
    pipename = r'\\.\pipe\diskrec'
elif os.name == 'posix':
    pipename = '/tmp/diskrec.pipe'
else:
    raise 'DiskrecServer not implemented for {}'.format(os.name)

class DiskrecServer(threading.Thread):
    '''A server for receiving requests to make direct-to-disk recordings.'''
    def __init__(self):
        self.pipename = pipename
        self.outbufsize = 65536
        self.inbufsize = 65536
        self.streamer = None
        if os.name == 'nt':
            self._open_win()
        elif os.name == 'posix':
            self._open_posix()

    def listen(self):
        '''Listen for messages and act accordingly.'''
        #win32pipe.ConnectNamedPipe(self.pipein, None)
        while True:
            msg = ''
            try:
                if os.name == 'nt':
                    msg = self._read_win()
                elif os.name == 'posix':
                    msg = self._read_posix()
            except:
                pass
            msg = msg.decode('utf-8')
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
        openmode = win32pipe.PIPE_ACCESS_DUPLEX
        pipemode = win32pipe.PIPE_TYPE_MESSAGE | \
                   win32pipe.PIPE_READMODE_MESSAGE | \
                   win32pipe.PIPE_WAIT
        maxinstances = 1
        defaulttimeout = 0
        securityattrib = None
        try:
            self.pipein = win32pipe.CreateNamedPipe(
                self.pipename,
                openmode,
                pipemode,
                maxinstances,
                self.outbufsize,
                self.inbufsize,
                defaulttimeout,
                securityattrib,
            )
            if self.pipein == win32file.INVALID_HANDLE_VALUE:
                raise 'Error calling CreateNamedPipe.'
        except:
# TODO:
            raise

    def _open_posix(self):
        '''Open the pipe on a posix system.'''
        try:
            os.mkfifo(self.pipename)
        except FileExistsError:
            pass
        self.pipein = os.open(self.pipename, os.O_RDONLY | os.O_NONBLOCK)

    def _read_win(self):
        res, data = win32file.ReadFile(self.pipein, self.inbufsize)
        return data

    def _read_posix(self):
        resp = os.read(self.pipein, self.inbufsize)
        return resp

    def close(self):
        if os.name == 'nt':
            self._close_win()
        elif os.name == 'posix':
            self._close_posix()

    def _close_win(self):
        win32file.CloseHandle(self.pipein)

    def _close_posix(self):
        os.close(self.pipein)
