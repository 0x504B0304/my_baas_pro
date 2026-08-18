import json
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, call, patch

import numpy as np

from modules.activity import activity_story, cn_activity, god_cross
from modules.baas import restart


class FakeLogger:
    def info(self, *_args, **_kwargs):
        pass

    def warning(self, *_args, **_kwargs):
        pass


class ActivityPageTests(unittest.TestCase):
    def test_activity_page_accepts_multiple_markers_and_forwards_retry(self):
        fake = SimpleNamespace()
        with patch.object(cn_activity.image, 'detect', return_value='cm_activity-notice') as detect, \
             patch.object(cn_activity.home, 'wake_home_ui') as wake, \
             patch.object(cn_activity, 'is_target_activity_page', return_value=True):
            result = cn_activity.to_activity_page(fake, retry=7)
        self.assertEqual(result, 'cm_activity-notice')
        wake.assert_not_called()
        self.assertEqual(detect.call_args.args[1], cn_activity.ACTIVITY_PAGE_MARKERS)
        self.assertEqual(detect.call_args.kwargs['retry'], 7)

    @patch.object(cn_activity.time, 'sleep', return_value=None)
    def test_activity_page_retries_when_wrong_activity_is_open(self, _sleep):
        fake = SimpleNamespace(click=Mock(), logger=FakeLogger())
        with patch.object(cn_activity.image, 'detect', return_value='cm_activity-notice') as detect, \
             patch.object(cn_activity.home, 'wake_home_ui'), \
             patch.object(cn_activity, 'is_target_activity_page', side_effect=[False, True]):
            result = cn_activity.to_activity_page(fake, retry=9)
        self.assertEqual(result, 'cm_activity-notice')
        fake.click.assert_called_once_with(1233, 25)
        self.assertEqual(detect.call_count, 2)

    @patch.object(cn_activity.time, 'sleep', return_value=None)
    def test_activity_page_backs_out_of_remembered_activity_subpage(self, _sleep):
        fake = SimpleNamespace(click=Mock(), logger=FakeLogger())
        with patch.object(cn_activity.image, 'detect', return_value='cm_activity-menu') as detect, \
             patch.object(cn_activity.home, 'wake_home_ui'), \
             patch.object(cn_activity, 'is_target_activity_page', side_effect=[False, True]) as is_target:
            result = cn_activity.to_activity_page(fake, retry=9)
        self.assertEqual(result, 'cm_activity-menu')
        fake.click.assert_called_once_with(55, 35, False)
        self.assertEqual(detect.call_count, 2)
        self.assertEqual(
            is_target.call_args_list,
            [call(fake, retry=1), call(fake, retry=1)],
        )

    def test_activity_page_cycles_right_home_carousel_without_event_title_template(self):
        fake = SimpleNamespace()
        with patch.object(cn_activity.image, 'detect', return_value='cm_activity-menu') as detect, \
             patch.object(cn_activity.home, 'wake_home_ui'), \
             patch.object(cn_activity, 'is_target_activity_page', return_value=True):
            cn_activity.to_activity_page(fake, retry=7)
        home_action = detect.call_args.args[2]['home_student']
        self.assertIs(home_action[0], cn_activity.open_next_home_activity_candidate)
        self.assertEqual(home_action[1], (fake,))
        self.assertEqual(
            detect.call_args.args[2]['home_quick-home'],
            (1233, 25),
        )
        self.assertNotIn('cn_activity_event-logo', detect.call_args.args[2])
        self.assertNotIn('cn_activity_home-entry', detect.call_args.args[2])

    def test_home_activity_carousel_index_uses_generic_page_dots(self):
        screenshot = np.zeros((720, 1280, 3), dtype=np.uint8)
        x, y = (1204, 267)
        screenshot[y - 2:y + 3, x - 2:x + 3] = (250, 200, 40)
        self.assertEqual(cn_activity._home_activity_carousel_index(screenshot), 1204)

    @patch.object(cn_activity.time, 'sleep', return_value=None)
    def test_home_activity_candidate_clicks_right_carousel_and_tracks_seen(self, _sleep):
        fake = SimpleNamespace(click=Mock(), logger=FakeLogger())
        with patch.object(
            cn_activity,
            '_wait_home_activity_candidate',
            side_effect=[1194, 1204],
        ) as wait_candidate:
            self.assertFalse(cn_activity.open_next_home_activity_candidate(fake))
            self.assertFalse(cn_activity.open_next_home_activity_candidate(fake))
        self.assertEqual(
            wait_candidate.call_args_list,
            [call(fake, set()), call(fake, {1194})],
        )
        self.assertEqual(fake._activity_home_carousel_seen, {1194, 1204})
        self.assertEqual(
            fake.click.call_args_list,
            [call(1185, 215, False), call(1185, 215, False)],
        )

    @patch.object(cn_activity.time, 'sleep', return_value=None)
    @patch.object(cn_activity.time, 'monotonic', side_effect=[0, 0, 0, 0])
    def test_home_activity_candidate_waits_for_stable_untried_page(self, _monotonic, _sleep):
        screenshot = np.full((720, 1280, 3), 120, dtype=np.uint8)
        x, y = (1194, 267)
        screenshot[y - 2:y + 3, x - 2:x + 3] = (250, 200, 40)
        fake = SimpleNamespace(get_screenshot_array=Mock(return_value=screenshot))
        self.assertEqual(
            cn_activity._wait_home_activity_candidate(fake, {1184}, timeout=1),
            1194,
        )
        self.assertEqual(fake.get_screenshot_array.call_count, 2)

    def test_activity_page_timeout_restarts_current_task(self):
        fake = SimpleNamespace()
        with patch.object(cn_activity.image, 'detect', return_value=None), \
             patch.object(cn_activity.home, 'wake_home_ui'):
            with self.assertRaisesRegex(
                restart.RestartTaskException,
                '进入国服活动页面失败，超过5次图片检索',
            ):
                cn_activity.to_activity_page(fake, retry=5)


class ActivityTabTests(unittest.TestCase):
    def test_cn_activity_start_schedules_challenge_flow(self):
        fake = SimpleNamespace(game_server='cn')
        with patch.object(cn_activity.home, 'go_home'), \
             patch.object(cn_activity, 'to_activity_page'), \
             patch.object(cn_activity, 'start_exp'), \
             patch.object(cn_activity, 'challenge_task') as challenge, \
             patch.object(cn_activity, 'start_bonus'), \
             patch.object(cn_activity, 'start_scan', return_value=None), \
             patch.object(cn_activity, 'start_dice'), \
             patch.object(cn_activity, 'start_exchange'), \
             patch.object(cn_activity, 'start_draw_card'), \
             patch.object(cn_activity, 'finish_task'):
            cn_activity.start(fake)
        challenge.assert_called_once_with(fake)

    def test_cn_activity_config_template_exposes_disabled_challenge_task(self):
        path = Path(__file__).resolve().parents[1] / 'web' / 'static' / 'baas.json'
        config = json.loads(path.read_text(encoding='utf-8'))
        self.assertEqual(
            config['cn_activity']['challenge-task'],
            {'enable': False},
        )

    def test_finish_task_disables_one_time_challenge_flow(self):
        fake = SimpleNamespace(tc={
            'story_exp': {'enable': True},
            'task_exp': {'enable': True},
            'bonus': {'enable': True},
            'challenge-task': {'enable': True},
        })
        cn_activity.finish_task(fake)
        self.assertFalse(fake.tc['challenge-task']['enable'])

    def test_selected_tab_requires_blue_background_not_gray_overlay(self):
        screenshot = np.zeros((720, 1280, 3), dtype=np.uint8)
        screenshot[104, 900] = (78, 78, 78)
        fake = SimpleNamespace(
            get_screenshot_array=Mock(return_value=screenshot),
            logger=FakeLogger(),
        )
        self.assertFalse(cn_activity._activity_tab_selected(fake, 'task'))

        screenshot[104, 900] = (85, 60, 46)
        self.assertTrue(cn_activity._activity_tab_selected(fake, 'task'))

    @patch.object(cn_activity.time, 'sleep', return_value=None)
    def test_story_task_and_challenge_click_ocr_positions_in_right_top_area(self, _sleep):
        positions = {
            'story': (762, 109),
            'task': (944, 109),
            'challenge': (1126, 109),
        }
        for tab, click_pos in positions.items():
            with self.subTest(tab=tab):
                fake = SimpleNamespace(click=Mock())
                with patch.object(
                    cn_activity,
                    '_activity_tab_selected',
                    side_effect=[False, True],
                ), patch.object(
                    cn_activity,
                    '_activity_tab_positions_by_ocr',
                    return_value=positions,
                ):
                    cn_activity.to_tab(fake, tab)
                fake.click.assert_called_once_with(*click_pos, False)

    @patch.object(cn_activity.time, 'sleep', return_value=None)
    def test_tab_falls_back_to_right_top_coordinates_when_ocr_misses(self, _sleep):
        fake = SimpleNamespace(click=Mock())
        with patch.object(cn_activity, '_activity_tab_selected', side_effect=[False, True]), \
             patch.object(cn_activity, '_activity_tab_positions_by_ocr', return_value={}):
            cn_activity.to_tab(fake, 'story')
        fake.click.assert_called_once_with(760, 110, False)

    def test_activity_tab_ocr_position_is_relative_to_right_top_crop(self):
        fake = SimpleNamespace(ocr=object())
        output = [{
            'text': '任务',
            'position': [[250, 15], [310, 15], [310, 55], [250, 55]],
        }]
        with patch.object(cn_activity.ocr, 'screenshot_cut_get_text', return_value=output) as get_text:
            positions = cn_activity._activity_tab_positions_by_ocr(fake)
        self.assertEqual(positions['task'], (950, 110))
        get_text.assert_called_once_with(
            fake, cn_activity.ACTIVITY_STAGE_TAB_AREA, 0, False,
        )

    @patch.object(cn_activity.time, 'sleep', return_value=None)
    def test_tab_timeout_restarts_current_task(self, _sleep):
        fake = SimpleNamespace(click=Mock())
        with patch.object(cn_activity, '_activity_tab_selected', return_value=False), \
             patch.object(cn_activity, '_activity_tab_positions_by_ocr', return_value={}):
            with self.assertRaisesRegex(
                restart.RestartTaskException,
                '活动页签切换失败: story',
            ):
                cn_activity.to_tab(fake, 'story')
        self.assertEqual(fake.click.call_count, 1)

    def test_challenge_task_switches_to_right_top_challenge_tab(self):
        fake = SimpleNamespace(
            tc={'challenge-task': {'enable': True}},
            log_title=Mock(),
        )
        with patch.object(cn_activity, 'to_activity_page') as to_activity, \
             patch.object(cn_activity, 'to_tab') as to_tab, \
             patch.object(cn_activity.image, 'detect'), \
             patch.object(cn_activity, 'start_fight'):
            cn_activity.challenge_task(fake)
        self.assertEqual(to_activity.call_count, 2)
        self.assertEqual(
            to_tab.call_args_list,
            [call(fake, 'challenge'), call(fake, 'challenge')],
        )

    def test_scan_switches_to_right_top_task_tab(self):
        fake = SimpleNamespace(
            tc={'scan': {'enable': True, 'stage': []}},
            log_title=Mock(),
        )
        with patch.object(cn_activity, 'to_activity_page'), \
             patch.object(cn_activity, 'to_tab') as to_tab:
            cn_activity.start_scan(fake)
        to_tab.assert_called_once_with(fake, 'task')

    def test_bonus_switches_to_right_top_task_tab(self):
        fake = SimpleNamespace(
            tc={'bonus': {'enable': True}},
            log_title=Mock(),
        )
        with patch.object(cn_activity, 'to_activity_page'), \
             patch.object(cn_activity, 'to_tab') as to_tab:
            cn_activity.start_bonus(fake)
        to_tab.assert_called_once_with(fake, 'task')

    def test_activity_archive_story_switches_to_right_top_story_tab(self):
        fake = SimpleNamespace(
            game_server='cn',
            logger=SimpleNamespace(critical=Mock()),
            click=Mock(),
        )
        with patch.object(activity_story.time, 'sleep', return_value=None), \
             patch.object(cn_activity, 'to_activity_page'), \
             patch.object(cn_activity, 'to_tab') as to_tab, \
             patch.object(cn_activity, 'calc_need_fight_stage', return_value=(None, 0)), \
             patch.object(activity_story.stage, 'screen_swipe'):
            self.assertFalse(activity_story.do_exp(fake))
        to_tab.assert_called_once_with(fake, 'story')

    def test_bottom_activity_feature_uses_ocr_label_position(self):
        fake = SimpleNamespace(ocr=object())
        output = [
            {
                'text': '商店',
                'position': [[220, 55], [280, 55], [280, 95], [220, 95]],
            },
            {
                'text': '抽卡',
                'position': [[460, 55], [520, 55], [520, 95], [460, 95]],
            },
        ]
        with patch.object(cn_activity.ocr, 'screenshot_cut_get_text', return_value=output):
            position, ocr_available = cn_activity._activity_bottom_entry_by_ocr(
                fake, ('抽卡', '卡片商店'),
            )
        self.assertEqual(position, (520, 665))
        self.assertTrue(ocr_available)

    def test_missing_bottom_activity_label_does_not_use_wrong_fixed_entry(self):
        fake = SimpleNamespace(ocr=object(), click=Mock(), logger=FakeLogger())
        with patch.object(cn_activity.image, 'compare_image', return_value=False), \
             patch.object(
                 cn_activity,
                 '_activity_bottom_entry_by_ocr',
                 return_value=(None, True),
             ):
            self.assertFalse(
                cn_activity._enter_activity_feature_page(
                    fake, 'cm_dice-menu', ('骰子', '赛跑'), (515, 635),
                ),
            )
        fake.click.assert_not_called()

    def test_activity_feature_page_uses_bounded_marker_wait(self):
        fake = SimpleNamespace(click=Mock(), logger=FakeLogger())
        with patch.object(
            cn_activity.image,
            'compare_image',
            side_effect=[False, True],
        ) as compare_image, patch.object(
            cn_activity,
            '_activity_bottom_entry_by_ocr',
            return_value=((519, 670), True),
        ):
            self.assertTrue(
                cn_activity._enter_activity_feature_page(
                    fake,
                    'brzx_draw-menu',
                    ('抽卡', '卡片商店'),
                    (520, 640),
                ),
            )
        fake.click.assert_called_once_with(519, 670, False)
        self.assertEqual(compare_image.call_args_list[-1].kwargs['retry'], 5)


class ActivityExpansionTests(unittest.TestCase):
    @patch.object(cn_activity.time, 'monotonic', return_value=10.0)
    def test_activity_fight_prompt_confirms_current_defeat_screen(self, _time):
        engine = SimpleNamespace(ocr=Mock(return_value=[
            {'text': '战败'},
            {'text': '战斗时间 01:44'},
            {'text': '确认'},
        ]))
        fake = SimpleNamespace(
            ocr=engine,
            latest_img_array=np.zeros((720, 1280, 3), dtype=np.uint8),
            click=Mock(),
            logger=FakeLogger(),
        )
        self.assertEqual(
            cn_activity.handle_activity_fight_prompt(fake),
            ('click', 'progress'),
        )
        fake.click.assert_called_once_with(640, 655, False)

    @patch.object(cn_activity.time, 'monotonic', return_value=10.0)
    def test_activity_fight_prompt_confirms_terrain_explanation(self, _time):
        screenshot = np.zeros((720, 1280, 3), dtype=np.uint8)
        engine = SimpleNamespace(ocr=Mock(return_value=[
            {'text': '提示！'},
            {'text': '街区战'},
            {'text': '野外战'},
            {'text': '室内战'},
            {'text': '返回大厅'},
            {'text': '确认'},
        ]))
        fake = SimpleNamespace(
            ocr=engine,
            latest_img_array=screenshot,
            click=Mock(),
            logger=FakeLogger(),
        )
        self.assertEqual(
            cn_activity.handle_activity_fight_prompt(fake),
            ('click', 'progress'),
        )
        engine.ocr.assert_called_once()
        np.testing.assert_array_equal(
            engine.ocr.call_args.args[0],
            screenshot[70:710, 250:1030],
        )
        fake.click.assert_called_once_with(775, 660, False)

    @patch.object(cn_activity.time, 'monotonic', return_value=10.0)
    def test_activity_fight_prompt_confirms_generic_battle_tip(self, _time):
        engine = SimpleNamespace(ocr=Mock(return_value=[
            {'text': '提示！'},
            {'text': '特定的攻击属性可以对敌人造成更多伤害。'},
            {'text': '返回大厅'},
            {'text': '确认'},
        ]))
        fake = SimpleNamespace(
            ocr=engine,
            latest_img_array=np.zeros((720, 1280, 3), dtype=np.uint8),
            click=Mock(),
            logger=FakeLogger(),
        )
        self.assertEqual(
            cn_activity.handle_activity_fight_prompt(fake),
            ('click', 'progress'),
        )
        fake.click.assert_called_once_with(775, 660, False)

    @patch.object(cn_activity.time, 'monotonic', return_value=10.0)
    def test_activity_fight_prompt_ignores_unrelated_confirm_dialog(self, _time):
        engine = SimpleNamespace(ocr=Mock(return_value=[
            {'text': '通知'},
            {'text': '确认'},
        ]))
        fake = SimpleNamespace(
            ocr=engine,
            latest_img_array=np.zeros((720, 1280, 3), dtype=np.uint8),
            click=Mock(),
            logger=FakeLogger(),
        )
        self.assertIsNone(cn_activity.handle_activity_fight_prompt(fake))
        fake.click.assert_not_called()

    def test_wait_fight_over_uses_terrain_prompt_handler(self):
        fake = SimpleNamespace()
        with patch.object(
            cn_activity.image,
            'detect',
            return_value='cm_activity-menu',
        ) as detect:
            cn_activity.wait_fight_over(fake)
        self.assertIs(
            detect.call_args.kwargs['pre_func'],
            cn_activity.handle_activity_fight_prompt,
        )
        self.assertEqual(detect.call_args.kwargs['pre_argv'], (fake,))

    def test_enter_activity_stage_page_returns_when_already_on_stage_page(self):
        fake = SimpleNamespace()
        with patch.object(cn_activity, 'is_activity_stage_page', return_value=True), \
             patch.object(cn_activity.image, 'compare_image') as compare_image, \
             patch.object(cn_activity.image, 'detect') as detect:
            cn_activity.enter_activity_stage_page(fake)
        compare_image.assert_not_called()
        detect.assert_not_called()

    def test_activity_stage_page_accepts_selected_story_tab_template(self):
        fake = SimpleNamespace()
        with patch.object(cn_activity.image, 'compare_image', return_value=True) as compare_image:
            self.assertTrue(cn_activity.is_activity_stage_page(fake))
        compare_image.assert_called_once_with(
            fake, 'cn_activity_stage-story-tab', retry=0, threshold=0.75,
        )

    def test_target_activity_page_uses_regular_structure_not_event_logo(self):
        fake = SimpleNamespace()
        with patch.object(cn_activity, 'is_activity_stage_page', return_value=True) as is_stage, \
             patch.object(cn_activity, 'is_activity_ended', return_value=False) as is_ended, \
             patch.object(cn_activity.image, 'compare_image') as compare_image:
            self.assertTrue(cn_activity.is_target_activity_page(fake))
        is_stage.assert_called_once_with(fake)
        is_ended.assert_called_once_with(fake)
        compare_image.assert_not_called()

    @patch.object(cn_activity.time, 'sleep', return_value=None)
    def test_target_activity_page_waits_for_tabs_to_finish_fading_in(self, _sleep):
        fake = SimpleNamespace()
        with patch.object(
            cn_activity,
            'is_activity_stage_page',
            side_effect=[False, False, True],
        ), patch.object(cn_activity, 'is_activity_ended', return_value=False):
            self.assertTrue(cn_activity.is_target_activity_page(fake, retry=4))

    def test_ended_activity_is_not_target_even_with_right_top_tabs(self):
        fake = SimpleNamespace()
        with patch.object(cn_activity, 'is_activity_stage_page', return_value=True), \
             patch.object(cn_activity, 'is_activity_ended', return_value=True):
            self.assertFalse(cn_activity.is_target_activity_page(fake))

    def test_ended_activity_uses_generic_content_ocr(self):
        fake = SimpleNamespace(ocr=object())
        with patch.object(cn_activity.ocr, 'screenshot_check_text', return_value=True) as check_text:
            self.assertTrue(cn_activity.is_activity_ended(fake))
        check_text.assert_called_once_with(
            fake,
            '活动时间已结束',
            cn_activity.ACTIVITY_STAGE_CONTENT_AREA,
            0,
            0,
            False,
        )

    def test_stage_tabs_accept_single_selected_right_top_tab(self):
        fake = SimpleNamespace(ocr=None)
        with patch.object(cn_activity.image, 'compare_image', return_value=False), \
             patch.object(cn_activity, '_activity_tab_selected', side_effect=[False, True, False]):
            self.assertTrue(cn_activity.has_activity_stage_tabs(fake))

    def test_stage_page_recognizes_generic_right_top_tabs_by_ocr(self):
        fake = SimpleNamespace(ocr=object())
        with patch.object(cn_activity.image, 'compare_image', return_value=False), \
             patch.object(
                 cn_activity,
                 '_activity_tab_positions_by_ocr',
                 return_value={
                     'story': (760, 110),
                     'task': (935, 110),
                     'challenge': (1125, 110),
                 },
             ), patch.object(cn_activity, '_activity_tab_selected') as selected:
            self.assertTrue(cn_activity.has_activity_stage_tabs(fake))
        selected.assert_not_called()

    def test_stage_tabs_reject_page_without_right_top_structure(self):
        fake = SimpleNamespace(ocr=None)
        with patch.object(cn_activity.image, 'compare_image', return_value=False), \
             patch.object(cn_activity, '_activity_tab_selected', return_value=False):
            self.assertFalse(cn_activity.has_activity_stage_tabs(fake))

    def test_enter_activity_stage_page_rejects_missing_right_top_tabs(self):
        fake = SimpleNamespace()
        with patch.object(cn_activity, 'is_activity_stage_page', return_value=False):
            with self.assertRaisesRegex(
                restart.RestartTaskException,
                '活动右上关卡页签识别失败',
            ):
                cn_activity.enter_activity_stage_page(fake)

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

    def test_task_expansion_opens_first_task_after_list_reset(self):
        fake = SimpleNamespace(logger=FakeLogger(), click=Mock())
        with patch.object(cn_activity, 'wait_task_info', return_value=True) as wait_info, \
             patch.object(cn_activity, 'check_task_state', return_value=None):
            self.assertEqual(cn_activity.calc_need_fight_stage(fake, 'task'), (None, 0))
        wait_info.assert_called_once_with(
            fake,
            click_pos=cn_activity.ACTIVITY_FIRST_STAGE_POS['task'],
        )

    @patch.object(cn_activity.time, 'sleep', return_value=None)
    def test_task_list_reset_pulls_first_card_below_fixed_tabs(self, _sleep):
        fake = SimpleNamespace(swipe=Mock())
        with patch.object(cn_activity.stage, 'screen_swipe') as screen_swipe:
            cn_activity.reset_activity_stage_list(fake, 'task')
        screen_swipe.assert_called_once_with(
            fake,
            0,
            False,
            threshold2=False,
            reset=False,
            f=(926, 150, 926, 720, 0.1),
        )
        fake.swipe.assert_called_once_with(930, 300, 930, 520, 0.5)

    @patch.object(cn_activity.time, 'sleep', return_value=None)
    def test_story_blue_first_reward_marks_unfinished_stage(self, _sleep):
        fake = SimpleNamespace()
        with patch.object(cn_activity, 'wait_task_info', return_value=True), \
             patch.object(
                 cn_activity.image,
                 'compare_image',
                 side_effect=lambda _self, name, *_args, **_kwargs: name == 'cn_activity_first-reward-blue',
             ) as compare_image, \
             patch.object(cn_activity.ocr, 'screenshot_check_text') as check_text:
            self.assertEqual(cn_activity.check_task_state(fake, 'story'), 'no-sss')
        compare_image.assert_called_once_with(fake, 'cn_activity_first-reward-blue', 0, 0.75)
        check_text.assert_not_called()

    @patch.object(cn_activity.time, 'sleep', return_value=None)
    def test_story_ocr_first_reward_marks_unfinished_stage(self, _sleep):
        fake = SimpleNamespace(ocr=object())
        with patch.object(cn_activity, 'wait_task_info', return_value=True), \
             patch.object(cn_activity.image, 'compare_image', return_value=False) as compare_image, \
             patch.object(cn_activity.ocr, 'screenshot_check_text', return_value=True) as check_text:
            self.assertEqual(cn_activity.check_task_state(fake, 'story'), 'no-sss')
        self.assertEqual(
            compare_image.call_args_list,
            [
                call(fake, 'cn_activity_first-reward-blue', 0, 0.75),
                call(fake, 'cn_activity_first-reward', 0, 0.8),
            ],
        )
        check_text.assert_called_once_with(fake, '首次', (340, 300, 665, 395), 0, 0, False)

    @patch.object(cn_activity.time, 'sleep', return_value=None)
    def test_story_first_reward_fallback_marks_unfinished_stage(self, _sleep):
        fake = SimpleNamespace()
        with patch.object(cn_activity, 'wait_task_info', return_value=True), \
             patch.object(
                 cn_activity.image,
                 'compare_image',
                 side_effect=lambda _self, name, *_args, **_kwargs: name == 'cn_activity_first-reward',
             ) as compare_image, \
             patch.object(cn_activity.ocr, 'screenshot_check_text', return_value=False):
            self.assertEqual(cn_activity.check_task_state(fake, 'story'), 'no-sss')
        self.assertEqual(
            compare_image.call_args_list,
            [
                call(fake, 'cn_activity_first-reward-blue', 0, 0.75),
                call(fake, 'cn_activity_first-reward', 0, 0.8),
            ],
        )

    @patch.object(cn_activity.time, 'sleep', return_value=None)
    def test_story_without_unfinished_markers_marks_completed_stage(self, _sleep):
        fake = SimpleNamespace()
        with patch.object(cn_activity, 'wait_task_info', return_value=True), \
             patch.object(cn_activity.image, 'compare_image', return_value=False) as compare_image, \
             patch.object(cn_activity.ocr, 'screenshot_check_text', return_value=False):
            self.assertEqual(cn_activity.check_task_state(fake, 'story'), 'sss')
        self.assertEqual(
            compare_image.call_args_list,
            [
                call(fake, 'cn_activity_first-reward-blue', 0, 0.75),
                call(fake, 'cn_activity_first-reward', 0, 0.8),
            ],
        )

    @patch.object(cn_activity.time, 'sleep', return_value=None)
    def test_story_without_ocr_object_marks_completed_stage(self, _sleep):
        fake = SimpleNamespace(ocr=None)
        with patch.object(cn_activity, 'wait_task_info', return_value=True), \
             patch.object(cn_activity.image, 'compare_image', return_value=False), \
             patch.object(cn_activity.ocr, 'screenshot_check_text') as check_text:
            self.assertEqual(cn_activity.check_task_state(fake, 'story'), 'sss')
        check_text.assert_not_called()

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
             patch.object(cn_activity, 'enter_activity_stage_page'), \
             patch.object(cn_activity, 'reset_activity_stage_list'), \
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


class ActivityDrawCardTests(unittest.TestCase):
    def test_draw_resource_ocr_crop_excludes_event_item_icon(self):
        self.assertEqual(
            cn_activity.DRAW_RESOURCE_AREA,
            (712, 165, 790, 202),
        )

    def test_draw_number_parses_high_confidence_digits(self):
        engine = SimpleNamespace(
            ocr=Mock(return_value=[{'text': '1,234', 'score': 0.9}]),
        )
        fake = SimpleNamespace(ocrNum=engine, logger=FakeLogger())
        screenshot = np.zeros((720, 1280, 3), dtype=np.uint8)
        self.assertEqual(
            cn_activity._draw_number(
                fake,
                cn_activity.DRAW_RESOURCE_AREA,
                screenshot,
            ),
            1234,
        )

    def test_draw_number_rejects_low_confidence_graphic_noise(self):
        engine = SimpleNamespace(
            ocr=Mock(return_value=[{'text': '63299', 'score': 0.17}]),
        )
        fake = SimpleNamespace(ocrNum=engine, logger=FakeLogger())
        screenshot = np.zeros((720, 1280, 3), dtype=np.uint8)
        self.assertIsNone(
            cn_activity._draw_number(
                fake,
                cn_activity.DRAW_RESOURCE_AREA,
                screenshot,
            ),
        )

    def test_draw_state_prefers_enabled_single_draw_button(self):
        fake = SimpleNamespace(logger=FakeLogger())
        screenshot = np.zeros((720, 1280, 3), dtype=np.uint8)
        with patch.object(cn_activity.color, 'check_rgb', return_value=True), \
             patch.object(cn_activity, '_draw_number') as draw_number:
            self.assertEqual(
                cn_activity._draw_card_state(fake, screenshot),
                'draw',
            )
        draw_number.assert_not_called()

    def test_draw_state_shuffles_completed_round_when_resource_is_enough(self):
        fake = SimpleNamespace(logger=FakeLogger())
        screenshot = np.zeros((720, 1280, 3), dtype=np.uint8)
        with patch.object(cn_activity.color, 'check_rgb', side_effect=[False, True]), \
             patch.object(cn_activity, '_draw_number', side_effect=[493, 210]):
            self.assertEqual(
                cn_activity._draw_card_state(fake, screenshot),
                'shuffle',
            )

    def test_draw_state_stops_when_resource_is_below_single_cost(self):
        fake = SimpleNamespace(logger=FakeLogger())
        screenshot = np.zeros((720, 1280, 3), dtype=np.uint8)
        with patch.object(cn_activity.color, 'check_rgb', return_value=False), \
             patch.object(cn_activity, '_draw_number', side_effect=[53, 250]):
            self.assertEqual(
                cn_activity._draw_card_state(fake, screenshot),
                'done',
            )

    @patch.object(cn_activity.time, 'sleep', return_value=None)
    def test_draw_card_closes_rewards_and_shuffles_without_random_reward_template(self, _sleep):
        fake = SimpleNamespace(
            tc={'draw_card': {'enable': True}},
            click=Mock(),
            get_screenshot_array=Mock(return_value=np.zeros((720, 1280, 3))),
            logger=FakeLogger(),
        )
        with patch.object(cn_activity, 'to_activity_page'), \
             patch.object(cn_activity, '_enter_activity_feature_page', return_value=True), \
             patch.object(cn_activity, '_draw_card_state', side_effect=['draw', 'shuffle', 'done']), \
             patch.object(cn_activity, '_close_draw_reward') as close_reward:
            cn_activity.start_draw_card(fake)
        self.assertEqual(
            fake.click.call_args_list,
            [
                call(*cn_activity.DRAW_SINGLE_BUTTON_POS, False),
                call(*cn_activity.DRAW_SHUFFLE_BUTTON_POS, False),
            ],
        )
        close_reward.assert_called_once_with(fake)

    def test_close_draw_reward_waits_for_overlay_to_appear_and_disappear(self):
        fake = SimpleNamespace(click=Mock())
        with patch.object(
            cn_activity.image,
            'compare_image',
            side_effect=[True, True],
        ) as compare_image:
            cn_activity._close_draw_reward(fake)
        fake.click.assert_called_once_with(640, 635, False)
        self.assertEqual(
            compare_image.call_args_list,
            [
                call(
                    fake,
                    'cm_get-prize',
                    retry=60,
                    threshold=0.8,
                ),
                call(
                    fake,
                    'cm_get-prize',
                    retry=60,
                    threshold=0.8,
                    n=True,
                ),
            ],
        )

    def test_draw_card_missing_entry_skips_unavailable_event_feature(self):
        fake = SimpleNamespace(
            tc={'draw_card': {'enable': True}},
            get_screenshot_array=Mock(),
        )
        with patch.object(cn_activity, 'to_activity_page'), \
             patch.object(cn_activity, '_enter_activity_feature_page', return_value=False):
            self.assertIsNone(cn_activity.start_draw_card(fake))
        fake.get_screenshot_array.assert_not_called()

    def test_exchange_and_dice_skip_when_current_event_lacks_their_entry(self):
        fake = SimpleNamespace(
            tc={
                'exchange': {'enable': True},
                'dice': {'enable': True},
            },
            log_title=Mock(),
            click=Mock(),
        )
        with patch.object(cn_activity, 'to_activity_page'), \
             patch.object(cn_activity, '_enter_activity_feature_page', return_value=False):
            self.assertIsNone(cn_activity.start_exchange(fake))
            self.assertIsNone(cn_activity.start_dice(fake))
        fake.click.assert_not_called()

    def test_god_cross_reuses_generic_right_top_tab_logic(self):
        fake = SimpleNamespace()
        with patch.object(cn_activity, 'to_tab') as to_tab:
            god_cross.to_tab(fake, 'story')
        to_tab.assert_called_once_with(fake, 'story')

    def test_god_cross_reuses_verified_draw_card_state_machine(self):
        fake = SimpleNamespace(tc={'draw_card': {'enable': True}})
        with patch.object(god_cross, 'to_activity_page'), \
             patch.object(god_cross.image, 'detect', return_value='brzx_draw-menu') as detect, \
             patch.object(cn_activity, 'draw_cards_on_current_page') as draw_cards:
            god_cross.start_draw_card(fake)
        self.assertEqual(detect.call_args.kwargs['retry'], 5)
        draw_cards.assert_called_once_with(fake)


if __name__ == '__main__':
    unittest.main()
