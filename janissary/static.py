CIVILIZATION_MAP = {
    1: "Britons",
    2: "Franks",
    3: "Goths",
    4: "Teutons",
    5: "Japanese",
    6: "Chinese",
    7: "Byzantines",
    8: "Persians",
    9: "Saracens",
    10: "Turks",
    11: "Vikings",
    12: "Mongols",
    13: "Celts",
    14: "Spanish",
    15: "Aztecs",
    16: "Mayans",
    17: "Huns",
    18: "Koreans",
}

# NOTE: It seems likely that all objects share the same ID namespace, and so
# buildings and units may be combined.
UNIT_MAP = {
    4: "Archer",
    5: "Hand Cannoneer",
    7: "Skirmisher",
    35: "Ram",
    39: "Cavalry Archer",
    74: "Infantry",
    83: "Peasant",
    93: "Pikeman",
    279: "Scorpion",
    280: "Onager",
    331: "Trebuchet",
    440: "Petard",
    725: "Jaguar Warrior",
    751: "Eagle Warrior"
}

BUILDING_TYPE_MAP = {
    12: "Barracks",
    49: "Siege Workshop",
    68: "Mill",
    70: "House",
    82: "Castle",
    84: "Market",
    87: "Archery Range",
    101: "Stables",
    103: "Blacksmith",
    109: "Town Hall",

}

MAP_TYPE_MAP = {
    9: "Arabia",
    10: "Archipelago",
    11: "Baltic",
    12: "Black Forest",
    13: "Coastal",
    14: "Continental",
    15: "Crater Lake",
    16: "Fortress",
    17: "Gold Rush",
    18: "Highland",
    19: "Islands",
    20: "Mediterranean",
    21: "Migration",
    22: "Rivers",
    23: "Team Islands",
    24: "Random",
    25: "Scandinavia",
    26: "Mongolia",
    27: "Yucatan",
    28: "Salt Marsh",
    29: "Arena",
    30: "King of the Hill",
    31: "Oasis",
    32: "Ghost Lake",
    33: "Nomad",
}

GAME_TYPE_MAP = {
    0: "Random Map",
    1: "Regicide",
    2: "Death Match",
    6: "King of the Hill"
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