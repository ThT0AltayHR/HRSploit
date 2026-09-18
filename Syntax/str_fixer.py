"""Kapatılmamış string ve triple-quote literal'larını düzelt."""
import re


def fix_strings(code: str) -> str:
    # 1. Bozuk triple-quote suffix: '""r"' → '"""'
    code = code.replace('""r"', '"""')
    code = code.replace("''r'", "'''")

    # 2. Çift tırnak sayısı tek ise sona ekle
    lines = code.split("\n")
    new_lines = []
    in_triple_dq = False
    in_triple_sq = False

    for line in lines:
        # Triple quote geçişlerini say
        dq_count = line.count('"""')
        sq_count = line.count("'''")
        if dq_count % 2 != 0:
            in_triple_dq = not in_triple_dq
        if sq_count % 2 != 0:
            in_triple_sq = not in_triple_sq
        new_lines.append(line)

    # Eğer hâlâ açık triple var kapat
    result = "\n".join(new_lines)
    if in_triple_dq:
        result = result.rstrip() + '\n"""\n'
    if in_triple_sq:
        result = result.rstrip() + "\n'''\n"

    return result
