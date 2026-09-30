@echo off
rem Builds the standalone WindowStream.exe (PyInstaller). Run it in the folder with the script.
rem Install first: pip install pywin32 pillow mss pystray numpy PyTurboJPEG
setlocal

rem libjpeg-turbo is bundled into the exe so nothing has to be installed on other PCs
set TJ=C:\libjpeg-turbo64\bin\turbojpeg.dll
if not exist "%TJ%" set TJ=D:\libjpeg-turbo64\bin\turbojpeg.dll
set EXTRA=
if exist "%TJ%" (
    set EXTRA=--add-binary "%TJ%;."
) else (
    echo WARNING: turbojpeg.dll not found in C:\libjpeg-turbo64 or D:\libjpeg-turbo64 - the exe will encode with Pillow ^(slower^).
)

python -m pip install --upgrade pyinstaller || goto :error
python make_icon.py || goto :error

python -m PyInstaller --noconfirm --clean --onefile --noconsole ^
    --name WindowStream --icon icon.ico ^
    --hidden-import pystray._win32 ^
    --exclude-module tkinter --exclude-module matplotlib ^
    %EXTRA% window_stream.py || goto :error

echo.
echo Done: dist\WindowStream.exe
goto :eof

:error
echo Build failed.
exit /b 1
