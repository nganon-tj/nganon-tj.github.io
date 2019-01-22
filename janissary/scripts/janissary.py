import click
import janissary
import yaml
from tabulate import tabulate


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
    with open(gamefile, 'rb') as f:
        rec = janissary.RecordedGame(f)
        body = janissary.BodyParser(rec.body_bytes())
    
    command_counts = {}
    for op in body:
        if isinstance(op, janissary.Command):
            if op.type not in command_counts:
                command_counts[op.type] = 0
            command_counts[op.type] += 1
            print("Command %d\n" % op.type)
            if op.type == 0x81:
                print_hex(op.data)


    print("Cmd  | Count")
    print("------------")

    rows = []
    for k, v in command_counts.items():
        rows.append((k, COMMAND_NAME_MAP.get(k, "UNKNOWN"), v))
    
    print(tabulate(rows, headers=["CMD ID", "CMD Name", "Count"]))
