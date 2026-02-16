from .. import deploy
import yaml
import os
from pprint import pprint


def test_applies_to_host():
    assert deploy.applies_to_host({"hosts": ["localhost"]})
    assert not deploy.applies_to_host({"hosts": ["other"]})


def test_source_exists():
    assert deploy.source_exists({"source": "src/myscript"})
    assert not deploy.source_exists({"source": "src/nope"})


def test_target_exists():
    assert deploy.target_exists({"target": "dest/myscript"})
    assert not deploy.target_exists({"target": "dest/nope"})


def test_resolve_item_paths():
    items = yaml.safe_load("""
        - hosts: [localhost]
          source: src/myscript
          target: dest/myscript
        - hosts: [localhost]
          source: src/missing
          target: dest/missing
        - hosts: [localhost, iknowthis]
          source: src/scripts/
          target: dest/local/bin
          owner: rwxrob
          group: everyone
          options:
            - recurse
    """)
    base = os.getcwd()
    items = deploy.resolve_item_paths(items, base)
    for i in range(0, 3):
        assert items[i]["source"].is_relative_to(base)
        assert items[i]["target"].is_relative_to(base)


def test_parse():
    items = deploy.parse()
    assert items[1]["hosts"][0] == "localhost"


def test_gitdiff():
    res = deploy.gitdiff("src/myscript", "dest/myscript")
    assert res.returncode == 0
    res = deploy.gitdiff("src/missing", "dest/missing")
    assert res.returncode == 1


def test_check():
    deploy.check(deploy.parse())


def test_preview():
    deploy.preview()
