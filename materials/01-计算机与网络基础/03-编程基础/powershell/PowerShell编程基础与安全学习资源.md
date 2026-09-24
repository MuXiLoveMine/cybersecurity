# PowerShell 编程基础与安全学习资源

> 本文系统介绍 PowerShell 编程基础与安全领域应用：PowerShell 在安全中的定位、编程基础（安全视角）、常用命令与模块、安全运维核心用法、2026 年免费学习资源、推荐 GitHub 项目，以及两个可运行的示例脚本（basics.ps1 和 security_cases.ps1）。面向 Windows 管理员与安全工程师，全部内容从防御、自动化和授权测试的正向角度出发。

---

## 目录

- [一、PowerShell 在网络安全中的定位](#一powershell-在网络安全中的定位)
- [二、PowerShell 编程基础（安全视角）](#二powershell-编程基础安全视角)
- [三、常用命令与模块](#三常用命令与模块)
- [四、安全运维核心用法](#四安全运维核心用法)
- [五、2026 年免费学习资源](#五2026-年免费学习资源)
- [六、2026 年推荐 GitHub 项目](#六2026-年推荐-github-项目)
- [七、示例代码文件](#七示例代码文件)
- [附：优化后的提示词模板](#附优化后的提示词模板)

---

## 一、PowerShell 在网络安全中的定位

### 1.1 为什么安全从业者必须掌握 PowerShell

**PowerShell** 是微软推出的跨平台任务自动化与配置管理框架，由命令行 Shell 和脚本语言组成。它是 Windows 系统管理与安全运维的**核心脚本语言**，任何 Windows 环境（从 Windows 7 到 Windows 11，从 Server 2008 R2 到 Server 2022）都内置了 PowerShell。

| 优势 | 说明 |
|------|------|
| **Windows 原生** | 所有现代 Windows 系统自带，无需额外安装 |
| **对象化管道** | 传递的是 .NET 对象而非纯文本，处理能力远超 CMD |
| **深度集成** | 直接访问 WMI/CIM、注册表、AD、Exchange、Azure 等 |
| **远程管理** | WinRM 原生支持，可批量管理数百台 Windows 主机 |
| **应急响应必备** | 入侵排查、日志分析、取证收集的首选工具 |
| **防御与攻击双面** | 攻击者爱用（Living-off-the-Land），防御者更必须懂 |

> **安全视角的重要性**：PowerShell 是攻击者常用的 Living-off-the-Land（LotL）工具之一，因为它系统自带、功能强大、容易绕过传统杀毒。**防御者必须精通 PowerShell，才能识别恶意脚本、开展威胁狩猎、实现自动化检测与响应。**

### 1.2 PowerShell 版本演进

| 版本 | 发布时间 | 对应系统 | 关键特性 |
|------|---------|---------|---------|
| PowerShell 1.0 | 2006 | Windows XP/2003 | 初版，129 个 Cmdlet |
| PowerShell 2.0 | 2009 | Windows 7/2008 R2 | 远程管理、ISE、模块 |
| PowerShell 3.0 | 2012 | Windows 8/2012 | CIM、更新的 WMI |
| PowerShell 4.0 | 2013 | Windows 8.1/2012 R2 | Desired State Configuration (DSC) |
| PowerShell 5.0/5.1 | 2016 | Windows 10/2016/2019/2022 | 类与枚举、PackageManagement、PowerShellGet |
| **PowerShell 7.x** | 2020+ | 跨平台（Windows/Linux/macOS） | 基于 .NET Core/.NET，性能提升，跨平台 |

> **安全建议**：生产环境建议升级到 PowerShell 5.1 或 7.x，旧版本存在已知安全漏洞。同时启用 PowerShell 日志（Script Block Logging、Module Logging）以便审计与溯源。

### 1.3 安全领域的应用方向

| 方向 | PowerShell 的作用 | 典型场景 |
|------|------------------|---------|
| **安全运维** | 批量安全配置、基线检查 | 域内批量设置密码策略、检查补丁状态 |
| **日志分析** | 事件日志查询与统计 | 分析登录事件（Event ID 4624/4625）、排查异常进程 |
| **AD 管理** | 域用户/组/计算机审计 | 查找禁用账户、审计管理员组、检查 stale 账户 |
| **威胁狩猎** | 系统状态采集与关联分析 | 网络连接与进程关联、计划任务审计、启动项排查 |
| **应急响应** | 快速取证与处置 | 进程 dump、服务排查、账户禁用、隔离主机 |
| **安全基线** | 系统安全配置核查 | 检查注册表安全项、审计策略、防火墙规则 |

---

## 二、PowerShell 编程基础（安全视角）

### 2.1 Cmdlet 命名规范

PowerShell 的命令称为 **Cmdlet**（读作 command-let），遵循**动词-名词（Verb-Noun）**的命名规范。

```powershell
Get-Process    # 获取进程
Stop-Service   # 停止服务
New-Item       # 新建项目
Set-ADUser     # 设置 AD 用户
```

#### 常用动词速查

| 动词 | 含义 | 示例 |
|------|------|------|
| **Get** | 获取/查询 | Get-Process、Get-Service、Get-EventLog |
| **Set** | 设置/修改 | Set-Content、Set-Service、Set-ADUser |
| **New** | 新建 | New-Item、New-ADUser、New-Service |
| **Add** | 添加 | Add-Content、Add-Member、Add-WindowsFeature |
| **Remove** | 删除/移除 | Remove-Item、Remove-ADUser、Remove-Service |
| **Start** | 启动 | Start-Service、Start-Process、Start-Job |
| **Stop** | 停止 | Stop-Process、Stop-Service、Stop-Computer |
| **Export** | 导出 | Export-Csv、Export-Clixml、Export-ModuleMember |
| **Import** | 导入 | Import-Csv、Import-Module、Import-Clixml |
| **Invoke** | 调用/执行 | Invoke-Command、Invoke-WebRequest、Invoke-Expression |
| **Test** | 测试/验证 | Test-Connection、Test-Path、Test-NetConnection |
| **Enable/Disable** | 启用/禁用 | Enable-PSRemoting、Disable-ADAccount |

> **记忆技巧**：先想动词（要做什么），再想名词（操作对象）。不知道完整命令时，用 `Get-Command` 搜索：`Get-Command *-Service` 列出所有和 Service 相关的 Cmdlet。

### 2.2 变量与数据类型

#### 变量声明

```powershell
# 变量以 $ 开头
$name = "Alice"
$age = 25
$ip = "192.168.1.100"

# 查看变量类型
$name.GetType().FullName   # System.String
$age.GetType().FullName    # System.Int32
```

#### 常用数据类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `[string]` | 字符串 | `"Hello"`、`'World'` |
| `[int]` | 整数 | `42`、`-10` |
| `[bool]` | 布尔 | `$true`、`$false` |
| `[double]` | 浮点数 | `3.14` |
| `[datetime]` | 日期时间 | `Get-Date` |
| `[array]` | 数组 | `@(1, 2, 3)` |
| `[hashtable]` | 哈希表 | `@{key="value"}` |
| `[pscustomobject]` | 自定义对象 | `[PSCustomObject]@{...}` |

#### 字符串操作

```powershell
# 双引号支持变量插值，单引号不支持
$name = "Bob"
"Hello, $name!"          # Hello, Bob!
'Hello, $name!'          # Hello, $name!

# 字符串方法
"hello world".ToUpper()          # HELLO WORLD
"  trim me  ".Trim()             # "trim me"
"a,b,c".Split(",")               # 拆分成数组
"hello".Replace("l", "L")        # heLLo
"hello world".Contains("world")  # True
```

### 2.3 数组与哈希表

#### 数组（Array）

```powershell
# 创建数组
$services = @("Spooler", "W32Time", "Dhcp")
$processes = "notepad", "explorer", "cmd"   # 简写

# 访问元素（索引从 0 开始）
$services[0]     # Spooler
$services[-1]    # Dhcp（最后一个）

# 常用操作
$services.Count           # 元素数量
$services += "WinRM"      # 添加元素
$services -contains "W32Time"  # True
```

#### 哈希表（Hashtable）

```powershell
# 创建哈希表（键值对）
$systemInfo = @{
    ComputerName = "DC01"
    OS           = "Windows Server 2022"
    IPAddress    = "192.168.1.10"
    IsDomain     = $true
}

# 访问
$systemInfo.ComputerName     # DC01
$systemInfo["OS"]            # Windows Server 2022

# 添加/修改
$systemInfo.Admin = "administrator@corp.local"
$systemInfo.IPAddress = "192.168.1.11"

# 遍历
$systemInfo.GetEnumerator() | ForEach-Object {
    "$($_.Key): $($_.Value)"
}
```

### 2.4 流程控制

#### if / elseif / else

```powershell
$score = 85

if ($score -ge 90) {
    "优秀"
} elseif ($score -ge 60) {
    "及格"
} else {
    "不及格"
}
```

> **注意**：PowerShell 的比较运算符是 `-eq`、`-ne`、`-gt`、`-lt`、`-ge`、`-le`，而不是 `==`、`>`、`<` 等。因为 `>` 在 Shell 中是重定向符号。

#### switch（相当于增强版 if/else）

```powershell
$day = "Monday"

switch ($day) {
    "Monday"    { "工作日第一天" }
    "Friday"    { "最后一个工作日" }
    "Saturday"  { "周末" }
    "Sunday"    { "周末" }
    default     { "普通工作日" }
}

# switch 还可以处理数组
@(1, 2, 3, 4, 5) | switch {
    { $_ % 2 -eq 0 } { "$_ 是偶数" }
    { $_ % 2 -ne 0 } { "$_ 是奇数" }
}
```

#### foreach 循环

```powershell
# 遍历数组
$users = @("alice", "bob", "charlie")

foreach ($user in $users) {
    "处理用户: $user"
}

# 管道方式遍历
$users | ForEach-Object {
    "处理用户: $_"   # $_ 代表当前对象
}

# 简写（不推荐用于复杂逻辑）
$users | % { "处理用户: $_" }
```

#### while 循环

```powershell
$count = 0
while ($count -lt 5) {
    "计数: $count"
    $count++
}

# do...while（至少执行一次）
$i = 0
do {
    "i = $i"
    $i++
} while ($i -lt 3)
```

### 2.5 管道（Pipeline）

管道是 PowerShell 最强大的特性之一。与 Bash 传递文本不同，PowerShell 管道传递的是**对象**。

```powershell
# 获取所有运行中的进程，按 CPU 降序，取前 5 个
Get-Process | Where-Object { $_.CPU -gt 10 } | Sort-Object CPU -Descending | Select-Object -First 5

# 获取服务 → 筛选停止的 → 按名称排序 → 导出 CSV
Get-Service | Where-Object { $_.Status -eq "Stopped" } | Sort-Object Name | Export-Csv stopped_services.csv -Encoding UTF8
```

#### 常用管道 Cmdlet

| Cmdlet | 别名 | 作用 | 示例 |
|--------|------|------|------|
| `Where-Object` | `?`、`where` | 筛选对象 | `Get-Service \| Where Status -eq Running` |
| `Select-Object` | `select` | 选择属性/数量 | `Get-Process \| Select Name,CPU -First 10` |
| `Sort-Object` | `sort` | 排序 | `Get-Process \| Sort CPU -Descending` |
| `ForEach-Object` | `%`、`foreach` | 遍历处理 | `1..10 \| % { $_ * 2 }` |
| `Group-Object` | `group` | 分组统计 | `Get-Process \| Group Company` |
| `Measure-Object` | `measure` | 度量统计 | `Get-ChildItem \| Measure Length -Sum` |
| `Format-Table` | `ft` | 表格输出 | `Get-Service \| ft Name,Status -Auto` |
| `Format-List` | `fl` | 列表输出 | `Get-Process notepad \| fl *` |

### 2.6 函数

```powershell
# 基本函数
function Get-IPInfo {
    param(
        [string]$IPAddress
    )
    # 简单的 IP 格式验证
    if ($IPAddress -match '^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$') {
        [PSCustomObject]@{
            IP      = $IPAddress
            Valid   = $true
            Parts   = $IPAddress.Split('.')
        }
    } else {
        [PSCustomObject]@{
            IP      = $IPAddress
            Valid   = $false
            Parts   = @()
        }
    }
}

# 调用
Get-IPInfo -IPAddress "192.168.1.1"
```

#### 高级函数参数

```powershell
function Test-SecurityBaseline {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true, ValueFromPipeline=$true)]
        [string[]]$ComputerName,

        [Parameter()]
        [string]$OutputPath = "baseline_report.csv",

        [Parameter()]
        [switch]$Detailed
    )

    process {
        foreach ($computer in $ComputerName) {
            Write-Verbose "正在检查 $computer 的安全基线..."
            # ... 检查逻辑 ...
        }
    }
}
```

> **安全脚本最佳实践**：使用 `[CmdletBinding()]` 获得 `-Verbose`、`-Debug`、`-WhatIf` 等高级功能；参数明确类型和验证；输出使用结构化对象（PSCustomObject）而非纯文本。

### 2.7 文件与注册表操作

#### 文件系统操作

| Cmdlet | 说明 | 示例 |
|--------|------|------|
| `Get-ChildItem` | 列出目录内容 | `Get-ChildItem C:\Users` |
| `Get-Content` | 读取文件内容 | `Get-Content app.log -Tail 100` |
| `Set-Content` | 写入文件 | `Set-Content out.txt "hello"` |
| `Add-Content` | 追加内容 | `Add-Content log.txt "new entry"` |
| `Copy-Item` | 复制 | `Copy-Item file.txt D:\backup\` |
| `Move-Item` | 移动 | `Move-Item old.txt new.txt` |
| `Remove-Item` | 删除 | `Remove-Item temp.txt` |
| `New-Item` | 新建文件/目录 | `New-Item -ItemType Directory logs` |
| `Test-Path` | 路径是否存在 | `Test-Path C:\Windows\System32` |
| `Select-String` | 文本搜索（类似 grep） | `Select-String -Path *.log -Pattern "error"` |

> **⚠️ 高风险警告**：`Remove-Item -Recurse -Force` 相当于 `rm -rf`，使用前务必确认路径正确，建议先用 `-WhatIf` 预览效果：`Remove-Item -Path $path -Recurse -Force -WhatIf`

#### 注册表操作

PowerShell 将注册表作为驱动器（Registry Drive）访问：

```powershell
# 进入 HKLM 驱动器
Set-Location HKLM:

# 读取注册表项
Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion"

# 读取具体值
(Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion").ProductName

# 新建/修改注册表值
Set-ItemProperty -Path "HKCU:\Software\MyApp" -Name "Version" -Value "1.0" -Type String

# 新建注册表项
New-Item -Path "HKCU:\Software\MyApp\Settings" -Force
```

> **⚠️ 高风险警告**：修改注册表前务必备份！可以用 `reg export HKLM\Path backup.reg` 或 PowerShell 的 `Export-Clixml` 备份。错误修改可能导致系统无法启动。

### 2.8 远程管理

PowerShell 远程管理基于 **WinRM**（Windows Remote Management），可以在一台机器上管理多台远程主机。

#### 常用远程 Cmdlet

| Cmdlet | 作用 | 示例 |
|--------|------|------|
| `Invoke-Command` | 在远程计算机上执行命令 | `Invoke-Command -ComputerName SRV01 -ScriptBlock { Get-Process }` |
| `Enter-PSSession` | 进入交互式远程会话 | `Enter-PSSession -ComputerName DC01` |
| `New-PSSession` | 创建持久会话 | `$s = New-PSSession -ComputerName SRV01,SRV02` |
| `Copy-Item -ToSession` | 远程文件传输 | `Copy-Item -Path C:\script.ps1 -ToSession $s -Destination C:\` |

```powershell
# 单台远程执行
Invoke-Command -ComputerName "DC01.corp.local" -ScriptBlock {
    Get-Service | Where-Object { $_.Status -eq "Running" }
} -Credential (Get-Credential)

# 多台批量执行
$servers = @("DC01", "SRV01", "SRV02")
Invoke-Command -ComputerName $servers -ScriptBlock {
    hostname
    Get-EventLog -LogName Security -Newest 10
}

# 使用持久会话（多次调用复用连接）
$session = New-PSSession -ComputerName $servers
Invoke-Command -Session $session -ScriptBlock { Get-Process }
Invoke-Command -Session $session -ScriptBlock { Get-Service }
Remove-PSSession $session
```

> **⚠️ 安全提示**：远程操作需有适当权限。生产环境建议使用 HTTPS 传输（WinRM over HTTPS），避免明文传递凭证。启用 PowerShell 日志审计所有远程命令。

### 2.9 错误处理

```powershell
# try/catch/finally
try {
    Get-Process -Name "NonExistentProcess" -ErrorAction Stop
    Write-Host "进程存在"
} catch {
    Write-Warning "发生错误: $($_.Exception.Message)"
} finally {
    Write-Host "清理工作..."
}

# 错误首选项（控制错误处理行为）
$ErrorActionPreference = "Stop"      # 遇错即停（类似 bash set -e）
$ErrorActionPreference = "Continue"  # 默认，继续执行
$ErrorActionPreference = "SilentlyContinue"  # 静默忽略

# 查看最近的错误
$Error[0]  # 最近一条错误
$Error.Count  # 错误总数
```

### 2.10 脚本调试与安全选项

| 命令/参数 | 作用 |
|-----------|------|
| `Set-PSDebug -Trace 2` | 打开详细跟踪（类似 bash set -x） |
| `Set-PSDebug -Off` | 关闭调试 |
| `$VerbosePreference = "Continue"` | 显示 Verbose 输出 |
| `-WhatIf` | 预览执行效果，不实际修改 |
| `-Confirm` | 执行前确认 |

---

## 三、常用命令与模块

### 3.1 系统管理核心 Cmdlet

| 分类 | Cmdlet | 说明 | 示例 |
|------|--------|------|------|
| **进程** | `Get-Process` | 获取进程列表 | `Get-Process \| Sort CPU -Desc \| Select -First 5` |
| | `Stop-Process` | 停止进程 | `Stop-Process -Name notepad -WhatIf` |
| | `Start-Process` | 启动进程 | `Start-Process notepad.exe` |
| **服务** | `Get-Service` | 获取服务列表 | `Get-Service \| Where Status -eq Stopped` |
| | `Start-Service` | 启动服务 | `Start-Service -Name WinRM` |
| | `Stop-Service` | 停止服务 | `Stop-Service -Name Spooler` |
| | `Set-Service` | 设置服务属性 | `Set-Service -Name Telnet -StartupType Disabled` |
| **事件日志** | `Get-EventLog` | 获取传统事件日志 | `Get-EventLog -LogName Security -Newest 50` |
| | `Get-WinEvent` | 获取 Windows 事件日志（推荐） | `Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4624} -MaxEvents 10` |
| **计算机信息** | `Get-ComputerInfo` | 获取系统信息 | `Get-ComputerInfo \| Select OsName,OsVersion` |
| | `Get-CimInstance` | WMI/CIM 查询 | `Get-CimInstance Win32_OperatingSystem` |

### 3.2 Active Directory 模块

Active Directory 模块（`ActiveDirectory`）是 Windows 安全管理的核心工具，需要 RSAT 工具安装。

| Cmdlet | 说明 | 示例 |
|--------|------|------|
| `Get-ADUser` | 查询 AD 用户 | `Get-ADUser -Filter * -Properties LastLogonDate` |
| `Get-ADGroup` | 查询 AD 组 | `Get-ADGroup -Filter {Name -like "*Admin*"}` |
| `Get-ADGroupMember` | 查组成员 | `Get-ADGroupMember "Domain Admins"` |
| `Set-ADUser` | 修改用户属性 | `Set-ADUser -Identity jdoe -Enabled $false` |
| `Set-ADAccountPassword` | 重置密码 | `Set-ADAccountPassword -Identity jdoe -Reset` |
| `Disable-ADAccount` | 禁用账户 | `Disable-ADAccount -Identity jdoe` |
| `Enable-ADAccount` | 启用账户 | `Enable-ADAccount -Identity jdoe` |
| `Search-ADAccount` | 搜索账户 | `Search-ADAccount -AccountInactive -TimeSpan 90.00:00:00` |
| `Get-ADComputer` | 查询计算机 | `Get-ADComputer -Filter * -Properties LastLogonDate` |
| `Get-ADDomain` | 域信息 | `Get-ADDomain` |

```powershell
# 查找 90 天未登录的用户（安全审计常用）
Search-ADAccount -AccountInactive -TimeSpan "90.00:00:00" -UsersOnly |
    Select-Object Name, LastLogonDate, Enabled |
    Sort-Object LastLogonDate |
    Export-Csv "inactive_users.csv" -Encoding UTF8

# 审计 Domain Admins 组成员
Get-ADGroupMember "Domain Admins" -Recursive |
    Select-Object Name, SamAccountName, ObjectClass |
    Export-Csv "domain_admins.csv" -Encoding UTF8
```

> **⚠️ 高风险警告**：AD 操作直接影响域环境，修改前务必确认，建议先在测试环境验证。禁用/删除账户前确认没有业务依赖。

### 3.3 网络安全相关 Cmdlet

| Cmdlet | 说明 | 示例 |
|--------|------|------|
| `Get-NetTCPConnection` | TCP 连接（类似 netstat） | `Get-NetTCPConnection -State Listen` |
| `Test-NetConnection` | 网络连通性测试 | `Test-NetConnection -ComputerName dc01 -Port 445` |
| `Resolve-DnsName` | DNS 解析 | `Resolve-DnsName www.microsoft.com` |
| `Test-Connection` | Ping 测试 | `Test-Connection -ComputerName 8.8.8.8 -Count 2` |
| `Get-NetIPAddress` | IP 地址信息 | `Get-NetIPAddress -AddressFamily IPv4` |
| `Get-NetRoute` | 路由表 | `Get-NetRoute -AddressFamily IPv4` |
| `Get-NetFirewallRule` | 防火墙规则 | `Get-NetFirewallRule -Enabled True -Direction Inbound` |
| `Get-NetFirewallProfile` | 防火墙配置 | `Get-NetFirewallProfile -Name Domain` |
| `Invoke-WebRequest` | HTTP 请求 | `Invoke-WebRequest -Uri https://example.com` |

```powershell
# 查看所有监听端口及其关联进程
Get-NetTCPConnection -State Listen |
    Select-Object LocalAddress, LocalPort, OwningProcess,
        @{Name="ProcessName";Expression={(Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue).ProcessName}} |
    Sort-Object LocalPort |
    Format-Table -AutoSize
```

### 3.4 文件系统安全相关 Cmdlet

| Cmdlet | 说明 | 示例 |
|--------|------|------|
| `Get-Acl` | 获取访问控制列表 | `Get-Acl C:\SensitiveData` |
| `Set-Acl` | 设置访问控制列表 | `Set-Acl -Path $path -AclObject $acl` |
| `Get-FileHash` | 计算文件哈希 | `Get-FileHash -Algorithm SHA256 file.exe` |
| `Get-Item` | 获取文件/目录信息 | `Get-Item C:\Windows\System32\cmd.exe` |
| `Get-ChildItem` | 递归查找文件 | `Get-ChildItem -Path C:\ -Recurse -Filter *.ps1 -ErrorAction SilentlyContinue` |

```powershell
# 计算文件哈希（完整性校验）
Get-FileHash -Algorithm SHA256 -Path "C:\Windows\System32\cmd.exe"

# 查找系统中所有 .ps1 脚本（威胁狩猎场景）
Get-ChildItem -Path C:\ -Recurse -Filter "*.ps1" -File -ErrorAction SilentlyContinue |
    Select-Object FullName, Length, LastWriteTime |
    Export-Csv "ps1_files.csv" -Encoding UTF8
```

---

## 四、安全运维核心用法

### 4.1 事件日志分析

事件日志分析是 Windows 安全运维的核心技能。`Get-WinEvent` 是最强大的日志查询工具。

#### 常用安全事件 ID

| 事件 ID | 说明 | 日志名 |
|---------|------|--------|
| **4624** | 登录成功 | Security |
| **4625** | 登录失败 | Security |
| **4634** | 注销 | Security |
| **4648** | 显式凭据登录（runas） | Security |
| **4672** | 管理员登录（特殊权限登录） | Security |
| **4698/4699** | 计划任务创建/删除 | Security |
| **4720** | 创建用户 | Security |
| **4726** | 删除用户 | Security |
| **4728** | 添加成员到安全启用的全局组 | Security |
| **4732** | 添加成员到本地组 | Security |
| **4740** | 用户账户被锁定 | Security |
| **7045** | 服务安装 | System |
| **104** | 日志被清除 | System |

#### 日志分析示例

```powershell
# 查询最近 24 小时的登录失败记录
$startTime = (Get-Date).AddHours(-24)
Get-WinEvent -FilterHashtable @{
    LogName = 'Security'
    ID      = 4625
    StartTime = $startTime
} -MaxEvents 100 |
    Select-Object TimeCreated,
        @{Name='TargetUserName';Expression={$_.Properties[5].Value}},
        @{Name='IPAddress';Expression={$_.Properties[19].Value}},
        @{Name='FailureReason';Expression={$_.Properties[8].Value}} |
    Group-Object IPAddress |
    Sort-Object Count -Descending |
    Select-Object -First 10
```

> **安全提示**：大量 4625 事件来自同一 IP → 可能是暴力破解攻击。建议结合防火墙自动封禁。

### 4.2 AD 安全审计

```powershell
# 1. 查找所有启用但密码永不过期的用户（安全风险）
Get-ADUser -Filter {Enabled -eq $true -and PasswordNeverExpires -eq $true} `
    -Properties PasswordLastSet, LastLogonDate |
    Select-Object Name, SamAccountName, PasswordLastSet, LastLogonDate |
    Export-Csv "password_never_expires.csv" -Encoding UTF8

# 2. 查找管理员组中的所有成员
$adminGroups = @("Domain Admins", "Enterprise Admins", "Schema Admins")
foreach ($group in $adminGroups) {
    Get-ADGroupMember -Identity $group -Recursive |
        Select-Object @{Name='Group';Expression={$group}},
            Name, SamAccountName, ObjectClass
} | Export-Csv "admin_group_members.csv" -Encoding UTF8

# 3. 查找被锁定的账户
Search-ADAccount -LockedOut |
    Select-Object Name, SamAccountName, LastLogonDate |
    Export-Csv "locked_out_users.csv" -Encoding UTF8
```

### 4.3 系统安全基线检查

```powershell
# 1. 检查防火墙状态
Get-NetFirewallProfile -Name Domain, Private, Public |
    Select-Object Name, Enabled

# 2. 检查自动更新服务状态
Get-Service -Name wuauserv | Select-Object Name, Status, StartType

# 3. 检查 SMBv1 是否启用（应禁用）
Get-WindowsOptionalFeature -Online -FeatureName SMB1Protocol |
    Select-Object FeatureName, State

# 4. 检查账户策略（密码策略）
secedit /export /cfg secpol.cfg /areas SECURITYPOLICY
Get-Content secpol.cfg | Select-String "Password"

# 5. 检查 RDP 是否启用
Get-ItemProperty "HKLM:\System\CurrentControlSet\Control\Terminal Server" |
    Select-Object fDenyTSConnections
```

### 4.4 威胁狩猎：网络连接与进程关联

```powershell
# 关联网络连接与进程信息（威胁狩猎核心技巧）
$connections = Get-NetTCPConnection -State Established

foreach ($conn in $connections) {
    $proc = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue
    if ($proc) {
        [PSCustomObject]@{
            LocalAddress  = $conn.LocalAddress
            LocalPort     = $conn.LocalPort
            RemoteAddress = $conn.RemoteAddress
            RemotePort    = $conn.RemotePort
            ProcessId     = $conn.OwningProcess
            ProcessName   = $proc.ProcessName
            ProcessPath   = $proc.Path
            CommandLine   = (Get-CimInstance Win32_Process -Filter "ProcessId=$($conn.OwningProcess)").CommandLine
        }
    }
} | Export-Csv "network_process_map.csv" -Encoding UTF8
```

> **威胁狩猎思路**：查找异常的对外连接——比如 notepad.exe 对外连接 443 端口、未知进程连接境外 IP 等，都是可疑信号。

### 4.5 应急响应：快速采集

```powershell
# 应急响应快速信息采集脚本（核心信息）
$outputDir = "C:\IR_Collection_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $outputDir -Force | Out-Null

# 进程列表
Get-Process | Select-Object Id, ProcessName, Path, StartTime |
    Export-Csv "$outputDir\processes.csv" -Encoding UTF8

# 网络连接
Get-NetTCPConnection | Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort, State, OwningProcess |
    Export-Csv "$outputDir\network.csv" -Encoding UTF8

# 服务列表
Get-Service | Select-Object Name, DisplayName, Status, StartType |
    Export-Csv "$outputDir\services.csv" -Encoding UTF8

# 计划任务
Get-ScheduledTask | Select-Object TaskName, State, TaskPath |
    Export-Csv "$outputDir\scheduled_tasks.csv" -Encoding UTF8

# 最近登录事件
Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4624,4625} -MaxEvents 100 |
    Select-Object TimeCreated, Id,
        @{Name='User';Expression={$_.Properties[5].Value}},
        @{Name='IP';Expression={$_.Properties[19].Value}} |
    Export-Csv "$outputDir\logon_events.csv" -Encoding UTF8

Write-Host "采集完成: $outputDir"
```

---

## 五、2026 年免费学习资源

| 资源 | 类型 | 说明 | 链接/获取方式 |
|------|------|------|--------------|
| **Microsoft Learn - PowerShell** | 交互式课程 | 微软官方免费学习路径，从入门到高级，含沙箱练习 | [learn.microsoft.com](https://learn.microsoft.com/powershell/) |
| **PowerShell 团队博客** | 博客 | 直接从产品团队获取最新动态、最佳实践 | [devblogs.microsoft.com/powershell](https://devblogs.microsoft.com/powershell/) |
| **Cyber Mentor - PowerShell for Hunting** | 视频 | Introduction to PowerShell - Hunting Network Activity（约 24 分钟），面向威胁狩猎 | YouTube 搜索 "Cyber Mentor PowerShell Hunting" |
| **PowerShell Gallery** | 模块仓库 | 官方模块仓库，可搜索安全相关模块 | [powershellgallery.com](https://www.powershellgallery.com/) |
| **PowerShell 官方文档** | 文档 | 完整的 Cmdlet 参考和概念文档 | [learn.microsoft.com/powershell/scripting](https://learn.microsoft.com/powershell/scripting/) |

> **2026 年时效性标注**：以上资源均为长期维护的官方或社区知名资源。PowerShell 7.x 是当前及未来的重点版本，建议以 PowerShell 7+ 的特性为主要学习方向。

---

## 六、2026 年推荐 GitHub 项目

| 项目 | Stars（约） | 说明 | 适用场景 |
|------|------------|------|---------|
| **Mustangrim/PowerShell-Fundamentals-Labs** | 数百+ | 面向安全专业人员和 SOC 分析师的 PowerShell 实操培训系列，涵盖 Windows 安全管理、事件响应自动化和威胁狩猎技术 | SOC 分析、事件响应入门 |
| **0x0allenace/purple-team-simulation-01** | 数百+ | 紫队模拟练习，涵盖 PowerShell 反向 Shell 检测与调查，使用 Elastic Security、Splunk、Sysmon 和 Wireshark | 紫队演练、检测工程 |
| **yPin9/Learning-with-Claude** | 数百+ | PowerShell 全面学习笔记，从零到系统运维自动化，含大量示例 | 系统学习、运维自动化 |
| **PowerShell/PowerShell** | 4万+ | PowerShell 官方源码仓库，7.x 跨平台版本 | 深入学习、源码阅读 |
| **PowerShellMafia/PowerSploit** | 7k+ | 知名的 PowerShell 安全工具集（含检测与利用），需授权环境使用 | 授权测试、防御研究 |

> **⚠️ 免责声明**：以上 GitHub 项目仅供学习研究使用。PowerSploit 等工具包含攻击性代码，**仅限在完全授权的环境中使用**。未经授权使用这些工具进行测试可能违反法律。防御者应重点关注其原理，用于提升检测能力。

---

## 七、示例代码文件

`code/` 目录下包含两个可运行的 PowerShell 脚本：

| 文件 | 内容 | 运行方式 |
|------|------|---------|
| `basics.ps1` | PowerShell 基础语法示例：变量、数组、哈希表、管道、函数、条件、循环、错误处理 | `powershell -ExecutionPolicy Bypass -File basics.ps1` |
| `security_cases.ps1` | 安全案例集：Event ID 4624 登录审计、AD 用户审计、系统安全基线检查、日志导出 | `powershell -ExecutionPolicy Bypass -File security_cases.ps1` |

### 7.1 basics.ps1 内容概览

- 变量与数据类型
- 数组与哈希表
- 管道操作
- 条件判断（if / switch）
- 循环（foreach / while / for）
- 函数（含高级参数）
- 文件操作
- 错误处理
- 对象操作（Select / Where / Sort）

### 7.2 security_cases.ps1 内容概览

| 案例 | 功能 | 权限要求 |
|------|------|---------|
| **登录事件审计** | 分析 Event ID 4624/4625，统计登录来源 IP，检测异常登录 | 需管理员权限访问 Security 日志 |
| **AD 用户安全审计** | 检查密码永不过期、90天未登录、管理员组成员、锁定账户 | 需域管理员权限 + AD 模块 |
| **系统安全基线检查** | 防火墙、更新服务、SMBv1、RDP、账户策略等检查 | 需管理员权限 |
| **安全日志导出** | 按事件类型导出安全日志为 CSV | 需管理员权限 |

> **运行注意**：
> - 部分功能需要管理员权限（如访问 Security 日志、AD 模块）
> - 建议在测试环境中先验证脚本
> - AD 相关功能需要安装 RSAT-AD-PowerShell 模块
> - 执行策略默认禁止脚本运行，需用 `-ExecutionPolicy Bypass` 或先设置执行策略

---

## 附：优化后的提示词模板

```
# 角色
你是一名资深 Windows 系统与 PowerShell 安全专家，精通 PowerShell 自动化、AD 管理、事件日志分析、威胁狩猎与安全运维。

# 任务
请针对以下 PowerShell 安全任务给出完整方案：
【在此处填入具体任务，如"编写一个自动化安全巡检脚本"】

# 输出要求
- 完整的 PowerShell 脚本，带注释
- 参数化设计，可复用
- 输出结构化（PSCustomObject / CSV）
- 错误处理与日志记录
- 安全注意事项与风险提示

# 约束
- 仅限防御与授权测试场景
- 修改系统配置前必须有 -WhatIf 支持
- 高风险操作需明确警告
- 脚本需遵循 PowerShell 最佳实践
```

---

> **免责声明**：本文档所有内容仅用于学习、研究和授权环境下的安全运维与防御测试。任何未经授权的测试或攻击行为均属违法。读者应遵守所在地区法律法规，对自己的行为负责。
