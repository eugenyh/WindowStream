"""Frame buffer, window matching and small helpers."""
import sys
import threading
import time
import types
import unittest
from unittest import mock

from support import ws


class FrameBufferTests(unittest.TestCase):
    def test_publish_updates_state(self):
        buf = ws.FrameBuffer()
        buf.publish(b"a", ts=1.5)
        buf.publish(b"b")
        self.assertEqual(2, buf.seq)
        self.assertEqual(b"b", buf.jpeg)

    def test_wait_new_returns_immediately_for_a_new_frame(self):
        buf = ws.FrameBuffer()
        buf.publish(b"a", ts=2.0)
        self.assertEqual((1, b"a", 2.0), buf.wait_new(0, timeout=1))

    def test_wait_new_times_out_when_nothing_changes(self):
        buf = ws.FrameBuffer()
        buf.publish(b"a")
        started = time.time()
        seq, jpeg, _ = buf.wait_new(1, timeout=0.05)
        self.assertEqual((1, b"a"), (seq, jpeg))
        self.assertLess(time.time() - started, 1.0)

    def test_publish_wakes_a_waiting_client(self):
        buf = ws.FrameBuffer()
        result = []
        t = threading.Thread(target=lambda: result.append(buf.wait_new(0, timeout=5)))
        t.start()
        time.sleep(0.05)
        buf.publish(b"x", ts=3.0)
        t.join(2)
        self.assertEqual([(1, b"x", 3.0)], result)

    def test_close_wakes_a_waiting_client(self):
        buf = ws.FrameBuffer()
        t = threading.Thread(target=lambda: buf.wait_new(0, timeout=5))
        t.start()
        time.sleep(0.05)
        buf.close()
        t.join(2)
        self.assertFalse(t.is_alive())
        self.assertTrue(buf.closed)

    def test_client_counter(self):
        buf = ws.FrameBuffer()
        buf.add_client(1)
        buf.add_client(1)
        buf.add_client(-1)
        self.assertEqual(1, buf.clients)


class FindWindowTests(unittest.TestCase):
    WINDOWS = [(1, "Map - Linkage"), (2, "Map"), (3, "Big Map viewer"), (4, "Notes"), (5, "Hidden map")]
    PROCS = {1: "linkage.exe", 2: "other.exe", 3: "linkage.exe", 4: "notes.exe", 5: "linkage.exe"}
    AREAS = {1: 100, 2: 50, 3: 900, 4: 10, 5: 5000}

    def find(self, substr, process=None):
        patches = [
            mock.patch.object(ws, "list_windows", lambda: list(self.WINDOWS)),
            mock.patch.object(ws, "_usable", lambda hwnd: hwnd != 5),  # window 5 is not usable
            mock.patch.object(ws, "process_name", lambda hwnd: self.PROCS[hwnd]),
            mock.patch.object(ws, "_area", lambda hwnd: self.AREAS[hwnd]),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        return ws.find_window(substr, process)

    def test_exact_match_wins_over_prefix_and_substring(self):
        self.assertEqual((2, "Map"), self.find("map"))

    def test_prefix_wins_over_substring(self):
        self.assertEqual((1, "Map - Linkage"), self.find("map -"))

    def test_substring_match(self):
        self.assertEqual((3, "Big Map viewer"), self.find("viewer"))

    def test_no_match(self):
        self.assertIsNone(self.find("nothing"))
        self.assertIsNone(self.find(""))

    def test_unusable_windows_are_skipped(self):
        self.assertIsNone(self.find("hidden"))

    def test_process_filter_restricts_candidates(self):
        self.assertEqual((1, "Map - Linkage"), self.find("map", "linkage.exe"))

    def test_largest_window_of_the_process_when_title_changed(self):
        self.assertEqual((3, "Big Map viewer"), self.find("old title", "linkage.exe"))

    def test_process_without_windows(self):
        self.assertIsNone(self.find("map", "missing.exe"))


class HelperTests(unittest.TestCase):
    def test_menu_text_short_is_unchanged(self):
        self.assertEqual("Map", ws.menu_text("Map"))

    def test_menu_text_is_truncated_with_ellipsis(self):
        text = ws.menu_text("x" * 100, limit=10)
        self.assertEqual("x" * 9 + "…", text)

    def test_menu_text_escapes_ampersand(self):
        self.assertEqual("Tom && Jerry", ws.menu_text("Tom & Jerry"))

    def test_autostart_command_for_frozen_exe(self):
        default = ws.default_config_path()
        with mock.patch.object(sys, "frozen", True, create=True), \
                mock.patch.object(sys, "executable", "C:\\Tools\\WindowStream.exe"):
            self.assertEqual('"C:\\Tools\\WindowStream.exe"', ws.autostart_command(default))
            custom = ws.autostart_command("D:\\ws\\first.json")
        self.assertTrue(custom.endswith('--config "D:\\ws\\first.json"'))

    def test_local_ips_prefers_main_route_and_puts_link_local_last(self):
        fake_sock = mock.MagicMock()
        fake_sock.getsockname.return_value = ("192.168.1.20", 0)
        with mock.patch.object(ws.socket, "socket", return_value=fake_sock), \
                mock.patch.object(ws.socket, "gethostbyname_ex",
                                  return_value=("h", [], ["169.254.3.4", "10.0.0.5", "127.0.0.1", "192.168.1.20"])), \
                mock.patch.object(ws.socket, "gethostname", return_value="h"):
            self.assertEqual(["192.168.1.20", "10.0.0.5", "169.254.3.4"], ws.local_ips())

    @unittest.skipIf(isinstance(ws.Image, mock.Mock), "Pillow is not installed")
    def test_encode_jpeg_with_pillow(self):
        args = types.SimpleNamespace(no_turbo=True, scale=1.0, quality=80)
        data = bytes([10, 20, 30, 0]) * 8  # 4x2 pixels, BGRX
        jpeg = ws.encode_jpeg(data, (4, 2), args)
        self.assertTrue(jpeg.startswith(b"\xff\xd8"))
        args.scale = 0.5
        self.assertTrue(ws.encode_jpeg(data, (4, 2), args).startswith(b"\xff\xd8"))


if __name__ == "__main__":
    unittest.main()
