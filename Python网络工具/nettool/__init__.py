"""
nettool 包
============
网络工具箱的核心功能包，按功能拆分为三个模块：

    ping_tool.py  —— Ping 网络连通性检测
    ip_tool.py    —— IP 地址查询（本机信息、公网 IP、归属地）
    dns_tool.py   —— DNS 域名解析（正向解析、反向解析）

公共的输入校验与输出格式放在 utils.py 中，供上面三个模块复用。
"""

__version__ = "1.0.0"
