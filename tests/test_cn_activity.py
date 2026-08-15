import unittest
from types import SimpleNamespace
from unittest.mock import Mock, call, patch

from modules.activity import cn_activity
from modules.baas import restart


class FakeLogger:
    def info(self, *_args, **_kwargs):
        pass

    def warning(self, *_args, **_kwargs):
        pass


class ActivityPageTests(unittest.TestCase):
    def test_activity_page_accepts_multiple_markers_and_forwards_retry(self):
        fake = SimpleNamespace()
        with patch.object(cn_activity.image, 'detect', return_value='cm_activity-notice') as detect:
            result = cn_activity.to_activity_page(fake, retry=7)
        self.assertEqual(result, 'cm_activity-notice')
        self.assertEqual(detect.call_args.args[1], cn_activity.ACTIVITY_PAGE_MARKERS)
        self.assertEqual(detect.call_args.kwargs['retry'], 7)

    def test_activity_page_timeout_restarts_current_task(self):
        fake = SimpleNamespace()
        with patch.object(cn_activity.image, 'detect', return_value=None):
            with self.assertRaisesRegex(
                restart.RestartTaskException,
                '进入国服活动页面失败，超过5次图片检索',
            ):
                cn_activity.to_activity_page(fake, retry=5)


class ActivityTabTests(unittest.TestCase):
    @patch.object(cn_activity.time, 'sleep', return_value=None)
    def test_tab_falls_back_to_legacy_layout(self, _sleep):
        fake = SimpleNamespace(click=Mock())
        with patch.object(cn_activity.image, 'compare_image', return_value=False), \
             patch.object(
                 cn_activity.color,
                 'check_rgb',
                 side_effect=[False] * 8 + [True],
             ) as check_rgb:
            cn_activity.to_tab(fake, 'task')
        self.assertEqual(fake.click.call_count, 8)
        self.assertEqual(fake.click.call_args_list[0], call(935, 110, False))
        self.assertEqual(check_rgb.call_args_list[-1].args[1], (1060, 104))

    @patch.object(cn_activity.time, 'sleep', return_value=None)
    def test_tab_timeout_restarts_current_task(self, _sleep):
        fake = SimpleNamespace(click=Mock())
        with patch.object(cn_activity.image, 'compare_image', return_value=False), \
             patch.object(cn_activity.color, 'check_rgb', return_value=False):
            with self.assertRaisesRegex(
                restart.RestartTaskException,
                '活动页签切换失败: story',
            ):
                cn_activity.to_tab(fake, 'story')
        self.assertEqual(fake.click.call_count, 16)


class ActivityExpansionTests(unittest.TestCase):
    def test_calc_need_stage_stops_after_supported_stages(self):
        fake = SimpleNamespace(logger=FakeLogger(), click=Mock())
        with patch.object(cn_activity, 'wait_task_info', return_value=True), \
             patch.object(cn_activity, 'check_task_state', return_value='sss'):
            self.assertEqual(cn_activity.calc_need_fight_stage(fake, 'story'), (None, 0))
        self.assertEqual(fake.click.call_count, 15)

    def test_wait_task_info_uses_current_cn_entry_position(self):
        fake = SimpleNamespace()
        with patch.object(cn_activity.image, 'detect', return_value='cn_activity_info-window') as detect:
            self.assertEqual(cn_activity.wait_task_info(fake), 'cn_activity_info-window')
        self.assertEqual(detect.call_args.kwargs['cl'], (1130, 190))
        self.assertIn('cn_activity_info-window', detect.call_args.args[1])

    @patch.object(cn_activity.time, 'sleep', return_value=None)
    def test_story_first_reward_marks_unfinished_stage(self, _sleep):
        fake = SimpleNamespace()
        with patch.object(cn_activity, 'wait_task_info', return_value=True), \
             patch.object(cn_activity.image, 'compare_image', return_value=True) as compare_image:
            self.assertEqual(cn_activity.check_task_state(fake, 'story'), 'no-sss')
        compare_image.assert_called_once_with(fake, 'cn_activity_first-reward', 0, 0.8)

    @patch.object(cn_activity.time, 'sleep', return_value=None)
    def test_story_without_first_reward_marks_completed_stage(self, _sleep):
        fake = SimpleNamespace()
        with patch.object(cn_activity, 'wait_task_info', return_value=True), \
             patch.object(cn_activity.image, 'compare_image', return_value=False) as compare_image:
            self.assertEqual(cn_activity.check_task_state(fake, 'story'), 'sss')
        compare_image.assert_called_once_with(fake, 'cn_activity_first-reward', 0, 0.8)

    @patch.object(cn_activity.time, 'sleep', return_value=None)
    def test_task_detail_uses_three_star_marker(self, _sleep):
        fake = SimpleNamespace()
        with patch.object(cn_activity, 'wait_task_info', return_value=True), \
             patch.object(cn_activity.image, 'compare_image', return_value=False) as compare_image:
            self.assertEqual(cn_activity.check_task_state(fake, 'task'), 'no-sss')
        compare_image.assert_called_once_with(fake, 'normal_task_sss', 0, 0.9)

    @patch.object(cn_activity.time, 'sleep', return_value=None)
    def test_missing_detail_window_marks_end_of_stage_list(self, _sleep):
        fake = SimpleNamespace()
        with patch.object(cn_activity, 'wait_task_info', return_value=False), \
             patch.object(cn_activity.image, 'compare_image') as compare_image:
            self.assertIsNone(cn_activity.check_task_state(fake, 'task'))
        compare_image.assert_not_called()

    def test_do_exp_stops_without_starting_fight_when_complete(self):
        fake = SimpleNamespace(logger=FakeLogger())
        with patch.object(cn_activity, 'to_tab'), \
             patch.object(cn_activity, 'to_activity_page'), \
             patch.object(cn_activity.stage, 'screen_swipe'), \
             patch.object(cn_activity, 'calc_need_fight_stage', return_value=(None, 0)), \
             patch.object(cn_activity, 'start_fight') as start_fight:
            cn_activity.do_exp(fake, 'task')
        start_fight.assert_not_called()

    def test_skip_story_timeout_restarts_current_task(self):
        fake = SimpleNamespace()
        with patch.object(cn_activity.image, 'detect', return_value=None) as detect:
            with self.assertRaisesRegex(
                restart.RestartTaskException,
                '活动剧情跳过流程识别超时',
            ):
                cn_activity.skip_story(fake)
        self.assertEqual(detect.call_args.kwargs['retry'], 300)

    def test_start_fight_timeout_restarts_current_task(self):
        fake = SimpleNamespace()
        with patch.object(cn_activity.image, 'detect', return_value=None) as detect:
            with self.assertRaisesRegex(
                restart.RestartTaskException,
                '活动关卡启动流程识别超时',
            ):
                cn_activity.start_fight(fake, 'exp', 0, 1, 'task')
        self.assertEqual(detect.call_args.kwargs['retry'], 300)

    def test_activity_stage_position_for_reference_scan(self):
        self.assertEqual(cn_activity.activity_stage_position(12), (1130, 640))


if __name__ == '__main__':
    unittest.main()
