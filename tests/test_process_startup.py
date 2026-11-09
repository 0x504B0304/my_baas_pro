import builtins
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from common import encrypt, process


class ProcessStartupTests(unittest.TestCase):
    def test_engine_import_failure_is_logged_and_reported(self):
        original_import = builtins.__import__
        logger = Mock()
        state = {}

        def fail_engine_import(name, *args, **kwargs):
            if name == 'common.baas':
                raise ImportError('broken bundled dependency')
            return original_import(name, *args, **kwargs)

        with patch('builtins.__import__', side_effect=fail_engine_import), \
             patch.object(process.log, 'create_logger', return_value=logger):
            process.baas_dashboard('test', state, '', process.log._log_enabled)

        self.assertTrue(state[encrypt.md5('test')]['error'])
        self.assertIn('broken bundled dependency', logger.critical.call_args_list[0].args[0])
        self.assertIn('ImportError', logger.critical.call_args_list[1].args[0])

    def test_startup_check_loads_config_without_constructing_engine(self):
        engine = Mock()
        state = {}
        with patch.dict('sys.modules', {'common.baas': SimpleNamespace(Baas=engine)}), \
             patch.object(process.log, 'create_logger', return_value=Mock()), \
             patch('common.config.load_ba_config', return_value={}) as load:
            process.baas_dashboard('test', state, '', process.log._log_enabled, True)

        engine.assert_not_called()
        load.assert_called_once_with('test')
        self.assertTrue(state[encrypt.md5('test')]['startup_checked'])


if __name__ == '__main__':
    unittest.main()
