# services /
# __init__.py
# analysis_service.py  # main workflow orchestration
# baseline_policy.py  # baseline precedence rules (isolated)
# prompt_builder.py  # build_prompt only
# url_normalizer.py  # normalize_url + validate_http_url

from __future__ import annotations

from tga_cli.services.baseline_policy import is_blank_baseline


def build_prompt(
    doc_text: str,
    competitor_text: str,
    baseline_text: str,
    competitor_url: str,
    baseline_url: str,
) -> str:
    baseline_url = (baseline_url or "").strip()

    if is_blank_baseline(baseline_url):
        return f"""
You are a technology analyst. Produce a structured comparison report.

INPUTS
1) Company document text
2) Competitor site text

Compare company vs competitor.

--- COMPANY DOCUMENT ---
{doc_text}

--- COMPETITOR ({competitor_url}) ---
{competitor_text}
""".strip()

    return f"""
You are a technology analyst. Produce a structured comparison report.

INPUTS
1) Company document text
2) Competitor site text
3) Baseline site text

Compare company vs competitor vs baseline.

--- COMPANY DOCUMENT ---
{doc_text}

--- COMPETITOR ({competitor_url}) ---
{competitor_text}

--- BASELINE ({baseline_url}) ---
{baseline_text}
""".strip()
