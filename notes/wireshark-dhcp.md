# 实验 08：DHCP 动态地址分配与 Wireshark 抓包

实验日期：2026-11-04～2026-11-05  
最后更新：2026-11-05  
记录 ID：LAB-2026-11-04-DHCP  
来源：本次实验实际操作、终端输出与 Wireshark 抓包结果。

## 实验目的与状态

观察 DHCP 地址分配报文，理解 Discover、Offer、Request、ACK（DORA）四个阶段；对照客户端实际配置，并验证网络连通性和 DNS 解析。

2026-11-04 首次实验只捕获到 Request 和 ACK。2026-11-05 使用新的临时 NetworkManager 连接重新触发初始地址获取，成功捕获完整 DORA。四个报文的事务 ID 均为 `0x61e5a867`，确认属于同一次交换。**实验已完成。**

## 实验环境

- VMware 中的 Ubuntu，网卡 `ens33`
- Ubuntu IPv4：`192.168.168.128/24`
- DHCP/DNS 服务器：`192.168.168.10`
- 默认网关：`192.168.168.2`
- 域名：`srv01.lab.test`
- 工具：Wireshark、NetworkManager（nmcli）、ip、ping、resolvectl
- 相关记录：[DHCP 服务器实验](windows-server-dhcp.md)、[Ubuntu 网络基础](ubuntu-network-basics.md)

## 实验过程

1. 确认活动连接为 `netplan-ens33`，网卡为 `ens33`。
2. 在 Wireshark 中选择 `ens33` 开始抓包，使用显示过滤器 `dhcp || bootp`。
3. 首次重新连接时只捕获到 Request/ACK，说明客户端仍在利用已有租约信息尝试恢复地址。
4. 新建不自动连接的临时 DHCP 连接：

```bash
sudo nmcli connection add type ethernet ifname ens33 con-name dora-test ipv4.method auto ipv6.method disabled connection.autoconnect no
```

5. 开始新的抓包后激活临时连接：

```bash
sudo nmcli connection up dora-test
```

6. 在 Wireshark 中捕获到连续的 Discover、Offer、Request、ACK，并逐个核对事务 ID。
7. 将抓包保存为 `2026-11-05-dhcp-dora.pcapng`，保存在 Ubuntu 的 Documents 目录。
8. 恢复原连接并删除临时连接：

```bash
sudo nmcli connection up netplan-ens33
sudo nmcli connection delete dora-test
nmcli connection show
```

9. 使用以下命令进行最终验收：

```bash
ip -br addr show ens33
ip route
ping -c 4 192.168.168.10
resolvectl query srv01.lab.test
```

## 完整 DORA 抓包结果

| 包号 | 报文 | 源地址 | 目标地址 | 作用 |
|---|---|---|---|---|
| 85 | DHCP Discover | `0.0.0.0` | `255.255.255.255` | 客户端广播寻找 DHCP 服务器 |
| 86 | DHCP Offer | `192.168.168.10` | `255.255.255.255` | 服务器提供可用地址和配置 |
| 87 | DHCP Request | `0.0.0.0` | `255.255.255.255` | 客户端广播请求采用该地址 |
| 88 | DHCP ACK | `192.168.168.10` | `255.255.255.255` | 服务器确认租约并下发配置 |

四个报文的 Transaction ID 均为 `0x61e5a867`，时间顺序连续，因此可确认属于同一次 DHCP 地址分配过程。

## DHCP 参数与验证结果

| 证据/项目 | 实际结果 |
|---|---|
| 分配的 IPv4 地址 | `192.168.168.128/24` |
| 子网掩码 | `255.255.255.0` |
| 默认网关 | `192.168.168.2` |
| DHCP 服务器 | `192.168.168.10` |
| DNS 服务器 | `192.168.168.10` |
| 租约时间 | 8 天（691200 秒） |
| T1 续租时间 | 4 天（345600 秒） |
| T2 重新绑定时间 | 7 天（604800 秒） |
| 网卡状态 | `ens33 UP` |
| 路由 | 默认路由经 `192.168.168.2` |
| Ping 服务器 | 4 发 4 收，丢包率 0% |
| DNS 查询 | `srv01.lab.test → 192.168.168.10` |
| 临时连接 | `dora-test` 已删除 |
| 原连接 | `netplan-ens33` 已恢复 |

## 问题与排查

### 为什么第一次只有 Request 和 ACK？

客户端原本已有可用租约信息。普通的断开再连接可能进入租约恢复或续租相关状态，客户端会直接请求原地址，因此不一定重新经历 Discover 和 Offer。

本次通过创建新的临时 NetworkManager 连接，使客户端以新的连接配置重新获取地址，从而捕获完整 DORA。实验结束后恢复原连接并删除临时连接，没有改变长期网络配置。

## 知识点总结

- DORA 表示 Discover、Offer、Request、ACK。
- DHCP 客户端尚未获得地址时使用 `0.0.0.0`，并通过广播寻找服务器。
- Offer 是服务器的提议，真正确认租约需要看到 ACK。
- Transaction ID 用于关联同一次 DHCP 交换中的多个报文。
- DHCP 不仅分配 IP，还可下发掩码、网关、DNS 和租约参数。
- DHCP 使用 UDP：服务器端口 67，客户端端口 68。
- T1 是客户端优先向原服务器续租的时间点；T2 是未续租成功后尝试向任意服务器重新绑定的时间点。
- 仅看到 Request/ACK 不代表抓包失败，但不能据此宣称已观察到完整 DORA。

## 截图与原始证据

完整抓包已保存为 `2026-11-05-dhcp-dora.pcapng`。仓库暂不上传截图和 PCAP，避免公开 MAC 地址、客户端标识及无关网络流量；文档仅记录经过核对的实验结果。

## 复习题

1. DORA 四种报文分别由谁发送，各有什么作用？
2. 为什么 Discover 的源地址是 `0.0.0.0`？
3. 如何使用 Transaction ID 判断四个报文属于同一次交换？
4. Offer 与 ACK 在地址分配中的作用有什么不同？
5. 为什么已有租约时可能只捕获到 Request 和 ACK？
6. 本次 DHCP 服务器、网关和 DNS 分别是什么地址？
7. T1、T2 与租约到期有什么区别？

## 实验结论

Ubuntu 客户端已成功完成 DHCP 地址获取，Wireshark 捕获到包号 85～88 的完整 DORA 四步报文，四个报文事务 ID 相同。客户端最终获得 `192.168.168.128/24`，网关为 `192.168.168.2`，DNS 与 DHCP 服务器均为 `192.168.168.10`。最终连通性、路由和 DNS 解析验收全部通过，临时连接已清理，原网络连接已恢复。
