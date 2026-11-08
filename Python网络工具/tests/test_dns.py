import socket
import unittest
from unittest.mock import patch

from nettool import dns_tool


class TestDns(unittest.TestCase):

    @patch("nettool.dns_tool.socket.getaddrinfo")
    def test_forward_success(self, mock_getaddrinfo):
        mock_getaddrinfo.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, 0,
             "example.com", ("192.0.2.10", 0)),
            (socket.AF_INET6, socket.SOCK_STREAM, 0,
             "", ("2001:db8::10", 0, 0, 0)),
        ]

        result = dns_tool.resolve_hostname("example.com")

        self.assertEqual(result["ipv4"], ["192.0.2.10"])
        self.assertEqual(result["ipv6"], ["2001:db8::10"])
        self.assertEqual(result["canonical"], "example.com")
        self.assertGreaterEqual(result["elapsed"], 0)

    @patch("nettool.dns_tool.socket.getaddrinfo")
    def test_forward_failure(self, mock_getaddrinfo):
        mock_getaddrinfo.side_effect = socket.gaierror(
            socket.EAI_NONAME, "Name not known"
        )

        with self.assertRaises(socket.gaierror):
            dns_tool.resolve_hostname("invalid.example")

    @patch("nettool.dns_tool.socket.gethostbyaddr")
    def test_reverse_success(self, mock_gethostbyaddr):
        mock_gethostbyaddr.return_value = (
            "example.com", ["alias.example.com"], ["192.0.2.10"]
        )

        hostname, aliases = dns_tool.reverse_lookup("192.0.2.10")

        self.assertEqual(hostname, "example.com")
        self.assertEqual(aliases, ["alias.example.com"])

    @patch("nettool.dns_tool.socket.gethostbyaddr")
    def test_reverse_failure(self, mock_gethostbyaddr):
        mock_gethostbyaddr.side_effect = socket.herror(
            1, "Unknown host"
        )

        with self.assertRaises(socket.herror):
            dns_tool.reverse_lookup("192.0.2.10")

    @patch("nettool.dns_tool.socket.getaddrinfo")
    def test_timeout_restored_after_error(self, mock_getaddrinfo):
        mock_getaddrinfo.side_effect = socket.gaierror(
            socket.EAI_NONAME, "Name not known"
        )

        original = socket.getdefaulttimeout()

        with self.assertRaises(socket.gaierror):
            dns_tool.resolve_hostname("invalid.example", timeout=2.0)

        self.assertEqual(socket.getdefaulttimeout(), original)


if __name__ == "__main__":
    unittest.main()