"""Syntax Fixer: Tip hatalarını ve geçersiz annotation'ları düzelt"""
import re, ast


def fix_type(code: str) -> str:
    """Tip hatalarını ve geçersiz annotation'ları düzelt"""
    try:
        ast.parse(code)
        return code
    except SyntaxError:
        pass
    return re.sub(r':\s*([A-Z]\w+)\s*=', r' =', code)
