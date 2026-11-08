import contextlib
import io
import subprocess
import unittest
from unittest.mock import patch

from nettool import ping_tool


class TestPing(unittest.TestCase):

    def test_unknown_loss_does_not_show_none_percent(self):
        result = {
            "ok": True,
            "error": None,
            "raw": "",
            "sent": None,
            "received": 3,
            "loss_percent": None,
            "avg_time_ms": None,
            "target_ip": "192.0.2.1",
            "unresolved": False,
        }
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            ping_tool.print_report(result, "192.0.2.1", 4)

        self.assertNotIn("None%", output.getvalue())
        self.assertNotIn("连接可能不稳定", output.getvalue())

    @patch("nettool.ping_tool.subprocess.run")
    def test_ping_timeout(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired(["ping"], 10)
        result = ping_tool.ping_host("127.0.0.1")
        self.assertFalse(result["ok"])
        self.assertIn("超时", result["error"])

    @patch("nettool.ping_tool.subprocess.run")
    def test_ping_command_not_found(self, mock_run):
        mock_run.side_effect = FileNotFoundError()
        result = ping_tool.ping_host("127.0.0.1")
        self.assertFalse(result["ok"])
        self.assertIn("找不到", result["error"])

    @patch("nettool.ping_tool.subprocess.run")
    def test_ping_permission_denied(self, mock_run):
        mock_run.side_effect = PermissionError()
        result = ping_tool.ping_host("127.0.0.1")
        self.assertFalse(result["ok"])
        self.assertIn("权限", result["error"])

    def test_failed_result_structure(self):
        result = ping_tool._failed_result("模拟执行失败")
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "模拟执行失败")
        self.assertIsNone(result["loss_percent"])


if __name__ == "__main__":
    unittest.main()