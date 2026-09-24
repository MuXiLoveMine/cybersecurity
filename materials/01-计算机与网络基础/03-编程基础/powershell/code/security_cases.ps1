# security_cases.ps1 —— PowerShell 安全案例集（防御/运维视角）
#
# 涵盖 4 个安全案例：
#   1. 登录事件审计 —— 分析 Event ID 4624/4625，检测暴力破解
#   2. 系统安全基线检查 —— 防火墙、服务、注册表、账户策略
#   3. 进程与网络关联分析 —— 威胁狩猎，查找可疑网络连接
#   4. 安全日志导出 —— 按事件类型导出为 CSV
#
# 运行方式:
#   powershell -ExecutionPolicy Bypass -File security_cases.ps1          # 运行所有演示
#   powershell -ExecutionPolicy Bypass -File security_cases.ps1 --help   # 查看帮助
#   powershell -ExecutionPolicy Bypass -File security_cases.ps1 login    # 登录事件审计
#   powershell -ExecutionPolicy Bypass -File security_cases.ps1 baseline # 安全基线检查
#   powershell -ExecutionPolicy Bypass -File security_cases.ps1 network  # 网络关联分析
#   powershell -ExecutionPolicy Bypass -File security_cases.ps1 export   # 日志导出
#
# 注意：
#   - 所有工具仅限在授权的环境中使用
#   - 生产环境使用前请充分测试
#   - 安全日志访问需要管理员权限
#   - AD 相关功能需要安装 RSAT-AD-PowerShell 模块

#Requires -Version 5.1

param(
    [Parameter(Position=0)]
    [ValidateSet("all", "login", "baseline", "network", "export", "help")]
    [string]$Mode = "all"
)

# ============================================================
# 配置与辅助函数
# ============================================================

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$OutputDir = Join-Path $ScriptDir "output"

# 颜色输出函数
function Write-Info    { Write-Host "[INFO]  $args" -ForegroundColor Cyan }
function Write-Success { Write-Host "[OK]    $args" -ForegroundColor Green }
function Write-Warn    { Write-Host "[WARN]  $args" -ForegroundColor Yellow }
function Write-ErrorMsg { Write-Host "[ERROR] $args" -ForegroundColor Red }
function Write-Section { Write-Host ""; Write-Host "=== $args ===" -ForegroundColor Magenta; Write-Host "" }

# 检查是否为管理员
function Test-IsAdmin {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# 确保输出目录存在
function Ensure-OutputDir {
    if (-not (Test-Path $OutputDir)) {
        New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    }
}

# 生成时间戳
function Get-Timestamp {
    return Get-Date -Format "yyyyMMdd_HHmmss"
}

# ============================================================
# 帮助信息
# ============================================================
function Show-Help {
    Write-Host ""
    Write-Host "PowerShell 安全案例集 - 使用帮助" -ForegroundColor Cyan
    Write-Host "==================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "用法: powershell -ExecutionPolicy Bypass -File security_cases.ps1 [模式]"
    Write-Host ""
    Write-Host "模式:"
    Write-Host "  all       - 运行所有案例（默认）"
    Write-Host "  login     - 登录事件审计（4624/4625）"
    Write-Host "  baseline  - 系统安全基线检查"
    Write-Host "  network   - 进程与网络关联分析"
    Write-Host "  export    - 安全日志导出"
    Write-Host "  help      - 显示此帮助"
    Write-Host ""
    Write-Host "注意事项:"
    Write-Host "  - 部分功能需要管理员权限（如访问 Security 日志）"
    Write-Host "  - 输出文件保存在 code\output\ 目录下"
    Write-Host "  - 建议在测试环境中先验证脚本"
    Write-Host ""
}

# ============================================================
# 案例 1：登录事件审计
# ============================================================
function Invoke-LoginAudit {
    Write-Section "案例 1：登录事件审计（Event ID 4624/4625）"

    # 检查权限
    $isAdmin = Test-IsAdmin
    if (-not $isAdmin) {
        Write-Warn "当前非管理员权限，可能无法访问 Security 日志"
        Write-Warn "建议以管理员身份运行 PowerShell"
    }

    # 时间范围（最近 24 小时）
    $startTime = (Get-Date).AddHours(-24)
    $endTime = Get-Date
    Write-Info "分析时间范围: $startTime ~ $endTime"
    Write-Info ""

    # ---- 登录成功统计（4624） ----
    Write-Info "【1.1 登录成功统计（Event ID 4624）】"
    try {
        $successLogons = Get-WinEvent -FilterHashtable @{
            LogName   = "Security"
            ID        = 4624
            StartTime = $startTime
        } -MaxEvents 500 -ErrorAction Stop

        Write-Success "成功登录事件数: $($successLogons.Count)"

        # 提取登录用户和来源 IP
        $loginDetails = $successLogons | ForEach-Object {
            $xml = [xml]$_.ToXml()
            $props = @{}
            foreach ($data in $xml.Event.EventData.Data) {
                $props[$data.Name] = $data.'#text'
            }
            [PSCustomObject]@{
                TimeCreated   = $_.TimeCreated
                TargetUser    = $props.TargetUserName
                TargetDomain  = $props.TargetDomainName
                LogonType     = $props.LogonType
                IPAddress     = $props.IpAddress
                Workstation   = $props.WorkstationName
                LogonProcess  = $props.LogonProcessName
            }
        }

        # 按用户统计
        Write-Info ""
        Write-Info "按用户统计登录次数 (前 10):"
        $loginDetails | Group-Object TargetUser | Sort-Object Count -Descending |
            Select-Object -First 10 @{Name='用户';Expression={$_.Name}}, Count |
            Format-Table -AutoSize | Out-String | ForEach-Object { Write-Host "  $_" }

        # 按来源 IP 统计
        Write-Info "按来源 IP 统计 (前 10):"
        $loginDetails | Where-Object { $_.IPAddress -and $_.IPAddress -ne "-" } |
            Group-Object IPAddress | Sort-Object Count -Descending |
            Select-Object -First 10 @{Name='来源IP';Expression={$_.Name}}, Count |
            Format-Table -AutoSize | Out-String | ForEach-Object { Write-Host "  $_" }

        # 登录类型说明
        Write-Info "登录类型说明:"
        Write-Host "  2 = 交互式登录（本地登录）"
        Write-Host "  3 = 网络登录（共享文件夹、IIS等）"
        Write-Host "  4 = 批处理登录（计划任务）"
        Write-Host "  5 = 服务登录"
        Write-Host "  7 = 解锁"
        Write-Host "  10 = 远程桌面 (RDP)"
        Write-Host "  11 = 缓存交互式登录"

        # 导出 CSV
        Ensure-OutputDir
        $outFile = Join-Path $OutputDir "login_success_$(Get-Timestamp).csv"
        $loginDetails | Export-Csv -Path $outFile -NoTypeInformation -Encoding UTF8
        Write-Success "登录成功明细已导出: $outFile"

    } catch {
        Write-ErrorMsg "获取登录成功事件失败: $($_.Exception.Message)"
        if ($_.Exception.Message -like "*未找到任何事件*") {
            Write-Info "可能原因：24 小时内无成功登录事件，或无权限访问 Security 日志"
        }
    }

    Write-Host ""

    # ---- 登录失败统计（4625） ----
    Write-Info "【1.2 登录失败统计（Event ID 4625）】"
    try {
        $failedLogons = Get-WinEvent -FilterHashtable @{
            LogName   = "Security"
            ID        = 4625
            StartTime = $startTime
        } -MaxEvents 500 -ErrorAction Stop

        Write-Warn "失败登录事件数: $($failedLogons.Count)"

        # 提取详情
        $failedDetails = $failedLogons | ForEach-Object {
            $xml = [xml]$_.ToXml()
            $props = @{}
            foreach ($data in $xml.Event.EventData.Data) {
                $props[$data.Name] = $data.'#text'
            }
            [PSCustomObject]@{
                TimeCreated   = $_.TimeCreated
                TargetUser    = $props.TargetUserName
                IPAddress     = $props.IpAddress
                Workstation   = $props.WorkstationName
                FailureReason = $props.Status
                LogonType     = $props.LogonType
            }
        }

        # 按来源 IP 统计（暴力破解检测）
        Write-Info ""
        Write-Warn "可疑来源 IP (失败次数 Top 10) —— 可能的暴力破解:"
        $failedDetails | Where-Object { $_.IPAddress -and $_.IPAddress -ne "-" } |
            Group-Object IPAddress | Sort-Object Count -Descending |
            Select-Object -First 10 @{Name='来源IP';Expression={$_.Name}}, Count |
            Format-Table -AutoSize | Out-String | ForEach-Object { Write-Host "  $_" }

        # 按目标用户统计
        Write-Info "被攻击用户 Top 10:"
        $failedDetails | Where-Object { $_.TargetUser } |
            Group-Object TargetUser | Sort-Object Count -Descending |
            Select-Object -First 10 @{Name='目标用户';Expression={$_.Name}}, Count |
            Format-Table -AutoSize | Out-String | ForEach-Object { Write-Host "  $_" }

        # 失败原因说明
        Write-Info "常见失败状态码:"
        Write-Host "  0xC0000064 = 用户名不存在"
        Write-Host "  0xC000006A = 密码错误"
        Write-Host "  0xC0000234 = 账户已锁定"
        Write-Host "  0xC0000072 = 账户已禁用"
        Write-Host "  0xC0000071 = 密码已过期"
        Write-Host "  0xC0000193 = 账户已过期"

        # 导出 CSV
        Ensure-OutputDir
        $outFile = Join-Path $OutputDir "login_failed_$(Get-Timestamp).csv"
        $failedDetails | Export-Csv -Path $outFile -NoTypeInformation -Encoding UTF8
        Write-Success "登录失败明细已导出: $outFile"

        # 暴力破解检测
        Write-Info ""
        Write-Info "【1.3 暴力破解检测】"
        $threshold = 5
        $suspiciousIPs = $failedDetails | Where-Object { $_.IPAddress -and $_.IPAddress -ne "-" } |
            Group-Object IPAddress | Where-Object { $_.Count -ge $threshold } |
            Sort-Object Count -Descending

        if ($suspiciousIPs) {
            Write-Warn "检测到 $($suspiciousIPs.Count) 个 IP 失败登录超过 $threshold 次:"
            $suspiciousIPs | ForEach-Object {
                Write-Warn "  - $($_.Name) : $($_.Count) 次失败"
            }
            Write-Warn "建议：检查防火墙规则，考虑封禁这些 IP"
        } else {
            Write-Success "未检测到明显的暴力破解行为（阈值: $threshold 次）"
        }

    } catch {
        Write-ErrorMsg "获取登录失败事件失败: $($_.Exception.Message)"
        if ($_.Exception.Message -like "*未找到任何事件*") {
            Write-Info "可能原因：24 小时内无失败登录事件，或未启用登录审计策略"
        }
    }

    Write-Host ""
}

# ============================================================
# 案例 2：系统安全基线检查
# ============================================================
function Invoke-SecurityBaselineCheck {
    Write-Section "案例 2：系统安全基线检查"

    $isAdmin = Test-IsAdmin
    if (-not $isAdmin) {
        Write-Warn "当前非管理员权限，部分检查可能不完整"
    }

    $results = @()

    # 2.1 防火墙状态
    Write-Info "【2.1 防火墙状态】"
    try {
        $firewallProfiles = Get-NetFirewallProfile -ErrorAction Stop
        foreach ($profile in $firewallProfiles) {
            $status = if ($profile.Enabled) { "已启用" } else { "已禁用" }
            $risk = if ($profile.Enabled) { "低" } else { "高" }
            $level = if ($profile.Enabled) { "PASS" } else { "FAIL" }
            Write-Host "  $($profile.Name) 配置文件: $status" -ForegroundColor $(if ($profile.Enabled) { "Green" } else { "Red" })

            $results += [PSCustomObject]@{
                Category    = "防火墙"
                CheckItem   = "$($profile.Name) 配置文件"
                Status      = $status
                RiskLevel   = $risk
                Passed      = ($profile.Enabled)
                Recommendation = if (-not $profile.Enabled) { "启用 $($profile.Name) 防火墙配置文件" } else { "" }
            }
        }
    } catch {
        Write-ErrorMsg "  检查防火墙失败: $($_.Exception.Message)"
        $results += [PSCustomObject]@{
            Category    = "防火墙"
            CheckItem   = "防火墙状态"
            Status      = "未知"
            RiskLevel   = "未知"
            Passed      = $false
            Recommendation = "无法获取防火墙状态，需手动检查"
        }
    }
    Write-Host ""

    # 2.2 关键服务状态
    Write-Info "【2.2 关键安全服务状态】"
    $criticalServices = @(
        @{Name="MpsSvc";       Display="Windows Defender 防火墙"; Expected="Running"; StartType="Automatic"}
        @{Name="wuauserv";     Display="Windows Update";          Expected="Running"; StartType="Automatic"}
        @{Name="WinDefend";    Display="Windows Defender 防病毒";  Expected="Running"; StartType="Automatic"}
        @{Name="EventLog";     Display="Windows Event Log";       Expected="Running"; StartType="Automatic"}
        @{Name="TermService";  Display="远程桌面服务";             Expected="Stopped"; StartType="Manual"}
    )

    foreach ($svcInfo in $criticalServices) {
        try {
            $svc = Get-Service -Name $svcInfo.Name -ErrorAction Stop
            $statusOk = ($svc.Status -eq $svcInfo.Expected)
            $level = if ($statusOk) { "PASS" } else { "WARN" }
            $color = if ($statusOk) { "Green" } else { "Yellow" }

            Write-Host "  $($svcInfo.Display): $($svc.Status) (启动类型: $($svc.StartType))" -ForegroundColor $color

            $results += [PSCustomObject]@{
                Category    = "服务"
                CheckItem   = $svcInfo.Display
                Status      = $svc.Status.ToString()
                RiskLevel   = if ($statusOk) { "低" } else { "中" }
                Passed      = $statusOk
                Recommendation = if (-not $statusOk) { "检查服务 $($svcInfo.Name)，预期状态: $($svcInfo.Expected)" } else { "" }
            }
        } catch {
            Write-Warn "  $($svcInfo.Display): 未找到服务"
            $results += [PSCustomObject]@{
                Category    = "服务"
                CheckItem   = $svcInfo.Display
                Status      = "未安装/未找到"
                RiskLevel   = "未知"
                Passed      = $false
                Recommendation = "确认服务是否存在"
            }
        }
    }
    Write-Host ""

    # 2.3 注册表安全项
    Write-Info "【2.3 注册表安全配置】"
    $regChecks = @(
        @{
            Path = "HKLM:\System\CurrentControlSet\Control\Terminal Server"
            Name = "fDenyTSConnections"
            Expected = 1
            Display = "禁用 RDP 远程桌面"
            Risk = "高"
            Desc = "0=启用, 1=禁用"
        }
        @{
            Path = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
            Name = "EnableLUA"
            Expected = 1
            Display = "UAC 用户账户控制"
            Risk = "中"
            Desc = "0=禁用, 1=启用"
        }
        @{
            Path = "HKLM:\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters"
            Name = "AutoShareServer"
            Expected = 0
            Display = "禁用管理共享 (ADMIN$)"
            Risk = "中"
            Desc = "0=禁用, 1=启用；值不存在表示默认启用"
        }
    )

    foreach ($check in $regChecks) {
        try {
            $value = Get-ItemProperty -Path $check.Path -Name $check.Name -ErrorAction Stop
            $actual = $value.$($check.Name)
            $passed = ($actual -eq $check.Expected)
            $color = if ($passed) { "Green" } else { "Red" }

            Write-Host "  $($check.Display): $actual" -ForegroundColor $color

            $results += [PSCustomObject]@{
                Category    = "注册表"
                CheckItem   = $check.Display
                Status      = "值: $actual"
                RiskLevel   = $check.Risk
                Passed      = $passed
                Recommendation = if (-not $passed) { "建议设置 $($check.Name) = $($check.Expected) ($($check.Desc))" } else { "" }
            }
        } catch {
            # 值不存在的情况
            Write-Warn "  $($check.Display): 未配置（值不存在）"
            $results += [PSCustomObject]@{
                Category    = "注册表"
                CheckItem   = $check.Display
                Status      = "未配置"
                RiskLevel   = $check.Risk
                Passed      = $false
                Recommendation = "建议配置注册表项: $($check.Path)\$($check.Name) = $($check.Expected)"
            }
        }
    }
    Write-Host ""

    # 2.4 SMBv1 状态
    Write-Info "【2.4 SMBv1 状态（应禁用）】"
    try {
        $smb1 = Get-WindowsOptionalFeature -Online -FeatureName SMB1Protocol -ErrorAction Stop
        $smb1Enabled = ($smb1.State -eq "Enabled")
        $color = if (-not $smb1Enabled) { "Green" } else { "Red" }
        Write-Host "  SMB1Protocol: $($smb1.State)" -ForegroundColor $color

        $results += [PSCustomObject]@{
            Category    = "协议"
            CheckItem   = "SMBv1 协议"
            Status      = $smb1.State
            RiskLevel   = "高"
            Passed      = (-not $smb1Enabled)
            Recommendation = if ($smb1Enabled) { "强烈建议禁用 SMBv1，存在严重安全风险（如永恒之蓝）" } else { "" }
        }
    } catch {
        Write-Warn "  无法检查 SMBv1 状态: $($_.Exception.Message)"
        $results += [PSCustomObject]@{
            Category    = "协议"
            CheckItem   = "SMBv1 协议"
            Status      = "未知"
            RiskLevel   = "未知"
            Passed      = $false
            Recommendation = "手动检查 SMBv1 是否启用"
        }
    }
    Write-Host ""

    # 2.5 账户与密码策略
    Write-Info "【2.5 账户策略】"
    try {
        # 使用 net accounts 获取本地账户策略
        $accountsOutput = & net accounts 2>$null
        Write-Host "  本地账户策略:"
        $accountsOutput | Select-Object -Skip 0 | ForEach-Object {
            if ($_ -match '\S') { Write-Host "    $_" }
        }

        $results += [PSCustomObject]@{
            Category    = "账户策略"
            CheckItem   = "密码策略检查"
            Status      = "已检查（详见上方输出）"
            RiskLevel   = "中"
            Passed      = $true
            Recommendation = "确保密码长度 >= 8，启用复杂度要求，设置账户锁定策略"
        }
    } catch {
        Write-ErrorMsg "  获取账户策略失败: $($_.Exception.Message)"
    }
    Write-Host ""

    # 2.6 汇总报告
    Write-Info "【2.6 基线检查汇总】"
    $passed = ($results | Where-Object { $_.Passed }).Count
    $failed = ($results | Where-Object { -not $_.Passed }).Count
    $total = $results.Count

    Write-Host "  总检查项: $total"
    Write-Host "  通过: $passed" -ForegroundColor Green
    Write-Host "  未通过/警告: $failed" -ForegroundColor $(if ($failed -gt 0) { "Red" } else { "Green" })

    if ($failed -gt 0) {
        Write-Warn "未通过的检查项:"
        $results | Where-Object { -not $_.Passed } | ForEach-Object {
            Write-Warn "  [$($_.Category)] $($_.CheckItem) - $($_.Status)"
            if ($_.Recommendation) {
                Write-Host "    建议: $($_.Recommendation)" -ForegroundColor Yellow
            }
        }
    }

    # 导出报告
    Ensure-OutputDir
    $reportFile = Join-Path $OutputDir "security_baseline_$(Get-Timestamp).csv"
    $results | Export-Csv -Path $reportFile -NoTypeInformation -Encoding UTF8
    Write-Success "基线检查报告已导出: $reportFile"

    Write-Host ""
}

# ============================================================
# 案例 3：进程与网络关联分析（威胁狩猎）
# ============================================================
function Invoke-NetworkProcessAnalysis {
    Write-Section "案例 3：进程与网络关联分析（威胁狩猎）"

    $isAdmin = Test-IsAdmin
    if (-not $isAdmin) {
        Write-Warn "当前非管理员权限，部分网络信息可能不完整"
    }

    # 3.1 网络连接概览
    Write-Info "【3.1 网络连接状态概览】"
    try {
        $connections = Get-NetTCPConnection -ErrorAction Stop
        $stateGroup = $connections | Group-Object State | Sort-Object Count -Descending

        Write-Host "  总连接数: $($connections.Count)"
        Write-Host "  按状态分布:"
        $stateGroup | ForEach-Object {
            Write-Host "    $($_.Name): $($_.Count)"
        }
    } catch {
        Write-ErrorMsg "  获取网络连接失败: $($_.Exception.Message)"
        return
    }
    Write-Host ""

    # 3.2 监听端口分析
    Write-Info "【3.2 监听端口列表（含进程信息）】"
    try {
        $listeners = Get-NetTCPConnection -State Listen -ErrorAction Stop |
            Sort-Object LocalPort

        $listenerDetails = foreach ($conn in $listeners) {
            $proc = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue
            $procPath = if ($proc) { $proc.Path } else { "未知" }
            $procName = if ($proc) { $proc.ProcessName } else { "未知(PID:$($conn.OwningProcess))" }

            [PSCustomObject]@{
                LocalAddress = $conn.LocalAddress
                LocalPort    = $conn.LocalPort
                ProcessId    = $conn.OwningProcess
                ProcessName  = $procName
                ProcessPath  = $procPath
            }
        }

        $listenerDetails | Format-Table -AutoSize | Out-String | ForEach-Object { Write-Host "  $_" }

        # 导出
        Ensure-OutputDir
        $outFile = Join-Path $OutputDir "listening_ports_$(Get-Timestamp).csv"
        $listenerDetails | Export-Csv -Path $outFile -NoTypeInformation -Encoding UTF8
        Write-Success "监听端口列表已导出: $outFile"

    } catch {
        Write-ErrorMsg "  获取监听端口失败: $($_.Exception.Message)"
    }
    Write-Host ""

    # 3.3 外部连接分析
    Write-Info "【3.3 对外建立连接分析（排除本地/内网）】"
    try {
        $established = Get-NetTCPConnection -State Established -ErrorAction Stop

        $externalConns = $established | Where-Object {
            $_.RemoteAddress -notlike "127.*" -and
            $_.RemoteAddress -notlike "192.168.*" -and
            $_.RemoteAddress -notlike "10.*" -and
            $_.RemoteAddress -notlike "172.1[6-9].*" -and
            $_.RemoteAddress -notlike "172.2[0-9].*" -and
            $_.RemoteAddress -notlike "172.3[0-1].*" -and
            $_.RemoteAddress -notlike "::1" -and
            $_.RemoteAddress -notlike "fe80:*"
        }

        Write-Host "  对外连接数: $($externalConns.Count)"

        if ($externalConns.Count -gt 0) {
            $extDetails = $externalConns | Select-Object -First 20 | ForEach-Object {
                $proc = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue
                [PSCustomObject]@{
                    RemoteAddress = $_.RemoteAddress
                    RemotePort    = $_.RemotePort
                    LocalPort     = $_.LocalPort
                    ProcessName   = if ($proc) { $proc.ProcessName } else { "未知" }
                    ProcessId     = $_.OwningProcess
                }
            }

            $extDetails | Format-Table -AutoSize | Out-String | ForEach-Object { Write-Host "  $_" }
            Write-Host "  (仅显示前 20 条，完整数据请查看导出文件)" -ForegroundColor Gray

            # 导出
            Ensure-OutputDir
            $outFile = Join-Path $OutputDir "external_connections_$(Get-Timestamp).csv"
            $externalConns | ForEach-Object {
                $proc = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue
                [PSCustomObject]@{
                    RemoteAddress = $_.RemoteAddress
                    RemotePort    = $_.RemotePort
                    LocalAddress  = $_.LocalAddress
                    LocalPort     = $_.LocalPort
                    ProcessName   = if ($proc) { $proc.ProcessName } else { "未知" }
                    ProcessId     = $_.OwningProcess
                    ProcessPath   = if ($proc) { $proc.Path } else { "未知" }
                }
            } | Export-Csv -Path $outFile -NoTypeInformation -Encoding UTF8
            Write-Success "对外连接明细已导出: $outFile"
        }
    } catch {
        Write-ErrorMsg "  分析外部连接失败: $($_.Exception.Message)"
    }
    Write-Host ""

    # 3.4 可疑进程检测
    Write-Info "【3.4 可疑进程检测（启发式）】"
    Write-Host "  检查规则:"
    Write-Host "    - 进程路径在临时目录或用户目录"
    Write-Host "    - 进程名与系统进程名相似但路径不对"
    Write-Host "    - 无公司签名信息的进程"
    Write-Host ""

    try {
        $suspicious = @()
        $processes = Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.Path }

        foreach ($proc in $processes) {
            $reasons = @()

            # 检查是否在可疑路径
            if ($proc.Path -like "*\AppData\*" -or $proc.Path -like "*\Temp\*" -or
                $proc.Path -like "*\Public\*" -or $proc.Path -like "*\Downloads\*") {
                $reasons += "路径可疑"
            }

            # 检查是否有签名
            try {
                $sig = Get-AuthenticodeSignature -FilePath $proc.Path -ErrorAction SilentlyContinue
                if ($sig.Status -ne "Valid") {
                    $reasons += "签名无效/无签名"
                }
            } catch {
                # 忽略签名检查错误
            }

            if ($reasons.Count -gt 0) {
                $suspicious += [PSCustomObject]@{
                    ProcessName = $proc.ProcessName
                    ProcessId   = $proc.Id
                    Path        = $proc.Path
                    Reasons     = $reasons -join "; "
                    CPU         = [math]::Round($proc.CPU, 2)
                }
            }
        }

        if ($suspicious.Count -gt 0) {
            Write-Warn "发现 $($suspicious.Count) 个可能可疑的进程:"
            $suspicious | Select-Object -First 15 ProcessName, ProcessId, Reasons, Path |
                Format-Table -AutoSize -Wrap | Out-String | ForEach-Object { Write-Host "  $_" }
            Write-Host "  注意：这只是启发式检测，结果仅供参考，需人工进一步确认" -ForegroundColor Yellow
        } else {
            Write-Success "未发现明显可疑的进程（启发式检测）"
        }

        # 导出
        if ($suspicious.Count -gt 0) {
            Ensure-OutputDir
            $outFile = Join-Path $OutputDir "suspicious_processes_$(Get-Timestamp).csv"
            $suspicious | Export-Csv -Path $outFile -NoTypeInformation -Encoding UTF8
            Write-Success "可疑进程列表已导出: $outFile"
        }
    } catch {
        Write-ErrorMsg "  可疑进程检测失败: $($_.Exception.Message)"
    }

    Write-Host ""
}

# ============================================================
# 案例 4：安全日志导出
# ============================================================
function Invoke-SecurityLogExport {
    Write-Section "案例 4：安全日志导出"

    $isAdmin = Test-IsAdmin
    if (-not $isAdmin) {
        Write-Warn "当前非管理员权限，可能无法访问 Security 日志"
    }

    # 导出时间范围（最近 24 小时）
    $startTime = (Get-Date).AddHours(-24)
    Write-Info "导出时间范围: $startTime ~ $(Get-Date)"
    Write-Host ""

    # 4.1 重要安全事件类型
    $eventTypes = @(
        @{ID = 4624; Name = "登录成功"; LogName = "Security"}
        @{ID = 4625; Name = "登录失败"; LogName = "Security"}
        @{ID = 4634; Name = "账户注销"; LogName = "Security"}
        @{ID = 4648; Name = "显式凭据登录"; LogName = "Security"}
        @{ID = 4672; Name = "特殊权限登录"; LogName = "Security"}
        @{ID = 4720; Name = "创建用户账户"; LogName = "Security"}
        @{ID = 4726; Name = "删除用户账户"; LogName = "Security"}
        @{ID = 4728; Name = "添加成员到全局组"; LogName = "Security"}
        @{ID = 4732; Name = "添加成员到本地组"; LogName = "Security"}
        @{ID = 4740; Name = "账户锁定"; LogName = "Security"}
        @{ID = 4698; Name = "创建计划任务"; LogName = "Security"}
        @{ID = 4699; Name = "删除计划任务"; LogName = "Security"}
        @{ID = 7045; Name = "服务安装"; LogName = "System"}
        @{ID = 104;  Name = "日志被清除"; LogName = "System"}
    )

    Ensure-OutputDir
    $timestamp = Get-Timestamp

    foreach ($eventType in $eventTypes) {
        try {
            Write-Info "正在导出: Event ID $($eventType.ID) ($($eventType.Name))..."

            $events = Get-WinEvent -FilterHashtable @{
                LogName   = $eventType.LogName
                ID        = $eventType.ID
                StartTime = $startTime
            } -MaxEvents 200 -ErrorAction Stop

            if ($events.Count -gt 0) {
                # 提取关键字段
                $eventDetails = $events | ForEach-Object {
                    [PSCustomObject]@{
                        TimeCreated = $_.TimeCreated
                        EventID     = $_.Id
                        Level       = $_.LevelDisplayName
                        Provider    = $_.ProviderName
                        MachineName = $_.MachineName
                        Message     = $_.Message -split "`n" | Select-Object -First 3 | Out-String
                    }
                }

                $safeName = $eventType.Name -replace '[\\/:*?"<>|]', '_'
                $outFile = Join-Path $OutputDir "event_$($eventType.ID)_${safeName}_${timestamp}.csv"
                $eventDetails | Export-Csv -Path $outFile -NoTypeInformation -Encoding UTF8
                Write-Success "  导出 $($events.Count) 条 -> $outFile"
            } else {
                Write-Host "  无事件记录" -ForegroundColor Gray
            }
        } catch {
            if ($_.Exception.Message -like "*未找到任何事件*") {
                Write-Host "  无事件记录" -ForegroundColor Gray
            } else {
                Write-ErrorMsg "  导出失败: $($_.Exception.Message)"
            }
        }
    }

    Write-Host ""
    Write-Info "【4.2 导出汇总】"
    Write-Host "  输出目录: $OutputDir"
    $exportedFiles = Get-ChildItem -Path $OutputDir -Filter "*_${timestamp}.csv"
    Write-Host "  本次导出文件数: $($exportedFiles.Count)"
    Write-Host ""
    Write-Success "日志导出完成！"
    Write-Host ""
}

# ============================================================
# 主程序入口
# ============================================================

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  PowerShell 安全案例集" -ForegroundColor Cyan
Write-Host "  Security Cases for PowerShell" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# 检查管理员状态
$adminStatus = if (Test-IsAdmin) { "已获得管理员权限" } else { "未获得管理员权限（部分功能受限）" }
Write-Info "当前权限: $adminStatus"
Write-Info "输出目录: $OutputDir"
Write-Host ""

# 按模式执行
switch ($Mode) {
    "help" {
        Show-Help
    }
    "login" {
        Invoke-LoginAudit
    }
    "baseline" {
        Invoke-SecurityBaselineCheck
    }
    "network" {
        Invoke-NetworkProcessAnalysis
    }
    "export" {
        Invoke-SecurityLogExport
    }
    "all" {
        Write-Info "运行所有安全案例..."
        Write-Host ""

        Invoke-LoginAudit
        Invoke-SecurityBaselineCheck
        Invoke-NetworkProcessAnalysis
        Invoke-SecurityLogExport

        Write-Section "全部案例执行完毕"
        Write-Success "所有安全案例已运行完成"
        Write-Info "输出文件保存在: $OutputDir"
        Write-Host ""
    }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  免责声明" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  本脚本仅供学习、研究和授权环境下的安全运维使用。"
Write-Host "  任何未经授权的测试或攻击行为均属违法。"
Write-Host "  使用者应遵守所在地区法律法规，对自己的行为负责。"
Write-Host ""
