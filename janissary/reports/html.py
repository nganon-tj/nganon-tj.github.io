import jinja2
import json
import os

from .report import report

@jinja2.contextfunction                                                                                                                                                                                         
def include_file(ctx, name):                                                                                                                                                                                   
    env = ctx.environment                                                                                                                                                                                      
    return jinja2.Markup(env.loader.get_source(env, name)[0])  

def render_html(header_dict, timestamped_commands):
    report_data = report(header_dict, timestamped_commands)

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
    templateEnv.globals['include_file'] = include_file
    template = templateEnv.get_template("report.html")
    return template.render(
        game_attrs=report_data['header']['game_attributes'],
        players=report_data['header']['players'],
        command_summary=report_data['reports']['command_summary'],
        unit_production=report_data['reports']['unit_production'],
        jsdata=json.dumps(jsdata))