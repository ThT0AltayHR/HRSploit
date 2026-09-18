"""Syntax Fixer: Generator ve yield ifade sorunları"""
import re, ast


def fix_yield(code: str) -> str:
    """Generator ve yield ifade sorunları"""
    try:
        ast.parse(code)
        return code
    except SyntaxError:
        pass
    return code.replace('yield from', 'yield from ')
