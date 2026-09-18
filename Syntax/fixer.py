"""SyntaxFixer — tek dosya veya string üzerinde tüm fixerleri çalıştırır."""
import ast
from pathlib import Path
from typing import Optional

from .str_fixer       import fix_strings
from .import_fixer    import fix_imports
from .indent_fixer    import fix_indent
from .escape_fixer    import fix_escapes
from .trailing_fixer  import fix_trailing
from .encoding_fixer  import fix_encoding
from .docstring_fixer import fix_docstrings
from .blank_fixer     import fix_blank_lines
from .semicolon_fixer import fix_semicolons
from .print_fixer     import fix_print_statements
from .octal_fixer     import fix_octal_literals

ALL_FIXERS = [
    fix_encoding, fix_escapes, fix_strings, fix_docstrings,
    fix_print_statements, fix_octal_literals, fix_indent,
    fix_semicolons, fix_trailing, fix_blank_lines, fix_imports,
]


class SyntaxFixer:
    def fix_code(self, code: str, max_rounds: int = 5) -> tuple:
        """(fixed_code, ok: bool, applied_fixes: list)"""
        applied = []
        for _ in range(max_rounds):
            try:
                ast.parse(code)
                return code, True, applied
            except SyntaxError:
                for fn in ALL_FIXERS:
                    new = fn(code)
                    if new != code:
                        applied.append(fn.__name__)
                        code = new
        try:
            ast.parse(code)
            return code, True, applied
        except SyntaxError:
            return code, False, applied

    def fix_file(self, path: Path) -> dict:
        path = Path(path)
        try:
            code = path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            return {"ok": False, "error": str(e)}
        fixed, ok, fixes = self.fix_code(code)
        if ok and fixes:
            path.write_text(fixed, encoding="utf-8")
        return {"ok": ok, "fixes": fixes, "path": str(path)}
