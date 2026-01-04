# sqlserver_presets.py
#
#
from __future__ import annotations

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

    DB schema:
      preset_id             INT
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
        return {"server": server, "database": db, "active_presets": int(active_count), "table": self.table_name}

    def get_active_presets(self) -> List[Dict[str, Any]]:
        """
        For dropdown. IMPORTANT: returns keys {id, name}
        so templates should render p.id and p.name.
        """
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
                {
                    "id": int(r.preset_id),
                    "name": f"{r.companyname} — {r.preset_display_name}",
                }
                for r in rows
            ]

    def get_preset(self, preset_id: int) -> Optional[Preset]:
        """
        For pre-fill. This MUST include instruction_preset from DB.
        """
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
        FROM {self.table_name}
        WHERE preset_id = ? AND is_active = 1
        """
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(sql, preset_id)
            r = cur.fetchone()
            if not r:
                return None

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
            )
