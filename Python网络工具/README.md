# 网络工具箱（Python 实训项目）

一个面向**计算机网络技术专业初学者**的 Python 小项目，包含三个常用的网络诊断功能。项目使用全中文界面和中文注释，并且只依赖 Python 标准库。

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Dependencies](https://img.shields.io/badge/dependencies-none-green)

## 一、功能简介

| 编号 | 功能 | 说明 |
| --- | --- | --- |
| 1 | Ping 网络连通性检测 | 发送 ICMP 探测包，显示收发包数、丢包率和平均延迟 |
| 2 | IP 地址查询 | 查看本机地址、公网出口 IP，以及指定 IP 或域名的归属地 |
| 3 | DNS 域名解析 | 正向解析域名的 IPv4/IPv6 地址，以及反向查询 IP 对应的域名 |

## 二、项目结构

```text
Python网络工具/
├── main.py                  # 程序入口：欢迎界面和主菜单
├── README.md                # 项目说明
├── requirements.txt         # 说明项目只使用标准库
├── nettool/                 # 核心功能包
│   ├── __init__.py
│   ├── utils.py             # 输入校验和格式化输出
│   ├── ping_tool.py         # Ping 网络连通性检测
│   ├── ip_tool.py           # IP 地址查询
│   └── dns_tool.py          # DNS 域名解析
└── tests/
    └── test_utils.py        # 输入校验和 Ping 解析测试
```

## 三、运行环境

- Python 3.8 或更高版本；
- 支持 Windows、Linux 和 macOS；
- 只使用 Python 标准库；
- 无需安装第三方 Python 软件包；
- Ping 功能需要操作系统提供 `ping` 命令；
- IP 归属地查询和公网 IP 查询需要连接互联网。

项目主要使用以下标准库：

- `subprocess`
- `socket`
- `ipaddress`
- `urllib`
- `json`
- `re`
- `platform`
- `contextlib`
- `time`

## 四、如何运行

### 方式 1：命令行运行

先进入 `Python网络工具` 文件夹，然后执行：

```powershell
python main.py
```

如果系统同时安装了多个 Python 版本，也可以执行：

```powershell
py main.py
```

### 方式 2：通过 Windows 文件资源管理器运行

1. 打开文件资源管理器；
2. 找到下载或克隆的 `network-learning` 文件夹；
3. 进入其中的 `Python网络工具` 文件夹；
4. 点击文件资源管理器顶部的地址栏；
5. 输入 `powershell`，然后按回车；
6. 在打开的 PowerShell 窗口中执行：

```powershell
python main.py
```

如果提示找不到 `python`，可以尝试：

```powershell
py main.py
```

> 不建议直接双击 `main.py`。如果程序发生错误，直接双击打开的窗口可能立即关闭，不方便查看错误信息。

### 方式 3：在 VS Code 中运行

1. 打开 VS Code；
2. 选择 `文件` → `打开文件夹...`；
3. 找到下载或克隆的 `network-learning` 仓库；
4. 选择其中的 `Python网络工具` 文件夹；
5. 如果尚未安装，请在扩展面板中安装 Microsoft 发布的 Python 扩展；
6. 按 `Ctrl + Shift + P`；
7. 执行 `Python: Select Interpreter`；
8. 选择 Python 3.8 或更高版本；
9. 打开 `main.py`；
10. 点击右上角的运行按钮，或者在集成终端中执行：

```powershell
python main.py
```

程序将在 VS Code 下方的终端面板中运行。

> 如果按 `F5` 后提示选择调试配置，请选择 `Python File`。

## 五、使用说明

程序启动后会显示以下主菜单：

```text
--------------------------------------------------
  1. Ping 网络连通性检测
  2. IP 地址查询
  3. DNS 域名解析
  0. 退出程序
--------------------------------------------------
请输入功能编号：
```

操作方法：

- 输入功能编号并按回车，即可进入对应功能；
- 每个功能内部可能包含二级菜单；
- 输入 `0` 可以返回上一级菜单；
- 在输入位置直接按回车，可以返回或退出当前功能；
- 在主菜单输入 `q` 也可以退出程序；
- 按 `Ctrl + C` 可以中断当前操作，程序会尽量安全返回或退出。

### 输入示例

| 功能 | 输入示例 |
| --- | --- |
| Ping 检测 | `www.baidu.com`、`127.0.0.1`、`8.8.8.8` |
| DNS 正向解析 | `www.qq.com`、`www.baidu.com` |
| DNS 反向解析 | `8.8.8.8`、`114.114.114.114` |
| IP 归属地查询 | `8.8.8.8`、`www.qq.com` |

程序也支持整理部分常见输入格式，例如：

```text
https://www.baidu.com/s?wd=python
example.com:8080
[::1]
```

## 六、实现原理

### 1. Ping 网络连通性检测

Ping 基于 ICMP 协议。本机向目标发送回显请求，目标收到后可以返回回显应答。

程序使用 `subprocess.run()` 调用操作系统提供的 `ping` 命令，并尝试从输出中提取以下信息：

- 发送包数；
- 接收包数；
- 丢包率；
- 平均延迟；
- 目标 IP 地址。

Windows、Linux 和 macOS 的 Ping 参数及输出格式存在差异，因此程序会根据操作系统生成不同的命令，并使用多套规则解析中英文输出。

如果程序无法识别当前系统的 Ping 输出格式，部分统计结果可能显示为“未知”。此时仍可以参考程序显示的原始 Ping 输出。

### 2. IP 地址查询

本机地址查询使用：

- `socket.gethostname()` 获取计算机名；
- `socket.getaddrinfo()` 查询本机 IPv4 和 IPv6 地址；
- `ipaddress` 判断地址类型；
- UDP 套接字探测当前主要出口网卡的 IPv4 地址。

公网出口 IP 和归属地通过第三方免费接口查询。主接口失败后，程序会依次尝试备用接口。

备用接口的返回内容会经过 `ipaddress.ip_address()` 验证，只有合法的 IPv4 或 IPv6 地址才会被接受。

本机网卡地址与公网出口 IP 可能不同。这是因为家庭、学校和企业网络通常使用 NAT，让多台设备共享一个公网出口地址。

### 3. DNS 域名解析

DNS 正向解析使用 `socket.getaddrinfo()` 查询：

- A 记录对应的 IPv4 地址；
- AAAA 记录对应的 IPv6 地址。

DNS 反向解析使用 `socket.gethostbyaddr()` 查询 IP 地址对应的主机名，也就是常见的 PTR 反向查询。

程序会尝试设置 5 秒的默认网络超时，但 DNS 查询由操作系统的系统解析器完成，实际等待时间可能受到操作系统、本机 DNS 配置和网络环境影响。

## 七、运行检查和测试

请先进入 `Python网络工具` 文件夹。

### 1. 检查 Python 语法

Windows PowerShell：

```powershell
python -m py_compile main.py nettool\utils.py nettool\ping_tool.py nettool\ip_tool.py nettool\dns_tool.py
```

如果命令没有输出，说明这些文件通过了基础语法检查。

### 2. 运行单元测试

```powershell
python -m unittest discover -s tests -v
```

当前自动化测试主要覆盖：

- 用户输入整理；
- IPv4 和 IPv6 格式判断；
- 域名格式判断；
- IP 地址类型说明；
- 中文 Windows Ping 输出解析；
- Linux Ping 输出解析；
- 域名解析失败的 Ping 输出；
- Ping 命令的基础构造。

当前测试尚未完整覆盖：

- 真实网络连接；
- 公网 IP 接口和备用接口切换；
- IP 归属地接口；
- DNS 正向和反向查询；
- 主菜单交互流程。

因此，单元测试通过并不代表所有网络功能在每一种网络环境中都能正常使用。

## 八、常见问题

### 1. 提示“系统找不到 ping 命令”

操作系统可能没有提供 `ping` 命令，或者该命令没有加入系统环境变量。

可以先在 PowerShell 或终端中直接执行：

```powershell
ping 127.0.0.1
```

如果系统同样提示找不到命令，需要先检查操作系统的网络工具配置。

### 2. Ping 显示丢包或全部超时，但网页可以打开

部分服务器和防火墙会拦截 ICMP 请求。因此，Ping 不通不一定表示网站或服务器无法访问。

可以继续使用 DNS 解析功能检查域名是否可以正常解析。

### 3. IP 归属地查询失败

可能原因包括：

- 本机没有连接互联网；
- 免费接口暂时不可用；
- 请求次数超过接口限制；
- 学校、企业或代理网络拦截了请求；
- 查询的是内网地址或特殊用途地址。

主接口失败时，程序会尝试通过备用接口获取公网 IP，但备用接口不提供完整的归属地信息。

### 4. DNS 反向解析查不到域名

不是所有 IP 地址都设置了 PTR 反向解析记录。无法查询到域名并不一定代表 DNS 或网络发生故障。

### 5. 终端显示中文乱码

建议使用以下终端：

- Windows Terminal；
- PowerShell；
- VS Code 集成终端。

同时确认项目文件使用 UTF-8 编码保存。

### 6. 提示找不到 `nettool` 文件夹或 Python 文件

请确认当前终端位于 `Python网络工具` 文件夹。

可以在 PowerShell 中执行：

```powershell
dir
```

正常情况下应该看到：

```text
main.py
README.md
requirements.txt
nettool
tests
```

## 九、隐私与使用限制

- IP 归属地来自第三方数据库，只能作为近似参考，不能代表准确的物理位置；
- 查询公网 IP 或指定地址时，查询内容会发送给外部接口；
- 当前部分免费接口使用 HTTP，不适合查询敏感地址或内部业务地址；
- 不建议使用本项目扫描或查询未经授权的目标；
- Ping 不通不一定表示目标网站或服务器无法访问；
- DNS 查询的实际等待时间可能受到操作系统和网络环境影响；
- 免费接口的地址、限制和返回格式将来可能发生变化；
- 本项目用于网络基础学习，不应作为生产环境中的专业诊断工具。

## 十、可以继续扩展的练习

1. 允许用户设置 Ping 探测次数；
2. 增加批量 Ping 功能；
3. 增加 TCP 端口连通性检测；
4. 将检测结果保存为 CSV 或日志文件；
5. 为公网 IP 查询增加自动化测试；
6. 为 DNS 正向和反向解析增加自动化测试；
7. 使用 `tkinter` 制作图形界面版本；
8. 添加 GitHub Actions，在每次提交后自动运行测试。

## 十一、许可说明

本项目目前用于个人学习、课堂练习和学习成果展示。

仓库当前没有提供正式的开源许可证。在添加 `LICENSE` 文件之前，请不要默认本项目已经授予不受限制的复制、分发或商业使用权限。

如果后续希望允许其他人自由学习、修改和分发，可以考虑在仓库根目录添加 MIT License。
