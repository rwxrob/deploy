import sys
import yaml
import socket
import pathlib
import subprocess

hostname = socket.gethostname()


def applies_to_host(item):
    for host in item["hosts"]:
        if host == "localhost" or host == hostname:
            return True
    return False


def source_exists(item):
    return pathlib.Path(item["source"]).exists()


def resolve_item_paths(items, base):
    base = pathlib.Path(base)

    for item in items:
        src = pathlib.Path(item["source"])
        tgt = pathlib.Path(item["target"])

        if not src.is_absolute():
            src = base / src

        if not tgt.is_absolute():
            tgt = base / tgt

        item["source"] = src
        item["target"] = tgt

    return items


def parse(filemap="filemap.yaml"):
    fullpath = pathlib.Path(filemap).resolve()
    base = fullpath.parent
    try:
        with open(fullpath, "r") as f:
            items = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"{filemap} not found", file=sys.stderr)
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Invalid YAML: {e}", file=sys.stderr)
        sys.exit(1)
    return resolve_item_paths(items, base)


def gitdiff_all(items):
    changes = []
    # TODO add exception handler
    for item in items:
        if not applies_to_host(item):
            continue
        if not source_exists(item):
            continue
        res = gitdiff(item["source"], item["target"])
        if res.returncode != 0:
            changes.append(res)
    return changes


def preview(filemap="filemap.yaml"):
    items = parse(filemap)
    changes = gitdiff_all(items)
    for change in changes:
        print(changes.stdout)


# TODO
def push(items):
    print("would do the deployed changes")


def gitdiff(a, b):
    return subprocess.run(
        ["git", "-c", "core.fileMode=false", "diff", "--color", "--no-index", a, b],
        text=True,
        capture_output=True,
    )
