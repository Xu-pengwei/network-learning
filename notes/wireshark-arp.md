# 实验 11：ARP 地址解析协议（Address Resolution Protocol）

## 实验基本信息

| 项目 | 内容 |
|---|---|
| 实验编号 | 11 |
| 实验日期 | 2026-11-18 |
| 实验名称 | ARP 地址解析协议 |
| 实验分类 | 网络协议分析 / 局域网通信 |
| 实验平台 | Windows |
| 实验工具 | Wireshark、PowerShell |
| 涉及协议 | ARP、IPv4、Ethernet |
| 实验状态 | 已完成 |
| 理论学习 | 已完成 |
| 抓包验证 | 已完成 |
| 知识掌握程度 | 基本掌握，需巩固 |

## 一、实验目的

1. 理解 ARP（地址解析协议）的基本作用。
2. 掌握 IPv4 地址与 MAC 地址之间的映射关系。
3. 理解 ARP Request（请求）和 ARP Reply（应答）的工作过程。
4. 学会使用 Wireshark 捕获和分析 ARP 报文。
5. 理解 ARP 缓存表的作用及其基本查看方法。

## 二、实验环境

- 操作系统：Windows
- 抓包工具：Wireshark
- 命令行工具：PowerShell
- 网络协议：IPv4、Ethernet、ARP

## 三、ARP 基本原理

ARP（Address Resolution Protocol，地址解析协议）主要用于将 IPv4 地址解析为对应的 MAC 地址。

在以太网通信中，设备通常使用 IP 地址确定通信目标，但在实际发送以太网帧时，需要知道下一跳设备的 MAC 地址。

因此，当设备需要向同一局域网中的某个 IPv4 地址发送数据，但不知道目标 MAC 地址时，就会通过 ARP 协议进行查询。

### 1. ARP 请求（Request）

当主机不知道目标 IP 地址对应的 MAC 地址时，会发送 ARP Request 报文。

主要特点：

- Opcode：1（Request）。
- 目标 MAC 地址：未知时通常填写 `00:00:00:00:00:00`。
- 以太网目的 MAC 地址：`ff:ff:ff:ff:ff:ff`（广播地址）。
- 同一广播域内的设备都可以收到该广播报文。

### 2. ARP 应答（Reply）

目标设备收到 ARP 请求后，会检查请求中的目标 IP 地址。

如果目标 IP 地址与自身 IP 地址一致，就会发送 ARP Reply 报文。

主要特点：

- Opcode：2（Reply）。
- 携带目标设备自己的 MAC 地址。
- 通常采用单播方式发送给 ARP 请求的发起者。

### 3. ARP 工作过程

1. 主机 A 需要向主机 B 发送数据。
2. 主机 A 检查本地 ARP 缓存表。
3. 如果缓存中没有对应记录，主机 A 广播 ARP Request。
4. 主机 B 收到请求后，确认目标 IP 地址是自己。
5. 主机 B 返回 ARP Reply。
6. 主机 A 获取主机 B 的 MAC 地址，并更新 ARP 缓存。
7. 主机 A 使用目标 MAC 地址封装以太网帧，发送数据。

**注意：** 如果通信目标不在本地子网，主机通常需要解析默认网关的 MAC 地址，而不是远程目标主机的 MAC 地址。

## 四、Wireshark 抓包分析

### 1. 抓包准备

1. 打开 Wireshark。
2. 选择当前正在使用的网络接口。
3. 开始抓包。
4. 通过网络通信触发 ARP 查询。
5. 使用显示过滤器筛选 ARP 报文。

显示过滤器：

```text
arp
```

该过滤器用于显示 ARP 协议报文。

### 2. ARP Request 报文分析

在 ARP 请求报文中，重点关注以下字段：

| 字段 | 含义 |
|---|---|
| Hardware type | 硬件类型，Ethernet 为 1 |
| Protocol type | 协议类型，IPv4 为 0x0800 |
| Hardware size | MAC 地址长度，6 字节 |
| Protocol size | IPv4 地址长度，4 字节 |
| Opcode | 操作码，Request 为 1 |
| Sender MAC address | 发送方 MAC 地址 |
| Sender IP address | 发送方 IP 地址 |
| Target MAC address | 目标 MAC 地址 |
| Target IP address | 目标 IP 地址 |

实验中观察到的 ARP Request 报文信息：

| 字段 | 实际抓包结果 |
|---|---|
| Hardware type | Ethernet (1) |
| Protocol type | IPv4 (0x0800) |
| Hardware size | 6 |
| Protocol size | 4 |
| Opcode | request (1) |
| Sender MAC address | 46:7b:2b:d9:1f:4a |
| Sender IP address | 10.15.228.239 |
| Target MAC address | 00:00:00:00:00:00 |
| Target IP address | 实际抓包中显示的目标 IPv4 地址 |

**分析：**

ARP Request 用于查询目标 IPv4 地址对应的 MAC 地址。

由于发送方尚不知道目标设备的 MAC 地址，因此 ARP 报文中的 Target MAC address 通常为全零。

### 3. ARP Reply 报文分析

ARP Reply 的 Opcode 为 2，表示应答。

目标设备收到 ARP Request 后，如果发现请求中的 Target IP address 与自身 IP 地址一致，就会返回 ARP Reply。

应答报文会携带目标设备的 MAC 地址，使请求方能够完成 IP 地址到 MAC 地址的解析。

**分析重点：**

- Opcode 是否为 2。
- Sender MAC address 是否为应答设备的 MAC 地址。
- Sender IP address 是否为被查询的 IP 地址。
- Target IP address 是否为原请求发起方的 IP 地址。

## 五、ARP 缓存表查看

### 1. 查看 ARP 缓存表

在 Windows PowerShell 或 CMD 中执行：

```powershell
arp -a
```

该命令用于查看本机 ARP 缓存表。

实验中观察到的部分记录：

| Internet 地址 | 物理地址 | 类型 |
|---|---|---|
| 10.15.228.239 | 46-7b-2b-d9-1f-4a | 动态 |
| 10.15.228.255 | ff-ff-ff-ff-ff-ff | 动态 |

### 2. ARP 缓存表字段说明

- Internet 地址：设备的 IPv4 地址。
- 物理地址：与 IPv4 地址对应的 MAC 地址。
- 类型：映射记录的类型，例如动态或静态。

ARP 缓存表用于保存 IP 地址与 MAC 地址之间的映射关系，减少重复进行 ARP 查询的次数，提高局域网通信效率。

**补充说明：**

ARP 缓存表中的记录不一定都是普通主机的单播映射。对于广播地址、特殊地址等记录，需要结合具体网络环境判断，不能仅凭一条记录推断设备身份。

### 3. 常用命令

```powershell
# 查看 ARP 缓存表
arp -a

# 查看 ARP 命令帮助
arp -?
```

## 六、实验知识总结

通过本次实验，掌握了以下知识：

1. ARP 的主要作用是实现 IPv4 地址到 MAC 地址的解析。
2. ARP Request 使用广播方式发送。
3. ARP Reply 通常使用单播方式返回。
4. ARP Request 的 Opcode 为 1，ARP Reply 的 Opcode 为 2。
5. ARP 缓存表保存 IP 地址与 MAC 地址之间的映射关系。
6. Windows 可以使用 `arp -a` 查看本机 ARP 缓存表。
7. 当通信目标不在本地子网时，通常需要解析默认网关的 MAC 地址。

## 七、实验总结

通过本次实验，我了解了 ARP 协议的基本作用，掌握了 IPv4 地址与 MAC 地址之间的解析关系。

通过 Wireshark 抓包，我认识了 ARP Request 和 ARP Reply 报文，并了解了 Opcode、Sender MAC Address、Sender IP Address、Target MAC Address 和 Target IP Address 等重要字段的含义。

同时，通过 `arp -a` 命令查看了本机 ARP 缓存表，进一步理解了 ARP 缓存保存 IP 地址与 MAC 地址映射关系的作用。

本次实验让我认识到，ARP 是 IPv4 网络中实现局域网通信的重要基础协议，也是后续学习交换机转发、局域网通信和网络故障排查的重要基础。

## 八、实验完成情况

| 检查项目 | 完成情况 |
|---|---|
| ARP 基本原理学习 | 已完成 |
| ARP Request 报文分析 | 已完成 |
| ARP Reply 原理学习 | 已完成 |
| Wireshark 抓包 | 已完成 |
| ARP 报文字段识别 | 已完成 |
| ARP 缓存表查看 | 已完成 |
| 实验笔记整理 | 已完成 |

### 学习状态

- 理论学习：已完成
- 实践验证：已完成
- 知识掌握：基本掌握
- 后续巩固：进一步熟悉 ARP 请求与应答过程，以及本地通信和跨网段通信时的 MAC 地址解析区别。
