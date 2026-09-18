"""Bozuk docstring'leri düzelt."""
import re

def fix_docstrings(code: str) -> str:
    # '""r"' ve '""r"' pattern'larını düzelt (önceki araçtan kalan)
    code = re.sub(r'"""([^"]*)""r"', r'"""\1"""', code)
    code = re.sub(r"'''([^']*)''r'", r"'''\1'''", code)
    # f-string içindeki triple quote sorunu
    code = code.replace('f"""', '"""').replace("f'''", "'''")
    return code
