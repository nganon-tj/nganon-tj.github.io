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

class GameContext(object):
    """A context object for command parsers

    Sometimes parsing a command depends on previous commands. This object is
    used by all parsers to share a common state
    """
    def __init__(self):
        self.timestamp = 0
        self.last_selected_ids = []
        self.objects = {}
        self.unresolved_lookups = []

    def create_building(self, building_id, building_type, player_id):
        """Whenever a unit is trained, we learn about the building it was trained at
        """
        if building_id not in self.objects:
            self.objects[building_id] = {
                'type': 'building',
                'object_id': building_id,
                'object_type_id': building_type,
                'player_id': player_id
            }

    def create_unit(self, unit_id, unit_type_id, player_id):
        """Whenever we can, associate a type or a owner with a unit ID
        """
        if unit_id not in self.objects:
            self.objects[unit_id] = {
                'type': 'unit',
                'object_id': unit_id,
                'object_type_id': unit_type_id,
                'player_id': player_id
            }
        else:
            if unit_type_id is not None:
                self.objects[unit_id]['object_type_id'] = unit_type_id
            if player_id is not None:
                self.objects[unit_id]['player_id'] = player_id

    def lookup_player_from_objects(self, object_ids, callback=None):
        """Lookup a player based on a list of selected object IDs

        Works like `lookup_player_from_object`, but with a list of IDs. If we
        know the owner of any, we can return a player_id
        """
        # TODO: Objections in a selected group tell us that all of the objects
        # are owned by the same player. If we identify any one in the future, we
        # can identy all. We should track these associations.
        player_id = None
        for id in object_ids:
            player_id = self.lookup_player_from_object(id)
            if player_id is not None:
                break

        if callback is not None:
            if player_id is not None:
                callback(player_id)
            else:
                self.unresolved_lookups.append({
                    'object_id': object_ids,
                    'callback': callback
                })

        return player_id

    def lookup_player_from_object(self, object_id, callback=None):
        """Lookup a player based on a single building or unit ID

        If found, player_id is returned. Otherwise, None.
        However, it is possible that we do not know who owns the building yet,
        but that we will learn by the time we are finished parsingn the log. If
        a callback method is provided, it will be called either now, or after
        parsing the entire log with a single argument: the player id.
        """
        player_id = None
        if object_id in self.objects:
            player_id = self.objects[object_id]['player_id']

        if player_id is not None and callback is not None:
                callback(player_id)
        elif callback is not None:
            #no player id found, schedule to check later
            self.unresolved_lookups.append({
                'object_id': object_id,
                'callback': callback
            })

        return player_id # None if not found

    def resolve_lookups(self):
        for lu in self.unresolved_lookups:
            player_id = None
            if isinstance(lu['object_id'], list):
                for id in lu['object_id']:
                    player_id = self.lookup_player_from_object(id)
                    if player_id is not None:
                        break
            else:
                player_id = self.lookup_player_from_object(lu['object_id'])

            if player_id is not None:
                lu['callback'](player_id)

class TimestampedCommand(object):
    def __init__(self, command_type, command_data, game_context):
        self.type = command_type
        self.data = command_data
        self.timestamp = game_context.timestamp
        self._attributes = {}
        self.parse(game_context)

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

        Specific command types can override this if needed
        """
        return self._attributes

    def player_id(self):
        """Default blank player ID getter

        Specific command types which are able to infer the player ID should
        return it here
        """
        return self._attributes.get('player_id', None)

    def parse(self, game_context):
        """Default blank parse method

        To be overridden
        """
        pass

    @staticmethod
    def get_selected_ids(game_context, bin_reader, selection_count):
        selected_ids = None
        if selection_count == 0xFF:
            selected_ids = game_context.last_selected_ids.copy()
        else:
            selected_ids = [bin_reader.read_u32() for _ in range(selection_count)]
            game_context.last_selected_ids = selected_ids.copy()
        return selected_ids

class AttackCommand(TimestampedCommand):
    """Notably, this action is used for all right-click commands, so it isn't
    just attack
    """
    def parse(self, game_context):
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
        a['selected_ids'] = self.get_selected_ids(game_context, br, selection_count)

        for id in a['selected_ids']:
            game_context.create_unit(id, None, a['player_id'])

        self._attributes = a

class BackToWorkCommand(TimestampedCommand):
    def parse(self, game_context):
        a = {}
        br = BinReader(self.data)
        br.read_u8() # command id
        br.read(3) # padding
        a['building_id'] = br.read_u32()

        def player_id_callback(player_id):
            a['player_id'] = player_id
        game_context.lookup_player_from_object(a['building_id'], player_id_callback)

        self._attributes = a

class BuildCommand(TimestampedCommand):
    def parse(self, game_context):
        a = {}
        br = BinReader(self.data)
        br.read_u8() # command id
        selection_count = br.read_u8()
        a['player_id'] = br.read_u8()
        br.read_u8()
        a['x_coord'] = br.read_float()
        a['y_coord'] = br.read_float()
        a['building_type_id'] = br.read_u16()
        br.read_u16() # padding
        br.read_u32() # unknown
        br.read_u32() # sprite ID
        a['selected_ids'] = self.get_selected_ids(game_context, br, selection_count)

        self._attributes = a

class BuyCommand(TimestampedCommand):
    RESOURCE_TYPE = {
        0: "Food",
        1: "Wood",
        2: "Stone"
    }

    def parse(self, game_context):
        a = {}
        br = BinReader(self.data)
        br.read_u8() # command id
        a['player_id'] = br.read_u8()
        a['resource_type_id'] = br.read_u8()
        a['resource_type'] = self.RESOURCE_TYPE.get(a['resource_type_id'], "UNKNOWN")
        a['amount'] = br.read_u8()
        a['building_id'] = br.read_u32()
        # We learned that this is a market, owned by player
        game_context.create_building(a['building_id'], 84, a['player_id'])
        self._attributes = a

class DeleteCommand(TimestampedCommand):
    def parse(self, game_context):
        a = {}
        br = BinReader(self.data)
        br.read_u32() # command id + pad
        a['object_id'] = br.read_u32()
        a['player_id'] = br.read_u8()

        self._attributes = a

class GarrisonCommand(TimestampedCommand):
    GARRISON_TYPES = {
        1: "PACK", # For trebuchet
        2: "UNPACK", # For trebuchet
        4: "CANCEL", # when cancelling units in training queue
        5: "GARRISON", # garrisoning units in building or boat
    }
    def parse(self, game_context):
        a = {}
        br = BinReader(self.data)
        br.read_u8() # command id
        selection_count = br.read_u8()
        br.read_u16()
        a['building_id'] = br.read_u32()
        a['garrison_type_id'] = br.read_u8()
        a['garrison_type'] = self.GARRISON_TYPES.get(a['garrison_type_id'], "UNKNOWN")
        # I believe this is the position in the queue which is cancelled
        a['position'] = br.read_u8() # This may apply only to CANCEL commands. 
        br.read_u16()
        a['x_coord'] = br.read_float()
        a['y_coord'] = br.read_float()
        br.read_u32() # always FFs
        a['selected_ids'] = self.get_selected_ids(game_context, br, selection_count)
        def set_player_id(player_id):
            a['player_id'] = player_id
        game_context.lookup_player_from_objects(a['selected_ids'], set_player_id)
        self._attributes = a

class GuardCommand(TimestampedCommand):
    def parse(self, game_context):
        a = {}
        br = BinReader(self.data)
        br.read_u8() # command id
        selection_count = br.read_u8()
        br.read_u16() # pad
        a['guarded_id'] = br.read_u32()
        a['selected_ids'] = self.get_selected_ids(game_context, br, selection_count)

        def set_player_id(player_id):
            a['player_id'] = player_id
        game_context.lookup_player_from_object(a['guarded_id'], set_player_id)
        game_context.lookup_player_from_objects(a['selected_ids'], set_player_id)

        self._attributes = a

class MoveCommand(TimestampedCommand):
    def parse(self, game_context):
        a = {}
        br = BinReader(self.data)
        br.read_u8() # command id
        a['player_id'] = br.read_u8()
        br.read_u16()
        br.read_u32()
        selection_count = br.read_u32()
        a['x_coord'] = br.read_float()
        a['y_coord'] = br.read_float()
        a['selected_ids'] = self.get_selected_ids(game_context, br, selection_count)

        for id in a['selected_ids']:
            game_context.create_unit(id, None, a['player_id'])

        self._attributes = a

class MultipurposeCommand(TimestampedCommand):
    ACTION_TYPES = {
        0: "Diplomacy",
        1: "Change Game Speed",
        4: "Cheat Response",
        5: "Allied Victory",
        6: "Cheat",
        10: "Research Treason",
        11: "AI policy"
    }
    def parse(self, game_context):
        a = {}
        br = BinReader(self.data)
        br.read_u8() # command id
        a['action_type_id'] = br.read_u8()
        a['action_type'] = self.ACTION_TYPES.get(a['action_type_id'], 'UNKNOWN')
        # This field isn't actually the player ID in a cheat response
        if a['action_type'] != "Cheat Response":
            a['player_id'] = br.read_u8()
        else:
            a['cheat_response_value'] = br.read_u8()
        br.read_u8()
        a['option1'] = br.read_u8()
        br.read(3)
        a['option2'] = br.read_float()
        a['diplomatic_stance'] = br.read_u8()

        self._attributes = a

class RallyCommand(TimestampedCommand):
    def parse(self, game_context):
        a =  {}
        br = BinReader(self.data)
        br.read_u8() # command id
        selection_count = br.read_u8()
        br.read_u16()
        # I assume that one of these is the unique ID, and one is the type? But
        # I'm not really sure
        a['target_id'] = br.read_u32()
        a['target_unit_id'] = br.read_u32()
        a['x_coord'] = br.read_float()
        a['y_coord'] = br.read_float()
        a['selected_ids'] = self.get_selected_ids(game_context, br, selection_count)

        def set_player_id(player_id):
            a['player_id'] = player_id
        game_context.lookup_player_from_objects(a['selected_ids'], set_player_id)

        self._attributes = a

class ResearchCommand(TimestampedCommand):
    def parse(self, game_context):
        # NOTE: Could infer the type of the building here based on what's being researched, if we need it
        a = {}
        br = BinReader(self.data)
        br.read_u32()
        a['building_id'] = br.read_u32()
        a['player_id'] = br.read_u8()
        br.read_u8()
        a['technology_id'] = br.read_u16()
        self._attributes = a

class SellCommand(TimestampedCommand):
    RESOURCE_TYPE = {
        0: "Food",
        1: "Wood",
        2: "Stone"
    }

    def parse(self, game_context):
        a = {}
        br = BinReader(self.data)
        br.read_u8() # command id
        a['player_id'] = br.read_u8()
        a['resource_type_id'] = br.read_u8()
        a['resource_type'] = self.RESOURCE_TYPE.get(a['resource_type_id'], "UNKNOWN")
        a['amount'] = br.read_u8()
        a['building_id'] = br.read_u32()
        # We learned that this is a market, owned by player
        game_context.create_building(a['building_id'], 84, a['player_id'])
        self._attributes = a

class StanceCommand(TimestampedCommand):
    STANCE_TYPE = {
        0: "Aggressive",
        1: "Defensive",
        2: "Stand Ground",
        3: "Passive"
    }
    def parse(self, game_context):
        a = {}
        br = BinReader(self.data)
        br.read_u8() # command id
        selection_count = br.read_u8()
        a['stance_id'] = br.read_u8()
        a['selected_ids'] = self.get_selected_ids(game_context, br, selection_count)

        def set_player_id(player_id):
            a['player_id'] = player_id

        game_context.lookup_player_from_objects(a['selected_ids'], set_player_id)

        self._attributes = a

class StopCommand(TimestampedCommand):
    def parse(self, game_context):
        br = BinReader(self.data)
        br.read_u8() # command id
        selected_count = br.read_u8()
        a = {}
        a['selected_ids'] = self.get_selected_ids(game_context, br, selected_count)

        def set_player_id(player_id):
            a['player_id'] = player_id
        game_context.lookup_player_from_objects(a['selected_ids'], set_player_id)

        self._attributes = a

class TownBellCommand(TimestampedCommand):
    def parse(self, game_context):
        a = {}
        br = BinReader(self.data)
        br.read_u8() # command id
        br.read(3) # pad
        a['building_id'] = br.read_u32()
        a['active'] = br.read_u8()

        def set_player_id(player_id):
            a['player_id'] = player_id
        game_context.lookup_player_from_object(a['building_id'], set_player_id)

        self._attributes = a

class Train2Command(TimestampedCommand):
    def parse(self, game_context):
        a = {}
        br = BinReader(self.data)
        br.read_u8() # command id
        a['player_id'] = br.read_u8()
        a['building_type'] = br.read_u16()
        a['unknown1'] = br.read_u16()
        a['unit_type'] = br.read_u16()
        a['count'] = br.read_u16()
        a['building_id'] = br.read_u16()
        a['unknown2'] = br.read_u16()

        game_context.create_building(a['building_id'], a['building_type'], a['player_id'])

        self._attributes = a

class WallCommand(TimestampedCommand):
    def parse(self, game_context):
        a = {}
        br = BinReader(self.data)
        br.read_u8() # command id
        selection_count = br.read_u8()
        a['player_id'] = br.read_u8()
        a['start_x_coord'] = br.read_u8()
        a['start_y_coord'] = br.read_u8()
        a['end_x_coord'] = br.read_u8()
        a['end_y_coord'] = br.read_u8()
        br.read_u8() # pad
        a['building_type'] = br.read_u32()
        br.read_u32() # const
        a['selected_ids'] = self.get_selected_ids(game_context, br, selection_count)

        for id in a['selected_ids']:
            game_context.create_unit(id, None, a['player_id'])

        self._attributes = a

class WaypointCommand(TimestampedCommand):
    def parse(self, game_context):
        a = {}
        br = BinReader(self.data)
        br.read_u8() # command id
        a['player_id']  = br.read_u8()
        selection_count = br.read_u8()
        a['x_coord'] = br.read_u8()
        a['y_coord'] = br.read_u8()
        a['selected_ids'] = self.get_selected_ids(game_context, br, selection_count)

        for id in a['selected_ids']:
            # We learn who owns these units
            game_context.create_unit(id, None, a['player_id'])

        self._attributes = a

COMMAND_TYPE_MAP = {
    "ATTACK": AttackCommand,
    "BACKTOWORK": BackToWorkCommand,
    "BUILD": BuildCommand,
    "BUY": BuyCommand,
    "DELETE": DeleteCommand,
    "GARRISON": GarrisonCommand,
    "GUARD": GuardCommand,
    "MOVE": MoveCommand,
    "MULTIPURPOSE": MultipurposeCommand,
    "RALLY": RallyCommand,
    "RESEARCH": ResearchCommand,
    "SELL": SellCommand,
    "STANCE": StanceCommand,
    "STOP": StopCommand,
    "TOWNBELL": TownBellCommand,
    "TRAIN2": Train2Command,
    "WALL": WallCommand,
    "WAYPOINT": WaypointCommand,
}

def timestamped_commands(bin_reader):
    """Parses a body and returns a list of timestamped commands

    Timestamps are inferred from the preceding Sync. I don't think this is
    the exactly right timestamp for simulation of the game. But it is
    close enough for our report purposes.
    """
    parser = BodyParser(bin_reader)
    game_context = GameContext()
    commands = []
    for op in parser:
        if isinstance(op, Sync):
            game_context.timestamp += op.time_delta
        if isinstance(op, Command):
            # Create a specific derived type, if available
            cmd_name = command_name(op.type)
            if cmd_name in COMMAND_TYPE_MAP:
                cmdType = COMMAND_TYPE_MAP[cmd_name]
                tscmd = cmdType(op.type, op.data, game_context)
            else: # make generic
                tscmd = TimestampedCommand(op.type, op.data, game_context)
            commands.append(tscmd)

    # Go back and update any player ID requests that we didn't know at the time
    game_context.resolve_lookups()
    return commands

