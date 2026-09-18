"""Eksik ve bozuk import ifadelerini düzelt."""
import re

COMMON_IMPORTS = {
    "requests":  "import requests",
    "json":      "import json",
    "time":      "import time",
    "os":        "import os",
    "sys":       "import sys",
    "re":        "import re",
    "socket":    "import socket",
    "subprocess":"import subprocess",
    "threading": "import threading",
    "pathlib":   "from pathlib import Path",
    "datetime":  "from datetime import datetime",
    "hashlib":   "import hashlib",
    "base64":    "import base64",
    "random":    "import random",
    "typing":    "from typing import Dict, List, Optional, Tuple",
}

def fix_imports(code: str) -> str:
    existing = set(re.findall(r'^(?:import|from)\s+(\w+)', code, re.MULTILINE))
    missing  = []
    for mod, stmt in COMMON_IMPORTS.items():
        if mod not in existing and re.search(rf'\b{re.escape(mod)}\b', code):
            missing.append(stmt)
    if missing:
        header = "\n".join(missing) + "\n"
        # Mevcut import bloğunun sonuna ekle
        m = re.search(r'^(?:import|from)\s+\w+[^\n]*\n', code, re.MULTILINE)
        if m:
            pos = code.rfind('\n', 0, m.end()) + 1
            code = code[:pos] + header + code[pos:]
        else:
            code = header + code
    return code
