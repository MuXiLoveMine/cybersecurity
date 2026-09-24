# Windows安全基线与加固

### 8.1 账户策略

#### 8.1.1 密码策略

密码策略是账户安全的第一道防线：

```
本地组策略编辑器 → 计算机配置 → Windows设置 → 安全设置 → 账户策略 → 密码策略
```

| 策略 | 推荐值 | 说明 |
|------|--------|------|
| 密码必须符合复杂性要求 | 已启用 | 密码需包含大写、小写、数字、符号中的3种 |
| 密码长度最小值 | 12个字符 | 越长越安全，建议至少12位 |
| 密码最短使用期限 | 1天 | 防止用户频繁改回旧密码 |
| 密码最长使用期限 | 90天 | 定期更换密码 |
| 强制密码历史 | 24个记住的密码 | 防止重复使用旧密码 |
| 用可还原的加密来储存密码 | 已禁用 | 明文等价存储，必须禁用 |

```cmd
:: 查看密码策略
net accounts

:: 使用secedit导出安全策略
secedit /export /cfg "C:\temp\secpol.cfg" /areas SECURITYPOLICY
```

#### 8.1.2 账户锁定策略

```
本地组策略编辑器 → 计算机配置 → Windows设置 → 安全设置 → 账户策略 → 账户锁定策略
```

| 策略 | 推荐值 | 说明 |
|------|--------|------|
| 账户锁定阈值 | 5次无效登录 | 5次失败后锁定 |
| 账户锁定时间 | 30分钟 | 锁定持续时间 |
| 重置账户锁定计数器 | 30分钟 | 失败计数重置周期 |

#### 8.1.3 Kerberos策略（域环境）

```
域安全策略 → 计算机配置 → Windows设置 → 安全设置 → 账户策略 → Kerberos策略
```

| 策略 | 推荐值 | 说明 |
|------|--------|------|
| 服务票据最长有效期 | 600分钟 | 服务票据使用期限 |
| 用户票据最长有效期 | 10小时 | TGT票据有效期 |
| 用户票据续订最长期限 | 7天 | 票据可续订的最长时间 |
| 计算机时钟同步的最大容差 | 5分钟 | 防止重放攻击的时间窗口 |

### 8.2 本地策略

#### 8.2.1 审核策略

详细内容见"Windows日志系统与安全审计"章节，核心建议：
- 登录事件：成功+失败审核
- 账户登录事件：成功+失败审核
- 账户管理：成功+失败审核
- 策略更改：成功+失败审核
- 系统事件：成功+失败审核
- 进程追踪：成功审核（进程创建）
- 对象访问：按需配置

#### 8.2.2 用户权限分配

```
本地组策略编辑器 → 计算机配置 → Windows设置 → 安全设置 → 本地策略 → 用户权限分配
```

**关键权限配置**：

| 权限 | 推荐设置 | 说明 |
|------|----------|------|
| 从网络访问此计算机 | Administrators, Users | 限制可通过网络访问的用户 |
| 允许本地登录 | Administrators | 限制可本地登录的用户 |
| 允许通过远程桌面服务登录 | Administrators, Remote Desktop Users | 限制RDP访问 |
| 拒绝本地登录 | Guest, 其他受限账户 | 明确禁止的账户 |
| 拒绝从网络访问这台计算机 | Guest, 匿名账户 | 禁止网络访问 |
| 以操作系统方式执行 | （空） | 高危权限，不分配给普通用户 |
| 调试程序 | Administrators（按需移除） | SeDebugPrivilege，可被滥用 |
| 备份文件和目录 | Administrators | SeBackupPrivilege，可读取敏感文件 |
| 还原文件和目录 | Administrators | SeRestorePrivilege，可写入系统文件 |
| 管理审核和安全日志 | Administrators | 可修改审计策略和清除日志 |
| 关闭系统 | Administrators | 限制关闭系统的权限 |

#### 8.2.3 安全选项

```
本地组策略编辑器 → 计算机配置 → Windows设置 → 安全设置 → 本地策略 → 安全选项
```

**重要安全选项**：

| 策略 | 推荐值 | 说明 |
|------|--------|------|
| 账户：管理员账户状态 | 已禁用 | 禁用内置管理员账户 |
| 账户：来宾账户状态 | 已禁用 | 禁用Guest账户 |
| 账户：重命名系统管理员账户 | 自定义名称 | 重命名Administrator |
| 账户：重命名来宾账户 | 自定义名称 | 重命名Guest |
| 交互式登录：不显示最后的用户名 | 已启用 | 防止用户名泄露 |
| 交互式登录：提示用户在密码到期前更改密码 | 14天 | 提前提醒更换密码 |
| 交互式登录：计算机账户锁定阈值 | 10 | 限制失败次数 |
| 交互式登录：需要Ctrl+Alt+Del | 已启用 | 防止凭据窃取 |
| 网络安全：LAN管理器身份验证级别 | 仅发送NTLMv2响应。拒绝LM & NTLM | 禁用弱认证协议 |
| 网络安全：在下一次更改密码时不存储LAN管理器哈希值 | 已启用 | 防止LM哈希泄露 |
| 网络访问：不允许SAM账户的匿名枚举 | 已启用 | 防止信息泄露 |
| 网络访问：不允许SAM账户和共享的匿名枚举 | 已启用 | 防止信息泄露 |
| 网络访问：限制匿名访问命名管道和共享 | 已启用 | 限制匿名访问 |
| 设备：防止用户安装打印机驱动程序 | 已启用 | 防止驱动程序攻击 |
| 设备：只有本地登录的用户才能访问CD-ROM | 已启用 | 限制物理访问 |
| 系统对象：加强内部系统对象的默认权限 | 已启用 | 加强内核对象安全 |
| 关机：允许在未登录前关机 | 已禁用 | 防止未登录关机 |

### 8.3 用户账户控制（UAC）

#### 8.3.1 UAC概述

用户账户控制（User Account Control，UAC）是Windows的安全基础设施：
- 管理员默认以标准用户权限运行
- 执行需要管理员权限的操作时，提示用户确认
- 防止恶意软件在不知情的情况下获得管理员权限

#### 8.3.2 UAC级别

```
控制面板 → 用户账户 → 更改用户账户控制设置
```

| 级别 | 说明 | 推荐 |
|------|------|------|
| 始终通知 | 对所有更改都通知 | 高安全环境 |
| 默认 | 仅当程序尝试更改我的计算机时通知我 | 推荐设置 |
| 仅当程序尝试更改时不降低桌面亮度 | 与默认类似，但不锁定桌面 | 不推荐 |
| 从不通知 | 完全关闭UAC | 不推荐 |

#### 8.3.3 UAC组策略配置

```
本地组策略编辑器 → 计算机配置 → Windows设置 → 安全设置 → 本地策略 → 安全选项
```

| 策略 | 推荐值 |
|------|--------|
| 用户账户控制：管理员批准模式中管理员的提升权限提示行为 | 提示同意 |
| 用户账户控制：标准用户的提升权限提示行为 | 自动拒绝提升请求 |
| 用户账户控制：检测应用程序安装并提示提升 | 已启用 |
| 用户账户控制：仅提升安装在安全位置的UIAccess应用程序 | 已启用 |
| 用户账户控制：以管理员批准模式运行所有管理员 | 已启用 |
| 用户账户控制：用于内置管理员账户的管理员批准模式 | 已启用 |

### 8.4 Windows Defender配置

#### 8.4.1 Windows Defender概述

Windows Defender（现名Microsoft Defender）是Windows内置的杀毒软件：
- 从Windows 8开始内置，Windows 10/11功能完善
- 包含实时保护、云保护、样本提交等功能
- 是系统安全的基础防线

#### 8.4.2 PowerShell配置管理

```powershell
# 查看Windows Defender状态
Get-MpComputerStatus

# 查看实时保护状态
(Get-MpComputerStatus).RealTimeProtectionEnabled

# 启用/禁用实时保护
Set-MpPreference -DisableRealtimeMonitoring $false   # 启用
Set-MpPreference -DisableRealtimeMonitoring $true    # 禁用（不推荐）

# 启用云保护
Set-MpPreference -DisableCloudDeliveredProtection $false

# 配置排除项
Add-MpPreference -ExclusionPath "C:\Temp"
Add-MpPreference -ExclusionExtension ".log"
Add-MpPreference -ExclusionProcess "devenv.exe"

# 移除排除项
Remove-MpPreference -ExclusionPath "C:\Temp"

# 手动扫描
Start-MpScan -ScanType QuickScan
Start-MpScan -ScanType FullScan
Start-MpScan -ScanPath "C:\Users\Test"

# 更新定义
Update-MpSignature

# 查看威胁历史记录
Get-MpThreat
Get-MpThreatDetection
```

#### 8.4.3 最佳实践配置

```powershell
# 推荐的Defender配置
Set-MpPreference -DisableRealtimeMonitoring $false
Set-MpPreference -DisableCloudDeliveredProtection $false
Set-MpPreference -DisableBlockAtFirstSeen $false
Set-MpPreference -DisableBehaviorMonitoring $false
Set-MpPreference -DisableScriptScanning $false
Set-MpPreference -DisableRemovableDriveScanning $false
Set-MpPreference -DisableEmailScanning $false
Set-MpPreference -DisableArchiveScanning $false
Set-MpPreference -EnableControlledFolderAccess Enabled
Set-MpPreference -EnableNetworkProtection Enabled
Set-MpPreference -PUAProtection Enabled
```

### 8.5 自动更新与补丁管理

#### 8.5.1 Windows更新配置

```
设置 → 更新和安全 → Windows更新
或
控制面板 → Windows更新
```

```powershell
# 查看更新状态
Get-HotFix
Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 10

# 检查更新
(New-Object -ComObject Microsoft.Update.AutoUpdate).DetectNow()

# 查看更新服务状态
Get-Service -Name wuauserv
```

#### 8.5.2 补丁管理最佳实践

- **启用自动更新**：确保及时获取安全补丁
- **建立补丁测试流程**：生产环境补丁部署前先测试
- **定期扫描缺失补丁**：使用WSUS、SCCM等工具统一管理
- **紧急补丁快速部署**：高危漏洞补丁（如永恒之蓝）需紧急部署
- **保留补丁回滚能力**：确保补丁出问题时可回退

#### 8.5.3 WSUS与企业补丁管理

Windows Server Update Services（WSUS）是企业补丁管理方案：
- 集中下载和分发更新
- 控制更新批准和部署时间
- 生成更新合规报告
- 支持按计算机组分类部署

### 8.6 BitLocker磁盘加密

#### 8.6.1 BitLocker概述

BitLocker是Windows内置的全盘加密功能：
- 加密整个系统驱动器或数据驱动器
- 保护计算机丢失或被盗时的数据安全
- 支持TPM芯片、USB密钥、密码等多种保护方式
- 企业版/专业版及以上版本支持

#### 8.6.2 系统要求

- **TPM 1.2或2.0**：推荐配置，提供硬件级安全
- **BIOS/UEFI**：支持USB设备启动
- **系统分区**：需要独立的系统分区（通常100-500MB）

#### 8.6.3 BitLocker配置

```
控制面板 → BitLocker驱动器加密
或
设置 → 系统 → 关于 → BitLocker设置
```

```powershell
# 查看BitLocker状态
Get-BitLockerVolume
Get-BitLockerVolume -MountPoint "C:"

# 启用BitLocker（系统盘，使用TPM）
Enable-BitLocker -MountPoint "C:" -EncryptionMethod Aes256 -UsedSpaceOnly -TpmProtector

# 启用BitLocker（使用密码保护）
Enable-BitLocker -MountPoint "D:" -EncryptionMethod Aes256 -PasswordProtector -Password (ConvertTo-SecureString "YourPassword" -AsPlainText -Force)

# 备份恢复密钥
Backup-BitLockerKeyProtector -MountPoint "C:" -KeyProtectorId (Get-BitLockerVolume -MountPoint "C:").KeyProtector.KeyProtectorId[0]

# 挂起/恢复BitLocker
Suspend-BitLocker -MountPoint "C:" -RebootCount 1
Resume-BitLocker -MountPoint "C:"

# 解密驱动器
Disable-BitLocker -MountPoint "D:"
```

#### 8.6.4 恢复密钥管理

- **恢复密钥**：BitLocker出现问题时用于解锁驱动器的48位密钥
- **保存位置**：
  - Microsoft账户（推荐个人用户）
  - Active Directory（企业环境）
  - 文件（保存到安全位置）
  - 打印（纸质保存）
- **重要**：务必妥善保管恢复密钥，否则数据将永久丢失

### 8.7 应用程序控制策略

#### 8.7.1 AppLocker

AppLocker是Windows的应用程序控制功能：
- 控制哪些应用程序可以运行
- 支持EXE、DLL、脚本、Windows Installer、打包应用
- 支持发布者、路径、文件哈希三种规则类型
- 仅企业版/旗舰版/教育版支持

```
本地组策略编辑器 → 计算机配置 → Windows设置 → 安全设置 → 应用程序控制策略 → AppLocker
```

**规则类型**：
- **发布者规则**：基于数字签名，最灵活
- **路径规则**：基于文件路径，最简单
- **文件哈希规则**：基于文件哈希，最严格

**AppLocker模式**：
- **强制实施**：规则生效，阻止未允许的程序
- **仅审核**：不阻止，仅记录日志（测试阶段使用）

```powershell
# 查看AppLocker策略
Get-AppLockerPolicy -Effective
Get-AppLockerPolicy -Local

# 测试AppLocker策略
Test-AppLockerPolicy -Path C:\test\app.exe -User Everyone
```

#### 8.7.2 WDAC（Windows Defender应用程序控制）

WDAC（原Device Guard）是更强大的应用程序控制方案：
- 基于虚拟化的安全（VBS）提供更强保护
- 与HVCI（内存完整性）配合使用
- 支持Windows 10企业版及以上
- 策略可配置为仅允许受信任的应用运行

WDAC相比AppLocker的优势：
- 内核级保护，更难绕过
- 支持更多文件类型
- 与HVCI集成，防止内存篡改
- 可通过MOM/Intune集中管理

### 8.8 浏览器安全配置

#### 8.8.1 Microsoft Edge安全配置

- **启用SmartScreen**：防范恶意网站和下载
- **禁用自动填充密码**：使用密码管理器代替
- **禁用保存密码**：使用专业密码管理器
- **启用增强安全模式**：限制JavaScript等危险功能
- **定期清除浏览数据**：保护隐私
- **控制扩展程序**：只安装必要的扩展

#### 8.8.2 浏览器安全最佳实践

- **保持浏览器更新**：及时修补安全漏洞
- **使用扩展程序**：如uBlock Origin、NoScript等
- **警惕钓鱼网站**：检查URL和证书
- **不保存敏感信息**：不使用浏览器保存密码和信用卡信息
- **企业环境**：使用组策略统一配置浏览器安全策略

---

---

## 🛠️ 补充：实战拓展

### 安全基线检查脚本

```powershell
# Windows安全基线快速检查
function Invoke-SecurityBaselineCheck {
    Write-Host "=== 账户策略检查 ===" -ForegroundColor Cyan
    net accounts

    Write-Host "=== 防火墙状态 ===" -ForegroundColor Cyan
    Get-NetFirewallProfile | Select-Object Name, Enabled, DefaultInboundAction | Format-Table -AutoSize

    Write-Host "=== Windows Defender状态 ===" -ForegroundColor Cyan
    $defender = Get-MpComputerStatus -ErrorAction SilentlyContinue
    if ($defender) {
        Write-Host "实时保护: $($defender.RealTimeProtectionEnabled)"
        Write-Host "云保护: $($defender.CloudDeliveredProtectionEnabled)"
        Write-Host "反恶意软件版本: $($defender.AMServiceVersion)"
    } else {
        Write-Host "无法获取Defender状态" -ForegroundColor Yellow
    }

    Write-Host "=== 自动更新状态 ===" -ForegroundColor Cyan
    $autoUpdate = (New-Object -ComObject Microsoft.Update.AutoUpdate).Settings
    Write-Host "自动更新通知级别: $($autoUpdate.NotificationLevel)"

    Write-Host "=== BitLocker状态 ===" -ForegroundColor Cyan
    Get-BitLockerVolume -ErrorAction SilentlyContinue | Select-Object MountPoint, VolumeStatus, EncryptionMethod, ProtectionStatus | Format-Table -AutoSize

    Write-Host "=== UAC状态 ===" -ForegroundColor Cyan
    $uac = Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "EnableLUA" -ErrorAction SilentlyContinue
    Write-Host "UAC启用: $($uac.EnableLUA -eq 1)"
}
```

### 安全加固PowerShell命令速查

```powershell
# 密码策略
# （通过secedit配置，见上文）

# 禁用Guest账户
Disable-LocalUser -Name "Guest"

# 重命名管理员账户
Rename-LocalUser -Name "Administrator" -NewName "CustomAdmin"

# 启用UAC
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "EnableLUA" -Value 1

# 启用Windows Defender实时保护
Set-MpPreference -DisableRealtimeMonitoring $false

# 启用网络保护
Set-MpPreference -EnableNetworkProtection Enabled

# 启用PUA保护
Set-MpPreference -PUAProtection 1

# 禁用SMBv1（防止永恒之蓝等漏洞）
Disable-WindowsOptionalFeature -Online -FeatureName SMB1Protocol -NoRestart

# 禁用LLMNR
Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows NT\DNSClient" -Name "EnableMulticast" -Value 0 -Type DWord

# 禁用NetBIOS（如不需要）
# 需在网卡属性中配置
```

---

