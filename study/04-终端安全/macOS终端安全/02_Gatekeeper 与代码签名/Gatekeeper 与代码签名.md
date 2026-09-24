# Gatekeeper 与代码签名

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

---

