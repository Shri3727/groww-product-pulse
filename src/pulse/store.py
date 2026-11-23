"""Approval-gated log: notes append and an email draft. Nothing is sent."""

from __future__ import annotations

import json
import os
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]


def _output_dir() -> Path:
    """Vercel can read the project files and can write only under /tmp."""
    if os.getenv("VERCEL"):
        path = Path("/tmp/pulse")
    else:
        path = _ROOT / "deliverables" / "pulse"
    path.mkdir(parents=True, exist_ok=True)
    return path


def email_draft(package: dict) -> str:
    bullets = "\n".join(f"- {line}" for line in package["explanation_bullets"])
    links = "\n".join(package["source_links"])
    return f"""Subject: Weekly Product Pulse + Customer Clarification — Equity brokerage and sell-side charges

Weekly product pulse
{package['weekly_pulse'].strip()}

Fee explanation (reusable support snippet)
{bullets}

Last checked: {package['last_checked']}
{links}

This is a draft. It was not sent.
"""


def notes_entry(package: dict) -> str:
    payload = {
        "date": package["date"],
        "top_themes": package["top_themes"],
        "weekly_pulse": package["weekly_pulse"].strip(),
        "identified_fee_issue": package["identified_fee_issue"],
        "explanation_bullets": package["explanation_bullets"],
        "source_links": package["source_links"],
    }
    body = json.dumps(payload, indent=2, ensure_ascii=False)
    return f"\n\n## {package['date']}\n\n```json\n{body}\n```\n"


def write_pulse_preview(package: dict) -> Path:
    if os.getenv("VERCEL"):
        return _ROOT / "deliverables" / "pulse" / "weekly_product_pulse.md"
    folder = _output_dir()
    pulse_path = folder / "weekly_product_pulse.md"
    sources_path = folder / "sources.md"
    pulse_path.write_text(package["weekly_pulse"], encoding="utf-8")
    lines = ["# Sources", ""]
    for url in package["source_list"]:
        lines.append(f"- {url}")
    lines.append("")
    lines.append(f"Last checked: {package['last_checked']}")
    lines.append("")
    sources_path.write_text("\n".join(lines), encoding="utf-8")
    return pulse_path


def commit_approved(package: dict) -> dict[str, str]:
    """Append the notes entry and write the email draft. Call only after approval."""
    folder = _output_dir()
    notes_path = folder / "notes.md"
    email_path = folder / "email_draft.txt"
    if notes_path.exists():
        existing = notes_path.read_text(encoding="utf-8")
    else:
        bundled = _ROOT / "deliverables" / "pulse" / "notes.md"
        existing = bundled.read_text(encoding="utf-8") if bundled.exists() else "# Product pulse notes\n"
    notes_path.write_text(existing.rstrip() + notes_entry(package), encoding="utf-8")
    email_path.write_text(email_draft(package), encoding="utf-8")
    return {"notes": str(notes_path), "email_draft": str(email_path)}
