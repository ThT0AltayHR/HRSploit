"""Syntax Fixer: Lambda ifade hatalarını düzelt"""
import re, ast


def fix_lambda(code: str) -> str:
    """Lambda ifade hatalarını düzelt"""
    try:
        ast.parse(code)
        return code
    except SyntaxError:
        pass
    return re.sub(r'lambda\s*:', 'lambda x:', code)
