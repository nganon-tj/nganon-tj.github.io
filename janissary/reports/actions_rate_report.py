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

    cmd_idx = 0
    while cur_time < end_time:
        commands_this_period = 0
        while cmd_idx < len(timestamped_commands) and timestamped_commands[cmd_idx].timestamp < cur_time + period_ms:
            if timestamped_commands[cmd_idx].player_id() == player_id:
                commands_this_period += 1
            cmd_idx += 1
        time.append(cur_time)
        command_rate.append(60.0 * float(commands_this_period) / (period_ms * 1e-3) )
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
