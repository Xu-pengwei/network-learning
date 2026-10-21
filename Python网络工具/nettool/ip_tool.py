"""
IP 地址查询模块
=================
功能：
    1. 查看本机网络信息：主机名、本机 IPv4 / IPv6 地址，并判断是内网还是公网；
    2. 查询本机的公网出口 IP 及其归属地（国家、省市、运营商）；
    3. 查询指定 IP 或域名对应的归属地。

原理提示：
    家用电脑通常没有独立公网 IP，而是通过路由器的 NAT 技术共享一个公网 IP。
    所以"本机网卡地址"（多为 192.168.x.x）和"公网出口 IP"往往是两个不同的地址。

联网说明：
    归属地查询需要访问免费接口 ip-api.com，该接口免费版限制为每分钟 45 次，
    学习使用完全够用。程序统一设置了 5 秒超时，失败时会自动尝试备用接口。
"""

from __future__ import annotations

import ipaddress
import json
import socket
import urllib.error
import urllib.request

from . import utils

# ---------------------------------------------------------------- 接口配置
# {query} 会被替换成要查询的 IP 或域名，留空表示"查询本机公网 IP"
IP_API_URL = (
    "http://ip-api.com/json/{query}"
    "?lang=zh-CN"
    "&fields=status,message,query,country,regionName,city,isp,timezone"
)

# 备用接口列表：主接口失败时按顺序尝试，只要有一个成功就返回。
# 免费接口随时可能调整，所以这里准备多个来源，提高程序的可用性。
FALLBACK_URLS = (
    ("ip-api 简易接口", "http://ip-api.com/line/?fields=query"),
    ("ipify 接口", "http://api.ipify.org/?format=json"),
    ("icanhazip 接口", "http://icanhazip.com"),
)

# 访问网络接口的最长等待时间（秒）
HTTP_TIMEOUT = 5.0

# 用 UDP 连接一个外部地址来"探测"本机出口网卡地址。
# 注意：UDP 的 connect() 只设置默认目标，并不会真的发送数据包，
# 因此即使对方不可达也能立刻拿到本机网卡地址。
PROBE_TARGET = ("8.8.8.8", 80)


# ---------------------------------------------------------------- 本机信息
def get_primary_local_ip() -> str | None:
    """获取本机用于访问外网的那块网卡的 IPv4 地址，失败时返回 None。"""
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        probe.connect(PROBE_TARGET)
        return probe.getsockname()[0]
    except OSError:
        return None
    finally:
        probe.close()


def collect_addresses(host: str) -> tuple[list[str], list[str]]:
    """
    查询某个主机名对应的全部 IPv4 和 IPv6 地址，分别返回两个列表。
    """
    ipv4: list[str] = []
    ipv6: list[str] = []

    for family, bucket in ((socket.AF_INET, ipv4), (socket.AF_INET6, ipv6)):
        try:
            infos = socket.getaddrinfo(host, None, family, socket.SOCK_STREAM)
        except socket.gaierror:
            continue
        for info in infos:
            address = info[4][0].split("%")[0]
            if address not in bucket:
                bucket.append(address)

    return ipv4, ipv6


def get_local_info() -> dict:
    """
    汇总本机网络信息，返回字典：
        hostname —— 计算机名
        primary  —— 主要网卡 IPv4 地址
        ipv4/ipv6 —— 本机全部地址
        error    —— 出错说明，正常时为 None
    """
    try:
        hostname = socket.gethostname()
    except OSError as exc:
        return {"hostname": "", "primary": None, "ipv4": [], "ipv6": [],
                "error": f"获取计算机名失败：{exc}"}

    try:
        ipv4, ipv6 = collect_addresses(hostname)
    except OSError as exc:  # 理论上 collect_addresses 已忽略解析错误，这里做兜底
        return {"hostname": hostname, "primary": None, "ipv4": [], "ipv6": [],
                "error": f"查询本机地址失败：{exc}"}

    return {
        "hostname": hostname,
        "primary": get_primary_local_ip(),
        "ipv4": ipv4,
        "ipv6": ipv6,
        "error": None,
    }


# ---------------------------------------------------------------- 归属地查询
def query_ip_info(query: str | None = None) -> dict:
    """
    调用 ip-api.com 查询 IP 归属地。

    参数：
        query —— 要查询的 IP 或域名；传 None 表示查询本机公网出口 IP

    返回接口原始字典，查询成功时 status 字段为 "success"。
    网络异常、超时或接口返回失败时抛出异常，由调用者处理。
    """
    url = IP_API_URL.format(query=query or "")
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "PythonNetworkToolbox/1.0"},  # 有些接口要求带 UA
    )

    # urlopen 支持 with 语法，退出时会自动关闭连接
    with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT) as response:
        raw = response.read()

    data = json.loads(raw.decode("utf-8"))
    if data.get("status") != "success":
        raise RuntimeError(data.get("message") or "接口返回了失败状态")

    return data


def query_public_ip_simple() -> str:
    """
    备用方案：只获取公网 IP 地址，不查询归属地。

    依次尝试 FALLBACK_URLS 中的接口，任何一个成功就立即返回。
    全部失败时抛出 RuntimeError，并把每个接口的失败原因写进提示里。
    """
    errors: list[str] = []

    for name, url in FALLBACK_URLS:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "PythonNetworkToolbox/1.0"},
        )
        try:
            with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT) as response:
                body = response.read().decode("utf-8", errors="replace").strip()
        except Exception as exc:
            errors.append(f"{name}：{exc}")
            continue

        # 接口可能返回纯文本 IP，也可能返回 JSON，两种都要兼容
        if body.startswith("{"):
            try:
                body = json.loads(body).get("ip", "")
            except ValueError:
                body = ""
                
if body:
    try:
        return str(ipaddress.ip_address(body))
    except ValueError:
        errors.append(f"{name}：返回的内容不是合法 IP 地址")
        continue

errors.append(f"{name}：返回内容为空")        

    raise RuntimeError("；".join(errors) or "所有备用接口均不可用")

def print_ip_info(data: dict) -> None:
    """把归属地查询结果按统一格式输出。"""
    address = data.get("query", "")
    utils.print_kv("IP 地址", address or "未知")
    utils.print_kv("地址类型", utils.describe_ip(address))
    utils.print_kv("国家/地区", data.get("country") or "未知")
    utils.print_kv("省/直辖市", data.get("regionName") or "未知")
    utils.print_kv("城市", data.get("city") or "未知")
    utils.print_kv("运营商", data.get("isp") or "未知")
    utils.print_kv("时区", data.get("timezone") or "未知")


def _can_connect_error(exc: BaseException) -> bool:
    """
    判断异常是否属于"网络相关错误"。

    urllib 抛出的 URLError 包裹了 socket 超时、DNS 失败等多种情况，
    这里统一归为一类，方便给出同一条中文提示。
    """
    return isinstance(
        exc,
        (urllib.error.URLError, socket.timeout, TimeoutError, ConnectionError, OSError),
    )


# ---------------------------------------------------------------- 交互流程
def run_local_info() -> None:
    """显示本机网络信息。"""
    utils.print_title("本机 IP 信息")
    utils.print_info("正在读取本机网卡信息...")

    info = get_local_info()

    if info["error"]:
        utils.print_fail(info["error"])
        utils.pause()
        return

    print()
    utils.print_kv("计算机名", info["hostname"])
    if info["primary"]:
        utils.print_kv("主要网卡地址", info["primary"])
        utils.print_kv("地址类型", utils.describe_ip(info["primary"]))
    else:
        utils.print_warn("无法探测主要网卡地址，可能是本机没有连接任何网络。")

    if info["ipv4"]:
        utils.print_info(f"本机 IPv4 地址共 {len(info['ipv4'])} 个：")
        for index, address in enumerate(info["ipv4"], start=1):
            print(f"    {index}. {address}  [{utils.describe_ip(address)}]")
    else:
        utils.print_warn("没有找到本机 IPv4 地址。")

    if info["ipv6"]:
        utils.print_info(f"本机 IPv6 地址共 {len(info['ipv6'])} 个：")
        for index, address in enumerate(info["ipv6"], start=1):
            print(f"    {index}. {address}  [{utils.describe_ip(address)}]")
    else:
        utils.print_info("本机没有启用 IPv6，或未获取到 IPv6 地址。")

    print()
    utils.print_info("提示：192.168.x.x、10.x.x.x、172.16~31.x.x 都属于内网地址。")
    utils.pause()


def run_public_ip() -> None:
    """查询本机的公网出口 IP 及归属地。"""
    utils.print_title("公网 IP 与归属地查询")
    utils.print_info("正在连接查询接口，请稍候...")

    try:
        data = query_ip_info()
    except Exception as exc:  # 主接口失败时进入备用方案，因此这里需要捕获所有异常
        if _can_connect_error(exc):
            utils.print_fail(f"访问归属地接口失败：网络不可用或请求超时（{exc}）")
        else:
            utils.print_fail(f"归属地查询失败：{exc}")

        utils.print_info("正在尝试备用接口...")
        try:
            address = query_public_ip_simple()
        except Exception as backup_exc:
            utils.print_fail(f"备用接口同样失败：{backup_exc}")
            utils.print_info("请检查本机网络连接后重试。")
            utils.pause()
            return

        utils.print_ok("已通过备用接口获取公网 IP")
        print()
        utils.print_kv("公网 IP", address)
        utils.print_kv("地址类型", utils.describe_ip(address))
        utils.print_info("备用接口不提供归属地信息。")
        utils.pause()
        return

    print()
    utils.print_ok("查询成功")
    print_ip_info(data)
    utils.print_info("说明：这里显示的是路由器对外的公网 IP，不是本机网卡的内网地址。")
    utils.pause()


def run_query_target() -> None:
    """查询指定 IP 或域名的归属地。"""
    utils.print_title("指定 IP / 域名 归属地查询")
    print("示例：8.8.8.8、114.114.114.114、www.qq.com")
    print()

    target = utils.ask("请输入 IP 或域名（直接回车返回）：")
    if not target:
        utils.print_warn("没有输入内容，已返回上一级菜单。")
        return

    query = utils.normalize_target(target)
    if not utils.is_valid_target(query):
        utils.print_fail(f"“{query}”不是合法的 IP 或域名，请重新输入。")
        utils.pause()
        return

    utils.print_info(f"正在查询 {query}，请稍候...")

    try:
        data = query_ip_info(query)
    except Exception as exc:
        if _can_connect_error(exc):
            utils.print_fail(f"查询失败：网络不可用或请求超时（{exc}）")
        else:
            utils.print_fail(f"查询失败：{exc}")
        utils.print_info("如果输入的是内网地址，公共接口无法查询归属地，这是正常现象。")
        utils.pause()
        return

    print()
    utils.print_ok("查询成功")
    print_ip_info(data)
    utils.pause()


def run() -> None:
    """IP 查询功能的二级菜单。"""
    while True:
        utils.print_title("IP 地址查询")
        print("  1. 查看本机 IP 信息")
        print("  2. 查询本机公网 IP 及归属地")
        print("  3. 查询指定 IP / 域名 的归属地")
        print("  0. 返回主菜单")
        utils.print_line()

        choice = utils.ask("请输入功能编号：")

        if choice == "1":
            run_local_info()
        elif choice == "2":
            run_public_ip()
        elif choice == "3":
            run_query_target()
        elif choice == "0" or choice == "":
            return
        else:
            utils.print_warn("输入无效，请输入 0、1、2 或 3。")
