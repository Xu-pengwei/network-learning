import unittest

from nettool import utils


class TestUtilsEdge(unittest.TestCase):

    def test_ipv4_broadcast(self):
        result = utils.describe_ip("255.255.255.255")
        self.assertNotIn("公网", result)
        self.assertNotIn("内网", result)

    def test_ipv4_multicast(self):
        result = utils.describe_ip("224.0.0.1")
        self.assertNotIn("公网", result)
        self.assertNotIn("内网", result)

    def test_ipv6_unspecified(self):
        result = utils.describe_ip("::")
        self.assertNotIn("公网", result)
        self.assertNotIn("内网", result)

    def test_overlong_hostname_label(self):
        hostname = "a" * 64 + ".example.com"
        self.assertFalse(utils.is_valid_hostname(hostname))


if __name__ == "__main__":
    unittest.main()