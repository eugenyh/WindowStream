"""Loads window_stream for the tests.

window_stream imports Windows-only modules (pywin32, winreg, ...). On any other OS they are replaced
by stubs so the pure logic can still be tested; on Windows the real modules are used.
"""
import ctypes
import os
import sys
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _install_stubs():
    ctypes.windll = mock.MagicMock()
    ctypes.WinDLL = mock.MagicMock()
    for name in ("winreg", "mss", "pystray", "win32con", "win32gui", "win32process", "win32ui"):
        sys.modules.setdefault(name, mock.MagicMock())
    try:
        import PIL.Image  # noqa: F401
        import PIL.ImageDraw  # noqa: F401
    except ImportError:
        for name in ("PIL", "PIL.Image", "PIL.ImageDraw"):
            sys.modules.setdefault(name, mock.MagicMock())


if sys.platform != "win32":
    _install_stubs()

sys.path.insert(0, ROOT)
import window_stream as ws  # noqa: E402

SOURCE_PATH = os.path.join(ROOT, "window_stream.py")
