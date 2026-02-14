
import sys
import yaml
import socket
import pathlib

hostname = socket.gethostname()
exe = pathlib.Path(sys.argv[0]).resolve()
base = exe.parent

def applies_to_host(item):
    print("made")
    for host in item["hosts"]:
        if host == "localhost" or host == hostname:
            return True
    return False

def source_exists(item):
    return pathlib.Path(item["source"]).exists()
