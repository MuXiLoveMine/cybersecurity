# RDP与远程访问安全加固

### 5.1 RDP协议基础与安全风险

#### 5.1.1 RDP协议概述

远程桌面协议（Remote Desktop Protocol，RDP）是微软开发的多通道远程显示协议：
- 默认端口：TCP 3389，UDP 3389（Windows 8/Server 2012起支持UDP传输）
- 基于TPC/IP协议栈，支持多种数据通道传输
- 支持虚拟通道扩展：打印机重定向、剪贴板、驱动器重定向等
- 当前版本：RDP 10.x

#### 5.1.2 RDP安全风险

**网络层风险**：
- 端口暴露：3389端口是常见的扫描和攻击目标
- 暴力破解：针对弱口令账户的密码爆破攻击
- 中间人攻击：未正确配置加密时可能被截获数据

**协议层风险**：
- BlueKeep（CVE-2019-0708）：RDP远程代码执行漏洞，影响Windows XP/7/2008
- DejaBlue：Windows 7/2008 R2/2003等系统的RDP漏洞
- 其他RDP相关漏洞：每年都有新的RDP漏洞被发现

**会话层风险**：
- 会话劫持：获取已建立的RDP会话控制权
- 剪贴板重定向：恶意程序通过剪贴板传播
- 驱动器重定向：本地磁盘被映射到远程主机，成为攻击通道
- 弱加密配置：使用过时的加密算法

**账户安全风险**：
- 弱口令账户：Administrator等常见账户的弱密码
- 凭据窃取：通过Keylogger等方式窃取登录凭据
- 凭据转发：RDP会话中的凭据可能被转发利用

### 5.2 RDP安全配置

#### 5.2.1 启用网络级别认证（NLA）

网络级别认证（Network Level Authentication，NLA）要求用户在建立完整RDP连接前完成身份验证：
- 减少资源消耗，降低拒绝服务攻击影响
- 更早验证身份，防止未认证连接
- 是RDP安全的基本配置，建议始终启用

```powershell
# 查看NLA配置
Get-CimInstance Win32_TerminalServiceSetting -Namespace root\cimv2\terminalservices |
    Select-Object Name, UserAuthenticationRequired

# 启用NLA
(Get-CimInstance Win32_TerminalServiceSetting -Namespace root\cimv2\terminalservices).SetUserAuthenticationRequired(1)

# 注册表方式
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" -Name "UserAuthentication" -Value 1
```

#### 5.2.2 加密级别配置

RDP支持四种加密级别：
- **低（Low）**：仅加密从客户端到服务器的数据，使用56位加密
- **客户端兼容（Client Compatible）**：使用客户端支持的最大密钥强度加密双向数据
- **高（High）**：使用128位加密双向数据
- **符合FIPS（FIPS Compliant）**：使用FIPS加密算法加密双向数据

```powershell
# 注册表配置加密级别
# 1 = 低, 2 = 客户端兼容, 3 = 高, 4 = FIPS
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" -Name "MinEncryptionLevel" -Value 3
```

#### 5.2.3 RDP安全层

RDP安全层决定了连接建立时使用的安全协议：

```powershell
# 注册表配置安全层
# 0 = RDP安全层, 1 = 协商(默认), 2 = SSL(TLS 1.0)
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" -Name "SecurityLayer" -Value 2
```

建议设置为SSL（TLS）方式，配合证书使用提供更强的安全性。

#### 5.2.4 图形界面配置

```
运行 → sysdm.cpl → 远程选项卡
或
运行 → gpedit.msc → 计算机配置 → 管理模板 → Windows组件 → 远程桌面服务 → 远程桌面会话主机 → 安全
```

相关组策略设置：
- 要求使用特定的安全层进行远程（RDP）连接
- 要求使用网络级别身份验证对远程连接进行用户身份验证
- 客户端连接加密级别
- 设置远程桌面服务用户会话远程控制的规则

### 5.3 端口修改与防火墙规则

#### 5.3.1 修改RDP默认端口

修改默认端口是一种"安全通过隐蔽性"的手段，虽然不能阻止专业攻击，但可以降低自动化扫描和暴力破解的概率。

```powershell
# 修改RDP端口（需重启RDP服务生效）
$rdpPort = 33899  # 新端口号
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" -Name "PortNumber" -Value $rdpPort -Type DWord

# 重启远程桌面服务
Restart-Service -Name TermService -Force
```

```cmd
:: 也可以使用reg命令
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" /v PortNumber /t REG_DWORD /d 33899 /f
```

#### 5.3.2 防火墙规则配置

```powershell
# 放行新的RDP端口
$rdpPort = 33899
New-NetFirewallRule -DisplayName "允许RDP（自定义端口）" -Direction Inbound -Protocol TCP -LocalPort $rdpPort -Action Allow

# 限制来源IP（推荐）
New-NetFirewallRule -DisplayName "允许RDP（仅限管理IP）" -Direction Inbound -Protocol TCP -LocalPort $rdpPort -RemoteAddress "192.168.1.0/24", "10.0.0.5" -Action Allow

# 禁用默认RDP规则
Disable-NetFirewallRule -DisplayGroup "远程桌面"
```

#### 5.3.3 修改后连接方式

```
mstsc /v:服务器IP:端口号
```

或在远程桌面连接客户端的"计算机"字段中输入 `IP:端口`。

### 5.4 账户锁定策略

#### 5.4.1 账户锁定阈值

账户锁定策略可以有效防止暴力破解攻击，多次登录失败后锁定账户：

**配置路径**：
```
本地组策略编辑器 → 计算机配置 → Windows设置 → 安全设置 → 账户策略 → 账户锁定策略
```

| 策略 | 推荐值 | 说明 |
|------|--------|------|
| 账户锁定阈值 | 5次无效登录 | 5次失败后锁定账户 |
| 账户锁定时间 | 30分钟 | 锁定持续时间 |
| 重置账户锁定计数器 | 30分钟 | 失败计数重置时间 |

```powershell
# 使用PowerShell配置（需要管理员权限）
# 方法：通过secedit导出/导入安全策略
secedit /export /cfg "C:\temp\secpol.cfg" /areas SECURITYPOLICY

# 修改配置文件中的锁定策略后重新导入
# 锁定阈值：LockoutBadCount = 5
# 锁定时间：LockoutDuration = 30
# 重置时间：ResetLockoutCount = 30

secedit /configure /db "C:\Windows\security\local.sdb" /cfg "C:\temp\secpol.cfg" /areas SECURITYPOLICY
```

#### 5.4.2 重命名管理员账户

默认Administrator账户是暴力破解的首选目标，重命名可降低风险：

```
本地组策略编辑器 → 计算机配置 → Windows设置 → 安全设置 → 本地策略 → 安全选项 → 账户：重命名系统管理员账户
```

```powershell
# PowerShell重命名管理员账户
Rename-LocalUser -Name "Administrator" -NewName "AdminUser"
```

#### 5.4.3 禁用Guest账户

```powershell
# 禁用Guest账户
Disable-LocalUser -Name "Guest"
```

### 5.5 多因素认证配置

#### 5.5.1 MFA概述

多因素认证（Multi-Factor Authentication，MFA）要求用户提供两种或以上的验证因素：
- **知识因素**：密码、PIN码
- **持有因素**：手机令牌、硬件令牌、短信验证码
- **固有因素**：指纹、面部识别、虹膜扫描

#### 5.5.2 Windows Hello企业版

Windows Hello企业版是微软推荐的强身份验证方案：
- 基于证书或密钥的双因素认证
- 替代密码，支持生物识别（指纹、面部）
- 支持Active Directory和Azure AD
- 配置通过组策略或MDM完成

```
组策略路径：
计算机配置 → 管理模板 → Windows组件 → Windows Hello企业版
```

#### 5.5.3 RD网关与MFA

远程桌面网关（RD Gateway）配合NPS（网络策略服务器）可实现RDP的MFA：
- RD Gateway提供HTTPS上的RDP连接
- NPS支持RADIUS协议，可集成第三方MFA解决方案
- 常见方案：Azure MFA、Duo、RSA SecurID等

#### 5.5.4 第三方MFA方案

| 方案 | 说明 |
|------|------|
| Azure AD MFA | 微软云MFA服务，支持Azure AD和本地AD |
| Duo Security | Cisco旗下，支持多种应用的MFA |
| Google Authenticator | 基于TOTP的免费方案，需配合RD网关 |
| RSA SecurID | 企业级硬件令牌方案 |

### 5.6 跳板机与堡垒机概念

#### 5.6.1 跳板机（Jump Server）

跳板机是一种网络安全架构设计：
- 所有远程管理连接必须先经过跳板机
- 跳板机是唯一可以直接访问目标服务器的节点
- 目标服务器的RDP/SSH仅对跳板机IP开放

**安全优势**：
- 减少攻击面：目标服务器不直接暴露管理端口
- 集中管控：所有管理操作经过统一入口
- 审计追溯：跳板机可记录所有操作日志

#### 5.6.2 堡垒机（Bastion Host）

堡垒机是更完善的跳板机方案，通常包含：
- **身份认证**：统一身份管理、多因素认证
- **权限控制**：细粒度的访问控制和命令审批
- **操作审计**：全程录屏、命令审计、日志记录
- **会话管理**：会话监控、会话中断、会话回放

#### 5.6.3 Windows环境跳板机配置要点

```
1. 独立的网络区域（DMZ或管理网段）
2. 严格的防火墙规则：仅允许特定IP访问跳板机RDP
3. 目标服务器RDP仅允许跳板机IP访问
4. 跳板机启用完整的安全审计和日志记录
5. 跳板机使用强密码或MFA认证
6. 定期更新和加固跳板机系统
7. 跳板机不用于日常办公，仅用于管理操作
```

### 5.7 WinRM与PowerShell远程管理安全

#### 5.7.1 WinRM概述

Windows远程管理（WinRM）是基于Web服务管理（WS-Management）协议的远程管理技术：
- 默认端口：HTTP 5985，HTTPS 5986
- PowerShell远程管理（PowerShell Remoting）基于WinRM
- 是Windows Server的核心管理通道

#### 5.7.2 WinRM安全配置

```powershell
# 查看WinRM配置
winrm get winrm/config

# 启用WinRM（HTTP）
Enable-PSRemoting -Force

# 配置WinRM HTTPS（推荐，使用SSL加密）
# 需要先安装证书
winrm create winrm/config/Listener?Address=*+Transport=HTTPS "@{Hostname=`"server01.example.com`"; CertificateThumbprint=`"证书指纹`"}"

# 配置WinRM服务
winrm set winrm/config/service/Auth "@{Basic=`"false`"}"      # 禁用基本认证
winrm set winrm/config/service/Auth "@{Kerberos=`"true`"}"   # 启用Kerberos
winrm set winrm/config/service/Auth "@{Negotiate=`"true`"}"  # 启用协商
winrm set winrm/config/service "@{AllowUnencrypted=`"false`"}"  # 禁止未加密传输
```

#### 5.7.3 PowerShell远程管理安全

```powershell
# 测试远程连接
Test-WSMan -ComputerName server01

# 创建PSSession
Enter-PSSession -ComputerName server01
Enter-PSSession -ComputerName server01 -Credential (Get-Credential)

# 使用HTTPS连接
Enter-PSSession -ComputerName server01 -UseSSL -Credential (Get-Credential)

# 查看会话配置
Get-PSSessionConfiguration

# 受限会话配置（JEA - Just Enough Administration）
# 可配置用户只能执行特定命令
```

#### 5.7.4 JEA（Just Enough Administration）

JEA是PowerShell的最小权限管理技术：
- 用户以虚拟管理员账户执行指定命令
- 限制可执行的命令和参数
- 所有操作都有详细日志记录
- 通过会话配置文件定义权限

```powershell
# JEA配置示例（概念）
# 1. 创建会话配置文件
New-PSSessionConfigurationFile -Path "C:\JEA\AdminSupport.pssc" -SessionType RestrictedRemoteServer

# 2. 创建角色能力文件
New-PSRoleCapabilityFile -Path "C:\JEA\HelpDeskRole.psrc" -VisibleCmdlets @("Restart-Service", "Get-Service")

# 3. 注册会话配置
Register-PSSessionConfiguration -Name "AdminSupport" -Path "C:\JEA\AdminSupport.pssc"
```

---

---

## 🛠️ 补充：实战拓展

### RDP安全加固检查清单

```powershell
# RDP安全审计脚本
function Invoke-RDPSecurityAudit {
    Write-Host "=== RDP服务状态 ===" -ForegroundColor Cyan
    Get-Service -Name TermService | Select-Object Name, Status, StartType

    Write-Host "=== RDP启用状态 ===" -ForegroundColor Cyan
    $rdpEnabled = Get-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server" -Name "fDenyTSConnections" -ErrorAction SilentlyContinue
    if ($rdpEnabled) {
        Write-Host "RDP启用: $($rdpEnabled.fDenyTSConnections -eq 0)"
    }

    Write-Host "=== NLA配置 ===" -ForegroundColor Cyan
    $nla = Get-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" -Name "UserAuthentication" -ErrorAction SilentlyContinue
    Write-Host "网络级别认证(NLA): $($nla.UserAuthentication -eq 1)"

    Write-Host "=== RDP端口 ===" -ForegroundColor Cyan
    $port = Get-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" -Name "PortNumber" -ErrorAction SilentlyContinue
    Write-Host "RDP端口: $($port.PortNumber)"

    Write-Host "=== 加密级别 ===" -ForegroundColor Cyan
    $enc = Get-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" -Name "MinEncryptionLevel" -ErrorAction SilentlyContinue
    $encLevel = switch ($enc.MinEncryptionLevel) { 1 { "低" } 2 { "客户端兼容" } 3 { "高" } 4 { "FIPS" } default { "未知" } }
    Write-Host "加密级别: $encLevel"

    Write-Host "=== 防火墙规则 ===" -ForegroundColor Cyan
    Get-NetFirewallRule -DisplayGroup "远程桌面" -ErrorAction SilentlyContinue | Select-Object DisplayName, Enabled, Direction, Action

    Write-Host "=== 账户锁定策略 ===" -ForegroundColor Cyan
    net accounts
}
```

### RDP安全加固PowerShell脚本

```powershell
# RDP一键加固脚本（需管理员权限）
function Invoke-RDPHardening {
    param(
        [int]$RDPPort = 33899,
        [string[]]$AllowedIPs = @("192.168.1.0/24")
    )

    Write-Host "开始RDP安全加固..." -ForegroundColor Yellow

    # 1. 启用NLA
    Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" -Name "UserAuthentication" -Value 1 -Type DWord
    Write-Host "[+] 已启用网络级别认证(NLA)" -ForegroundColor Green

    # 2. 设置加密级别为高
    Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" -Name "MinEncryptionLevel" -Value 3 -Type DWord
    Write-Host "[+] 已设置加密级别为高" -ForegroundColor Green

    # 3. 设置安全层为SSL
    Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" -Name "SecurityLayer" -Value 2 -Type DWord
    Write-Host "[+] 已设置安全层为SSL(TLS)" -ForegroundColor Green

    # 4. 修改RDP端口
    Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" -Name "PortNumber" -Value $RDPPort -Type DWord
    Write-Host "[+] 已修改RDP端口为 $RDPPort" -ForegroundColor Green

    # 5. 配置防火墙规则
    Disable-NetFirewallRule -DisplayGroup "远程桌面" -ErrorAction SilentlyContinue
    New-NetFirewallRule -DisplayName "允许RDP（自定义端口）" -Direction Inbound -Protocol TCP -LocalPort $RDPPort -RemoteAddress $AllowedIPs -Action Allow
    Write-Host "[+] 已配置防火墙规则，仅允许IP: $($AllowedIPs -join ', ')" -ForegroundColor Green

    # 6. 重启RDP服务
    Restart-Service -Name TermService -Force
    Write-Host "[+] 已重启RDP服务" -ForegroundColor Green

    Write-Host "`nRDP安全加固完成！" -ForegroundColor Green
    Write-Host "新RDP端口: $RDPPort"
    Write-Host "连接命令: mstsc /v:<IP>:$RDPPort"
}
```

---

## 📋 内容审核与补充建议

> 针对「RDP与远程访问安全加固」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 💡 知识拓展
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### ⚔️ 攻击技术
- ⚠️ 缺少attack相关内容

### 📖 参考资料
- ⚠️ 缺少参考资料/延伸阅读

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：Microsoft Docs、MSDN、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客
