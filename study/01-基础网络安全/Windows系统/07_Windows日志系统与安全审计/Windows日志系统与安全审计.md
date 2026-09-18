# Windows日志系统与安全审计

### 6.1 Windows日志体系

#### 6.1.1 Windows事件日志概述

Windows事件日志系统是操作系统的核心审计组件，从Windows Vista/Server 2008开始采用基于XML的事件日志格式（.evtx）：
- 日志文件存储位置：`%SystemRoot%\System32\winevt\Logs\`
- 日志格式：EVTX（二进制XML格式）
- 服务名称：Windows Event Log（eventlog服务）

#### 6.1.2 标准日志分类

| 日志名称 | 文件名 | 说明 |
|----------|--------|------|
| 应用程序（Application） | Application.evtx | 应用程序相关事件 |
| 安全（Security） | Security.evtx | 安全审计事件，需配置审核策略 |
| 系统（System） | System.evtx | 系统组件事件 |
| Setup | Setup.evtx | 安装和配置相关事件 |
| Forwarded Events | ForwardedEvents.evtx | 从其他计算机转发的事件 |

#### 6.1.3 应用程序和服务日志

除标准日志外，Windows还有大量应用程序和服务日志：
- **Windows PowerShell**：PowerShell相关事件
- **Microsoft-Windows-PowerShell/Operational**：PowerShell操作日志（含脚本块日志）
- **Microsoft-Windows-Sysmon/Operational**：Sysmon日志（需安装）
- **Microsoft-Windows-WinRM/Operational**：WinRM相关日志
- **Microsoft-Windows-TerminalServices-LocalSessionManager/Operational**：RDP会话日志
- **Microsoft-Windows-TerminalServices-RemoteConnectionManager/Operational**：RDP连接日志
- **Microsoft-Windows-Security-Auditing**：与Security日志重叠
- **WMI-Activity**：WMI活动日志

```powershell
# 查看所有日志类别
Get-WinEvent -ListLog * | Select-Object LogName, RecordCount, IsEnabled | Format-Table -AutoSize

# 按记录数排序
Get-WinEvent -ListLog * | Sort-Object RecordCount -Descending | Select-Object -First 20 LogName, RecordCount, IsEnabled
```

#### 6.1.4 事件级别

| 级别 | 关键字 | 说明 |
|------|--------|------|
| 1 | 关键（Critical） | 灾难性故障，可能导致系统或应用程序完全失败 |
| 2 | 错误（Error） | 重大问题，影响功能 |
| 3 | 警告（Warning） | 可能指示未来问题的事件 |
| 4 | 信息（Information） | 描述成功操作的事件 |
| 5 | 详细（Verbose） | 更详细的信息事件 |

### 6.2 事件查看器使用

#### 6.2.1 打开事件查看器

```
运行 → eventvwr.msc
或
运行 → eventvwr
或
计算机管理 → 系统工具 → 事件查看器
```

#### 6.2.2 事件查看器界面

- **自定义视图**：预定义和自定义的筛选视图
  - 管理事件：汇总所有级别为错误/警告的关键事件
  - 按角色分类的事件视图
- **Windows日志**：标准的五个日志类别
- **应用程序和服务日志**：应用程序和组件的详细日志
- **订阅**：从其他计算机收集的转发事件

#### 6.2.3 事件属性

每个事件包含以下关键字段：
- **事件ID**：事件类型的唯一标识符
- **级别**：严重级别（信息/警告/错误/关键）
- **来源**：产生事件的组件
- **日志**：所属的日志类别
- **任务类别**：更细粒度的事件分类
- **关键字**：事件分类标签
- **用户**：产生事件的用户账户
- **计算机**：产生事件的计算机名
- **日期和时间**：事件发生时间
- **事件数据**：事件的详细信息（XML格式）

#### 6.2.4 常用操作

**筛选当前日志**：
- 按事件级别筛选（关键、错误、警告）
- 按事件来源筛选
- 按事件ID筛选
- 按时间范围筛选
- 按用户/计算机筛选

**自定义视图**：
- 可跨多个日志创建统一视图
- 可通过XML高级筛选定义复杂条件
- 可导入/导出自定义视图

### 6.3 安全审计策略配置

#### 6.3.1 审计策略概述

安全审计策略决定了哪些安全事件会被记录到安全日志中：
- 默认情况下，Windows启用了部分审计策略
- 完整的审计策略覆盖登录、对象访问、特权使用等多个方面
- 审计策略可以通过本地策略或组策略配置

#### 6.3.2 配置路径

```
本地组策略编辑器 → 计算机配置 → Windows设置 → 安全设置 → 本地策略 → 审核策略
```

#### 6.3.3 高级审计策略配置

Windows Vista/Server 2008引入了更细粒度的高级审计策略：

```
本地组策略编辑器 → 计算机配置 → Windows设置 → 安全设置 → 高级审核策略配置 → 系统审核策略
```

**十大审计类别**：

| 类别 | 说明 | 推荐配置 |
|------|------|----------|
| 账户登录审计 | 域控制器上的账户身份验证 | 成功+失败 |
| 账户管理审计 | 用户账户和组的创建、修改、删除 | 成功+失败 |
| 详细跟踪审计 | 进程创建/终止、RPC事件 | 成功（进程创建） |
| DS访问审计 | 活动目录对象访问 | 成功+失败（域控） |
| 登录/注销审计 | 交互式登录、网络登录等 | 成功+失败 |
| 对象访问审计 | 文件、注册表等对象访问 | 按需配置 |
| 策略更改审计 | 审计策略、用户权限等更改 | 成功+失败 |
| 特权使用审计 | 用户权限的使用 | 失败 |
| 系统审计 | 系统启动/关机、安全日志相关 | 成功+失败 |
| 全局对象访问审计 | 全局文件系统和注册表审计 | 按需配置 |

#### 6.3.4 审计策略配置命令

```cmd
:: 查看当前审计策略
auditpol /get /category:*
auditpol /get /category:"登录/注销"

:: 配置审计策略
auditpol /set /category:"登录/注销" /success:enable /failure:enable
auditpol /set /subcategory:"登录" /success:enable /failure:enable
auditpol /set /subcategory:"进程创建" /success:enable

:: 备份/恢复审计策略
auditpol /backup /file:C:\audit_backup.csv
auditpol /restore /file:C:\audit_backup.csv
```

```powershell
# 使用PowerShell查看审计策略
auditpol /get /category:* | Out-String

# 获取子类别列表
auditpol /list /subcategory:*
```

### 6.4 常见安全事件ID说明

#### 6.4.1 登录/注销相关

| 事件ID | 说明 |
|--------|------|
| 4624 | 账户成功登录 |
| 4625 | 账户登录失败 |
| 4626 | 用户/设备声明信息（登录成功后） |
| 4634 | 账户已注销 |
| 4647 | 用户发起注销 |
| 4648 | 使用显式凭据尝试登录（runas等） |
| 4672 | 管理员登录（使用特殊权限登录） |
| 4778 | 会话重新连接（RDP重连） |
| 4779 | 会话断开连接（RDP断开） |
| 4800 | 工作站被锁定 |
| 4801 | 工作站被解锁 |
| 4802 | 屏幕保护程序启动 |
| 4803 | 屏幕保护程序被解除 |

**登录类型（Logon Type）说明**：
- Type 2：交互式登录（本地控制台）
- Type 3：网络登录（共享文件夹、IIS等）
- Type 4：批处理登录（计划任务）
- Type 5：服务登录（服务启动）
- Type 7：解锁（屏幕解锁）
- Type 8：网络明文登录（IIS基本认证）
- Type 9：新凭据登录（runas /netonly）
- Type 10：远程交互式登录（RDP）
- Type 11：缓存交互式登录（使用缓存凭据）

#### 6.4.2 账户管理相关

| 事件ID | 说明 |
|--------|------|
| 4720 | 创建用户账户 |
| 4722 | 启用用户账户 |
| 4723 | 尝试更改账户密码 |
| 4724 | 尝试重置账户密码 |
| 4725 | 禁用用户账户 |
| 4726 | 删除用户账户 |
| 4727 | 创建启用安全的全局组 |
| 4728 | 成员添加到启用安全的全局组 |
| 4732 | 成员添加到启用安全的本地组 |
| 4735 | 启用安全的本地组属性更改 |
| 4740 | 用户账户被锁定 |
| 4756 | 成员添加到启用安全的通用组 |

#### 6.4.3 对象访问相关

| 事件ID | 说明 |
|--------|------|
| 4656 | 请求对象的句柄（文件/注册表访问开始） |
| 4658 | 对象的句柄已关闭（文件/注册表访问结束） |
| 4660 | 删除对象 |
| 4663 | 尝试访问对象（具体的访问操作） |
| 4670 | 对象的权限已更改 |

#### 6.4.4 进程相关

| 事件ID | 说明 |
|--------|------|
| 4688 | 进程已创建（关键事件，追踪程序执行） |
| 4689 | 进程已退出 |
| 4696 | 主令牌已分配给进程 |
| 5140 | 网络共享对象被访问 |

#### 6.4.5 策略与系统相关

| 事件ID | 说明 |
|--------|------|
| 4697 | 服务已安装到系统中 |
| 4704 | 用户权限已分配 |
| 4719 | 系统审核策略已更改 |
| 4720 | 创建用户账户 |
| 4732 | 成员添加到本地组 |
| 4946 | 已对Windows防火墙例外列表进行更改 |
| 4947 | 已对Windows防火墙例外列表进行更改（规则） |
| 1102 | 审计日志已被清除 |

### 6.5 wevtutil命令与PowerShell日志查询

#### 6.5.1 wevtutil命令

```cmd
:: 查看日志列表
wevtutil el                    :: 枚举日志名称
wevtutil gl Security           :: 查看日志配置

:: 查询日志
wevtutil qe Security /c:10 /f:text          :: 查询最近10条安全日志
wevtutil qe Security /q:"*[System[(EventID=4625)]]" /c:5  :: 按事件ID筛选
wevtutil qe Security /q:"*[System[(Level=2)]]" /c:10      :: 按级别筛选
wevtutil qe Security /r:DC01                 :: 查询远程计算机

:: 导出日志
wevtutil epl Security C:\backup\security.evtx
wevtutil epl Security C:\backup\security.evtx /q:"*[System[(EventID=4624 or EventID=4625)]]"

:: 清除日志
wevtutil cl Security
wevtutil cl Security /bu:C:\backup\security_backup.evtx  :: 清除前备份
```

#### 6.5.2 PowerShell日志查询

```powershell
# 获取安全日志中的登录失败事件
Get-WinEvent -LogName Security -FilterXPath "*[System[EventID=4625]]" -MaxEvents 10

# 获取指定时间段的事件
$startTime = (Get-Date).AddDays(-1)
$endTime = Get-Date
Get-WinEvent -LogName Security -FilterHashtable @{
    LogName = 'Security'
    Id = 4624, 4625
    StartTime = $startTime
    EndTime = $endTime
}

# 获取指定事件并查看详细信息
$events = Get-WinEvent -LogName Security -FilterHashtable @{Id=4625} -MaxEvents 5
$events | ForEach-Object {
    Write-Host "时间: $($_.TimeCreated)"
    Write-Host "来源: $($_.ProviderName)"
    Write-Host "事件ID: $($_.Id)"
    Write-Host "消息:"
    Write-Host $_.Message
    Write-Host "---"
}

# 解析事件XML数据
$event = Get-WinEvent -LogName Security -FilterHashtable @{Id=4624} -MaxEvents 1
$xml = [xml]$event.ToXml()
$xml.Event.EventData.Data | ForEach-Object {
    [PSCustomObject]@{
        名称 = $_.Name
        值 = $_.'#text'
    }
} | Format-Table -AutoSize
```

#### 6.5.3 常用日志查询示例

```powershell
# 1. 最近的登录失败事件
function Get-LoginFailures {
    param([int]$Days = 1, [int]$MaxEvents = 50)
    $start = (Get-Date).AddDays(-$Days)
    Get-WinEvent -FilterHashtable @{
        LogName = 'Security'
        Id = 4625
        StartTime = $start
    } -MaxEvents $MaxEvents | ForEach-Object {
        $xml = [xml]$_.ToXml()
        $targetUser = ($xml.Event.EventData.Data | Where-Object { $_.Name -eq 'TargetUserName' }).'#text'
        $ipAddress = ($xml.Event.EventData.Data | Where-Object { $_.Name -eq 'IpAddress' }).'#text'
        $logonType = ($xml.Event.EventData.Data | Where-Object { $_.Name -eq 'LogonType' }).'#text'
        [PSCustomObject]@{
            时间 = $_.TimeCreated
            目标用户 = $targetUser
            来源IP = $ipAddress
            登录类型 = $logonType
        }
    }
}

# 2. 最近创建的进程（需启用进程创建审计）
function Get-NewProcesses {
    param([int]$Days = 1, [int]$MaxEvents = 100)
    $start = (Get-Date).AddDays(-$Days)
    Get-WinEvent -FilterHashtable @{
        LogName = 'Security'
        Id = 4688
        StartTime = $start
    } -MaxEvents $MaxEvents -ErrorAction SilentlyContinue | ForEach-Object {
        $xml = [xml]$_.ToXml()
        $processName = ($xml.Event.EventData.Data | Where-Object { $_.Name -eq 'NewProcessName' }).'#text'
        $commandLine = ($xml.Event.EventData.Data | Where-Object { $_.Name -eq 'CommandLine' }).'#text'
        $user = ($xml.Event.EventData.Data | Where-Object { $_.Name -eq 'SubjectUserName' }).'#text'
        [PSCustomObject]@{
            时间 = $_.TimeCreated
            进程名 = $processName
            命令行 = $commandLine
            用户 = $user
        }
    }
}

# 3. 账户锁定事件
function Get-LockedOutAccounts {
    param([int]$Days = 7)
    $start = (Get-Date).AddDays(-$Days)
    Get-WinEvent -FilterHashtable @{
        LogName = 'Security'
        Id = 4740
        StartTime = $start
    } -ErrorAction SilentlyContinue | ForEach-Object {
        $xml = [xml]$_.ToXml()
        $targetUser = ($xml.Event.EventData.Data | Where-Object { $_.Name -eq 'TargetUserName' }).'#text'
        [PSCustomObject]@{
            时间 = $_.TimeCreated
            被锁定账户 = $targetUser
        }
    }
}
```

### 6.6 日志收集与转发

#### 6.6.1 日志转发架构

**Windows事件收集（WEC）**：
- 基于WS-Management协议的事件转发机制
- 支持集中式日志收集
- 分为收集器（Collector）和源计算机（Source）

**架构模式**：
- **源初始化（Push订阅）**：源计算机主动向收集器发送事件
- **收集器初始化（Pull订阅）**：收集器主动从源计算机拉取事件

#### 6.6.2 配置事件转发

**收集器配置**：
```cmd
:: 启用事件收集服务
wecutil qc
```

**源计算机配置**：
```cmd
:: 配置WinRM
winrm quickconfig

:: 将收集器计算机账户添加到Event Log Readers组
net localgroup "Event Log Readers" /add "DOMAIN\CollectorMachine$"
```

**创建订阅**：
```
事件查看器 → 订阅 → 创建订阅
```

```cmd
:: 命令行创建订阅
wecutil cs SubscriptionName
```

#### 6.6.3 SIEM对接

安全信息和事件管理（SIEM）系统是企业安全运营的核心：

**常见SIEM产品**：
- Microsoft Sentinel（云原生SIEM）
- Splunk Enterprise Security
- IBM QRadar
- ArcSight
- Elastic Stack（ELK）

**对接方式**：
- **Syslog转发**：通过NXLog、rsyslog等工具转发
- **WMI/WEC**：Windows原生事件收集
- **Agent代理**：SIEM厂商提供的日志收集代理
- **API接口**：云SIEM通过API接入

#### 6.6.4 日志保留策略

日志保留的安全最佳实践：
- **安全日志大小**：建议至少4GB，避免日志被覆盖
- **日志保留时间**：
  - 在线热数据：30-90天
  - 归档数据：6个月-1年
  - 合规要求：根据行业规范（如等保2.0要求6个月）
- **日志保护**：
  - 限制对日志文件的访问权限
  - 将日志转发到集中存储
  - 定期备份日志
  - 监控日志清除事件（事件ID 1102）

---

---

## 🛠️ 补充：实战拓展

### 命令速查表

```powershell
# 安全日志快速审计脚本
function Invoke-SecurityLogAudit {
    Write-Host "=== 最近24小时登录失败统计 ===" -ForegroundColor Cyan
    $failures = Get-LoginFailures -Days 1 -MaxEvents 1000
    if ($failures) {
        $failures | Group-Object 来源IP | Sort-Object Count -Descending | Select-Object -First 10 Count, Name | Format-Table -AutoSize
    } else { Write-Host "无登录失败事件" }

    Write-Host "=== 最近24小时RDP登录 ===" -ForegroundColor Cyan
    $rdpLogins = Get-WinEvent -FilterHashtable @{
        LogName = 'Security'; Id = 4624; StartTime = (Get-Date).AddDays(-1)
    } -ErrorAction SilentlyContinue | Where-Object { $_.Message -match '登录类型:\s+10' }
    Write-Host "RDP登录次数: $($rdpLogins.Count)"

    Write-Host "=== 最近的账户锁定 ===" -ForegroundColor Cyan
    $lockouts = Get-LockedOutAccounts -Days 7
    if ($lockouts) { $lockouts | Format-Table -AutoSize }
    else { Write-Host "近7天无账户锁定" }

    Write-Host "=== 最近安装的服务 ===" -ForegroundColor Cyan
    $services = Get-WinEvent -FilterHashtable @{
        LogName = 'Security'; Id = 4697; StartTime = (Get-Date).AddDays(-7)
    } -ErrorAction SilentlyContinue
    Write-Host "近7天新增服务数: $($services.Count)"
}
```

### 日志分析实用脚本

```powershell
# 暴力破解检测脚本
function Find-BruteForceAttacks {
    param([int]$Threshold = 5, [int]$Minutes = 10)
    
    $startTime = (Get-Date).AddHours(-24)
    $failures = Get-WinEvent -FilterHashtable @{
        LogName = 'Security'
        Id = 4625
        StartTime = $startTime
    } -ErrorAction SilentlyContinue

    if (-not $failures) {
        Write-Host "未找到登录失败事件"
        return
    }

    $ipFailures = @{}
    foreach ($event in $failures) {
        $xml = [xml]$event.ToXml()
        $ip = ($xml.Event.EventData.Data | Where-Object { $_.Name -eq 'IpAddress' }).'#text'
        if ($ip -and $ip -ne '-') {
            if (-not $ipFailures.ContainsKey($ip)) {
                $ipFailures[$ip] = @()
            }
            $ipFailures[$ip] += $event.TimeCreated
        }
    }

    Write-Host "暴力破解嫌疑IP（$Threshold 分钟内失败 $Threshold 次以上）：" -ForegroundColor Red
    foreach ($ip in $ipFailures.Keys) {
        $times = $ipFailures[$ip] | Sort-Object
        for ($i = 0; $i -lt $times.Count; $i++) {
            $windowStart = $times[$i]
            $windowEnd = $windowStart.AddMinutes($Minutes)
            $count = ($times | Where-Object { $_ -ge $windowStart -and $_ -le $windowEnd }).Count
            if ($count -ge $Threshold) {
                Write-Host "IP: $ip, 失败次数: $count, 起始时间: $windowStart"
                break
            }
        }
    }
}
```

---

## 📋 内容审核与补充建议

> 针对「Windows日志系统与安全审计」部分的内容审核结果：

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
