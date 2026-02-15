from .. import deploy
import yaml
import os


def test_applies_to_host():
    deploy.applies_to_host({"hosts": {}})
    assert True


def test_source_exists_yes():
    assert deploy.source_exists({"source": "src/myscript"})


def test_source_exists_no():
    assert not deploy.source_exists({"source": "src/nope"})


def test_gitdiff_same():
    res = deploy.gitdiff("src/myscript", "dest/myscript")
    assert res.returncode == 0


def test_gitdiff_missing():
    res = deploy.gitdiff("src/missing", "dest/missing")
    assert res.returncode == 1


def test_resolve_item_paths():
    items = yaml.safe_load("""
        - hosts: [localhost]
          source: src/myscript
          target: dest/myscript
        - hosts: [localhost]
          source: src/missing
          target: dest/missing
    """)
    items = deploy.resolve_item_paths(items, os.getcwd())


def test_gitdiff_all_changes():
    items = yaml.safe_load("""
        - hosts: [localhost]
          source: src/myscript
          target: dest/myscript
        - hosts: [localhost]
          source: src/missing
          target: dest/missing
    """)
    changed = deploy.gitdiff_all(items)
    assert len(changed) == 1
