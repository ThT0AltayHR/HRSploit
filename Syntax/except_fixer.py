"""Syntax Fixer: Except ifadesi Python2→3 dönüşümü"""
import re, ast


def fix_except(code: str) -> str:
    """Except ifadesi Python2→3 dönüşümü"""
    try:
        ast.parse(code)
        return code
    except SyntaxError:
        pass
    return re.sub(r'except (\w+),\s*(\w+):', r'except \1 as \2:', code)
