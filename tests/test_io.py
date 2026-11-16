"""CSV input/output and the command line."""

from __future__ import annotations

import csv

import pytest

from elevator_sim.__main__ import main
from elevator_sim.csv_io import load_requests

SPEC = "time,id,source,dest\n0,passenger1,1,51\n0,passenger2,1,37\n10,passenger3,20,1\n"


def write(tmp_path, text):
    path = tmp_path / "requests.csv"
    path.write_text(text)
    return path


def test_reads_the_briefs_format(tmp_path):
    requests = load_requests(write(tmp_path, SPEC))
    assert [(r.time, r.id, r.source, r.dest) for r in requests] == [
        (0, "passenger1", 1, 51), (0, "passenger2", 1, 37), (10, "passenger3", 20, 1)]


@pytest.mark.parametrize("text", ["time,id,source,dest\n0,a,1,3,extra\n", "time,id,source,dest\nzero,a,1,3\n",
                                  "time,id,source,dest\n0,a,1\n", "0,a,1,3\n"])
def test_bad_input_rejected(tmp_path, text):
    with pytest.raises(ValueError):
        load_requests(write(tmp_path, text))


def test_cli_writes_one_position_row_per_tick_from_zero(tmp_path, capsys):
    main([str(write(tmp_path, SPEC)), "--floors", "60", "--cars", "2", "--out", str(tmp_path / "out")])
    rows = list(csv.reader(open(tmp_path / "out" / "positions.csv")))
    assert rows[0] == ["time", "car_0", "car_1"]
    assert [int(r[0]) for r in rows[1:]] == list(range(len(rows) - 1))
    assert "wait" in capsys.readouterr().out


def test_cli_reports_bad_input_without_a_traceback(tmp_path, capsys):
    with pytest.raises(SystemExit) as exit_:
        main([str(write(tmp_path, "time,id,source,dest\n0,a,1,99\n")), "--floors", "60"])
    assert exit_.value.code == 2
    assert "floor outside" in capsys.readouterr().err
