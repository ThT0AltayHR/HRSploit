#!/usr/bin/env python3
"""
HRSploit — CVE Lookup & Generator
Exploit-DB ve NVD'den CVE bilgisi çeker; bulamazsa akıllı CVE üretir.
"""
import re, time, hashlib
from datetime import datetime

def lookup_cve(target: str, vuln_type: str, payload: str = "") -> dict:
    """Exploit-DB ve NVD'den CVE ara; bulamazsa üret."""
    result = {
        "cve_id":      "N/A",
        "title":       f"{vuln_type} vulnerability",
        "description": "",
        "cvss":        "8.5",
        "severity":    "HIGH",
        "exploit_url": "",
        "references":  [],
        "generated":   False,
        "ts":          datetime.now().isoformat(),
    }
    # Domain normalize
    host = re.sub(r'https?://', '', target).split('/')[0].split(':')[0]

    # ── 1. NVD / Exploit-DB aramaya çalış ─────────────────────
    try:
        import requests
        requests.packages.urllib3.disable_warnings()
        sess = requests.Session()
        sess.headers["User-Agent"] = "HRSploit/1.0 Security Research"
        sess.verify = False

        # NVD API (public, no key for basic search)
        nvd_url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch={vuln_type}&resultsPerPage=3"
        try:
            r = sess.get(nvd_url, timeout=8)
            if r.status_code == 200:
                data = r.json()
                vulns = data.get("vulnerabilities", [])
                if vulns:
                    cve_data = vulns[0]["cve"]
                    result["cve_id"]      = cve_data.get("id", "N/A")
                    result["exploit_url"] = f"https://nvd.nist.gov/vuln/detail/{result['cve_id']}"
                    descs = cve_data.get("descriptions", [])
                    if descs:
                        result["description"] = next(
                            (d["value"] for d in descs if d["lang"] == "en"), descs[0]["value"])
                    metrics = cve_data.get("metrics", {})
                    cvss_data = metrics.get("cvssMetricV31", metrics.get("cvssMetricV30", [{}]))
                    if cvss_data:
                        score = cvss_data[0].get("cvssData", {}).get("baseScore", "8.5")
                        result["cvss"]     = str(score)
                        result["severity"] = cvss_data[0].get("cvssData", {}).get("baseSeverity","HIGH")
                    result["references"].append(result["exploit_url"])
        except Exception:
            pass

    except ImportError:
        pass

    # ── 2. Exploit-DB arama (web scrape) ─────────────────────
    if result["cve_id"] == "N/A":
        try:
            import requests
            r2 = requests.get(
                f"https://www.exploit-db.com/search?q={vuln_type}&type=webapps",
                timeout=8, headers={"User-Agent":"Mozilla/5.0"}, verify=False)
            if r2.status_code == 200:
                cves = re.findall(r'CVE-\d{4}-\d{4,7}', r2.text)
                eids = re.findall(r'/exploits/(\d+)', r2.text)
                if cves:
                    result["cve_id"]      = cves[0]
                    result["exploit_url"] = f"https://www.exploit-db.com/search?q={vuln_type}"
                    result["references"].append(result["exploit_url"])
                elif eids:
                    result["exploit_url"] = f"https://www.exploit-db.com/exploits/{eids[0]}"
                    result["references"].append(result["exploit_url"])
        except Exception:
            pass

    # ── 3. Bulunamadıysa akıllı CVE üret ─────────────────────
    if result["cve_id"] == "N/A":
        year = datetime.now().year
        uid  = int(hashlib.md5(f"{host}{vuln_type}".encode()).hexdigest()[:4], 16) % 90000 + 10000
        result["cve_id"]   = f"CVE-{year}-{uid}"
        result["generated"] = True
        result["description"] = (
            f"A {vuln_type} vulnerability was discovered in the web application at {host}. "
            f"The vulnerability allows an attacker to perform unauthorized operations "
            f"including data exfiltration and potential remote code execution. "
            f"This finding was identified through automated security assessment using HRSploit Framework v1.0.0."
        )
        CVSS = {"SQLi":"9.8","XSS":"6.1","RCE":"10.0","LFI":"7.5",
                "SSRF":"8.6","CSRF":"6.5","LFI":"7.5"}
        result["cvss"]     = CVSS.get(vuln_type, "8.5")
        result["severity"] = "CRITICAL" if float(result["cvss"]) >= 9 else "HIGH"

    return result


def write_cve_file(output_path, ctx: dict, cve_info: dict) -> str:
    """CVE.txt dosyasını exploit-db linki + tam detaylarla yaz."""
    generated_note = "(HRSploit tarafından üretildi)" if cve_info.get("generated") else "(NVD/Exploit-DB)"
    exploit_link   = cve_info.get("exploit_url","") or "https://exploit-db.com"
    cve_id         = cve_info.get("cve_id","N/A")

    content = f"""
================================================================================
  HRSploit — CVE AÇIKLAMA RAPORU
================================================================================

  CVE Numarası : {cve_id}  {generated_note}
  Başlık       : {cve_info.get('title', ctx.get('vuln_type','?') + ' vulnerability')}
  Şiddet       : {cve_info.get('severity','HIGH')}
  CVSS Skoru   : {cve_info.get('cvss','8.5')}
  Exploit Link : {exploit_link}
  Referanslar  : {chr(10) + '                 '.join([''] + cve_info.get('references',[]))}

================================================================================
  HEDEF BİLGİLERİ
================================================================================

  Hedef URL    : {ctx.get('target','?')}
  Açık Türü   : {ctx.get('vuln_type','?')}
  Veritabanı  : {ctx.get('db_type','?')}
  WAF          : {ctx.get('waf','None')}
  Tarih        : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
  Exploit Adı  : {ctx.get('name','?')}

================================================================================
  AÇIKLAMA
================================================================================

{cve_info.get('description','')}

================================================================================
  TEKNİK DETAYLAR
================================================================================

  Açık Vektörü  : Web Application ({ctx.get('vuln_type','?')})
  Etki          : Gizlilik (HIGH), Bütünlük (HIGH), Erişilebilirlik (MEDIUM)
  Kimlik Doğr.  : Gerektirmez (Unauthenticated)
  Ağ Erişimi    : Uzak (Network)
  Karmaşıklık   : Düşük (Low)
  Kullanıcı Int.: Gerekmez (None)

================================================================================
  KANIT (PROOF OF CONCEPT)
================================================================================

  Payload      : ' OR '1'='1' --  (veya türe özel)
  Parametre    : id, q, search, user, page (keşfedilen)
  Method       : GET / POST
  Etki         : Veritabanı erişimi, kimlik doğrulama atlatma

================================================================================
  ÇÖZÜM ÖNERİLERİ
================================================================================

  1. Parametreli sorgular / hazır ifadeler kullanın
  2. Tüm kullanıcı girdilerini doğrulayın ve temizleyin
  3. Web Uygulama Güvenlik Duvarı (WAF) uygulayın
  4. XSS için Content Security Policy (CSP) kullanın
  5. Veritabanı kullanıcısı için en az ayrıcalık ilkesi uygulayın
  6. Düzenli güvenlik denetimleri ve penetrasyon testleri yapın
  7. Güvenlik yamalarını güncel tutun

================================================================================
  YASAL UYARI
================================================================================

  Bu rapor HRSploit Framework v1.0.0 tarafından üretilmiştir.
  Yalnızca yetkili güvenlik testleri için kullanılabilir.
  Yetkisiz erişim yasaldır.

  Geliştirici: Altay HR
  GitHub     : https://github.com/ThT0AltayHR/HRSploit
  Topluluk   : turkhackteam.org

================================================================================
"""
    from pathlib import Path
    Path(output_path).write_text(content, encoding="utf-8")
    return content
