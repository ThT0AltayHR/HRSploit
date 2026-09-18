"""Syntax Fixer: Operatör hatalarını düzelt"""
import re, ast


def fix_operator(code: str) -> str:
    """Operatör hatalarını düzelt"""
    try:
        ast.parse(code)
        return code
    except SyntaxError:
        pass
    return re.sub(r'<>', '!=', code)
