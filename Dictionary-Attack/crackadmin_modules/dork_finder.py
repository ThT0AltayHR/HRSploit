"""
CrackAdmin - Dork Finder (100+ dork, Türkçe yok, tam profesyonel)
"""

import re, time, requests, threading
from urllib.parse import urljoin, urlparse, quote_plus
from typing import List, Set, Optional, Callable
from pathlib import Path
import urllib3
urllib3.disable_warnings()

from config import OLDSITE_FILE, FW_CODES, REQ_TIMEOUT

DORK_LIST = [
    'intitle:"Admin Login"','intitle:"Admin Panel"','intitle:"Administration"',
    'intitle:"Administrator Login"','intitle:"Admin Area"','intitle:"Control Panel"',
    'intitle:"Site Administration"','intitle:"Web Admin"','intitle:"Backend Login"',
    'intitle:"Management Console"','intitle:"Login Page"','intitle:"User Login"',
    'intitle:"Member Login"','intitle:"Secure Login"','intitle:"Portal Login"',
    'intitle:"CMS Login"','intitle:"Content Management"','intitle:"Site Manager"',
    'intitle:"Dashboard" inurl:admin','intitle:"Dashboard" inurl:panel',
    'inurl:admin','inurl:admin/login','inurl:admin.php','inurl:admin.html',
    'inurl:admin.asp','inurl:admin.aspx','inurl:admin/index.php',
    'inurl:admin/admin.php','inurl:/administrator/','inurl:/administrator/index.php',
    'inurl:/administrator/login','inurl:/manage','inurl:/management',
    'inurl:/backend','inurl:/controlpanel','inurl:/cp','inurl:/cpanel',
    'inurl:wp-admin','inurl:wp-login.php','inurl:/user/login','inurl:/users/login',
    'inurl:/account/login','inurl:/login.php','inurl:/login.asp','inurl:/login.aspx',
    'inurl:/signin.php','inurl:/panel','inurl:/panel.php','inurl:/dashboard',
    'inurl:/admin_panel','inurl:/site/admin','inurl:webadmin','inurl:web_admin',
    'inurl:siteadmin','inurl:phpmyadmin','inurl:pma','inurl:myadmin',
    'inurl:sqlmanager','inurl:admin_login.php','inurl:admin_login.asp',
    'inurl:admin_area','inurl:admin_panel','inurl:secure_admin',
    'inurl:wp-admin intitle:"WordPress"','inurl:wp-login.php intitle:"WordPress"',
    'intitle:"WordPress" inurl:admin',
    'inurl:/administrator intitle:"Joomla"','intitle:"Joomla Administrator"',
    'inurl:/user/login intitle:"Drupal"','inurl:/?q=user/login intitle:"Drupal"',
    'inurl:2082 intitle:"cPanel"','inurl:2083 intitle:"cPanel"',
    'inurl:2086 intitle:"WHM"','inurl:2087 intitle:"WHM"',
    'inurl:8880 intitle:"Plesk"','inurl:8443 intitle:"Plesk"',
    'inurl:10000 intitle:"Webmin"',
    'inurl:/admin intitle:"OpenCart"','inurl:/admin intitle:"Magento"',
    'inurl:/admin intitle:"PrestaShop"','inurl:/admin intitle:"WooCommerce"',
    'inurl:/admincp intitle:"vBulletin"','inurl:/adm intitle:"phpBB"',
    'intitle:"phpMyAdmin" inurl:phpmyadmin','inurl:phpmyadmin/index.php',
    'inurl:admin site:.tr','inurl:admin site:.de','inurl:admin site:.ru',
    'inurl:admin site:.br','inurl:admin site:.in','inurl:admin site:.cn',
    'intitle:"ASP.NET" inurl:admin','intitle:"PHP" inurl:admin',
    'inurl:admin.asp intitle:"login"','inurl:admin.aspx intitle:"login"',
    'inurl:/api/admin','inurl:/v1/admin','inurl:/api/login',
    'intitle:"Admin" inurl:index.php','intitle:"Admin" inurl:login.php',
    'intitle:"Administrator" inurl:login',
    'inurl:/admin intitle:"Laravel"','inurl:/admin/ intitle:"Django"',
    'intitle:"Log In" inurl:admin','intitle:"Sign In" inurl:admin',
    'intitle:"Enter Password" inurl:admin',
    'intitle:"Tomcat Manager"','intitle:"JBoss Management"',
    'intitle:"system admin"','intitle:"admin login" inurl:login',
    'intitle:"phpMyAdmin"',
    'inurl:admin intitle:"login" site:.com',
    'inurl:admin intitle:"login" site:.net',
    'inurl:admin intitle:"login" site:.org',
    'inurl:login intitle:"admin"',
    'inurl:cp intitle:"login"',
    'inurl:portal intitle:"login"',
]

ADMIN_PATHS = [
    "/admin","/admin/","/administrator","/administrator/",
    "/admin/login","/admin/login.php","/admin/index.php",
    "/administrator/index.php","/administrator/login",
    "/manage","/management","/backend","/panel",
    "/cpanel","/cp","/controlpanel","/dashboard",
    "/wp-admin","/wp-login.php","/user/login","/login",
    "/signin","/login.php","/login.asp","/login.aspx",
    "/admin.php","/admin.asp","/admin.aspx",
    "/admin_panel","/admin_area","/site/admin",
    "/phpmyadmin","/pma","/myadmin",
]

ADMIN_KW = [
    "password","username","user name","enter password",
    "administration","dashboard","log in","sign in",
    "control panel","backend","management",
    "input type=\"password\"","input type='password'",
]

UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/119.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:121.0) Gecko/20100101 Firefox/121.0",
]

class DorkFinder:
    def __init__(self, log_fn=None, stream_fn=None):
        self._log    = log_fn    or (lambda t,k="": print(t))
        self._stream = stream_fn or (lambda t: print(t))
        self.old_sites: Set[str] = self._load_old()
        self.found:     Set[str] = set()
        self._ua_idx = 0
        self._stop   = threading.Event()

    def _load_old(self) -> Set[str]:
        if OLDSITE_FILE.exists():
            return set(OLDSITE_FILE.read_text(encoding="utf-8").splitlines())
        return set()

    def _ua(self) -> str:
        u = UA_LIST[self._ua_idx % len(UA_LIST)]
        self._ua_idx += 1
        return u

    def _get(self, url, timeout=10) -> Optional[requests.Response]:
        try:
            return requests.get(url, timeout=timeout,
                                headers={"User-Agent": self._ua()},
                                allow_redirects=True, verify=False)
        except Exception:
            return None

    def _search_bing(self, dork: str, max_r: int = 15) -> List[str]:
        q   = quote_plus(dork)
        res = self._get(f"https://www.bing.com/search?q={q}&count=30")
        if not res:
            return []
        raw  = re.findall(r'<a[^>]+href=["\']?(https?://[^r"\'>\s]+)["\']?', res.text, re.I)
        skip = {"bing.com","microsoft.com","google.com","youtube.com","wikipedia.org"}
        seen = set()
        out  = []
        for u in raw:
            p = urlparse(u)
            base = f"{p.scheme}://{p.netloc}"
            if (base not in self.old_sites and
                base not in self.found and
                base not in seen and
                not any(s in base for s in skip) and
                len(base) > 12):
                out.append(base)
                seen.add(base)
                if len(out) >= max_r:
                    break
        return out

    def verify_admin(self, base_url: str) -> Optional[str]:
        for path in ADMIN_PATHS:
            if self._stop.is_set():
                return None
            url = base_url.rstrip("/") + path
            r   = self._get(url, timeout=6)
            if not r:
                continue
            if r.status_code in FW_CODES:
                return None
            if r.status_code == 200:
                body = r.text.lower()
                if any(kw in body for kw in ADMIN_KW):
                    return url
        return None

    def find_sites(self, target: int, custom_dorks: List[str] = None,
                   on_found: Callable[[str], None] = None) -> List[str]:
        import warnings; warnings.filterwarnings("ignore")
        self._stop.clear()

        dorks   = (custom_dorks or []) + DORK_LIST
        results = []

        for i, dork in enumerate(dorks):
            if self._stop.is_set() or len(results) >= target:
                break

            self._stream(f"[{i+1}/{len(dorks)}] {dork}")
            candidates = self._search_bing(dork, max_r=target - len(results) + 5)

            for base in candidates:
                if self._stop.is_set() or len(results) >= target:
                    break
                if base in self.found or base in self.old_sites:
                    continue
                self._stream(f"  verifying: {base}")
                admin_url = self.verify_admin(base)
                if admin_url:
                    self.found.add(base)
                    results.append(admin_url)
                    self._log(f"Admin panel: {admin_url}")
                    if on_found:
                        on_found(admin_url)

            time.sleep(1)

        self._save_old(list(self.found))
        return results

    def _save_old(self, sites):
        all_sites = self.old_sites | set(sites)
        OLDSITE_FILE.write_text("\n".join(sorted(all_sites)), encoding="utf-8")
        self.old_sites = all_sites

    def stop(self):
        self._stop.set()
