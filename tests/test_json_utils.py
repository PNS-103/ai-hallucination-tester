from pathlib import Path
from utils.json_utils import save_json, load_json, parse_json_object


def test_json_round_trip(tmp_path):
    path = tmp_path / "x.json"
    save_json(path, {"a": 1})
    assert load_json(path) == {"a": 1}


def test_fenced_json():
    assert parse_json_object("```json\n{\"a\": 1}\n```") == {"a": 1}
