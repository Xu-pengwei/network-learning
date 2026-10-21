"""
网络工具箱 —— 程序入口
========================
本文件负责显示主菜单，并根据用户输入调用对应的功能模块。

运行方式：
    在项目根目录打开终端，执行：
        python main.py

模块分工：
    nettool/ping_tool.py  —— Ping 网络连通性检测
    nettool/ip_tool.py    —— IP 地址查询
    nettool/dns_tool.py   —— DNS 域名解析
"""

from __future__ import annotations

import sys

from nettool import dns_tool, ip_tool, ping_tool, utils

# 菜单项与对应的处理函数，集中放在这里，方便以后增加新功能
MENU_ITEMS = {
    "1": ("Ping 网络连通性检测", ping_tool.run),
    "2": ("IP 地址查询", ip_tool.run),
    "3": ("DNS 域名解析", dns_tool.run),
}


def show_welcome() -> None:
    """显示程序欢迎界面。"""
    utils.print_line("=")
    print("            网络工具箱  v1.0")
    print("     计算机网络技术专业 · Python 实训项目")
    utils.print_line("=")
    print("  本程序包含三个网络诊断功能，全部使用中文界面。")
    print("  运行环境：Python 3.8+（标准库，无需安装第三方包）")


def show_menu() -> None:
    """显示主菜单。"""
    print()
    utils.print_line()
    for key, (name, _function) in MENU_ITEMS.items():
        print(f"  {key}. {name}")
    print("  0. 退出程序")
    utils.print_line()


def main() -> int:
    """主循环：显示菜单 -> 读取输入 -> 调用功能，直到用户选择退出。"""
    show_welcome()

    while True:
        show_menu()
        choice = utils.ask("请输入功能编号：")

        # 直接回车视为退出，方便快速关闭程序
        if choice in ("0", "") or choice.lower() == "q":
            print()
            print("感谢使用网络工具箱，再见！")
            return 0

        item = MENU_ITEMS.get(choice)
        if item is None:
            utils.print_warn(f"没有编号为“{choice}”的功能，请输入 0~{len(MENU_ITEMS)}。")
            continue

        name, handler = item
        try:
            handler()
        except KeyboardInterrupt:
            # 在功能内部按 Ctrl+C 时，回到主菜单而不是直接退出程序
            print()
            utils.print_warn(f"已中断“{name}”功能，返回主菜单。")
        except Exception as exc:  # 兜底：任何意外错误都不让程序崩溃
            print()
            utils.print_fail(f"功能执行出错：{exc}")
            utils.print_info("这通常是网络异常或系统环境问题，可以换一个目标重新尝试。")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        # 在菜单等待输入时按 Ctrl+C
        print()
        print("程序已被用户中断，再见！")
        sys.exit(0)
    except EOFError:
        # 通过管道运行且输入结束时，安静退出即可
        print()
        sys.exit(0)
