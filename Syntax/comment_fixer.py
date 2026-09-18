"""Syntax Fixer: Bozuk yorum satırlarını temizle"""
import re, ast


def fix_comment(code: str) -> str:
    """Bozuk yorum satırlarını temizle"""
    try:
        ast.parse(code)
        return code
    except SyntaxError:
        pass
    return re.sub(r'^(\s*)###+', r'\1#', code, flags=re.MULTILINE)
