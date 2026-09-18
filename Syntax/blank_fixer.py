"""PEP8: üst seviye tanımlar arası 2 boş satır, method'lar arası 1."""
import re

def fix_blank_lines(code: str) -> str:
    # 4'ten fazla ardışık boş satırı 2'ye indir
    code = re.sub(r'\n{5,}', '\n\n\n', code)
    return code
