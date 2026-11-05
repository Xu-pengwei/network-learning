# 计算机网络技术学习记录

你好，我是一名计算机网络技术专业的大学生。

这个仓库用于记录课程实验、配置过程、验证方法和故障排查经验。我会把课堂上完成的实验逐步整理成笔记，方便复习和展示学习成果。

## 学习方向

- Windows Server 2022
- DNS、DHCP 与域服务
- Linux 基础与网络配置
- IP 地址与子网划分
- 交换与路由基础
- Python 网络小工具

## 实验笔记

| 序号 | 实验内容 | 状态 |
|---|---|---|
| 01 | [Windows Server 2022 DNS 实验](notes/windows-server-dns.md) | 已完成 |
| 02 | [Windows 10 加入域与域账户登录](notes/windows10-domain-login.md) | 已完成 |
| 03 | [Python 网络工具箱](Python网络工具/README.md) | 已完成，持续完善 |
| 04 | [DHCP 服务器配置与验证](notes/windows-server-dhcp.md) | 已完成 |
| 05 | [Ubuntu 网络基础配置](notes/ubuntu-network-basics.md) | 已完成 |
| 06 | [Wireshark ICMP 抓包实验](notes/wireshark-icmp.md) | 已完成 |
| 07 | [Wireshark DNS 抓包分析](notes/wireshark-dns.md) | 已完成 |
| 08 | [Wireshark DHCP 抓包分析](notes/wireshark-dhcp.md) | 已完成：完整 DORA 抓包与网络验收通过 |

## 实验环境

- VMware 虚拟机
- Windows Server 2022
- Windows 10
- Ubuntu Linux

## 后期学习路线

后续学习将从“会配置网络”逐步过渡到“能观察数据包、解释协议过程并独立排查故障”。

| 阶段 | 计划内容 | 预期成果 | 状态 |
|---|---|---|---|
| 第一阶段 | Wireshark 基础与 ICMP 抓包 | 识别 Ping 请求和响应，查看源 IP、目标 IP 与 ICMP 类型 | 已完成 |
| 第二阶段 | DNS 抓包分析 | 观察 DNS 查询、响应、记录类型和解析结果 | 已完成 |
| 第三阶段 | DHCP 抓包分析 | 理解 Discover、Offer、Request、ACK 四个阶段 | 已完成 |
| 第四阶段 | TCP 三次握手与四次挥手 | 识别 SYN、ACK、FIN 和常见 TCP 标志位 | 待开始 |
| 第五阶段 | HTTP 与 HTTPS 基础分析 | 区分明文请求与 TLS 加密流量，理解常见端口 | 待开始 |
| 第六阶段 | IP 地址与子网划分练习 | 能够计算网络地址、广播地址和可用主机范围 | 待开始 |
| 第七阶段 | 交换与路由基础实验 | 理解 ARP、MAC 地址、网关和跨网段通信 | 待开始 |
| 第八阶段 | Linux 网络服务与防火墙 | 学习 SSH、端口监听、服务状态和 UFW 基础配置 | 待开始 |
| 第九阶段 | Python 网络工具完善 | 增加异常处理、参数输入、结果保存和自动化测试 | 持续完善 |
| 第十阶段 | 综合网络故障排查 | 综合使用 Windows Server、Ubuntu、Wireshark 和 Python 完成排错报告 | 待开始 |

## 近期实验安排

2026-11-05 已完成 [08 - Wireshark DHCP 抓包分析](notes/wireshark-dhcp.md)：在 Wireshark 中捕获同一次事务的 Discover、Offer、Request、ACK，核对地址、网关、DNS 与租约参数，并完成连通性和 DNS 解析验收。下一步进入 TCP 三次握手与四次挥手实验。

## 学习节奏

- 每次学习控制在 30～45 分钟。
- 每次完成“理论、操作、验证、练习、总结”五个环节。
- 每周至少整理两篇真实实验记录。
- 实验状态只根据实际操作结果更新。
- 每完成一个阶段，在 README 和对应实验文档中记录成果。

## 说明

仓库内容主要来自个人课程学习与实验实践。文档中涉及的域名、IP 地址和网络环境可能根据不同实验进行调整。
