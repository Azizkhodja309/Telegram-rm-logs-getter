"""
Tillar / Языки / Languages: uz, ru, en.

Barcha ekranga chiqadigan matnlar shu faylda. Yangi til qo'shish uchun har bir
kalitga yangi til kodini qo'shish kifoya.

Ishlatilishi:
    from i18n import t
    print(t("app.title"))
    print(t("login.flood", seconds=37))
"""

from __future__ import annotations

LANGUAGES = [
    ("uz", "O'zbekcha"),
    ("ru", "Russkiy / Русский"),
    ("en", "English"),
]
DEFAULT = "uz"
CODES = [code for code, _ in LANGUAGES]

_current = DEFAULT


def set_language(code: str) -> None:
    global _current
    if code not in CODES:
        raise ValueError("Unknown language code: " + code)
    _current = code


def current() -> str:
    return _current


def t(key: str, **kw) -> str:
    """Kalit bo'yicha matn. Til topilmasa - o'zbekchaga qaytadi."""
    row = TEXTS.get(key)
    if row is None:
        return key  # tarjima qilinmagan kalit - kalitning o'zini ko'rsatamiz
    text = row.get(_current) or row[DEFAULT]
    return text.format(**kw) if kw else text


def ask_language() -> str:
    """Dastur boshida tilni so'raydi. Menyu uchta tilda ko'rsatiladi."""
    line = "=" * 68
    print("\n" + line)
    print("  Til / Язык / Language")
    print(line)
    for index, (_code, label) in enumerate(LANGUAGES, start=1):
        print("  " + str(index) + ". " + label)
    print()

    while True:
        answer = input("Tanlang / Выберите / Select [1-3]: ").strip().lower()
        if answer.isdigit() and 1 <= int(answer) <= len(LANGUAGES):
            code = LANGUAGES[int(answer) - 1][0]
            set_language(code)
            return code
        if answer in CODES:
            set_language(answer)
            return answer
        print("  1, 2, 3 / uz, ru, en")


def yes_values() -> set[str]:
    """Hamma tildagi 'ha' javoblari."""
    return {"h", "ha", "y", "yes", "d", "da", "д", "да"}


# --------------------------------------------------------------------------
# Matnlar
# --------------------------------------------------------------------------
TEXTS: dict[str, dict[str, str]] = {
    # ---------------- umumiy / общее / general ----------------
    "app.title": {
        "uz": "TELEGRAM ADMIN LOG - O'CHIRILGAN XABARLARNI TEKSHIRISH",
        "ru": "TELEGRAM ADMIN LOG - ПОИСК УДАЛЁННЫХ СООБЩЕНИЙ",
        "en": "TELEGRAM ADMIN LOG - DELETED MESSAGE INSPECTOR",
    },
    "ui.yes": {"uz": "ha", "ru": "да", "en": "y"},
    "ui.no": {"uz": "yo'q", "ru": "нет", "en": "n"},
    "ui.ctrl_c": {
        "uz": "Chiqish uchun istalgan paytda Ctrl+C bosing.",
        "ru": "Для выхода в любой момент нажмите Ctrl+C.",
        "en": "Press Ctrl+C at any time to quit.",
    },
    "ui.another_range": {
        "uz": "Yana boshqa sana oralig'i? (chiqish uchun Ctrl+C)",
        "ru": "Ещё один период? (для выхода Ctrl+C)",
        "en": "Another date range? (Ctrl+C to quit)",
    },
    "ui.cancelled": {"uz": "Bekor qilindi.", "ru": "Отменено.", "en": "Cancelled."},
    "ui.eof": {
        "uz": "Kiritish oqimi tugadi (dastur javob kutayotgan edi).",
        "ru": "Поток ввода закончился (программа ждала ответа).",
        "en": "Input stream ended while the program was waiting for an answer.",
    },
    # ---------------- sozlamalar / настройки / config ----------------
    "cfg.problem": {
        "uz": "Sozlamada muammo:",
        "ru": "Проблема в настройках:",
        "en": "Configuration problem:",
    },
    "cfg.no_env": {
        "uz": (
            ".env fayli topilmadi: {path}\n"
            ".env.example ni .env nomi bilan ko'chirib, API ID va API hash yozing.\n"
            "Ularni https://my.telegram.org -> API development tools dan olasiz."
        ),
        "ru": (
            "Файл .env не найден: {path}\n"
            "Скопируйте .env.example в .env и впишите API ID и API hash.\n"
            "Получить их можно на https://my.telegram.org -> API development tools."
        ),
        "en": (
            ".env not found at {path}\n"
            "Copy .env.example to .env and fill in your API ID and API hash.\n"
            "You can create them at https://my.telegram.org -> API development tools."
        ),
    },
    "cfg.missing": {
        "uz": ".env ichida TELEGRAM_API_ID va/yoki TELEGRAM_API_HASH yo'q.",
        "ru": "В .env отсутствует TELEGRAM_API_ID и/или TELEGRAM_API_HASH.",
        "en": "TELEGRAM_API_ID and/or TELEGRAM_API_HASH is missing from .env.",
    },
    "cfg.example_values": {
        "uz": (
            "Siz hali .env.example dagi namuna qiymatlarni ishlatayapsiz.\n"
            ".env ichiga o'zingizning API ID va API hash'ingizni yozing."
        ),
        "ru": (
            "Вы всё ещё используете примерные значения из .env.example.\n"
            "Впишите в .env свои API ID и API hash."
        ),
        "en": (
            "You are still using the example values from .env.example.\n"
            "Put your own API ID and API hash into .env."
        ),
    },
    "cfg.id_not_number": {
        "uz": "TELEGRAM_API_ID faqat raqamlardan iborat bo'lishi kerak, masalan 1234567.",
        "ru": "TELEGRAM_API_ID должен состоять только из цифр, например 1234567.",
        "en": "TELEGRAM_API_ID must be a number (digits only), for example 1234567.",
    },
    "cfg.hash_len_warn": {
        "uz": (
            "Ogohlantirish: API hash odatda 32 belgidan iborat bo'ladi. "
            "Sizdagisi boshqa uzunlikda - .env ni tekshirib ko'ring."
        ),
        "ru": (
            "Предупреждение: API hash обычно состоит из 32 символов. "
            "У вас другая длина - проверьте .env."
        ),
        "en": (
            "Warning: the API hash is usually a 32-character string. "
            "Yours has a different length - double-check .env."
        ),
    },
    # ---------------- kirish / вход / login ----------------
    "login.failed": {
        "uz": "Kirish amalga oshmadi:",
        "ru": "Не удалось войти:",
        "en": "Login failed:",
    },
    "login.connect_fail": {
        "uz": "Telegram serverlariga ulanib bo'lmadi: {error}",
        "ru": "Не удалось подключиться к серверам Telegram: {error}",
        "en": "Could not reach Telegram servers: {error}",
    },
    "login.already": {
        "uz": "Allaqachon kirgansiz: {user} (saqlangan sessiya).",
        "ru": "Вы уже вошли: {user} (сохранённая сессия).",
        "en": "Already signed in as {user} (saved session).",
    },
    "login.first_run": {
        "uz": "Birinchi ishga tushirish - Telegramga kirish kerak.",
        "ru": "Первый запуск - нужно войти в Telegram.",
        "en": "First run - Telegram login required.",
    },
    "login.first_run_note": {
        "uz": "(Keyin sessiya saqlanadi, shuning uchun bu faqat bir marta bo'ladi.)",
        "ru": "(Сессия будет сохранена, поэтому это понадобится только один раз.)",
        "en": "(Your session is saved afterwards, so this happens only once.)",
    },
    "login.phone_prompt": {
        "uz": "Telefon raqam (xalqaro formatda, masalan +998901234567): ",
        "ru": "Номер телефона (в международном формате, например +998901234567): ",
        "en": "Phone number (international format, e.g. +998901234567): ",
    },
    "login.no_phone": {
        "uz": "Telefon raqam kiritilmadi.",
        "ru": "Номер телефона не введён.",
        "en": "No phone number entered.",
    },
    "login.api_invalid": {
        "uz": (
            "Telegram API ID va API hash juftligini xato deb rad etdi.\n"
            ".env ichidagi TELEGRAM_API_ID va TELEGRAM_API_HASH ni tekshiring\n"
            "(https://my.telegram.org dan qaytadan ko'chirib yozing)."
        ),
        "ru": (
            "Telegram отклонил пару API ID / API hash как недействительную.\n"
            "Проверьте TELEGRAM_API_ID и TELEGRAM_API_HASH в .env\n"
            "(скопируйте их заново с https://my.telegram.org)."
        ),
        "en": (
            "Telegram rejected the API ID / API hash pair as invalid.\n"
            "Check TELEGRAM_API_ID and TELEGRAM_API_HASH in .env\n"
            "(copy them again from https://my.telegram.org)."
        ),
    },
    "login.phone_invalid": {
        "uz": "Bu telefon raqam Telegram uchun yaroqli emas.",
        "ru": "Этот номер телефона недействителен для Telegram.",
        "en": "That phone number is not valid for Telegram.",
    },
    "login.phone_banned": {
        "uz": "Bu telefon raqam Telegramda bloklangan.",
        "ru": "Этот номер телефона заблокирован в Telegram.",
        "en": "This phone number is banned from Telegram.",
    },
    "login.flood": {
        "uz": "Kirishga juda ko'p urinish bo'ldi. Telegram {seconds} soniya kutishni so'rayapti.",
        "ru": "Слишком много попыток входа. Telegram просит подождать {seconds} секунд.",
        "en": "Too many login attempts. Telegram asks you to wait {seconds} seconds.",
    },
    "login.code_sent": {
        "uz": "Kirish kodi Telegram ilovangizga yuborildi.",
        "ru": "Код входа отправлен в ваше приложение Telegram.",
        "en": "A login code has been sent to your Telegram app.",
    },
    "login.code_prompt": {
        "uz": "Kirish kodi: ",
        "ru": "Код входа: ",
        "en": "Login code: ",
    },
    "login.code_wrong": {
        "uz": "Kod xato. Yana {left} ta urinish qoldi.",
        "ru": "Неверный код. Осталось попыток: {left}.",
        "en": "Wrong code. {left} attempt(s) left.",
    },
    "login.code_expired": {
        "uz": "Bu kodning muddati tugadi. Yangi kod olish uchun dasturni qayta ishga tushiring.",
        "ru": "Срок действия кода истёк. Запустите программу снова, чтобы получить новый.",
        "en": "That code has expired. Run the program again to get a new one.",
    },
    "login.code_failed": {
        "uz": "Kirib bo'lmadi: kirish kodi uch marta xato kiritildi.",
        "ru": "Не удалось войти: код был введён неверно три раза.",
        "en": "Could not sign in: the login code was wrong three times.",
    },
    "login.2fa_enabled": {
        "uz": "Bu akkauntda ikki qadamli tasdiqlash (2FA) yoqilgan.",
        "ru": "На этом аккаунте включена двухфакторная аутентификация (2FA).",
        "en": "Two-factor authentication is enabled on this account.",
    },
    "login.2fa_prompt": {
        "uz": "2FA paroli (yozganingiz ko'rinmaydi): ",
        "ru": "Пароль 2FA (ввод скрыт): ",
        "en": "2FA password (input is hidden): ",
    },
    "login.2fa_wrong": {
        "uz": "Parol xato. Yana {left} ta urinish qoldi.",
        "ru": "Неверный пароль. Осталось попыток: {left}.",
        "en": "Wrong password. {left} attempt(s) left.",
    },
    "login.2fa_failed": {
        "uz": "Kirib bo'lmadi: 2FA paroli uch marta xato kiritildi.",
        "ru": "Не удалось войти: пароль 2FA был введён неверно три раза.",
        "en": "Could not sign in: the 2FA password was wrong three times.",
    },
    "login.signed_in": {
        "uz": "Kirdingiz: {user}",
        "ru": "Вы вошли: {user}",
        "en": "Signed in as {user}",
    },
    "login.noname": {"uz": "(ismsiz)", "ru": "(без имени)", "en": "(no name)"},
    # ---------------- sessiyalar / сессии / sessions ----------------
    "session.header": {
        "uz": "AKKAUNT TANLASH",
        "ru": "ВЫБОР АККАУНТА",
        "en": "ACCOUNT SELECTION",
    },
    "session.none": {
        "uz": "Saqlangan akkaunt yo'q - yangi kirish kerak.",
        "ru": "Сохранённых аккаунтов нет - нужно войти заново.",
        "en": "No saved account - a fresh login is needed.",
    },
    "session.saved_list": {
        "uz": "Saqlangan akkauntlar:",
        "ru": "Сохранённые аккаунты:",
        "en": "Saved accounts:",
    },
    "session.opt_new": {
        "uz": "  y. Yangi akkaunt bilan kirish",
        "ru": "  y. Войти под новым аккаунтом",
        "en": "  y. Sign in with a new account",
    },
    "session.opt_del": {
        "uz": "  o. Saqlangan akkauntni o'chirish (logout)",
        "ru": "  o. Удалить сохранённый аккаунт (выход)",
        "en": "  o. Delete a saved account (log out)",
    },
    "session.select": {"uz": "Tanlang: ", "ru": "Выберите: ", "en": "Select: "},
    "session.bad_choice": {
        "uz": "  Noto'g'ri tanlov.",
        "ru": "  Неверный выбор.",
        "en": "  Invalid choice.",
    },
    "session.new_name_intro": {
        "uz": "Yangi akkauntga nom bering - bu faqat fayl nomi uchun, masalan: ishxona, shaxsiy, test",
        "ru": "Дайте имя новому аккаунту - только для имени файла, например: rabota, lichnyy, test",
        "en": "Name the new account - it is only used for the file name, e.g. work, personal, test",
    },
    "session.name_prompt": {
        "uz": "Nom [{default}]: ",
        "ru": "Имя [{default}]: ",
        "en": "Name [{default}]: ",
    },
    "session.name_taken": {
        "uz": (
            "  '{name}' nomli akkaunt allaqachon saqlangan. Boshqa nom tanlang yoki\n"
            "  menyudan shu akkauntni tanlang."
        ),
        "ru": (
            "  Аккаунт с именем '{name}' уже сохранён. Выберите другое имя или\n"
            "  выберите этот аккаунт в меню."
        ),
        "en": (
            "  An account named '{name}' already exists. Pick another name or\n"
            "  choose that account from the menu."
        ),
    },
    "session.name_empty": {
        "uz": "Nom bo'sh bo'lmasligi kerak.",
        "ru": "Имя не должно быть пустым.",
        "en": "The name must not be empty.",
    },
    "session.name_too_long": {
        "uz": "Nom juda uzun (40 belgidan oshmasin).",
        "ru": "Имя слишком длинное (не более 40 символов).",
        "en": "The name is too long (40 characters maximum).",
    },
    "session.name_bad_chars": {
        "uz": (
            "Nomda ruxsat etilmagan belgi bor: {chars}\n"
            "  Faqat lotin harflari, raqamlar, _ va - ishlatilsin "
            "(masalan: ishxona yoki mening_akkauntim)."
        ),
        "ru": (
            "В имени есть недопустимые символы: {chars}\n"
            "  Используйте только латинские буквы, цифры, _ и - "
            "(например: rabota или moy_akkaunt)."
        ),
        "en": (
            "The name contains characters that are not allowed: {chars}\n"
            "  Use only Latin letters, digits, _ and - "
            "(for example: work or my_account)."
        ),
    },
    "session.del_which": {
        "uz": "Qaysi akkauntni o'chiramiz?",
        "ru": "Какой аккаунт удалить?",
        "en": "Which account should be deleted?",
    },
    "session.del_prompt": {
        "uz": "Raqam (bekor qilish - Enter): ",
        "ru": "Номер (отмена - Enter): ",
        "en": "Number (Enter to cancel): ",
    },
    "session.del_warn": {
        "uz": (
            "'{name}' sessiyasi o'chiriladi. Keyinchalik bu akkaunt bilan ishlash uchun\n"
            "telefon raqam va Telegramdan keladigan kodni qaytadan kiritishingiz kerak\n"
            "bo'ladi."
        ),
        "ru": (
            "Сессия '{name}' будет удалена. Чтобы снова работать с этим аккаунтом,\n"
            "понадобится заново ввести номер телефона и код из Telegram."
        ),
        "en": (
            "The '{name}' session will be deleted. To use this account again you will\n"
            "have to enter the phone number and the Telegram code once more."
        ),
    },
    "session.del_confirm": {
        "uz": "Davom etamizmi? [{yes}/{no}]: ",
        "ru": "Продолжить? [{yes}/{no}]: ",
        "en": "Continue? [{yes}/{no}]: ",
    },
    "session.deleted": {
        "uz": "O'chirildi: {files}",
        "ru": "Удалено: {files}",
        "en": "Deleted: {files}",
    },
    "session.not_found": {
        "uz": "Fayl topilmadi - allaqachon o'chirilgan bo'lsa kerak.",
        "ru": "Файл не найден - вероятно, он уже удалён.",
        "en": "File not found - it was probably already deleted.",
    },
    "session.current": {
        "uz": "Akkaunt (sessiya): {name}",
        "ru": "Аккаунт (сессия): {name}",
        "en": "Account (session): {name}",
    },
    "session.bad_cli_name": {
        "uz": "--session nomi xato: {error}",
        "ru": "Неверное имя для --session: {error}",
        "en": "Invalid --session name: {error}",
    },
    # ---------------- chat tanlash / выбор чата / chat selection ----------------
    "chat.available": {
        "uz": "Mavjud chatlar:",
        "ru": "Доступные чаты:",
        "en": "Available chats:",
    },
    "chat.none_found": {
        "uz": "Bu akkauntda guruh yoki kanal topilmadi.",
        "ru": "В этом аккаунте не найдено групп или каналов.",
        "en": "No groups or channels found on this account.",
    },
    "chat.list_hint": {
        "uz": "Ro'yxatdan raqam, @username yoki raqamli chat ID kiriting.",
        "ru": "Введите номер из списка, @username или числовой ID чата.",
        "en": "Enter a number from the list, a @username, or a numeric chat ID.",
    },
    "chat.select": {
        "uz": "Chatni tanlang: ",
        "ru": "Выберите чат: ",
        "en": "Select a chat: ",
    },
    "chat.selected": {
        "uz": "Tanlangan chat:",
        "ru": "Выбранный чат:",
        "en": "Selected chat:",
    },
    "chat.f_title": {"uz": "  Nomi: ", "ru": "  Название: ", "en": "  Title: "},
    "chat.f_id": {"uz": "  ID:   ", "ru": "  ID:       ", "en": "  ID:    "},
    "chat.f_type": {"uz": "  Turi: ", "ru": "  Тип:      ", "en": "  Type:  "},
    "chat.f_rights": {
        "uz": "  Sizning huquqingiz: ",
        "ru": "  Ваши права: ",
        "en": "  Your rights: ",
    },
    "chat.nameless": {"uz": "(nomsiz)", "ru": "(без названия)", "en": "(no title)"},
    "chat.kind_basic": {
        "uz": "oddiy guruh - admin log yo'q",
        "ru": "обычная группа - админ-лога нет",
        "en": "basic group - no admin log",
    },
    "chat.kind_super": {"uz": "supergroup", "ru": "супергруппа", "en": "supergroup"},
    "chat.kind_channel": {"uz": "kanal", "ru": "канал", "en": "channel"},
    "chat.basic_warning": {
        "uz": (
            "\n  Bu ODDIY guruh. Telegram oddiy guruhlar uchun admin log yuritmaydi.\n"
            "  Uni supergroup'ga aylantiring (sozlamalardan birini, masalan chat\n"
            "  tarixi ko'rinishini o'zgartirsangiz avtomatik aylanadi) va qayta urinib\n"
            "  ko'ring."
        ),
        "ru": (
            "\n  Это ОБЫЧНАЯ группа. Telegram не ведёт админ-лог для обычных групп.\n"
            "  Преобразуйте её в супергруппу (например, изменив видимость истории\n"
            "  чата - это происходит автоматически) и попробуйте снова."
        ),
        "en": (
            "\n  This is a BASIC group. Telegram keeps no admin log for basic groups.\n"
            "  Convert it to a supergroup (changing a setting such as chat history\n"
            "  visibility does it automatically) and try again."
        ),
    },
    "chat.not_admin_warning": {
        "uz": (
            "\n  Siz bu yerda administrator EMASSIZ. Telegramning admin log API'si\n"
            "  (channels.getAdminLog) administrator huquqini talab qiladi, shuning\n"
            "  uchun so'rov rad etilishi ehtimoli juda katta."
        ),
        "ru": (
            "\n  Вы здесь НЕ администратор. API админ-лога Telegram\n"
            "  (channels.getAdminLog) требует права администратора, поэтому запрос,\n"
            "  скорее всего, будет отклонён."
        ),
        "en": (
            "\n  You are NOT an administrator here. Telegram's admin-log API\n"
            "  (channels.getAdminLog) requires administrator rights, so the request\n"
            "  will almost certainly be refused."
        ),
    },
    "chat.confirm": {
        "uz": "Shu chatning admin logini tekshiramizmi? [{yes}/{no}]: ",
        "ru": "Проверить админ-лог этого чата? [{yes}/{no}]: ",
        "en": "Query this chat's admin log? [{yes}/{no}]: ",
    },
    "chat.nothing_entered": {
        "uz": "Hech narsa kiritilmadi.",
        "ru": "Ничего не введено.",
        "en": "Nothing entered.",
    },
    "chat.private_err": {
        "uz": (
            "Bu chat yopiq va bu akkaunt unga kira olmaydi.\n"
            "Siz guruh a'zosi (va administrator) bo'lishingiz kerak."
        ),
        "ru": (
            "Этот чат закрытый, и этот аккаунт не имеет к нему доступа.\n"
            "Вы должны быть участником группы (и администратором)."
        ),
        "en": (
            "That chat is private and this account cannot access it.\n"
            "You must be a member of the group (and an administrator)."
        ),
    },
    "chat.session_invalid": {
        "uz": (
            "Saqlangan sessiya endi yaroqsiz. Sessiya faylini o'chirib, dasturni "
            "qayta ishga tushiring."
        ),
        "ru": (
            "Сохранённая сессия больше недействительна. Удалите файл сессии и "
            "запустите программу снова."
        ),
        "en": (
            "The saved session is no longer valid. Delete the session file and run "
            "the program again."
        ),
    },
    "chat.not_found_err": {
        "uz": (
            "Telegram '{answer}' uchun chat topa olmadi.\n"
            "Maslahat: ro'yxatdan raqam tanlang, @username yozing yoki yuqorida\n"
            "ko'rsatilgan to'liq raqamli ID ni ishlating (supergroup ID'lari -100 bilan\n"
            "boshlanadi)."
        ),
        "ru": (
            "Telegram не нашёл чат по '{answer}'.\n"
            "Совет: выберите номер из списка, укажите @username или используйте\n"
            "полный числовой ID, как показано выше (ID супергрупп начинаются с -100)."
        ),
        "en": (
            "Telegram could not find a chat for '{answer}'.\n"
            "Tips: pick a number from the list, use a @username, or use the full\n"
            "numeric ID exactly as shown above (supergroup IDs start with -100)."
        ),
    },
    "rights.creator": {
        "uz": "egasi (creator)",
        "ru": "владелец (creator)",
        "en": "creator",
    },
    "rights.admin": {"uz": "administrator", "ru": "администратор", "en": "administrator"},
    "rights.not_admin": {"uz": "admin emas", "ru": "не администратор", "en": "not an admin"},
    "rights.unknown": {"uz": "aniqlanmadi", "ru": "не определено", "en": "unknown"},
    # ---------------- sanalar / даты / dates ----------------
    "date.menu": {
        "uz": (
            "Sana oraligi:\n\n"
            "1. Oxirgi 24 soat\n"
            "2. Oxirgi 7 kun\n"
            "3. Shu oy\n"
            "4. O'tgan oy\n"
            "5. O'zim sana kiritaman\n"
        ),
        "ru": (
            "Период:\n\n"
            "1. Последние 24 часа\n"
            "2. Последние 7 дней\n"
            "3. Текущий месяц\n"
            "4. Прошлый месяц\n"
            "5. Свой период\n"
        ),
        "en": (
            "Date range:\n\n"
            "1. Last 24 hours\n"
            "2. Last 7 days\n"
            "3. Current month\n"
            "4. Previous month\n"
            "5. Custom date range\n"
        ),
    },
    "date.select": {
        "uz": "Tanlang [1-5]: ",
        "ru": "Выберите [1-5]: ",
        "en": "Select [1-5]: ",
    },
    "date.start_prompt": {
        "uz": "Boshlanish sanasi (YYYY-MM-DD): ",
        "ru": "Дата начала (YYYY-MM-DD): ",
        "en": "Start date (YYYY-MM-DD): ",
    },
    "date.end_prompt": {
        "uz": "Tugash sanasi    (YYYY-MM-DD): ",
        "ru": "Дата окончания   (YYYY-MM-DD): ",
        "en": "End date   (YYYY-MM-DD): ",
    },
    "date.bad_format": {
        "uz": "Sana formati xato: '{value}'. YYYY-MM-DD ko'rinishida yozing, masalan 2026-09-01.",
        "ru": "Неверный формат даты: '{value}'. Используйте YYYY-MM-DD, например 2026-09-01.",
        "en": "Invalid date format: '{value}'. Use YYYY-MM-DD, e.g. 2026-09-01.",
    },
    "date.end_before_start": {
        "uz": "Tugash sanasi boshlanish sanasidan oldin turibdi.",
        "ru": "Дата окончания раньше даты начала.",
        "en": "The end date is before the start date.",
    },
    "date.bad_choice": {
        "uz": "1, 2, 3, 4 yoki 5 ni tanlang.",
        "ru": "Выберите 1, 2, 3, 4 или 5.",
        "en": "Pick 1, 2, 3, 4 or 5.",
    },
    "date.range": {
        "uz": "Oraliq: {start}  ->  {end}  (mahalliy vaqt)",
        "ru": "Период: {start}  ->  {end}  (местное время)",
        "en": "Range: {start}  ->  {end}  (your local time)",
    },
    # ---------------- o'qish / чтение / fetching ----------------
    "fetch.reading": {
        "uz": "Admin log o'qilmoqda (yangilaridan boshlab)...",
        "ru": "Чтение админ-лога (начиная с новых)...",
        "en": "Reading admin log (newest first)...",
    },
    "fetch.page": {
        "uz": "  sahifa {page}: {count} ta hodisa, eng eskisi {oldest}",
        "ru": "  страница {page}: событий {count}, самое старое {oldest}",
        "en": "  page {page}: {count} event(s), oldest so far {oldest}",
    },
    "fetch.flood": {
        "uz": "Telegram so'rov chegarasiga yetildi.",
        "ru": "Достигнут лимит запросов Telegram.",
        "en": "Telegram rate limit reached.",
    },
    "fetch.flood_wait": {
        "uz": "{seconds} soniya kutilmoqda...",
        "ru": "Ожидание {seconds} секунд...",
        "en": "Waiting {seconds} seconds...",
    },
    "fetch.flood_continue": {
        "uz": "Davom etamiz.",
        "ru": "Продолжаем.",
        "en": "Continuing.",
    },
    "fetch.not_admin": {
        "uz": (
            "Telegram bu chatning admin logini bermadi (CHAT_ADMIN_REQUIRED).\n"
            "Admin log API'si guruhda administrator huquqini talab qiladi."
        ),
        "ru": (
            "Telegram не выдал админ-лог этого чата (CHAT_ADMIN_REQUIRED).\n"
            "API админ-лога требует права администратора в группе."
        ),
        "en": (
            "Telegram refused the admin log for this chat (CHAT_ADMIN_REQUIRED).\n"
            "The admin-log API requires administrator rights in the group."
        ),
    },
    "fetch.not_admin_short": {
        "uz": "Telegram bu chatning admin logini bermadi (CHAT_ADMIN_REQUIRED).",
        "ru": "Telegram не выдал админ-лог этого чата (CHAT_ADMIN_REQUIRED).",
        "en": "Telegram refused the admin log for this chat (CHAT_ADMIN_REQUIRED).",
    },
    "fetch.unknown_name": {
        "uz": "aniqlanmadi",
        "ru": "не определено",
        "en": "unknown",
    },
    "fetch.unknown_admin": {
        "uz": "admin aniqlanmadi",
        "ru": "администратор не определён",
        "en": "unknown admin",
    },
    "fetch.unknown_author": {
        "uz": "aniqlanmadi / anonim",
        "ru": "не определён / анонимно",
        "en": "unknown / anonymous",
    },
    # ---------------- natijalar / результаты / results ----------------
    "event.header": {
        "uz": "O'CHIRILGAN XABAR HODISALARI",
        "ru": "СОБЫТИЯ УДАЛЕНИЯ СООБЩЕНИЙ",
        "en": "DELETED MESSAGE EVENTS",
    },
    "event.action": {
        "uz": "Amal: XABAR O'CHIRILDI",
        "ru": "Действие: СООБЩЕНИЕ УДАЛЕНО",
        "en": "Action: MESSAGE DELETED",
    },
    "event.admin_user": {
        "uz": "Admin/Foydalanuvchi: {name}",
        "ru": "Админ/Пользователь: {name}",
        "en": "Admin/User: {name}",
    },
    "event.msg_id": {
        "uz": "Xabar ID: {id}",
        "ru": "ID сообщения: {id}",
        "en": "Message ID: {id}",
    },
    "event.not_given": {"uz": "berilmagan", "ru": "не предоставлено", "en": "not provided"},
    "event.deleted_by": {
        "uz": "  Kim o'chirdi: {name} (id={id})",
        "ru": "  Кто удалил: {name} (id={id})",
        "en": "  Deleted by: {name} (id={id})",
    },
    "event.author": {
        "uz": "  Asl muallif: {name}{id}",
        "ru": "  Исходный автор: {name}{id}",
        "en": "  Original author: {name}{id}",
    },
    "event.sent_at": {
        "uz": "  Xabar yozilgan vaqt: {date}",
        "ru": "  Время отправки сообщения: {date}",
        "en": "  Message sent at: {date}",
    },
    "event.text": {
        "uz": "  Xabar matni: {text}",
        "ru": "  Текст сообщения: {text}",
        "en": "  Message text: {text}",
    },
    "event.no_text": {
        "uz": "  Xabar matni: (bu hodisa uchun API matn bermadi)",
        "ru": "  Текст сообщения: (для этого события API не вернул текст)",
        "en": "  Message text: (not provided by the API for this event)",
    },
    "event.media": {"uz": "  Media: {media}", "ru": "  Медиа: {media}", "en": "  Media: {media}"},
    "event.event_id": {
        "uz": "  Hodisa ID: {id}",
        "ru": "  ID события: {id}",
        "en": "  Event ID: {id}",
    },
    "event.none_found": {
        "uz": "So'ralgan oraliqda o'chirilgan xabar hodisasi topilmadi.",
        "ru": "В запрошенном периоде событий удаления сообщений не найдено.",
        "en": "No deleted-message events found inside the requested range.",
    },
    "event.scanned": {
        "uz": "O'qilgan sahifa: {pages}, ko'rilgan hodisa: {scanned}",
        "ru": "Прочитано страниц: {pages}, просмотрено событий: {scanned}",
        "en": "Pages fetched: {pages}, events scanned: {scanned}",
    },
    "event.total": {
        "uz": "Jami: {n} ta o'chirish hodisasi   (o'qilgan sahifa: {pages}, ko'rilgan hodisa: {scanned})",
        "ru": "Всего: {n} событий удаления   (прочитано страниц: {pages}, просмотрено событий: {scanned})",
        "en": "Total: {n} deletion event(s)   (pages fetched: {pages}, events scanned: {scanned})",
    },
    "event.page_cap": {
        "uz": "Eslatma: xavfsizlik chegarasi - {pages} sahifada to'xtadi.",
        "ru": "Примечание: остановлено на защитном лимите - {pages} страниц.",
        "en": "Note: stopped at the safety cap of {pages} pages.",
    },
    # ---------------- tarixiy test / исторический тест / historical test ----------------
    "horizon.header": {
        "uz": "TARIXIY MA'LUMOT TESTI (Telegram aslida nima qaytardi)",
        "ru": "ТЕСТ ИСТОРИЧЕСКОГО ДОСТУПА (что Telegram вернул на самом деле)",
        "en": "HISTORICAL ACCESS TEST (what Telegram actually returned)",
    },
    "horizon.requested": {
        "uz": "So'ralgan oraliq : {start}  ->  {end}",
        "ru": "Запрошенный период : {start}  ->  {end}",
        "en": "Requested range : {start}  ->  {end}",
    },
    "horizon.entries": {
        "uz": "Logdagi yozuvlar : {total} ta (barcha amal turlari, {pages} sahifa)",
        "ru": "Записей в логе     : {total} (все типы действий, страниц: {pages})",
        "en": "Entries in log  : {total} (all action types, {pages} page(s))",
    },
    "horizon.oldest_none": {
        "uz": "Eng eski yozuv   : yo'q - admin log bo'sh qaytdi.",
        "ru": "Самая старая запись: нет - админ-лог вернулся пустым.",
        "en": "Oldest entry    : none - the admin log came back empty.",
    },
    "horizon.measured_nothing": {
        "uz": (
            "O'LCHANDI: hech narsa. Bo'sh log Telegram eski hodisalarni o'chirib\n"
            "tashlaganini ham, bu chatda umuman admin amali bo'lmaganini ham\n"
            "ko'rsatmaydi. Hech narsa isbotlanmadi."
        ),
        "ru": (
            "ИЗМЕРЕНО: ничего. Пустой лог не показывает ни того, что Telegram удалил\n"
            "старые события, ни того, что в этом чате вообще не было действий\n"
            "администратора. Ничего не доказано."
        ),
        "en": (
            "MEASURED: nothing. An empty log cannot tell you whether Telegram\n"
            "discarded older events or whether no admin action was ever logged\n"
            "in this chat. Nothing is proven either way."
        ),
    },
    "horizon.oldest": {
        "uz": "Eng eski yozuv   : {date}",
        "ru": "Самая старая запись: {date}",
        "en": "Oldest entry    : {date}",
    },
    "horizon.newest": {
        "uz": "Eng yangi yozuv  : {date}",
        "ru": "Самая новая запись: {date}",
        "en": "Newest entry    : {date}",
    },
    "horizon.age": {
        "uz": "Eng eski yozuv yoshi: {hours} soat",
        "ru": "Возраст самой старой записи: {hours} ч",
        "en": "Oldest entry age: {hours} hours",
    },
    "horizon.full_range": {
        "uz": (
            "O'LCHANDI: Telegram siz so'ragan boshlanish sanasiga yetib boradigan (yoki\n"
            "undan ham eski) yozuvlarni qaytardi. Ya'ni bu chat uchun so'ralgan\n"
            "oraliqning hammasi mavjud edi."
        ),
        "ru": (
            "ИЗМЕРЕНО: Telegram вернул записи, доходящие до запрошенной даты начала\n"
            "(или старше). То есть для этого чата весь запрошенный период был\n"
            "доступен."
        ),
        "en": (
            "MEASURED: Telegram returned entries reaching back to or beyond your\n"
            "requested start date, so the full requested range was available for\n"
            "this chat."
        ),
    },
    "horizon.measured_cut": {
        "uz": (
            "O'LCHANDI: sahifalash log oxiriga yetdi va Telegram {oldest}\n"
            "dan eski hech narsa bermadi (siz {start} dan so'ragan bo'lsangiz ham)."
        ),
        "ru": (
            "ИЗМЕРЕНО: постраничное чтение дошло до конца лога, и Telegram не выдал\n"
            "ничего старше {oldest} (хотя вы запрашивали с {start})."
        ),
        "en": (
            "MEASURED: pagination reached the end of the log and Telegram returned\n"
            "nothing older than {oldest}, although you asked from {start}."
        ),
    },
    "horizon.near_window": {
        "uz": (
            "TALQIN: eng eski yozuv {hours} soat chegarasiga juda yaqin turibdi - server\n"
            "tomonidagi saqlash muddati devori aynan shunday ko'rinadi. Hujjatlardagi\n"
            "muddatga mos keladi, lekin bu hali rasmiy isbot emas."
        ),
        "ru": (
            "ТОЛКОВАНИЕ: самая старая запись находится очень близко к границе {hours}\n"
            "часов - именно так выглядит серверный предел хранения. Это согласуется с\n"
            "документацией, но формальным доказательством пока не является."
        ),
        "en": (
            "INTERPRETATION: the oldest entry sits close to the {hours}-hour mark,\n"
            "which is what a server-side retention cut-off looks like. Consistent with\n"
            "the documented window - still not a formal proof."
        ),
    },
    "horizon.not_measured": {
        "uz": (
            "TALQIN: bu ishga tushirish saqlash muddatini O'LCHAMADI va uni\n"
            "isbotlamaydi ham."
        ),
        "ru": (
            "ТОЛКОВАНИЕ: этот запуск НЕ измерил предел хранения и не доказывает его."
        ),
        "en": (
            "INTERPRETATION: this run did NOT measure a retention limit, and does\n"
            "not prove one."
        ),
    },
    "horizon.thin_log": {
        "uz": "Butun logdagi yozuvlar soni: {total}; eng eskisi esa faqat {hours} soatlik.",
        "ru": "Всего записей во всём логе: {total}; самой старой - лишь {hours} ч.",
        "en": "Entries in the whole log: {total}; the oldest is just {hours} hours old.",
    },
    "horizon.quiet_chat": {
        "uz": (
            "Undan oldingi bo'sh davr - yangi yoki jim guruh uchun mutlaqo normal\n"
            "holat: ehtimol oldin hech qanday admin amali bo'lmagan.\n"
            "\"Eski hodisa qaytmadi\" degani \"Telegram ularni o'chirgan\" degani EMAS."
        ),
        "ru": (
            "Пустой период до неё - совершенно нормально для новой или тихой группы:\n"
            "возможно, раньше просто не было действий администратора.\n"
            "\"Старые события не вернулись\" НЕ значит \"Telegram их удалил\"."
        ),
        "en": (
            "An empty stretch before that is exactly what a new or quiet chat looks\n"
            "like: there may simply never have been a logged admin action earlier.\n"
            "\"No older events returned\" is not the same as \"Telegram deleted them\"."
        ),
    },
    "horizon.how_to_measure": {
        "uz": (
            "Muddatni haqiqatan o'lchash uchun sizga {hours} soatdan ko'proq vaqt oldin\n"
            "aniq admin amali (o'chirish, ban, pin) bo'lgan chat kerak.\n"
            "Bugun bir xabarni o'chiring, so'ng 3 kundan keyin shu tekshiruvni qayta\n"
            "ishga tushiring: agar hodisa yo'qolgan bo'lsa - muddatni o'z\n"
            "akkauntingizda o'lchagan bo'lasiz."
        ),
        "ru": (
            "Чтобы действительно измерить окно, нужен чат, в котором точно было\n"
            "действие администратора (удаление, бан, закрепление) более {hours} часов\n"
            "назад. Удалите сообщение сегодня, а через 3 дня запустите проверку снова:\n"
            "если событие исчезло - вы измерили предел на своём аккаунте."
        ),
        "en": (
            "To actually measure the window you need a chat that definitely had a\n"
            "logged admin action (a deletion, a ban, a pin) more than {hours} hours\n"
            "ago. Delete a message today, then re-run this check in 3 days: if the\n"
            "event has vanished, you have measured the limit on your own account."
        ),
    },
    "horizon.reference": {
        "uz": (
            "Ma'lumot uchun: Telethon va TDLib hujjatlari admin logni taxminan oxirgi\n"
            "{hours} soatni qamraydi deb yozadi. Telegramning o'z MTProto sahifasi\n"
            "(channels.getAdminLog) esa saqlash muddati haqida umuman hech narsa\n"
            "yozmagan. API hech qanday chegara xabarini yubormaydi - yuqoridagi\n"
            "satrlar shu dasturning sizning ma'lumotingizga qaragan talqini."
        ),
        "ru": (
            "Для справки: документация Telethon и TDLib описывает админ-лог как\n"
            "покрывающий примерно последние {hours} часов. Собственная страница\n"
            "Telegram по MTProto (channels.getAdminLog) не указывает срок хранения\n"
            "вообще. API не присылает никакого сообщения о пределе - строки выше\n"
            "являются толкованием ваших данных этой программой."
        ),
        "en": (
            "For reference: Telethon's and TDLib's documentation describe the admin\n"
            "log as covering roughly the last {hours} hours. Telegram's own MTProto\n"
            "page for channels.getAdminLog states no retention period at all. The API\n"
            "sends no limit message - the lines above are this tool's reading of your\n"
            "data."
        ),
    },
    # ---------------- CSV ----------------
    "csv.note": {
        "uz": "Yuqoridagi natijalar faqat ekranda. Faylga saqlash mumkin:",
        "ru": "Результаты выше только на экране. Их можно сохранить в файл:",
        "en": "The results above are on screen only. They can be saved to a file:",
    },
    "csv.prompt": {
        "uz": "Shu faylga saqlaymizmi? [{yes}/{no}]: ",
        "ru": "Сохранить в этот файл? [{yes}/{no}]: ",
        "en": "Save to this file? [{yes}/{no}]: ",
    },
    "csv.saved": {"uz": "SAQLANDI: {path}", "ru": "СОХРАНЕНО: {path}", "en": "SAVED: {path}"},
    "csv.open_hint": {
        "uz": "Excel yoki Notepad bilan shu manzildan ochishingiz mumkin.",
        "ru": "Файл можно открыть в Excel или Notepad по этому пути.",
        "en": "You can open it from that path with Excel or Notepad.",
    },
    "csv.not_saved": {
        "uz": "Saqlanmadi - fayl yaratilmadi.",
        "ru": "Не сохранено - файл не создан.",
        "en": "Not saved - no file was created.",
    },
    "csv.fail": {
        "uz": "CSV yozib bo'lmadi: {error}",
        "ru": "Не удалось записать CSV: {error}",
        "en": "Could not write the CSV: {error}",
    },
    # ---------------- xatolar / ошибки / errors ----------------
    "err.refused_admin": {
        "uz": (
            "Telegram so'rovni rad etdi: guruhning admin logini o'qish uchun\n"
            "administrator huquqi kerak."
        ),
        "ru": (
            "Telegram отклонил запрос: для чтения админ-лога группы нужны права\n"
            "администратора."
        ),
        "en": (
            "Telegram refused the request: administrator rights are required to\n"
            "read a group's admin log."
        ),
    },
    "err.private": {
        "uz": "Bu chat yopiq yoki bu akkaunt undan chiqarilgan.",
        "ru": "Этот чат закрыт или этот аккаунт был из него удалён.",
        "en": "This chat is private or this account was removed from it.",
    },
    "err.flood": {
        "uz": "Telegram so'rov chegarasi: {seconds} soniya kutib, qayta urinib ko'ring.",
        "ru": "Лимит запросов Telegram: подождите {seconds} секунд и попробуйте снова.",
        "en": "Telegram rate limit: wait {seconds} seconds and try again.",
    },
    "err.rpc": {
        "uz": "Telegram API xatosi: {name}: {error}",
        "ru": "Ошибка Telegram API: {name}: {error}",
        "en": "Telegram API error: {name}: {error}",
    },
    # ---------------- CLI ----------------
    "cli.description": {
        "uz": "Telegram guruhidagi o'chirilgan xabar hodisalarini admin logdan topadi.",
        "ru": "Находит события удаления сообщений в админ-логе группы Telegram.",
        "en": "Finds deleted-message events in a Telegram group's admin log.",
    },
    "cli.session_help": {
        "uz": (
            "Qaysi akkaunt (sessiya fayli) bilan ishlash. Ko'rsatilmasa dastur "
            "menyudan so'raydi. Masalan: --session ishxona"
        ),
        "ru": (
            "С каким аккаунтом (файлом сессии) работать. Если не указано, программа "
            "спросит в меню. Например: --session rabota"
        ),
        "en": (
            "Which account (session file) to use. If omitted, the program asks in a "
            "menu. For example: --session work"
        ),
    },
    "cli.lang_help": {
        "uz": "Til: uz, ru yoki en. Ko'rsatilmasa dastur boshida so'raydi.",
        "ru": "Язык: uz, ru или en. Если не указан, программа спросит при запуске.",
        "en": "Language: uz, ru or en. If omitted, the program asks at startup.",
    },
}
