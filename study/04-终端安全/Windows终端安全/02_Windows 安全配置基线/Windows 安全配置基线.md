# Windows 安全配置基线

### 2.1 账户策略

**密码策略**

| 策略 | 推荐值 | 说明 |
|------|--------|------|
| 密码必须符合复杂性要求 | 已启用 | 密码需包含大小写字母、数字、特殊字符中的3类 |
| 密码长度最小值 | 14个字符 | 越长越安全，NIST 建议至少8位，高安全环境14位以上 |
| 密码最短使用期限 | 1天 | 防止用户频繁更换密码绕过历史记录 |
| 密码最长使用期限 | 90天 | 定期更换密码 |
| 强制密码历史 | 24个记住的密码 | 防止重复使用旧密码 |
| 用可还原的加密来存储密码 | 已禁用 | 除非有特殊需求，否则必须禁用 |

**账户锁定策略**

| 策略 | 推荐值 | 说明 |
|------|--------|------|
| 账户锁定阈值 | 5次无效登录 | 防止暴力破解 |
| 账户锁定时间 | 30分钟 | 锁定后自动解锁时间 |
| 重置账户锁定计数器 | 30分钟 | 失败计数重置时间 |

**Kerberos 策略（域环境）**

| 策略 | 推荐值 | 说明 |
|------|--------|------|
| 强制用户登录限制 | 已启用 | 验证用户账户的登录权限 |
| 服务票证最长寿命 | 600分钟 | 服务票据有效期 |
| 用户票证最长寿命 | 10小时 | TGT 有效期 |
| 用户票证续订最长寿命 | 7天 | TGT 可续订期限 |
| 计算机账户密码最长使用期限 | 30天 | 域机器账户密码更换周期 |

**配置命令**

```powershell
# 使用本地安全策略命令行工具
secedit /export /cfg C:\temp\secpol.cfg

# 修改密码策略（在导出的配置文件中修改后导入）
# [System Access]
# MinimumPasswordAge = 1
# MaximumPasswordAge = 90
# MinimumPasswordLength = 14
# PasswordComplexity = 1
# PasswordHistorySize = 24
# LockoutBadCount = 5
# LockoutDuration = 30
# ResetLockoutCount = 30

secedit /configure /db C:\Windows\security\local.sdb /cfg C:\temp\secpol.cfg /areas SECURITYPOLICY
```

### 2.2 审核策略

**基本审核策略**

| 策略 | 推荐设置 | 说明 |
|------|----------|------|
| 审核账户登录事件 | 成功,失败 | 记录域控制器上的账户登录验证 |
| 审核账户管理 | 成功,失败 | 记录账户创建、修改、删除、密码更改等 |
| 审核目录服务访问 | 失败 | 记录 AD 对象访问（仅域控制器） |
| 审核登录事件 | 成功,失败 | 记录本地登录/注销事件 |
| 审核对象访问 | 失败 | 记录文件、注册表等对象访问 |
| 审核策略更改 | 成功,失败 | 记录安全策略更改 |
| 审核特权使用 | 失败 | 记录用户权限的使用 |
| 审核过程追踪 | 无 | 记录进程创建/终止（详细但日志量大） |
| 审核系统事件 | 成功,失败 | 记录系统启动/关机等事件 |

**高级审核策略（推荐）**

```
账户登录
├── 审核凭据验证 → 成功,失败
├── 审核 Kerberos 身份验证服务 → 成功,失败
├── 审核 Kerberos 服务票据操作 → 成功,失败
└── 审核其他账户登录事件 → 成功,失败

账户管理
├── 审核计算机账户管理 → 成功
├── 审核分发组管理 → 成功
├── 审核安全组管理 → 成功,失败
├── 审核其他账户管理事件 → 成功,失败
└── 审核用户账户管理 → 成功,失败

详细追踪
├── 审核进程创建 → 成功（含命令行）
├── 审核进程终止 → 成功
└── 审核 RPC 事件 → 无

登录/注销
├── 审核账户锁定 → 失败
├── 审核组成员身份 → 成功
├── 审核交互式登录 → 成功,失败
├── 审核网络策略服务器 → 成功,失败
├── 审核其他登录/注销事件 → 成功,失败
└── 审核特殊登录 → 成功,失败

对象访问
├── 审核文件系统 → 失败
├── 审核注册表 → 失败
├── 审核筛选平台连接 → 失败
└── 审核其他对象访问事件 → 失败

策略更改
├── 审核审核策略更改 → 成功,失败
├── 审核身份验证策略更改 → 成功
└── 审核授权策略更改 → 成功,失败

特权使用
├── 审核非敏感特权使用 → 无
├── 审核敏感特权使用 → 失败
└── 审核其他特权使用事件 → 失败

系统
├── 审核 IPsec 驱动程序 → 成功,失败
├── 审核其他系统事件 → 成功,失败
├── 审核安全状态更改 → 成功
└── 审核系统完整性 → 失败
```

**启用进程创建审核（含命令行）**

```powershell
# 启用进程创建审核
auditpol /set /subcategory:"Process Creation" /success:enable /failure:enable

# 启用命令行审计（注册表）
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\Audit" /v ProcessCreationIncludeCmdLine_Enabled /t REG_DWORD /d 1 /f

# 查看审核策略
auditpol /get /category:*
```

**重要事件 ID**

| 事件 ID | 描述 |
|---------|------|
| 4624 | 账户成功登录 |
| 4625 | 账户登录失败 |
| 4634 | 账户注销 |
| 4648 | 显式凭据登录（runas等） |
| 4672 | 管理员登录（特殊权限登录） |
| 4688 | 进程创建 |
| 4697 | 服务安装 |
| 4698 | 计划任务创建 |
| 4720 | 用户账户创建 |
| 4726 | 用户账户删除 |
| 4732 | 成员添加到本地组 |
| 4738 | 用户账户更改 |
| 4776 | NTLM 身份验证 |
| 7045 | 服务安装（System日志） |

### 2.3 防火墙配置

**Windows Defender 防火墙基本配置**

```powershell
# 启用防火墙（所有配置文件）
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True

# 设置默认入站策略为阻止
Set-NetFirewallProfile -Profile Domain,Public,Private -DefaultInboundAction Block

# 设置默认出站策略为允许（可根据需要改为阻止）
Set-NetFirewallProfile -Profile Domain,Public,Private -DefaultOutboundAction Allow

# 显示防火墙配置文件状态
Get-NetFirewallProfile | Select-Object Name, Enabled, DefaultInboundAction, DefaultOutboundAction
```

**常用入站规则配置**

```powershell
# 允许 ICMP（Ping）
New-NetFirewallRule -DisplayName "Allow ICMPv4-In" -Protocol ICMPv4 -IcmpType 8 -Direction Inbound -Action Allow -Enabled True

# 允许 RDP（仅指定 IP 段）
New-NetFirewallRule -DisplayName "Allow RDP from Internal" -Direction Inbound -Protocol TCP -LocalPort 3389 -RemoteAddress 192.168.1.0/24 -Action Allow -Enabled True

# 允许 SSH
New-NetFirewallRule -DisplayName "Allow SSH-In" -Direction Inbound -Protocol TCP -LocalPort 22 -Action Allow -Enabled True

# 阻止特定端口
New-NetFirewallRule -DisplayName "Block Telnet" -Direction Inbound -Protocol TCP -LocalPort 23 -Action Block -Enabled True
```

**常用出站规则配置**

```powershell
# 阻止 SMB 出站（防止横向移动）
New-NetFirewallRule -DisplayName "Block SMB Outbound" -Direction Outbound -Protocol TCP -RemotePort 445 -Action Block -Enabled True

# 阻止远程 PowerShell 出站
New-NetFirewallRule -DisplayName "Block WinRM Outbound" -Direction Outbound -Protocol TCP -RemotePort 5985,5986 -Action Block -Enabled True
```

**加固建议**

1. 启用所有配置文件的防火墙
2. 默认入站策略设置为"阻止"
3. 仅开放必要的端口，遵循最小权限原则
4. 限制远程管理端口（RDP、WinRM、SSH）的源地址
5. 考虑启用出站过滤（白名单模式）
6. 定期审查防火墙规则，清理不必要的规则

---

---

