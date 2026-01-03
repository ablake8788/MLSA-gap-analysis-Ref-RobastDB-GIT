#### references.py ###

import re
from datetime import datetime
from typing import Optional

URL_RE = re.compile(r"https?://[^\s\)>\]]+", re.IGNORECASE)

def extract_urls(*texts: Optional[str]) -> list[str]:
    urls = []
    seen = set()
    for t in texts:
        if not t:
            continue
        for m in URL_RE.findall(t):
            u = m.strip().rstrip(".,;:")
            if u not in seen:
                seen.add(u)
                urls.append(u)
    return urls

import re
from datetime import datetime
from typing import Optional

URL_RE = re.compile(r"https?://[^\s\)>\]]+", re.IGNORECASE)

def extract_urls(*texts: Optional[str]) -> list[str]:
    urls = []
    seen = set()
    for t in texts:
        if not t:
            continue
        for m in URL_RE.findall(t):
            u = m.strip().rstrip(".,;:")
            if u not in seen:
                seen.add(u)
                urls.append(u)
    return urls

def append_references_appendix(
    doc,  # python-docx Document
    *,
    competitor_url: Optional[str],
    baseline_url: Optional[str],
    input_file: Optional[str],
    generated_at: Optional[datetime],
    competitor_text: Optional[str] = None,
    baseline_text: Optional[str] = None,
    model_output_text: Optional[str] = None,
):
    doc.add_page_break()
    doc.add_heading("Appendix: References", level=1)

    refs: list[str] = []
    if competitor_url:
        refs.append(f"Primary competitor: {competitor_url}")
    if baseline_url:
        refs.append(f"Secondary competitor (baseline): {baseline_url}")
    if input_file:
        refs.append(f"Input file: {input_file}")
    if generated_at:
        refs.append(f"Generated: {generated_at.strftime('%Y-%m-%d %H:%M:%S')}")

    discovered_urls = extract_urls(competitor_text, baseline_text, model_output_text)
    for u in discovered_urls:
        if competitor_url and u == competitor_url:
            continue
        if baseline_url and u == baseline_url:
            continue
        refs.append(u)

    if not refs:
        doc.add_paragraph("No references available.")
        return

    for i, r in enumerate(refs, start=1):
        doc.add_paragraph(f"{i}. {r}")



def append_references_appendix(
    doc,  # python-docx Document
    *,
    competitor_url: Optional[str],
    baseline_url: Optional[str],
    input_file: Optional[str],
    generated_at: Optional[datetime],
    competitor_text: Optional[str] = None,
    baseline_text: Optional[str] = None,
    model_output_text: Optional[str] = None,
):
    doc.add_page_break()
    doc.add_heading("Appendix: References", level=1)

    refs: list[str] = []
    if competitor_url:
        refs.append(f"Primary competitor: {competitor_url}")
    if baseline_url:
        refs.append(f"Secondary competitor (baseline): {baseline_url}")
    if input_file:
        refs.append(f"Input file: {input_file}")
    if generated_at:
        refs.append(f"Generated: {generated_at.strftime('%Y-%m-%d %H:%M:%S')}")

    discovered_urls = extract_urls(competitor_text, baseline_text, model_output_text)
    for u in discovered_urls:
        if competitor_url and u == competitor_url:
            continue
        if baseline_url and u == baseline_url:
            continue
        refs.append(u)

    if not refs:
        doc.add_paragraph("No references available.")
        return

    for i, r in enumerate(refs, start=1):
        doc.add_paragraph(f"{i}. {r}")
