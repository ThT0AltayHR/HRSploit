"""Satır sonu noktalı virgülleri ve çoklu statement'ları düzelt."""
import re

def fix_semicolons(code: str) -> str:
    lines = code.split("\n")
    fixed = []
    for line in lines:
        stripped = line.rstrip()
        # Satır sonundaki noktalı virgülü kaldır (string içinde değilse)
        if stripped.endswith(";") and not stripped.strip().startswith(("#","'",'"')):
            stripped = stripped[:-1]
        fixed.append(stripped)
    return "\n".join(fixed)
