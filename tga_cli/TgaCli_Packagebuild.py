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


#################################
# Set-Location "C:\Ara\Python\Titanium Inteligent Soultions\Titanium technology gap analysis Ref"
#
# @'
# from tga_cli.cli.controller import main
#
# if __name__ == "__main__":
#     raise SystemExit(main())
# '@ | Set-Content -Encoding UTF8 .\tga_cli_main.py
#
# dir .\tga_cli_main.py
#
# python -m PyInstaller --clean --noconfirm --onefile `
#   --name TitaniumTechnologyGapAnalysisCLI `
#   --add-data "TitaniumTechnologyGapAnalysisRef.ini;." `
#   .\tga_cli_main.py
#
#
#
#
#
#
# #############################################################
# A) Verify Python + working directory + sys.path
# python -c "import os,sys; print('cwd=', os.getcwd()); print('python=', sys.executable); print('path0=', sys.path[0])"
#
#
# Expected: cwd is your project root and python points to .venv.
#
# B) Verify tga_cli package resolution + exported symbols
# python -c "import tga_cli; print('tga_cli file:', tga_cli.__file__); print('has create_service:', hasattr(tga_cli,'create_service')); print('create_service in dir:', 'create_service' in dir(tga_cli))"
#
#
# If has create_service is False, your tga_cli/__init__.py isn’t exporting it.
#
# C) Verify all core modules import (fast health check)
# python -c "mods=['tga_cli.app_factory','tga_cli.config.ini_config','tga_cli.services.analysis_service','tga_cli.services.url_normalizer','tga_cli.services.baseline_policy','tga_cli.services.prompt_builder','tga_cli.repositories.report_repository','tga_cli.adapters.fetch_requests','tga_cli.adapters.llm_openai','tga_cli.adapters.readers_pdf','tga_cli.adapters.readers_docx','tga_cli.adapters.readers_image','tga_cli.renderers.html_renderer','tga_cli.renderers.docx_renderer','tga_cli.renderers.pptx_renderer']; import importlib; ok=[];
# for m in mods: importlib.import_module(m); ok.append(m);
# print('IMPORTED', len(ok), 'modules OK')"
#
#
# If this fails, it will show the exact missing dependency/module.
#
# D) Verify external dependencies (pinpoints missing pip installs)
# python -c "pkgs=['openai','requests','bs4','lxml','markdown','docx','pptx','pypdf','pytesseract','PIL']; import importlib; missing=[];
# for p in pkgs:
#   try: importlib.import_module(p)
#   except Exception as e: missing.append((p,str(e)))
# print('missing=', missing if missing else 'none')"
#
#
# If anything is missing, install it and re-run.
#
# E) Verify INI discovery + settings load (most important)
# python -c "from tga_cli.config import IniConfig; ini=IniConfig.from_env_or_default(); s=ini.load_settings();
# print('INI:', s.paths.ini_path);
# print('reports_dir:', s.paths.reports_dir);
# print('compare_dir:', s.paths.compare_dir);
# print('model:', s.openai.model);
# print('baseline(INI):', repr(s.settings.baseline_url))"
#
#
# If it can’t find the INI, set it explicitly:
#
# $env:APP_INI="C:\Ara\Python\Titanium Inteligent Soultions\Titanium technology gap analysis Ref\TitaniumTechnologyGapAnalysisRef.ini"
#
# F) Verify service wiring (DI / composition root)
# python -c "from tga_cli.app_factory import create_service; svc=create_service();
# print('service=', type(svc).__name__);
# print('has llm:', svc.llm is not None);
# print('has fetcher:', svc.fetcher is not None);
# print('readers:', sorted(list(svc.readers.keys()))[:5], '... total', len(svc.readers))"
#
# G) Verify URL normalization behavior (unit-style)
# python -c "from tga_cli.services.url_normalizer import normalize_url, validate_http_url;
# tests=['door.com','door','https://door.com','localhost','http://localhost:5000/x'];
# for t in tests:
#   try: print(t,'->', validate_http_url(t,'T'))
#   except Exception as e: print(t,'-> ERROR', e)"
#
# H) Verify baseline precedence rules (critical behavior)
# python -c "from tga_cli.services.baseline_policy import choose_baseline, is_blank_baseline;
# ini='https://baseline.com';
# cases=[('flag absent', None),('flag present blank',''),('flag present NA','NA'),('flag present url','https://x.com')];
# for name,cli in cases:
#   b=choose_baseline(cli, ini);
#   print(name,'cli=',repr(cli),'-> chosen=',repr(b),'blank?',is_blank_baseline(b))"
#
# I) Verify report directory creation and naming (filesystem)
# python -c "from tga_cli.config import IniConfig; from tga_cli.repositories.report_repository import ReportRepository;
# from tga_cli.utils.text import build_report_base_name;
# s=IniConfig.from_env_or_default().load_settings();
# repo=ReportRepository(s.paths.reports_dir);
# rb=build_report_base_name('https://door.com');
# rd=repo.ensure_run_dir(rb);
# print('created:', rd); print('exists:', rd.exists())"
#
# J) End-to-end “no OpenAI” smoke test (reads file + fetches site)
#
# This verifies: file reading + HTTP fetch, without calling OpenAI.
# You need a real file path that exists.
#
# python -c "from tga_cli.app_factory import create_service; from tga_cli.domain.models import CliArgs;
# svc=create_service();
# args=CliArgs(file=r'C:\path\to\your.pdf', competitor='https://door.com', baseline='', model='', max_rows=10);
# # internal helpers are private; we just call a limited subset safely:
# from tga_cli.services.url_normalizer import validate_http_url;
# c=validate_http_url(args.competitor,'Competitor');
# print('competitor ok:', c);
# p=svc._resolve_input_file(args.file); print('file ok:', p);
# ext=p.suffix.lower(); txt=svc.readers[ext].read(p); print('doc chars:', len(txt));
# site=svc.fetcher.fetch_text(c); print('site chars:', len(site))"
#
#
# If this works, your environment is solid. The remaining step is the OpenAI call.
#
# K) Full run (calls OpenAI)
#
# Only run this when you’re ready and your API key is configured:
#
# python -m tga_cli --file "C:\path\to\your.pdf" --competitor "https://door.com" --baseline
#
# Convenience: “single command” full health report
#
# This prints a consolidated report and stops at the first failure.
#
# python -c "import importlib, os, sys;
# print('cwd=',os.getcwd()); print('python=',sys.executable);
# import tga_cli; print('tga_cli=',tga_cli.__file__);
# from tga_cli.config import IniConfig; s=IniConfig.from_env_or_default().load_settings();
# print('ini=',s.paths.ini_path); print('reports=',s.paths.reports_dir); print('compare=',s.paths.compare_dir);
# from tga_cli.app_factory import create_service; svc=create_service(); print('service ok:', type(svc).__name__);
# mods=['tga_cli.services.analysis_service','tga_cli.adapters.fetch_requests','tga_cli.adapters.llm_openai','tga_cli.renderers.pptx_renderer'];
# for m in mods: importlib.import_module(m); print('import ok:', m);
# print('DONE')"

