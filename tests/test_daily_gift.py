import unittest
from types import SimpleNamespace
from unittest.mock import Mock, call, patch

from modules.reward import daily_gift


class FakeLogger:
    def info(self, *_args, **_kwargs):
        pass


class DailyGiftTests(unittest.TestCase):
    def test_gift_page_distinguishes_both_states_at_exact_threshold(self):
        fake = SimpleNamespace(game_server='cn', click=Mock(), logger=FakeLogger())
        with patch.object(daily_gift.home, 'go_home'), \
             patch.object(daily_gift.image, 'get_box', return_value=(770, 154, 1031, 206)), \
             patch.object(
                 daily_gift.image,
                 'detect',
                 side_effect=['daily_gift_shop-title', 'daily_gift_free-unavailable'],
             ) as detect:
            self.assertTrue(daily_gift.to_daily_gift(fake))
        self.assertEqual(
            detect.call_args_list[1].args[1],
            (
                ('daily_gift_free-available', 0.9),
                ('daily_gift_free-unavailable', 0.9),
            ),
        )
        self.assertEqual(detect.call_args_list[1].kwargs['retry'], 5)
        self.assertEqual(
            fake.click.call_args_list,
            [call(979, 37, False), call(900, 180, False)],
        )

    def test_available_status_is_checked_before_unavailable(self):
        fake = SimpleNamespace(game_server="cn", logger=FakeLogger())
        with patch.object(daily_gift.image, "compare_image", return_value=True) as compare:
            self.assertTrue(daily_gift.is_free_gift_available(fake))
        compare.assert_called_once_with(fake, 'daily_gift_free-available', 0, 0.9)

    def test_unavailable_status_is_detected_after_available_misses(self):
        fake = SimpleNamespace(game_server="cn", logger=FakeLogger())

        def compare_image(_self, name, *_args, **_kwargs):
            return name == "daily_gift_free-unavailable"

        with patch.object(daily_gift.image, "compare_image", side_effect=compare_image):
            self.assertFalse(daily_gift.is_free_gift_available(fake))

    def test_purchase_clicks_use_configured_box_centers(self):
        fake = SimpleNamespace(click=Mock(), logger=FakeLogger())
        boxes = {
            'daily_gift_free-button': (291, 484, 474, 522),
            'daily_gift_confirm-button': (724, 559, 791, 589),
        }

        with patch.object(daily_gift, 'is_free_gift_available', return_value=True), \
             patch.object(daily_gift.image, 'detect', return_value=True), \
             patch.object(daily_gift.image, 'compare_image', return_value=True), \
             patch.object(daily_gift.image, 'get_box', side_effect=lambda _self, name: boxes[name]), \
             patch.object(daily_gift.stage, 'close_prize_info') as close_prize_info:
            daily_gift.buy_free_gift(fake)

        self.assertEqual(
            fake.click.call_args_list,
            [call(382, 503, False), call(757, 574, False)],
        )
        close_prize_info.assert_called_once_with(fake, True)


if __name__ == "__main__":
    unittest.main()
