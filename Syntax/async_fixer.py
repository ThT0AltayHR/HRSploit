"""Syntax Fixer: Async/await sözdizimi sorunları"""
import re, ast


def fix_async(code: str) -> str:
    """Async/await sözdizimi sorunları"""
    try:
        ast.parse(code)
        return code
    except SyntaxError:
        pass
    return re.sub(r'async def (\w+)\(', r'def \1(', code)
