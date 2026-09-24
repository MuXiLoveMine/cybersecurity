# iOS 系统架构

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

---

