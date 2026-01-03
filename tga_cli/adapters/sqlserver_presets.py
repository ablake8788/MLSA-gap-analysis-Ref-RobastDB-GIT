# sqlserver_presets.py
#
# SQL Server adapter for dbo.GapAnalysisPresets.
# Extended to support report reference settings via either:
#   A) report_options (NVARCHAR(MAX) JSON), recommended
#   B) include_references/reference_format/citation_level columns (optional fallback)
#
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

import pyodbc

from tga_cli.config.ini_config import load_sqlserver_settings
from tga_cli.domain.models import Preset
from tga_cli.ports.presets import PresetRepository

log = logging.getLogger("tga_cli")


class SqlServerPresetRepository(PresetRepository):
    """
    SQL Server adapter for dbo.GapAnalysisPresets.

    Expected base schema (existing):
      preset_id             INT (IDENTITY)
      companyname           NVARCHAR(200)
      preset_display_name   NVARCHAR(200)
      competitor            NVARCHAR(500)
      baseline              NVARCHAR(500)
      instruction_preset    NVARCHAR(100)
      extra_instructions    NVARCHAR(MAX)
      source_file_path      NVARCHAR(500)
      web                   NVARCHAR(50)
      processor             NVARCHAR(100)
      is_active             BIT

    Optional schema extensions (choose one approach):

    A) JSON options (recommended):
      report_options        NVARCHAR(MAX) NULL
        e.g. {"include_references": true, "reference_format": "appendix", "citation_level": "section"}

    B) Explicit columns:
      include_references    BIT NULL
      reference_format      NVARCHAR(50) NULL
      citation_level        NVARCHAR(50) NULL
    """

    def __init__(self, ini_path: str, table_name: str = "dbo.GapAnalysisPresets"):
        self.ini_path = ini_path
        self.table_name = table_name

    def _connect(self) -> pyodbc.Connection:
        s = load_sqlserver_settings(self.ini_path)

        if not s.database:
            raise ValueError("INI missing sqlserver.database")
        if not s.username:
            raise ValueError("INI missing sqlserver.username")
        if not s.password:
            raise ValueError("INI missing sqlserver.password")

        conn_str = (
            f"DRIVER={{{s.driver}}};"
            f"SERVER={s.server};"
            f"DATABASE={s.database};"
            f"UID={s.username};"
            f"PWD={s.password};"
            f"TrustServerCertificate={'yes' if s.trust_cert else 'no'};"
        )
        return pyodbc.connect(conn_str)

    def debug_info(self) -> Dict[str, Any]:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT @@SERVERNAME")
            server = cur.fetchone()[0]
            cur.execute("SELECT DB_NAME()")
            db = cur.fetchone()[0]
            cur.execute(f"SELECT COUNT(*) FROM {self.table_name} WHERE is_active = 1")
            active_count = cur.fetchone()[0]
        return {
            "server": server,
            "database": db,
            "active_presets": int(active_count),
            "table": self.table_name,
        }

    def _has_column(self, conn: pyodbc.Connection, column_name: str) -> bool:
        if "." in self.table_name:
            schema, table = self.table_name.split(".", 1)
        else:
            schema, table = "dbo", self.table_name

        sql = """
        SELECT 1
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ? AND COLUMN_NAME = ?
        """
        cur = conn.cursor()
        cur.execute(sql, (schema, table, column_name))
        return cur.fetchone() is not None

    def get_active_presets(self) -> List[Dict[str, Any]]:
        log.info("SQL presets: querying %s", self.table_name)

        sql = f"""
        SELECT preset_id, companyname, preset_display_name
        FROM {self.table_name}
        WHERE is_active = 1
        ORDER BY companyname, preset_display_name
        """
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()

            return [
                {"id": int(r.preset_id), "name": f"{r.companyname} — {r.preset_display_name}"}
                for r in rows
            ]

    def get_preset(self, preset_id: int) -> Optional[Preset]:
        with self._connect() as conn:
            has_report_options = self._has_column(conn, "report_options")
            has_include_refs = self._has_column(conn, "include_references")
            has_ref_format = self._has_column(conn, "reference_format")
            has_citation_level = self._has_column(conn, "citation_level")

            optional_selects: List[str] = []
            if has_report_options:
                optional_selects.append("report_options")
            if has_include_refs:
                optional_selects.append("include_references")
            if has_ref_format:
                optional_selects.append("reference_format")
            if has_citation_level:
                optional_selects.append("citation_level")

            optional_sql = ""
            if optional_selects:
                optional_sql = ",\n            " + ",\n            ".join(optional_selects)

            sql = f"""
            SELECT
                preset_id,
                preset_display_name,
                competitor,
                baseline,
                instruction_preset,
                extra_instructions,
                source_file_path,
                web,
                processor
                {optional_sql}
            FROM {self.table_name}
            WHERE preset_id = ? AND is_active = 1
            """

            cur = conn.cursor()
            cur.execute(sql, preset_id)
            r = cur.fetchone()
            if not r:
                return None

            report_options: Optional[Dict[str, Any]] = None

            if has_report_options:
                raw = getattr(r, "report_options", None)
                if raw:
                    try:
                        report_options = json.loads(str(raw))
                    except Exception:
                        log.warning(
                            "Preset %s has invalid JSON in report_options; ignoring.",
                            preset_id,
                            exc_info=True,
                        )
                        report_options = None

            if report_options is None:
                include_references = None
                reference_format = None
                citation_level = None

                if has_include_refs:
                    include_references = getattr(r, "include_references", None)
                    if include_references is not None:
                        include_references = bool(include_references)

                if has_ref_format:
                    reference_format = getattr(r, "reference_format", None)
                    if reference_format is not None:
                        reference_format = str(reference_format)

                if has_citation_level:
                    citation_level = getattr(r, "citation_level", None)
                    if citation_level is not None:
                        citation_level = str(citation_level)

                if include_references is not None or reference_format is not None or citation_level is not None:
                    report_options = {
                        "include_references": include_references if include_references is not None else False,
                        "reference_format": reference_format or "appendix",
                        "citation_level": citation_level or "section",
                    }

            return Preset(
                id=int(r.preset_id),
                name=str(r.preset_display_name),
                competitor=str(r.competitor),
                baseline=(str(r.baseline) if r.baseline is not None else None),
                instruction_preset=(str(r.instruction_preset) if r.instruction_preset is not None else None),
                extra_instructions=(str(r.extra_instructions) if r.extra_instructions is not None else None),
                file=(str(r.source_file_path) if r.source_file_path is not None else None),
                web=(str(r.web) if r.web is not None else None),
                processor=(str(r.processor) if r.processor is not None else None),
                report_options=report_options,
            )










# # sqlserver_presets.py
# #
# # SQL Server adapter for dbo.GapAnalysisPresets.
# # Extended to support report reference settings via either:
# #   A) report_options (NVARCHAR(MAX) JSON), recommended
# #   B) include_references/reference_format/citation_level columns (optional fallback)
# #
# from __future__ import annotations
#
# import json
# import logging
# from typing import Any, Dict, List, Optional
#
# import pyodbc
#
# from tga_cli.config.ini_config import load_sqlserver_settings
# from tga_cli.domain.models import Preset
# from tga_cli.ports.presets import PresetRepository
#
# log = logging.getLogger("tga_cli")
#
#
# class SqlServerPresetRepository(PresetRepository):
#     """
#     SQL Server adapter for dbo.GapAnalysisPresets.
#
#     Expected base schema (existing):
#       preset_id             INT (IDENTITY)
#       companyname           NVARCHAR(200)
#       preset_display_name   NVARCHAR(200)
#       competitor            NVARCHAR(500)
#       baseline              NVARCHAR(500)
#       instruction_preset    NVARCHAR(100)
#       extra_instructions    NVARCHAR(MAX)
#       source_file_path      NVARCHAR(500)
#       web                   NVARCHAR(50)
#       processor             NVARCHAR(100)
#       is_active             BIT
#
#     Optional schema extensions (choose one approach):
#
#     A) JSON options (recommended):
#       report_options        NVARCHAR(MAX) NULL
#         e.g. {"include_references": true, "reference_format": "appendix", "citation_level": "section"}
#
#     B) Explicit columns:
#       include_references    BIT NULL
#       reference_format      NVARCHAR(50) NULL
#       citation_level        NVARCHAR(50) NULL
#     """
#
#     def __init__(self, ini_path: str, table_name: str = "dbo.GapAnalysisPresets"):
#         self.ini_path = ini_path
#         self.table_name = table_name
#
#     # ----------------------------
#     # Connection + Introspection
#     # ----------------------------
#     def _connect(self) -> pyodbc.Connection:
#         s = load_sqlserver_settings(self.ini_path)
#
#         if not s.database:
#             raise ValueError("INI missing sqlserver.database")
#         if not s.username:
#             raise ValueError("INI missing sqlserver.username")
#         if not s.password:
#             raise ValueError("INI missing sqlserver.password")
#
#         conn_str = (
#             f"DRIVER={{{s.driver}}};"
#             f"SERVER={s.server};"
#             f"DATABASE={s.database};"
#             f"UID={s.username};"
#             f"PWD={s.password};"
#             f"TrustServerCertificate={'yes' if s.trust_cert else 'no'};"
#         )
#         return pyodbc.connect(conn_str)
#
#     def debug_info(self) -> Dict[str, Any]:
#         with self._connect() as conn:
#             cur = conn.cursor()
#             cur.execute("SELECT @@SERVERNAME")
#             server = cur.fetchone()[0]
#             cur.execute("SELECT DB_NAME()")
#             db = cur.fetchone()[0]
#             cur.execute(f"SELECT COUNT(*) FROM {self.table_name} WHERE is_active = 1")
#             active_count = cur.fetchone()[0]
#         return {
#             "server": server,
#             "database": db,
#             "active_presets": int(active_count),
#             "table": self.table_name,
#         }
#
#     def _has_column(self, conn: pyodbc.Connection, column_name: str) -> bool:
#         """
#         Checks whether the configured table contains a given column.
#         Uses INFORMATION_SCHEMA.COLUMNS for compatibility.
#         """
#         # Split schema + table for INFORMATION_SCHEMA query
#         if "." in self.table_name:
#             schema, table = self.table_name.split(".", 1)
#         else:
#             schema, table = "dbo", self.table_name
#
#         sql = """
#         SELECT 1
#         FROM INFORMATION_SCHEMA.COLUMNS
#         WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ? AND COLUMN_NAME = ?
#         """
#         cur = conn.cursor()
#         cur.execute(sql, (schema, table, column_name))
#         return cur.fetchone() is not None
#
#     # ----------------------------
#     # Presets API
#     # ----------------------------
#     def get_active_presets(self) -> List[Dict[str, Any]]:
#         """
#         For dropdown. IMPORTANT: returns keys {id, name}
#         so templates should render p.id and p.name.
#         """
#         log.info("SQL presets: querying %s", self.table_name)
#
#         sql = f"""
#         SELECT preset_id, companyname, preset_display_name
#         FROM {self.table_name}
#         WHERE is_active = 1
#         ORDER BY companyname, preset_display_name
#         """
#         with self._connect() as conn:
#             cur = conn.cursor()
#             cur.execute(sql)
#             rows = cur.fetchall()
#
#             return [
#                 {"id": int(r.preset_id), "name": f"{r.companyname} — {r.preset_display_name}"}
#                 for r in rows
#             ]
#
#     def get_preset(self, preset_id: int) -> Optional[Preset]:
#         """
#         For pre-fill. This MUST include instruction_preset from DB.
#
#         Additionally supports reference options via:
#           - report_options JSON (preferred), or
#           - include_references/reference_format/citation_level columns
#
#         NOTE: Your Preset model must support one of:
#           - report_options: Optional[Dict[str, Any]]
#           OR
#           - include_references/reference_format/citation_level fields
#         """
#         with self._connect() as conn:
#             # Detect optional columns once per call (cheap and safe)
#             has_report_options = self._has_column(conn, "report_options")
#             has_include_refs = self._has_column(conn, "include_references")
#             has_ref_format = self._has_column(conn, "reference_format")
#             has_citation_level = self._has_column(conn, "citation_level")
#
#             optional_selects: List[str] = []
#             if has_report_options:
#                 optional_selects.append("report_options")
#             if has_include_refs:
#                 optional_selects.append("include_references")
#             if has_ref_format:
#                 optional_selects.append("reference_format")
#             if has_citation_level:
#                 optional_selects.append("citation_level")
#
#             optional_sql = ""
#             if optional_selects:
#                 optional_sql = ",\n            " + ",\n            ".join(optional_selects)
#
#             sql = f"""
#             SELECT
#                 preset_id,
#                 preset_display_name,
#                 competitor,
#                 baseline,
#                 instruction_preset,
#                 extra_instructions,
#                 source_file_path,
#                 web,
#                 processor
#                 {optional_sql}
#             FROM {self.table_name}
#             WHERE preset_id = ? AND is_active = 1
#             """
#
#             cur = conn.cursor()
#             cur.execute(sql, preset_id)
#             r = cur.fetchone()
#             if not r:
#                 return None
#
#             # Build report options consistently
#             report_options: Optional[Dict[str, Any]] = None
#
#             # A) Preferred: JSON report_options
#             if has_report_options:
#                 raw = getattr(r, "report_options", None)
#                 if raw:
#                     try:
#                         report_options = json.loads(str(raw))
#                     except Exception:
#                         log.warning(
#                             "Preset %s has invalid JSON in report_options; ignoring.",
#                             preset_id,
#                             exc_info=True,
#                         )
#                         report_options = None
#
#             # B) Fallback: explicit columns
#             # Only apply if JSON is absent
#             if report_options is None:
#                 include_references = None
#                 reference_format = None
#                 citation_level = None
#
#                 if has_include_refs:
#                     include_references = getattr(r, "include_references", None)
#                     # pyodbc may return bool/int for BIT
#                     if include_references is not None:
#                         include_references = bool(include_references)
#
#                 if has_ref_format:
#                     reference_format = getattr(r, "reference_format", None)
#                     if reference_format is not None:
#                         reference_format = str(reference_format)
#
#                 if has_citation_level:
#                     citation_level = getattr(r, "citation_level", None)
#                     if citation_level is not None:
#                         citation_level = str(citation_level)
#
#                 # Only set if any were present
#                 if include_references is not None or reference_format is not None or citation_level is not None:
#                     report_options = {
#                         "include_references": include_references if include_references is not None else False,
#                         "reference_format": reference_format or "appendix",
#                         "citation_level": citation_level or "section",
#                     }
#
#             # IMPORTANT:
#             # This assumes Preset has a `report_options` field.
#             # If your Preset model does not yet have it, add it there.
#             return Preset(
#                 id=int(r.preset_id),
#                 name=str(r.preset_display_name),
#                 competitor=str(r.competitor),
#                 baseline=(str(r.baseline) if r.baseline is not None else None),
#                 instruction_preset=(str(r.instruction_preset) if r.instruction_preset is not None else None),
#                 extra_instructions=(str(r.extra_instructions) if r.extra_instructions is not None else None),
#                 file=(str(r.source_file_path) if r.source_file_path is not None else None),
#                 web=(str(r.web) if r.web is not None else None),
#                 processor=(str(r.processor) if r.processor is not None else None),
#                 report_options=report_options,
#             )
#
#
#
#
#
#
#
#
#
#
#
# # # sqlserver_presets.py
# # #
# # #
# # from __future__ import annotations
# #
# # import logging
# # from typing import Any, Dict, List, Optional
# #
# # import pyodbc
# #
# # from tga_cli.config.ini_config import load_sqlserver_settings
# # from tga_cli.domain.models import Preset
# # from tga_cli.ports.presets import PresetRepository
# #
# # log = logging.getLogger("tga_cli")
# #
# #
# # class SqlServerPresetRepository(PresetRepository):
# #     """
# #     SQL Server adapter for dbo.GapAnalysisPresets.
# #
# #     DB schema:
# #       preset_id             INT
# #       companyname           NVARCHAR(200)
# #       preset_display_name   NVARCHAR(200)
# #       competitor            NVARCHAR(500)
# #       baseline              NVARCHAR(500)
# #       instruction_preset    NVARCHAR(100)
# #       extra_instructions    NVARCHAR(MAX)
# #       source_file_path      NVARCHAR(500)
# #       web                   NVARCHAR(50)
# #       processor             NVARCHAR(100)
# #       is_active             BIT
# #     """
# #
# #     def __init__(self, ini_path: str, table_name: str = "dbo.GapAnalysisPresets"):
# #         self.ini_path = ini_path
# #         self.table_name = table_name
# #
# #     def _connect(self) -> pyodbc.Connection:
# #         s = load_sqlserver_settings(self.ini_path)
# #
# #         if not s.database:
# #             raise ValueError("INI missing sqlserver.database")
# #         if not s.username:
# #             raise ValueError("INI missing sqlserver.username")
# #         if not s.password:
# #             raise ValueError("INI missing sqlserver.password")
# #
# #         conn_str = (
# #             f"DRIVER={{{s.driver}}};"
# #             f"SERVER={s.server};"
# #             f"DATABASE={s.database};"
# #             f"UID={s.username};"
# #             f"PWD={s.password};"
# #             f"TrustServerCertificate={'yes' if s.trust_cert else 'no'};"
# #         )
# #         return pyodbc.connect(conn_str)
# #
# #     def debug_info(self) -> Dict[str, Any]:
# #         with self._connect() as conn:
# #             cur = conn.cursor()
# #             cur.execute("SELECT @@SERVERNAME")
# #             server = cur.fetchone()[0]
# #             cur.execute("SELECT DB_NAME()")
# #             db = cur.fetchone()[0]
# #             cur.execute(f"SELECT COUNT(*) FROM {self.table_name} WHERE is_active = 1")
# #             active_count = cur.fetchone()[0]
# #         return {"server": server, "database": db, "active_presets": int(active_count), "table": self.table_name}
# #
# #     def get_active_presets(self) -> List[Dict[str, Any]]:
# #         """
# #         For dropdown. IMPORTANT: returns keys {id, name}
# #         so templates should render p.id and p.name.
# #         """
# #         log.info("SQL presets: querying %s", self.table_name)
# #
# #         sql = f"""
# #         SELECT preset_id, companyname, preset_display_name
# #         FROM {self.table_name}
# #         WHERE is_active = 1
# #         ORDER BY companyname, preset_display_name
# #         """
# #         with self._connect() as conn:
# #             cur = conn.cursor()
# #             cur.execute(sql)
# #             rows = cur.fetchall()
# #
# #             return [
# #                 {
# #                     "id": int(r.preset_id),
# #                     "name": f"{r.companyname} — {r.preset_display_name}",
# #                 }
# #                 for r in rows
# #             ]
# #
# #     def get_preset(self, preset_id: int) -> Optional[Preset]:
# #         """
# #         For pre-fill. This MUST include instruction_preset from DB.
# #         """
# #         sql = f"""
# #         SELECT
# #             preset_id,
# #             preset_display_name,
# #             competitor,
# #             baseline,
# #             instruction_preset,
# #             extra_instructions,
# #             source_file_path,
# #             web,
# #             processor
# #         FROM {self.table_name}
# #         WHERE preset_id = ? AND is_active = 1
# #         """
# #         with self._connect() as conn:
# #             cur = conn.cursor()
# #             cur.execute(sql, preset_id)
# #             r = cur.fetchone()
# #             if not r:
# #                 return None
# #
# #             return Preset(
# #                 id=int(r.preset_id),
# #                 name=str(r.preset_display_name),
# #                 competitor=str(r.competitor),
# #                 baseline=(str(r.baseline) if r.baseline is not None else None),
# #                 instruction_preset=(str(r.instruction_preset) if r.instruction_preset is not None else None),
# #                 extra_instructions=(str(r.extra_instructions) if r.extra_instructions is not None else None),
# #                 file=(str(r.source_file_path) if r.source_file_path is not None else None),
# #                 web=(str(r.web) if r.web is not None else None),
# #                 processor=(str(r.processor) if r.processor is not None else None),
# #             )
