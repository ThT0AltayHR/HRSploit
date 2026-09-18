"""Syntax Fixer: Karşılaştırma ifadesi sorunları"""
import re, ast


def fix_comparison(code: str) -> str:
    """Karşılaştırma ifadesi sorunları"""
    try:
        ast.parse(code)
        return code
    except SyntaxError:
        pass
    return re.sub(r'\bis\s+not\s+None\b', 'is not None', code)
