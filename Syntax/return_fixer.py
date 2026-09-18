"""Syntax Fixer: Fonksiyon dışı return kaldır"""
import re, ast


def fix_return(code: str) -> str:
    """Fonksiyon dışı return kaldır"""
    try:
        ast.parse(code)
        return code
    except SyntaxError:
        pass
    return re.sub(r'^return\s+', '# return ', code, flags=re.MULTILINE)
