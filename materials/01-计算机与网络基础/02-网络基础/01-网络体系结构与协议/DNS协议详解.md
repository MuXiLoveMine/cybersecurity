# DNS 协议详解

> 本文系统介绍 DNS（域名系统），从域名结构、记录类型、解析流程，到 Linux 配置实践、DNS 服务器搭建与安全加固。兼顾原理深度与实战操作，面向系统管理员、运维工程师和安全工程师。引用 RFC 1035、RFC 4033 等核心规范。

---

## 目录

- [一、基本概念](#一基本概念)
- [二、DNS 记录类型](#二dns-记录类型)
- [三、解析流程](#三解析流程)
- [四、Linux 实践](#四linux-实践)
- [五、安全与常见问题](#五安全与常见问题)
- [附：优化后的提示词模板](#附优化后的提示词模板)

---

## 一、基本概念

### 1.1 什么是 DNS

**DNS（Domain Name System，域名系统）**是互联网的"电话簿"，它将人类易记的**域名**（如 `www.example.com`）翻译成机器可读的**IP 地址**（如 `93.184.216.34`）。

DNS 是一个**分布式、层次化**的数据库系统，工作在应用层，默认使用 UDP 的 53 端口（大响应和区域传输使用 TCP 53）。

| 核心特性 | 说明 |
|---------|------|
| **分布式** | 数据分散存储在全球各地的 DNS 服务器中 |
| **层次化** | 域名结构和服务器都是树状层级的 |
| **容错性** | 多台服务器冗余，单台故障不影响 |
| **缓存机制** | 多级缓存提升解析速度，减轻根服务器压力 |
| **UDP 为主** | 响应 < 512 字节时用 UDP，更大用 TCP（EDNS 后可更大） |

> DNS 的原始规范是 **RFC 1034** 和 **RFC 1035**（1987 年），后续有大量扩展 RFC。

### 1.2 域名结构

域名是**从右到左**的层级结构，用点（.）分隔，最右边是顶级域，最左边是主机名。

```
      根域（.）← 最顶层，通常省略不写
        │
   ┌────┴────┐
   │         │
  com       org       ← 顶级域（TLD，Top-Level Domain）
   │         │
 example   wikipedia   ← 二级域（注册域，Second-Level Domain）
   │         │
  www      en        ← 三级域/子域（Subdomain / Host）
   │         │
 mail     www       ← 四级域/主机名
```

| 层级 | 名称 | 英文 | 例子 | 说明 |
|------|------|------|------|------|
| 最顶层 | 根域 | Root Domain | `.` | 全球 13 组根服务器 |
| 第一层 | 顶级域 | TLD | `com`、`org`、`cn`、`net` | 由注册管理机构管理 |
| 第二层 | 二级域 | SLD | `example.com` | 企业/个人注册的域名 |
| 第三层+ | 子域 | Subdomain | `www.example.com` | 域名所有者自行管理 |
| 最左边 | 主机名 | Hostname | `mail.example.com` | 具体的主机/服务 |

**完全限定域名（FQDN, Fully Qualified Domain Name）**：以点结尾的完整域名，如 `www.example.com.`。平时我们输入的域名最后那个点一般省略不写。

**顶级域（TLD）分类**：

| 类型 | 例子 | 说明 |
|------|------|------|
| **通用顶级域** | `.com`、`.org`、`.net`、`.info` | gTLD，最常见 |
| **国家代码顶级域** | `.cn`、`.us`、`.jp`、`.uk` | ccTLD，两个字母 |
| **赞助顶级域** | `.edu`、`.gov`、`.mil` | sTLD，有限制条件 |
| **新通用顶级域** | `.app`、`.io`、`.dev`、`.xyz` | 新 gTLD，上千种 |
| **反向解析域** | `.arpa` | 特殊用途，IP→域名反向解析 |

### 1.3 正向解析与反向解析

| 类型 | 英文 | 作用 | 典型记录 |
|------|------|------|---------|
| **正向解析** | Forward DNS | 域名 → IP 地址 | A、AAAA、CNAME、MX 等 |
| **反向解析** | Reverse DNS | IP 地址 → 域名 | PTR 记录 |

反向解析使用特殊的域名空间：
- IPv4：`IP反序.in-addr.arpa`，如 `1.168.192.in-addr.arpa` 对应 `192.168.1.x`
- IPv6：`IP反序.ip6.arpa`

```
正向解析：  www.example.com  →  93.184.216.34
反向解析：  34.216.184.93.in-addr.arpa  →  www.example.com
                          ↑
                    IP 地址倒过来写
```

### 1.4 递归查询与迭代查询

DNS 有两种基本查询模式：

| 模式 | 英文 | 特点 | 典型场景 |
|------|------|------|---------|
| **递归查询** | Recursive Query | 服务器替你查到底，返回最终结果 | 客户端 → 本地 DNS（递归解析器） |
| **迭代查询** | Iterative Query | 服务器返回"我不知道，但你可以去问 XX" | 递归解析器 → 根/TLD/权威服务器 |

```
完整解析流程（以查询 www.example.com 为例）：

客户端
  │
  │ ① 递归查询 www.example.com
  ▼
本地 DNS（递归解析器）
  │
  │ ② 迭代查询 → 问根服务器：www.example.com 在哪？
  ▼
根服务器 ── "我不知道.com 的，去问 TLD 服务器"
  │
  │ ③ 迭代查询 → 问 .com TLD 服务器
  ▼
.com TLD 服务器 ── "我不知道 example.com 的，去问它的权威服务器"
  │
  │ ④ 迭代查询 → 问 example.com 权威服务器
  ▼
example.com 权威服务器 ── "www.example.com = 93.184.216.34"
  │
  │ ⑤ 返回结果给客户端，同时缓存起来
  ▼
客户端得到 IP 地址
```

**角色区分**：

| 角色 | 英文 | 功能 | 例子 |
|------|------|------|------|
| **存根解析器** | Stub Resolver | 客户端的简易解析器，只负责向递归服务器发请求 | 操作系统的 DNS 客户端 |
| **递归解析器** | Recursive Resolver | 替客户端做完整的迭代查询 | ISP DNS、8.8.8.8、1.1.1.1、本地 DNS 服务器 |
| **权威服务器** | Authoritative Server | 持有某个域的原始数据，提供权威回答 | 域名注册商 DNS、自建 BIND |
| **根服务器** | Root Server | DNS 树的根，知道所有 TLD 的权威服务器 | 全球 13 组（A~M） |
| **TLD 服务器** | TLD Server | 管理某个顶级域的权威服务器 | .com 服务器、.cn 服务器 |

---

## 二、DNS 记录类型

### 2.1 核心记录类型

| 类型 | 全称 | 作用 | 示例 |
|------|------|------|------|
| **A** | Address | IPv4 地址 | `www → 93.184.216.34` |
| **AAAA** | IPv6 Address | IPv6 地址 | `www → 2606:2800:220:1:248:1893:25c8:1946` |
| **CNAME** | Canonical Name | 别名（指向另一个域名） | `blog → example.com.` |
| **MX** | Mail Exchanger | 邮件服务器（带优先级） | `@ → 10 mail.example.com.` |
| **NS** | Name Server | 域名服务器（权威服务器地址） | `@ → ns1.example.com.` |
| **TXT** | Text | 文本记录（任意用途） | `v=spf1 include:_spf.google.com ~all` |
| **SOA** | Start of Authority | 起始授权（域的管理信息） | 见下方详解 |
| **PTR** | Pointer | 反向解析（IP→域名） | `34.216.184.93.in-addr.arpa → www.example.com.` |
| **SRV** | Service Locator | 服务定位（端口+权重+优先级） | `_sip._tcp → 10 60 5060 sip.example.com.` |
| **CAA** | Certification Authority Authorization | 允许哪些 CA 发证书 | `0 issue "letsencrypt.org"` |
| **SPF** | Sender Policy Framework | 发件人策略（防邮件伪造） | 现在通常用 TXT 记录承载 |
| **DKIM** | DomainKeys Identified Mail | 邮件签名（防伪造） | 用 TXT 记录承载公钥 |
| **DMARC** | Domain-based Message Authentication | 邮件认证策略 | 用 TXT 记录（_dmarc 子域） |
| **NAPTR** | Naming Authority Pointer | 命名权威指针（ENUM 等） | 比较少见 |

### 2.2 各记录详解

#### （1）A / AAAA 记录

最常用的记录，把域名映射到 IP 地址。

```
格式：  主机名  IN  A     IPv4地址
        主机名  IN  AAAA  IPv6地址

示例：
www.example.com.    IN  A       93.184.216.34
www.example.com.    IN  AAAA    2606:2800:220:1:248:1893:25c8:1946
```

#### （2）CNAME 记录

别名记录，把一个域名指向另一个域名。查询时 DNS 会"跟着"CNAME 继续解析，直到找到 A/AAAA 记录。

```
格式：  别名  IN  CNAME  规范域名

示例：
blog.example.com.   IN  CNAME   example.com.
cdn.example.com.    IN  CNAME   cdn-provider.net.
```

> **注意**：
> - CNAME 指向的是域名，不是 IP
> - 根域（@ / example.com）不能设 CNAME（会和其他记录冲突）
> - CNAME 后面可以再接 CNAME，但链太长影响性能
> - MX、NS、TXT 等记录不能和 CNAME 共存

#### （3）MX 记录

邮件交换记录，指定接收该域名邮件的服务器。有优先级数字，数字越小优先级越高。

```
格式：  域名  IN  MX  优先级  邮件服务器

示例：
example.com.   IN  MX  10  mail1.example.com.
example.com.   IN  MX  20  mail2.example.com.
example.com.   IN  MX  50  backup.other.com.
```

发送邮件时，先查 MX 记录，按优先级从低到高尝试连接。10 优先，连不上再试 20，还不行试 50。

#### （4）NS 记录

域名服务器记录，指定这个域由哪些权威 DNS 服务器管理。

```
格式：  域名  IN  NS  服务器域名

示例：
example.com.   IN  NS  ns1.example.com.
example.com.   IN  NS  ns2.example.com.
```

> 通常至少有 2 条 NS 记录（冗余）。NS 记录对应的服务器必须有 A/AAAA 记录（胶水记录，Glue Record），否则解析器不知道 NS 的 IP。

#### （5）SOA 记录

起始授权记录，每个域有且只有一条 SOA，包含这个域的管理信息。

```
格式：
域名  IN  SOA  主NS 管理员邮箱 (
        序列号     ; 版本号，每次修改 +1
        刷新时间    ; 从服务器多久查一次更新
        重试时间    ; 刷新失败后多久重试
        过期时间    ; 多久联系不上主服务器就失效
        最小TTL     ; 否定缓存的 TTL
        )

示例：
example.com.  IN  SOA  ns1.example.com. admin.example.com. (
        2024092401  ; Serial
        3600        ; Refresh (1 hour)
        900         ; Retry (15 min)
        604800      ; Expire (1 week)
        86400       ; Minimum TTL (1 day)
        )
```

#### （6）TXT 记录

文本记录，可存任意文本，用途广泛。

```
示例：

# SPF（邮件发件人验证）
example.com.  IN  TXT  "v=spf1 include:_spf.google.com ~all"

# DKIM（邮件域名密钥）
selector._domainkey.example.com.  IN  TXT  "v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb..."

# DMARC（邮件策略）
_dmarc.example.com.  IN  TXT  "v=DMARC1; p=none; rua=mailto:dmarc@example.com"

# 域名所有权验证（Google、Let's Encrypt 等）
_acme-challenge.example.com.  IN  TXT  "abcdef123456"
```

#### （7）PTR 记录

指针记录，用于反向解析（IP → 域名），存在 `.in-addr.arpa`（IPv4）或 `.ip6.arpa`（IPv6）域中。

```
格式：  反向IP.in-addr.arpa.  IN  PTR  域名

示例：
34.216.184.93.in-addr.arpa.  IN  PTR  www.example.com.
1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa.  IN  PTR  www.example.com.
```

> 反向解析常用于邮件服务器验证（防止垃圾邮件）、日志记录（IP 转域名显示）。

#### （8）SRV 记录

服务定位记录，指定某个服务在哪台服务器的哪个端口上，还有权重和优先级。

```
格式：  _服务._协议.域名  IN  SRV  优先级  权重  端口  目标

示例：
_sip._tcp.example.com.   IN  SRV  10 60 5060 sip1.example.com.
_sip._tcp.example.com.   IN  SRV  20 40 5060 sip2.example.com.
_xmpp-server._tcp.example.com.  IN  SRV  5 0 5269 xmpp.example.com.
```

#### （9）CAA 记录

证书颁发机构授权记录，指定哪些 CA 可以为该域名颁发证书。

```
格式：  域名  IN  CAA  标志  标签  值

标志：
  0 = 关键标志不设置
  1 = 关键标志（不认识的 CA 必须拒绝）

标签：
  issue     = 允许为该域颁发证书
  issuewild = 允许颁发通配符证书
  iodef     = 违规报告地址

示例：
example.com.  IN  CAA  0 issue "letsencrypt.org"
example.com.  IN  CAA  0 issue "digicert.com"
example.com.  IN  CAA  0 iodef "mailto:caa@example.com"
```

### 2.3 记录类型速查表

| 用途 | 推荐记录类型 |
|------|-------------|
| 域名 → IPv4 | A |
| 域名 → IPv6 | AAAA |
| 别名 → 另一个域名 | CNAME |
| 邮件服务器 | MX |
| 域名服务器 | NS |
| 反向解析（IP→域名） | PTR |
| 任意文本/验证/SPF/DKIM | TXT |
| 服务定位（端口+权重） | SRV |
| 限制证书颁发机构 | CAA |
| 域管理信息 | SOA |

---

## 三、解析流程

### 3.1 完整解析流程

```
查询 www.example.com 的完整过程：

1. 浏览器 → 操作系统
   │ "www.example.com 的 IP 是多少？"
   ▼
2. 操作系统检查：
   ├─ 浏览器缓存？→ 有就返回
   ├─ 系统缓存？→ 有就返回
   └─ hosts 文件？→ 有就返回

3. 没有 → 向本地 DNS 服务器（递归解析器）发递归查询
   ▼
4. 递归解析器检查自己的缓存
   ├─ 有缓存？→ 返回缓存结果
   └─ 没有 → 开始迭代查询

5. 迭代查询（一步步问）：
   a) 问根服务器 → 返回 .com TLD 服务器地址
   b) 问 .com TLD → 返回 example.com 权威服务器地址
   c) 问 example.com 权威 → 返回 www.example.com 的 A 记录

6. 递归解析器把结果返回给客户端，并缓存起来（按 TTL 时间）

7. 浏览器拿到 IP，建立 TCP 连接，发 HTTP 请求
```

### 3.2 DNS 缓存与 TTL

**TTL（Time To Live）**：DNS 记录的存活时间（秒），告诉解析器可以缓存多久。

| 缓存层级 | 位置 | 说明 |
|---------|------|------|
| **浏览器缓存** | 浏览器内存 | 几分钟到几小时，浏览器自己管理 |
| **操作系统缓存** | 系统内存 | nscd / systemd-resolved 等 |
| **递归解析器缓存** | ISP/公共 DNS 服务器 | 按 TTL 缓存，用户共享 |
| **权威服务器** | 权威 DNS | 原始数据，TTL 由权威设置 |

```
TTL 经验值：
  - 稳定服务：3600（1 小时）~ 86400（1 天）
  - 即将变更：降到 300（5 分钟）甚至更低
  - 变更后：改回正常值（减少权威服务器压力）
  - TXT 验证：300（5 分钟，快速生效）
```

### 3.3 EDNS

**EDNS（Extension Mechanisms for DNS，RFC 2671 / RFC 6891）**是 DNS 的扩展机制，解决了传统 DNS 响应 512 字节的限制。

| 特性 | 传统 DNS | EDNS |
|------|---------|------|
| **UDP 最大响应** | 512 字节 | 可达 4096 字节（或更大） |
| **支持 DNSSEC** | 困难 | 支持 |
| **支持的选项** | 少 | 多（ECS、Cookie 等） |

EDNS 不修改 DNS 协议，而是通过附加伪资源记录（OPT RR）来传递扩展信息，向后兼容。

### 3.4 DNSSEC 基础

**DNSSEC（DNS Security Extensions，RFC 4033-4035）** 给 DNS 回答加上数字签名，确保：

| 安全目标 | 说明 |
|---------|------|
| **数据完整性** | 数据在传输中没有被篡改 |
| **来源认证** | 数据确实来自声称的权威服务器 |
| **已验证的不存在** | NXDOMAIN（不存在）的回答也是真实的 |

```
DNSSEC 的信任链：

根区域（信任锚，Trust Anchor）
  │ 用根 ZSK 签名
  ▼
TLD 区域（.com）
  │ 用 TLD ZSK 签名，用 TLD KSK 签名，KSK 又被上一级签名
  ▼
二级域（example.com）
  │ 用自己的 ZSK 签名
  ▼
具体记录（A、MX 等）
  每条记录都有 RRSIG（签名）

验证：每条记录的 RRSIG → 用该区的 DNSKEY 验证 → DNSKEY 用 DS 记录验证 →
     DS 在上一级区域签名 → ... → 一直到根（信任锚）
```

| 概念 | 说明 |
|------|------|
| **RRSIG** | Resource Record Signature，资源记录签名 |
| **DNSKEY** | DNS 公钥（ZSK = 区域签名密钥，KSK = 密钥签名密钥） |
| **DS** | Delegation Signer，委托签名者，存在父域 |
| **NSEC / NSEC3** | Next Secure，证明某记录不存在 |
| **信任锚** | Trust Anchor，验证起点（通常是根的 DNSKEY） |

> DNSSEC 只能保证数据真实和完整，**不提供保密性**（查询内容还是明文的）。加密传输用 DoH / DoT。

---

## 四、Linux 实践

### 4.1 系统 DNS 配置文件

#### （1）/etc/hosts — 本地 hosts 文件

静态域名映射，优先级最高（取决于 nsswitch.conf），DNS 查不到的或想覆盖的可以写在这里。

```
格式：  IP地址   主机名  [别名...]

示例：
127.0.0.1       localhost
127.0.1.1       myserver
::1             localhost ip6-localhost ip6-loopback
192.168.1.100   server01
10.0.0.5        db.internal db
```

> ⚠️ **修改提示**：修改 `/etc/hosts` 前建议先备份：`cp /etc/hosts /etc/hosts.bak`。错误的 hosts 配置可能导致服务异常。

#### （2）/etc/resolv.conf — DNS 解析配置

```
格式：
nameserver <DNS服务器IP>     # DNS 服务器，最多 3 个
search <域名>                 # 搜索域（补全短域名）
domain <域名>                 # 本地域名
options <选项>                # 选项

示例：
nameserver 8.8.8.8
nameserver 8.8.4.4
search example.com internal.com
options timeout:2 attempts:2 rotate
```

| 常用选项 | 说明 |
|---------|------|
| `timeout:n` | 查询超时时间（秒），默认 5 |
| `attempts:n` | 尝试次数，默认 2 |
| `rotate` | 轮询使用 nameserver（负载均衡） |
| `ndots:n` | 域名中点的数量少于 n 时才用 search |
| `single-request-reopen` | 分开 A 和 AAAA 查询（某些有问题的防火墙） |

> ⚠️ **修改提示**：
> - 备份：`cp /etc/resolv.conf /etc/resolv.conf.bak`
> - 很多现代系统 `/etc/resolv.conf` 是符号链接（被 systemd-resolved 或 NetworkManager 管理），直接修改可能被覆盖
> - systemd-resolved 管理的系统用 `resolvectl dns` 或修改 netplan/NetworkManager 配置

#### （3）/etc/nsswitch.conf — 名称服务切换

指定系统查找各种信息的顺序（不仅是 DNS，还包括用户、组等）。

```
# 主机名解析顺序：先查 files（/etc/hosts），再查 dns（/etc/resolv.conf）
hosts:          files dns

# 其他常见配置
passwd:         files systemd
group:          files systemd
shadow:         files
networks:       files
protocols:      files
services:       files
```

修改 `hosts:` 那一行可以调整解析顺序，比如 `hosts: dns files` 就会先查 DNS 再查 hosts（不推荐）。

### 4.2 systemd-resolved 与 NetworkManager

现代 Linux 发行版（Ubuntu 18.04+、RHEL 8+、Fedora）通常用 systemd-resolved 管理 DNS。

```bash
# ===== systemd-resolved =====

# 查看状态
systemctl status systemd-resolved
resolvectl status
systemd-resolve --status      # 旧命令（兼容）

# 查看 DNS 服务器
resolvectl dns
resolvectl dns eth0           # 指定接口

# 查看域名
resolvectl domain

# 设置 DNS 服务器🔑
resolvectl dns eth0 8.8.8.8 8.8.4.4

# 设置搜索域🔑
resolvectl domain eth0 example.com

# 刷新缓存🔑
resolvectl flush-caches

# 查看缓存统计
resolvectl statistics

# DNS 测试
resolvectl query example.com
resolvectl query -t MX gmail.com

# ===== NetworkManager =====

# 查看连接
nmcli connection show

# 修改 DNS🔑
nmcli connection modify "Wired connection 1" ipv4.dns "8.8.8.8 8.8.4.4"
nmcli connection modify "Wired connection 1" ipv4.dns-search "example.com"
nmcli connection up "Wired connection 1"

# DNS 模式
nmcli connection modify <name> ipv4.ignore-auto-dns yes   # 忽略 DHCP 的 DNS
```

> `/etc/resolv.conf` 的三种管理方式：
> 1. **systemd-resolved 管理**：`/etc/resolv.conf → ../run/systemd/resolve/stub-resolv.conf`，用 `resolvectl` 管理
> 2. **NetworkManager 管理**：NM 直接写 resolv.conf
> 3. **手动管理**：自己编辑，不被任何服务覆盖

### 4.3 查询命令

#### （1）dig — 推荐使用，信息最详细

```
语法：dig [@服务器] [域名] [类型] [选项]

常用选项：
  @server         指定 DNS 服务器
  -t type         指定记录类型（A/AAAA/MX/NS/TXT...）
  -x IP           反向解析
  +short          简短输出（只显示答案）
  +noall +answer  只显示回答部分
  +trace          跟踪完整解析过程（从根开始）
  +tcp            用 TCP 查询
  +dnssec         请求 DNSSEC 记录
  -4 / -6         只用 IPv4 / IPv6
  -f file         从文件批量查询
```

```bash
# 基本查询（A 记录）
dig example.com
dig @8.8.8.8 example.com                # 指定 DNS 服务器

# 指定记录类型
dig example.com MX
dig example.com NS
dig example.com TXT
dig example.com AAAA
dig example.com SOA
dig example.com ANY                       # 所有类型（很多服务器拒绝）

# 简短输出
dig +short example.com
dig +short example.com MX
dig +short example.com NS

# 反向解析
dig -x 8.8.8.8
dig -x 2001:4860:4860::8888

# 跟踪完整解析过程（从根查起，看每一步）
dig +trace example.com

# DNSSEC
dig +dnssec example.com
dig +dnssec +multi example.com           # 多行显示更易读

# TCP 查询（大响应用）
dig +tcp example.com ANY

# 批量查询
dig -f domains.txt

# 只看回答部分
dig +noall +answer example.com MX

# 查询特定子域
dig www.example.com
dig mail.example.com MX
_dmarc.example.com TXT
```

#### （2）nslookup — 经典工具，跨平台

```bash
# 基本查询
nslookup example.com
nslookup example.com 8.8.8.8            # 指定服务器

# 指定类型
nslookup -type=mx gmail.com
nslookup -type=ns example.com
nslookup -type=txt example.com
nslookup -type=aaaa example.com

# 反向解析
nslookup 8.8.8.8

# 交互模式
nslookup
> server 8.8.8.8
> set type=mx
> gmail.com
> exit
```

#### （3）host — 简单工具

```bash
# 基本查询
host example.com
host example.com 8.8.8.8               # 指定服务器

# 指定类型
host -t mx gmail.com
host -t ns example.com
host -t txt example.com
host -t aaaa example.com
host -t soa example.com

# 反向解析
host 8.8.8.8

# 详细输出
host -v example.com
host -a example.com                    # 所有类型
```

#### （4）其他工具

```bash
# whois — 域名注册信息查询
whois example.com
whois -h whois.verisign-grs.com example.com   # 指定注册局

# ping 也可以看解析结果（A 记录）
ping -c 1 example.com

# getent — 通过系统 NSS 查询（走 /etc/nsswitch.conf，模拟真实解析）
getent hosts example.com
getent ahosts example.com             # 所有地址
```

### 4.4 DNS 服务器搭建

#### （1）dnsmasq — 轻量级 DNS/DHCP 服务器

适合小型网络、本地开发环境、家庭路由。

```bash
# 安装
# Debian/Ubuntu: apt install dnsmasq
# RHEL/CentOS: yum install dnsmasq（EPEL 源）

# 配置文件：/etc/dnsmasq.conf

# 常用配置：
# 监听地址
listen-address=127.0.0.1,192.168.1.1

# 上游 DNS 服务器
server=8.8.8.8
server=8.8.4.4
server=1.1.1.1

# 本地域名（从 /etc/hosts 读取）
expand-hosts
domain=example.com
local=/example.com/

# 自定义 DNS 记录
address=/dev.local/127.0.0.1
address=/api.example.com/192.168.1.100
cname=alias.example.com,real.example.com

# MX 记录
mx-host=example.com,mail.example.com,10

# 缓存大小
cache-size=1000

# 不转发没有点的名字
domain-needed

# 不转发私有地址的反向查询
bogus-priv

# 启动/重启
systemctl start dnsmasq
systemctl enable dnsmasq

# 测试
dig @localhost example.com
```

#### （2）BIND 9 — 功能最全面的 DNS 服务器

ISC BIND 是最广泛使用的 DNS 服务器软件，可做权威服务器和递归服务器。

```bash
# 安装
# Debian/Ubuntu: apt install bind9
# RHEL/CentOS: yum install bind

# 主配置文件：
# Debian/Ubuntu: /etc/bind/named.conf
# RHEL/CentOS:   /etc/named.conf

# 配置文件结构：
#   named.conf            主配置
#   named.conf.options    全局选项
#   named.conf.local      本地区域
#   named.conf.default-zones  默认区域（根等）

# ===== 作为缓存/递归 DNS 服务器 =====

# /etc/bind/named.conf.options
options {
    directory "/var/cache/bind";
    listen-on { any; };
    listen-on-v6 { any; };

    # 允许递归的客户端
    allow-recursion { 127.0.0.1; 192.168.1.0/24; };
    allow-query { any; };

    # 转发器（可选，转发到上游 DNS）
    forwarders {
        8.8.8.8;
        8.8.4.4;
    };
    # forward only;  # 只转发，不自己迭代查询

    dnssec-validation auto;
};

# ===== 作为权威服务器（example.com 主区域） =====

# /etc/bind/named.conf.local
zone "example.com" {
    type master;
    file "/etc/bind/db.example.com";
    allow-transfer { 192.168.1.2; };   # 允许从服务器传输
    also-notify { 192.168.1.2; };       # 变更时通知从服务器
};

# 区域文件 /etc/bind/db.example.com
$TTL 3600
@   IN  SOA  ns1.example.com. admin.example.com. (
            2024092401  ; Serial
            3600        ; Refresh
            900         ; Retry
            604800      ; Expire
            86400       ; Minimum TTL
            )

    IN  NS   ns1.example.com.
    IN  NS   ns2.example.com.
    IN  MX   10 mail.example.com.
    IN  MX   20 mail2.example.com.
    IN  TXT  "v=spf1 mx ~all"

ns1     IN  A    192.168.1.1
ns2     IN  A    192.168.1.2
mail    IN  A    192.168.1.10
mail2   IN  A    192.168.1.11
www     IN  A    93.184.216.34
api     IN  A    192.168.1.100
blog    IN  CNAME www
```

```bash
# 检查配置语法
named-checkconf
named-checkzone example.com /etc/bind/db.example.com

# 启动服务
systemctl start named       # RHEL
systemctl start bind9       # Debian
systemctl enable named

# 测试
dig @localhost example.com
dig @localhost example.com MX
dig @localhost example.com NS
```

#### （3）CoreDNS — 云原生 DNS 服务器

Go 语言编写，插件化架构，Kubernetes 默认 DNS。

```bash
# Corefile 配置示例
.:53 {
    errors
    health
    ready

    # 缓存插件
    cache 30

    # 负载均衡上游 DNS
    forward . 8.8.8.8 8.8.4.4 1.1.1.1 {
        policy round_robin
    }

    # 本地 hosts 插件
    hosts /etc/coredns/hosts {
        fallthrough
    }

    loop
    reload
    loadbalance
}

# 启动
coredns -conf Corefile
```

### 4.5 抓包分析 🔑

```bash
# ===== tcpdump 抓 DNS =====

# 抓取 53 端口（UDP + TCP）
tcpdump -i any -n 'port 53'
tcpdump -i any -n 'udp port 53'         # 仅 UDP
tcpdump -i any -n 'tcp port 53'         # 仅 TCP（区域传输/大响应）

# 保存到文件
tcpdump -i any -n 'port 53' -w dns.pcap
tcpdump -i any -n 'port 53' -c 100 -w dns.pcap   # 抓 100 个包

# 读取 pcap
tcpdump -r dns.pcap -n

# 更详细的输出（看到查询内容）
tcpdump -i any -n 'port 53' -A            # ASCII
tcpdump -i any -n 'port 53' -X            # 十六进制 + ASCII

# 过滤特定域名（需要一定偏移计算，用 -A + grep 更简单）
tcpdump -i any -n 'port 53' -A | grep -i example.com

# 只看查询（QR=0）或响应（QR=1）
# DNS 头部第 3 位是 QR 位，比较复杂，通常直接看内容即可

# 查看查询类型和响应码
tcpdump -i any -n 'udp port 53' -vvv

# ===== 用 dig 模拟各种查询配合抓包 =====

# 终端 1：抓包
tcpdump -i lo -n 'port 53' -w /tmp/dns.pcap

# 终端 2：各种查询
dig @127.0.0.1 example.com
dig @127.0.0.1 example.com MX
dig @127.0.0.1 -x 8.8.8.8

# 用 tshark 分析（Wireshark 命令行版）
tshark -r dns.pcap
tshark -r dns.pcap -Y "dns.qry.name == example.com"
tshark -r dns.pcap -T fields -e dns.qry.name -e dns.resp.type -e dns.a
```

> ⚠️ **安全提示**：DNS 抓包可以看到所有查询内容，涉及用户隐私。只在授权环境中进行，pcap 文件妥善保管。

---

## 五、安全与常见问题

### 5.1 常见 DNS 攻击

| 攻击类型 | 英文 | 原理 | 危害 | 防御手段 |
|---------|------|------|------|---------|
| **DNS 劫持** | DNS Hijacking | 篡改 DNS 解析结果，指向恶意 IP | 用户访问钓鱼/恶意网站 | DNSSEC、DoH/DoT、HTTPS + HSTS |
| **缓存投毒** | Cache Poisoning | 往递归服务器缓存里注入虚假记录 | 大量用户被误导 | DNSSEC、源端口随机化、事务 ID 随机 |
| **DNS 隧道** | DNS Tunneling | 把数据藏在 DNS 查询/响应中 | 绕过防火墙、数据窃取 | 监控异常 DNS 流量、检测长域名、限制出站 DNS |
| **DNS 放大攻击** | DNS Amplification DDoS | 利用 DNS 响应比请求大得多放大流量 | DDoS 目标服务器 | 限制递归服务范围、响应速率限制、Anycast |
| **NXDOMAIN 洪水** | NXDOMAIN Flood | 大量查询不存在的域名，占满缓存 | 耗尽递归服务器资源 | 限速、缓存、检测异常模式 |
| **子域劫持** | Subdomain Takeover | 子域指向已失效的服务，攻击者接管 | 冒充子域名服务 | 定期审计 DNS 记录，及时删除不用的 |
| **域欺骗（钓鱼）** | Typosquatting | 注册相似域名的恶意网站 | 用户输错域名进钓鱼网站 | 监控相关域名、用户教育 |

### 5.2 DNS 安全加固

#### （1）DNSSEC — 数据完整性

- 为重要域名配置 DNSSEC 签名
- 递归解析器启用 DNSSEC 验证（`dnssec-validation auto`）
- 信任锚定期更新

#### （2）DoH / DoT — 传输加密

| 协议 | 全称 | 端口 | 特点 |
|------|------|------|------|
| **DoH** | DNS over HTTPS | 443 | DNS 查询走 HTTPS，和普通 Web 流量混在一起，难被检测/封锁 |
| **DoT** | DNS over TLS | 853 | DNS 查询走 TLS，专用端口，性能更好 |
| **DNSCrypt** | — | 443/其他 | 较早的加密 DNS 协议，使用较少 |

```bash
# systemd-resolved 配置 DoT
# /etc/systemd/resolved.conf
[Resolve]
DNS=8.8.8.8 8.8.4.4
FallbackDNS=1.1.1.1 1.0.0.1
DNSOverTLS=yes   # 或 opportunistic（可用就用）
Domains=~.

# 重启服务
systemctl restart systemd-resolved

# dnsmasq 不直接支持 DoH/DoT，可配合 dnscrypt-proxy 或 stubby
# CoreDNS 支持 DoT/DoH 插件
```

#### （3）递归服务器安全

```
递归 DNS 服务器安全加固：

1. 访问控制
   □ 限制允许递归的客户端 IP 范围（allow-recursion）
   □ 不对外提供开放式递归（容易被用于放大攻击）
   □ 速率限制（rate-limit）

2. 防缓存投毒
   □ 启用 DNSSEC 验证
   □ 源端口随机化
   □ 事务 ID 随机化
   □ 查询名称大小写随机化（0x20 编码）

3. 响应策略
   □ 限制响应大小
   □ 禁用不必要的递归功能
   □ 版本隐藏（version none;）

4. 安全补丁
   □ 及时更新 BIND/dnsmasq 版本
   □ 关注安全公告

5. 监控
   □ 监控查询量、响应时间
   □ 监控异常域名（长度、字符）
   □ 告警配置
```

#### （4）权威服务器安全

```
权威 DNS 服务器安全加固：

1. 区域传输限制
   □ 限制允许区域传输（zone transfer）的 IP（allow-transfer）
   □ 使用 TSIG / SIG(0) 认证区域传输
   □ 禁止任意 AXFR/IXFR

2. 隐藏主服务器
   □ 主 DNS 只对从服务器开放
   □ 对外只公布从服务器地址

3. DNSSEC
   □ 部署 DNSSEC 签名
   □ 密钥轮换（ZSK 频繁，KSK 较少）
   □ 定期检查 DS 记录

4. DDoS 防护
   □ Anycast 部署
   □ 流量清洗
   □ 限速和限流

5. 版本信息隐藏
   □ version "not disclosed";
   □ hostname none;
```

### 5.3 日志审计与监控

#### BIND 日志配置

```
# named.conf 中配置日志
logging {
    channel default_log {
        file "/var/log/named/default.log" versions 3 size 50m;
        severity info;
        print-time yes;
        print-severity yes;
        print-category yes;
    };

    channel query_log {
        file "/var/log/named/query.log" versions 3 size 200m;
        severity info;
        print-time yes;
    };

    category default { default_log; };
    category queries { query_log; };
    category security { default_log; };
    category xfer-in { default_log; };
    category xfer-out { default_log; };
    category notify { default_log; };
};
```

```bash
# 查看 BIND 状态
rndc status
rndc stats                    # 输出统计
rndc reload                   # 重新加载配置
rndc reconfig                 # 重新加载配置（不中断服务）
rndc flush                    # 清空缓存
rndc dumpdb -cache            # 导出缓存

# 监控查询量
wc -l /var/log/named/query.log

# 统计 top 查询域名
awk '{print $NF}' /var/log/named/query.log | sort | uniq -c | sort -rn | head -20

# dnstop — 实时 DNS 流量统计（需安装）
dnstop eth0
```

#### 常见监控指标

| 指标 | 说明 | 告警建议 |
|------|------|---------|
| **查询速率（QPS）** | 每秒查询数 | 突增可能是攻击或异常 |
| **响应延迟** | 平均查询响应时间 | 升高说明性能下降 |
| **缓存命中率** | 缓存回答占比 | 过低说明缓存有问题 |
| **错误率** | SERVFAIL / NXDOMAIN 比例 | 突增可能有问题 |
| **区域传输次数** | AXFR/IXFR 次数 | 异常的区域传输要警惕 |
| **服务器状态** | 服务是否运行 | 宕机告警 |

### 5.4 常见故障排查

```
DNS 故障排查思路：

1. 确认问题范围
   → 是单台机器还是所有机器？
   → 是某个域名还是所有域名？
   → 是解析超时还是结果不对？

2. 本地排查
   → ping 域名？（测试 A 记录解析）
   → dig 域名？（详细信息）
   → 用不同 DNS 服务器试？（dig @8.8.8.8 对比本地）

3. 配置检查
   → /etc/resolv.conf 是否正确？
   → /etc/hosts 有没有错误？
   → /etc/nsswitch.conf 解析顺序？
   → systemd-resolved 状态？resolvectl status？

4. 连通性检查
   → ping DNS 服务器通吗？
   → telnet / nc 到 53 端口（UDP 和 TCP）？
   → 防火墙有没有拦 53 端口？

5. 服务器排查（如果是自己的 DNS）
   → 服务运行吗？systemctl status named/bind9/dnsmasq
   → 日志有没有报错？
   → 磁盘满了吗？
   → 上游 DNS 通吗？
   → 区域文件语法对吗？named-checkzone

6. 抓包分析
   → tcpdump 抓 53 端口，看请求有没有发出去、响应有没有回来
   → 响应码是多少？NOERROR / SERVFAIL / NXDOMAIN / REFUSED？
```

```bash
# ===== 常见排查命令组合 =====

# 1. 测试本地解析
dig example.com                     # 用系统配置的 DNS
dig @8.8.8.8 example.com            # 用公共 DNS 对比
getent hosts example.com            # 模拟系统真实解析（含 hosts）

# 2. 检查配置
cat /etc/resolv.conf
cat /etc/hosts | grep example
cat /etc/nsswitch.conf | grep hosts

# 3. systemd-resolved 系统
resolvectl status
resolvectl query example.com
resolvectl statistics

# 4. 检查 DNS 服务器连通性
ping -c 4 8.8.8.8
nc -zv 8.8.8.8 53                  # TCP 53
nc -zuv 8.8.8.8 53                 # UDP 53

# 5. 抓包
tcpdump -i any -n 'port 53' -vvv   # 实时看

# 6. 查 SOA/NS 判断权威
dig +short NS example.com
dig +trace example.com | tail

# 7. SERVFAIL 排查
dig +dnssec example.com            # 是不是 DNSSEC 验证失败
dig @ns1.example.com example.com    # 直接问权威服务器
```

---

## 附：优化后的提示词模板

以下是可复用的网络协议深度解析提示词模板：

```markdown
# 角色
你是一名资深 Linux 系统与协议专家，精通【协议名称】原理、报文结构、
服务配置与安全加固。

# 任务
请系统介绍【协议名称】，包括：
1. 基本概念（定义、特性、作用、相关 RFC）
2. 报文/帧/记录结构（各字段含义、类型分类、示例）
3. 工作流程（交互流程、状态机、关键机制）
4. Linux 实践
   - 系统配置文件（路径与发行版差异）
   - 相关系统服务
   - 查询/调试命令（每个命令附语法、参数、示例）
   - 服务器软件搭建（至少 2-3 种主流软件）
   - 抓包分析
5. 安全与常见问题
   - 常见攻击类型与原理
   - 防护手段与加固建议
   - 日志审计与监控
   - 故障排查思路

# 输出要求
- Markdown 格式，按大类小类组织
- 关键内容用表格对比
- 命令附语法、参数、示例
- 引用相关 RFC
- 面向系统管理员、运维、安全工程师
- 配置示例标注发行版差异（Ubuntu/Debian、CentOS/RHEL）

# 约束
- 配置文件示例需标注路径与发行版差异
- 修改系统配置前提示备份
- 高风险操作给出警告
- 抓包示例说明权限与风险
- 最后附"优化后的提示词模板"
```

**使用说明**：将【协议名称】替换为"DHCP""SMTP""FTP""BGP"等，即可生成同等深度的协议详解文档。

---

> **总结**：DNS 是互联网的基础中的基础——没有它我们就得靠 IP 地址访问一切。理解域名的层次结构、各种记录类型的用途、递归与迭代查询的区别、完整解析流程，掌握 Linux 上的 DNS 配置文件和查询工具（dig/nslookup/host），熟悉至少一种 DNS 服务器的配置和安全加固，以及常见攻击类型与排查方法，是系统/运维/安全工程师的必备基本功。DNS 虽然简单，但出问题影响巨大——做好冗余、做好监控、做好安全加固，才能确保这根互联网的"电话线"永远畅通。
