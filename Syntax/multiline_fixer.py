"""Syntax Fixer: Çok satırlı ifade sorunları"""
import re, ast


def fix_multiline(code: str) -> str:
    """Çok satırlı ifade sorunları"""
    try:
        ast.parse(code)
        return code
    except SyntaxError:
        pass
    return re.sub(r'\\\n\s+', ' ', code)
