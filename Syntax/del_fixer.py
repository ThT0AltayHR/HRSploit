"""Syntax Fixer: Del ifadesi sorunları"""
import re, ast


def fix_del(code: str) -> str:
    """Del ifadesi sorunları"""
    try:
        ast.parse(code)
        return code
    except SyntaxError:
        pass
    return code
