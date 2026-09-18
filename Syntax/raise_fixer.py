"""Syntax Fixer: Raise ifadesi Python2→3"""
import re, ast


def fix_raise(code: str) -> str:
    """Raise ifadesi Python2→3"""
    try:
        ast.parse(code)
        return code
    except SyntaxError:
        pass
    return re.sub(r'raise (\w+),\s*(.+)', r'raise \1(\2)', code)
