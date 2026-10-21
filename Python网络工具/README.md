# 网络工具箱（Python 实训项目）

一个面向**计算机网络技术专业初学者**的 Python 小项目，包含三个常用的网络诊断功能，全中文界面、全中文注释、只使用 Python 标准库。

![Python](https://img.shields.io/badge/Python-3.8%2B-blue) ![License](https://img.shields.io/badge/依赖-无-green)

## 一、功能简介

| 编号 | 功能 | 说明 |
| --- | --- | --- |
| 1 | Ping 网络连通性检测 | 发送 ICMP 探测包，显示收发包数、丢包率、平均延迟 |
| 2 | IP 地址查询 | 本机网卡地址（内网/公网判断）、公网出口 IP、指定 IP/域名归属地 |
| 3 | DNS 域名解析 | 正向解析（域名→IPv4/IPv6）、反向解析（IP→域名） |

## 二、项目结构

```
默认项目/
├── main.py                  # 程序入口：欢迎界面 + 主菜单
├── README.md                # 本文件
├── requirements.txt         # 说明仅使用标准库
├── nettool/                 # 核心功能包
│   ├── __init__.py
│   ├── utils.py             # 公共工具：输入校验、格式化输出
│   ├── ping_tool.py         # 功能①：Ping 检测
│   ├── ip_tool.py           # 功能②：IP 查询
│   └── dns_tool.py          # 功能③：DNS 解析
└── tests/
    └── test_utils.py        # 单元测试
```

## 三、运行环境

- Python 3.8 及以上（本项目在 Python 3.14.7 上测试通过）
- 仅使用标准库：`subprocess`、`socket`、`ipaddress`、`urllib`、`re`、`platform`
- 无需 `pip install` 任何东西

## 四、如何运行

### 方式 1：命令行（最直接）

在项目文件夹中打开终端（PowerShell 或 CMD），执行：

```powershell
python main.py
```

如果系统里同时装了多个 Python 版本，也可以用：

```powershell
py main.py
```

### 方式 2：Windows 图形界面操作

**打开项目文件夹：**

1. 按 `Win + E` 打开"文件资源管理器"；
2. 在顶部的地址栏中粘贴下面的路径，然后按回车：
   ```
   C:\Users\Xupengwei--1014\Documents\默认项目
   ```
3. 即可看到 `main.py`、`nettool`、`tests` 等文件。

> 小技巧：也可以按 `Win + R`，输入上面的路径后回车，同样能直接打开该文件夹。

**在图形界面里运行：**

- 直接**双击 `main.py`**：如果 `.py` 文件已关联到 Python，会弹出一个黑色控制台窗口并启动程序；
- 或者：在文件夹空白处**按住 Shift + 鼠标右键** → 选择"在此处打开 PowerShell 窗口" → 输入 `python main.py` 回车。

### 方式 3：在 VS Code 中运行

1. 打开 VS Code；
2. 菜单 `文件` → `打开文件夹...`，选择
   `C:\Users\Xupengwei--1014\Documents\默认项目`；
3. 若首次使用 Python，请在左侧扩展面板（`Ctrl + Shift + X`）中安装 **Python** 扩展（Microsoft 官方）；
4. 按 `Ctrl + Shift + P`，输入 `Python: Select Interpreter`，选择本机的 `Python 3.14.7`；
5. 打开 `main.py`，然后任选一种方式运行：
   - 点击右上角的 **▷ 运行** 按钮；
   - 或按 `F5`（调试运行）/ `Ctrl + F5`（直接运行）；
   - 或打开集成终端（`` Ctrl + ` ``），输入 `python main.py`。
6. 程序运行在 VS Code 下方的"终端"面板中，按提示输入数字选择功能。

> 如果按 `F5` 弹出"选择调试配置"，选择 **Python File**（当前文件）即可，无需额外创建配置文件。
> 也可以在 `.vscode/launch.json` 中自行添加配置，本项目未预先创建。

## 五、使用说明

启动后主菜单如下：

```
--------------------------------------------------
  1. Ping 网络连通性检测
  2. IP 地址查询
  3. DNS 域名解析
  0. 退出程序
--------------------------------------------------
请输入功能编号：
```

- 输入数字后按回车进入对应功能；
- 每个功能内部还有二级菜单，输入 `0` 返回上一级；
- 在任何输入处直接按回车，等同于返回/退出当前功能；
- 按 `Ctrl + C` 可随时中断当前操作，不会导致程序崩溃。

### 各功能输入示例

| 功能 | 可输入内容 |
| --- | --- |
| Ping 检测 | `www.baidu.com`、`127.0.0.1`、`8.8.8.8` |
| DNS 正向解析 | `www.qq.com`、`www.baidu.com` |
| DNS 反向解析 | `8.8.8.8`、`114.114.114.114` |
| 归属地查询 | `8.8.8.8`、`www.qq.com` |

## 六、实现原理速览

### Ping 检测

`ping` 命令基于 **ICMP 协议**：本机发送"回显请求"，目标主机回复"回显应答"。
程序用 `subprocess.run()` 调用系统 `ping`，再用正则表达式从输出中提取
丢包率和平均延迟。由于 Windows 与 Linux/macOS 的命令参数、输出语言都不同，
代码里做了多套正则和平台判断，解析失败时仍会展示原始输出，不会直接报错。

### IP 查询

- 本机地址：`socket.gethostname()` + `socket.getaddrinfo()`，再用 `ipaddress`
  判断是内网地址（192.168/10.x/172.16~31.x）还是公网地址；
- 公网出口 IP：通过 `ip-api.com` 的免费接口查询，设置了 5 秒超时；
  主接口失败时依次尝试 `ip-api` 简易接口、`ipify`、`icanhazip` 等多个备用来源
  （备用接口只返回 IP，不含归属地）；
- 内网 IP 与公网 IP 不同，是因为家庭/学校网络普遍使用 **NAT** 共享出口。

### DNS 解析

`socket.getaddrinfo()` 调用系统解析器获取 A 记录（IPv4）和 AAAA 记录
（IPv6），`socket.gethostbyaddr()` 做 PTR 反向查询。查询统一加 5 秒超时
（通过 `socket.setdefaulttimeout()`），避免无响应时卡死。

## 七、运行测试

在项目根目录执行：

```powershell
python -m unittest discover -s tests -v
```

测试只覆盖输入校验和 ping 输出解析，不依赖真实网络，可以离线运行。

## 八、常见问题

**1. 提示"系统找不到 ping 命令"**
极少数精简版 Windows 缺少 ping.exe，请在其他机器上运行，或改用 TCP 端口探测。

**2. Ping 显示丢包或全部超时，但网页能打开**
很多服务器/防火墙默认**拦截 ICMP**，此时 ping 不通不代表网站不能访问。
可以改用 DNS 解析来确认域名是否正常。

**3. 归属地查询失败**
`ip-api.com` 免费接口限制每分钟 45 次，且需要联网。失败时程序会自动尝试
备用接口，只获取公网 IP。

**4. 反向解析查不到域名**
不是所有 IP 都配置了 PTR 记录，查不到属于正常现象。

**5. 终端里中文显示乱码**
请使用 Windows Terminal、VS Code 集成终端或 PowerShell，并确认文件以 UTF-8 保存。

## 九、可以继续扩展的练习

1. 把 Ping 的探测次数改成用户可输入（`ping_host()` 已支持 `count` 参数）；
2. 增加"批量 Ping"功能：从文本文件读取多个地址，逐个检测；
3. 增加"端口探测"功能：用 `socket.connect_ex()` 检测 80/443/22 端口是否开放；
4. 把结果保存成 CSV 或日志文件，方便写实验报告；
5. 用 `tkinter`（标准库自带）做一个图形界面版本。

## 十、许可

本项目为教学示例，可自由用于课堂练习与二次修改。
