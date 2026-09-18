#!/usr/bin/env python3
"""HRSploit SQLi Injector Engine."""
import sys
from pathlib import Path
BASE = Path(__file__).parent

def run(target=None, dump=False):
    script = BASE / "hrsploit_sqli.py"
    if script.exists():
        import subprocess
        cmd = [sys.executable, str(script), "-u", target or "http://test.com", "--batch"]
        if dump: cmd += ["--dump"]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in proc.stdout:
            if line.strip(): print(f"  [SQLI] {line.strip()}")
        proc.wait(timeout=180)
    return {"status":"completed"}

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else input("URL: ").strip()
    run(target)
