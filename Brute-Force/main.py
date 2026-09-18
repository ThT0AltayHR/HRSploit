#!/usr/bin/env python3
"""HRSploit Brute-Force Engine."""
import sys
from pathlib import Path
BASE = Path(__file__).parent

def run(target=None, wordlist=None):
    script = BASE / "crackadmin.py"
    if script.exists():
        import subprocess
        cmd = [sys.executable, str(script), "--url", target or "http://test.com", "--batch"]
        if wordlist: cmd += ["--wordlist", wordlist]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in proc.stdout:
            if line.strip(): print(f"  [BRUTE] {line.strip()}")
        proc.wait(timeout=180)
    return {"status":"completed"}

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else input("URL: ").strip()
    run(target)
