# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\asynchat.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 11635 bytes
import asyncore
from collections import deque

class async_chat(asyncore.dispatcher):
    ac_in_buffer_size = 65536
    ac_out_buffer_size = 65536
    use_encoding = 0
    encoding = 'latin-1'

    def __init__(self, sock=None, map=None):
        self.ac_in_buffer = b''
        self.incoming = []
        self.producer_fifo = deque()
        asyncore.dispatcher.__init__(self, sock, map)

    def collect_incoming_data(self, data):
        raise NotImplementedError('must be implemented in subclass')

    def _collect_incoming_data(self, data):
        self.incoming.append(data)

    def _get_data(self):
        d = (b'').join(self.incoming)
        del self.incoming[:]
        return d

    def found_terminator(self):
        raise NotImplementedError('must be implemented in subclass')

    def set_terminator(self, term):
        if isinstance(term, str) and self.use_encoding:
            term = bytes(term, self.encoding)
        else:
            if isinstance(term, int):
                if term < 0:
                    raise ValueError('the number of received bytes must be positive')
        self.terminator = term

    def get_terminator(self):
        return self.terminator

    def handle_read(self):
        try:
            data = self.recv(self.ac_in_buffer_size)
        except BlockingIOError:
            return
        except OSError as why:
            try:
                self.handle_error()
                return
            finally:
                why = None
                del why

        if isinstance(data, str):
            if self.use_encoding:
                data = bytes(str, self.encoding)
        self.ac_in_buffer = self.ac_in_buffer + data
        while self.ac_in_buffer:
            lb = len(self.ac_in_buffer)
            terminator = self.get_terminator()
            if not terminator:
                self.collect_incoming_data(self.ac_in_buffer)
                self.ac_in_buffer = b''
            elif isinstance(terminator, int):
                n = terminator
                if lb < n:
                    self.collect_incoming_data(self.ac_in_buffer)
                    self.ac_in_buffer = b''
                    self.terminator = self.terminator - lb
                else:
                    self.collect_incoming_data(self.ac_in_buffer[:n])
                    self.ac_in_buffer = self.ac_in_buffer[n:]
                    self.terminator = 0
                    self.found_terminator()
            else:
                terminator_len = len(terminator)
                index = self.ac_in_buffer.find(terminator)
                if index != -1:
                    if index > 0:
                        self.collect_incoming_data(self.ac_in_buffer[:index])
                    self.ac_in_buffer = self.ac_in_buffer[index + terminator_len:]
                    self.found_terminator()
                else:
                    index = find_prefix_at_end(self.ac_in_buffer, terminator)
                    if index:
                        if index != lb:
                            self.collect_incoming_data(self.ac_in_buffer[:-index])
                            self.ac_in_buffer = self.ac_in_buffer[-index:]
                        break
                    else:
                        self.collect_incoming_data(self.ac_in_buffer)
                        self.ac_in_buffer = b''

    def handle_write(self):
        self.initiate_send()

    def handle_close(self):
        self.close()

    def push(self, data):
        if not isinstance(data, (bytes, bytearray, memoryview)):
            raise TypeError('data argument must be byte-ish (%r)', type(data))
        sabs = self.ac_out_buffer_size
        if len(data) > sabs:
            for i in range(0, len(data), sabs):
                self.producer_fifo.append(data[i:i + sabs])

        else:
            self.producer_fifo.append(data)
        self.initiate_send()

    def push_with_producer(self, producer):
        self.producer_fifo.append(producer)
        self.initiate_send()

    def readable(self):
        return 1

    def writable(self):
        return self.producer_fifo or not self.connected

    def close_when_done(self):
        self.producer_fifo.append(None)

    def initiate_send(self):
        while self.producer_fifo:
            if self.connected:
                first = self.producer_fifo[0]
                if not first:
                    del self.producer_fifo[0]
                    if first is None:
                        self.handle_close()
                        return
                obs = self.ac_out_buffer_size
                try:
                    data = first[:obs]
                except TypeError:
                    data = first.more()
                    if data:
                        self.producer_fifo.appendleft(data)
                    else:
                        del self.producer_fifo[0]
                    continue

                if isinstance(data, str):
                    if self.use_encoding:
                        data = bytes(data, self.encoding)
                try:
                    num_sent = self.send(data)
                except OSError:
                    self.handle_error()
                    return
                else:
                    if num_sent:
                        if num_sent < len(data) or obs < len(first):
                            self.producer_fifo[0] = first[num_sent:]
            else:
                del self.producer_fifo[0]
            return

    def discard_buffers(self):
        self.ac_in_buffer = b''
        del self.incoming[:]
        self.producer_fifo.clear()


class simple_producer:

    def __init__(self, data, buffer_size=512):
        self.data = data
        self.buffer_size = buffer_size

    def more(self):
        if len(self.data) > self.buffer_size:
            result = self.data[:self.buffer_size]
            self.data = self.data[self.buffer_size:]
            return result
        result = self.data
        self.data = b''
        return result


def find_prefix_at_end(haystack, needle):
    l = len(needle) - 1
    while l:
        haystack.endswith(needle[:l]) or l -= 1

    return l