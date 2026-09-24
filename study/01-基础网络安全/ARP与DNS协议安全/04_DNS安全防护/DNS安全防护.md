# DNS安全防护

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

---

