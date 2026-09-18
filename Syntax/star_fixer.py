"""Syntax Fixer: Starred expression sorunları"""
import re, ast


def fix_star(code: str) -> str:
    """Starred expression sorunları"""
    try:
        ast.parse(code)
        return code
    except SyntaxError:
        pass
    return code
