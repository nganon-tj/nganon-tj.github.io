import janissary
from janissary.reports import CommandSummaryReport

def test_command_summary_v58(datafile):
    with open(datafile('example_v5.8.aoe2record'), 'rb') as f:
        rec = janissary.RecordedGame(f)
        body_reader = janissary.BinReader(rec.body_bytes())
        timestamped_commands = janissary.body.timestamped_commands(body_reader)
        header_dict = rec.header().header_dict()

    report = CommandSummaryReport(header_dict, timestamped_commands)

    expected_headers = ["Player", "ATTACK", "BUILD", "GARRISON", "MOVE", 
        "MULTIPURPOSE", "RALLY", "RESEARCH", "TOWNBELL", "TRAIN2", "WALL", "WAYPOINT"]
    expected_rows = [
        ["Squisher", 79, 37, 3, 212, 0, 0, 11, 0, 49, 0, 0],
        ["punkkiri", 74, 37, 1, 124, 3, 5, 3, 1, 36, 5, 1],
    ]
    assert report.player_command_headers() == expected_headers
    assert report.player_command_rows() == expected_rows

    # TODO: Check the unassigned values, but this is still in flux and most of them will be assigned


