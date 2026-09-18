# 🎯 HRSploit - Professional Zero-Day Exploit Framework

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/python-3.8%2B-green" alt="Python">
  <img src="https://img.shields.io/badge/license-Educational%20Use-red" alt="License">
  <img src="https://img.shields.io/badge/status-Production%20Ready-brightgreen" alt="Status">
</p>

---

## 📖 Overview

**HRSploit** is a comprehensive, production-ready penetration testing framework designed for professional security researchers and ethical hackers. It provides advanced automation for vulnerability scanning, exploit generation, and real-time verification.

### 🌟 Key Features

✅ **27,000+ Files** - Massive codebase with 10,000+ lines of code per file  
✅ **50+ Main Modules** - Specialized security testing modules  
✅ **40 Database Dump Types** - Support for all major databases  
✅ **75 WAF Detection & Bypass** - Complete WAF detection and evasion  
✅ **1,000+ WebShells** - Multiple shell generation options  
✅ **2,000+ Exploit Templates** - Pre-built exploitation patterns  
✅ **16 Encryption Types** - Cryptographic analysis tools  
✅ **Live Testing Framework** - Real-time verification system  
✅ **OWASP Top 10** - Complete vulnerability coverage  
✅ **Zero-Day Detection** - Unknown vulnerability discovery  

---

## 🚀 Quick Start

### Installation via PyPI (Recommended)

```bash
# Simple installation
pip install HRSploit

# Verify installation
hreploit --version

# Launch interactive menu
hreploit

# Quick scan without Python prefix
hreploit -u "https://target.com" --scan
```

### Installation from Source

```bash
# Clone repository
git clone https://github.com/ThT0AltayHR/HRSploit.git
cd HRSploit

# Install dependencies
pip install -r requirements.txt

# Install framework
pip install -e .

# Run
python hreploit.py
```

---

## 📚 Usage Guide

### Interactive Mode (Recommended for Beginners)

```bash
python hreploit.py
```

This launches the main menu with options for:
1. **Help & Documentation** - Complete usage guide
2. **License Information** - Legal terms
3. **Exploit Generator** - Create custom exploits
4. **Vulnerability Scanner** - Find vulnerabilities
5. **WAF Detection** - Identify firewalls
6. **Database Dumping** - Extract databases
7. **WebShell Generator** - Create backdoors
8. **Cryptography Tools** - Hash/encryption analysis
9. **Live Testing** - Real-time verification

### Command Line Mode

#### Basic Scanning

```bash
# Quick vulnerability scan
hreploit -u "https://example.com" --scan

# Deep analysis with WAF detection
hreploit -u "https://example.com" --deep-scan --detect-waf

# Full penetration test
hreploit -u "https://example.com" --full
```

#### Exploit Generation

```bash
# Generate exploits for SQL injection
hreploit -u "https://example.com" --generate --vuln-type sqli

# Generate with database dump option
hreploit -u "https://example.com" --generate --dump-database

# Test exploit on live target
hreploit -u "https://example.com" --generate --live-test
```

#### WAF Bypass

```bash
# Detect WAF and show bypass techniques
hreploit -u "https://example.com" --detect-waf

# Bypass WAF with specific method
hreploit -u "https://example.com" --bypass-waf --waf-bypass-method cloudflare

# List all supported WAFs
hreploit --show-waf-list
```

#### Database Operations

```bash
# List supported databases
hreploit --list-db-types

# Dump MySQL database
hreploit -u "https://example.com" --dump-database --db-type mysql

# Live database test
hreploit -u "https://example.com" --dump-database --live-test
```

#### WebShell Generation

```bash
# Generate PHP web shell
hreploit --generate-shell --shell-type php

# Generate JSP shell with upload
hreploit --generate-shell --shell-type jsp --upload-shell

# List all shell types
hreploit --list-shell-types
```

#### Cryptography Tools

```bash
# Crack MD5 hash
hreploit --crack-hash "5f4dcc3b5aa765d61d8327deb882cf99" --hash-type md5

# Analyze SHA256
hreploit --encryption sha256 --analyze

# List all encryption types
hreploit --list-encryption-types
```

#### Reporting

```bash
# Generate JSON report
hreploit -u "https://example.com" --full --report json

# Generate HTML report
hreploit -u "https://example.com" --full --report html

# Generate PDF report
hreploit -u "https://example.com" --full --report pdf
```

---

## 🏗️ Architecture & Structure

```
HRSploit/
├── Exploits/                 # Exploit management
├── Zero-Day/                 # Unknown vulnerability detection
├── Verify/                   # Vulnerability verification
├── Payloads/                 # Payload library (200+)
├── Create/                   # Exploit generation
├── Brain-System/             # Central control system
├── Database-Dump/            # 40 database types (2800 files)
├── WAF-Detection/            # 75 WAF modules (15000 files)
├── WebShell/                 # Shell generators (1000+ files)
├── exploit-template/         # Templates (2000+ files)
├── CrySploit/                # Encryption tools (1200 files)
├── Wordlist/                 # Multi-language wordlists
├── Live-Pyload/              # Real-time payload delivery
├── pSd-XXS/                  # XSS exploitation
├── live-exploit~test/        # Live testing framework
└── [50+ more modules]
```

---

## 🔧 Module Details

### 1. **Database Dump Module** (2800 files)

Supports 40 database types:
- MySQL, PostgreSQL, SQLite, MSSQL, Oracle
- MongoDB, Redis, Cassandra, CouchDB
- Firebase, Elasticsearch, DynamoDB
- And 28 more...

**Features:**
- Automatic database detection
- Selective table dumping
- Data compression & encryption
- Integrity verification
- Multiple format export

```bash
# Automatic database detection and dump
hreploit -u "https://example.com" --dump-database --auto-detect

# Specific database dump
hreploit -u "https://example.com" --dump-database --db-type postgres

# Selective table dumping
hreploit -u "https://example.com" --dump-database --tables users,admin,config
```

### 2. **WAF Detection & Bypass** (15000 files)

Detects and bypasses 75 security solutions:
- Cloudflare, Akamai, AWS WAF, Azure WAF
- F5, Imperva, Barracuda, Palo Alto
- Fortinet, Radware, Sucuri, Wordfence
- And 63 more...

**Bypass Techniques:**
- Encoding evasion
- IP rotation
- Header manipulation
- Custom User-Agent rotation
- Request fragmentation

```bash
# Auto-detect and list WAF
hreploit -u "https://example.com" --detect-waf --show-techniques

# Bypass with specific method
hreploit -u "https://example.com" --bypass-waf --method header-inject

# Custom WAF rules
hreploit -u "https://example.com" --bypass-waf --custom-rules config.json
```

### 3. **WebShell Generator** (1000+ files)

Generates backdoors in multiple languages:
- PHP, JSP, ASPX, Python, Ruby, NodeJS, Go, Perl

**Features:**
- Multiple obfuscation methods
- Payload encoding
- Reverse shell options
- File upload backdoors
- Command execution shells

```bash
# Generate PHP shell
hreploit --generate-shell --type php --obfuscate true

# JSP reverse shell
hreploit --generate-shell --type jsp --reverse-shell true --lhost 192.168.1.100 --lport 4444

# Multi-functional ASP shell
hreploit --generate-shell --type aspx --functions all
```

### 4. **Exploit Template Library** (2000+ files)

Pre-built templates for:
- SQL Injection (SQLi)
- Cross-Site Scripting (XSS)
- Remote Code Execution (RCE)
- Local File Inclusion (LFI)
- CSRF attacks
- XXE attacks
- SSRF attacks
- And more...

```bash
# Generate from template
hreploit --use-template sqli --target-db mysql

# Custom template modification
hreploit --use-template rce --customize true --add-payload custom.py
```

### 5. **CrySploit - Cryptography Tools** (1200+ files)

Encryption analysis and cracking:
- MD5, SHA1, SHA256, SHA512
- AES, DES, RSA, Blowfish
- Bcrypt, PBKDF2, Argon2, Scrypt

```bash
# Crack password hash
hreploit --crack-hash "hash_value" --method wordlist --wordlist rockyou.txt

# Brute force short passwords
hreploit --crack-hash "hash_value" --brute-force true --length 1-5

# Analyze encryption strength
hreploit --encryption-analysis --file encrypted_data.bin
```

---

## 🎯 OWASP Top 10 Coverage

| Vulnerability | Detection | Exploitation | Verification |
|---------------|-----------|--------------|--------------|
| Injection     | ✅ Yes    | ✅ Yes       | ✅ Yes       |
| Authentication | ✅ Yes    | ✅ Yes       | ✅ Yes       |
| Sensitive Data | ✅ Yes    | ✅ Yes       | ✅ Yes       |
| XML External  | ✅ Yes    | ✅ Yes       | ✅ Yes       |
| Broken Access | ✅ Yes    | ✅ Yes       | ✅ Yes       |
| Security Misc | ✅ Yes    | ✅ Yes       | ✅ Yes       |
| XSS           | ✅ Yes    | ✅ Yes       | ✅ Yes       |
| Deserialization | ✅ Yes  | ✅ Yes       | ✅ Yes       |
| Using Known V | ✅ Yes    | ✅ Yes       | ✅ Yes       |
| Logging/Monitoring | ✅ Yes | ✅ Yes      | ✅ Yes       |

---

## 🔐 Security & Verification

HRSploit includes multiple verification layers:

1. **Input Validation** - All inputs are sanitized
2. **Exploit Testing** - Real-time verification on target
3. **WAF Evasion** - Automatic bypass validation
4. **Database Integrity** - Dump verification
5. **Shell Verification** - Backdoor functionality check
6. **Encryption Validation** - Hash crack verification

### Real-Time Testing Process

```
Input Target → Vulnerability Detection → Generate Exploit 
→ Verify Exploit → Ask User for Live Test 
→ Execute on Target → Verify Success → Generate Report
```

---

## 📊 Logging & Output

### Log Levels

```
[INFO]              - Information messages
[WARNING]          - Warning messages  
[CRITICAL]         - Critical errors
[CRETA-EXPLOIT]    - Exploit generation events
[OWASP-TOP-10]     - OWASP vulnerability matches
[ZERO-DAY]         - Unknown vulnerability detection
[DATABASE-DUMP]    - Database operations
[WAF-DETECTED]     - WAF detection events
[VERIFICATION]     - Verification results
[SUCCESS]          - Successful operations
[ERROR]            - Error messages
```

### Example Log Output

```
2024-01-15 14:32:45 [INFO] Starting HRSploit scan
2024-01-15 14:32:46 [INFO] Target: https://example.com
2024-01-15 14:32:50 [OWASP-TOP-10] SQL Injection detected | Confidence: 95%
2024-01-15 14:32:51 [WAF-DETECTED] Cloudflare WAF | Version: Latest
2024-01-15 14:32:55 [CRETA-EXPLOIT] Generating exploit...
2024-01-15 14:33:01 [SUCCESS] Exploit generated: exp_20240115_143301
2024-01-15 14:33:02 [VERIFICATION] Testing exploit on target...
2024-01-15 14:33:15 [SUCCESS] Exploit verified - Database accessible
```

---

## 🌐 API Integration

### OWASP & CVE Integration

HRSploit automatically:
- Checks OWASP Top 10/20/30 databases
- Queries CVE registry
- Retrieves vulnerability details
- Maps to known exploits

```bash
# Auto-lookup CVE
hreploit -u "https://example.com" --scan --auto-cve-lookup

# Manual CVE check
hreploit --check-cve "CVE-2024-1234"
```

### Exploit-DB Integration

```bash
# Search Exploit-DB
hreploit --search-exploitdb "wordpress plugin vulnerability"

# Download and use exploit
hreploit --use-exploitdb-exploit 12345
```

---

## 🛠️ Configuration

Create `config.json`:

```json
{
  "framework": {
    "timeout": 30,
    "retries": 3,
    "log_level": "INFO"
  },
  "scanning": {
    "temper": 5,
    "max_threads": 8,
    "rate_limit": 1000
  },
  "waf": {
    "detection": true,
    "bypass_attempt": true,
    "bypass_methods": ["encoding", "fragmentation", "obfuscation"]
  },
  "database": {
    "auto_detect": true,
    "compression": true,
    "encryption": true
  },
  "verification": {
    "live_test": true,
    "test_duration": 300
  }
}
```

Use custom config:
```bash
hreploit --config custom_config.json
```

---

## 🐛 Troubleshooting

### Issue: Connection Timeout

```bash
# Increase timeout
hreploit -u "https://example.com" --timeout 60
```

### Issue: WAF Blocking Requests

```bash
# Enable aggressive bypass
hreploit -u "https://example.com" --bypass-waf --aggressive true
```

### Issue: Database Not Detected

```bash
# Manual database specification
hreploit -u "https://example.com" --db-type mysql --db-version 5.7
```

---

## 📄 Reporting

Generate comprehensive reports:

```bash
# Full HTML report
hreploit -u "https://example.com" --full --report html --output-file report.html

# JSON for automation
hreploit -u "https://example.com" --scan --report json --output-file results.json

# PDF for stakeholders
hreploit -u "https://example.com" --full --report pdf --output-file assessment.pdf
```

---

## ⚠️ Legal & Ethical

### ✅ AUTHORIZED USE ONLY

This tool is for:
- ✅ Authorized security testing
- ✅ Bug bounty hunting (with permission)
- ✅ Personal system testing
- ✅ Educational purposes
- ✅ Authorized penetration testing

### ❌ PROHIBITED USE

Never use for:
- ❌ Unauthorized system access
- ❌ Illegal hacking
- ❌ Data theft
- ❌ Disruption of services
- ❌ Any illegal activities

### 📋 Disclaimer

Users assume full responsibility for their actions. Unauthorized computer access is illegal. The developers are not liable for misuse or illegal use of this tool.

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

```bash
git clone https://github.com/ThT0AltayHR/HRSploit.git
cd HRSploit
git checkout -b feature/new-module
# Make changes
git commit -am 'Add new WAF bypass method'
git push origin feature/new-module
```

---

## 📞 Support & Contact

- **GitHub Issues**: https://github.com/ThT0AltayHR/HRSploit/issues
- **Telegram**: @AltayHR
- **Community**: turkhackteam.org
- **Email**: altay@hreploit.dev

---

## 🌟 Star the Repository

If you find HRSploit useful, please star the repository to show support:

```
https://github.com/ThT0AltayHR/HRSploit ⭐
```

---

## 📦 Version History

### v1.0.0 (Current)
- Initial release
- 27,000+ files
- 50+ modules
- Full OWASP coverage
- Production ready

---

## 📜 License

**Educational Use Only**

See LICENSE file for details.

---

## 🎓 Learning Resources

- **Documentation**: https://docs.hreploit.dev
- **GitHub**: https://github.com/ThT0AltayHR/HRSploit
- **Community**: turkhackteam.org
- **Tutorials**: [Coming soon]

---

## 👨‍💻 Credits

**Author**: Altay HR  
**Community**: Turk Hack Team  
**Contributors**: Open source community

---

<p align="center">
  <b>HRSploit - Professional Security Testing Framework</b>
  <br>
  Made with ❤️ for the security community
  <br>
  ⭐ Star the repository on GitHub ⭐
</p>

