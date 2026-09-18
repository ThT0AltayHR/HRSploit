"""Syntax Fixer: Decorator sözdizimi hatalarını düzelt"""
import re, ast


def fix_decorator(code: str) -> str:
    """Decorator sözdizimi hatalarını düzelt"""
    try:
        ast.parse(code)
        return code
    except SyntaxError:
        pass
    return re.sub(r'^@(\w+)\s*\n', r'@\1\n', code, flags=re.MULTILINE)
