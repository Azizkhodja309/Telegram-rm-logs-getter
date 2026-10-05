"""
Sozlamalar, Telegramga kirish va chat tanlash.

Maxfiy qiymatlar faqat .env ichida turadi. API hash va 2FA paroli hech qachon
ekranga chiqarilmaydi. Ekranga chiqadigan matnlar i18n.py ichida.
"""

from __future__ import annotations

import os
import sys
from getpass import getpass
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import (
    ApiIdInvalidError,
    AuthKeyError,
    ChannelPrivateError,
    FloodWaitError,
    PasswordHashInvalidError,
    PhoneCodeEmptyError,
    PhoneCodeExpiredError,
    PhoneCodeInvalidError,
    PhoneNumberBannedError,
    PhoneNumberInvalidError,
    SessionPasswordNeededError,
)
from telethon.tl.types import Channel, Chat

from i18n import t

PROJECT_DIR = Path(__file__).resolve().parent
SESSION_SUFFIX = ".session"
DEFAULT_SESSION = "admin_log"
SAFE_NAME_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")


class ConfigError(Exception):
    """.env faylida muammo bor."""


class LoginError(Exception):
    """Telegramga kirish amalga oshmadi."""


# --------------------------------------------------------------------------
# Sozlamalar
# --------------------------------------------------------------------------
def load_config() -> tuple[int, str]:
    """TELEGRAM_API_ID / TELEGRAM_API_HASH ni .env dan o'qiydi (chiqarmaydi)."""
    env_file = PROJECT_DIR / ".env"
    if not env_file.exists():
        raise ConfigError(t("cfg.no_env", path=str(env_file)))

    load_dotenv(env_file)

    raw_id = (os.getenv("TELEGRAM_API_ID") or "").strip()
    api_hash = (os.getenv("TELEGRAM_API_HASH") or "").strip()

    if not raw_id or not api_hash:
        raise ConfigError(t("cfg.missing"))
    if raw_id == "12345678" or api_hash == "your_api_hash_here":
        raise ConfigError(t("cfg.example_values"))
    try:
        api_id = int(raw_id)
    except ValueError:
        raise ConfigError(t("cfg.id_not_number")) from None
    if len(api_hash) != 32:
        print(t("cfg.hash_len_warn"), file=sys.stderr)

    return api_id, api_hash


# --------------------------------------------------------------------------
# Sessiyalar (har bir akkaunt uchun alohida fayl)
# --------------------------------------------------------------------------
def session_file(name: str) -> Path:
    """Sessiya faylining to'liq manzili, masalan .../ishxona.session"""
    return PROJECT_DIR / (name + SESSION_SUFFIX)


def list_session_names() -> list[str]:
    """Loyiha papkasidagi saqlangan sessiyalar nomlari."""
    return sorted(p.stem for p in PROJECT_DIR.glob("*" + SESSION_SUFFIX))


def check_session_name(name: str) -> str:
    """Fayl nomi sifatida xavfsizligini tekshiradi."""
    name = name.strip()
    if not name:
        raise ValueError(t("session.name_empty"))
    if len(name) > 40:
        raise ValueError(t("session.name_too_long"))
    bad = sorted(set(name) - SAFE_NAME_CHARS)
    if bad:
        raise ValueError(
            t("session.name_bad_chars", chars=", ".join(repr(ch) for ch in bad))
        )
    return name


def delete_session(name: str) -> list[Path]:
    """Sessiya fayllarini o'chiradi (logout). O'chirilgan fayllarni qaytaradi."""
    removed = []
    for path in (session_file(name), PROJECT_DIR / (name + SESSION_SUFFIX + "-journal")):
        if path.exists():
            path.unlink()
            removed.append(path)
    return removed


# --------------------------------------------------------------------------
# Telegramga kirish
# --------------------------------------------------------------------------
def create_client(
    api_id: int, api_hash: str, session_name: str = DEFAULT_SESSION
) -> TelegramClient:
    """Mijozni yaratadi. flood_sleep_threshold=0 - FloodWait'ni o'zimiz boshqaramiz."""
    client = TelegramClient(str(PROJECT_DIR / session_name), api_id, api_hash)
    client.flood_sleep_threshold = 0
    return client


async def login(client: TelegramClient) -> None:
    """
    Shaxsiy akkaunt bilan kirish (bot token EMAS).

    Birinchi marta: telefon raqam -> kod -> kerak bo'lsa 2FA paroli.
    Keyin sessiya faylda saqlanadi va bu qadamlar boshqa takrorlanmaydi.
    """
    try:
        await client.connect()
    except OSError as exc:
        raise LoginError(t("login.connect_fail", error=str(exc))) from exc

    if await client.is_user_authorized():
        me = await client.get_me()
        print(t("login.already", user=_describe_user(me)) + "\n")
        return

    print(t("login.first_run"))
    print(t("login.first_run_note") + "\n")

    phone = input(t("login.phone_prompt")).strip()
    if not phone:
        raise LoginError(t("login.no_phone"))

    try:
        await client.send_code_request(phone)
    except ApiIdInvalidError:
        raise LoginError(t("login.api_invalid")) from None
    except PhoneNumberInvalidError:
        raise LoginError(t("login.phone_invalid")) from None
    except PhoneNumberBannedError:
        raise LoginError(t("login.phone_banned")) from None
    except FloodWaitError as exc:
        raise LoginError(t("login.flood", seconds=exc.seconds)) from None

    print(t("login.code_sent"))

    for attempt in range(3):
        code = input(t("login.code_prompt")).strip()
        try:
            await client.sign_in(phone=phone, code=code)
            break
        except (PhoneCodeInvalidError, PhoneCodeEmptyError):
            print(t("login.code_wrong", left=2 - attempt))
        except PhoneCodeExpiredError:
            raise LoginError(t("login.code_expired")) from None
        except SessionPasswordNeededError:
            await _sign_in_with_password(client)
            break
    else:
        raise LoginError(t("login.code_failed"))

    me = await client.get_me()
    print("\n" + t("login.signed_in", user=_describe_user(me)) + "\n")


async def _sign_in_with_password(client: TelegramClient) -> None:
    """Ikki qadamli tasdiqlash. Parol yashirin o'qiladi va chiqarilmaydi."""
    print("\n" + t("login.2fa_enabled"))
    for attempt in range(3):
        password = getpass(t("login.2fa_prompt"))
        try:
            await client.sign_in(password=password)
            return
        except PasswordHashInvalidError:
            print(t("login.2fa_wrong", left=2 - attempt))
        finally:
            del password
    raise LoginError(t("login.2fa_failed"))


def _describe_user(user) -> str:
    name = " ".join(p for p in [user.first_name, user.last_name] if p) or t("login.noname")
    return name + " (id=" + str(user.id) + ")"


# --------------------------------------------------------------------------
# Chat tanlash
# --------------------------------------------------------------------------
async def list_chats(client: TelegramClient, limit: int = 200) -> list:
    """Bu akkaunt ko'ra oladigan guruh / supergroup / kanallar."""
    chats = []
    async for dialog in client.iter_dialogs(limit=limit):
        if dialog.is_group or dialog.is_channel:
            chats.append(dialog)
    return chats


def print_chats(chats: list) -> None:
    if not chats:
        print(t("chat.none_found"))
        return
    print(t("chat.available") + "\n")
    for index, dialog in enumerate(chats, start=1):
        print(str(index) + ". " + str(dialog.name))
        print("   ID: " + str(dialog.id) + "   (" + chat_kind(dialog.entity) + ")")
        print()


def chat_kind(entity) -> str:
    if isinstance(entity, Chat):
        return t("chat.kind_basic")
    if isinstance(entity, Channel):
        return t("chat.kind_super") if entity.megagroup else t("chat.kind_channel")
    return type(entity).__name__


async def resolve_chat(client: TelegramClient, chats: list, answer: str):
    """
    Ro'yxatdagi raqam, @username yoki raqamli chat ID ni qabul qiladi.

    Ro'yxat chegarasiga tushadigan oddiy raqam - ro'yxat o'rni deb olinadi;
    boshqa har qanday butun son - chat ID deb olinadi.
    """
    answer = answer.strip()
    if not answer:
        raise ValueError(t("chat.nothing_entered"))

    if answer.isdigit() and 1 <= int(answer) <= len(chats):
        return chats[int(answer) - 1].entity

    as_int = None
    try:
        as_int = int(answer)
    except ValueError:
        pass

    target = as_int if as_int is not None else answer.lstrip("@")
    try:
        return await client.get_entity(target)
    except ChannelPrivateError:
        raise ValueError(t("chat.private_err")) from None
    except AuthKeyError:
        raise ValueError(t("chat.session_invalid")) from None
    except (ValueError, TypeError):
        raise ValueError(t("chat.not_found_err", answer=answer)) from None


async def describe_admin_rights(client: TelegramClient, entity) -> str:
    """Bu akkaunt admin logni o'qiy oladimi - imkon qadar tekshiradi."""
    try:
        perms = await client.get_permissions(entity, "me")
    except Exception:
        return t("rights.unknown")
    if getattr(perms, "is_creator", False):
        return t("rights.creator")
    if getattr(perms, "is_admin", False):
        return t("rights.admin")
    return t("rights.not_admin")
