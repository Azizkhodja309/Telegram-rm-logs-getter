"""O'chirilgan xabar hodisalarini CSV faylga saqlash."""

from __future__ import annotations

import csv
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent

# Ustun nomlari ataylab inglizcha qoldirilgan (texnik format).
COLUMNS = [
    "date",
    "action",
    "admin_id",
    "admin_name",
    "message_id",
    "chat_id",
    "message_text",
    # Telegram o'chirish hodisasi uchun beradigan qo'shimcha ma'lumot
    "author_id",
    "author_name",
    "message_date",
    "media",
    "event_id",
]


def default_path(name: str = "deleted_messages.csv") -> Path:
    """Fayl loyiha papkasining ichiga saqlanadi - topish oson bo'lishi uchun."""
    return PROJECT_DIR / name


def export_csv(events, path=None) -> Path:
    """Hodisalarni Excel to'g'ri ochadigan UTF-8 CSV faylga yozadi."""
    out = Path(path).resolve() if path else default_path()
    # utf-8-sig - Windows'dagi Excel o'zbekcha harflarni to'g'ri ko'rsatishi uchun
    with out.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(COLUMNS)
        for ev in events:
            writer.writerow(
                [
                    ev.when.strftime("%Y-%m-%d %H:%M:%S"),
                    "MESSAGE_DELETED",
                    ev.admin_id if ev.admin_id is not None else "",
                    ev.admin_name,
                    ev.message_id if ev.message_id is not None else "",
                    ev.chat_id,
                    ev.text,
                    ev.author_id if ev.author_id is not None else "",
                    ev.author_name,
                    ev.message_date.strftime("%Y-%m-%d %H:%M:%S") if ev.message_date else "",
                    ev.media,
                    ev.event_id,
                ]
            )
    return out
