# Forensics取证

### 9.1 磁盘取证

```python
# 使用Autopsy进行磁盘取证分析
# Autopsy是基于The Sleuth Kit的图形化取证工具

# 常见磁盘取证分析:
disk_forensics = {
    "文件恢复": "使用foremost/photorec恢复已删除文件",
    "时间线分析": "分析文件的MAC时间（Modified/Accessed/Created）",
    "隐藏分区": "检查分区表中的隐藏分区",
    " slack空间": "检查文件slack空间中的隐藏数据",
    "交换分区": "分析swap分区中的数据",
    "磁盘镜像": "使用dd制作磁盘镜像",
}

# 使用foremost恢复文件
# foremost -i image.dd -o output/
# foremost -t jpeg,png -i image.dd  # 指定恢复类型

# 使用tshark分析网络取证
# tshark -r evidence.pcap -Y "http" -T fields -e http.request.uri

# 分析NTFS Alternate Data Stream (ADS)
# dir /r  # Windows查看ADS
```

### 9.2 内存取证

```python
# 使用Volatility进行内存分析
# Volatility是内存取证的标准工具

volatility_commands = {
    # 基本信息识别
    "imageinfo": "volatility -f mem.dmp imageinfo",
    
    # 进程分析
    "pslist": "volatility -f mem.dmp --profile=Win7SP1x64 pslist",
    "pstree": "volatility -f mem.dmp --profile=Win7SP1x64 pstree",
    "psscan": "volatility -f mem.dmp --profile=Win7SP1x64 psscan",  # 发现已隐藏进程
    
    # 网络连接
    "netscan": "volatility -f mem.dmp --profile=Win7SP1x64 netscan",
    "connections": "volatility -f mem.dmp --profile=Win7SP1x64 connections",
    
    # 注册表
    "hivelist": "volatility -f mem.dmp --profile=Win7SP1x64 hivelist",
    "hashdump": "volatility -f mem.dmp --profile=Win7SP1x64 hashdump",  # 提取密码哈希
    
    # 文件提取
    "filescan": "volatility -f mem.dmp --profile=Win7SP1x64 filescan",
    "dump-files": "volatility -f mem.dmp --profile=Win7SP1x64 dump-files -D output/",
    
    # 命令行历史
    "cmdline": "volatility -f mem.dmp --profile=Win7SP1x64 cmdline",
    "consoles": "volatility -f mem.dmp --profile=Win7SP1x64 consoles",
    
    # 恶意代码检测
    "malfind": "volatility -f mem.dmp --profile=Win7SP1x64 malfind",
    "yarascan": "volatility -f mem.dmp --profile=Win7SP1x64 yarascan",
    
    # 进程内存dump
    "memdump": "volatility -f mem.dmp --profile=Win7SP1x64 memdump -p <PID> -D output/",
}

# Python辅助分析
def analyze_memory_dump(dump_path, profile):
    """分析内存dump"""
    import subprocess
    
    # 获取进程列表
    result = subprocess.run(
        ['volatility', '-f', dump_path, '--profile', profile, 'pslist'],
        capture_output=True, text=True
    )
    
    # 解析进程列表
    processes = []
    for line in result.stdout.split('\n')[3:]:  # 跳过表头
        parts = line.split()
        if len(parts) >= 6:
            processes.append({
                'pid': parts[2],
                'ppid': parts[3],
                'name': parts[4] if len(parts) > 4 else 'Unknown',
            })
    
    return processes
```

### 9.3 日志分析

```python
import re
from collections import Counter

def analyze_apache_log(log_path):
    """分析Apache/Nginx访问日志"""
    with open(log_path, 'r') as f:
        lines = f.readlines()
    
    # 统计IP访问频率
    ip_counter = Counter()
    url_counter = Counter()
    status_counter = Counter()
    
    # Apache日志格式示例:
    # 192.168.1.1 - - [10/Oct/2023:13:55:36] "GET /admin HTTP/1.1" 200 1234
    log_pattern = r'(\S+) \S+ \S+ \[([^\]]+)\] "(\S+) (\S+) \S+" (\d+)'
    
    for line in lines:
        match = re.match(log_pattern, line)
        if match:
            ip, time, method, url, status = match.groups()
            ip_counter[ip] += 1
            url_counter[url] += 1
            status_counter[status] += 1
    
    print("=== 访问频率最高的IP ===")
    for ip, count in ip_counter.most_common(10):
        print(f"  {ip}: {count}次")
    
    print("=== 访问频率最高的URL ===")
    for url, count in url_counter.most_common(10):
        print(f"  {url}: {count}次")
    
    print("=== 状态码分布 ===")
    for status, count in status_counter.most_common():
        print(f"  {status}: {count}次")
    
    # 检测攻击行为
    attack_patterns = {
        "SQL注入": r"union|select|'|or 1=1|information_schema",
        "XSS": r"<script|onerror|alert|javascript:",
        "目录遍历": r"\.\./|%2e%2e%2f",
        "命令注入": r";|cat|ls|whoami|id",
        "文件包含": r"php://|file://|data://",
    }
    
    print("=== 可疑请求 ===")
    for line in lines:
        for attack, pattern in attack_patterns.items():
            if re.search(pattern, line, re.IGNORECASE):
                print(f"  [{attack}] {line.strip()[:100]}")
                break
```

---

---

