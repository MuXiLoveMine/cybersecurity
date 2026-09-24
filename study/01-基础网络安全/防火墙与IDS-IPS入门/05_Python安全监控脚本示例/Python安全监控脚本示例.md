# Python安全监控脚本示例

### 5.1 日志分析脚本

```python
"""
安全日志分析脚本 - 模拟教育版
功能：分析模拟的Web访问日志，检测以下安全威胁：
  - 暴力破解（同一IP大量401响应）
  - 目录扫描（大量404响应）
  - SQL注入特征检测
  - 路径遍历攻击检测
注意：使用模拟日志数据，不读取真实系统日志。
"""

import re
from collections import defaultdict, Counter
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class LogEntry:
    """日志条目"""
    timestamp: str
    client_ip: str
    method: str
    path: str
    status: int
    bytes_sent: int


class LogAnalyzer:
    """安全日志分析器"""

    def __init__(self):
        self.entries: List[LogEntry] = []
        self.alerts: List[str] = []

    def add_entry(self, timestamp: str, client_ip: str, method: str,
                  path: str, status: int, bytes_sent: int = 0):
        """添加日志条目"""
        self.entries.append(LogEntry(
            timestamp, client_ip, method, path, status, bytes_sent
        ))

    def check_brute_force(self, threshold: int = 10,
                          window: int = 300) -> List[str]:
        """检测暴力破解（大量401/403响应）"""
        alerts = []
        # 按IP统计401/403响应
        ip_failures: Dict[str, int] = defaultdict(int)
        for entry in self.entries:
            if entry.status in (401, 403):
                ip_failures[entry.client_ip] += 1

        for ip, count in sorted(ip_failures.items(),
                                key=lambda x: x[1], reverse=True):
            if count >= threshold:
                alert = (
                    f"[BRUTE FORCE] 暴力破解检测! "
                    f"IP={ip}, "
                    f"失败请求={count}次(401/403), "
                    f"阈值={threshold}"
                )
                alerts.append(alert)
                self.alerts.append(alert)
        return alerts

    def check_dir_scan(self, threshold: int = 20) -> List[str]:
        """检测目录扫描（大量404响应）"""
        alerts = []
        ip_404: Dict[str, int] = defaultdict(int)
        for entry in self.entries:
            if entry.status == 404:
                ip_404[entry.client_ip] += 1

        for ip, count in sorted(ip_404.items(),
                                key=lambda x: x[1], reverse=True):
            if count >= threshold:
                alert = (
                    f"[DIR SCAN] 目录扫描检测! "
                    f"IP={ip}, "
                    f"404响应={count}次, "
                    f"阈值={threshold}"
                )
                alerts.append(alert)
                self.alerts.append(alert)
        return alerts

    def check_sqli(self) -> List[str]:
        """检测SQL注入特征"""
        alerts = []
        sqli_patterns = [
            r"(?i)union\s+select",
            r"(?i)'\s*or\s*'?\d+'?\s*=\s*'?\d+",
            r"(?i)select\s+.*\s+from\s+",
            r"(?i)insert\s+into\s+",
            r"(?i)drop\s+table\s+",
            r"(?i)exec(\s|\()+",
            r"(?i)xp_cmdshell",
            r"(?i)(%27|')\s*(or|and)\s*",
        ]

        for entry in self.entries:
            for pattern in sqli_patterns:
                if re.search(pattern, entry.path):
                    alert = (
                        f"[SQL INJECTION] SQL注入特征! "
                        f"IP={entry.client_ip}, "
                        f"路径={entry.path}, "
                        f"匹配模式={pattern}, "
                        f"时间={entry.timestamp}"
                    )
                    alerts.append(alert)
                    self.alerts.append(alert)
                    break  # 每条日志只告警一次
        return alerts

    def check_path_traversal(self) -> List[str]:
        """检测路径遍历攻击"""
        alerts = []
        traversal_patterns = [
            r"\.\./",
            r"\.\.\\",
            r"%2e%2e%2f",
            r"%2e%2e%5c",
            r"\.\.%2f",
            r"\.\.%5c",
            r"/etc/passwd",
            r"/etc/shadow",
            r"c:\\windows\\system32",
        ]

        for entry in self.entries:
            for pattern in traversal_patterns:
                if re.search(pattern, entry.path, re.IGNORECASE):
                    alert = (
                        f"[PATH TRAVERSAL] 路径遍历攻击! "
                        f"IP={entry.client_ip}, "
                        f"路径={entry.path}, "
                        f"时间={entry.timestamp}"
                    )
                    alerts.append(alert)
                    self.alerts.append(alert)
                    break
        return alerts

    def print_summary(self):
        """打印分析摘要"""
        print(f"\n=== 日志分析摘要 ===")
        print(f"  总请求数: {len(self.entries)}")
        status_counts = Counter(e.status for e in self.entries)
        print(f"  状态码分布: {dict(sorted(status_counts.items()))}")
        ip_counts = Counter(e.client_ip for e in self.entries)
        print(f"  TOP 5 IP:")
        for ip, count in ip_counts.most_common(5):
            print(f"    {ip}: {count}次请求")

    def print_alerts(self):
        """打印所有安全告警"""
        print(f"\n=== 安全告警 ({len(self.alerts)}条) ===")
        if not self.alerts:
            print("  无告警，日志未发现安全威胁。")
            return
        for i, alert in enumerate(self.alerts, 1):
            print(f"  [{i}] {alert}")


def main():
    """主函数 - 模拟日志分析"""
    analyzer = LogAnalyzer()

    # === 场景1: 正常流量 ===
    print("=" * 60)
    print("场景1: 正常Web访问流量")
    print("=" * 60)
    normal_ips = [f"10.0.0.{i}" for i in range(1, 21)]
    import random
    random.seed(42)
    for i in range(100):
        ip = random.choice(normal_ips)
        paths = ["/", "/index.html", "/about", "/products",
                 "/api/v1/users", "/static/style.css"]
        analyzer.add_entry(
            timestamp=f"2026-09-12 10:{i:02d}:00",
            client_ip=ip,
            method="GET",
            path=random.choice(paths),
            status=200,
        )
    analyzer.print_summary()
    analyzer.check_brute_force()
    analyzer.check_dir_scan()
    analyzer.check_sqli()
    analyzer.check_path_traversal()
    analyzer.print_alerts()

    # === 场景2: 暴力破解 + 目录扫描 ===
    print("\n" + "=" * 60)
    print("场景2: 暴力破解 + 目录扫描")
    print("=" * 60)
    attacker_ip = "203.0.113.66"
    # 模拟暴力破解（401响应）
    for i in range(15):
        analyzer.add_entry(
            timestamp=f"2026-09-12 14:{i:02d}:00",
            client_ip=attacker_ip,
            method="POST",
            path="/login",
            status=401,
        )
    # 模拟目录扫描（404响应）
    scan_paths = ["/admin", "/phpmyadmin", "/.env", "/wp-admin",
                  "/config.php", "/backup.zip", "/.git/config"]
    for i, path in enumerate(scan_paths * 4):  # 28次404
        analyzer.add_entry(
            timestamp=f"2026-09-12 15:{i:02d}:00",
            client_ip=attacker_ip,
            method="GET",
            path=path,
            status=404,
        )
    analyzer.check_brute_force()
    analyzer.check_dir_scan()

    # === 场景3: SQL注入 + 路径遍历 ===
    print("\n" + "=" * 60)
    print("场景3: SQL注入 + 路径遍历攻击")
    print("=" * 60)
    sqli_ip = "198.51.100.77"
    analyzer.add_entry(
        "2026-09-12 16:00:00", sqli_ip, "GET",
        "/products?id=1 UNION SELECT username,password FROM users", 200
    )
    analyzer.add_entry(
        "2026-09-12 16:01:00", sqli_ip, "GET",
        "/login?user=admin' OR '1'='1", 200
    )
    analyzer.add_entry(
        "2026-09-12 16:02:00", sqli_ip, "GET",
        "/download?file=../../../etc/passwd", 200
    )
    analyzer.add_entry(
        "2026-09-12 16:03:00", sqli_ip, "GET",
        "/page?tpl=../../etc/shadow", 200
    )
    analyzer.check_sqli()
    analyzer.check_path_traversal()

    # === 最终汇总 ===
    analyzer.print_summary()
    analyzer.print_alerts()


if __name__ == "__main__":
    main()
```

### 5.2 端口监控脚本

```python
"""
端口监控脚本 - 模拟教育版
功能：监控主机开放端口变化，检测以下风险：
  - 新增异常端口（可能后门）
  - 监听端口变化
  - 非标准端口上的服务
注意：使用模拟端口数据，不执行真实系统命令。
"""

from dataclasses import dataclass
from typing import Dict, List, Set
from datetime import datetime


@dataclass
class PortInfo:
    """端口信息"""
    port: int
    protocol: str  # tcp / udp
    state: str     # LISTEN / ESTABLISHED
    process: str   # 进程名
    pid: int       # 进程ID


# 常见合法服务端口白名单
LEGITIMATE_PORTS = {
    22: "SSH",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    443: "HTTPS",
    3306: "MySQL",
    5432: "PostgreSQL",
    6379: "Redis",
    8080: "HTTP-Alt",
    9090: "Prometheus",
}

# 已知恶意/可疑端口
SUSPICIOUS_PORTS = {
    4444: "Metasploit Meterpreter",
    31337: "Back Orifice / Elite",
    12345: "NetBus",
    6667: "IRC Botnet (常见)",
    6660: "IRC Botnet",
    9001: "Tor / 代理",
    5900: "VNC (需确认是否授权)",
}


class PortMonitor:
    """端口监控器"""

    def __init__(self):
        self.baseline_ports: Set[int] = set()
        self.current_ports: Set[int] = set()
        self.port_details: Dict[int, PortInfo] = {}

    def set_baseline(self, ports: List[PortInfo]):
        """设置基线端口"""
        for p in ports:
            self.baseline_ports.add(p.port)
        print(f"基线端口已设置: {sorted(self.baseline_ports)}")

    def scan_current(self, ports: List[PortInfo]):
        """扫描当前端口"""
        self.current_ports = set()
        self.port_details = {}
        for p in ports:
            self.current_ports.add(p.port)
            self.port_details[p.port] = p

    def check_new_ports(self) -> List[str]:
        """检测新增端口"""
        alerts = []
        new_ports = self.current_ports - self.baseline_ports
        for port in sorted(new_ports):
            detail = self.port_details.get(port)
            proc = detail.process if detail else "unknown"
            if port in SUSPICIOUS_PORTS:
                alert = (
                    f"[HIGH] 新增可疑端口! "
                    f"端口={port}/{detail.protocol if detail else '?'}, "
                    f"进程={proc}, "
                    f"已知关联={SUSPICIOUS_PORTS[port]}"
                )
            elif port in LEGITIMATE_PORTS:
                alert = (
                    f"[INFO] 新增标准端口: "
                    f"端口={port}, "
                    f"服务={LEGITIMATE_PORTS[port]}, "
                    f"进程={proc}"
                )
            else:
                alert = (
                    f"[MEDIUM] 新增未知端口: "
                    f"端口={port}/{detail.protocol if detail else '?'}, "
                    f"进程={proc}, "
                    f"需人工确认"
                )
            alerts.append(alert)
        return alerts

    def check_closed_ports(self) -> List[str]:
        """检测关闭的端口"""
        alerts = []
        closed = self.baseline_ports - self.current_ports
        for port in sorted(closed):
            service = LEGITIMATE_PORTS.get(port, "unknown")
            alerts.append(
                f"[INFO] 端口已关闭: "
                f"端口={port}, 原服务={service}"
            )
        return alerts

    def check_suspicious(self) -> List[str]:
        """检测已知可疑端口"""
        alerts = []
        for port in self.current_ports:
            if port in SUSPICIOUS_PORTS:
                detail = self.port_details.get(port)
                alert = (
                    f"[CRITICAL] 检测到可疑端口! "
                    f"端口={port}, "
                    f"进程={detail.process if detail else '?'}, "
                    f"PID={detail.pid if detail else '?'}, "
                    f"已知关联={SUSPICIOUS_PORTS[port]}"
                )
                alerts.append(alert)
        return alerts

    def print_current(self):
        """打印当前端口状态"""
        print(f"\n=== 当前监听端口 ({len(self.current_ports)}个) ===")
        print(f"{'端口':<10} {'协议':<6} {'状态':<12} {'进程':<15} {'PID':<8} {'备注'}")
        print("-" * 75)
        for port in sorted(self.current_ports):
            d = self.port_details.get(port)
            if d:
                note = LEGITIMATE_PORTS.get(port, "")
                if port in SUSPICIOUS_PORTS:
                    note = f"⚠ {SUSPICIOUS_PORTS[port]}"
                print(f"{d.port:<10} {d.protocol:<6} {d.state:<12} "
                      f"{d.process:<15} {d.pid:<8} {note}")


def main():
    """主函数 - 模拟端口监控"""
    monitor = PortMonitor()

    # === 设置基线端口 ===
    print("=" * 60)
    print("步骤1: 建立端口基线（正常运行状态）")
    print("=" * 60)
    baseline = [
        PortInfo(22, "tcp", "LISTEN", "sshd", 1234),
        PortInfo(80, "tcp", "LISTEN", "nginx", 5678),
        PortInfo(443, "tcp", "LISTEN", "nginx", 5678),
        PortInfo(3306, "tcp", "LISTEN", "mysqld", 9012),
    ]
    monitor.set_baseline(baseline)

    # === 场景1: 正常（无变化） ===
    print("\n" + "=" * 60)
    print("场景1: 端口无变化（正常）")
    print("=" * 60)
    monitor.scan_current(baseline)
    monitor.print_current()
    alerts = monitor.check_new_ports() + monitor.check_suspicious()
    print(f"\n检测结果: {'发现异常!' if alerts else '正常，端口无变化。'}")

    # === 场景2: 新增可疑端口（后门） ===
    print("\n" + "=" * 60)
    print("场景2: 检测到新增可疑端口（可能后门）")
    print("=" * 60)
    current = [
        PortInfo(22, "tcp", "LISTEN", "sshd", 1234),
        PortInfo(80, "tcp", "LISTEN", "nginx", 5678),
        PortInfo(443, "tcp", "LISTEN", "nginx", 5678),
        PortInfo(3306, "tcp", "LISTEN", "mysqld", 9012),
        # 新增可疑端口
        PortInfo(4444, "tcp", "LISTEN", "unknown", 6666),
        PortInfo(31337, "tcp", "LISTEN", "unknown", 7777),
        # 新增非标准端口
        PortInfo(9999, "tcp", "LISTEN", "python3", 8888),
    ]
    monitor.scan_current(current)
    monitor.print_current()

    all_alerts = []
    all_alerts.extend(monitor.check_new_ports())
    all_alerts.extend(monitor.check_closed_ports())
    all_alerts.extend(monitor.check_suspicious())

    print(f"\n=== 端口监控告警 ({len(all_alerts)}条) ===")
    for i, alert in enumerate(all_alerts, 1):
        print(f"  [{i}] {alert}")


if __name__ == "__main__":
    main()
```

---

---

