"""Syntax Fixer: Exec Python2→3: exec 'x' → exec('x')"""
import re, ast


def fix_exec(code: str) -> str:
    """Exec Python2→3: exec 'x' → exec('x')"""
    try:
        ast.parse(code)
        return code
    except SyntaxError:
        pass
    return re.sub(r"^(\s*)exec\s+(['\"][^'\"]+['\"])", r"\1exec(\2)", code, flags=re.MULTILINE)
