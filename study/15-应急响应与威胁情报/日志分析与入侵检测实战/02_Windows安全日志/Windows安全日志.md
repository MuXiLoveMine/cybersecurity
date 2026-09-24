# Windows安全日志

### 2.1 关键事件ID

| 事件ID | 日志名称 | 说明 |
|--------|----------|------|
| 4624 | Security | 成功登录 |
| 4625 | Security | 登录失败 |
| 4634 | Security | 注销 |
| 4648 | Security | 显式凭证登录(runas) |
| 4656 | Security | 句柄请求(文件/注册表) |
| 4663 | Security | 对象访问 |
| 4672 | Security | 管理员登录分配的权限 |
| 4688 | Security | 进程创建 |
| 4698 | Security | 创建计划任务 |
| 4702 | Security | 修改计划任务 |
| 4720 | Security | 创建用户账户 |
| 4722 | Security | 启用用户账户 |
| 4724 | Security | 重置密码 |
| 4732 | Security | 添加成员到安全组 |
| 4776 | Security | NTLM认证 |
| 4779 | Security | 会话断开(SMB) |
| 4798 | Security | 用户组枚举 |
| 4825 | Security | Web服务拒绝访问 |
| 4946 | Security | 防火墙规则修改 |
| 5140 | Security | 网络共享访问 |
| 5145 | Security | 网络共享文件详细映射 |
| 5156 | Security | 防火墙允许连接 |
| 5157 | Security | 防火墙阻止连接 |
| 7045 | System | 服务创建 |
| 7036 | System | 服务状态变更 |

**登录类型 (Logon Type)**

| 类型 | 名称 | 说明 |
|------|------|------|
| 2 | Interactive | 交互式(本地键盘) |
| 3 | Network | 网络(SMB/共享) |
| 4 | Batch | 批处理 |
| 5 | Service | 服务 |
| 7 | Unlock | 解锁屏幕 |
| 8 | NetworkCleartext | 明文网络(自选) |
| 9 | NewCredentials | 新凭证(runas /netonly) |
| 10 | RemoteInteractive | 远程交互(RDP) |
| 11 | CachedInteractive | 缓存交互(离线) |
| 12 | RemoteInteractive | 远程交互(缓存) |
| 13 | CachedUnlock | 缓存解锁 |

### 2.2 登录审计分析

```powershell
# 查看所有成功登录
Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4624} | 
    Select-Object TimeCreated, 
        @{N='User';E={$_.Properties[5].Value}},
        @{N='LogonType';E={$_.Properties[8].Value}},
        @{N='SourceIP';E={$_.Properties[18].Value}}

# 查看登录失败(暴力破解检测)
Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4625} |
    Group-Object @{E={$_.Properties[5].Value}} |  # 按用户分组
    Where-Object {$_.Count -gt 10} |  # 失败超过10次
    Sort-Object Count -Descending

# 查看RDP登录
Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4624} |
    Where-Object {$_.Properties[8].Value -eq 10} |  # LogonType=10
    Select-Object TimeCreated,
        @{N='User';E={$_.Properties[5].Value}},
        @{N='SourceIP';E={$_.Properties[18].Value}}

# 检测非工作时间登录
Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4624} |
    Where-Object {
        $_.TimeCreated.Hour -lt 6 -or $_.TimeCreated.Hour -gt 22
    }
```

**4624事件解析**

```xml
<Event>
  <EventData>
    <Data Name="SubjectUserSid">S-1-5-18</Data>      <!-- [0] -->
    <Data Name="SubjectUserName">DESKTOP$</Data>       <!-- [1] -->
    <Data Name="TargetUserSid">S-1-5-21-...-1001</Data> <!-- [4] -->
    <Data Name="TargetUserName">admin</Data>           <!-- [5] -->
    <Data Name="TargetDomainName">DESKTOP</Data>        <!-- [6] -->
    <Data Name="LogonType">3</Data>                     <!-- [8] -->
    <Data Name="LogonProcessName">NtlmSsp</Data>        <!-- [9] -->
    <Data Name="AuthenticationPackageName">NTLM</Data> <!-- [10] -->
    <Data Name="WorkstationName">DESKTOP-PC</Data>      <!-- [11] -->
    <Data Name="IpAddress">192.168.1.50</Data>          <!-- [18] -->
    <Data Name="IpPort">49152</Data>                    <!-- [19] -->
  </EventData>
</Event>
```

### 2.3 进程审计

```powershell
# 启用进程审计
auditpol /set /subcategory:"Process Creation" /success:enable

# 查看进程创建事件
Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4688} |
    Select-Object TimeCreated,
        @{N='Process';E={$_.Properties[5].Value}},
        @{N='CommandLine';E={$_.Properties[8].Value}}

# 检测可疑进程创建
Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4688} |
    Where-Object {
        $_.Properties[8].Value -match 'powershell.*-enc' -or
        $_.Properties[8].Value -match 'cmd.*\/c' -or
        $_.Properties[8].Value -match 'certutil.*decode' -or
        $_.Properties[8].Value -match 'bitsadmin'
    }

# 启用命令行审计
# 注册表设置:
# HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\Audit\
#   CreateProcessCommandlineEnable = 1 (DWORD)
```

### 2.4 计划任务审计

```powershell
# 查看计划任务创建(持久化检测)
Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4698} |
    Select-Object TimeCreated,
        @{N='TaskName';E={$_.Properties[5].Value}},
        @{N='User';E={$_.Properties[1].Value}}

# 检测可疑计划任务
Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4698} |
    Where-Object {
        $_.Properties[5].Value -match 'Update|Security|Defender|Windows' -and
        $_.Properties[1].Value -notmatch 'SYSTEM|NETWORK SERVICE'
    }
```

---

---

