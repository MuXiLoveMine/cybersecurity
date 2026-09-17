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

---

## 十四、NSE 脚本开发

### 14.1 NSE 脚本结构

NSE（Nmap Scripting Engine）使用 Lua 语言编写脚本。每个 NSE 脚本必须包含以下字段：

```lua
-- 示例：自定义 HTTP 信息收集脚本
description = [[
自定义 HTTP 信息收集脚本
收集服务器标题、Server 头、X-Powered-By 等信息
]]

-- 脚本分类
categories = {"discovery", "safe"}

-- 依赖
dependencies = {"http-default-accounts"}

-- 作者
author = "Security Researcher"

-- 许可证
license = "Same as Nmap--See https://nmap.org/book/man-legal.html"

-- 端口规则（哪些端口触发脚本）
portrule = function(host, port)
    return port.protocol == "tcp" and port.state == "open"
end

-- 主执行函数
action = function(host, port)
    local result = {}
    
    -- 发送 HTTP 请求
    local response = http.get(host, port, "/")
    
    if response then
        -- 提取 Server 头
        if response.header["server"] then
            table.insert(result, "Server: " .. response.header["server"])
        end
        
        -- 提取 X-Powered-By
        if response.header["x-powered-by"] then
            table.insert(result, "X-Powered-By: " .. response.header["x-powered-by"])
        end
        
        -- 提取标题
        local title = string.match(response.body, "<title>(.-)</title>")
        if title then
            table.insert(result, "Title: " .. title)
        end
    end
    
    -- 返回结果
    if #result > 0 then
        return table.concat(result, "\n")
    end
end
```

### 14.2 NSE API 常用函数

```lua
-- ====== 网络操作 ======
local socket = nmap.new_socket()
socket:connect(host, port)
socket:send("GET / HTTP/1.0\r\n\r\n")
local status, data = socket:receive()
socket:close()

-- ====== HTTP 操作（需导入 http 库） ======
local http = require("http")
-- GET 请求
local response = http.get(host, port, "/path")
-- POST 请求
local response = http.post(host, port, "/login", nil, nil, "user=admin&pass=123")
-- 自定义头请求
local options = {header = {["User-Agent"] = "Custom/1.0"}}
local response = http.get(host, port, "/path", options)

-- ====== 字符串操作 ======
-- 正则匹配
local match = string.match(response.body, "version[%s]*=[%s]*([%d%.]+)")
-- 字符串分割
local lines = stdnse.strsplit("\n", response.body)

-- ====== 输出与日志 ======
stdnse.print_debug(1, "Debug message: %s", variable)
stdnse.verbose(1, "Verbose message")

-- ====== 脚本参数 ======
local args = nmap.registry.args
local timeout = stdnse.get_script_args("timeout") or 5

-- ====== 加密操作 ======
local openssl = require("openssl")
local md5 = openssl.md5("data")
local sha256 = openssl.sha256("data")

-- ====== 目标信息 ======
local ip = host.ip
local hostname = host.targetname
local os = host.os
```

### 14.3 自定义漏洞检测脚本

```lua
-- 检测特定 CVE 漏洞的脚本
description = [[
检测 CVE-2021-44228 (Log4Shell) 漏洞
通过发送特殊构造的请求检测目标是否存在 Log4j JNDI 注入漏洞
]]

author = "Security Team"
license = "Same as Nmap"
categories = {"vuln", "safe"}

portrule = function(host, port)
    local http_ports = {80, 443, 8080, 8443, 8888}
    for _, p in ipairs(http_ports) do
        if port.number == p and port.protocol == "tcp" then
            return true
        end
    end
    return false
end

action = function(host, port)
    local http = require("http")
    local stdnse = require("stdnse")
    
    -- 构造 JNDI 探测 Payload
    local payload = "${jndi:ldap://nmap-detector.example.com/a}"
    
    -- 在多个参数位置注入 Payload
    local paths = {"/", "/api", "/login", "/test"}
    local headers = {
        ["X-Api-Version"] = payload,
        ["User-Agent"] = payload,
        ["X-Forwarded-For"] = payload,
        ["Referer"] = payload,
    }
    
    for _, path in ipairs(paths) do
        local response = http.get(host, port, path, {header = headers})
        if response and response.status ~= nil then
            -- 检查是否有异常延迟（时间盲注检测）
            -- 或检查 DNS 回连
            return "Potential Log4Shell vulnerability detected"
        end
    end
end
```

---

## 十五、服务指纹识别

### 15.1 服务指纹识别原理

```
Nmap 服务指纹识别流程：
1. 连接目标端口
2. 发送一组探测数据（Probes）
3. 收集响应数据
4. 与 nmap-service-probes 数据库匹配
5. 输出服务名称和版本

指纹数据库位置：
- /usr/share/nmap/nmap-service-probes
- 包含数千种服务的指纹规则

探测策略：
- NULL 探测：不发送数据，等待服务主动发送 Banner
- 通用探测：发送常见协议探测数据
- RPC 探测：针对 RPC 服务
- TLS 探测：针对 SSL/TLS 服务
```

### 15.2 自定义服务探测

```bash
# 提高版本探测强度（0-9）
nmap -sV --version-intensity 9 192.168.1.1

# 轻量级探测（更快但可能漏掉信息）
nmap -sV --version-light 192.168.1.1

# 回退到端口扫描，不做版本探测
nmap -sV --version-intensity 0 192.168.1.1

# 指定探测端口
nmap -sV --version-intensity 5 -p 80,443,8080 192.168.1.1

# 添加自定义服务指纹
# 编辑 /usr/share/nmap/nmap-service-probes
# 添加自定义匹配规则
```

### 15.3 常见服务指纹特征

```
SSH 服务：
  OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
  特征：SSH-2.0-OpenSSH_7.9p1

HTTP 服务：
  Apache httpd 2.4.38 ((Debian))
  nginx 1.18.0 (Ubuntu)
  特征：Server 头

数据库服务：
  MySQL 5.7.31
  PostgreSQL 12.4
  特征：握手协议中的版本号

Redis：
  Redis 6.0.8
  特征：-ERR wrong number of arguments
  或 +PONG 响应
```

---

## 十六、防火墙/IDS 绕过扫描技术

### 16.1 高级绕过技术

```bash
# 1. SYN 扫描 + 分片 + 慢速
nmap -sS -f -T2 --data-length 50 192.168.1.1

# 2. 诱饵扫描（混合真实 IP）
nmap -sS -D 10.0.0.1,10.0.0.2,10.0.0.3,ME,RND:3 192.168.1.1
# ME = 本机地址，RND:3 = 随机3个IP

# 3. 源端口欺骗（利用防火墙白名单端口）
nmap -sS -g 53 192.168.1.1    # DNS 端口
nmap -sS -g 80 192.168.1.1    # HTTP 端口
nmap -sS --source-port 53 192.168.1.1

# 4. MAC 地址欺骗
nmap -sS --spoof-mac 0 192.168.1.1          # 随机 MAC
nmap -sS --spoof-mac 00:11:22:33:44:55 192.168.1.1  # 指定 MAC
nmap -sS --spoof-mac Apple 192.168.1.1     # 苹果厂商前缀

# 5. 空闲扫描（通过僵尸主机扫描）
# 需要找到一个空闲的僵尸主机
nmap -sI zombie_ip:port 192.168.1.1

# 6. 自定义 TCP Flag 组合
# 设置特定 Flag 组合绕过状态检测防火墙
nmap -sS --scanflags SYN,FIN,URG,PSH 192.168.1.1

# 7. 延迟和速率控制
nmap -sS --scan-delay 2s --max-rate 10 192.168.1.1
nmap -sS --max-retries 2 --host-timeout 30m 192.168.1.1

# 8. 分片 MTU 设置
nmap -sS -f --mtu 16 192.168.1.1    # 最小分片
nmap -sS -f --mtu 24 192.168.1.1
nmap -sS -f --mtu 32 192.168.1.1
```

### 16.2 IDS 规避策略

```
IDS 规避策略对比：

技术               | 隐蔽性 | 速度   | 可靠性
-------------------|--------|--------|--------
SYN 扫描           | 中     | 快     | 高
分片扫描           | 高     | 中     | 中
诱饵扫描           | 高     | 中     | 高
空闲扫描           | 极高   | 慢     | 中
慢速扫描           | 高     | 极慢   | 高
源端口欺骗         | 中     | 快     | 中
Flag 组合          | 中     | 中     | 低

组合策略（最隐蔽）：
nmap -sS -f -D RND:5 -g 53 --scan-delay 1s -T2 --data-length 25 192.168.1.1
```

---

## 十七、IPv6 扫描

```bash
# 1. 发现 IPv6 主机
nmap -6 -sn 2001:db8::/64

# 2. IPv6 端口扫描
nmap -6 -sS fe80::1%eth0
nmap -6 -p 80,443,22 2001:db8::1

# 3. IPv6 全面扫描
nmap -6 -A 2001:db8::1

# 4. IPv6 脚本扫描
nmap -6 --script=ipv6-info 2001:db8::1

# 5. 本地链路地址扫描
nmap -6 -sn -PR --send-eth fe80::/64%eth0

# 注意事项：
# - IPv6 地址空间巨大，全端口扫描不现实
# - 依赖邻居发现协议（NDP）发现主机
# - 使用 -6 参数启用 IPv6 模式
# - 链路本地地址需要指定接口（%eth0）
```

---

## 十八、Top 端口扫描优化

```bash
# 扫描最常用端口（快速，适合初步探测）
nmap --top-ports 100 192.168.1.1     # 前100常用端口
nmap --top-ports 1000 192.168.1.1    # 前1000常用端口

# Fast 模式（100个最常用端口）
nmap -F 192.168.1.1

# 优化策略：
# 1. 先快速扫描常用端口
nmap -sS -F -T4 192.168.1.1

# 2. 再全端口扫描（分批）
nmap -sS -p 1-32768 -T4 192.168.1.1
nmap -sS -p 32769-65535 -T4 192.168.1.1

# 3. 合并结果分析

# 4. 使用 nmap 的 --defeat-rst-ratelimit 选项
# 加速 filtered 端口判定
nmap -sS -p- --defeat-rst-ratelimit -T4 192.168.1.1

# 5. UDP 优化（只扫常用 UDP 端口）
nmap -sU --top-ports 50 -T4 192.168.1.1
```

---

## 十九、Zenmap 可视化

### 19.1 Zenmap 界面

```
Zenmap 是 Nmap 的图形界面版本：

功能：
- 图形化扫描配置
- 扫描结果可视化
- 拓扑图绘制
- 扫描结果对比
- 扫描配置文件管理

扫描配置文件：
  Intense scan        - 深入扫描（-T4 -A -v）
  Intense scan + UDP  - 深入扫描+UDP
  Intense scan, all TCP ports - 全TCP端口
  Intense scan, no ping      - 不Ping扫描
  Ping scan           - 仅Ping扫描
  Quick scan          - 快速扫描（-T4 -F）
  Quick scan plus     - 快速增强扫描
  Quick traceroute    - 快速路由追踪
  Regular scan        - 常规扫描
  Slow comprehensive scan - 慢速全面扫描
```

### 19.2 拓扑图功能

```
Zenmap 拓扑图：
- 显示扫描主机之间的网络拓扑
- 可视化网络结构
- 标注路由器和防火墙位置
- 支持导出拓扑图

使用方式：
1. Tools → Topology → Fingerprint
2. 可查看网络中各主机的连接关系
3. 可查看路由跳数
4. 可导出为图片
```

---

## 二十、Nmap 输出解析自动化

### 20.1 XML 输出解析

```python
#!/usr/bin/env python3
"""Nmap XML 输出解析脚本"""
import xml.etree.ElementTree as ET

def parse_nmap_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    results = []
    
    for host in root.findall('host'):
        ip = host.find('address').get('addr')
        
        host_info = {
            'ip': ip,
            'status': host.find('status').get('state'),
            'ports': [],
            'os': None
        }
        
        # 解析端口信息
        ports = host.find('ports')
        if ports:
            for port in ports.findall('port'):
                port_info = {
                    'port': port.get('portid'),
                    'protocol': port.get('protocol'),
                    'state': port.find('state').get('state'),
                    'service': None,
                    'version': None
                }
                
                service = port.find('service')
                if service:
                    port_info['service'] = service.get('name')
                    port_info['version'] = service.get('version')
                    port_info['product'] = service.get('product')
                
                host_info['ports'].append(port_info)
        
        # 解析操作系统信息
        os_elem = host.find('os')
        if os_elem:
            osmatch = os_elem.find('osmatch')
            if osmatch:
                host_info['os'] = osmatch.get('name')
        
        results.append(host_info)
    
    return results

# 使用示例
results = parse_nmap_xml('scan_result.xml')
for host in results:
    print(f"\n{host['ip']} ({host['status']})")
    if host['os']:
        print(f"  OS: {host['os']}")
    for port in host['ports']:
        if port['state'] == 'open':
            print(f"  {port['port']}/{port['protocol']} - "
                  f"{port['service']} {port.get('version', '')}")
```

### 20.2 Grepable 格式解析

```bash
# Grepable 格式一行一个主机，便于 grep
nmap -oG scan.gnmap 192.168.1.0/24

# 提取开放 22 端口的主机
grep "22/open" scan.gnmap | awk '{print $2}'

# 提取所有开放端口
grep -oP '\d+/open' scan.gnmap | sort -t/ -n | uniq -c | sort -rn

# 提取运行 HTTP 的主机
grep "80/open\|443/open\|8080/open" scan.gnmap | awk '{print $2}'

# 提取特定服务
grep -i "mysql\|postgresql\|redis" scan.gnmap | awk '{print $2}'

# 导出为 CSV
awk '{print $2 "," $5}' scan.gnmap > hosts.csv
```

---

## 二十一、实战扫描案例

### 21.1 案例一：企业内网安全评估

```bash
# 阶段一：存活主机发现
nmap -sn -PR -n 10.0.0.0/24 -oA discovery

# 阶段二：关键端口快速扫描
nmap -sS -F -T4 -iL discovery.gnmap -oA quick_scan

# 阶段三：重点主机深入扫描
# 提取开放 Web 服务的主机
grep "80/open\|443/open" quick_scan.gnmap | awk '{print $2}' > web_hosts.txt

# 对 Web 主机进行深入扫描
nmap -sV -sC -p 80,443,8080,8443 --script=http-enum,http-headers \
     -iL web_hosts.txt -oA web_deep

# 阶段四：数据库服务扫描
nmap -sV -p 3306,1433,5432,6379,27017,9200 -iL discovery.gnmap -oA db_scan

# 阶段五：漏洞扫描
nmap --script=vuln -iL discovery.gnmap -oA vuln_scan
```

### 21.2 案例二：隐蔽渗透测试扫描

```bash
# 目标有 IDS/IPS，需要隐蔽扫描

# 1. 慢速 SYN 扫描 + 分片
nmap -sS -f -T2 --scan-delay 5s -n -Pn -p 22,80,443,3306 192.168.1.1

# 2. 使用诱饵
nmap -sS -D RND:10 -T2 -n -Pn -p 22,80,443 192.168.1.1

# 3. 源端口欺骗（如果防火墙允许 DNS 流量）
nmap -sS -g 53 -T3 -n -Pn -p 1-1000 192.168.1.1

# 4. 空闲扫描（最隐蔽）
nmap -sI zombie_ip -Pn -n -p 1-1000 192.168.1.1

# 5. 分段扫描（避免连续端口扫描）
nmap -sS -p 1-100,200-300,400-500 -T2 -n -Pn 192.168.1.1
nmap -sS -p 101-199,301-399,501-600 -T2 -n -Pn 192.168.1.1
```

### 21.3 案例三：云服务器安全检查

```bash
# 检查云服务器是否暴露了不应该公开的服务

# 1. 扫描所有端口
nmap -p- -sS -T4 -n -Pn cloud_server_ip

# 2. 重点检查高危端口
nmap -sV -p 22,23,3306,6379,27017,9200,11211,2375 \
     --script=default,vuln cloud_server_ip

# 3. 检查是否暴露 Redis
nmap -p 6379 --script redis-info cloud_server_ip

# 4. 检查是否暴露 Docker API
nmap -p 2375 --script docker-version cloud_server_ip

# 5. 检查是否暴露 Elasticsearch
nmap -p 9200 --script http-enum cloud_server_ip

# 6. 生成完整报告
nmap -p- -sV -sC -O -T4 -oA full_scan cloud_server_ip
```
