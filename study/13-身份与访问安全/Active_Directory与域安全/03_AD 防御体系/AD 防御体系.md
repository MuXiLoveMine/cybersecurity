# AD 防御体系

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

---

## 📋 内容审核与补充建议

> 针对「AD 防御体系」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

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
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客
