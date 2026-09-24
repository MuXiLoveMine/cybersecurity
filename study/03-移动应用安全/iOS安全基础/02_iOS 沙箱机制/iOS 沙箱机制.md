# iOS 沙箱机制

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

---

