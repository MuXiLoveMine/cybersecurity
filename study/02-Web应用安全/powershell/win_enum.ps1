<#
================================================================================
  Windows 信息收集脚本 - win_enum.ps1
================================================================================
  功能说明：
    本脚本用于收集 Windows 系统的各类信息，用于红蓝对抗中的
    信息收集阶段和系统安全评估。所有信息均通过系统标准 API 获取。

  收集内容：
    1. 系统基本信息（主机名、OS 版本、域信息等）
    2. 用户与组信息（当前用户、本地用户、管理员组等）
    3. 网络配置信息（IP 地址、网卡、路由、ARP 表等）
    4. 进程信息（运行中的进程列表）
    5. 服务信息（系统服务列表及状态）
    6. 启动项信息（注册表启动项、计划任务等）
    7. 已安装软件
    8. 共享文件夹
    9. 补丁信息（已安装的 Hotfix）
    10. 安全产品检测（杀软、防火墙状态）

  使用方法：
    .\win_enum.ps1 [选项]

  示例：
    # 完整信息收集
    .\win_enum.ps1

    # 输出到文件
    .\win_enum.ps1 -Output "enum_result.txt"

    # 仅收集指定类别
    .\win_enum.ps1 -Categories "system,network,process"

    # 显示帮助
    .\win_enum.ps1 -Help

  免责声明：
    本脚本仅供安全学习和授权测试使用。
    仅用于授权的系统安全评估和红蓝对抗演练。
    请勿在未授权的系统上运行本脚本。
    使用本脚本造成的一切后果由使用者自行承担。
================================================================================
#>

param(
    [Parameter(Mandatory=$false, HelpMessage="输出文件路径")]
    [string]$Output,

    [Parameter(Mandatory=$false, HelpMessage="收集类别（逗号分隔）")]
    [string]$Categories,

    [Parameter(Mandatory=$false, HelpMessage="显示帮助")]
    [switch]$Help
)

# ============================================================
# 全局变量
# ============================================================
$script:outputBuffer = @()

# ============================================================
# 打印帮助信息
# ============================================================
function Show-Help {
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host "  Windows 信息收集脚本 - 安全研究用" -ForegroundColor Cyan
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "用法: .\win_enum.ps1 [选项]"
    Write-Host ""
    Write-Host "参数说明:"
    Write-Host "  -Output       输出结果到文件"
    Write-Host "  -Categories   指定收集类别（逗号分隔）"
    Write-Host "  -Help         显示此帮助信息"
    Write-Host ""
    Write-Host "可用类别:"
    Write-Host "  system      - 系统基本信息"
    Write-Host "  user        - 用户与组信息"
    Write-Host "  network     - 网络配置信息"
    Write-Host "  process     - 进程信息"
    Write-Host "  service     - 服务信息"
    Write-Host "  startup     - 启动项信息"
    Write-Host "  software    - 已安装软件"
    Write-Host "  share       - 共享文件夹"
    Write-Host "  patch       - 补丁信息"
    Write-Host "  security    - 安全产品检测"
    Write-Host "  all         - 全部（默认）"
    Write-Host ""
    Write-Host "示例:"
    Write-Host "  .\win_enum.ps1"
    Write-Host "  .\win_enum.ps1 -Output result.txt"
    Write-Host "  .\win_enum.ps1 -Categories system,network,process"
    Write-Host "================================================================" -ForegroundColor Cyan
}

# ============================================================
# 输出函数（同时输出到屏幕和缓冲区）
# ============================================================
function Write-EnumOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )

    Write-Host $Message -ForegroundColor $Color
    if ($Output) {
        $script:outputBuffer += $Message
    }
}

function Write-EnumSection {
    param([string]$Title)

    $line = "=" * 64
    Write-EnumOutput ""
    Write-EnumOutput $line "Cyan"
    Write-EnumOutput "  $Title" "Cyan"
    Write-EnumOutput $line "Cyan"
    Write-EnumOutput ""
}

function Write-EnumSubSection {
    param([string]$Title)

    Write-EnumOutput ""
    Write-EnumOutput "  --- $Title ---" "Yellow"
}

# ============================================================
-- 1. 系统基本信息收集
-- ============================================================
function Get-SystemInfo {
    Write-EnumSection "一、系统基本信息"

    try {
        $os = Get-CimInstance Win32_OperatingSystem -ErrorAction SilentlyContinue
        $cs = Get-CimInstance Win32_ComputerSystem -ErrorAction SilentlyContinue
        $bios = Get-CimInstance Win32_BIOS -ErrorAction SilentlyContinue
        $cpu = Get-CimInstance Win32_Processor -ErrorAction SilentlyContinue | Select-Object -First 1

        Write-EnumOutput "  主机名:         $($cs.Name)"
        Write-EnumOutput "  域名:           $($cs.Domain)"
        Write-EnumOutput "  工作组/域模式:  $($cs.Workgroup)"
        Write-EnumOutput "  操作系统:       $($os.Caption)"
        Write-EnumOutput "  版本号:         $($os.Version)"
        Write-EnumOutput "  构建号:         $($os.BuildNumber)"
        Write-EnumOutput "  系统类型:       $($os.OSType)"
        Write-EnumOutput "  架构:           $($os.OSArchitecture)"
        Write-EnumOutput "  安装日期:       $($os.InstallDate)"
        Write-EnumOutput "  最后启动时间:   $($os.LastBootUpTime)"
        Write-EnumOutput "  系统目录:       $($os.SystemDirectory)"
        Write-EnumOutput "  Windows 目录:   $($os.WindowsDirectory)"
        Write-EnumOutput "  制造商:         $($cs.Manufacturer)"
        Write-EnumOutput "  型号:           $($cs.Model)"
        Write-EnumOutput "  BIOS 版本:      $($bios.SMBIOSBIOSVersion)"
        Write-EnumOutput "  CPU:            $($cpu.Name)"
        Write-EnumOutput "  内存:           $([math]::Round($cs.TotalPhysicalMemory / 1GB, 2)) GB"
        Write-EnumOutput "  处理器数量:     $($cs.NumberOfProcessors)"
        Write-EnumOutput "  逻辑处理器:     $($cs.NumberOfLogicalProcessors)"
        Write-EnumOutput "  时区:           $($os.CurrentTimeZone)"
        Write-EnumOutput "  语言:           $($os.OSLanguage)"
    }
    catch {
        Write-EnumOutput "  [错误] 获取系统信息失败: $($_.Exception.Message)" "Red"
    }

    # 环境变量
    Write-EnumSubSection "环境变量"
    $importantEnv = @("COMPUTERNAME", "USERDOMAIN", "USERNAME", "WINDIR", "SYSTEMROOT", "SYSTEMDRIVE", "PROGRAMFILES", "APPDATA", "LOCALAPPDATA", "TEMP", "PATH")
    foreach ($envName in $importantEnv) {
        $val = [Environment]::GetEnvironmentVariable($envName)
        if ($val) {
            Write-EnumOutput "  $($envName.PadRight(15)) = $val"
        }
    }
}

# ============================================================
-- 2. 用户与组信息收集
-- ============================================================
function Get-UserGroupInfo {
    Write-EnumSection "二、用户与组信息"

    # 当前用户信息
    Write-EnumSubSection "当前用户"
    $currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent()
    Write-EnumOutput "  用户名:         $($currentUser.Name)"
    Write-EnumOutput "  SID:            $($currentUser.User.Value)"
    Write-EnumOutput "  认证类型:       $($currentUser.AuthenticationType)"
    Write-EnumOutput "  系统账户:       $($currentUser.IsSystem)"
    Write-EnumOutput "  来宾账户:       $($currentUser.IsGuest)"

    # 管理员权限检测
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
    Write-EnumOutput "  管理员权限:     $isAdmin" $(if ($isAdmin) { "Green" } else { "Yellow" })

    # 本地用户列表
    Write-EnumSubSection "本地用户列表"
    try {
        $users = Get-CimInstance Win32_UserAccount -Filter "LocalAccount=True" -ErrorAction SilentlyContinue
        foreach ($u in $users) {
            $status = @()
            if ($u.Disabled) { $status += "禁用" }
            if ($u.Lockout) { $status += "锁定" }
            if ($u.PasswordRequired -eq $false) { $status += "无密码" }
            $statusStr = if ($status.Count -gt 0) { "[$($status -join ', ')]" } else { "[正常]" }
            Write-EnumOutput "  $($u.Name.PadRight(20)) $statusStr"
        }
    }
    catch {
        Write-EnumOutput "  [错误] 获取用户列表失败: $($_.Exception.Message)" "Red"
    }

    # 本地组列表
    Write-EnumSubSection "本地组列表（前20个）"
    try {
        $groups = Get-CimInstance Win32_Group -Filter "LocalAccount=True" -ErrorAction SilentlyContinue | Select-Object -First 20
        foreach ($g in $groups) {
            Write-EnumOutput "  $($g.Name)"
        }
    }
    catch {
        Write-EnumOutput "  [错误] 获取组列表失败: $($_.Exception.Message)" "Red"
    }

    # 管理员组成员
    Write-EnumSubSection "管理员组 (Administrators) 成员"
    try {
        $adminGroup = Get-CimInstance Win32_Group -Filter "Name='Administrators' and LocalAccount=True" -ErrorAction SilentlyContinue
        if ($adminGroup) {
            $members = Get-CimAssociatedInstance -InputObject $adminGroup -ResultClassName Win32_UserAccount -ErrorAction SilentlyContinue
            foreach ($m in $members) {
                Write-EnumOutput "  $($m.Name) ($($m.Domain))"
            }
        }
    }
    catch {
        Write-EnumOutput "  [错误] 获取管理员组成员失败: $($_.Exception.Message)" "Red"
    }
}

# ============================================================
-- 3. 网络配置信息收集
-- ============================================================
function Get-NetworkInfo {
    Write-EnumSection "三、网络配置信息"

    # 网络适配器信息
    Write-EnumSubSection "网络适配器"
    try {
        $adapters = Get-CimInstance Win32_NetworkAdapterConfiguration -Filter "IPEnabled=True" -ErrorAction SilentlyContinue
        foreach ($a in $adapters) {
            Write-EnumOutput "  描述:  $($a.Description)"
            Write-EnumOutput "  MAC:   $($a.MACAddress)"
            if ($a.IPAddress) {
                foreach ($ip in $a.IPAddress) {
                    Write-EnumOutput "  IP:    $ip"
                }
            }
            if ($a.IPSubnet) {
                Write-EnumOutput "  掩码:  $($a.IPSubnet -join ', ')"
            }
            if ($a.DefaultIPGateway) {
                Write-EnumOutput "  网关:  $($a.DefaultIPGateway -join ', ')"
            }
            if ($a.DNSServerSearchOrder) {
                Write-EnumOutput "  DNS:   $($a.DNSServerSearchOrder -join ', ')"
            }
            Write-EnumOutput "  DHCP:  $($a.DHCPEnabled)"
            Write-EnumOutput ""
        }
    }
    catch {
        Write-EnumOutput "  [错误] 获取网络适配器失败: $($_.Exception.Message)" "Red"
    }

    # 监听端口
    Write-EnumSubSection "监听端口 (TCP)"
    try {
        $listening = Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Sort-Object LocalPort
        Write-EnumOutput "  端口     进程ID   进程名"
        Write-EnumOutput "  -------  -------  -------"
        foreach ($conn in $listening | Select-Object -First 30) {
            $procName = ""
            try {
                $proc = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue
                $procName = $proc.ProcessName
            } catch {}
            Write-EnumOutput "  $($conn.LocalPort.ToString().PadRight(7))  $($conn.OwningProcess.ToString().PadRight(7))  $procName"
        }
        if ($listening.Count -gt 30) {
            Write-EnumOutput "  ... 共 $($listening.Count) 个监听端口"
        }
    }
    catch {
        Write-EnumOutput "  [错误] 获取监听端口失败: $($_.Exception.Message)" "Red"
    }

    # 网络连接
    Write-EnumSubSection "活跃网络连接 (ESTABLISHED)"
    try {
        $established = Get-NetTCPConnection -State Established -ErrorAction SilentlyContinue
        Write-EnumOutput "  本地地址:端口           远程地址:端口         进程"
        Write-EnumOutput "  ---------------------  ---------------------  -------"
        foreach ($conn in $established | Select-Object -First 20) {
            $procName = ""
            try {
                $proc = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue
                $procName = $proc.ProcessName
            } catch {}
            $local = "$($conn.LocalAddress):$($conn.LocalPort)"
            $remote = "$($conn.RemoteAddress):$($conn.RemotePort)"
            Write-EnumOutput "  $($local.PadRight(21))  $($remote.PadRight(21))  $procName"
        }
        if ($established.Count -gt 20) {
            Write-EnumOutput "  ... 共 $($established.Count) 个活跃连接"
        }
    }
    catch {
        Write-EnumOutput "  [错误] 获取网络连接失败: $($_.Exception.Message)" "Red"
    }
}

# ============================================================
-- 4. 进程信息收集
-- ============================================================
function Get-ProcessInfo {
    Write-EnumSection "四、进程信息"

    try {
        $processes = Get-Process -ErrorAction SilentlyContinue
        Write-EnumOutput "  总进程数: $($processes.Count)"
        Write-EnumOutput ""
        Write-EnumOutput "  PID     进程名                 内存(MB)   会话ID"
        Write-EnumOutput "  ------  ---------------------  ---------  -------"

        # 按内存排序，显示前30个
        $topProcs = $processes | Sort-Object WorkingSet64 -Descending | Select-Object -First 30
        foreach ($p in $topProcs) {
            $mem = [math]::Round($p.WorkingSet64 / 1MB, 1)
            Write-EnumOutput "  $($p.Id.ToString().PadRight(6))  $($p.ProcessName.PadRight(21))  $($mem.ToString().PadLeft(8))   $($p.SessionId)"
        }

        if ($processes.Count -gt 30) {
            Write-EnumOutput "  ... 共 $($processes.Count) 个进程"
        }
    }
    catch {
        Write-EnumOutput "  [错误] 获取进程列表失败: $($_.Exception.Message)" "Red"
    }
}

# ============================================================
-- 5. 服务信息收集
-- ============================================================
function Get-ServiceInfo {
    Write-EnumSection "五、服务信息"

    try {
        $services = Get-Service -ErrorAction SilentlyContinue
        $running = ($services | Where-Object { $_.Status -eq "Running" }).Count
        $stopped = ($services | Where-Object { $_.Status -eq "Stopped" }).Count

        Write-EnumOutput "  总服务数:   $($services.Count)"
        Write-EnumOutput "  运行中:     $running"
        Write-EnumOutput "  已停止:     $stopped"
        Write-EnumOutput ""

        Write-EnumSubSection "正在运行的服务（前30个）"
        Write-EnumOutput "  服务名                  显示名称"
        Write-EnumOutput "  ----------------------  ----------------------------------------"

        $runningSvcs = $services | Where-Object { $_.Status -eq "Running" } | Sort-Object Name | Select-Object -First 30
        foreach ($s in $runningSvcs) {
            Write-EnumOutput "  $($s.Name.PadRight(22))  $($s.DisplayName)"
        }

        if (($services | Where-Object { $_.Status -eq "Running" }).Count -gt 30) {
            Write-EnumOutput "  ... 共 $running 个运行中服务"
        }
    }
    catch {
        Write-EnumOutput "  [错误] 获取服务列表失败: $($_.Exception.Message)" "Red"
    }
}

# ============================================================
-- 6. 启动项信息收集
-- ============================================================
function Get-StartupInfo {
    Write-EnumSection "六、启动项信息"

    # 注册表启动项
    Write-EnumSubSection "注册表启动项 (Run)"
    $runPaths = @(
        "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run",
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run",
        "HKLM:\Software\Microsoft\Windows\CurrentVersion\RunOnce",
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\RunOnce"
    )

    foreach ($path in $runPaths) {
        if (Test-Path $path) {
            Write-EnumOutput ""
            Write-EnumOutput "  $path" "Gray"
            try {
                $items = Get-ItemProperty $path -ErrorAction SilentlyContinue
                $props = $items.PSObject.Properties | Where-Object { $_.Name -notlike "PS*" }
                if ($props.Count -eq 0) {
                    Write-EnumOutput "    (空)"
                }
                else {
                    foreach ($p in $props) {
                        Write-EnumOutput "    $($p.Name) = $($p.Value)"
                    }
                }
            }
            catch {
                Write-EnumOutput "    [读取失败]" "Red"
            }
        }
    }

    # 启动文件夹
    Write-EnumSubSection "启动文件夹"
    $startupPaths = @(
        "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup",
        "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\Startup"
    )

    foreach ($path in $startupPaths) {
        Write-EnumOutput ""
        Write-EnumOutput "  $path" "Gray"
        if (Test-Path $path) {
            $items = Get-ChildItem $path -ErrorAction SilentlyContinue
            if ($items.Count -eq 0) {
                Write-EnumOutput "    (空)"
            }
            else {
                foreach ($item in $items) {
                    Write-EnumOutput "    $($item.Name)"
                }
            }
        }
        else {
            Write-EnumOutput "    (路径不存在)"
        }
    }

    # 计划任务
    Write-EnumSubSection "计划任务（前20个）"
    try {
        $tasks = Get-ScheduledTask -ErrorAction SilentlyContinue | Select-Object -First 20
        foreach ($t in $tasks) {
            $state = $t.State
            Write-EnumOutput "  $($t.TaskName.PadRight(30)) [$state]"
        }
    }
    catch {
        Write-EnumOutput "  [错误] 获取计划任务失败: $($_.Exception.Message)" "Red"
    }
}

# ============================================================
-- 7. 已安装软件
-- ============================================================
function Get-SoftwareInfo {
    Write-EnumSection "七、已安装软件"

    try {
        $software = Get-CimInstance Win32_Product -ErrorAction SilentlyContinue
        if ($software) {
            Write-EnumOutput "  已安装软件数: $($software.Count)"
            Write-EnumOutput ""
            Write-EnumOutput "  软件名称                         版本          厂商"
            Write-EnumOutput "  -------------------------------  ------------  --------------------"

            foreach ($s in $software | Sort-Object Name | Select-Object -First 30) {
                $name = if ($s.Name.Length -gt 30) { $s.Name.Substring(0, 29) + "..." } else { $s.Name }
                $version = $s.Version ?? "?"
                $vendor = if ($s.Vendor) { $s.Vendor } else { "?" }
                if ($vendor.Length -gt 20) { $vendor = $vendor.Substring(0, 19) + "..." }
                Write-EnumOutput "  $($name.PadRight(31)) $($version.PadRight(12)) $vendor"
            }

            if ($software.Count -gt 30) {
                Write-EnumOutput "  ... 共 $($software.Count) 个软件"
            }
        }
        else {
            Write-EnumOutput "  未获取到已安装软件列表"
        }
    }
    catch {
        Write-EnumOutput "  [错误] 获取软件列表失败: $($_.Exception.Message)" "Red"
    }
}

# ============================================================
-- 8. 共享文件夹
-- ============================================================
function Get-ShareInfo {
    Write-EnumSection "八、共享文件夹"

    try {
        $shares = Get-CimInstance Win32_Share -ErrorAction SilentlyContinue
        if ($shares) {
            Write-EnumOutput "  共享名称        路径                          类型      描述"
            Write-EnumOutput "  --------------  ----------------------------  --------  --------"
            foreach ($s in $shares) {
                $type = switch ($s.Type) {
                    0 { "磁盘" }
                    1 { "打印机" }
                    2 { "设备" }
                    3 { "IPC" }
                    default { "未知" }
                }
                $name = $s.Name.PadRight(14)
                $path = if ($s.Path) { $s.Path } else { "" }
                if ($path.Length -gt 28) { $path = $path.Substring(0, 27) + "..." }
                $path = $path.PadRight(28)
                $type = $type.PadRight(8)
                $desc = $s.Description ?? ""
                Write-EnumOutput "  $name $path $type $desc"
            }
        }
    }
    catch {
        Write-EnumOutput "  [错误] 获取共享文件夹失败: $($_.Exception.Message)" "Red"
    }
}

# ============================================================
-- 9. 补丁信息
-- ============================================================
function Get-PatchInfo {
    Write-EnumSection "九、补丁信息"

    try {
        $hotfixes = Get-CimInstance Win32_QuickFixEngineering -ErrorAction SilentlyContinue
        if ($hotfixes) {
            Write-EnumOutput "  已安装补丁数: $($hotfixes.Count)"
            Write-EnumOutput ""
            Write-EnumOutput "  HotFixID        安装日期       描述"
            Write-EnumOutput "  --------------  -------------  ------------------------"

            foreach ($h in $hotfixes | Sort-Object InstalledOn -Descending | Select-Object -First 20) {
                $date = if ($h.InstalledOn) { $h.InstalledOn.ToString("yyyy-MM-dd") } else { "未知" }
                $desc = $h.Description ?? "?"
                Write-EnumOutput "  $($h.HotFixID.PadRight(14))  $($date.PadRight(13))  $desc"
            }

            if ($hotfixes.Count -gt 20) {
                Write-EnumOutput "  ... 共 $($hotfixes.Count) 个补丁"
            }
        }
    }
    catch {
        Write-EnumOutput "  [错误] 获取补丁信息失败: $($_.Exception.Message)" "Red"
    }
}

# ============================================================
-- 10. 安全产品检测
-- ============================================================
function Get-SecurityInfo {
    Write-EnumSection "十、安全产品检测"

    # 防病毒产品
    Write-EnumSubSection "防病毒产品"
    try {
        $av = Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntivirusProduct -ErrorAction SilentlyContinue
        if ($av) {
            foreach ($a in $av) {
                Write-EnumOutput "  产品名称: $($a.displayName)"
                Write-EnumOutput "  产品状态: $($a.productState)"
                Write-EnumOutput "  启用状态: $(($a.productState -band 0x10) -ne 0)"
            }
        }
        else {
            Write-EnumOutput "  未检测到防病毒产品（或 SecurityCenter 不可用）" "Yellow"
        }
    }
    catch {
        Write-EnumOutput "  [错误] 检测失败: $($_.Exception.Message)" "Red"
    }

    # 防火墙状态
    Write-EnumSubSection "防火墙状态"
    try {
        $fw = Get-CimInstance -Namespace root/StandardCimv2 -ClassName MSFT_NetFirewallProfile -ErrorAction SilentlyContinue
        if ($fw) {
            foreach ($p in $fw) {
                $status = if ($p.Enabled) { "已启用" } else { "已禁用" }
                $color = if ($p.Enabled) { "Green" } else { "Red" }
                Write-EnumOutput "  $($p.Name) 配置文件: $status" $color
            }
        }
        else {
            Write-EnumOutput "  无法获取防火墙状态" "Yellow"
        }
    }
    catch {
        Write-EnumOutput "  [错误] 检测失败: $($_.Exception.Message)" "Red"
    }

    # Windows Defender 状态
    Write-EnumSubSection "Windows Defender"
    try {
        $defender = Get-MpComputerStatus -ErrorAction SilentlyContinue
        if ($defender) {
            Write-EnumOutput "  实时保护: $($defender.RealTimeProtectionEnabled)"
            Write-EnumOutput "  反病毒启用: $($defender.AntivirusEnabled)"
            Write-EnumOutput "  反间谍软件: $($defender.AntispywareEnabled)"
            Write-EnumOutput "  病毒定义版本: $($defender.AntivirusSignatureVersion)"
            Write-EnumOutput "  定义更新时间: $($defender.AntivirusSignatureLastUpdated)"
        }
    }
    catch {
        Write-EnumOutput "  未检测到 Windows Defender 或无权限访问" "Yellow"
    }

    # UAC 状态
    Write-EnumSubSection "UAC 状态"
    try {
        $uac = Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -ErrorAction SilentlyContinue
        if ($uac.EnableLUA -ne $null) {
            $uacStatus = if ($uac.EnableLUA -eq 1) { "已启用" } else { "已禁用" }
            Write-EnumOutput "  UAC: $uacStatus"
        }
    }
    catch {
        Write-EnumOutput "  无法获取 UAC 状态" "Yellow"
    }
}

# ============================================================
# 主程序入口
# ============================================================
function Main {
    if ($Help) {
        Show-Help
        return
    }

    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host "  Windows 信息收集脚本" -ForegroundColor Cyan
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host ""

    # 解析收集类别
    $categoryList = @("system", "user", "network", "process", "service", "startup", "software", "share", "patch", "security")
    if ($Categories) {
        if ($Categories -eq "all") {
            $selected = $categoryList
        }
        else {
            $selected = $Categories -split "," | ForEach-Object { $_.Trim().ToLower() }
        }
    }
    else {
        $selected = $categoryList
    }

    Write-Host "[信息] 开始信息收集..." -ForegroundColor Yellow
    Write-Host "[信息] 收集类别: $($selected -join ', ')" -ForegroundColor Yellow

    $startTime = Get-Date

    # 根据选择执行对应的收集函数
    if ($selected -contains "system")   { Get-SystemInfo }
    if ($selected -contains "user")     { Get-UserGroupInfo }
    if ($selected -contains "network")  { Get-NetworkInfo }
    if ($selected -contains "process")  { Get-ProcessInfo }
    if ($selected -contains "service")  { Get-ServiceInfo }
    if ($selected -contains "startup")  { Get-StartupInfo }
    if ($selected -contains "software") { Get-SoftwareInfo }
    if ($selected -contains "share")    { Get-ShareInfo }
    if ($selected -contains "patch")    { Get-PatchInfo }
    if ($selected -contains "security") { Get-SecurityInfo }

    $endTime = Get-Date
    $duration = ($endTime - $startTime).TotalSeconds

    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host "  信息收集完成，耗时 $([math]::Round($duration, 2)) 秒" -ForegroundColor Cyan
    Write-Host "================================================================" -ForegroundColor Cyan

    # 保存输出到文件
    if ($Output) {
        $script:outputBuffer | Out-File -FilePath $Output -Encoding UTF8
        Write-Host ""
        Write-Host "[信息] 结果已保存到: $Output" -ForegroundColor Yellow
    }
}

# 运行主程序
Main
