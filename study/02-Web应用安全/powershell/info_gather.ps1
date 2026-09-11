<#
.SYNOPSIS
    Windows 信息收集工具 - PowerShell 安全实战
.DESCRIPTION
    收集 Windows 系统的安全相关信息：系统信息、网络配置、用户、
    进程、服务、共享、防火墙规则等
.NOTES
    仅用于安全学习和授权测试
.EXAMPLE
    .\info_gather.ps1
    .\info_gather.ps1 -Export report.txt
#>

param(
    [string]$Export
)

Write-Host @"
========================================
  Windows 安全信息收集工具
  仅用于安全学习和授权测试
========================================
"@ -ForegroundColor Cyan

$output = @()

function Add-Section($title) {
    $line = "=" * 50
    Write-Host "`n$line" -ForegroundColor Cyan
    Write-Host "  $title" -ForegroundColor Cyan
    Write-Host "$line" -ForegroundColor Cyan
    $output += "`n$line`n  $title`n$line`n"
}

# ===== 系统信息 =====
Add-Section "1. 系统信息"
$os = Get-CimInstance Win32_OperatingSystem
$cs = Get-CimInstance Win32_ComputerSystem
Write-Host "  主机名:    $($cs.Name)" -ForegroundColor White
Write-Host "  域名:      $($cs.Domain)" -ForegroundColor White
Write-Host "  操作系统:  $($os.Caption)" -ForegroundColor White
Write-Host "  版本:      $($os.Version)" -ForegroundColor White
Write-Host "  架构:      $($os.OSArchitecture)" -ForegroundColor White
Write-Host "  内存:      $([math]::Round($os.TotalVisibleMemorySize/1MB,2)) GB" -ForegroundColor White
Write-Host "  安装时间:  $($os.InstallDate)" -ForegroundColor White
Write-Host "  最后启动:  $($os.LastBootUpTime)" -ForegroundColor White

# ===== 已安装补丁 =====
Add-Section "2. 已安装补丁"
$hotfixes = Get-HotFix | Sort-Object InstalledOn -Descending
Write-Host "  补丁总数: $($hotfixes.Count)" -ForegroundColor White
$hotfixes | Select-Object -First 10 | ForEach-Object {
    Write-Host "  $($_.HotFixID)  $($_.Description)  $($_.InstalledOn)" -ForegroundColor Gray
}

# ===== 网络配置 =====
Add-Section "3. 网络配置"
$ipConfig = Get-NetIPConfiguration | Where-Object { $_.IPv4DefaultGateway }
foreach ($nic in $ipConfig) {
    Write-Host "  接口:     $($nic.InterfaceAlias)" -ForegroundColor White
    Write-Host "  IP 地址:  $($nic.IPv4.Address.IPAddress)" -ForegroundColor White
    Write-Host "  网关:     $($nic.IPv4DefaultGateway.NextHop)" -ForegroundColor White
    if ($nic.DNSServer) {
        Write-Host "  DNS:      $($nic.DNSServer.ServerAddresses -join ', ')" -ForegroundColor White
    }
    Write-Host ""
}

# ===== 监听端口 =====
Add-Section "4. 监听端口"
$listeners = Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
    Where-Object { $_.LocalAddress -ne '127.0.0.1' -and $_.LocalAddress -ne '::1' } |
    Sort-Object LocalPort
$portMap = @{
    22='SSH'; 80='HTTP'; 443='HTTPS'; 445='SMB'; 1433='MSSQL';
    3306='MySQL'; 3389='RDP'; 5985='WinRM'; 8080='HTTP-Alt'
}
foreach ($conn in $listeners) {
    $svc = if ($portMap.ContainsKey($conn.LocalPort)) { $portMap[$conn.LocalPort] } else { "" }
    $proc = try { (Get-Process -Id $conn.OwningProcess -ErrorAction Stop).Name } catch { "N/A" }
    Write-Host "  $($conn.LocalAddress):$($conn.LocalPort)  PID:$($conn.OwningProcess)  $proc  $svc" -ForegroundColor Yellow
}

# ===== 用户和组 =====
Add-Section "5. 本地用户"
$users = Get-LocalUser
foreach ($u in $users) {
    $status = if ($u.Enabled) { "启用" } else { "禁用" }
    $color = if ($u.Enabled) { "Green" } else { "DarkGray" }
    Write-Host "  $($u.Name)  [$status]  最后登录: $($u.LastLogon)" -ForegroundColor $color
}

Add-Section "6. 管理员组成员"
$admins = Get-LocalGroupMember -Group "Administrators"
foreach ($a in $admins) {
    Write-Host "  $($a.Name)  ($($a.ObjectClass))" -ForegroundColor Red
}

# ===== 进程（高风险） =====
Add-Section "7. 高风险进程"
$suspectNames = @("cmd", "powershell", "wmic", "nc", "netcat", "mimikatz",
                   "procdump", "hashcat", "john", "hydra", "nmap", "wireshark")
$processes = Get-Process
foreach ($p in $processes) {
    if ($p.Name -match ($suspectNames -join '|')) {
        Write-Host "  [!] $($p.Name) (PID: $($p.Id))  路径: $($p.Path)" -ForegroundColor Red
    }
}

# ===== 服务 =====
Add-Section "8. 运行中的服务"
$services = Get-Service | Where-Object { $_.Status -eq 'Running' }
Write-Host "  运行中的服务数: $($services.Count)" -ForegroundColor White
$services | Select-Object -First 20 | ForEach-Object {
    Write-Host "  $($_.Name) - $($_.DisplayName)" -ForegroundColor Gray
}

# ===== 共享 =====
Add-Section "9. 网络共享"
$shares = Get-SmbShare | Where-Object { $_.Name -notmatch '\$' -and $_.Name -ne 'IPC$' }
if ($shares) {
    foreach ($s in $shares) {
        Write-Host "  $($s.Name)  ->  $($s.Path)" -ForegroundColor Yellow
    }
} else {
    $allShares = Get-SmbShare
    foreach ($s in $allShares) {
        Write-Host "  $($s.Name)  ->  $($s.Path)" -ForegroundColor DarkGray
    }
}

# ===== 防火墙规则 =====
Add-Section "10. 防火墙规则（入站允许）"
$fwRules = Get-NetFirewallRule -Direction Inbound -Enabled True -Action Allow -ErrorAction SilentlyContinue
Write-Host "  入站允许规则数: $($fwRules.Count)" -ForegroundColor White
$fwRules | Select-Object -First 15 | ForEach-Object {
    Write-Host "  $($_.DisplayName)  ($($_.Profile))" -ForegroundColor Gray
}

# ===== 计划任务 =====
Add-Section "11. 计划任务（非微软）"
try {
    $tasks = Get-ScheduledTask | Where-Object {
        $_.State -ne 'Disabled' -and $_.TaskPath -notmatch '\\Microsoft\\'
    } | Select-Object -First 20
    foreach ($t in $tasks) {
        Write-Host "  $($t.TaskName)  ($($t.TaskPath))  [$($t.State)]" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  [!] 无法读取计划任务" -ForegroundColor Red
}

# ===== 自动启动项 =====
Add-Section "12. 自动启动项"
$startup = Get-CimInstance Win32_StartupCommand
foreach ($s in $startup) {
    Write-Host "  $($s.Name)" -ForegroundColor Yellow
    Write-Host "    命令: $($s.Command)" -ForegroundColor Gray
    Write-Host "    位置: $($s.Location)" -ForegroundColor Gray
}

# ===== 总结 =====
Add-Section "收集完成"
Write-Host "  系统信息收集完毕，请人工审查以上内容" -ForegroundColor Green
Write-Host "  重点关注: 高风险进程、管理员成员、开放端口、共享`n" -ForegroundColor Yellow

# 导出报告
if ($Export) {
    $output | Out-File $Export -Encoding UTF8
    Write-Host "[*] 报告已导出到: $Export" -ForegroundColor Green
}
