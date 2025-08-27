import os
import sys
import stat
import zipfile
import requests
import platform
import subprocess
from pathlib import Path
from typing import Tuple

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

def _posix_make_executable(path: Path):
    try:
        mode = path.stat().st_mode
        path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    except Exception as e:
        raise RuntimeError(f"Failed to make executable: {path} ({e})")

def download_and_extract(stableTag: str, osname: str, arch: str) -> Path:
    script_dir = Path(__file__).resolve().parent
    tmp_dir = (script_dir / ".." / "tmp").resolve()
    tmp_dir.mkdir(parents=True, exist_ok=True)

    url = f"https://github.com/YPSH-DGC/YPSH/releases/download/{stableTag}/YPSH-{osname}-{arch}.zip"
    zip_path = tmp_dir / f"YPSH-{osname}-{arch}.zip"

    resp = requests.get(url, stream=True, timeout=60)
    resp.raise_for_status()
    with open(zip_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=1024 * 256):
            if chunk:
                f.write(chunk)

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(tmp_dir)

    if platform.system().lower().startswith("windows"):
        exec_name = f"YPSH-{osname}-{arch}.exe"
    else:
        exec_name = f"YPSH-{osname}-{arch}"

    exec_path = (tmp_dir / exec_name).resolve()

    if not exec_path.exists():
        candidates = list(tmp_dir.rglob(exec_name))
        if candidates:
            exec_path = candidates[0]
        else:
            raise FileNotFoundError(f"Executable not found after extraction: {exec_name}")

    if osname in ("macos", "linux"):
        _posix_make_executable(exec_path)

    return exec_path

def runWithStdin(path: Path, content: str, errorOnNonZero: bool = True) -> str:
    result = subprocess.run(
        [str(path)],
        input=content,
        capture_output=True,
        text=True,
        check=errorOnNonZero
    )
    return result.stdout

TestCase1 = """
print(ypsh.version)
"""

TestCase2 = """
import("stdmath")
for i in range(1,1000) {
    print(i)
}
"""

def main():
    osname, arch = get_os_arch()
    stableTag = requests.get("https://ypsh-dgc.github.io/YPSH/channels/stable.txt").text.strip()
    execFilePath = download_and_extract(stableTag, osname, arch)

    print("Test Case 1: print the 'ypsh.version'")
    print(runWithStdin(execFilePath, TestCase1))

    print("Test Case 2: 'for' Syntax")
    print(runWithStdin(execFilePath, TestCase2))

if __name__ == "__main__":
    main()
