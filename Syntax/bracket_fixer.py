"""Syntax Fixer: Kapanmamış parantez/köşeli parantez/küme"""
import re, ast


def fix_bracket(code: str) -> str:
    """Kapanmamış parantez/köşeli parantez/küme"""
    try:
        ast.parse(code)
        return code
    except SyntaxError:
        pass
    opens  = {'(':')', '[':']', '{':'}'}
    stack  = []
    for ch in code:
        if ch in opens:   stack.append(opens[ch])
        elif ch in ')}]' and stack and stack[-1]==ch: stack.pop()
    code = code.rstrip()
    for close in reversed(stack): code += close
    return code
