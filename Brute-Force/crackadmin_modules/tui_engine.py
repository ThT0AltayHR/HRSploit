"""
CrackAdmin - Codex benzeri CLI TUI Engine
Ekran görüntüsündeki gibi:
- Üstte mesaj akışı (bullet • ile)
- Altta > prompt
- / ile komut autocomplete listesi
- Ok tuşları ile seçim
"""

import sys, os, threading, time, textwrap, readline
from datetime import datetime
from collections import deque
from enum import Enum

# ── ANSI renk yardımcıları ───────────────────────────────────────────────────
def _c(code): return f"\033[{code}m"
RST   = _c(0)
BOLD  = _c(1)
DIM   = _c(2)
CYAN  = _c(36)
BCYAN = _c(96)
GREEN = _c(32)
BGRN  = _c(92)
RED   = _c(31)
BRED  = _c(91)
YEL   = _c(33)
BYEL  = _c(93)
WHT   = _c(37)
BWHT  = _c(97)
BLU   = _c(34)
BBLU  = _c(94)
MAG   = _c(35)
BMAG  = _c(95)
GRY   = _c("38;5;242")
DGRN  = _c("38;5;28")

def clr():
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()

def move_up(n):
    sys.stdout.write(f"\033[{n}A")
def erase_line():
    sys.stdout.write("\033[2K\r")

# ── Mesaj tipleri ────────────────────────────────────────────────────────────
class M(Enum):
    INFO    = "info"
    SUCCESS = "success"
    ERROR   = "error"
    WARN    = "warn"
    SYSTEM  = "system"
    STREAM  = "stream"   # canlı güncellenen satır
    DIM     = "dim"
    HEADER  = "header"
    BULLET  = "bullet"   # Codex'teki • stili

# ── Log satırı ───────────────────────────────────────────────────────────────
class LogLine:
    __slots__ = ("text","mtype","ts","indent")
    def __init__(self, text, mtype=M.INFO, indent=0):
        self.text   = text
        self.mtype  = mtype
        self.ts     = datetime.now().strftime("%H:%M:%S")
        self.indent = indent

# ── Komut tanımları (Codex'teki gibi / ile) ──────────────────────────────────
COMMANDS = [
    ("/start",    "yeni tarama başlat"),
    ("/stop",     "aktif taramayı durdur"),
    ("/results",  "başarılı girişleri göster"),
    ("/wordlist", "wordlist istatistikleri"),
    ("/wordlist add <dosya>", "dış wordlist ekle"),
    ("/status",   "sistem durumunu göster"),
    ("/clear",    "ekranı temizle"),
    ("/help",     "yardım ekranını göster"),
    ("/new",      "yeni oturum başlat"),
    ("/exit",     "programdan çık"),
]

# ── Spinner ──────────────────────────────────────────────────────────────────
SPIN = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]

# ── Ana TUI sınıfı ───────────────────────────────────────────────────────────
class TUI:
    """
    Codex'e birebir benzer CLI akışı:
    • mesajlar yukarıdan aşağı akar
    • en altta > prompt
    • / yazınca dropdown komut listesi açılır
    • ok tuşları ile seçim yapılır
    """

    def __init__(self):
        self._lock      = threading.Lock()
        self._lines     = deque(maxlen=500)
        self._stream_ln = None          # son STREAM satırı
        self._spin_idx  = 0
        self._spin_on   = False
        self._spin_lbl  = ""
        self._spin_thr  = None
        self._cb        = None          # input callback
        self._running   = True
        self._stats     = {"sites":0,"attempts":0,"hits":0,"blocked":0}
        self._input_hist= []
        self._term_w    = self._get_w()

    # ── Boyut ────────────────────────────────────────────────────────────────
    def _get_w(self):
        try:
            return os.get_terminal_size().columns
        except Exception:
            return 80

    def _w(self):
        self._term_w = self._get_w()
        return self._term_w

    # ── Public log API ───────────────────────────────────────────────────────
    def log(self, text, mtype=M.INFO, indent=0):
        with self._lock:
            self._stream_ln = None
            for ln in str(text).split("\n"):
                self._lines.append(LogLine(ln, mtype, indent))
        self._print_line(self._lines[-1] if self._lines else None)

    def bullet(self, text):
        """Codex'teki • bullet stili"""
        self.log(text, M.BULLET)

    def sub(self, text):
        """Alt satır (└─ stili)"""
        self.log(text, M.DIM, indent=2)

    def ok(self, text):
        self.log(text, M.SUCCESS)

    def err(self, text):
        self.log(text, M.ERROR)

    def warn(self, text):
        self.log(text, M.WARN)

    def sys(self, text):
        self.log(text, M.SYSTEM)

    def stream(self, text):
        """Aynı satırı güncelle (canlı çıktı)"""
        with self._lock:
            self._stream_ln = text
        self._print_stream(text)

    def sep(self):
        """Yatay ayırıcı çizgi"""
        w = self._w()
        self._raw_print(f"{GRY}{'─'*w}{RST}")

    # ── İç print ─────────────────────────────────────────────────────────────
    def _fmt(self, ln: LogLine) -> str:
        w   = self._w()
        txt = ln.text
        ind = "  " * ln.indent

        if ln.mtype == M.SUCCESS:
            return f"{BGRN}✓ {ind}{txt}{RST}"
        elif ln.mtype == M.ERROR:
            return f"{BRED}✗ {ind}{txt}{RST}"
        elif ln.mtype == M.WARN:
            return f"{BYEL}⚠ {ind}{txt}{RST}"
        elif ln.mtype == M.SYSTEM:
            return f"{CYAN}  {ind}{txt}{RST}"
        elif ln.mtype == M.BULLET:
            return f"{BWHT}• {ind}{txt}{RST}"
        elif ln.mtype == M.HEADER:
            return f"{BOLD}{BCYAN}{txt}{RST}"
        elif ln.mtype == M.DIM:
            return f"{GRY}  {ind}└─ {txt}{RST}"
        elif ln.mtype == M.STREAM:
            return f"{BLU}  {txt}{RST}"
        else:
            return f"  {ind}{txt}"

    def _print_line(self, ln):
        if ln is None:
            return
        try:
            print(self._fmt(ln))
        except Exception:
            pass

    def _print_stream(self, text):
        try:
            sys.stdout.write(f"\r{BLU}  ↻ {text[:self._w()-6]}{RST}\033[K")
            sys.stdout.flush()
        except Exception:
            pass

    def _raw_print(self, text):
        try:
            print(text)
        except Exception:
            pass

    # ── İstatistik güncelle ──────────────────────────────────────────────────
    def update_stats(self, **kw):
        self._stats.update(kw)

    # ── Spinner ──────────────────────────────────────────────────────────────
    def spin_start(self, label="İşleniyor"):
        self._spin_on  = True
        self._spin_lbl = label
        if self._spin_thr and self._spin_thr.is_alive():
            return
        def _run():
            while self._spin_on:
                f = SPIN[self._spin_idx % len(SPIN)]
                sys.stdout.write(f"\r{CYAN}{f} {self._spin_lbl}...{RST}\033[K")
                sys.stdout.flush()
                self._spin_idx += 1
                time.sleep(0.08)
            sys.stdout.write("\r\033[K")
            sys.stdout.flush()
        self._spin_thr = threading.Thread(target=_run, daemon=True)
        self._spin_thr.start()

    def spin_stop(self, ok_msg=None):
        self._spin_on = False
        if self._spin_thr:
            self._spin_thr.join(timeout=0.3)
        if ok_msg:
            self.ok(ok_msg)

    # ── Header banner ────────────────────────────────────────────────────────
    def print_banner(self):
        w = self._w()
        clr()
        self._raw_print(f"{BCYAN}{BOLD}")
        lines = [
            "  ██████╗██████╗  █████╗  ██████╗██╗  ██╗",
            " ██╔════╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝",
            " ██║     ██████╔╝███████║██║     █████╔╝  ",
            " ██║     ██╔══██╗██╔══██║██║     ██╔═██╗  ",
            " ╚██████╗██║  ██║██║  ██║╚██████╗██║  ██╗ ",
            "  ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝",
        ]
        for l in lines:
            print(l)
        self._raw_print(f"{RST}")
        sub = f" Admin Panel Tester v2.0  •  yalnızca yasal test"
        self._raw_print(f"{GRY}{sub}{RST}")
        self._raw_print(f"{GRY}{'─'*min(w,50)}{RST}\n")

    # ── /help ekranı ─────────────────────────────────────────────────────────
    def print_help(self):
        w = self._w()
        self.sep()
        self._raw_print(f"\n{BOLD}{BWHT}  Komutlar{RST}\n")
        for cmd, desc in COMMANDS:
            pad = 30 - len(cmd)
            self._raw_print(f"  {BCYAN}{cmd}{RST}{' '*pad}{GRY}{desc}{RST}")
        self._raw_print(f"\n  {GRY}/ yazarak komut listesini açabilirsiniz{RST}")
        self._raw_print(f"  {GRY}↑↓ ok tuşları ile seçin, Enter ile çalıştırın{RST}\n")
        self.sep()

    # ── Komut dropdown (Codex'teki gibi) ─────────────────────────────────────
    def _show_dropdown(self, prefix):
        """/ yazınca altta komut listesini göster"""
        matches = [(c,d) for c,d in COMMANDS if c.startswith(prefix)]
        if not matches:
            matches = COMMANDS
        sys.stdout.write("\n")
        for i,(cmd,desc) in enumerate(matches):
            pad = 26 - len(cmd)
            marker = f"{BCYAN}>{RST}" if i == 0 else " "
            sys.stdout.write(f"  {marker} {BCYAN}{cmd}{RST}{' '*max(1,pad)}{GRY}{desc}{RST}\n")
        sys.stdout.flush()
        return matches

    # ── Ana input döngüsü ────────────────────────────────────────────────────
    def set_callback(self, fn):
        self._cb = fn

    def run(self):
        """Ana giriş döngüsü - Codex gibi"""
        import termios, tty

        fd  = sys.stdin.fileno()
        old = termios.tcgetattr(fd)

        def _restore():
            try:
                termios.tcsetattr(fd, termios.TCSADRAIN, old)
            except Exception:
                pass

        try:
            while self._running:
                self._input_loop(fd, old)
        except (KeyboardInterrupt, EOFError):
            pass
        finally:
            _restore()
            print()

    def _input_loop(self, fd, old_term):
        import termios, tty

        buf      = []
        hist_idx = -1
        dropdown = False
        dd_items = []
        dd_sel   = 0
        dd_lines = 0  # kaç satır çizildi

        termios.tcsetattr(fd, termios.TCSADRAIN, old_term)
        sys.stdout.write(f"\n{BOLD}{BCYAN} >{RST} ")
        sys.stdout.flush()

        tty.setraw(fd)
        try:
            while True:
                ch = sys.stdin.read(1)

                # Ctrl+C
                if ch == "\x03":
                    self._running = False
                    return

                # Enter
                if ch in ("\r", "\n"):
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_term)
                    if dropdown and dd_items:
                        # Seçili komutu al
                        cmd = dd_items[dd_sel][0]
                        # Dropdown temizle
                        for _ in range(dd_lines + 1):
                            move_up(1); erase_line()
                        sys.stdout.write(f"\n{BOLD}{BCYAN} >{RST} {BWHT}{cmd}{RST}\n")
                        sys.stdout.flush()
                        if self._cb:
                            threading.Thread(target=self._cb, args=(cmd,), daemon=True).start()
                        return
                    else:
                        cmd = "".join(buf).strip()
                        sys.stdout.write("\n")
                        sys.stdout.flush()
                        if cmd:
                            self._input_hist.append(cmd)
                            if self._cb:
                                threading.Thread(target=self._cb, args=(cmd,), daemon=True).start()
                        return

                # Backspace
                if ch in ("\x7f", "\x08"):
                    if buf:
                        buf.pop()
                        sys.stdout.write("\b \b")
                        sys.stdout.flush()
                    # Dropdown'u güncelle
                    if dropdown:
                        for _ in range(dd_lines):
                            move_up(1); erase_line()
                        prefix = "".join(buf)
                        if prefix.startswith("/"):
                            dd_items = [(c,d) for c,d in COMMANDS if c.startswith(prefix)]
                            if not dd_items:
                                dd_items = COMMANDS
                            sys.stdout.write("\n")
                            for i,(cmd,desc) in enumerate(dd_items):
                                pad = 26-len(cmd)
                                marker = f"{BCYAN}>{RST}" if i==dd_sel else " "
                                sys.stdout.write(f"  {marker} {BCYAN}{cmd}{RST}{' '*max(1,pad)}{GRY}{desc}{RST}\n")
                            dd_lines = len(dd_items)
                            sys.stdout.flush()
                    continue

                # Escape sequence (ok tuşları)
                if ch == "\x1b":
                    nxt = sys.stdin.read(1)
                    if nxt == "[":
                        arr = sys.stdin.read(1)
                        if arr == "A":  # Yukarı ok
                            if dropdown and dd_items:
                                old_sel = dd_sel
                                dd_sel  = (dd_sel - 1) % len(dd_items)
                                # Sadece marker'ları güncelle
                                for _ in range(dd_lines):
                                    move_up(1); erase_line()
                                sys.stdout.write("\n")
                                for i,(cmd,desc) in enumerate(dd_items):
                                    pad    = 26-len(cmd)
                                    marker = f"{BCYAN}>{RST}" if i==dd_sel else " "
                                    sys.stdout.write(f"  {marker} {BCYAN}{cmd}{RST}{' '*max(1,pad)}{GRY}{desc}{RST}\n")
                                dd_lines = len(dd_items)
                                sys.stdout.flush()
                            else:
                                # Komut geçmişi
                                if self._input_hist:
                                    hist_idx = min(hist_idx+1, len(self._input_hist)-1)
                                    buf = list(self._input_hist[-(hist_idx+1)])
                                    line = "".join(buf)
                                    erase_line()
                                    sys.stdout.write(f"{BOLD}{BCYAN} >{RST} {BWHT}{line}{RST}")
                                    sys.stdout.flush()
                        elif arr == "B":  # Aşağı ok
                            if dropdown and dd_items:
                                dd_sel = (dd_sel + 1) % len(dd_items)
                                for _ in range(dd_lines):
                                    move_up(1); erase_line()
                                sys.stdout.write("\n")
                                for i,(cmd,desc) in enumerate(dd_items):
                                    pad    = 26-len(cmd)
                                    marker = f"{BCYAN}>{RST}" if i==dd_sel else " "
                                    sys.stdout.write(f"  {marker} {BCYAN}{cmd}{RST}{' '*max(1,pad)}{GRY}{desc}{RST}\n")
                                dd_lines = len(dd_items)
                                sys.stdout.flush()
                            else:
                                if hist_idx > 0:
                                    hist_idx -= 1
                                    buf = list(self._input_hist[-(hist_idx+1)])
                                else:
                                    hist_idx = -1
                                    buf = []
                                line = "".join(buf)
                                erase_line()
                                sys.stdout.write(f"{BOLD}{BCYAN} >{RST} {BWHT}{line}{RST}")
                                sys.stdout.flush()
                    continue

                # Ctrl+L = ekran temizle
                if ch == "\x0c":
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_term)
                    clr()
                    sys.stdout.write(f"{BOLD}{BCYAN} >{RST} ")
                    sys.stdout.flush()
                    tty.setraw(fd)
                    buf = []
                    dropdown = False
                    continue

                # Normal karakter
                if ch.isprintable():
                    buf.append(ch)
                    sys.stdout.write(f"{BWHT}{ch}{RST}")
                    sys.stdout.flush()

                    current = "".join(buf)

                    # / ile dropdown aç
                    if current == "/" or (current.startswith("/") and len(current) >= 1):
                        if not dropdown:
                            dropdown = True
                            dd_sel   = 0
                        else:
                            # Dropdown güncelle
                            for _ in range(dd_lines):
                                move_up(1); erase_line()

                        dd_items = [(c,d) for c,d in COMMANDS if c.startswith(current)]
                        if not dd_items:
                            dd_items = [(c,d) for c,d in COMMANDS]
                        dd_sel = min(dd_sel, len(dd_items)-1)
                        sys.stdout.write("\n")
                        for i,(cmd,desc) in enumerate(dd_items):
                            pad    = 26-len(cmd)
                            marker = f"{BCYAN}>{RST}" if i==dd_sel else " "
                            sys.stdout.write(f"  {marker} {BCYAN}{cmd}{RST}{' '*max(1,pad)}{GRY}{desc}{RST}\n")
                        dd_lines = len(dd_items)
                        sys.stdout.flush()
                    else:
                        # / ile başlamıyorsa dropdown kapat
                        if dropdown:
                            for _ in range(dd_lines):
                                move_up(1); erase_line()
                            dropdown = False
                            dd_lines = 0

        except Exception:
            pass
        finally:
            try:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_term)
            except Exception:
                pass

    # ── Onay promptu ─────────────────────────────────────────────────────────
    def ask(self, prompt: str, default="") -> str:
        """Blocking soru sor"""
        try:
            return input(f"\n{BOLD}{BCYAN} >{RST} {BWHT}{prompt}{RST} ").strip() or default
        except Exception:
            return default

    def confirm(self, prompt: str) -> bool:
        ans = self.ask(f"{prompt} (e/h)", "h")
        return ans.lower() in ("e","evet","y","yes")
