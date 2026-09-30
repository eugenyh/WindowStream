@echo off
chcp 65001 >nul
rem Сборка автономного WindowStream.exe (PyInstaller). Запускать в папке со скриптом.
rem Перед сборкой должны быть установлены: pip install pywin32 pillow mss pystray numpy PyTurboJPEG
setlocal

rem Библиотека libjpeg-turbo кладётся внутрь exe, чтобы на других ПК ничего ставить не нужно
set TJ=D:\libjpeg-turbo64\bin\turbojpeg.dll
set EXTRA=
if exist "%TJ%" (
    set EXTRA=--add-binary "%TJ%;."
) else (
    echo ВНИМАНИЕ: %TJ% не найден - exe будет кодировать через Pillow ^(медленнее^).
)

python -m pip install --upgrade pyinstaller || goto :error
python make_icon.py || goto :error

python -m PyInstaller --noconfirm --clean --onefile --noconsole ^
    --name WindowStream --icon icon.ico ^
    --hidden-import pystray._win32 ^
    --exclude-module tkinter --exclude-module matplotlib ^
    %EXTRA% window_stream.py || goto :error

echo.
echo Готово: dist\WindowStream.exe
goto :eof

:error
echo Сборка не удалась.
exit /b 1
