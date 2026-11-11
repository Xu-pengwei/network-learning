# 实验 10：Wireshark HTTP 明文与 HTTPS 加密对比

实验日期：2026-11-11  
最后更新：2026-11-11  
记录 ID：LAB-2026-11-11-HTTP-HTTPS  
来源：本次实验实际操作、终端输出与 Wireshark 抓包结果。

## 实验目的与状态

通过 Wireshark 分别捕获 HTTP 和 HTTPS 通信，比较请求、响应及数据可见性的区别，并观察 TLS 1.3 握手过程。

- 学习进度：实验操作已完成
- 实验验证：已通过
- 知识掌握：基本掌握 HTTP 明文传输、HTTPS 加密传输及 TLS 握手过程

## 实验环境

- VMware 虚拟机
- Ubuntu 客户端网卡：`ens33`
- Ubuntu IPv4：`192.168.168.128/24`
- 默认网关：`192.168.168.2`
- DNS 服务器：`192.168.168.10`
- HTTP 测试站点：`http://neverssl.com/`
- HTTPS 测试站点：`https://example.com/`
- 工具：Wireshark、ip、ping、resolvectl、wget

## 实验前检查

执行：

```bash
ip -br addr show ens33
ip route
ping -c 4 192.168.168.10
ping -c 4 8.8.8.8
resolvectl query example.com
wget --version | head -n 1
```

验证结果：

| 项目 | 实际结果 |
|---|---|
| 网卡状态 | `ens33 UP` |
| 客户端地址 | `192.168.168.128/24` |
| 默认路由 | 经 `192.168.168.2` |
| 内网连通性 | `192.168.168.10`，4 发 4 收，丢包率 0% |
| 外网连通性 | `8.8.8.8`，4 发 4 收，丢包率 0% |
| DNS 解析 | `example.com` 解析成功 |
| HTTP 客户端 | GNU Wget 1.25.0 |

## HTTP 明文抓包

Wireshark 显示过滤器：

```wireshark
http || tcp.port == 80
```

发起请求：

```bash
wget -S -O /dev/null --timeout=15 http://neverssl.com/
```

本次连接信息：

| 包号 | 报文 | 含义 |
|---:|---|---|
| 50 | SYN | 客户端请求建立 TCP 连接 |
| 51 | TCP Retransmission | SYN 重传 |
| 52 | SYN, ACK | 服务器同意建立连接 |
| 53 | ACK | TCP 三次握手完成 |
| 54 | `GET / HTTP/1.1` | HTTP 明文请求 |
| 69 | `HTTP/1.1 200 OK` | HTTP 明文响应 |

- 客户端：`192.168.168.128:37820`
- 服务器：`34.223.124.45:80`
- 响应服务器：Apache
- 内容类型：`text/html; charset=UTF-8`
- 内容长度：3961 字节

抓包中能够直接读取请求方法、URI、Host、User-Agent、状态码、响应头和网页内容，说明 HTTP 应用数据未加密。

抓包文件已保存为 `2026-11-11-http.pcapng`。

## HTTPS 与 TLS 1.3 抓包

发起请求：

```bash
wget -S -O /dev/null --timeout=15 https://example.com/
```

Wireshark 显示过滤器：

```wireshark
ip.addr == 172.66.147.243 && tcp.port == 443
```

本次连接信息：

| 包号 | 报文 | 含义 |
|---:|---|---|
| 683 | SYN | 客户端请求建立 TCP 连接 |
| 684 | TCP Retransmission | SYN 重传 |
| 685 | SYN, ACK | 服务器同意建立连接 |
| 686 | ACK | TCP 三次握手完成 |
| 687 | TLS Client Hello | 客户端提出 TLS 参数 |
| 689 | TLS Server Hello | 服务器确认 TLS 参数 |

- 客户端：`192.168.168.128:32990`
- 服务器：`172.66.147.243:443`
- SNI：`example.com`
- 客户端支持：TLS 1.3、TLS 1.2
- 最终协商版本：TLS 1.3
- 密码套件：`TLS_AES_256_GCM_SHA384`

界面中的 `Version: TLS 1.2 (0x0303)` 是 TLS 1.3 为兼容旧实现保留的 `legacy_version` 字段，实际协商版本应以 `supported_versions: TLS 1.3` 为准。

握手完成后，请求和响应显示为 `Application Data`，无法像 HTTP 抓包一样直接读取 GET 请求、响应状态码和网页正文。

抓包文件已保存为 `2026-11-11-https-tls.pcapng`。

## HTTP 与 HTTPS 对比

| 对比项 | HTTP | HTTPS |
|---|---|---|
| 默认端口 | 80 | 443 |
| 应用数据 | 明文 | TLS 加密 |
| 请求方法 | 可直接看到 GET | 抓包中不可直接读取 |
| 响应状态 | 可直接看到 200 OK | 加密后不可直接读取 |
| 网页正文 | 可直接查看 | 显示为 Application Data |
| 身份验证 | 无 TLS 证书验证 | 通过 TLS 证书验证服务器身份 |
| 主要风险或作用 | 容易被窃听、篡改 | 提供机密性、完整性和身份认证 |

## 知识点总结

- HTTP 默认使用 TCP 80 端口，应用层内容通常以明文传输。
- HTTPS 是 HTTP 运行在 TLS 安全通道之上，默认使用 TCP 443 端口。
- 建立 HTTPS 通信前，仍需先完成 TCP 三次握手。
- Client Hello 携带客户端支持的 TLS 版本、密码套件、密钥交换参数和 SNI。
- Server Hello 确认 TLS 版本、密码套件及密钥交换参数。
- SNI 用于说明客户端准备访问的域名。
- TLS 1.3 握手完成后，HTTP 请求与响应以加密的 Application Data 传输。
- SYN 重传说明首次请求未及时获得确认，但不代表最终连接失败。

## 截图与隐私说明

本次已保存 HTTP 和 HTTPS 原始抓包文件，但仓库不上传截图和 PCAP。原始证据可能包含 MAC 地址、临时端口及无关网络流量，因此仓库仅记录经过核对的实验结果。

## 复习题

1. 为什么 HTTP 抓包可以直接看到 GET 请求，而 HTTPS 不可以？
2. HTTPS 建立连接前为什么仍需要完成 TCP 三次握手？
3. Client Hello 中的 SNI 有什么作用？
4. TLS 1.3 中为什么仍可能显示 `TLS 1.2 (0x0303)`？
5. Server Hello 如何表明最终选择了 TLS 1.3？
6. `Application Data` 表示什么？
7. SYN 重传是否一定代表网络连接失败？

## 实验结论

Ubuntu 客户端成功完成 HTTP 与 HTTPS 对比抓包。HTTP 抓包能够直接读取 GET 请求、200 OK 响应及网页内容；HTTPS 抓包确认 `example.com` 使用 TLS 1.3，并采用 `TLS_AES_256_GCM_SHA384` 密码套件。TLS 握手完成后的 HTTP 请求和响应均显示为加密的 Application Data，验证了 HTTPS 相比 HTTP 在数据机密性方面的作用。
