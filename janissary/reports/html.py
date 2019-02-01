import jinja2
import json
import os


from .command_summary_report import CommandSummaryReport
from .unit_production_report import UnitProductionReport
from .actions_rate_report import ActionsRateReport
import janissary.static as static

def render_html(header_dict, timestamped_commands):
    # Collect a subset of game level config options to display
    game_attributes = [
        ('Title', header_dict['game_title']),
        ('Map Size', header_dict['map_size']),
        ('Map Type', static.map_type_name(header_dict['map_id'])),
        ('Game Type', static.game_type_name(header_dict['game_type'])),
    ]

    def decorated_player(p):
        return {
            'name': p['name'],
            'civilization_name': static.civilization_name(p['civ']),
            'team': p['team']
        }
    players = [decorated_player(p) for p in header_dict['players']]
    command_summary = CommandSummaryReport(header_dict, timestamped_commands)
    unit_production = UnitProductionReport(header_dict, timestamped_commands)
    actions_rate = ActionsRateReport(header_dict, timestamped_commands)

    jsdata = {
        'aps_graph': {
            'series': actions_rate.series,
            'players': {x['player_index']: x['name'] for x in header_dict['players']}
        }
    }

    fileDir = os.path.dirname(os.path.realpath(__file__))
    searchpath = [os.path.join(fileDir, "templates/"), os.path.join(fileDir, "js/dist")]
    templateLoader = jinja2.FileSystemLoader(searchpath=searchpath)
    templateEnv = jinja2.Environment(loader=templateLoader)
    template = templateEnv.get_template("report.html")
    return template.render(
        game_attrs=game_attributes,
        players=players,
        command_summary=command_summary,
        unit_production=unit_production,
        jsdata=json.dumps(jsdata))