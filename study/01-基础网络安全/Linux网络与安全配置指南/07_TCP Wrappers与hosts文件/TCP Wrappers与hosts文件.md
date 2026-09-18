# TCP Wrappers与hosts文件

```bash
# /etc/hosts.allow - 允许规则
# 格式: 服务: 客户端 [: 命令]

# 允许SSH特定IP
sshd: 192.168.1.0/24 192.168.2.100
sshd: .example.com

# 允许所有服务给localhost
ALL: 127.0.0.1 [::1]

# 允许特定服务
vsftpd: 192.168.1.0/24
nginx: ALL

# 带动作的规则
sshd: 192.168.1.100: spawn echo "%h attempted access" >> /var/log/sshd_access.log

# /etc/hosts.deny - 拒绝规则
# 拒绝所有（默认拒绝策略）
ALL: ALL

# 拒绝特定IP
ALL: 10.0.0.0/8
sshd: ALL EXCEPT 192.168.1.0/24

# 带日志的拒绝
ALL: ALL: spawn echo "%h connect to %d" >> /var/log/tcpd.log

# 注意：hosts.allow优先于hosts.deny
# 检查tcpd是否编译到服务中
ldd /usr/sbin/sshd | grep wrap
```

---

---

## 📋 内容审核与补充建议

> 针对「TCP Wrappers与hosts文件」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

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
