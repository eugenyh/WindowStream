"""Interface strings: the two languages must stay in sync and every used key must exist."""
import ast
import re
import string
import unittest

from support import SOURCE_PATH, ws


def placeholders(text):
    return {field for _, field, _, _ in string.Formatter().parse(text) if field}


def static_keys_used_in_source():
    """Keys passed as a literal to T("...") anywhere in window_stream.py."""
    with open(SOURCE_PATH, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    keys = set()
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "T"
                and node.args and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)):
            keys.add(node.args[0].value)
    return keys


def page_tokens():
    return set(re.findall(r"@@(\w+)@@", ws.PAGE.decode("utf-8"))) - {"lang"}


class I18NTests(unittest.TestCase):
    def setUp(self):
        self._lang = ws.LANG

    def tearDown(self):
        ws.LANG = self._lang

    def test_languages_have_identical_keys(self):
        en, ru = set(ws.I18N["en"]), set(ws.I18N["ru"])
        self.assertEqual(set(), en - ru, "keys missing in ru")
        self.assertEqual(set(), ru - en, "keys missing in en")

    def test_placeholders_match_between_languages(self):
        for key, text in ws.I18N["en"].items():
            self.assertEqual(placeholders(text), placeholders(ws.I18N["ru"][key]), key)

    def test_no_empty_strings(self):
        for lang, table in ws.I18N.items():
            for key, text in table.items():
                self.assertTrue(text.strip(), f"{lang}.{key} is empty")

    def test_keys_used_in_code_exist(self):
        used = static_keys_used_in_source() | set(ws.STATE_KEY.values())
        self.assertEqual(set(), used - set(ws.I18N["en"]))

    def test_page_tokens_have_web_strings(self):
        for token in page_tokens():
            self.assertIn("web_" + token, ws.I18N["en"], token)

    def test_no_unused_keys(self):
        used = static_keys_used_in_source() | set(ws.STATE_KEY.values())
        used |= {"web_" + t for t in page_tokens()}
        self.assertEqual(set(), set(ws.I18N["en"]) - used)

    def test_web_strings_are_safe_inside_js_and_html(self):
        # page_for() html-escapes these and also puts them into JS string literals,
        # so characters that html.escape rewrites (or that break a JS string) are not allowed
        for lang, table in ws.I18N.items():
            for key, text in table.items():
                if key.startswith("web_"):
                    for bad in "&<>\"'\\\n":
                        self.assertNotIn(bad, text, f"{lang}.{key}")

    def test_T_formats_arguments(self):
        ws.LANG = "en"
        self.assertEqual("Window \"X\" not found", ws.T("window_not_found", title="X"))
        ws.LANG = "ru"
        self.assertEqual("Окно «X» не найдено", ws.T("window_not_found", title="X"))

    def test_T_unknown_language_falls_back_to_english(self):
        ws.LANG = "xx"
        self.assertEqual(ws.I18N["en"]["menu_exit"], ws.T("menu_exit"))

    def test_T_unknown_key_raises(self):
        with self.assertRaises(KeyError):
            ws.T("no_such_key")


if __name__ == "__main__":
    unittest.main()
