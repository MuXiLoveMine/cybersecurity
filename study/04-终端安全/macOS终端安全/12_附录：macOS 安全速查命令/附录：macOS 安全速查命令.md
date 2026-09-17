# 附录：macOS 安全速查命令

```bash
# === 系统安全状态 ===
csrutil status                                    # SIP 状态
spctl --status                                    # Gatekeeper 状态
fdesetup status                                   # FileVault 状态
/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate  # 防火墙状态
sw_vers                                           # 系统版本
softwareupdate --list                             # 可用更新

# === 权限与访问控制 ===
id                                                # 当前用户信息
sudo -l                                           # sudo 权限
sqlite3 ~/Library/Application\ Support/com.apple.TCC/TCC.db \
  "SELECT client, service, auth_value FROM access;"  # TCC 权限

# === 持久化检查 ===
ls ~/Library/LaunchAgents/                        # 用户级 LaunchAgent
ls /Library/LaunchAgents/                         # 系统级 LaunchAgent
ls /Library/LaunchDaemons/                        # 系统级 LaunchDaemon
crontab -l                                        # 用户 cron
sudo crontab -l                                   # root cron

# === 网络安全 ===
sudo lsof -i -P -n | grep LISTEN                  # 监听端口
sudo lsof -i -P -n | grep ESTABLISHED             # 活动连接
sudo pfctl -s rules                               # pf 规则
netstat -an                                       # 网络连接

# === 代码签名 ===
codesign -dv --verbose=4 /Applications/App.app     # 签名信息
spctl --assess --verbose /Applications/App.app    # Gatekeeper 评估

# === 日志与审计 ===
sudo log show --last 1h --predicate 'process == "sudo"' --info  # sudo 日志
last                                              # 登录历史
sudo log show --last 24h --predicate \
  'subsystem == "com.apple.TCC"' --info          # TCC 变更日志

# === 应急响应 ===
sudo fs_usage -f filesys                          # 文件系统活动
sudo log collect --last 24h --output /tmp/ir.logarchive  # 收集日志
ps aux                                            # 进程列表
```

---

> 本文档持续更新，建议结合实际环境验证命令可用性。macOS 安全机制随版本演进不断变化，请参考 Apple 最新安全文档和 CIS Benchmark 最新版本进行配置。

---

## 📋 内容审核与补充建议

> 针对「附录：macOS 安全速查命令」部分的内容审核结果：

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

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客
