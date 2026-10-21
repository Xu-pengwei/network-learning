"""
Ping 网络连通性检测模块
==========================
功能：
    调用操作系统自带的 ping 命令，检测本机到目标主机之间是否连通，
    并解析出"发送包数、接收包数、丢包率、平均延迟"等关键指标。

原理提示：
    ping 使用的是 ICMP 协议：本机发出"回显请求"，目标主机回复"回显应答"。
    如果对方关机、网络中断，或者防火墙拦截了 ICMP，我们就会看到丢包。

跨平台说明：
    Windows 与 Linux/macOS 的 ping 参数不同，本模块用 platform.system()
    自动判断系统，生成对应的命令参数，做到一套代码多平台运行。
"""

from __future__ import annotations

import locale
import platform
import re
import subprocess

from . import utils

# ---------------------------------------------------------------- 默认参数
DEFAULT_COUNT = 4           # 默认发送 4 个探测包
DEFAULT_TIMEOUT_MS = 2000   # 单个包最长等待时间（毫秒）

# ping 的输出文字会随"系统语言"和"操作系统"变化，所以每个指标准备多个
# 正则表达式，只要有一个匹配成功即可。这样程序不会因为中英文系统而失效。
_PATTERNS = {
    "sent": [
        r"已发送\s*=\s*(\d+)",          # 中文 Windows
        r"Sent\s*=\s*(\d+)",            # 英文 Windows
        r"(\d+)\s+packets\s+transmitted",  # Linux / macOS
    ],
    "received": [
        r"已接收\s*=\s*(\d+)",
        r"Received\s*=\s*(\d+)",
        r"(\d+)\s+(?:packets\s+)?received",
    ],
    "loss": [
        r"丢失\s*=\s*\d+\s*\((\d+)%",
        r"Lost\s*=\s*\d+\s*\((\d+)%",
        r"(\d+)%\s+packet\s+loss",
    ],
    "avg": [
        r"平均\s*=\s*(\d+(?:\.\d+)?)\s*ms",
        r"Average\s*=\s*(\d+(?:\.\d+)?)\s*ms",
        r"min/avg/max[^=]*=\s*[\d.]+/([\d.]+)/",
    ],
}

# 目标 IP 可能出现在这些句子里，例如：
#   "正在 Ping www.baidu.com [110.242.68.66] 具有 32 字节的数据:"
#   "Pinging www.baidu.com [110.242.68.66] with 32 bytes of data:"
#   "PING www.baidu.com (110.242.68.66): 56 data bytes"
_IP_PATTERNS = [
    r"Ping\s+\S+\s+\[([^\]]+)\]",
    r"Pinging\s+\S+\s+\[([^\]]+)\]",
    r"PING\s+\S+\s+\(([^)]+)\)",
]

# 出现这些关键词，说明域名根本没解析成功，属于"输入错误"而不是"网络不通"
_UNRESOLVED_KEYWORDS = (
    "找不到主机",
    "could not find host",
    "cannot resolve",
    "name or service not known",
    "unknown host",
)


def _decode_output(raw: bytes) -> str:
    """
    把 ping 命令返回的字节数据解码成文字。

    中文 Windows 的 ping 输出通常是 GBK 编码，而部分环境是 UTF-8，
    所以依次尝试多种编码，保证中文不会变成乱码。
    """
    encodings = ("utf-8", locale.getpreferredencoding(False), "gbk")
    for encoding in encodings:
        try:
            return raw.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            continue
    return raw.decode("utf-8", errors="replace")


def build_ping_command(host: str, count: int = DEFAULT_COUNT,
                       timeout_ms: int = DEFAULT_TIMEOUT_MS) -> list[str]:
    """
    根据当前操作系统，生成 ping 命令的参数列表。

    参数含义：
        Windows ：-n 发送次数，-w 单次超时（毫秒）
        Linux   ：-c 发送次数，-W 单次超时（秒）
        macOS   ：-c 发送次数，-W 单次超时（毫秒）
    """
    system = platform.system().lower()

    if system == "windows":
        return ["ping", "-n", str(count), "-w", str(timeout_ms), host]

    if system == "darwin":  # macOS
        return ["ping", "-c", str(count), "-W", str(timeout_ms), host]

    # 其他系统按 Linux 处理：-W 的单位是秒
    timeout_s = max(1, timeout_ms // 1000)
    return ["ping", "-c", str(count), "-W", str(timeout_s), host]


def _search_number(patterns: list[str], text: str) -> int | None:
    """在文本中依次尝试多个正则，返回第一个匹配到的整数。"""
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))
    return None


def parse_ping_output(text: str) -> dict:
    """
    从 ping 的文本输出中提取关键数据。

    返回字典包含：
        sent / received / loss_percent / avg_time_ms / target_ip / unresolved
    提取失败的项目为 None，调用者可以据此显示"未知"。
    """
    result = {
        "sent": _search_number(_PATTERNS["sent"], text),
        "received": _search_number(_PATTERNS["received"], text),
        "loss_percent": _search_number(_PATTERNS["loss"], text),
        "avg_time_ms": None,
        "target_ip": None,
        "unresolved": any(word in text.lower() for word in _UNRESOLVED_KEYWORDS),
    }

    # 平均延迟允许是小数（Linux 常见 11.456ms）
    for pattern in _PATTERNS["avg"]:
        match = re.search(pattern, text)
        if match:
            result["avg_time_ms"] = float(match.group(1))
            break

    for pattern in _IP_PATTERNS:
        match = re.search(pattern, text)
        if match:
            result["target_ip"] = match.group(1)
            break

    # 某些系统只给出丢包率不给收发数量，这里用丢包率反推，方便展示
    if result["loss_percent"] is None and result["sent"] and result["received"] is not None:
        result["loss_percent"] = round(
            (result["sent"] - result["received"]) / result["sent"] * 100
        )

    return result


def ping_host(host: str, count: int = DEFAULT_COUNT,
              timeout_ms: int = DEFAULT_TIMEOUT_MS) -> dict:
    """
    对目标主机执行 ping 检测。

    参数：
        host       —— 域名或 IP 地址
        count      —— 发送探测包的个数
        timeout_ms —— 每个包等待回应的毫秒数

    返回字典的键：
        ok           —— 是否成功拿到 ping 结果（不代表网络一定通）
        error        —— 出错时的中文说明，正常时为 None
        raw          —— ping 的原始输出，便于排查问题
        sent/received/loss_percent/avg_time_ms/target_ip/unresolved
    """
    command = build_ping_command(host, count, timeout_ms)

    # 给整个进程留一点额外时间，避免单个包超时累积后进程被强杀
    overall_timeout = max(10.0, count * (timeout_ms / 1000.0) + 5.0)

    # Windows 下不弹出黑色控制台窗口（该常量只在 Windows 上存在）
    creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            timeout=overall_timeout,
            creationflags=creation_flags,
        )
    except FileNotFoundError:
        return _failed_result("系统找不到 ping 命令，请确认系统是否支持 ping。")
    except subprocess.TimeoutExpired:
        return _failed_result(
            f"ping 命令执行超时（超过 {overall_timeout:g} 秒），目标可能完全无响应。"
        )
    except PermissionError:
        return _failed_result("没有权限执行 ping 命令，请检查系统安全设置。")

    # stdout 和 stderr 都转成文字，有些系统把错误信息写在 stderr 里
    raw_text = _decode_output(completed.stdout) + _decode_output(completed.stderr)

    result = parse_ping_output(raw_text)
    result["ok"] = True
    result["error"] = None
    result["raw"] = raw_text
    return result


def _failed_result(message: str) -> dict:
    """构造一个"命令未能执行"的失败结果，保证返回结构统一。"""
    return {
        "ok": False,
        "error": message,
        "raw": "",
        "sent": None,
        "received": None,
        "loss_percent": None,
        "avg_time_ms": None,
        "target_ip": None,
        "unresolved": False,
    }


def _format_number(value, unit: str = "") -> str:
    """把可能为 None 的数值格式化成可读文字。"""
    if value is None:
        return "未知"
    if isinstance(value, float):
        # 去掉没有意义的小数末尾 0，例如 11.0 -> 11
        return f"{value:g}{unit}"
    return f"{value}{unit}"


def print_report(result: dict, host: str, count: int) -> None:
    """把 ping 检测结果按固定格式打印出来，并给出通俗的结论。"""
    print()
    utils.print_kv("检测目标", host)
    # 输入本身就是 IP 时，ping 输出里不会出现方括号，这里直接显示目标地址
    target_ip = result["target_ip"] or (host if utils.is_ip_address(host) else None)
    if target_ip:
        utils.print_kv("目标地址", target_ip)
    utils.print_kv("发送包数", _format_number(result["sent"], " 个"))
    utils.print_kv("接收包数", _format_number(result["received"], " 个"))
    utils.print_kv("丢包率", _format_number(result["loss_percent"], " %"))
    utils.print_kv("平均延迟", _format_number(result["avg_time_ms"], " ms"))
    print()

    if result["unresolved"]:
        utils.print_fail("域名解析失败：无法把域名转换成 IP 地址。")
        utils.print_info("请检查域名是否拼写正确，以及本机 DNS 设置是否正常。")
        return

    received = result["received"]
    loss = result["loss_percent"]

    if received == 0:
        utils.print_fail("检测失败：目标主机没有任何回应。")
        utils.print_info("可能原因：对方关机、网络断开，或防火墙拦截了 ICMP 请求。")
    elif loss == 0:
        utils.print_ok("网络连通正常，所有探测包都收到了回应。")
    else:
        utils.print_warn(f"网络可以连通，但存在 {loss}% 的丢包，连接可能不稳定。")

    if result["raw"].strip():
        utils.print_info("如需查看原始输出，请参考下方内容：")
        print_line = "-" * utils.LINE_WIDTH
        print(print_line)
        print(result["raw"].strip())
        print(print_line)


def run() -> None:
    """Ping 功能的交互入口：提示输入目标、执行检测、显示结果。"""
    utils.print_title("Ping 网络连通性检测")
    print("输入域名或 IP 地址即可检测连通性。")
    print("示例：www.baidu.com、127.0.0.1、8.8.8.8")
    print()

    target = utils.ask("请输入目标地址（直接回车返回）：")
    if not target:
        utils.print_warn("没有输入内容，已返回主菜单。")
        return

    host = utils.normalize_target(target)
    if not utils.is_valid_target(host):
        utils.print_fail(f"“{host}”不是合法的域名或 IP 地址，请重新输入。")
        utils.pause()
        return

    utils.print_info(
        f"正在检测 {host}，共发送 {DEFAULT_COUNT} 个探测包，最长约等待 "
        f"{DEFAULT_COUNT * DEFAULT_TIMEOUT_MS // 1000} 秒..."
    )

    result = ping_host(host, DEFAULT_COUNT, DEFAULT_TIMEOUT_MS)

    if not result["ok"]:
        utils.print_fail(result["error"])
        utils.pause()
        return

    print_report(result, host, DEFAULT_COUNT)
    utils.pause()
