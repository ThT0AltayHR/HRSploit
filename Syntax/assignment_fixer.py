"""Syntax Fixer: Atama ifadesi sorunları"""
import re, ast


def fix_assignment(code: str) -> str:
    """Atama ifadesi sorunları"""
    try:
        ast.parse(code)
        return code
    except SyntaxError:
        pass
    return re.sub(r'^(\s*)(\w+)\s*==\s*(.+)$', r'\1\2 = \3', code, flags=re.MULTILINE)
