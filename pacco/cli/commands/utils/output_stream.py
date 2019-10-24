import sys


class OutputStream:
    def __init__(self):
        self._stream = sys.stdout
        self._stream_err = sys.stderr

    def writeln(self, data, error=False):
        self.write(data, newline=True, error=error)

    def write(self, data, newline=False, error=False):
        if newline:
            data = "%s\n" % data
        if error:
            self._write_err(data)
        else:
            self._write(data)

    def _write(self, data):
        self._stream.write(data)

    def _write_err(self, data):
        self._stream_err.write(data)
