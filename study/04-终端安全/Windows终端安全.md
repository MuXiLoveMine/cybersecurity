# Windows 终端安全详解

> 本文档深入讲解 Windows 终端安全的各个方面，包括安全机制、配置基线、漏洞类型、提权方法、横向移动、权限维持、恶意代码分析、应急响应和安全加固。

---

## 一、Windows 安全机制

### 1.1 用户账户控制（UAC）

**UAC 概述**

用户账户控制（User Account Control）是 Windows Vista 及以后版本引入的安全机制，旨在防止恶意软件以管理员权限运行。当用户以标准用户身份登录时，大部分操作会以标准权限执行，只有获得管理员授权的操作才能以管理员权限运行。

**UAC 工作原理**

- 用户登录时，系统会创建两个访问令牌：标准用户令牌和管理员令牌
- 默认情况下，应用程序使用标准用户令牌运行
- 当应用程序需要管理员权限时，会触发 UAC 提示，用户确认后切换到管理员令牌

**UAC 级别**

| 级别 | 描述 |
|------|------|
| 始终通知 | 最严格，任何程序更改都需要确认 |
| 仅在程序尝试更改我的计算机时通知 | 默认级别，Windows 自身更改不通知 |
| 仅在程序尝试更改我的计算机时通知（不降低桌面亮度） | 同上，但不锁定桌面 |
| 从不通知 | 关闭 UAC，不推荐 |

**UAC 绕过技术**

UAC 并非完美的安全边界，存在多种绕过方法：

```
常见 UAC 绕过方法：
1. 注册表劫持 - 劫持 HKCU\Software\Classes 下的 COM 接口
2. 自动提升的进程 - 利用系统自动提升权限的进程（如 mmc.exe、taskmgr.exe）
3. DLL 劫持 - 在高权限进程可写目录放置恶意 DLL
4. 环境变量劫持 - 修改环境变量指向恶意程序
5. 计划任务 - 通过任务计划程序以最高权限运行
6. COM 提升 - 利用 COM 对象的提升权限功能
```

**实际案例**：某 APT 组织使用 fodhelper.exe 绕过 UAC。fodhelper.exe 是 Windows 自带的"功能"程序，会自动提升权限。攻击者通过修改注册表 `HKCU\Software\Classes\ms-settings\shell\open\command`，将默认值设置为恶意程序路径，当 fodhelper.exe 启动时会执行该恶意程序并继承管理员权限。

### 1.2 地址空间随机化（ASLR）

**ASLR 概述**

地址空间布局随机化（Address Space Layout Randomization）是一种内存保护机制，通过随机化进程地址空间中关键区域的位置，使攻击者难以预测漏洞利用的目标地址。

**ASLR 随机化的区域**

- 可执行映像基地址（Image Base）
- 动态链接库加载地址
- 堆地址
- 栈地址
- PEB/TEB 地址
- 其他系统数据结构

**ASLR 配置注册表**

```
注册表路径：HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management
值名称：MoveImages
值类型：DWORD
- 0 = 禁用 ASLR
- 1 = 强制所有映像使用 ASLR（默认）
- -1 = 仅对有 IMAGE_DLLCHARACTERISTICS_DYNAMIC_BASE 标志的映像启用
```

**ASLR 绕过技术**

1. **信息泄露漏洞**：通过信息泄露漏洞获取已加载模块的基地址，计算出其他模块地址
2. **部分覆盖**：只覆盖返回地址的低 16 位或低 32 位，利用地址的部分可预测性
3. **NOP sled**：堆喷射结合 NOP 雪橇，增加命中概率
4. **暴力破解**：32 位系统地址空间有限，可暴力破解基地址
5. **返回导向编程（ROP）**：利用已加载模块中的 gadgets 构建攻击链

**实际案例**：MS17-010（永恒之蓝）漏洞利用中，攻击者通过信息泄露获取 NT 内核基地址和堆地址，然后利用这些已知地址构造 ROP 链绕过 ASLR 和 DEP 保护，最终执行任意代码。

### 1.3 数据执行保护（DEP/NX）

**DEP 概述**

数据执行保护（Data Execution Prevention）是一种安全机制，将内存页面标记为不可执行，防止攻击者在数据区域（如栈、堆）执行代码。在 Intel/AMD 处理器上称为 NX（No eXecute）位。

**DEP 工作模式**

| 模式 | 描述 |
|------|------|
| OptIn（默认） | 仅对 Windows 系统组件和选择加入的程序启用 DEP |
| OptOut | 对所有程序启用 DEP，排除列表中的程序除外 |
| AlwaysOn | 对所有程序强制启用 DEP |
| AlwaysOff | 完全禁用 DEP |

**查看 DEP 状态**

```powershell
# 查看系统 DEP 设置
Get-WmiObject -Class Win32_OperatingSystem | Select-Object DataExecutionPrevention_SupportPolicy

# 查看进程 DEP 状态
Get-Process | Select-Object Name, Id, @{Name="DEP";Expression={$_.StartInfo.EnvironmentVariables["_DEP"]}}
```

**DEP 绕过技术**

1. **返回导向编程（ROP）**：利用程序中已有的代码片段（gadgets）构建攻击链，通过 ret 指令串联执行
2. **返回至 libc**：跳转到系统库函数（如 system、WinExec）执行命令
3. **VirtualProtect/VirtualAlloc**：通过 ROP 调用 VirtualProtect 修改内存页属性为可执行，或调用 VirtualAlloc 分配可执行内存
4. **写文件 + 加载**：将 shellcode 写入文件，然后加载执行
5. **利用可执行内存区域**：寻找已存在的可执行内存区域进行写入

**ROP 示例原理**

```
传统攻击：
  栈溢出 → 覆盖返回地址 → 跳转到栈上的 shellcode → 执行（被 DEP 阻止）

ROP 攻击：
  栈溢出 → 覆盖返回地址 → 跳转到 gadget1 → 执行后 ret → 跳转到 gadget2 → ... → 最终调用 VirtualProtect → 修改内存属性 → 执行 shellcode
```

### 1.4 结构化异常处理覆盖保护（SEHOP）

**SEHOP 概述**

结构化异常处理覆盖保护（Structured Exception Handler Overwrite Protection）是一种针对 SEH 覆盖攻击的保护机制，在 Windows Vista SP1 和 Windows Server 2008 中引入。

**SEH 基础**

Windows 使用结构化异常处理（SEH）处理程序异常。每个线程都有一个 SEH 链，链中的每个节点包含异常处理函数地址。SEH 节点存储在栈上，因此栈溢出可能覆盖异常处理函数地址。

**SEHOP 工作原理**

- 在 SEH 链末尾添加一个特殊的异常处理程序（最终异常处理程序）
- 异常发生时，系统会遍历整个 SEH 链验证完整性
- 验证 SEH 记录是否在栈上、处理程序地址是否有效、链是否完整
- 如果验证失败，系统会终止进程

**SEHOP 绕过技术**

1. **部分覆盖（Partial Overwrite）**：只覆盖 SEH 处理程序地址的低字节，利用地址的低字节可预测性
2. **返回至 S.E.H. 链的下一个节点**：利用下一个 SEH 节点的处理程序
3. **堆喷 + 伪造 SEH 链**：在堆上伪造完整的 SEH 链
4. **利用 SafeSEH 未保护的模块**：没有 SafeSEH 保护的模块中的地址可用于覆盖

### 1.5 强制完整性控制（MIC）

**MIC 概述**

强制完整性控制（Mandatory Integrity Control）是 Windows Vista 引入的安全机制，通过为进程和安全对象（如文件、注册表项）分配完整性级别，防止低完整性进程访问高完整性对象。

**完整性级别**

| 级别 | 描述 | SID |
|------|------|-----|
| 不受信任（Untrusted） | 最低级别，用于匿名/来宾访问 | S-1-16-0 |
| 低（Low） | 用于 Internet Explorer 保护模式等 | S-1-16-4096 |
| 中（Medium） | 默认级别，普通用户进程 | S-1-16-8192 |
| 高（High） | 管理员提升权限的进程 | S-1-16-12288 |
| 系统（System） | 系统服务和内核 | S-1-16-16384 |
| 受保护进程（Protected） | 受保护的进程 | S-1-16-20480 |

**MIC 访问控制规则**

- 低完整性进程 **不能** 写入或修改中/高/系统完整性对象
- 低完整性进程 **可以** 读取高完整性对象（除非有额外限制）
- 低完整性进程 **不能** 向高完整性进程发送消息（UIPI）
- 高完整性进程可以访问低完整性对象

**查看完整性级别**

```powershell
# 查看进程完整性级别
Get-Process -Name explorer | ForEach-Object {
    $_.Handle | Out-Null
    Write-Host "$($_.Name): $($_.StartInfo.EnvironmentVariables['__COMPAT_LAYER'])"
}

# 使用 Sysinternals Process Explorer 查看更准确
# 或使用 accesschk /accepteula -p -f -v <pid>
```

**MIC 绕过与利用**

1. **令牌操纵**：修改进程令牌的完整性级别
2. **COM 提升**：利用某些可以跨完整性级别访问的 COM 对象
3. **计划任务**：通过任务计划程序创建高完整性任务
4. **服务利用**：利用以 SYSTEM 运行的服务进行权限提升

---

## 二、Windows 安全配置基线

### 2.1 账户策略

**密码策略**

| 策略 | 推荐值 | 说明 |
|------|--------|------|
| 密码必须符合复杂性要求 | 已启用 | 密码需包含大小写字母、数字、特殊字符中的3类 |
| 密码长度最小值 | 14个字符 | 越长越安全，NIST 建议至少8位，高安全环境14位以上 |
| 密码最短使用期限 | 1天 | 防止用户频繁更换密码绕过历史记录 |
| 密码最长使用期限 | 90天 | 定期更换密码 |
| 强制密码历史 | 24个记住的密码 | 防止重复使用旧密码 |
| 用可还原的加密来存储密码 | 已禁用 | 除非有特殊需求，否则必须禁用 |

**账户锁定策略**

| 策略 | 推荐值 | 说明 |
|------|--------|------|
| 账户锁定阈值 | 5次无效登录 | 防止暴力破解 |
| 账户锁定时间 | 30分钟 | 锁定后自动解锁时间 |
| 重置账户锁定计数器 | 30分钟 | 失败计数重置时间 |

**Kerberos 策略（域环境）**

| 策略 | 推荐值 | 说明 |
|------|--------|------|
| 强制用户登录限制 | 已启用 | 验证用户账户的登录权限 |
| 服务票证最长寿命 | 600分钟 | 服务票据有效期 |
| 用户票证最长寿命 | 10小时 | TGT 有效期 |
| 用户票证续订最长寿命 | 7天 | TGT 可续订期限 |
| 计算机账户密码最长使用期限 | 30天 | 域机器账户密码更换周期 |

**配置命令**

```powershell
# 使用本地安全策略命令行工具
secedit /export /cfg C:\temp\secpol.cfg

# 修改密码策略（在导出的配置文件中修改后导入）
# [System Access]
# MinimumPasswordAge = 1
# MaximumPasswordAge = 90
# MinimumPasswordLength = 14
# PasswordComplexity = 1
# PasswordHistorySize = 24
# LockoutBadCount = 5
# LockoutDuration = 30
# ResetLockoutCount = 30

secedit /configure /db C:\Windows\security\local.sdb /cfg C:\temp\secpol.cfg /areas SECURITYPOLICY
```

### 2.2 审核策略

**基本审核策略**

| 策略 | 推荐设置 | 说明 |
|------|----------|------|
| 审核账户登录事件 | 成功,失败 | 记录域控制器上的账户登录验证 |
| 审核账户管理 | 成功,失败 | 记录账户创建、修改、删除、密码更改等 |
| 审核目录服务访问 | 失败 | 记录 AD 对象访问（仅域控制器） |
| 审核登录事件 | 成功,失败 | 记录本地登录/注销事件 |
| 审核对象访问 | 失败 | 记录文件、注册表等对象访问 |
| 审核策略更改 | 成功,失败 | 记录安全策略更改 |
| 审核特权使用 | 失败 | 记录用户权限的使用 |
| 审核过程追踪 | 无 | 记录进程创建/终止（详细但日志量大） |
| 审核系统事件 | 成功,失败 | 记录系统启动/关机等事件 |

**高级审核策略（推荐）**

```
账户登录
├── 审核凭据验证 → 成功,失败
├── 审核 Kerberos 身份验证服务 → 成功,失败
├── 审核 Kerberos 服务票据操作 → 成功,失败
└── 审核其他账户登录事件 → 成功,失败

账户管理
├── 审核计算机账户管理 → 成功
├── 审核分发组管理 → 成功
├── 审核安全组管理 → 成功,失败
├── 审核其他账户管理事件 → 成功,失败
└── 审核用户账户管理 → 成功,失败

详细追踪
├── 审核进程创建 → 成功（含命令行）
├── 审核进程终止 → 成功
└── 审核 RPC 事件 → 无

登录/注销
├── 审核账户锁定 → 失败
├── 审核组成员身份 → 成功
├── 审核交互式登录 → 成功,失败
├── 审核网络策略服务器 → 成功,失败
├── 审核其他登录/注销事件 → 成功,失败
└── 审核特殊登录 → 成功,失败

对象访问
├── 审核文件系统 → 失败
├── 审核注册表 → 失败
├── 审核筛选平台连接 → 失败
└── 审核其他对象访问事件 → 失败

策略更改
├── 审核审核策略更改 → 成功,失败
├── 审核身份验证策略更改 → 成功
└── 审核授权策略更改 → 成功,失败

特权使用
├── 审核非敏感特权使用 → 无
├── 审核敏感特权使用 → 失败
└── 审核其他特权使用事件 → 失败

系统
├── 审核 IPsec 驱动程序 → 成功,失败
├── 审核其他系统事件 → 成功,失败
├── 审核安全状态更改 → 成功
└── 审核系统完整性 → 失败
```

**启用进程创建审核（含命令行）**

```powershell
# 启用进程创建审核
auditpol /set /subcategory:"Process Creation" /success:enable /failure:enable

# 启用命令行审计（注册表）
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\Audit" /v ProcessCreationIncludeCmdLine_Enabled /t REG_DWORD /d 1 /f

# 查看审核策略
auditpol /get /category:*
```

**重要事件 ID**

| 事件 ID | 描述 |
|---------|------|
| 4624 | 账户成功登录 |
| 4625 | 账户登录失败 |
| 4634 | 账户注销 |
| 4648 | 显式凭据登录（runas等） |
| 4672 | 管理员登录（特殊权限登录） |
| 4688 | 进程创建 |
| 4697 | 服务安装 |
| 4698 | 计划任务创建 |
| 4720 | 用户账户创建 |
| 4726 | 用户账户删除 |
| 4732 | 成员添加到本地组 |
| 4738 | 用户账户更改 |
| 4776 | NTLM 身份验证 |
| 7045 | 服务安装（System日志） |

### 2.3 防火墙配置

**Windows Defender 防火墙基本配置**

```powershell
# 启用防火墙（所有配置文件）
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True

# 设置默认入站策略为阻止
Set-NetFirewallProfile -Profile Domain,Public,Private -DefaultInboundAction Block

# 设置默认出站策略为允许（可根据需要改为阻止）
Set-NetFirewallProfile -Profile Domain,Public,Private -DefaultOutboundAction Allow

# 显示防火墙配置文件状态
Get-NetFirewallProfile | Select-Object Name, Enabled, DefaultInboundAction, DefaultOutboundAction
```

**常用入站规则配置**

```powershell
# 允许 ICMP（Ping）
New-NetFirewallRule -DisplayName "Allow ICMPv4-In" -Protocol ICMPv4 -IcmpType 8 -Direction Inbound -Action Allow -Enabled True

# 允许 RDP（仅指定 IP 段）
New-NetFirewallRule -DisplayName "Allow RDP from Internal" -Direction Inbound -Protocol TCP -LocalPort 3389 -RemoteAddress 192.168.1.0/24 -Action Allow -Enabled True

# 允许 SSH
New-NetFirewallRule -DisplayName "Allow SSH-In" -Direction Inbound -Protocol TCP -LocalPort 22 -Action Allow -Enabled True

# 阻止特定端口
New-NetFirewallRule -DisplayName "Block Telnet" -Direction Inbound -Protocol TCP -LocalPort 23 -Action Block -Enabled True
```

**常用出站规则配置**

```powershell
# 阻止 SMB 出站（防止横向移动）
New-NetFirewallRule -DisplayName "Block SMB Outbound" -Direction Outbound -Protocol TCP -RemotePort 445 -Action Block -Enabled True

# 阻止远程 PowerShell 出站
New-NetFirewallRule -DisplayName "Block WinRM Outbound" -Direction Outbound -Protocol TCP -RemotePort 5985,5986 -Action Block -Enabled True
```

**加固建议**

1. 启用所有配置文件的防火墙
2. 默认入站策略设置为"阻止"
3. 仅开放必要的端口，遵循最小权限原则
4. 限制远程管理端口（RDP、WinRM、SSH）的源地址
5. 考虑启用出站过滤（白名单模式）
6. 定期审查防火墙规则，清理不必要的规则

---

## 三、Windows 常见漏洞类型

### 3.1 缓冲区溢出

**原理**

缓冲区溢出是指程序向缓冲区写入数据时超出了缓冲区的大小，导致覆盖了相邻的内存区域。攻击者可以利用这种漏洞覆盖函数返回地址，从而控制程序执行流程。

**栈溢出示例（C 代码）**

```c
#include <stdio.h>
#include <string.h>

void vulnerable_function(char *input) {
    char buffer[64];  // 64字节缓冲区
    strcpy(buffer, input);  // 不安全的字符串复制，无长度检查
}

int main(int argc, char *argv[]) {
    if (argc > 1) {
        vulnerable_function(argv[1]);
    }
    return 0;
}
```

**漏洞分析**

- `strcpy` 函数不检查目标缓冲区大小
- 当输入超过 64 字节时，会覆盖栈上的返回地址
- 攻击者可以构造特定输入，将返回地址指向 shellcode

**内存布局（栈）**

```
高地址
┌───────────────┐
│   返回地址    │  ← 被覆盖
├───────────────┤
│   旧的 EBP    │  ← 可能被覆盖
├───────────────┤
│               │
│   buffer[64]  │  ← 用户输入写入这里
│               │
└───────────────┘
低地址
```

**防护措施**

- 使用安全的字符串函数（`strncpy`、`strlcpy`、`snprintf`）
- 启用编译器安全选项（/GS 栈保护、ASLR、DEP）
- 代码审计和静态分析
- 使用现代编程语言（Rust、Go 等内存安全语言）

**实际案例**：MS08-067 是 Windows Server 服务中的一个经典缓冲区溢出漏洞。攻击者通过向 `NetprPathCanonicalize` 函数发送精心构造的请求，触发栈溢出，从而以 SYSTEM 权限执行任意代码。该漏洞被 Conficker 蠕虫大规模利用。

### 3.2 释放后使用（UAF）

**原理**

释放后使用（Use-After-Free）是指程序在释放内存后仍然使用指向该内存的指针。如果攻击者能够在内存释放后重新分配该内存块并控制其内容，就可以实现任意代码执行。

**UAF 示例（C 代码）**

```c
#include <stdio.h>
#include <stdlib.h>

typedef struct {
    void (*callback)(void);
    int data;
} Object;

Object *global_obj;

void init_object() {
    global_obj = (Object *)malloc(sizeof(Object));
    global_obj->callback = NULL;
    global_obj->data = 0;
}

void free_object() {
    free(global_obj);  // 释放内存
    // 注意：没有将 global_obj 置为 NULL
}

void use_object() {
    if (global_obj->callback) {  // 释放后仍使用指针
        global_obj->callback();  // 调用虚函数/回调
    }
}

int main() {
    init_object();
    free_object();  // 释放对象
    // ... 攻击者在此期间分配内存覆盖 global_obj 指向的区域
    use_object();   // 触发 UAF
    return 0;
}
```

**漏洞分析**

- `free_object` 释放了 `global_obj` 指向的内存
- 但没有将指针置为 NULL
- `use_object` 仍然使用该指针
- 如果攻击者能在释放和使用之间重新分配并控制该内存，就可以控制 `callback` 函数指针

**UAF 利用步骤**

1. 创建一个包含虚函数指针的对象
2. 释放该对象（但指针未置空）
3. 攻击者分配相同大小的内存，覆盖虚函数指针
4. 程序调用虚函数时，执行攻击者控制的代码

**防护措施**

- 释放内存后将指针置为 NULL
- 使用智能指针（C++ shared_ptr/unique_ptr）
- 使用内存安全语言
- 启用堆保护机制（Heap Cookie、DEP、ASLR）

**实际案例**：CVE-2021-31956 是 Windows 内核中的一个 UAF 漏洞，存在于 win32k.sys 驱动中。攻击者可以通过创建和操作特定的窗口对象触发 UAF，从而实现本地权限提升。该漏洞在野被积极利用。

### 3.3 整数溢出

**原理**

整数溢出是指当算术运算的结果超出了整数类型所能表示的范围时发生的溢出。这可能导致意外的行为，例如分配过少的内存，进而导致缓冲区溢出。

**整数溢出示例（C 代码）**

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void vulnerable_copy(int count, char *input) {
    // 整数溢出：count * sizeof(int) 可能溢出
    int size = count * sizeof(int);
    int *buffer = (int *)malloc(size);
    
    if (buffer == NULL) return;
    
    // 实际复制 count * sizeof(int) 字节到 buffer
    // 如果 size 溢出（变成很小的数），malloc 分配的内存不够
    memcpy(buffer, input, count * sizeof(int));
    
    free(buffer);
}

int main() {
    // count = 0x40000001 (1073741825)
    // count * 4 = 0x100000004 → 32位溢出后为 4
    // malloc(4) 只分配4字节，但 memcpy 复制大量数据 → 堆溢出
    return 0;
}
```

**整数溢出类型**

1. **有符号整数溢出**：有符号整数超出表示范围（undefined behavior）
2. **无符号整数回绕**：无符号整数超出表示范围（定义为模运算）
3. **截断**：将大整数赋值给小整数类型
4. **符号扩展**：有符号整数向更宽类型转换时符号位扩展

**整数溢出检测**

```c
// 安全的整数加法检查
int safe_add(int a, int b, int *result) {
    if ((b > 0 && a > INT_MAX - b) ||
        (b < 0 && a < INT_MIN - b)) {
        return -1;  // 溢出
    }
    *result = a + b;
    return 0;
}

// 安全的整数乘法检查
int safe_mul(int a, int b, int *result) {
    if (a == 0 || b == 0) {
        *result = 0;
        return 0;
    }
    if (a > 0) {
        if (b > 0) {
            if (a > INT_MAX / b) return -1;
        } else {
            if (b < INT_MIN / a) return -1;
        }
    } else {
        if (b > 0) {
            if (a < INT_MIN / b) return -1;
        } else {
            if (b != 0 && a < INT_MAX / b) return -1;
        }
    }
    *result = a * b;
    return 0;
}
```

**防护措施**

- 在进行算术运算前检查边界
- 使用安全整数库（如 SafeInt）
- 编译器警告和静态分析
- 代码审计

---

## 四、Windows 提权方法

### 4.1 内核漏洞提权

**原理**

内核漏洞是指操作系统内核中的漏洞，利用这些漏洞可以从用户态提升到内核态（SYSTEM 权限）。内核漏洞通常是最严重的本地提权漏洞。

**常见内核漏洞类型**

1. **缓冲区溢出**：内核驱动中的栈/堆溢出
2. **释放后使用（UAF）**：内核对象释放后使用
3. **竞态条件**：内核中的 TOCTOU 漏洞
4. **类型混淆**：内核对象类型混淆
5. **整数溢出**：内核中的整数溢出导致缓冲区溢出

**著名内核提权漏洞**

| 漏洞编号 | 影响系统 | 类型 | 描述 |
|----------|----------|------|------|
| MS15-051 | Windows 7/8/2008/2012 | 内核漏洞 | win32k.sys 中的漏洞 |
| MS16-032 | Windows 7-10/2008-2012 | 内核漏洞 | Secondary Logon 服务漏洞 |
| CVE-2018-8120 | Windows 7/2008 | 内核漏洞 | win32k.sys 空指针解引用 |
| CVE-2019-1458 | Windows 7-10/2008-2019 | 内核漏洞 | win32k.sys UAF |
| CVE-2021-31956 | Windows 10/Server | 内核漏洞 | win32k.sys UAF |
| CVE-2023-32019 | Windows 10-11/Server | 内核漏洞 | 内核信息泄露 + 提权 |

**提权检测工具**

```powershell
# Windows Exploit Suggester - Next Generation
# https://github.com/bitsadmin/wesng

# 使用 systeminfo 收集系统信息
systeminfo > systeminfo.txt

# 使用 wes.py 检测缺失补丁
python wes.py systeminfo.txt

# PowerShell 版本的提权检测
# Sherlock - https://github.com/rasta-mouse/Sherlock
Import-Module Sherlock.ps1
Find-AllVulns

# WinPEAS - 全面的提权枚举
# https://github.com/carlospolop/PEASS-ng
```

**提权利用示例（MS16-032）**

```powershell
# MS16-032 利用示例（Invoke-MS16032）
# 该漏洞存在于 Secondary Logon 服务中
# 当进程以受限令牌运行时，可以利用此漏洞提升到 SYSTEM

# 加载 PowerShell 模块
Import-Module .\Invoke-MS16032.ps1

# 执行提权，以 SYSTEM 运行命令
Invoke-MS16032 -Command "cmd.exe /c whoami > C:\temp\result.txt"
```

### 4.2 服务权限配置错误

**原理**

Windows 服务通常以 SYSTEM 或高权限账户运行。如果服务的可执行文件路径、服务配置或注册表权限配置不当，普通用户可能可以修改服务配置，从而以高权限执行代码。

**常见服务提权场景**

**场景1：服务可执行文件路径可写**

```
如果服务的可执行文件（.exe）所在目录或文件本身可被普通用户写入：
1. 替换服务可执行文件为恶意程序
2. 重启服务（或等待系统重启）
3. 恶意程序以服务账户权限（通常是 SYSTEM）运行
```

**场景2：服务路径未加引号（Unquoted Service Path）**

```
服务路径示例：
C:\Program Files\My Service\service.exe

如果路径没有引号，Windows 会按以下顺序查找可执行文件：
1. C:\Program.exe
2. C:\Program Files\My.exe
3. C:\Program Files\My Service\service.exe

如果攻击者能在 C:\ 根目录写入 Program.exe，服务启动时会执行该文件。
```

**检测方法**

```powershell
# 检测未加引号的服务路径
Get-WmiObject -Class Win32_Service | 
    Where-Object { $_.PathName -notlike '"*' -and $_.PathName -like "* *" } | 
    Select-Object Name, PathName, StartName

# 使用 wmic 命令
wmic service get name,pathname,startname | findstr /i /v """ | findstr /i " "

# 检测可写的服务目录
# 使用 accesschk（Sysinternals）
accesschk.exe /accepteula -uwcqv "Authenticated Users" *
accesschk.exe /accepteula -uwdq "C:\Program Files\"
```

**场景3：服务配置可修改**

```
如果普通用户有权修改服务配置（如 ChangeConfig 权限）：
1. 修改服务的 binPath 指向恶意程序
2. 修改服务的启动类型为自动
3. 重启服务或等待重启
```

**利用示例**

```powershell
# 检查当前用户对服务的权限
sc sdshow <ServiceName>

# 修改服务可执行路径（需要权限）
sc config <ServiceName> binPath= "C:\temp\malware.exe"

# 重启服务
sc stop <ServiceName>
sc start <ServiceName>
```

### 4.3 注册表权限配置错误

**原理**

注册表存储了 Windows 系统和应用程序的大量配置信息。如果某些注册表键的权限配置不当，普通用户可能可以修改敏感配置，从而实现权限提升。

**常见注册表提权场景**

**场景1：服务注册表键可写**

```
服务配置存储在：HKLM\SYSTEM\CurrentControlSet\Services\<ServiceName>
如果该键对普通用户可写，可以：
1. 修改 ImagePath 值指向恶意程序
2. 修改 Type 改变服务类型
3. 重启服务后以 SYSTEM 执行代码
```

**场景2：启动项注册表键可写**

```
常见启动项位置：
- HKLM\Software\Microsoft\Windows\CurrentVersion\Run
- HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce
- HKCU\Software\Microsoft\Windows\CurrentVersion\Run（当前用户权限）

如果 HKLM 下的启动项键可写，添加的程序会在用户登录时以用户权限执行。
如果添加的程序在管理员登录时执行，则获得管理员权限。
```

**场景3：映像劫持（IFEO）**

```
注册表位置：HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\

如果可以在此键下创建子键，可以设置 Debugger 值：
当目标程序启动时，会先启动 Debugger 指定的程序
如果目标程序以高权限运行，则 Debugger 程序继承高权限
```

**检测方法**

```powershell
# 检查可写的注册表键
# 使用 accesschk
accesschk.exe /accepteula -kvu "Authenticated Users" "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
accesschk.exe /accepteula -kvu "Authenticated Users" "HKLM\SYSTEM\CurrentControlSet\Services"

# PowerShell 检查注册表权限
Get-Acl "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" | 
    Select-Object -ExpandProperty Access |
    Where-Object { $_.IdentityReference -match "Users|Authenticated Users" -and $_.RegistryRights -match "Write|FullControl" }
```

### 4.4 计划任务提权

**原理**

计划任务（Scheduled Tasks）是 Windows 的定时执行功能。如果计划任务配置不当，普通用户可能可以利用计划任务提升权限。

**常见计划任务提权场景**

**场景1：任务可执行文件可写**

```
如果计划任务执行的程序或脚本可被普通用户修改：
1. 替换任务执行的脚本/程序
2. 等待任务触发执行
3. 以任务配置的账户权限执行代码
```

**场景2：任务可被修改**

```
如果普通用户有修改计划任务的权限：
1. 修改任务的执行程序或参数
2. 修改任务的运行账户
3. 手动触发任务执行
```

**检测方法**

```powershell
# 列出所有计划任务
Get-ScheduledTask | Select-Object TaskName, TaskPath, State, Author

# 查看任务详情（包括执行的操作和运行账户）
Get-ScheduledTask -TaskName "<TaskName>" | Get-ScheduledTaskInfo
Get-ScheduledTask -TaskName "<TaskName>" | Select-Object -ExpandProperty Actions

# 使用 schtasks 命令
schtasks /query /fo LIST /v

# 检查任务文件权限
# 任务文件存储在：C:\Windows\System32\Tasks\
Get-Acl "C:\Windows\System32\Tasks\<TaskName>"
```

**利用示例**

```powershell
# 检查任务操作和运行账户
$task = Get-ScheduledTask -TaskName "VulnerableTask"
$task.Actions  # 查看执行的程序
$task.Principal.UserId  # 查看运行账户

# 修改任务（需要权限）
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c whoami > C:\temp\result.txt"
Set-ScheduledTask -TaskName "VulnerableTask" -Action $action

# 立即运行任务
Start-ScheduledTask -TaskName "VulnerableTask"
```

### 4.5 令牌窃取与 AlwaysInstallElevated

**令牌窃取**

```
令牌窃取（Token Stealing）是指获取高权限进程的访问令牌，
然后用该令牌创建新进程，从而继承高权限。

常见场景：
1. SeDebugPrivilege 权限 - 可以调试任何进程，窃取其令牌
2. SeImpersonatePrivilege 权限 - 可以模拟客户端令牌
3. 服务账户权限 - 服务账户常具有这些特权
```

**Juicy Potato / PrintSpoofer 提权**

```
利用 SeImpersonatePrivilege 权限的提权工具：
- Juicy Potato：通过 COM 对象模拟 SYSTEM 令牌
- PrintSpoofer：利用打印后台处理程序服务的命名管道模拟 SYSTEM

使用条件：
- 当前账户具有 SeImpersonatePrivilege 或 SeAssignPrimaryTokenPrivilege
- 常见于 IIS APPPOOL、服务账户等

示例：
PrintSpoofer.exe -i -c cmd.exe
# 以 SYSTEM 权限启动 cmd.exe
```

**AlwaysInstallElevated 提权**

```
如果以下两个注册表键都设置为 1：
- HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer\AlwaysInstallElevated
- HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer\AlwaysInstallElevated

则任何用户都可以以 SYSTEM 权限安装 MSI 包。

检测：
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated

利用：
1. 使用 msfvenom 生成恶意 MSI
2. msiexec /quiet /qn /i malicious.msi
```

---

## 五、Windows 横向移动

### 5.1 SMB 横向移动

**SMB 协议概述**

SMB（Server Message Block）是 Windows 文件共享和打印共享的协议，使用端口 445（TCP）。SMB 是横向移动中最常用的协议之一。

**SMB 信息收集**

```powershell
# 探测主机的 SMB 共享
net view \\<target>
net use \\<target>\ipc$ "" /user:""  # 空会话

# 使用 PowerShell
Get-SmbShare -CimSession <target>

# 列出共享文件
dir \\<target>\share
```

**SMB 凭据传递（Pass-the-Hash）**

```
Pass-the-Hash (PtH) 是一种攻击技术，攻击者使用用户的 NTLM 哈希
而不是明文密码进行身份验证。

工具：
- Mimikatz：提取内存中的哈希
- CrackMapExec：SMB 横向移动工具
- Impacket：psexec、smbexec 等

示例（Mimikatz 提取哈希）：
privilege::debug
sekurlsa::logonpasswords

示例（psexec 横向移动）：
psexec.py administrator:password@target_ip cmd.exe
psexec.py -hashes aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0 administrator@target_ip cmd.exe
```

**SMB 远程执行**

| 技术 | 说明 | 需要权限 |
|------|------|----------|
| PsExec | 通过服务执行命令 | 管理员权限 |
| WMI 执行 | 通过 WMI 执行命令 | 管理员权限 |
| SCM 服务执行 | 通过服务控制管理器 | 管理员权限 |
| DCOM 执行 | 通过 DCOM 执行 |  varying |
| 计划任务 | 通过计划任务执行 |  varying |

**CrackMapExec 使用示例**

```bash
# 检测 SMB 签名
crackmapexec smb 192.168.1.0/24

# 密码喷洒
crackmapexec smb 192.168.1.0/24 -u user -p 'Password123'

# 哈希传递
crackmapexec smb 192.168.1.10 -u administrator -H 'aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0'

# 执行命令
crackmapexec smb 192.168.1.10 -u admin -p 'pass' -x 'whoami'

# 转储 SAM 哈希
crackmapexec smb 192.168.1.10 -u admin -p 'pass' --sam
```

### 5.2 WMI 横向移动

**WMI 概述**

WMI（Windows Management Instrumentation）是 Windows 的管理基础设施，提供了统一的方式来管理 Windows 系统。WMI 使用端口 135（DCOM）和动态端口（1024-65535）。

**WMI 信息收集**

```powershell
# 远程获取系统信息
Get-WmiObject -Class Win32_OperatingSystem -ComputerName <target>
Get-CimInstance -ClassName Win32_OperatingSystem -ComputerName <target>

# 获取进程列表
Get-WmiObject -Class Win32_Process -ComputerName <target>

# 获取服务列表
Get-WmiObject -Class Win32_Service -ComputerName <target>

# 获取已安装软件
Get-WmiObject -Class Win32_Product -ComputerName <target>
```

**WMI 远程命令执行**

```powershell
# 使用 wmic 执行命令
wmic /node:<target> /user:<user> /password:<pass> process call create "cmd.exe /c whoami > C:\temp\out.txt"

# 使用 PowerShell
$username = "domain\user"
$password = ConvertTo-SecureString "password" -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential($username, $password)

Invoke-WmiMethod -Class Win32_Process -Name Create -ArgumentList "cmd.exe /c whoami" -ComputerName <target> -Credential $cred

# 使用 CIM
Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine="cmd.exe /c whoami"} -ComputerName <target> -Credential $cred
```

**WMI 横向移动检测**

```
检测 WMI 横向移动的指标：
1. 事件 ID 4688：wmic.exe 或 wmiprvse.exe 进程创建
2. 事件 ID 5140：网络共享访问（WMI 可能通过 ADMIN$ 共享）
3. 端口 135 和动态端口的异常连接
4. WMI 活动日志：Microsoft-Windows-WMI-Activity/Operational
   - 事件 ID 5857：WMI 提供程序加载
   - 事件 ID 5858：WMI 操作失败
   - 事件 ID 5859：WMI 事件消费者注册
```

### 5.3 WinRM 横向移动

**WinRM 概述**

WinRM（Windows Remote Management）是 Microsoft 实现的 WS-Management 协议，用于远程管理 Windows 系统。使用端口 5985（HTTP）和 5986（HTTPS）。

**WinRM 远程命令执行**

```powershell
# 启用 WinRM（目标端）
Enable-PSRemoting -Force

# 远程 PowerShell 会话
Enter-PSSession -ComputerName <target> -Credential <cred>

# 远程执行命令
Invoke-Command -ComputerName <target> -ScriptBlock { whoami } -Credential <cred>

# 远程执行脚本
Invoke-Command -ComputerName <target> -FilePath C:\script.ps1 -Credential <cred>

# 使用 IP 地址（需要将 IP 添加到受信任主机）
Set-Item WSMan:\localhost\Client\TrustedHosts -Value "192.168.1.100" -Force
Enter-PSSession -ComputerName 192.168.1.100 -Credential <cred>
```

**WinRM 检测与防护**

```
检测指标：
1. 端口 5985/5986 的异常连接
2. PowerShell 事件日志中的远程命令执行
3. 事件 ID 4688：wsmprovhost.exe 进程创建
4. WinRM 事件日志：Microsoft-Windows-WinRM/Operational

防护措施：
1. 限制 WinRM 访问的源地址（防火墙规则）
2. 使用 HTTPS（5986）传输，启用证书认证
3. 限制具有 WinRM 访问权限的账户
4. 监控 WinRM 活动日志
5. 启用 PowerShell 模块日志和脚本块日志
```

**Evil-WinRM 使用示例**

```bash
# 使用密码连接
evil-winrm -i <target_ip> -u <username> -p <password>

# 使用哈希连接（Pass-the-Hash）
evil-winrm -i <target_ip> -u <username> -H <ntlm_hash>

# 使用 SSL 连接
evil-winrm -i <target_ip> -u <username> -p <password> -S

# 上传/下载文件
upload local_file.txt
download remote_file.txt
```

### 5.4 RDP 横向移动

**RDP 概述**

RDP（Remote Desktop Protocol）是 Windows 远程桌面协议，使用端口 3389（TCP/UDP）。RDP 是最常见的远程管理方式，也是攻击者横向移动的重要途径。

**RDP 信息收集**

```powershell
# 检测 RDP 是否启用
Get-ItemProperty "HKLM:\System\CurrentControlSet\Control\Terminal Server" -Name fDenyTSConnections

# 检测 RDP 端口
Get-ItemProperty "HKLM:\System\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" -Name PortNumber

# 检测 NLA（网络级别身份验证）
Get-ItemProperty "HKLM:\System\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" -Name UserAuthentication

# 查看 RDP 会话
qwinsta /server:<target>
query session /server:<target>
```

**RDP 攻击方法**

1. **密码喷洒/暴力破解**：使用已知用户名列表和常见密码尝试登录
2. **Pass-the-Hash**：使用 NTLM 哈希进行 RDP 认证（Restricted Admin 模式）
3. **RDP 会话劫持**：劫持已登录用户的 RDP 会话
4. **BlueKeep 漏洞**：CVE-2019-0708，RDP 远程代码执行漏洞

**RDP 会话劫持**

```powershell
# 查看当前会话
query user

# 劫持会话（需要 SYSTEM 权限）
# 连接到另一个用户的会话
tscon <session_id> /dest:<current_session_name>

# 示例：从 SYSTEM 会话切换到管理员会话
tscon 2 /dest:console
```

**RDP 防护措施**

1. 使用强密码和账户锁定策略
2. 启用网络级别身份验证（NLA）
3. 限制 RDP 访问的源地址（防火墙）
4. 更改默认 RDP 端口（安全性有限，主要减少噪音）
5. 配置 RDP 证书（TLS 加密）
6. 监控 RDP 登录事件（事件 ID 4624、4625、4634）
7. 使用 VPN 或 RD Gateway 进行远程访问
8. 启用受限管理模式（防止凭据盗窃）

---

## 六、Windows 权限维持

### 6.1 注册表持久化

**启动项注册表键**

```
用户级启动项（当前用户权限）：
HKCU\Software\Microsoft\Windows\CurrentVersion\Run
HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce
HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnceEx

系统级启动项（SYSTEM/管理员权限，取决于触发时机）：
HKLM\Software\Microsoft\Windows\CurrentVersion\Run
HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce
HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnceEx
HKLM\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer\Run

其他启动位置：
HKLM\Software\Microsoft\Windows NT\CurrentVersion\Winlogon\Userinit
HKLM\Software\Microsoft\Windows NT\CurrentVersion\Winlogon\Shell
HKLM\Software\Microsoft\Windows NT\CurrentVersion\Windows\AppInit_DLLs
```

**示例**

```powershell
# 添加启动项
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "MaliciousUpdate" /t REG_SZ /d "C:\temp\malware.exe" /f

# 添加到 RunOnce（运行一次后自动删除）
reg add "HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce" /v "Update" /t REG_SZ /d "C:\temp\malware.exe" /f
```

**映像劫持（IFEO）**

```
注册表位置：
HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\<exe_name>

设置 Debugger 值后，当目标程序启动时，会先启动 Debugger 指定的程序。
Debugger 程序接收目标程序路径作为命令行参数。

示例：
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\notepad.exe" /v Debugger /t REG_SZ /d "C:\temp\malware.exe" /f

当用户启动 notepad.exe 时，实际上会运行 malware.exe
```

### 6.2 服务持久化

**服务持久化原理**

Windows 服务在系统启动时自动运行，通常以 SYSTEM 权限运行。创建新服务或修改现有服务是常见的持久化方法。

**创建服务**

```powershell
# 使用 sc 命令创建服务
sc create "UpdateService" binPath= "C:\temp\malware.exe" start= auto type= own
sc description "UpdateService" "Windows Update Service"
sc start "UpdateService"

# 使用 PowerShell 创建服务
New-Service -Name "UpdateService" -BinaryPathName "C:\temp\malware.exe" -StartupType Automatic -Description "Windows Update Service"
Start-Service -Name "UpdateService"
```

**服务持久化检测**

```powershell
# 列出所有服务
Get-Service | Select-Object Name, DisplayName, Status, StartType

# 列出自动启动的服务
Get-Service | Where-Object { $_.StartType -eq "Automatic" }

# 查看服务详情
Get-WmiObject -Class Win32_Service | Select-Object Name, PathName, StartName, StartMode

# 查看非 Microsoft 的服务
Get-WmiObject -Class Win32_Service | Where-Object { $_.PathName -notlike "*C:\Windows*" } | Select-Object Name, PathName, StartName

# 事件日志
# 事件 ID 4697：服务安装（安全日志）
# 事件 ID 7045：服务安装（系统日志）
```

### 6.3 计划任务持久化

**计划任务持久化原理**

计划任务可以配置为在特定时间、特定事件或系统启动时执行程序。计划任务可以配置运行账户，支持以 SYSTEM 权限运行。

**创建计划任务**

```powershell
# 使用 schtasks 创建任务
schtasks /create /tn "WindowsUpdate" /tr "C:\temp\malware.exe" /sc onstart /ru SYSTEM /f

# 使用 PowerShell 创建任务
$action = New-ScheduledTaskAction -Execute "C:\temp\malware.exe"
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -Hidden -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName "WindowsUpdate" -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description "Windows Automatic Update"
```

**计划任务检测**

```powershell
# 列出所有计划任务
Get-ScheduledTask | Select-Object TaskName, TaskPath, State

# 查看任务详情
Get-ScheduledTask | ForEach-Object {
    [PSCustomObject]@{
        TaskName = $_.TaskName
        Execute = ($_.Actions | Select-Object -ExpandProperty Execute)
        Arguments = ($_.Actions | Select-Object -ExpandProperty Arguments)
        UserId = $_.Principal.UserId
        RunLevel = $_.Principal.RunLevel
        Triggers = ($_.Triggers | ForEach-Object { $_.StartBoundary + " " + $_.Enabled })
    }
}

# 检测可疑任务
# 1. 以 SYSTEM 运行的自定义任务
# 2. 执行路径在临时目录的任务
# 3. 隐藏的任务
```

### 6.4 WMI 事件订阅持久化

**WMI 持久化原理**

WMI 事件订阅可以在特定系统事件发生时触发脚本或命令执行。WMI 持久化具有隐蔽性强、无文件（存储在 WMI 仓库中）等特点。

**WMI 持久化组件**

1. **事件过滤器（EventFilter）**：定义触发条件（什么事件）
2. **事件消费者（EventConsumer）**：定义触发后执行的操作
3. **过滤器消费者绑定（FilterToConsumerBinding）**：将过滤器和消费者关联

**常见事件触发器**

- 系统启动（__InstanceModificationEvent 监控 Win32_OperatingSystem）
- 用户登录（__InstanceCreationEvent 监控 Win32_LogonSession）
- 定时触发（__TimerEvent）
- 进程创建（__InstanceCreationEvent 监控 Win32_Process）

**WMI 持久化示例**

```powershell
# 创建事件过滤器（系统启动后触发）
$filter = ([wmiclass]"root\subscription:__EventFilter").CreateInstance()
$filter.Name = "WindowsUpdateFilter"
$filter.Query = "SELECT * FROM __InstanceModificationEvent WITHIN 60 WHERE TargetInstance ISA 'Win32_PerfFormattedData_PerfOS_System'"
$filter.QueryLanguage = "WQL"
$filter.EventNamespace = "root\cimv2"
$filter.Put()

# 创建事件消费者（执行命令）
$consumer = ([wmiclass]"root\subscription:CommandLineEventConsumer").CreateInstance()
$consumer.Name = "WindowsUpdateConsumer"
$consumer.CommandLineTemplate = "cmd.exe /c C:\temp\malware.exe"
$consumer.Put()

# 创建绑定
$binding = ([wmiclass]"root\subscription:__FilterToConsumerBinding").CreateInstance()
$binding.Filter = "__EventFilter.Name='WindowsUpdateFilter'"
$binding.Consumer = "CommandLineEventConsumer.Name='WindowsUpdateConsumer'"
$binding.Put()
```

**WMI 持久化检测**

```powershell
# 列出所有事件过滤器
Get-WmiObject -Namespace root\subscription -Class __EventFilter | Select-Object Name, Query

# 列出所有事件消费者
Get-WmiObject -Namespace root\subscription -Class __EventConsumer | Select-Object Name, __CLASS

# 列出所有绑定
Get-WmiObject -Namespace root\subscription -Class __FilterToConsumerBinding | Select-Object Filter, Consumer

# 使用 Autoruns 检测
# autorunsc.exe -a wmi  # 列出 WMI 持久化
```

---

## 七、Windows 恶意代码分析基础

### 7.1 PE 文件结构

**PE 文件概述**

PE（Portable Executable）是 Windows 平台的可执行文件格式，包括 .exe、.dll、.sys、.ocx 等。理解 PE 文件结构是恶意代码分析的基础。

**PE 文件结构**

```
┌─────────────────────┐
│    DOS Header       │  ← MZ 签名
├─────────────────────┤
│    DOS Stub         │  ← DOS 下的小程序（通常显示"This program cannot be run in DOS mode"）
├─────────────────────┤
│    NT Header        │  ← PE\0\0 签名 + File Header + Optional Header
│  ├─ Signature       │
│  ├─ File Header     │  ← 机器类型、节数量、时间戳等
│  └─ Optional Header │  ← 入口点、映像基地址、节对齐、数据目录等
├─────────────────────┤
│   Section Table     │  ← 节表，每个节的描述信息
├─────────────────────┤
│     .text 节        │  ← 代码节，存储可执行代码
├─────────────────────┤
│     .data 节        │  ← 数据节，存储初始化的全局变量
├─────────────────────┤
│     .rdata 节       │  ← 只读数据，包括导入表、导出表
├─────────────────────┤
│     .rsrc 节        │  ← 资源节，图标、菜单、对话框等
├─────────────────────┤
│     .reloc 节       │  ← 重定位节
└─────────────────────┘
```

**重要的数据目录**

| 目录 | 说明 |
|------|------|
| Export Table | 导出表，列出该文件导出的函数 |
| Import Table | 导入表，列出该文件导入的函数 |
| Resource Table | 资源表，图标、菜单、字符串等 |
| Exception Table | 异常表，SEH 处理信息 |
| Base Relocation Table | 基址重定位表 |
| TLS Table | 线程局部存储表 |
| Import Address Table | 导入地址表 |
| Delay Import Table | 延迟导入表 |
| COM Descriptor | CLR/.NET 描述符 |

**PE 分析工具**

- CFF Explorer：PE 文件编辑器和分析工具
- PEview：PE 文件结构查看器
- IDA Pro / Ghidra：反汇编和反编译
- x64dbg：动态调试

### 7.2 导入表分析

**导入表的作用**

导入表记录了程序需要从其他 DLL 中导入的函数。分析导入表可以了解程序的功能和行为。

**常见可疑导入函数**

**进程/线程相关**
```
CreateProcess / CreateRemoteThread  → 创建进程/远程线程
OpenProcess / VirtualAllocEx        → 进程注入相关
WriteProcessMemory / ReadProcessMemory → 进程内存读写
CreateThread / QueueUserAPC        → 线程创建/APC 注入
```

**文件操作相关**
```
CreateFile / WriteFile             → 文件创建和写入
FindFirstFile / FindNextFile       → 文件遍历
CopyFile / MoveFile                → 文件复制/移动
DeleteFile                         → 文件删除
```

**注册表相关**
```
RegOpenKeyEx / RegSetValueEx       → 注册表打开/写入
RegCreateKeyEx / RegDeleteKey      → 注册表创建/删除
RegQueryValueEx                    → 注册表查询
```

**网络相关**
```
WSAStartup / socket / connect      → Winsock 初始化/连接
send / recv                        → 网络数据收发
InternetOpen / InternetOpenUrl     → WinINet HTTP 访问
HttpOpenRequest / HttpSendRequest  → HTTP 请求
```

**调试/反调试相关**
```
IsDebuggerPresent                  → 检测调试器
CheckRemoteDebuggerPresent         → 远程调试器检测
OutputDebugString                  → 调试输出
GetTickCount / QueryPerformanceCounter → 时间检测
```

### 7.3 恶意代码常见行为

**持久化行为**

1. 创建注册表启动项
2. 创建系统服务
3. 创建计划任务
4. 修改系统配置
5. 注入到系统进程

**信息窃取行为**

1. 读取浏览器密码和 Cookie
2. 记录键盘输入（键盘记录器）
3. 截取屏幕截图
4. 读取剪贴板内容
5. 窃取文件和文档

**网络行为**

1. 连接 C2 服务器
2. 下载后续 payload
3. 上传窃取的数据
4. 端口扫描
5. 横向移动

**对抗分析行为**

1. 检测调试器
2. 检测虚拟机
3. 检测沙箱
4. 加密/混淆代码
5. 延迟执行

### 7.4 加壳与脱壳

**常见加壳器**

| 加壳器 | 类型 | 说明 |
|--------|------|------|
| UPX | 压缩壳 | 开源，最常见的压缩壳 |
| ASProtect | 加密壳 | 带有反调试、反分析功能 |
| Themida/VMProtect | 虚拟化壳 | 代码虚拟化，强度很高 |
| Enigma Protector | 加密壳 | 功能丰富的保护工具 |
| PECompact | 压缩壳 | 压缩+一些保护功能 |
| MPRESS | 压缩壳 | 免费的压缩壳 |
| Obsidium | 加密壳 | 带授权管理的保护工具 |

**加壳识别方法**

```
1. PEiD / DIE：查壳工具，识别常见加壳器
2. 节区名称：加壳后通常有特殊的节名（UPX0、UPX1、.themida 等）
3. 导入表：加壳后导入表函数很少，通常只有 LoadLibrary 和 GetProcAddress
4. 入口点：入口点不在 .text 节，或在末尾的节中
5. 文件熵：加壳后文件熵值很高（接近8）
```

**UPX 脱壳示例**

```bash
# 使用 UPX 自带的脱壳功能
upx -d malware.exe -o unpacked.exe

# 手动脱壳（ESP 定律）
# 1. 用 x64dbg 打开加壳程序
# 2. 在入口点观察 ESP 寄存器
# 3. 在 ESP 指向的地址下硬件访问断点
# 4. 运行程序，断下后就是 OEP（原始入口点）
# 5. 使用 Scylla 插件转储并修复 IAT
```

---

## 八、Windows 应急响应流程

### 8.1 应急响应准备

**准备工作**

1. **取证工具包**：准备好应急响应所需的工具
2. **备份策略**：确保有可靠的数据备份
3. **应急预案**：制定详细的应急响应预案
4. **联系人清单**：关键人员联系方式
5. **日志配置**：确保关键日志已启用并集中存储

**应急响应工具清单**

| 类别 | 工具 | 用途 |
|------|------|------|
| 进程分析 | Process Explorer、Process Hacker | 查看进程详情 |
| 进程监控 | Process Monitor | 监控进程行为 |
| 网络分析 | Wireshark、TCPView、netstat | 网络连接分析 |
| 启动项分析 | Autoruns | 查看所有启动项 |
| 内存取证 | FTK Imager、WinPmem、Volatility | 内存镜像和分析 |
| 注册表分析 | Regshot、Registry Explorer | 注册表对比和分析 |
| 文件分析 | Sigcheck、Strings、HashMyFiles | 文件哈希和签名验证 |
| 日志分析 | Event Log Explorer、Log Parser | 事件日志分析 |

### 8.2 事件确认与范围确定

**确认入侵迹象**

1. **防病毒/EDR 告警**：终端防护产品的告警
2. **异常行为**：用户报告的异常情况
3. **网络异常**：异常的网络连接和流量
4. **系统异常**：系统变慢、文件异常、未知进程

**初步信息收集**

```powershell
# 系统基本信息
systeminfo | findstr /i "主机名 操作系统 版本 制造商"

# 当前登录用户
query user

# 网络连接
netstat -ano | findstr /i "estab listen"

# 进程列表
tasklist /v

# 服务列表
sc query type= service state= all

# 计划任务
schtasks /query /fo LIST /v

# 用户账户
net user
net localgroup administrators
```

### 8.3 证据保全

**易失性数据收集顺序**

按照从易失到不易失的顺序收集证据：

1. 内存镜像
2. 网络连接和状态
3. 运行中的进程
4. 打开的文件
5. 系统日志
6. 硬盘镜像

**内存镜像**

```powershell
# 使用 WinPmem 提取内存镜像
winpmem_mini_x64.exe C:\evidence\memory.raw

# 使用 FTK Imager
# File → Capture Memory → 选择保存路径
```

**磁盘镜像**

```powershell
# 使用 FTK Imager 创建磁盘镜像
# File → Create Disk Image → Physical Drive → 选择磁盘 → 选择 E01/RAW 格式

# 使用 dd（Linux 下）
dd if=/dev/sda of=/evidence/disk.dd bs=4096 conv=noerror,sync
```

**日志收集**

```powershell
# 导出事件日志
wevtutil epl System C:\evidence\system.evtx
wevtutil epl Security C:\evidence\security.evtx
wevtutil epl Application C:\evidence\application.evtx

# 导出 PowerShell 日志
wevtutil epl "Windows PowerShell" C:\evidence\powershell.evtx
wevtutil epl "Microsoft-Windows-PowerShell/Operational" C:\evidence\powershell_operational.evtx

# 导出所有日志
wevtutil el > C:\evidence\loglist.txt
foreach ($log in Get-Content C:\evidence\loglist.txt) {
    wevtutil epl $log "C:\evidence\$($log.Replace('/', '_')).evtx"
}
```

### 8.4 入侵分析

**进程分析**

```
检查要点：
1. 未知的可疑进程
2. 进程路径异常（如临时目录、用户目录）
3. 进程签名验证（无签名或无效签名）
4. 异常的子进程关系（如 svchost.exe 启动 cmd.exe）
5. 进程注入迹象（内存中的可疑模块）

工具：
- Process Explorer：查看进程树、验证签名、查看 DLL
- Process Hacker：查看进程内存、句柄、网络连接
- tasklist /m：查看进程加载的 DLL
```

**网络分析**

```
检查要点：
1. 异常的对外连接（特别是未知 IP）
2. 连接到可疑端口（如 4444、8080、8443 等）
3. 大量出站连接（可能是横向移动或 C2 通信）
4. DNS 查询异常（连接到 DGA 域名）

工具：
- netstat -ano：查看网络连接
- TCPView：实时查看网络连接
- Wireshark：抓包分析
```

**启动项分析**

```
检查要点：
1. 未知的启动程序
2. 路径异常的启动项
3. 可疑的服务和驱动
4. 可疑的计划任务
5. WMI 事件订阅
6. 浏览器扩展和插件

工具：
- Autoruns：全面的启动项分析工具
- reg query：手动检查注册表启动项
```

**文件系统分析**

```
检查要点：
1. 最近创建/修改的可疑文件
2. 临时目录中的可执行文件
3. 异常命名的文件（随机字符串名称）
4. 被替换的系统文件
5. 隐藏文件和系统文件

工具：
- dir /a：显示所有文件（包括隐藏和系统文件）
- Sigcheck：验证文件签名
- Strings：提取文件中的字符串
```

### 8.5 遏制与根除

**遏制措施**

1. **网络隔离**：断开受感染主机的网络连接
2. **账户禁用**：禁用被攻陷的账户
3. **密码重置**：重置所有可能泄露的密码
4. **服务停止**：停止恶意服务
5. **进程终止**：终止恶意进程（注意：可能触发自我保护）

**根除措施**

1. **删除恶意文件**：删除所有恶意程序和相关文件
2. **清理持久化**：移除注册表启动项、服务、计划任务等
3. **修复系统文件**：修复被篡改的系统文件（sfc /scannow）
4. **恢复配置**：恢复被修改的系统配置
5. **补丁修复**：安装被利用漏洞的补丁

**系统修复命令**

```powershell
# 系统文件检查
sfc /scannow

# DISM 修复
DISM /Online /Cleanup-Image /RestoreHealth

# 检查磁盘
chkdsk C: /f /r
```

### 8.6 恢复与总结

**恢复步骤**

1. 从干净备份恢复系统（优先选择）
2. 或在确认清除恶意代码后重新接入网络
3. 加强监控，观察是否有复发迹象
4. 修复被利用的漏洞和弱点

**事件报告**

```
应急响应报告应包含：
1. 事件概述：时间、影响范围、严重程度
2. 入侵路径：攻击者是如何进入的
3. 攻击链：攻击者做了什么（时间线）
4. 影响评估：数据泄露、系统破坏、业务影响
5. 处置措施：采取了哪些遏制和根除措施
6. IOC 指标：IP、域名、文件哈希、注册表项等
7. 改进建议：如何防止类似事件再次发生
```

---

## 九、Windows 安全加固检查清单

### 9.1 系统更新

- [ ] 启用 Windows Update 自动更新
- [ ] 安装所有关键和安全更新
- [ ] 定期检查补丁状态
- [ ] 建立补丁管理流程
- [ ] 测试补丁后再部署到生产环境

### 9.2 账户安全

- [ ] 启用密码复杂性要求
- [ ] 设置密码最小长度（至少 14 位）
- [ ] 配置密码历史记录（至少 24 个）
- [ ] 设置密码最长使用期限（90 天）
- [ ] 启用账户锁定策略（5 次失败锁定 30 分钟）
- [ ] 禁用 Guest 账户
- [ ] 重命名 Administrator 账户
- [ ] 限制本地管理员组成员
- [ ] 禁用不需要的用户账户

### 9.3 审核与日志

- [ ] 启用安全审核策略
- [ ] 启用进程创建审核（含命令行）
- [ ] 启用登录/注销审核
- [ ] 启用账户管理审核
- [ ] 启用对象访问审核（关键文件/注册表）
- [ ] 启用特权使用审核
- [ ] 配置日志大小（至少 1GB 安全日志）
- [ ] 配置日志保留策略
- [ ] 配置集中日志收集（SIEM）
- [ ] 启用 PowerShell 模块日志和脚本块日志

### 9.4 网络安全

- [ ] 启用 Windows Defender 防火墙
- [ ] 默认入站策略设为阻止
- [ ] 关闭不必要的端口和服务
- [ ] 限制 RDP/SSH/WinRM 的源地址
- [ ] 启用 SMB 签名
- [ ] 禁用 SMBv1
- [ ] 配置网络分段
- [ ] 启用 Windows Defender 应用控制

### 9.5 服务加固

- [ ] 禁用不必要的服务
- [ ] 服务以最小权限运行
- [ ] 定期审查服务配置
- [ ] 验证服务文件完整性
- [ ] 限制服务权限

### 9.6 注册表加固

- [ ] 限制注册表关键键的权限
- [ ] 禁用自动运行（Autorun）
- [ ] 禁用默认共享（ADMIN$、C$）
- [ ] 限制对 SAM 的访问
- [ ] 增强 LSASS 保护（RunAsPPL）
- [ ] 禁用 LM 哈希
- [ ] 限制 NTLM 使用

### 9.7 UAC 配置

- [ ] 启用 UAC
- [ ] 设置 UAC 为最高级别
- [ ] 禁用内置管理员账户的管理员批准模式（视情况）
- [ ] 标准用户提升提示行为：自动拒绝

### 9.8 RDP 安全

- [ ] 启用网络级别身份验证（NLA）
- [ ] 限制具有 RDP 权限的用户
- [ ] 配置防火墙限制 RDP 源地址
- [ ] 使用 RD Gateway 或 VPN 进行远程访问
- [ ] 考虑更改默认端口（次要措施）
- [ ] 启用 RDP 登录审核
- [ ] 配置 RDP TLS 证书

### 9.9 恶意软件防护

- [ ] 启用 Windows Defender
- [ ] 更新病毒定义
- [ ] 启用实时保护
- [ ] 启用云提供的保护
- [ ] 配置定期扫描
- [ ] 启用勒索软件防护（受控文件夹访问）
- [ ] 启用网络保护
- [ ] 启用攻击面减少（ASR）规则

### 9.10 数据保护

- [ ] 启用 BitLocker 加密
- [ ] 配置安全启动
- [ ] 启用基于虚拟化的安全（VBS）
- [ ] 配置关键文件权限
- [ ] 配置共享文件夹权限
- [ ] 实施数据备份策略（3-2-1 原则）

### 9.11 应用安全

- [ ] 卸载不必要的软件
- [ ] 及时更新应用程序
- [ ] 配置 AppLocker 应用控制
- [ ] 禁用 Office 宏（默认禁用）
- [ ] 启用浏览器安全设置
- [ ] 配置 Flash/Java 限制

---

> 💡 **安全加固是一个持续的过程，不是一次性的任务。定期审计、持续监控、及时更新，才能有效保障终端安全。**
