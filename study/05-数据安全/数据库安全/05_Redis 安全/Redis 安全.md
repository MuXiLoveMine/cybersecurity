# Redis 安全

### 5.1 认证配置

```conf
# redis.conf - 设置密码
requirepass YourStrong@Password#2024

# Redis 6+ ACL 系统
# 创建用户并限制权限
user default off
user appuser on >AppPassword123 ~app:* +get +set +del -@all

# 启用 ACL 文件
aclfile /etc/redis/users.acl
```

### 5.2 命令禁用

```conf
# redis.conf - 禁用危险命令
rename-command FLUSHALL ""
rename-command FLUSHDB ""
rename-command CONFIG ""
rename-command KEYS ""
rename-command DEBUG ""
rename-command SHUTDOWN ""
```

### 5.3 网络隔离

```conf
# redis.conf - 绑定内网地址
bind 10.0.0.20 127.0.0.1
protected-mode yes
port 0              # 禁用 TCP，仅用 Unix socket
unixsocket /var/run/redis/redis.sock
```

### 5.4 常见攻击

| 攻击类型 | 原理 | 防护 |
|----------|------|------|
| **未授权访问** | 无密码且暴露公网 | 设置 requirepass + bind 内网 |
| **主从复制 RCE** | 利用 REPLICAOF 加载恶意 .so | 禁用 MODULE/SLAVEOF 命令，最低权限运行 |
| **Lua 沙箱绕过** | 利用 EVAL 执行恶意 Lua 脚本 | 禁用 EVAL，使用 ACL 限制 |
| **SSRF 利用** | Redis 作为 SSRF 跳板攻击内网 | 禁用 SSRF 高危命令，网络隔离 |

---

---

## 📋 内容审核与补充建议

> 针对「Redis 安全」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

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
