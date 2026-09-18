# Windows 安全加固检查清单

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

---

## 📋 内容审核与补充建议

> 针对「Windows 安全加固检查清单」部分的内容审核结果：

### 💻 代码示例
- ⚠️ 缺少code相关内容

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 📖 参考资料
- ⚠️ 缺少参考资料/延伸阅读

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客

---

## 🛠️ 补充：实战拓展

### 一、Windows 安全配置命令速查表

#### 系统更新与补丁

```powershell
# ===== 检查已安装的更新 =====
wmic qfe list brief
# 或
Get-HotFix

# ===== 检查更新历史 =====
Get-WindowsUpdateLog

# ===== 使用 PowerShell 模块检查更新 =====
# 安装模块
Install-Module -Name PSWindowsUpdate -Force
# 检查可用更新
Get-WindowsUpdate
# 安装所有更新
Install-WindowsUpdate -AcceptAll -AutoReboot

# ===== 检查系统版本 =====
winver
# 或
[System.Environment]::OSVersion.Version
```

#### 账户与密码策略

```powershell
# ===== 查看本地用户列表 =====
Get-LocalUser
net user

# ===== 查看管理员组成员 =====
Get-LocalGroupMember -Group "Administrators"
net localgroup administrators

# ===== 禁用 Guest 账户 =====
Disable-LocalUser -Name "Guest"
net user guest /active:no

# ===== 重命名 Administrator 账户 =====
Rename-LocalUser -Name "Administrator" -NewName "NewAdminName"

# ===== 查看密码策略 =====
net accounts
# 或使用组策略结果
gpresult /r

# ===== 设置密码策略（本地）=====
# 密码最小长度14位
net accounts /minpwlen:14
# 密码最长使用期限90天
net accounts /maxpwage:90
# 密码最短使用期限1天
net accounts /minpwage:1
# 密码历史记录24个
net accounts /uniquepw:24
# 账户锁定阈值5次，锁定30分钟
net accounts /lockoutthreshold:5
net accounts /lockoutduration:30
net accounts /lockoutwindow:30
```

#### 审核与日志配置

```powershell
# ===== 查看当前审核策略 =====
auditpol /get /category:*

# ===== 启用关键审核策略 =====
# 登录/注销审核
auditpol /set /subcategory:"Logon" /success:enable /failure:enable
auditpol /set /subcategory:"Logoff" /success:enable

# 进程创建审核（含命令行）
auditpol /set /subcategory:"Process Creation" /success:enable /failure:enable
# 启用命令行审计（注册表）
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\Audit" /v ProcessCreationIncludeCmdLine_Enabled /t REG_DWORD /d 1 /f

# 账户管理审核
auditpol /set /subcategory:"User Account Management" /success:enable /failure:enable

# 对象访问审核
auditpol /set /subcategory:"File System" /success:enable /failure:enable
auditpol /set /subcategory:"Registry" /success:enable /failure:enable

# 特权使用审核
auditpol /set /subcategory:"Sensitive Privilege Use" /success:enable /failure:enable

# ===== 配置安全日志大小 =====
wevtutil sl Security /ms:1073741824
# 设置为1GB（单位：字节）

# ===== 导出安全日志 =====
wevtutil epl Security security_log.evtx
Get-WinEvent -LogName Security -MaxEvents 100 | Export-Csv -Path security_events.csv

# ===== 启用 PowerShell 日志 =====
# 模块日志
reg add "HKLM\SOFTWARE\Wow6432Node\Policies\Microsoft\Windows\PowerShell\ModuleLogging" /v EnableModuleLogging /t REG_DWORD /d 1 /f
reg add "HKLM\SOFTWARE\Wow6432Node\Policies\Microsoft\Windows\PowerShell\ModuleLogging\ModuleNames" /v "*" /t REG_SZ /d "*" /f

# 脚本块日志
reg add "HKLM\SOFTWARE\Wow6432Node\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging" /v EnableScriptBlockLogging /t REG_DWORD /d 1 /f
```

#### 网络与防火墙配置

```powershell
# ===== 查看防火墙状态 =====
Get-NetFirewallProfile
netsh advfirewall show allprofiles

# ===== 启用防火墙 =====
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True
netsh advfirewall set allprofiles state on

# ===== 设置默认入站策略为阻止 =====
Set-NetFirewallProfile -DefaultInboundAction Block

# ===== 查看防火墙规则 =====
Get-NetFirewallRule | Where-Object { $_.Enabled -eq 'True' } | Format-Table Name,Direction,Action
netsh advfirewall firewall show rule name=all

# ===== 限制 RDP 端口（仅允许特定IP）=====
New-NetFirewallRule -DisplayName "Allow RDP from specific IP" -Direction Inbound -Protocol TCP -LocalPort 3389 -RemoteAddress 192.168.1.0/24 -Action Allow
# 然后禁用默认RDP规则或删除开放规则

# ===== 禁用 SMBv1 =====
Disable-WindowsOptionalFeature -Online -FeatureName SMB1Protocol
# 或通过注册表
reg add "HKLM\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters" /v SMB1 /t REG_DWORD /d 0 /f

# ===== 启用 SMB 签名 =====
reg add "HKLM\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters" /v requiresecuritysignature /t REG_DWORD /d 1 /f
reg add "HKLM\SYSTEM\CurrentControlSet\Services\LanmanWorkstation\Parameters" /v requiresecuritysignature /t REG_DWORD /d 1 /f

# ===== 查看网络连接 =====
netstat -ano
Get-NetTCPConnection | Where-Object { $_.State -eq 'Listen' }
```

#### 注册表与系统加固

```powershell
# ===== 禁用自动运行（Autorun）=====
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v NoDriveTypeAutoRun /t REG_DWORD /d 255 /f

# ===== 禁用默认共享（ADMIN$、C$）=====
reg add "HKLM\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters" /v AutoShareServer /t REG_DWORD /d 0 /f
reg add "HKLM\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters" /v AutoShareWks /t REG_DWORD /d 0 /f
# 重启后生效

# ===== 增强 LSASS 保护（RunAsPPL）=====
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Lsa" /v RunAsPPL /t REG_DWORD /d 1 /f
# 重启后生效，防止未签名代码注入LSASS

# ===== 禁用 LM 哈希存储 =====
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Lsa" /v NoLMHash /t REG_DWORD /d 1 /f

# ===== 限制 NTLM 使用 =====
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Lsa" /v LmCompatibilityLevel /t REG_DWORD /d 5 /f
# 5 = 只发送NTLMv2响应，拒绝LM和NTLM

# ===== 启用 UAC 最高级别 =====
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v ConsentPromptBehaviorAdmin /t REG_DWORD /d 2 /f
# 2 = 提示凭据（最高级别）

# ===== 禁用 WDigest（防止明文密码存储）=====
reg add "HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\WDigest" /v UseLogonCredential /t REG_DWORD /d 0 /f
```

#### RDP 安全配置

```powershell
# ===== 查看 RDP 配置 =====
Get-ItemProperty -Path "HKLM:\System\CurrentControlSet\Control\Terminal Server"
Get-ItemProperty -Path "HKLM:\System\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp"

# ===== 启用网络级别身份验证（NLA）=====
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" /v UserAuthentication /t REG_DWORD /d 1 /f

# ===== 查看 RDP 用户组 =====
Get-LocalGroupMember -Group "Remote Desktop Users"

# ===== 更改 RDP 端口 =====
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" /v PortNumber /t REG_DWORD /d 3390 /f
# 更改后需重启终端服务并更新防火墙规则
```

#### Windows Defender 配置

```powershell
# ===== 查看 Defender 状态 =====
Get-MpComputerStatus

# ===== 启用实时保护 =====
Set-MpPreference -DisableRealtimeMonitoring $false

# ===== 启用云保护 =====
Set-MpPreference -DisableCloudDeliveredProtection $false

# ===== 启用勒索软件防护（受控文件夹访问）=====
Set-MpPreference -EnableControlledFolderAccess Enabled
# 添加受保护的文件夹
Add-MpPreference -ControlledFolderAccessProtectedFolders "C:\Users\Public\Documents"

# ===== 启用攻击面减少（ASR）规则 =====
# 阻止Office应用创建子进程
Set-MpPreference -AttackSurfaceReductionRules_Ids D4F940AB-401B-4EFC-AADC-AD5F3C50688A -AttackSurfaceReductionRules_Actions Enabled
# 阻止来自PSExec和WMI的进程创建
Set-MpPreference -AttackSurfaceReductionRules_Ids 3B576869-A4EC-4529-8536-B80A7769E899 -AttackSurfaceReductionRules_Actions Enabled
# 阻止可疑的WSExec命令
Set-MpPreference -AttackSurfaceReductionRules_Ids 7674ba52-37eb-4a4f-a9a1-f0f9a1619a2c -AttackSurfaceReductionRules_Actions Enabled

# ===== 执行快速扫描 =====
Start-MpScan -ScanType QuickScan

# ===== 更新病毒定义 =====
Update-MpSignature
```

### 二、PowerShell 安全审计脚本

```powershell
<#
.SYNOPSIS
Windows 安全配置审计脚本
.DESCRIPTION
检查Windows系统的关键安全配置项，生成审计报告
#>

#Requires -RunAsAdministrator

$ErrorActionPreference = "SilentlyContinue"
$report = @()

function Add-Result {
    param([string]$Category, [string]$Check, [string]$Status, [string]$Details)
    $global:report += [PSCustomObject]@{
        Category = $Category
        Check = $Check
        Status = $Status
        Details = $Details
    }
}

Write-Host "===== Windows 安全审计开始 =====" -ForegroundColor Cyan
Write-Host ""

# ===== 1. 系统信息 =====
Write-Host "[1/8] 系统信息收集..." -ForegroundColor Yellow
$os = Get-CimInstance Win32_OperatingSystem
Add-Result -Category "系统信息" -Check "操作系统" -Status "信息" -Details "$($os.Caption) $($os.Version)"
Add-Result -Category "系统信息" -Check "最后启动时间" -Status "信息" -Details $os.LastBootUpTime
Add-Result -Category "系统信息" -Check "安装日期" -Status "信息" -Details $os.InstallDate

# ===== 2. 账户安全 =====
Write-Host "[2/8] 账户安全检查..." -ForegroundColor Yellow

# 检查管理员组成员
$admins = Get-LocalGroupMember -Group "Administrators" | Select-Object -ExpandProperty Name
Add-Result -Category "账户安全" -Check "管理员组成员" -$(if($admins.Count -gt 3){"警告"}else{"通过"}) -Details ($admins -join ", ")

# 检查Guest账户状态
$guest = Get-LocalUser -Name "Guest"
Add-Result -Category "账户安全" -Check "Guest账户状态" -$(if($guest.Enabled){"失败"}else{"通过"}) -Details "已禁用"

# 检查密码策略
$pwPolicy = net accounts | Out-String
$minPwLen = if($pwPolicy -match "最小密码年龄.*?(\d+)") { $matches[1] } else { "未知" }
Add-Result -Category "账户安全" -Check "密码策略" -Status "信息" -Details "见 net accounts 输出"

# 检查是否有永不过期的账户
$neverExpire = Get-LocalUser | Where-Object { $_.PasswordNeverExpires -eq $true -and $_.Enabled -eq $true } | Select-Object -ExpandProperty Name
Add-Result -Category "账户安全" -Check "密码永不过期账户" -$(if($neverExpire.Count -gt 0){"警告"}else{"通过"}) -Details ($neverExpire -join ", ")

# ===== 3. 审核策略 =====
Write-Host "[3/8] 审核策略检查..." -ForegroundColor Yellow

$auditPolicy = auditpol /get /category:* /r | ConvertFrom-Csv
$processAudit = $auditPolicy | Where-Object { $_.'Subcategory' -eq 'Process Creation' }
Add-Result -Category "审核策略" -Check "进程创建审核" -$(if($processAudit.'Inclusion Setting' -match 'Success and Failure'){"通过"}else{"失败"}) -Details $processAudit.'Inclusion Setting'

$logonAudit = $auditPolicy | Where-Object { $_.'Subcategory' -eq 'Logon' }
Add-Result -Category "审核策略" -Check "登录审核" -$(if($logonAudit.'Inclusion Setting' -match 'Success and Failure'){"通过"}else{"失败"}) -Details $logonAudit.'Inclusion Setting'

# ===== 4. 防火墙配置 =====
Write-Host "[4/8] 防火墙配置检查..." -ForegroundColor Yellow

$firewall = Get-NetFirewallProfile
foreach($profile in $firewall) {
    Add-Result -Category "防火墙" -Check "$($profile.Name)配置文件" -$(if($profile.Enabled){"通过"}else{"失败"}) -Details "启用状态: $($profile.Enabled), 入站默认: $($profile.DefaultInboundAction)"
}

# ===== 5. Windows Defender =====
Write-Host "[5/8] Defender 安全检查..." -ForegroundColor Yellow

try {
    $defender = Get-MpComputerStatus
    Add-Result -Category "Defender" -Check "实时保护" -$(if($defender.RealTimeProtectionEnabled){"通过"}else{"失败"}) -Details "状态: $($defender.RealTimeProtectionEnabled)"
    Add-Result -Category "Defender" -Check "病毒定义" -Status "信息" -Details "版本: $($defender.AntivirusSignatureVersion), 更新时间: $($defender.AntivirusSignatureLastUpdated)"
} catch {
    Add-Result -Category "Defender" -Check "Defender状态" -Status "警告" -Details "无法获取Defender状态"
}

# ===== 6. 注册表安全 =====
Write-Host "[6/8] 注册表安全检查..." -ForegroundColor Yellow

# SMBv1
$smbv1 = Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters" -Name SMB1 -ErrorAction SilentlyContinue
Add-Result -Category "注册表加固" -Check "SMBv1禁用" -$(if($smbv1.SMB1 -eq 0){"通过"}else{"失败/未配置"}) -Details "值: $($smbv1.SMB1)"

# 自动运行
$autorun = Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer" -Name NoDriveTypeAutoRun -ErrorAction SilentlyContinue
Add-Result -Category "注册表加固" -Check "自动运行禁用" -$(if($autorun.NoDriveTypeAutoRun -eq 255){"通过"}else{"警告"}) -Details "值: $($autorun.NoDriveTypeAutoRun)"

# LSASS保护
$lsass = Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Control\Lsa" -Name RunAsPPL -ErrorAction SilentlyContinue
Add-Result -Category "注册表加固" -Check "LSASS保护(RunAsPPL)" -$(if($lsass.RunAsPPL -eq 1){"通过"}else{"警告"}) -Details "值: $($lsass.RunAsPPL)"

# ===== 7. 服务与启动项 =====
Write-Host "[7/8] 可疑服务与启动项检查..." -ForegroundColor Yellow

# 检查未签名的服务（粗略）
$services = Get-Service | Where-Object { $_.StartType -eq 'Automatic' } | Measure-Object
Add-Result -Category "服务安全" -Check "自动启动服务数" -Status "信息" -Details "$($services.Count) 个服务设置为自动启动"

# ===== 8. 网络连接 =====
Write-Host "[8/8] 网络连接检查..." -ForegroundColor Yellow

$listeningPorts = Get-NetTCPConnection -State Listen | Measure-Object
Add-Result -Category "网络安全" -Check "监听端口数" -Status "信息" -Details "$($listeningPorts.Count) 个端口在监听"

$rdpPort = Get-NetTCPConnection -LocalPort 3389 -State Listen -ErrorAction SilentlyContinue
Add-Result -Category "网络安全" -Check "RDP端口(3389)" -$(if($rdpPort){"警告"}else{"信息"}) -Details $(if($rdpPort){"RDP端口开放"}else{"未开放"})

# ===== 输出报告 =====
Write-Host ""
Write-Host "===== 审计报告 =====" -ForegroundColor Cyan
Write-Host ""

$report | Format-Table -AutoSize

# 统计
$passed = ($report | Where-Object { $_.Status -eq "通过" }).Count
$failed = ($report | Where-Object { $_.Status -eq "失败" }).Count
$warning = ($report | Where-Object { $_.Status -eq "警告" }).Count
$info = ($report | Where-Object { $_.Status -eq "信息" }).Count

Write-Host ""
Write-Host "统计: 通过 $passed | 失败 $failed | 警告 $warning | 信息 $info" -ForegroundColor $(if($failed -gt 0){"Red"}elseif($warning -gt 0){"Yellow"}else{"Green"})

# 导出CSV
$outputPath = "$env:TEMP\Windows_Security_Audit_$(Get-Date -Format 'yyyyMMdd_HHmmss').csv"
$report | Export-Csv -Path $outputPath -NoTypeInformation -Encoding UTF8
Write-Host ""
Write-Host "报告已导出至: $outputPath" -ForegroundColor Green
```

### 三、快速安全检查一键命令

```powershell
# ===== 一键收集关键安全信息 =====
# 保存为 security_check.ps1 以管理员身份运行

Write-Host "=== 系统信息 ===" -ForegroundColor Cyan
systeminfo | Select-String "OS Name|OS Version|System Type|Hotfix"

Write-Host "`n=== 管理员组成员 ===" -ForegroundColor Cyan
net localgroup administrators

Write-Host "`n=== 本地用户列表 ===" -ForegroundColor Cyan
net user

Write-Host "`n=== 监听端口 ===" -ForegroundColor Cyan
netstat -ano | findstr LISTENING

Write-Host "`n=== 服务状态 ===" -ForegroundColor Cyan
Get-Service | Where-Object { $_.Status -eq 'Running' -and $_.StartType -eq 'Automatic' } | Format-Table Name,DisplayName

Write-Host "`n=== 计划任务 ===" -ForegroundColor Cyan
schtasks /query /fo LIST | Select-String "TaskName|Next Run Time"

Write-Host "`n=== 防火墙状态 ===" -ForegroundColor Cyan
netsh advfirewall show allprofiles state

Write-Host "`n=== 最近安全事件 ===" -ForegroundColor Cyan
Get-WinEvent -LogName Security -MaxEvents 20 | Format-Table TimeCreated,Id,Message -AutoSize
```

### 四、Windows 安全加固工具清单

| 工具 | 用途 | 说明 |
|------|------|------|
| `gpedit.msc` | 组策略编辑器 | 配置系统安全策略 |
| `secpol.msc` | 本地安全策略 | 账户策略、审核策略等 |
| `rsop.msc` | 策略结果集 | 查看当前生效的组策略 |
| `gpresult` | 组策略结果 | 命令行查看策略应用情况 |
| `msinfo32` | 系统信息 | 查看系统详细配置 |
| `eventvwr.msc` | 事件查看器 | 查看系统/安全日志 |
| HardeningKitty | 第三方工具 | 基于HardeningMeasures的Windows加固脚本 |
| `sconfig` | 服务器配置 | Windows Server核心配置工具 |
| Microsoft Baseline Security Analyzer | 微软官方 | 安全基线扫描（较旧） |

> **安全提示**：
> - 修改注册表前务必备份：`reg export HKLM\Path backup.reg`
> - 重要策略修改前先在测试环境验证
> - 定期运行安全审计脚本，对比基线配置
> - 启用集中日志收集（SIEM/WEF）以便安全分析
> - 关键服务器配置LAPS管理本地管理员密码
