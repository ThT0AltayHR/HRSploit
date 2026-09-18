#!/usr/bin/env python3
"""HRSploit Network Analysis"""
import sys,socket,ssl,json,time,requests,re
from pathlib import Path
from datetime import datetime
requests.packages.urllib3.disable_warnings()
def log(t,m): print(f"[{datetime.now().strftime('%H:%M:%S')}][{t}] {m}",flush=True); time.sleep(0.05)
def analyze(target):
    host=re.sub(r"https?://","",target).split("/")[0].split(":")[0]
    result={"target":target,"host":host,"ts":datetime.now().isoformat()}
    try:
        ip=socket.gethostbyname(host); result["ip"]=ip; log("NET",f"IP: {ip}")
        try: result["rdns"]=socket.gethostbyaddr(ip)[0]; log("NET",f"rDNS: {result['rdns']}")
        except: pass
    except Exception as e: log("NET",f"DNS: {e}"); return result
    try:
        ctx=ssl.create_default_context()
        with socket.create_connection((host,443),timeout=5) as s:
            with ctx.wrap_socket(s,server_hostname=host) as ss:
                cert=ss.getpeercert(); result["ssl"]={"version":ss.version(),"expiry":cert.get("notAfter","")}
                log("NET",f"SSL: {ss.version()}")
    except: pass
    try:
        sess=requests.Session(); sess.verify=False
        r=sess.get(target,timeout=10,allow_redirects=True)
        result["http"]={"status":r.status_code,"time":r.elapsed.total_seconds(),"server":r.headers.get("Server","?")}
        log("NET",f"HTTP {r.status_code} | {r.elapsed.total_seconds():.2f}s")
        sec=["X-Frame-Options","Content-Security-Policy","Strict-Transport-Security"]
        miss=[h for h in sec if h not in r.headers]; result["missing_headers"]=miss
        if miss: log("NET",f"Eksik: {miss}")
    except Exception as e: log("NET",f"HTTP: {e}")
    out=Path("reports"); out.mkdir(exist_ok=True)
    (out/f"network_{host}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json").write_text(json.dumps(result,indent=2))
    log("NET",f"Rapor tamamlandi"); return result
if __name__ == "__main__":
    target=sys.argv[1] if len(sys.argv)>1 else input("Hedef URL: ").strip()
    analyze(target)
