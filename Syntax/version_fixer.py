"""Syntax Fixer: Python versiyon uyumluluk sorunları"""
import re, ast


def fix_version(code: str) -> str:
    """Python versiyon uyumluluk sorunları"""
    try:
        ast.parse(code)
        return code
    except SyntaxError:
        pass
    return code.replace('print_function','').replace('unicode_literals','')
