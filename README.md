# HRSploit v1.0.0 - Professional Zero-Day Exploit Framework

#turkhackteam.org

@İnstall

https://pypi.org/project/HRSploit/?replit_sid=61715864-8ed1-41bd-b5e8-1584ad75e1be

https://github.com/ThT0AltayHR/HRSploit.git

#pip install HRSploit
![Version](https://img.shields.io/badge/version-1.0.0-brightgreen) ![License](https://img.shields.io/badge/license-MIT-blue) ![Status](https://img.shields.io/badge/status-Production-green)

## Overview

**HRSploit** is a comprehensive, multi-engine penetration testing framework that integrates industry-standard security tools into a unified, intelligent system. Designed for professional security researchers and authorized penetration testers.

### Integrated Tools (7 Engines)

| Tool | Purpose | Integration |
|------|---------|-------------|
| **XSStrike** | XSS fuzzing, DOM analysis, filter bypass | XSS-Injector module |
| **sqlmap** | SQL injection detection & database extraction | SQLi-Injector, All-SQL, Database-Dump modules |
| **waf-bypass** | WAF evasion payload generation | WAF-Detection, Evasion modules |
| **wafw00f** | WAF fingerprinting (70+ signatures) | WAF-Detection module |
| **CrackAdmin v2** | Admin panel brute-force with dork discovery | Brute-Force, Dictionary-Attack modules |
| **checkhost** | Multi-node host reachability checking | Network-Analysis, Reconnaissance modules |
| **Metasploit MSF** | Exploit modules, payloads, post-exploitation | Exploits, Payload-Generator, Post-Exploitation modules |

---

## Installation

### Requirements
- Python 3.8+
- pip
- Git

### Quick Start

```bash
# Clone or extract HRSploit
cd HRSploit

# Install dependencies
pip install -r requirements.txt

# Run interactive menu
python HRSploit.py

# Run with target
python HRSploit.py -u https://target.com --scan

# Full auto mode (all 10 phases)
python HRSploit.py --auto -u https://target.com --report html
```

---

## Usage

### Interactive Menu (Beginners)

```bash
python HRSploit.py
```

Launches the full interactive menu with 15 options:
- 1. Vulnerability Scanner
- 2. WAF Detection & Bypass
- 3. XSS Attack
- 4. SQL Injection
- 5. Admin Brute-Force
- 6. Exploit Generator
- 7. Payload Generator
- 8. WebShell Generator
- 9. Network & Recon
- 10. Cryptography Tools
- 11. Post-Exploitation
- 12. Report Generator
- 13. Auto Mode (full pentest)
- 14. Help & Documentation
- 15. About & Credits

### Command Line (Advanced)

#### Help
```bash
python HRSploit.py -h              # Short help (command list)
python HRSploit.py --help          # Full help with examples
python HRSploit.py --about         # Integrated tools info
python HRSploit.py --version       # Version info
```

#### Target Specification
```bash
python HRSploit.py -u https://target.com         # Single URL
python HRSploit.py --target-list targets.txt     # Multiple URLs
```

#### Scanning & Detection
```bash
python HRSploit.py -u https://target.com --scan          # Quick scan
python HRSploit.py -u https://target.com --deep-scan     # Deep analysis
python HRSploit.py -u https://target.com --detect-waf    # WAF detection
python HRSploit.py -u https://target.com --bypass-waf    # WAF bypass
python HRSploit.py -u https://target.com --show-waf-list # List WAFs
```

#### Exploitation
```bash
python HRSploit.py -u https://target.com --xss           # XSS scan (XSStrike)
python HRSploit.py -u https://target.com --sqli          # SQLi scan (sqlmap)
python HRSploit.py -u https://target.com --dump-database # DB dump
python HRSploit.py -u https://target.com --brute-admin   # Admin brute-force
python HRSploit.py -u https://target.com --generate      # Generate exploits
python HRSploit.py -u https://target.com --test          # Test exploits
python HRSploit.py -u https://target.com --live-test     # Live verification
```

#### Database Operations
```bash
python HRSploit.py -u https://target.com --dump-database --db-type mysql
python HRSploit.py --list-db-types                       # Show DB types
```

#### Payload & Exploit Generation
```bash
python HRSploit.py --msf-payload windows/meterpreter/reverse_tcp
python HRSploit.py --msf-payload linux/x86/shell_reverse_tcp
python HRSploit.py --list-payloads                       # List all payloads
python HRSploit.py --list-exploits                       # List all exploits
```

#### WebShell
```bash
python HRSploit.py -u https://target.com --generate-shell --shell-type php
python HRSploit.py --generate-shell --shell-type aspx
```

#### Network & Reconnaissance
```bash
python HRSploit.py -u https://target.com --network-check # Reachability check
python HRSploit.py -u https://target.com --port-scan     # Port scanner
python HRSploit.py -u https://target.com --recon         # Full recon
```

#### Reporting
```bash
python HRSploit.py -u https://target.com --full --report html
python HRSploit.py -u https://target.com --full --report json --output results.json
python HRSploit.py -u https://target.com --full --report pdf
```

#### Auto Mode (10-Phase Full Pentest)
```bash
python HRSploit.py --auto -u https://target.com
python HRSploit.py --auto -u https://target.com --report html
```

**Auto Mode Phases:**
1. Network Reachability (checkhost)
2. WAF Detection (wafw00f)
3. WAF Bypass Preparation (waf-bypass)
4. Vulnerability Scan
5. XSS Attack (XSStrike)
6. SQL Injection (sqlmap)
7. Admin Brute-Force (CrackAdmin v2)
8. Exploit Generation (Metasploit)
9. Live Verification
10. Report Generation

---

## Example Workflows

### 1. Basic Vulnerability Scan
```bash
python HRSploit.py -u https://example.com --scan
```

### 2. WAF Detection + Bypass + XSS
```bash
python HRSploit.py -u https://example.com --detect-waf --bypass-waf --xss
```

### 3. SQLi with Database Dump
```bash
python HRSploit.py -u https://example.com --sqli --dump-database --db-type mysql
```

### 4. Admin Brute-Force with Custom Wordlist
```bash
python HRSploit.py -u https://example.com --brute-admin --wordlist rockyou.txt --brute-user admin
```

### 5. Generate MSF Payload
```bash
python HRSploit.py --msf-payload linux/x86/shell_reverse_tcp
```

### 6. Full Auto Pentest + HTML Report
```bash
python HRSploit.py --auto -u https://example.com --report html
```

### 7. Network Recon + Port Scan
```bash
python HRSploit.py -u https://example.com --network-check --port-scan --recon
```

### 8. Brute-Force + Exploit + Verify
```bash
python HRSploit.py -u https://example.com --brute-admin --generate --live-test
```

---

## Output & Reports

HRSploit generates outputs in multiple formats:

### Directory Structure
```
HRSploit/
├── reports/              # Generated reports (JSON, HTML, PDF, TXT)
├── generated_exploits/   # Exploit packages and shells
├── payloads_custom/      # Custom-generated payloads
├── wordlists/            # Wordlist files
├── cve_database/         # CVE data
└── hrsploit_session.log  # Session log file
```

### Report Formats
- **JSON**: Structured vulnerability data
- **HTML**: Web-viewable interactive report
- **PDF**: Professional printable format
- **TXT**: Plain text summary

---

## Supported WAF Products (70+)

Cloudflare, Akamai, F5 BIG-IP, Imperva, Citrix Netscaler, ModSecurity, Palo Alto, Fortinet, Checkpoint, AWS WAF, Azure WAF, Barracuda, SonicWall, Sophos, Watchguard, pfSense, Endian, and many more.

---

## Supported Databases

- MySQL / MariaDB
- PostgreSQL
- Microsoft SQL Server
- Oracle
- MongoDB
- SQLite
- Cassandra
- Redis

---

## Threat Model & Scope

HRSploit is designed for:
- ✅ Authorized penetration testing
- ✅ Security research & education
- ✅ Vulnerability assessment (with permission)
- ✅ Red team exercises (authorized)

⚠️ **Legal Notice**: Unauthorized testing is ILLEGAL. Always obtain written permission before testing any system. Users are responsible for all misuse.

---

## Architecture

### Brain System Integration
All modules are connected through the Brain System, which:
- Coordinates between engines
- Manages shared vulnerability data
- Handles payload encoding/obfuscation
- Logs all operations
- Generates comprehensive reports
- Implements error handling & verification

### Module Architecture
```
HRSploit/
├── Brain-System/           # Intelligence & coordination
├── Vulnerability modules/  # Scanner, detector engines
├── Exploitation modules/   # Exploit & payload generators
├── Evasion modules/       # WAF bypass, obfuscation
├── Post-Exploitation/     # Lateral movement, persistence
├── Network modules/       # Recon, scanning, analysis
└── Utility modules/       # Encoding, cryptography, reporting
```

---

## Credits & Acknowledgments

HRSploit integrates and enhances these excellent open-source projects:

- **XSStrike** - XSS vulnerability scanner
- **sqlmap** - SQL injection tool
- **waf-bypass** - WAF evasion engine
- **wafw00f** - WAF fingerprinting tool
- **CrackAdmin v2** - Admin panel brute-force
- **checkhost** - Host reachability checker
- **Metasploit Framework** - Exploit framework

---

## Support & Community

- **GitHub**: https://github.com/ThT0AltayHR/HRSploit
- **Issues**: https://github.com/ThT0AltayHR/HRSploit/issues
- **Community**: turkhackteam.org
- **Telegram**: @AltayHR

---

## License

MIT License - See LICENSE file for details

---

## Disclaimer

**⚠️ LEGAL NOTICE**

HRSploit is provided for authorized security testing and educational purposes ONLY. Unauthorized access to computer systems is ILLEGAL and punishable by law. 

- Users must have written authorization before testing any system
- The authors assume NO liability for misuse or illegal use
- Users assume ALL responsibility for their actions
- Always comply with applicable laws and regulations

---

**Version**: 1.0.0  
**Updated**: 2026-09-12  
**Author**: Altay HR  
**Status**: Production Ready
