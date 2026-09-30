"""The embedded web page: placeholder substitution, title escaping, language."""
import re
import unittest

from support import ws


class PageTests(unittest.TestCase):
    def setUp(self):
        self._lang = ws.LANG

    def tearDown(self):
        ws.LANG = self._lang

    def render(self, title=None, lang="en"):
        ws.LANG = lang
        page = ws.page_for(title)
        self.assertIsInstance(page, bytes)
        return page.decode("utf-8")

    def test_no_placeholders_left(self):
        for lang in ws.I18N:
            self.assertIsNone(re.search(r"@@\w+@@", self.render("T", lang)), lang)

    def test_title_placeholder_kept_without_window_title(self):
        self.assertIn("<title>Map</title>", self.render(None))

    def test_title_is_replaced_and_escaped(self):
        page = self.render("A <b> & \"c\"")
        self.assertIn("<title>A &lt;b&gt; &amp; &quot;c&quot;</title>", page)
        self.assertNotIn("<title>Map</title>", page)

    def test_only_first_title_placeholder_is_replaced(self):
        self.assertEqual(1, self.render("X").count("<title>X</title>"))

    def test_language_attribute_and_strings(self):
        en = self.render("X", "en")
        ru = self.render("X", "ru")
        self.assertIn('<html lang="en">', en)
        self.assertIn('<html lang="ru">', ru)
        self.assertIn(ws.I18N["en"]["web_running"], en)
        self.assertIn(ws.I18N["ru"]["web_running"], ru)
        self.assertNotIn(ws.I18N["ru"]["web_running"], en)


if __name__ == "__main__":
    unittest.main()
