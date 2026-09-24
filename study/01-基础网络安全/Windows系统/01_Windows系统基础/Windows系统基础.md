# Windows系统基础

### 1.1 Windows系统架构

Windows操作系统采用分层架构设计，核心分为**内核态（Kernel Mode）**和**用户态（User Mode）**两大部分，通过系统调用机制进行交互。

#### 1.1.1 内核态与用户态

**内核态（Kernel Mode）**：
- 拥有最高权限，可直接访问所有硬件和内存
- 运行Windows内核（NTOSKRNL.EXE）、硬件抽象层（HAL）、设备驱动程序
- 崩溃会导致系统蓝屏（BSOD）
- 内存空间受保护，用户态无法直接访问

**用户态（User Mode）**：
- 权限受限，通过系统调用访问内核服务
- 运行应用程序、系统服务进程、环境子系统
- 崩溃仅影响当前进程，不会导致系统宕机
- 每个用户态进程拥有独立的虚拟地址空间

#### 1.1.2 NT内核

Windows NT内核是现代Windows系统的核心，主要组件包括：

- **执行体（Executive）**：包含进程管理器、内存管理器、I/O管理器、对象管理器、安全引用监视器、即插即用管理器、电源管理器等
- **内核（Kernel）**：提供线程调度、中断和异常处理、多处理器同步等底层机制
- **硬件抽象层（HAL）**：屏蔽硬件差异，提供统一的硬件接口
- **设备驱动程序**：硬件与操作系统之间的桥梁
- **窗口和图形系统**：处理图形输出和用户输入

#### 1.1.3 系统服务（System Service）

系统服务是在后台运行的可执行程序，通常无需用户交互：
- 由服务控制管理器（SCM）管理，对应服务数据库存储在注册表 `HKLM\SYSTEM\CurrentControlSet\Services`
- 可以以SYSTEM、LOCAL SERVICE、NETWORK SERVICE等账户运行
- 常见类型：Win32服务、驱动程序服务、文件系统驱动服务

### 1.2 Windows版本介绍

#### 1.2.1 客户端版本

| 版本 | 发布时间 | 主要特性 |
|------|----------|----------|
| Windows 10 | 2015年 | 统一平台、Cortana、Edge浏览器、Windows Hello |
| Windows 10 21H2 | 2021年 | LTSC长期服务版，稳定支持至2027年 |
| Windows 11 | 2021年 | 全新UI、TPM 2.0要求、WSL2改进、安全增强 |
| Windows 11 22H2/23H2 | 2022/2023年 | 功能更新，持续安全加固 |

#### 1.2.2 服务器版本

| 版本 | 发布时间 | 主要特性 |
|------|----------|----------|
| Windows Server 2016 | 2016年 | Nano Server、容器支持、Shielded VM |
| Windows Server 2019 | 2019年 | Windows Admin Center、改进混合云、WSL2 |
| Windows Server 2022 | 2021年 | 多层安全、Azure集成、SMB加密增强 |

#### 1.2.3 版本差异要点

- **客户端版**面向桌面用户，侧重用户体验和兼容性
- **服务器版**面向企业服务器，侧重稳定性、安全性和服务角色
- **LTSC/LTSB版**为长期服务通道，仅接收安全更新，无功能更新，适合工控等稳定场景
- 内核版本号可通过 `winver` 命令或 `[Environment]::OSVersion.Version` 查看

### 1.3 用户账户与权限体系

#### 1.3.1 账户类型

**本地账户**：
- **管理员账户（Administrator）**：拥有系统最高权限，默认禁用
- **标准用户账户**：日常使用账户，权限受限，执行敏感操作需UAC提升
- **来宾账户（Guest）**：最低权限，默认禁用

**内置系统账户**：
- **SYSTEM（本地系统）**：最高权限账户，用于运行核心系统服务，权限高于管理员
- **LOCAL SERVICE**：用于运行本地服务，权限与标准用户类似，以匿名身份访问网络资源
- **NETWORK SERVICE**：用于运行网络服务，以计算机账户身份访问网络资源
- **TrustedInstaller**：用于Windows模块安装服务，拥有系统文件和注册表的最高控制权

#### 1.3.2 权限与特权

**权限（Permissions）**：
- NTFS文件/文件夹权限：完全控制、修改、读取和执行、读取、写入
- 注册表权限：完全控制、读取、写入、创建子项等
- 共享权限：完全控制、更改、读取

**特权（Privileges）**：
- 系统级权限，如 `SeDebugPrivilege`（调试程序）、`SeBackupPrivilege`（备份文件）、`SeShutdownPrivilege`（关闭系统）
- 通过本地策略或组策略分配
- 可使用 `whoami /priv` 查看当前账户特权

#### 1.3.3 用户账户控制（UAC）

UAC是Windows的安全机制，防止未经授权的系统级更改：
- 标准用户需输入管理员凭据才能执行管理操作
- 管理员默认以标准用户权限运行，执行管理操作时需确认提升
- UAC级别可通过控制面板或组策略调整

### 1.4 文件系统基础

#### 1.4.1 NTFS权限

NTFS（New Technology File System）是Windows的默认文件系统，支持细粒度权限控制：

```powershell
# 查看文件/文件夹NTFS权限
Get-Acl "C:\Windows" | Format-List

# 图形界面查看：右键属性 → 安全选项卡
```

**标准权限**：
- **完全控制**：可读取、写入、修改、删除文件/文件夹，并可更改权限和获取所有权
- **修改**：可读取、写入、修改、删除文件/文件夹
- **读取和执行**：可读取文件内容并执行程序
- **读取**：仅可读取文件内容
- **写入**：可写入文件/文件夹
- **特殊权限**：更细粒度的权限控制

#### 1.4.2 共享权限

共享权限与NTFS权限叠加时，取两者中**更严格**的权限：
- 共享权限仅对通过网络访问的用户生效
- 本地登录用户不受共享权限限制，仅受NTFS权限约束
- 建议：共享权限设为"Everyone完全控制"，通过NTFS权限进行精细控制

#### 1.4.3 EFS加密

EFS（Encrypting File System）是NTFS内置的文件加密功能：
- 基于公钥加密，用户透明访问加密文件
- 加密文件对其他用户不可读
- 需妥善备份EFS证书，否则数据永久丢失

```cmd
:: 使用cipher命令管理EFS
cipher /E 文件名        :: 加密文件
cipher /D 文件名        :: 解密文件
cipher /C 文件名        :: 显示加密信息
cipher /K               :: 生成新的EFS证书和密钥
```

### 1.5 注册表基础

#### 1.5.1 注册表结构

注册表是Windows的核心配置数据库，采用层级结构存储系统和应用程序配置：

**五大根键**：

| 根键 | 缩写 | 说明 |
|------|------|------|
| HKEY_CLASSES_ROOT | HKCR | 文件关联和COM对象注册 |
| HKEY_CURRENT_USER | HKCU | 当前用户的配置信息 |
| HKEY_LOCAL_MACHINE | HKLM | 系统级配置，影响所有用户 |
| HKEY_USERS | HKU | 所有用户的配置文件 |
| HKEY_CURRENT_CONFIG | HKCC | 当前硬件配置文件 |

#### 1.5.2 常用注册表路径

```
HKLM\SYSTEM\CurrentControlSet\Services     # 服务配置
HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion  # 系统版本与组件
HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon  # 登录配置
HKCU\Software\Microsoft\Windows\CurrentVersion\Run  # 用户启动项
HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run  # 系统启动项
HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server  # RDP配置
```

#### 1.5.3 注册表权限

注册表项同样支持权限控制：
- 管理员默认拥有大部分注册表项的完全控制权
- SYSTEM账户拥有全部控制权
- 可通过 `regedit` 图形界面或 `reg` 命令修改权限
- 修改注册表前建议先备份

```cmd
:: reg命令基本操作
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion"
reg add "HKCU\Software\Test" /v ValueName /t REG_SZ /d "data"
reg export "HKLM\SOFTWARE\Microsoft\Windows" backup.reg
```

### 1.6 进程与服务管理

#### 1.6.1 进程树

Windows进程以树状结构组织，常见系统进程：

| 进程名 | 说明 |
|--------|------|
| System Idle Process | 空闲进程，CPU空闲时间统计 |
| System | 系统内核进程 |
| smss.exe | 会话管理器，第一个用户态进程 |
| csrss.exe | 客户端/服务器运行时子系统 |
| wininit.exe | Windows启动应用进程 |
| winlogon.exe | 登录进程，处理交互式登录 |
| services.exe | 服务控制管理器（SCM） |
| svchost.exe | 通用服务宿主进程，承载多个系统服务 |
| lsass.exe | 本地安全机构子系统，处理身份验证 |
| explorer.exe | Windows资源管理器，桌面外壳 |

#### 1.6.2 进程管理命令

```powershell
# 查看进程列表
Get-Process
tasklist
tasklist /svc                    # 查看进程承载的服务
tasklist /m                      # 查看进程加载的DLL
tasklist /v                      # 查看详细信息

# 查看进程树
tasklist /fi "imagename eq svchost.exe"

# 结束进程
taskkill /PID 1234
taskkill /IM notepad.exe
taskkill /F /IM notepad.exe      # 强制结束
Stop-Process -Name notepad

# 查看进程详细信息
Get-Process -Name explorer | Select-Object *
```

#### 1.6.3 服务控制管理器（SCM）

服务控制管理器（services.exe）负责管理Windows服务：
- 服务配置存储在 `HKLM\SYSTEM\CurrentControlSet\Services`
- 服务启动类型：自动（Automatic）、自动（延迟启动）、手动（Manual）、禁用（Disabled）
- 服务运行状态：运行中、已停止、已暂停、正在启动、正在停止

```powershell
# 服务管理命令
Get-Service                         # 查看所有服务
Get-Service -Name TermService       # 查看指定服务
Start-Service -Name TermService     # 启动服务
Stop-Service -Name TermService      # 停止服务
Set-Service -Name Telnet -StartupType Disabled  # 设置启动类型
```

---

---

## 🛠️ 补充：实战拓展

### 命令速查表

```powershell
# 系统信息查询
systeminfo                          # 系统详细信息
winver                              # Windows版本
[Environment]::OSVersion.Version    # PowerShell版本查询

# 用户与权限
whoami                              # 当前用户名
whoami /priv                        # 当前用户特权
whoami /groups                      # 当前用户所属组
net user                            # 本地用户列表
net localgroup                      # 本地组列表
net localgroup administrators       # 管理员组成员

# 进程与服务
tasklist /svc                       # 进程与服务对照
net start                           # 已启动的服务
netstat -ano                        # 网络连接与端口

# 注册表
reg query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion /v ProductName
```

### 实用脚本示例

```powershell
# 系统基本信息收集脚本
$sysInfo = @{
    计算机名 = $env:COMPUTERNAME
    操作系统 = (Get-CimInstance Win32_OperatingSystem).Caption
    版本号 = (Get-CimInstance Win32_OperatingSystem).Version
    架构 = (Get-CimInstance Win32_OperatingSystem).OSArchitecture
    处理器 = (Get-CimInstance Win32_Processor).Name
    内存GB = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 2)
    最后启动时间 = (Get-CimInstance Win32_OperatingSystem).LastBootUpTime
}
$sysInfo | Format-Table -AutoSize
```

---

