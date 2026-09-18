"""Syntax Fixer: Unicode karakter sorunları"""
import re, ast


def fix_unicode(code: str) -> str:
    """Unicode karakter sorunları"""
    try:
        ast.parse(code)
        return code
    except SyntaxError:
        pass
    return code.encode('ascii','replace').decode('ascii')
