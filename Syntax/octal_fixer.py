"""Python 2 octal literal'larını düzelt: 0755 → 0o755."""
import re

def fix_octal_literals(code: str) -> str:
    # 0[0-7]+ → 0o[0-7]+
    def _replace(m):
        val = m.group(0)
        # Zaten 0o/0x/0b/0B mi?
        if re.match(r'0[oObBxX]', val):
            return val
        digits = val[1:]
        if all(c in '01234567' for c in digits) and len(digits) >= 2:
            return '0o' + digits
        return val

    code = re.sub(r'\b0\d+\b', _replace, code)
    return code
