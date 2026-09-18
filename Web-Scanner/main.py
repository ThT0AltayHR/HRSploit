#!/usr/bin/env python3
"""HRSploit Web Scanner Engine"""
import sys,requests,re,json,time
from pathlib import Path
from datetime import datetime
requests.packages.urllib3.disable_warnings()
def log(t,m,c="\033[96m"): print(f"{c}[{datetime.now().strftime('%H:%M:%S')}][{t}]\033[0m {m}",flush=True); time.sleep(0.05)
def scan(target):
    sess=requests.Session(); sess.verify=False
    sess.headers["User-Agent"]="Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36"
    findings=[]; log("WSCAN",f"Baslaniyor: {target}")
    try:
        r=sess.get(target,timeout=10,allow_redirects=True)
        log("WSCAN",f"HTTP {r.status_code} | {len(r.text):,} byte | {r.elapsed.total_seconds():.2f}s")
        body=r.text.lower(); hdr=r.headers
        for cms,sigs in {"WordPress":["wp-content","xmlrpc"],"Joomla":["com_content"],"Drupal":["drupal"],"Laravel":["laravel_session"]}.items():
            if any(s in body for s in sigs): log("WSCAN",f"CMS: {cms}","\033[93m"); findings.append({"type":"CMS","name":cms})
        for payload in ["'","' OR '1'='1","1 AND SLEEP(3)--"]:
            try:
                rp=sess.get(target,params={"id":payload},timeout=10)
                if any(e in rp.text.lower() for e in ["sql","mysql","syntax error","you have an error"]):
                    log("WSCAN",f"SQLi: {payload[:30]}","\033[91m"); findings.append({"type":"SQLi","payload":payload}); break
            except: pass
        for key in ["Server","X-Powered-By"]:
            if key in hdr: log("WSCAN",f"Info: {key}: {hdr[key]}","\033[93m"); findings.append({"type":"InfoLeak","header":key,"value":hdr[key]})
        for h in ["X-Frame-Options","Content-Security-Policy"]:
            if h not in hdr: findings.append({"type":"MissingHeader","header":h})
    except Exception as e: log("WSCAN",f"Hata: {e}","\033[91m")
    out=Path("reports"); out.mkdir(exist_ok=True)
    (out/f"web_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json").write_text(json.dumps({"target":target,"findings":findings},indent=2))
    log("WSCAN",f"Tamamlandi: {len(findings)} bulgu","\033[92m"); return findings
if __name__ == "__main__":
    target=sys.argv[1] if len(sys.argv)>1 else input("Hedef URL: ").strip()
    scan(target)
