import importlib.util
import unittest
from pathlib import Path
from unittest.mock import MagicMock, call, patch


MODULE_PATH = Path(__file__).with_name("test_server.py")


def load_manual_checks_module():
    spec = importlib.util.spec_from_file_location("manual_server_checks", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ManualServerChecksTest(unittest.TestCase):
    def test_default_run_does_not_send_player_controls(self):
        module = load_manual_checks_module()

        with (
            patch.object(
                module,
                "check_healthcheck",
                new=MagicMock(return_value="healthcheck"),
            ),
            patch.object(
                module,
                "check_poll",
                new=MagicMock(return_value="poll"),
            ),
            patch.object(
                module,
                "check_control_ypm",
                new=MagicMock(),
            ) as check_control_ypm,
            patch.object(
                module,
                "check_control_spotify",
                new=MagicMock(),
            ) as check_control_spotify,
            patch.object(module.asyncio, "run") as run,
        ):
            module.main([])

        self.assertEqual(run.call_args_list, [call("healthcheck"), call("poll")])
        check_control_ypm.assert_not_called()
        check_control_spotify.assert_not_called()


if __name__ == "__main__":
    unittest.main()
