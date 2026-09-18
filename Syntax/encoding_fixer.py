"""Encoding sorunlarını düzelt: BOM, null byte, geçersiz UTF-8."""

def fix_encoding(code: str) -> str:
    # BOM kaldır
    code = code.lstrip("\ufeff")
    # Null byte kaldır
    code = code.replace("\x00", "")
    # Windows CRLF → LF
    code = code.replace("\r\n", "\n").replace("\r", "\n")
    return code
