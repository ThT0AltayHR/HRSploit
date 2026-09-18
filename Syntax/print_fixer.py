"""Python 2 print ifadelerini Python 3 fonksiyona çevir."""
import re

def fix_print_statements(code: str) -> str:
    # print "..." → print("...")
    # print x, y  → print(x, y)
    def _replace(m):
        indent = m.group(1)
        args   = m.group(2).strip()
        if args.startswith("("):
            return m.group(0)  # Zaten fonksiyon
        return f"{indent}print({args})"

    code = re.sub(r'^(\s*)print ([^(\n].+)$', _replace, code, flags=re.MULTILINE)
    return code
