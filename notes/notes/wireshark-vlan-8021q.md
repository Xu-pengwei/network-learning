# 实验十四：Wireshark 802.1Q VLAN 标签抓包分析

## 一、实验基本信息

- **实验编号：** 实验十四
- **实验日期：** 2026-11-20
- **学习主题：** IEEE 802.1Q VLAN 标签分析
- **实验工具：** eNSP、Wireshark、华为 S5700 交换机
- **关联实验：** 实验十三——eNSP VLAN 划分与跨 VLAN 通信

## 二、实验目的

1. 理解 VLAN 的作用及 802.1Q 标签的基本原理。
2. 掌握 IEEE 802.1Q 标签的字段结构。
3. 使用 eNSP 抓包功能捕获交换机 Trunk 链路上的数据帧。
4. 使用 Wireshark 识别 VLAN ID。
5. 理解 Access 与 Trunk 端口在数据帧转发过程中的区别。

## 三、实验拓扑与环境

沿用实验十三的 VLAN 拓扑。

### 1. 交换机连接

- SW1 GE0/0/1 ↔ SW2 GE0/0/1：Trunk 链路
- SW1 GE0/0/2：Access，VLAN 10
- SW1 GE0/0/3：Access，VLAN 20
- SW2 GE0/0/2：Access，VLAN 10
- SW2 GE0/0/3：Access，VLAN 20

### 2. VLAN 与终端地址

| 终端 | VLAN | IP 地址 |
|---|---:|---|
| PC1 | 10 | 192.168.10.10/24 |
| PC2 | 20 | 192.168.20.10/24 |
| PC3 | 10 | 192.168.10.20/24 |
| PC4 | 20 | 192.168.20.20/24 |

### 3. 实验前配置检查

分别在 SW1 和 SW2 执行：

```text
display vlan
```

检查结果：

- 两台交换机均存在 VLAN 10 和 VLAN 20。
- GE0/0/1 在 VLAN 10、VLAN 20 中均显示 Tagged、UP。
- GE0/0/2 在 VLAN 10 中显示 Untagged、UP。
- GE0/0/3 在 VLAN 20 中显示 Untagged、UP。

两台交换机的 VLAN 配置均正常保留，Trunk 链路状态正常。

## 四、实验过程

### 1. 启动抓包

1. 启动 eNSP 中的 SW1、SW2。
2. 确认两台交换机的 VLAN 配置正常。
3. 在 SW1 与 SW2 之间的 GE0/0/1 链路上使用 eNSP 自带的数据抓包功能。
4. 使用 Wireshark 查看捕获的数据帧。

### 2. VLAN 10 数据帧抓包

在 PC1 上执行：

```text
ping 192.168.10.20
```

PC1 到 PC3 的通信成功。

在 Wireshark 显示过滤器中输入：

```wireshark
vlan
```

选择数据包并展开 `802.1Q Virtual LAN`，观察到：

```text
802.1Q Virtual LAN, PRI: 0, DEI: 0, ID: 10
Priority: Best Effort (default)
DEI: Ineligible
ID: 10
Type: IPv4 (0x0800)
```

分析：

- PRI（PCP）= 0：默认优先级 Best Effort。
- DEI = 0：未设置丢弃资格标记。
- ID（VID）= 10：数据帧属于 VLAN 10。
- Type = 0x0800：标签之后的原始以太网类型字段表示 IPv4。

### 3. VLAN 20 数据帧抓包

通过 PC2 到 PC4 的 VLAN 20 通信产生数据流量。

在 Wireshark 中继续使用过滤器：

```wireshark
vlan
```

选择新产生的数据包，展开 `802.1Q Virtual LAN`。

实际观察到：

```text
ID: 20
```

说明 Trunk 链路上也捕获到了 VLAN 20 的带标签数据帧。

## 五、802.1Q 标签结构

IEEE 802.1Q 标签长度为 4 字节，共 32 bit。

| 字段 | 长度 | 作用 |
|---|---:|---|
| TPID | 16 bit | 标识 VLAN 标签类型，常见值为 0x8100 |
| PCP | 3 bit | 数据帧优先级 |
| DEI | 1 bit | 丢弃资格指示 |
| VID | 12 bit | 标识 VLAN |

其中：

- TPID：Tag Protocol Identifier。
- PCP：Priority Code Point，优先级字段，范围为 0～7。
- DEI：Drop Eligible Indicator，用于指示数据帧在拥塞情况下是否具有较高的丢弃资格。
- VID：VLAN Identifier，用于区分 VLAN。

注意：本次抓包实际确认了 PCP、DEI、VID 和 IPv4 类型字段；TPID 的 0x8100 是协议知识，本次记录没有单独保存其抓包字段值。

## 六、Access 与 Trunk 的区别

| 对比项 | Access | Trunk |
|---|---|---|
| 常见连接对象 | 计算机等终端 | 交换机之间 |
| VLAN 承载 | 通常一个 VLAN | 可以承载多个 VLAN |
| 数据帧处理 | 通常向终端发送不带标签的帧 | 通过 802.1Q 标签区分 VLAN |
| 主要作用 | 连接终端 | 在交换设备之间传递多个 VLAN 的流量 |

### 数据帧转发过程

以 PC1 向 PC3 发送 VLAN 10 数据为例：

1. PC1 发送普通以太网数据帧。
2. SW1 的 Access 端口将数据帧归入 VLAN 10。
3. 数据帧经 Trunk 链路转发时携带 VLAN 10 的 802.1Q 标签。
4. SW2 根据标签识别 VLAN 10。
5. SW2 从对应的 Access 端口转发数据帧，通常以不带标签的形式发送给 PC3。

## 七、实验结果

| 验证项目 | 实际结果 | 状态 |
|---|---|---|
| SW1 VLAN 配置检查 | VLAN 10、20 正常 | 通过 |
| SW2 VLAN 配置检查 | VLAN 10、20 正常 | 通过 |
| Trunk 链路抓包 | 成功捕获数据帧 | 通过 |
| VLAN 10 标签识别 | VID = 10 | 通过 |
| VLAN 20 标签识别 | VID = 20 | 通过 |
| PCP 字段观察 | 0 | 通过 |
| DEI 字段观察 | 0 | 通过 |
| Access 与 Trunk 原理 | 已理解并完成问答 | 已学习 |

## 八、实验总结

本次实验在实验十三 VLAN 划分与跨 VLAN 通信的基础上，进一步使用 eNSP 和 Wireshark 对交换机之间的 Trunk 链路进行抓包分析。

通过实际捕获的数据帧，分别识别出了 VLAN 10 和 VLAN 20 的 802.1Q 标签，并观察了 PCP、DEI 和 VID 等字段。

本次实验加深了对 VLAN 标签结构、Trunk 链路和 Access 端口工作方式的理解，也掌握了使用 Wireshark 过滤和分析 VLAN 数据帧的基本方法。

**本次实验完成了 VLAN 10、VLAN 20 的标签识别，但没有单独抓取 Access 链路进行帧格式对比。**

## 九、后续学习方向

1. 进一步学习交换机 MAC 地址表及动态 MAC 地址学习。
2. 学习 STP 生成树协议，理解交换网络中的环路问题。
3. 继续学习静态路由和不同网段之间的通信。
4. 在后续综合实验中结合 VLAN、Trunk、VLANIF 和路由进行排错练习。
