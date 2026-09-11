# ============================================================
# Windows 安全加固脚本
# 版本：v1.0
# 适用系统：Windows 10 / Windows 11 / Windows Server 2016+
# 运行要求：以管理员身份运行 PowerShell
# ============================================================

<#
.SYNOPSIS
    Windows 系统安全加固脚本
.DESCRIPTION
    本脚本用于加固 Windows 系统安全，包括账户策略、审核策略、服务加固、
    防火墙配置、注册表加固、UAC 配置、RDP 安全配置等多个方面。
    执行前请确认已了解脚本功能，并做好系统备份。
.NOTES
    运行命令：powershell -ExecutionPolicy Bypass -File .\windows_hardening.ps1
    执行前建议：创建系统还原点或快照
#>

# ============================================================
# 初始化部分
# ============================================================

# 检查是否以管理员身份运行
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "[-] 错误：请以管理员身份运行此脚本！" -ForegroundColor Red
    Write-Host "[-] 请右键点击 PowerShell，选择'以管理员身份运行'" -ForegroundColor Red
    exit 1
}

Write-Host "[*] ============================================================" -ForegroundColor Cyan
Write-Host "[*] Windows 系统安全加固脚本 v1.0" -ForegroundColor Cyan
Write-Host "[*] ============================================================" -ForegroundColor Cyan
Write-Host ""

# 创建日志文件
$logPath = "C:\Windows\Temp\hardening_log_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
"=== Windows 安全加固日志 - $(Get-Date) ===" | Out-File -FilePath $logPath -Encoding utf8

# 日志函数
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    $logEntry | Out-File -FilePath $logPath -Append -Encoding utf8
    
    switch ($Level) {
        "INFO"  { Write-Host "[+] $Message" -ForegroundColor Green }
        "WARN"  { Write-Host "[!] $Message" -ForegroundColor Yellow }
        "ERROR" { Write-Host "[-] $Message" -ForegroundColor Red }
        "SKIP"  { Write-Host "[=] $Message" -ForegroundColor Gray }
    }
}

Write-Log "脚本开始执行"
Write-Log "日志文件路径：$logPath"

# ============================================================
# 一、账户策略加固
# ============================================================

Write-Host ""
Write-Host "[*] ============================================================" -ForegroundColor Cyan
Write-Host "[*] 一、账户策略加固" -ForegroundColor Cyan
Write-Host "[*] ============================================================" -ForegroundColor Cyan
Write-Host ""

try {
    # 导出当前安全策略
    $secpolPath = "C:\Windows\Temp\secpol_export.cfg"
    secedit /export /cfg $secpolPath /areas SECURITYPOLICY | Out-Null
    Write-Log "已导出当前安全策略到 $secpolPath"

    # 读取配置文件内容
    $secpolContent = Get-Content $secpolPath -Raw

    # 1.1 密码策略配置
    Write-Log "正在配置密码策略..."

    # 密码必须符合复杂性要求
    if ($secpolContent -match "PasswordComplexity\s*=\s*\d") {
        $secpolContent = $secpolContent -replace "PasswordComplexity\s*=\s*\d", "PasswordComplexity = 1"
    } else {
        $secpolContent += "`r`nPasswordComplexity = 1"
    }

    # 密码长度最小值 = 14个字符
    if ($secpolContent -match "MinimumPasswordLength\s*=\s*\d+") {
        $secpolContent = $secpolContent -replace "MinimumPasswordLength\s*=\s*\d+", "MinimumPasswordLength = 14"
    } else {
        $secpolContent += "`r`nMinimumPasswordLength = 14"
    }

    # 密码最短使用期限 = 1天
    if ($secpolContent -match "MinimumPasswordAge\s*=\s*\d+") {
        $secpolContent = $secpolContent -replace "MinimumPasswordAge\s*=\s*\d+", "MinimumPasswordAge = 1"
    } else {
        $secpolContent += "`r`nMinimumPasswordAge = 1"
    }

    # 密码最长使用期限 = 90天
    if ($secpolContent -match "MaximumPasswordAge\s*=\s*\d+") {
        $secpolContent = $secpolContent -replace "MaximumPasswordAge\s*=\s*\d+", "MaximumPasswordAge = 90"
    } else {
        $secpolContent += "`r`nMaximumPasswordAge = 90"
    }

    # 强制密码历史 = 24个记住的密码
    if ($secpolContent -match "PasswordHistorySize\s*=\s*\d+") {
        $secpolContent = $secpolContent -replace "PasswordHistorySize\s*=\s*\d+", "PasswordHistorySize = 24"
    } else {
        $secpolContent += "`r`nPasswordHistorySize = 24"
    }

    # 用可还原的加密来存储密码 = 禁用
    if ($secpolContent -match "ClearTextPassword\s*=\s*\d") {
        $secpolContent = $secpolContent -replace "ClearTextPassword\s*=\s*\d", "ClearTextPassword = 0"
    } else {
        $secpolContent += "`r`nClearTextPassword = 0"
    }

    # 1.2 账户锁定策略
    Write-Log "正在配置账户锁定策略..."

    # 账户锁定阈值 = 5次无效登录
    if ($secpolContent -match "LockoutBadCount\s*=\s*\d+") {
        $secpolContent = $secpolContent -replace "LockoutBadCount\s*=\s*\d+", "LockoutBadCount = 5"
    } else {
        $secpolContent += "`r`nLockoutBadCount = 5"
    }

    # 账户锁定时间 = 30分钟
    if ($secpolContent -match "LockoutDuration\s*=\s*\d+") {
        $secpolContent = $secpolContent -replace "LockoutDuration\s*=\s*\d+", "LockoutDuration = 30"
    } else {
        $secpolContent += "`r`nLockoutDuration = 30"
    }

    # 重置账户锁定计数器 = 30分钟
    if ($secpolContent -match "ResetLockoutCount\s*=\s*\d+") {
        $secpolContent = $secpolContent -replace "ResetLockoutCount\s*=\s*\d+", "ResetLockoutCount = 30"
    } else {
        $secpolContent += "`r`nResetLockoutCount = 30"
    }

    # 保存修改后的配置
    $secpolContent | Out-File -FilePath $secpolPath -Encoding utf8

    # 导入安全策略
    secedit /configure /db C:\Windows\security\local.sdb /cfg $secpolPath /areas SECURITYPOLICY | Out-Null
    Write-Log "账户策略配置完成"
}
catch {
    Write-Log "账户策略配置失败：$($_.Exception.Message)" "ERROR"
}

# 1.3 禁用 Guest 账户
try {
    Write-Log "正在禁用 Guest 账户..."
    net user guest /active:no | Out-Null
    Write-Log "Guest 账户已禁用"
}
catch {
    Write-Log "禁用 Guest 账户失败：$($_.Exception.Message)" "ERROR"
}

# 1.4 重命名 Administrator 账户（可选，默认不执行，取消注释启用）
<#
try {
    Write-Log "正在重命名 Administrator 账户..."
    $adminSid = New-Object System.Security.Principal.SecurityIdentifier("S-1-5-32-544")
    $adminGroup = $adminSid.Translate([System.Security.Principal.NTAccount])
    # 注意：这里重命名的是管理员账户，需要根据实际情况调整
    # Rename-LocalUser -Name "Administrator" -NewName "WinAdmin"
    Write-Log "Administrator 账户已重命名"
}
catch {
    Write-Log "重命名 Administrator 账户失败：$($_.Exception.Message)" "ERROR"
}
#>

# ============================================================
# 二、审核策略配置
# ============================================================

Write-Host ""
Write-Host "[*] ============================================================" -ForegroundColor Cyan
Write-Host "[*] 二、审核策略配置" -ForegroundColor Cyan
Write-Host "[*] ============================================================" -ForegroundColor Cyan
Write-Host ""

try {
    Write-Log "正在配置高级审核策略..."

    # 2.1 账户登录审核
    auditpol /set /subcategory:"凭据验证" /success:enable /failure:enable | Out-Null
    Write-Log "已启用：凭据验证审核（成功+失败）"

    auditpol /set /subcategory:"Kerberos 身份验证服务" /success:enable /failure:enable | Out-Null
    Write-Log "已启用：Kerberos 身份验证服务审核"

    auditpol /set /subcategory:"Kerberos 服务票据操作" /success:enable /failure:enable | Out-Null
    Write-Log "已启用：Kerberos 服务票据操作审核"

    # 2.2 账户管理审核
    auditpol /set /subcategory:"用户账户管理" /success:enable /failure:enable | Out-Null
    Write-Log "已启用：用户账户管理审核"

    auditpol /set /subcategory:"计算机账户管理" /success:enable /failure:enable | Out-Null
    Write-Log "已启用：计算机账户管理审核"

    auditpol /set /subcategory:"安全组管理" /success:enable /failure:enable | Out-Null
    Write-Log "已启用：安全组管理审核"

    auditpol /set /subcategory:"分发组管理" /success:enable /failure:enable | Out-Null
    Write-Log "已启用：分发组管理审核"

    auditpol /set /subcategory:"其他账户管理事件" /success:enable /failure:enable | Out-Null
    Write-Log "已启用：其他账户管理事件审核"

    # 2.3 登录/注销审核
    auditpol /set /subcategory:"登录" /success:enable /failure:enable | Out-Null
    Write-Log "已启用：登录审核"

    auditpol /set /subcategory:"注销" /success:enable /failure:enable | Out-Null
    Write-Log "已启用：注销审核"

    auditpol /set /subcategory:"账户锁定" /success:enable /failure:enable | Out-Null
    Write-Log "已启用：账户锁定审核"

    auditpol /set /subcategory:"特殊登录" /success:enable /failure:enable | Out-Null
    Write-Log "已启用：特殊登录审核"

    auditpol /set /subcategory:"其他登录/注销事件" /success:enable /failure:enable | Out-Null
    Write-Log "已启用：其他登录/注销事件审核"

    # 2.4 详细追踪（进程创建）
    auditpol /set /subcategory:"进程创建" /success:enable /failure:enable | Out-Null
    Write-Log "已启用：进程创建审核"

    auditpol /set /subcategory:"进程终止" /success:enable /failure:enable | Out-Null
    Write-Log "已启用：进程终止审核"

    # 2.5 对象访问审核
    auditpol /set /subcategory:"文件系统" /failure:enable | Out-Null
    Write-Log "已启用：文件系统访问失败审核"

    auditpol /set /subcategory:"注册表" /failure:enable | Out-Null
    Write-Log "已启用：注册表访问失败审核"

    auditpol /set /subcategory:"筛选平台连接" /failure:enable | Out-Null
    Write-Log "已启用：筛选平台连接失败审核"

    # 2.6 策略更改审核
    auditpol /set /subcategory:"审核策略更改" /success:enable /failure:enable | Out-Null
    Write-Log "已启用：审核策略更改审核"

    auditpol /set /subcategory:"身份验证策略更改" /success:enable /failure:enable | Out-Null
    Write-Log "已启用：身份验证策略更改审核"

    auditpol /set /subcategory:"授权策略更改" /success:enable /failure:enable | Out-Null
    Write-Log "已启用：授权策略更改审核"

    # 2.7 特权使用审核
    auditpol /set /subcategory:"敏感特权使用" /failure:enable | Out-Null
    Write-Log "已启用：敏感特权使用失败审核"

    auditpol /set /subcategory:"其他特权使用事件" /failure:enable | Out-Null
    Write-Log "已启用：其他特权使用失败审核"

    # 2.8 系统事件审核
    auditpol /set /subcategory:"安全状态更改" /success:enable /failure:enable | Out-Null
    Write-Log "已启用：安全状态更改审核"

    auditpol /set /subcategory:"系统完整性" /failure:enable | Out-Null
    Write-Log "已启用：系统完整性失败审核"

    auditpol /set /subcategory:"其他系统事件" /success:enable /failure:enable | Out-Null
    Write-Log "已启用：其他系统事件审核"

    Write-Log "审核策略配置完成"
}
catch {
    Write-Log "审核策略配置失败：$($_.Exception.Message)" "ERROR"
}

# 2.9 启用进程创建命令行审计
try {
    Write-Log "正在启用进程创建命令行审计..."
    $regPath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\Audit"
    if (-not (Test-Path $regPath)) {
        New-Item -Path $regPath -Force | Out-Null
    }
    Set-ItemProperty -Path $regPath -Name "ProcessCreationIncludeCmdLine_Enabled" -Value 1 -Type DWord
    Write-Log "进程创建命令行审计已启用"
}
catch {
    Write-Log "启用进程创建命令行审计失败：$($_.Exception.Message)" "ERROR"
}

# 2.10 配置安全日志大小
try {
    Write-Log "正在配置安全日志大小..."
    wevtutil sl Security /ms:1073741824 /rt:false  # 1GB
    Write-Log "安全日志大小已设置为 1GB"
}
catch {
    Write-Log "配置安全日志大小失败：$($_.Exception.Message)" "ERROR"
}

# ============================================================
# 三、关闭不安全服务
# ============================================================

Write-Host ""
Write-Host "[*] ============================================================" -ForegroundColor Cyan
Write-Host "[*] 三、关闭不安全服务" -ForegroundColor Cyan
Write-Host "[*] ============================================================" -ForegroundColor Cyan
Write-Host ""

# 定义要禁用的服务列表
$disableServices = @(
    @{ Name = "RemoteRegistry"; DisplayName = "远程注册表"; Reason = "允许远程修改注册表，存在安全风险" },
    @{ Name = "TermService"; DisplayName = "远程桌面服务"; Reason = "如不需要RDP，建议禁用；如需要请启用并加固" },
    @{ Name = "Telnet"; DisplayName = "Telnet 服务"; Reason = "明文传输，不安全，应使用 SSH 替代" },
    @{ Name = "FTPSVC"; DisplayName = "FTP 服务"; Reason = "明文传输，建议使用 SFTP/SCP 替代" },
    @{ Name = "W3SVC"; DisplayName = "IIS 服务"; Reason = "如不需要 Web 服务建议禁用" },
    @{ Name = "SSDPSRV"; DisplayName = "SSDP 发现"; Reason = "UPnP 设备发现，存在安全风险" },
    @{ Name = "upnphost"; DisplayName = "UPnP 设备主机"; Reason = "UPnP 服务，存在安全风险" },
    @{ Name = "FDResPub"; DisplayName = "功能发现资源发布"; Reason = "网络发现相关，如不需要可禁用" },
    @{ Name = "WMPNetworkSvc"; DisplayName = "Windows Media Player 网络共享服务"; Reason = "媒体共享，非必要服务" },
    @{ Name = "Fax"; DisplayName = "传真服务"; Reason = "如不使用传真建议禁用" },
    @{ Name = "RemoteAccess"; DisplayName = "路由和远程访问"; Reason = "如不需要 VPN/路由建议禁用" },
    @{ Name = "PolicyAgent"; DisplayName = "IPsec 策略代理"; Reason = "如不使用 IPsec 可禁用" },
    @{ Name = "SessionEnv"; DisplayName = "远程桌面配置服务"; Reason = "远程桌面相关，如不需要可禁用" }
)

foreach ($svc in $disableServices) {
    try {
        $service = Get-Service -Name $svc.Name -ErrorAction SilentlyContinue
        if ($service) {
            if ($service.Status -ne 'Stopped') {
                Stop-Service -Name $svc.Name -Force -ErrorAction Stop
                Write-Log "已停止服务：$($svc.DisplayName) ($($svc.Name)) - $($svc.Reason)"
            }
            # 设置启动类型为禁用
            Set-Service -Name $svc.Name -StartupType Disabled -ErrorAction Stop
            Write-Log "已禁用服务：$($svc.DisplayName) ($($svc.Name)) - $($svc.Reason)"
        } else {
            Write-Log "服务不存在，跳过：$($svc.DisplayName) ($($svc.Name))" "SKIP"
        }
    }
    catch {
        Write-Log "处理服务失败 $($svc.Name)：$($_.Exception.Message)" "ERROR"
    }
}

# ============================================================
# 四、防火墙规则配置
# ============================================================

Write-Host ""
Write-Host "[*] ============================================================" -ForegroundColor Cyan
Write-Host "[*] 四、防火墙规则配置" -ForegroundColor Cyan
Write-Host "[*] ============================================================" -ForegroundColor Cyan
Write-Host ""

try {
    Write-Log "正在配置 Windows Defender 防火墙..."

    # 4.1 启用所有配置文件的防火墙
    Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True
    Write-Log "已启用所有配置文件的防火墙"

    # 4.2 设置默认入站策略为阻止
    Set-NetFirewallProfile -Profile Domain,Public,Private -DefaultInboundAction Block
    Write-Log "已设置默认入站策略为阻止"

    # 4.3 设置默认出站策略为允许
    Set-NetFirewallProfile -Profile Domain,Public,Private -DefaultOutboundAction Allow
    Write-Log "已设置默认出站策略为允许"

    # 4.4 允许 ICMP (Ping) - 入站
    $icmpRule = Get-NetFirewallRule -DisplayName "Allow ICMPv4-In" -ErrorAction SilentlyContinue
    if (-not $icmpRule) {
        New-NetFirewallRule -DisplayName "Allow ICMPv4-In" -Protocol ICMPv4 -IcmpType 8 -Direction Inbound -Action Allow -Enabled True -Profile Any | Out-Null
        Write-Log "已添加入站规则：允许 ICMPv4 (Ping)"
    } else {
        Write-Log "ICMPv4 入站规则已存在" "SKIP"
    }

    # 4.5 阻止 SMB 出站（防止横向移动，根据实际需要调整）
    $blockSmbOut = Get-NetFirewallRule -DisplayName "Block SMB Outbound" -ErrorAction SilentlyContinue
    if (-not $blockSmbOut) {
        New-NetFirewallRule -DisplayName "Block SMB Outbound" -Direction Outbound -Protocol TCP -RemotePort 445 -Action Block -Enabled True -Profile Any | Out-Null
        Write-Log "已添加出站规则：阻止 SMB (445端口) 出站"
    } else {
        Write-Log "SMB 出站阻止规则已存在" "SKIP"
    }

    # 4.6 阻止 NetBIOS 出站
    $blockNetbiosOut = Get-NetFirewallRule -DisplayName "Block NetBIOS Outbound" -ErrorAction SilentlyContinue
    if (-not $blockNetbiosOut) {
        New-NetFirewallRule -DisplayName "Block NetBIOS Outbound" -Direction Outbound -Protocol TCP -RemotePort 137,138,139 -Action Block -Enabled True -Profile Any | Out-Null
        Write-Log "已添加出站规则：阻止 NetBIOS (137-139端口) 出站"
    } else {
        Write-Log "NetBIOS 出站阻止规则已存在" "SKIP"
    }

    # 4.7 启用防火墙日志
    Set-NetFirewallProfile -Profile Domain,Public,Private -LogAllowed False -LogBlocked True -LogMaxSizeKilobytes 4096
    Write-Log "已启用防火墙阻止日志（最大 4MB）"

    Write-Log "防火墙配置完成"
}
catch {
    Write-Log "防火墙配置失败：$($_.Exception.Message)" "ERROR"
}

# ============================================================
# 五、注册表安全加固
# ============================================================

Write-Host ""
Write-Host "[*] ============================================================" -ForegroundColor Cyan
Write-Host "[*] 五、注册表安全加固" -ForegroundColor Cyan
Write-Host "[*] ============================================================" -ForegroundColor Cyan
Write-Host ""

# 5.1 禁用自动运行（Autorun）
try {
    Write-Log "正在禁用自动运行（Autorun）..."
    $regPath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer"
    if (-not (Test-Path $regPath)) {
        New-Item -Path $regPath -Force | Out-Null
    }
    Set-ItemProperty -Path $regPath -Name "NoDriveTypeAutoRun" -Value 255 -Type DWord
    Set-ItemProperty -Path $regPath -Name "NoAutoRun" -Value 1 -Type DWord
    Write-Log "自动运行（Autorun）已禁用"
}
catch {
    Write-Log "禁用自动运行失败：$($_.Exception.Message)" "ERROR"
}

# 5.2 禁用默认管理共享（ADMIN$、C$ 等）
try {
    Write-Log "正在禁用默认管理共享..."
    $regPath = "HKLM:\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters"
    Set-ItemProperty -Path $regPath -Name "AutoShareServer" -Value 0 -Type DWord
    Set-ItemProperty -Path $regPath -Name "AutoShareWks" -Value 0 -Type DWord
    Write-Log "默认管理共享已禁用"
}
catch {
    Write-Log "禁用默认管理共享失败：$($_.Exception.Message)" "ERROR"
}

# 5.3 禁用 LM 哈希存储
try {
    Write-Log "正在禁用 LM 哈希存储..."
    $regPath = "HKLM:\SYSTEM\CurrentControlSet\Control\Lsa"
    Set-ItemProperty -Path $regPath -Name "NoLMHash" -Value 1 -Type DWord
    Write-Log "LM 哈希存储已禁用"
}
catch {
    Write-Log "禁用 LM 哈希存储失败：$($_.Exception.Message)" "ERROR"
}

# 5.4 限制 NTLM（仅发送 NTLMv2 响应）
try {
    Write-Log "正在配置 NTLM 安全级别..."
    $regPath = "HKLM:\SYSTEM\CurrentControlSet\Control\Lsa\MSV1_0"
    Set-ItemProperty -Path $regPath -Name "NtlmMinClientSec" -Value 537395200 -Type DWord
    Set-ItemProperty -Path $regPath -Name "NtlmMinServerSec" -Value 537395200 -Type DWord
    Write-Log "NTLM 安全级别已设置为仅 NTLMv2"
}
catch {
    Write-Log "配置 NTLM 安全级别失败：$($_.Exception.Message)" "ERROR"
}

# 5.5 增强 LSASS 保护（RunAsPPL）
try {
    Write-Log "正在启用 LSASS 保护（RunAsPPL）..."
    $regPath = "HKLM:\SYSTEM\CurrentControlSet\Control\Lsa"
    Set-ItemProperty -Path $regPath -Name "RunAsPPL" -Value 1 -Type DWord
    Write-Log "LSASS 保护（RunAsPPL）已启用"
}
catch {
    Write-Log "启用 LSASS 保护失败：$($_.Exception.Message)" "ERROR"
}

# 5.6 禁用 SMBv1
try {
    Write-Log "正在禁用 SMBv1..."
    # 服务器端
    $smb1Server = Get-WindowsOptionalFeature -Online -FeatureName SMB1Protocol -ErrorAction SilentlyContinue
    if ($smb1Server.State -eq "Enabled") {
        Disable-WindowsOptionalFeature -Online -FeatureName SMB1Protocol -NoRestart
        Write-Log "SMBv1 协议已禁用"
    } else {
        Write-Log "SMBv1 已禁用" "SKIP"
    }
    
    # 客户端
    $smb1Client = Get-WindowsOptionalFeature -Online -FeatureName SMB1Protocol-Client -ErrorAction SilentlyContinue
    if ($smb1Client.State -eq "Enabled") {
        Disable-WindowsOptionalFeature -Online -FeatureName SMB1Protocol-Client -NoRestart
        Write-Log "SMBv1 客户端已禁用"
    }
}
catch {
    Write-Log "禁用 SMBv1 失败：$($_.Exception.Message)" "ERROR"
}

# 5.7 启用 SMB 签名
try {
    Write-Log "正在启用 SMB 签名..."
    $regPath = "HKLM:\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters"
    Set-ItemProperty -Path $regPath -Name "RequireSecuritySignature" -Value 1 -Type DWord
    Set-ItemProperty -Path $regPath -Name "EnableSecuritySignature" -Value 1 -Type DWord
    
    $regPathClient = "HKLM:\SYSTEM\CurrentControlSet\Services\LanmanWorkstation\Parameters"
    Set-ItemProperty -Path $regPathClient -Name "RequireSecuritySignature" -Value 1 -Type DWord
    Set-ItemProperty -Path $regPathClient -Name "EnableSecuritySignature" -Value 1 -Type DWord
    Write-Log "SMB 签名已启用（服务器端和客户端）"
}
catch {
    Write-Log "启用 SMB 签名失败：$($_.Exception.Message)" "ERROR"
}

# 5.8 禁用 Windows 脚本宿主（可选，根据实际需要启用）
<#
try {
    Write-Log "正在禁用 Windows Script Host..."
    $regPath = "HKCU:\Software\Microsoft\Windows Script Host\Settings"
    if (-not (Test-Path $regPath)) {
        New-Item -Path $regPath -Force | Out-Null
    }
    Set-ItemProperty -Path $regPath -Name "Enabled" -Value 0 -Type DWord
    
    $regPathLM = "HKLM:\Software\Microsoft\Windows Script Host\Settings"
    if (-not (Test-Path $regPathLM)) {
        New-Item -Path $regPathLM -Force | Out-Null
    }
    Set-ItemProperty -Path $regPathLM -Name "Enabled" -Value 0 -Type DWord
    Write-Log "Windows Script Host 已禁用"
}
catch {
    Write-Log "禁用 Windows Script Host 失败：$($_.Exception.Message)" "ERROR"
}
#>

# ============================================================
# 六、UAC 配置
# ============================================================

Write-Host ""
Write-Host "[*] ============================================================" -ForegroundColor Cyan
Write-Host "[*] 六、UAC 配置" -ForegroundColor Cyan
Write-Host "[*] ============================================================" -ForegroundColor Cyan
Write-Host ""

try {
    Write-Log "正在配置用户账户控制（UAC）..."

    $regPath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"

    # 6.1 启用 UAC
    Set-ItemProperty -Path $regPath -Name "EnableLUA" -Value 1 -Type DWord
    Write-Log "UAC 已启用"

    # 6.2 UAC 提示级别 - 最高级别（始终通知）
    # PromptOnSecureDesktop = 1 (在安全桌面提示)
    # ConsentPromptBehaviorAdmin = 2 (始终通知)
    # ConsentPromptBehaviorUser = 3 (自动拒绝)
    Set-ItemProperty -Path $regPath -Name "PromptOnSecureDesktop" -Value 1 -Type DWord
    Set-ItemProperty -Path $regPath -Name "ConsentPromptBehaviorAdmin" -Value 2 -Type DWord
    Set-ItemProperty -Path $regPath -Name "ConsentPromptBehaviorUser" -Value 3 -Type DWord
    Write-Log "UAC 提示级别已设置为最高（始终通知，安全桌面）"

    # 6.3 内置管理员账户的管理员批准模式
    Set-ItemProperty -Path $regPath -Name "FilterAdministratorToken" -Value 0 -Type DWord
    Write-Log "内置管理员账户管理员批准模式已禁用（使用内置管理员时需谨慎）"

    # 6.4 提升提示时安全桌面
    Set-ItemProperty -Path $regPath -Name "PromptOnSecureDesktop" -Value 1 -Type DWord
    Write-Log "UAC 安全桌面提示已启用"

    Write-Log "UAC 配置完成"
}
catch {
    Write-Log "UAC 配置失败：$($_.Exception.Message)" "ERROR"
}

# ============================================================
# 七、RDP 安全配置
# ============================================================

Write-Host ""
Write-Host "[*] ============================================================" -ForegroundColor Cyan
Write-Host "[*] 七、RDP 安全配置" -ForegroundColor Cyan
Write-Host "[*] ============================================================" -ForegroundColor Cyan
Write-Host ""

try {
    Write-Log "正在配置 RDP 安全..."

    $rdpRegPath = "HKLM:\System\CurrentControlSet\Control\Terminal Server"
    $rdpTcpPath = "HKLM:\System\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp"

    # 7.1 检测 RDP 是否启用
    $rdpEnabled = (Get-ItemProperty -Path $rdpRegPath -Name "fDenyTSConnections" -ErrorAction SilentlyContinue).fDenyTSConnections
    if ($rdpEnabled -eq 0) {
        Write-Log "检测到 RDP 已启用，进行安全加固..."
        
        # 7.2 启用网络级别身份验证（NLA）
        Set-ItemProperty -Path $rdpTcpPath -Name "UserAuthentication" -Value 1 -Type DWord
        Write-Log "已启用网络级别身份验证（NLA）"

        # 7.3 禁用剪贴板重定向（防止凭据通过剪贴板窃取）
        $clipboardPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows NT\Terminal Services"
        if (-not (Test-Path $clipboardPath)) {
            New-Item -Path $clipboardPath -Force | Out-Null
        }
        Set-ItemProperty -Path $clipboardPath -Name "fDisableClip" -Value 1 -Type DWord
        Write-Log "已禁用 RDP 剪贴板重定向"

        # 7.4 禁用驱动器重定向
        Set-ItemProperty -Path $clipboardPath -Name "fDisableCdm" -Value 1 -Type DWord
        Write-Log "已禁用 RDP 驱动器重定向"

        # 7.5 设置 RDP 加密级别为高
        Set-ItemProperty -Path $rdpTcpPath -Name "MinEncryptionLevel" -Value 3 -Type DWord
        Write-Log "RDP 加密级别已设置为高"

        # 7.6 限制 RDP 用户组
        # 仅允许 Administrators 和 Remote Desktop Users 组的成员登录
        # 可根据需要调整：net localgroup "Remote Desktop Users" /add username

        # 7.7 限制并发连接数
        $tsPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows NT\Terminal Services"
        if (-not (Test-Path $tsPath)) {
            New-Item -Path $tsPath -Force | Out-Null
        }
        Set-ItemProperty -Path $tsPath -Name "MaxInstanceCount" -Value 2 -Type DWord
        Write-Log "RDP 最大并发连接数已限制为 2"

        # 7.8 空闲会话超时（30分钟）
        Set-ItemProperty -Path $tsPath -Name "MaxIdleTime" -Value 1800000 -Type DWord
        Write-Log "RDP 空闲会话超时已设置为 30 分钟"

        Write-Log "RDP 安全加固完成"
    } else {
        Write-Log "RDP 未启用，跳过 RDP 安全配置" "SKIP"
    }
}
catch {
    Write-Log "RDP 安全配置失败：$($_.Exception.Message)" "ERROR"
}

# ============================================================
# 八、Windows Defender 配置
# ============================================================

Write-Host ""
Write-Host "[*] ============================================================" -ForegroundColor Cyan
Write-Host "[*] 八、Windows Defender 配置" -ForegroundColor Cyan
Write-Host "[*] ============================================================" -ForegroundColor Cyan
Write-Host ""

try {
    Write-Log "正在配置 Windows Defender..."

    # 检查 Defender 服务状态
    $defenderService = Get-Service -Name WinDefend -ErrorAction SilentlyContinue
    if ($defenderService -and $defenderService.Status -eq "Running") {
        
        # 8.1 启用实时保护
        Set-MpPreference -DisableRealtimeMonitoring $false
        Write-Log "实时保护已启用"

        # 8.2 启用云提供的保护
        Set-MpPreference -DisableCloudDeliveredProtection $false
        Write-Log "云提供的保护已启用"

        # 8.3 启用自动提交样本
        Set-MpPreference -SubmitSamplesConsent 1  # 1 = 自动发送安全样本
        Write-Log "自动提交样本已启用"

        # 8.4 启用行为监控
        Set-MpPreference -DisableBehaviorMonitoring $false
        Write-Log "行为监控已启用"

        # 8.5 启用勒索软件防护（受控文件夹访问）
        # 注意：启用前请确认需要保护的文件夹
        # Set-MpPreference -EnableControlledFolderAccess Enabled
        # Write-Log "受控文件夹访问（勒索软件防护）已启用"

        # 8.6 启用网络保护
        Set-MpPreference -EnableNetworkProtection Enabled
        Write-Log "网络保护已启用"

        # 8.7 启用攻击面减少（ASR）规则
        # 启用常见的 ASR 规则（审计模式，建议先审计再阻止）
        $asrRules = @(
            "BE9BA2D9-53EA-4CDC-84E5-9B1EEEE46550",  # 阻止可执行文件从电子邮件客户端运行
            "D4F940AB-401B-4EFC-AADC-AD5F3C50688A",  # 阻止 Office 应用创建子进程
            "3B576869-A4EC-4529-8536-B80A7769E899",  # 阻止 Office 应用将代码注入其他进程
            "7674ba52-37eb-4a4f-a9a1-f0f9a1619a2c",  # 阻止 Adobe Reader 创建子进程
            "D1E49AAC-8F56-4280-B9BA-993A6D77406C",  # 阻止从 USB 运行的可疑进程
            "5BEB7EFE-FD9A-4556-801D-275E5FFC04CC"   # 阻止混淆脚本
        )
        
        foreach ($rule in $asrRules) {
            Add-MpPreference -AttackSurfaceReductionRules_Ids $rule
            Add-MpPreference -AttackSurfaceReductionRules_Actions AuditMode
        }
        Write-Log "攻击面减少（ASR）规则已启用（审计模式）"

        # 8.8 配置扫描排除项（根据需要添加）
        # Add-MpPreference -ExclusionPath "C:\Path\To\Exclude"

        Write-Log "Windows Defender 配置完成"
    } else {
        Write-Log "Windows Defender 未运行，跳过配置" "WARN"
    }
}
catch {
    Write-Log "Windows Defender 配置失败：$($_.Exception.Message)" "ERROR"
}

# ============================================================
# 九、PowerShell 安全配置
# ============================================================

Write-Host ""
Write-Host "[*] ============================================================" -ForegroundColor Cyan
Write-Host "[*] 九、PowerShell 安全配置" -ForegroundColor Cyan
Write-Host "[*] ============================================================" -ForegroundColor Cyan
Write-Host ""

try {
    Write-Log "正在配置 PowerShell 安全..."

    # 9.1 设置 PowerShell 执行策略
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine -Force
    Write-Log "PowerShell 执行策略已设置为 RemoteSigned（本地脚本可运行，远程脚本需签名）"

    # 9.2 启用 PowerShell 模块日志
    $psLogPath = "HKLM:\SOFTWARE\Wow6432Node\Policies\Microsoft\Windows\PowerShell\ModuleLogging"
    if (-not (Test-Path $psLogPath)) {
        New-Item -Path $psLogPath -Force | Out-Null
    }
    Set-ItemProperty -Path $psLogPath -Name "EnableModuleLogging" -Value 1 -Type DWord
    
    # 记录所有模块
    $moduleNamesPath = "$psLogPath\ModuleNames"
    if (-not (Test-Path $moduleNamesPath)) {
        New-Item -Path $moduleNamesPath -Force | Out-Null
    }
    Set-ItemProperty -Path $moduleNamesPath -Name "*" -Value "*" -Type String
    Write-Log "PowerShell 模块日志已启用"

    # 9.3 启用 PowerShell 脚本块日志
    $scriptBlockPath = "HKLM:\SOFTWARE\Wow6432Node\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging"
    if (-not (Test-Path $scriptBlockPath)) {
        New-Item -Path $scriptBlockPath -Force | Out-Null
    }
    Set-ItemProperty -Path $scriptBlockPath -Name "EnableScriptBlockLogging" -Value 1 -Type DWord
    Write-Log "PowerShell 脚本块日志已启用"

    # 9.4 启用 PowerShell 转录
    $transcriptPath = "HKLM:\SOFTWARE\Wow6432Node\Policies\Microsoft\Windows\PowerShell\Transcription"
    if (-not (Test-Path $transcriptPath)) {
        New-Item -Path $transcriptPath -Force | Out-Null
    }
    Set-ItemProperty -Path $transcriptPath -Name "EnableTranscripting" -Value 1 -Type DWord
    Set-ItemProperty -Path $transcriptPath -Name "EnableInvocationHeader" -Value 1 -Type DWord
    # 设置转录文件输出目录
    $outputDir = "C:\ProgramData\PowerShellTranscripts"
    if (-not (Test-Path $outputDir)) {
        New-Item -Path $outputDir -ItemType Directory -Force | Out-Null
    }
    Set-ItemProperty -Path $transcriptPath -Name "OutputDirectory" -Value $outputDir -Type String
    Write-Log "PowerShell 转录已启用，输出目录：$outputDir"

    Write-Log "PowerShell 安全配置完成"
}
catch {
    Write-Log "PowerShell 安全配置失败：$($_.Exception.Message)" "ERROR"
}

# ============================================================
# 十、其他安全加固
# ============================================================

Write-Host ""
Write-Host "[*] ============================================================" -ForegroundColor Cyan
Write-Host "[*] 十、其他安全加固" -ForegroundColor Cyan
Write-Host "[*] ============================================================" -ForegroundColor Cyan
Write-Host ""

# 10.1 禁用 NetBIOS over TCP/IP
try {
    Write-Log "正在禁用 NetBIOS over TCP/IP..."
    $adapters = Get-WmiObject -Class Win32_NetworkAdapterConfiguration -Filter "IPEnabled='True'"
    foreach ($adapter in $adapters) {
        $adapter.SetTCPIPNetBIOSOptions(2) | Out-Null  # 2 = 禁用 NetBIOS
    }
    Write-Log "NetBIOS over TCP/IP 已禁用"
}
catch {
    Write-Log "禁用 NetBIOS over TCP/IP 失败：$($_.Exception.Message)" "ERROR"
}

# 10.2 配置 DNS 客户端缓存大小
try {
    Write-Log "正在加固 DNS 客户端配置..."
    $dnsPath = "HKLM:\SYSTEM\CurrentControlSet\Services\Dnscache\Parameters"
    Set-ItemProperty -Path $dnsPath -Name "MaxCacheTtl" -Value 86400 -Type DWord  # 24小时
    Set-ItemProperty -Path $dnsPath -Name "MaxNegativeCacheTtl" -Value 0 -Type DWord  # 禁用负缓存
    Write-Log "DNS 客户端缓存配置已更新"
}
catch {
    Write-Log "DNS 客户端配置失败：$($_.Exception.Message)" "ERROR"
}

# 10.3 禁用 WPAD（Web 代理自动发现）
try {
    Write-Log "正在禁用 WPAD..."
    $wpadPath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings\WinHttp"
    Set-ItemProperty -Path $wpadPath -Name "DisableWpad" -Value 1 -Type DWord
    
    # 也禁用自动检测设置
    $iePath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings"
    Set-ItemProperty -Path $iePath -Name "AutoDetect" -Value 0 -Type DWord
    Write-Log "WPAD 已禁用"
}
catch {
    Write-Log "禁用 WPAD 失败：$($_.Exception.Message)" "ERROR"
}

# 10.4 启用 DEP 数据执行保护
try {
    Write-Log "正在启用 DEP（数据执行保护）..."
    # 设置为 OptOut 模式（对所有程序启用 DEP，排除列表除外）
    $result = & bcdedit.exe /set "{current}" nx OptOut
    Write-Log "DEP 已设置为 OptOut 模式（所有程序启用 DEP）"
}
catch {
    Write-Log "启用 DEP 失败：$($_.Exception.Message)" "ERROR"
}

# 10.5 配置 Windows 更新
try {
    Write-Log "正在配置 Windows 更新..."
    $auPath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update"
    if (-not (Test-Path $auPath)) {
        New-Item -Path $auPath -Force | Out-Null
    }
    Set-ItemProperty -Path $auPath -Name "AUOptions" -Value 4 -Type DWord  # 4 = 自动下载并安装
    Write-Log "Windows 更新已设置为自动下载并安装"
}
catch {
    Write-Log "配置 Windows 更新失败：$($_.Exception.Message)" "ERROR"
}

# 10.6 禁用旧版协议（TLS 1.0、TLS 1.1）
try {
    Write-Log "正在禁用旧版 TLS 协议..."
    
    # 禁用 TLS 1.0 客户端
    $tls10Client = "HKLM:\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.0\Client"
    if (-not (Test-Path $tls10Client)) {
        New-Item -Path $tls10Client -Force | Out-Null
    }
    Set-ItemProperty -Path $tls10Client -Name "Enabled" -Value 0 -Type DWord
    Set-ItemProperty -Path $tls10Client -Name "DisabledByDefault" -Value 1 -Type DWord

    # 禁用 TLS 1.0 服务端
    $tls10Server = "HKLM:\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.0\Server"
    if (-not (Test-Path $tls10Server)) {
        New-Item -Path $tls10Server -Force | Out-Null
    }
    Set-ItemProperty -Path $tls10Server -Name "Enabled" -Value 0 -Type DWord
    Set-ItemProperty -Path $tls10Server -Name "DisabledByDefault" -Value 1 -Type DWord

    # 禁用 TLS 1.1 客户端
    $tls11Client = "HKLM:\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.1\Client"
    if (-not (Test-Path $tls11Client)) {
        New-Item -Path $tls11Client -Force | Out-Null
    }
    Set-ItemProperty -Path $tls11Client -Name "Enabled" -Value 0 -Type DWord
    Set-ItemProperty -Path $tls11Client -Name "DisabledByDefault" -Value 1 -Type DWord

    # 禁用 TLS 1.1 服务端
    $tls11Server = "HKLM:\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.1\Server"
    if (-not (Test-Path $tls11Server)) {
        New-Item -Path $tls11Server -Force | Out-Null
    }
    Set-ItemProperty -Path $tls11Server -Name "Enabled" -Value 0 -Type DWord
    Set-ItemProperty -Path $tls11Server -Name "DisabledByDefault" -Value 1 -Type DWord

    # 启用 TLS 1.2
    $tls12Client = "HKLM:\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.2\Client"
    if (-not (Test-Path $tls12Client)) {
        New-Item -Path $tls12Client -Force | Out-Null
    }
    Set-ItemProperty -Path $tls12Client -Name "Enabled" -Value 1 -Type DWord
    Set-ItemProperty -Path $tls12Client -Name "DisabledByDefault" -Value 0 -Type DWord

    $tls12Server = "HKLM:\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.2\Server"
    if (-not (Test-Path $tls12Server)) {
        New-Item -Path $tls12Server -Force | Out-Null
    }
    Set-ItemProperty -Path $tls12Server -Name "Enabled" -Value 1 -Type DWord
    Set-ItemProperty -Path $tls12Server -Name "DisabledByDefault" -Value 0 -Type DWord

    Write-Log "已禁用 TLS 1.0 和 TLS 1.1，启用 TLS 1.2"
}
catch {
    Write-Log "配置 TLS 协议失败：$($_.Exception.Message)" "ERROR"
}

# ============================================================
# 十一、加固完成
# ============================================================

Write-Host ""
Write-Host "[*] ============================================================" -ForegroundColor Cyan
Write-Host "[*] 加固完成" -ForegroundColor Cyan
Write-Host "[*] ============================================================" -ForegroundColor Cyan
Write-Host ""

Write-Log "脚本执行完毕"
Write-Log "详细日志已保存到：$logPath"

Write-Host ""
Write-Host "[!] 重要提示：" -ForegroundColor Yellow
Write-Host "    1. 建议重启系统以确保所有设置生效" -ForegroundColor Yellow
Write-Host "    2. 请仔细检查各功能是否正常工作，特别是业务相关服务" -ForegroundColor Yellow
Write-Host "    3. 加固前请确保已创建系统还原点或备份" -ForegroundColor Yellow
Write-Host "    4. 部分设置可能需要根据实际业务需求调整" -ForegroundColor Yellow
Write-Host "    5. 日志文件位置：$logPath" -ForegroundColor Yellow
Write-Host ""

# 询问是否重启
$restart = Read-Host "是否立即重启系统？(y/N)"
if ($restart -eq "y" -or $restart -eq "Y") {
    Write-Host "[*] 系统将在 10 秒后重启..." -ForegroundColor Yellow
    shutdown /r /t 10 /c "Windows 安全加固完成，系统重启以应用所有设置"
} else {
    Write-Host "[*] 请稍后手动重启系统以应用所有设置。" -ForegroundColor Green
}

exit 0
