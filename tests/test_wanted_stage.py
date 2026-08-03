import unittest
from types import SimpleNamespace

from modules.attack import special_entrust


class WantedStageTests(unittest.TestCase):
    def test_cn_wanted_stage_positions_include_new_stage_10(self):
        fake = SimpleNamespace(tc={"task": "wanted"}, game_server="cn")

        self.assertEqual((1116, 360), special_entrust.get_lv_position(fake, 7))
        self.assertEqual((1116, 460), special_entrust.get_lv_position(fake, 8))
        self.assertEqual((1116, 560), special_entrust.get_lv_position(fake, 9))
        self.assertEqual((1116, 655), special_entrust.get_lv_position(fake, 10))

    def test_non_cn_wanted_positions_are_unchanged(self):
        fake = SimpleNamespace(tc={"task": "wanted"}, game_server="jp")
        self.assertEqual((1116, 630), special_entrust.get_lv_position(fake, 10))
        fake.game_server = "intl"
        self.assertEqual((1116, 630), special_entrust.get_lv_position(fake, 10))


if __name__ == "__main__":
    unittest.main()
