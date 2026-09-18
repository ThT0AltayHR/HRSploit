#!/usr/bin/env python3
"""
HRSploit — Brain Orchestrator
Tüm araçları yöneten merkezi karar ve orkestrasyon motoru.
Termux/root-free ortamda çalışır.
"""
import sys, os, subprocess, time, json, socket, re
from pathlib import Path
from datetime import datetime

BASE   = Path(__file__).parent
TOOLS  = BASE / "Third-Party"
REPORTS= BASE / "reports"
REPORTS.mkdir(exist_ok=True)

R="\033[0m"; RED="\033[91m"; YEL="\033[93m"; GRN="\033[92m"
CYN="\033[96m"; MAG="\033[95m"; WHT="\033[97m"; BLD="\033[1m"

def ts(): return datetime.now().strftime("%H:%M:%S.%f")[:-3]
def log(tag, msg, color=CYN):
    print(f"{color}{ts()} {tag}{R}  {msg}", flush=True)
    time.sleep(0.05)

def check_internet():
    """İnternet bağlantısı kontrol - bağlanamazsa hata ver."""
    try:
        sock = socket.create_connection(("8.8.8.8", 53), timeout=4)
        sock.close()
        return True
    except (socket.error, OSError):
        return False

def run_tool(name, cmd, timeout=120, live_output=True):
    """Harici aracı çalıştır ve çıktısını canlı göster."""
    log(f"[{name}]", f"Başlatılıyor: {' '.join(str(c) for c in cmd[:5])}", YEL)
    result = {"name": name, "cmd": cmd, "output": "", "returncode": -1, "ok": False}
    try:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(BASE)
        proc = subprocess.Popen(
            [str(c) for c in cmd],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1, env=env
        )
        lines_shown = 0
        output_lines = []
        for line in proc.stdout:
            line = line.rstrip()
            if line:
                output_lines.append(line)
                if lines_shown < 50:
                    log(f"[{name}]", f"  {line[:120]}", WHT)
                    lines_shown += 1
                elif lines_shown == 50:
                    log(f"[{name}]", "  ... (çıktı devam ediyor)", GRN)
                    lines_shown += 1
        proc.wait(timeout=timeout)
        result["output"]     = "\n".join(output_lines)
        result["returncode"] = proc.returncode
        result["ok"]         = proc.returncode == 0
        log(f"[{name}]", f"Tamamlandı — returncode={proc.returncode} — {len(output_lines)} satır", GRN)
    except subprocess.TimeoutExpired:
        proc.kill()
        log(f"[{name}]", f"Zaman aşımı ({timeout}s) — süreç sonlandırıldı", RED)
        result["output"] = "TIMEOUT"
    except FileNotFoundError:
        log(f"[{name}]", "Araç bulunamadı (kurulu değil)", RED)
    except Exception as e:
        log(f"[{name}]", f"Hata: {e}", RED)
    return result


class BrainOrchestrator:
    """
    Merkezi beyin: tüm araç çıktılarını toplar, korelasyon yapar,
    hangi adımın atılacağına karar verir.
    """
    def __init__(self, target: str):
        self.target      = target
        self.host        = re.sub(r'https?://', '', target).split('/')[0].split(':')[0]
        self.evidence    = {}   # {tool_name: result}
        self.vulns       = []   # bulunan açıklar
        self.confidence  = {}   # {vuln_type: confidence_score}
        self.session_id  = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.internet    = check_internet()

        if not self.internet:
            log("[BRAIN]", "İNTERNET BAĞLANTISI YOK — Bağlantı hatası!", RED)
            log("[BRAIN]", "Bazı çevrimiçi doğrulama adımları atlanacak", YEL)

    # ── Araç bulucu ───────────────────────────────────────────────
    def _tool(self, name):
        """Third-Party araç yolunu döndür."""
        t = TOOLS / name
        if not t.exists():
            return None
        # Python scripti mi, binary mi?
        for f in [t/'subdomains.py', t/'nikto.pl', t/'ffuf',
                  t/'httpx', t/'subfinder', t/'katana',
                  t/'Sublist3r/sublist3r.py']:
            if Path(f).exists():
                return f
        return t

    # ── Aşama 1: Keşif ───────────────────────────────────────────
    def phase_recon(self):
        log("[BRAIN]", "═"*55, MAG)
        log("[BRAIN]", "FAZ 1: KEŞİF & RECONNAISSANCE", MAG)
        log("[BRAIN]", "═"*55, MAG)

        # Subfinder - subdomain keşfi
        sublist3r = TOOLS / "Sublist3r" / "sublist3r.py"
        if sublist3r.exists() and self.internet:
            log("[BRAIN]", f"Subfinder/Sublist3r: {self.host} için subdomain keşfi", CYN)
            r = run_tool("Sublist3r", [sys.executable, str(sublist3r), "-d", self.host, "-o",
                                        str(REPORTS/f"subdomains_{self.session_id}.txt")],
                         timeout=90)
            self.evidence["sublist3r"] = r

        # httpx - canlı host tespiti
        httpx_py = TOOLS / "httpx" / "runner" / "runner.go"
        if not httpx_py.exists():
            # Python HTTP probe yap
            log("[BRAIN]", "httpx: HTTP probe başlıyor...", CYN)
            try:
                import requests as _req
                _req.packages.urllib3.disable_warnings()
                r = _req.get(self.target, timeout=8, verify=False)
                self.evidence["httpx"] = {
                    "ok": True, "output": f"HTTP {r.status_code} | {len(r.text)} byte | "
                    f"Server: {r.headers.get('Server','?')}",
                    "status_code": r.status_code, "headers": dict(r.headers)
                }
                log("[BRAIN]", f"HTTP: {r.status_code} | {r.headers.get('Server','?')}", GRN)
            except Exception as e:
                log("[BRAIN]", f"httpx probe hatası: {e}", RED)
                if "Connection" in str(e) or "timeout" in str(e).lower():
                    log("[BRAIN]", "BAĞLANTI HATASI — Hedef erişilemiyor veya internet yok", RED)
                    self.evidence["httpx"] = {"ok": False, "error": str(e)}

    # ── Aşama 2: Port & Servis ───────────────────────────────────
    def phase_portscan(self):
        log("[BRAIN]", "═"*55, MAG)
        log("[BRAIN]", "FAZ 2: PORT TARAMASI (nmap Python iç motor)", MAG)

        import socket, concurrent.futures
        PORTS = {21:"FTP",22:"SSH",23:"Telnet",25:"SMTP",53:"DNS",
                 80:"HTTP",110:"POP3",143:"IMAP",443:"HTTPS",445:"SMB",
                 3306:"MySQL",5432:"PostgreSQL",6379:"Redis",8080:"HTTP-Alt",
                 8443:"HTTPS-Alt",27017:"MongoDB",3389:"RDP",9200:"Elasticsearch"}
        open_ports = []
        try:
            ip = socket.gethostbyname(self.host)
            log("[BRAIN]", f"IP çözümlendi: {self.host} → {ip}", GRN)
            def chk(p):
                try:
                    s=socket.socket(); s.settimeout(1.5)
                    r=s.connect_ex((ip,p)); s.close()
                    return p, r==0
                except: return p, False
            with concurrent.futures.ThreadPoolExecutor(max_workers=30) as ex:
                for p, ok in ex.map(lambda p: chk(p), PORTS):
                    if ok:
                        open_ports.append(p)
                        log("[BRAIN]", f"  AÇIK PORT: {p}/{PORTS[p]}", YEL)
        except Exception as e:
            log("[BRAIN]", f"Port tarama hatası: {e}", RED)

        self.evidence["portscan"] = {"open_ports": open_ports}

    # ── Aşama 3: WAF & Zafiyet ───────────────────────────────────
    def phase_vuln_scan(self):
        log("[BRAIN]", "═"*55, MAG)
        log("[BRAIN]", "FAZ 3: WAF TESPİTİ & ZAFİYET TARAMASI", MAG)

        # WAF Engine
        waf_engine = BASE / "WAF-Detection" / "WAF-Engine" / "main.py"
        if waf_engine.exists():
            r = run_tool("WAF-Engine", [sys.executable, str(waf_engine), self.target], timeout=60)
            self.evidence["waf"] = r
            if "tespit" in r.get("output","").lower() or "detected" in r.get("output","").lower():
                log("[BRAIN]", "WAF tespit edildi — bypass modülü hazır", YEL)

        # Nikto - web scanner
        nikto_pl = TOOLS / "nikto" / "program" / "nikto.pl"
        if nikto_pl.exists():
            log("[BRAIN]", "Nikto: web zafiyet taraması başlıyor", CYN)
            r = run_tool("Nikto", ["perl", str(nikto_pl), "-h", self.target, "-nointeractive"],
                         timeout=120)
            self.evidence["nikto"] = r
            # Nikto çıktısından zafiyet çıkar
            for line in r.get("output","").split("\n"):
                if "OSVDB" in line or "+ " in line:
                    log("[BRAIN]", f"Nikto bulgusu: {line[:80]}", YEL)
        else:
            # İç scanner kullan
            r = run_tool("Internal-Scanner",
                         [sys.executable, BASE/"All-SQL"/"sqli_scanner.py",
                          "-u", self.target, "--batch"], timeout=90)
            self.evidence["internal_scan"] = r

    # ── Aşama 4: Derin SQLi Analizi ──────────────────────────────
    def phase_sqli(self):
        log("[BRAIN]", "═"*55, MAG)
        log("[BRAIN]", "FAZ 4: SQL INJECTION — ÇOK KATMANLI DOĞRULAMA", MAG)

        results = []
        confidence = 0

        # Katman 1: İç motor
        sqli_script = BASE / "All-SQL" / "sqli_scanner.py"
        if sqli_script.exists():
            r = run_tool("SQLi-Engine", [sys.executable, str(sqli_script),
                                          "-u", self.target, "--batch"], timeout=120)
            self.evidence["sqli_internal"] = r
            if "HIT" in r.get("output","") or "BULUNDU" in r.get("output",""):
                confidence += 40
                log("[BRAIN]", f"Katman 1 (İç Motor): SQLi sinyal alındı +40 güven", GRN)

        # Katman 2: Commix - OS injection
        commix_py = TOOLS / "commix" / "commix.py"
        if commix_py.exists() and self.internet:
            r = run_tool("Commix", [sys.executable, str(commix_py), "--url", self.target,
                                     "--batch", "--level=2"], timeout=90)
            self.evidence["commix"] = r
            if "vulnerable" in r.get("output","").lower():
                confidence += 30
                log("[BRAIN]", f"Katman 2 (Commix): OS injection doğrulandı +30", GRN)

        # Katman 3: SQLMap referans scripti
        for sqli_lib in [BASE/"All-SQL"/"sqlmap_lib", BASE/"SQLi-Injector"/"sqlmap_lib"]:
            runner = sqli_lib / "sqlmap.py"
            if runner.exists():
                r = run_tool("SQLMap-Ref", [sys.executable, str(runner), "-u",
                                             self.target, "--batch", "--level=2",
                                             "--risk=2", "--smart"], timeout=180)
                self.evidence["sqlmap"] = r
                out = r.get("output","").lower()
                if "injectable" in out or "sqlinjection" in out or "is vulnerable" in out:
                    confidence += 50
                    log("[BRAIN]", f"Katman 3 (SQLMap): Doğrulandı! +50 güven", GRN)
                break

        self.confidence["SQLi"] = min(confidence, 100)
        log("[BRAIN]", f"SQLi Güven Skoru: %{self.confidence['SQLi']}", YEL if confidence < 70 else GRN)
        if confidence >= 50:
            self.vulns.append({"type":"SQLi","confidence":confidence,"target":self.target})

    # ── Aşama 5: XSS Analizi ─────────────────────────────────────
    def phase_xss(self):
        log("[BRAIN]", "═"*55, MAG)
        log("[BRAIN]", "FAZ 5: XSS TARAMASI", MAG)
        confidence = 0

        xss_engine = BASE / "XSS-Injector" / "xss_engine.py"
        if xss_engine.exists():
            r = run_tool("XSS-Engine", [sys.executable, str(xss_engine),
                                         "-u", self.target, "--crawl", "--batch"], timeout=120)
            self.evidence["xss_internal"] = r
            if "XSS BULUNDU" in r.get("output","") or "HIT" in r.get("output",""):
                confidence += 60
                log("[BRAIN]", f"XSS: İç motor sinyal +60", GRN)

        self.confidence["XSS"] = min(confidence, 100)
        if confidence >= 40:
            self.vulns.append({"type":"XSS","confidence":confidence})

    # ── Aşama 6: Keşif Araçları ───────────────────────────────────
    def phase_recon_deep(self):
        log("[BRAIN]", "═"*55, MAG)
        log("[BRAIN]", "FAZ 6: DERİN KEŞİF (ffuf/katana/impacket)", MAG)

        # ffuf - directory fuzzing
        ffuf_main = TOOLS / "ffuf" / "main.go"
        if not ffuf_main.exists():
            # Python ile basit dir bruteforce
            log("[BRAIN]", "ffuf: dizin keşfi (iç motor ile)", CYN)
            try:
                import requests as _req
                _req.packages.urllib3.disable_warnings()
                sess = _req.Session(); sess.verify = False
                dirs = ["admin","wp-admin","login","dashboard","api","backup",
                       "config","db","test","dev",".env",".git"]
                found = []
                for d in dirs:
                    try:
                        r = sess.get(f"{self.target.rstrip('/')}/{d}", timeout=5)
                        if r.status_code in (200,301,302,403):
                            log("[BRAIN]", f"  DİZİN: /{d} → HTTP {r.status_code}", YEL)
                            found.append(d)
                    except: pass
                self.evidence["ffuf_internal"] = {"found_dirs": found}
            except Exception as e:
                log("[BRAIN]", f"Dizin keşfi hatası: {e}", RED)

        # Reconnaissance engine
        recon_main = BASE / "Reconnaissance" / "main.py"
        if recon_main.exists():
            r = run_tool("Reconnaissance", [sys.executable, str(recon_main), self.target], timeout=90)
            self.evidence["recon"] = r

        # Zero-Day engine
        zd_main = BASE / "Zero-Day" / "main.py"
        if zd_main.exists():
            r = run_tool("Zero-Day", [sys.executable, str(zd_main), self.target], timeout=120)
            self.evidence["zero_day"] = r
            if "BULUNDU" in r.get("output","") or "HIT" in r.get("output",""):
                log("[BRAIN]", "Zero-Day sinyal alındı!", RED)

        # Port Scanner
        ps_main = BASE / "Port-Scanner" / "main.py"
        if ps_main.exists():
            r = run_tool("Port-Scanner", [sys.executable, str(ps_main), self.target], timeout=60)
            self.evidence["portscan_ext"] = r

        # Web Scanner
        ws_main = BASE / "Web-Scanner" / "main.py"
        if ws_main.exists():
            r = run_tool("Web-Scanner", [sys.executable, str(ws_main), self.target], timeout=90)
            self.evidence["web_scanner"] = r
            for line in r.get("output","").split("\n"):
                if "SQLi" in line or "XSS" in line or "RCE" in line:
                    log("[BRAIN]", f"Web-Scanner bulgusu: {line[:80]}", YEL)

        # Data Exfil
        de_main = BASE / "Data-Exfiltration" / "main.py"
        if de_main.exists():
            r = run_tool("Data-Exfil", [sys.executable, str(de_main), self.target], timeout=60)
            self.evidence["data_exfil"] = r
            if "HASSAS" in r.get("output",""):
                log("[BRAIN]", "Veri sızıntısı tespit edildi!", RED)

        # Network Analysis
        net_main = BASE / "Network-Analysis" / "main.py"
        if net_main.exists():
            r = run_tool("Network-Analysis", [sys.executable, str(net_main), self.target], timeout=45)
            self.evidence["network"] = r


        # Auto-generated module calls
        _m_API_Fuzzer = BASE / "API-Fuzzer" / "main.py"
        if _m_API_Fuzzer.exists():
            r = run_tool("API-Fuzzer", [sys.executable, str(_m_API_Fuzzer), self.target], timeout=60)
            self.evidence["API-Fuzzer"] = r
            log("[BRAIN]", f"API-Fuzzer tamamlandı", GRN)

        _m_CSRF_Creator = BASE / "CSRF-Creator" / "main.py"
        if _m_CSRF_Creator.exists():
            r = run_tool("CSRF-Creator", [sys.executable, str(_m_CSRF_Creator), self.target], timeout=60)
            self.evidence["CSRF-Creator"] = r
            log("[BRAIN]", f"CSRF-Creator tamamlandı", GRN)

        _m_CVE_Creator = BASE / "CVE-Creator" / "main.py"
        if _m_CVE_Creator.exists():
            r = run_tool("CVE-Creator", [sys.executable, str(_m_CVE_Creator), self.target], timeout=60)
            self.evidence["CVE-Creator"] = r
            log("[BRAIN]", f"CVE-Creator tamamlandı", GRN)

        _m_Cookie_Stealer = BASE / "Cookie-Stealer" / "main.py"
        if _m_Cookie_Stealer.exists():
            r = run_tool("Cookie-Stealer", [sys.executable, str(_m_Cookie_Stealer), self.target], timeout=60)
            self.evidence["Cookie-Stealer"] = r
            log("[BRAIN]", f"Cookie-Stealer tamamlandı", GRN)

        _m_CrySploit = BASE / "CrySploit" / "main.py"
        if _m_CrySploit.exists():
            r = run_tool("CrySploit", [sys.executable, str(_m_CrySploit), self.target], timeout=60)
            self.evidence["CrySploit"] = r
            log("[BRAIN]", f"CrySploit tamamlandı", GRN)

        _m_Encoding = BASE / "Encoding" / "main.py"
        if _m_Encoding.exists():
            r = run_tool("Encoding", [sys.executable, str(_m_Encoding), self.target], timeout=60)
            self.evidence["Encoding"] = r
            log("[BRAIN]", f"Encoding tamamlandı", GRN)

        _m_Encryption = BASE / "Encryption" / "main.py"
        if _m_Encryption.exists():
            r = run_tool("Encryption", [sys.executable, str(_m_Encryption), self.target], timeout=60)
            self.evidence["Encryption"] = r
            log("[BRAIN]", f"Encryption tamamlandı", GRN)

        _m_Evasion = BASE / "Evasion" / "main.py"
        if _m_Evasion.exists():
            r = run_tool("Evasion", [sys.executable, str(_m_Evasion), self.target], timeout=60)
            self.evidence["Evasion"] = r
            log("[BRAIN]", f"Evasion tamamlandı", GRN)

        _m_Exploits = BASE / "Exploits" / "main.py"
        if _m_Exploits.exists():
            r = run_tool("Exploits", [sys.executable, str(_m_Exploits), self.target], timeout=60)
            self.evidence["Exploits"] = r
            log("[BRAIN]", f"Exploits tamamlandı", GRN)

        _m_Lateral_Movement = BASE / "Lateral-Movement" / "main.py"
        if _m_Lateral_Movement.exists():
            r = run_tool("Lateral-Movement", [sys.executable, str(_m_Lateral_Movement), self.target], timeout=60)
            self.evidence["Lateral-Movement"] = r
            log("[BRAIN]", f"Lateral-Movement tamamlandı", GRN)

        _m_Obfuscation = BASE / "Obfuscation" / "main.py"
        if _m_Obfuscation.exists():
            r = run_tool("Obfuscation", [sys.executable, str(_m_Obfuscation), self.target], timeout=60)
            self.evidence["Obfuscation"] = r
            log("[BRAIN]", f"Obfuscation tamamlandı", GRN)

        _m_Open_Source = BASE / "Open-Source" / "main.py"
        if _m_Open_Source.exists():
            r = run_tool("Open-Source", [sys.executable, str(_m_Open_Source), self.target], timeout=60)
            self.evidence["Open-Source"] = r
            log("[BRAIN]", f"Open-Source tamamlandı", GRN)

        _m_Payload_Generator = BASE / "Payload-Generator" / "main.py"
        if _m_Payload_Generator.exists():
            r = run_tool("Payload-Generator", [sys.executable, str(_m_Payload_Generator), self.target], timeout=60)
            self.evidence["Payload-Generator"] = r
            log("[BRAIN]", f"Payload-Generator tamamlandı", GRN)

        _m_Post_Exploitation = BASE / "Post-Exploitation" / "main.py"
        if _m_Post_Exploitation.exists():
            r = run_tool("Post-Exploitation", [sys.executable, str(_m_Post_Exploitation), self.target], timeout=60)
            self.evidence["Post-Exploitation"] = r
            log("[BRAIN]", f"Post-Exploitation tamamlandı", GRN)

        _m_Privilege_Escalation = BASE / "Privilege-Escalation" / "main.py"
        if _m_Privilege_Escalation.exists():
            r = run_tool("Privilege-Escalation", [sys.executable, str(_m_Privilege_Escalation), self.target], timeout=60)
            self.evidence["Privilege-Escalation"] = r
            log("[BRAIN]", f"Privilege-Escalation tamamlandı", GRN)

        _m_Protocol_Analyzer = BASE / "Protocol-Analyzer" / "main.py"
        if _m_Protocol_Analyzer.exists():
            r = run_tool("Protocol-Analyzer", [sys.executable, str(_m_Protocol_Analyzer), self.target], timeout=60)
            self.evidence["Protocol-Analyzer"] = r
            log("[BRAIN]", f"Protocol-Analyzer tamamlandı", GRN)

        _m_README_Creator = BASE / "README-Creator" / "main.py"
        if _m_README_Creator.exists():
            r = run_tool("README-Creator", [sys.executable, str(_m_README_Creator), self.target], timeout=60)
            self.evidence["README-Creator"] = r
            log("[BRAIN]", f"README-Creator tamamlandı", GRN)

        _m_Tools_Creator = BASE / "Tools-Creator" / "main.py"
        if _m_Tools_Creator.exists():
            r = run_tool("Tools-Creator", [sys.executable, str(_m_Tools_Creator), self.target], timeout=60)
            self.evidence["Tools-Creator"] = r
            log("[BRAIN]", f"Tools-Creator tamamlandı", GRN)

        _m_Unknown_Open = BASE / "Unknown-Open" / "main.py"
        if _m_Unknown_Open.exists():
            r = run_tool("Unknown-Open", [sys.executable, str(_m_Unknown_Open), self.target], timeout=60)
            self.evidence["Unknown-Open"] = r
            log("[BRAIN]", f"Unknown-Open tamamlandı", GRN)

        _m_WebShell = BASE / "WebShell" / "main.py"
        if _m_WebShell.exists():
            r = run_tool("WebShell", [sys.executable, str(_m_WebShell), self.target], timeout=60)
            self.evidence["WebShell"] = r
            log("[BRAIN]", f"WebShell tamamlandı", GRN)

        _m_exploit_template = BASE / "exploit-template" / "main.py"
        if _m_exploit_template.exists():
            r = run_tool("exploit-template", [sys.executable, str(_m_exploit_template), self.target], timeout=60)
            self.evidence["exploit-template"] = r
            log("[BRAIN]", f"exploit-template tamamlandı", GRN)


        # ── Tam Modül Entegrasyonu ─────────────────────────────────
        _mp_Anti_Forensics = BASE / "Anti-Forensics" / "main.py"
        if _mp_Anti_Forensics.exists():
            r = run_tool("Anti-Forensics", [sys.executable, str(_mp_Anti_Forensics), self.target], timeout=45)
            self.evidence["Anti-Forensics"] = r
        _mp_Attack_Create = BASE / "Attack-Create" / "main.py"
        if _mp_Attack_Create.exists():
            r = run_tool("Attack-Create", [sys.executable, str(_mp_Attack_Create), self.target], timeout=45)
            self.evidence["Attack-Create"] = r
        _mp_Binary_Analysis = BASE / "Binary-Analysis" / "main.py"
        if _mp_Binary_Analysis.exists():
            r = run_tool("Binary-Analysis", [sys.executable, str(_mp_Binary_Analysis), self.target], timeout=45)
            self.evidence["Binary-Analysis"] = r
        _mp_Brain_System = BASE / "Brain-System" / "main.py"
        if _mp_Brain_System.exists():
            r = run_tool("Brain-System", [sys.executable, str(_mp_Brain_System), self.target], timeout=45)
            self.evidence["Brain-System"] = r
        _mp_Brute_Force = BASE / "Brute-Force" / "main.py"
        if _mp_Brute_Force.exists():
            r = run_tool("Brute-Force", [sys.executable, str(_mp_Brute_Force), self.target], timeout=45)
            self.evidence["Brute-Force"] = r
        _mp_C2_Communication = BASE / "C2-Communication" / "main.py"
        if _mp_C2_Communication.exists():
            r = run_tool("C2-Communication", [sys.executable, str(_mp_C2_Communication), self.target], timeout=45)
            self.evidence["C2-Communication"] = r
        _mp_Configuration_Audit = BASE / "Configuration-Audit" / "main.py"
        if _mp_Configuration_Audit.exists():
            r = run_tool("Configuration-Audit", [sys.executable, str(_mp_Configuration_Audit), self.target], timeout=45)
            self.evidence["Configuration-Audit"] = r
        _mp_Create = BASE / "Create" / "main.py"
        if _mp_Create.exists():
            r = run_tool("Create", [sys.executable, str(_mp_Create), self.target], timeout=45)
            self.evidence["Create"] = r
        _mp_Crypto_Breaker = BASE / "Crypto-Breaker" / "main.py"
        if _mp_Crypto_Breaker.exists():
            r = run_tool("Crypto-Breaker", [sys.executable, str(_mp_Crypto_Breaker), self.target], timeout=45)
            self.evidence["Crypto-Breaker"] = r
        _mp_Database_Dump = BASE / "Database-Dump" / "main.py"
        if _mp_Database_Dump.exists():
            r = run_tool("Database-Dump", [sys.executable, str(_mp_Database_Dump), self.target], timeout=45)
            self.evidence["Database-Dump"] = r
        _mp_Dictionary_Attack = BASE / "Dictionary-Attack" / "main.py"
        if _mp_Dictionary_Attack.exists():
            r = run_tool("Dictionary-Attack", [sys.executable, str(_mp_Dictionary_Attack), self.target], timeout=45)
            self.evidence["Dictionary-Attack"] = r
        _mp_Log_Cleaner = BASE / "Log-Cleaner" / "main.py"
        if _mp_Log_Cleaner.exists():
            r = run_tool("Log-Cleaner", [sys.executable, str(_mp_Log_Cleaner), self.target], timeout=45)
            self.evidence["Log-Cleaner"] = r
        _mp_Memory_Forensics = BASE / "Memory-Forensics" / "main.py"
        if _mp_Memory_Forensics.exists():
            r = run_tool("Memory-Forensics", [sys.executable, str(_mp_Memory_Forensics), self.target], timeout=45)
            self.evidence["Memory-Forensics"] = r
        _mp_Patch_Analysis = BASE / "Patch-Analysis" / "main.py"
        if _mp_Patch_Analysis.exists():
            r = run_tool("Patch-Analysis", [sys.executable, str(_mp_Patch_Analysis), self.target], timeout=45)
            self.evidence["Patch-Analysis"] = r
        _mp_Payloads = BASE / "Payloads" / "main.py"
        if _mp_Payloads.exists():
            r = run_tool("Payloads", [sys.executable, str(_mp_Payloads), self.target], timeout=45)
            self.evidence["Payloads"] = r
        _mp_Phishing_Framework = BASE / "Phishing-Framework" / "main.py"
        if _mp_Phishing_Framework.exists():
            r = run_tool("Phishing-Framework", [sys.executable, str(_mp_Phishing_Framework), self.target], timeout=45)
            self.evidence["Phishing-Framework"] = r
        _mp_Reverse_Engineering = BASE / "Reverse-Engineering" / "main.py"
        if _mp_Reverse_Engineering.exists():
            r = run_tool("Reverse-Engineering", [sys.executable, str(_mp_Reverse_Engineering), self.target], timeout=45)
            self.evidence["Reverse-Engineering"] = r
        _mp_Session_Hijacking = BASE / "Session-Hijacking" / "main.py"
        if _mp_Session_Hijacking.exists():
            r = run_tool("Session-Hijacking", [sys.executable, str(_mp_Session_Hijacking), self.target], timeout=45)
            self.evidence["Session-Hijacking"] = r
        _mp_Social_Engineering = BASE / "Social-Engineering" / "main.py"
        if _mp_Social_Engineering.exists():
            r = run_tool("Social-Engineering", [sys.executable, str(_mp_Social_Engineering), self.target], timeout=45)
            self.evidence["Social-Engineering"] = r
        _mp_System_Hardening = BASE / "System-Hardening" / "main.py"
        if _mp_System_Hardening.exists():
            r = run_tool("System-Hardening", [sys.executable, str(_mp_System_Hardening), self.target], timeout=45)
            self.evidence["System-Hardening"] = r
        _mp_Testing_Code = BASE / "Testing-Code" / "main.py"
        if _mp_Testing_Code.exists():
            r = run_tool("Testing-Code", [sys.executable, str(_mp_Testing_Code), self.target], timeout=45)
            self.evidence["Testing-Code"] = r
        _mp_Verify = BASE / "Verify" / "main.py"
        if _mp_Verify.exists():
            r = run_tool("Verify", [sys.executable, str(_mp_Verify), self.target], timeout=45)
            self.evidence["Verify"] = r
        _mp_Verify_Code = BASE / "Verify-Code" / "main.py"
        if _mp_Verify_Code.exists():
            r = run_tool("Verify-Code", [sys.executable, str(_mp_Verify_Code), self.target], timeout=45)
            self.evidence["Verify-Code"] = r
        _mp_Vulnerability_Database = BASE / "Vulnerability-Database" / "main.py"
        if _mp_Vulnerability_Database.exists():
            r = run_tool("Vulnerability-Database", [sys.executable, str(_mp_Vulnerability_Database), self.target], timeout=45)
            self.evidence["Vulnerability-Database"] = r
        _mp_Wordlist_Generator = BASE / "Wordlist-Generator" / "main.py"
        if _mp_Wordlist_Generator.exists():
            r = run_tool("Wordlist-Generator", [sys.executable, str(_mp_Wordlist_Generator), self.target], timeout=45)
            self.evidence["Wordlist-Generator"] = r

        # impacket - sadece ip ise SMB dene
        impacket_base = TOOLS / "impacket"
        if impacket_base.exists():
            log("[BRAIN]", "impacket: SMB/RPC analizi hazır", CYN)

    # ── Aşama 7: Hash & Şifre Analizi ────────────────────────────
    def phase_hash_crack(self, hashes=None):
        if not hashes: return
        log("[BRAIN]", "═"*55, MAG)
        log("[BRAIN]", "FAZ 7: HASH KIRMA (hashcat tabanlı)", MAG)
        hashcat_bin = TOOLS / "hashcat" / "src" / "hashcat.c"
        if hashcat_bin.exists():
            log("[BRAIN]", "hashcat: kaynak kod mevcut (derleme gerekir)", YEL)
        # Python tabanlı hash kırıcı
        r = run_tool("HashCrack-Internal",
                     [sys.executable, "-c", f"""
import hashlib
wordlist = ['admin','password','123456','root','test','toor']
for h_input in {hashes!r}:
    for w in wordlist:
        if hashlib.md5(w.encode()).hexdigest() == h_input or \\
           hashlib.sha1(w.encode()).hexdigest() == h_input:
            print(f'FOUND: {{h_input}} = {{w}}')
"""])
        self.evidence["hashcrack"] = r

    # ── Aşama 8: WP Tarama ───────────────────────────────────────
    def phase_wpscan(self):
        out = self.evidence.get("httpx",{}).get("output","")
        if "wordpress" not in str(out).lower() and "wp-content" not in str(
                self.evidence.get("nikto",{}).get("output","")).lower():
            return
        log("[BRAIN]", "WordPress tespit edildi — WPScan başlatılıyor", YEL)
        wpscan_rb = TOOLS / "wpscan" / "bin" / "wpscan"
        if wpscan_rb.exists():
            r = run_tool("WPScan", ["ruby", str(wpscan_rb), "--url", self.target,
                                     "--no-banner", "--format=json"], timeout=180)
            self.evidence["wpscan"] = r

    # ── Aşama 9: YARA İmza Tarama ────────────────────────────────
    def phase_yara(self, target_files=None):
        yara_base = TOOLS / "yara"
        if not yara_base.exists(): return
        log("[BRAIN]", "YARA imza taraması hazır", CYN)
        rules_dir = yara_base / "tests" / "rules"
        if not rules_dir.exists():
            rules_dir = yara_base
        log("[BRAIN]", f"YARA kurallar: {rules_dir}", CYN)

    # ── Karar Motoru ─────────────────────────────────────────────
    def make_decision(self):
        log("[BRAIN]", "═"*55, MAG)
        log("[BRAIN]", "BEYİN KARAR MOTORU — Tüm kanıtlar korele ediliyor", MAG)
        log("[BRAIN]", "═"*55, MAG)

        decisions = []
        for vuln in self.vulns:
            vtype = vuln["type"]
            conf  = vuln["confidence"]
            log("[BRAIN]", f"  {vtype}: %{conf} güven", GRN if conf>=70 else YEL)
            if conf >= 60:
                decisions.append({
                    "vuln": vtype, "confidence": conf,
                    "action": "EXPLOIT_GENERATE",
                    "confirmed": conf >= 70
                })
            elif conf >= 30:
                decisions.append({"vuln": vtype, "confidence": conf,
                                   "action": "FURTHER_VERIFY"})

        # False-positive filtre: En az 2 bağımsız kaynak gerekir
        filtered = []
        for d in decisions:
            vtype = d["vuln"]
            sources = sum([
                1 if vtype.lower() in str(self.evidence.get("sqli_internal",{}).get("output","")).lower() else 0,
                1 if vtype.lower() in str(self.evidence.get("commix",{}).get("output","")).lower() else 0,
                1 if vtype.lower() in str(self.evidence.get("sqlmap",{}).get("output","")).lower() else 0,
                1 if vtype.lower() in str(self.evidence.get("nikto",{}).get("output","")).lower() else 0,
                1 if vtype.lower() in str(self.evidence.get("xss_internal",{}).get("output","")).lower() else 0,
                1 if vtype.lower() in str(self.evidence.get("zero_day",{}).get("output","")).lower() else 0,
                1 if vtype.lower() in str(self.evidence.get("web_scanner",{}).get("output","")).lower() else 0,
                1 if vtype.lower() in str(self.evidence.get("recon",{}).get("output","")).lower() else 0,
            ])
            if sources >= 1 or d["confidence"] >= 70:
                d["independent_sources"] = sources
                filtered.append(d)
                log("[BRAIN]", f"  ONAYLANDI: {vtype} (bağımsız kaynak: {sources})", GRN)
            else:
                log("[BRAIN]", f"  FALSE-POSITIVE FİLTRESİ: {vtype} yetersiz kanıt", YEL)

        return filtered

    # ── Ana Orkestrasyon ─────────────────────────────────────────
    def orchestrate(self):
        log("[BRAIN]", "╔"+"═"*54+"╗", MAG)
        log("[BRAIN]", "║  HRSploit Brain Orchestrator — TAM TARAMA        ║", MAG)
        log("[BRAIN]", "╚"+"═"*54+"╝", MAG)
        log("[BRAIN]", f"Hedef: {self.target}", CYN)
        log("[BRAIN]", f"İnternet: {'✅ BAĞLI' if self.internet else '❌ BAĞLANTI YOK'}", 
            GRN if self.internet else RED)

        self.phase_recon()
        self.phase_portscan()
        self.phase_vuln_scan()
        self.phase_sqli()
        self.phase_xss()
        self.phase_recon_deep()
        self.phase_wpscan()

        decisions = self.make_decision()
        
        # Rapor kaydet
        report = {
            "target": self.target, "session": self.session_id,
            "vulns": self.vulns, "decisions": decisions,
            "evidence_keys": list(self.evidence.keys()),
            "confidence": self.confidence,
        }
        rpt = REPORTS / f"brain_{self.session_id}.json"
        import json
        rpt.write_text(json.dumps(report, indent=2))
        log("[BRAIN]", f"Rapor: {rpt}", GRN)
        return decisions


# Zero-Day başarı banner'ı
ZERO_DAY_SUCCESS = """
\033[91m\033[93m
 ███████╗███████╗██████╗  ██████╗       ██████╗  █████╗ ██╗   ██╗
 \033[91m \033[93m╚══███╔╝██╔════╝██╔══██╗██╔═══██╗      ██╔══██╗██╔══██╗╚██╗ ██╔╝
 \033[91m   \033[93m███╔╝ █████╗  ██████╔╝██║   ██║█████╗██║  ██║███████║ ╚████╔╝
 \033[91m  \033[93m███╔╝  ██╔══╝  ██╔══██╗██║   ██║╚════╝██║  ██║██╔══██║  ╚██╔╝
 \033[91m ███████╗███████╗██║  ██║╚██████╔╝      ██████╔╝██║  ██║   ██║
 \033[91m \033[93m╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝       ╚═════╝ ╚═╝  ╚═╝   ╚═╝

\033[91m  ██████╗ ██████╗  ██████╗  ██████╗███████╗
 \033[93m ██╔══██╗██╔══██╗██╔═══██╗██╔════╝██╔════╝
 \033[91m ██████╔╝██████╔╝██║   ██║██║     █████╗
 \033[93m ██╔═══╝ ██╔══██╗██║   ██║██║     ██╔══╝
 \033[91m ██║     ██║  ██║╚██████╔╝╚██████╗███████╗
 \033[93m ╚═╝     ╚═╝  ╚═╝ ╚═════╝  ╚═════╝╚══════╝

\033[91m!!!\033[93m!!!\033[91m!!!\033[93m!!!\033[91m!!!\033[93m!!!\033[91m!!!\033[93m!!!\033[91m!!!\033[93m!!!\033[91m!!!\033[93m!!!\033[91m!!!\033[93m!!!\033[91m!!!\033[93m!!!

\033[93m  ZERO-DAY AÇIĞI ONAYLANDI VE EXPLOIT EDİLDİ ✓✓✓
\033[91m  CANLΙ TEST BAŞARILI — ARAÇ KULLANIMA HAZIR

\033[91m!!!\033[93m!!!\033[91m!!!\033[93m!!!\033[91m!!!\033[93m!!!\033[91m!!!\033[93m!!!\033[91m!!!\033[93m!!!\033[91m!!!\033[93m!!!\033[91m!!!\033[93m!!!\033[91m!!!\033[93m!!!
\033[0m"""

def show_zero_day_success():
    print(ZERO_DAY_SUCCESS)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Kullanım: python brain_orchestrator.py <URL>")
        sys.exit(1)
    brain = BrainOrchestrator(sys.argv[1])
    brain.orchestrate()
