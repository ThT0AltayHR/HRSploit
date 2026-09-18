#!/usr/bin/env python3
"""HRSploit Port Scanner"""
import sys,socket,concurrent.futures,json,time,re
from pathlib import Path
from datetime import datetime

def log(t,m): print(f"[{datetime.now().strftime('%H:%M:%S')}][{t}] {m}",flush=True)
PORTS={21:"FTP",22:"SSH",23:"Telnet",25:"SMTP",53:"DNS",80:"HTTP",110:"POP3",
       143:"IMAP",443:"HTTPS",445:"SMB",3306:"MySQL",5432:"PostgreSQL",
       6379:"Redis",8080:"HTTP-Alt",8443:"HTTPS-Alt",27017:"MongoDB",
       3389:"RDP",9200:"Elasticsearch",1433:"MSSQL",5900:"VNC"}

def scan(host,timeout=1.5,threads=30):
    host=re.sub(r"https?://","",host).split("/")[0].split(":")[0]
    try: ip=socket.gethostbyname(host); log("SCAN",f"IP: {host} -> {ip}")
    except Exception as e: log("SCAN",f"DNS hata: {e}"); return {}
    def chk(p):
        try:
            s=socket.socket(); s.settimeout(timeout); r=s.connect_ex((ip,p)); s.close(); return p,r==0
        except: return p,False
    open_ports={}; done=0; total=len(PORTS)
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as ex:
        for p,ok in ex.map(chk,list(PORTS.keys())):
            done+=1; pct=int((done/total)*40); bar="#"*pct+"-"*(40-pct)
            print(f"\r  [{bar}] {done}/{total}",end="",flush=True)
            if ok:
                open_ports[p]=PORTS[p]; print()
                log("SCAN",f"  ACIK: {p}/{PORTS[p]}")
    print()
    result={"host":host,"ip":ip,"open_ports":open_ports}
    out=Path("reports"); out.mkdir(exist_ok=True)
    (out/f"portscan_{host}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json").write_text(json.dumps(result,indent=2))
    log("SCAN",f"Toplam: {len(open_ports)} acik port"); return result

if __name__ == "__main__":
    host=sys.argv[1] if len(sys.argv)>1 else input("Host/IP: ").strip()
    scan(host)
