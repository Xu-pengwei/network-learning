"""
DNS 域名解析模块
==================
功能：
    1. 正向解析：把域名转换成 IP 地址（查询 A 记录和 AAAA 记录）；
    2. 反向解析：把 IP 地址反查成域名（查询 PTR 记录）。

原理提示：
    DNS（域名系统）就像互联网的"电话簿"，负责把 www.baidu.com 这样的
    名字翻译成 110.242.68.66 这样的 IP 地址。
    Python 的 socket.getaddrinfo() 会调用系统自带的解析器完成查询，
    所以本机 DNS 配置错误时，这里也会跟着解析失败。
"""

from __future__ import annotations

import contextlib
import ipaddress
import socket
import time

from . import utils

# DNS 查询的最长等待时间（秒），避免某个域名无响应时程序卡死
DNS_TIMEOUT = 5.0


@contextlib.contextmanager
def _socket_timeout(timeout: float):
    """
    临时修改全局 socket 超时时间，离开代码块时自动恢复。

    socket.getaddrinfo() 和 socket.gethostbyaddr() 都不接受 timeout 参数，
    只能通过 socket.setdefaulttimeout() 统一设置，所以用上下文管理器保证
    即使查询抛出异常，也能把全局设置恢复原样，不影响程序其他部分。
    """
    old_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(timeout)
    try:
        yield
    finally:
        socket.setdefaulttimeout(old_timeout)


def resolve_hostname(host: str, timeout: float = DNS_TIMEOUT) -> dict:
    """
    正向解析域名，返回该域名对应的全部 IPv4 和 IPv6 地址。

    参数：
        host    —— 域名，例如 www.baidu.com
        timeout —— 最长等待时间（秒）

    返回字典：
        ipv4      —— IPv4 地址列表
        ipv6      —— IPv6 地址列表
        canonical —— 规范主机名（解析结果中的正式名称）
        elapsed   —— 本次解析耗时（秒）

    解析失败时抛出 socket.gaierror，由调用者负责提示用户。
    """
    started = time.perf_counter()

    # 通过 AI_CANONNAME 让解析器顺带返回规范主机名
    with _socket_timeout(timeout):
        infos = socket.getaddrinfo(
            host,
            None,
            socket.AF_UNSPEC,
            socket.SOCK_STREAM,
            0,
            socket.AI_CANONNAME,
        )

    ipv4: list[str] = []
    ipv6: list[str] = []
    canonical = ""

    for info in infos:
        address = info[4][0]
        # IPv6 链路本地地址可能带 %网卡编号 后缀，展示时去掉
        address = address.split("%")[0]

        if not canonical and info[3]:
            canonical = info[3].rstrip(".")

        if ":" in address:
            if address not in ipv6:
                ipv6.append(address)
        elif address not in ipv4:
            ipv4.append(address)

    # 按 IP 数值大小排序，让同一域名多次查询的显示顺序保持稳定
    ipv4.sort(key=ipaddress.ip_address)
    ipv6.sort(key=ipaddress.ip_address)

    return {
        "host": host,
        "ipv4": ipv4,
        "ipv6": ipv6,
        "canonical": canonical or host,
        "elapsed": time.perf_counter() - started,
    }


def reverse_lookup(ip_text: str, timeout: float = DNS_TIMEOUT) -> tuple[str, list[str]]:
    """
    反向解析 IP 地址（PTR 记录），返回 (主机名, 别名列表)。

    不是所有 IP 都配置了反向解析，查不到时会抛出 socket.herror，
    这属于正常现象，调用者应当给出友好提示而不是报错退出。
    """
    with _socket_timeout(timeout):
        hostname, aliases, _addresses = socket.gethostbyaddr(ip_text)
    return hostname, aliases


def run_forward() -> None:
    """正向解析的交互流程。"""
    utils.print_title("DNS 正向解析（域名 -> IP）")
    print("示例：www.baidu.com、www.qq.com")
    print()

    target = utils.ask("请输入要解析的域名（直接回车返回）：")
    if not target:
        utils.print_warn("没有输入内容，已返回上一级菜单。")
        return

    host = utils.normalize_target(target)
    if not utils.is_valid_hostname(host):
        utils.print_fail(f"“{host}”不是合法的域名，请重新输入。")
        utils.pause()
        return

    utils.print_info(f"正在解析 {host} ...")

    try:
        result = resolve_hostname(host, DNS_TIMEOUT)
    except socket.gaierror as exc:
        utils.print_fail(f"解析失败：找不到 {host} 对应的 IP 地址。")
        utils.print_info(f"系统返回的错误信息：{exc}")
        utils.print_info("请检查域名拼写，或者稍后再试（也可能是本机网络未连接）。")
        utils.pause()
        return

    print()
    utils.print_ok("解析成功")
    utils.print_kv("查询域名", result["host"])
    utils.print_kv("规范名称", result["canonical"])
    utils.print_kv("解析耗时", f"{result['elapsed'] * 1000:.1f} ms")
    print()

    if result["ipv4"]:
        utils.print_info(f"IPv4 地址（A 记录）共 {len(result['ipv4'])} 个：")
        for index, address in enumerate(result["ipv4"], start=1):
            print(f"    {index}. {address}  [{utils.describe_ip(address)}]")
    else:
        utils.print_warn("没有查询到 IPv4 地址（A 记录）。")

    if result["ipv6"]:
        utils.print_info(f"IPv6 地址（AAAA 记录）共 {len(result['ipv6'])} 个：")
        for index, address in enumerate(result["ipv6"], start=1):
            print(f"    {index}. {address}  [{utils.describe_ip(address)}]")
    else:
        utils.print_info("没有查询到 IPv6 地址（AAAA 记录），该域名可能未启用 IPv6。")

    utils.print_info("说明：一个域名对应多个 IP，通常是为了做负载均衡或多线接入。")
    utils.pause()


def run_reverse() -> None:
    """反向解析的交互流程。"""
    utils.print_title("DNS 反向解析（IP -> 域名）")
    print("示例：8.8.8.8、114.114.114.114")
    print()

    target = utils.ask("请输入要反查的 IP 地址（直接回车返回）：")
    if not target:
        utils.print_warn("没有输入内容，已返回上一级菜单。")
        return

    address = utils.normalize_target(target)
    if not utils.is_ip_address(address):
        utils.print_fail(f"“{address}”不是合法的 IP 地址，请重新输入。")
        utils.pause()
        return

    utils.print_info(f"正在反查 {address} 的域名（PTR 记录）...")

    try:
        hostname, aliases = reverse_lookup(address, DNS_TIMEOUT)
    except socket.herror as exc:
        utils.print_warn(f"没有查到 {address} 对应的域名。")
        utils.print_info(f"系统返回的错误信息：{exc}")
        utils.print_info("原因：该 IP 的所有者没有配置反向解析记录，这是很常见的情况。")
        utils.pause()
        return
    except socket.gaierror as exc:
        utils.print_fail(f"反查失败：{exc}")
        utils.pause()
        return

    print()
    utils.print_ok("反查成功")
    utils.print_kv("IP 地址", address)
    utils.print_kv("地址类型", utils.describe_ip(address))
    utils.print_kv("主机名", hostname)
    if aliases:
        utils.print_kv("别名", "、".join(aliases))
    utils.pause()


def run() -> None:
    """DNS 功能的二级菜单。"""
    while True:
        utils.print_title("DNS 域名解析")
        print("  1. 正向解析：域名 -> IP")
        print("  2. 反向解析：IP -> 域名")
        print("  0. 返回主菜单")
        utils.print_line()

        choice = utils.ask("请输入功能编号：")

        if choice == "1":
            run_forward()
        elif choice == "2":
            run_reverse()
        elif choice == "0" or choice == "":
            return
        else:
            utils.print_warn("输入无效，请输入 0、1 或 2。")
