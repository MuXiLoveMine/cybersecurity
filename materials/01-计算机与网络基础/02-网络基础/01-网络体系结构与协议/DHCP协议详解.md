# DHCP 协议详解

> 本文系统介绍 DHCP（动态主机配置协议），从基本概念、报文交互流程、地址分配机制，到 Linux 服务端/客户端配置、抓包分析与安全加固。兼顾原理深度与实战操作，面向系统管理员、运维工程师和安全工程师。引用 RFC 2131（DHCPv4）、RFC 8415（DHCPv6）等核心规范。

---

## 目录

- [一、基本概念](#一基本概念)
- [二、报文与流程](#二报文与流程)
- [三、配置与分配](#三配置与分配)
- [四、Linux 实践](#四linux-实践)
- [五、安全与常见问题](#五安全与常见问题)
- [附：优化后的提示词模板](#附优化后的提示词模板)

---

## 一、基本概念

### 1.1 什么是 DHCP

**DHCP（Dynamic Host Configuration Protocol，动态主机配置协议）**是一种局域网网络协议，用于自动为客户端分配 IP 地址、子网掩码、网关、DNS 等网络配置参数，让管理员不用手动给每台机器配置网络。

DHCP 工作在应用层，基于 UDP 协议：
- 服务端监听 **UDP 67** 端口（BootP Server）
- 客户端监听 **UDP 68** 端口（BootP Client）

| 核心特性 | 说明 |
|---------|------|
| **自动配置** | 客户端即插即用，无需手动设置 IP |
| **集中管理** | 所有 IP 分配信息在服务器统一管理 |
| **地址复用** | 租约到期回收，地址可重新分配 |
| **灵活分配** | 动态分配、固定保留、排除范围等多种模式 |
| **丰富选项** | 除 IP 外还可下发网关、DNS、域名、NTP 等几十种参数 |

**适用场景**：
- 企业/学校/家庭局域网（终端数量多，变动频繁）
- 移动办公环境（笔记本电脑接入不同网络）
- 虚拟机/容器环境（动态创建和销毁）
- PXE 无盘启动（通过 DHCP 获取 IP 和引导文件）

### 1.2 与静态 IP、BOOTP 的关系

#### 静态 IP vs 动态 IP（DHCP）

| 维度 | 静态 IP | 动态 IP（DHCP） |
|------|---------|----------------|
| **配置方式** | 手动设置 | 自动获取 |
| **地址变化** | 固定不变 | 租约到期可能变化 |
| **管理成本** | 高（每台机器手动配） | 低（集中管理） |
| **可追踪性** | 好（地址固定对应设备） | 需结合日志/租约记录 |
| **适用场景** | 服务器、网络设备、打印机 | PC、笔记本、手机、虚拟机 |
| **出错率** | 低（配置好就稳定） | 依赖 DHCP 服务器可用性 |

> 最佳实践：**服务器和网络设备用静态 IP 或 DHCP 保留地址，终端用户设备用动态分配**。

#### BOOTP → DHCP 的演进

| 特性 | BOOTP | DHCP |
|------|-------|------|
| **全称** | Bootstrap Protocol | Dynamic Host Configuration Protocol |
| **RFC** | RFC 951 | RFC 2131 |
| **地址分配** | 静态绑定（手动配置每台机器） | 动态分配（地址池自动分配） |
| **租约机制** | 无（永久分配） | 有（租期到期可续租/回收） |
| **选项数量** | 少（vendor 扩展） | 多（几十种标准选项） |
| **移动性** | 差（换子网需重新配置） | 好（自动获取新地址） |
| **兼容性** | — | DHCP 向后兼容 BOOTP |

> DHCP 是 BOOTP 的增强版，端口相同（67/68），报文格式基本兼容，新增了动态分配、租约机制和更多选项。

### 1.3 DHCPv4 与 DHCPv6

| 特性 | DHCPv4 | DHCPv6 |
|------|--------|--------|
| **RFC** | RFC 2131 | RFC 8415 |
| **传输协议** | UDP 67（服务器）/ 68（客户端） | UDP 546（客户端）/ 547（服务器） |
| **地址分配** | 有状态（Stateful） | 有状态 + 无状态（Stateless） |
| **广播** | 使用广播（255.255.255.255） | 使用组播（ff02::1:2） |
| **网关** | DHCP 下发默认网关 | 网关由 RA（路由通告）提供，不由 DHCPv6 下发 |
| **SLAAC** | 无 | 支持（无状态自动配置，不需要 DHCPv6） |
| **客户端标识符** | chaddr（MAC 地址）+ client-id | DUID（DHCP Unique Identifier） |
| **中继代理** | BOOTP Relay Agent（UDP 67） | DHCPv6 Relay（UDP 547） |

**IPv6 地址获取的三种模式**：

| 模式 | 说明 | M 位 | O 位 |
|------|------|-----|-----|
| **SLAAC** | 无状态自动配置（自己生成地址，DNS 也不用 DHCP） | 0 | 0 |
| **SLAAC + DHCPv6（无状态）** | 地址自己生成，其他选项（如 DNS）从 DHCPv6 获取 | 0 | 1 |
| **DHCPv6（有状态）** | 地址和其他选项都从 DHCPv6 获取 | 1 | 1 |

> M（Managed Address Configuration）位和 O（Other Configuration）位在路由器的 RA（Router Advertisement）报文中设置，决定客户端使用哪种模式。

---

## 二、报文与流程

### 2.1 DHCPv4 报文类型

| 报文类型 | 方向 | 说明 |
|---------|------|------|
| **DHCPDISCOVER** | 客户端 → 服务器 | 客户端广播寻找 DHCP 服务器 |
| **DHCPOFFER** | 服务器 → 客户端 | 服务器回应，提供 IP 租约 |
| **DHCPREQUEST** | 客户端 → 服务器 | 客户端请求/确认/续租 IP |
| **DHCPACK** | 服务器 → 客户端 | 服务器确认，分配完成 |
| **DHCPNAK** | 服务器 → 客户端 | 服务器拒绝（地址已被占用/租约无效） |
| **DHCPDECLINE** | 客户端 → 服务器 | 客户端拒绝（IP 已被占用） |
| **DHCPRELEASE** | 客户端 → 服务器 | 客户端主动释放 IP |
| **DHCPINFORM** | 客户端 → 服务器 | 客户端已有 IP，只请求其他选项 |

### 2.2 DORA 流程详解

客户端首次获取 IP 地址的经典四步流程，简称 **DORA**（Discover → Offer → Request → Ack）。

```
客户端（UDP 68）                              服务器（UDP 67）
      │                                            │
      │  1. DHCPDISCOVER（广播）                      │
      │  源 IP: 0.0.0.0                              │
      │  目的 IP: 255.255.255.255                    │
      │  内容：我的 MAC 是 xx，我要 IP 地址             │
      ├─────────────────────────────────────────────►│
      │                                            │
      │  2. DHCPOFFER（广播/单播）                    │
      │  内容：给你 192.168.1.100，租期 86400 秒       │
      │        网关 192.168.1.1，DNS 8.8.8.8          │
      │◄─────────────────────────────────────────────┤
      │                                            │
      │  3. DHCPREQUEST（广播）                       │
      │  内容：我选这个服务器的 offer，请求 192.168.1.100 │
      │        （广播是为了通知其他服务器我没选它们）     │
      ├─────────────────────────────────────────────►│
      │                                            │
      │  4. DHCPACK（广播/单播）                      │
      │  内容：确认，192.168.1.100 租期 86400s        │
      │◄─────────────────────────────────────────────┤
      │                                            │
      ✦ 配置完成，开始使用 IP 地址                    │
```

**为什么前两步用广播？**
- DISCOVER 广播：客户端还不知道 DHCP 服务器在哪，只能广播找
- OFFER 可以是单播（如果客户端还没 IP，很多实现还是广播）
- REQUEST 广播：告诉所有 DHCP 服务器"我选了 XX 服务器的 offer"，其他服务器可以回收他们的 offer
- ACK 确认最终分配

### 2.3 租约、续租与释放

#### （1）租约时间线

```
分配时刻         T1(50%)         T2(87.5%)        租期到期
──┼───────────────────┼──────────────────┼───────────►
  │                   │                  │
  获得 IP            开始续租            重新绑定
                     （向原服务器单播）    （广播找任意服务器）
```

| 时间点 | 占租期比例 | 行为 |
|--------|-----------|------|
| **T1** | 50% | 客户端向**原服务器**单播 DHCPREQUEST 续租 |
| **T2** | 87.5% | T1 没成功，向**任意服务器**广播 DHCPREQUEST 重新绑定 |
| **到期** | 100% | 都没成功，停止使用 IP，重新开始 DORA 流程 |

```bash
# 续租流程：
# T1（50%）：发单播 DHCPREQUEST 给原服务器 → 收到 DHCPACK → 租期刷新
# T2（87.5%）：T1 失败，广播 DHCPREQUEST → 收到任意服务器的 ACK → 租期刷新
# 到期：都失败 → 停止使用 IP → 重新 DISCOVER
```

#### （2）释放（RELEASE）

客户端不再需要 IP 时（比如正常关机），主动发送 DHCPRELEASE 给服务器，服务器回收地址，标记为可用。

```
客户端 ── DHCPRELEASE ──► 服务器
"我不用这个 IP 了，还给你"
```

> 注意：很多客户端（比如手机直接断开 WiFi）不会发送 RELEASE，地址会等租期到期后自动回收。

#### （3）DHCPDECLINE

客户端收到 ACK 后，用 ARP 检测这个 IP 是否已经被占用了。如果发现被占用了，就发 DHCPDECLINE 拒绝这个地址，然后重新开始 DORA。

### 2.4 中继代理（DHCP Relay）

**问题**：DHCPDISCOVER 是广播的，路由器默认不转发广播包 → 每个子网都得有 DHCP 服务器？

**解决方案**：DHCP 中继代理（Relay Agent / IP Helper）。路由器/三层交换机上启用中继，把 DHCP 广播包改成单播，转发给远程 DHCP 服务器。

```
子网 A（192.168.1.0/24）         路由器/中继         DHCP 服务器（10.0.0.1）
        │                            │                        │
        │  DHCPDISCOVER 广播          │                        │
        ├────────────────────────────►│                        │
        │                            │                        │
        │                            │  改成单播，加 giaddr 字段   │
        │                            ├───────────────────────►│
        │                            │                        │
        │                            │  DHCPOFFER              │
        │                            │◄───────────────────────┤
        │                            │                        │
        │  DHCPOFFER 广播            │                        │
        │◄───────────────────────────┤                        │
        │                            │                        │
```

| 关键概念 | 说明 |
|---------|------|
| **giaddr** | Gateway IP Address，中继代理的 IP（客户端所在子网的网关 IP） |
| **中继代理地址** | 服务器根据 giaddr 决定从哪个地址池分配 IP |
| **UDP 端口** | 中继使用 67 端口和服务器通信 |

> 多子网环境下必须配置中继（或每个子网一个 DHCP 服务器）。服务器通过 giaddr 判断客户端在哪个子网，从对应地址池分配 IP。

---

## 三、配置与分配

### 3.1 地址分配方式

| 分配方式 | 英文 | 说明 | 适用场景 |
|---------|------|------|---------|
| **动态分配** | Dynamic Allocation | 从地址池里自动分配，有租期，到期回收 | 普通终端（PC、手机） |
| **自动分配** | Automatic Allocation | 动态分配但永久租用（相当于永久给它） | 半固定场景 |
| **固定/保留** | Static / Reservation | 特定 MAC 地址固定分配特定 IP | 服务器、打印机、网络设备 |

### 3.2 地址池配置要素

```
一个典型的子网配置包含：

1. 子网网络号 + 子网掩码
   例：192.168.1.0 / 255.255.255.0

2. 地址池范围（Range）
   例：192.168.1.100 - 192.168.1.200
   → 可动态分配的地址范围

3. 排除地址（Exclude）
   例：192.168.1.150 - 192.168.1.160
   → 地址池里排除不用（手动静态占用的）

4. 保留地址（Reservation / Host）
   例：MAC=00:11:22:33:44:55 → 固定分配 192.168.1.50
   → 特定机器永远拿到同一个 IP

5. 租约时间（Lease Time）
   例：默认 86400 秒（1 天）
   → IP 地址的租期长度

6. 选项（Options）
   例：
   - 默认网关（Option 3）：192.168.1.1
   - DNS 服务器（Option 6）：8.8.8.8, 8.8.4.4
   - 域名（Option 15）：example.com
   - NTP 服务器（Option 42）：ntp.example.com
```

### 3.3 常见 DHCP 选项

| 选项号 | 名称 | 说明 | 示例 |
|-------|------|------|------|
| **1** | Subnet Mask | 子网掩码 | 255.255.255.0 |
| **3** | Router | 默认网关 | 192.168.1.1 |
| **6** | Domain Name Server | DNS 服务器 | 8.8.8.8, 8.8.4.4 |
| **12** | Host Name | 主机名 | client01 |
| **15** | Domain Name | 域名 | example.com |
| **28** | Broadcast Address | 广播地址 | 192.168.1.255 |
| **42** | NTP Servers | NTP 服务器 | ntp.example.com |
| **51** | Lease Time | 租约时间（秒） | 86400 |
| **53** | DHCP Message Type | 报文类型 | 1=DISCOVER, 2=OFFER, ... |
| **54** | Server Identifier | 服务器 IP | 192.168.1.1 |
| **58** | Renewal Time | T1 续租时间（秒） | 43200 |
| **59** | Rebinding Time | T2 重绑时间（秒） | 75600 |
| **66** | TFTP Server Name | TFTP 服务器名 | PXE 用 |
| **67** | Bootfile Name | 引导文件名 | PXE 用（pxelinux.0） |
| **82** | Relay Agent Info | 中继代理信息 | 中继用 |
| **119** | Domain Search | 搜索域名 | example.com |
| **121** | Classless Static Route | 无类静态路由 | 多条静态路由 |

### 3.4 DHCP 与 PXE 引导

**PXE（Preboot eXecution Environment，预启动执行环境）** 让计算机在操作系统启动之前通过网络启动，从服务器下载引导文件。

DHCP 在 PXE 中的作用：
1. PXE 客户端发 DHCPDISCOVER，携带 PXE 相关选项
2. DHCP 服务器回应 IP 地址 + TFTP 服务器地址（Option 66）+ 引导文件名（Option 67）
3. 客户端拿到 IP 后，通过 TFTP 下载引导文件
4. 执行引导文件，进入安装/启动流程

```
PXE 启动流程：
  1. 网卡 PXE ROM 启动 → 发 DHCPDISCOVER（带 PXE 选项）
  2. DHCP 服务器回应 IP + 网关 + DNS + Option 66（TFTP IP）+ Option 67（boot filename）
  3. 客户端配置 IP
  4. 客户端向 TFTP 服务器请求引导文件（pxelinux.0）
  5. 执行引导程序 → 加载内核 + initrd → 启动系统/安装程序
```

---

## 四、Linux 实践

### 4.1 服务端软件对比

| 软件 | 开发者 | 特点 | 配置风格 | 适用场景 |
|------|--------|------|---------|---------|
| **isc-dhcp-server** | ISC | 最经典、功能最全、成熟稳定 | 配置文件 | 企业级、复杂网络 |
| **Kea** | ISC | 新一代、模块化、REST API、高性能 | 配置文件 + API | 现代、自动化、高性能 |
| **dnsmasq** | 个人 | 轻量、DNS+DHCP 一体、简单 | 配置文件 | 小型网络、家庭、开发环境 |
| **udhcpd** | BusyBox | 超轻量、嵌入式 | 配置文件 | 嵌入式、路由器 |
| **CoreDNS** | CNCF | 插件化、支持 DHCP 插件 | Corefile | 云原生、K8s |

### 4.2 isc-dhcp-server 配置

ISC DHCP Server 是最经典的 DHCP 服务器，功能最全面。

```bash
# 安装
# Debian/Ubuntu:
apt install isc-dhcp-server

# RHEL/CentOS:
yum install dhcp
# 服务名是 dhcpd
```

**配置文件路径**：
- Debian/Ubuntu：`/etc/dhcp/dhcpd.conf`
- RHEL/CentOS：`/etc/dhcp/dhcpd.conf`
- 服务名：`isc-dhcp-server`（Debian）/ `dhcpd`（RHEL）

**全局配置 + 单子网示例**：

```dhcpd.conf
# ===== 全局参数 =====
ddns-update-style none;           # 不做动态 DNS 更新
default-lease-time 86400;         # 默认租期 1 天（秒）
max-lease-time 172800;            # 最大租期 2 天
authoritative;                    # 权威模式（这个子网的正式服务器）
log-facility local7;              # 日志发到 syslog local7

option domain-name "example.com";
option domain-name-servers 8.8.8.8, 8.8.4.4;
option routers 192.168.1.1;
option subnet-mask 255.255.255.0;
option broadcast-address 192.168.1.255;
option ntp-servers ntp.example.com;

# ===== 子网声明 =====
subnet 192.168.1.0 netmask 255.255.255.0 {
    range 192.168.1.100 192.168.1.200;     # 地址池
    option routers 192.168.1.1;            # 网关（覆盖全局）

    # 排除范围（不在地址池里但属于这个子网的手动分配地址）
    # range 本身就隐含排除了范围外的

    # 保留地址（特定 MAC 固定 IP）
    host server01 {
        hardware ethernet 00:11:22:33:44:55;
        fixed-address 192.168.1.50;
        option host-name "server01";
    }

    host printer01 {
        hardware ethernet aa:bb:cc:dd:ee:ff;
        fixed-address 192.168.1.60;
        option host-name "printer01";
    }
}
```

**多子网 + 中继场景**：

```dhcpd.conf
# 多子网环境（有中继）

subnet 192.168.1.0 netmask 255.255.255.0 {
    range 192.168.1.100 192.168.1.200;
    option routers 192.168.1.1;
    option domain-name-servers 8.8.8.8;
}

subnet 192.168.2.0 netmask 255.255.255.0 {
    range 192.168.2.100 192.168.2.200;
    option routers 192.168.2.1;
    option domain-name-servers 8.8.8.8;
}

subnet 10.0.0.0 netmask 255.255.255.0 {
    # 服务器自己所在的子网（即使没有地址池也要声明）
}

# PXE 引导配置
subnet 192.168.10.0 netmask 255.255.255.0 {
    range 192.168.10.100 192.168.10.200;
    option routers 192.168.10.1;
    option domain-name-servers 8.8.8.8;

    # PXE 相关选项
    next-server 192.168.10.10;        # TFTP 服务器 IP
    filename "pxelinux.0";             # 引导文件名

    # 仅允许 PXE 客户端使用（可选）
    # class "pxe" {
    #     match if substring (option vendor-class-identifier, 0, 9) = "PXEClient";
    # }
}
```

```bash
# 检查配置语法
dhcpd -t                    # 测试配置文件
dhcpd -t -cf /etc/dhcp/dhcpd.conf

# 启动服务
# Debian:
systemctl start isc-dhcp-server
systemctl enable isc-dhcp-server

# RHEL:
systemctl start dhcpd
systemctl enable dhcpd

# 查看状态
systemctl status isc-dhcp-server

# 查看租约文件
# Debian: /var/lib/dhcp/dhcpd.leases
# RHEL:   /var/lib/dhcpd/dhcpd.leases
cat /var/lib/dhcp/dhcpd.leases
```

> ⚠️ **修改配置前提示**：修改 dhcpd.conf 前务必备份：`cp /etc/dhcp/dhcpd.conf /etc/dhcp/dhcpd.conf.bak`。修改后先 `dhcpd -t` 测试语法，确认无误再重启服务。生产环境建议先在测试环境验证。

### 4.3 dnsmasq 配置

轻量级 DNS + DHCP 一体的服务，适合小型环境。

```bash
# 安装
# Debian/Ubuntu: apt install dnsmasq
# RHEL/CentOS: yum install dnsmasq（EPEL）

# 配置文件：/etc/dnsmasq.conf
```

```
# ===== DHCP 配置 =====

# 启用 DHCP 服务
dhcp-range=192.168.1.100,192.168.1.200,12h
# 格式：dhcp-range=<起始IP>,<结束IP>,<租期>

# 网关（不指定的话用 dnsmasq 监听的 IP）
dhcp-option=option:router,192.168.1.1

# DNS 服务器（不指定的话用 dnsmasq 自己）
dhcp-option=option:dns-server,8.8.8.8,8.8.4.4

# 域名
dhcp-option=option:domain-name,example.com

# 租期（也可以在 range 里指定）
dhcp-lease-max=256
dhcp-leasefile=/var/lib/dnsmasq/dnsmasq.leases

# ===== 保留地址 =====
dhcp-host=00:11:22:33:44:55,192.168.1.50,server01,12h
# 格式：dhcp-host=<MAC>,<IP>,<主机名>,<租期>

dhcp-host=aa:bb:cc:dd:ee:ff,printer01,infinite   # 无限租期

# ===== 多子网 =====
# 监听多个接口/多个网段
interface=eth0
interface=eth1

dhcp-range=eth0,192.168.1.100,192.168.1.200,12h
dhcp-range=eth1,10.0.0.100,10.0.0.200,12h

# ===== PXE 引导 =====
dhcp-boot=pxelinux.0,tftp-server,192.168.1.10
enable-tftp
tftp-root=/var/lib/tftpboot

# ===== 其他选项 =====
# 不分配给未知的 MAC 地址
# dhcp-ignore=tag:!known

# 静态租约文件
dhcp-hostsfile=/etc/dnsmasq.d/hosts

# 日志
log-dhcp
```

```bash
# 启动服务
systemctl start dnsmasq
systemctl enable dnsmasq

# 查看租约
cat /var/lib/dnsmasq/dnsmasq.leases

# 测试
dig @localhost example.com
# 客户端测试：dhclient -v eth0
```

### 4.4 Kea 配置

ISC Kea 是新一代 DHCP 服务器，支持 REST API、配置后端数据库、高性能。

```bash
# 安装（Debian/Ubuntu）
apt install kea

# 配置文件：/etc/kea/kea-dhcp4.conf（JSON 格式）
```

```json
{
    "Dhcp4": {
        "valid-lifetime": 86400,
        "renew-timer": 43200,
        "rebind-timer": 75600,

        "interfaces-config": {
            "interfaces": ["eth0"]
        },

        "lease-database": {
            "type": "memfile",
            "persist": true,
            "name": "/var/lib/kea/kea-leases.csv"
        },

        "subnet4": [
            {
                "subnet": "192.168.1.0/24",
                "pools": [
                    {
                        "pool": "192.168.1.100 - 192.168.1.200"
                    }
                ],
                "option-data": [
                    { "name": "router", "data": "192.168.1.1" },
                    { "name": "domain-name-servers", "data": "8.8.8.8, 8.8.4.4" },
                    { "name": "domain-name", "data": "example.com" }
                ],
                "reservations": [
                    {
                        "hw-address": "00:11:22:33:44:55",
                        "ip-address": "192.168.1.50",
                        "hostname": "server01"
                    }
                ]
            }
        ],

        "control-socket": {
            "socket-type": "unix",
            "socket-name": "/run/kea/kea-dhcp4-ctrl.sock"
        }
    }
}
```

```bash
# 启动
systemctl start kea-dhcp4-server
systemctl enable kea-dhcp4-server

# 通过命令行管理
kea-shell
# 或用 REST API（需配置）
```

### 4.5 客户端配置

#### （1）dhclient — ISC DHCP 客户端

```bash
# 请求 IP（前台运行，看详细过程）
dhclient -v eth0

# 后台运行
dhclient eth0

# 释放 IP
dhclient -r eth0

# 配置文件：/etc/dhcp/dhclient.conf

# 查看租约文件
# /var/lib/dhcp/dhclient.leases
cat /var/lib/dhcp/dhclient.eth0.leases
```

**dhclient.conf 示例**：

```
# 请求的选项列表
request subnet-mask, broadcast-address, time-offset, routers,
        domain-name, domain-name-servers, domain-search, host-name,
        ntp-servers;

# 超时时间
timeout 60;

# 重试间隔
retry 60;

# 选择超时
select-timeout 5;

# 初始租约时间
initial-interval 10;

# 发送指定主机名
send host-name = gethostname();

# 请求特定 IP（不保证成功）
# dhclient 会优先请求上次的 IP
```

#### （2）NetworkManager

```bash
# 查看连接
nmcli connection show

# 设置为自动获取 IP（DHCP，默认）
nmcli connection modify "Wired connection 1" ipv4.method auto

# 设置为手动
nmcli connection modify "Wired connection 1" \
    ipv4.method manual \
    ipv4.addresses "192.168.1.100/24" \
    ipv4.gateway "192.168.1.1" \
    ipv4.dns "8.8.8.8 8.8.4.4"

nmcli connection up "Wired connection 1"
```

#### （3）systemd-networkd

```ini
# /etc/systemd/network/20-eth0.network
[Match]
Name=eth0

[Network]
DHCP=yes

# 也可以手动配置
# Address=192.168.1.100/24
# Gateway=192.168.1.1
# DNS=8.8.8.8

[DHCP]
UseDNS=yes
UseNTP=yes
UseHostname=yes
```

```bash
systemctl restart systemd-networkd
networkctl status eth0
```

### 4.6 抓包分析 🔑

```bash
# ===== tcpdump 抓 DHCP 包 =====

# 抓 DHCPv4（UDP 67/68）
tcpdump -i any -n 'udp port 67 or udp port 68'
tcpdump -i eth0 -n 'udp port 67 or udp port 68'

# 详细输出（看到完整报文）
tcpdump -i eth0 -n 'udp port 67 or udp port 68' -vvv
tcpdump -i eth0 -n 'udp port 67 or udp port 68' -X

# 保存到文件
tcpdump -i any -n 'udp port 67 or udp port 68' -w dhcp.pcap
tcpdump -i any -n 'udp port 67 or udp port 68' -c 20 -w dhcp.pcap  # 抓 20 个

# 读取文件
tcpdump -r dhcp.pcap -n
tcpdump -r dhcp.pcap -n -vvv

# DHCPv6
tcpdump -i any -n 'udp port 546 or udp port 547'

# 只看特定类型（用 tshark 更方便）
tshark -r dhcp.pcap -Y "dhcp.option.dhcp == 1"  # DISCOVER
tshark -r dhcp.pcap -Y "dhcp.option.dhcp == 2"  # OFFER
tshark -r dhcp.pcap -Y "dhcp.option.dhcp == 3"  # REQUEST
tshark -r dhcp.pcap -Y "dhcp.option.dhcp == 5"  # ACK

# 显示关键字段
tshark -r dhcp.pcap -T fields \
    -e frame.time \
    -e ip.src -e ip.dst \
    -e dhcp.option.dhcp \
    -e dhcp.option.requested_ip_address \
    -e dhcp.option.server_id \
    -e dhcp.client_id_mac_addr
```

> ⚠️ **风险提示**：tcpdump 抓 DHCP 包需要 root 权限。可以看到客户端 MAC 地址、主机名等信息，涉及隐私。只在授权环境中操作。

### 4.7 日志分析

#### isc-dhcp-server 日志

```bash
# 日志位置（取决于 syslog 配置）
# 通常在 /var/log/syslog 或 /var/log/messages
# 也可以配置专用日志文件

# 查看 DHCP 相关日志
grep dhcpd /var/log/syslog
grep -i "dhcp.*DISCOVER\|dhcp.*OFFER\|dhcp.*REQUEST\|dhcp.*ACK" /var/log/syslog

# 实时跟踪
tail -f /var/log/syslog | grep dhcpd

# 常见日志格式：
# Sep 24 10:00:00 server dhcpd: DHCPDISCOVER from 00:11:22:33:44:55 via eth0
# Sep 24 10:00:00 server dhcpd: DHCPOFFER on 192.168.1.100 to 00:11:22:33:44:55 via eth0
# Sep 24 10:00:00 server dhcpd: DHCPREQUEST for 192.168.1.100 from 00:11:22:33:44:55 via eth0
# Sep 24 10:00:00 server dhcpd: DHCPACK on 192.168.1.100 to 00:11:22:33:44:55 via eth0

# 统计 DISCOVER 数量（异常多可能是攻击）
grep -c "DHCPDISCOVER" /var/log/syslog

# 查看最近分配的 IP
grep "DHCPACK" /var/log/syslog | tail -20

# dnsmasq 日志
grep dnsmasq-dhcp /var/log/syslog
```

---

## 五、安全与常见问题

### 5.1 常见攻击类型

| 攻击 | 英文 | 原理 | 危害 | 防御手段 |
|------|------|------|------|---------|
| **伪造 DHCP 服务器（Rogue DHCP）** | Rogue DHCP Server | 私接恶意 DHCP 服务器，下发错误的网关/DNS | 中间人攻击、流量劫持、钓鱼 | DHCP Snooping、端口安全、802.1X |
| **DHCP 饥饿攻击** | DHCP Starvation | 伪造大量不同 MAC 地址的请求，耗尽地址池 | 合法用户无法获取 IP，拒绝服务 | DHCP Snooping + 限速、端口安全 |
| **DHCP 中间人** | MITM via DHCP | 伪造服务器下发恶意网关/DNS | 窃听、篡改、钓鱼 | DHCP Snooping、DNSSEC、HTTPS |
| **DHCP 报文伪造** | DHCP Spoofing | 伪造 DHCPRELEASE / DHCPDECLINE | 释放合法客户端的 IP | 认证、DHCP Snooping |
| **DHCP 选项滥用** | Option Abuse | 利用 DHCP 选项注入恶意配置 | WPAD 攻击、恶意 NTP 服务器 | 限制下发的选项、白名单 |

**伪造 DHCP 服务器攻击流程**：

```
攻击者接入局域网 → 启动伪造 DHCP 服务器
    │
    ├─ 客户端发 DHCPDISCOVER 广播
    │   真服务器和假服务器都会回应 OFFER
    │   客户端通常选先到的那个
    │
    └─ 客户端接受假服务器的 OFFER → 获得恶意网关/DNS
        → 所有流量经过攻击者 → 中间人攻击
```

### 5.2 DHCP Snooping

**DHCP Snooping** 是交换机上的安全特性，防止伪造 DHCP 服务器。

| 概念 | 说明 |
|------|------|
| **信任端口（Trusted）** | 连接合法 DHCP 服务器或上联端口，允许所有 DHCP 报文 |
| **非信任端口（Untrusted）** | 连接终端用户的端口，只允许 DHCP 请求，拒绝 DHCP 服务器报文 |
| **绑定表（Binding Table）** | 记录端口 + MAC + IP + 租期的对应关系 |

```
工作原理：
  1. 交换机所有端口默认是非信任端口
  2. 管理员手动把连接 DHCP 服务器的端口设为信任端口
  3. 非信任端口收到的 DHCP 服务器报文（OFFER/ACK/NAK）直接丢弃
  4. 建立 DHCP Snooping 绑定表（IP-MAC-端口-租期）
  5. 绑定表可被 IP Source Guard、DAI 等其他安全功能使用
```

> DHCP Snooping 是交换机功能，不是服务器配置。运维人员需和网络团队配合部署。

### 5.3 DHCP 服务器安全加固

```
DHCP 服务器安全加固清单：

1. 服务器本身安全
   □ 操作系统最小化安装
   □ 防火墙只开放必要端口（UDP 67）
   □ 定期更新系统和 dhcpd 补丁
   □ 启用 SELinux/AppArmor
   □ 限制 ssh 登录管理

2. 配置安全
   □ 修改配置前备份
   □ 使用 authoritative 模式（防止客户端被其他服务器干扰）
   □ 地址池大小合理规划（留有余量但不浪费）
   □ 重要设备使用保留地址（静态绑定）
   □ 租约时间合理（移动终端短一些，固定设备长一些）
   □ 不下发不必要的 DHCP 选项

3. 日志与监控
   □ 启用详细日志
   □ 监控 DHCP 报文数量（异常突增告警）
   □ 监控地址池使用率（超过 80% 告警）
   □ 监控服务运行状态
   □ 定期审计租约表和保留地址

4. 网络层防护
   □ 交换机部署 DHCP Snooping
   □ 端口安全（限制端口 MAC 数量）
   □ 802.1X 认证
   □ IP Source Guard + DAI（动态 ARP 检测）
   □ DHCP 服务器尽量和客户端在不同 VLAN，通过中继转发

5. 高可用
   □ 部署主备两台 DHCP 服务器
   □ 地址池拆分（避免冲突）
   □ 定期备份租约数据库
```

### 5.4 常见故障排查

```
DHCP 故障排查思路：

1. 客户端问题？服务器问题？网络问题？
   → 一台机器不行还是所有机器都不行？
   → 静态 IP 能通吗？（先排除网络层）
   → 客户端有没有收到 IP？（ip addr / ipconfig）

2. 客户端侧排查
   → 网络接口状态？
   → 有没有发 DHCP 请求？（抓包看）
   → 有没有收到响应？
   → dhclient -v 手动请求看详细输出
   → 防火墙有没有拦 UDP 68？

3. 网络侧排查
   → 中继代理配置了吗？（跨子网场景）
   → 交换机有没有 DHCP Snooping 拦截？
   → 路由器/防火墙有没有拦 UDP 67/68？
   → 服务器和客户端之间通不通？

4. 服务器侧排查
   → 服务运行吗？systemctl status isc-dhcp-server
   → 配置语法对吗？dhcpd -t
   → 端口在监听吗？ss -ulnp | grep :67
   → 日志有没有报错？
   → 地址池用完了吗？
   → 对应子网配置了吗？（giaddr 匹配的子网）
   → 防火墙有没有拦 UDP 67？

5. 抓包确认
   → 服务器端抓 67/68 端口
   → 客户端有没有发 DISCOVER？
   → 服务器有没有回应 OFFER？
   → 有没有 REQUEST？有没有 ACK？
```

```bash
# ===== 常用排查命令 =====

# 客户端侧（Linux）
dhclient -v eth0                    # 手动请求，看详细过程
dhclient -r eth0                   # 释放
ip addr show eth0                  # 查看有没有拿到 IP

# 服务器侧
systemctl status isc-dhcp-server   # 服务状态
dhcpd -t                           # 配置语法检查
ss -ulnp | grep 67                 # 端口监听
tail -f /var/log/syslog | grep dhcp  # 实时日志

# 地址池使用率
# 统计租约文件中的活跃租约
cat /var/lib/dhcp/dhcpd.leases | grep -c "lease "

# 抓包（两端同时抓对比）
tcpdump -i eth0 -n 'udp port 67 or udp port 68' -vvv
```

---

## 附：优化后的提示词模板

以下是可复用的网络服务协议深度解析提示词模板：

```markdown
# 角色
你是一名资深 Linux 系统与服务协议专家，精通【协议名称】原理、
报文交互、服务端配置与安全加固。

# 任务
请系统介绍【协议名称】，包括：
1. 基本概念（作用、适用场景、历史演进、v4/v6 差异）
2. 报文与工作流程（报文类型、完整交互流程、状态机、关键机制）
3. 配置与分配机制（地址池/参数、选项、特殊场景如 PXE/中继）
4. Linux 实践
   - 服务端软件：至少 3 种主流实现对比 + 完整配置示例
   - 客户端：至少 2-3 种客户端工具
   - 抓包分析（tcpdump / tshark）
   - 日志分析
5. 安全与常见问题
   - 攻击类型与原理
   - 防御手段（服务器侧 + 网络侧）
   - 加固清单
   - 故障排查思路与命令组合

# 输出要求
- Markdown 格式，按大类小类组织
- 表格对比
- 配置文件附完整路径与示例
- 引用相关 RFC
- 面向系统管理员、运维、安全工程师
- 标注发行版差异（Ubuntu/Debian、CentOS/RHEL）

# 约束
- 修改配置前提示备份
- 多子网/中继场景需说明
- 高风险操作警告
- 抓包示例说明权限与风险
- 最后附"优化后的提示词模板"
```

**使用说明**：将【协议名称】替换为"FTP""SMTP""NTP""SNMP"等，即可生成同等深度的服务协议详解文档。

---

> **总结**：DHCP 是局域网中最基础也最重要的服务之一——没有它，每台机器都得手动配 IP，网络管理会变成噩梦。理解 DORA 四步交互流程、租约续租机制、中继代理工作原理，掌握 isc-dhcp-server / dnsmasq / Kea 至少一种服务器的配置，熟悉客户端的调试方法和抓包分析，了解伪造 DHCP 服务器和饥饿攻击等常见威胁以及 DHCP Snooping 等防御手段，是运维工程师的基本功。DHCP 服务一旦出问题影响面极大，务必做好高可用、监控和安全加固。
