import sys
import yaml
import socket
import pathlib
import subprocess

hostname = socket.gethostname()
exe = pathlib.Path(sys.argv[0]).resolve()
base = exe.parent


def applies_to_host(item):
    for host in item["hosts"]:
        if host == "localhost" or host == hostname:
            return True
    return False


def source_exists(item):
    return pathlib.Path(item["source"]).exists()


def parse_filemap(path="filemap.yaml"):
    try:
        with open(path, "r") as f:
            items = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"{path} not found", file=sys.stderr)
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Invalid YAML: {e}", file=sys.stderr)
        sys.exit(1)
    return items


def preview_changes(items):
    for item in items:
        print(f"source: {item['source']}")
        if not applies_to_host(item):
            continue
        if not source_exists(item):
            continue


# TODO
def deploy_changes(items):
    print("would do the deployed changes")


def gitdiff(a, b):
    return subprocess.run(
        ["git", "-c", "core.fileMode=false", "diff", "--color", "--no-index", a, b],
        text=True,
        capture_output=True,
    )
