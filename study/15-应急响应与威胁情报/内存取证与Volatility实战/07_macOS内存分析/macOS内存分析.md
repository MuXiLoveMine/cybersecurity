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

## 📋 内容审核与补充建议

> 针对「macOS内存分析」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

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
