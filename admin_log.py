"""
Admin log o'qish: sana oraliqlari, sahifalash, FloodWait (so'rov chegarasi).

Ishlatilgan Telethon metodi: client.iter_admin_log(entity, limit=..., max_id=..., delete=True)
Asosdagi MTProto API:        channels.getAdminLog + ChannelAdminLogEventsFilter(delete=True)

O'chirish hodisasining xom ko'rinishi - ChannelAdminLogEventActionDeleteMessage,
uning .message maydonida o'chirilgan Message turadi (Telethon buni event.old deb
ham beradi). Ya'ni asl matnni Telegram O'ZI beradi - biz taxmin qilmaymiz.

Ekranga chiqadigan matnlar i18n.py ichida.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from telethon import utils
from telethon.errors import ChatAdminRequiredError, FloodWaitError

from i18n import t

PAGE_SIZE = 100
MAX_PAGES = 500

# Hujjatlarga ko'ra Telegram admin log yozuvlarini ~48 soat saqlaydi.
RETENTION_HOURS = 48


class NotAdminError(Exception):
    """Bu akkaunt shu chatning admin logini o'qiy olmaydi."""


# --------------------------------------------------------------------------
# Sana oraliqlari (kompyuterning mahalliy vaqti bo'yicha)
# --------------------------------------------------------------------------
def parse_date(text: str) -> date:
    try:
        return datetime.strptime(text.strip(), "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(t("date.bad_format", value=text.strip())) from None


def day_start(d: date) -> datetime:
    """Shu kunning 00:00:00 vaqti, mahalliy vaqt zonasida."""
    return datetime.combine(d, time.min).astimezone()


def day_end(d: date) -> datetime:
    """Shu kunning 23:59:59 vaqti, mahalliy vaqt zonasida."""
    return datetime.combine(d, time.max).astimezone()


def preset_range(choice: str) -> tuple[datetime, datetime]:
    now = datetime.now().astimezone()
    today = now.date()

    if choice == "1":
        return now - timedelta(hours=24), now
    if choice == "2":
        return now - timedelta(days=7), now
    if choice == "3":
        return day_start(today.replace(day=1)), now
    if choice == "4":
        this_month_first = today.replace(day=1)
        prev_month_last = this_month_first - timedelta(days=1)
        return day_start(prev_month_last.replace(day=1)), day_end(prev_month_last)
    raise ValueError(t("date.bad_choice"))


def custom_range() -> tuple[datetime, datetime]:
    start = parse_date(input(t("date.start_prompt")))
    end = parse_date(input(t("date.end_prompt")))
    if end < start:
        raise ValueError(t("date.end_before_start"))
    return day_start(start), day_end(end)


def ask_date_range() -> tuple[datetime, datetime]:
    print(t("date.menu"))
    while True:
        choice = input(t("date.select")).strip()
        try:
            if choice == "5":
                return custom_range()
            return preset_range(choice)
        except ValueError as exc:
            print("  " + str(exc))


# --------------------------------------------------------------------------
# Natija yozuvi
# --------------------------------------------------------------------------
@dataclass
class DeletedEvent:
    event_id: int
    when: datetime            # o'chirish qachon sodir bo'lgani (mahalliy vaqt)
    admin_id: int | None      # kim o'chirgani
    admin_name: str
    message_id: int | None    # o'chirilgan xabar
    message_date: datetime | None
    author_id: int | None     # xabarni asli kim yozgani
    author_name: str
    text: str                 # Telegram matn bermasa - bo'sh
    media: str                # media bo'lmasa - bo'sh
    chat_id: int


# --------------------------------------------------------------------------
# Ism aniqlash (keshlanadi, imkon qadar)
# --------------------------------------------------------------------------
async def _name_of(client, cache: dict, peer_id, fallback: str) -> str:
    if peer_id is None:
        return fallback
    if peer_id in cache:
        return cache[peer_id]
    name = "id=" + str(peer_id)
    try:
        entity = await client.get_entity(peer_id)
        name = utils.get_display_name(entity) or name
    except Exception:
        pass
    cache[peer_id] = name
    return name


def _media_label(message) -> str:
    media = getattr(message, "media", None)
    if media is None:
        return ""
    return type(media).__name__.replace("MessageMedia", "")


# --------------------------------------------------------------------------
# Sahifalab o'qish
# --------------------------------------------------------------------------
async def fetch_deleted_events(client, entity, start: datetime, end: datetime):
    """
    Admin logni yangilaridan eskilariga qarab, sahifa-sahifa o'qiydi. To'xtaydi:
    boshlanish sanasidan o'tib ketganda yoki Telegram boshqa hodisa bermaganda.

    Qaytaradi: (hodisalar, statistika).
    """
    chat_id = utils.get_peer_id(entity)
    cache: dict = {}
    events: list[DeletedEvent] = []

    max_id = 0
    pages = 0
    scanned = 0
    oldest_seen: datetime | None = None
    reached_start = False

    print("\n" + t("fetch.reading"))

    while pages < MAX_PAGES:
        page = []
        try:
            async for raw in client.iter_admin_log(
                entity, limit=PAGE_SIZE, max_id=max_id, delete=True
            ):
                page.append(raw)
        except FloodWaitError as exc:
            print("\n" + t("fetch.flood"))
            print(t("fetch.flood_wait", seconds=exc.seconds))
            await asyncio.sleep(exc.seconds + 1)
            print(t("fetch.flood_continue") + "\n")
            continue  # max_id o'zgarmaydi, yarim sahifadan hech narsa olinmadi
        except ChatAdminRequiredError:
            raise NotAdminError(t("fetch.not_admin")) from None

        if not page:
            break

        pages += 1
        for raw in page:
            scanned += 1
            when = raw.date.astimezone()
            if oldest_seen is None or when < oldest_seen:
                oldest_seen = when

            if when < start:
                reached_start = True
                break
            if when > end:
                continue

            message = getattr(raw.action, "message", None) or raw.old
            message_id = getattr(message, "id", None)
            message_date = getattr(message, "date", None)
            if message_date is not None:
                message_date = message_date.astimezone()

            author_id = None
            from_id = getattr(message, "from_id", None)
            if from_id is not None:
                try:
                    author_id = utils.get_peer_id(from_id)
                except Exception:
                    author_id = None

            events.append(
                DeletedEvent(
                    event_id=raw.id,
                    when=when,
                    admin_id=raw.user_id,
                    admin_name=await _name_of(
                        client, cache, raw.user_id, t("fetch.unknown_admin")
                    ),
                    message_id=message_id,
                    message_date=message_date,
                    author_id=author_id,
                    author_name=await _name_of(
                        client, cache, author_id, t("fetch.unknown_author")
                    ),
                    text=(getattr(message, "message", None) or ""),
                    media=_media_label(message) if message is not None else "",
                    chat_id=chat_id,
                )
            )

        print(
            t(
                "fetch.page",
                page=pages,
                count=len(page),
                oldest=oldest_seen.strftime("%Y-%m-%d %H:%M:%S"),
            )
        )

        if reached_start:
            break
        max_id = page[-1].id

    stats = {
        "pages": pages,
        "scanned": scanned,
        "oldest_seen": oldest_seen,
        "reached_start": reached_start,
        "hit_page_cap": pages >= MAX_PAGES,
    }
    return events, stats


async def probe_log_horizon(client, entity):
    """
    Telegram SHU chatning admin logini qanchagacha orqaga o'qishga ruxsat beradi?

    Filtrsiz (barcha amal turlari) butun logni oxirigacha o'qib, server hali ham
    qaytarishga tayyor bo'lgan eng eski yozuvni topadi. "Eski hodisalar bormi?"
    degan savolga aynan shu javob beradi.
    """
    oldest: datetime | None = None
    newest: datetime | None = None
    total = 0
    max_id = 0
    pages = 0

    while pages < MAX_PAGES:
        page = []
        try:
            async for raw in client.iter_admin_log(entity, limit=PAGE_SIZE, max_id=max_id):
                page.append(raw)
        except FloodWaitError as exc:
            print("\n" + t("fetch.flood"))
            print(t("fetch.flood_wait", seconds=exc.seconds))
            await asyncio.sleep(exc.seconds + 1)
            continue
        except ChatAdminRequiredError:
            raise NotAdminError(t("fetch.not_admin_short")) from None

        if not page:
            break
        pages += 1
        for raw in page:
            total += 1
            when = raw.date.astimezone()
            if oldest is None or when < oldest:
                oldest = when
            if newest is None or when > newest:
                newest = when
        max_id = page[-1].id

    return {"total": total, "oldest": oldest, "newest": newest, "pages": pages}


# --------------------------------------------------------------------------
# Ekranga chiqarish
# --------------------------------------------------------------------------
def print_event(ev: DeletedEvent) -> None:
    print("[" + ev.when.strftime("%Y-%m-%d %H:%M:%S") + "]")
    print(t("event.action"))
    print(t("event.admin_user", name=ev.admin_name))
    print(
        t(
            "event.msg_id",
            id=str(ev.message_id) if ev.message_id else t("event.not_given"),
        )
    )
    print(t("event.deleted_by", name=ev.admin_name, id=ev.admin_id))
    print(
        t(
            "event.author",
            name=ev.author_name,
            id=(" (id=" + str(ev.author_id) + ")") if ev.author_id else "",
        )
    )
    if ev.message_date:
        print(t("event.sent_at", date=ev.message_date.strftime("%Y-%m-%d %H:%M:%S")))
    if ev.text:
        print(t("event.text", text=repr(ev.text)))
    else:
        print(t("event.no_text"))
    if ev.media:
        print(t("event.media", media=ev.media))
    print(t("event.event_id", id=ev.event_id))
    print()
