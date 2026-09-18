"""Syntax Fixer: With statement sorunları"""
import re, ast


def fix_with(code: str) -> str:
    """With statement sorunları"""
    try:
        ast.parse(code)
        return code
    except SyntaxError:
        pass
    return code
