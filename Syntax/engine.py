"""
SyntaxEngine — Merkezi koordinatör.
Bir dizini (örn. tools/<exploit>/) tarar, her .py dosyasını düzeltir ve test eder.
"""
import ast, time, subprocess, sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

from .fixer       import SyntaxFixer
from .tester      import CodeTester
from .report      import SyntaxReport
from .str_fixer   import fix_strings
from .import_fixer import fix_imports
from .indent_fixer import fix_indent
from .escape_fixer import fix_escapes
from .trailing_fixer import fix_trailing
from .encoding_fixer import fix_encoding
from .docstring_fixer import fix_docstrings
from .blank_fixer import fix_blank_lines
from .semicolon_fixer import fix_semicolons
from .print_fixer import fix_print_statements
from .octal_fixer import fix_octal_literals


MAX_ROUNDS = 5   # Her dosya için maksimum düzeltme turu

class SyntaxEngine:
    """Tek noktadan syntax denetleme + otomatik düzeltme + test sistemi."""

    FIXERS = [
        fix_encoding,        # Encoding hataları
        fix_escapes,         # Geçersiz escape dizileri
        fix_strings,         # Kapatılmamış string/triple-quote
        fix_docstrings,      # Bozuk docstring'ler
        fix_print_statements,# Python 2 print ifadeleri
        fix_octal_literals,  # 0700 → 0o700
        fix_indent,          # Girinti hataları
        fix_semicolons,      # Satır sonu noktalı virgül
        fix_trailing,        # Boşluk ve satır sonu sorunları
        fix_blank_lines,     # Gereksiz boş satırlar
        fix_imports,         # Eksik/bozuk import'lar
    ]

    def __init__(self, base_path: Path = None):
        self.base   = base_path or Path.cwd()
        self.fixer  = SyntaxFixer()
        self.tester = CodeTester()
        self.report = SyntaxReport()

    # ─────────────────────────────────────────────────────────────────────
    def clean_directory(self, directory: Path) -> Dict:
        """Dizindeki tüm .py dosyalarını temizle ve raporla."""
        directory = Path(directory)
        results   = {"directory": str(directory), "files": {}, "ts": datetime.now().isoformat()}

        py_files = list(directory.rglob("*.py"))
        if not py_files:
            return results

        print(f"\n  \033[96m[SYNTAX] {len(py_files)} dosya temizleniyor: {directory.name}/\033[0m")
        total = len(py_files)

        for i, f in enumerate(py_files, 1):
            pct  = int((i / total) * 40)
            bar  = "█" * pct + "░" * (40 - pct)
            print(f"\r  \033[96m[{bar}] {i}/{total}  {f.name:<35}\033[0m", end="", flush=True)
            r = self.clean_file(f)
            results["files"][str(f)] = r
            time.sleep(0.05)
        print()

        ok     = sum(1 for r in results["files"].values() if r["final_ok"])
        errors = total - ok
        results["summary"] = {"total": total, "ok": ok, "errors": errors}
        print(f"  \033[92m✅ Temizlendi: {ok}/{total}\033[0m" +
              (f"  \033[91m❌ Kalan: {errors}\033[0m" if errors else ""))
        return results

    # ─────────────────────────────────────────────────────────────────────
    def clean_file(self, filepath: Path) -> Dict:
        """Tek dosya: parse → fix döngüsü → test."""
        filepath = Path(filepath)
        result   = {"path": str(filepath), "rounds": 0, "fixes": [], "final_ok": False}

        try:
            code = filepath.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            result["error"] = str(e)
            return result

        for round_n in range(1, MAX_ROUNDS + 1):
            result["rounds"] = round_n
            try:
                ast.parse(code)
                result["final_ok"] = True
                break
            except SyntaxError as e:
                applied = []
                for fixer_fn in self.FIXERS:
                    try:
                        new_code = fixer_fn(code)
                        if new_code != code:
                            applied.append(fixer_fn.__name__)
                            code = new_code
                    except Exception:
                        pass
                if not applied:
                    # Kaba kuvvet: hata satırını sil
                    code = self._nuke_bad_line(code, e.lineno)
                    applied.append("nuke_bad_line")
                result["fixes"].extend(applied)

        if result["final_ok"]:
            try:
                filepath.write_text(code, encoding="utf-8")
            except Exception as e:
                result["write_error"] = str(e)

        return result

    # ─────────────────────────────────────────────────────────────────────
    @staticmethod
    def _nuke_bad_line(code: str, lineno: int) -> str:
        """Son çare: hatalı satırı yorum satırına çevir."""
        lines = code.split("\n")
        if lineno and 0 < lineno <= len(lines):
            lines[lineno - 1] = "# [SYNTAX-AUTO-REMOVED] " + lines[lineno - 1]
        return "\n".join(lines)

    # ─────────────────────────────────────────────────────────────────────
    def verify_directory(self, directory: Path) -> Tuple[int, int]:
        """(ok_count, error_count) döndürür — düzeltme yapmaz."""
        ok = err = 0
        for f in Path(directory).rglob("*.py"):
            try:
                ast.parse(f.read_text(encoding="utf-8", errors="replace"))
                ok += 1
            except SyntaxError:
                err += 1
        return ok, err
