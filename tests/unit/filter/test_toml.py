# Copyright: (c) 2018, Matt Martz <matt@sivel.net>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest
from ansible.errors import AnsibleFilterError

from ansible_collections.sivel.toiletwater.plugins.filter import toml

SIMPLE_TOML = 'name = "Alice"\nage = 42\nactive = true\n'
SIMPLE_DICT = {"name": "Alice", "age": 42, "active": True}

COMPLEX_DICT = {
    "title": "TOML Example",
    "database": {
        "enabled": True,
        "ports": [8000, 8001, 8002],
        "temp_targets": {"cpu": 90.0, "case": 82.0},
    },
    "servers": {
        "alpha": {"ip": "10.0.0.1"},
        "beta": {"ip": "10.0.0.2"},
    },
}


@pytest.mark.parametrize("data", [
    SIMPLE_DICT,
    COMPLEX_DICT,
])
def test_roundtrip(data):
    assert toml.from_toml(toml.to_toml(data)) == data


def test_from_toml_valid():
    assert toml.from_toml(SIMPLE_TOML) == SIMPLE_DICT


def test_to_toml_output_contains_keys():
    out = toml.to_toml(COMPLEX_DICT)
    assert 'title = "TOML Example"' in out
    assert 'cpu = 90.0' in out
    assert 'case = 82.0' in out


def test_from_toml_invalid_syntax():
    with pytest.raises(AnsibleFilterError, match="Failed to parse TOML"):
        toml.from_toml("invalid =/ [1, 2 ]")  # trailing slash after equal is not allowed


def test_wrong_input_types():
    with pytest.raises(AnsibleFilterError, match="expects a string"):
        toml.from_toml(123)

    with pytest.raises(AnsibleFilterError, match="expects a dict-like"):
        toml.to_toml("not a dict")
