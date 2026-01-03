# html_renderer.py          # markdown + CSS template

from __future__ import annotations

import markdown

from tga_cli.domain.models import RunContext, RunArtifacts


class HtmlRenderer:
    def render(self, *, report_md: str, ctx: RunContext, artifacts: RunArtifacts) -> None:
        body_html = markdown.markdown(
            report_md,
            extensions=["tables", "fenced_code", "sane_lists", "toc"],
            output_format="html5",
        )

        title = "Competitor Gap Analysis Report"
        meta = [
            ("Primary Competitor", ctx.competitor_url),
            ("Generated", ctx.generated_at),
            ("Input file", ctx.input_file.name),
        ]
        if ctx.baseline_enabled:
            meta.append(("Secondary Competitor", ctx.baseline_url))

        meta_rows = "\n".join([f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in meta])

        css = """
        body{font-family:Arial, sans-serif;background:#f6f7f9;margin:0;color:#111827}
        .wrap{max-width:1100px;margin:24px auto;padding:0 16px}
        .card{background:#fff;border:1px solid #e5e7eb;border-radius:14px;padding:18px}
        h1{margin:0 0 10px 0}
        table{width:100%;border-collapse:collapse;border:1px solid #e5e7eb}
        th,td{padding:10px;border-bottom:1px solid #e5e7eb;border-right:1px solid #e5e7eb;vertical-align:top}
        th{background:#f3f4f6;text-align:left;width:220px}
        pre{background:#0b1020;color:#e5e7eb;padding:12px;border-radius:10px;overflow:auto}
        code{background:#eef2ff;padding:2px 6px;border-radius:8px}
        """

        html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>{title}</title><style>{css}</style></head>
<body>
<div class="wrap">
  <div class="card">
    <h1>{title}</h1>
    <table><tbody>{meta_rows}</tbody></table>
    <div class="content">{body_html}</div>
  </div>
</div>
</body></html>"""

        artifacts.html_path.write_text(html, encoding="utf-8")
