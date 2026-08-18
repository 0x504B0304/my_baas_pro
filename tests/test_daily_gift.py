import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from modules.reward import daily_gift


class FakeLogger:
    def info(self, *_args, **_kwargs):
        pass


class DailyGiftTests(unittest.TestCase):
    def test_gift_page_checks_unavailable_state_first_with_current_threshold(self):
        fake = SimpleNamespace(game_server='cn', click=Mock(), logger=FakeLogger())
        with patch.object(daily_gift.home, 'go_home'), \
             patch.object(
                 daily_gift.image,
                 'detect',
                 side_effect=['daily_gift_shop-title', 'daily_gift_free-unavailable'],
             ) as detect:
            self.assertTrue(daily_gift.to_daily_gift(fake))
        self.assertEqual(
            detect.call_args_list[1].args[1],
            (
                ('daily_gift_free-unavailable', 0.8),
                ('daily_gift_free-available', 0.9),
            ),
        )
        self.assertEqual(detect.call_args_list[1].kwargs['retry'], 5)

    def test_unavailable_status_wins_over_similar_available_template(self):
        fake = SimpleNamespace(game_server="cn", logger=FakeLogger())

        def compare_image(_self, name, *_args, **_kwargs):
            return name == "daily_gift_free-unavailable"

        with patch.object(daily_gift.image, "compare_image", side_effect=compare_image):
            self.assertFalse(daily_gift.is_free_gift_available(fake))

    def test_available_status_is_detected_after_unavailable_misses(self):
        fake = SimpleNamespace(game_server="cn", logger=FakeLogger())

        def compare_image(_self, name, *_args, **_kwargs):
            return name == "daily_gift_free-available"

        with patch.object(daily_gift.image, "compare_image", side_effect=compare_image):
            self.assertTrue(daily_gift.is_free_gift_available(fake))


if __name__ == "__main__":
    unittest.main()
