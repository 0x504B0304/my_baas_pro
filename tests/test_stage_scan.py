import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from common import stage


class ScanResultTests(unittest.TestCase):
    def test_scan_result_waits_for_confirm_without_clicking_skip(self):
        fake = SimpleNamespace(click=Mock())
        with patch.object(stage.image, 'detect', return_value='normal_task_scan-confirm') as detect, \
             patch.object(stage.home, 'click_house_under') as click_home:
            stage.start_scan(fake)

        possibles = detect.call_args.args[2]
        self.assertNotIn('normal_task_scan-skip', possibles)
        self.assertEqual(
            possibles['normal_task_quick-battle-notice'],
            (770, 500),
        )
        fake.click.assert_called_once_with(643, 586)
        click_home.assert_called_once_with(fake)


if __name__ == '__main__':
    unittest.main()
