# 实验 08：DHCP 动态地址分配与 Wireshark 抓包

实验日期：2026-11-04  
最后更新：2026-11-04  
记录 ID：LAB-2026-11-04-DHCP  
来源：用户提供的本次实验结果；关联课程“继续DHCP课程”。

## 实验目的与状态

观察 DHCP 地址分配报文，对照客户端实际配置，并验证当前 DNS 与域名解析。

本次已完成 Request、ACK 抓包及客户端参数核对。**未捕获 Discover 和 Offer，完整 DORA 四步抓包尚未完成。** 实验进度为进行中；以下成功结果按用户提供的实测信息记录，本次整理未重新操作虚拟机，也未独立复核原始抓包。理论掌握程度待复习题评估。

## 实验环境

- VMware 中的 Ubuntu，网卡 `ens33`，使用 DHCP 自动获取 IPv4 配置。
- DHCP 服务器：`192.168.168.10`；相关配置背景见 [DHCP 服务器实验](windows-server-dhcp.md)。
- 客户端配置背景见 [Ubuntu 网络基础](ubuntu-network-basics.md)。
- 工具：Wireshark、nmcli、resolvectl；本次未提供软件版本。

## 实验过程

1. 在 Ubuntu 的 ens33 上使用 DHCP 自动获取配置。
2. 使用 Wireshark 捕获并检查 DHCP Request 与 DHCP ACK，查看 Requested IP 和服务器信息，以及 ACK 的各项配置选项。
3. 使用 nmcli 对照客户端实际地址、网关和 DNS；三项均与抓包一致。
4. 执行 `resolvectl status ens33`，确认当前 DNS 服务器。
5. 执行 `resolvectl query www.baidu.com`，测试域名解析。

以下为后续复核可使用的 nmcli 命令，原始命令全文未提供，不作为本次终端输出转录：

```bash
nmcli -f GENERAL.DEVICE,IP4.ADDRESS,IP4.GATEWAY,IP4.DNS device show ens33
```

未记录本次触发 DHCP 请求的具体操作，不补写释放租约、重启连接等未确认步骤。

## 抓包与验证结果

| 证据/项目 | 实际结果 |
| --- | --- |
| DHCP Request | Requested IP：`192.168.168.128` |
| DHCP ACK | 服务器：`192.168.168.10` |
| ACK 子网掩码 | `255.255.255.0`（/24） |
| ACK 默认网关 | `192.168.168.2` |
| ACK DNS | `192.168.168.10` |
| ACK 租约 | 8 天（691200 秒） |
| ACK T1 | 4 天（345600 秒） |
| ACK T2 | 7 天（604800 秒） |
| nmcli 地址 | `192.168.168.128/24`，与抓包一致 |
| nmcli 网关 | `192.168.168.2`，与抓包一致 |
| nmcli DNS | `192.168.168.10`，与抓包一致 |
| resolvectl status ens33 | 当前 DNS 服务器为 `192.168.168.10` |
| resolvectl query www.baidu.com | 成功返回 IPv4 和 IPv6；未提供具体地址，不补写 |
| Discover / Offer | 未捕获；不能标记完整 DORA 已完成 |

这些结果支持 DHCP 参数已应用到客户端，以及本次域名解析成功；返回 IPv6 地址不等于已验证 IPv6 网络连通性，也不代表 DHCPv4 分配了 IPv6 地址。

## 知识点

- DORA 指 Discover（发现）、Offer（提供）、Request（请求）、ACK（确认）。本次直接观察到的只有后两类报文。
- Request 中的 Requested IP 表示客户端请求的地址，不能仅凭该字段确认服务器已分配；需要结合 ACK 和客户端实际配置判断。
- DHCP 不仅分配地址，还可下发掩码、网关、DNS 与租约参数。服务器地址与网关地址不必相同。
- T1 是开始尝试续租的时间点；T2 是进入重新绑定阶段的时间点。本次分别为租期的 50% 和 87.5%。这些时间值来自本次 ACK，未实际等待 4 天或 7 天验证续租行为。
- 只见 Request/ACK 可能与已有租约、客户端状态或捕获时机有关；缺少完整报文与触发过程，不能确定本次缺失前两步的原因。
- `resolvectl status ens33` 检查接口当前 DNS；`resolvectl query` 检查名称解析结果，两者应结合检查。

## 截图与原始证据

仓库现有记录没有图片目录，已有 DHCP 实验采用文字记录结果、暂不上传原始截图的方式。本次沿用该方式。

当前仓库未包含今天的截图或 PCAP，本次输入也未附原始文件，因此没有创建图片链接或声称已复核截图。上述结果来自用户提供的实测信息。

后续补充证据清单：Request 的 Requested IP、ACK 的服务器及全部租约选项、nmcli 配置、resolvectl 状态与解析结果。保留原始证据，公开副本按需遮盖 MAC、主机标识及无关流量；本次没有上传抓包文件。

## 遗留任务

- [ ] 在独立实验环境中先开始捕获，再触发一次初始地址获取，补齐 Discover、Offer、Request、ACK。
- [ ] 对照事务 ID、客户端标识和时间顺序，确认四类报文属于同一次交换。
- [ ] 记录实际触发操作、软件版本、包号及报文细节，判断本次 Request/ACK 所处的客户端状态。
- [ ] 补充脱敏截图或证据引用；完成后再更新完整 DORA 状态。

以上是后续计划，本次未执行。

## 复习题

1. DORA 四种报文分别由谁发送，作用是什么？
2. 为什么 Request 中出现 Requested IP 不能单独证明地址分配成功？
3. 本次服务器、网关、DNS 各是什么地址？各自负责什么？
4. T1、T2 与租约到期的区别是什么？本次各是多少天？
5. 为什么只看到 Request 和 ACK 不能宣称完整 DORA 抓包完成？
6. nmcli 与 resolvectl 分别帮助核对什么？解析出 IPv6 是否证明 IPv6 可达？

## 实验结论

按用户提供的实际结果，Ubuntu ens33 已通过 DHCP 获取配置；Request/ACK、nmcli 参数及当前 DNS 检查相互一致，www.baidu.com 的 IPv4/IPv6 解析成功。完整 DORA 抓包仍待补齐 Discover 和 Offer。
