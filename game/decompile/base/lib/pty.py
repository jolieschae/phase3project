# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\pty.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 4933 bytes
from select import select
import os, tty
__all__ = [
 'openpty', 'fork', 'spawn']
STDIN_FILENO = 0
STDOUT_FILENO = 1
STDERR_FILENO = 2
CHILD = 0

def openpty():
    try:
        return os.openpty()
    except (AttributeError, OSError):
        pass

    master_fd, slave_name = _open_terminal()
    slave_fd = slave_open(slave_name)
    return (master_fd, slave_fd)


def master_open():
    try:
        master_fd, slave_fd = os.openpty()
    except (AttributeError, OSError):
        pass
    else:
        slave_name = os.ttyname(slave_fd)
        os.close(slave_fd)
        return (master_fd, slave_name)
        return _open_terminal()


def _open_terminal():
    for x in 'pqrstuvwxyzPQRST':
        for y in '0123456789abcdef':
            pty_name = '/dev/pty' + x + y
            try:
                fd = os.open(pty_name, os.O_RDWR)
            except OSError:
                continue

            return (
             fd, '/dev/tty' + x + y)

    raise OSError('out of pty devices')


def slave_open(tty_name):
    result = os.open(tty_name, os.O_RDWR)
    try:
        from fcntl import ioctl, I_PUSH
    except ImportError:
        return result
    else:
        try:
            ioctl(result, I_PUSH, 'ptem')
            ioctl(result, I_PUSH, 'ldterm')
        except OSError:
            pass

        return result


def fork():
    try:
        pid, fd = os.forkpty()
    except (AttributeError, OSError):
        pass
    else:
        if pid == CHILD:
            try:
                os.setsid()
            except OSError:
                pass

        else:
            return (
             pid, fd)
            master_fd, slave_fd = openpty()
            pid = os.fork()
            if pid == CHILD:
                os.setsid()
                os.close(master_fd)
                os.dup2(slave_fd, STDIN_FILENO)
                os.dup2(slave_fd, STDOUT_FILENO)
                os.dup2(slave_fd, STDERR_FILENO)
                if slave_fd > STDERR_FILENO:
                    os.close(slave_fd)
                tmp_fd = os.open(os.ttyname(STDOUT_FILENO), os.O_RDWR)
                os.close(tmp_fd)
            else:
                os.close(slave_fd)
        return (pid, master_fd)


def _writen(fd, data):
    while data:
        n = os.write(fd, data)
        data = data[n:]


def _read(fd):
    return os.read(fd, 1024)


def _copy(master_fd, master_read=_read, stdin_read=_read):
    fds = [
     master_fd, STDIN_FILENO]
    while 1:
        rfds, wfds, xfds = select(fds, [], [])
        if master_fd in rfds:
            data = master_read(master_fd)
            if not data:
                fds.remove(master_fd)
            else:
                os.write(STDOUT_FILENO, data)
        if STDIN_FILENO in rfds:
            data = stdin_read(STDIN_FILENO)
            if not data:
                fds.remove(STDIN_FILENO)
            else:
                _writen(master_fd, data)


def spawn(argv, master_read=_read, stdin_read=_read):
    if type(argv) == type(''):
        argv = (
         argv,)
    else:
        pid, master_fd = fork()
        if pid == CHILD:
            (os.execlp)(argv[0], *argv)
        try:
            mode = tty.tcgetattr(STDIN_FILENO)
            tty.setraw(STDIN_FILENO)
            restore = 1
        except tty.error:
            restore = 0

    try:
        _copy(master_fd, master_read, stdin_read)
    except OSError:
        if restore:
            tty.tcsetattr(STDIN_FILENO, tty.TCSAFLUSH, mode)

    os.close(master_fd)
    return os.waitpid(pid, 0)[1]