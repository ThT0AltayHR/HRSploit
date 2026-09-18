#!/usr/bin/env python3
"""
HRSploit — WAF Detection Engine
Gerçek HTTP isteğiyle WAF/güvenlik duvarı tespit eder.
"""
import sys, requests, re, time, socket, ssl
from datetime import datetime

requests.packages.urllib3.disable_warnings()

WAF_SIGNATURES = {
    "Cloudflare":    ["cloudflare","cf-ray","__cfduid","cf-cache-status","cf-request-id"],
    "Akamai":        ["akamai","x-akamai","x-check-cacheable","x-serial"],
    "AWS WAF":       ["awselb","x-amzn-requestid","x-amz-cf-id","aws-cf-id"],
    "Imperva":       ["incapsula","visid_incap","incap_ses","x-iinfo","x-cdn=imperva"],
    "F5 BIG-IP":     ["bigip","ts01","ts0","x-wa-info","f5-lb"],
    "ModSecurity":   ["mod_security","modsecurity","406 not acceptable","naxsi"],
    "Sucuri":        ["sucuri","x-sucuri-id","x-sucuri-cache","x-sucuri-block"],
    "Barracuda":     ["barracuda","barra_counter_session","bwi-"],
    "Fortiweb":      ["fortigate","fortiweb","fgd_icon","x-fw-"],
    "Wordfence":     ["wordfence","wf-cf-"],
    "SiteLock":      ["sitelock","x-sitelock"],
    "Reblaze":       ["reblaze","rbzid","x-reblaze"],
    "DenyAll":       ["denyall","sessioncookie"],
    "Generic WAF":   ["waf","firewall","blocked by","security","access denied"],
}

PROBE_PAYLOADS = [
    "' OR '1'='1",
    "<script>alert(1)</script>",
    "../../../../etc/passwd",
    "1 AND 1=1",
    "UNION SELECT NULL--",
]

def detect_waf(target: str) -> dict:
    result = {
        "target":    target,
        "timestamp": datetime.now().isoformat(),
        "detected":  "None",
        "confidence": 0,
        "evidence":  [],
        "bypass_strategy": {}
    }

    session = requests.Session()
    session.headers["User-Agent"] = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/124 Safari/537.36")
    session.verify = False

    # 1. Baseline isteği
    print(f"[WAF-ENGINE] Hedef analiz ediliyor: {target}")
    try:
        baseline = session.get(target, timeout=10)
        all_headers = {k.lower(): v.lower() for k, v in baseline.headers.items()}
        header_str  = " ".join(f"{k}:{v}" for k, v in all_headers.items())
        body_lower  = baseline.text.lower()

        print(f"[WAF-ENGINE] HTTP {baseline.status_code} | {len(baseline.text):,} byte")
        print(f"[WAF-ENGINE] Başlık taraması yapılıyor...")

        for waf_name, sigs in WAF_SIGNATURES.items():
            for sig in sigs:
                if sig in header_str or sig in body_lower:
                    result["detected"]   = waf_name
                    result["confidence"] = 85
                    result["evidence"].append(f"header/body match: {sig}")
                    print(f"[WAF-ENGINE] Tespit edildi (header): {waf_name} — imza: {sig}")
                    return result

    except Exception as e:
        print(f"[WAF-ENGINE] Baseline hatası: {e}")

    # 2. Probe payload'ları
    print("[WAF-ENGINE] Probe payload'ları gönderiliyor...")
    for payload in PROBE_PAYLOADS:
        try:
            r = session.get(target, params={"id": payload, "q": payload}, timeout=8)
            combined = (r.text + " ".join(f"{k}:{v}" for k,v in r.headers.items())).lower()

            for waf_name, sigs in WAF_SIGNATURES.items():
                for sig in sigs:
                    if sig in combined:
                        result["detected"]   = waf_name
                        result["confidence"] = 75
                        result["evidence"].append(f"probe response: {sig}")
                        print(f"[WAF-ENGINE] Tespit edildi (probe): {waf_name}")
                        return result

            if r.status_code in (403, 406, 429, 503):
                result["detected"]   = "Generic WAF"
                result["confidence"] = 60
                result["evidence"].append(f"HTTP {r.status_code} on payload")
                print(f"[WAF-ENGINE] WAF varlığı: HTTP {r.status_code} (Generic WAF)")
                break

        except Exception:
            pass
        time.sleep(0.3)

    if result["detected"] == "None":
        print("[WAF-ENGINE] Aktif WAF tespit edilmedi")
    else:
        print(f"[WAF-ENGINE] *** {result['detected']} *** güvenlik duvarı tespit edildi!")
        print(f"[WAF-ENGINE] Güven: %{result['confidence']}  Kanıt: {result['evidence']}")

    return result

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "http://testphp.vulnweb.com"
    detect_waf(target)
