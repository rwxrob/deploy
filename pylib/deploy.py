import sys
import os
import yaml
import socket
import pathlib
import subprocess
import shutil

hostname = socket.gethostname()

RED = "\033[31m"
GREEN = "\033[32m"
RESET = "\033[0m"


def applies_to_host(item):
    for host in item["hosts"]:
        if host == "localhost" or host == hostname:
            return True
    return False


def source_exists(item):
    return pathlib.Path(item["source"]).exists()


def target_exists(item):
    return pathlib.Path(item["target"]).exists()


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


def gitdiff(a, b):
    return subprocess.run(
        ["git", "diff", "--color", "--no-index", b, a],
        text=True,
        capture_output=True,
    )


def check(items):
    for item in items:
        if not applies_to_host(item):
            item["status"] = f"ignored on {hostname}"
            continue
        if not source_exists(item):
            item["error"] = "source not found"
            continue
        if not target_exists(item):
            item["would"] = "create target"
            continue
        res = gitdiff(item["source"], item["target"])
        if res.returncode == 1:
            item["would"] = res.stdout
            continue
        elif res.returncode == 0:
            continue
        else:
            item["error"] = res.stderr
    return items


def preview(filemap="filemap.yaml"):
    items = check(parse(filemap))
    lines = []
    for item in items:
        would = item.get("would")
        error = item.get("error")
        if error is not None:
            lines.append(f"{RED}ERROR:  -------------------------------------{RESET}")
            lines.append(f"  source:  {item["source"]}")
            lines.append(f"  target:  {item["target"]}")
            lines.append(f"  message: {error}")
            continue
        if would is not None:
            lines.append(f"{GREEN}CHANGE: -------------------------------------{RESET}")
            lines.append(f"  source:  {item["source"]}")
            lines.append(f"  target:  {item["target"]}")
            if would.find("\n") >= 0:
                lines.append(f"  message:\n{would}")
            else:
                lines.append(f"  message: {would}")
    print_or_page("\n".join(lines))


def get_pager():
    return os.environ.get("PAGER") or shutil.which("less")


def print_or_page(text: str) -> None:
    if not sys.stdout.isatty():
        print(text)
        return
    rows = shutil.get_terminal_size(fallback=(80, 24)).lines
    line_count = text.count("\n") + 1
    if line_count >= rows:
        pager = get_pager()
        if pager:
            subprocess.run([pager], input=text, text=True)
            return
    print(text)


# TODO
def push(items):
    print("would do the deployed changes")
