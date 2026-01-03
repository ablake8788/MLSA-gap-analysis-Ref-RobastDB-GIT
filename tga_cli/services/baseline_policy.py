# services /
# __init__.py
# analysis_service.py  # main workflow orchestration
# baseline_policy.py  # baseline precedence rules (isolated)
# prompt_builder.py  # build_prompt only
# url_normalizer.py  # normalize_url + validate_http_url

from __future__ import annotations

def is_blank_baseline(url: str | None) -> bool:
    if url is None:
        return True
    s = str(url).strip()
    if not s:
        return True
    return s.lower() in {"n/n", "na", "n.a.", "none", "null", "-"}


def choose_baseline(cli_baseline: str | None, ini_baseline: str) -> str:
    """
    Precedence:
      - if CLI flag present -> cli_baseline (even blank disables)
      - else -> ini_baseline
    """
    if cli_baseline is not None:
        return cli_baseline
    return ini_baseline
