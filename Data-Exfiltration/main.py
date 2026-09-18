#!/usr/bin/env python3
"""HRSploit Data Exfiltration Scanner"""
import sys,requests,json,time,re
from pathlib import Path
from datetime import datetime
requests.packages.urllib3.disable_warnings()
def log(t,m,c="\033[91m"): print(f"{c}[{datetime.now().strftime('%H:%M:%S')}][{t}]\033[0m {m}",flush=True); time.sleep(0.05)
PATHS=["/.env","/.git/config","/.git/HEAD","/config.php","/wp-config.php","/.htaccess","/.htpasswd",
       "/phpinfo.php","/debug","/api/keys","/api/v1/users","/graphql","/swagger.json","/openapi.json",
       "/robots.txt","/.DS_Store","/backup.zip","/database.sql","/server-status","/admin/export"]
SENSITIVE=["password","passwd","secret","api_key","token","database","credentials","private","mysql","db_"]
def scan(target):
    sess=requests.Session(); sess.verify=False
    sess.headers["User-Agent"]="Mozilla/5.0 (Windows NT 10.0)"
    findings=[]; base=target.rstrip("/"); log("EXFIL",f"Baslaniyor: {target}")
    for i,path in enumerate(PATHS,1):
        pct=int((i/len(PATHS))*40); bar="#"*pct+"-"*(40-pct)
        print(f"\r  [{bar}] {i}/{len(PATHS)} {path:<30}",end="",flush=True)
        try:
            r=sess.get(base+path,timeout=6,allow_redirects=False)
            if r.status_code==200:
                sens=any(s in r.text.lower() for s in SENSITIVE)
                print(); log("EXFIL",f"{'HASSAS: '+path if sens else 'Erisim: '+path}  [{r.status_code}]","\033[91m" if sens else "\033[93m")
                findings.append({"path":path,"status":r.status_code,"sensitive":sens})
        except: pass
    print()
    out=Path("reports"); out.mkdir(exist_ok=True)
    (out/f"exfil_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json").write_text(json.dumps({"target":target,"findings":findings},indent=2))
    log("EXFIL",f"Tamamlandi: {len(findings)} bulgu","\033[92m"); return findings
if __name__ == "__main__":
    target=sys.argv[1] if len(sys.argv)>1 else input("Hedef URL: ").strip()
    scan(target)
