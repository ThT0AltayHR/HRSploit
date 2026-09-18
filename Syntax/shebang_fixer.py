"""Syntax Fixer: Shebang satırı kontrolü"""
import re, ast


def fix_shebang(code: str) -> str:
    """Shebang satırı kontrolü"""
    try:
        ast.parse(code)
        return code
    except SyntaxError:
        pass
    return code if code.startswith('#!') else code
