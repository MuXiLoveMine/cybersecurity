# Windows网络配置

### 2.1 网卡配置

#### 2.1.1 网络配置基础要素

Windows网络配置的核心要素包括：
- **IP地址**：主机在网络中的唯一标识
- **子网掩码**：用于区分网络位和主机位
- **默认网关**：本地网络的出口路由器地址
- **DNS服务器**：域名解析服务地址
- **DHCP**：动态主机配置协议，自动分配IP地址

#### 2.1.2 图形界面配置

通过"网络和共享中心"或"设置 → 网络和Internet"进行配置：
1. 打开控制面板 → 网络和共享中心 → 更改适配器设置
2. 右键点击网卡 → 属性 → Internet协议版本4（TCP/IPv4）→ 属性
3. 选择"自动获取IP地址"或"使用下面的IP地址"
4. 配置IP地址、子网掩码、默认网关和DNS服务器

#### 2.1.3 命令行配置

```cmd
:: 查看网络配置
ipconfig
ipconfig /all          :: 详细信息
ipconfig /release      :: 释放IP（DHCP）
ipconfig /renew        :: 续订IP（DHCP）
ipconfig /flushdns     :: 清除DNS缓存
ipconfig /displaydns   :: 显示DNS缓存
```

```powershell
# PowerShell网络配置
# 查看网络适配器
Get-NetAdapter
Get-NetAdapter -Name "以太网" | Format-List *

# 查看IP地址配置
Get-NetIPAddress
Get-NetIPAddress -InterfaceAlias "以太网" -AddressFamily IPv4

# 配置静态IP地址
New-NetIPAddress -InterfaceAlias "以太网" -IPAddress 192.168.1.100 -PrefixLength 24 -DefaultGateway 192.168.1.1

# 配置DNS服务器
Set-DnsClientServerAddress -InterfaceAlias "以太网" -ServerAddresses 8.8.8.8, 114.114.114.114

# 启用DHCP
Set-NetIPInterface -InterfaceAlias "以太网" -Dhcp Enabled
Set-DnsClientServerAddress -InterfaceAlias "以太网" -ResetServerAddresses
```

### 2.2 netsh命令与PowerShell网络命令

#### 2.2.1 netsh命令

netsh（Network Shell）是Windows强大的网络配置命令行工具：

```cmd
:: 接口配置
netsh interface show interface          :: 显示所有网络接口
netsh interface ip show config          :: 显示IP配置
netsh interface ip show addresses       :: 显示IP地址

:: 设置静态IP
netsh interface ip set address "以太网" static 192.168.1.100 255.255.255.0 192.168.1.1

:: 设置DNS
netsh interface ip set dns "以太网" static 8.8.8.8 primary
netsh interface ip add dns "以太网" 114.114.114.114 index=2

:: 启用DHCP
netsh interface ip set address "以太网" dhcp
netsh interface ip set dns "以太网" dhcp
```

#### 2.2.2 netsh高级命令

```cmd
:: 防火墙配置（详见防火墙章节）
netsh advfirewall show allprofiles

:: WLAN配置
netsh wlan show profiles                :: 显示保存的WiFi配置
netsh wlan show interfaces              :: 显示无线网卡信息
netsh wlan export profile folder="C:\wifi" key=clear  :: 导出WiFi配置（含密码）

:: 网络诊断
netsh diag connect iphost 192.168.1.1

:: TCP/IP重置（修复网络问题）
netsh int ip reset
netsh winsock reset
```

#### 2.2.3 PowerShell网络命令

```powershell
# 网络接口管理
Get-NetAdapter                          # 获取所有网络适配器
Enable-NetAdapter -Name "以太网"        # 启用网卡
Disable-NetAdapter -Name "以太网"       # 禁用网卡
Rename-NetAdapter -Name "以太网" -NewName "LAN"  # 重命名网卡

# IP地址管理
Get-NetIPAddress                        # 获取所有IP地址
New-NetIPAddress                        # 添加IP地址
Remove-NetIPAddress                     # 删除IP地址
Set-NetIPAddress                        # 修改IP地址

# 路由管理
Get-NetRoute                            # 获取路由表
New-NetRoute                            # 添加路由
Remove-NetRoute                         # 删除路由

# DNS管理
Get-DnsClient                           # 获取DNS客户端配置
Get-DnsClientServerAddress              # 获取DNS服务器地址
Set-DnsClientServerAddress              # 设置DNS服务器
Clear-DnsClientCache                    # 清除DNS缓存
```

### 2.3 网络适配器管理

#### 2.3.1 启用/禁用适配器

```cmd
:: netsh方式
netsh interface set interface "以太网" enabled
netsh interface set interface "以太网" disabled

:: wmic方式
wmic path win32_networkadapter where "NetConnectionID='以太网'" call enable
wmic path win32_networkadapter where "NetConnectionID='以太网'" call disable
```

```powershell
# PowerShell方式
Enable-NetAdapter -Name "以太网"
Disable-NetAdapter -Name "以太网" -Confirm:$false

# 重启网卡
Restart-NetAdapter -Name "以太网"
```

#### 2.3.2 高级设置

**网卡高级属性**（设备管理器 → 网卡属性 → 高级）：
- **速度和双工**：可设置自动协商或强制10/100/1000Mbps全双工/半双工
- **巨型帧（Jumbo Frame）**：大于1500字节的帧，可提升大文件传输性能
- **唤醒功能**：支持网络唤醒（Wake-on-LAN）
- **TCP/UDP校验和卸载**：将校验和计算交给网卡处理，减轻CPU负担
- **接收端缩放（RSS）**：多CPU核心处理网络流量

```powershell
# 查看网卡高级属性
Get-NetAdapterAdvancedProperty -Name "以太网"

# 设置网卡速率和双工
Set-NetAdapterAdvancedProperty -Name "以太网" -DisplayName "速度和双工" -DisplayValue "1.0 Gbps 全双工"

# 启用巨型帧
Set-NetAdapterAdvancedProperty -Name "以太网" -DisplayName "巨型数据包" -DisplayValue "9014 Bytes"
```

#### 2.3.3 网络绑定顺序

网络绑定顺序决定了多网卡环境下的网络优先级：
- 控制面板 → 网络和共享中心 → 更改适配器设置
- 按Alt键 → 高级 → 高级设置
- 在"适配器和绑定"选项卡中调整顺序

```powershell
# 查看接口跃点数
Get-NetIPInterface -AddressFamily IPv4 | Sort-Object InterfaceMetric

# 设置接口跃点数（越小优先级越高）
Set-NetIPInterface -InterfaceAlias "以太网" -InterfaceMetric 10
```

### 2.4 Hosts文件配置

#### 2.4.1 Hosts文件位置与作用

Hosts文件用于本地域名解析，优先级高于DNS查询：
- **文件位置**：`C:\Windows\System32\drivers\etc\hosts`
- **格式**：`IP地址 域名`
- 一行一条记录，#开头为注释
- 修改需要管理员权限

#### 2.4.2 常用操作

```cmd
:: 查看hosts文件
type C:\Windows\System32\drivers\etc\hosts

:: 以管理员身份用记事本编辑
notepad C:\Windows\System32\drivers\etc\hosts
```

```powershell
# 查看hosts文件
Get-Content C:\Windows\System32\drivers\etc\hosts

# 添加hosts记录（需管理员权限）
Add-Content -Path C:\Windows\System32\drivers\etc\hosts -Value "192.168.1.100 server01.test.com"

# 备份hosts文件
Copy-Item C:\Windows\System32\drivers\etc\hosts C:\Windows\System32\drivers\etc\hosts.bak
```

#### 2.4.3 安全注意事项

- Hosts文件常被恶意软件篡改，用于钓鱼或屏蔽安全网站
- 定期检查hosts文件是否有异常条目
- 默认hosts文件仅包含 `127.0.0.1 localhost` 和 `::1 localhost`
- 可通过设置hosts文件为只读来防止篡改

### 2.5 路由表管理

#### 2.5.1 route命令

```cmd
:: 查看路由表
route print
route print -4           :: 仅IPv4路由
route print -6           :: 仅IPv6路由
route print 10.*         :: 筛选特定网段

:: 添加路由
route add 10.0.0.0 mask 255.0.0.0 192.168.1.1
route add 172.16.0.0/12 192.168.1.1 metric 2

:: 添加永久路由（重启后保留）
route -p add 10.0.0.0 mask 255.0.0.0 192.168.1.1

:: 删除路由
route delete 10.0.0.0
route delete 10.0.0.0 mask 255.0.0.0

:: 修改路由
route change 10.0.0.0 mask 255.0.0.0 192.168.1.2
```

#### 2.5.2 PowerShell路由管理

```powershell
# 查看路由表
Get-NetRoute -AddressFamily IPv4
Get-NetRoute -DestinationPrefix "0.0.0.0/0"  # 默认路由

# 添加路由
New-NetRoute -DestinationPrefix "10.0.0.0/8" -NextHop 192.168.1.1 -InterfaceAlias "以太网"

# 删除路由
Remove-NetRoute -DestinationPrefix "10.0.0.0/8" -Confirm:$false

# 修改路由
Set-NetRoute -DestinationPrefix "10.0.0.0/8" -NextHop 192.168.1.2
```

### 2.6 网络故障排查

#### 2.6.1 连通性测试

```cmd
:: ping测试
ping 192.168.1.1
ping -t 192.168.1.1         :: 持续ping
ping -n 10 192.168.1.1      :: 指定次数
ping -l 1500 192.168.1.1    :: 指定数据包大小
ping -a 192.168.1.1         :: 解析主机名

:: 测试TCP端口连通性
telnet 192.168.1.1 3389
```

```powershell
# PowerShell连通性测试
Test-Connection -ComputerName 192.168.1.1 -Count 4
Test-NetConnection -ComputerName 192.168.1.1 -Port 3389
Test-NetConnection -ComputerName www.baidu.com -CommonTCPPort HTTP
Test-NetConnection -InformationLevel Detailed
```

#### 2.6.2 路径追踪

```cmd
:: tracert追踪路由
tracert 8.8.8.8
tracert -d 8.8.8.8          :: 不解析主机名，速度更快
tracert -h 30 8.8.8.8       :: 设置最大跳数

:: pathping（结合ping和tracert）
pathping 8.8.8.8
pathping -n 8.8.8.8         :: 不解析主机名
```

#### 2.6.3 DNS排查

```cmd
:: nslookup域名解析
nslookup www.baidu.com
nslookup www.baidu.com 8.8.8.8    :: 指定DNS服务器
nslookup -type=mx baidu.com       :: 查询MX记录
nslookup -type=ns baidu.com       :: 查询NS记录
nslookup -debug www.baidu.com     :: 调试模式
```

```powershell
# PowerShell DNS查询
Resolve-DnsName www.baidu.com
Resolve-DnsName -Name baidu.com -Type MX
Resolve-DnsName -Name baidu.com -Server 8.8.8.8
```

#### 2.6.4 网络状态查看

```cmd
:: 查看网络连接
netstat -ano                  :: 所有连接和监听端口+PID
netstat -ano | findstr "LISTENING"  :: 仅监听端口
netstat -ano | findstr ":3389"      :: 特定端口
netstat -rn                   :: 路由表
netstat -e                    :: 网卡统计
netstat -b                    :: 涉及的可执行文件（需管理员）
```

```powershell
# PowerShell网络连接查看
Get-NetTCPConnection
Get-NetTCPConnection -State Listen
Get-NetTCPConnection -LocalPort 3389
Get-NetUDPEndpoint
```

---

---

## 🛠️ 补充：实战拓展

### 命令速查表

```powershell
# 快速网络诊断脚本
function Test-NetworkHealth {
    Write-Host "=== 网络适配器状态 ===" -ForegroundColor Cyan
    Get-NetAdapter | Select-Object Name, Status, LinkSpeed | Format-Table -AutoSize

    Write-Host "=== IP地址配置 ===" -ForegroundColor Cyan
    Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notlike "*Loopback*" } | Select-Object InterfaceAlias, IPAddress, PrefixLength | Format-Table -AutoSize

    Write-Host "=== 默认网关 ===" -ForegroundColor Cyan
    Get-NetRoute -DestinationPrefix "0.0.0.0/0" | Select-Object InterfaceAlias, NextHop | Format-Table -AutoSize

    Write-Host "=== DNS服务器 ===" -ForegroundColor Cyan
    Get-DnsClientServerAddress -AddressFamily IPv4 | Select-Object InterfaceAlias, ServerAddresses | Format-Table -AutoSize

    Write-Host "=== 外网连通性测试 ===" -ForegroundColor Cyan
    Test-Connection -ComputerName 8.8.8.8 -Count 2 -ErrorAction SilentlyContinue | Select-Object Address, ResponseTime

    Write-Host "=== DNS解析测试 ===" -ForegroundColor Cyan
    try { Resolve-DnsName www.baidu.com -ErrorAction Stop | Select-Object Name, IPAddress -First 1 } catch { Write-Host "DNS解析失败" -ForegroundColor Red }
}
```

### 常见网络故障排查流程

```
1. 检查物理连接 → 网线、网卡指示灯
2. 检查网卡状态 → ipconfig / Get-NetAdapter
3. 检查IP配置 → 是否获取正确IP、网关、DNS
4. 测试本地连通性 → ping 网关
5. 测试外网连通性 → ping 8.8.8.8
6. 测试DNS解析 → nslookup / Resolve-DnsName
7. 测试端口连通性 → telnet / Test-NetConnection
8. 追踪路径 → tracert / pathping
9. 检查防火墙 → 临时关闭测试
10. 重置网络栈 → netsh int ip reset; netsh winsock reset
```

---

## 📋 内容审核与补充建议

> 针对「Windows网络配置」部分的内容审核结果：

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

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
