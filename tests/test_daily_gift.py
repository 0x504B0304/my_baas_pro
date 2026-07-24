import unittest
from types import SimpleNamespace
from unittest.mock import patch

from modules.reward import daily_gift


class FakeLogger:
    def info(self, *_args, **_kwargs):
        pass


class DailyGiftTests(unittest.TestCase):
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
