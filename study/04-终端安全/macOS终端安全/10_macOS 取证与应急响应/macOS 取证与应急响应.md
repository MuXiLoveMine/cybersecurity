# macOS 取证与应急响应

### 10.1 统一日志系统（OSLog）使用

```bash
# 系统日志架构
# /var/log/         — 传统日志目录（部分旧系统）
# /var/db/diagnostics/ — 统一日志数据库（OSLog）
# log 命令通过 os_log API 访问

# 收集完整系统日志
sudo log collect --last 7d --output /tmp/forensic_logs.logarchive

# 分析日志存档
log show /tmp/forensic_logs.logarchive --predicate \
  'process == "screensharingd" OR process == "sshd"' --info

# 查看进程活动时间线
log show --last 24h --predicate \
  'eventMessage CONTAINS "launch"' --style compact | \
  awk '{print $0}' | sort

# 提取用户登录登出事件
log show --last 7d --predicate \
  'subsystem == "com.apple.Authorization" OR \
   subsystem == "com.apple.securityd" OR \
   process == "loginwindow"' --info

# 提取 USB 设备连接事件
log show --last 7d --predicate \
  'subsystem == "com.apple.usb"' --info
```

### 10.2 内存取证

```bash
# macOS 内存取证工具

# 1. recon-pcap — Apple 官方内存分析工具（需要开发者账户）
# 2. Volatility 3 — 开源内存取证框架（macOS 支持）

# 获取内存镜像（需要 SIP 禁用 + 特定驱动）
# Intel Mac 使用 /dev/mem（SIP 禁用后）
sudo dd if=/dev/mem of=/tmp/memory.dump bs=1m

# Apple Silicon Mac 使用 mac-memory 解决方案
# 需要通过 Apple Silicon 特定的内存获取工具

# Volatility 3 分析 macOS 内存
# 需要对应的 symbol tables
python3 vol.py -f memory.dump banners.Banners
python3 vol.py -f memory.dump pslist.PsList
python3 vol.py -f memory.dump netscan.NetScan
python3 vol.py -f memory.dump malfind.Malfind

# 关键取证内存对象
# - 进程列表（含隐藏进程）
# - 网络连接（含已断开的）
# - 加载的内核模块/KEXT
# - Mach 端口
# - 内存中的恶意代码
```

### 10.3 磁盘取证与分析

```bash
# 创建磁盘镜像（只读挂载）
sudo dd if=/dev/disk0 of=/tmp/disk_image.dd bs=1m conv=noerror,sync
sudo dd if=/dev/disk0 of=/tmp/disk_image.img bs=4m conv=sync,noerror status=progress

# 或使用 dd_rescue（更好的错误处理）
# 使用 hdiutil 创建 DMG 镜像
sudo hdiutil create -srcdevice /dev/disk0 /tmp/disk_image.dmg

# 挂载镜像（只读模式）
sudo hdiutil attach -readonly /tmp/disk_image.dmg

# 文件系统取证

# 1. 时间线分析
# 提取文件时间戳（MACB times: Modified, Accessed, Changed, Born）
find /Volumes/disk_image -type f -exec stat -f "%m %N" {} \; | sort -n > timeline.txt

# 2. 查找最近修改的文件
find / -type f -mtime -1 -ls 2>/dev/null | head -50

# 3. 查找可疑文件权限
find / -perm -4000 -type f 2>/dev/null    # SUID 文件
find / -perm -2000 -type f 2>/dev/null    # SGID 文件
find / -perm -o+w -type f 2>/dev/null     # 全局可写文件

# 4. 查找隐藏文件
find / -name ".*" -type f 2>/dev/null | grep -v "^\./\..*$"

# 5. 分析 LaunchAgents/Daemons（持久化）
ls -la ~/Library/LaunchAgents/
ls -la /Library/LaunchAgents/
ls -la /Library/LaunchDaemons/
ls -la /System/Library/LaunchAgents/
ls -la /System/Library/LaunchDaemons/

# 检查所有 LaunchAgent plist
for f in ~/Library/LaunchAgents/*.plist \
         /Library/LaunchAgents/*.plist \
         /Library/LaunchDaemons/*.plist; do
    echo "=== $f ==="
    defaults read "$f" 2>/dev/null
done

# 6. 检查登录项
osascript -e 'tell application "System Events" to get the name of every login item'

# 7. 检查 cron 任务
crontab -l
sudo crontab -l
ls -la /etc/cron.* 2>/dev/null
```

### 10.4 常见 macOS 恶意软件分析案例

| 恶意软件名称 | 首次出现 | 行为特征 | 持久化方式 |
|-------------|----------|----------|------------|
| Flashback | 2012 | 通过 Java 漏洞感染，劫持 DNS | LaunchAgent + Safari 注入 |
| Genieo/Pirrit | 2014 | 广告软件，修改浏览器主页和搜索 | LaunchAgent + Safari 扩展 |
| KeRanger | 2016 | 首个 macOS 勒索软件，加密用户文件 | Transmission BT 客户端感染 |
| Fruitfly | 2017 | 间谍软件，远程控制摄像头和键盘 | LaunchAgent + 启动项 |
| Shlayer | 2018 | 通过伪造 Adobe Flash 更新传播 | LaunchAgent + 浏览器配置文件修改 |
| XCSSET | 2020 | 感染 Xcode 项目，窃取 Safari Cookie | Xcode 项目植入 + LaunchAgent |
| Silver Sparrow | 2021 | M1 芯片原生恶意软件，行为待定 | LaunchAgent（~/.manifest） |
| XLoader | 2021 | 信息窃取，macOS/Windows 跨平台 | 伪装合法应用 + LaunchAgent |
| CloudMensis | 2022 | 后门，通过 Cloud 存储中转 C2 | LaunchAgent |
| Realst | 2023 | 通过伪造会议软件窃取密码和加密钱包 | 伪装 Zoom/Teams 安装包 |
| Banshee Stealer | 2024 | 信息窃取，可绕过沙箱和 TCC 部分保护 | 伪装合法应用 |

**恶意软件分析流程**

```bash
# 1. 初始静态分析
# 查看文件类型
file /path/to/suspicious_binary

# 查看代码签名
codesign -dv --verbose=4 /path/to/suspicious_binary

# 查看 entitlements
codesign -d --entitlements - /path/to/suspicious_binary

# 查看 quarantine 属性
xattr -l /path/to/suspicious_binary

# 提取字符串
strings /path/to/suspicious_binary | grep -i "http\|url\|password\|key\|curl\|base64"

# 查看 Mach-O 头部
otool -hv /path/to/suspicious_binary
otool -L /path/to/suspicious_binary   # 动态库依赖

# 2. 行为分析（沙箱环境）
# 监控文件系统操作
sudo fs_usage -f filesys /path/to/suspicious_binary

# 监控网络连接
sudo lsof -i -r 1 | grep suspicious_binary

# 监控进程操作
sudo log stream --predicate \
  'processImagePath CONTAINS "suspicious_binary"' --info --debug

# 3. 动态分析（调试器）
# 使用 lldb 附加
lldb /path/to/suspicious_binary
(lldb) breakpoint set --name main
(lldb) run
(lldb) image list   # 加载的库
(lldb) register read
```

### 10.5 应急响应工具清单

| 工具 | 用途 | 安装方式 |
|------|------|----------|
| log | 统一日志查询 | 系统内置 |
| fs_usage | 文件系统活动监控 | 系统内置（需 root） |
| lsof | 打开文件/网络连接查看 | 系统内置 |
| netstat/nettop | 网络连接监控 | 系统内置 |
| ps/pstree | 进程树查看 | 系统内置 |
| launchctl | LaunchAgent/Daemon 管理 | 系统内置 |
| codesign | 代码签名验证 | 系统内置 |
| spctl | Gatekeeper 状态 | 系统内置 |
| csrutil | SIP 状态 | 系统内置 |
| fdesetup | FileVault 管理 | 系统内置 |
| tccutil | TCC 权限管理 | 系统内置 |
| profiles | MDM Profile 管理 | 系统内置 |
| sqlite3 | TCC.db 查询 | 系统内置 |
| KnockKnock | 持久化项扫描 | `brew install knockknock` |
| TaskExplorer | 进程管理（SleuthKit） | 官方下载 |
| LuLu | 开源 macOS 防火墙 | `brew install --cask lulu` |
| Suspicious Package | PKG 安装包分析 | 官方下载 |
| ImHex | 十六进制分析 | `brew install --cask imhex` |
| Volatility 3 | 内存取证 | Python pip |
| Autopsy | 磁盘取证 | 官方下载 |

**应急响应快速脚本**

```bash
#!/bin/bash
# macOS IR 快速信息收集脚本

IR_DIR="/tmp/ir_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$IR_DIR"

echo "=== System Info ==="
sw_vers > "$IR_DIR/system_info.txt"
system_profiler SPHardwareDataType >> "$IR_DIR/system_info.txt"

echo "=== Running Processes ==="
ps aux > "$IR_DIR/processes.txt"

echo "=== Network Connections ==="
sudo lsof -i -P -n > "$IR_DIR/network_connections.txt"
netstat -an >> "$IR_DIR/network_connections.txt"

echo "=== LaunchAgents/Daemons ==="
ls -la ~/Library/LaunchAgents/ > "$IR_DIR/launchagents.txt" 2>&1
ls -la /Library/LaunchAgents/ >> "$IR_DIR/launchagents.txt" 2>&1
ls -la /Library/LaunchDaemons/ >> "$IR_DIR/launchagents.txt" 2>&1

echo "=== Login Items ==="
osascript -e 'tell application "System Events" to get the name of every login item' \
  > "$IR_DIR/login_items.txt" 2>&1

echo "=== TCC Database ==="
sqlite3 ~/Library/Application\ Support/com.apple.TCC/TCC.db \
  "SELECT client, service, auth_value FROM access;" \
  > "$IR_DIR/tcc_database.txt" 2>&1

echo "=== Crontab ==="
crontab -l > "$IR_DIR/crontab.txt" 2>&1
sudo crontab -l >> "$IR_DIR/crontab.txt" 2>&1

echo "=== Code Signatures ==="
for app in /Applications/*.app; do
    codesign -dv --verbose=2 "$app" >> "$IR_DIR/code_signatures.txt" 2>&1
done

echo "=== FileVault Status ==="
fdesetup status > "$IR_DIR/filevault.txt" 2>&1

echo "=== Security Settings ==="
spctl --status > "$IR_DIR/security_settings.txt" 2>&1
csrutil status >> "$IR_DIR/security_settings.txt" 2>&1
fdesetup status >> "$IR_DIR/security_settings.txt" 2>&1

echo "=== Recent Logs ==="
sudo log show --last 1h --predicate \
  'process == "sudo" OR process == "sshd" OR process == "screensharingd"' \
  --info > "$IR_DIR/recent_logs.txt" 2>&1

echo "=== Last Logins ==="
last > "$IR_DIR/login_history.txt" 2>&1

echo "IR data collected at: $IR_DIR"
```

---

---

