"""Syntax Fixer: F-string sözdizimi hatalarını düzelt"""
import re, ast


def fix_fstring(code: str) -> str:
    """F-string sözdizimi hatalarını düzelt"""
    try:
        ast.parse(code)
        return code
    except SyntaxError:
        pass
    return code.replace('{{}', '{{').replace('}}', '}}')
