



from __future__ import annotations
from tga_cli.cli.controller import main

if __name__ == "__main__":
    raise SystemExit(main())

import logging

from tga_cli.cli.args import parse_args
from tga_cli.domain.errors import ValidationError, FatalError

logger = logging.getLogger("tga_cli")


def main() -> int:
    args = parse_args()

    # Import inside function to avoid circular imports in PyInstaller onefile mode.
    from tga_cli.app_factory import create_service
    from tga_cli.config.ini_config import load_settings, INI_DEFAULT_NAME
    from tga_cli.adapters.opener_os import open_path

    # If you already have a shared "resolve_ini_path" helper elsewhere, use it.
    # Otherwise this is a safe minimal resolver:
    from pathlib import Path
    import sys

    def resolve_ini_path(filename: str) -> Path:
        if getattr(sys, "frozen", False):
            return Path(sys.executable).resolve().parent / filename
        return Path(__file__).resolve().parents[1] / filename  # project_root/INI

    ini_path = resolve_ini_path(INI_DEFAULT_NAME)
    settings = load_settings(ini_path)

    svc = create_service()

    try:
        result = svc.run(args)
        logger.info("Done. Run folder: %s", result.artifacts.run_dir)

        # Open Word report only if enabled in INI
        if settings.open_report:
            open_path(result.artifacts.docx_path)

        return 0 if result.status == "ok" else 2

    except ValidationError as e:
        logger.error("Validation error: %s", e)
        return 2
    except FatalError as e:
        logger.error("Fatal error: %s", e)
        return 2
    except Exception:
        logger.exception("Unhandled error")
        return 2



# architectural design comments for this codebase, including the key design patterns embodied by the structure
#
# *********************************************
# Key design patterns used
# •	Application Factory: create_app() builds the app and dependencies.
# •	Dependency Injection (manual): dependencies are passed into routes and service constructors.
# •	Service Layer: AnalysisService encapsulates the use case.
# •	Repository: RunRepository encapsulates filesystem queries.
# •	Strategy: UrlNormalizer allows you to swap normalization logic.
## *********************************************
# #############################################
# # # composition root (wiring)cd
# # project_root/
# #   TitaniumTechnologyGapAnalysisRef.ini
# #   tga_cli/
# #     __init__.py
# #     __main__.py                 # python -m tga_cli
# #     app_factory.py              # composition root (wiring)
# #
# #     config/
# #       __init__.py
# #       ini_config.py             # load INI + normalize paths -> AppSettings
# #
# #     domain/
# #       __init__.py
# #       models.py                 # dataclasses: Inputs, Outputs, RunContext, Result
# #       errors.py                 # domain exceptions (ValidationError, FatalError, etc.)
# #
# #     cli/
# #       __init__.py
# #       args.py                   # argparse only
# #       controller.py             # calls service, handles exit codes/logging
# #
# #     logging/
# #       __init__.py
# #       setup.py                  # setup_logging + resource_path
# #
# #     services/
# #       __init__.py
# #       analysis_service.py       # main workflow orchestration
# #       baseline_policy.py        # baseline precedence rules (isolated)
# #       prompt_builder.py         # build_prompt only
# #       url_normalizer.py         # normalize_url + validate_http_url
# #
# #     ports/
# #       __init__.py
# #       llm.py                    # interface for LLM client
# #       fetcher.py                # interface for website fetch
# #       readers.py                # interface for document reader
# #       renderers.py              # interface for report renderers
# #       emailer.py                # interface for email sender
# #
# #     adapters/s
# #       __init__.py
# #       llm_openai.py             # OpenAI adapter
# #       fetch_requests.py         # requests + BS4 (+ readability) adapter
# #       readers_pdf.py            # pypdf + pdf2image + tesseract adapter
# #       readers_docx.py
# #       readers_image.py
# #       email_smtp.py             # smtplib adapter
# #
# #     renderers/
# #       __init__.py
# #       markdown_normalizer.py    # normalize_report_markdown
# #       html_renderer.py          # markdown + CSS template
# #       docx_renderer.py          # markdown_to_docx
# #       pptx_renderer.py          # markdown_to_pptx_table_style
# #
# #     repositories/
# #       __init__.py
# #       report_repository.py      # ensure_reports_dir / ensure_run_dir / file naming
# #
# #     utils/
# #       __init__.py
# #       text.py                   # truncate, safe_slug, competitor_slug_from_url
# #
# #   tests/
# #     test_url_normalizer.py
# #     test_baseline_policy.py
# #     test_prompt_builder.py
# #     test_report_repository.py
# #     test_analysis_service_unit.py
#
#
# #############################################
#
# # CLI entrypoint
# #
# # tga_cli/__main__.py starts the app via app_factory.py.
# #
# # Controller triggers the workflow
# #
# # cli/controller.py receives parsed args (from cli/args.py) and calls the main orchestration:
# #
# # services/analysis_service.py
# #
# # Inputs are gathered and normalized (still no ChatGPT call)
# #
# # config/ini_config.py loads and normalizes config into AppSettings.
# #
# # services/url_normalizer.py normalizes/validates URLs.
# #
# # services/baseline_policy.py applies precedence rules for which baseline to use.
# #
# # adapters/fetch_requests.py fetches website content if needed.
# #
# # adapters/readers_*.py read documents (PDF/DOCX/images).
# #
# # The comparison prompt is assembled
# #
# # services/prompt_builder.py constructs the final prompt (the actual “comparison request” text).
# #
# # This is where it is submitted to ChatGPT
# #
# # Inside services/analysis_service.py, after the prompt is built, the service calls the LLM via the port:
# #
# # ports/llm.py (interface)
# #
# # implemented by adapters/llm_openai.py (OpenAI / ChatGPT adapter)
# #
# # So the specific point is:
# #
# # services/analysis_service.py → calls ports.llm (implemented by adapters/llm_openai.py) with the prompt produced by services/prompt_builder.py.
# #
# # If you want to identify the exact line(s), look for something shaped like:
# #
# # prompt = prompt_builder.build_prompt(...)
# #
# # llm_response = llm_client.generate(...) / llm_client.complete(...) / llm_client.chat(...)
# #
# # and that llm_client is created/wired in app_factory.py.
#
#
# ) Architectural style and intent
# This project implements a Clean Architecture / Hexagonal (Ports & Adapters) style with a thin CLI delivery mechanism and explicit dependency inversion:
# •	Domain contains pure business concepts and errors (no I/O).
# •	Services implement application workflows (use cases) and orchestrate domain + ports.
# •	Ports define abstract interfaces for external capabilities (LLM, fetching, reading, rendering, email).
# •	Adapters implement those ports using concrete libraries (OpenAI SDK, requests/BS4, PDF/DOCX readers, SMTP).
# •	Composition root wires concrete adapters into ports at runtime (app_factory.py), so the rest of the code depends only on abstractions.
# Primary objectives:
# •	Keep the workflow logic testable without network/files.
# •	Make it easy to swap integrations (e.g., OpenAI ↔ other LLM, requests ↔ Playwright).
# •	Make output formats pluggable (HTML/DOCX/PPTX).
# ________________________________________
# 2) Module responsibilities (descriptive framework)
# Composition Root
# tga_cli/app_factory.py
# •	Central wiring point for dependency injection.
# •	Constructs the concrete implementations of:
# o	ports.llm.LLMClient → adapters.llm_openai.OpenAIClient
# o	ports.fetcher.Fetcher → adapters.fetch_requests.RequestsFetcher
# o	ports.readers.DocumentReader → adapters.readers_pdf/PDFReader, etc.
# o	ports.renderers.ReportRenderer → renderers.html_renderer/...
# o	ports.emailer.Emailer → adapters.email_smtp.SMTPEmailer
# •	Returns an application/controller instance ready to run.
# Pattern: Composition Root, Dependency Injection (manual DI)
# ________________________________________
# Delivery (CLI Layer)
# cli/args.py
# •	CLI surface area only: parses args, validates basic structure, help text.
# •	No workflow logic.
# cli/controller.py
# •	Translates CLI arguments into application inputs.
# •	Calls the use case/service.
# •	Handles exit codes, top-level exception mapping, user-facing logging.
# Patterns: Controller, Thin Delivery Layer
# ________________________________________
# Configuration
# config/ini_config.py
# •	Reads INI file and converts it into typed settings (e.g., AppSettings).
# •	Normalizes relative paths into absolute paths early.
# •	Performs structural validation of configuration required for the run.
# Patterns: Configuration Provider, Normalization at boundaries
# ________________________________________
# Domain
# domain/models.py
# •	Pure dataclasses that represent:
# o	Inputs (what the use case consumes)
# o	Outputs (what it produces)
# o	RunContext (run-id, directories, timestamps, traceability)
# o	Result (final report text + metadata + artifacts)
# •	Should be free of I/O and third-party dependencies.
# domain/errors.py
# •	Domain-level exceptions with clear semantics:
# o	ValidationError for recoverable input/config issues.
# o	FatalError for unrecoverable failures (e.g., missing required resources).
# Patterns: Domain Model, Explicit Error Taxonomy
# ________________________________________
# Application Services (Use Cases)
# services/analysis_service.py
# •	The primary use case/workflow orchestrator.
# •	Sequence:
# 1.	validate/normalize inputs and settings
# 2.	determine baseline (policy)
# 3.	fetch/read data (through ports)
# 4.	build prompt
# 5.	call LLM (through LLM port)
# 6.	normalize and render output
# 7.	persist outputs via repository
# 8.	optionally email results
# services/baseline_policy.py
# •	Encapsulates baseline selection and precedence rules.
# •	Must remain isolated, deterministic, and easy to unit test.
# services/prompt_builder.py
# •	Pure function(s) that transform inputs/context into the final LLM request payload:
# o	either a single prompt string or structured chat messages.
# •	No network, no file access.
# services/url_normalizer.py
# •	Validates URLs and normalizes forms consistently (scheme, trailing slash rules, etc.).
# •	Ensures upstream components get canonical URLs.
# Patterns: Use Case / Application Service, Policy Object, Pure Builder
# ________________________________________
# Ports (Interfaces)
# ports/*.py
# •	Abstract contracts describing required capabilities.
# •	These are the “edges” of the application:
# o	llm.py: generate(messages|prompt) -> LLMResponse
# o	fetcher.py: fetch web pages
# o	readers.py: read PDFs/DOCX/images to text
# o	renderers.py: produce output artifacts from normalized markdown
# o	emailer.py: send outputs
# These should be narrow interfaces that enable mocking/faking in tests.
# Patterns: Dependency Inversion, Interface Segregation
# ________________________________________
# Adapters (Concrete Integrations)
# adapters/llm_openai.py
# •	Implements the ports.llm contract.
# •	Translates your internal LLMRequest into OpenAI API calls.
# •	Handles retries/timeouts, response parsing, error translation.
# adapters/fetch_requests.py
# •	Implements web fetching via requests + HTML parsing.
# •	May include readability extraction.
# •	Must return consistent structures expected by services.
# adapters/readers_*.py
# •	Format-specific extractors (PDF, DOCX, images).
# •	Keep each adapter specialized and composable.
# adapters/email_smtp.py
# •	Email sending, attachments, SMTP configuration.
# Patterns: Adapter, Gateway, Anti-Corruption Layer (translating external shapes/errors into internal ones)
# ________________________________________
# Renderers
# renderers/markdown_normalizer.py
# •	Stabilizes markdown so downstream renderers produce consistent artifacts:
# o	heading normalization, table cleanup, etc.
# renderers/html_renderer.py / docx_renderer.py / pptx_renderer.py
# •	Convert normalized markdown into final artifacts.
# •	Should not contain workflow logic—only formatting/conversion.
# Patterns: Strategy (multiple renderers), Pipeline stage
# ________________________________________
# Repository
# repositories/report_repository.py
# •	Single responsibility: filesystem organization and persistence conventions:
# o	reports directory structure
# o	run directories
# o	stable naming conventions
# •	Prevents scattering path logic across services.
# Patterns: Repository (filesystem), Convention over Configuration
# ________________________________________
# Utilities
# utils/text.py
# •	Non-domain-specific helpers that are safe and deterministic:
# o	slugging, truncation, url->competitor slug, etc.
# ________________________________________
# 3) End-to-end workflow overview (sequence)
# A) Process-level
# 1.	python -m tga_cli invokes __main__.py
# 2.	app_factory.py wires dependencies (ports ↔ adapters)
# 3.	cli/args.py parses CLI arguments
# 4.	cli/controller.py constructs domain Inputs + RunContext
# 5.	analysis_service.run(inputs) executes the use case
# 6.	Outputs are persisted and optionally emailed
# B) Within analysis_service.py (use case)
# Typical internal steps:
# 1.	Load config (ini_config -> AppSettings)
# 2.	Normalize inputs/URLs (url_normalizer)
# 3.	Select baseline (baseline_policy)
# 4.	Acquire sources via ports:
# o	fetch competitor pages
# o	read PDFs/DOCX/images
# 5.	Build prompt (prompt_builder)
# 6.	LLM call via port (ports.llm → adapters.llm_openai)
# 7.	Normalize markdown (markdown_normalizer)
# 8.	Render artifacts (HTML/DOCX/PPTX)
# 9.	Persist via report_repository
# 10.	Email (optional) via ports.emailer
# ________________________________________
# 4) Key design patterns (explicit mapping)
# 1.	Hexagonal / Ports & Adapters
# o	Ports: ports/*.py
# o	Adapters: adapters/*.py
# o	Services and domain depend inward, never outward.
# 2.	Dependency Injection / Composition Root
# o	app_factory.py is the only place where concrete classes are chosen.
# 3.	Use Case (Application Service)
# o	analysis_service.py orchestrates the workflow, owning sequencing and coordination.
# 4.	Strategy Pattern
# o	Renderer selection (HTML/DOCX/PPTX) and potentially readers by file type.
# 5.	Policy Object
# o	baseline_policy.py isolates decision rules with deterministic behavior.
# 6.	Builder (Pure Function)
# o	prompt_builder.py constructs LLM requests from inputs/context.
# 7.	Repository Pattern
# o	report_repository.py encapsulates storage conventions and persistence.
# 8.	Anti-Corruption Layer
# o	llm_openai.py converts internal contracts to external API and back; same for fetchers/readers.
# ________________________________________
# 5) Architectural comments you can place in the repo (ready-to-paste)
# Comment for app_factory.py
# •	“Composition root. This module wires port interfaces to concrete adapters. No business logic should appear here.”
# Comment for analysis_service.py
# •	“Application service implementing the technology gap analysis use case. Orchestrates normalization, source acquisition, prompt construction, LLM invocation, rendering, and persistence. All external I/O occurs through ports.”
# Comment for prompt_builder.py
# •	“Pure prompt composition. No network, filesystem, or external dependencies. Changes here alter only the LLM request payload.”
# Comment for ports/
# •	“Abstract interfaces for external capabilities. Services depend only on ports; adapters implement ports.”
# ________________________________________
# 6) Design quality notes (what to emphasize)
# If this is meant to be a formal architectural design, these are the “talking points” reviewers typically want:
# •	Testability: most logic is in pure services/policies/builders; ports can be mocked.
# •	Replaceability: OpenAI adapter can be swapped without touching the use case.
# •	Single responsibility: each module has one clear job.
# •	Boundary discipline: normalization/validation happens at the edges (config/cli), not deep in domain.
#


