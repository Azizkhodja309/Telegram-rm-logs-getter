"""
Telegram admin log tekshiruvchisi: siz administrator bo'lgan guruhdagi
"xabar o'chirildi" hodisalarini topadi.

Ishga tushirish:  run.bat   (yoki .venv/Scripts/python.exe main.py)
Tillar:           uz / ru / en - dastur boshida so'raydi, yoki --lang bilan.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import datetime

import i18n
from i18n import t
from telethon import utils
from telethon.errors import (
    ChannelPrivateError,
    ChatAdminRequiredError,
    FloodWaitError,
    RPCError,
)
from telethon.tl.types import Channel, Chat

import admin_log
import exporter
import telegram_client as tc

LINE = "-" * 68
CSV_NAME = "deleted_messages.csv"


def header(text: str) -> None:
    print("\n" + LINE)
    print(text)
    print(LINE)


def is_yes(answer: str) -> bool:
    """Har qanday tildagi 'ha' javobi."""
    return answer.strip().lower() in i18n.yes_values()


def yn() -> dict:
    """'[ha/yo'q]' ko'rinishidagi so'rov uchun qiymatlar."""
    return {"yes": t("ui.yes"), "no": t("ui.no")}


# --------------------------------------------------------------------------
# Akkaunt (sessiya) tanlash
# --------------------------------------------------------------------------
def choose_session() -> str:
    """
    Qaysi akkaunt bilan ishlashni so'raydi.

    Har bir akkaunt o'z sessiya faylida saqlanadi (masalan ishxona.session),
    shuning uchun bir nechta akkauntni yonma-yon ishlatish mumkin: kodni
    har bir akkaunt uchun faqat bir martadan kiritasiz.
    """
    while True:
        names = tc.list_session_names()

        if not names:
            print("\n" + t("session.none"))
            return ask_new_session_name()

        header(t("session.header"))
        print(t("session.saved_list") + "\n")
        for index, name in enumerate(names, start=1):
            print("  " + str(index) + ". " + name)
        print("\n" + t("session.opt_new"))
        print(t("session.opt_del"))

        answer = input("\n" + t("session.select")).strip().lower()

        if answer == "y":
            return ask_new_session_name()
        if answer == "o":
            forget_session(names)
            continue
        if answer.isdigit() and 1 <= int(answer) <= len(names):
            return names[int(answer) - 1]
        print(t("session.bad_choice"))


def ask_new_session_name() -> str:
    """Yangi akkaunt uchun nom so'raydi (fayl nomi sifatida ishlatiladi)."""
    print("\n" + t("session.new_name_intro"))
    while True:
        raw = input(t("session.name_prompt", default=tc.DEFAULT_SESSION)).strip()
        raw = raw or tc.DEFAULT_SESSION
        try:
            name = tc.check_session_name(raw)
        except ValueError as exc:
            print("  " + str(exc))
            continue
        if name in tc.list_session_names():
            print(t("session.name_taken", name=name))
            continue
        return name


def forget_session(names: list[str]) -> None:
    """Sessiya faylini o'chiradi, ya'ni o'sha akkauntdan chiqadi."""
    print("\n" + t("session.del_which"))
    for index, name in enumerate(names, start=1):
        print("  " + str(index) + ". " + name)
    answer = input(t("session.del_prompt")).strip()
    if not answer.isdigit() or not 1 <= int(answer) <= len(names):
        print(t("ui.cancelled"))
        return

    name = names[int(answer) - 1]
    print("\n" + t("session.del_warn", name=name))
    if not is_yes(input(t("session.del_confirm", **yn()))):
        print(t("ui.cancelled"))
        return

    removed = tc.delete_session(name)
    if removed:
        print(t("session.deleted", files=", ".join(p.name for p in removed)))
    else:
        print(t("session.not_found"))


# --------------------------------------------------------------------------
# Chat tanlash
# --------------------------------------------------------------------------
async def pick_chat(client):
    chats = await tc.list_chats(client)
    tc.print_chats(chats)
    print(t("chat.list_hint"))

    while True:
        answer = input(t("chat.select"))
        try:
            entity = await tc.resolve_chat(client, chats, answer)
        except ValueError as exc:
            print("  " + str(exc) + "\n")
            continue

        title = getattr(entity, "title", None) or t("chat.nameless")

        print("\n" + t("chat.selected"))
        print(t("chat.f_title") + str(title))
        print(t("chat.f_id") + str(utils.get_peer_id(entity)))
        print(t("chat.f_type") + tc.chat_kind(entity))

        if isinstance(entity, Chat):
            print(t("chat.basic_warning"))
        elif isinstance(entity, Channel):
            rights = await tc.describe_admin_rights(client, entity)
            print(t("chat.f_rights") + rights)
            if rights == t("rights.not_admin"):
                print(t("chat.not_admin_warning"))

        if is_yes(input("\n" + t("chat.confirm", **yn()))):
            return entity
        print()


# --------------------------------------------------------------------------
# Tarixiy ma'lumot testi
# --------------------------------------------------------------------------
def report_horizon(horizon, start, end) -> None:
    """
    Telegram qanchagacha orqaga o'qishga ruxsat berganini aytadi va bu ma'lumot
    NIMANI isbotlab, nimani isbotlamasligini ochiq yozadi.

    Telegram API hech qanday "saqlash muddati" xabarini yubormaydi. Pastdagi
    hamma xulosa - shu dasturning server qaytargan yozuvlarga qaragan talqini.
    """
    header(t("horizon.header"))
    print(
        t(
            "horizon.requested",
            start=start.strftime("%Y-%m-%d %H:%M"),
            end=end.strftime("%Y-%m-%d %H:%M"),
        )
    )
    print(t("horizon.entries", total=horizon["total"], pages=horizon["pages"]))

    if horizon["total"] == 0:
        print(t("horizon.oldest_none"))
        print("\n" + t("horizon.measured_nothing"))
        return

    oldest = horizon["oldest"]
    print(t("horizon.oldest", date=oldest.strftime("%Y-%m-%d %H:%M:%S")))
    print(t("horizon.newest", date=horizon["newest"].strftime("%Y-%m-%d %H:%M:%S")))

    hours = (datetime.now().astimezone() - oldest).total_seconds() / 3600
    print(t("horizon.age", hours="%.1f" % hours))

    if oldest <= start:
        print("\n" + t("horizon.full_range"))
        return

    print(
        "\n"
        + t(
            "horizon.measured_cut",
            oldest=oldest.strftime("%Y-%m-%d %H:%M:%S"),
            start=start.strftime("%Y-%m-%d %H:%M"),
        )
    )

    # Bu haqiqatan saqlash muddati devorimi yoki shunchaki jim guruhmi?
    if hours >= admin_log.RETENTION_HOURS * 0.8:
        print("\n" + t("horizon.near_window", hours=admin_log.RETENTION_HOURS))
    else:
        print("\n" + t("horizon.not_measured"))
        if horizon["total"] < 10:
            print(
                t("horizon.thin_log", total=horizon["total"], hours="%.1f" % hours)
            )
        print(t("horizon.quiet_chat"))
        print("\n" + t("horizon.how_to_measure", hours=admin_log.RETENTION_HOURS))

    print("\n" + t("horizon.reference", hours=admin_log.RETENTION_HOURS))


# --------------------------------------------------------------------------
# Asosiy oqim
# --------------------------------------------------------------------------
async def run(session_name: str | None = None) -> int:
    header(t("app.title"))

    try:
        api_id, api_hash = tc.load_config()
    except tc.ConfigError as exc:
        print(t("cfg.problem") + "\n" + str(exc))
        return 1

    if session_name is None:
        session_name = choose_session()
    else:
        try:
            session_name = tc.check_session_name(session_name)
        except ValueError as exc:
            print(t("session.bad_cli_name", error=str(exc)))
            return 1

    print("\n" + t("session.current", name=session_name))
    client = tc.create_client(api_id, api_hash, session_name)

    try:
        try:
            await tc.login(client)
        except tc.LoginError as exc:
            print(t("login.failed") + "\n" + str(exc))
            return 1

        entity = await pick_chat(client)
        if not isinstance(entity, Channel):
            return 1

        # Orqaga qancha o'qish mumkinligi sana oralig'iga bog'liq emas, shuning
        # uchun bir marta o'lchab, har bir so'rovda qayta ishlatamiz.
        try:
            horizon = await admin_log.probe_log_horizon(client, entity)
        except admin_log.NotAdminError as exc:
            print("\n" + str(exc))
            return 1

        print("\n" + t("ui.ctrl_c"))

        while True:
            if await query_once(client, entity, horizon) != 0:
                return 1
    finally:
        await client.disconnect()


async def query_once(client, entity, horizon) -> int:
    """Bitta so'rov: sanani so'rash, o'qish, ko'rsatish, CSV taklif qilish."""
    start, end = admin_log.ask_date_range()
    print(
        "\n"
        + t(
            "date.range",
            start=start.strftime("%Y-%m-%d %H:%M:%S"),
            end=end.strftime("%Y-%m-%d %H:%M:%S"),
        )
    )

    try:
        events, stats = await admin_log.fetch_deleted_events(client, entity, start, end)
    except admin_log.NotAdminError as exc:
        print("\n" + str(exc))
        return 1
    except ChatAdminRequiredError:
        print("\n" + t("err.refused_admin"))
        return 1
    except ChannelPrivateError:
        print("\n" + t("err.private"))
        return 1
    except FloodWaitError as exc:
        print("\n" + t("err.flood", seconds=exc.seconds))
        return 1
    except RPCError as exc:
        print("\n" + t("err.rpc", name=type(exc).__name__, error=str(exc)))
        return 1

    header(t("event.header"))
    if not events:
        print(t("event.none_found"))
        print(t("event.scanned", pages=stats["pages"], scanned=stats["scanned"]))
    else:
        for ev in events:
            admin_log.print_event(ev)
        print(
            t(
                "event.total",
                n=len(events),
                pages=stats["pages"],
                scanned=stats["scanned"],
            )
        )
        if stats["hit_page_cap"]:
            print(t("event.page_cap", pages=admin_log.MAX_PAGES))

    report_horizon(horizon, start, end)

    if events:
        target = exporter.default_path(CSV_NAME)
        print("\n" + t("csv.note"))
        print("  " + str(target))
        if is_yes(input(t("csv.prompt", **yn()))):
            try:
                path = exporter.export_csv(events, target)
                print("\n" + t("csv.saved", path=str(path)))
                print(t("csv.open_hint"))
            except OSError as exc:
                print(t("csv.fail", error=str(exc)))
        else:
            print(t("csv.not_saved"))

    print("\n" + LINE)
    print(t("ui.another_range"))
    return 0


def main() -> int:
    # Til tanlovi argparse'dan oldin kerak, chunki yordam matni ham tarjimali.
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument("--lang", choices=i18n.CODES)
    known, _ = pre.parse_known_args()

    if known.lang:
        i18n.set_language(known.lang)
    else:
        try:
            i18n.ask_language()
        except (KeyboardInterrupt, EOFError):
            print()
            return 130

    parser = argparse.ArgumentParser(description=t("cli.description"))
    parser.add_argument("--session", metavar="NAME", help=t("cli.session_help"))
    parser.add_argument("--lang", choices=i18n.CODES, help=t("cli.lang_help"))
    args = parser.parse_args()

    try:
        return asyncio.run(run(args.session))
    except KeyboardInterrupt:
        print("\n" + t("ui.cancelled"))
        return 130
    except EOFError:
        print("\n" + t("ui.eof"))
        return 1


if __name__ == "__main__":
    sys.exit(main())
