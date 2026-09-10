# Nmap 使用指南

> Nmap（Network Mapper）是最流行的网络扫描和安全审计工具，用于发现网络中的主机、端口、服务和操作系统等信息。

---

## 目录

- [一、Nmap 简介](#一nmap-简介)
- [二、安装](#二安装)
- [三、基本使用](#三基本使用)
- [四、主机发现](#四主机发现)
- [五、端口扫描](#五端口扫描)
- [六、服务与版本探测](#六服务与版本探测)
- [七、操作系统探测](#七操作系统探测)
- [八、脚本扫描（NSE）](#八脚本扫描nse)
- [九、防火墙绕过](#九防火墙绕过)
- [十、输出格式](#十输出格式)
- [十一、常用扫描组合](#十一常用扫描组合)
- [十二、Nmap 脚本引擎详解](#十二nmap-脚本引擎详解)
- [十三、使用技巧与注意事项](#十三使用技巧与注意事项)

---

## 一、Nmap 简介

Nmap 是由 Gordon Lyon（Fyodor）开发的开源网络扫描工具。

**主要功能**：
- 主机发现（Host Discovery）
- 端口扫描（Port Scanning）
- 版本探测（Version Detection）
- 操作系统探测（OS Detection）
- 脚本扫描（Nmap Scripting Engine）

**特点**：
- 功能强大，支持多种扫描技术
- 跨平台（Windows/Linux/Mac）
- 可扩展的脚本引擎（NSE）
- 性能优秀，适合大规模扫描

---

## 二、安装

### 2.1 Linux

```bash
# Debian/Ubuntu
sudo apt-get install nmap

# CentOS/RHEL
sudo yum install nmap

# Kali Linux（自带）
nmap --version
```

### 2.2 Windows

1. 官网下载：https://nmap.org/download.html
2. 安装包安装（包含 Zenmap 图形界面）

### 2.3 Mac

```bash
brew install nmap
```

### 2.4 验证安装

```bash
nmap --version
nmap -h
```

---

## 三、基本使用

### 3.1 最简单的扫描

```bash
# 扫描单个 IP
nmap 192.168.1.1

# 扫描域名
nmap example.com

# 扫描多个 IP
nmap 192.168.1.1 192.168.1.2 192.168.1.3

# 扫描网段
nmap 192.168.1.0/24
nmap 192.168.1.1-254

# 扫描范围
nmap 192.168.1.1-100
```

### 3.2 从文件读取目标

```bash
# 每行一个 IP/域名
nmap -iL targets.txt
```

### 3.3 排除目标

```bash
nmap 192.168.1.0/24 --exclude 192.168.1.1
nmap 192.168.1.0/24 --exclude 192.168.1.1,192.168.1.100
nmap -iL targets.txt --excludefile exclude.txt
```

### 3.4 扫描参数速查

| 参数 | 说明 |
|------|------|
| `-sS` | SYN 半开放扫描（默认，需 root） |
| `-sT` | TCP 连接扫描 |
| `-sU` | UDP 扫描 |
| `-sP` / `-sn` | 仅主机发现（Ping 扫描） |
| `-sV` | 服务版本探测 |
| `-O` | 操作系统探测 |
| `-A` | 全面扫描（-sV -O -sC --traceroute） |
| `-p` | 指定端口 |
| `-Pn` | 跳过主机发现，直接扫描 |
| `-n` | 不做 DNS 解析 |
| `-T` | 时序模板（0-5） |
| `-oN/-oX/-oG` | 输出格式（普通/XML/grepable） |
| `-v` / `-vv` | 详细输出 |

---

## 四、主机发现

### 4.1 主机发现技术

| 参数 | 说明 |
|------|------|
| `-sP` / `-sn` | Ping 扫描，仅发现存活主机 |
| `-Pn` | 跳过主机发现（假设所有主机都存活） |
| `-PS` | TCP SYN Ping |
| `-PA` | TCP ACK Ping |
| `-PU` | UDP Ping |
| `-PE` | ICMP Echo Ping |
| `-PP` | ICMP Timestamp Ping |
| `-PM` | ICMP Netmask Ping |
| `-PR` | ARP Ping（局域网最快） |
| `-n` | 不做 DNS 反向解析 |
| `-R` | 总是做 DNS 解析 |

### 4.2 常用主机发现

```bash
# Ping 扫描（最常用，快速发现存活主机）
nmap -sn 192.168.1.0/24

# 不做 DNS 解析，更快
nmap -sn -n 192.168.1.0/24

# TCP SYN Ping（目标禁 Ping 时使用）
nmap -sn -PS22,80,443 192.168.1.0/24

# UDP Ping
nmap -sn -PU53,161 192.168.1.0/24

# ARP Ping（局域网最快，最准确）
nmap -sn -PR 192.168.1.0/24

# 多种探测组合
nmap -sn -PS22,80,443 -PU53,161 -PE 192.168.1.0/24
```

### 4.3 输出结果解读

```
Nmap scan report for 192.168.1.1
Host is up (0.0050s latency).
MAC Address: 00:11:22:33:44:55 (Cisco)
```

---

## 五、端口扫描

### 5.1 端口状态

| 状态 | 说明 |
|------|------|
| **open** | 开放，有程序在监听 |
| **closed** | 关闭，端口可达但无程序监听 |
| **filtered** | 被过滤，被防火墙/设备阻挡 |
| **unfiltered** | 未过滤，端口可达但无法判断状态 |
| **open\|filtered** | 开放或过滤（无法确定） |
| **closed\|filtered** | 关闭或过滤（无法确定） |

### 5.2 扫描类型

| 参数 | 类型 | 说明 | 特点 |
|------|------|------|------|
| `-sS` | TCP SYN | 半开放扫描，只发 SYN 包 | 快、隐蔽，需 root，默认 |
| `-sT` | TCP Connect | 完整 TCP 连接 | 不需要 root，慢，易被记录 |
| `-sU` | UDP | UDP 端口扫描 | 慢，常用 UDP 服务 |
| `-sA` | TCP ACK | ACK 扫描 | 探测防火墙规则 |
| `-sW` | TCP Window | 窗口扫描 | 判断端口开放/关闭 |
| `-sM` | Maimon | Maimon 扫描 | 特殊系统有效 |
| `-sN` | Null | 无标志位 | 绕过某些防火墙 |
| `-sF` | FIN | FIN 标志位 | 绕过无状态防火墙 |
| `-sX` | Xmas | FIN+PSH+URG | 圣诞包扫描 |

### 5.3 指定端口

```bash
# 扫描指定端口
nmap -p 22 192.168.1.1
nmap -p 22,80,443 192.168.1.1
nmap -p 1-1000 192.168.1.1

# 常用端口
nmap -F 192.168.1.1        # Fast，100 个常用端口
nmap --top-ports 100 192.168.1.1  # 前 100 个常用端口

# 所有端口（1-65535）
nmap -p- 192.168.1.1
nmap -p 1-65535 192.168.1.1

# 指定协议
nmap -p T:80,443,U:53 192.168.1.1

# 按名称
nmap -p http,https,ssh 192.168.1.1
```

### 5.4 端口扫描示例

```bash
# 默认扫描（SYN，1000 个常用端口）
nmap 192.168.1.1

# TCP 全端口扫描
nmap -p- 192.168.1.1

# UDP 扫描
nmap -sU 192.168.1.1
nmap -sU -p 53,67,69,161 192.168.1.1

# 同时扫描 TCP 和 UDP
nmap -sS -sU -p T:1-1000,U:53,161 192.168.1.1
```

---

## 六、服务与版本探测

### 6.1 版本探测

```bash
# 探测服务版本
nmap -sV 192.168.1.1

# 版本探测强度（0-9，默认 7）
nmap -sV --version-intensity 5 192.168.1.1
nmap -sV --version-all 192.168.1.1     # 最高强度 9
nmap -sV --version-light 192.168.1.1   # 轻量级 2
```

### 6.2 输出示例

```
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
80/tcp   open  http    Apache httpd 2.4.38 ((Debian))
443/tcp  open  ssl/ssl OpenSSL 1.1.1d
```

---

## 七、操作系统探测

### 7.1 基本用法

```bash
# 操作系统探测
nmap -O 192.168.1.1

# 同时探测版本和 OS
nmap -sV -O 192.168.1.1

# 激进猜测（信息不足时多猜几个）
nmap -O --osscan-guess 192.168.1.1
```

### 7.2 输出示例

```
Device type: general purpose
Running: Linux 4.X|5.X
OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5
OS details: Linux 4.15 - 5.6
```

---

## 八、脚本扫描（NSE）

Nmap Scripting Engine（NSE）是 Nmap 的脚本引擎，使用 Lua 编写，可以扩展各种功能。

### 8.1 基本用法

```bash
# 使用默认安全脚本扫描
nmap -sC 192.168.1.1

# 指定脚本
nmap --script=script-name 192.168.1.1

# 多个脚本（逗号分隔）
nmap --script=http-title,ssh-auth-methods 192.168.1.1

# 脚本分类
nmap --script=default 192.168.1.1      # 默认脚本
nmap --script=safe 192.168.1.1         # 安全脚本
nmap --script=discovery 192.168.1.1    # 发现类
nmap --script=vuln 192.168.1.1         # 漏洞扫描
nmap --script=auth 192.168.1.1         # 认证相关
nmap --script=brute 192.168.1.1        # 暴力破解
nmap --script=exploit 192.168.1.1      # 漏洞利用
```

### 8.2 脚本分类

| 类别 | 说明 |
|------|------|
| `auth` | 认证绕过相关 |
| `broadcast` | 广播探测 |
| `brute` | 暴力破解 |
| `default` | 默认脚本（安全且信息丰富） |
| `discovery` | 服务/主机发现 |
| `dos` | 拒绝服务攻击 |
| `exploit` | 漏洞利用 |
| `external` | 依赖外部资源 |
| `fuzzer` | Fuzz 测试 |
| `intrusive` | 可能触发报警/破坏 |
| `malware` | 恶意软件检测 |
| `safe` | 安全无害 |
| `version` | 版本探测辅助 |
| `vuln` | 漏洞检测 |

### 8.3 常用脚本

**HTTP 相关**：
```bash
# HTTP 标题
nmap --script=http-title -p 80,443 192.168.1.1

# HTTP 方法
nmap --script=http-methods -p 80 192.168.1.1

# 目录枚举
nmap --script=http-enum -p 80 192.168.1.1

# WAF 检测
nmap --script=http-waf-detect -p 80 192.168.1.1

# Wordpress 扫描
nmap --script=http-wordpress* -p 80 192.168.1.1
```

**认证/暴力破解**：
```bash
# SSH 认证方式
nmap --script=ssh-auth-methods -p 22 192.168.1.1

# FTP 匿名登录
nmap --script=ftp-anon -p 21 192.168.1.1

# MySQL 空密码
nmap --script=mysql-empty-password -p 3306 192.168.1.1
```

**漏洞扫描**：
```bash
# 漏洞脚本分类扫描
nmap --script=vuln 192.168.1.1

# 心脏出血
nmap --script=ssl-heartbleed -p 443 192.168.1.1

# MS17-010 永恒之蓝
nmap --script=smb-vuln-ms17-010 -p 445 192.168.1.1
```

### 8.4 脚本参数

```bash
# 传递参数给脚本
nmap --script=http-enum --script-args http-enum.url-path=/admin 192.168.1.1

# 暴力破解脚本参数
nmap --script=ssh-brute \
     --script-args userdb=users.txt,passdb=passwords.txt \
     -p 22 192.168.1.1
```

### 8.5 查看脚本帮助

```bash
nmap --script-help=http-enum
nmap --script-help=ssh-brute
```

---

## 九、防火墙绕过

### 9.1 分片

```bash
# 将扫描包分片（绕过某些简单防火墙）
nmap -f 192.168.1.1

# 指定分片大小（必须是 8 的倍数）
nmap --mtu 24 192.168.1.1
```

### 9.2 诱饵/僵尸

```bash
# 诱饵扫描（混入假 IP）
nmap -D 10.0.0.1,10.0.0.2,ME 192.168.1.1
nmap -D RND:5 192.168.1.1  # 随机 5 个诱饵

# 空闲扫描（僵尸扫描，完全隐蔽）
nmap -sI zombie_ip 192.168.1.1
```

### 9.3 源地址/端口

```bash
# 指定源 IP
nmap -S 10.0.0.100 192.168.1.1

# 指定源端口
nmap --source-port 53 192.168.1.1
nmap -g 80 192.168.1.1
```

### 9.4 其他绕过

```bash
# 随机化目标顺序
nmap --randomize-hosts 192.168.1.0/24

# 改变数据长度
nmap --data-length 25 192.168.1.1

# 随机 MAC 地址
nmap --spoof-mac 0 192.168.1.1  # 随机 MAC
nmap --spoof-mac Apple 192.168.1.1  # 指定厂商前缀
```

---

## 十、输出格式

### 10.1 输出格式

| 参数 | 格式 | 说明 |
|------|------|------|
| `-oN` | Normal | 普通文本格式（人可读） |
| `-oX` | XML | XML 格式（程序解析） |
| `-oG` | Grepable | Grep 友好格式（一行一条） |
| `-oA` | All | 同时输出以上三种格式 |
| `-oS` | Script Kiddie | 搞怪格式 |

### 10.2 示例

```bash
# 普通文本输出
nmap -oN scan_result.txt 192.168.1.0/24

# XML 输出
nmap -oX scan_result.xml 192.168.1.0/24

# 所有格式（生成 .nmap .xml .gnmap）
nmap -oA full_scan 192.168.1.1

# 输出到指定目录
nmap -oA ./output/scan 192.168.1.1
```

### 10.3 详细程度

```bash
nmap -v 192.168.1.1      # 详细输出
nmap -vv 192.168.1.1     # 更详细
nmap -d 192.168.1.1      # 调试输出
nmap -dd 192.168.1.1     # 更详细调试
```

---

## 十一、常用扫描组合

### 11.1 快速主机发现

```bash
# 快速存活主机扫描
nmap -sn -n 192.168.1.0/24

# 更快，只发 SYN 到常用端口
nmap -sn -PS22,80,443 -n 192.168.1.0/24
```

### 11.2 快速端口扫描

```bash
# 常用端口快速扫描
nmap -F 192.168.1.1

# 全端口快速扫描
nmap -p- -T4 192.168.1.1
```

### 11.3 全面扫描

```bash
# 最全面的扫描（-A = -sV -O -sC --traceroute）
nmap -A 192.168.1.1

# 全端口 + 版本 + 脚本 + OS
nmap -p- -sV -O -sC 192.168.1.1
```

### 11.4 漏洞扫描

```bash
# 漏洞脚本扫描
nmap --script=vuln -sV 192.168.1.1

# 常见服务漏洞
nmap --script=vuln,auth,brute -sV 192.168.1.1
```

### 11.5 隐蔽扫描

```bash
# SYN 扫描 + 慢速 + 分片
nmap -sS -f -T2 192.168.1.1

# 空闲扫描（最隐蔽）
nmap -sI zombie_ip -Pn -n 192.168.1.1
```

### 11.6 生产环境安全扫描

```bash
# 只做版本探测，不做危险操作
nmap -sV -sC safe -T3 192.168.1.1
```

---

## 十二、Nmap 脚本引擎详解

### 12.1 脚本位置

| 系统 | 路径 |
|------|------|
| Linux | `/usr/share/nmap/scripts/` |
| Windows | `C:\Program Files (x86)\Nmap\scripts\` |
| Mac | `/usr/local/share/nmap/scripts/` |

### 12.2 更新脚本数据库

```bash
# 更新脚本数据库（添加新脚本后运行）
sudo nmap --script-updatedb
```

### 12.3 常用脚本清单

**信息收集**：
| 脚本名 | 说明 |
|--------|------|
| `http-title` | 获取网页标题 |
| `http-server-header` | 获取服务器响应头 |
| `http-methods` | 支持的 HTTP 方法 |
| `http-enum` | 目录枚举 |
| `dns-zone-transfer` | DNS 区域传输 |
| `smb-os-discovery` | SMB 系统发现 |
| `snmp-info` | SNMP 信息 |

**漏洞检测**：
| 脚本名 | 说明 |
|--------|------|
| `ssl-heartbleed` | 心脏出血 |
| `ssl-poodle` | Poodle 漏洞 |
| `smb-vuln-ms17-010` | 永恒之蓝 |
| `smb-vuln-ms08-067` | MS08-067 |
| `http-vuln-cve2014-6271` | Shellshock |

**暴力破解**：
| 脚本名 | 说明 |
|--------|------|
| `ssh-brute` | SSH 爆破 |
| `ftp-brute` | FTP 爆破 |
| `mysql-brute` | MySQL 爆破 |
| `http-brute` | HTTP 认证爆破 |
| `smb-brute` | SMB 爆破 |

---

## 十三、使用技巧与注意事项

### 13.1 扫描速度

**时序模板（-T0 到 -T5）**：

| 模板 | 名称 | 说明 |
|------|------|------|
| `-T0` | Paranoid | 极慢，每 5 分钟发一个包，用于躲避 IDS |
| `-T1` | Sneaky | 慢速，每 15 秒一个包 |
| `-T2` | Polite | 礼貌，降低带宽使用 |
| `-T3` | Normal | 默认速度 |
| `-T4` | Aggressive | 快速，局域网推荐 |
| `-T5` | Insane | 疯狂，很快但可能漏报 |

```bash
# 快速扫描（推荐）
nmap -T4 192.168.1.1

# 极快（可能不准）
nmap -T5 192.168.1.1
```

### 13.2 性能优化

```bash
# 并行主机数
nmap --min-parallelism 100 192.168.1.0/24

# 最小/最大速率
nmap --min-rate 1000 192.168.1.0/24
nmap --max-rate 100 192.168.1.0/24

# 主机超时
nmap --host-timeout 5m 192.168.1.0/24
```

### 13.3 注意事项

1. **合法授权**：扫描前确保获得授权
2. **控制速率**：不要用 T5 扫描生产环境
3. **避开业务高峰**：在低峰期进行扫描
4. **白名单扫描**：将扫描 IP 加入 WAF 白名单
5. **分段扫描**：大网段分批扫描
6. **保留证据**：保存扫描结果

### 13.4 常见问题

**Q: 扫描结果不准确？**
- 可能被防火墙拦截，尝试 `-Pn` 跳过 ping
- 尝试不同的扫描类型（-sS / -sT / -sA）
- 降低扫描速度

**Q: 扫描太慢？**
- 使用 `-T4` 或 `-T5`
- 减少扫描端口范围
- 使用 `-n` 不做 DNS 解析
- 增加 `--min-rate`

---

> **延伸学习**：Nmap 是网络安全的基础工具，熟练掌握 Nmap 是渗透测试的第一步。建议学习 NSE 脚本开发，以及 Nmap 配合其他工具（如 Metasploit、Nessus）的使用。
