### OAuth (Open Authorization) is a standard protocol for secure delegated access.


# project_root/
#   TitaniumTechnologyGapAnalysisRef.ini
#   tga_cli/
#     __init__.py
#     __main__.py                 # python -m tga_cli
#     app_factory.py              # composition root (wiring)
#
#     config/
#       __init__.py
#       ini_config.py             # load INI + normalize paths -> AppSettings
#
#     domain/
#       __init__.py
#       models.py                 # dataclasses: Inputs, Outputs, RunContext, Result
#       errors.py                 # domain exceptions (ValidationError, FatalError, etc.)
#
#     cli/
#       __init__.py
#       args.py                   # argparse only
#       controller.py             # calls service, handles exit codes/logging
#
#     logging/
#       __init__.py
#       setup.py                  # setup_logging + resource_path
#
#     services/
#       __init__.py
#       analysis_service.py       # main workflow orchestration
#       baseline_policy.py        # baseline precedence rules (isolated)
#       prompt_builder.py         # build_prompt only
#       url_normalizer.py         # normalize_url + validate_http_url
#
#     ports/
#       __init__.py
#       llm.py                    # interface for LLM client
#       fetcher.py                # interface for website fetch
#       readers.py                # interface for document reader
#       renderers.py              # interface for report renderers
#       emailer.py                # interface for email sender
#
#     adapters/
#       __init__.py
#       llm_openai.py             # OpenAI adapter
#       fetch_requests.py         # requests + BS4 (+ readability) adapter
#       readers_pdf.py            # pypdf + pdf2image + tesseract adapter
#       readers_docx.py
#       readers_image.py
#       email_smtp.py             # smtplib adapter
#
#     renderers/
#       __init__.py
#       markdown_normalizer.py    # normalize_report_markdown
#       html_renderer.py          # markdown + CSS template
#       docx_renderer.py          # markdown_to_docx
#       pptx_renderer.py          # markdown_to_pptx_table_style
#
#     repositories/
#       __init__.py
#       report_repository.py      # ensure_reports_dir / ensure_run_dir / file naming
#
#     utils/
#       __init__.py
#       text.py                   # truncate, safe_slug, competitor_slug_from_url
#
#   tests/
#     test_url_normalizer.py
#     test_baseline_policy.py
#     test_prompt_builder.py
#     test_report_repository.py
#     test_analysis_service_unit.py

# python -m PyInstaller --clean --noconfirm --onefile ` --name TitaniumTechnologyGapAnalysisCLI ` tga_cli_main.py --add-data "TitaniumTechnologyGapAnalysisRef.ini:."

from tga_cli.cli.controller import main

if __name__ == "__main__":
    raise SystemExit(main())
