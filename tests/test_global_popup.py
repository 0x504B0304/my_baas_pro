import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

import numpy as np

from common import image
from modules.baas import home, restart


class FakeLogger:
    def info(self, *_args, **_kwargs):
        pass

    def warning(self, *_args, **_kwargs):
        pass

    def debug(self, *_args, **_kwargs):
        pass


class FakeBaas(SimpleNamespace):
    def __init__(self, popup_text=''):
        ocr = Mock()
        ocr.ocr.return_value = [{'text': popup_text}]
        super().__init__(game_server='cn', logger=FakeLogger(), ocr=ocr)
        self.clicks = []

    def click(self, x, y, wait=True, *_args, **_kwargs):
        self.clicks.append((x, y, wait))


class GlobalPopupTests(unittest.TestCase):
    def setUp(self):
        self.screenshot = np.zeros((720, 1280, 3), dtype=np.uint8)

    def _assert_popup(self, text, expected_click, expected_message):
        fake = FakeBaas(text)
        with patch.object(image, 'compare_image_once', return_value=False), \
             patch.object(image.time, 'sleep', return_value=None):
            with self.assertRaisesRegex(restart.RestartTaskException, expected_message):
                image.handle_global_popup(fake, self.screenshot)
        self.assertEqual(fake.clicks, [expected_click])

    def test_auth_timeout_popup_restarts_current_task(self):
        self._assert_popup(
            '认证信息已超时，将返回标题画面',
            (640, 505, False),
            '登录会话超时',
        )

    def test_network_popup_clicks_reconnect(self):
        self._assert_popup(
            '网络连接不稳定，请再次连接',
            (765, 503, False),
            '网络连接异常',
        )

    def test_update_popup_confirms_download(self):
        self._assert_popup(
            '需要下载919.94KB更新包，是否继续',
            (766, 503, False),
            '游戏资源更新',
        )

    def test_auth_timeout_template_skips_ocr_fallback(self):
        fake = FakeBaas()
        with patch.object(image, 'compare_image_once', return_value=True), \
             patch.object(image.time, 'sleep', return_value=None):
            with self.assertRaisesRegex(restart.RestartTaskException, '登录会话超时'):
                image.handle_global_popup(fake, self.screenshot)
        self.assertEqual(fake.clicks, [(640, 505, False)])
        fake.ocr.ocr.assert_not_called()

    def test_popup_ocr_is_throttled(self):
        fake = FakeBaas('网络连接不稳定，请再次连接')
        fake._last_global_popup_ocr_check = 10.0
        with patch.object(image.time, 'monotonic', return_value=10.5):
            self.assertEqual(image._popup_ocr_text(fake, self.screenshot), '')
        fake.ocr.ocr.assert_not_called()

    def test_popup_ocr_accepts_non_dict_items(self):
        fake = FakeBaas()
        fake.ocr.ocr.return_value = ['网络连接不稳定', {'text': '请再次连接'}]
        with patch.object(image.time, 'monotonic', return_value=10.0):
            self.assertEqual(
                image._popup_ocr_text(fake, self.screenshot),
                '网络连接不稳定请再次连接',
            )

    def test_non_cn_client_skips_popup_ocr(self):
        fake = FakeBaas('网络连接不稳定，请再次连接')
        fake.game_server = 'intl'
        with patch.object(image, 'compare_image_once') as compare_once:
            self.assertFalse(image.handle_global_popup(fake, self.screenshot))
        compare_once.assert_not_called()
        fake.ocr.ocr.assert_not_called()


class MenuRetryTests(unittest.TestCase):
    def test_go_home_does_not_reopen_menu_after_home_is_detected(self):
        fake = SimpleNamespace(
            game_server='cn',
            click=Mock(),
            double_click=Mock(),
            logger=SimpleNamespace(info=Mock()),
        )
        with patch.object(home, 'wake_home_ui'), \
             patch.object(home.image, 'detect', return_value='home_student'):
            self.assertTrue(home.recursion_click_house(fake))
        fake.click.assert_not_called()
        fake.double_click.assert_not_called()

    def test_go_home_passes_story_recovery_to_detector(self):
        fake = SimpleNamespace(
            game_server='cn',
            click=Mock(),
            double_click=Mock(),
            logger=SimpleNamespace(info=Mock()),
        )
        with patch.object(home, 'wake_home_ui'), \
             patch.object(home.image, 'detect', return_value='home_student') as detect:
            self.assertTrue(home.recursion_click_house(fake))
        self.assertIs(detect.call_args.kwargs['pre_func'], home.recover_story_playback)
        self.assertEqual(detect.call_args.kwargs['pre_argv'], (fake,))

    def test_to_menu_does_not_click_screen_before_detecting_current_page(self):
        fake = SimpleNamespace(click=Mock())
        with patch.object(home, 'wake_home_ui') as wake, \
             patch.object(home.image, 'detect', return_value='schedule_menu'):
            self.assertEqual(
                home.to_menu(fake, 'schedule_menu', {}),
                'schedule_menu',
            )
        wake.assert_not_called()
        fake.click.assert_not_called()

    def test_to_menu_raises_when_retry_limit_is_reached(self):
        fake = SimpleNamespace(click=Mock())
        with patch.object(home.image, 'detect', return_value=None) as detect:
            with self.assertRaisesRegex(
                restart.RestartTaskException,
                '进入菜单失败，超过3次图片检索: arena_menu',
            ):
                home.to_menu(fake, 'arena_menu', {}, retry=3)
        self.assertEqual(detect.call_args.kwargs['retry'], 3)


class StoryHomeRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.fake = SimpleNamespace(
            latest_img_array=np.zeros((720, 1280, 3), dtype=np.uint8),
            click=Mock(),
            logger=FakeLogger(),
        )

    def test_clicks_skip_before_menu_when_toolbar_is_open(self):
        def compare(_self, name, *_args, **_kwargs):
            return name in ('momo_talk_skip', 'momo_talk_menu')

        with patch.object(home.image, 'compare_image', side_effect=compare):
            result = home.recover_story_playback(self.fake)

        self.assertEqual(result, ('click', 'story_skip', 'progress'))
        self.fake.click.assert_called_once_with(1212, 116, False)

    def test_opens_story_menu_when_no_choice_is_visible(self):
        def compare(_self, name, *_args, **_kwargs):
            return name == 'momo_talk_menu'

        with patch.object(home.image, 'compare_image', side_effect=compare):
            result = home.recover_story_playback(self.fake)

        self.assertEqual(result, ('click', 'story_menu', 'progress'))
        self.fake.click.assert_called_once_with(1205, 42, False)

    def test_selects_first_of_two_story_choices(self):
        screenshot = self.fake.latest_img_array
        screenshot[240:281, 230:1050] = 255
        screenshot[328:369, 230:1050] = 255

        def compare(_self, name, *_args, **_kwargs):
            return name == 'momo_talk_menu'

        with patch.object(home.image, 'compare_image', side_effect=compare):
            result = home.recover_story_playback(self.fake)

        self.assertEqual(result, ('click', 'story_choice', 'progress'))
        self.fake.click.assert_called_once_with(640, 260, False)

    def test_selects_centered_single_story_choice(self):
        self.fake.latest_img_array[284:325, 230:1050] = 255

        def compare(_self, name, *_args, **_kwargs):
            return name == 'momo_talk_menu'

        with patch.object(home.image, 'compare_image', side_effect=compare):
            result = home.recover_story_playback(self.fake)

        self.assertEqual(result, ('click', 'story_choice', 'progress'))
        self.fake.click.assert_called_once_with(640, 304, False)


if __name__ == '__main__':
    unittest.main()
