# App 签名与证书

### 3.1 代码签名机制

iOS 的代码签名机制是安全体系的核心之一，确保所有运行的代码都经过 Apple 或开发者的签名认证。

#### 签名验证流程

```
应用启动
   │
   ▼
AMFI 检查签名 ──→ 签名无效？ ──→ 拒绝运行
   │
   ▼
检查权限（entitlements）──→ 权限与描述文件不匹配？ ──→ 拒绝运行
   │
   ▼
检查沙箱规则
   │
   ▼
应用运行
```

#### 签名的作用

1. **完整性验证**：确保应用未被篡改
2. **身份认证**：确认应用的来源（开发者/企业/App Store）
3. **权限授权**：通过 entitlements 声明应用的特殊权限
4. **防止篡改**：修改应用会导致签名失效，无法运行

### 3.2 证书类型

| 证书类型 | 用途 | 设备限制 |
|----------|------|---------|
| 开发证书 (Development) | 开发调试 | 最多 100 台设备 |
| 发布证书 (Distribution) | App Store 发布 | 无限制（需审核） |
| Ad Hoc 证书 | 内部分发 | 最多 100 台设备 |
| 企业证书 (Enterprise) | 企业内部分发 | 无设备数量限制 |
| 描述文件 (Provisioning Profile) | 关联证书、设备、App ID | - |

### 3.3 签名文件结构

一个签名的 iOS 应用包含以下签名相关文件：

```
MyApp.app/
├── _CodeSignature/
│   └── CodeResources         # 资源文件签名（Code Directory）
├── embedded.mobileprovision   # 描述文件（含证书、设备列表、entitlements）
├── CodeDirectory              # 代码目录（Mach-O 加载命令中）
├── CodeSignature              # 代码签名（Mach-O 加载命令中）
└── Entitlements               # 权限声明（Mach-O 加载命令中）
```

#### Code Directory（代码目录）

代码目录是代码签名的核心，包含：
- 代码各部分的哈希值
- 标识符（Bundle ID）
- 版本号
- 团队 ID
- 运行时硬ening 标志

#### Entitlements（权限声明）

Entitlements 是一个 plist 文件，声明应用需要的特殊权限。

```xml
<!-- 常见 entitlements 示例 -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <!-- 应用标识 -->
    <key>application-identifier</key>
    <string>TEAMID.com.example.myapp</string>
    
    <!-- 团队 ID -->
    <key>com.apple.developer.team-identifier</key>
    <string>TEAMID</string>
    
    <!-- 调试权限（只有开发版有） -->
    <key>get-task-allow</key>
    <true/>
    
    <!-- iCloud 权限 -->
    <key>com.apple.developer.icloud-container-identifiers</key>
    <array>
        <string>iCloud.com.example.myapp</string>
    </array>
    
    <!-- 推送通知 -->
    <key>aps-environment</key>
    <string>production</string>
    
    <!-- Keychain 共享组 -->
    <key>keychain-access-groups</key>
    <array>
        <string>TEAMID.com.example.myapp</string>
    </array>
    
    <!-- 后台模式 -->
    <key>com.apple.developer.background-audio</key>
    <true/>
</dict>
</plist>
```

### 3.4 重签名与篡改检测

#### 重签名流程

```
原始 IPA → 解压 → 移除旧签名 → 修改内容 → 用新证书签名 → 打包 → 新 IPA
```

#### 常用重签名工具
- **iOS App Signer**：图形化重签名工具
- **sigh**（Fastlane 工具）：命令行重签名
- **ideviceinstaller**：命令行安装工具
- **frida-ios-dump**：砸壳后重签名

#### 防重签名措施

**1. 校验签名信息**
```swift
// 检查签名中的 Team ID
func verifySignature() -> Bool {
    guard let info = Bundle.main.infoDictionary else { return false }
    
    // 检查 Bundle ID
    let bundleId = info["CFBundleIdentifier"] as? String
    if bundleId != "com.example.myapp" {
        return false
    }
    
    // 检查代码签名
    if let secCode = SecCodeCopySelf(SecCSFlags(), nil) {
        var codeInfo: CFDictionary?
        SecCodeCopySigningInformation(secCode, SecCSFlags(), &codeInfo)
        if let info = codeInfo as? [String: Any] {
            let teamId = info["teamid"] as? String
            if teamId != "YOUR_TEAM_ID" {
                return false
            }
        }
    }
    
    return true
}
```

**2. 完整性校验**
- 校验关键文件的哈希值
- 校验 Mach-O 文件的签名

**3. 越狱检测**
- 越狱设备更容易进行重签名
- 检测越狱环境并限制功能

---

---

## 📋 内容审核与补充建议

> 针对「App 签名与证书」部分的内容审核结果：

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
