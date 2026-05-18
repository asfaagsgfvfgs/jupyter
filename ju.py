# jupyterlab_ngrok.py
# Runs JupyterLab and exposes it via an ngrok HTTPS URL.
# REQUIREMENT: Set env var NGROK_AUTHTOKEN in your cloud platform's Secrets/Env settings.

import os
import sys
import subprocess
import time
import json
import platform
import zipfile
import urllib.request
import stat
import re

PORT = int(os.environ.get("PORT", "8888"))
NGROK_AUTHTOKEN = "3DulmdV0HaKMzfui8UenLjMyndG_2U451LoLF2TtHQG2Xydb9"  # do NOT hardcode

def pip_install(*pkgs: str):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", *pkgs])

def download_ngrok(dest_dir=".") -> str:
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == "linux":
        arch = "amd64" if machine in ("x86_64", "amd64") else "arm64" if ("aarch64" in machine or "arm64" in machine) else None
        if not arch:
            raise RuntimeError(f"Unsupported Linux arch: {machine}")
        url = f"https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-{arch}.zip"
        exe = "ngrok"
    elif system == "darwin":
        arch = "amd64" if machine in ("x86_64", "amd64") else "arm64"
        url = f"https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-darwin-{arch}.zip"
        exe = "ngrok"
    elif system == "windows":
        url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
        exe = "ngrok.exe"
    else:
        raise RuntimeError(f"Unsupported OS: {system}")

    ngrok_path = os.path.join(dest_dir, exe)
    if os.path.exists(ngrok_path):
        return ngrok_path

    zip_path = os.path.join(dest_dir, "ngrok.zip")
    print("Downloading ngrok...")
    urllib.request.urlretrieve(url, zip_path)

    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(dest_dir)
    os.remove(zip_path)

    if system != "windows":
        os.chmod(ngrok_path, os.stat(ngrok_path).st_mode | stat.S_IEXEC)

    return ngrok_path

def start_jupyterlab() -> subprocess.Popen:
    cmd = [
        sys.executable, "-m", "jupyter", "lab",
        "--ip=0.0.0.0",
        f"--port={PORT}",
        "--no-browser",
        "--ServerApp.allow_remote_access=True",
        # Keep token auth ON (default). Do not disable it.
    ]
    print("Starting JupyterLab...")
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

def wait_for_jupyter_token_url(proc: subprocess.Popen, timeout_sec: int = 60) -> str:
    deadline = time.time() + timeout_sec
    token_url = None

    while time.time() < deadline:
        line = proc.stdout.readline()
        if not line:
            if proc.poll() is not None:
                raise RuntimeError("JupyterLab exited before producing a token URL.")
            time.sleep(0.05)
            continue

        print(line, end="")
        m = re.search(r"(http://127\.0\.0\.1:\d+/\?token=\w+)", line)
        if m:
            token_url = m.group(1)
            break

    if not token_url:
        raise RuntimeError("Timed out waiting for Jupyter token URL in logs.")
    return token_url

def ngrok_configure(ngrok_path: str):
    if not NGROK_AUTHTOKEN:
        raise RuntimeError("Missing NGROK_AUTHTOKEN env var. Set it in your platform Secrets/Env settings.")
    subprocess.check_call([ngrok_path, "config", "add-authtoken", NGROK_AUTHTOKEN])

def start_ngrok(ngrok_path: str) -> subprocess.Popen:
    print(f"Starting ngrok tunnel to port {PORT}...")
    return subprocess.Popen(
        [ngrok_path, "http", str(PORT)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )

def get_ngrok_https_url(timeout_sec: int = 20) -> str:
    # ngrok local API endpoint
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        try:
            with urllib.request.urlopen("http://127.0.0.1:4040/api/tunnels", timeout=2) as r:
                data = json.loads(r.read().decode("utf-8"))
            for t in data.get("tunnels", []):
                u = t.get("public_url", "")
                if u.startswith("https://"):
                    return u
        except Exception:
            time.sleep(0.2)
    raise RuntimeError("Could not fetch ngrok public URL from local API (http://127.0.0.1:4040).")

def main():
    # Install dependencies (quiet)
    pip_install("jupyterlab")

    ngrok_path = download_ngrok(".")
    ngrok_configure(ngrok_path)

    jupyter_proc = start_jupyterlab()
    token_url = wait_for_jupyter_token_url(jupyter_proc)

    ngrok_proc = start_ngrok(ngrok_path)
    public_https = get_ngrok_https_url()

    token = token_url.split("token=")[-1]
    print("\n==== JUPYTERLAB PUBLIC LINK ====")
    print(f"{public_https}/?token={token}")
    print("================================\n")
    print("Leave this script running to keep JupyterLab + ngrok alive.")

    try:
        while True:
            time.sleep(1)
            if jupyter_proc.poll() is not None:
                raise RuntimeError("JupyterLab stopped.")
            if ngrok_proc.poll() is not None:
                raise RuntimeError("ngrok stopped.")
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
