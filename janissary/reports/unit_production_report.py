import math

import janissary.body as body
import janissary.static as static

class UnitLogEntry(object):
    def __init__(self, player_id, unit_type, building_id, delta, timestamp):
        self.player_id = player_id
        self.unit_type = unit_type
        self.building_id = building_id
        self.delta = delta
        self.timestamp = timestamp

    def serializeable(self):
        return self.__dict__

class UnitProductionReport(object):
    """Count the number of units produced throughout the game
    
    Provides cumulative total, and time series

    There's a big caveat to these numbers: If multiple types of units 
    are produced at the same building, and some are cancelled, we can't 
    reliably tell which unit was cancelled. This is because we would have to
    know exactly what units were in the queue at the time of the cancel command.
    We can improve this somewhat, by including a model of unit production time,
    but even still, I think there are many cases that cannot be readily solved. 
    Consider:
      - Every unit has different build times
      - The build time for units depends on current research and player civ
      - Unit queues may be stopped by lack of houses
      - Without cycle accurate synchronization, there are race conditions: what
        happens if a cancel command nearly coincides with the completion of a 
        unit? It's important to process these events in the correct order, but
        it will be difficult to infer a sufficiently accurate model to do so 
        from outside the game. 

    There's a second caveat: It doesn't account for initial units that are 
    present at the start of the game. This information should be in the header,
    and could be extracted in the future. 

    Still, these errors are small enough that I believe the results are still 
    interesting, if not always precise. In the vast majority of situations, 
    hundreds of units will be produced, and no more than a handful of CANCEL
    commands will be incorrectly applied. 
    """

    
    def __init__(self, header_dict, timestamped_commands):
        self._num_players = header_dict['num_players']
        self._header_dict = header_dict
        self.unit_log = []
        self._type_ids = []
        
        unique_cancel_commands = {}
        
        for cmd in timestamped_commands:
            # TODO: I believe other versions of the game use the TRAIN
            # command for this same purpose. But as I haven't tried to parse
            # any of these, I don't support it yet. 
            attr = cmd.attributes()
            if isinstance(cmd, body.Train2Command):
                self.unit_log.append(UnitLogEntry(
                    attr['player_id'],
                    attr['unit_type'],
                    attr['building_id'],
                    attr['count'],
                    cmd.timestamp))
                # Pre-compute a list of all the type IDs trained in the game
                # TODO: Order columns more sensically, by category, or building they are produced at
                if attr['unit_type'] not in self._type_ids:
                    self._type_ids.append(attr['unit_type'])
            elif isinstance(cmd, body.GarrisonCommand) and attr['garrison_type'] == 'CANCEL':
                # Cancel the last unit produced in the specified building
                # This is quite naive, as it could have been any unit in the 
                # queue that was cancelled. We don't know which, but we could
                # create a model of training time to make better guesses. 

                # Empirically, it seems its possible to send multiple cancel commands in 
                # the same timestamp, and that these duplicates are not acted upon. So 
                # remove duplicate cancels by skipping this command if we've seen it
                # before, and storing its hash to check later if we have not. 
                cmd_hash = hash((attr['building_id'], cmd.timestamp))
                if cmd_hash in unique_cancel_commands:
                    continue
                unique_cancel_commands[cmd_hash] = True

                entry_to_update = None
                if len(attr['selected_ids']) != 1:
                    raise RuntimeError("CANCEL command has %d selected_ids. what do? (%s)" % attr)
                for entry in reversed(self.unit_log):
                    if entry.building_id == attr['selected_ids'][0]:
                        entry_to_update = entry
                        break
                if entry_to_update is None:
                    # I don't believe this is possible, so will fail loudly if it occurs
                    #raise RuntimeError("Couldn't find corresponding TRAIN command for CANCEL: %s" % attr)
                    print("Couldn't find corresponding TRAIN command for CANCEL: %s" % attr)
                    continue
                if entry_to_update.delta == 1:
                    self.unit_log.remove(entry_to_update)
                else:
                    entry_to_update.delta -= 1

        self.time_vector = self._compute_time_points(timestamped_commands)
        
    def unit_log_for_player(self, player_id):
        return [x for x in self.unit_log if x.player_id == player_id]
    
    def total_units_table_header(self):
        return ["Unit"] + [self._header_dict['players'][player_id]['name'] for player_id in range(self._num_players)]

    def total_units_rows(self):
        rows = []
        for type_id in self._type_ids: 
            row = [static.unit_name(type_id)]
            for player_id in range(1, self._num_players + 1):
                row.append(self._count_total(player_id=player_id, unit_type=type_id))
            rows.append(row)
        return rows
             
    def _count_total(self, player_id=None, unit_type=None):
        count = 0
        for entry in self.unit_log:
            if (player_id is None or entry.player_id == player_id) and \
                (unit_type is None or entry.unit_type == unit_type):
                count += entry.delta
        return count

    @staticmethod
    def _compute_time_points(timestamped_commands, deltaT=60.0):
        time = []
        cur_time = round(timestamped_commands[0].timestamp * 1e-3 / 60.0) * 60.0
        end_time = timestamped_commands[-1].timestamp * 1e-3
        while cur_time < end_time: 
            time.append(cur_time)
            cur_time += deltaT
        return time
    
    def _compute_player_counts(self):
        def _compute_unit_counts(player_id):
            player_log = self.unit_log_for_player(player_id)
            # Collect all the unit types built by this player during the game
            unit_counts = {}
            for entry in player_log:
                if entry.unit_type not in unit_counts:
                    unit_counts[entry.unit_type] = {
                        'unit_name': static.unit_name(entry.unit_type),
                        'counts': []
                    }
            
            log_idx = 0
            period_counter = { unit_id: 0 for unit_id in unit_counts.keys() }
            for cur_time in self.time_vector:
                while log_idx < len(player_log):
                    entry = player_log[log_idx]
                    if entry.timestamp * 1e-3 > cur_time:
                        break
                    log_idx += 1
                    period_counter[entry.unit_type] += entry.delta

                for unit_id in unit_counts.keys(): 
                    unit_counts[unit_id]['counts'].append(period_counter[unit_id])
            return unit_counts

        player_counts = {}
        for player_id in range(1, self._num_players + 1):
            player_counts[player_id] = {
                'player_name': self._header_dict['players'][player_id-1]['name'],
                'units': _compute_unit_counts(player_id)
            }
        
        return player_counts

    def serializeable(self):
        """Return a serializeable dict representing the report
    
        For serialization to, e.g. JSON or YAML
        """
        return {
            'unit_log': [entry.serializeable() for entry in self.unit_log],
            'total_units_table': {
                'header': self.total_units_table_header(),
                'rows': self.total_units_rows()
            },
            'series': {
                'time': self.time_vector,
                'players': self._compute_player_counts()
            }
        }
