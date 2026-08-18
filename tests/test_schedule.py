import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from modules.daily import schedule


class ScheduleCourseInfoTests(unittest.TestCase):
    def test_cn_course_info_uses_popup_title_ocr(self):
        fake = SimpleNamespace(game_server='cn', ocr=object())
        with patch.object(
            schedule.ocr,
            'screenshot_check_text',
            return_value=True,
        ) as check_text, patch.object(schedule.image, 'compare_image') as compare:
            self.assertTrue(schedule.course_info_popup_visible(fake))
        check_text.assert_called_once_with(
            fake,
            '日程信息',
            schedule.COURSE_INFO_TITLE_AREA,
            0,
            0,
            False,
        )
        compare.assert_not_called()

    def test_non_cn_does_not_use_cn_popup_text(self):
        fake = SimpleNamespace(game_server='jp', ocr=object())
        with patch.object(schedule.ocr, 'screenshot_check_text') as check_text:
            self.assertFalse(schedule.course_info_popup_visible(fake))
        check_text.assert_not_called()

    @patch.object(schedule.time, 'sleep', return_value=None)
    def test_to_schedule_closes_course_info_before_back_navigation(self, _sleep):
        fake = SimpleNamespace(click=Mock())
        with patch.object(schedule, 'close_course_info', return_value=True) as close, \
             patch.object(schedule.home, 'to_menu') as to_menu:
            schedule.to_schedule(fake)
        close.assert_called_once_with(fake)
        to_menu.assert_called_once_with(
            fake,
            'schedule_menu',
            {
                'home_student': (212, 656),
                'schedule_choose-course': (59, 36),
            },
        )

    @patch.object(schedule.time, 'sleep', return_value=None)
    def test_close_course_info_clicks_current_popup_x(self, _sleep):
        fake = SimpleNamespace(click=Mock())
        with patch.object(schedule, 'course_info_popup_visible', return_value=True):
            self.assertTrue(schedule.close_course_info(fake))
        fake.click.assert_called_once_with(*schedule.COURSE_INFO_CLOSE_POS, False)

    def test_to_course_info_keeps_region_map_template_navigation(self):
        fake = SimpleNamespace()
        with patch.object(schedule.image, 'detect') as detect:
            schedule.to_course_info(fake, 7)
        detect.assert_called_once_with(
            fake,
            'schedule_course-info',
            {'schedule_menu': schedule.schedule_position[7]},
        )

    def test_choose_course_returns_through_popup_aware_navigation(self):
        fake = SimpleNamespace(tc={'config': [{'schedule': 9, 'count': 1}]})
        with patch.object(schedule, 'to_college'), \
             patch.object(schedule, 'learn_course', return_value=False), \
             patch.object(schedule, 'to_schedule') as to_schedule:
            schedule.choose_course(fake)
        to_schedule.assert_called_once_with(fake)


if __name__ == '__main__':
    unittest.main()
