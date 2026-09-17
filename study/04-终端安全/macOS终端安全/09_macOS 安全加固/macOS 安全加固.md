# macOS 安全加固

### 9.1 安全配置基线（CIS Benchmark for macOS）

CIS（Center for Internet Security）Benchmark 为 macOS 提供了详细的安全配置基线。

**关键 CIS 控制项**

| 控制编号 | 控制项 | 配置方法 |
|----------|--------|----------|
| 1.1 | 确保 FileVault 已启用 | `sudo fdesetup enable` |
| 2.1 | 确保 Gatekeeper 已启用 | `sudo spctl --master-enable` |
| 2.3 | 确保 SIP 已启用 | 恢复模式 `csrutil enable` |
| 3.1 | 确保防火墙已启用 | `socketfilterfw --setglobalstate on` |
| 3.4 | 启用隐身模式 | `socketfilterfw --setstealthmode on` |
| 4.1 | 禁用远程登录（SSH） | `sudo systemsetup -setremotelogin off` |
| 4.5 | 禁用自动登录 | `sudo defaults write /Library/Preferences/com.apple.loginwindow autoLoginUser -int 0` |
| 5.1 | 设置屏幕锁定延迟 | `defaults write com.apple.screensaver idle -int 300` |
| 5.3 | 禁用自动打开安全文件 | Safari 偏好设置中关闭 |
| 6.1 | 确保 sudo 超时设置 | `/etc/sudoers` 添加 `Defaults timestamp_timeout=5` |
| 6.2 | 确保密码策略 | 配置密码最小长度和复杂度 |
| 6.5 | 确保账户锁定 | 配置失败登录锁定 |
| 7.1 | 限制 AFP/SMB 共享 | 关闭不必要的文件共享服务 |
| 8.1 | 禁用蓝牙（未使用时） | `sudo defaults write /Library/Preferences/com.apple.Bluetooth ControllerPowerState -int 0` |

**自动化基线检查脚本**

```bash
#!/bin/bash
# macOS CIS 基线快速检查脚本

echo "=== macOS Security Baseline Check ==="
echo ""

echo "[1] FileVault Status:"
fdesetup status

echo "[2] Gatekeeper Status:"
spctl --status

echo "[3] SIP Status:"
csrutil status

echo "[4] Firewall Status:"
/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
/usr/libexec/ApplicationFirewall/socketfilterfw --getstealthmode

echo "[5] SSH Status:"
sudo systemsetup -getremotelogin

echo "[6] Auto-login Status:"
defaults read /Library/Preferences/com.apple.loginwindow autoLoginUser 2>/dev/null \
  && echo "WARNING: Auto-login ENABLED" || echo "Auto-login DISABLED"

echo "[7] Screen Lock Idle Time:"
defaults read com.apple.screensaver idle 2>/dev/null || echo "Not set"

echo "[8] Sudo Timeout:"
grep timestamp_timeout /etc/sudoers 2>/dev/null || echo "Default (15min)"

echo "[9] Bluetooth Status:"
defaults read /Library/Preferences/com.apple.Bluetooth ControllerPowerState 2>/dev/null

echo "[10] Guest Account:"
sudo defaults read /Library/Preferences/com.apple.loginwindow GuestEnabled 2>/dev/null
```

### 9.2 企业级安全策略（MDM/Profile Manager/JAMF）

**MDM（Mobile Device Management）核心功能**

```
┌─────────────────────────────────────────────┐
│  MDM 服务器（JAMF Pro / Profile Manager）   │
├─────────────────────────────────────────────┤
│  ├─ 设备注册与策略分发                       │
│  ├─ 配置 Profile（Configuration Profiles）  │
│  ├─ 应用分发与更新                           │
│  ├─ 合规性监控                               │
│  ├─ 远程锁定/擦除                            │
│  └─ 安全报告                                 │
├─────────────────────────────────────────────┤
│  Configuration Profile 类型                  │
│  ├─ com.apple.security.FDE（FileVault）      │
│  ├─ com.apple.security.firewall              │
│  ├─ com.apple.security.GKApproval            │
│  ├─ com.apple.TCC.configuration-profile-policy │
│  ├─ com.apple.systempolicy.kernel-extension-policy │
│  ├─ com.apple.MCX（托管偏好）               │
│  ├─ com.apple.apsl（APN 推送）               │
│  ├─ com.apple.vpn.managed                    │
│  ├─ com.apple.passwordpolicy                 │
│  ├─ com.apple.security.smartcard             │
│  └─ com.apple.security.certificate...       │
└─────────────────────────────────────────────┘
```

**JAMF Pro 关键配置**

```bash
# JAMF Pro 策略示例（通过 API 或 GUI）

# 1. 强制 FileVault 加密
# Configuration Profile: com.apple.security.FDE
# - ShowRecoveryKey: true
# - RecoveryKeyEscrow: <MDM URL>
# - DestroyFVKeyOnStandby: true

# 2. 强制 Gatekeeper
# Configuration Profile: com.apple.security.GKApproval
# - GKApproval: 2 (App Store + Developer ID)

# 3. 限制系统偏好设置面板
# Configuration Profile: com.apple.systempreferences
# - DisabledPreferencePanes: [com.apple.preferences.sharing, ...]

# 4. 强制密码策略
# Configuration Profile: com.apple.passwordpolicy
# - minLength: 12
# - minComplexChars: 4
# - requireAlphanumeric: true
# - maxGracePeriod: 0
# - maxFailedAttempts: 5

# 检查 MDM 注册状态
sudo profiles status -type enrollment
sudo profiles list
sudo profiles show -type configuration
```

### 9.3 补丁管理与自动更新

```bash
# 查看系统版本
sw_vers
# 输出：
# ProductName:    macOS
# ProductVersion: 15.0
# BuildVersion:   24A335

# 检查可用更新
softwareupdate --list

# 安装所有更新
sudo softwareupdate --install --all

# 安装特定更新
sudo softwareupdate --install "macOS Sequoia 15.0.1-XXXXX"

# 仅安装推荐更新
sudo softwareupdate --install --recommended

# 配置自动检查更新
sudo defaults write /Library/Preferences/com.apple.SoftwareUpdate \
  AutomaticCheckEnabled -bool true

# 配置自动下载更新
sudo defaults write /Library/Preferences/com.apple.SoftwareUpdate \
  AutomaticDownload -int 1

# 配置自动安装系统数据更新
sudo defaults write /Library/Preferences/com.apple.SoftwareUpdate \
  ConfigDataInstall -int 1

# 配置自动安装安全更新
sudo defaults write /Library/Preferences/com.apple.SoftwareUpdate \
  CriticalUpdateInstall -int 1

# 快速安全响应更新（macOS 13+ 的快速补丁）
# RSR (Rapid Security Response) 更新独立于主版本
softwareupdate --list-full-installers  # 列出完整安装器版本
```

### 9.4 审计日志与监控

macOS 10.12+ 使用统一日志系统（Unified Logging System, ULS），通过 `log` 命令访问。

```bash
# 查看实时日志流
sudo log stream --level info

# 按谓词过滤日志
sudo log stream --predicate 'process == "sudo"' --info

# 查看最近 1 小时认证日志
sudo log show --last 1h --predicate \
  'subsystem == "com.apple.Authorization"' --info

# 查看最近 24 小时安全相关日志
sudo log show --last 24h --predicate \
  'category == "security" OR processImagePath CONTAINS "securityd"' \
  --style compact

# 导出日志供分析
sudo log collect --output /tmp/system_logs.logarchive --last 24h

# 搜索特定关键字
sudo log show --last 7d --predicate \
  'eventMessage CONTAINS "failed authentication"' --info

# 查看登录历史
last | head -20

# 查看当前登录用户
w

# 审计进程启动记录
sudo log show --last 1h --predicate \
  'eventMessage CONTAINS "exec"' --info | grep -i "process"

# 关键安全监控谓词
# 1. 监控 sudo 使用
sudo log stream --predicate 'process == "sudo"'
# 2. 监控 SSH 连接
sudo log stream --predicate 'process == "sshd"'
# 3. 监控 TCC 变更
sudo log stream --predicate 'subsystem == "com.apple.TCC"'
# 4. 监控 LaunchAgent/Daemon 加载
sudo log stream --predicate 'process == "launchd"'
# 5. 监控网络连接
sudo log stream --predicate 'subsystem == "com.apple.network"'

# 配置日志持久化（默认是循环缓冲）
# /etc/asl/ 目录下配置持久化规则
# /Library/Logs/ 目录存放应用日志
```

---

---

## 📋 内容审核与补充建议

> 针对「macOS 安全加固」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

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
