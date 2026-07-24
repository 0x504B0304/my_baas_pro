import unittest
from types import SimpleNamespace
from unittest.mock import patch

from modules.daily import cafe


class FakeBaas(SimpleNamespace):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.clicks = []

    def click(self, x, y, wait=True, count=1, rate=0):
        self.clicks.append((x, y, wait, count, rate))


class CafeInviteTests(unittest.TestCase):
    def test_confirm_popup_is_handled_before_invitation_list(self):
        fake = FakeBaas(game_server="cn", ocr=object())
        menu_checks = 0

        def compare_image(_self, name, *_args, **_kwargs):
            nonlocal menu_checks
            if name == "cafe_menu":
                menu_checks += 1
                return menu_checks > 1
            if name == "cafe_inv-confirm":
                return True
            if name == "cafe_invitation-ticket":
                raise AssertionError("invitation list should not be checked after confirm matched")
            return False

        with patch.object(cafe.image, "compare_image", side_effect=compare_image), \
             patch.object(cafe.time, "sleep", return_value=None):
            cafe.do_invite_girl(fake)

        self.assertEqual(fake.clicks, [(706, 497, False, 1, 0)])

    def test_invitation_list_click_does_not_run_ocr_fallback(self):
        fake = FakeBaas(game_server="cn", ocr=object())
        menu_checks = 0

        def compare_image(_self, name, *_args, **_kwargs):
            nonlocal menu_checks
            if name == "cafe_menu":
                menu_checks += 1
                return menu_checks > 1
            return name == "cafe_invitation-ticket"

        with patch.object(cafe.image, "compare_image", side_effect=compare_image), \
             patch.object(cafe.ocr, "screenshot_check_text") as check_text, \
             patch.object(cafe.time, "sleep", return_value=None):
            cafe.do_invite_girl(fake)

        check_text.assert_not_called()
        self.assertEqual(fake.clicks, [(790, 220, False, 1, 0)])

    def test_cn_ocr_fallback_confirms_unknown_popup(self):
        fake = FakeBaas(game_server="cn", ocr=object())
        menu_checks = 0

        def compare_image(_self, name, *_args, **_kwargs):
            nonlocal menu_checks
            if name == "cafe_menu":
                menu_checks += 1
                return menu_checks > 1
            return False

        def check_text(_self, text, *_args, **_kwargs):
            return text in {"通知", "确认"}

        with patch.object(cafe.image, "compare_image", side_effect=compare_image), \
             patch.object(cafe.ocr, "screenshot_check_text", side_effect=check_text), \
             patch.object(cafe.time, "sleep", return_value=None):
            cafe.do_invite_girl(fake)

        self.assertEqual(fake.clicks, [(706, 497, False, 1, 0)])


if __name__ == "__main__":
    unittest.main()
