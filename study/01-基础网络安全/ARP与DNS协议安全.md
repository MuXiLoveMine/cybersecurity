# ARP与DNS协议安全

> 本文档用于网络安全教学与防御技术研究。所有脚本与配置均基于模拟环境，仅供学习使用。

---

## 目录

- [一、ARP协议基础与安全威胁](#一arp协议基础与安全威胁)
- [二、ARP攻击检测与防御](#二arp攻击检测与防御)
- [三、DNS协议基础与安全威胁](#三dns协议基础与安全威胁)
- [四、DNS安全防护](#四dns安全防护)

---

## 一、ARP协议基础与安全威胁

### 1.1 ARP协议工作原理

ARP（Address Resolution Protocol，地址解析协议）用于将IP地址解析为MAC地址。在以太网中，数据链路层传输依赖MAC地址，而网络层使用IP地址，ARP充当两者之间的桥梁。

**工作流程（以主机A访问主机B为例）：**

```
主机A(192.168.1.10) 需要与 主机B(192.168.1.20) 通信

步骤1: A查看本地ARP缓存表
  ┌─────────────────────┐
  │ ARP缓存表           │
  │ 192.168.1.20 → ?    │  ← 缓存未命中
  └─────────────────────┘

步骤2: A广播ARP请求（目标MAC为 FF:FF:FF:FF:FF:FF）
  ┌──────────────────────────────────┐
  │ ARP Request (广播)                │
  │ Who has 192.168.1.20?            │
  │ Tell 192.168.1.10                │
  └──────────────────────────────────┘
         ↓ 广播到全网
    [主机B] [主机C] [主机D] ...

步骤3: 只有主机B回应ARP应答（单播）
  ┌──────────────────────────────────┐
  │ ARP Reply (单播给A)              │
  │ 192.168.1.20 is at AA:BB:CC:DD:EE:FF │
  └──────────────────────────────────┘

步骤4: A更新ARP缓存表，开始正常通信
  ┌─────────────────────┐
  │ ARP缓存表           │
  │ 192.168.1.20 → AA:BB:CC:DD:EE:FF │  ← 缓存命中
  └─────────────────────┘
```

**关键特性：**
- ARP是无状态协议，不验证请求来源的真实性
- ARP应答可以被主动发送（Gratuitous ARP， gratuitous ARP）
- ARP缓存有过期时间（通常Linux为60-300秒不等）

### 1.2 ARP欺骗原理与攻击流程

ARP协议的核心安全缺陷：**任何主机都可以发送未经请求的ARP应答，接收方会无条件更新缓存。**

**ARP欺骗攻击流程：**

```
正常情况：
  主机A ←→ 网关(192.168.1.1)
  主机A的ARP表: 192.168.1.1 → GW_MAC

攻击者(192.168.1.100)介入：

步骤1: 攻击者持续向主机A发送伪造ARP应答
  ┌─────────────────────────────────────┐
  │ ARP Reply (单播给A)                 │
  │ 192.168.1.1 is at ATTACKER_MAC      │  ← 伪造网关MAC
  └─────────────────────────────────────┘

步骤2: 攻击者同时向网关发送伪造ARP应答
  ┌─────────────────────────────────────┐
  │ ARP Reply (单播给网关)              │
  │ 192.168.1.10 is at ATTACKER_MAC     │  ← 伪造主机A的MAC
  └─────────────────────────────────────┘

结果：
  主机A的ARP表: 192.168.1.1 → ATTACKER_MAC  (错误！)
  网关ARP表: 192.168.1.10 → ATTACKER_MAC    (错误！)

  主机A的流量 → 攻击者 → 网关  (中间人)
  网关的流量 → 攻击者 → 主机A  (中间人)
```

### 1.3 中间人攻击（MITM）实现原理

ARP欺骗是MITM攻击在局域网中最常见的实现方式。攻击者在主机与网关之间转发流量，实现流量窃听和篡改。

```
           正常通信路径
  主机A ←─────────────────→ 网关 ←→ 互联网

           ARP欺骗后
  主机A ←──→ 攻击者 ←──→ 网关 ←→ 互联网
              │
              ├── 窃听：抓取密码、Cookie、敏感数据
              ├── 篡改：修改页面内容、注入恶意JS
              └── 注入：替换下载文件、注入恶意代码
```

**典型MITM工具链（仅理论介绍）：**
- `arpspoof`：执行ARP欺骗
- `ettercap`：综合性中间人攻击框架
- `mitmproxy`：HTTP/HTTPS流量代理与篡改

> 注意：上述工具仅用于授权安全测试。在生产网络上使用需获得书面授权。

### 1.4 ARP风暴攻击

ARP风暴（ARP Storm）是攻击者向局域网高速广播大量ARP请求或应答包，导致：

- 交换机CAM表溢出，退化为集线器模式（泛洪攻击）
- 网络设备CPU利用率飙升
- 局域网内合法通信被严重干扰

```
攻击者以每秒数万速率发送ARP请求：
  ┌─────────────────────────────────┐
  │ Who has 192.168.1.1?            │
  │ Who has 192.168.1.2?            │
  │ Who has 192.168.1.3?            │
  │ Who has 192.168.1.4?            │
  │ ... (大量伪造IP)                 │
  └─────────────────────────────────┘
        ↓ 交换机CAM表被填满
  ┌────────────────────┐
  │ 交换机退化为Hub模式 │ → 所有端口泛洪 → 网络瘫痪
  └────────────────────┘
```

---

## 二、ARP攻击检测与防御

### 2.1 静态ARP绑定

最直接有效的防御：将关键设备的IP-MAC映射手动绑定，使其不被ARP欺骗影响。

**Linux静态绑定配置：**

```bash
# 查看当前ARP表
ip neigh show
# 192.168.1.1 dev eth0 lladdr 00:11:22:33:44:55 REACHABLE

# 添加静态ARP绑定（网关）
sudo ip neigh add 192.168.1.1 lladdr 00:11:22:33:44:55 dev eth0 nud permanent

# 或者修改配置文件持久化
# /etc/ethers 文件格式: MAC  IP
echo "00:11:22:33:44:55 192.168.1.1" | sudo tee -a /etc/ethers
# 在 /etc/network/interfaces 中添加:
#   up arp -f /etc/ethers
```

**Windows静态绑定（需管理员权限）：**

```cmd
:: 查看ARP表
arp -a

:: 添加静态绑定
netsh interface ip add neighbors "以太网" 192.168.1.1 00-11-22-33-44-55

:: 删除绑定
netsh interface ip delete neighbors "以太网" 192.168.1.1
```

**局限性：** 静态绑定只保护已绑定的条目，且大规模部署维护成本高。

### 2.2 DAI（动态ARP检测）

DAI（Dynamic ARP Inspection）是交换机层面的防御机制，配合DHCP Snooping使用，对非信任端口的ARP报文进行合法性校验。

**Cisco交换机DAI配置示例：**

```cisco
! 启用DHCP Snooping（DAI依赖其绑定表）
Switch(config)# ip dhcp snooping
Switch(config)# ip dhcp snooping vlan 10

! 指定上联端口为信任端口（连接DHCP服务器或网关）
Switch(config)# interface GigabitEthernet0/24
Switch(config-if)# ip dhcp snooping trust

! 启用DAI
Switch(config)# ip arp inspection vlan 10

! 指定上联端口为ARP信任端口
Switch(config)# interface GigabitEthernet0/24
Switch(config-if)# ip arp inspection trust

! 可选：配置ARP速率限制，防止ARP风暴
Switch(config)# interface range GigabitEthernet0/1-23
Switch(config-if-range)# ip arp inspection limit rate 15 burst interval 1
```

**工作原理：**
1. DHCP Snooping维护IP-MAC绑定表
2. 交换机收到ARP请求/应答时，检查绑定表
3. 不匹配的ARP包被丢弃并记录日志

### 2.3 ARP监控工具（arpwatch等）

**arpwatch** 盽听网络中的ARP活动，记录IP-MAC变化并通过邮件告警。

```bash
# Ubuntu/Debian安装
sudo apt-get install arpwatch

# CentOS/RHEL安装
sudo yum install arpwatch

# 启动arpwatch监听eth0
sudo arpwatch -i eth0 -f /var/lib/arpwatch/arp.dat

# 配置告警邮件接收人
# 修改 /etc/arpwatch.conf:
#   eth0    -m    security@example.com
```

**arpwatch告警示例：**
```
Subject: changed ethernet address

hostname: <unknown>
ip address: 192.168.1.1
ethernet address: 0:11:22:33:44:55  (旧MAC)
ethernet address: 66:77:88:99:aa:bb  (新MAC，可能是ARP欺骗)
timestamp: Saturday, September 12, 2026 10:30:45
```

**其他常用ARP监控工具：**
- `arping`：验证特定IP的MAC地址
- `arping -D`：Duplicate Address Detection
- `Scapy`：构建自定义ARP检测脚本

### 2.4 Python检测脚本示例

以下脚本模拟ARP欺骗检测，通过对比静态绑定表与实际ARP响应来发现异常。

```python
"""
ARP欺骗检测脚本 - 模拟教育版
功能：对比预设的IP-MAC绑定表与实际网络ARP响应，
      发现MAC地址变化则触发告警。
注意：使用模拟数据，不执行真实网络扫描。
"""

import time
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class ARPEntry:
    """ARP表项"""
    ip: str
    mac: str
    last_seen: str
    status: str = "normal"


class ARPTable:
    """模拟ARP缓存管理"""

    def __init__(self, trusted_bindings: Dict[str, str]):
        # trusted_bindings: {"192.168.1.1": "00:11:22:33:44:55", ...}
        self.trusted_bindings = trusted_bindings
        self.current_table: Dict[str, ARPEntry] = {}
        self.alerts = []

    def update_entry(self, ip: str, mac: str):
        """模拟收到一个ARP响应，更新ARP表"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.current_table[ip] = ARPEntry(ip=ip, mac=mac, last_seen=timestamp)

    def check_spoofing(self) -> list:
        """检测是否存在ARP欺骗"""
        alerts = []
        for ip, entry in self.current_table.items():
            trusted_mac = self.trusted_bindings.get(ip)
            if trusted_mac and entry.mac.lower() != trusted_mac.lower():
                alert = (
                    f"[ALERT] ARP欺骗检测! "
                    f"IP={ip}, 预期MAC={trusted_mac}, "
                    f"实际MAC={entry.mac}, "
                    f"时间={entry.last_seen}"
                )
                alerts.append(alert)
                self.alerts.append(alert)
        return alerts

    def print_table(self):
        """打印当前ARP表"""
        print("\n=== 当前ARP缓存表 ===")
        print(f"{'IP地址':<18} {'MAC地址':<22} {'状态':<10} {'最后发现时间'}")
        print("-" * 70)
        for ip, entry in self.current_table.items():
            trusted_mac = self.trusted_bindings.get(ip)
            status = "OK" if (trusted_mac and
                              entry.mac.lower() == trusted_mac.lower()) else "SPOOFED"
            print(f"{entry.ip:<18} {entry.mac:<22} {status:<10} {entry.last_seen}")

    def print_alerts(self):
        """打印所有告警"""
        if not self.alerts:
            print("\n无告警，网络状态正常。")
            return
        print(f"\n=== ARP告警记录 ({len(self.alerts)}条) ===")
        for i, alert in enumerate(self.alerts, 1):
            print(f"[{i}] {alert}")


def main():
    """主函数 - 模拟ARP欺骗检测"""
    # 预设的可信IP-MAC绑定表
    trusted = {
        "192.168.1.1": "00:11:22:33:44:55",   # 网关
        "192.168.1.10": "aa:bb:cc:dd:ee:01",  # 主机A
        "192.168.1.20": "aa:bb:cc:dd:ee:02",  # 主机B
    }

    arp_table = ARPTable(trusted)

    # === 模拟正常ARP响应 ===
    print("=" * 60)
    print("场景1: 正常网络环境")
    print("=" * 60)
    arp_table.update_entry("192.168.1.1", "00:11:22:33:44:55")
    arp_table.update_entry("192.168.1.10", "aa:bb:cc:dd:ee:01")
    arp_table.update_entry("192.168.1.20", "aa:bb:cc:dd:ee:02")
    arp_table.print_table()
    alerts = arp_table.check_spoofing()
    print(f"\n检测结果: {'发现异常!' if alerts else '正常，未检测到ARP欺骗。'}")

    # === 模拟ARP欺骗攻击 ===
    print("\n" + "=" * 60)
    print("场景2: ARP欺骗攻击（网关MAC被伪造）")
    print("=" * 60)
    # 攻击者伪造网关MAC为攻击者MAC
    arp_table.update_entry("192.168.1.1", "de:ad:be:ef:00:01")  # 被篡改!
    arp_table.print_table()
    alerts = arp_table.check_spoofing()
    if alerts:
        print(f"\n检测结果: 发现异常! 共 {len(alerts)} 条告警:")
        for a in alerts:
            print(f"  {a}")

    # === 打印所有历史告警 ===
    arp_table.print_alerts()


if __name__ == "__main__":
    main()
```

**运行输出示例：**
```
============================================================
场景1: 正常网络环境
============================================================

=== 当前ARP缓存表 ===
IP地址             MAC地址               状态       最后发现时间
----------------------------------------------------------------------
192.168.1.1        00:11:22:33:44:55     OK        2026-09-12 10:30:45
192.168.1.10       aa:bb:cc:dd:ee:01     OK        2026-09-12 10:30:45
192.168.1.20       aa:bb:cc:dd:ee:02     OK        2026-09-12 10:30:45

检测结果: 正常，未检测到ARP欺骗。

============================================================
场景2: ARP欺骗攻击（网关MAC被伪造）
============================================================
[ALERT] ARP欺骗检测! IP=192.168.1.1, 预期MAC=00:11:22:33:44:55, 实际MAC=de:ad:be:ef:00:01, 时间=2026-09-12 10:30:46
检测结果: 发现异常! 共 1 条告警:
```

---

## 三、DNS协议基础与安全威胁

### 3.1 DNS协议工作原理

DNS（Domain Name System）是互联网的"电话簿"，负责将人类可读的域名（如 `www.example.com`）转换为IP地址。

**DNS解析流程：**

```
用户访问 www.example.com

步骤1: 查询本地DNS缓存 → 未命中
步骤2: 查询操作系统hosts文件 → 未命中
步骤3: 查询本地配置的递归DNS服务器（如8.8.8.8）

步骤4: 递归DNS服务器开始迭代查询:
  ┌──────────────────────────────────────────────────┐
  │ 4a. 查询根DNS服务器(.)                           │
  │     → 返回 .com TLD服务器地址                      │
  │                                                    │
  │ 4b. 查询 .com TLD服务器                           │
  │     → 返回 example.com 权威服务器地址              │
  │                                                    │
  │ 4c. 查询 example.com 权威服务器                    │
  │     → 返回 www.example.com 的A记录(93.184.216.34) │
  └──────────────────────────────────────────────────┘

步骤5: 递归服务器缓存结果并返回给用户
步骤6: 用户浏览器连接 93.184.216.34:443
```

**DNS记录类型：**

| 记录类型 | 说明 | 示例 |
|---------|------|------|
| A | 域名→IPv4地址 | `example.com. IN A 93.184.216.34` |
| AAAA | 域名→IPv6地址 | `example.com. IN AAAA 2606:2800:220:1::` |
| CNAME | 别名记录 | `www.example.com. IN CNAME example.com.` |
| MX | 邮件交换 | `example.com. IN MX 10 mail.example.com.` |
| TXT | 文本记录（SPF等） | `example.com. IN TXT "v=spf1 -all"` |
| NS | 权威名称服务器 | `example.com. IN NS ns1.example.com.` |

### 3.2 DNS劫持/投毒攻击

**DNS投毒（DNS Poisoning）** 通过向DNS缓存注入伪造记录，使用户访问域名时被导向恶意IP。

```
DNS缓存投毒攻击流程:

1. 用户查询 www.example.com → 递归DNS服务器
2. 递归服务器向权威服务器发起查询（ Transaction ID = 0xAB12）
3. 攻击者抢先向递归服务器发送伪造应答:
   ┌──────────────────────────────────────────┐
   │ DNS Response (伪造)                      │
   │ Transaction ID: 0xAB12 (需猜对)          │
   │ www.example.com → A 6.6.6.6 (恶意IP)     │
   └──────────────────────────────────────────┘
4. 递归服务器缓存伪造记录
5. 后续所有用户访问 www.example.com → 6.6.6.6
```

**DNS劫持类型：**
- **本地DNS劫持**：修改本机hosts文件或DNS配置
- **路由器DNS劫持**：利用路由器弱口令修改DNS设置
- **ISP级DNS劫持**：运营商层面的DNS重定向（常用于广告插入）
- **缓存投毒**：向DNS服务器缓存注入伪造记录

### 3.3 DNS隧道技术

DNS隧道利用DNS协议（53端口）传输非DNS数据，常用于绕过网络访问控制或构建隐蔽C2通道。

```
DNS隧道工作原理:

受控主机                    DNS隧道服务器               C2服务器
   │                              │                        │
   │ 1. 将数据编码为子域名        │                        │
   │    data→base64→xxx.evil.com │                        │
   ├────────────────────────────→│                        │
   │ 2. DNS查询(TXT记录)         │                        │
   │                              │ 3. 解码数据,转发给C2  │
   │                              ├───────────────────────→│
   │                              │ 4. C2响应             │
   │                              ←───────────────────────┤
   │ 5. 伪造DNS TXT应答           │                        │
   │    包含编码后的命令数据       │                        │
   ←────────────────────────────┤                        │
   │ 6. 解码命令并执行            │                        │
```

**常用DNS隧道工具（理论介绍）：**
- `iodine`：IP over DNS隧道
- `dnscat2`：DNS隧道C2框架
- `dns2tcp`：TCP over DNS隧道

### 3.4 DNS放大攻击（DDoS）

DNS放大攻击（DNS Amplification）利用开放DNS解析器，将小请求放大为大响应，实现反射式DDoS。

```
DNS放大攻击流程:

攻击者(伪造源IP=受害者IP)     开放DNS解析器(放大器)      受害者
   │                              │                      │
   │ 1. 发送小DNS查询(60字节)     │                      │
   │    源IP伪造为受害者IP         │                      │
   ├─────────────────────────────→│                      │
   │    查询ANY记录(evil.com)    │                      │
   │    放大倍数: 50-100x         │                      │
   │                              │ 2. 返回大DNS响应     │
   │                              │    (3000-4000字节)   │
   │                              ├─────────────────────→│ 3. 大量流量
   │                              │    大量响应洪泛受害者 │   淹没受害者
   │                              │                      │
```

**放大倍数计算：**
- 请求大小：约60字节（UDP DNS查询）
- 响应大小：约3000-4000字节（ANY查询，含DNSSEC时更大）
- 放大倍数：50x ~ 70x

### 3.5 子域名枚举

子域名枚举是信息收集阶段的重要技术，攻击者通过发现子域名来扩大攻击面。

**子域名枚举方法：**

```
方法1: 字典枚举
  遍历常见子域名字典:
    admin.example.com  → 解析成功 → 存在
    mail.example.com   → 解析成功 → 存在
    test.example.com   → NXDOMAIN → 不存在
    dev.example.com    → 解析成功 → 存在

方法2: 证书透明度日志
  查询 ct.example.com 或 crt.sh:
    搜索 *.example.com 的TLS证书记录
    证书中包含的SAN字段暴露子域名

方法3: DNS区域传送(AXFR)
  dig @ns.example.com example.com AXFR
  (若服务器配置不当,可获取完整区域文件)

方法4: 搜索引擎语法
  Google: site:example.com -www
```

---

## 四、DNS安全防护

### 4.1 DNSSEC原理与部署

DNSSEC（DNS Security Extensions）通过数字签名机制，为DNS解析过程提供数据完整性和来源认证。

**DNSSEC工作原理：**

```
传统DNS解析（无验证）:
  用户 → 递归服务器 → 权威服务器 → 返回IP (无法验证真伪)

DNSSEC解析（带签名验证）:
  用户 → 递归服务器 → 权威服务器 → 返回IP + RRSIG(签名)
                                    ↓
  递归服务器验证签名链:
    RRSIG 用 ZSK 验证 → ZSK 用 KSK 验证 → KSK 用 DS记录验证
    → DS记录由上级区域签名 → 一直追溯到根的KSK(信任锚)
```

**DNSSEC密钥层级：**

```
根区域(.)                        KSK_root (信任锚)
  │ DS记录
TLD(.com)                        KSK_com
  │ DS记录
二级域(example.com)              KSK_example, ZSK_example
  │
  www.example.com  A记录 + RRSIG
```

**BIND DNSSEC配置示例：**

```bash
# 1. 生成密钥对（KSK和ZSK）
dnssec-keygen -a RSASHA256 -b 2048 -f KSK -n ZONE example.com
dnssec-keygen -a RSASHA256 -b 1024 -n ZONE example.com

# 2. 在区域文件中引入密钥
# /etc/bind/db.example.com 中添加:
$INCLUDE Kexample.com.+008+12345.key   ; KSK
$INCLUDE Kexample.com.+008+67890.key   ; ZSK

# 3. 签名区域文件
dnssec-signzone -o example.com -N increment /etc/bind/db.example.com

# 4. 在named.conf中启用DNSSEC
options {
    dnssec-enable yes;
    dnssec-validation auto;
    trust-anchor-telemetry yes;
};
```

### 4.2 DNS over HTTPS/TLS

传统DNS查询使用明文UDP传输，可被窃听和篡改。DoH（DNS over HTTPS）和DoT（DNS over TLS）通过加密传输保护DNS隐私。

```
传统DNS:
  用户 ──(明文UDP 53)──→ DNS服务器
  问题: ISP/中间人可窃听和篡改

DoH (DNS over HTTPS):
  用户 ──(HTTPS加密 443)──→ DoH服务器(如1.1.1.1)
  优势: 与正常HTTPS流量混合，难以区分和封锁

DoT (DNS over TLS):
  用户 ──(TLS加密 853)──→ DoT服务器
  优势: 专用端口，便于网络管理
```

**主流DoH/DoT服务提供商：**

| 服务商 | DoH地址 | DoT地址 |
|--------|---------|---------|
| Cloudflare | `https://cloudflare-dns.com/dns-query` | `1dot1dot1dot1.cloudflare-dns.com` |
| Google | `https://dns.google/dns-query` | `dns.google` |
| Quad9 | `https://dns.quad9.net/dns-query` | `dns.quad9.net` |

### 4.3 DNS防火墙配置

DNS防火墙（Response Policy Zone, RPZ）通过策略重写DNS响应，实现恶意域名阻断。

**BIND RPZ配置示例：**

```bash
# /etc/bind/named.conf.options

# 定义RPZ区域
options {
    response-policy {
        zone "rpz-blocklist";
    };
};

# 创建RPZ区域文件 /etc/bind/rpz-blocklist.db
$TTL 2h
@       IN SOA  localhost. root.localhost. (
            2026091201 3h 1h 1w 1h )
        IN NS   localhost.

; 阻断恶意域名（返回NXDOMAIN）
malware.example.com    IN CNAME .

; 重定向到安全页面
phishing.example.com   IN CNAME safe-page.example.com.

; 阻断特定子域
*.ads.example.com      IN CNAME .
```

**Pi-hole DNS黑洞配置（家庭/小型环境）：**

```bash
# 安装Pi-hole
curl -sSL https://install.pi-hole.net | bash

# 添加黑名单域名
pihole -b malware.example.com phishing.example.com

# 查看DNS查询日志
pihole -t

# 查看统计信息
pihole -stats
```

### 4.4 Python DNS安全检测脚本示例

以下脚本模拟DNS安全检测，检查DNS响应是否被篡改、是否存在DNS放大攻击风险等。

```python
"""
DNS安全检测脚本 - 模拟教育版
功能：
  1. 检测DNS响应是否被篡改（对比多个DNS源的解析结果）
  2. 检测开放DNS解析器（DNS放大攻击风险）
  3. 检测DNS隧道特征（异常长子域名）
注意：使用模拟数据，不执行真实DNS查询。
"""

import re
from datetime import datetime
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DNSRecord:
    """DNS记录"""
    domain: str
    record_type: str  # A, AAAA, CNAME, MX, TXT
    value: str
    ttl: int
    source: str  # 来源DNS服务器标识


class DNSSecurityChecker:
    """DNS安全检测器"""

    def __init__(self):
        self.records: List[DNSRecord] = []
        self.alerts: List[str] = []

    def add_record(self, domain: str, record_type: str,
                   value: str, ttl: int, source: str):
        """添加DNS记录"""
        record = DNSRecord(domain, record_type, value, ttl, source)
        self.records.append(record)

    def check_dns_poisoning(self) -> List[str]:
        """
        检测DNS投毒：对比多个DNS源对同一域名的解析结果。
        若不同源返回不同IP，则可能存在DNS劫持。
        """
        alerts = []
        domain_values: Dict[str, Dict[str, str]] = defaultdict(dict)

        for record in self.records:
            if record.record_type == "A":
                domain_values[record.domain][record.source] = record.value

        for domain, sources in domain_values.items():
            unique_ips = set(sources.values())
            if len(unique_ips) > 1:
                alert = (
                    f"[POISONING?] DNS解析不一致! "
                    f"域名={domain}, "
                    f"各DNS源结果={sources}, "
                    f"不同IP数量={len(unique_ips)}"
                )
                alerts.append(alert)
                self.alerts.append(alert)

        return alerts

    def check_dns_tunneling(self, threshold_length: int = 30) -> List[str]:
        """
        检测DNS隧道：正常子域名长度通常<30字符，
        DNS隧道编码数据会导致子域名过长。
        """
        alerts = []
        for record in self.records:
            # 提取子域名部分
            parts = record.domain.split(".")
            if len(parts) > 2:
                subdomain = ".".join(parts[:-2])
                if len(subdomain) > threshold_length:
                    # 检查是否包含Base64编码特征
                    is_base64 = bool(re.match(
                        r'^[A-Za-z0-9+/=]+$', subdomain
                    ))
                    alert = (
                        f"[TUNNELING?] 可疑长子域名! "
                        f"域名={record.domain}, "
                        f"子域名长度={len(subdomain)}, "
                        f"Base64特征={'是' if is_base64 else '否'}, "
                        f"记录类型={record.record_type}"
                    )
                    alerts.append(alert)
                    self.alerts.append(alert)

        return alerts

    def check_open_resolver(self, known_open_resolvers: List[str]) -> List[str]:
        """
        检测开放DNS解析器：若DNS服务器对任意来源
        的递归查询都响应，则存在放大攻击风险。
        """
        alerts = []
        for record in self.records:
            if record.source in known_open_resolvers:
                alert = (
                    f"[AMPLIFICATION RISK] 开放DNS解析器! "
                    f"源={record.source}, "
                    f"可能被用于DNS放大攻击"
                )
                alerts.append(alert)
                self.alerts.append(alert)
        return alerts

    def print_all_records(self):
        """打印所有DNS记录"""
        print("\n=== DNS记录列表 ===")
        print(f"{'域名':<40} {'类型':<6} {'值':<20} {'TTL':<8} {'来源'}")
        print("-" * 90)
        for r in self.records:
            print(f"{r.domain:<40} {r.record_type:<6} {r.value:<20} {r.ttl:<8} {r.source}")

    def print_alerts(self):
        """打印所有告警"""
        print(f"\n=== DNS安全告警 ({len(self.alerts)}条) ===")
        if not self.alerts:
            print("无告警，DNS解析状态正常。")
            return
        for i, alert in enumerate(self.alerts, 1):
            print(f"[{i}] {alert}")


def main():
    """主函数 - 模拟DNS安全检测"""
    checker = DNSSecurityChecker()

    # 已知开放DNS解析器列表（模拟）
    known_open_resolvers = ["8.8.8.8", "1.1.1.1"]

    # === 场景1: 正常DNS解析 ===
    print("=" * 60)
    print("场景1: 正常DNS解析（多源一致）")
    print("=" * 60)
    checker.add_record("www.example.com", "A", "93.184.216.34", 3600, "Google-8.8.8.8")
    checker.add_record("www.example.com", "A", "93.184.216.34", 3600, "Cloudflare-1.1.1.1")
    checker.add_record("www.example.com", "A", "93.184.216.34", 3600, "Local-Resolver")
    checker.print_all_records()
    alerts = checker.check_dns_poisoning()
    print(f"\nDNS投毒检测: {'发现异常!' if alerts else '正常，各源解析一致。'}")

    # === 场景2: DNS劫持 ===
    print("\n" + "=" * 60)
    print("场景2: DNS劫持（某DNS源返回恶意IP）")
    print("=" * 60)
    checker.add_record("www.example.com", "A", "6.6.6.6", 3600, "ISP-Resolver")
    alerts = checker.check_dns_poisoning()
    if alerts:
        for a in alerts:
            print(f"  {a}")

    # === 场景3: DNS隧道检测 ===
    print("\n" + "=" * 60)
    print("场景3: DNS隧道检测（异常长子域名）")
    print("=" * 60)
    # 模拟DNS隧道数据（Base64编码的长子域名）
    tunnel_domain = "ZWNobyBoZWxsbw0K.evil-tunnel.com"
    checker.add_record(tunnel_domain, "TXT", "base64-encoded-c2-data", 0, "Local-Resolver")
    alerts = checker.check_dns_tunneling()
    if alerts:
        for a in alerts:
            print(f"  {a}")

    # === 场景4: 开放解析器检测 ===
    print("\n" + "=" * 60)
    print("场景4: 开放DNS解析器检测")
    print("=" * 60)
    alerts = checker.check_open_resolver(known_open_resolvers)
    if alerts:
        for a in alerts:
            print(f"  {a}")

    # === 汇总 ===
    checker.print_alerts()


if __name__ == "__main__":
    main()
```

**运行输出示例：**
```
============================================================
场景1: 正常DNS解析（多源一致）
============================================================
DNS投毒检测: 正常，各源解析一致。

============================================================
场景2: DNS劫持（某DNS源返回恶意IP）
============================================================
  [POISONING?] DNS解析不一致! 域名=www.example.com, ...
  不同IP数量=2

============================================================
场景3: DNS隧道检测（异常长子域名）
============================================================
  [TUNNELING?] 可疑长子域名! 域名=ZWNobyBoZWxsbw0K.evil-tunnel.com, ...
  Base64特征=是

=== DNS安全告警 (3条) ===
```

---

## 总结

| 威胁类型 | 核心缺陷 | 关键防御措施 |
|---------|---------|------------|
| ARP欺骗 | ARP无状态、不验证来源 | 静态绑定、DAI、arpwatch |
| ARP风暴 | 交换机CAM表可溢出 | 端口速率限制、端口安全 |
| DNS投毒 | DNS响应无签名验证 | DNSSEC |
| DNS劫持 | DNS明文传输、可篡改 | DoH/DoT、RPZ防火墙 |
| DNS隧道 | DNS端口53通常放行 | DNS防火墙、流量分析 |
| DNS放大 | 开放解析器+源IP伪造 | 关闭递归、BCP38过滤 |
| 子域名枚举 | 公开DNS信息泄露 | 限制区域传送、证书管理 |
