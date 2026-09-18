#!/usr/bin/env python3
"""HRSploit — Cookie & Session Stealer/Analyzer"""
import sys, requests, re, json, time
from pathlib import Path
from datetime import datetime
requests.packages.urllib3.disable_warnings()

def log(t, m, c="\033[93m"): print(f"{c}[{datetime.now().strftime('%H:%M:%S')}][{t}]\033[0m {m}", flush=True); time.sleep(0.05)

def analyze(target: str) -> dict:
    sess = requests.Session(); sess.verify = False
    sess.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    findings = []; log("COOKIE", f"Hedef: {target}")
    try:
        r = sess.get(target, timeout=10, allow_redirects=True)
        log("COOKIE", f"HTTP {r.status_code} | {len(r.cookies)} cookie")
        for ck in r.cookies:
            issues = []
            if not ck.secure:      issues.append("Secure eksik")
            if not ck.has_nonstandard_attr("httponly"): issues.append("HttpOnly eksik")
            if len(ck.value) < 16: issues.append(f"Kisa ID ({len(ck.value)} char)")
            samesite = ck._rest.get("SameSite","") if hasattr(ck,"_rest") else ""
            if not samesite: issues.append("SameSite eksik")
            severity = "HIGH" if len(issues) >= 2 else ("MEDIUM" if issues else "LOW")
            status = "HASSAS" if issues else "GUVENLI"
            log("COOKIE", f"  {ck.name}: {status} | {' | '.join(issues) if issues else 'OK'}", "\033[91m" if issues else "\033[92m")
            findings.append({"name": ck.name, "value": ck.value[:20]+"...", "secure": ck.secure, "issues": issues, "severity": severity})
        # CSRF token var mi?
        body = r.text.lower()
        if not any(t in body for t in ["csrf","_token","csrftoken"]): 
            log("COOKIE", "CSRF token yok - CSRF saldirisi mumkun!", "\033[91m")
            findings.append({"type": "CSRF-Missing", "severity": "HIGH"})
    except Exception as e: log("COOKIE", f"Hata: {e}", "\033[91m")
    out = Path("reports"); out.mkdir(exist_ok=True)
    (out/f"cookie_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json").write_text(json.dumps({"target": target, "findings": findings}, indent=2))
    log("COOKIE", f"Toplam: {len(findings)} bulgu", "\033[92m")
    return {"target": target, "findings": findings}

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else input("Hedef URL: ").strip()
    analyze(target)
