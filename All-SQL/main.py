#!/usr/bin/env python3
"""HRSploit All-SQL Engine - SQLi Scanner ana girisi."""
import sys
from pathlib import Path
BASE = Path(__file__).parent
sys.path.insert(0, str(BASE.parent))

def run(target=None, dump=False, dbms=None):
    """Tum SQL injection tekniklerini calistir."""
    script = BASE / "sqli_scanner.py"
    if not script.exists():
        script = BASE.parent / "SQLi-Injector" / "hrsploit_sqli.py"
    if script.exists():
        import subprocess
        cmd = [sys.executable, str(script), "-u", target or "http://test.com", "--batch"]
        if dump: cmd += ["--dump"]
        if dbms: cmd += ["--dbms", dbms]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in proc.stdout:
            if line.strip(): print(f"  [ALL-SQL] {line.strip()}")
        proc.wait(timeout=180)
        return {"status": "completed", "returncode": proc.returncode}
    print("[ALL-SQL] SQLi scanner bulunamadi")
    return {"status": "not_found"}

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else input("Hedef URL: ").strip()
    run(target)
