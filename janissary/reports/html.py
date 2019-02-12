import jinja2
import json
import os

from .report import report

@jinja2.contextfunction                                                                                                                                                                                         
def include_file(ctx, name):
    """Create a jinja2 function for including a file without parsing it as a template

    The standard jinja2 `include` function will attempt to parse the included 
    file as a template, and javascript (not enclosed in a <script> tag) is not a valid
    jinja2 template. 
    """
    env = ctx.environment
    return jinja2.Markup(env.loader.get_source(env, name)[0])  

def render_html(header_dict, timestamped_commands):
    """Returns HTML output for report file

    header_dict - A dict containing the information parsed from the header of the log file
    timestamped_commands - List of TimestampedCommand objects parsed from the body of the log file
    """
    report_data = report(header_dict, timestamped_commands)

    fileDir = os.path.dirname(os.path.realpath(__file__))
    searchpath = [os.path.join(fileDir, "templates/"), os.path.join(fileDir, "js/dist")]
    templateLoader = jinja2.FileSystemLoader(searchpath=searchpath)
    templateEnv = jinja2.Environment(loader=templateLoader)
    templateEnv.globals['include_file'] = include_file
    template = templateEnv.get_template("report.html")
    return template.render(jsdata=json.dumps(report_data))