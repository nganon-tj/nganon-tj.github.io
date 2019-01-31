from io import BytesIO
import struct

class EndOfData(Exception):
    pass

class BinReader(object):
    """Utility class used as a IO handle for parsers
    It look like any IO object, but with the addition of helper methods for
    concise reading of values (e.g. read_u32)
    """
    def __init__(self, data, offset=0):
        """Create a new BinReader
        data is a bytes, or an IO object from which to read
        offset optionally allows the derived stream to begin at the specified
        offset in data
        """
        if isinstance(data, bytes):
            self._data = BytesIO(data)
        else: # Assume it is an IO object
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
    