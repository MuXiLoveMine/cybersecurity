# Windows 安全机制

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

---

