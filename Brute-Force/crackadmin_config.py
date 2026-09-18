"""CrackAdmin v2.0 - Merkezi Yapılandırma"""
from pathlib import Path

BASE_DIR    = Path(__file__).parent
DATA_DIR    = BASE_DIR / "data"
LOGS_DIR    = BASE_DIR / "logs"
INFO_DIR    = BASE_DIR / "info"

for d in [DATA_DIR, LOGS_DIR, INFO_DIR]:
    d.mkdir(exist_ok=True)

WORDLIST_FILE  = DATA_DIR / "wordlist.txt"
PAYLOADS_FILE  = DATA_DIR / "payloads.txt"
DORKS_FILE     = DATA_DIR / "dorks.txt"
SUCCESS_FILE   = LOGS_DIR / "successites.txt"
OLDSITE_FILE   = LOGS_DIR / "oldsites.txt"
ACTIVE_LOG     = LOGS_DIR / "active.log"
ERROR_LOG      = LOGS_DIR / "error.log"

MAX_THREADS    = 70
REQ_TIMEOUT    = 12
RETRY_COUNT    = 2
DELAY_BASE     = 0.25

FW_CODES       = {403, 429, 503}
FW_PATTERNS    = ["cloudflare","waf","blocked","forbidden",
                  "rate limit","access denied","captcha","ddos"]
SUCCESS_TOKENS = ["dashboard","logout","welcome","admin panel",
                  "administrator","control panel","sign out",
                  "log out","my account","configuration","settings"]
FAIL_TOKENS    = ["invalid","incorrect","failed","wrong password",
                  "error","unauthorized","bad credentials","try again"]

VERSION = "2.0"
