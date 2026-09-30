# WindowStream — User Manual

This manual describes how to use the **ready-made executable `WindowStream.exe`**. You do not need to install Python or any libraries.

> **Interface language.** The program uses an English interface by default. To switch to Russian, open the settings file (menu item **Open settings file**), set `"language": "ru"` and restart the program. This manual names menu items and messages as they appear in the English interface.

## Contents

1. [What the program does](#1-what-the-program-does)
2. [Requirements](#2-requirements)
3. [Installation and first launch](#3-installation-and-first-launch)
4. [Quick start: five steps](#4-quick-start-five-steps)
5. [The notification-area icon](#5-the-notification-area-icon)
6. [The icon menu](#6-the-icon-menu)
7. [Choosing the window to broadcast](#7-choosing-the-window-to-broadcast)
8. [Viewing on the tablet](#8-viewing-on-the-tablet)
9. [The settings file](#9-the-settings-file)
10. [Capture modes: screen and printwindow](#10-capture-modes-screen-and-printwindow)
11. [Running with parameters](#11-running-with-parameters)
12. [Start with Windows](#12-start-with-windows)
13. [Pause, stop and exit](#13-pause-stop-and-exit)
14. [Several broadcasts at once](#14-several-broadcasts-at-once)
15. [Updating and uninstalling](#15-updating-and-uninstalling)
16. [Security](#16-security)
17. [Program messages](#17-program-messages)
18. [Troubleshooting](#18-troubleshooting)
19. [Limitations](#19-limitations)
20. [Frequently asked questions](#20-frequently-asked-questions)

---

## 1. What the program does

WindowStream shows **one window** from your computer on the screen of another device (a tablet, a phone, another computer) in an ordinary web browser. The picture is updated in real time. You cannot control the window from the tablet: it is view-only.

In a nutshell: the program on the PC captures the contents of the selected window and serves it over the local network as a video stream. On the tablet you open the computer's address in a browser, for example `http://192.168.1.20:8080/`, and see the window.

The program runs in the background and is controlled through an icon in the notification area (next to the clock).

## 2. Requirements

**On the computer:**

- Windows 10 or 11, 64-bit.
- The file `WindowStream.exe`. Nothing needs to be installed.

**On the tablet or other device:**

- A modern browser (Chrome, Edge, Firefox and similar).
- A connection to the **same network** as the computer (usually the same Wi-Fi network).

**On the network:**

- The router must not forbid devices from talking to each other (on routers this feature is often called "client isolation" or "AP isolation").

## 3. Installation and first launch

### Installation

1. Create a permanent folder, for example `C:\Tools\WindowStream\`, and copy `WindowStream.exe` into it.
2. Do not run the program from the *Downloads* folder or from temporary folders, especially if you plan to enable autostart: if the file is later moved or deleted, autostart will stop working.

There is no separate installer: the program does not write files to `Program Files` and does not need administrator rights.

### First launch

1. Double-click `WindowStream.exe`.
2. **SmartScreen warning.** The file is not digitally signed, so Windows may show a blue "Windows protected your PC" window. Click **More info → Run anyway**. Antivirus software may also react to such a file; if that happens, add the program to the exclusions.
3. **Firewall prompt.** Windows will ask whether to allow the program to access the network. Tick **Private networks** and click **Allow access**. Without this the tablet cannot connect. There is no need to allow public networks.
4. A gray icon appears in the notification area (the program does not open a window). If you cannot see the icon, click the **^ "Show hidden icons"** arrow on the taskbar. To keep the icon always visible, drag it from that list onto the taskbar.

On first launch the program creates a settings file (see [section 9](#9-the-settings-file)).

## 4. Quick start: five steps

1. **Start** `WindowStream.exe` and find the icon in the notification area.
2. **Open the window you want to show** (it must be restored, not minimized to the taskbar).
3. **Right-click** the icon → item **Window: not selected** → choose the window in the list. The broadcast starts immediately and the icon turns green.
4. **Find out the address:** hover over the icon — the tooltip shows the address, for example `http://192.168.1.20:8080/`.
5. **Enter this address in the tablet's browser.** You will see the window from the computer.

The next time the program starts, it remembers the window and starts broadcasting by itself: you do not need to select it again.

## 5. The notification-area icon

### Icon colors

| Icon | State |
| --- | --- |
| Gray circle with a square | Broadcast stopped |
| Green circle with a triangle | Broadcast running |
| Yellow circle with two bars | Paused |

### Tooltip

When you hover over the icon during a broadcast, it shows, for example:

```
Window broadcast: live
Capture 10 fps · new frames 3 fps · clients 1
http://192.168.1.20:8080/
```

- **Capture** — how many times per second the program grabs the window.
- **new frames** — how many changed frames per second are sent. If the picture in the window does not change, this will be `0`. That is normal: the program does not send identical frames, which saves CPU and network.
- **clients** — how many browsers are watching the broadcast right now.
- The last line is the address for the tablet.

The numbers are refreshed once per second. If **Capture** is noticeably lower than the configured frame rate (10 by default), the computer cannot keep up: reduce the frame rate, scale or quality (see [section 9](#9-the-settings-file)).

## 6. The icon menu

The menu opens with a **right click** on the icon.

| Item | What it does |
| --- | --- |
| **Start broadcast** | Starts broadcasting the selected window. Available when the broadcast is stopped. |
| **Pause / Resume** | Pauses and resumes the broadcast. The tablet keeps the last frame with a "Paused" label. The item's name changes depending on the state. |
| **Stop broadcast** | Stops the broadcast completely and closes the connections. The tablet shows "No connection". |
| **Window: …** | Opens the list of windows available for broadcasting. The current window is marked. Your choice is saved and immediately starts broadcasting that window. |
| **Bring window to front** | Restores the window (if it is minimized) and brings it on top of the others. |
| **Start with Windows** | Turns autostart on and off (a check mark shows that it is on). |
| **Open settings file** | Opens the settings file in Notepad. |
| **Exit** | Stops the broadcast and closes the program. |

Items that are not available at the moment are grayed out.

## 7. Choosing the window to broadcast

### How to choose

Right-click the icon → **Window: …** → pick a window from the list.

What happens when you choose:

1. the window is remembered (its title and the name of the program it belongs to);
2. if the window was minimized, it is restored and then brought to the front;
3. the broadcast restarts on the new window and a notification with the address appears.

The list shows ordinary application windows (up to 40, alphabetically). It does not show: command-prompt and terminal windows, the desktop, tool and hidden windows, and very small windows. If the window you need is not in the list, make sure it is open and not minimized, then open the menu again: the list is built every time the menu opens.

### How the program finds the window later

The program remembers the window's **title** and the **program file name** (for example `myapp.exe`). When looking for the window it applies these rules in order:

1. the title matches exactly;
2. the title starts with the saved text;
3. the title contains the saved text;
4. if nothing matched but the program name is known — the **largest visible window of that program** is taken.

Thanks to the fourth rule the broadcast is not lost when the window title changes. For example, the title of many programs contains the name of the open file, and when you open another file the title changes.

To always broadcast the window even if the title changes, you can put only a part of the title in the settings (for example, the program name without the file name): see the `title` parameter in [section 9](#9-the-settings-file).

### The window is closed or not open yet

- If you close the window during a broadcast, the program searches for it again and continues showing it when it reappears.
- If the window is not open when the program starts (for example, right after you log in to Windows), the program shows the notification "Window "…" not found. Waiting for the window to appear..." and checks every 5 seconds until it appears.

## 8. Viewing on the tablet

### How to open

1. Make sure the tablet is connected to the same network as the computer.
2. In the tablet's browser, enter the address from the icon tooltip, for example `http://192.168.1.20:8080/`. The address starts with `http://` (not `https://`).
3. It is handy to bookmark the page.

### How to find the address if the tooltip shows the wrong one

The tooltip shows the most suitable address, but the computer may have several network connections. To see all addresses:

1. press `Win + R`, type `cmd` and press Enter;
2. run the command `ipconfig`;
3. find the **IPv4 address** of the connection through which the computer is linked to the tablet (usually starting with `192.168.` or `10.`).

Addresses starting with **`169.254.`** are link-local: Windows assigned them itself because it did not get an address from the router. They only work if the tablet also has an address from this range. With such an address you should normally check the network connection.

The port (`8080`) can be changed in the settings.

### What you see on the page

The window picture is fitted into a neat frame with rounded corners that fills the whole browser window, keeping the proportions. The browser tab title matches the title of the broadcast window and is updated along with it.

**Mode indicator in the top right corner:**

| Indicator | Meaning |
| --- | --- |
| Green blinking dot, **Live** | The broadcast is running. Next to it `N fps · M ms` is shown: how many new frames per second the tablet receives and the approximate delay. |
| Yellow dot, **Paused** | The broadcast is paused on the computer. The picture is frozen and dimmed. |
| Red dot, **No connection** | The computer is unreachable or the broadcast is stopped. The picture is gray with a spinner over it. The page reconnects by itself; you do not need to refresh it. |

The color of the thin glow along the edge of the frame also matches the mode (green, yellow, red).

**Auto-hide.** During a normal broadcast the indicator and buttons disappear after 4 seconds so they do not cover the picture. Tap the screen to show them again. During a pause and when the connection is lost they stay on screen permanently.

### Gesture controls

| Action | Result |
| --- | --- |
| Tap | Show the indicator and buttons |
| Two fingers (pinch and spread) | Zoom up to ×8 |
| One finger while zoomed in | Move the picture |
| Double tap | Zoom in 2.5 times at that point; another double tap returns to the original view |
| Tap the `×2.4 · reset` label (bottom right) | Reset the zoom |
| Long press (about 0.7 s) | Hide or show the `fps · ms` line. The choice is remembered in the browser |
| Button in the top left corner | Full-screen mode |
| Mouse wheel (on a computer) | Zoom |

The zoom label at the bottom right appears while the picture is zoomed in and stays visible.

> Tip: when zoomed in, the picture is as sharp as it is transmitted from the computer. For sharp zooming keep `scale` at `1.0` (the default).

### Several devices

Several devices can be connected to one broadcast at the same time: the number of connections is shown in the icon tooltip ("clients").

## 9. The settings file

### Where it is

```
%APPDATA%\WindowStream\settings.json
```

Usually this is `C:\Users\<user name>\AppData\Roaming\WindowStream\settings.json`.

The easiest way to open it is from the icon menu: **Open settings file** (it opens in Notepad). The file is created automatically on first launch.

> **Changes take effect after the program is restarted.** Close it with **Exit** and start it again.

The window you choose in the menu is saved to the file automatically (parameters `title` and `process`).

### Example

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

Keep to the JSON format: strings in double quotes, commas between parameters, no comma after the last parameter, and `true` and `false` in lowercase without quotes. If the file is damaged, the program ignores it and uses the default values. In that case fix the file or delete it: it will be created again at the next start.

### Parameters

| Parameter | Default | Description |
| --- | --- | --- |
| `title` | empty | Window title or a part of it (case-insensitive). |
| `process` | empty | File name of the program that owns the window (for example `mapapp.exe`). Helps to find the window when the title changes. Filled in automatically when you choose a window from the menu. |
| `port` | `8080` | The port on which the broadcast is available. Change it if the port is used by another program. |
| `fps` | `10` | Maximum frames per second (not less than 0.5). The higher, the smoother and the higher the load. |
| `quality` | `75` | JPEG quality from 1 to 95. Higher is sharper but heavier for the network. |
| `scale` | `1.0` | Scale of the transmitted frame (not less than 0.1). `0.5` is half the size along each side. |
| `mode` | `"screen"` | Capture mode: `"screen"` or `"printwindow"` ([section 10](#10-capture-modes-screen-and-printwindow)). |
| `no_diff` | `false` | `true` — disable change detection and send every frame (increases the load, usually not needed). |
| `no_turbo` | `false` | `true` — do not use the fast JPEG encoder (only needed for comparison). |
| `autostart_broadcast` | `true` | `false` — do not start broadcasting right after the program starts, but wait for the **Start broadcast** command in the menu. |
| `language` | `"en"` | Interface language: `"en"` — English (default), `"ru"` — Russian. Affects the tray menu, notifications, console messages, `--help` and the tablet page. Restart the program after changing it. |

### Recommended values

| Situation | Settings |
| --- | --- |
| Ordinary map viewing | defaults (`fps` 10, `quality` 75, `scale` 1.0) |
| Weak Wi-Fi or a weak tablet | `fps` 10–15, `quality` 60–70, `scale` 0.75 |
| Maximum sharpness, lots of zooming | `scale` 1.0, `quality` 80–90, `fps` 10 |
| Smooth motion | `fps` 20–30 (higher load on the computer) |
| Lower load on the computer | `fps` 5–10, `scale` 0.5–0.75 |

If the picture in the window does not change, the program hardly loads the computer or the network — this is done by frame change detection, which is on by default.

## 10. Capture modes: screen and printwindow

The `mode` parameter determines how the program obtains the window picture.

| | `screen` (default) | `printwindow` |
| --- | --- | --- |
| Principle | Copies the window's rectangle from the screen | Asks the window itself to draw its contents |
| Other windows on top of the needed one | **Appear in the broadcast** | Do not appear |
| Window covered by other windows | You see what is on top | Broadcast normally |
| GPU-rendered programs (3D maps, video, games) | Works | Some programs give a black or outdated picture |
| Minimized window | Not broadcast | Not broadcast |

**How to choose:**

1. First try `"printwindow"`. If the picture is correct, keep this mode: other windows will no longer get into the broadcast.
2. If the picture is black or does not update, go back to `"screen"`. In this mode keep the window in the foreground and make sure nothing covers it. When you choose a window from the menu, the program brings it to the front by itself, and the **Bring window to front** item does this at any time.

What is always broadcast is the **client area of the window** (without the title bar and borders), at its real size in pixels.

## 11. Running with parameters

Normally you do not need command-line parameters: everything is stored in the settings file. But if you wish, you can start the program with switches.

### How to run from the command line

Open a command prompt in the program's folder and type, for example:

```
WindowStream.exe --title "Untitled - Map" --mode printwindow --save
```

### A shortcut with parameters

1. Right-click `WindowStream.exe` → **Send to → Desktop (create shortcut)**.
2. Right-click the shortcut → **Properties**.
3. In the **Target** field, after the path to the file, add the parameters separated by a space, for example:
   `"C:\Tools\WindowStream\WindowStream.exe" --port 9000`

### List of switches

| Switch | Description |
| --- | --- |
| `--title "text"` | Window title or a part of it. |
| `--list` | Show the list of open windows (handle, program, title) and exit. |
| `--port N` | Port (default 8080). |
| `--fps N` | Maximum frames per second (default 10). |
| `--quality N` | JPEG quality 1–95 (default 75). |
| `--scale X` | Frame scale, for example `0.5` (default 1.0). |
| `--mode screen` / `--mode printwindow` | Capture mode. |
| `--no-diff` | Disable frame change detection. |
| `--no-turbo` | Do not use the fast JPEG encoder. |
| `--no-autostart` | Do not start broadcasting at launch; wait for a menu command. This switch has nothing to do with Windows autostart. |
| `--config "path"` | Use another settings file. |
| `--save` | Save this run's parameters to the settings file. |
| `--help` | Help on the switches. |

**Priorities.** Command-line switches take precedence over the settings file, but they do not get into the file by themselves unless you specify `--save`. Toggle switches (`--no-diff`, `--no-turbo`) can only be turned on; to turn such a parameter off, edit the settings file.

### List of windows

The built program has no console window of its own, so `--list` and `--help` print their text to **the command prompt from which they are run**:

```
WindowStream.exe --list
```

If you run this command by double-clicking, there is nowhere to show the text.

## 12. Start with Windows

### How to turn it on

Right-click the icon → **Start with Windows**. A check mark appears next to the item. Selecting the item again turns autostart off.

Autostart is enabled only for your user account and does not need administrator rights.

### What happens when you log in to Windows

1. The program starts in the background and the icon appears in the notification area.
2. If a window is set in the settings and `autostart_broadcast` is `true`, the program starts broadcasting.
3. If the window does not exist yet (for example, the needed program is also starting), the program waits for it, checks every 5 seconds and then starts broadcasting by itself.

If no window is selected in the settings, the program only shows a hint to choose a window in the icon menu.

### If the file was moved

If you moved `WindowStream.exe` to another folder and started it from there, the program updates the path in autostart by itself. If you deleted the file without turning autostart off, Windows will not find the program at logon; to remove the entry, run the program again from any folder and turn autostart off in the menu.

## 13. Pause, stop and exit

| Action | What happens | What the tablet sees |
| --- | --- | --- |
| **Pause** | Capturing the window is suspended, the program keeps running | The last frame, the "Paused" label |
| **Resume** | Capturing resumes | Live picture |
| **Stop broadcast** | Capturing and serving stop, the port is released, the icon is gray | "No connection"; the page reconnects by itself when you start the broadcast again |
| **Exit** | The program closes completely | "No connection" |

If the window is minimized, the picture on the tablet stays on the last frame until the window is restored. The program keeps running meanwhile.

## 14. Several broadcasts at once

By default only **one copy** of the program can run: on a second launch the message "The program is already running" appears with a hint to find the icon near the clock, and the second copy closes. The port is not affected.

To broadcast several windows at the same time, start copies with **different settings files and different ports**:

```
WindowStream.exe --config "D:\ws\first.json" --port 8080 --title "Window 1" --save
WindowStream.exe --config "D:\ws\second.json" --port 8081 --title "Window 2" --save
```

On the tablet open different addresses: `http://192.168.1.20:8080/` and `http://192.168.1.20:8081/`. Both ports must be allowed in the firewall, and autostart will work for the copy from which you turned it on.

## 15. Updating and uninstalling

### Updating

1. Close the program: right-click the icon → **Exit**.
2. Replace `WindowStream.exe` with the new version in the same folder.
3. Start it. Your settings are kept, because they are stored separately from the program.

If autostart was on, it keeps working (the path stays the same).

### Complete removal

1. Turn autostart off: right-click the icon → clear the check mark at **Start with Windows**.
2. Close the program with **Exit**.
3. Delete `WindowStream.exe`.
4. If you wish, delete the settings folder `%APPDATA%\WindowStream\` (type this path into the File Explorer address bar).

## 16. Security

- The broadcast is **not password-protected and not encrypted**. Anyone connected to your network who knows the address can see the window contents.
- Use the program only in trusted networks (a home or work network with only your own devices connected). Do not use it in public networks (cafés, hotels).
- In the firewall allow access for **private networks** only.
- Do not broadcast windows with confidential data if there are outsiders on the network.
- For access from another network use a VPN. Do not open the program's port to the internet.
- The tablet cannot control the computer through this program: it is view-only.

## 17. Program messages

The built program does not show a console, so messages appear as Windows notifications near the clock.

| Message | Meaning and what to do |
| --- | --- |
| **Broadcast started. Open on the tablet: …** | All is well, open the given address on the tablet. |
| **Window "…" not found. Waiting for the window to appear...** | The needed window is not open. Open it: the broadcast starts by itself. Or choose another window in the menu. |
| **No window selected: choose one in the tray menu ("Window" item)** / **Choose a window in the tray menu: "Window" item** | There is no window in the settings. Choose a window in the icon menu. |
| **Could not open port 8080: …** | The port is used by another program or another copy. Change `port` in the settings file. |
| **Streaming: …** | The broadcast has switched to the selected window. |
| **The program will start with Windows** / **Autostart disabled** | The result of toggling autostart. |
| **Could not change autostart: …** | The registry entry is not accessible (for example, forbidden by an organization policy). Contact your administrator. |
| **Could not open the settings file: …** | Notepad did not start. Open the file manually (see [section 9](#9-the-settings-file)). |
| The **The program is already running** window | A copy of the program is already running. Find its icon near the clock, possibly among the hidden icons. |

## 18. Troubleshooting

| Problem | Possible cause and solution |
| --- | --- |
| The tablet does not open the page | 1) The tablet and the computer are on different networks — connect them to the same one. 2) The firewall blocks access — allow the program for private networks (Start → "Allow an app through Windows Firewall"). 3) Wrong address — check it with `ipconfig` (see [section 8](#8-viewing-on-the-tablet)). 4) The router has client isolation turned on — turn it off. 5) The address starts with `169.254.` — check the network connection. |
| The icon is not visible | Click the **^** arrow ("Show hidden icons") on the taskbar and drag the icon onto the bar. |
| The program does not start, nothing happens | It may already be running: the icon may be among the hidden ones. Try starting it again: if the message "The program is already running" appears, it is running. |
| SmartScreen or antivirus blocks the file | The file is not signed. Click "More info → Run anyway" or add the file to the antivirus exclusions. |
| Other windows are visible on top of the needed one | The `screen` mode copies the image from the screen. Set `"mode": "printwindow"` in the settings or keep the needed window in the foreground. |
| The picture is black | The window is drawn through the GPU and does not give its contents to the `printwindow` mode. Set `"mode": "screen"`. |
| Part of the window does not update | That part is beyond the screen edge: Windows and the program do not redraw it. Move the window so that it fits completely on the screen, or use a second monitor. |
| The picture is frozen but the indicator says "Live" | The window is minimized. Restore it or choose **Bring window to front**. |
| The tooltip says "new frames 0 fps" | The picture in the window does not change. This is normal. |
| After switching windows the tablet kept the old picture | In `screen` mode the new window may end up behind other windows. When you choose a window from the menu it is now brought to the front automatically; if not, use the **Bring window to front** item. |
| High CPU load | Reduce `fps`, set `scale` to 0.5–0.75, reduce `quality`. |
| The picture jerks or lags | Weak Wi-Fi or a weak tablet: reduce `scale` and `quality`; if possible connect to a 5 GHz network. Watch the delay in ms on the tablet and the capture rate in the icon tooltip. |
| The delay on the tablet shows "—" | This is normal in the first seconds after connecting. |
| The broadcast does not start after logging in to Windows | The needed window is not open yet (the program is waiting for it) or no window is selected in the settings — choose it in the icon menu. |
| The window of a program run as administrator is not broadcast | Run WindowStream as administrator too (right-click the file → "Run as administrator"): Windows does not let ordinary programs handle windows with elevated rights. |
| Settings have no effect | Changes take effect after the program is restarted. Also check the file format (commas, quotes): with an error the file is ignored. |
| The settings file needs to be reset | Close the program, delete `%APPDATA%\WindowStream\settings.json` and start again. |

## 19. Limitations

- One window is broadcast per copy of the program.
- No sound.
- No control from the tablet: view-only.
- Only the client area of the window is shown (without the title bar and borders).
- A minimized window is not broadcast: the tablet keeps the last frame.
- A part of the window beyond the screen edge does not update.
- In `printwindow` mode some GPU-rendered programs give a black picture; copy-protected video is not shown in either mode.
- No password and no encryption (plain `http://` only).
- The program's interface is available in English and Russian (`language` setting).

## 20. Frequently asked questions

**Do I need the internet?**
No. A local network between the computer and the tablet is enough. The program does not use the internet.

**Can I watch from a phone or another computer?**
Yes. Any device with a modern browser on the same network will do.

**How many devices can watch at the same time?**
Several. The number of connections is visible in the icon tooltip.

**Does the program close the window or interfere with working in it?**
No. It only captures the window's contents. You can work in it on the computer as usual. The only thing it does to the window is bring it to the front when you choose it from the menu or use the **Bring window to front** item.

**What happens if I close the window that is being broadcast?**
The program keeps running and finds the window again when it reappears. Until then the tablet shows the last frame.

**What happens if the window title changes?**
The program finds the window by the program name (the largest window of that program). The tab title on the tablet is updated.

**How do I change the port?**
Change `port` in the settings file and restart the program. On the tablet use the new address, for example `http://192.168.1.20:9000/`.

**Why is the address in the tooltip different from what I expected?**
The computer may have several network adapters (Wi-Fi, Ethernet, virtual ones). Use `ipconfig` to pick the address of the connection through which the computer is linked to the tablet.

**Where can I see the settings and what can be changed in them?**
The menu item **Open settings file** and [section 9](#9-the-settings-file).

**How do I stop the program completely?**
Right-click the icon → **Exit**. There is no need to close a window: the program has no window, only an icon.
