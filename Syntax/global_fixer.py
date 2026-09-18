"""Syntax Fixer: Global/nonlocal ifade sorunları"""
import re, ast


def fix_global(code: str) -> str:
    """Global/nonlocal ifade sorunları"""
    try:
        ast.parse(code)
        return code
    except SyntaxError:
        pass
    return code
