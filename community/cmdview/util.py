import threading
import subprocess
import multiprocessing
from threading import Timer
import time


class SelfEmittingList(list):
    def __init__(self, call_on_emit, *args, **kwargs):
        self._call_on_emit = call_on_emit
        self._timer = None
        return super().__init__(*args, **kwargs)

    def _on_update(self):
        if self._timer:
            self._timer.cancel()
        def on_timer():
            self._timer = None
            self._call_on_emit(self)
            self[:] = []
        self._timer = Timer(0.2, on_timer)
        self._timer.start()

    def append(self, *args, **kwargs):
        self._on_update()
        return super().append(*args, **kwargs)


class PipedProcess(object):
    def __init__(self, cmd, func=threading.Thread): #threading.Thread / multiprocessing.Process
        self.cmd = cmd
        self.p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, universal_newlines=True)
        self.t = func(target=self.reader)
        self.te = func(target=self.readere)
        self.t.start()
        self.te.start()

    def writeline(self, t):
        self.p.stdin.write("{0}\n".format(t))

    def reader(self):
        while True:
            try:
                def on_emit(l):
                    print("STDOUT:", "".join(l))
                stdoutbuf = SelfEmittingList(on_emit)
                while True:
                    new = self.p.stdout.read(1)
                    if new:
                        stdoutbuf.append(new)
            except ValueError as e:
                print("Error reading STDOUT:", e)

    def readere(self):
        while True:
            try:
                def on_emit(l):
                    print("STDERR:", "".join(l))
                stderrbuf = SelfEmittingList(on_emit)
                while True:
                    new = self.p.stderr.read(1)
                    if new:
                        stderrbuf.append(new)
            except Exception as e:
                print("Error reading STDERR:", e)
