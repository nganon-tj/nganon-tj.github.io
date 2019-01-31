from .utils import EndOfData, BinReader
from .static import command_name

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
        self.time_delta = time
        self.view_x = view_x
        self.view_y = view_y
        self.player_index = player_index

    @staticmethod
    def parse(io):
        """Consume a Sync operation frmo the BinReader object
        """
        time_delta = io.read_s32()
        # unknown
        unknown1 = io.read_u32()
        if unknown1 == 0:
            io.read(28)
        view_x = io.read_float()
        view_y = io.read_float()
        player_index = io.read_u32()
        return Sync(time_delta, view_x, view_y, player_index)
    
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
    """Provide iterator to iterate over the operations stored in the log body
    """
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

class TimestampedCommand(object):
    def __init__(self, command_type, command_data, timestamp):
        self.type = command_type
        self.data = command_data
        self.timestamp = timestamp
    
    def command_name(self):
        return command_name(self.type)

    def serializable(self):
        """Return a serializable dict version of the command

        Suitable for serializing to JSON
        """
        r = {}
        r['id'] = self.type
        r['name'] = command_name(self.type)
        r['time'] = self.timestamp
        r['bytes'] = [b for b in self.data]
        r['attributes'] = self.attributes()
        return r

    def attributes(self):
        """Default blank attribute parser

        Specific command types can override this to parse the payload into a
        dict of attributes
        """
        return {}

    def player_id(self):
        """Default blank player ID getter

        Specific command types which are able to infer the player ID should
        return it here
        """
        return None

class BuildCommand(TimestampedCommand):
    def player_id(self):
        br = BinReader(self.data)
        br.seek(2)
        return br.read_u8()

    def attributes(self):
        a = {}
        br = BinReader(self.data)
        br.read_u8() # command id
        a['selection_count'] = br.read_u8()
        a['player_id'] = br.read_u8()
        br.read_u8()
        a['x_coord'] = br.read_float()
        a['y_coord'] = br.read_float()
        a['building_id'] = br.read_u16()
        br.read_u16() # padding
        br.read_u32() # unknown
        br.read_u32() # sprite ID
        a['selected_ids'] = [br.read_u32() for _ in range(a['selection_count'])]
        return a

class ResearchCommand(TimestampedCommand):
    def player_id(self):
        br = BinReader(self.data)
        br.seek(8)
        return br.read_u8()
    
    def attributes(self):
        a = {}
        br = BinReader(self.data)
        br.read_u32()
        a['building_id'] = br.read_u32()
        a['player_id'] = br.read_u8()
        br.read_u8()
        a['technology_id'] = br.read_u16()
        return a

class AttackCommand(TimestampedCommand):
    """Notably, this action is used for all right-click commands, so it isn't 
    just attack
    """
    def player_id(self):
        br = BinReader(self.data)
        br.seek(1)
        return br.read_u8()
    
    def attributes(self):
        a = {}
        br = BinReader(self.data)
        br.read_u8() # command id
        a['player_id'] = br.read_u8()
        br.read_u16()
        # The ID of the targetted object (Do trees have IDs??)
        a['target_id'] = br.read_u32()
        selection_count = br.read_u32()
        a['x_coord'] = br.read_float()
        a['y_coord'] = br.read_float()
        a['selected_ids'] = [br.read_u32() for _ in range(selection_count)]
        return a

class MoveCommand(TimestampedCommand):
    def player_id(self):
        br = BinReader(self.data)
        br.seek(1)
        return br.read_u8()

    def attributes(self):
        br = BinReader(self.data)
        br.read_u8() # command id
        a = {}
        a['player_id'] = br.read_u8()
        br.read_u16()
        br.read_u32()
        selection_count = br.read_u32()
        a['x_coord'] = br.read_float()
        a['y_coord'] = br.read_float()
        if selection_count < 0xff:
            a['selected_ids'] = [br.read_u32() for _ in range(selection_count)]
        else:
            a['selected_ids'] = []
        
class StopCommand(TimestampedCommand):
    def attributes(self):
        br = BinReader(self.data)
        br.read_u8() # command id
        selected_count = br.read_u8()
        return {'selected_ids': [br.read_u32() for _ in range(selected_count)]}

class Train2Command(TimestampedCommand):
    def attributes(self):
        return {}

    
COMMAND_TYPE_MAP = {
    "ATTACK": AttackCommand,
    "BUILD": BuildCommand,
    "MOVE": MoveCommand,
    "TRAIN2": Train2Command,
    "STOP": StopCommand,
    "RESEARCH": ResearchCommand,
}

def timestamped_commands(bin_reader):
    """Parses a body and returns a list of timestamped commands
    
    Timestamps are inferred from the preceding Sync. I don't think this is 
    the exactly right timestamp for simulation of the game. But it is
    close enough for our report purposes. 
    """
    parser = BodyParser(bin_reader)
    lastTime = 0
    commands = []
    for op in parser:
        if isinstance(op, Sync):
            lastTime += op.time_delta
        if isinstance(op, Command):
            # Create a specific derived type, if available
            cmd_name = command_name(op.type)
            if cmd_name in COMMAND_TYPE_MAP:
                cmdType = COMMAND_TYPE_MAP[cmd_name] 
                tscmd = cmdType(op.type, op.data, lastTime)
            else: # make generic
                tscmd = TimestampedCommand(op.type, op.data, lastTime)
            commands.append(tscmd)
    return commands

