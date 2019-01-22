import janissary
import yaml

def test_header_length(datafile):
    with open(datafile('example_v5.8.aoe2record'), 'rb') as f:
        rec = janissary.RecordedGame(f)
        assert rec.header_length == 0x17450

def test_header_version(datafile):
    with open(datafile('example_v5.8.aoe2record'), 'rb') as f:
        rec = janissary.RecordedGame(f)
        assert rec.header().get_version() == ("VER 9.4", 12.5)

def test_header_bytes(datafile):
    with open(datafile('example_v5.8.aoe2record'), 'rb') as f:
        rec = janissary.RecordedGame(f)
        header_bytes = rec.header_bytes()

        header_data = rec.header().header_dict()
        with open('header.yml') as output:
            yaml.dump(header_data, outfile, default_flow_style=False)
            