"""
utils 模块单元测试
====================
运行方式（在项目根目录执行）：
    python -m unittest discover -s tests -v

测试重点：
    输入校验是三个功能共同的"第一道关卡"，如果这里判断错误，
    用户输入合法地址也会被拒绝，所以单独为它写测试。
"""

import unittest

from nettool import utils


class TestNormalizeTarget(unittest.TestCase):
    """测试地址整理的兼容性。"""

    def test_plain_domain(self):
        self.assertEqual(utils.normalize_target("www.baidu.com"), "www.baidu.com")

    def test_strip_whitespace(self):
        self.assertEqual(utils.normalize_target("  www.qq.com  "), "www.qq.com")

    def test_strip_http_prefix_and_path(self):
        self.assertEqual(
            utils.normalize_target("https://www.baidu.com/s?wd=python"),
            "www.baidu.com",
        )

    def test_strip_port(self):
        self.assertEqual(utils.normalize_target("example.com:8080"), "example.com")

    def test_ipv6_brackets(self):
        self.assertEqual(utils.normalize_target("[::1]"), "::1")

    def test_ipv6_without_brackets(self):
        self.assertEqual(utils.normalize_target("2001:db8::1"), "2001:db8::1")

    def test_empty(self):
        self.assertEqual(utils.normalize_target(""), "")
        self.assertEqual(utils.normalize_target("   "), "")


class TestIpAddress(unittest.TestCase):
    """测试 IP 地址判断。"""

    def test_valid_ipv4(self):
        self.assertTrue(utils.is_ip_address("192.168.1.1"))
        self.assertTrue(utils.is_ip_address("8.8.8.8"))

    def test_valid_ipv6(self):
        self.assertTrue(utils.is_ip_address("::1"))
        self.assertTrue(utils.is_ip_address("2001:db8::1"))

    def test_invalid(self):
        self.assertFalse(utils.is_ip_address("256.1.1.1"))
        self.assertFalse(utils.is_ip_address("www.baidu.com"))
        self.assertFalse(utils.is_ip_address(""))


class TestHostname(unittest.TestCase):
    """测试域名判断。"""

    def test_valid_domains(self):
        self.assertTrue(utils.is_valid_hostname("www.baidu.com"))
        self.assertTrue(utils.is_valid_hostname("localhost"))
        self.assertTrue(utils.is_valid_hostname("a-b.example.com"))
        self.assertTrue(utils.is_valid_hostname("www.example.com."))

    def test_invalid_domains(self):
        self.assertFalse(utils.is_valid_hostname(""))
        self.assertFalse(utils.is_valid_hostname("-bad.example.com"))
        self.assertFalse(utils.is_valid_hostname("bad-.example.com"))
        self.assertFalse(utils.is_valid_hostname("hello world"))
        self.assertFalse(utils.is_valid_hostname("a..b"))
        self.assertFalse(utils.is_valid_hostname("x" * 64 + ".com"))


class TestDescribeIp(unittest.TestCase):
    """测试 IP 类型的中文描述。"""

    def test_loopback(self):
        self.assertIn("回环", utils.describe_ip("127.0.0.1"))

    def test_private(self):
        self.assertIn("内网", utils.describe_ip("192.168.1.1"))
        self.assertIn("内网", utils.describe_ip("10.0.0.1"))
        self.assertIn("内网", utils.describe_ip("172.16.5.5"))

    def test_public(self):
        self.assertIn("公网", utils.describe_ip("8.8.8.8"))

    def test_invalid(self):
        self.assertIn("无法识别", utils.describe_ip("not-an-ip"))


class TestPingParsing(unittest.TestCase):
    """测试 ping 输出解析（不真正执行 ping，只验证解析逻辑）。"""

    def test_parse_chinese_windows_output(self):
        from nettool import ping_tool

        text = (
            "正在 Ping www.baidu.com [110.242.68.66] 具有 32 字节的数据:\n"
            "来自 110.242.68.66 的回复: 字节=32 时间=11ms TTL=54\n"
            "    数据包: 已发送 = 4，已接收 = 4，丢失 = 0 (0% 丢失)，\n"
            "    最短 = 10ms，最长 = 12ms，平均 = 11ms\n"
        )
        result = ping_tool.parse_ping_output(text)

        self.assertEqual(result["sent"], 4)
        self.assertEqual(result["received"], 4)
        self.assertEqual(result["loss_percent"], 0)
        self.assertEqual(result["avg_time_ms"], 11)
        self.assertEqual(result["target_ip"], "110.242.68.66")
        self.assertFalse(result["unresolved"])

    def test_parse_linux_output(self):
        from nettool import ping_tool

        text = (
            "PING www.baidu.com (110.242.68.66) 56(84) bytes of data.\n"
            "4 packets transmitted, 4 received, 0% packet loss, time 3004ms\n"
            "rtt min/avg/max/mdev = 10.123/11.456/12.789/1.234 ms\n"
        )
        result = ping_tool.parse_ping_output(text)

        self.assertEqual(result["sent"], 4)
        self.assertEqual(result["received"], 4)
        self.assertEqual(result["loss_percent"], 0)
        self.assertAlmostEqual(result["avg_time_ms"], 11.456)

    def test_parse_unresolved(self):
        from nettool import ping_tool

        text = "Ping 请求找不到主机 not-exist.invalid。请检查该名称，然后重试。\n"
        result = ping_tool.parse_ping_output(text)
        self.assertTrue(result["unresolved"])


class TestPingCommand(unittest.TestCase):
    """测试 ping 命令生成是否随平台变化。"""

    def test_command_contains_host_and_count(self):
        from nettool import ping_tool

        command = ping_tool.build_ping_command("127.0.0.1", 2, 1000)
        self.assertEqual(command[0], "ping")
        self.assertIn("127.0.0.1", command)
        self.assertIn("2", command)


if __name__ == "__main__":
    unittest.main()
