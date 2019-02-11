from typing import List

from .command_summary_report import CommandSummaryReport
from .unit_production_report import UnitProductionReport
from .actions_rate_report import ActionsRateReport

from janissary.body import TimestampedCommand
import janissary.static as static
    

def report(header_dict, timestamped_commands: List[TimestampedCommand]):
    """Return a dict with all report outputs
    
    This dict is what gets serialized to JSON and passed to the React display
    app.
    """
    def decorated_player(p: dict) -> dict:
        return {
            'player_id': p['player_index'],
            'name': p['name'],
            'civilization_name': static.civilization_name(p['civ']),
            'team': p['team']
        }

    report =  {
        "header_raw": header_dict,
        "header": {
            "game_attributes": [
                ('Title', header_dict['game_title']),
                ('Map Size', header_dict['map_size']),
                ('Map Type', static.map_type_name(header_dict['map_id'])),
                ('Game Type', static.game_type_name(header_dict['game_type'])),
            ],
            "players": [decorated_player(p) for p in header_dict['players']]
        },
        "reports": {},
        "commands": [c.serializable() for c in timestamped_commands]
    }

    report["reports"]["command_summary"] = CommandSummaryReport(header_dict, timestamped_commands).serializeable()
    report["reports"]["unit_production"] = UnitProductionReport(header_dict, timestamped_commands).serializeable()
    report["reports"]["actions_rate"] = ActionsRateReport(header_dict, timestamped_commands).serializeable()

    return report