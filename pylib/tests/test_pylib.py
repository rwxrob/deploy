from .. import applies_to_host, gitdiff, source_exists, preview_changes
import yaml


def test_applies_to_host():
    applies_to_host({"hosts": {}})
    assert True


def test_source_exists_yes():
    assert source_exists({"source": "src/myscript"})


def test_source_exists_no():
    assert not source_exists({"source": "src/nope"})


def test_gitdiff_same():
    res = gitdiff("src/myscript", "dest/myscript")
    assert res.returncode == 0


def test_gitdiff_missing():
    res = gitdiff("src/missing", "dest/missing")
    assert res.returncode == 1


def test_preview_changes():
    items = yaml.safe_load("""
        - hosts: [localhost]
          source: src/myscript
          target: dest/myscript
        - hosts: [localhost]
          source: src/missing
          target: dest/missing
    """)
    changed = preview_changes(items)
    assert len(changed) == 1
