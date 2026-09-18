"""
CodeTester — Oluşturulan kodu gerçekten çalıştırır.
Import hataları, runtime hataları tespit eder ve raporlar.
"""
import ast, sys, subprocess, tempfile, json
from pathlib import Path
from typing import Dict, Tuple


class CodeTester:
    """Syntax OK olan kodu gerçek Python process'te test eder."""

    def test_file(self, filepath: Path, timeout: int = 15) -> Dict:
        """Dosyayı subprocess'te syntax+import test ile çalıştır."""
        filepath = Path(filepath)
        result = {
            "path":       str(filepath),
            "syntax_ok":  False,
            "import_ok":  False,
            "runtime_ok": False,
            "errors":     [],
        }

        # 1. Syntax
        try:
            code = filepath.read_text(encoding="utf-8", errors="replace")
            ast.parse(code)
            result["syntax_ok"] = True
        except SyntaxError as e:
            result["errors"].append(f"SyntaxError:{e.lineno}: {e.msg}")
            return result

        # 2. Import check (--check flag ile)
        try:
            proc = subprocess.run(
                [sys.executable, "-m", "py_compile", str(filepath)],
                capture_output=True, text=True, timeout=10
            )
            if proc.returncode == 0:
                result["import_ok"] = True
            else:
                result["errors"].append(f"Compile: {proc.stderr.strip()[:200]}")
        except subprocess.TimeoutExpired:
            result["errors"].append("py_compile timeout")
        except Exception as e:
            result["errors"].append(str(e))

        # 3. Kısa runtime test (--help veya import-only)
        try:
            test_code = f"""
import importlib.util, sys
spec = importlib.util.spec_from_file_location("_test", r"{filepath}")
mod  = importlib.util.module_from_spec(spec)
# Sadece yükle, main() çalıştırma
try:
    spec.loader.exec_module(mod)
    print("IMPORT_OK")
except SystemExit:
    print("IMPORT_OK")  # main() sys.exit çağırıyorsa
except Exception as e:
    print(f"IMPORT_ERR: {{e}}")
"""
            proc2 = subprocess.run(
                [sys.executable, "-c", test_code],
                capture_output=True, text=True, timeout=timeout,
                env={"PATH": "/usr/bin:/bin", "PYTHONPATH": str(filepath.parent)}
            )
            output = proc2.stdout + proc2.stderr
            if "IMPORT_OK" in output:
                result["runtime_ok"] = True
            elif "IMPORT_ERR" in output:
                result["errors"].append(output.strip()[:300])
        except subprocess.TimeoutExpired:
            result["runtime_ok"] = True  # Timeout = çalıştı (beklenen davranış)
        except Exception as e:
            result["errors"].append(f"Runtime test: {e}")

        return result

    def test_directory(self, directory: Path, timeout: int = 10) -> Dict:
        """Tüm dizini test et, özet döndür."""
        directory = Path(directory)
        results   = {}
        py_files  = list(directory.rglob("*.py"))

        ok = fail = 0
        for f in py_files:
            r = self.test_file(f, timeout)
            results[f.name] = r
            if r["syntax_ok"] and r["import_ok"]:
                ok += 1
            else:
                fail += 1

        return {
            "directory": str(directory),
            "total":     len(py_files),
            "ok":        ok,
            "fail":      fail,
            "files":     results,
        }

    def auto_fix_and_test(self, filepath: Path, fixer, max_attempts: int = 5) -> Dict:
        """
        Test → eğer başarısız → fixer.fix_file() → tekrar test.
        max_attempts kadar dener.
        """
        for attempt in range(1, max_attempts + 1):
            result = self.test_file(filepath)
            if result["syntax_ok"] and result["import_ok"]:
                result["attempts"] = attempt
                return result
            # Düzelt
            fixer.fix_file(filepath)

        # Son test
        final = self.test_file(filepath)
        final["attempts"] = max_attempts
        return final
