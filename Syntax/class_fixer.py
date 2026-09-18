"""Syntax Fixer: Sınıf tanımı hatalarını düzelt"""
import re, ast


def fix_class(code: str) -> str:
    """Sınıf tanımı hatalarını düzelt"""
    try:
        ast.parse(code)
        return code
    except SyntaxError:
        pass
    return re.sub(r'class (\w+)\(\):', r'class \1:', code)
