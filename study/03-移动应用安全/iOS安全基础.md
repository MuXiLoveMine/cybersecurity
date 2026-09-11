# iOS 安全基础

> 本文档详细介绍 iOS 平台的安全机制、沙箱体系、签名证书、权限管理、越狱与漏洞类型，以及应用安全检测要点。

---

## 一、iOS 系统架构

### 1.1 四层架构详解

iOS 系统架构同样采用分层设计，基于 Darwin 内核，整体分为四层：

```
┌─────────────────────────────────────────┐
│     Cocoa Touch Layer (触摸层)           │  ← UIKit、触摸事件、多任务
├─────────────────────────────────────────┤
│     Media Layer (媒体层)                 │  ← 图形、音频、视频
├─────────────────────────────────────────┤
│   Core Services Layer (核心服务层)       │  ← Foundation、Core Data、网络
├─────────────────────────────────────────┤
│    Core OS Layer (核心 OS 层)            │  ← Darwin 内核、驱动、安全机制
└─────────────────────────────────────────┘
```

#### 第一层：Cocoa Touch Layer（触摸层）

**位置**：最顶层，提供 UI 和交互相关的框架

**核心框架**：
- **UIKit**：界面控件、视图控制器、触摸事件处理
- **SwiftUI**：声明式 UI 框架（iOS 13+）
- **EventKit**：日历事件管理
- **GameKit**：游戏中心
- **MessageUI**：邮件/短信发送界面
- **MapKit**：地图服务
- **AddressBookUI**：联系人选择界面（已废弃）
- **PushKit**：VoIP 推送

**安全要点**：
- UI 层面的注入攻击
- 剪贴板数据泄露
- 屏幕录制与截图防护

#### 第二层：Media Layer（媒体层）

**位置**：提供图形、音频、视频等多媒体功能

**核心框架**：
- **Core Graphics**：2D 图形绘制
- **Core Animation**：动画引擎
- **Core Image**：图像处理
- **Metal**：底层 3D 图形 API
- **OpenGL ES**：跨平台 3D 图形 API
- **AVFoundation**：音视频播放与录制
- **Core Audio**：底层音频处理
- **Media Player**：媒体播放

#### 第三层：Core Services Layer（核心服务层）

**位置**：提供核心系统服务

**核心框架**：
- **Foundation**：基础数据结构、字符串、集合、文件操作等
- **Core Data**：数据持久化框架
- **CFNetwork**：底层网络框架
- **Core Foundation**：C 语言层面的基础库
- **Core Location**：定位服务
- **Core Motion**：运动传感器（加速度计、陀螺仪）
- **Security**：安全框架（加密、钥匙串、证书管理）
- **System Configuration**：系统配置
- **Accounts**：账户管理
- **Social**：社交分享
- **WebKit**：Web 渲染引擎

#### 第四层：Core OS Layer（核心 OS 层）

**位置**：最底层，基于 Darwin 内核

**核心组件**：
- **Darwin 内核**：基于 FreeBSD 的 Mach 微内核 + BSD 层
- **设备驱动**：硬件驱动程序
- **内存管理**：虚拟内存、内存保护
- **文件系统**：APFS（Apple File System）
- **网络协议栈**：TCP/IP 协议栈
- **安全机制**：
  - **Secure Enclave**：安全隔区，存储密钥和生物识别数据
  - **AMFI**（Apple Mobile File Integrity）：Apple 移动文件完整性
  - **Sandbox**：应用沙箱机制
  - **Code Signing**：代码签名
  - **ASLR**：地址空间布局随机化
  - **DEP/NX**：数据执行保护
  - **PAC**（Pointer Authentication Codes）：指针身份验证（A12+）

### 1.2 iOS 安全启动链

iOS 采用严格的安全启动链，确保系统不被篡改：

```
Boot ROM → LLB → iBoot → iOS Kernel → 系统服务 → SpringBoard
   │        │       │        │
   └─ 每一步都验证下一级的签名，确保完整性
```

| 阶段 | 说明 | 安全机制 |
|------|------|---------|
| Boot ROM | 芯片内置的引导代码，不可修改 | 硬件级信任根 |
| LLB (Low-Level Bootloader) | 低级引导加载器 | 被 Boot ROM 验证签名 |
| iBoot | 二级引导加载器，负责加载内核 | 被 LLB 验证签名 |
| iOS Kernel | XNU 内核（Mach + BSD） | 被 iBoot 验证签名 |
| 系统服务 | 启动系统守护进程和服务 | 每个可执行文件都有签名 |
| SpringBoard | 主屏幕应用 | 系统应用，受签名保护 |

### 1.3 XNU 内核

iOS 的内核是 XNU（X is Not Unix），是 macOS 和 iOS 共用的内核。

**组成**：
- **Mach 微内核**：进程管理、内存管理、IPC（消息传递）
- **BSD 层**：POSIX 接口、文件系统、网络协议栈
- **I/O Kit**：设备驱动框架
- **libkern**：内核库（C++）

**安全相关的内核组件**：
- **MACF**（Mandatory Access Control Framework）：强制访问控制框架，沙箱基于此实现
- **AMFI**：Apple 移动文件完整性，强制代码签名
- **Sandbox.kext**：沙箱内核扩展，基于 Seatbelt 沙箱模型
- **KTRR**（Kernel Text Read-Only Region）：内核只读区域保护

---

## 二、iOS 沙箱机制

### 2.1 沙箱概述

iOS 沙箱是一种强制访问控制机制，限制应用的行为范围，确保应用只能访问其被允许的资源。

**核心原则**：
- 每个应用有独立的沙箱目录
- 应用默认只能访问自己沙箱内的文件
- 访问系统资源（相机、通讯录、位置等）需要用户授权
- 应用间不能直接通信，只能通过系统提供的机制
- 所有系统调用都经过沙箱策略检查

### 2.2 应用沙箱目录结构

每个应用安装后会生成一个唯一 GUID 命名的目录，位于 `/var/containers/Bundle/Application/` 和 `/var/mobile/Containers/Data/Application/`。

```
App 安装目录（Bundle 目录，只读）：
/var/containers/Bundle/Application/<GUID>/
├── MyApp.app/
│   ├── MyApp                 # 可执行文件（Mach-O）
│   ├── Info.plist            # 应用配置
│   ├── Assets.car            # 资源包
│   ├── Frameworks/           # 嵌入式动态库
│   ├── PlugIns/              # App Extension
│   ├── _CodeSignature/       # 代码签名
│   ├── embedded.mobileprovision  # 描述文件
│   └── ...

App 数据目录（可读写）：
/var/mobile/Containers/Data/Application/<GUID>/
├── Documents/                # 用户文档，iTunes 会备份
├── Library/
│   ├── Preferences/          # 设置文件（.plist）
│   ├── Caches/               # 缓存文件，系统可能清理
│   ├── Application Support/  # 应用支持文件
│   └── Cookies/              # Cookie 存储
├── tmp/                      # 临时文件，系统可能清理
└── SystemData/               # 系统数据
```

### 2.3 沙箱规则（Seatbelt Profile）

iOS 沙箱基于 Seatbelt（又称 Sandbox.framework）实现，使用 Scheme-like（TinyScheme 方言）的规则语言定义。

#### 沙箱规则示例

```scheme
(version 1)
(deny default)                   ; 默认拒绝所有操作

(allow file-read*                ; 允许读取自己的 Bundle
    (subpath (param "BUNDLE_PATH")))

(allow file-write*               ; 允许写入数据目录
    (subpath (param "DATA_PATH")))

(allow file-read*                ; 允许读取系统库
    (subpath "/System/Library")
    (subpath "/usr/lib"))

(allow network-outbound          ; 允许网络连接
    (literal "*"))

(allow ipc-posix-shm)            ; 允许共享内存通信

(allow mach-lookup                ; 允许查找的 Mach 服务
    (global-name "com.apple.networkd")
    (global-name "com.apple.securityd")
    ...)
```

#### 沙箱规则类型

| 操作类型 | 说明 |
|----------|------|
| file-read* | 文件读取（含元数据） |
| file-write* | 文件写入（创建、修改、删除） |
| file-read-metadata | 文件元数据读取 |
| file-write-metadata | 文件元数据修改 |
| network-outbound | 出站网络连接 |
| network-inbound | 入站网络连接 |
| mach-lookup | Mach 服务查找 |
| mach-register | Mach 服务注册 |
| ipc-posix-shm | POSIX 共享内存 |
| ipc-sysv-sem | System V 信号量 |
| process-fork | 进程 fork |
| process-exec | 进程执行 |
| syscall-unix | Unix 系统调用 |

### 2.4 沙箱绕过

#### 常见沙箱逃逸方法

**1. 利用内核漏洞**
- 内核漏洞可以获取 root 权限，完全绕过沙箱
- 常见攻击面：IOKit 驱动、文件系统、网络协议栈

**2. 利用系统服务漏洞**
- 通过 IPC 与系统服务通信
- 利用系统服务的漏洞提权
- 系统服务通常有更高的权限

**3. WebKit 漏洞 + 沙箱逃逸**
- 先通过 WebKit 漏洞获取代码执行
- 再利用沙箱漏洞逃逸出 WebContent 沙箱
- WebContent 进程沙箱比普通应用更严格

**4. 侧信道攻击**
- 利用侧信道信息推断其他应用的数据
- 例如通过内存压力、功耗等推断键盘输入

#### 著名沙箱逃逸漏洞
- **Pangu 越狱**：利用多个漏洞组合实现沙箱逃逸和内核提权
- **JailbreakMe**：基于 PDF 漏洞的网页越狱
- **checkra1n**：基于 BootROM 漏洞的硬件级越狱（不可修复）
- **Taurine/unc0ver**：利用内核漏洞的越狱工具

---

## 三、App 签名与证书

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

## 四、iOS 权限机制

### 4.1 权限分类

iOS 的权限控制比 Android 更严格，所有需要访问用户隐私或系统功能的操作都需要用户授权。

#### 系统级权限（需用户授权）

| 权限 | 说明 | Info.plist Key |
|------|------|---------------|
| 相机 | 访问摄像头拍照/录像 | NSCameraUsageDescription |
| 照片 | 访问相册 | NSPhotoLibraryUsageDescription |
| 麦克风 | 录音、语音通话 | NSMicrophoneUsageDescription |
| 位置 | 定位服务 | NSLocationWhenInUseUsageDescription / NSLocationAlwaysAndWhenInUseUsageDescription |
| 通讯录 | 访问联系人 | NSContactsUsageDescription |
| 日历 | 访问日历事件 | NSCalendarsUsageDescription |
| 提醒事项 | 访问提醒事项 | NSRemindersUsageDescription |
| 蓝牙 | 蓝牙通信 | NSBluetoothAlwaysUsageDescription |
| 健康数据 | 访问 HealthKit | NSHealthShareUsageDescription / NSHealthUpdateUsageDescription |
| HomeKit | 智能家居控制 | NSHomeKitUsageDescription |
| Face ID / Touch ID | 生物识别 | NSFaceIDUsageDescription |
| 本地网络 | 本地网络扫描 | NSLocalNetworkUsageDescription |
| 追踪 | 跨应用跟踪用户 | AppTrackingTransparency |

#### 特殊权限（需 Apple 审核）

| 权限 | 说明 | 获取方式 |
|------|------|---------|
| VoIP | 后台语音通话 | 申请特殊 entitlement |
| 推送通知 | 远程推送 | 开发者后台配置 |
| 后台定位 | 持续后台定位 | 需说明用途 |
| 后台音频 | 后台播放音乐 | Capability 配置 |
| 后台下载 | 后台下载数据 | Background Modes |
| Network Extension | 网络扩展（VPN、代理等） | 需 Apple 批准 |

### 4.2 权限申请与检测

#### 权限申请流程

```
应用调用 API
   │
   ▼
系统检查权限状态
   ├── 未决定 ──→ 弹出授权对话框 → 用户选择 → 记录结果
   ├── 已授权 ──→ 正常执行
   └── 已拒绝 ──→ 返回错误/空数据
```

#### 代码示例

```swift
import AVFoundation
import Photos
import CoreLocation

// 相机权限检测
func checkCameraPermission() {
    let status = AVCaptureDevice.authorizationStatus(for: .video)
    switch status {
    case .authorized:
        print("已授权")
    case .denied, .restricted:
        print("已拒绝/受限制")
    case .notDetermined:
        // 请求授权
        AVCaptureDevice.requestAccess(for: .video) { granted in
            print("用户\(granted ? "同意" : "拒绝")")
        }
    @unknown default:
        break
    }
}

// 位置权限检测
let locationManager = CLLocationManager()
locationManager.delegate = self
locationManager.requestWhenInUseAuthorization()
```

### 4.3 权限安全问题

#### 常见问题

**1. 权限滥用**
- 申请不必要的权限，过度收集用户数据
- 例如：手电筒 App 请求通讯录权限

**2. 权限绕过**
- 利用系统漏洞绕过权限检查
- 例如：通过剪贴板间接获取数据

**3. 权限提升**
- 从普通应用权限提升到系统权限
- 通常利用系统服务漏洞

**4. 敏感 API 滥用**
- 滥用后台定位、麦克风等权限
- 偷录、偷拍、偷收集位置信息

#### 安全建议

- 只申请必要的权限
- 在需要使用时才请求权限
- 清晰说明权限用途（Usage Description）
- 处理用户拒绝权限的情况
- 定期审计权限使用情况

---

## 五、越狱与非越狱

### 5.1 什么是越狱

越狱（Jailbreak）是指通过利用 iOS 系统漏洞，获取系统最高权限（root），突破 Apple 的安全限制的行为。

#### 越狱能做什么

1. **获取 root 权限**：可以读写系统文件
2. **安装未签名应用**：绕过 App Store 安装任意应用
3. **自定义系统界面**：修改主题、图标、动画等
4. **安装插件**：通过 Cydia/Sileo 安装各种插件
5. **系统级修改**：修改系统行为、解锁功能限制
6. **逆向分析**：调试、Hook 其他应用

#### 越狱的代价

1. **失去保修**：越狱后 Apple 不提供保修
2. **安全风险**：系统安全机制被削弱，更容易被攻击
3. **系统不稳定**：插件可能导致系统崩溃、耗电增加
4. **无法正常升级**：升级系统会丢失越狱
5. **支付安全风险**：银行、支付类应用可能检测越狱并拒绝服务

### 5.2 越狱类型

| 分类方式 | 类型 | 说明 |
|----------|------|------|
| 按完美程度 | 完美越狱 | 重启后越狱状态保留 |
| | 不完美越狱 | 重启后越狱失效，需重新引导 |
| | 半完美越狱 | 重启后部分功能受限 |
| 按利用方式 | 硬件级越狱 | 利用 BootROM/硬件漏洞（不可修复） |
| | 软件级越狱 | 利用系统软件漏洞（可通过更新修复） |
| | 网页越狱 | 通过浏览器漏洞实现越狱 |

#### 著名越狱工具

| 工具 | 支持版本 | 类型 | 说明 |
|------|---------|------|------|
| checkra1n | iOS 12.3 - 14.x | 硬件级 | 基于 checkm8 漏洞，A5-A11 设备 |
| unc0ver | iOS 11 - 14.x | 软件级 | 最流行的越狱工具之一 |
| Taurine | iOS 14 | 软件级 | 基于 libhooker |
| Odyssey | iOS 13 | 软件级 | Chimera 的继任者 |
| palera1n | iOS 15 - 16.x | 硬件级 | 基于 checkm8，A8-A11 |
| Dopamine | iOS 15 - 16.x | 软件级 | A12+ 设备 |

### 5.3 checkm8 漏洞

checkm8 是一个 BootROM 级别的漏洞，由安全研究员 axi0mX 发现，影响 Apple A5 到 A11 芯片的设备。

**特点**：
- **不可修复**：位于 BootROM 中，无法通过软件更新修复
- **硬件级**：漏洞在硬件层面，是永久的
- **影响范围广**：iPhone 4s 到 iPhone 8/X
- **安全研究利器**：是 iOS 安全研究的重要工具

### 5.4 越狱检测与绕过

#### 常见越狱检测方法

**1. 文件检测**
```swift
func isJailbroken() -> Bool {
    // 检查常见的越狱文件是否存在
    let jailbreakFiles = [
        "/Applications/Cydia.app",
        "/Library/MobileSubstrate/MobileSubstrate.dylib",
        "/bin/bash",
        "/usr/sbin/sshd",
        "/etc/apt",
        "/private/var/stash",
        "/private/var/mobile/Library/SBSettings/Themes",
        "/private/var/lib/apt/"
    ]
    
    for path in jailbreakFiles {
        if FileManager.default.fileExists(atPath: path) {
            return true
        }
    }
    
    return false
}
```

**2. 沙箱检测**
```swift
// 尝试访问沙箱外的文件
do {
    try "test".write(toFile: "/private/jailbreak.txt", 
                     atomically: true, encoding: .utf8)
    // 能写入说明越狱了（沙箱被绕过）
    return true
} catch {
    return false
}
```

**3. 环境变量检测**
```swift
// 检查是否有越狱相关的环境变量
if let env = getenv("DYLD_INSERT_LIBRARIES") {
    let libs = String(cString: env)
    if libs.contains("MobileSubstrate") || libs.contains("Substitute") {
        return true
    }
}
```

**4. URL Scheme 检测**
```swift
// 检查 Cydia URL Scheme 是否可用
if let url = URL(string: "cydia://") {
    if UIApplication.shared.canOpenURL(url) {
        return true
    }
}
```

**5. 系统调用检测**
- 检查 `fork()` 是否能成功（沙箱内会失败）
- 检查是否能获得 root 权限

#### 越狱检测绕过方法

**1. 使用越狱屏蔽插件**
- **Shadow**：功能强大的越狱屏蔽插件
- **Choicy**：精细控制 Tweak 注入
- **Liberty Lite**：基础的越狱屏蔽
- **KernBypass**：内核级绕过

**2. Frida Hook 绕过**
```javascript
// Hook 文件存在检测
var fileManager = ObjC.classes.NSFileManager;
var origFileExists = fileManager["- fileExistsAtPath:"];
// 替换实现，对特定路径返回 false

// Hook canOpenURL
var application = ObjC.classes.UIApplication;
var origCanOpenURL = application["- canOpenURL:"];
```

**3. 修改二进制**
- 静态修改越狱检测的判断逻辑
- 将条件跳转改为相反结果

### 5.5 非越狱环境分析

即使不越狱，也可以进行一些安全分析：

#### 方法1：使用自己的开发者证书重签

**适用场景**：
- 有目标应用的 IPA 文件
- 有个人开发者证书（免费也可以）
- 设备未越狱

**分析能力**：
- 静态分析（砸壳后）
- 基本的动态调试
- Frida 调试（受限制）

**局限性**：
- 只能分析自己重签的应用
- 部分系统功能不可用（如推送、Apple Pay）
- 不能 Hook 系统进程

#### 方法2：使用 AltStore / SideStore

- 利用开发者证书自签应用
- 安装未上架 App Store 的应用
- 每 7 天需要刷新签名（免费证书）

---

## 六、常见 iOS 漏洞类型

### 6.1 系统级漏洞

#### 内核漏洞

**常见类型**：
- **缓冲区溢出**：内核驱动中的内存破坏
- **UAF（Use-After-Free）**：释放后使用
- **整数溢出**：整数运算溢出导致的内存问题
- **竞态条件**：多线程竞争导致的安全问题
- **IOKit 漏洞**：用户态与内核交互的驱动漏洞

**著名漏洞**：
- **Pangu 9**：iOS 9 越狱，利用多个内核漏洞
- **Yalu**：iOS 10 越狱，基于 IOKit 漏洞
- **tfp0**：获取 task_for_pid(0) 权限，即内核任务端口

#### WebKit 漏洞

WebKit 是 iOS 系统的浏览器内核，也是最常见的攻击面之一。

**常见类型**：
- **JIT 漏洞**：JavaScript JIT 编译器的漏洞
- **类型混淆**：对象类型错误导致的内存破坏
- **UAF**：对象释放后使用
- **越界读写**：数组越界访问

**著名漏洞链**：
- **JailbreakMe**：通过浏览器访问网页即可越狱
- **Pangu Web**：基于 WebKit 的越狱方案

#### 沙箱逃逸

沙箱逃逸是指从受限的沙箱环境中突破出来，获得更高权限。

**常见方法**：
- 利用 Mach 消息漏洞攻击系统服务
- 利用 XPC 服务漏洞
- 利用内核漏洞直接提权
- 利用文件系统漏洞

### 6.2 应用级漏洞

#### 数据存储不安全

**常见问题**：
- **钥匙串使用不当**：虽然钥匙串是安全的，但如果配置不当也有风险
- **plist 文件明文存储**：敏感信息存储在 UserDefaults 的 plist 中
- **剪贴板数据泄露**：敏感信息复制到剪贴板后被其他应用读取
- **屏幕截图泄露**：应用进入后台时的截图可能包含敏感信息
- **日志泄露**：NSLog 输出敏感信息

**示例：不安全的 UserDefaults**
```swift
// 危险：明文存储密码
UserDefaults.standard.set(password, forKey: "user_password")

// 安全：使用 Keychain 存储
let query: [String: Any] = [
    kSecClass as String: kSecClassGenericPassword,
    kSecAttrAccount as String: "user_password",
    kSecValueData as String: password.data(using: .utf8)!
]
SecItemAdd(query as CFDictionary, nil)
```

#### 通信安全问题

**常见问题**：
- **ATS 配置不当**：允许 HTTP 明文传输
- **证书校验绕过**：自定义 URLProtocol 或 SSL 代理导致证书校验失效
- **SSL Pinning 实现缺陷**：实现有漏洞的证书固定

**ATS（App Transport Security）**：
```xml
<!-- 危险：完全禁用 ATS -->
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
</dict>

<!-- 推荐：仅对特定域名允许 HTTP -->
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <false/>
    <key>NSExceptionDomains</key>
    <dict>
        <key>api.example.com</key>
        <dict>
            <key>NSExceptionAllowsInsecureHTTPLoads</key>
            <false/>
        </dict>
    </dict>
</dict>
```

#### WebView 漏洞

**常见问题**：
- **JavaScript 接口注入**：通过 JavaScript 调用原生代码
- **URL Scheme 攻击**：通过自定义 URL Scheme 调用应用功能
- **Universal Link 绕过**：绕过 Universal Link 校验
- **文件域漏洞**：通过 file:// 协议读取本地文件

#### URL Scheme 安全

**风险**：
- 恶意应用注册相同的 URL Scheme
- 通过 URL Scheme 调用应用内部功能
- 参数注入导致越权操作

**示例：URL Scheme 调用**
```swift
// 调用其他应用
if let url = URL(string: "myapp://pay?amount=100") {
    UIApplication.shared.open(url)
}
```

### 6.3 业务逻辑漏洞

与 Web 应用类似，移动应用也存在业务逻辑漏洞：

- **越权访问**：修改用户 ID 查看他人数据
- **支付漏洞**：修改支付金额、绕过支付验证
- **验证码绕过**：验证码可重放、可预测
- **密码重置漏洞**：重置逻辑缺陷
- **刷积分/刷奖励**：利用业务逻辑漏洞

---

## 七、iOS 应用安全检测要点

### 7.1 静态检测

#### 1. 二进制文件检测

| 检测项 | 说明 | 检测方法 |
|--------|------|---------|
| 代码签名 | 签名是否有效 | codesign -vvv |
| 权限配置 | entitlements 是否合理 | codesign -d --entitlements |
| PIE 保护 | 地址空间随机化 | otool -hv |
| Stack Canary | 栈保护 | otool -I \| grep stack_chk |
| ARC | 自动引用计数 | 查看编译标志 |
| 加密标志 | 是否加密（App Store 应用会加密） | otool -l \| grep cryptid |

**检测命令**：
```bash
# 查看 Mach-O 文件头信息（看 PIE）
otool -hv MyApp.app/MyApp

# 查看加密信息
otool -l MyApp.app/MyApp | grep -A 4 LC_ENCRYPTION_INFO

# 查看共享库依赖
otool -L MyApp.app/MyApp

# 查看签名信息
codesign -dvvv MyApp.app/MyApp

# 查看 entitlements
codesign -d --entitlements - MyApp.app/MyApp

# 导出头文件（class-dump）
class-dump MyApp.app/MyApp
```

#### 2. 资源文件检测

| 检测项 | 说明 |
|--------|------|
| Info.plist | 检查 ATS 配置、URL Scheme、权限声明 |
| 配置文件 | 检查是否有敏感配置（URL、密钥等） |
| 证书文件 | 检查是否包含敏感证书/密钥 |
| 数据库文件 | 检查 SQLite 数据库是否有敏感数据 |
| 网页资源 | HTML/JS 文件中是否有敏感信息 |

#### 3. 代码检测

**检测内容**：
- 硬编码的密钥、密码、URL
- 不安全的加密算法（MD5、SHA1、ECB 模式）
- 不安全的随机数生成（arc4random 是安全的，rand 不安全）
- 日志输出（NSLog 打印敏感信息）
- 越狱检测是否完善
- SSL Pinning 实现是否正确
- 数据存储是否使用 Keychain

### 7.2 动态检测

#### 1. 数据存储检测

| 检测项 | 检测方法 |
|--------|---------|
| UserDefaults | 查看 Library/Preferences/ 下的 plist 文件 |
| Keychain | 使用 Keychain 查看工具或 Frida Hook |
| 文件存储 | 浏览 Documents、Library、tmp 目录 |
| 数据库 | 检查 .db、.sqlite 文件 |
| 剪贴板 | 操作应用后检查剪贴板内容 |
| 键盘缓存 | 检查键盘的自动更正缓存 |

#### 2. 通信安全检测

| 检测项 | 检测方法 |
|--------|---------|
| 明文传输 | 使用 Charles/Burp 抓包，查看是否有 HTTP 明文 |
| 证书校验 | 使用自签名证书，看应用是否接受 |
| SSL Pinning | 安装系统 CA 证书，看能否抓包 |
| 弱加密算法 | 查看 TLS 版本和加密套件 |
| 敏感数据加密 | 传输的敏感数据是否额外加密 |

#### 3. 运行时安全检测

| 检测项 | 检测方法 |
|--------|---------|
| 越狱检测 | 在越狱设备上运行，看是否检测 |
| 调试检测 | 尝试用 LLDB 附加调试 |
| 完整性校验 | 修改应用文件，看能否运行 |
| 重签名检测 | 用其他证书重签，看能否正常运行 |
| Hook 检测 | 用 Frida 注入，看是否被检测 |
| 后台截图 | 按 Home 键，检查任务栏截图是否敏感 |

#### 4. 组件安全检测

**URL Scheme 测试**：
```bash
# 列出应用的 URL Scheme
# 查看 Info.plist 中的 CFBundleURLSchemes

# 测试调用
idevice-app-launch -u UDID --scheme myapp://test
```

**Universal Link 测试**：
- 测试 apple-app-site-association 文件
- 测试 Universal Link 的跳转逻辑
- 检查是否存在绕过可能

**App Extension 测试**：
- 检查共享数据容器
- 检查扩展与主应用的通信
- 测试扩展的权限边界

### 7.3 渗透测试工具

| 工具 | 用途 | 平台 |
|------|------|------|
| Frida | 动态插桩、Hook | macOS/Linux/Windows |
| class-dump | 导出头文件 | macOS |
| Hopper | 反汇编、反编译 | macOS |
| IDA Pro | 反汇编、反编译、调试 | 多平台 |
| Ghidra | 开源逆向工具 | 多平台 |
| Cycript | 动态调试 | iOS（Cydia） |
| LLDB | 调试器 | macOS/Xcode |
| Charles | HTTP/HTTPS 抓包 | 多平台 |
| Burp Suite | 抓包与渗透测试 | 多平台 |
| MobSF | 自动化移动安全测试 | 多平台 |
| objection | Frida 封装工具 | 多平台 |
| checkra1n | 越狱工具 | macOS/Linux |
| frida-ios-dump | 砸壳工具 | 多平台 |
| iProxy | 端口转发 | macOS/Linux |

### 7.4 安全测试流程

```
1. 信息收集
   ├── 获取 IPA 文件
   ├── 分析 Info.plist
   ├── 分析 URL Scheme
   ├── 分析 Frameworks
   └── 识别第三方 SDK

2. 静态分析
   ├── class-dump 导出头文件
   ├── Hopper/IDA 反编译
   ├── 搜索敏感字符串
   ├── 分析关键函数
   ├── 检查加密算法
   └── 检查数据存储

3. 动态分析（越狱设备）
   ├── 安装应用
   ├── Frida Hook 关键函数
   ├── 抓包分析通信
   ├── 浏览文件系统
   ├── 查看 Keychain 数据
   ├── 测试越狱检测
   └── 调试关键功能

4. 漏洞验证
   ├── 验证发现的问题
   ├── 构造 PoC
   ├── 评估风险等级
   └── 复现步骤

5. 报告编写
   ├── 漏洞描述
   ├── 风险等级
   ├── 复现步骤
   ├── 修复建议
   └── 证据截图
```

---

> 提示：iOS 安全研究门槛相对较高，需要 macOS 设备和一定的逆向基础。建议从基础的静态分析入手，逐步学习动态调试和漏洞挖掘。
