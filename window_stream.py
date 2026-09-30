r"""
window_stream.py - streams the contents of a Windows window to a browser (MJPEG over HTTP)
with a system tray icon.

Install:      pip install pywin32 pillow mss pystray numpy PyTurboJPEG
             (on Windows TurboJPEG also needs the libjpeg-turbo library)
List windows: python window_stream.py --list
Run:          python window_stream.py                 (pick the window in the tray menu)
             python window_stream.py --title "part of the window title" [--save]
No console:   pythonw window_stream.py
On the tablet: http://<PC-address>:8080/

Settings are stored in %APPDATA%\WindowStream\settings.json (created on first run).
Command-line options take precedence over the file; --save writes them to the file.
Interface language: English by default; set "language": "ru" in the settings file for Russian.
Tray menu: Start / Pause / Stop broadcast, window selection, autostart with Windows, Exit.
Standalone exe build: build_exe.bat (PyInstaller).
View-only: the client cannot control anything.
"""
__version__ = "1.0.0"  # keep in sync with the release tag (vX.Y.Z)

import argparse
import ctypes
import html
import json
import os
import re
import socket
import subprocess
import sys
import threading
import time
import winreg
import zlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO

import mss
import pystray
import win32con
import win32gui
import win32process
import win32ui
from PIL import Image, ImageDraw

# Fast JPEG encoding via libjpeg-turbo. If unavailable, fall back to Pillow.
try:
    import numpy as np
    from turbojpeg import TJFLAG_FASTDCT, TJPF_BGRX, TJPF_RGB, TurboJPEG

    # In a PyInstaller-built exe the library sits in the temporary unpack folder
    _lib = os.path.join(getattr(sys, "_MEIPASS", ""), "turbojpeg.dll")
    _turbo = TurboJPEG(lib_path=_lib) if getattr(sys, "_MEIPASS", None) and os.path.exists(_lib) else TurboJPEG()
    _turbo_error = None
except Exception as _e:  # package or libjpeg-turbo library missing
    _turbo = None
    _turbo_error = _e

# So window coordinates and sizes are in real pixels at 125/150% display scaling
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


# ---------- interface language ----------
LANG = "en"  # "en" or "ru"; set from the settings file ("language") at startup

I18N = {
    "en": {
        "web_offline_title": "No connection to the PC",
        "web_offline_sub": "The connection will be restored automatically",
        "web_fullscreen": "Full screen",
        "web_no_link": "No connection",
        "web_running": "Live",
        "web_paused": "Paused",
        "web_ms": "ms",
        "web_reset": "reset",
        "no_window_selected": "No window selected: choose one in the tray menu (\"Window\" item)",
        "window_not_found": "Window \"{title}\" not found",
        "port_failed": "Could not open port {port}: {err}",
        "broadcast_started": "Broadcast started: {title!r}, mode {mode}",
        "broadcast_stopped": "Broadcast stopped",
        "capture_error": "Capture error:",
        "state_stopped": "stopped", "state_running": "live", "state_paused": "paused",
        "settings_read_failed": "Could not read {path}: {err}. Using defaults",
        "setting_invalid": "Setting {key!r} is invalid and was ignored",
        "settings_save_failed": "Could not save settings to {path}: {err}",
        "settings_saved": "Settings saved:",
        "msg_title": "Window broadcast",
        "already_running": "The program is already running.\n\nThe icon is in the notification area near the clock. "
                           "If you cannot see it, click the \"Show hidden icons\" arrow.",
        "argp_desc": "Streams a Windows window to a browser (view-only)",
        "argp_epilog": "Default settings file: {path}",
        "help_title": "part of the window title (case-insensitive); if omitted - taken from the settings file",
        "help_list": "list windows and exit",
        "help_port": "port (default 8080)",
        "help_fps": "maximum frames per second (default 10)",
        "help_quality": "JPEG quality 1-95 (default 75)",
        "help_scale": "frame scale, e.g. 0.5 (default 1.0)",
        "help_mode": "screen - copy from the screen (window must not be covered); "
                     "printwindow - capture even a covered window (does not work for all applications)",
        "help_no_autostart": "do not start broadcasting at launch, wait for a menu command",
        "help_no_diff": "disable frame change detection: encode and send every frame",
        "help_no_turbo": "do not use TurboJPEG, encode with Pillow (for comparison)",
        "help_config": "path to the settings file",
        "help_save": "write this run's parameters to the settings file",
        "help_version": "show the program version and exit",
        "enc_pillow_off": "JPEG encoder: Pillow (disabled by --no-turbo)",
        "enc_turbo": "JPEG encoder: TurboJPEG",
        "enc_pillow_unavail": "JPEG encoder: Pillow (TurboJPEG unavailable: {err})",
        "port_label": "port {port}",
        "tip_title": "Window broadcast: {state}",
        "tip_stats": "Capture {grab:.0f} fps \u00b7 new frames {frames:.0f} fps \u00b7 clients {clients}",
        "open_on_tablet": "Open on the tablet: {url}",
        "broadcast_started_title": "Broadcast started",
        "error_title": "Error",
        "waiting_window": ". Waiting for the window to appear...",
        "streaming": "Streaming: {title}\n{url}",
        "no_windows": "(no windows found)",
        "window_label": "Window: {title}",
        "not_selected": "not selected",
        "autostart_on": "The program will start with Windows",
        "autostart_off": "Autostart disabled",
        "autostart_failed": "Could not change autostart: {err}",
        "settings_open_failed": "Could not open the settings file: {err}",
        "menu_start": "Start broadcast",
        "menu_resume": "Resume",
        "menu_pause": "Pause",
        "menu_stop": "Stop broadcast",
        "menu_raise": "Bring window to front",
        "menu_autostart": "Start with Windows",
        "menu_settings": "Open settings file",
        "menu_exit": "Exit",
        "pc_addresses": "PC addresses (use the one from the tablet's network):",
        "choose_window": "Choose a window in the tray menu: \"Window\" item",
    },
    "ru": {
        "web_offline_title": "Нет связи с ПК",
        "web_offline_sub": "Подключение восстановится автоматически",
        "web_fullscreen": "На весь экран",
        "web_no_link": "Нет связи",
        "web_running": "Транслируется",
        "web_paused": "Пауза",
        "web_ms": "мс",
        "web_reset": "сброс",
        "no_window_selected": "Окно не выбрано: выберите его в меню трея (пункт «Окно»)",
        "window_not_found": "Окно «{title}» не найдено",
        "port_failed": "Не удалось открыть порт {port}: {err}",
        "broadcast_started": "Трансляция запущена: {title!r}, режим {mode}",
        "broadcast_stopped": "Трансляция остановлена",
        "capture_error": "Ошибка захвата:",
        "state_stopped": "остановлена", "state_running": "идёт", "state_paused": "на паузе",
        "settings_read_failed": "Не удалось прочитать {path}: {err}. Используются значения по умолчанию",
        "setting_invalid": "Настройка {key!r} задана неверно и пропущена",
        "settings_save_failed": "Не удалось сохранить настройки в {path}: {err}",
        "settings_saved": "Настройки сохранены:",
        "msg_title": "Трансляция окна",
        "already_running": "Программа уже работает.\n\nЗначок находится в области уведомлений возле часов. "
                           "Если его не видно, нажмите стрелку «Показать скрытые значки».",
        "argp_desc": "Трансляция окна Windows в браузер (только просмотр)",
        "argp_epilog": "Файл настроек по умолчанию: {path}",
        "help_title": "часть заголовка окна (без учёта регистра); если не задано - из файла настроек",
        "help_list": "показать список окон и выйти",
        "help_port": "порт (по умолчанию 8080)",
        "help_fps": "максимум кадров в секунду (по умолчанию 10)",
        "help_quality": "качество JPEG 1-95 (по умолчанию 75)",
        "help_scale": "масштаб кадра, напр. 0.5 (по умолчанию 1.0)",
        "help_mode": "screen - копия с экрана (окно должно быть не перекрыто); "
                     "printwindow - захват даже перекрытого окна (не у всех приложений работает)",
        "help_no_autostart": "не начинать трансляцию при запуске, ждать команды из меню",
        "help_no_diff": "отключить проверку изменения кадра: кодировать и отправлять каждый кадр",
        "help_no_turbo": "не использовать TurboJPEG, кодировать через Pillow (для сравнения)",
        "help_config": "путь к файлу настроек",
        "help_save": "записать параметры этого запуска в файл настроек",
        "help_version": "показать версию программы и выйти",
        "enc_pillow_off": "Кодировщик JPEG: Pillow (отключено ключом --no-turbo)",
        "enc_turbo": "Кодировщик JPEG: TurboJPEG",
        "enc_pillow_unavail": "Кодировщик JPEG: Pillow (TurboJPEG недоступен: {err})",
        "port_label": "порт {port}",
        "tip_title": "Трансляция окна: {state}",
        "tip_stats": "Захват {grab:.0f} к/с \u00b7 новых кадров {frames:.0f} к/с \u00b7 клиентов {clients}",
        "open_on_tablet": "Откройте на планшете: {url}",
        "broadcast_started_title": "Трансляция запущена",
        "error_title": "Ошибка",
        "waiting_window": ". Жду появления окна...",
        "streaming": "Транслируется: {title}\n{url}",
        "no_windows": "(окна не найдены)",
        "window_label": "Окно: {title}",
        "not_selected": "не выбрано",
        "autostart_on": "Программа будет запускаться вместе с Windows",
        "autostart_off": "Автозапуск отключён",
        "autostart_failed": "Не удалось изменить автозапуск: {err}",
        "settings_open_failed": "Не удалось открыть файл настроек: {err}",
        "menu_start": "Начать трансляцию",
        "menu_resume": "Продолжить",
        "menu_pause": "Пауза",
        "menu_stop": "Закончить трансляцию",
        "menu_raise": "Вывести окно на передний план",
        "menu_autostart": "Запускать вместе с Windows",
        "menu_settings": "Открыть файл настроек",
        "menu_exit": "Выйти",
        "pc_addresses": "Адреса ПК (используйте тот, что из сети планшета):",
        "choose_window": "Выберите окно в меню иконки: пункт «Окно»",
    },
}


def T(key, **kw):
    """Translated string for the current interface language (English fallback)."""
    text = I18N.get(LANG, I18N["en"]).get(key) or I18N["en"][key]
    return text.format(**kw) if kw else text


class WindowNotFound(str):
    """Error text meaning that the window to stream does not exist (yet)."""


# ---------- window search ----------
def list_windows():
    result = []

    def cb(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title.strip():
                result.append((hwnd, title))

    win32gui.EnumWindows(cb, None)
    return result


_SKIP_CLASSES = {"ConsoleWindowClass", "CASCADIA_HOSTING_WINDOW_CLASS", "PseudoConsoleWindow", "Progman"}

_k32 = ctypes.windll.kernel32
_k32.OpenProcess.restype = ctypes.c_void_p
_k32.OpenProcess.argtypes = [ctypes.c_uint, ctypes.c_int, ctypes.c_uint]
_k32.CloseHandle.argtypes = [ctypes.c_void_p]
_k32.QueryFullProcessImageNameW.argtypes = [
    ctypes.c_void_p, ctypes.c_uint, ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_uint)]
_dwm = ctypes.windll.dwmapi
_dwm.DwmGetWindowAttribute.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_void_p, ctypes.c_uint]


def process_name(hwnd):
    """Name of the exe file of the process that owns the window (lowercase)."""
    try:
        pid = win32process.GetWindowThreadProcessId(hwnd)[1]
        h = _k32.OpenProcess(0x1000, 0, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not h:
            return ""
        try:
            buf = ctypes.create_unicode_buffer(1024)
            size = ctypes.c_uint(1024)
            if _k32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(size)):
                return os.path.basename(buf.value).lower()
        finally:
            _k32.CloseHandle(h)
    except Exception:
        pass
    return ""


def _is_cloaked(hwnd):
    """Hidden windows of UWP apps are formally "visible"; they must be skipped."""
    try:
        c = ctypes.c_int(0)
        _dwm.DwmGetWindowAttribute(hwnd, 14, ctypes.byref(c), ctypes.sizeof(c))  # DWMWA_CLOAKED
        return c.value != 0
    except Exception:
        return False


def _usable(hwnd):
    """The window is suitable for streaming: not a console, not hidden and not a tool window."""
    if hwnd == ctypes.windll.kernel32.GetConsoleWindow() or _is_cloaked(hwnd):
        return False
    try:
        if win32gui.GetClassName(hwnd) in _SKIP_CLASSES:
            return False
        if win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) & win32con.WS_EX_TOOLWINDOW:
            return False
    except Exception:
        return False
    return True


def _area(hwnd):
    try:
        _, _, w, h = win32gui.GetClientRect(hwnd)
        return w * h
    except Exception:
        return 0


def bring_to_front(hwnd):
    """Restores the window if it is minimized and brings it to the foreground.
    Needed by screen mode: it copies what is visible on the screen, not the window's own contents."""
    try:
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        return
    except Exception:
        pass
    try:  # Windows sometimes forbids changing the foreground window; "pressing" Alt lifts the restriction
        u = ctypes.windll.user32
        u.keybd_event(0x12, 0, 0, 0)
        win32gui.SetForegroundWindow(hwnd)
        u.keybd_event(0x12, 0, 2, 0)
    except Exception:
        pass


def app_windows():
    """List of windows for the tray menu."""
    me = os.getpid()
    result = []
    for hwnd, title in list_windows():
        if not _usable(hwnd):
            continue
        try:
            if win32process.GetWindowThreadProcessId(hwnd)[1] == me:
                continue
        except Exception:
            continue
        if not win32gui.IsIconic(hwnd) and _area(hwnd) < 50 * 50:
            continue
        result.append({"hwnd": hwnd, "title": title, "process": process_name(hwnd)})
    return sorted(result, key=lambda w: w["title"].lower())


def find_window(substr, process=None):
    """Finds a window. Title priority: exact match, prefix, substring.
    If a process is given, only its windows are considered, and when the title has changed
    (e.g. another file was opened), the largest window of that application is taken.
    Console windows are skipped: their title contains the command line with the searched text."""
    substr = (substr or "").lower()
    process = (process or "").lower()
    exact, starts, contains, by_proc = [], [], [], []
    for hwnd, title in list_windows():
        if not _usable(hwnd):
            continue
        if process and process_name(hwnd) != process:
            continue
        t = title.lower()
        if substr and t == substr:
            exact.append((hwnd, title))
        elif substr and t.startswith(substr):
            starts.append((hwnd, title))
        elif substr and substr in t:
            contains.append((hwnd, title))
        elif process:
            by_proc.append((hwnd, title))
    for group in (exact, starts, contains):
        if group:
            return group[0]
    if by_proc:
        return max(by_proc, key=lambda x: _area(x[0]))
    return None


# ---------- capture ----------
def grab_screen(hwnd, sct):
    """Copies the window area from the screen. The window must be visible and not covered."""
    _, _, w, h = win32gui.GetClientRect(hwnd)
    if w <= 0 or h <= 0:
        return None
    x, y = win32gui.ClientToScreen(hwnd, (0, 0))
    shot = sct.grab({"left": x, "top": y, "width": w, "height": h})
    data = shot.raw if hasattr(shot, "raw") else shot.bgra  # raw BGRA buffer without copying
    return data, shot.size


def grab_printwindow(hwnd):
    """Asks the window itself to render into a bitmap. Works for covered windows too,
    but not for every application (some GPU apps produce a black frame)."""
    _, _, w, h = win32gui.GetClientRect(hwnd)
    if w <= 0 or h <= 0:
        return None
    wdc = win32gui.GetWindowDC(hwnd)
    mfc = win32ui.CreateDCFromHandle(wdc)
    save = mfc.CreateCompatibleDC()
    bmp = win32ui.CreateBitmap()
    try:
        bmp.CreateCompatibleBitmap(mfc, w, h)
        save.SelectObject(bmp)
        # 1 = PW_CLIENTONLY, 2 = PW_RENDERFULLCONTENT
        ok = ctypes.windll.user32.PrintWindow(hwnd, save.GetSafeHdc(), 3)
        if not ok:
            return None
        info = bmp.GetInfo()
        bits = bmp.GetBitmapBits(True)
        return bits, (info["bmWidth"], info["bmHeight"])
    finally:
        win32gui.DeleteObject(bmp.GetHandle())
        save.DeleteDC()
        mfc.DeleteDC()
        win32gui.ReleaseDC(hwnd, wdc)


# ---------- shared frame buffer ----------
class FrameBuffer:
    def __init__(self):
        self.cond = threading.Condition()
        self.jpeg = None
        self.seq = 0
        self.ts = 0.0
        self.closed = False
        self.clients = 0

    def publish(self, jpeg, ts=None):
        with self.cond:
            self.jpeg = jpeg
            self.ts = ts if ts is not None else time.time()
            self.seq += 1
            self.cond.notify_all()

    def close(self):
        with self.cond:
            self.closed = True
            self.cond.notify_all()

    def add_client(self, n):
        with self.cond:
            self.clients += n

    def wait_new(self, last_seq, timeout=5.0):
        with self.cond:
            self.cond.wait_for(lambda: self.seq != last_seq or self.closed, timeout)
            return self.seq, self.jpeg, self.ts


def encode_jpeg(data, size, args):
    """Encodes a raw BGRX frame to JPEG. TurboJPEG if available, otherwise Pillow."""
    w, h = size
    use_turbo = _turbo is not None and not args.no_turbo
    if use_turbo and args.scale == 1.0:
        # Fast path: mss buffer straight into the encoder, no Pillow
        arr = np.frombuffer(data, np.uint8).reshape(h, w, 4)
        return _turbo.encode(arr, quality=args.quality, pixel_format=TJPF_BGRX, flags=TJFLAG_FASTDCT)

    img = Image.frombuffer("RGB", size, data, "raw", "BGRX", 0, 1)
    if args.scale != 1.0:
        img = img.resize(
            (max(1, int(w * args.scale)), max(1, int(h * args.scale))),
            Image.BILINEAR,
        )
    if use_turbo:
        return _turbo.encode(np.asarray(img), quality=args.quality, pixel_format=TJPF_RGB, flags=TJFLAG_FASTDCT)
    out = BytesIO()
    img.save(out, "JPEG", quality=args.quality)
    return out.getvalue()


def capture_loop(args, hwnd, title, buf, stop, paused, stats):
    interval = 1.0 / args.fps
    last_crc = None
    MSS = getattr(mss, "MSS", None) or mss.mss  # mss.mss is deprecated in newer versions
    with MSS() as sct:  # mss must be created in the thread where it is used
        while not stop.is_set():
            t0 = time.time()
            try:
                if paused.is_set():  # paused - the last frame stays on the tablet screen
                    stop.wait(0.2)
                    continue
                if not win32gui.IsWindow(hwnd):
                    found = find_window(args.title, args.process)
                    if found:
                        hwnd, title = found
                        stats["hwnd"] = hwnd
                    else:
                        stop.wait(1)
                        continue
                if win32gui.IsIconic(hwnd):  # minimized - keep the last frame
                    stop.wait(0.5)
                    continue

                frame = grab_printwindow(hwnd) if args.mode == "printwindow" else grab_screen(hwnd, sct)
                if frame is None:
                    stop.wait(0.2)
                    continue
                data, size = frame
                stats["grabs"] += 1

                # crc32 is computed directly on the raw buffer; the Pillow image is created only when needed
                crc = None if args.no_diff else zlib.crc32(data)
                if args.no_diff or crc != last_crc:  # encode only when the picture has changed
                    last_crc = crc
                    buf.publish(encode_jpeg(data, size, args), t0)
                    stats["frames"] += 1
            except Exception as e:
                print(T("capture_error"), e)
                stop.wait(0.5)

            delay = interval - (time.time() - t0)
            if delay > 0:
                stop.wait(delay)


# ---------- HTTP ----------
PAGE = r"""<!doctype html>
<html lang="@@lang@@"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">
<meta name="theme-color" content="#0a0d12">
<title>Map</title>
<style>
:root{--pad:6px;--bezel:6px;--accent:#8b95a5;--glow:rgba(139,149,165,.22);--edge:#3a4250}
body[data-state=running]{--accent:#2fcf7a;--glow:rgba(47,207,122,.30);--edge:#2a7a51}
body[data-state=paused]{--accent:#f5a623;--glow:rgba(245,166,35,.30);--edge:#9a6b1a}
body[data-state=offline]{--accent:#e5484d;--glow:rgba(229,72,77,.30);--edge:#8f3a3d}
*{box-sizing:border-box}
html,body{margin:0;height:100%;overflow:hidden;background:#0a0d12;
  background-image:radial-gradient(ellipse at 50% 35%,#171d27 0%,#0a0d12 70%);
  font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;color:#e8ecf2;
  touch-action:none;overscroll-behavior:none;
  -webkit-tap-highlight-color:transparent;user-select:none;-webkit-user-select:none}
.stage{position:fixed;inset:0;padding:var(--pad)}
.frame{width:100%;height:100%;padding:var(--bezel);border-radius:20px;
  background:linear-gradient(145deg,#2b323e,#141920);
  border:1px solid var(--edge);
  box-shadow:0 0 0 1px rgba(0,0,0,.7),0 0 30px var(--glow);
  transition:border-color .4s,box-shadow .4s}
.screen{position:relative;width:100%;height:100%;border-radius:13px;overflow:hidden;
  background:#000;isolation:isolate}
.screen::after{content:"";position:absolute;inset:0;border-radius:inherit;pointer-events:none;z-index:1;
  box-shadow:inset 0 0 0 1px rgba(255,255,255,.06),inset 0 0 30px rgba(0,0,0,.35)}

/* Image layer: scaled and moved with fingers */
.view{position:absolute;inset:0;transform-origin:0 0;touch-action:none;will-change:transform}
.view.anim{transition:transform .28s cubic-bezier(.2,.8,.2,1)}
.view img{width:100%;height:100%;object-fit:contain;display:block;pointer-events:none;
  -webkit-user-drag:none;transition:filter .4s}
body[data-state=paused] .view img{filter:saturate(.55) brightness(.7)}
body[data-state=offline] .view img{filter:grayscale(1) brightness(.4) blur(2px)}

/* Mode badge (top right) and buttons: auto-hide */
.badge{position:absolute;top:12px;right:12px;z-index:3;display:flex;align-items:center;gap:8px;
  padding:7px 13px 7px 11px;border-radius:999px;background:rgba(9,12,17,.72);
  -webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px);
  border:1px solid rgba(255,255,255,.12);font-weight:600;font-size:12px;line-height:1;
  letter-spacing:.09em;text-transform:uppercase;pointer-events:none;
  opacity:0;transition:opacity .35s}
body.ui .badge,body:not([data-state=running]) .badge{opacity:1}
.dot{width:9px;height:9px;border-radius:50%;background:var(--accent);box-shadow:0 0 8px var(--accent)}
body[data-state=running] .dot{animation:pulse 1.8s ease-out infinite}
@keyframes pulse{
  0%{box-shadow:0 0 0 0 var(--glow),0 0 8px var(--accent)}
  70%{box-shadow:0 0 0 9px transparent,0 0 8px var(--accent)}
  100%{box-shadow:0 0 0 0 transparent,0 0 8px var(--accent)}}
.stats{display:flex;align-items:center;gap:8px;font-weight:500;letter-spacing:.03em;
  text-transform:none;color:#aab3c0;font-variant-numeric:tabular-nums}
.stats::before{content:"";width:1px;height:12px;background:rgba(255,255,255,.18)}
body:not([data-state=running]) .stats,body.nostats .stats{display:none}

.iconbtn{position:absolute;top:8px;left:12px;z-index:3;width:38px;height:38px;padding:0;border-radius:50%;
  border:1px solid rgba(255,255,255,.12);background:rgba(9,12,17,.72);color:#e8ecf2;
  -webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px);
  display:flex;align-items:center;justify-content:center;
  opacity:0;pointer-events:none;transition:opacity .35s}
body.ui .iconbtn{opacity:1;pointer-events:auto}

.zoom{position:absolute;right:12px;bottom:12px;z-index:3;display:none;padding:7px 13px;border-radius:999px;
  background:rgba(9,12,17,.72);-webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px);
  border:1px solid rgba(255,255,255,.12);font-size:12px;font-weight:600;letter-spacing:.04em;
  font-variant-numeric:tabular-nums;cursor:pointer}
.zoom.on{display:block}

/* No connection */
.overlay{position:absolute;inset:0;z-index:2;display:none;flex-direction:column;align-items:center;
  justify-content:center;gap:12px;text-align:center;color:#c9d1dc;font-size:16px;letter-spacing:.03em;
  pointer-events:none}
.overlay small{font-size:13px;color:#8b95a5}
body[data-state=offline] .overlay{display:flex}
.spinner{width:34px;height:34px;border-radius:50%;border:3px solid rgba(255,255,255,.15);
  border-top-color:var(--accent);animation:spin 1s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
@media (max-width:600px){.badge{top:8px;right:8px;font-size:11px;padding:6px 11px 6px 9px}}
</style></head>
<body data-state="offline">
<div class="stage"><div class="frame"><div class="screen" id="screen">
  <div class="view" id="view"><img id="v" alt=""></div>
  <div class="overlay"><div class="spinner"></div><div>@@offline_title@@</div>
    <small>@@offline_sub@@</small></div>
  <button class="iconbtn" id="fs" aria-label="@@fullscreen@@">
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
      stroke-linecap="round" stroke-linejoin="round"><path d="M8 3H5a2 2 0 0 0-2 2v3M16 3h3a2 2 0 0 1 2 2v3M8 21H5a2 2 0 0 1-2-2v-3M16 21h3a2 2 0 0 0 2-2v-3"/></svg>
  </button>
  <div class="badge"><span class="dot"></span><span id="label">@@no_link@@</span>
    <span class="stats" id="stats">— fps · — @@ms@@</span></div>
  <div class="zoom" id="zoom">×1.0 · @@reset@@</div>
</div></div></div>
<script>
(() => {
'use strict';
const $ = id => document.getElementById(id);
const screenEl = $('screen'), view = $('view'), img = $('v'), label = $('label'),
      statsEl = $('stats'), zoomEl = $('zoom'), fsBtn = $('fs');
const LABELS = {running: '@@running@@', paused: '@@paused@@', offline: '@@no_link@@'};
let state = 'offline';

/* ---------- UI auto-hide ---------- */
let uiTimer = null;
function showUI() {
  document.body.classList.add('ui');
  clearTimeout(uiTimer);
  // During normal streaming the UI hides; on pause or connection loss it stays visible
  if (state === 'running') uiTimer = setTimeout(() => document.body.classList.remove('ui'), 4000);
}

/* ---------- Show/hide fps and latency (long press) ---------- */
let nostats = false;
try { nostats = localStorage.getItem('nostats') === '1'; } catch (e) {}
document.body.classList.toggle('nostats', nostats);
function toggleStats() {
  nostats = !nostats;
  document.body.classList.toggle('nostats', nostats);
  try { localStorage.setItem('nostats', nostats ? '1' : '0'); } catch (e) {}
  if (navigator.vibrate) navigator.vibrate(30);
  showUI();
}

/* ---------- Zoom and pan ---------- */
const MAX = 8;
let s = 1, tx = 0, ty = 0;
const rect = () => screenEl.getBoundingClientRect();
function clampT() {
  const r = rect();
  tx = Math.min(0, Math.max(r.width - r.width * s, tx));
  ty = Math.min(0, Math.max(r.height - r.height * s, ty));
}
function apply() {
  view.style.transform = 'translate(' + tx + 'px,' + ty + 'px) scale(' + s + ')';
  const z = s > 1.02;
  zoomEl.classList.toggle('on', z);
  if (z) zoomEl.textContent = '×' + s.toFixed(1) + ' · @@reset@@';
}
function animate() {
  view.classList.add('anim');
  setTimeout(() => view.classList.remove('anim'), 320);
}
function zoomAt(x, y, ns) {
  ns = Math.min(MAX, Math.max(1, ns));
  const r = rect();
  const cx = (x - r.left - tx) / s, cy = (y - r.top - ty) / s;
  tx = x - r.left - cx * ns;
  ty = y - r.top - cy * ns;
  s = ns;
  clampT();
  apply();
}
function resetZoom() { animate(); s = 1; tx = 0; ty = 0; apply(); }

const pts = new Map();
let g = null, press = null, lpTimer = null, lastTap = null;

function baseline() {
  const a = [...pts.values()];
  if (a.length === 1) g = {type: 'pan', x: a[0].x, y: a[0].y, tx: tx, ty: ty};
  else if (a.length >= 2) {
    g = {type: 'pinch', d: Math.hypot(a[0].x - a[1].x, a[0].y - a[1].y) || 1,
         mx: (a[0].x + a[1].x) / 2, my: (a[0].y + a[1].y) / 2, s: s, tx: tx, ty: ty};
  } else g = null;
}

function handleTap(x, y) {
  const now = performance.now();
  if (lastTap && now - lastTap.t < 320 && Math.hypot(x - lastTap.x, y - lastTap.y) < 40) {
    lastTap = null;
    if (s > 1.05) resetZoom(); else { animate(); zoomAt(x, y, 2.5); }
  } else {
    lastTap = {t: now, x: x, y: y};
    showUI();
  }
}

view.addEventListener('pointerdown', e => {
  try { view.setPointerCapture(e.pointerId); } catch (_) {}
  pts.set(e.pointerId, {x: e.clientX, y: e.clientY});
  view.classList.remove('anim');
  if (pts.size === 1) {
    press = {t: performance.now(), x: e.clientX, y: e.clientY, moved: false, multi: false, long: false};
    clearTimeout(lpTimer);
    lpTimer = setTimeout(() => {
      if (press && !press.moved && !press.multi) { press.long = true; toggleStats(); }
    }, 700);
  } else if (press) {
    press.multi = true;
    clearTimeout(lpTimer);
  }
  baseline();
});

view.addEventListener('pointermove', e => {
  const p = pts.get(e.pointerId);
  if (!p) return;
  p.x = e.clientX; p.y = e.clientY;
  if (press && Math.hypot(e.clientX - press.x, e.clientY - press.y) > 10) {
    press.moved = true;
    clearTimeout(lpTimer);
  }
  if (!g) return;
  if (g.type === 'pinch' && pts.size >= 2) {
    const a = [...pts.values()];
    const d = Math.hypot(a[0].x - a[1].x, a[0].y - a[1].y) || 1;
    const mx = (a[0].x + a[1].x) / 2, my = (a[0].y + a[1].y) / 2;
    const r = rect();
    const ns = Math.min(MAX, Math.max(1, g.s * d / g.d));
    const cx = (g.mx - r.left - g.tx) / g.s, cy = (g.my - r.top - g.ty) / g.s;
    s = ns;
    tx = mx - r.left - cx * ns;
    ty = my - r.top - cy * ns;
    clampT();
    apply();
  } else if (g.type === 'pan' && s > 1) {
    tx = g.tx + (e.clientX - g.x);
    ty = g.ty + (e.clientY - g.y);
    clampT();
    apply();
  }
});

function endPointer(e) {
  if (!pts.has(e.pointerId)) return;
  pts.delete(e.pointerId);
  clearTimeout(lpTimer);
  if (pts.size === 0) {
    if (press && e.type === 'pointerup' && !press.moved && !press.multi && !press.long &&
        performance.now() - press.t < 300) handleTap(e.clientX, e.clientY);
    press = null;
    g = null;
  } else baseline();
}
view.addEventListener('pointerup', endPointer);
view.addEventListener('pointercancel', endPointer);
view.addEventListener('contextmenu', e => e.preventDefault());
// Mouse wheel - for testing from a regular computer
view.addEventListener('wheel', e => {
  e.preventDefault();
  zoomAt(e.clientX, e.clientY, s * Math.exp(-e.deltaY * 0.0015));
}, {passive: false});

zoomEl.addEventListener('click', resetZoom);
fsBtn.addEventListener('click', () => {
  const d = document;
  if (d.fullscreenElement) d.exitFullscreen();
  else if (d.documentElement.requestFullscreen) d.documentElement.requestFullscreen();
  showUI();
});
window.addEventListener('resize', () => { clampT(); apply(); });

/* ---------- Frame stream (MJPEG parsed manually: fps and latency are needed) ---------- */
let frames = 0, lat = null, offset = null, lastSeq = -1, curUrl = null;
const samples = [];
const dec = new TextDecoder('ascii');

function concat(a, b) {
  if (!a.length) return b;
  const c = new Uint8Array(a.length + b.length);
  c.set(a);
  c.set(b, a.length);
  return c;
}
function findHeaderEnd(b) {
  for (let i = 0; i <= b.length - 4; i++) {
    if (b[i] === 13 && b[i + 1] === 10 && b[i + 2] === 13 && b[i + 3] === 10) return i;
  }
  return -1;
}
function show(jpeg) {
  const url = URL.createObjectURL(new Blob([jpeg], {type: 'image/jpeg'}));
  const prev = curUrl;
  curUrl = url;
  img.src = url;
  if (prev) setTimeout(() => URL.revokeObjectURL(prev), 1500);
}

let streamCtl = null;
function stopStream() {
  if (streamCtl) { streamCtl.abort(); streamCtl = null; }
}
async function startStream() {
  stopStream();
  const ctl = new AbortController();
  streamCtl = ctl;
  lastSeq = -1;
  let last = performance.now();
  // The server sends a frame at least every 5 s; longer silence means a dropped connection
  const wd = setInterval(() => { if (performance.now() - last > 12000) ctl.abort(); }, 2000);
  try {
    const resp = await fetch('/stream?t=' + Date.now(), {signal: ctl.signal, cache: 'no-store'});
    if (!resp.ok || !resp.body) throw new Error('stream');
    const reader = resp.body.getReader();
    let buf = new Uint8Array(0);
    for (;;) {
      const r = await reader.read();
      if (r.done) break;
      last = performance.now();
      buf = concat(buf, r.value);
      let latest = null;
      for (;;) {
        const h = findHeaderEnd(buf);
        if (h < 0) break;
        const head = dec.decode(buf.subarray(0, h));
        const m = /Content-Length:\s*(\d+)/i.exec(head);
        if (!m) { buf = buf.subarray(h + 4); continue; }
        const end = h + 4 + parseInt(m[1], 10);
        if (buf.length < end) break;
        const sm = /X-Seq:\s*(\d+)/i.exec(head), tm = /X-Ts:\s*([\d.]+)/i.exec(head);
        const seq = sm ? parseInt(sm[1], 10) : -2;
        // A frame with the same number is a keep-alive; do not display it again
        if (!sm || seq !== lastSeq) {
          lastSeq = seq;
          frames++;
          latest = {jpeg: buf.slice(h + 4, end), ts: tm ? parseFloat(tm[1]) : null};
        }
        buf = buf.subarray(end);
      }
      if (latest) {
        show(latest.jpeg);
        if (latest.ts != null && offset != null) {
          const l = Math.max(0, Date.now() - latest.ts + offset);
          lat = lat == null ? l : lat * 0.7 + l * 0.3;
        }
      }
    }
  } catch (e) {}
  finally {
    clearInterval(wd);
    if (streamCtl === ctl) {
      streamCtl = null;
      if (state !== 'offline') {
        setTimeout(() => { if (!streamCtl && state !== 'offline') startStream(); }, 1500);
      }
    }
  }
}

/* ---------- State and server polling ---------- */
function setState(ns) {
  if (ns === state) return;
  const was = state;
  state = ns;
  document.body.dataset.state = ns;
  label.textContent = LABELS[ns];
  if (ns === 'offline') stopStream();
  else if (was === 'offline') startStream();
  showUI();
}

async function poll() {
  const t0 = Date.now();
  try {
    const ctl = new AbortController();
    const timer = setTimeout(() => ctl.abort(), 2500);
    const r = await fetch('/status', {cache: 'no-store', signal: ctl.signal});
    const j = await r.json();
    clearTimeout(timer);
    const rtt = Date.now() - t0;
    if (typeof j.t === 'number') {
      // Clock offset between PC and tablet: take the measurement with the lowest round-trip time
      samples.push({rtt: rtt, off: j.t - (t0 + rtt / 2)});
      if (samples.length > 30) samples.shift();
      offset = samples.reduce((m, x) => x.rtt < m.rtt ? x : m).off;
    }
    setState(j.state === 'paused' ? 'paused' : 'running');
    // The browser tab is named after the streamed window (the title may change)
    if (j.title && document.title !== j.title) document.title = j.title;
  } catch (e) {
    setState('offline');
  }
}
setInterval(poll, 1000);
poll();

setInterval(() => {
  const fps = frames;
  frames = 0;
  statsEl.textContent = fps + ' fps · ' + (lat == null ? '—' : Math.round(lat) + ' @@ms@@');
}, 1000);
})();
</script>
</body></html>""".encode("utf-8")


def page_for(title):
    """Page in the selected language; the browser tab title equals the streamed window's title."""
    page = PAGE.decode("utf-8")
    if title:
        page = page.replace("<title>Map</title>", f"<title>{html.escape(title)}</title>", 1)
    page = page.replace("@@lang@@", LANG)
    page = re.sub(r"@@(\w+)@@", lambda m: html.escape(T("web_" + m.group(1)), quote=True), page)
    return page.encode("utf-8")


def make_handler(buf, get_status):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            path = self.path.split("?")[0]
            if path in ("/", "/index.html"):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                page = page_for(get_status().get("title"))
                self.send_header("Content-Length", str(len(page)))
                self.end_headers()
                self.wfile.write(page)
            elif path == "/status":
                data = dict(get_status())
                data["t"] = time.time() * 1000  # PC time for latency estimation
                body = json.dumps(data).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            elif path == "/snapshot.jpg":
                _, jpeg, _ts = buf.wait_new(-1, 3)
                if not jpeg:
                    self.send_error(503)
                    return
                self.send_response(200)
                self.send_header("Content-Type", "image/jpeg")
                self.send_header("Content-Length", str(len(jpeg)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(jpeg)
            elif path == "/stream":
                self.send_response(200)
                self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                seq = -1
                buf.add_client(1)
                try:
                    while not buf.closed:
                        seq, jpeg, ts = buf.wait_new(seq, 5)
                        if jpeg is None or buf.closed:
                            continue
                        # X-Seq / X-Ts are needed by the page for the frame counter and latency estimate
                        self.wfile.write(
                            b"--frame\r\nContent-Type: image/jpeg\r\nContent-Length: "
                            + str(len(jpeg)).encode()
                            + b"\r\nX-Seq: " + str(seq).encode()
                            + b"\r\nX-Ts: " + f"{ts * 1000:.1f}".encode()
                            + b"\r\n\r\n" + jpeg + b"\r\n"
                        )
                except (ConnectionError, OSError):
                    pass
                finally:
                    buf.add_client(-1)
            else:
                self.send_error(404)

    return Handler


def local_ips():
    ips = set()
    main_ip = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))
        main_ip = s.getsockname()[0]
        ips.add(main_ip)
        s.close()
    except Exception:
        pass
    try:
        ips.update(socket.gethostbyname_ex(socket.gethostname())[2])
    except Exception:
        pass
    ips = [i for i in ips if not i.startswith("127.")]
    # Main-route address first, then ordinary ones, link-local (169.254.x.x) last
    return sorted(ips, key=lambda i: (i != main_ip, i.startswith("169.254."), i))


# ---------- broadcast control ----------
STOPPED, RUNNING, PAUSED = "stopped", "running", "paused"


class Broadcaster:
    def __init__(self, args, on_change, on_stats=None):
        self.args = args
        self.on_change = on_change
        self.on_stats = on_stats
        self.state = STOPPED
        self.lock = threading.Lock()
        self.buf = self.stop_evt = self.server = None
        self.paused = threading.Event()
        self.threads = []
        self.stats = {"grabs": 0, "frames": 0}
        self.fps_grab = 0.0    # how many times per second the window is grabbed
        self.fps_frames = 0.0  # how many new frames per second are actually encoded and sent

    def start(self):
        """Returns None on success or an error message."""
        with self.lock:
            if self.state != STOPPED:
                return None
            if not self.args.title:
                return T("no_window_selected")
            found = find_window(self.args.title, self.args.process)
            if not found:
                return WindowNotFound(T("window_not_found", title=self.args.title))
            hwnd, title = found
            self.buf = FrameBuffer()
            try:
                self.server = ThreadingHTTPServer(("0.0.0.0", self.args.port), make_handler(self.buf, lambda: {"state": self.state, "title": self.window_title()}))
            except OSError as e:
                return T("port_failed", port=self.args.port, err=e)
            self.server.daemon_threads = True
            self.stop_evt = threading.Event()
            self.paused.clear()
            self.stats = {"grabs": 0, "frames": 0, "hwnd": hwnd}
            self.fps_grab = self.fps_frames = 0.0
            self.threads = [
                threading.Thread(target=self.server.serve_forever, daemon=True),
                threading.Thread(
                    target=capture_loop,
                    args=(self.args, hwnd, title, self.buf, self.stop_evt, self.paused, self.stats),
                    daemon=True,
                ),
                threading.Thread(target=self._stats_loop, args=(self.stop_evt, self.stats), daemon=True),
            ]
            for t in self.threads:
                t.start()
            self.state = RUNNING
        print(T("broadcast_started", title=title, mode=self.args.mode))
        self.on_change()
        return None

    def window_title(self):
        """Current title of the streamed window (it may change, e.g. when a file is opened)."""
        try:
            hwnd = self.stats.get("hwnd")
            if hwnd and win32gui.IsWindow(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title.strip():
                    return title
        except Exception:
            pass
        return self.args.title

    def _stats_loop(self, stop_evt, stats):
        """Once a second computes the real capture and send frame rates."""
        last_t = time.time()
        last_g, last_f = stats["grabs"], stats["frames"]
        while not stop_evt.wait(1.0):
            now = time.time()
            dt = max(now - last_t, 1e-3)
            g, f = stats["grabs"], stats["frames"]
            self.fps_grab = (g - last_g) / dt
            self.fps_frames = (f - last_f) / dt
            last_t, last_g, last_f = now, g, f
            if self.on_stats and self.state == RUNNING:
                self.on_stats()

    def toggle_pause(self):
        with self.lock:
            if self.state == RUNNING:
                self.paused.set()
                self.fps_grab = self.fps_frames = 0.0
                self.state = PAUSED
            elif self.state == PAUSED:
                self.paused.clear()
                self.state = RUNNING
            else:
                return
        self.on_change()

    def stop(self):
        with self.lock:
            if self.state == STOPPED:
                return
            self.stop_evt.set()
            self.buf.close()  # client connections are closed
            self.server.shutdown()
            self.server.server_close()
            for t in self.threads:
                t.join(timeout=2)
            self.state = STOPPED
            self.fps_grab = self.fps_frames = 0.0
        print(T("broadcast_stopped"))
        self.on_change()


# ---------- tray icon ----------
def make_icon_image(state):
    color = {STOPPED: (130, 130, 130), RUNNING: (40, 170, 70), PAUSED: (230, 170, 20)}[state]
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((2, 2, 62, 62), fill=color)
    white = (255, 255, 255)
    if state == RUNNING:
        d.polygon([(24, 16), (24, 48), (50, 32)], fill=white)  # play
    elif state == PAUSED:
        d.rectangle((20, 17, 28, 47), fill=white)  # pause
        d.rectangle((36, 17, 44, 47), fill=white)
    else:
        d.rectangle((20, 20, 44, 44), fill=white)  # stop
    return img


STATE_KEY = {STOPPED: "state_stopped", RUNNING: "state_running", PAUSED: "state_paused"}


# ---------- settings file ----------
DEFAULT_SETTINGS = {
    "title": "",                  # window title (or part of it) to stream
    "process": "",                # exe name of the window: helps find it when the title changes
    "port": 8080,
    "fps": 10.0,
    "quality": 75,
    "scale": 1.0,
    "mode": "screen",             # screen or printwindow
    "no_diff": False,
    "no_turbo": False,
    "autostart_broadcast": True,  # start broadcasting right when the program starts
    "language": "en",             # interface language: en or ru
}


def _to_bool(v):
    return v if isinstance(v, bool) else str(v).strip().lower() in ("1", "true", "yes", "on", "да")


_SETTING_TYPES = {
    "title": str, "process": str, "port": int, "fps": float, "quality": int, "scale": float,
    "mode": str, "no_diff": _to_bool, "no_turbo": _to_bool, "autostart_broadcast": _to_bool,
    "language": str,
}


def default_config_path():
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    return os.path.join(base, "WindowStream", "settings.json")


def load_settings(path):
    s = dict(DEFAULT_SETTINGS)
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return s
    except Exception as e:
        print(T("settings_read_failed", path=path, err=e))
        return s
    for key, cast in _SETTING_TYPES.items():
        if key in data:
            try:
                s[key] = cast(data[key])
            except (TypeError, ValueError):
                print(T("setting_invalid", key=key))
    if s["mode"] not in ("screen", "printwindow"):
        s["mode"] = "screen"
    s["language"] = str(s["language"]).strip().lower()
    if s["language"] not in I18N:
        s["language"] = "en"
    return s


def save_settings(path, settings):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(T("settings_save_failed", path=path, err=e))
        return False


# ---------- autostart with Windows ----------
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
RUN_NAME = "WindowStream"


def autostart_command(cfg_path):
    if getattr(sys, "frozen", False):  # built exe
        cmd = f'"{sys.executable}"'
    else:
        exe = sys.executable
        pyw = os.path.join(os.path.dirname(exe), "pythonw.exe")  # run without a console window
        if os.path.exists(pyw):
            exe = pyw
        cmd = f'"{exe}" "{os.path.abspath(__file__)}"'
    if os.path.abspath(cfg_path) != os.path.abspath(default_config_path()):
        cmd += f' --config "{cfg_path}"'
    return cmd


def autostart_value():
    """Current autostart command from the registry, or None if autostart is off."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as k:
            return winreg.QueryValueEx(k, RUN_NAME)[0]
    except OSError:
        return None


def autostart_enabled():
    return autostart_value() is not None


def set_autostart(enable, cmd):
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as k:
        if enable:
            winreg.SetValueEx(k, RUN_NAME, 0, winreg.REG_SZ, cmd)
        else:
            try:
                winreg.DeleteValue(k, RUN_NAME)
            except FileNotFoundError:
                pass


def menu_text(title, limit=55):
    t = title if len(title) <= limit else title[: limit - 1] + "…"
    return t.replace("&", "&&")  # a single & in a Windows menu marks a hotkey


_instance_mutex = None  # the mutex reference must be kept while the program runs


def acquire_single_instance(key):
    """Acquires a named mutex. False if such a copy of the program is already running.
    The key is the settings file path: copies with different settings may run simultaneously."""
    global _instance_mutex
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    k32.CreateMutexW.restype = ctypes.c_void_p
    k32.CreateMutexW.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_wchar_p]
    name = "Local\\WindowStream_" + format(zlib.crc32(os.path.abspath(key).lower().encode("utf-8")), "08x")
    handle = k32.CreateMutexW(None, 0, name)
    if not handle:
        return True  # could not create the mutex - do not block startup
    if ctypes.get_last_error() == 183:  # ERROR_ALREADY_EXISTS
        return False
    _instance_mutex = handle
    return True


def message_box(text, title=None):
    title = title or T("msg_title")
    try:
        # 0x40 - "information" icon, 0x40000 - topmost
        ctypes.windll.user32.MessageBoxW(None, text, title, 0x40 | 0x40000)
    except Exception:
        print(text)


def attach_console():
    """An exe built without a console has no stdout. For --list and --help we attach
    to the console it was launched from (if there is one)."""
    if sys.stdout is not None:
        return
    try:
        if ctypes.windll.kernel32.AttachConsole(0xFFFFFFFF):  # ATTACH_PARENT_PROCESS
            sys.stdout = sys.stderr = open("CONOUT$", "w", encoding="utf-8")
    except Exception:
        pass


class TrayIcon(pystray.Icon):
    """Icon that rebuilds its menu before showing it.
    On Windows pystray builds the menu once (and on update_menu), so without this the window list
    and checkmarks would be stale: windows opened after startup would never appear in it."""

    def _on_notify(self, wparam, lparam):
        if lparam == 0x0205:  # WM_RBUTTONUP: the user opens the menu
            try:
                self.update_menu()
            except Exception:
                pass
        return super()._on_notify(wparam, lparam)


def main():
    global LANG
    if any(a in sys.argv for a in ("--list", "--version", "-h", "--help")):
        attach_console()
    # The interface language comes from the settings file, so find the file before building the parser
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument("--config")
    pre_args, _ = pre.parse_known_args()
    LANG = load_settings(pre_args.config or default_config_path())["language"]

    p = argparse.ArgumentParser(
        description=T("argp_desc"),
        epilog=T("argp_epilog", path=default_config_path()),
    )
    p.add_argument("--title", default=None, help=T("help_title"))
    p.add_argument("--list", action="store_true", help=T("help_list"))
    p.add_argument("--port", type=int, default=None, help=T("help_port"))
    p.add_argument("--fps", type=float, default=None, help=T("help_fps"))
    p.add_argument("--quality", type=int, default=None, help=T("help_quality"))
    p.add_argument("--scale", type=float, default=None, help=T("help_scale"))
    p.add_argument("--mode", choices=["screen", "printwindow"], default=None, help=T("help_mode"))
    p.add_argument("--no-autostart", action="store_true", help=T("help_no_autostart"))
    p.add_argument("--no-diff", action="store_true", help=T("help_no_diff"))
    p.add_argument("--no-turbo", action="store_true", help=T("help_no_turbo"))
    p.add_argument("--config", help=T("help_config"))
    p.add_argument("--save", action="store_true", help=T("help_save"))
    p.add_argument("--version", action="version", version=f"WindowStream {__version__}", help=T("help_version"))
    args = p.parse_args()

    if args.list:
        for hwnd, title in list_windows():
            print(f"{hwnd:>10}  {process_name(hwnd) or '-':<24}  {title}")
        return

    cfg_path = args.config or default_config_path()
    if not acquire_single_instance(cfg_path):
        message_box(T("already_running"))
        return
    settings = load_settings(cfg_path)

    # Command-line options take precedence over the settings file
    if args.title is None or args.title == settings["title"]:
        args.process = settings["process"]
    else:
        args.process = ""  # title set manually - the process from the file does not apply to it
    for key in ("title", "port", "fps", "quality", "scale", "mode"):
        if getattr(args, key) is None:
            setattr(args, key, settings[key])
    args.no_diff = args.no_diff or settings["no_diff"]
    args.no_turbo = args.no_turbo or settings["no_turbo"]
    args.autostart_broadcast = settings["autostart_broadcast"] and not args.no_autostart
    args.fps = max(0.5, args.fps)
    args.quality = min(95, max(1, args.quality))
    args.scale = max(0.1, args.scale)

    if args.save or not os.path.exists(cfg_path):
        for key in ("title", "process", "port", "fps", "quality", "scale", "mode", "no_diff", "no_turbo"):
            settings[key] = getattr(args, key)
        if save_settings(cfg_path, settings):
            print(T("settings_saved"), cfg_path)

    if args.no_turbo:
        print(T("enc_pillow_off"))
    elif _turbo is not None:
        print(T("enc_turbo"))
    else:
        print(T("enc_pillow_unavail", err=_turbo_error))

    ip_cache = [0.0, []]

    def get_url():
        # Recompute the address: at autostart the network may come up later than the program
        if time.time() - ip_cache[0] > 10:
            ip_cache[:] = [time.time(), local_ips()]
        ips = ip_cache[1]
        return f"http://{ips[0]}:{args.port}/" if ips else T("port_label", port=args.port)

    icon = None

    def tooltip():
        tip = T("tip_title", state=T(STATE_KEY[bc.state]))
        if bc.state == RUNNING:
            clients = bc.buf.clients if bc.buf else 0
            tip += "\n" + T("tip_stats", grab=bc.fps_grab, frames=bc.fps_frames, clients=clients)
        if bc.state != STOPPED:
            tip += f"\n{get_url()}"
        return tip[:127]  # Windows tooltip length limit

    def refresh():
        if icon is None:
            return
        icon.icon = make_icon_image(bc.state)
        icon.title = tooltip()
        icon.update_menu()

    def refresh_tooltip():
        if icon is None:
            return
        tip = tooltip()
        if icon.title != tip:
            icon.title = tip

    bc = Broadcaster(args, refresh, refresh_tooltip)
    cancel_auto = threading.Event()

    def notify(msg, title=None):
        try:
            title = title or T("msg_title")
            icon.notify(msg, title)
        except Exception:
            pass

    def auto_start_loop():
        """Runs at program start; if the window does not exist yet (e.g. right after Windows login), wait for it."""
        warned = False
        while not cancel_auto.is_set():
            err = bc.start()
            if not err:
                notify(T("open_on_tablet", url=get_url()), T("broadcast_started_title"))
                return
            if not isinstance(err, WindowNotFound):
                notify(err, T("error_title"))
                return
            if not warned:
                notify(err + T("waiting_window"))
                warned = True
            cancel_auto.wait(5)

    def do_start(icon_=None, item=None):
        cancel_auto.set()
        err = bc.start()
        if err:
            notify(err, T("error_title"))
        else:
            notify(T("open_on_tablet", url=get_url()), T("broadcast_started_title"))

    def do_pause(icon_=None, item=None):
        bc.toggle_pause()

    def do_stop(icon_=None, item=None):
        cancel_auto.set()
        bc.stop()

    def do_exit(icon_=None, item=None):
        cancel_auto.set()
        bc.stop()
        icon.stop()

    def select_window(w):
        cancel_auto.set()
        args.title, args.process = w["title"], w["process"]
        settings["title"], settings["process"] = args.title, args.process
        save_settings(cfg_path, settings)
        # Screen mode captures what is visible on the screen: the window must be restored and not covered
        try:
            was_min = win32gui.IsIconic(w["hwnd"])
            bring_to_front(w["hwnd"])
            time.sleep(0.4 if was_min else 0.15)  # let the window repaint
        except Exception:
            pass
        bc.stop()
        err = bc.start()
        if err:
            notify(err, T("error_title"))
        else:
            notify(T("streaming", title=w["title"], url=get_url()), T("broadcast_started_title"))
        refresh()

    def make_select(w):
        def action(icon_, item):
            select_window(w)
        return action

    def make_checked(w):
        return lambda item: w["title"] == args.title and (not args.process or w["process"] == args.process)

    def windows_menu():
        items = [
            pystray.MenuItem(menu_text(w["title"]), make_select(w), checked=make_checked(w), radio=True)
            for w in app_windows()[:40]
        ]
        if not items:
            items = [pystray.MenuItem(T("no_windows"), lambda icon_, item: None, enabled=False)]
        return items

    def window_label(item=None):
        return T("window_label", title=menu_text(args.title, 30) if args.title else T("not_selected"))

    def do_toggle_autostart(icon_=None, item=None):
        try:
            enable = not autostart_enabled()
            set_autostart(enable, autostart_command(cfg_path))
            notify(T("autostart_on") if enable else T("autostart_off"))
        except Exception as e:
            notify(T("autostart_failed", err=e), T("error_title"))
        icon.update_menu()

    def do_open_settings(icon_=None, item=None):
        try:
            if not os.path.exists(cfg_path):
                save_settings(cfg_path, settings)
            subprocess.Popen(["notepad.exe", cfg_path])
        except Exception as e:
            notify(T("settings_open_failed", err=e), T("error_title"))

    def do_raise(icon_=None, item=None):
        found = find_window(args.title, args.process)
        if found:
            bring_to_front(found[0])
        else:
            notify(T("window_not_found", title=args.title), T("error_title"))

    menu = pystray.Menu(
        pystray.MenuItem(T("menu_start"), do_start, enabled=lambda i: bc.state == STOPPED),
        pystray.MenuItem(
            lambda i: T("menu_resume") if bc.state == PAUSED else T("menu_pause"),
            do_pause,
            enabled=lambda i: bc.state != STOPPED,
        ),
        pystray.MenuItem(T("menu_stop"), do_stop, enabled=lambda i: bc.state != STOPPED),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(window_label, pystray.Menu(windows_menu)),
        pystray.MenuItem(T("menu_raise"), do_raise, enabled=lambda i: bool(args.title)),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(T("menu_autostart"), do_toggle_autostart,
                         checked=lambda i: autostart_enabled()),
        pystray.MenuItem(T("menu_settings"), do_open_settings),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(T("menu_exit"), do_exit),
    )
    icon = TrayIcon("window_stream", make_icon_image(STOPPED), T("tip_title", state=T("state_stopped")), menu)

    def setup(icon_):
        icon_.visible = True
        if getattr(sys, "frozen", False):
            # If the exe was moved to another folder, update the autostart path
            try:
                cmd = autostart_command(cfg_path)
                cur = autostart_value()
                if cur is not None and cur != cmd:
                    set_autostart(True, cmd)
            except Exception:
                pass
        print(T("pc_addresses"))
        for ip in ip_cache[1] or local_ips():
            print(f"  http://{ip}:{args.port}/")
        if not args.autostart_broadcast:
            return
        if args.title:
            threading.Thread(target=auto_start_loop, daemon=True).start()
        else:
            notify(T("choose_window"))

    icon.run(setup)


if __name__ == "__main__":
    main()
