#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

# A simple stream-to-disk audio recorder.

import os
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
        while True:
            try:
                if os.name == 'nt':
                    msg = self._read_win()
                elif os.name == 'posix':
                    msg = self._read_posix()
            except:
                pass
            print('read {}'.format(msg))
            if msg.startswith('STARTREC '.encode('utf-8')):
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
        print('_open_win')
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
            win32pipe.ConnectNamedPipe(self.pipein, None)
        except:
# TODO:
            raise
        print('opened')

    def _open_posix(self):
        '''Open the pipe on a posix system.'''
        try:
            os.mkfifo(self.pipename)
        except FileExistsError:
            pass
        self.pipein = os.open(self.pipename, os.O_RDONLY | os.O_NONBLOCK)

    def _read_win(self):
        print('reading')
        res, data = win32file.ReadFile(self.pipein, self.inbufsize)
        print('read')
        print('result ', res)
        print('data ', data)
        return data

    def _read_posix(self):
        resp = os.read(self.pipein, self.inbufsize)
        return resp

    def close(self):
# TODO: posix vs. win
        os.close(self.pipein)
