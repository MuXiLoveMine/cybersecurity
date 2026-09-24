# Windows内存分析

### 4.1 进程提取

```bash
# 进程列表
vol -f memory.raw windows.pslist

# 输出示例：
# Offset    Name                 PID    PPID   CreateTime
# 0x...     System               4      0      2024-01-15 08:00:00
# 0x...     smss.exe             264    4      2024-01-15 08:00:02
# 0x...     csrss.exe            372    360    2024-01-15 08:00:05
# 0x...     wininit.exe          392    360    2024-01-15 08:00:05
# 0x...     services.exe         668    392    2024-01-15 08:00:06
# 0x...     lsass.exe            692    392    2024-01-15 08:00:06
# 0x...     svchost.exe          860    668    2024-01-15 08:00:08

# 进程树（显示父子关系）
vol -f memory.raw windows.pstree

# 进程扫描（发现被隐藏的进程）
vol -f memory.raw windows.psscan

# 多视图交叉验证（对比不同方法的检测结果）
# Volatility 2: psxview
# Volatility 3中需要手动对比pslist和psscan

# 提取进程可执行文件
vol -f memory.raw windows.pslist --pid 1234 --dump

# 提取进程内存
vol -f memory.raw windows.memmap --pid 1234 --dump
```

**进程分析自动化脚本：**

```python
import subprocess
import json
import re

class ProcessAnalyzer:
    def __init__(self, memory_image):
        self.image = memory_image
        self.suspicious_processes = []
        self.known_good_names = {
            'System', 'smss.exe', 'csrss.exe', 'wininit.exe',
            'services.exe', 'lsass.exe', 'svchost.exe', 'explorer.exe',
            'winlogon.exe', 'fontdrvhost.exe', 'dwm.exe', 'taskhostw.exe'
        }
        self.suspicious_paths = [
            'C:\\Temp\\', 'C:\\Users\\Public\\',
            'C:\\ProgramData\\', '\\AppData\\Local\\Temp\\'
        ]

    def get_processes(self):
        """获取进程列表"""
        result = subprocess.run(
            ['vol', '-f', self.image, 'windows.pslist'],
            capture_output=True, text=True
        )
        return result.stdout

    def analyze_processes(self):
        """分析进程异常"""
        processes = self.get_processes()

        # 解析进程列表
        for line in processes.split('\n'):
            # 检查可疑路径
            for pattern in self.suspicious_paths:
                if pattern.lower() in line.lower():
                    self.suspicious_processes.append(
                        f"Suspicious path: {line.strip()}"
                    )

            # 检查可疑名称
            parts = line.split()
            if len(parts) > 2:
                name = parts[1]
                if name not in self.known_good_names:
                    if not name.endswith('.exe') and \
                       not name.startswith('System'):
                        self.suspicious_processes.append(
                            f"Non-standard name: {name}"
                        )

            # 检查svchost.exe的异常父进程
            if 'svchost.exe' in line:
                if 'services.exe' not in line and \
                   'svchost.exe' not in line.split()[-1:]:
                    self.suspicious_processes.append(
                        f"svchost.exe with wrong parent: {line.strip()}"
                    )

        return self.suspicious_processes

    def check_hidden_processes(self):
        """检测隐藏进程"""
        # 获取pslist结果
        pslist = subprocess.run(
            ['vol', '-f', self.image, 'windows.pslist'],
            capture_output=True, text=True
        ).stdout

        # 获取psscan结果
        psscan = subprocess.run(
            ['vol', '-f', self.image, 'windows.psscan'],
            capture_output=True, text=True
        ).stdout

        # 提取PID
        pids_pslist = set()
        pids_psscan = set()

        for line in pslist.split('\n'):
            match = re.search(r'\b(\d{1,6})\b', line)
            if match:
                pids_pslist.add(match.group(1))

        for line in psscan.split('\n'):
            match = re.search(r'\b(\d{1,6})\b', line)
            if match:
                pids_psscan.add(match.group(1))

        # 在psscan中但不在pslist中的进程
        hidden = pids_psscan - pids_pslist
        if hidden:
            print(f"[!] Hidden processes detected: {hidden}")
        else:
            print("[+] No hidden processes found")

        return hidden

if __name__ == "__main__":
    analyzer = ProcessAnalyzer("memory.raw")
    suspicious = analyzer.analyze_processes()
    for item in suspicious:
        print(f"[!] {item}")
    analyzer.check_hidden_processes()
```

### 4.2 网络连接

```bash
# 网络连接分析
vol -f memory.raw windows.netscan

# 输出示例：
# Offset     Proto  LocalAddr      LocalPort  ForeignAddr     ForeignPort  State    PID     Owner
# 0x...      TCPv4  0.0.0.0:135    135       0.0.0.0         0            LISTEN   668    svchost.exe
# 0x...      TCPv4  192.168.1.100  49152    10.0.0.5         443          ESTAB    1234   explorer.exe
# 0x...      TCPv4  0.0.0.0:4444   4444      0.0.0.0          0            LISTEN    5678   malware.exe

# 可疑网络连接特征：
# 1. 非标准端口的监听
# 2. 连接到已知恶意IP
# 3. 异常进程发起的网络连接
# 4. 数据外传的大流量连接

# 结合进程信息分析
vol -f memory.raw windows.netscan --pid 1234
```

**网络连接分析脚本：**

```python
import subprocess
import re
from collections import defaultdict

class NetworkAnalyzer:
    # 已知恶意C2 IP（示例）
    KNOWN_BAD_IPS = {
        '185.220.101.1', '45.133.1.1', '194.165.22.1'
    }

    # 可疑端口
    SUSPICIOUS_PORTS = {4444, 4445, 31337, 1234, 5555, 9999, 8888}

    def __init__(self, memory_image):
        self.image = memory_image

    def analyze_network(self):
        """分析网络连接"""
        result = subprocess.run(
            ['vol', '-f', self.image, 'windows.netscan'],
            capture_output=True, text=True
        )

        connections = []
        alerts = []

        for line in result.stdout.split('\n'):
            # 解析网络连接
            parts = line.split()
            if len(parts) < 8:
                continue

            proto = parts[1]
            local = parts[2]
            foreign = parts[4]
            state = parts[6]
            pid = parts[7]
            owner = parts[8] if len(parts) > 8 else "unknown"

            conn = {
                'proto': proto,
                'local': local,
                'foreign': foreign,
                'state': state,
                'pid': pid,
                'owner': owner
            }
            connections.append(conn)

            # 检查已知恶意IP
            for ip in self.KNOWN_BAD_IPS:
                if ip in foreign:
                    alerts.append(
                        f"ALERT: Connection to known bad IP {ip} by {owner} (PID {pid})"
                    )

            # 检查可疑端口
            port = foreign.split(':')[-1] if ':' in foreign else ''
            if port.isdigit() and int(port) in self.SUSPICIOUS_PORTS:
                alerts.append(
                    f"ALERT: Suspicious port {port} used by {owner} (PID {pid})"
                )

            # 检查异常监听
            if state == 'LISTEN' and owner not in [
                'svchost.exe', 'System', 'lsass.exe',
                'services.exe', 'spoolsv.exe'
            ]:
                alerts.append(
                    f"NOTICE: Non-standard process {owner} (PID {pid}) listening on {local}"
                )

        # 统计
        print(f"\n[*] Total connections: {len(connections)}")
        print(f"[*] Alerts: {len(alerts)}")
        for alert in alerts:
            print(f"  {alert}")

        return connections, alerts

if __name__ == "__main__":
    analyzer = NetworkAnalyzer("memory.raw")
    analyzer.analyze_network()
```

### 4.3 注册表分析

```bash
# 列出注册表hive
vol -f memory.raw windows.registry.hivelist

# 输出示例：
# Offset       Name                       Valid  Virtual
# 0xfffff8a0... \SystemRoot\System32\Config\SAM    True  ...
# 0xfffff8a0... \SystemRoot\System32\Config\SECURITY True ...
# 0xfffff8a0... \SystemRoot\System32\Config\SYSTEM  True ...
# 0xfffff8a0... \SystemRoot\System32\Config\SOFTWARE True ...
# 0xfffff8a0... \??\C:\Users\Admin\NTUSER.DAT      True ...

# 读取注册表键
vol -f memory.raw windows.registry.printkey \
  --key "SOFTWARE\Microsoft\Windows\CurrentVersion\Run"

# 查看自启动项
vol -f memory.raw windows.registry.printkey \
  --key "SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"

# UserAssist（程序执行记录）
vol -f memory.raw windows.registry.userassist

# 查看服务
vol -f memory.raw windows.svcscan

# 查看Shimcache（AppCompatCache）
vol -f memory.raw windows.registry.printkey \
  --key "SYSTEM\ControlSet001\Services\AppCompatCache"
```

### 4.4 凭证提取

```bash
# 提取NTLM哈希
vol -f memory.raw windows.hashes

# 输出示例：
# Administrator:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73e59aa7fc88687:::
# Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73e59aa7fc88687:::
# user1:1001:aad3b435b51404eeaad3b435b51404ee:8846f7eaee8fb117ad06bdd830b7586c:::

# 提取LSA Secrets
vol -f memory.raw windows.lsadump

# 提取缓存的域凭据
vol -f memory.raw windows.cachedump

# 使用mimikatz配合分析（需要提取lsass进程内存）
vol -f memory.raw windows.pslist --pid 692  # lsass PID
vol -f memory.raw windows.memmap --pid 692 --dump
# 然后使用mimikatz分析
# mimikatz.exe "sekurlsa::minidump lsass.dmp" "sekurlsa::logonpasswords" exit
```

**凭证提取自动化脚本：**

```python
import subprocess
import re
import json

class CredentialExtractor:
    def __init__(self, memory_image):
        self.image = memory_image

    def extract_ntlm_hashes(self):
        """提取NTLM哈希"""
        result = subprocess.run(
            ['vol', '-f', self.image, 'windows.hashes'],
            capture_output=True, text=True
        )

        hashes = []
        for line in result.stdout.split('\n'):
            # 格式: username:rid:lmhash:nthash:::
            match = re.match(
                r'^(\S+):(\d+):([0-9a-fA-F]{32}):([0-9a-fA-F]{32}):::',
                line.strip()
            )
            if match:
                hashes.append({
                    'username': match.group(1),
                    'rid': match.group(2),
                    'lmhash': match.group(3),
                    'nthash': match.group(4)
                })

        return hashes

    def extract_lsa_secrets(self):
        """提取LSA Secrets"""
        result = subprocess.run(
            ['vol', '-f', self.image, 'windows.lsadump'],
            capture_output=True, text=True
        )
        return result.stdout

    def extract_cached_credentials(self):
        """提取缓存的域凭据"""
        result = subprocess.run(
            ['vol', '-f', self.image, 'windows.cachedump'],
            capture_output=True, text=True
        )
        return result.stdout

    def extract_all(self):
        """提取所有凭证"""
        print("=" * 60)
        print("Credential Extraction Report")
        print("=" * 60)

        # NTLM哈希
        hashes = self.extract_ntlm_hashes()
        print(f"\n[*] NTLM Hashes: {len(hashes)} found")
        for h in hashes:
            print(f"  {h['username']} (RID {h['rid']})")
            print(f"    NT: {h['nthash']}")
            # 检查空密码哈希
            if h['nthash'] == '31d6cfe0d16ae931b73e59aa7fc88687':
                print(f"    [!] Empty password")
            # 检查默认管理员哈希
            if h['username'] == 'Administrator' and \
               h['nthash'] == '31d6cfe0d16ae931b73e59aa7fc88687':
                print(f"    [!] Administrator with empty password!")

        # LSA Secrets
        lsa = self.extract_lsa_secrets()
        print(f"\n[*] LSA Secrets extracted")
        print(lsa[:500] + "..." if len(lsa) > 500 else lsa)

        # 缓存凭据
        cached = self.extract_cached_credentials()
        print(f"\n[*] Cached domain credentials:")
        print(cached[:500] + "..." if len(cached) > 500 else cached)

        return {
            'ntlm_hashes': hashes,
            'lsa_secrets': lsa,
            'cached_creds': cached
        }

if __name__ == "__main__":
    extractor = CredentialExtractor("memory.raw")
    extractor.extract_all()
```

---

---

