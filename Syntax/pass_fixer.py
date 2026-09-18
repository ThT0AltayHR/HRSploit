"""Syntax Fixer: Boş blok sorunları (eksik pass ekle)"""
import re, ast


def fix_pass(code: str) -> str:
    """Boş blok sorunları (eksik pass ekle)"""
    try:
        ast.parse(code)
        return code
    except SyntaxError:
        pass
    lines = code.split('\n')
    fixed = []
    for i, line in enumerate(lines):
        fixed.append(line)
        if line.rstrip().endswith(':'):
            # Sonraki satır boş veya yoksa pass ekle
            nxt = lines[i+1].strip() if i+1 < len(lines) else ''
            if not nxt or nxt.startswith('#'):
                fixed.append(' ' * (len(line) - len(line.lstrip()) + 4) + 'pass')
    code = '\n'.join(fixed)
    return code
