from io import BytesIO
import struct
import zlib

from .header import Header
from .utils import BinReader

class RecordedGame(object):
    def __init__(self, ioobj):
        self._file = ioobj
        self.header_length = self._get_header_length()

    def header_bytes(self):
        """Get the uncompressed header bytes
        """
        # Empirically, the first 4 bytes of the header are not part of the deflate
        # data; in fact it seems to be zeros, but maybe not all the time. Skip it. 
        self._file.seek(8) # 4 for length word, + 4 for unknown empty word
        data = zlib.decompress(self._file.read(self.header_length-8), -15)
        return data

    def header(self):
        """Return a Header parser object
        """
        header_bytes = self.header_bytes()
        header_io = BinReader(BytesIO(header_bytes))
        return Header(header_io)

    def body_bytes(self):
        """Get the uncompressed body bytes
        """
        self._file.seek(self.header_length)
        data = self._file.read()
        return data

    def _get_header_length(self):
        self._file.seek(0)
        # The first 4 bytes of the file appear to encode the length of the header
        return struct.unpack("<L", self._file.read(4))[0]


