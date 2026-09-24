# Python VPN安全检测脚本示例

以下脚本使用模拟数据，仅用于安全学习和防御检测，不应用于未授权测试。

### 6.1 VPN配置安全审计脚本

```python
#!/usr/bin/env python3
"""
VPN配置安全审计工具
功能：检查OpenVPN/WireGuard配置文件的安全设置
用途：安全合规自查与加固验证
注意：仅检测本地配置文件，使用模拟数据
"""

import re
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class SecurityCheck:
    """单项安全检查结果"""
    name: str
    status: str  # PASS / FAIL / WARN
    expected: str
    actual: str
    recommendation: str = ""


@dataclass
class AuditReport:
    """审计报告"""
    target: str
    checks: List[SecurityCheck] = field(default_factory=list)

    @property
    def pass_count(self) -> int:
        return sum(1 for c in self.checks if c.status == "PASS")

    @property
    def fail_count(self) -> int:
        return sum(1 for c in self.checks if c.status == "FAIL")

    @property
    def warn_count(self) -> int:
        return sum(1 for c in self.checks if c.status == "WARN")

    def print_report(self):
        print(f"\n{'='*60}")
        print(f"  VPN配置安全审计报告: {self.target}")
        print(f"{'='*60}")
        print(f"  通过: {self.pass_count}  失败: {self.fail_count}  警告: {self.warn_count}")
        print(f"{'='*60}\n")

        for check in self.checks:
            icon = {"PASS": "[OK]", "FAIL": "[X]", "WARN": "[!]"}[check.status]
            print(f"  {icon} {check.name}")
            print(f"      期望: {check.expected}")
            print(f"      实际: {check.actual}")
            if check.recommendation:
                print(f"      建议: {check.recommendation}")
            print()

        score = (self.pass_count / len(self.checks)) * 100 if self.checks else 0
        print(f"{'='*60}")
        print(f"  安全评分: {score:.0f}/100")
        print(f"{'='*60}")


def audit_openvpn_config(config_text: str) -> AuditReport:
    """审计OpenVPN配置"""
    report = AuditReport(target="OpenVPN Server Config")

    # 模拟配置内容用于演示
    config_text = """
    port 1194
    proto udp
    dev tun0
    cipher AES-256-GCM
    auth SHA512
    tls-version-min 1.2
    remote-cert-tls client
    user nobody
    group nogroup
    # dh dh.pem  # 旧版DH参数（未配置）
    tls-crypt /etc/openvpn/tls-crypt.key
    # 未配置CRL验证
    """

    lines = config_text.strip().split("\n")
    config_dict = {}
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#"):
            parts = line.split(None, 1)
            if len(parts) >= 2:
                config_dict[parts[0]] = parts[1]

    # 检查加密算法
    cipher = config_dict.get("cipher", "")
    if "AES-256-GCM" in cipher or "AES-128-GCM" in cipher:
        report.checks.append(SecurityCheck(
            name="加密算法",
            status="PASS",
            expected="AES-256-GCM 或 AES-128-GCM",
            actual=cipher
        ))
    elif "AES-256-CBC" in cipher:
        report.checks.append(SecurityCheck(
            name="加密算法",
            status="WARN",
            expected="AES-256-GCM（推荐GCM模式）",
            actual=cipher,
            recommendation="升级到GCM认证加密模式"
        ))
    else:
        report.checks.append(SecurityCheck(
            name="加密算法",
            status="FAIL",
            expected="AES-256-GCM",
            actual=cipher or "未配置",
            recommendation="配置强加密算法"
        ))

    # 检查TLS版本
    tls_min = config_dict.get("tls-version-min", "")
    if "1.2" in tls_min or "1.3" in tls_min:
        report.checks.append(SecurityCheck(
            name="TLS最低版本",
            status="PASS",
            expected="TLS 1.2+",
            actual=tls_min
        ))
    else:
        report.checks.append(SecurityCheck(
            name="TLS最低版本",
            status="FAIL",
            expected="tls-version-min 1.2",
            actual=tls_min or "未配置",
            recommendation="禁用TLS 1.0/1.1，设置最低版本1.2"
        ))

    # 检查权限降级
    user_set = "user" in config_dict
    group_set = "group" in config_dict
    if user_set and group_set:
        report.checks.append(SecurityCheck(
            name="权限降级",
            status="PASS",
            expected="user nobody + group nogroup",
            actual=f"user={config_dict.get('user')}, group={config_dict.get('group')}"
        ))
    else:
        report.checks.append(SecurityCheck(
            name="权限降级",
            status="FAIL",
            expected="user nobody + group nogroup",
            actual="未配置权限降级",
            recommendation="降权运行以减少提权风险"
        ))

    # 检查tls-crypt
    if "tls-crypt" in config_dict or "tls-auth" in config_dict:
        report.checks.append(SecurityCheck(
            name="控制通道保护",
            status="PASS",
            expected="tls-crypt 或 tls-auth",
            actual="已配置"
        ))
    else:
        report.checks.append(SecurityCheck(
            name="控制通道保护",
            status="FAIL",
            expected="tls-crypt",
            actual="未配置",
            recommendation="配置tls-crypt防止DoS和未认证连接"
        ))

    # 检查客户端证书验证
    if "remote-cert-tls" in config_dict:
        report.checks.append(SecurityCheck(
            name="客户端证书验证",
            status="PASS",
            expected="remote-cert-tls client",
            actual=config_dict.get("remote-cert-tls", "")
        ))
    else:
        report.checks.append(SecurityCheck(
            name="客户端证书验证",
            status="FAIL",
            expected="remote-cert-tls client",
            actual="未配置",
            recommendation="验证客户端证书扩展"
        ))

    return report


def audit_wireguard_config(config_text: str) -> AuditReport:
    """审计WireGuard配置"""
    report = AuditReport(target="WireGuard Config")

    # 模拟配置
    config_text = """
    [Interface]
    Address = 10.8.0.1/24
    ListenPort = 51820
    PrivateKey = ABCD1234EFGH5678IJKL9012MNOP3456QRST7890UVWX1234YZAB5678CDEF9012=
    PostUp = iptables -A FORWARD -i wg0 -j ACCEPT

    [Peer]
    PublicKey = WXYZ9012ABCD3456EFGH7890IJKL1234MNOP5678QRST9012UVWX3456YZAB7890=
    AllowedIPs = 10.8.0.2/32
    """

    # 检查私钥长度
    key_match = re.search(r'PrivateKey\s*=\s*(\S+)', config_text)
    if key_match:
        key = key_match.group(1).rstrip("=")
        if len(key) == 43:  # WireGuard base64编码私钥（不含padding）为43字符
            report.checks.append(SecurityCheck(
                name="私钥格式",
                status="PASS",
                expected="32字节(256位)Curve25519私钥",
                actual=f"密钥长度正常({len(key)}字符)"
            ))
        else:
            report.checks.append(SecurityCheck(
                name="私钥格式",
                status="WARN",
                expected="32字节私钥",
                actual=f"密钥长度异常({len(key)}字符)",
                recommendation="重新生成密钥对"
            ))

    # 检查AllowedIPs限制
    peers = config_text.split("[Peer]")
    for i, peer_block in enumerate(peers[1:], 1):
        allowed_match = re.search(r'AllowedIPs\s*=\s*(.+)', peer_block)
        if allowed_match:
            allowed = allowed_match.group(1).strip()
            if "/32" in allowed:
                report.checks.append(SecurityCheck(
                    name=f"Peer{i} AllowedIPs",
                    status="PASS",
                    expected="/32 单主机限制",
                    actual=allowed
                ))
            elif "0.0.0.0/0" in allowed and "ListenPort" not in peer_block:
                report.checks.append(SecurityCheck(
                    name=f"Peer{i} AllowedIPs",
                    status="WARN",
                    expected="/32 单主机限制（服务端）",
                    actual=allowed,
                    recommendation="服务端应限制为/32单主机"
                ))

    # 检查PostUp/PostDown防火墙规则
    if "PostUp" in config_text and "PostDown" in config_text:
        report.checks.append(SecurityCheck(
            name="防火墙规则配对",
            status="PASS",
            expected="PostUp + PostDown成对配置",
            actual="已配置"
        ))
    elif "PostUp" in config_text:
        report.checks.append(SecurityCheck(
            name="防火墙规则配对",
            status="WARN",
            expected="PostUp + PostDown成对配置",
            actual="仅有PostUp",
            recommendation="配置PostDown确保关闭时清理规则"
        ))

    return report


if __name__ == "__main__":
    print("=" * 60)
    print("  VPN配置安全审计工具 v1.0")
    print("  使用模拟配置数据 - 仅用于安全学习")
    print("=" * 60)

    # 审计OpenVPN配置
    openvpn_report = audit_openvpn_config("")
    openvpn_report.print_report()

    # 审计WireGuard配置
    wg_report = audit_wireguard_config("")
    wg_report.print_report()

    print("\n审计完成。请根据报告修复FAIL项并关注WARN项。")
```

### 6.2 VPN流量异常检测脚本

```python
#!/usr/bin/env python3
"""
VPN流量异常检测工具
功能：分析VPN连接日志，检测异常行为
用途：安全运营中心(SOC)辅助分析
注意：使用模拟日志数据，不读取真实VPN日志
"""

import re
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Tuple


@dataclass
class VPNSession:
    """VPN会话记录"""
    timestamp: datetime
    username: str
    source_ip: str
    action: str  # LOGIN / LOGOUT / AUTH_FAIL
    bytes_in: int = 0
    bytes_out: int = 0
    duration: int = 0


@dataclass
class AnomalyAlert:
    """异常告警"""
    severity: str  # HIGH / MEDIUM / LOW
    alert_type: str
    description: str
    username: str
    source_ip: str
    timestamp: datetime


def generate_mock_sessions() -> List[VPNSession]:
    """生成模拟VPN会话数据用于演示"""
    sessions = []
    base_time = datetime(2024, 3, 15, 8, 0, 0)

    # 正常用户会话
    sessions.extend([
        VPNSession(base_time, "alice", "192.168.1.10", "LOGIN", 1024, 2048, 28800),
        VPNSession(base_time + timedelta(hours=8), "alice", "192.168.1.10", "LOGOUT"),
        VPNSession(base_time, "bob", "192.168.1.20", "LOGIN", 512, 1024, 28800),
    ])

    # 异常：暴力破解（同IP多次认证失败）
    for i in range(15):
        sessions.append(VPNSession(
            base_time + timedelta(seconds=i * 2),
            "admin", "203.0.113.50", "AUTH_FAIL"
        ))

    # 异常：不可能旅行（不同地理位置短时间内登录）
    sessions.append(VPNSession(
        base_time + timedelta(minutes=5),
        "charlie", "198.51.100.10", "LOGIN"  # 北京IP
    ))
    sessions.append(VPNSession(
        base_time + timedelta(minutes=10),
        "charlie", "203.0.113.99", "LOGIN"  # 不同IP，10分钟内
    ))

    # 异常：异常大流量
    sessions.append(VPNSession(
        base_time + timedelta(hours=2),
        "dave", "192.168.1.30", "LOGIN",
        bytes_in=50000,  # 50GB
        bytes_out=100,
        duration=7200
    ))

    # 异常：非工作时间登录
    sessions.append(VPNSession(
        datetime(2024, 3, 15, 3, 30, 0),
        "eve", "192.168.1.40", "LOGIN"
    ))

    return sessions


def detect_brute_force(sessions: List[VPNSession]) -> List[AnomalyAlert]:
    """检测暴力破解"""
    alerts = []
    auth_fails = defaultdict(list)

    for s in sessions:
        if s.action == "AUTH_FAIL":
            auth_fails[s.source_ip].append(s)

    for ip, fails in auth_fails.items():
        # 同一IP在5分钟内超过5次认证失败
        if len(fails) > 5:
            time_span = (fails[-1].timestamp - fails[0].timestamp).total_seconds()
            if time_span < 300:
                alerts.append(AnomalyAlert(
                    severity="HIGH",
                    alert_type="暴力破解",
                    description=f"IP {ip} 在{time_span:.0f}秒内"
                                f"尝试{len(fails)}次认证失败",
                    username=fails[0].username,
                    source_ip=ip,
                    timestamp=fails[0].timestamp
                ))

    return alerts


def detect_impossible_travel(sessions: List[VPNSession]) -> List[AnomalyAlert]:
    """检测不可能旅行"""
    alerts = []
    user_logins = defaultdict(list)

    for s in sessions:
        if s.action == "LOGIN":
            user_logins[s.username].append(s)

    for user, logins in user_logins.items():
        logins.sort(key=lambda x: x.timestamp)
        for i in range(1, len(logins)):
            time_diff = (logins[i].timestamp - logins[i-1].timestamp).total_seconds()
            # 30分钟内从不同IP登录
            if time_diff < 1800 and logins[i].source_ip != logins[i-1].source_ip:
                alerts.append(AnomalyAlert(
                    severity="MEDIUM",
                    alert_type="不可能旅行",
                    description=f"用户 {user} 在{time_diff/60:.1f}分钟内"
                                f"从不同IP登录: "
                                f"{logins[i-1].source_ip} → {logins[i].source_ip}",
                    username=user,
                    source_ip=logins[i].source_ip,
                    timestamp=logins[i].timestamp
                ))

    return alerts


def detect_anomalous_traffic(sessions: List[Session]) -> List[AnomalyAlert]:
    """检测异常流量"""
    alerts = []
    threshold_bytes = 10 * 1024 * 1024  # 10GB阈值（模拟值）

    for s in sessions:
        if s.action == "LOGIN" and s.bytes_in > threshold_bytes:
            alerts.append(AnomalyAlert(
                severity="HIGH",
                alert_type="异常大流量",
                description=f"用户 {s.username} 下载量异常: "
                            f"{s.bytes_in / (1024*1024):.1f}GB",
                username=s.username,
                source_ip=s.source_ip,
                timestamp=s.timestamp
            ))

    return alerts


def detect_off_hours_access(sessions: List[VPNSession]) -> List[AnomalyAlert]:
    """检测非工作时间访问"""
    alerts = []
    work_start = 7  # 7:00
    work_end = 20   # 20:00

    for s in sessions:
        if s.action == "LOGIN":
            hour = s.timestamp.hour
            if hour < work_start or hour >= work_end:
                alerts.append(AnomalyAlert(
                    severity="LOW",
                    alert_type="非工作时间登录",
                    description=f"用户 {s.username} 在{s.timestamp.strftime('%H:%M')}登录",
                    username=s.username,
                    source_ip=s.source_ip,
                    timestamp=s.timestamp
                ))

    return alerts


def print_alerts(alerts: List[AnomalyAlert]):
    """打印告警报告"""
    severity_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    alerts.sort(key=lambda a: severity_order.get(a.severity, 99))

    print(f"\n{'='*70}")
    print(f"  VPN异常行为检测报告")
    print(f"  检测时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")

    if not alerts:
        print("  未检测到异常行为。")
        return

    stats = Counter(a.severity for a in alerts)
    print(f"  告警统计: 高危={stats['HIGH']} 中危={stats['MEDIUM']} 低危={stats['LOW']}")
    print(f"{'='*70}\n")

    for i, alert in enumerate(alerts, 1):
        icon = {"HIGH": "[!!!]", "MEDIUM": "[!!]", "LOW": "[!]"}[alert.severity]
        print(f"  告警 #{i} {icon} [{alert.severity}] {alert.alert_type}")
        print(f"    时间: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"    用户: {alert.username}")
        print(f"    来源: {alert.source_ip}")
        print(f"    描述: {alert.description}")
        print()


if __name__ == "__main__":
    print("=" * 70)
    print("  VPN流量异常检测工具 v1.0")
    print("  使用模拟数据 - 仅用于安全学习")
    print("=" * 70)

    # 生成模拟会话数据
    sessions = generate_mock_sessions()
    print(f"\n  已加载 {len(sessions)} 条模拟VPN会话记录")

    # 执行检测
    all_alerts = []
    all_alerts.extend(detect_brute_force(sessions))
    all_alerts.extend(detect_impossible_travel(sessions))
    all_alerts.extend(detect_anomalous_traffic(sessions))
    all_alerts.extend(detect_off_hours_access(sessions))

    # 输出报告
    print_alerts(all_alerts)

    print("\n  建议将此检测逻辑集成到SIEM系统中实现自动化告警。")
```

---

---

