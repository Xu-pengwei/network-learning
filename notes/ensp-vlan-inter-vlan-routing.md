# 实验十三：eNSP 华为交换机 VLAN 划分与跨 VLAN 通信

## 一、实验基本信息

- **实验编号：** 实验十三
- **实验名称：** eNSP 华为交换机 VLAN 划分与跨 VLAN 通信
- **实验环境：** eNSP
- **交换机型号：** Quidway S5700-28C-HI
- **VRP 版本：** VRP 5.110（S5700 V200R001C00）
- **实验日期：** 2026-11-19
- **实验状态：** 核心配置与通信验证已完成

## 二、实验目的

1. 理解 VLAN 的基本概念及其隔离广播域的作用。
2. 掌握华为交换机创建 VLAN 和配置 Access 端口的方法。
3. 掌握 Trunk 链路的配置方法，理解交换机之间如何传输多个 VLAN 的数据。
4. 掌握 VLANIF 三层接口的配置方法。
5. 实现不同 VLAN 之间的通信，理解三层交换机的跨 VLAN 路由原理。

## 三、实验拓扑

本实验使用两台华为 S5700 交换机和四台 PC，分别划分到 VLAN 10 和 VLAN 20。

### 设备连接关系

| 设备 | 接口 | 连接设备 | 接口 |
|---|---|---|---|
| SW1 | GE0/0/1 | SW2 | GE0/0/1 |
| SW1 | GE0/0/2 | PC1 | Ethernet |
| SW1 | GE0/0/3 | PC2 | Ethernet |
| SW2 | GE0/0/2 | PC3 | Ethernet |
| SW2 | GE0/0/3 | PC4 | Ethernet |

SW1 与 SW2 之间通过 GE0/0/1 互联，并配置为 Trunk 链路，允许 VLAN 10 和 VLAN 20 通过。

## 四、IP 地址与 VLAN 规划

| 设备 | VLAN | IP 地址 | 子网掩码 | 默认网关 |
|---|---|---|---|---|
| PC1 | VLAN 10 | 192.168.10.10 | 255.255.255.0 | 192.168.10.1 |
| PC2 | VLAN 20 | 192.168.20.10 | 255.255.255.0 | 192.168.20.1 |
| PC3 | VLAN 10 | 192.168.10.20 | 255.255.255.0 | 192.168.10.1 |
| PC4 | VLAN 20 | 192.168.20.20 | 255.255.255.0 | 192.168.20.1 |

VLAN 规划：

- VLAN 10：PC1、PC3，网段为 `192.168.10.0/24`。
- VLAN 20：PC2、PC4，网段为 `192.168.20.0/24`。

## 五、交换机配置

### 1. SW1 配置

创建 VLAN 10 和 VLAN 20：

```text
system-view
sysname SW1
vlan batch 10 20
```

配置 PC1 接口为 Access，加入 VLAN 10：

```text
interface GigabitEthernet 0/0/2
port link-type access
port default vlan 10
quit
```

配置 PC2 接口为 Access，加入 VLAN 20：

```text
interface GigabitEthernet 0/0/3
port link-type access
port default vlan 20
quit
```

配置 SW1 与 SW2 之间的 Trunk 链路：

```text
interface GigabitEthernet 0/0/1
port link-type trunk
port trunk allow-pass vlan 10 20
quit
```

配置 VLAN 10 的三层网关：

```text
interface Vlanif 10
ip address 192.168.10.1 24
```

配置 VLAN 20 的三层网关：

```text
interface Vlanif 20
ip address 192.168.20.1 24
```

### 2. SW2 配置

创建 VLAN 10 和 VLAN 20：

```text
system-view
sysname SW2
vlan batch 10 20
```

配置 PC3 接口为 Access，加入 VLAN 10：

```text
interface GigabitEthernet 0/0/2
port link-type access
port default vlan 10
quit
```

配置 PC4 接口为 Access，加入 VLAN 20：

```text
interface GigabitEthernet 0/0/3
port link-type access
port default vlan 20
quit
```

配置 SW2 与 SW1 之间的 Trunk 链路：

```text
interface GigabitEthernet 0/0/1
port link-type trunk
port trunk allow-pass vlan 10 20
quit
```

## 六、配置验证与保存

### 1. VLAN 验证

在 SW1 和 SW2 上执行：

```text
display vlan
```

验证结果：

- VLAN 10 的 Access 接口为 GE0/0/2。
- VLAN 20 的 Access 接口为 GE0/0/3。
- 两个 VLAN 均通过 GE0/0/1 的 Trunk 链路传输。

设备输出中对应接口状态显示为 U，表明相关接口处于 Up 状态。

### 2. VLANIF 验证

在 SW1 上执行：

```text
display ip interface brief
```

验证结果：

| 接口 | IP 地址 | 物理状态 | 协议状态 |
|---|---|---|---|
| Vlanif10 | 192.168.10.1/24 | UP | UP |
| Vlanif20 | 192.168.20.1/24 | UP | UP |

两个 VLANIF 接口均处于 UP/UP 状态。

### 3. 保存配置

SW1 和 SW2 分别执行：

```text
save
```

根据设备提示确认保存。

两台交换机最终均返回：

```text
Save the configuration successfully.
```

说明配置已经成功保存。

## 七、通信测试

本实验主要验证同 VLAN 跨交换机通信，以及不同 VLAN 之间的三层通信。

| 测试方向 | 目标 IP | 测试结果 |
|---|---|---|
| PC1 → PC3 | 192.168.10.20 | 成功 |
| PC2 → PC4 | 192.168.20.20 | 成功 |
| PC1 → PC2 | 192.168.20.10 | 成功 |
| PC2 → PC1 | 192.168.10.10 | 成功 |
| PC3 → PC4 | 192.168.20.20 | 成功 |

其中，PC1 → PC3 的一次重试测试获得以下结果：

```text
Packets: Sent = 5, Received = 5, Lost = 0 (0% loss)
```

说明该次测试数据包全部成功到达。

### 测试结果分析

1. PC1 与 PC3 同属于 VLAN 10，虽然连接在不同交换机上，但可以通过 Trunk 链路正常通信。
2. PC2 与 PC4 同属于 VLAN 20，也能够跨交换机正常通信。
3. PC1 与 PC2 分属不同 VLAN，但通过 SW1 上配置的 VLANIF 10 和 VLANIF 20 实现了跨 VLAN 通信。
4. PC2 与 PC1 的反向测试也成功，说明跨 VLAN 通信具有双向连通性。

## 八、实验过程中的问题与排错

### 1. VRP 命令输入问题

开始配置时，曾出现命令无法识别的情况。

原因是设备尚未进入系统视图，导致在用户视图中输入了系统视图下的配置命令。

解决方法：

```text
<Huawei>system-view
```

成功进入系统视图后，才能继续配置交换机名称、VLAN 和接口。

### 2. PC 终端选择错误

测试 PC2 与 PC4 通信时，曾误在 PC1 上执行目标为 `192.168.20.20` 的 ping 命令。

通过执行：

```text
ipconfig
```

核对当前 PC 的 IP 地址，确认当时所在终端是 PC1（192.168.10.10），随后切换至 PC2（192.168.20.10）重新测试，通信成功。

这次排错提醒我：执行网络测试前，应先确认当前终端、源 IP 和目标 IP，避免因测试设备选择错误而误判网络故障。

### 3. 配置保存提示

SW2 执行 `save` 时，第一次未按要求输入确认内容，设备提示需要先选择 YES 或 NO。

随后按照提示输入确认内容，最终保存成功。

## 九、实验原理总结

### 1. VLAN 的作用

VLAN（Virtual Local Area Network，虚拟局域网）可以在一台或多台交换机上对网络进行逻辑划分。

不同 VLAN 之间的二层广播域相互隔离，可以减少广播影响，提高网络管理的灵活性。

### 2. Access 与 Trunk 的区别

- **Access：** 通常连接普通终端，属于一个 VLAN。
- **Trunk：** 通常用于交换机之间的互联，可以同时承载多个 VLAN 的流量。

本实验中，连接 PC 的接口配置为 Access，SW1 与 SW2 之间的互联接口配置为 Trunk。

### 3. 802.1Q VLAN 标签

Trunk 链路通常使用 IEEE 802.1Q 标记区分不同 VLAN 的数据帧。

本实验虽然配置并验证了 Trunk 链路，但尚未使用 Wireshark 抓取并检查 802.1Q 数据帧，因此标签字段的实际抓包观察暂未完成。

### 4. VLANIF 与跨 VLAN 通信

不同 VLAN 默认不能直接进行二层通信。

本实验在 SW1 上创建 VLANIF 10 和 VLANIF 20，并分别配置：

- VLANIF 10：192.168.10.1/24
- VLANIF 20：192.168.20.1/24

PC 访问其他 VLAN 的网络时，将数据发送给默认网关，由交换机进行三层路由转发，从而实现不同 VLAN 之间的通信。

## 十、实验结论

本次实验完成了两台华为 S5700 交换机的 VLAN 划分、Access 接口配置、Trunk 链路配置，以及 VLANIF 三层接口配置。

通过五项通信测试，验证了同 VLAN 跨交换机通信和不同 VLAN 之间的双向通信均能够正常进行。

实验让我进一步理解了 VLAN 的广播域隔离原理、Trunk 链路的作用，以及 VLANIF 在跨 VLAN 通信中的作用。

**实验完成情况：**

- [x] 创建 VLAN 10 和 VLAN 20
- [x] 配置 Access 接口
- [x] 配置 Trunk 链路
- [x] 配置 VLANIF 三层网关
- [x] 验证 VLAN 和接口状态
- [x] 保存 SW1、SW2 配置
- [x] 完成五项通信测试
- [ ] Wireshark 抓取并验证 802.1Q VLAN 标签

**备注：** Wireshark 抓包项目尚未执行，不计入本次已完成的验证内容。
