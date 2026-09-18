"""Satır sonu boşlukları ve Windows satır sonlarını temizle."""

def fix_trailing(code: str) -> str:
    lines = code.split("\n")
    fixed = [line.rstrip() for line in lines]
    # Dosya sonu boş satır garantisi
    while fixed and not fixed[-1].strip():
        fixed.pop()
    fixed.append("")
    return "\n".join(fixed)
