#!/usr/bin/env python3
"""HRSploit Reconnaissance Engine"""
import sys,socket,re,json,time,requests,concurrent.futures
from pathlib import Path
from datetime import datetime
requests.packages.urllib3.disable_warnings()
def log(t,m): print(f"[{datetime.now().strftime('%H:%M:%S')}][{t}] {m}",flush=True); time.sleep(0.05)
def run(target):
    host=re.sub(r"https?://","",target).split("/")[0].split(":")[0]
    result={"target":target,"host":host,"ts":datetime.now().isoformat()}
    log("RECON",f"Hedef: {host}")
    try:
        ip=socket.gethostbyname(host); result["ip"]=ip; log("RECON",f"DNS: {host} -> {ip}")
        try: result["rdns"]=socket.gethostbyaddr(ip)[0]; log("RECON",f"rDNS: {result['rdns']}")
        except: pass
    except Exception as e: log("RECON",f"DNS: {e}")
    try:
        sess=requests.Session(); sess.verify=False
        r=sess.get(target,timeout=8,allow_redirects=True)
        result["http"]=r.status_code; result["server"]=r.headers.get("Server","?")
        result["powered"]=r.headers.get("X-Powered-By","?")
        log("RECON",f"HTTP {r.status_code} | Server:{result['server']}")
        body=r.text.lower()
        for cms,sigs in {"WordPress":["wp-content"],"Joomla":["com_content"],"Drupal":["drupal"]}.items():
            if any(s in body for s in sigs): result["cms"]=cms; log("RECON",f"CMS: {cms}"); break
    except Exception as e: log("RECON",f"HTTP: {e}")
    PORTS={22:"SSH",80:"HTTP",443:"HTTPS",3306:"MySQL",5432:"PgSQL",8080:"HTTP-Alt"}
    open_ports=[]; host_ip=result.get("ip",host)
    def chk(p):
        try: s=socket.socket(); s.settimeout(1.2); r=s.connect_ex((host_ip,p)); s.close(); return p,r==0
        except: return p,False
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as ex:
        for p,ok in ex.map(chk,list(PORTS.keys())):
            if ok: open_ports.append(p); log("RECON",f"Acik port: {p}/{PORTS[p]}")
    result["open_ports"]=open_ports
    out=Path("reports"); out.mkdir(exist_ok=True)
    (out/f"recon_{host}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json").write_text(json.dumps(result,indent=2))
    log("RECON",f"Tamamlandi"); return result
if __name__ == "__main__":
    target=sys.argv[1] if len(sys.argv)>1 else input("Hedef URL: ").strip()
    run(target)
