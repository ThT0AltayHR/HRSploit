"""Geçersiz escape dizilerini düzelt: \d \w \s → raw string veya double-backslash."""
import re, ast

def fix_escapes(code: str) -> str:
    # Sadece SyntaxWarning değil, gerçek SyntaxError'lara neden olanları yakala
    # Normal string literal içindeki \d \w \s → \\d \\w \\s
    def _fix_str_literal(m):
        quote = m.group(1)
        body  = m.group(2)
        # Zaten raw mı?
        if quote.startswith(('r','R')):
            return m.group(0)
        bad = re.search(r'\\[dDwWsS]', body)
        if bad:
            # r prefix ekle
            return "r" + m.group(0)
        return m.group(0)

    # Tek tırnak string'ler
    code = re.sub(r'(\")((?:[^\"\\]|\\.)*)\"', _fix_str_literal, code)
    return code
