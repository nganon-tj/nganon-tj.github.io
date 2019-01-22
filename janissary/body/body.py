from ..recorded_game import EndOfData, BinReader

class Command(object):
    def __init__(self, command_type, command_data, unknown1):
        self.type = command_type
        self.data = command_data
        self.unknown1 = unknown1

    @staticmethod
    def parse(io):
        """Consume a command from the io object
        """
        length = io.read_u32()
        data = io.read(length)
        unknown = io.read_u32()
        # First word of data is the command type
        # Note that it is left in the data attribute of the 
        # command object
        command_type = BinReader.from_bytes(data).read_u8()
        return Command(command_type, data, unknown)

class Sync(object):
    def __init__(self, time, view_x, view_y, player_index):
        self.time = time
        self.view_x = view_x
        self.view_y = view_y
        self.player_index = player_index

    @staticmethod
    def parse(io):
        """Consume a Sync operation frmo the BinReader object
        """
        time = io.read_s32()
        # unknown
        unknown1 = io.read_u32()
        if unknown1 == 0:
            io.read(28)
        view_x = io.read_float()
        view_y = io.read_float()
        player_index = io.read_u32()
        return Sync(time, view_x, view_y, player_index)
    
class GameStart(object):
    def __init__(self):
        pass

class Chat(object):
    def __init__(self, message):
        self.message = message
    
    @staticmethod
    def parse(io):
        command = io.read_u32()
        # Special case here: apparently sometimes this operation can be used for 
        # a GameStart message, not a chat message. The first four bytes are a 
        # command that distinguishes
        if command == 0x1F4:
            io.read(20) # unknown meaning
            return GameStart()
        if command != 0xFFFFFFFF:
            raise RuntimeError("Got unexpected chat command %x" % command)

        length = io.read_u32()
        message = io.read(length)
        return Chat(message)

class BodyParser(object):
    def __init__(self, bin_reader):
        self._io = bin_reader
    
    def __iter__(self):
        self._io.seek(0)
        return self

    def __next__(self):
        try:
            op_type = self._io.read_u32()
            if op_type == 1:
                return Command.parse(self._io)
            elif op_type == 2:
                return Sync.parse(self._io)
            elif op_type == 4:
                return Chat.parse(self._io)
            else:
                raise RuntimeError("Unknown op type %d" % op_type)

        except EndOfData:
            raise StopIteration