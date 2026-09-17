# EDR 响应能力

### 4.1 隔离（Isolation）

EDR 可以在不同层级实施隔离：

| 隔离层级 | 措施 | 影响 |
|----------|------|------|
| 进程隔离 | 终止恶意进程 | 最小影响 |
| 网络隔离 | 阻断出站连接 | 断网但本地可用 |
| 用户隔离 | 注销用户会话 | 中断用户操作 |
| 设备隔离 | 完全隔离终端 | 仅保留 EDR 通信 |

**网络隔离实现**：

```powershell
# EDR 网络隔离逻辑 (PowerShell 伪代码)
# 允许 EDR 通信端口，阻断其余所有网络流量

# 1. 创建隔离防火墙规则
New-NetFirewallRule -Name "EDR_Isolation_BlockAllOutbound" `
    -Direction Outbound -Action Block `
    -Profile Any -Enabled True

# 2. 允许 EDR Agent 通信（放行管理服务器IP）
New-NetFirewallRule -Name "EDR_Allow_MgmtServer" `
    -Direction Outbound -Action Allow `
    -RemoteAddress "10.0.0.100" `
    -RemotePort 443 -Protocol TCP

# 3. 允许 DNS（如需要）
New-NetFirewallRule -Name "EDR_Allow_DNS" `
    -Direction Outbound -Action Allow `
    -RemotePort 53 -Protocol UDP
```

### 4.2 终止与回滚

```
响应动作详解：

1. 终止进程
   - 终止恶意进程及其子进程
   - 清理进程注入的线程
   - 删除持久化项（计划任务/注册表自启/服务）

2. 文件回滚
   - 恢复被修改的文件（从备份/快照）
   - 删除释放的恶意文件
   - 恢复注册表修改

3. 网络连接阻断
   - 阻断 C2 连接
   - DNS 黑名单（恶意域名）
   - IP 封禁（恶意 IP）

4. 账户处理
   - 禁用被攻击者利用的账户
   - 撤销被窃取的凭据
   - 重置受影响用户密码
```

---

---

## 📋 内容审核与补充建议

> 针对「EDR 响应能力」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

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
