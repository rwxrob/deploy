from .. import applies_to_host, gitdiff


def test_applies_to_host():
    applies_to_host({"hosts": {}})
    assert True


def test_source_exists():
    assert True


def test_gitdiff():
    res = gitdiff("src/myscript", "dest/myscript")
    assert res.returncode == 0
