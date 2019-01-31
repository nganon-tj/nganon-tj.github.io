import click
import janissary
import janissary.body
import yaml
from tabulate import tabulate

from janissary.static import command_name
from janissary.report import render_html


@click.group()
def main():
    pass

@main.command()
@click.argument('gamefile')
def version(gamefile):
    """Read the version info from a log file
    """
    with open(gamefile, 'rb') as f:
        rec = janissary.RecordedGame(f)
        version, sub_version = rec.header().get_version()
    print("Version: %s, subversion: %f" % (version, sub_version))


@main.command()
@click.argument('gamefile')
@click.argument('outputfile')
def header_raw(gamefile, outputfile):
    """Store the raw, uncompressed bytes of the header
    """

    print("Writing header from %s to %s...\n" % (gamefile, outputfile))
    with open(gamefile, 'rb') as input:
        rec = janissary.RecordedGame(input)
        header = rec.header_bytes()
    
    with open(outputfile, 'wb') as f:
        f.write(header)

@main.command()
@click.argument('gamefile')
@click.argument('outputfile')
def header_yaml(gamefile, outputfile):
    """Store the parsed contents of the header as YAML
    """

    print("Writing header from %s to %s...\n" % (gamefile, outputfile))
    with open(gamefile, 'rb') as input:
        rec = janissary.RecordedGame(input)
        header = rec.header().header_dict()
    
    with open(outputfile, 'w') as f:
        yaml.dump(header, f, default_flow_style=False)

@main.command()
@click.argument('gamefile')
@click.argument('outputfile')
def body_raw(gamefile, outputfile):
    """Store the raw body bytes to a file
    """
    with open(gamefile, 'rb') as input:
        rec = janissary.RecordedGame(input)
        with open(outputfile, 'wb') as output:
            output.write(rec.body_bytes())


COMMAND_NAME_MAP = {
    0x0B: "RESIGN",
    0x65: "RESEARCH",
    0x77: "TRAIN",
    0x64: "TRAIN SINGLE",
    0x66: "BUILD",
    0x6C: "TRIBUTE",
    0xFF: "POSTGAME"
} 

def print_hex(data):
    counter = 0
    s = ""
    for b in data:
        if (counter % 16) == 0:
            if counter != 0:
                s += "\n"
            s += "%04x: " % counter
        counter += 1
        s += "%02x" % b
        if (counter % 2) == 0:
            s += " "
    print(s)

@main.command()
@click.argument('gamefile')
def command_summary(gamefile):
    """Print some info about the commands found in the log body (debug)
    """
    with open(gamefile, 'rb') as f:
        rec = janissary.RecordedGame(f)
        body = janissary.BodyParser(janissary.BinReader(rec.body_bytes()))
    
    command_counts = {}
    for op in body:
        if isinstance(op, janissary.Sync):
            print("Sync %d" % op.time)
        if isinstance(op, janissary.Command):
            if op.type not in command_counts:
                command_counts[op.type] = 0
            command_counts[op.type] += 1
            if op.type == 0x81:
                print("Command %x" % op.type)
                print_hex(op.data)


    print("Cmd  | Count")
    print("------------")

    rows = []
    for k, v in command_counts.items():
        rows.append(("0x%02x" % k, command_name(k), v))
    rows = sorted(rows, key=lambda x: x[0])
    
    print(tabulate(rows, headers=["CMD ID", "CMD Name", "Count"]))

@main.command()
@click.argument('gamefile')
@click.argument('outputfile')
def command_yaml(gamefile, outputfile):
    """Create a yaml output with commands
    """
    with open(gamefile, 'rb') as f:
        rec = janissary.RecordedGame(f)
        body_reader = janissary.BinReader(rec.body_bytes())
        commands = janissary.body.timestamped_commands(body_reader)
    
    commands = [c.serializable() for c in commands]
    with open(outputfile, 'w') as f:
        yaml.dump(commands, f)


@main.command()
@click.argument('gamefile')
def sync_summary(gamefile):
    """Print a list of sync message (debug)
    """
    with open(gamefile, 'rb') as f:
        rec = janissary.RecordedGame(f)
        body_reader = janissary.BinReader(rec.body_bytes())

    body = janissary.BodyParser(body_reader)
    for op in body:
        if isinstance(op, janissary.Sync):
            print("SYNC time_delta=%d, player_id=%d" % (op.time_delta, op.player_index))

@main.command()
@click.argument('gamefile')
@click.argument('htmlfile')
def report(gamefile, htmlfile):
    """Render html report"""
    with open(gamefile, 'rb') as f:
        rec = janissary.RecordedGame(f)
        header_dict = rec.header().header_dict()
        body_reader = janissary.BinReader(rec.body_bytes())
        timestamped_commands = janissary.body.timestamped_commands(body_reader)
    
    with open(htmlfile, 'w') as f:
        f.write(render_html(header_dict, timestamped_commands))