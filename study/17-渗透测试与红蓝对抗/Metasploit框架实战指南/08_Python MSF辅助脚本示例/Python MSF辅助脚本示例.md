# Python MSF辅助脚本示例

以下脚本使用模拟数据，仅用于演示自动化思路。

### 8.1 批量漏洞验证脚本（模拟数据）

```python
#!/usr/bin/env python3
"""
Metasploit 批量漏洞验证辅助脚本
使用模拟数据演示自动化漏洞验证思路
仅用于教育目的
"""
import json
from datetime import datetime
from typing import List, Dict

# 模拟 MSF RPC 客户端接口
class MockMSFRpcClient:
    """模拟 MSF RPC 客户端，不连接真实服务"""
    def __init__(self):
        self.hosts = []
        self.vulns_found = []

    def scan_host(self, host: str, port: int) -> Dict:
        """模拟扫描单个主机"""
        mock_services = {
            445: {"service": "smb", "version": "Windows 7"},
            80: {"service": "http", "version": "Apache 2.4"},
            22: {"service": "ssh", "version": "OpenSSH 7.2"},
            3389: {"service": "rdp", "version": "Microsoft RDP"},
        }
        return {
            "host": host,
            "port": port,
            "state": "open" if port in mock_services else "closed",
            "service": mock_services.get(port, {}).get("service", "unknown"),
        }

    def check_vuln(self, host: str, vuln_module: str) -> Dict:
        """模拟漏洞验证"""
        mock_results = {
            "ms17_010": {"status": "vulnerable", "severity": "critical"},
            "cve_2021_44228": {"status": "not_vulnerable", "severity": "high"},
            "cve_2020_0796": {"status": "vulnerable", "severity": "high"},
        }
        result = mock_results.get(
            vuln_module,
            {"status": "unknown", "severity": "info"}
        )
        result["host"] = host
        result["module"] = vuln_module
        result["timestamp"] = datetime.now().isoformat()
        if result["status"] == "vulnerable":
            self.vulns_found.append(result)
        return result

    def generate_report(self) -> Dict:
        """生成扫描报告"""
        return {
            "scan_time": datetime.now().isoformat(),
            "total_hosts": len(self.hosts),
            "total_vulns": len(self.vulns_found),
            "vulnerabilities": self.vulns_found,
            "summary": self._summarize()
        }

    def _summarize(self) -> str:
        critical = sum(1 for v in self.vulns_found if v["severity"] == "critical")
        high = sum(1 for v in self.vulns_found if v["severity"] == "high")
        return f"Critical: {critical}, High: {high}"


def batch_vuln_check(target_hosts: List[str], vuln_modules: List[str]):
    """批量漏洞验证主流程"""
    client = MockMSFRpcClient()

    print("=" * 60)
    print("Metasploit 批量漏洞验证（模拟模式）")
    print("=" * 60)

    # 阶段一: 端口扫描
    print("\n[阶段一] 端口扫描")
    print("-" * 40)
    scan_ports = [22, 80, 445, 3389, 8080]
    for host in target_hosts:
        client.hosts.append(host)
        print(f"\n扫描主机: {host}")
        for port in scan_ports:
            result = client.scan_host(host, port)
            if result["state"] == "open":
                print(f"  [+] {host}:{port} - {result['service']} OPEN")

    # 阶段二: 漏洞验证
    print("\n[阶段二] 漏洞验证")
    print("-" * 40)
    for host in target_hosts:
        for module in vuln_modules:
            result = client.check_vuln(host, module)
            status = result["status"]
            severity = result["severity"]
            if status == "vulnerable":
                print(f"  [!] {host} - {module}: {status} ({severity})")
            else:
                print(f"  [ok] {host} - {module}: {status}")

    # 阶段三: 生成报告
    print("\n[阶段三] 生成报告")
    print("-" * 40)
    report = client.generate_report()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return report


if __name__ == "__main__":
    # 模拟目标主机列表
    targets = ["192.168.1.10", "192.168.1.20", "192.168.1.30"]
    # 验证模块列表
    modules = ["ms17_010", "cve_2021_44228", "cve_2020_0796"]
    batch_vuln_check(targets, modules)
```

### 8.2 扫描结果导入脚本

```python
#!/usr/bin/env python3
"""
Nmap 扫描结果导入 MSF 数据库辅助脚本
将 Nmap XML 结果解析并格式化为 MSF 可用格式
仅用于教育目的
"""
import xml.etree.ElementTree as ET
import json
from typing import List, Dict


def parse_nmap_xml(xml_file: str) -> List[Dict]:
    """解析 Nmap XML 扫描结果"""
    tree = ET.parse(xml_file)
    root = tree.getroot()

    hosts = []
    for host_elem in root.findall('host'):
        addr_elem = host_elem.find('address')
        if addr_elem is None:
            continue

        host = {
            "address": addr_elem.get('addr'),
            "hostnames": [],
            "ports": [],
            "os": "unknown"
        }

        # 提取主机名
        hostnames_elem = host_elem.find('hostnames')
        if hostnames_elem is not None:
            for hn in hostnames_elem.findall('hostname'):
                host["hostnames"].append(hn.get('name'))

        # 提取端口信息
        ports_elem = host_elem.find('ports')
        if ports_elem is not None:
            for port_elem in ports_elem.findall('port'):
                state = port_elem.find('state')
                service = port_elem.find('service')
                port_info = {
                    "port": int(port_elem.get('portid')),
                    "protocol": port_elem.get('protocol'),
                    "state": state.get('state') if state is not None else "unknown",
                    "service": service.get('name') if service is not None else "unknown",
                    "product": service.get('product') if service is not None else "",
                    "version": service.get('version') if service is not None else ""
                }
                if port_info["state"] == "open":
                    host["ports"].append(port_info)

        # 提取操作系统信息
        os_elem = host_elem.find('os')
        if os_elem is not None:
            osmatch = os_elem.find('osmatch')
            if osmatch is not None:
                host["os"] = osmatch.get('name', 'unknown')

        if host["ports"]:
            hosts.append(host)

    return hosts


def generate_msf_commands(hosts: List[Hosts]) -> str:
    """根据扫描结果生成 MSF 命令"""
    commands = []
    commands.append("# MSF 自动化命令脚本")
    commands.append("# 由扫描结果导入脚本生成")
    commands.append("workspace -a ImportedScan")
    commands.append("")

    for host in hosts:
        addr = host["address"]
        commands.append(f"# === {addr} ===")

        # 根据开放端口生成对应命令
        for port_info in host["ports"]:
            port = port_info["port"]
            service = port_info["service"]

            if service == "smb" or port == 445:
                commands.append(f"setg RHOSTS {addr}")
                commands.append("use auxiliary/scanner/smb/smb_ms17_010")
                commands.append("run")
                commands.append("")

            elif service == "ssh" or port == 22:
                commands.append(f"setg RHOSTS {addr}")
                commands.append("use auxiliary/scanner/ssh/ssh_version")
                commands.append("run")
                commands.append("")

            elif service == "http" or port in [80, 8080]:
                commands.append(f"setg RHOSTS {addr}")
                commands.append("use auxiliary/scanner/http/http_version")
                commands.append("run")
                commands.append("")

            elif service == "mssql" or port == 1433:
                commands.append(f"setg RHOSTS {addr}")
                commands.append("use auxiliary/scanner/mssql/mssql_ping")
                commands.append("run")
                commands.append("")

    return "\n".join(commands)


# 使用示例（需提供真实 Nmap XML 文件）:
# nmap -sV -oX scan_results.xml 192.168.1.0/24
# hosts = parse_nmap_xml("scan_results.xml")
# commands = generate_msf_commands(hosts)
# print(commands)
# 保存为 .rc 文件: with open("auto_scan.rc", "w") as f: f.write(commands)
```

---

> **免责声明**: 本文档仅用于网络安全教育和授权渗透测试培训。所有技术说明均基于教育目的，不提供可直接用于未授权系统的攻击方法。未经授权对他人系统进行渗透测试属于违法行为。使用 Metasploit 等工具时，请确保已获得合法书面授权。

---

