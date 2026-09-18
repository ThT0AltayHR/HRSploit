"""Syntax Fixer: Assert ifadesi sorunları"""
import re, ast


def fix_assert(code: str) -> str:
    """Assert ifadesi sorunları"""
    try:
        ast.parse(code)
        return code
    except SyntaxError:
        pass
    return re.sub(r'assert (.*),(.*)', r'assert \1, \2', code)
