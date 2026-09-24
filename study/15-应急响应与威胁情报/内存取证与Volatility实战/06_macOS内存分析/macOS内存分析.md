# macOS内存分析

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

---

