#email_smtp.py             # smtplib adapter

from __future__ import annotations

import re
import smtplib
from email.message import EmailMessage
from pathlib import Path

from tga_cli.config.ini_config import EmailSettings
from tga_cli.domain.errors import FatalError


class SmtpEmailSender:
    def __init__(self, settings: EmailSettings):
        self.s = settings

    def send(self, attachment_paths: list[Path]) -> None:
        s = self.s
        required = {
            "smtp_server": s.smtp_server,
            "smtp_user": s.smtp_user,
            "smtp_password": s.smtp_password,
            "from_email": s.from_email,
            "to_email": s.to_email,
        }
        missing = [k for k, v in required.items() if not v]
        if missing:
            raise FatalError(f"Email enabled but missing: {', '.join(missing)}")

        recipients = [x.strip() for x in re.split(r"[;,]", s.to_email or "") if x.strip()]

        msg = EmailMessage()
        msg["Subject"] = s.subject
        msg["From"] = s.from_email
        msg["To"] = ", ".join(recipients)
        msg.set_content("Please find attached the analysis reports.")

        for path in attachment_paths:
            if not path.exists():
                continue

            data = path.read_bytes()
            suffix = path.suffix.lower()

            if suffix == ".md":
                maintype, subtype = "text", "markdown"
            elif suffix == ".html":
                maintype, subtype = "text", "html"
            elif suffix == ".docx":
                maintype, subtype = "application", "vnd.openxmlformats-officedocument.wordprocessingml.document"
            elif suffix == ".pptx":
                maintype, subtype = "application", "vnd.openxmlformats-officedocument.presentationml.presentation"
            else:
                maintype, subtype = "application", "octet-stream"

            msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=path.name)

        with smtplib.SMTP(s.smtp_server, s.smtp_port, timeout=30) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(s.smtp_user, s.smtp_password)
            smtp.send_message(msg)
