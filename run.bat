@echo off
rem Telegram admin log - ishga tushirish fayli.
rem Shu faylni ikki marta bosib ishga tushirsangiz bo'ladi.
rem Birinchi marta kerakli kutubxonalarni o'zi o'rnatadi.

chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo.
    echo Birinchi ishga tushirish: muhit yaratilmoqda, bir-ikki daqiqa ketadi...
    echo.
    py -m venv .venv
    if errorlevel 1 (
        echo.
        echo Python topilmadi. https://www.python.org/downloads/windows/ dan
        echo o'rnatib, "Add python.exe to PATH" ni belgilang.
        echo.
        pause
        exit /b 1
    )
    ".venv\Scripts\python.exe" -m pip install -q -r requirements.txt
    if errorlevel 1 (
        echo.
        echo Kutubxonalarni o'rnatib bo'lmadi. Internet aloqasini tekshiring.
        echo.
        pause
        exit /b 1
    )
    echo Muhit tayyor.
)

if not exist ".env" (
    echo.
    echo .env fayli yo'q. .env.example dan ko'chirib, API ID va API hash yozing.
    echo.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" main.py %*

echo.
pause
