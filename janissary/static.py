CIVILIZATION_MAP = {
    0: "Unknown 0"
}

UNIT_MAP = {
    0: "Unknown Unit 0"
}

BUILDING_TYPE_MAP = {
    12: "Barracks",
    70: "House",
    87: "Archery Range"
}

MAP_TYPE_MAP = {
}

GAME_TYPE_MAP = {
}

COMMAND_NAME_MAP = {
    0x00: "ATTACK",
    0x01: "STOP",
    0x02: "AI_PRIMARY",
    0x03: "MOVE",
    0x0A: "AI_MOVE",
    0x0B: "RESIGN",
    0x10: "WAYPOINT",
    0x12: "STANCE",
    0x13: "GUARD",
    0x14: "FOLLOW",
    0x15: "PATROL",
    0x17: "FORMATION",
    0x1b: "SAVEEXIT",
    0x1F: "AI_COORD",
    0x64: "AI_TRAIN",
    0x0B: "RESIGN",
    0x65: "RESEARCH",
    0x66: "BUILD",
    0x67: "MULTIPURPOSE",
    0x69: "WALL",
    0x6A: "DELETE",
    0x6B: "ATTACKGROUND",
    0x6C: "TRIBUTE",
    0x6E: "REPAIR",
    0x6F: "UNGARRISON",
    0x72: "GATE",
    0x73: "FLAIR",
    0x75: "GARRISON",
    0x77: "TRAIN",
    0x78: "RALLY",
    0x7A: "SELL",
    0x7B: "BUY",
    0x7E: "DROPRELIC",
    0x7F: "TOWNBELL",
    0x80: "BACKTOWORK",
    0x81: "TRAIN2",
    0xFF: "POSTGAME",
} 

def civilization_name(civ_id):
    if civ_id in CIVILIZATION_MAP:
        return CIVILIZATION_MAP[civ_id]
    else:
        return "Unknown civilization %d" % civ_id

def unit_name(unit_id):
    if unit_id in UNIT_MAP:
        return UNIT_MAP[unit_id]
    else:
        return "Unknown Unit %d" % unit_id

def command_name(command_id):
    return COMMAND_NAME_MAP.get(command_id, "UNKNOWN %02x" % command_id)
            
def map_type_name(map_id):
    return MAP_TYPE_MAP.get(map_id, "UNKNOWN (%d)" % map_id)

def game_type_name(game_type):
    return GAME_TYPE_MAP.get(game_type, "UNKNOWN (%d)" % game_type)