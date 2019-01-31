
import janissary.static as static

class CommandSummaryReport(object):
    def __init__(self, header_dict, timestamped_commands):
        self._num_players = header_dict['num_players']
        self._header_dict = header_dict
        self._player_commands = {}
        self._unassigned_commands = {}
        for c in timestamped_commands:
            if c.player_id() is not None:
                self._count_player_command(c.player_id(), c.type)
            else:
                self._count_unassigned_command(c.type)

    def _count_player_command(self, player_id, cmd_id):
        if cmd_id not in self._player_commands:
            self._player_commands[cmd_id] = {x+1: 0 for x in range(self._num_players)}
        self._player_commands[cmd_id][player_id] += 1
    
    def _count_unassigned_command(self, cmd_id):
        if cmd_id not in self._unassigned_commands:
            self._unassigned_commands[cmd_id] = 0
        self._unassigned_commands[cmd_id] += 1

    def player_command_headers(self):
        """Return a list of strings which can be used as a header to table
        
        e.g. ["Player", "ATTACK", "MOVE", ...]
        """
        command_ids = self._player_commands.keys()
        command_names = [static.command_name(x) for x in command_ids]
        return ["Player"] + sorted(command_names)

    def player_command_rows(self):
        """Return a list of lists, one per player for table display

        These correspond to the header returned by player_command_headers()
        e.g. [(Player1, ATTACK_COUNT, MOVE_COUNT, ...), (Player2, ATTACK_COUNT, MOVE_COUNT, ...)]
        """
        command_ids = self._player_commands.keys()
        command_names = [static.command_name(x) for x in command_ids]
        idnames = zip(command_ids, command_names)
        idnames = sorted(idnames, key=lambda x: x[1])
        rows = []
        for player_id in range(1, self._num_players+1):
            player_name = self._header_dict['players'][player_id-1]['name']
            row = [player_name]
            for cidname in idnames:
                row.append(self._player_commands[cidname[0]][player_id])
            rows.append(row)
        return rows

    def unassigned_command_headers(self):
        command_ids = self._unassigned_commands.keys()
        command_names = [static.command_name(x) for x in command_ids]
        return command_names
    
    def unassigned_command_counts(self):
        """Return a single row of command counts that are not assigned to a player
        """
        command_ids = self._unassigned_commands.keys()
        return [self._unassigned_commands[cid] for cid in command_ids]

