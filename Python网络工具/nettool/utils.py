"""
公共工具模块
==============
把"输入校验""结果输出""暂停等待"这些在三个功能里反复出现的小功能集中到
一个文件中，避免重复写代码。

设计思路：
    1. 校验函数只负责"判断对错"，不负责打印，方便被测试代码直接调用；
    2. 输出函数统一格式，保证整个程序界面风格一致；
    3. 所有用户可见文字都使用中文，方便课堂阅读。
"""

from __future__ import annotations

import ipaddress
import re
import unicodedata

# ---------------------------------------------------------------- 界面常量
LINE_CHAR = "-"     # 分隔线使用的字符
LINE_WIDTH = 50     # 分隔线长度

# 主机名（域名）中"一段"的合法写法：
# 以字母或数字开头和结尾，中间允许出现连字符，长度 1~63 个字符。
_LABEL_PATTERN = re.compile(r"^[A-Za-z0-9]([A-Za-z0-9-]{0,61}[A-Za-z0-9])?$")


# ---------------------------------------------------------------- 界面输出
def print_line(char: str = LINE_CHAR, width: int = LINE_WIDTH) -> None:
    """打印一条分隔线，用于划分界面区域。"""
    print(char * width)


def print_title(title: str, width: int = LINE_WIDTH) -> None:
    """打印带上下分隔线的标题，例如：

    ----------------------------------------
      DNS 域名解析
    ----------------------------------------
    """
    print()
    print_line("-", width)
    print(f"  {title}")
    print_line("-", width)


def print_ok(message: str) -> None:
    """打印"成功"信息。用文字前缀代替颜色，避免 Windows 终端乱码。"""
    print(f"[成功] {message}")


def print_fail(message: str) -> None:
    """打印"失败"信息。"""
    print(f"[失败] {message}")


def print_warn(message: str) -> None:
    """打印"警告"信息，例如网络连通但有丢包。"""
    print(f"[警告] {message}")


def print_info(message: str) -> None:
    """打印"提示"信息，例如操作说明、正在查询等。"""
    print(f"[提示] {message}")


def _display_width(text: str) -> int:
    """
    计算字符串在终端里占用的显示宽度。

    中文、全角符号在终端中占 2 列，英文和半角符号占 1 列。
    只有按显示宽度补齐，中文标签才能对齐，所以需要 unicodedata 帮忙判断。
    """
    width = 0
    for char in text:
        # W = 宽字符（如汉字），F = 全角字符（如"，"）
        width += 2 if unicodedata.east_asian_width(char) in ("W", "F") else 1
    return width


def print_kv(label: str, value: object, label_width: int = 14) -> None:
    """按"标签：值"的格式输出一行信息，并保证冒号对齐。"""
    padding = max(0, label_width - _display_width(label))
    print(f"  {label}{' ' * padding}：{value}")


# ---------------------------------------------------------------- 输入处理
def ask(prompt: str) -> str:
    """
    读取一行用户输入，并去掉首尾空白。

    如果用户按下 Ctrl+C 或输入流结束（例如通过管道运行），
    返回空字符串，由调用者决定如何提示，避免程序直接崩溃。
    """
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return ""


def pause(prompt: str = "按回车键返回上一级菜单...") -> None:
    """暂停程序，等待用户按回车，让用户有时间看完输出结果。"""
    ask("\n" + prompt)


# ---------------------------------------------------------------- 地址校验
def normalize_target(text: str) -> str:
    """
    把用户输入的地址整理成标准形式。

    支持用户直接粘贴浏览器地址，例如：
        https://www.baidu.com/s?wd=python  ->  www.baidu.com
        [::1]                              ->  ::1
        example.com:8080                   ->  example.com
    这样初学者不用关心格式细节。
    """
    text = (text or "").strip()
    if not text:
        return ""

    # 去掉 http:// 或 https:// 前缀
    lowered = text.lower()
    for prefix in ("http://", "https://"):
        if lowered.startswith(prefix):
            text = text[len(prefix):]
            break

    # 去掉路径、查询参数和锚点
    for separator in ("/", "?", "#"):
        if separator in text:
            text = text.split(separator, 1)[0]

    # IPv6 的方括号写法：[::1] 或 [::1]:80
    if text.startswith("["):
        end = text.find("]")
        if end != -1:
            return text[1:end].strip()

    # 去掉端口号，只处理"只有一个冒号"的情况，避免误伤 IPv6 地址
    if text.count(":") == 1:
        host, _, port = text.partition(":")
        if port.isdigit():
            text = host

    return text.strip()


def is_ip_address(text: str) -> bool:
    """判断字符串是否是合法的 IPv4 或 IPv6 地址。"""
    try:
        ipaddress.ip_address(text)
        return True
    except ValueError:
        return False


def is_valid_hostname(text: str) -> bool:
    """
    判断字符串是否是合法的主机名/域名。

    规则简化如下：
        1. 总长度不超过 253 个字符；
        2. 用"."分成若干段，每段 1~63 个字符；
        3. 每段只能包含字母、数字和连字符，且不能以连字符开头或结尾。
    """
    if not text or len(text) > 253:
        return False

    # 允许末尾带一个点（完全限定域名的写法，如 www.example.com.）
    if text.endswith("."):
        text = text[:-1]
    if not text:
        return False

    return all(_LABEL_PATTERN.match(label) for label in text.split("."))


def is_valid_target(text: str) -> bool:
    """判断用户输入的目标是否可用：合法 IP 或合法域名都可以。"""
    return is_ip_address(text) or is_valid_hostname(text)


def describe_ip(text: str) -> str:
    """
    判断 IP 地址的类型，返回中文说明。

    这是理解"内网 / 公网"概念的关键函数，ipaddress 模块已经帮我们判断好了。
    """
    try:
        ip = ipaddress.ip_address(text)
    except ValueError:
        return "无法识别的地址"

    if ip.is_loopback:
        return "回环地址（指向本机）"
    if ip.is_link_local:
        return "链路本地地址（局域网内部自动配置）"
    if ip.is_private:
        return "内网（私有）地址"
    if ip.is_multicast:
        return "组播地址"
    if ip.is_unspecified:
        return "未指定地址"
    return "公网地址"
