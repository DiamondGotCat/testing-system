import json
import subprocess
import sys
import os
import platform
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple

BASE_DIR = Path(__file__).resolve().parent
TESTS_DIR = BASE_DIR / "tests"
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

def epoch_64() -> int:
    return time.time_ns()

def get_os_arch() -> Tuple[str, str]:
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system.startswith("darwin"):
        osname = "macos"
    elif system.startswith("windows"):
        osname = "windows"
    elif system.startswith("linux"):
        osname = "linux"
    else:
        osname = system

    if machine in ("x86_64", "amd64"):
        arch = "amd64"
    elif machine in ("arm64", "aarch64"):
        arch = "arm64"
    else:
        arch = machine

    return osname, arch

def run_test(test_name: str) -> Tuple[int, Path]:
    test_file = TESTS_DIR / f"{test_name}.py"
    ts_ns = epoch_64()
    osname, arch = get_os_arch()
    log_path = LOGS_DIR / f"{ts_ns}_{test_name}_{osname}-{arch}.log"

    started_at = datetime.now(timezone.utc)
    env_info = {
        "python_executable": sys.executable,
        "python_version": sys.version.replace("\n", " "),
        "platform": platform.platform(),
        "cwd": str(BASE_DIR),
        "tests_dir": str(TESTS_DIR),
        "os": osname,
        "arch": arch,
    }
    cmd = [sys.executable, str(test_file)]

    with open(log_path, "w", encoding="utf-8") as log:
        def w(line=""):
            log.write(line + "\n")

        w("==== TEST RUN LOG ====")
        w(f"Test Name      : {test_name}")
        w(f"Test File      : {test_file}")
        w(f"Command        : {' '.join(cmd)}")
        w(f"Start (UTC)    : {started_at.isoformat()}")
        w(f"Epoch (ns)     : {ts_ns}")
        w("---- ENVIRONMENT ----")
        for k, v in env_info.items():
            w(f"{k:17}: {v}")
        w("----------------------")
        log.flush()

        if not test_file.exists():
            w("!! ERROR: Test file not found. Skipping execution.")
            finished_at = datetime.now(timezone.utc)
            w(f"End   (UTC)    : {finished_at.isoformat()}")
            w(f"Duration (s)   : {(finished_at - started_at).total_seconds():.6f}")
            w(f"Return Code    : 127")
            return 127, log_path

        try:
            proc = subprocess.run(
                cmd,
                cwd=str(BASE_DIR),
                capture_output=True,
                text=True,
                check=False,
                encoding="utf-8",
                errors="replace",
            )
            finished_at = datetime.now(timezone.utc)

            w("---- STDOUT ----")
            w(proc.stdout.rstrip("\n"))
            w("---- STDERR ----")
            w(proc.stderr.rstrip("\n"))
            w("-----------------")
            w(f"End   (UTC)    : {finished_at.isoformat()}")
            w(f"Duration (s)   : {(finished_at - started_at).total_seconds():.6f}")
            w(f"Return Code    : {proc.returncode}")
            w("======================")
            return proc.returncode, log_path

        except Exception as e:
            finished_at = datetime.now(timezone.utc)
            w("!! EXCEPTION while running subprocess")
            w(repr(e))
            w(f"End   (UTC)    : {finished_at.isoformat()}")
            w(f"Duration (s)   : {(finished_at - started_at).total_seconds():.6f}")
            w(f"Return Code    : 128")
            w("======================")
            return 128, log_path

def main():
    cfg_path = BASE_DIR / "config.json"
    with open(cfg_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    tests = config.get("tests", [])
    if not isinstance(tests, list):
        raise ValueError("'tests' in file 'config.json' must be an array.")

    summary = []
    print(f"Found {len(tests)} test(s).")
    for name in tests:
        print(f"+ Running: {name} ...")
        rc, log_path = run_test(name)
        status = "OK" if rc == 0 else f"FAIL({rc})"
        print(f"> {name}: {status} | log: {log_path.name}")
        summary.append((name, rc, log_path))

    failed = [s for s in summary if s[1] != 0]
    print("\n=== SUMMARY ===")
    for name, rc, log_path in summary:
        print(f"{name:30} rc={rc:>3}  log={log_path.name}")

if __name__ == "__main__":
    main()
