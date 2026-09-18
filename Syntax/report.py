"""SyntaxReport — Temizleme sonuçlarını JSON/HTML olarak yazar."""
import json
from pathlib import Path
from datetime import datetime


class SyntaxReport:
    def write(self, results: dict, output_dir: Path = None, fmt: str = "json") -> Path:
        output_dir = Path(output_dir or Path.cwd())
        output_dir.mkdir(parents=True, exist_ok=True)
        ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = f"syntax_report_{ts}"

        if fmt == "html":
            out  = output_dir / f"{name}.html"
            rows = ""
            for fpath, data in results.get("files", {}).items():
                ok    = data.get("final_ok", False)
                color = "#1a9e4a" if ok else "#c0392b"
                fixes = ", ".join(data.get("fixes", []))[:80]
                rows += (f'<tr><td>{Path(fpath).name}</td>'
                         f'<td style="color:{color}">{"✅ OK" if ok else "❌ ERR"}</td>'
                         f'<td>{data.get("rounds",0)}</td>'
                         f'<td>{fixes}</td></tr>\n')
            html = f"""<!DOCTYPE html><html>
<head><meta charset="UTF-8"><title>HRSploit Syntax Report</title>
<style>
  body{{font-family:monospace;background:#0d0d0d;color:#e0e0e0;padding:20px}}
  h1{{color:#e94560}}  table{{width:100%;border-collapse:collapse;margin-top:20px}}
  th{{background:#1a1a2e;color:#e94560;padding:10px;text-align:left}}
  td{{border:1px solid #333;padding:8px}}  tr:hover{{background:#1a1a2e}}
</style></head><body>
<h1>HRSploit — Syntax Engine Report</h1>
<p>Generated: {datetime.now().isoformat()}</p>
<p>Summary: {results.get("summary",{})}</p>
<table><tr><th>File</th><th>Status</th><th>Rounds</th><th>Fixes Applied</th></tr>
{rows}</table></body></html>"""
            out.write_text(html)
        else:
            out = output_dir / f"{name}.json"
            out.write_text(json.dumps(results, indent=2, ensure_ascii=False))
        return out
