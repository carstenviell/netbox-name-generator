from django.test import TestCase


class TranslationTests(TestCase):
    def test_compiled_catalog_is_current(self):
        """django.mo is shipped (target systems usually lack gettext) - it must contain every translated msgid."""
        import gettext
        import os
        import re
        base = os.path.join(os.path.dirname(__file__), "locale", "de", "LC_MESSAGES")
        po = open(os.path.join(base, "django.po"), encoding="utf-8").read()
        with open(os.path.join(base, "django.mo"), "rb") as f:
            catalog = gettext.GNUTranslations(f)._catalog
        missing = [m for m in re.findall(r"^msgid \"(.+)\"\nmsgstr \"(?!\")", po, re.M)
                   if m.replace(chr(92) + chr(34), chr(34)) not in catalog]
        self.assertEqual(missing, [], "django.mo is outdated - run makemessages/msgfmt (see CLAUDE.md)")
        self.assertNotIn("fuzzy", po, "fuzzy entries are guessed translations - fix them")
