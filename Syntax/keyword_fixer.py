"""Syntax Fixer: Anahtar kelime çakışmalarını düzelt"""
import re, ast


def fix_keyword(code: str) -> str:
    """Anahtar kelime çakışmalarını düzelt"""
    try:
        ast.parse(code)
        return code
    except SyntaxError:
        pass
    return code.replace('\nprint\n', '\nprint_\n')
