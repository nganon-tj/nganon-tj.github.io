import janissary.body as body
import janissary.static as static

def collect_events(player_id, timestamped_commands, period_ms):
    """Collect the number of commands per second in each time window

    Arguments:
        player_id - Only commands from this player are considered
        timestamped_commands - list of TimestampedCommand objects
        period_ms - The binning resolution in miliseconds
    Returns:
        time, command_rate - A list of time points, and corresponding command
        rate at that time (normalized to commands per minute)
    """
    time = []
    command_rate = []
    cur_time = timestamped_commands[0].timestamp
    end_time = timestamped_commands[-1].timestamp

    all_command_types = []
    for cmd in timestamped_commands:
        if cmd.command_name() not in all_command_types:
            all_command_types.append(cmd.command_name())
    
    cmd_idx = 0
    while cur_time < end_time:
        commands_this_period = {'Total': 0}
        for cmd in all_command_types:
            commands_this_period[cmd] = 0

        while cmd_idx < len(timestamped_commands) and timestamped_commands[cmd_idx].timestamp < cur_time + period_ms:
            if timestamped_commands[cmd_idx].player_id() == player_id:
                commands_this_period['Total'] += 1
                commands_this_period[timestamped_commands[cmd_idx].command_name()] += 1
            cmd_idx += 1
        time.append(cur_time)
        # Normalize command counts to counts per minute
        for k, v in commands_this_period.items():
            commands_this_period[k] = 60 * v / (period_ms * 1e-3)
        command_rate.append(commands_this_period)
        cur_time += period_ms

    return time, command_rate

class ActionsRateReport(object):
    def __init__(self, header_dict, timestamped_commands):
        TIME_SERIES_PERIOD = 60 * 1000 # ms
        self._num_players = header_dict['num_players']
        self._header_dict = header_dict

        start_time = timestamped_commands[0].timestamp
        end_time = timestamped_commands[-1].timestamp

        self.series = {}
        self.average = {}
        for player_id in range(1, self._num_players + 1):
            time, command_rate = collect_events(player_id, timestamped_commands, TIME_SERIES_PERIOD)
            self.series[player_id] = [(t, r) for t, r in zip(time, command_rate)]
            count = sum([1 for cmd in timestamped_commands if cmd.player_id() == player_id])
            self.average[player_id] = float(count) * 1000.0 / (end_time - start_time)

    def serializeable(self):
        """Returns a serializable dict for this report

        Which can be serialized to, e.g. JSON or YAML
        """
        return {
            'series': self.series,
            'average': self.average
        }