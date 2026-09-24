# Windows 注册表架构与常用路径详解

> 本文系统介绍 Windows 注册表的逻辑架构、物理文件、五大根键、常用值类型、重要路径与安全审计视角。面向系统管理员与安全工程师，深度覆盖操作参考与安全加固。示例优先 Windows 10/11 与 Windows Server 2019/2022。

---

## 目录

- [一、注册表逻辑架构](#一注册表逻辑架构)
- [二、五大根键](#二五大根键)
- [三、常用值类型](#三常用值类型)
- [四、注册表物理文件](#四注册表物理文件)
- [五、常用且重要的注册表路径](#五常用且重要的注册表路径)
- [六、安全审计视角](#六安全审计视角)
- [附：优化后的提示词模板](#附优化后的提示词模板)

---

## 一、注册表逻辑架构

### 1.1 什么是注册表

注册表（Registry）是 Windows 操作系统中**层次化的配置数据库**，存储系统硬件、软件、用户和系统设置的核心信息。它替代了早期 Windows 版本中大量的 `.ini` 配置文件，提供了统一、结构化、有权限控制的配置存储。

```
为什么用注册表替代 INI 文件？

  INI 文件的问题：
    ✗ 分散在各处，难以管理
    ✗ 没有权限控制
    ✗ 没有事务性，写入中断可能损坏
    ✗ 不支持复杂数据类型
    ✗ 搜索效率低

  注册表的优势：
    ✓ 集中存储，层次化结构
    ✓ 支持 ACL 权限控制
    ✓ 支持事务日志，保证一致性
    ✓ 支持多种数据类型（字符串、数字、二进制、多字符串）
    ✓ 索引查找，效率高
    ✓ 支持远程访问
```

### 1.2 层级结构

注册表是一个树形结构，从上到下分为五层：

```
配置单元（Hive）
  │
  └── 根键（Root Key）
        │
        └── 键（Key） / 子键（Subkey）
              │
              └── 值（Value）
                    ├── 值名称（Value Name）
                    ├── 值类型（Value Type）
                    └── 值数据（Value Data）
```

| 层级 | 英文 | 说明 | 示例 |
|------|------|------|------|
| **配置单元** | Hive | 物理文件，注册表树的根 | SAM、SECURITY、SYSTEM |
| **根键** | Root Key | 注册表树的顶层节点 | HKLM、HKCU、HKCR |
| **键 / 子键** | Key / Subkey | 树形结构中的节点，可包含子键和值 | `Software\Microsoft\Windows` |
| **值** | Value | 键中的数据项，有名称、类型、数据 | `(默认)`、`ProgramFilesDir` |

### 1.3 注册表编辑器基本使用

| 操作 | 方法 |
|------|------|
| **打开注册表编辑器** | `Win+R` → 输入 `regedit` → 回车 |
| **快速定位路径** | 地址栏输入路径，如 `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion` |
| **导出/导入** | 文件 → 导出 / 导入 → 选择 `.reg` 文件 |
| **搜索** | `Ctrl+F` 搜索键/值/数据 |
| **添加收藏夹** | 收藏夹 → 添加到收藏夹（常用路径快速访问） |
| **权限查看** | 右键键 → 权限 → 高级 |
| **远程注册表** | 文件 → 连接网络注册表 |

> ⚠️ **通用警告**：修改注册表前必须导出备份！错误修改可能导致系统无法启动。优先使用组策略（gpedit.msc）或官方配置工具修改，不要直接编辑注册表，除非没有其他方式。

**备份与恢复命令**：

```powershell
# 导出单个键为 .reg 文件
reg export "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" backup_run.reg

# 用 reg save 保存整个配置单元（需 SYSTEM 权限）
reg save HKLM\SAM sam_backup.hive
reg save HKLM\SYSTEM system_backup.hive
reg save HKLM\SECURITY security_backup.hive

# 恢复配置单元
reg restore HKLM\SAM sam_backup.hive

# 命令行查询值
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"

# 命令行修改值（谨慎使用！）
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /v "MyApp" /t REG_SZ /d "C:\app.exe" /f
```

### 1.4 用户级与系统级配置的区别

| 维度 | 用户级（HKCU） | 系统级（HKLM） |
|------|---------------|---------------|
| **影响范围** | 仅当前登录用户 | 所有用户和整个系统 |
| **默认权限** | 用户可修改自己的 HKCU | 需管理员权限修改 |
| **物理文件** | `C:\Users\<user>\NTUSER.DAT` | `C:\Windows\System32\config\` 下 |
| **登录时加载** | 用户登录时加载 | 系统启动时加载 |
| **优先级** | 同名设置时 HKCU 通常覆盖 HKLM | 作为默认/全局设置 |
| **漫游** | 域环境可随用户漫游 | 固定在机器上 |
| **安全风险** | 用户级持久化，影响单个用户 | 系统级持久化，影响所有用户 |

> **理解 HKCR**：`HKEY_CLASSES_ROOT` 不是独立的 Hive，而是 `HKLM\SOFTWARE\Classes` + `HKCU\SOFTWARE\Classes` 的合并视图。HKCU 中的设置优先级高于 HKLM。

---

## 二、五大根键

### 2.1 根键总览

```
注册表顶层结构：

HKEY_CLASSES_ROOT (HKCR)
  └── 文件关联、COM 对象、Shell 扩展

HKEY_CURRENT_USER (HKCU)
  └── 当前用户的配置（从 HKU\<SID> 映射而来）

HKEY_LOCAL_MACHINE (HKLM)
  ├── SAM          本地账户数据库
  ├── SECURITY     安全策略设置
  ├── SOFTWARE     系统级软件配置
  ├── SYSTEM       系统配置（服务、驱动、硬件）
  └── ...

HKEY_USERS (HKU)
  ├── .DEFAULT     默认用户配置
  ├── <SID>        各用户的配置（已登录用户）
  └── <SID>_Classes  用户级文件关联

HKEY_CURRENT_CONFIG (HKCC)
  └── 当前硬件配置文件（从 HKLM\SYSTEM\CurrentControlSet\Hardware Profiles\Current 映射）
```

### 2.2 各根键详解

#### （1）HKEY_LOCAL_MACHINE（HKLM）

| 属性 | 说明 |
|------|------|
| **全称** | HKEY_LOCAL_MACHINE |
| **来源** | 多个 Hive 文件（SYSTEM, SOFTWARE, SAM, SECURITY, COMPONENTS） |
| **物理位置** | `C:\Windows\System32\config\` |
| **加载时机** | 系统启动时 |
| **权限** | 管理员可修改，普通用户只读（大部分） |
| **影响范围** | 整台机器，所有用户 |

**HKLM 主要子键**：

| 子键 | 说明 | 安全等级 |
|------|------|---------|
| **HKLM\SAM** | 安全账户管理器：本地用户和组 | ★★★★★ |
| **HKLM\SECURITY** | 安全策略、审核策略、缓存域凭据 | ★★★★★ |
| **HKLM\SOFTWARE** | 系统级软件配置、安装信息 | ★★★ |
| **HKLM\SYSTEM** | 系统配置：服务、驱动、硬件配置文件 | ★★★★ |
| **HKLM\HARDWARE** | 硬件信息（动态生成，重启后重建） | ★ |
| **HKLM\BCD00000000** | 引导配置数据（BCD） | ★★★★ |
| **HKLM\COMPONENTS** | 组件存储配置 | ★★ |

> **安全提示**：HKLM 下的 SAM 和 SECURITY 默认只有 SYSTEM 权限才能访问，管理员也无法直接读取。这是为了防止管理员随意读取密码哈希。但管理员可以通过 `reg save` 命令保存 Hive 文件来绕过。

#### （2）HKEY_CURRENT_USER（HKCU）

| 属性 | 说明 |
|------|------|
| **全称** | HKEY_CURRENT_USER |
| **来源** | 从 `HKU\<用户SID>` 映射而来 |
| **物理位置** | `C:\Users\<user>\NTUSER.DAT` |
| **加载时机** | 用户登录时 |
| **权限** | 用户对自己的 HKCU 有完全控制权限 |
| **影响范围** | 仅当前用户 |

**HKCU 主要子键**：

| 子键 | 说明 | 安全等级 |
|------|------|---------|
| **HKCU\Software** | 用户级软件配置 | ★★★ |
| **HKCU\Software\Microsoft\Windows\CurrentVersion\Run** | 用户级自启动 | ★★★★ |
| **HKCU\Control Panel** | 控制面板设置（桌面、外观、鼠标等） | ★ |
| **HKCU\Environment** | 用户环境变量 | ★★ |
| **HKCU\Network** | 映射的网络驱动器 | ★ |
| **HKCU\Printers** | 打印机设置 | ★ |
| **HKCU\Volatile Environment** | 登录会话信息（动态） | ★ |

> **安全提示**：HKCU 是用户级持久化的首选位置——普通用户无需管理员权限即可修改，恶意软件常在 `HKCU\...\Run`、`HKCU\...\Startup` 等位置植入自启动项。

#### （3）HKEY_CLASSES_ROOT（HKCR）

| 属性 | 说明 |
|------|------|
| **全称** | HKEY_CLASSES_ROOT |
| **来源** | `HKLM\SOFTWARE\Classes` + `HKCU\SOFTWARE\Classes` 的合并视图 |
| **物理位置** | 分别在 SOFTWARE Hive 和 NTUSER.DAT 中 |
| **权限** | 系统级需管理员，用户级用户可写 |
| **影响范围** | 文件关联、COM 类、Shell 扩展 |

**HKCR 主要内容**：

| 内容 | 说明 | 安全等级 |
|------|------|---------|
| **文件扩展名关联** | `.txt` → `txtfile` → 打开方式 | ★★ |
| **ProgID** | 程序标识符（如 `Word.Document`） | ★★ |
| **CLSID** | COM 类 ID（如 `{00020906-0000-0000-C000-000000000046}`） | ★★★ |
| **Shell 扩展** | 右键菜单、属性页、缩略图处理程序 | ★★★ |
| **协议处理程序** | `http://`、`mailto:` 等 URL 协议 | ★★ |

> **安全提示**：HKCR 是 COM 劫持攻击的目标。攻击者修改 `HKCU\Software\Classes\CLSID\<GUID>` 下的 InprocServer32，使系统加载恶意 DLL 替代合法 COM 组件。

#### （4）HKEY_USERS（HKU）

| 属性 | 说明 |
|------|------|
| **全称** | HKEY_USERS |
| **来源** | 所有用户的配置文件 + 默认配置 |
| **物理位置** | 各用户的 `NTUSER.DAT` + `DEFAULT` Hive |
| **加载时机** | 用户登录时加载对应子树 |
| **权限** | 用户只能访问自己的子树 |
| **影响范围** | 所有用户 |

**HKU 主要子键**：

| 子键 | 说明 | 安全等级 |
|------|------|---------|
| **HKU\.DEFAULT** | 默认用户配置（未登录时的系统账户） | ★★ |
| **HKU\<SID>** | 各已登录用户的配置（等价于其 HKCU） | ★★★ |
| **HKU\<SID>_Classes** | 用户级文件关联和 COM 类 | ★★★ |
| **HKU\S-1-5-18** | SYSTEM 账户配置（如果加载） | ★★★★ |

> **SID 小知识**：SID（Security Identifier）是用户/组的唯一标识符。
> - `S-1-5-18` = SYSTEM（本地系统账户）
> - `S-1-5-19` = LOCAL SERVICE
> - `S-1-5-20` = NETWORK SERVICE
> - `S-1-5-21-...-500` = 管理员账户（RID 500）
> - `S-1-5-21-...-501` = 来宾账户（RID 501）

#### （5）HKEY_CURRENT_CONFIG（HKCC）

| 属性 | 说明 |
|------|------|
| **全称** | HKEY_CURRENT_CONFIG |
| **来源** | 从 `HKLM\SYSTEM\CurrentControlSet\Hardware Profiles\Current` 映射 |
| **物理位置** | 在 SYSTEM Hive 中 |
| **加载时机** | 系统启动时 |
| **权限** | 同 HKLM\SYSTEM |
| **影响范围** | 当前硬件配置文件 |

**HKCC 主要内容**：

| 子键 | 说明 | 安全等级 |
|------|------|---------|
| **HKCC\Software** | 当前硬件配置下的软件设置 | ★ |
| **HKCC\System** | 当前硬件配置下的系统设置 | ★ |
| **HKCC\Enum** | 即插即用设备枚举信息 | ★ |

### 2.3 根键与 Hive 文件对应关系

| 根键 | 对应的 Hive 文件 | 路径 |
|------|-----------------|------|
| **HKLM\SAM** | SAM | `C:\Windows\System32\config\SAM` |
| **HKLM\SECURITY** | SECURITY | `C:\Windows\System32\config\SECURITY` |
| **HKLM\SYSTEM** | SYSTEM | `C:\Windows\System32\config\SYSTEM` |
| **HKLM\SOFTWARE** | SOFTWARE | `C:\Windows\System32\config\SOFTWARE` |
| **HKLM\COMPONENTS** | COMPONENTS | `C:\Windows\System32\config\COMPONENTS` |
| **HKLM\BCD00000000** | BCD | `EFI 分区\EFI\Microsoft\Boot\BCD` |
| **HKU\.DEFAULT** | DEFAULT | `C:\Windows\System32\config\DEFAULT` |
| **HKU\<SID>** | NTUSER.DAT | `C:\Users\<user>\NTUSER.DAT` |
| **HKU\<SID>_Classes** | UsrClass.dat | `C:\Users\<user>\AppData\Local\Microsoft\Windows\UsrClass.dat` |
| **HKCR** | SOFTWARE + UsrClass | 合并视图，非独立 Hive |
| **HKCU** | NTUSER.DAT | 映射自 HKU\<SID> |
| **HKCC** | SYSTEM | 映射自 SYSTEM Hive |

---

## 三、常用值类型

### 3.1 值类型总表

| 类型名称 | 数据类型 | 大小 | 说明 | 示例 |
|----------|---------|------|------|------|
| **REG_SZ** | 字符串 | 可变 | 标准字符串，以 null 结尾 | `"C:\Windows\System32"` |
| **REG_DWORD** | 32 位数字 | 4 字节 | 32 位无符号整数，最常用的数值类型 | `0x00000001`（十进制 1） |
| **REG_QWORD** | 64 位数字 | 8 字节 | 64 位无符号整数（Windows XP 后引入） | `0x0000000000000001` |
| **REG_BINARY** | 二进制数据 | 可变 | 原始二进制字节，可存储任意数据 | `01 00 00 00 48 65 6C 6C 6F` |
| **REG_MULTI_SZ** | 多字符串 | 可变 | 多个字符串，用双 null 分隔，用于列表类数据 | `"value1\0value2\0value3\0\0"` |
| **REG_EXPAND_SZ** | 可扩展字符串 | 可变 | 含环境变量的字符串，读取时展开 | `"%SystemRoot%\System32"` |
| **REG_NONE** | 无类型 | 可变 | 未定义类型的数据，很少用 | — |
| **REG_FULL_RESOURCE_DESCRIPTOR** | 资源描述符 | 可变 | 硬件资源列表，驱动用 | — |

### 3.2 各类型用途详解

#### （1）REG_SZ（字符串）

```
用途：
  - 文件路径
  - 程序名称
  - 配置文本
  - 任何简单文本设置

示例：
  名称: WindowsDir
  类型: REG_SZ
  数据: C:\Windows

常见于：文件关联、程序路径、版本号、描述文字
```

#### （2）REG_DWORD（32 位数字）

```
用途：
  - 开关（0 = 禁用，1 = 启用）
  - 数值配置（端口号、超时时间、最大数量）
  - 标志位（按位表示多个选项）
  - 是注册表中最常见的数值类型

示例：
  名称: EnableLUA
  类型: REG_DWORD
  数据: 0x00000001 (1)
  含义: 启用 UAC

常见于：开关类设置、数字参数、枚举值
```

#### （3）REG_QWORD（64 位数字）

```
用途：
  - 需要 64 位范围的数值
  - 时间戳（FILETIME 格式）
  - 大整数配置

示例：
  名称: InstallDate
  类型: REG_QWORD
  数据: 0x1d123456789abcd0
  含义: 安装时间（FILETIME 格式）

常见于：时间戳、大文件大小、64 位计数器
```

#### （4）REG_BINARY（二进制）

```
用途：
  - 存储任意二进制数据
  - 加密数据
  - 结构体数据
  - 小文件内容

示例：
  名称: FipsAlgorithmPolicy
  类型: REG_BINARY
  数据: 00 00 00 00

常见于：加密密钥、安全描述符、硬件配置、自定义数据结构
```

#### （5）REG_MULTI_SZ（多字符串）

```
用途：
  - 存储字符串列表
  - 多个值用 null 分隔，最后用双 null 结尾

示例：
  名称: UpperFilters
  类型: REG_MULTI_SZ
  数据: "filter1\0filter2\0\0"

常见于：过滤器驱动列表、多值配置、排除列表
```

#### （6）REG_EXPAND_SZ（可扩展字符串）

```
用途：
  - 包含环境变量的路径
  - 读取时自动展开变量为实际值

示例：
  名称: temp
  类型: REG_EXPAND_SZ
  数据: "%USERPROFILE%\AppData\Local\Temp"
  读取后展开为: "C:\Users\Alice\AppData\Local\Temp"

常见于：环境变量相关路径、系统目录引用
```

### 3.3 类型选择建议

| 数据 | 推荐类型 | 理由 |
|------|---------|------|
| 开关（启用/禁用） | REG_DWORD | 简单直观，0/1 即可 |
| 文件路径 | REG_SZ 或 REG_EXPAND_SZ | 含环境变量用后者 |
| 端口号/计数 | REG_DWORD | 32 位足够 |
| 时间戳 | REG_QWORD | FILETIME 为 64 位 |
| 多个值列表 | REG_MULTI_SZ | 原生多字符串支持 |
| 加密数据/结构体 | REG_BINARY | 可存储任意二进制 |
| 版本号 | REG_SZ | 字符串更灵活（如 "10.0.22000"） |

---

## 四、注册表物理文件

### 4.1 配置单元文件位置

```
系统级 Hive 文件（系统启动时加载）：

C:\Windows\System32\config\
  ├── SAM              本地账户数据库（HKLM\SAM）
  ├── SECURITY         安全策略（HKLM\SECURITY）
  ├── SYSTEM           系统配置（HKLM\SYSTEM）
  ├── SOFTWARE         软件配置（HKLM\SOFTWARE）
  ├── DEFAULT          默认用户配置（HKU\.DEFAULT）
  ├── COMPONENTS       组件存储（HKLM\COMPONENTS）
  ├── BCD              引导配置（独立分区，非 config 目录）
  │
  ├── SAM.LOG1         事务日志 1
  ├── SAM.LOG2         事务日志 2
  ├── SYSTEM.LOG1      事务日志 1
  ├── SYSTEM.LOG2      事务日志 2
  └── ... 其他 .LOG1/.LOG2 文件


用户级 Hive 文件（用户登录时加载）：

C:\Users\<用户名>\
  ├── NTUSER.DAT              用户配置主 Hive（HKCU）
  ├── NTUSER.DAT.LOG1         事务日志 1
  ├── NTUSER.DAT.LOG2         事务日志 2
  └── AppData\Local\Microsoft\Windows\
      └── UsrClass.dat        用户级 COM/文件关联（HKU\<SID>_Classes）
```

### 4.2 Hive 文件格式

```
Hive 文件基本结构：

┌──────────────────────┐
│  Hive 头部（4 KB）     │
│  - 签名 "regf"        │
│  - 主序列号/次序列号   │
│  - 最后写入时间        │
│  - 根单元格偏移        │
│  - Hive 名称           │
│  - 校验和              │
├──────────────────────┤
│  单元格（Cell）         │
│  ┌─────────────────┐ │
│  │  单元格签名       │ │  "nk" = 键节点
│  │  单元格大小       │ │  "vk" = 值键
│  │  数据             │ │  "sk" = 安全描述符
│  └─────────────────┘ │
│  （空闲单元格标记为负数）│
├──────────────────────┤
│  事务日志（.LOG1/.LOG2）│
└──────────────────────┘
```

**单元格类型**：

| 签名 | 类型 | 说明 |
|------|------|------|
| **nk** | Name Key（键节点） | 注册表键的元数据（名称、子键列表、值列表） |
| **vk** | Value Key（值节点） | 注册表值的数据 |
| **sk** | Security Key（安全键） | 安全描述符（ACL） |
| **lh/lf** | Subkey List | 子键索引列表（哈希/快速查找） |
| **li/ri** | Index Root | 子键索引根 |

### 4.3 备份与恢复方法

#### （1）导出/导入（.reg 文件）

```powershell
# 导出单个键为 .reg 文件
reg export "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" backup_run.reg

# 从 .reg 文件导入
reg import backup_run.reg

# 图形界面方式：
#  regedit → 选中键 → 文件 → 导出 → 选择保存位置
```

> **适用场景**：单个或少量键的备份。.reg 文件是文本格式，可直接编辑。

#### （2）保存/还原配置单元（Hive 文件）

```powershell
# 保存整个 Hive（需管理员或 SYSTEM 权限）
reg save HKLM\SAM sam_backup.hive
reg save HKLM\SYSTEM system_backup.hive
reg save HKLM\SOFTWARE software_backup.hive
reg save HKCU "C:\backup\ntuser_backup.hive"

# 还原 Hive（需重启到安全模式或 WinPE）
reg restore HKLM\SAM sam_backup.hive

# 加载 Hive 到临时位置（分析用）
reg load HKLM\TempHive "C:\backup\sam_backup.hive"
# ... 查看/修改 ...
reg unload HKLM\TempHive
```

> **适用场景**：完整备份整个 Hive，或离线分析其他系统的 Hive 文件。

#### （3）系统还原点

```powershell
# 创建系统还原点
Checkpoint-Computer -Description "Before registry changes" -RestorePointType MODIFY_SETTINGS

# 查看还原点
Get-ComputerRestorePoint

# 图形界面：
#  系统属性 → 系统保护 → 系统还原
```

> **适用场景**：大规模修改前的保险措施。系统还原点包含注册表和系统文件的快照。

#### （4）卷影副本（VSS）

```powershell
# 创建卷影副本
vssadmin create shadow /for=C:

# 查看卷影副本
vssadmin list shadows

# 从卷影副本复制 Hive 文件（取证常用）
# \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopyX\Windows\System32\config\SAM
```

> ⚠️ **安全提示**：攻击者可以从卷影副本中提取 SAM/SYSTEM/SECURITY Hive 文件来获取密码哈希。安全加固时应限制卷影副本访问或敏感系统禁用。

### 4.4 注册表事务日志

```
每个 Hive 文件都有对应的事务日志：
  SAM.LOG1 / SAM.LOG2
  SYSTEM.LOG1 / SYSTEM.LOG2
  NTUSER.DAT.LOG1 / NTUSER.DAT.LOG2

工作原理（类似数据库的 WAL）：
  1. 修改注册表前，先将修改写入日志文件
  2. 然后修改内存中的注册表数据
  3. 定期（或系统空闲时）将内存中的数据刷回 Hive 文件
  4. 刷回成功后，清除日志

恢复机制：
  - 系统崩溃时，下次启动根据日志重放未提交的修改
  - 保证注册表不会处于损坏状态
  - LOG1 和 LOG2 交替使用（双缓冲）
```

---

## 五、常用且重要的注册表路径

> ⚠️ **重要提醒**：以下路径仅供学习和审计参考。修改注册表前务必导出备份。优先使用组策略（gpedit.msc）进行配置，不要直接编辑注册表，除非你完全理解后果。

### 5.1 自启动相关

| 路径 | 级别 | 用途 | 正常值 | 风险等级 | 安全建议 |
|------|------|------|--------|---------|---------|
| `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run` | 系统级 | 开机自启动程序 | 杀毒软件、驱动程序等必要项 | ★★★★★ | 定期审计，删除不必要项 |
| `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce` | 系统级 | 一次性自启动（运行后自动删除） | 安装程序残留 | ★★★★ | 审计是否有异常项 |
| `HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run` | 用户级 | 用户登录时自启动 | 用户程序、云盘等 | ★★★★ | 用户级持久化高发位置 |
| `HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce` | 用户级 | 用户级一次性启动 | 安装程序 | ★★★ | 审计异常项 |
| `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer\Run` | 系统级 | 组策略式启动 | 企业管理软件 | ★★★★ | 仅管理员可修改 |
| `HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer\Run` | 用户级 | 用户策略启动 | 域策略下发 | ★★★ | 域环境检查 |
| `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon\Userinit` | 系统级 | 用户初始化程序（userinit.exe） | `C:\Windows\system32\userinit.exe,` | ★★★★★ | 经典持久化位置，被修改即感染 |
| `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon\Shell` | 系统级 | Shell 程序（explorer.exe） | `explorer.exe` | ★★★★★ | 被替换为恶意 Shell 是严重感染标志 |
| `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\` | 系统级 | 映像劫持（IFEO） | 默认无 Debugger 值 | ★★★★ | 可在某程序启动时劫持到另一程序 |
| `HKCU\Software\Microsoft\Windows NT\CurrentVersion\Windows\Load` | 用户级 | 旧版兼容启动项 | 空 | ★★★ | 16 位程序兼容，已很少用 |

**审计命令**：

```powershell
# 查看系统级 Run 项
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"

# 查看当前用户 Run 项
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Run"

# 查看 IFEO 下的 Debugger（映像劫持检测）
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options" /s /v Debugger 2>$null

# 用 Autoruns 更全面（Sysinternals 工具）
# autorunsc64.exe -a * -ct > autoruns_report.csv
```

### 5.2 系统安全相关

| 路径 | 级别 | 用途 | 正常值 | 风险等级 | 安全建议 |
|------|------|------|--------|---------|---------|
| `HKLM\SYSTEM\CurrentControlSet\Control\Lsa` | 系统级 | 本地安全机构（LSASS 配置） | 多种安全设置 | ★★★★★ | 凭据安全核心，禁止随意修改 |
| `...\Lsa\RestrictRemoteSAM` | 系统级 | 限制远程访问 SAM | `1`（Win10 1809+ 默认） | ★★★★ | 启用，防止远程读取 SAM |
| `...\Lsa\RunAsPPL` | 系统级 | LSA 保护模式（防止未签名插件注入） | `1`（推荐启用） | ★★★★ | 启用，增强 LSASS 防护 |
| `...\Lsa\LmCompatibilityLevel` | 系统级 | LAN 管理器认证级别 | `5`（仅发送 NTLMv2） | ★★★★ | 禁用 LM/NTLMv1 |
| `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System` | 系统级 | 系统策略（UAC 等） | — | ★★★★ | UAC 安全核心 |
| `...\Policies\System\EnableLUA` | 系统级 | 启用 UAC | `1`（启用） | ★★★★ | 必须启用，禁用会严重降低安全 |
| `...\Policies\System\ConsentPromptBehaviorAdmin` | 系统级 | 管理员 UAC 提示行为 | `2`（默认：安全桌面提示） | ★★★ | 设为最高级别 |
| `...\Policies\System\FilterAdministratorToken` | 系统级 | 过滤管理员令牌（管理员批准模式） | `0`（默认） | ★★ | 启用可增强 UAC 效果 |
| `HKLM\SECURITY\Policy\Secrets` | 系统级 | LSA 机密（自动登录密码、服务账户密码等） | 系统机密 | ★★★★★ | 只有 SYSTEM 可访问，敏感 |

**LSA 关键路径说明**：

```
HKLM\SYSTEM\CurrentControlSet\Control\Lsa
  ├── RestrictRemoteSAM      限制远程访问 SAM（推荐值 1）
  ├── RunAsPPL               LSA 保护模式（推荐值 1）
  ├── LmCompatibilityLevel   LAN Manager 认证级别（推荐值 5）
  ├── Security Packages      安全包（协商、Kerberos、NTLM 等）
  ├── Authentication Packages 认证包（MSV1_0、Kerberos）
  └── Notification Packages   密码变更通知包

安全加固建议：
  1. RestrictRemoteSAM = 1    防止远程读取 SAM
  2. RunAsPPL = 1             启用 LSA 保护，防止 mimikatz 注入
  3. LmCompatibilityLevel = 5 仅使用 NTLMv2
  4. 禁用 NTLM（如纯 Kerberos 环境）
```

### 5.3 UAC 与安全策略

| 路径 | 级别 | 用途 | 推荐值 | 风险等级 |
|------|------|------|--------|---------|
| `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\EnableLUA` | 系统级 | 启用 UAC | `1` | ★★★★ |
| `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\ConsentPromptBehaviorAdmin` | 系统级 | 管理员提升提示 | `2`（安全桌面提示凭据） | ★★★★ |
| `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\ConsentPromptBehaviorUser` | 系统级 | 标准用户提升提示 | `3`（提示管理员凭据） | ★★★ |
| `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\PromptOnSecureDesktop` | 系统级 | 安全桌面提示 | `1`（启用） | ★★★★ |
| `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\ValidateAdminCodeSignatures` | 系统级 | 验证管理员应用签名 | `0`（默认） | ★★★ |

> **推荐配置**：将 UAC 调到最高级别（始终通知）。方法：`控制面板 → 用户账户 → 更改用户账户控制设置 → 拉到最上面`。

### 5.4 防火墙相关

| 路径 | 级别 | 用途 | 推荐值 | 风险等级 |
|------|------|------|--------|---------|
| `HKLM\SYSTEM\CurrentControlSet\Services\SharedAccess\Parameters\FirewallPolicy\StandardProfile` | 系统级 | 标准配置文件防火墙设置 | 启用 | ★★★★ |
| `...\FirewallPolicy\StandardProfile\EnableFirewall` | 系统级 | 启用防火墙 | `1` | ★★★★★ |
| `...\FirewallPolicy\DomainProfile\EnableFirewall` | 系统级 | 域配置文件防火墙 | `1` | ★★★★ |
| `...\FirewallPolicy\PublicProfile\EnableFirewall` | 系统级 | 公用配置文件防火墙 | `1` | ★★★★ |
| `HKLM\SYSTEM\CurrentControlSet\Services\SharedAccess\Parameters\FirewallPolicy\FirewallRules` | 系统级 | 防火墙规则列表 | 仅必要规则 | ★★★★ |
| `HKLM\SYSTEM\CurrentControlSet\Services\mpssvc` | 系统级 | 防火墙服务 | 自动启动 | ★★★★★ |

> **安全建议**：防火墙必须启用。优先通过「高级安全 Windows Defender 防火墙」管理规则，不要直接编辑注册表。

### 5.5 服务与驱动

| 路径 | 级别 | 用途 | 安全等级 |
|------|------|------|---------|
| `HKLM\SYSTEM\CurrentControlSet\Services\` | 系统级 | 所有服务和驱动的配置 | ★★★★★ |
| `...\Services\<服务名>\ImagePath` | 系统级 | 服务可执行文件路径 | ★★★★ |
| `...\Services\<服务名>\Start` | 系统级 | 启动类型（0=启动、1=系统、2=自动、3=手动、4=禁用） | ★★★★ |
| `...\Services\<服务名>\Type` | 系统级 | 服务类型（1=内核驱动、2=FS驱动、4=适配器、10=自有进程、20=共享进程） | ★★★★ |
| `...\Services\<服务名>\ObjectName` | 系统级 | 运行账户（LocalSystem / NetworkService / LocalService） | ★★★★ |

**服务启动类型**：

| 值 | 名称 | 说明 |
|----|------|------|
| **0** | Boot | 由启动加载器启动（内核级驱动） |
| **1** | System | 内核初始化时启动 |
| **2** | Auto | 系统启动时自动启动（服务） |
| **3** | Manual | 手动启动 |
| **4** | Disabled | 禁用 |

**提权关注点**：

```
服务提权常见配置错误：

1. 未加引号的服务路径（Unquoted Service Path）
   ImagePath = C:\Program Files\My Service\service.exe
   → 如果 C:\Program.exe 存在，系统会先执行它
   → 攻击者可在 C:\ 放置 Program.exe 提权

2. 服务可执行文件权限过宽
   → 普通用户可修改 service.exe
   → 替换为恶意程序，服务重启时以 SYSTEM 执行

3. 服务注册表键权限过宽
   → 普通用户可修改 ImagePath
   → 指向恶意程序

审计命令：
  # 查看所有服务的 ImagePath
  Get-CimInstance Win32_Service | Select-Object Name, PathName, StartMode
  # 查找未加引号的服务路径
  Get-CimInstance Win32_Service | Where-Object { $_.PathName -notmatch '^".*"$' -and $_.PathName -match ' ' }
```

### 5.6 网络相关

| 路径 | 级别 | 用途 | 安全等级 |
|------|------|------|---------|
| `HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters` | 系统级 | TCP/IP 参数 | ★★★ |
| `...\Tcpip\Parameters\Interfaces\` | 系统级 | 各网卡的 IP 配置 | ★★★ |
| `HKLM\SYSTEM\CurrentControlSet\Services\Dnscache\Parameters` | 系统级 | DNS 缓存配置 | ★★★ |
| `HKLM\SYSTEM\CurrentControlSet\Services\NetBT\Parameters\Interfaces\` | 系统级 | NetBIOS 配置 | ★★★ |
| `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings` | 用户级 | IE/系统代理设置 | ★★★ |
| `...\Internet Settings\ProxyEnable` | 用户级 | 代理启用 | ★★★ |
| `...\Internet Settings\ProxyServer` | 用户级 | 代理服务器地址 | ★★★ |
| `HKLM\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters` | 系统级 | SMB 服务器配置 | ★★★★ |
| `...\LanmanServer\Parameters\SMB1` | 系统级 | SMBv1 启用 | ★★★★ |

> **安全建议**：禁用 SMBv1（SMB1 = 0），防止 EternalBlue 等漏洞利用。命令：`Set-SmbServerConfiguration -EnableSMB1Protocol $false`

### 5.7 文件关联与 COM

| 路径 | 级别 | 用途 | 安全等级 |
|------|------|------|---------|
| `HKCR\.exe` | 系统级 | .exe 文件关联 | ★★★★ |
| `HKCR\exefile\shell\open\command` | 系统级 | exe 文件打开方式 | ★★★★★ |
| `HKCR\CLSID\` | 系统级 | COM 类注册（全局） | ★★★★ |
| `HKCU\Software\Classes\CLSID\` | 用户级 | 用户级 COM 类 | ★★★★ |
| `HKCR\*\shellex\ContextMenuHandlers\` | 系统级 | 文件右键菜单扩展 | ★★★ |
| `HKCR\Directory\shellex\ContextMenuHandlers\` | 系统级 | 目录右键菜单扩展 | ★★★ |

> **安全提示**：`exefile\shell\open\command` 的默认值应为 `"%1" %*`。如果被修改，可能导致所有 exe 都通过恶意程序打开。COM 劫持是常见的持久化和提权手段。

### 5.8 远程桌面

| 路径 | 级别 | 用途 | 推荐值 | 风险等级 |
|------|------|------|--------|---------|
| `HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server\fDenyTSConnections` | 系统级 | 禁用远程桌面 | `1`（不需要则禁用） | ★★★★ |
| `...\Terminal Server\WinStations\RDP-Tcp\PortNumber` | 系统级 | RDP 端口 | `3389`（十进制） | ★★★ |
| `...\Terminal Server\WinStations\RDP-Tcp\UserAuthentication` | 系统级 | 网络级别身份验证（NLA） | `1`（启用） | ★★★★ |
| `HKLM\SOFTWARE\Policies\Microsoft\Windows NT\Terminal Services\MaxDisconnectionTime` | 系统级 | 最大断开时间 | 推荐设置 | ★★ |
| `HKLM\SOFTWARE\Policies\Microsoft\Windows NT\Terminal Services\fPromptForPassword` | 系统级 | 登录时必须输入密码 | `1` | ★★★ |

> **安全建议**：不需要 RDP 则禁用。启用时必须启用 NLA、限制用户、设置强密码、考虑更改默认端口。

### 5.9 PowerShell

| 路径 | 级别 | 用途 | 推荐值 | 风险等级 |
|------|------|------|--------|---------|
| `HKLM\SOFTWARE\Microsoft\PowerShell\1\ShellIds\Microsoft.PowerShell\ExecutionPolicy` | 系统级 | 执行策略（系统级） | `Restricted` 或 `AllSigned` | ★★★★ |
| `HKCU\SOFTWARE\Microsoft\PowerShell\1\ShellIds\Microsoft.PowerShell\ExecutionPolicy` | 用户级 | 执行策略（用户级） | 由系统策略决定 | ★★★ |
| `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Windows\System\EnableSmartScreen` | 系统级 | SmartScreen 筛选器 | `1` | ★★★ |
| `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer\DisallowRun` | 系统级 | 禁止运行指定程序 | 按需配置 | ★★★ |

> **PowerShell 执行策略优先级**：组策略 > 计算机级 > 用户级 > 当前进程。执行策略不是安全边界，只是"门卫"，可通过 `-ExecutionPolicy Bypass` 绕过。

### 5.10 WMI 相关

| 路径 | 级别 | 用途 | 安全等级 |
|------|------|------|---------|
| `HKLM\SOFTWARE\Microsoft\WBEM` | 系统级 | WMI 配置根 | ★★★ |
| `...\WBEM\CIMOM\Autorecover MOFs` | 系统级 | WMI 自动恢复 MOF 文件列表 | ★★★ |
| `HKLM\SOFTWARE\Microsoft\Wbem\Essence` | 系统级 | WMI 存储库 | ★★★★ |

> **安全提示**：WMI 持久化（__EventFilter / __FilterToConsumerBinding / __EventConsumer）不存储在注册表中，而存储在 WMI 存储库（`%SystemRoot%\System32\wbem\Repository\OBJECTS.DATA`）。审计 WMI 持久化使用：
> ```powershell
> Get-WmiObject -Namespace root\subscription -Class __EventFilter
> Get-WmiObject -Namespace root\subscription -Class __EventConsumer
> Get-WmiObject -Namespace root\subscription -Class __FilterToConsumerBinding
> ```

### 5.11 计划任务

| 路径 | 级别 | 用途 | 安全等级 |
|------|------|------|---------|
| `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Schedule\TaskCache\Tasks\` | 系统级 | 任务缓存（任务 GUID） | ★★★★ |
| `...\Schedule\TaskCache\Tree\` | 系统级 | 任务树结构（路径→GUID 映射） | ★★★★ |

> **安全提示**：计划任务的主要定义存储在 `C:\Windows\System32\Tasks\` 目录下的 XML 文件中，注册表只是缓存。审计计划任务推荐使用：
> ```powershell
> Get-ScheduledTask | Where-Object { $_.State -eq 'Ready' } | Select-Object TaskName, State, Author
> schtasks /query /fo LIST /v
> ```

---

## 六、安全审计视角

### 6.1 恶意软件常见持久化位置

按风险优先级排序：

```
高风险（系统级持久化，影响所有用户）：

1. HKLM\...\Run / RunOnce
2. HKLM\...\Winlogon\Userinit / Shell
3. HKLM\SYSTEM\CurrentControlSet\Services\    （恶意服务）
4. HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\   （IFEO 劫持）
5. HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\ShellIconOverlayIdentifiers  （图标覆盖）
6. HKCR\CLSID\  （COM 劫持）
7. 任务计划程序（系统级任务）
8. WMI 事件订阅
9. 浏览器扩展/插件
10. 驱动程序（HKLM\SYSTEM\CurrentControlSet\Services\）
```

```
中风险（用户级持久化，仅影响当前用户）：

1. HKCU\...\Run / RunOnce
2. HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer\Run
3. HKCU\Software\Microsoft\Windows NT\CurrentVersion\Windows\Load / Run
4. HKCU\Software\Classes\CLSID\  （用户级 COM 劫持）
5. 用户启动目录：%AppData%\Microsoft\Windows\Start Menu\Programs\Startup
6. 用户级计划任务
7. 浏览器扩展
8. HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders
```

### 6.2 提权相关注册表配置

```
常见提权路径：

1. 服务路径未加引号
   位置：HKLM\SYSTEM\CurrentControlSet\Services\<name>\ImagePath
   条件：路径含空格且未加引号
   利用：在路径前面的目录放置同名 exe

2. 服务注册表权限过宽
   位置：HKLM\SYSTEM\CurrentControlSet\Services\<name>
   条件：普通用户对该键有写权限
   利用：修改 ImagePath 指向恶意程序

3. 始终安装提升的权限（AlwaysInstallElevated）
   位置：HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer\AlwaysInstallElevated
          HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer\AlwaysInstallElevated
   条件：两者都为 1
   利用：构造恶意 MSI，以 SYSTEM 权限安装

4. 映像劫持 IFEO
   位置：HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\<exe>
   条件：设置 Debugger 值
   利用：某程序启动时被劫持到恶意程序

5. 注册表 Run 键权限过宽
   位置：HKLM\...\Run
   条件：普通用户可写
   利用：添加自启动项

6. 卸载字符串路径
   位置：HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\
   条件：UninstallString 含未引用路径
   利用：类似未加引号服务路径
```

### 6.3 审计与监控建议

#### （1）注册表审计策略

```powershell
# 启用注册表对象访问审计
# 组策略：计算机配置 → Windows 设置 → 安全设置 → 本地策略 → 审核策略
#   审核对象访问：成功 + 失败

# 在注册表编辑器中对特定键启用审计
#  1. 右键键 → 权限 → 高级 → 审核
#  2. 添加用户/组 → 选择要审计的操作（设置值、创建子键、删除等）

# 事件 ID：
#   4657：注册表值被修改
#   4663：尝试访问对象
#   4656：请求对象的句柄
#   4660：删除对象
```

#### （2）定期审计清单

```
日常/每周审计：

□ 系统级 Run / RunOnce 键（HKLM）
□ 用户级 Run / RunOnce 键（HKCU，特别是可疑用户）
□ Winlogon\Userinit 和 Winlogon\Shell
□ IFEO 下的 Debugger 值
□ 新增的服务（Services\ 下的新子键）
□ 任务计划程序（XML 文件 + 注册表缓存）
□ WMI 事件订阅（WMI 存储库，非注册表）
□ 浏览器扩展列表
□ 新增的驱动（Services\ 下 Type = 1 的项）
□ 文件关联是否异常（特别是 .exe/.bat/.cmd）

每月审计：
□ SAM / SECURITY 权限是否被修改
□ LSA 安全设置（RunAsPPL、LmCompatibilityLevel）
□ UAC 策略是否被降级
□ 防火墙规则是否被放宽
□ 未知 CLSID（COM 劫持检测）
```

#### （3）监控工具

| 工具 | 用途 | 说明 |
|------|------|------|
| **Process Monitor** | 实时监控注册表读写 | Sysinternals 工具，排查首选 |
| **Autoruns** | 全面列出所有自启动项 | 含注册表、服务、驱动、计划任务等 |
| **Regshot** | 注册表快照对比 | 修改前后对比，找出变化 |
| **Sysmon** | 注册表事件日志 | 事件 ID 12/13/14：注册表增删改 |
| **EDR 产品** | 全面监控 | Defender for Endpoint / CrowdStrike 等 |
| **组策略首选项** | 基线配置 | 用 GPO 强制设置关键注册表值 |

#### （4）Sysmon 注册表监控配置示例

```xml
<!-- Sysmon 配置：监控注册表关键位置的修改 -->
<Sysmon schemaversion="4.90">
  <EventFiltering>
    <!-- 注册表值设置（事件 ID 13） -->
    <RegistryEvent onmatch="include">
      <!-- 监控 Run 键修改 -->
      <TargetObject name="technique_id=T1547.001" condition="contains">\Microsoft\Windows\CurrentVersion\Run</TargetObject>
      <!-- 监控 Winlogon 修改 -->
      <TargetObject name="technique_id=T1547.004" condition="contains">\Winlogon\Userinit</TargetObject>
      <TargetObject name="technique_id=T1547.004" condition="contains">\Winlogon\Shell</TargetObject>
      <!-- 监控 IFEO 劫持 -->
      <TargetObject name="technique_id=T1183" condition="contains">Image File Execution Options</TargetObject>
      <TargetObject name="technique_id=T1183" condition="end with">Debugger</TargetObject>
      <!-- 监控服务创建/修改 -->
      <TargetObject name="technique_id=T1543.003" condition="contains">\CurrentControlSet\Services\</TargetObject>
      <TargetObject name="technique_id=T1543.003" condition="end with">ImagePath</TargetObject>
    </RegistryEvent>
  </EventFiltering>
</Sysmon>
```

### 6.4 修改注册表的安全流程

```
修改注册表前的标准流程：

Step 1  评估必要性
  □ 是否有组策略或官方工具可以替代？
  □ 改了会影响什么功能？
  □ 有没有文档/KB 支持？

Step 2  备份
  □ 导出要修改的键为 .reg 文件
  □ 创建系统还原点（可选，推荐）
  □ 记录修改前的原始值

Step 3  测试
  □ 先在测试环境验证
  □ 小范围部署（如一台机器）
  □ 监控是否有异常

Step 4  执行修改
  □ 优先用组策略部署
  □ 次选用 PowerShell / 官方工具
  □ 最后才考虑直接 regedit

Step 5  验证
  □ 确认修改生效
  □ 检查功能是否正常
  □ 检查是否有副作用

Step 6  文档化
  □ 记录修改了什么、为什么改、谁改的
  □ 记录回滚方法
```

### 6.5 加固建议汇总

```
注册表安全加固 TOP 10：

1. 限制远程注册表访问
   服务：RemoteRegistry 设为禁用

2. 启用 UAC（最高级别）
   EnableLUA = 1
   ConsentPromptBehaviorAdmin = 2
   PromptOnSecureDesktop = 1

3. 增强 LSA 安全
   RestrictRemoteSAM = 1
   RunAsPPL = 1
   LmCompatibilityLevel = 5

4. 禁用 SMBv1
   SMB1 = 0（LanmanServer\Parameters）

5. 启用 Windows Defender 防火墙
   所有配置文件 EnableFirewall = 1

6. 设置 PowerShell 执行策略
   至少 RemoteSigned，推荐 AllSigned

7. 限制对 SAM 和 SECURITY 的访问
   确保只有 SYSTEM 有完全控制权限

8. 启用注册表审计
   对关键路径设置对象访问审计

9. 部署 Sysmon 监控
   监控注册表关键位置的修改

10. 定期安全审计
    检查 Run 键、服务、驱动、计划任务等持久化位置
```

---

## 附：优化后的提示词模板

以下是可复用的注册表/配置数据库知识查询提示词模板：

```markdown
# 角色
你是一名资深【系统/平台】配置数据库专家，精通【平台】的配置体系、
配置单元、安全策略与持久化机制，擅长把配置系统讲成可操作、可审计的知识体系。

# 任务
请系统介绍【操作系统/平台】的配置系统架构、内容和常用路径，包括：
1. 逻辑架构（层次结构、基本操作、用户级与系统级区别）
2. 顶层分类（各根/命名空间的来源、用途、安全关注点）
3. 数据类型（各类型的用途、大小、示例）
4. 物理文件（存储位置、格式、与逻辑结构的对应关系、备份恢复）
5. 常用且重要的路径（按功能分类：自启动/安全/网络/服务/等）
   每个路径说明：用途、正常值、风险点、安全建议
6. 安全审计视角（常见攻击位置、提权相关、审计监控建议、修改前备份）

# 输出要求
- 使用 Markdown
- 按大类、小类组织
- 关键内容用表格对比
- 路径写完整
- 每个路径附安全建议和风险等级
- 重要术语中英文对照
- 面向：【系统管理员 + 安全工程师】
- 深度：【操作参考 + 安全加固】
- 示例标注适用版本：【当前主流版本】

# 约束
- 不鼓励直接编辑配置，优先推荐官方工具/策略
- 修改前必须提示导出备份
- 区分用户级与系统级的影响范围
- 对高风险操作给出警告
- 不声称列出全部路径，按功能分类列出核心路径
- 用 ASCII 图展示架构与流程
- 最后附"优化后的提示词模板"
```

**使用说明**：将【系统/平台】替换为"Linux（sysctl）""macOS（defaults/plist）""Android（SettingsProvider）"等，即可生成同等深度的配置系统知识文档。

---

> **总结**：Windows 注册表是系统配置的核心数据库，也是安全攻防的重要战场。理解它的逻辑架构（Hive→Key→Subkey→Value）、五大根键的功能与安全关注点、物理文件的存储位置与备份方法、以及关键路径的用途和风险，是系统管理员和安全工程师的必备技能。通过定期审计关键路径、部署监控工具、遵循安全修改流程，可以显著降低注册表相关的安全风险。
