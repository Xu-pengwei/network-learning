# 实验 07：Wireshark DNS 抓包分析

实验日期：2026 年 11 月 3 日

## 实验目的

观察一次 DNS 查询和响应，识别查询名称、记录类型、事务标识和返回结果。

## 实验环境

- VMware：Windows Server 2022 与 Ubuntu
- Ubuntu 网卡：ens33；IPv4 地址：192.168.168.128/24
- 当前 DNS 服务器：192.168.168.10
- 抓包工具：Wireshark

## 操作过程

1. 启动 Windows Server 2022 和 Ubuntu，在 Ubuntu 中检查网络配置：

```bash
ip -br addr
resolvectl status ens33
```

2. 打开 Wireshark，选择 ens33 并开始捕获。
3. 在另一个终端直接向当前 DNS 服务器查询：

```bash
nslookup www.example.com 192.168.168.10
```

4. 查询结束后停止捕获，使用显示过滤器筛选：

```text
dns.qry.name == "www.example.com"
```

5. 展开 DNS 查询和响应，对照事务标识、查询类型及回答记录。抓包文件已保存于 Ubuntu 本地。

## 观察结果

终端显示查询获得 IPv4 和 IPv6 地址，并提示非权威应答。Wireshark 中重点分析了 AAAA 查询：

| 项目 | 查询：第 135 号包 | 响应：第 176 号包 |
| --- | --- | --- |
| 通信方向 | 192.168.168.128 → 192.168.168.10 | 192.168.168.10 → 192.168.168.128 |
| Transaction ID | 0x4c0f | 0x4c0f |
| 查询名称 | www.example.com | www.example.com |
| 类型 | AAAA | AAAA |
| 对应包 | Response In: 176 | Request In: 135 |

该查询使用 UDP，目标端口为 53。响应显示 No error，Answer RRs 为 2，返回以下 IPv6 地址：

- `2606:4700:10::ac42:93f3`
- `2606:4700:10::6814:179a`

Wireshark 显示这次查询到响应的间隔约 2.1265 秒。终端也显示了 IPv4 地址，但本次截图中详细分析的是 AAAA 查询与响应。公开域名的解析结果可能随时间变化。

## 总结

客户端向 DNS 服务器提出域名查询，服务器返回响应；可以结合通信双方、事务标识、查询名称和类型，将查询与响应配对。AAAA 记录用于 IPv6 地址查询，响应码和回答记录有助于判断这次查询结果。显示过滤器只改变当前显示，不删除原始捕获数据。

对于 IP 能访问而主机名访问失败的情况，可以先检查名称解析，同时核对解析出的地址和其他可能影响连接的因素。
