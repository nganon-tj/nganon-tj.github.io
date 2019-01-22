from io import BytesIO
import struct
import zlib

from .header.header import Header

class EndOfData(Exception):
    pass

class BinReader(object):
    """Utility class used as a IO handle for parsers
    It look like any IO object, but with the addition of helper methods for
    concise reading of values (e.g. read_u32)
    """
    def __init__(self, data, offset=0):
        """Create a new BinReader
        data is an IO object from which to read
        offset optionally allows the derived stream to begin at the specified
        offset in data
        """
        self._data = data
        self._offset = offset

    def seek(self, pos):
        self._data.seek(pos + self._offset)

    def tell(self):
        return self._data.tell() - self._offset

    def read(self, length):
        return self._data.read(length)

    def read_fmt(self, fmt, size):
        d = self._data.read(size)
        if len(d) < size:
            raise EndOfData
        return struct.unpack("<%s" % fmt, d)[0]
    
    def read_u8(self):
        return self.read_fmt("B", 1)

    def read_u16(self):
        return self.read_fmt("H", 2)
    
    def read_u32(self):
        return self.read_fmt("L", 4)

    def read_s32(self):
        return self.read_fmt("l", 4)

    def read_u64(self):
        return self.read_fmt("Q", 8)

    def read_float(self):
        return self.read_fmt("f", 4)
    
    def read_string(self):
        """Strings in the aoe2record file header are stored with a 2-byte 
        length, followed by the string
        """

        len = self.read_u16()
        strcode = self.read_u16()
        if strcode != 0x0A60: 
            print("WARNING: Got unexpected string code %04x @ pos %d" % (strcode, self.tell() - 4))
        return self._data.read(len).decode('utf-8')
    
    @staticmethod
    def from_bytes(data):
        return BinReader(BytesIO(data))
    
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


