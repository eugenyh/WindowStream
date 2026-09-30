# WindowStream

**Show a single Windows application window in any web browser on your local network — live, view-only, no client software.**

WindowStream is a small Windows tray application written in Python. It captures the contents of one chosen window and serves it as an MJPEG stream over HTTP. Open `http://<PC-address>:8080/` in the browser of a tablet, phone or another computer and you see what that window shows on the PC, updating in real time. Nothing can be controlled from the viewer: it is a one-way, read-only mirror of a single window.

It was built for a concrete need — showing a map application running on a work PC on an Android tablet over Wi-Fi — but it works with any window.

> **UI language.** The tray menu, notifications, console messages and the web viewer are in **English** by default. Set `"language": "ru"` in the [settings file](#settings-file) for Russian (see [Interface language](#interface-language)). Every tray menu item is listed in both languages in [Tray icon and menu](#tray-icon-and-menu). User manuals for the ready-made `.exe` are available in Russian (`user_manual_ru.md`), English (`user_manual_en.md`) and German (`user_manual_de.md`).

---

## Table of contents

- [Features](#features)
- [How it works](#how-it-works)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick start](#quick-start)
- [Usage](#usage)
  - [Tray icon and menu](#tray-icon-and-menu)
  - [Choosing the window](#choosing-the-window)
  - [The web viewer](#the-web-viewer)
  - [Command-line reference](#command-line-reference)
  - [Settings file](#settings-file)
  - [Interface language](#interface-language)
  - [Start with Windows](#start-with-windows)
  - [Single instance and multiple instances](#single-instance-and-multiple-instances)
- [Capture modes](#capture-modes)
- [Performance tuning](#performance-tuning)
- [HTTP endpoints and stream format](#http-endpoints-and-stream-format)
- [Building a standalone executable](#building-a-standalone-executable)
- [Networking and security](#networking-and-security)
- [Troubleshooting](#troubleshooting)
- [Known limitations](#known-limitations)
- [Project layout and code map](#project-layout-and-code-map)
- [License](#license)

---

## Features

**Streaming**

- Streams the client area of one window as MJPEG (`multipart/x-mixed-replace`) — works in any modern browser, no plugins.
- Strictly view-only: the viewer cannot send any input to the PC.
- Two capture modes: `screen` (copy of what is visible on screen) and `printwindow` (asks the window itself to render, so other windows on top do not appear in the stream).
- Change detection: a CRC32 of the raw frame is compared with the previous one, so an unchanged picture costs almost no CPU and no network traffic.
- Fast JPEG encoding through libjpeg-turbo (PyTurboJPEG), with an automatic fallback to Pillow.
- Adjustable frame rate, JPEG quality and scale.
- Several viewers can watch at the same time.

**Tray application**

- Lives in the system tray; colour-coded icon (grey — stopped, green — streaming, amber — paused).
- Menu: start, pause/resume, stop, pick the window from a list of open windows, bring the window to the front, toggle *start with Windows*, open the settings file, exit.
- Tooltip shows the real capture rate, the rate of new frames, the number of connected viewers and the address to open.
- Notifications for start, errors and waiting for the window.
- Bilingual interface (English by default, Russian on request).

**Convenience**

- Settings are stored in a JSON file; command-line switches override it, and `--save` writes them back.
- The chosen window is remembered by title *and* by process, so it is found again even if its title changes (for example when another document is opened).
- Start with Windows (per-user, no administrator rights). If the window is not open yet at logon, the program waits for it.
- Only one copy runs at a time per settings file; a second launch says the program is already running and exits.
- Single-file `.exe` build with PyInstaller (script included).

**Web viewer**

- Rounded "bezel" frame filling the whole browser window; the picture is fitted with the aspect ratio kept.
- Status badge in the top-right corner: *Live* / *Paused* / *No connection*; the frame glow follows the state.
- Pinch-to-zoom (up to ×8), drag to pan, double-tap to zoom in/out, mouse wheel on desktop.
- Live *fps* and *latency* readout (long-press to hide/show).
- The badge and buttons auto-hide during normal streaming and reappear on tap; they stay visible on pause and connection loss.
- Fullscreen button; the browser tab title follows the streamed window's title.
- Automatic reconnection when the PC side is restarted, stopped or the network drops.

---

## How it works

```
          Windows PC                                            Viewer (tablet / phone / PC)
 ┌─────────────────────────────────────────────────────────────────────────────────────┐        ┌───────────────────────────┐
 │  target window                                                                      │        │  browser                  │
 │       │  screen copy (mss)  or  PrintWindow                                         │        │   GET /          (page)   │
 │       ▼                                                                             │        │   GET /status    (1 Hz)   │
 │  capture thread ──► CRC32 changed? ──► JPEG                                         │  HTTP  │   GET /stream    (MJPEG)  │
 │                                        │                                            │ ─────► │        │                  │
 │                                        ▼                                            │        │        ▼                  │
 │                                  FrameBuffer                                        │        │  parse frames, show, zoom │
 │                                        │                                            │        └───────────────────────────┘
 │                     HTTP server threads (one per viewer)                            │
 │                                                                                     │                           
 │  tray icon (main thread) ◄─► Broadcaster (start / pause / stop, window switching)   │
 └─────────────────────────────────────────────────────────────────────────────────────┘
```

**Threads**

| Thread | Purpose |
| --- | --- |
| Main | Runs the tray icon (`pystray`) and its menu callbacks. |
| HTTP server | `ThreadingHTTPServer.serve_forever`; every request (and every open `/stream`) is handled in its own daemon thread. |
| Capture | Grabs the window at up to `--fps` times per second, detects changes, encodes JPEG, publishes it to the `FrameBuffer`. |
| Statistics | Once per second computes the real capture rate and new-frame rate for the tray tooltip. |
| Auto-start | At launch, retries starting the broadcast every 5 s until the window appears. |

**Frame buffer.** The capture thread publishes the latest JPEG together with a sequence number and the capture timestamp into a `FrameBuffer` guarded by a condition variable. Each `/stream` connection waits for a new sequence number and writes the newest frame; a slow viewer therefore skips frames instead of building up a queue, and one slow viewer does not slow down the others.

**Keep-alive.** If nothing changes for 5 seconds, the server re-sends the latest frame with the *same* sequence number. This keeps the connection alive and lets the page tell "no new frame" from "connection lost".

**Latency estimate.** The page polls `/status` once per second. The response contains the PC clock (`t`, milliseconds). From the round-trip time the page estimates the clock offset between the PC and the viewer (it keeps the sample with the smallest round trip out of the last 30) and computes `latency = now − capture_timestamp + offset` for every new frame. This is capture-to-receive time; decoding and painting add a little on top.

---

## Requirements

**To run the prebuilt `.exe`:** Windows 10 or 11 (64-bit). Nothing else — Python is not needed.

**To run from source:**

- Windows 10 / 11
- Python 3.9 or newer (64-bit)
- Packages (also listed in `requirements.txt`):

| Package | Used for | Required |
| --- | --- | --- |
| `pywin32` | window enumeration, window capture, process info | yes |
| `Pillow` | image handling, tray icon drawing, fallback JPEG encoder | yes |
| `mss` | fast screen capture | yes |
| `pystray` | system tray icon and menu | yes |
| `numpy` | passing frames to TurboJPEG | only for TurboJPEG |
| `PyTurboJPEG` | fast JPEG encoding | optional |
| libjpeg-turbo (native DLL) | backend for PyTurboJPEG | optional |

**Viewer:** any modern browser that supports `fetch` streaming and Pointer Events (current versions of Chrome, Edge, Firefox and other Chromium-based browsers, including the Android ones), on the same network as the PC.

---

## Installation

### Option A — prebuilt executable

1. Download `WindowStream.exe` from the [latest release](https://github.com/eugenyh/WindowStream/releases/latest) (each release lists a SHA-256 checksum; `--version` shows the version you have).
2. Put it in a permanent folder (for example `C:\Tools\WindowStream\`). Do not run it from a temporary or *Downloads* folder if you plan to use *Start with Windows*.
3. Run it. On first start Windows may show a SmartScreen warning (the file is not code-signed) and a firewall prompt — allow access on **private** networks.

### Option B — from source

```bat
git clone https://github.com/eugenyh/WindowStream.git
cd WindowStream

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
```

**Optional but recommended — libjpeg-turbo.** PyTurboJPEG needs the native library. Download the official *libjpeg-turbo* installer for Visual C++ (64-bit) from the project's releases page and install it to the default folder `C:\libjpeg-turbo64`. Without it the program prints a notice and encodes with Pillow, which works but uses more CPU.

Run:

```bat
python window_stream.py
```

To run without a console window use `pythonw window_stream.py`.

---

## Quick start

1. Start the program. A grey icon appears in the notification area (it may be under the ^ *Show hidden icons* arrow).
2. Right-click the icon → **Window: not selected** → choose the window to share. The broadcast starts immediately and the icon turns green.
3. Hover the icon: the tooltip shows the address, for example `http://192.168.1.20:8080/`.
4. Open that address in the browser of the tablet (same network).
5. Done. Next time the program starts, it remembers the window and begins streaming by itself.

Or, from the command line, in one step:

```bat
python window_stream.py --title "Untitled - Map" --mode printwindow --save
```

---

## Usage

### Tray icon and menu

**Icon states**

| Icon | Meaning |
| --- | --- |
| Grey circle with a square | Stopped |
| Green circle with a triangle | Streaming |
| Amber circle with two bars | Paused |

**Tooltip** (streaming):

```
Window broadcast: live
Capture 10 fps · new frames 3 fps · clients 1
http://192.168.1.20:8080/
```

- *Capture* — how many times per second the window is actually grabbed.
- *new frames* — how many changed frames per second are encoded and sent. It is `0` while the picture does not change; that is normal.
- *clients* — number of open viewer connections.

**Tray menu**

| Menu item (English, default) | Russian (`"language": "ru"`) | What it does |
| --- | --- | --- |
| Start broadcast | Начать трансляцию | Starts the server and capture. Enabled when stopped. |
| Pause / Resume | Пауза / Продолжить | Freezes capture. Viewers keep the last frame and see *Paused*. |
| Stop broadcast | Закончить трансляцию | Stops capture and closes the server and all connections. |
| Window: *title* ▸ (or *Window: not selected*) | Окно: *title* ▸ (or *Окно: не выбрано*) | Submenu listing open windows; the current one is marked. Selecting a window saves it, brings it to the front and restarts the broadcast on it. |
| Bring window to front | Вывести окно на передний план | Restores (if minimized) and activates the streamed window. |
| Start with Windows | Запускать вместе с Windows | Toggles the autostart registry entry. |
| Open settings file | Открыть файл настроек | Opens the JSON settings in Notepad. |
| Exit | Выйти | Stops everything and quits. |

**Notifications** (Windows toast / balloon)

| Text (English, default) | Russian | Meaning |
| --- | --- | --- |
| Broadcast started — Open on the tablet: *url* | Трансляция запущена — Откройте на планшете: *url* | Broadcast started |
| Streaming: *title* + *url* | Транслируется: *title* + *url* | Broadcast switched to the window chosen in the menu |
| Window "…" not found. Waiting for the window to appear... | Окно «…» не найдено. Жду появления окна... | Target window is not open yet; retrying every 5 s |
| No window selected: choose one in the tray menu ("Window" item) / Choose a window in the tray menu: "Window" item | Окно не выбрано: выберите его в меню трея (пункт «Окно») / Выберите окно в меню иконки: пункт «Окно» | No window configured yet |
| Could not open port *N*: … | Не удалось открыть порт *N*: … | The port is in use by another program |
| The program will start with Windows / Autostart disabled | Программа будет запускаться вместе с Windows / Автозапуск отключён | Autostart toggled |

### Choosing the window

The window to stream is described by a **title** (a full title or any part of it) and optionally a **process name** (for example `myapp.exe`). Selecting a window from the tray menu stores both.

Matching rules, in order of priority (case-insensitive):

1. the title equals the saved title;
2. the title starts with the saved text;
3. the title contains the saved text;
4. if a process name is saved and no title matched: the **largest visible window of that process** (so the stream survives a title change, e.g. when another document is opened in the same application).

If a process is saved, only windows of that process are considered.

The following are never matched or listed: console windows (classic console, Windows Terminal), the desktop, tool windows, cloaked/hidden UWP windows and — in the menu — the program's own windows and windows smaller than 50×50 px (unless minimized). The menu shows up to 40 windows, sorted by title.

Tip: run `WindowStream.exe --list` from a console to print handle, process and title of every window.

### The web viewer

**Status badge (top right)**

| Badge | State |
| --- | --- |
| green pulsing dot, **Live** | Live |
| amber dot, **Paused** | Paused on the PC — the picture is frozen and dimmed |
| red dot, **No connection** | The PC is unreachable or the broadcast is stopped — the picture is greyed out with an overlay; the page reconnects automatically |

While live, the badge shows `N fps · M ms` (received new frames per second · estimated latency). In Russian mode the labels are *Транслируется* / *Пауза* / *Нет связи* and `мс`.

**Controls**

| Action | Result |
| --- | --- |
| Tap | Show the badge and buttons (they auto-hide after 4 s while live) |
| Pinch with two fingers | Zoom, up to ×8 |
| Drag with one finger (when zoomed) | Pan |
| Double-tap | Zoom in ×2.5 at that point / reset if already zoomed |
| Tap the `×N · reset` pill (bottom right) | Reset zoom |
| Long-press (~0.7 s) | Hide / show the fps · latency readout (remembered in the browser) |
| Button in the top-left corner | Fullscreen on/off |
| Mouse wheel (desktop) | Zoom around the cursor |

The browser tab title equals the streamed window's title and follows it when it changes.

> For a sharp picture when zoomed in, use `--scale 1.0` (the default). With a smaller scale the frame is already downsized on the PC.

### Command-line reference

```
window_stream.py [options]
WindowStream.exe [options]
```

| Option | Default | Description |
| --- | --- | --- |
| `--title TEXT` | from settings | Window title or part of it. If it differs from the saved title, the saved process name is ignored. |
| `--list` | — | Print all windows (handle, process, title) and exit. |
| `--port N` | `8080` | HTTP port. |
| `--fps N` | `10` | Maximum captured frames per second (minimum 0.5). |
| `--quality N` | `75` | JPEG quality, clamped to 1–95. |
| `--scale X` | `1.0` | Scale factor of the sent frame (minimum 0.1); e.g. `0.5`. |
| `--mode screen\|printwindow` | `screen` | [Capture mode](#capture-modes). |
| `--no-diff` | off | Disable change detection: encode and send every captured frame. |
| `--no-turbo` | off | Force the Pillow JPEG encoder (for comparison). |
| `--no-autostart` | off | Do **not** start broadcasting on launch; wait for the menu. (Unrelated to *Start with Windows*.) |
| `--config PATH` | `%APPDATA%\WindowStream\settings.json` | Use another settings file. |
| `--save` | off | Write this run's parameters to the settings file. |
| `-h`, `--help` | — | Show help (in the interface language). |
| `--version` | — | Print the program version and exit. |

In the windowed `.exe` there is no console of its own: `--list`, `--help` and `--version` attach to the console they were started from (the program looks for it up the chain of parent processes, because a `--onefile` exe is started through a bootloader). The exe is a windowed program, so `cmd.exe` does not wait for it and the prompt may return before the text appears; use `start /wait "" WindowStream.exe --list` to wait. If no console is found (for example, started by double-click), the text is shown in a message box.

### Settings file

Location: `%APPDATA%\WindowStream\settings.json`. It is created on the first run from the effective parameters of that run. Use the tray item *Open settings file* to edit it; **restart the program** after editing.

```json
{
  "title": "Untitled - Map",
  "process": "mapapp.exe",
  "port": 8080,
  "fps": 15.0,
  "quality": 75,
  "scale": 1.0,
  "mode": "printwindow",
  "no_diff": false,
  "no_turbo": false,
  "autostart_broadcast": true,
  "language": "en"
}
```

| Key | Type | Default | Meaning |
| --- | --- | --- | --- |
| `title` | string | `""` | Window title or part of it. |
| `process` | string | `""` | Executable name of the window's process (helps when the title changes). |
| `port` | integer | `8080` | HTTP port. |
| `fps` | number | `10` | Maximum captured frames per second. |
| `quality` | integer | `75` | JPEG quality 1–95. |
| `scale` | number | `1.0` | Frame scale. |
| `mode` | string | `"screen"` | `"screen"` or `"printwindow"`. |
| `no_diff` | boolean | `false` | Disable change detection. |
| `no_turbo` | boolean | `false` | Force Pillow encoder. |
| `autostart_broadcast` | boolean | `true` | Begin broadcasting right after the program starts. |
| `language` | string | `"en"` | Interface language: `"en"` (English, default) or `"ru"` (Russian). Affects the tray menu, notifications, console messages, `--help` and the web page. Restart the program after changing it. |

**Precedence:** command-line options override the file. Boolean switches can only turn a feature *on* from the command line; to turn one off, edit the file. `--save` stores `title`, `process`, `port`, `fps`, `quality`, `scale`, `mode`, `no_diff` and `no_turbo` (not `autostart_broadcast` or `language`). A malformed file is ignored (defaults are used); wrong values of individual keys are skipped.

### Interface language

All user-visible text lives in the `I18N` dictionary in `window_stream.py` (`en` and `ru`), looked up with `T(key, **kw)`. The language is chosen once at startup from the `language` key of the settings file; an unknown value falls back to English. There is no command-line switch for it, so it is never written by `--save`.

The web page uses `@@key@@` tokens that are replaced with the `web_*` strings when the page is served, so the viewer follows the same language as the tray. To add a language, add a complete set of keys to `I18N` (the key sets of all languages must match).

### Start with Windows

The tray item **Start with Windows** adds or removes the value `WindowStream` under

```
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
```

No administrator rights are needed and it applies to the current user only.

- From the `.exe`: the value is the quoted path to the executable.
- From source: `pythonw.exe "<path>\window_stream.py"` (no console window).
- A non-default `--config` path is appended automatically.
- If the `.exe` is moved, the registry path is refreshed the next time the program is started from its new location.
- At logon the window may not be open yet. The program then waits and retries every 5 seconds until it appears.

### Single instance and multiple instances

A named mutex (`Local\WindowStream_<hash of the settings-file path>`) prevents starting a second copy that uses the same settings file. The second copy shows *"The program is already running."* and exits. `--list` and `--help` still work while another copy is running.

To stream two windows at once, run two copies with **different** `--config` files and different ports.

---

## Capture modes

| | `screen` (default) | `printwindow` |
| --- | --- | --- |
| How | Copies the window rectangle from the screen (`mss`) | Calls `PrintWindow` with `PW_CLIENTONLY \| PW_RENDERFULLCONTENT` |
| Other windows on top | **Appear in the stream** | Do not appear |
| Window on another virtual desktop / behind others | Captures whatever is on screen there | Works |
| GPU-accelerated / DirectX / video content | Works | May produce a black or stale frame in some applications |
| Minimized window | Not captured | Not captured |
| Part of the window outside the screen | Not painted by Windows | Not repainted by the application (stays frozen) |

Recommendation: try `printwindow` first (`--mode printwindow --save`); if the picture is black or wrong for your application, use `screen` and keep the window in front. When you select a window from the tray menu, it is restored and brought to the front automatically, which matters for `screen` mode.

The captured area is always the **client area** (without the title bar and borders), at real pixel size (the process is DPI-aware).

---

## Performance tuning

CPU is spent mainly on JPEG encoding and, when scaling, on resizing. Network use is proportional to frame size × new frames per second.

| Goal | What to change |
| --- | --- |
| Lower CPU | Lower `--fps`; use `--scale 0.5–0.75`; keep change detection on; install libjpeg-turbo so TurboJPEG is used. |
| Smoother motion | Raise `--fps` (20–30); make sure TurboJPEG is active; use 5 GHz Wi-Fi. |
| Sharper image / zoom | `--scale 1.0`, `--quality 80–90`. |
| Save bandwidth | `--quality 55–65`, `--scale 0.5–0.75`. |
| Diagnose | Watch the tray tooltip: if *capture* is well below `--fps`, the PC cannot keep up. |

Notes:

- With change detection on (default), a static picture costs almost nothing. `--no-diff` re-encodes every frame and is only useful for comparison.
- With `scale = 1.0` TurboJPEG encodes the raw capture buffer directly (fastest path). With `scale ≠ 1.0` the frame is first resized with Pillow (bilinear).
- The TurboJPEG encoder uses the fast-DCT flag and default 4:2:2 chroma subsampling.

---

## HTTP endpoints and stream format

The server is a standard-library `ThreadingHTTPServer` (HTTP/1.0) listening on `0.0.0.0:<port>`.

| Endpoint | Description |
| --- | --- |
| `GET /` , `/index.html` | The web viewer page (the tab title is filled with the window title). |
| `GET /stream` | MJPEG stream, `multipart/x-mixed-replace; boundary=frame`. |
| `GET /status` | JSON: `{"state": "running" \| "paused", "title": "<window title>", "t": <PC time, ms>}`. |
| `GET /snapshot.jpg` | The latest frame as a single JPEG (`503` if none has been captured yet). |

**Stream format.** Each part carries two extra headers used by the viewer; a plain `<img src="…/stream">` should still work, because browsers ignore part headers they do not know.

```
--frame
Content-Type: image/jpeg
Content-Length: 123456
X-Seq: 42
X-Ts: 1759140000123.4

<JPEG bytes>
```

- `X-Seq` — frame sequence number; a repeated number is a keep-alive re-send.
- `X-Ts` — capture time on the PC (Unix time, milliseconds).

Timing constants: server keep-alive 5 s; page polls `/status` every 1 s; stream reconnect 1.5 s; watchdog aborts a silent stream after 12 s; the UI auto-hides after 4 s.

---

## Building a standalone executable

Build on Windows (PyInstaller cannot cross-compile).

1. Install the runtime dependencies (see [Installation](#option-b--from-source)) and, ideally, libjpeg-turbo at `C:\libjpeg-turbo64` (`build_exe.bat` also looks in `D:\libjpeg-turbo64`).
2. Put `window_stream.py`, `build_exe.bat` and `make_icon.py` in one folder and run:

```bat
build_exe.bat
```

The script installs PyInstaller, generates `icon.ico`, and runs:

```bat
python -m PyInstaller --noconfirm --clean --onefile --noconsole ^
    --name WindowStream --icon icon.ico ^
    --hidden-import pystray._win32 ^
    --exclude-module tkinter --exclude-module matplotlib ^
    --add-binary "C:\libjpeg-turbo64\bin\turbojpeg.dll;." window_stream.py
```

Result: `dist\WindowStream.exe`.

Details worth knowing:

- `turbojpeg.dll` is bundled into the executable and located at runtime through `sys._MEIPASS`, so target machines need nothing installed. If the DLL is missing at build time the script warns you and the build falls back to Pillow encoding.
- `--hidden-import pystray._win32` is required: `pystray` picks its backend dynamically and PyInstaller does not detect it.
- `--noconsole` produces a GUI executable with no `stdout`; diagnostics are shown as tray notifications. For `--list` / `--help` the program attaches to the parent console.
- A `--onefile` executable unpacks itself to a temporary folder on every launch (1–3 s) and is ~40–60 MB because of numpy and Pillow. Use `--onedir` for faster start-up.
- Unsigned PyInstaller binaries are sometimes flagged by antivirus software (false positives are common with `pywin32`). Sign the executable or add an exclusion if needed.
- The `.bat` file must have Windows (CRLF) line endings.

**Publishing a release.** The built `dist\WindowStream.exe` is not stored in git (`dist/` is ignored); attach it to a GitHub release instead:

1. Set `__version__` in `window_stream.py` (semantic versioning, e.g. `1.0.0`), commit and merge to `main`.
2. Build with `build_exe.bat` and check the result: `dist\WindowStream.exe --version` from a console.
3. On GitHub: **Releases → Draft a new release**, create the tag `v<version>` (it must match `__version__`) on `main`, attach `WindowStream.exe`, add the SHA-256 (`Get-FileHash dist\WindowStream.exe` in PowerShell) and the change notes.

---

## Networking and security

- The server listens on **all interfaces**, without authentication and without encryption (plain HTTP). **Anyone who can reach the port can watch the window.** Use it only on trusted networks.
- Windows Firewall will ask on first start — allow **private** networks only. To restrict further, create an inbound rule for the program/port limited to your local subnet.
- Many Wi-Fi routers offer *client isolation* (AP isolation) which blocks device-to-device traffic; disable it for the network you use.
- Addresses `169.254.x.x` are link-local (Windows could not obtain an address from a DHCP server). They work only if the viewer is also in that range. Prefer a normal address such as `192.168.x.x` / `10.x.x.x`; it is listed first when available.
- The tray tooltip shows the preferred address; `ipconfig` lists all of them.
- The viewer is read-only, but the *content of the window* is exposed to everyone who connects. Do not stream windows with confidential data on shared networks.
- To reach it from outside the LAN, use a VPN. Do not expose the port to the Internet.

---

## Troubleshooting

| Symptom | Likely cause and fix |
| --- | --- |
| The tablet cannot open the page | Different network or client isolation on the router; Windows Firewall blocking (allow private networks); wrong address (`169.254.x.x`) — check with `ipconfig` and use the one from the tablet's network. |
| Tray icon not visible | Click the ^ *Show hidden icons* arrow in the taskbar and drag the icon out. |
| "Could not open port …" | Another program (or another copy with the same port) uses it. Change `port`. |
| Stream shows other windows over the target | `screen` mode copies the screen. Use `--mode printwindow`, or bring the window to the front. |
| Black picture | `printwindow` with a GPU-rendered window: switch to `screen`. |
| Part of the window is frozen | That part is outside the screen; Windows does not repaint it. Move the window fully on screen, use another monitor or a virtual display. |
| Picture frozen, badge says *Live* | The window is minimized (not captured). Restore it or use *Bring window to front*. |
| `new frames 0 fps` in the tooltip | The picture is not changing — normal with change detection. |
| After switching windows the old picture stays | In `screen` mode the new window is probably behind another one; it is now brought to the front on selection. |
| High CPU | Lower `fps`, use `scale 0.5–0.75`, install libjpeg-turbo, check the tooltip. |
| Latency shows `—` | It needs a couple of seconds after connecting to synchronise clocks. |
| Broadcast does not start after logon | The window is not open yet (the program keeps waiting) or `title` is empty — pick a window from the menu. |
| Window of an "Run as administrator" application is not captured | Run WindowStream elevated as well (Windows blocks messaging to higher-privilege windows; `PrintWindow` may fail). |
| Antivirus flags the `.exe` | Common false positive for PyInstaller builds; sign the file or add an exclusion. |
| Settings are ignored | JSON syntax error (the file is then ignored). Fix it or delete it to regenerate. |
| Interface is in the wrong language | Check `"language"` in the settings file (`"en"` or `"ru"`) and restart the program. |

---

## Known limitations

- One window per program instance; no audio; no input from the viewer; no multi-user access control.
- Only the client area is captured (no title bar).
- Minimized windows are not captured; the last frame remains on the viewer.
- Regions of a window outside the desktop are not updated (Windows/application behaviour).
- `printwindow` does not work correctly with every GPU-rendered application; DRM-protected video is black in both modes.
- Plain HTTP only; no authentication.
- Settings changes made by editing the file take effect after a restart.
- The user interface is available in English and Russian only (`language` setting); the German user manual describes the English interface.

---

## Project layout and code map

```
window_stream.py    the whole application (single file)
requirements.txt    runtime dependencies (CRLF line endings)
build_exe.bat       PyInstaller build script (CRLF line endings)
make_icon.py        generates icon.ico for the executable
tests/              unit tests (standard library only, run on any OS)
README.md           this file
user_manual_ru.md   user manual for the ready-made exe (Russian)
user_manual_en.md   user manual for the ready-made exe (English)
user_manual_de.md   user manual for the ready-made exe (German)
LICENSE             MIT license text
```

Main parts of `window_stream.py`:

| Part | Role |
| --- | --- |
| `I18N`, `T`, `LANG` | Interface strings (`en`/`ru`), lookup function and the current language |
| `list_windows`, `find_window`, `app_windows`, `process_name`, `bring_to_front` | Window discovery, matching and activation |
| `grab_screen`, `grab_printwindow` | The two capture back-ends; both return a raw BGRX buffer plus its size |
| `FrameBuffer` | Latest frame + sequence number + timestamp + client counter, guarded by a condition variable |
| `encode_jpeg` | TurboJPEG (direct or after Pillow resize) or Pillow |
| `capture_loop` | Grab → CRC32 → encode → publish; handles pause, minimized and vanished windows |
| `PAGE`, `page_for` | The embedded web viewer (HTML/CSS/JS with `@@key@@` tokens) and the title/language injection |
| `make_handler` | HTTP routes: `/`, `/status`, `/snapshot.jpg`, `/stream` |
| `Broadcaster` | Start / pause / stop, threads, per-second statistics |
| `SETTINGS`, `load_settings`, `save_settings` | One schema per setting (default, cast, whether it is saved); defaults and key lists are derived from it |
| `autostart_*`, `set_autostart` | Registry-based *Start with Windows* |
| `acquire_single_instance` | Named-mutex guard |
| `TrayIcon` | `pystray.Icon` subclass that rebuilds the menu right before it is shown (pystray builds the Windows menu only once), so the window list and check marks are always current |
| `main` | Argument parsing, precedence rules, tray menu wiring |

The web viewer is a single self-contained HTML document embedded in the script as a raw string; it can be edited in place. `page_for()` replaces the `<title>Map</title>` placeholder and the `@@…@@` tokens, so keep those placeholders intact when editing `PAGE`.

### Tests

```
python -m unittest discover -s tests -v
```

The tests cover the pure logic (interface strings in both languages, the web page, settings, frame buffer, window matching). Windows-only modules are stubbed on other systems, so no extra packages are needed.

---

## License

MIT License — see [LICENSE](LICENSE).
