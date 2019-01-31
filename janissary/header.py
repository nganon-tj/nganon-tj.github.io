import struct 

class Header(object):
    def __init__(self, bin_reader):
        """Create a header, using a BinReader as data source
        """
        self._data = bin_reader
    
    def get_version(self):
        """Returns version, and subversion from header file
        """
        
        # First 8 bytes contain a fixed length header string
        # Its follwed by a float subversion
        self._data.seek(0)
        version = self._data.read(8).decode('utf-8').rstrip('\x00')
        sub_version = self._data.read_float()
        return version, sub_version
        
    
    def header_dict(self):
        sio = self._data
        sio.seek(12)

        # def read(fmt, size):
        #     return struct.unpack("<%s" % fmt, sio.read(size))[0]

        # def read_string():
        #     len = sio.read_u16()
        #     return sio.read(len)
    
        d = {}
        
        version = sio.read_float() # Yes...apparently the version is a float
        d['version'] = version
        print("aoe2record version = %f", version)
        sio.read_u32()
        sio.read_u32()

        print("Reading datasets @ %d\n" % sio.tell())
        # No idea what these mean, but many thanks to whoever figured out that 
        # these bytes must be skipped
        datasets_count = sio.read_u32()

        d['datasets'] = [sio.read_u32() for _ in range(datasets_count)]
        
        d['difficulty'] = sio.read_u32()
        d['map_size'] = sio.read_u32()
        d['map_id'] = sio.read_u32()
        d['reveal_map'] = sio.read_u32()
        d['victory_type'] = sio.read_u32()
        d['starting_resources'] = sio.read_u32()
        d['starting_age'] = sio.read_u32()
        d['ending_age'] = sio.read_u32()
        d['game_type'] = sio.read_u32()
        
        if d['version'] >= 1006.0:
            # Unknown. There seems to be an extra 32-bit word in HD 5.8
            sio.read_u32()

        # 'separator'
        sio.read_u32()

        if d['version'] == 1000.0:
            d['map_name'] = sio.read_string()
            d['pad_string1'] = sio.read_string()

        # separator
        sio.read_u32()

        print("Reading game_speed @ %04x" % sio.tell())
        d['game_speed'] = sio.read_float()
        d['treaty_length'] = sio.read_u32()
        d['pop_limit'] = sio.read_u32()
        d['num_players'] = sio.read_u32()

        # unknown
        sio.read_u32()
        sio.read_u32()

        # separator
        sio.read_u32()

        d['trading_enabled'] = sio.read_u8()
        d['team_bonus_disabled'] = sio.read_u8()
        d['randomize_positions'] = sio.read_u8()
        d['full_tech_tree_enabled'] = sio.read_u8()
        d['number_of_starting_units'] = sio.read_u8()
        d['teams_locked'] = sio.read_u8()
        d['speed_locked'] = sio.read_u8()
        d['multiplayer'] = sio.read_u8()
        d['cheats_enabled'] = sio.read_u8()
        d['record_game_enabled'] = sio.read_u8()
        d['animals_enabled'] = sio.read_u8()
        d['predators_enabled'] = sio.read_u8()

        # separator
        sio.read_u32()

        # unknown
        sio.read_u32()
        sio.read_u32()

        if version < 1004.0:
            raise RuntimeError("Need to implement some things for older versions")
        
        players = []

        print("Beginning reading players @ %d" % sio.tell())
        for i in range(8):
            # unknown
            sio.read_u16()

            p = {}
            # I believe this is a hash of players data files
            p['data_crc'] = sio.read_u32()
            if version >= 1006.0:
                p['mp_version'] = sio.read_u16()
            else:
                p['mp_version'] = sio.read_u8()
            p['team'] = sio.read_u32()
            p['civ'] = sio.read_u32()
            p['ai_base_name'] = sio.read_string()
            p['ai_civ_name_idx'] = sio.read_u8()
            if version >= 1005.0:
                p['unknown_name'] = sio.read_string()
            
            p['name'] = sio.read_string()
            print("Reading player %d ('%s') @ %d\n" % (i, p['name'], sio.tell()))
            p['humanity'] = sio.read_u32()
            p['steam_id'] = sio.read_u64()
            p['player_index'] = sio.read_u32()
            p['unknown1'] = sio.read_u32()
            p['scenario_index'] = sio.read_u32()
            # It seems there's more data in each player block. I have no idea 
            # what it is; but I need to consume 8 more bytes to align with the
            # strings. All the fields after the player name may be wrong. 
            sio.read(8)  
            players.append(p)

        d['players'] = players[0:d['num_players']]
        
        #unknown
        sio.read_u8()

        d['fog_of_war'] = sio.read_u8()
        d['cheat_notification'] = sio.read_u8()
        d['colored_chat'] = sio.read_u8()

        # separator
        sio.read_u32()

        d['is_ranked'] = sio.read_u8()
        d['allow_spectators'] = sio.read_u8()

        d['lobby_visibility'] = sio.read_u32()
        d['custom_random_map_file_crc'] = sio.read_u32()

        # inknown ishes
        d['custom_scenario_or_campaign_file'] = sio.read_string()
        d['unknown1'] = sio.read_u64()
        d['custom_random_map_file'] = sio.read_string()
        d['unknown2'] = sio.read_u64()
        d['custom_random_map_scenario_file'] = sio.read_string()
        d['unknown3'] = sio.read_u64()
        
        # guid
        sio.read(16)
        d['game_title'] = sio.read_string()
        d['modded_dataset_title'] = sio.read_string()
        d['modded_dataset_workshop_id'] = sio.read_u64()
        
        if version >= 1005.0:
            d['unknown_string1'] = sio.read_string()
            d['unknown4'] = sio.read_u32()
        elif version >= 1004.0:
            sio.read_u64()
        
        return d
