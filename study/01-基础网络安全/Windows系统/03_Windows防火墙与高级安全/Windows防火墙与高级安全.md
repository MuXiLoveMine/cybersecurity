# Windows防火墙与高级安全

### 3.1 Windows防火墙基础

#### 3.1.1 防火墙概述

Windows Defender防火墙（原Windows防火墙）是Windows内置的主机防火墙，提供基于主机的双向流量过滤：
- 从Windows XP SP2开始引入，Windows 7/Server 2008 R2后功能大幅增强
- 默认启用，提供入站和出站过滤
- 支持基于配置文件的策略切换

#### 3.1.2 配置文件（网络位置）

Windows防火墙根据网络位置自动切换配置文件：

| 配置文件 | 适用场景 | 默认策略 |
|----------|----------|----------|
| 域配置文件 | 加入域的网络 | 较为宽松，允许域内通信 |
| 专用配置文件 | 家庭/工作网络（可信） | 中等严格，发现设备和文件共享 |
| 公用配置文件 | 公共场所网络（不可信） | 最严格，阻止所有入站连接 |

```powershell
# 查看当前网络配置文件
Get-NetConnectionProfile

# 设置网络配置文件
Set-NetConnectionProfile -InterfaceAlias "以太网" -NetworkCategory Private
Set-NetConnectionProfile -InterfaceAlias "以太网" -NetworkCategory Public
```

#### 3.1.3 入站与出站规则

**入站规则**：控制从外部到本机的流量
- 默认阻止所有未明确允许的入站连接
- 可按程序、端口、预定义服务、自定义规则配置

**出站规则**：控制从本机到外部的流量
- 默认允许所有出站连接
- 可配置阻止规则限制特定程序的网络访问

```powershell
# 查看防火墙状态
Get-NetFirewallProfile
Get-NetFirewallProfile -Name Domain,Private,Public

# 启用/禁用防火墙
Set-NetFirewallProfile -Profile Domain,Private,Public -Enabled True
Set-NetFirewallProfile -Profile Public -Enabled False
```

### 3.2 高级安全防火墙（wf.msc）

#### 3.2.1 打开高级安全防火墙

```
运行 → wf.msc
或
控制面板 → 系统和安全 → Windows Defender防火墙 → 高级设置
```

#### 3.2.2 高级安全防火墙界面

高级安全防火墙（Windows Defender Firewall with Advanced Security）提供完整的防火墙管理功能：

- **入站规则**：管理入站连接规则
- **出站规则**：管理出站连接规则
- **连接安全规则**：IPsec连接安全规则
- **监视**：查看当前活动规则、安全关联、快速模式等

#### 3.2.3 规则类型

| 规则类型 | 说明 |
|----------|------|
| 程序 | 基于可执行文件路径配置规则 |
| 端口 | 基于TCP/UDP端口配置规则 |
| 预定义 | Windows内置服务的预定义规则集 |
| 自定义 | 组合程序、协议、端口、源/目标IP等 |

#### 3.2.4 规则属性

每条防火墙规则包含以下关键属性：
- **常规**：名称、描述、是否启用、操作（允许/阻止）
- **程序和服务**：适用的程序路径和服务
- **协议和端口**：协议类型（TCP/UDP/ICMP等）、本地端口、远程端口
- **作用域**：本地IP地址、远程IP地址
- **高级**：适用的配置文件（域/专用/公用）、接口类型
- **用户和计算机**：基于用户或计算机的规则（需要IPsec）

### 3.3 防火墙规则配置

#### 3.3.1 GUI方式创建规则

以"允许RDP入站连接"为例：
1. 打开 `wf.msc` → 入站规则 → 新建规则
2. 规则类型选择"端口" → 下一步
3. 选择"TCP" → 特定本地端口输入"3389" → 下一步
4. 选择"允许连接" → 下一步
5. 选择适用的配置文件（域、专用、公用）→ 下一步
6. 输入规则名称和描述 → 完成

#### 3.3.2 netsh命令配置

```cmd
:: 查看所有入站规则
netsh advfirewall firewall show rule name=all dir=in

:: 添加入站规则（允许3389端口）
netsh advfirewall firewall add rule name="允许RDP" dir=in action=allow protocol=TCP localport=3389

:: 添加入站规则（限制IP范围）
netsh advfirewall firewall add rule name="限制RDP来源" dir=in action=allow protocol=TCP localport=3389 remoteip=192.168.1.0/24

:: 添加程序规则
netsh advfirewall firewall add rule name="允许Chrome" dir=out action=allow program="C:\Program Files\Google\Chrome\Application\chrome.exe"

:: 启用/禁用规则
netsh advfirewall firewall set rule name="允许RDP" new enable=yes
netsh advfirewall firewall set rule name="允许RDP" new enable=no

:: 删除规则
netsh advfirewall firewall delete rule name="允许RDP"

:: 修改规则
netsh advfirewall firewall set rule name="允许RDP" new remoteip=10.0.0.0/8
```

#### 3.3.3 PowerShell命令配置

```powershell
# 查看入站规则
Get-NetFirewallRule -Direction Inbound
Get-NetFirewallRule -DisplayName "*RDP*"
Get-NetFirewallRule -Enabled True -Direction Inbound

# 查看规则详细信息（含端口）
Get-NetFirewallRule -DisplayName "远程桌面 - 用户模式(TCP-In)" | Get-NetFirewallPortFilter

# 新建入站规则
New-NetFirewallRule -DisplayName "允许RDP" -Direction Inbound -Protocol TCP -LocalPort 3389 -Action Allow

# 新建带IP限制的规则
New-NetFirewallRule -DisplayName "限制RDP来源" -Direction Inbound -Protocol TCP -LocalPort 3389 -RemoteAddress 192.168.1.0/24 -Action Allow

# 新建程序规则
New-NetFirewallRule -DisplayName "阻止Chrome出站" -Direction Outbound -Program "C:\Program Files\Google\Chrome\Application\chrome.exe" -Action Block

# 启用/禁用规则
Enable-NetFirewallRule -DisplayName "允许RDP"
Disable-NetFirewallRule -DisplayName "允许RDP"

# 删除规则
Remove-NetFirewallRule -DisplayName "允许RDP"

# 修改规则
Set-NetFirewallRule -DisplayName "允许RDP" -RemoteAddress 10.0.0.0/8
```

### 3.4 连接安全规则（IPsec）

#### 3.4.1 IPsec概述

连接安全规则使用Internet协议安全（IPsec）保护网络流量：
- 提供身份验证、完整性、加密保护
- 与防火墙规则配合使用，实现端到端安全通信
- 支持多种身份验证方式：Kerberos、证书、预共享密钥

#### 3.4.2 连接安全规则类型

| 规则类型 | 说明 |
|----------|------|
| 隔离 | 根据身份验证标准限制连接 |
| 身份验证豁免 | 免除特定计算机的身份验证要求 |
| 服务器到服务器 | 保护两台特定计算机之间的通信 |
| 隧道 | 保护两个网关之间的隧道通信 |
| 自定义 | 自定义连接安全规则 |

#### 3.4.3 IPsec配置示例

```cmd
:: 配置IPsec规则（服务器到服务器）
netsh advfirewall consec add rule name="服务器间IPsec" endpoint1=192.168.1.10 endpoint2=192.168.1.20 action=requireinrequestout auth1=computercert auth1ca="CN=CA01"
```

```powershell
# 查看连接安全规则
Get-NetIPsecRule

# 新建服务器到服务器IPsec规则
New-NetIPsecRule -DisplayName "安全服务器通信" -InboundSecurity Require -OutboundSecurity Request -RemoteAddress 192.168.1.0/24 -Phase1AuthSet "计算机证书" -Phase2AuthSet "用户证书"

# 监控IPsec安全关联
Get-NetIPsecMainModeSA
Get-NetIPsecQuickModeSA
```

### 3.5 防火墙日志配置与分析

#### 3.5.1 启用防火墙日志

**图形界面配置**：
1. 打开 `wf.msc` → 右键"Windows Defender 防火墙高级安全" → 属性
2. 选择对应配置文件选项卡 → 日志 → 自定义
3. 设置日志文件路径、大小限制、记录选项

```cmd
:: 配置防火墙日志
netsh advfirewall set currentprofile logging filename "C:\logs\firewall.log"
netsh advfirewall set currentprofile logging maxfilesize 4096
netsh advfirewall set currentprofile logging droppedconnections enable
netsh advfirewall set currentprofile logging allowedconnections enable
```

```powershell
# 配置防火墙日志
Set-NetFirewallProfile -Profile Domain,Private,Public -LogFileName "C:\logs\firewall.log" -LogMaxSizeKilobytes 4096 -LogAllowed True -LogBlocked True
```

#### 3.5.2 日志格式

Windows防火墙日志为W3C扩展日志文件格式，字段包括：
- `date time`：日期时间
- `action`：操作（ALLOW/DROP）
- `protocol`：协议（TCP/UDP/ICMP等）
- `src-ip dst-ip`：源/目标IP
- `src-port dst-port`：源/目标端口
- `size`：数据包大小
- `tcpflags`：TCP标志位
- `tcpsyn tcpack tcpwin`：TCP序列号等
- `icmptype icmpcode`：ICMP类型和代码
- `info`：附加信息
- `path`：路径（发送/接收/转发）

#### 3.5.3 日志分析

```powershell
# 解析防火墙日志
$logPath = "C:\Windows\System32\LogFiles\Firewall\pfirewall.log"
$logs = Import-Csv -Path $logPath -Delimiter " " -Header date,time,action,protocol,srcip,dstip,srcport,dstport,size,tcpflags,tcpsyn,tcpack,tcpwin,icmptype,icmpcode,info,path -Skip 5

# 查看被阻止的入站连接
$logs | Where-Object { $_.action -eq "DROP" -and $_.path -eq "RECEIVE" } | Group-Object srcip | Sort-Object Count -Descending | Select-Object -First 10

# 统计被阻止的端口
$logs | Where-Object { $_.action -eq "DROP" } | Group-Object dstport | Sort-Object Count -Descending | Select-Object -First 10
```

### 3.6 常见服务端口放行配置

#### 3.6.1 常用服务端口表

| 服务 | 端口 | 协议 | 说明 |
|------|------|------|------|
| RDP | 3389 | TCP | 远程桌面 |
| HTTP | 80 | TCP | Web服务 |
| HTTPS | 443 | TCP | 加密Web服务 |
| FTP | 21 | TCP | 文件传输（控制） |
| FTP数据 | 20 | TCP | 文件传输（数据） |
| SSH | 22 | TCP | 安全Shell |
| Telnet | 23 | TCP | 远程终端（不安全） |
| DNS | 53 | UDP/TCP | 域名解析 |
| SMTP | 25 | TCP | 邮件发送 |
| POP3 | 110 | TCP | 邮件接收 |
| SMB | 445 | TCP | 文件共享 |
| NetBIOS | 137-139 | UDP/TCP | 网络基本输入输出 |
| WinRM | 5985/5986 | TCP | 远程管理（HTTP/HTTPS） |
| SQL Server | 1433 | TCP | SQL Server默认端口 |
| MySQL | 3306 | TCP | MySQL默认端口 |

#### 3.6.2 常用服务放行配置

```powershell
# 放行Web服务（80/443）
New-NetFirewallRule -DisplayName "HTTP入站" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow
New-NetFirewallRule -DisplayName "HTTPS入站" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow

# 放行FTP服务
New-NetFirewallRule -DisplayName "FTP控制端口" -Direction Inbound -Protocol TCP -LocalPort 21 -Action Allow
New-NetFirewallRule -DisplayName "FTP被动模式端口" -Direction Inbound -Protocol TCP -LocalPort 50000-51000 -Action Allow

# 放行SMB文件共享（谨慎开启）
# 注意：SMB 445端口是攻击热点，不建议暴露到公网
New-NetFirewallRule -DisplayName "SMB入站（仅内网）" -Direction Inbound -Protocol TCP -LocalPort 445 -RemoteAddress 192.168.1.0/24 -Action Allow

# 放行SQL Server（仅内网）
New-NetFirewallRule -DisplayName "SQL Server入站" -Direction Inbound -Protocol TCP -LocalPort 1433 -RemoteAddress 192.168.1.0/24 -Action Allow

# 启用预定义规则组
Enable-NetFirewallRule -DisplayGroup "远程桌面"
Enable-NetFirewallRule -DisplayGroup "文件和打印机共享"
Enable-NetFirewallRule -DisplayGroup "Windows远程管理"
```

#### 3.6.3 安全最佳实践

- **最小化开放端口**：仅开放必要的服务端口
- **限制来源IP**：管理类端口（RDP、WinRM）应限制来源IP范围
- **避免使用默认端口**：敏感服务可考虑修改默认端口（安全通过隐蔽性）
- **定期审计规则**：清理不必要的防火墙规则
- **启用出站规则**：配置出站规则阻止可疑程序联网
- **备份防火墙配置**：定期导出防火墙规则

---

---

## 🛠️ 补充：实战拓展

### 命令速查表

```powershell
# 防火墙快速诊断
function Get-FirewallStatus {
    Write-Host "=== 防火墙状态 ===" -ForegroundColor Cyan
    Get-NetFirewallProfile | Select-Object Name, Enabled, DefaultInboundAction, DefaultOutboundAction | Format-Table -AutoSize

    Write-Host "=== 入站规则统计 ===" -ForegroundColor Cyan
    $inbound = Get-NetFirewallRule -Direction Inbound -Enabled True
    Write-Host "启用的入站规则数: $($inbound.Count)"

    Write-Host "=== 出站规则统计 ===" -ForegroundColor Cyan
    $outbound = Get-NetFirewallRule -Direction Outbound -Enabled True
    Write-Host "启用的出站规则数: $($outbound.Count)"

    Write-Host "=== 开放的本地端口 ===" -ForegroundColor Cyan
    Get-NetFirewallRule -Direction Inbound -Enabled True | Get-NetFirewallPortFilter | Where-Object { $_.LocalPort -ne "Any" } | Select-Object @{n="规则";e={(Get-NetFirewallRule -AssociatedNetFirewallPortFilter $_).DisplayName}}, Protocol, LocalPort | Format-Table -AutoSize
}
```

### 防火墙配置备份与恢复

```powershell
# 导出防火墙配置
netsh advfirewall export "C:\backup\firewall_backup.wfw"

# 导入防火墙配置
netsh advfirewall import "C:\backup\firewall_backup.wfw"

# 重置防火墙到默认状态
netsh advfirewall reset
```

### 常用PowerShell防火墙脚本

```powershell
# 批量阻止可疑IP
$blockedIPs = @("1.2.3.4", "5.6.7.8", "9.10.11.12")
foreach ($ip in $blockedIPs) {
    New-NetFirewallRule -DisplayName "阻止IP_$ip" -Direction Inbound -RemoteAddress $ip -Action Block
    Write-Host "已阻止IP: $ip"
}

# 清理自定义规则（按名称前缀）
Get-NetFirewallRule | Where-Object { $_.DisplayName -like "阻止IP_*" } | Remove-NetFirewallRule
```

---

## 📋 内容审核与补充建议

> 针对「Windows防火墙与高级安全」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

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
