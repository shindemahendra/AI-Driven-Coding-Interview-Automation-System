import subprocess
import socket
import os
import sys
import time


def _get_free_port():
    s = socket.socket()
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def start_l4_server():
    port = _get_free_port()

    env = os.environ.copy()
    env["L4_PORT"] = str(port)

    proc = subprocess.Popen(
        [
            sys.executable,
            "coding_round_l4/exam_server.py"
        ],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    # small wait to ensure Flask boots
    time.sleep(1)

    return {
        "process": proc,
        "url": f"http://localhost:{port}",
        "port": port
    }


def stop_l4_server(proc):
    if proc and proc.poll() is None:
        proc.terminate()
