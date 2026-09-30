"""Settings file: defaults, type coercion, validation, round trip."""
import contextlib
import io
import json
import os
import tempfile
import unittest

from support import ws

EXPECTED_DEFAULTS = {
    "title": "",
    "process": "",
    "port": 8080,
    "fps": 10.0,
    "quality": 75,
    "scale": 1.0,
    "mode": "screen",
    "no_diff": False,
    "no_turbo": False,
    "autostart_broadcast": True,
    "language": "en",
}


class SettingsTests(unittest.TestCase):
    def setUp(self):
        self._lang = ws.LANG
        ws.LANG = "en"
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = os.path.join(self.tmp.name, "sub", "settings.json")

    def tearDown(self):
        ws.LANG = self._lang

    def write(self, data):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(data if isinstance(data, str) else json.dumps(data))

    def load(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            settings = ws.load_settings(self.path)
        return settings, out.getvalue()

    def test_defaults_are_unchanged(self):
        self.assertEqual(EXPECTED_DEFAULTS, ws.DEFAULT_SETTINGS)

    def test_schema_derived_sets(self):
        self.assertEqual(set(EXPECTED_DEFAULTS), set(ws.SETTINGS))
        self.assertEqual(
            ("title", "process", "port", "fps", "quality", "scale", "mode", "no_diff", "no_turbo"),
            ws.SAVED_SETTINGS)
        self.assertEqual(("title", "port", "fps", "quality", "scale", "mode"), ws.CLI_VALUE_SETTINGS)

    def test_every_saved_or_cli_setting_is_a_command_line_option(self):
        import inspect
        src = inspect.getsource(ws.main)
        for key in ws.CLI_VALUE_SETTINGS:
            self.assertIn("--" + key.replace("_", "-"), src, key)

    def test_missing_file_gives_defaults_and_a_copy(self):
        settings, out = self.load()
        self.assertEqual(EXPECTED_DEFAULTS, settings)
        self.assertEqual("", out)
        settings["port"] = 1
        self.assertEqual(8080, ws.DEFAULT_SETTINGS["port"])

    def test_broken_json_gives_defaults_and_a_message(self):
        self.write("{not json")
        settings, out = self.load()
        self.assertEqual(EXPECTED_DEFAULTS, settings)
        self.assertIn(self.path, out)

    def test_values_are_coerced_to_their_types(self):
        self.write({"port": "9090", "fps": "12.5", "quality": "80", "scale": "0.5",
                    "no_diff": "yes", "no_turbo": "0", "autostart_broadcast": "off", "title": "Map"})
        s, _ = self.load()
        self.assertEqual((9090, 12.5, 80, 0.5), (s["port"], s["fps"], s["quality"], s["scale"]))
        self.assertIs(True, s["no_diff"])
        self.assertIs(False, s["no_turbo"])
        self.assertIs(False, s["autostart_broadcast"])
        self.assertEqual("Map", s["title"])

    def test_invalid_value_is_skipped_with_a_message(self):
        self.write({"port": "abc", "quality": 60})
        s, out = self.load()
        self.assertEqual(8080, s["port"])
        self.assertEqual(60, s["quality"])
        self.assertIn("port", out)

    def test_unknown_keys_are_ignored(self):
        self.write({"nonsense": 1})
        s, _ = self.load()
        self.assertEqual(EXPECTED_DEFAULTS, s)

    def test_invalid_mode_falls_back_to_screen(self):
        self.write({"mode": "magic"})
        self.assertEqual("screen", self.load()[0]["mode"])
        self.write({"mode": "printwindow"})
        self.assertEqual("printwindow", self.load()[0]["mode"])

    def test_language_is_normalised_and_validated(self):
        for raw, expected in ((" RU ", "ru"), ("en", "en"), ("de", "en"), ("", "en")):
            self.write({"language": raw})
            self.assertEqual(expected, self.load()[0]["language"], raw)

    def test_save_and_load_round_trip(self):
        settings = dict(ws.DEFAULT_SETTINGS, title="Карта — Linkage", port=9000, no_diff=True)
        self.assertTrue(ws.save_settings(self.path, settings))
        with open(self.path, encoding="utf-8") as f:
            self.assertIn("Карта", f.read())  # written as UTF-8, not \u escapes
        self.assertEqual(settings, self.load()[0])

    def test_save_failure_returns_false(self):
        blocker = os.path.join(self.tmp.name, "file")
        with open(blocker, "w") as f:
            f.write("x")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertFalse(ws.save_settings(os.path.join(blocker, "settings.json"), {}))
        self.assertIn("settings.json", out.getvalue())

    def test_to_bool(self):
        for value in (True, "1", "true", "TRUE", " yes ", "on", "да"):
            self.assertIs(True, ws._to_bool(value), value)
        for value in (False, "0", "false", "no", "off", "", "нет"):
            self.assertIs(False, ws._to_bool(value), value)


if __name__ == "__main__":
    unittest.main()
