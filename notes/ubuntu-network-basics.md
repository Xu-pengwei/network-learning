# Ubuntu 网络基础配置与故障排查

## 一、实验目的

1. 熟悉 Ubuntu 中查看系统、网卡、IP 地址、路由和 DNS 的常用命令。
2. 验证 Ubuntu 通过 Windows Server DHCP 自动获取网络配置。
3. 测试 Ubuntu 与服务器、外网以及 DNS 解析的连通性。
4. 掌握“网卡无 IPv4 地址”问题的基本排查方法。
5. 安装 VMware Tools，恢复主机与虚拟机之间的复制粘贴功能。

## 二、实验环境

| 项目 | 实际配置 |
|---|---|
| 操作系统 | Ubuntu 26.04.1 LTS（Resolute） |
| 内核版本 | Linux 7.0.0-38-generic |
| 虚拟化软件 | VMware |
| 主机名 | `student-VMware-Virtual-Platform` |
| 网卡名称 | `ens33` |
| NetworkManager 连接 | `netplan-ens33` |
| IPv4 地址 | `192.168.168.128/24`（DHCP 动态获取） |
| 所属网段 | `192.168.168.0/24` |
| 默认网关 | `192.168.168.2` |
| DHCP 服务器 | `192.168.168.10` |
| DNS 服务器 | `192.168.168.10` |
| 实验域名 | `lab.test` |
| Windows Server 主机 | `srv01.lab.test` / `192.168.168.10` |

> IP 地址由 DHCP 动态分配，后续重新获取租约时可能发生变化。

## 三、查看系统信息

执行：

```bash
lsb_release -a
hostnamectl
```

验证结果：

- Ubuntu 版本为 26.04.1 LTS。
- 系统代号为 `resolute`。
- 虚拟化环境识别为 VMware。
- 系统架构为 x86-64。

## 四、检查网卡状态

执行：

```bash
ip addr
ip route
nmcli device status
```

最初的检查结果：

- `ens33` 状态为 `UP`。
- 网卡只有 IPv6 链路本地地址，没有 IPv4 地址。
- `ip route` 没有输出默认路由。
- NetworkManager 显示正在获取 IP 配置，随后提示网络连接激活失败。

这说明虚拟网卡已经启用，但没有从 DHCP 服务器获得 IPv4 配置。

## 五、故障原因与处理过程

### 1. 故障原因

检查实验环境后发现，提供 DHCP 服务的 Windows Server 2022 虚拟机没有开机。因此 Ubuntu 无法获得以下配置：

- IPv4 地址
- 子网前缀
- 默认网关
- DNS 服务器

### 2. 恢复 DHCP 服务

启动 Windows Server 2022 虚拟机后，在 Ubuntu 中重新激活连接：

```bash
nmcli connection up netplan-ens33
```

系统提示连接已成功激活。

### 3. 验证获得的 IPv4 地址

执行：

```bash
ip addr show ens33
```

关键结果：

```text
inet 192.168.168.128/24
state UP
```

说明 Ubuntu 已通过 DHCP 成功获得 IPv4 地址。

## 六、路由验证

执行：

```bash
ip route
```

关键结果：

```text
default via 192.168.168.2 dev ens33 proto dhcp src 192.168.168.128
192.168.168.0/24 dev ens33 proto kernel scope link src 192.168.168.128
```

结果表明：

- 默认网关为 `192.168.168.2`。
- 本地网段为 `192.168.168.0/24`。
- 默认路由通过 `ens33` 网卡发送。

## 七、服务器连通性与内部 DNS 验证

### 1. Ping Windows Server

执行：

```bash
ping -c 4 192.168.168.10
```

验证结果：

- 发送 4 个数据包，接收 4 个。
- 丢包率为 0%。
- Ubuntu 与 Windows Server 网络连通正常。

### 2. 解析内部域名

执行：

```bash
nslookup srv01.lab.test
```

关键结果：

```text
Name:    srv01.lab.test
Address: 192.168.168.10
```

`nslookup` 显示的查询地址为 `127.0.0.53`。这是 Ubuntu 的 `systemd-resolved` 本地 DNS 存根地址，并非最终的上游 DNS 服务器。

## 八、外网与互联网 DNS 验证

### 1. 测试外网 IP

执行：

```bash
ping -c 4 8.8.8.8
```

结果为 4 发 4 收，丢包率 0%，说明默认路由和外网连接正常。

### 2. 测试互联网域名

执行：

```bash
ping -c 4 www.baidu.com
```

域名成功解析为 IP 地址，并且 4 发 4 收、丢包率 0%，说明互联网 DNS 解析正常。

### 3. 确认实际 DNS 服务器

执行：

```bash
resolvectl status ens33
```

关键结果：

```text
Current DNS Server: 192.168.168.10
DNS Servers: 192.168.168.10
Default Route: yes
```

这证明 Ubuntu 实际使用 Windows Server `192.168.168.10` 作为 DNS 服务器。

## 九、安装 VMware Tools

为了启用 Windows 主机与 Ubuntu 虚拟机之间的复制粘贴功能，执行：

```bash
sudo apt update
sudo apt install open-vm-tools open-vm-tools-desktop -y
```

普通重启被当前用户会话阻止后，使用：

```bash
sudo systemctl reboot -i
```

重启完成后，Windows 与 Ubuntu 之间的复制粘贴恢复正常。

Ubuntu 终端常用快捷键：

| 操作 | 快捷键 |
|---|---|
| 复制 | `Ctrl + Shift + C` |
| 粘贴 | `Ctrl + Shift + V` |
| 中止当前命令 | `Ctrl + C` |
| 清空当前输入行 | `Ctrl + U` |
| 清屏 | `Ctrl + L` |

## 十、排错思路总结

本次故障可以按照以下顺序定位：

1. 用 `ip addr` 检查网卡是否获得 IPv4 地址。
2. 用 `ip route` 检查是否存在默认路由。
3. 用 `nmcli device status` 检查连接状态。
4. 检查 DHCP 服务器是否启动并正常提供服务。
5. 用 `nmcli connection up netplan-ens33` 重新激活网络连接。
6. Ping DHCP/DNS 服务器，验证局域网连通性。
7. Ping 外网 IP，验证路由。
8. 测试域名，验证 DNS。
9. 用 `resolvectl status ens33` 确认实际 DNS 服务器。

## 十一、实验结论

本次实验完成了 Ubuntu 网络基础配置和故障排查。Ubuntu 通过 Windows Server DHCP 成功获取 `192.168.168.128/24`，默认网关为 `192.168.168.2`，DNS 服务器为 `192.168.168.10`。局域网服务器、外网 IP、内部域名和互联网域名均验证成功，网络状态正常。

同时安装了 `open-vm-tools` 和 `open-vm-tools-desktop`，解决了 VMware 中主机与 Ubuntu 之间无法复制粘贴的问题。
