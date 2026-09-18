#!/usr/bin/env python3
"""HRSploit WAF Detection Engine."""
import sys
from pathlib import Path
BASE = Path(__file__).parent
sys.path.insert(0, str(BASE.parent))

def run(target=None):
    engine = BASE / "WAF-Engine" / "main.py"
    if engine.exists():
        import subprocess
        proc = subprocess.Popen([sys.executable, str(engine), target or "http://test.com"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in proc.stdout:
            if line.strip(): print(f"  [WAF] {line.strip()}")
        proc.wait(timeout=60)
        return {"status": "completed"}
    # Iç motor
    try:
        import requests; requests.packages.urllib3.disable_warnings()
        r = requests.get(target or "http://test.com", timeout=8, verify=False)
        for kw in ["cloudflare","akamai","incapsula","f5","modsec"]:
            if kw in str(r.headers).lower() or kw in r.text.lower():
                print(f"  [WAF] Tespit: {kw.title()}")
                return {"status":"detected","waf":kw}
        print("  [WAF] WAF bulunamadi")
        return {"status":"clean"}
    except Exception as e:
        print(f"  [WAF] Hata: {e}")
        return {"status":"error","error":str(e)}

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else input("Hedef URL: ").strip()
    run(target)
