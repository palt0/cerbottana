import glob
import json

import pytest

import plugins.points as points

basepath = "tests/fixtures/websocket/tournament/end"


@pytest.mark.parametrize("testfile", glob.glob(basepath + "**/*.json"))
def test_generator(testfile: str, generate_golden: bool) -> None:
    print(f"Testing against: {testfile}")
    tourdata: points.TournamentEnd
    with open(testfile) as testdata:
        tourdata = json.load(testdata)

    leaderboard = points.parse_tourdata(tourdata)

    golden_path = testfile + ".golden"
    if generate_golden:
        with open(golden_path, "w+") as golden:
            json.dump(leaderboard, golden)
    else:
        with open(golden_path) as golden:
            expected_leaderboard = json.load(golden)
            assert expected_leaderboard == leaderboard
