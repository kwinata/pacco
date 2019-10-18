import sys


class OutputStream:
    def __init__(self):
        self._stream = sys.stdout
        self._stream_err = sys.stderr

    def writeln(self, data, error=False):
        self.write(data, newline=True, error=error)

    def _write(self, data, newline=False):
        if newline:
            data = "%s\n" % data
        self._stream.write(data)

    def _write_err(self, data, newline=False):
        if newline:
            data = "%s\n" % data
        self._stream_err.write(data)

    def write(self, data, newline=False, error=False):
        if error:
            self._write_err(data, newline)
        else:
            self._write(data, newline)
