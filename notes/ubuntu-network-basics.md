# Ubuntu 网络基础配置与排错

## 一、实验目的

1. 熟悉 Ubuntu 系统中的常用网络命令。
2. 掌握查看 IP 地址、网卡、默认网关和 DNS 配置的方法。
3. 学会使用 `ping`、`ip` 和 `nmcli` 等命令检查网络状态。
4. 初步掌握 Ubuntu 网络故障排查流程。

## 二、实验环境

| 项目 | 配置信息 |
|---|---|
| 操作系统 | Ubuntu Linux |
| 虚拟化软件 | VMware Workstation |
| 网络模式 | 请填写实际网络模式 |
| 网卡名称 | 请填写实际网卡名称 |
| IPv4 地址 | 请填写实际 IP 地址 |
| 默认网关 | 请填写实际网关地址 |
| DNS 服务器 | 请填写实际 DNS 地址 |

> 当前报告中的部分网络信息暂时保留为占位内容，完成实际验证后再填写真实数据。

## 三、常用网络命令

### 1. 查看系统和主机名

查看 Ubuntu 系统版本：

```bash
lsb_release -a
```

查看当前主机名：

```bash
hostname
```

查看更完整的主机信息：

```bash
hostnamectl
```

### 2. 查看网卡和 IP 地址

执行以下命令：

```bash
ip addr
```

也可以使用简写：

```bash
ip a
```

该命令可以查看：

- 网卡名称
- 网卡运行状态
- IPv4 地址
- IPv6 地址
- MAC 地址
- 子网前缀长度

常见的网卡名称包括：

```text
ens33
ens160
eth0
```

其中，`lo` 是本地回环接口，不是实际使用的物理或虚拟网卡。

### 3. 查看指定网卡信息

假设网卡名称为 `ens33`，可以执行：

```bash
ip addr show ens33
```

如果实际网卡名称不同，需要将 `ens33` 替换为实际名称。

### 4. 查看网卡连接状态

执行：

```bash
ip link
```

如果网卡状态中出现：

```text
state UP
```

表示网卡已经启用。

如果出现：

```text
state DOWN
```

表示网卡没有启用或网络连接存在问题。

还可以执行：

```bash
nmcli device status
```

该命令可以查看网卡名称、网卡类型、连接状态和当前连接名称。

## 四、查看路由和默认网关

执行：

```bash
ip route
```

正常情况下可以看到类似结果：

```text
default via 192.168.10.1 dev ens33
192.168.10.0/24 dev ens33 proto kernel scope link
```

其中：

- `default via` 后面的地址是默认网关。
- `dev` 后面是使用的网卡名称。
- `/24` 表示子网前缀长度，对应子网掩码 `255.255.255.0`。

## 五、查看 DNS 配置

可以执行：

```bash
resolvectl status
```

该命令可以查看当前网卡使用的 DNS 服务器和 DNS 域信息。

也可以查看：

```bash
cat /etc/resolv.conf
```

可能看到类似内容：

```text
nameserver 127.0.0.53
```

在使用 `systemd-resolved` 的 Ubuntu 系统中，`127.0.0.53` 通常是本机的 DNS 解析服务地址，不一定是最终使用的上游 DNS 服务器。

因此，查看实际 DNS 服务器时，优先使用：

```bash
resolvectl status
```

## 六、网络连通性测试

### 1. 测试本机 TCP/IP

执行：

```bash
ping -c 4 127.0.0.1
```

如果能够收到回复，说明本机 TCP/IP 协议栈工作正常。

### 2. 测试默认网关

执行：

```bash
ping -c 4 默认网关地址
```

示例：

```bash
ping -c 4 192.168.10.1
```

如果能够收到回复，说明 Ubuntu 与本地网络之间基本连通。

### 3. 测试外网 IP

执行：

```bash
ping -c 4 8.8.8.8
```

如果能够收到回复，说明网络路由基本正常。

如果网关可以连通，但外网 IP 无法连通，可能是虚拟机网络模式、NAT 服务或上级网络存在问题。

### 4. 测试域名解析

执行：

```bash
ping -c 4 www.baidu.com
```

如果 IP 地址能够访问，但域名无法访问，通常说明 DNS 配置存在问题。

也可以执行：

```bash
nslookup www.baidu.com
```

如果系统提示没有找到 `nslookup` 命令，可以安装相关工具：

```bash
sudo apt update
sudo apt install dnsutils
```

## 七、使用 NetworkManager 查看网络信息

查看所有网络连接：

```bash
nmcli connection show
```

查看设备状态：

```bash
nmcli device status
```

查看详细网络信息：

```bash
nmcli device show
```

查看指定网卡信息：

```bash
nmcli device show ens33
```

使用时，需要将 `ens33` 替换为实际网卡名称。

## 八、自动获取 IP 地址

Ubuntu 虚拟机通常通过 DHCP 自动获取 IP 地址。

查看当前网络连接：

```bash
nmcli connection show
```

查看 IPv4 获取方式：

```bash
nmcli connection show "有线连接名称"
```

如果 IPv4 配置中显示自动获取，说明当前网络使用 DHCP。

不同 Ubuntu 版本和语言环境中的连接名称可能不同，应以实际显示结果为准。

## 九、网络故障排查顺序

遇到网络问题时，可以按照以下顺序进行检查：

1. 检查 VMware 虚拟机的网络适配器是否已经连接。
2. 使用 `ip link` 检查网卡是否启用。
3. 使用 `ip addr` 检查是否获得 IP 地址。
4. 使用 `ip route` 检查是否存在默认网关。
5. 使用 `ping` 测试本机和默认网关。
6. 使用 `ping 8.8.8.8` 测试外网 IP。
7. 使用 `ping www.baidu.com` 测试 DNS 解析。
8. 使用 `resolvectl status` 检查 DNS 服务器。
9. 使用 `nmcli device status` 检查网络连接状态。

## 十、常见问题

### 1. 网卡没有 IP 地址

可能原因：

- VMware 网络适配器没有连接。
- DHCP 服务异常。
- 网卡处于关闭状态。
- NetworkManager 服务异常。
- 虚拟机网络模式配置错误。

可以执行：

```bash
nmcli device status
ip addr
```

### 2. 出现 `Network is unreachable`

这通常表示系统没有可用的网络路由。

可以执行：

```bash
ip route
```

检查是否存在以 `default via` 开头的默认路由。

### 3. 可以访问 IP，但不能访问域名

这通常是 DNS 解析问题。

可以执行：

```bash
resolvectl status
ping -c 4 8.8.8.8
ping -c 4 www.baidu.com
```

通过对比测试结果判断是否为 DNS 故障。

### 4. 网卡显示 disconnected

可以先检查 VMware 中的网络适配器是否勾选“已连接”，然后执行：

```bash
nmcli device status
```

确认网卡状态。

## 十一、实验验证结果

计划执行以下命令完成验证：

```bash
hostnamectl
ip addr
ip route
nm
