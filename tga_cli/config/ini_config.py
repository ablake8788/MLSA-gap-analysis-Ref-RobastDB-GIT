from __future__ import annotations

import configparser
import os
import sys
from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path
#from tga_cli.domain.models import AppSettings


#INI_DEFAULT_NAME = "TitaniumTechnologyGapAnalysisRef.ini"
INI_DEFAULT_NAME = "MLSA_GapAnalysisRefDB.ini"

# def load_settings(ini_path: Path) -> AppSettings:
#     config = ConfigParser()
#     config.read(str(ini_path), encoding="utf-8")
#
#     open_report = config.getboolean("Settings", "open_report", fallback=False)
#     return AppSettings(open_report=open_report)


#########################################

def load_settings(ini_path: Path):
    # Local import avoids PyInstaller circular import during module init
    from tga_cli.domain.models import AppSettings

    config = ConfigParser()
    config.read(str(ini_path), encoding="utf-8")

    open_report = config.getboolean("Settings", "open_report", fallback=False)
    return AppSettings(open_report=open_report)

#######################
@dataclass(frozen=True)
class SqlServerSettings:
    driver: str
    server: str
    database: str
    username: str
    password: str
    trust_cert: bool

def load_sqlserver_settings(ini_path: str) -> SqlServerSettings:
    cfg = configparser.ConfigParser()
    ok = cfg.read(ini_path)
    if not ok:
        raise FileNotFoundError(f"INI not found or unreadable: {ini_path}")

    if "sqlserver" not in cfg:
        raise KeyError("Missing [sqlserver] section in INI")

    s = cfg["sqlserver"]
    trust_cert = s.get("trust_cert", "yes").strip().lower() in ("yes", "true", "1")

    return SqlServerSettings(
        driver=s.get("driver", "ODBC Driver 17 for SQL Server"),
        server=s.get("server", "localhost"),
        database=s.get("database", ""),
        username=s.get("username", ""),
        password=s.get("password", ""),
        trust_cert=trust_cert,
    )




#######################

@dataclass(frozen=True)
class OpenAISettings:
    api_key: str
    model: str


@dataclass(frozen=True)
class SettingsSection:
    baseline_url: str
    max_doc_chars: int
    max_site_chars: int
    report_location: str
    compare_file_location: str


@dataclass(frozen=True)
class HttpSettings:
    timeout_seconds: int


@dataclass(frozen=True)
class OcrSettings:
    tesseract_path: str
    pdf_dpi: int


@dataclass(frozen=True)
class EmailSettings:
    enabled: bool
    smtp_server: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    from_email: str
    to_email: str
    subject: str


@dataclass(frozen=True)
class LoggingSettings:
    level: str


@dataclass(frozen=True)
class PptxSettings:
    max_table_body_rows_per_slide: int


@dataclass(frozen=True)
class Paths:
    ini_path: Path
    ini_dir: Path
    reports_dir: Path
    compare_dir: Path


@dataclass(frozen=True)
class AppSettings:
    openai: OpenAISettings
    settings: SettingsSection
    http: HttpSettings
    ocr: OcrSettings
    email: EmailSettings
    logging: LoggingSettings
    pptx: PptxSettings
    paths: Paths
    open_report: bool = False


class IniConfig:
    def __init__(self, ini_path: Path):
        self._ini_path = ini_path
        self._cfg = ConfigParser()
        read_ok = self._cfg.read(str(ini_path), encoding="utf-8")
        if not read_ok:
            raise FileNotFoundError(f"INI file not found or unreadable: {ini_path}")

    @staticmethod
    def from_env_or_default() -> "IniConfig":
        ini_raw = (os.getenv("APP_INI") or "").strip()
        if ini_raw:
            return IniConfig(Path(ini_raw).resolve())

        # Prefer INI next to EXE when frozen; else next to project root (2 levels up from this file)
        if getattr(sys, "frozen", False):
            ini_path = Path(sys.executable).resolve().parent / INI_DEFAULT_NAME
        else:
            ini_path = Path(__file__).resolve().parents[2] / INI_DEFAULT_NAME

        return IniConfig(ini_path)

    @staticmethod
    def _expand(s: str) -> str:
        return os.path.expandvars(os.path.expanduser((s or "").strip()))

    @staticmethod
    def _resolve_path(p: str, base: Path) -> Path:
        raw = IniConfig._expand(p)
        path = Path(raw)
        if not path.is_absolute():
            path = base / path
        return path.resolve(strict=False)

    def load_settings(self) -> AppSettings:
        ini_path = self._ini_path
        ini_dir = ini_path.parent

        api_key = self._expand(self._cfg.get("OpenAI", "api_key", fallback=""))
        model = (self._cfg.get("OpenAI", "model", fallback="gpt-4.1-mini") or "gpt-4.1-mini").strip()

        if not api_key:
            raise RuntimeError(
                "OpenAI API key not found.\n"
                f"Set [OpenAI].api_key in {ini_path} or set env var OPENAI_API_KEY and reference it in the INI."
            )

        baseline_url = (self._cfg.get("Settings", "baseline_url", fallback="") or "").strip()
        max_doc_chars = self._cfg.getint("Settings", "max_doc_chars", fallback=60000)
        max_site_chars = self._cfg.getint("Settings", "max_site_chars", fallback=40000)
        report_location = (self._cfg.get("Settings", "report_location", fallback="reports") or "reports").strip()
        compare_location = (self._cfg.get("Settings", "compare_file_location", fallback="") or "").strip()

        http_timeout = self._cfg.getint("HTTP", "timeout_seconds", fallback=25)

        tesseract_path = self._expand(self._cfg.get("OCR", "tesseract_path", fallback=""))
        pdf_dpi = self._cfg.getint("OCR", "pdf_dpi", fallback=300)

        email_enabled = self._cfg.getboolean("Email", "enabled", fallback=False)
        email = EmailSettings(
            enabled=email_enabled,
            smtp_server=self._expand(self._cfg.get("Email", "smtp_server", fallback="")),
            smtp_port=self._cfg.getint("Email", "smtp_port", fallback=587),
            smtp_user=self._expand(self._cfg.get("Email", "smtp_user", fallback="")),
            smtp_password=self._expand(self._cfg.get("Email", "smtp_password", fallback="")),
            from_email=self._expand(self._cfg.get("Email", "from_email", fallback="")),
            to_email=self._expand(self._cfg.get("Email", "to_email", fallback="")),
            subject=(self._cfg.get("Email", "subject", fallback="Technology Gap Analysis Report") or "").strip()
            or "Technology Gap Analysis Report",
        )

        log_level = (self._cfg.get("Logging", "level", fallback="INFO") or "INFO").strip()

        pptx_max_rows = self._cfg.getint("PPTX", "max_table_body_rows_per_slide", fallback=12)

        reports_dir = self._resolve_path(report_location, ini_dir)
        reports_dir.mkdir(parents=True, exist_ok=True)

        compare_dir = self._resolve_path(compare_location, ini_dir) if compare_location else (ini_dir / "compare")
        compare_dir.mkdir(parents=True, exist_ok=True)

        return AppSettings(
            openai=OpenAISettings(api_key=api_key, model=model),
            settings=SettingsSection(
                baseline_url=baseline_url,
                max_doc_chars=max_doc_chars,
                max_site_chars=max_site_chars,
                report_location=report_location,
                compare_file_location=compare_location,
            ),
            http=HttpSettings(timeout_seconds=http_timeout),
            ocr=OcrSettings(tesseract_path=tesseract_path, pdf_dpi=pdf_dpi),
            email=email,
            logging=LoggingSettings(level=log_level),
            pptx=PptxSettings(max_table_body_rows_per_slide=pptx_max_rows),
            paths=Paths(
                ini_path=ini_path,
                ini_dir=ini_dir,
                reports_dir=reports_dir,
                compare_dir=compare_dir,
            ),
        )
