import io
import json
import socket
import unittest
from unittest.mock import MagicMock, patch

from nettool import ip_tool


class TestIp(unittest.TestCase):

    @patch("nettool.ip_tool.socket.socket")
    def test_primary_local_ip_success(self, mock_socket):
        probe = mock_socket.return_value
        probe.getsockname.return_value = ("192.168.1.10", 12345)

        result = ip_tool.get_primary_local_ip()

        self.assertEqual(result, "192.168.1.10")
        probe.connect.assert_called_once_with(ip_tool.PROBE_TARGET)
        probe.close.assert_called_once()

    @patch("nettool.ip_tool.socket.socket")
    def test_primary_local_ip_failure(self, mock_socket):
        probe = mock_socket.return_value
        probe.connect.side_effect = OSError("模拟网络异常")

        self.assertIsNone(ip_tool.get_primary_local_ip())
        probe.close.assert_called_once()

    @patch("nettool.ip_tool.socket.getaddrinfo")
    def test_collect_addresses(self, mock_getaddrinfo):
        def fake_lookup(host, port, family, socktype):
            if family == socket.AF_INET:
                return [
                    (family, socktype, 0, "", ("192.0.2.10", 0)),
                    (family, socktype, 0, "", ("192.0.2.10", 0)),
                ]
            return [
                (family, socktype, 0, "", ("2001:db8::10", 0, 0, 0)),
            ]

        mock_getaddrinfo.side_effect = fake_lookup

        ipv4, ipv6 = ip_tool.collect_addresses("example.com")

        self.assertEqual(ipv4, ["192.0.2.10"])
        self.assertEqual(ipv6, ["2001:db8::10"])

    @patch("nettool.ip_tool.urllib.request.urlopen")
    def test_query_ip_info_success(self, mock_urlopen):
        payload = {
            "status": "success",
            "query": "8.8.8.8",
            "country": "United States",
        }
        response = MagicMock()
        response.read.return_value = json.dumps(payload).encode()
        mock_urlopen.return_value.__enter__.return_value = response

        result = ip_tool.query_ip_info("8.8.8.8")

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["query"], "8.8.8.8")

    @patch("nettool.ip_tool.urllib.request.urlopen")
    def test_query_ip_info_failure(self, mock_urlopen):
        response = MagicMock()
        response.read.return_value = (
            b'{"status":"fail","message":"invalid query"}'
        )
        mock_urlopen.return_value.__enter__.return_value = response

        with self.assertRaises(RuntimeError):
            ip_tool.query_ip_info("invalid")

    @patch("nettool.ip_tool.urllib.request.urlopen")
    def test_public_ip_fallback(self, mock_urlopen):
        first = MagicMock()
        first.read.return_value = b"not-an-ip"

        second = MagicMock()
        second.read.return_value = b'{"ip":"203.0.113.10"}'

        mock_urlopen.return_value.__enter__.side_effect = [
            first,
            second,
        ]

        result = ip_tool.query_public_ip_simple()

        self.assertEqual(result, "203.0.113.10")
        self.assertEqual(mock_urlopen.call_count, 2)


if __name__ == "__main__":
    unittest.main()