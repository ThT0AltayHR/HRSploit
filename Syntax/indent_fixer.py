"""Girinti (indentation) hatalarını düzelt."""
import re

def fix_indent(code: str) -> str:
    lines = code.split("\n")
    fixed = []
    for line in lines:
        # Tab → 4 boşluk
        if "\t" in line:
            line = line.expandtabs(4)
        # Karışık boşluk temizle (satır başında sadece 4'ün katları)
        stripped = line.lstrip(" ")
        spaces   = len(line) - len(stripped)
        remainder = spaces % 4
        if remainder != 0:
            spaces -= remainder  # en yakın 4'e yuvarla aşağı
        fixed.append(" " * spaces + stripped)
    return "\n".join(fixed)
