# basics.ps1 —— PowerShell 基础语法示例（安全从业者视角）
#
# 涵盖内容：
#   1. 变量与数据类型
#   2. 数组
#   3. 哈希表
#   4. 管道操作
#   5. 条件判断（if / switch）
#   6. 循环（foreach / while / for）
#   7. 函数
#   8. 文件操作
#   9. 错误处理
#  10. 对象操作（Select / Where / Sort）
#
# 运行方式：
#   powershell -ExecutionPolicy Bypass -File basics.ps1
#
# 注意：本脚本用于学习参考，可以直接运行查看输出。

# ============================================================
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  PowerShell 基础语法示例（安全从业者视角）" -ForegroundColor Cyan
Write-Host "  PowerShell Basics for Security Practitioners" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# ============================================================
# 1. 变量与数据类型
# ============================================================
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host "【1. 变量与数据类型】" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host ""

# 1.1 基本变量
Write-Host "1.1 基本变量" -ForegroundColor Green
$name = "Alice"
$age = 25
$ipAddress = "192.168.1.100"
$isAdmin = $true

Write-Host "  姓名: $name"
Write-Host "  年龄: $age"
Write-Host "  IP: $ipAddress"
Write-Host "  是否管理员: $isAdmin"
Write-Host ""

# 1.2 变量类型
Write-Host "1.2 变量类型" -ForegroundColor Green
Write-Host "  `$name 类型: $($name.GetType().FullName)"
Write-Host "  `$age 类型: $($age.GetType().FullName)"
Write-Host "  `$isAdmin 类型: $($isAdmin.GetType().FullName)"
Write-Host ""

# 1.3 字符串操作
Write-Host "1.3 字符串操作" -ForegroundColor Green
$logEntry = "2026-01-15 10:30:00 INFO User alice logged in from 192.168.1.100"
Write-Host "  原始日志: $logEntry"
Write-Host "  转大写: $($logEntry.ToUpper())"
Write-Host "  是否包含 'ERROR': $($logEntry.Contains('ERROR'))"
Write-Host "  按空格分割（前5个）: $($logEntry.Split(' ')[0..4] -join '|')"
Write-Host "  替换 alice -> bob: $($logEntry.Replace('alice', 'bob'))"
Write-Host "  提取 IP（正则匹配）: $(if ($logEntry -match '\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}') { $Matches[0] } else { '未找到' })"
Write-Host ""

# 1.4 字符串插值
Write-Host "1.4 字符串插值" -ForegroundColor Green
$server = "DC01"
$port = 443
Write-Host "  双引号插值: 连接到 ${server}:$port"
Write-Host '  单引号原样: 连接到 ${server}:$port'
Write-Host ""

# ============================================================
# 2. 数组
# ============================================================
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host "【2. 数组】" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host ""

# 2.1 创建数组
Write-Host "2.1 创建数组" -ForegroundColor Green
$services = @("Spooler", "W32Time", "Dhcp", "WinRM", "wuauserv")
$ports = 22, 80, 443, 3389, 445
Write-Host "  服务列表: $($services -join ', ')"
Write-Host "  端口列表: $($ports -join ', ')"
Write-Host ""

# 2.2 访问元素
Write-Host "2.2 数组访问" -ForegroundColor Green
Write-Host "  第一个服务: $($services[0])"
Write-Host "  最后一个服务: $($services[-1])"
Write-Host "  第2到第4个: $($services[1..3] -join ', ')"
Write-Host ""

# 2.3 数组操作
Write-Host "2.3 数组操作" -ForegroundColor Green
Write-Host "  元素数量: $($services.Count)"
$services += "TermService"
Write-Host "  添加后数量: $($services.Count) -> $($services -join ', ')"
Write-Host "  包含 'WinRM' 吗? $($services -contains 'WinRM')"
Write-Host "  不包含 'Telnet' 吗? $($services -notcontains 'Telnet')"
Write-Host ""

# 2.4 安全场景：端口扫描模拟
Write-Host "2.4 安全场景：常用端口列表" -ForegroundColor Green
$commonPorts = @(
    [PSCustomObject]@{Port=22;   Service="SSH";     Risk="远程管理"},
    [PSCustomObject]@{Port=80;   Service="HTTP";    Risk="明文传输"},
    [PSCustomObject]@{Port=443;  Service="HTTPS";   Risk="加密传输"},
    [PSCustomObject]@{Port=445;  Service="SMB";     Risk="横向移动"},
    [PSCustomObject]@{Port=3389; Service="RDP";     Risk="远程桌面"}
)
$commonPorts | Format-Table -AutoSize
Write-Host ""

# ============================================================
# 3. 哈希表
# ============================================================
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host "【3. 哈希表（Hashtable）】" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host ""

# 3.1 创建哈希表
Write-Host "3.1 创建哈希表" -ForegroundColor Green
$systemInfo = @{
    ComputerName = "DC01"
    OS           = "Windows Server 2022"
    IPAddress    = "192.168.1.10"
    Domain       = "corp.local"
    IsDomainController = $true
}
Write-Host "  计算机名: $($systemInfo.ComputerName)"
Write-Host "  操作系统: $($systemInfo['OS'])"
Write-Host ""

# 3.2 添加和修改
Write-Host "3.2 添加和修改" -ForegroundColor Green
$systemInfo.AdminContact = "admin@corp.local"
$systemInfo.IPAddress = "192.168.1.11"
Write-Host "  添加管理员: $($systemInfo.AdminContact)"
Write-Host "  更新后 IP: $($systemInfo.IPAddress)"
Write-Host "  总键数: $($systemInfo.Count)"
Write-Host ""

# 3.3 遍历哈希表
Write-Host "3.3 遍历哈希表" -ForegroundColor Green
$systemInfo.GetEnumerator() | ForEach-Object {
    Write-Host "  $($_.Key): $($_.Value)"
}
Write-Host ""

# 3.4 安全场景：事件日志查询参数
Write-Host "3.4 安全场景：日志查询过滤表" -ForegroundColor Green
$logFilter = @{
    LogName   = "Security"
    ID        = 4624, 4625
    StartTime = (Get-Date).AddHours(-24)
}
Write-Host "  查询日志: $($logFilter.LogName)"
Write-Host "  事件 ID: $($logFilter.ID -join ', ')"
Write-Host "  起始时间: $($logFilter.StartTime)"
Write-Host "  说明: 这是 Get-WinEvent 的常用参数格式（FilterHashtable）"
Write-Host ""

# ============================================================
# 4. 管道操作
# ============================================================
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host "【4. 管道操作】" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host ""

# 4.1 基本管道
Write-Host "4.1 基本管道：服务筛选" -ForegroundColor Green
Get-Service | Where-Object { $_.Status -eq "Running" } |
    Select-Object Name, DisplayName -First 5 |
    Format-Table -AutoSize
Write-Host ""

# 4.2 排序与选择
Write-Host "4.2 排序与选择：进程按 CPU 排序" -ForegroundColor Green
Get-Process | Sort-Object CPU -Descending |
    Select-Object Name, Id, CPU -First 5 |
    Format-Table -AutoSize
Write-Host ""

# 4.3 分组统计
Write-Host "4.3 分组统计：服务按状态分组" -ForegroundColor Green
Get-Service | Group-Object Status |
    Select-Object Name, Count |
    Format-Table -AutoSize
Write-Host ""

# 4.4 管道 ForEach-Object
Write-Host "4.4 ForEach-Object：端口列表处理" -ForegroundColor Green
@(22, 80, 443, 3389) | ForEach-Object {
    Write-Host "  端口 $_ - 服务: $(switch ($_) { 22 {'SSH'} 80 {'HTTP'} 443 {'HTTPS'} 3389 {'RDP'} default {'Unknown'} })"
}
Write-Host ""

# ============================================================
# 5. 条件判断
# ============================================================
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host "【5. 条件判断】" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host ""

# 5.1 if / elseif / else
Write-Host "5.1 if / elseif / else" -ForegroundColor Green
$riskScore = 75
Write-Host "  风险分数: $riskScore"
if ($riskScore -ge 80) {
    Write-Host "  评估: 高危 - 立即处置" -ForegroundColor Red
} elseif ($riskScore -ge 50) {
    Write-Host "  评估: 中危 - 尽快处理" -ForegroundColor Yellow
} elseif ($riskScore -ge 20) {
    Write-Host "  评估: 低危 - 计划处理" -ForegroundColor Green
} else {
    Write-Host "  评估: 无风险" -ForegroundColor Cyan
}
Write-Host ""

# 5.2 比较运算符
Write-Host "5.2 常用比较运算符" -ForegroundColor Green
Write-Host "  -eq 等于:    5 -eq 5  -> $((5 -eq 5))"
Write-Host "  -ne 不等于:  5 -ne 3  -> $((5 -ne 3))"
Write-Host "  -gt 大于:    10 -gt 5 -> $((10 -gt 5))"
Write-Host "  -lt 小于:    3 -lt 5  -> $((3 -lt 5))"
Write-Host "  -ge 大于等于: 5 -ge 5 -> $((5 -ge 5))"
Write-Host "  -le 小于等于: 3 -le 5 -> $((3 -le 5))"
Write-Host "  -like 模糊匹配: 'security' -like '*sec*' -> $(('security' -like '*sec*'))"
Write-Host "  -match 正则:   '192.168.1.1' -match '\d+\.\d+\.\d+\.\d+' -> $(('192.168.1.1' -match '\d+\.\d+\.\d+\.\d+'))"
Write-Host "  -contains 包含: @(1,2,3) -contains 2 -> $((@(1,2,3) -contains 2))"
Write-Host ""

# 5.3 switch
Write-Host "5.3 switch 语句" -ForegroundColor Green
$eventID = 4625
Write-Host "  事件 ID: $eventID"
switch ($eventID) {
    4624 { Write-Host "  类型: 登录成功" -ForegroundColor Green }
    4625 { Write-Host "  类型: 登录失败" -ForegroundColor Red }
    4634 { Write-Host "  类型: 账户注销" -ForegroundColor Yellow }
    4720 { Write-Host "  类型: 创建用户账户" -ForegroundColor Magenta }
    default { Write-Host "  类型: 其他事件" -ForegroundColor Gray }
}
Write-Host ""

# 5.4 逻辑运算符
Write-Host "5.4 逻辑运算符" -ForegroundColor Green
$isFirewallOn = $true
$isAntivirusOn = $false
Write-Host "  防火墙开启: $isFirewallOn"
Write-Host "  杀毒软件开启: $isAntivirusOn"
Write-Host "  两者都开启（-and）: $($isFirewallOn -and $isAntivirusOn)"
Write-Host "  任一开启（-or）: $($isFirewallOn -or $isAntivirusOn)"
Write-Host "  防火墙没开（-not）: $(-not $isFirewallOn)"
Write-Host ""

# ============================================================
# 6. 循环
# ============================================================
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host "【6. 循环】" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host ""

# 6.1 foreach 循环
Write-Host "6.1 foreach 循环：遍历服务列表" -ForegroundColor Green
$keyServices = @("WinRM", "wuauserv", "MpsSvc")
foreach ($svc in $keyServices) {
    $service = Get-Service -Name $svc -ErrorAction SilentlyContinue
    if ($service) {
        $statusColor = if ($service.Status -eq "Running") { "Green" } else { "Red" }
        Write-Host "  $svc : $($service.Status)" -ForegroundColor $statusColor
    } else {
        Write-Host "  $svc : 未找到服务" -ForegroundColor Gray
    }
}
Write-Host ""

# 6.2 for 循环
Write-Host "6.2 for 循环：端口范围生成" -ForegroundColor Green
$portList = @()
for ($i = 1; $i -le 5; $i++) {
    $portList += 8000 + $i
}
Write-Host "  生成端口: $($portList -join ', ')"
Write-Host ""

# 6.3 while 循环
Write-Host "6.3 while 循环：重试机制（安全脚本常用）" -ForegroundColor Green
$attempt = 0
$maxAttempts = 3
$success = $false

while ($attempt -lt $maxAttempts -and -not $success) {
    $attempt++
    Write-Host "  第 $attempt 次尝试..."
    # 模拟检查
    if ($attempt -ge 2) {
        $success = $true
        Write-Host "  检查成功!" -ForegroundColor Green
    } else {
        Write-Host "  检查失败，重试中..." -ForegroundColor Yellow
    }
}
Write-Host ""

# 6.4 do...while 循环
Write-Host "6.4 do...while 循环" -ForegroundColor Green
$count = 0
do {
    $count++
    Write-Host "  计数: $count"
} while ($count -lt 3)
Write-Host ""

# ============================================================
# 7. 函数
# ============================================================
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host "【7. 函数】" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host ""

# 7.1 基本函数
Write-Host "7.1 基本函数：IP 格式验证" -ForegroundColor Green

function Test-IPFormat {
    param(
        [string]$IPAddress
    )
    if ($IPAddress -match '^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$') {
        # 进一步验证每段在 0-255
        $parts = $IPAddress.Split('.')
        foreach ($part in $parts) {
            if ([int]$part -lt 0 -or [int]$part -gt 255) {
                return $false
            }
        }
        return $true
    }
    return $false
}

$testIPs = @("192.168.1.1", "10.0.0.256", "invalid", "8.8.8.8")
foreach ($ip in $testIPs) {
    $valid = Test-IPFormat -IPAddress $ip
    $color = if ($valid) { "Green" } else { "Red" }
    Write-Host "  $ip -> $(if ($valid) { '有效' } else { '无效' })" -ForegroundColor $color
}
Write-Host ""

# 7.2 高级函数（带 CmdletBinding）
Write-Host "7.2 高级函数：端口检查（带 Verbose 输出）" -ForegroundColor Green

function Test-PortConnection {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$ComputerName,

        [Parameter(Mandatory=$true)]
        [int]$Port,

        [Parameter()]
        [int]$TimeoutMs = 1000
    )

    Write-Verbose "正在测试 $ComputerName : $port (超时 $TimeoutMs ms)"

    try {
        $tcpClient = New-Object System.Net.Sockets.TcpClient
        $connect = $tcpClient.BeginConnect($ComputerName, $Port, $null, $null)
        $wait = $connect.AsyncWaitHandle.WaitOne($TimeoutMs, $false)

        if ($wait) {
            $tcpClient.EndConnect($connect)
            $result = $true
        } else {
            $result = $false
        }
        $tcpClient.Close()
    } catch {
        $result = $false
        Write-Verbose "错误: $($_.Exception.Message)"
    }

    [PSCustomObject]@{
        ComputerName = $ComputerName
        Port         = $Port
        Open         = $result
        TestTime     = Get-Date
    }
}

# 测试本地常见端口
Write-Host "  测试本地端口（Verbose 模式开启）:"
Test-PortConnection -ComputerName "127.0.0.1" -Port 135 -Verbose
Write-Host ""

# 7.3 返回对象
Write-Host "7.3 函数返回结构化对象" -ForegroundColor Green

function Get-SystemSecuritySummary {
    $firewall = Get-NetFirewallProfile -Name Domain -ErrorAction SilentlyContinue
    $osInfo = Get-CimInstance Win32_OperatingSystem -ErrorAction SilentlyContinue

    [PSCustomObject]@{
        ComputerName     = $env:COMPUTERNAME
        OS               = if ($osInfo) { $osInfo.Caption } else { "未知" }
        FirewallEnabled  = if ($firewall) { $firewall.Enabled } else { "未知" }
        UserName         = $env:USERNAME
        IsAdmin          = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
        CheckTime        = Get-Date
    }
}

Get-SystemSecuritySummary | Format-List
Write-Host ""

# ============================================================
# 8. 文件操作
# ============================================================
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host "【8. 文件操作】" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host ""

# 8.1 目录与文件列举
Write-Host "8.1 目录列举" -ForegroundColor Green
$testDir = "$env:TEMP\PSBasicsTest"
New-Item -ItemType Directory -Path $testDir -Force | Out-Null
Write-Host "  测试目录: $testDir"

# 创建测试文件
"日志条目 1 - INFO - 系统启动" | Out-File "$testDir\app.log" -Encoding utf8
"日志条目 2 - ERROR - 连接失败" | Add-Content "$testDir\app.log"
"日志条目 3 - WARN - 高内存使用" | Add-Content "$testDir\app.log"
"配置数据" | Out-File "$testDir\config.txt" -Encoding utf8

$files = Get-ChildItem -Path $testDir -File
Write-Host "  文件数量: $($files.Count)"
$files | ForEach-Object { Write-Host "    $($_.Name) ($($_.Length) bytes)" }
Write-Host ""

# 8.2 读取文件
Write-Host "8.2 读取文件内容" -ForegroundColor Green
Write-Host "  app.log 全部内容:"
Get-Content "$testDir\app.log" | ForEach-Object { Write-Host "    $_" }
Write-Host ""

# 8.3 Select-String 搜索（类似 grep）
Write-Host "8.3 Select-String 搜索（类似 grep）" -ForegroundColor Green
Write-Host "  搜索 ERROR 行:"
Select-String -Path "$testDir\app.log" -Pattern "ERROR" | ForEach-Object {
    Write-Host "    行 $($_.LineNumber): $($_.Line)"
}
Write-Host ""

# 8.4 导出 CSV
Write-Host "8.4 导出 CSV" -ForegroundColor Green
$csvPath = "$testDir\security_report.csv"
[PSCustomObject]@{
    CheckItem = "防火墙"
    Status    = "已启用"
    Risk      = "低"
},
[PSCustomObject]@{
    CheckItem = "自动更新"
    Status    = "运行中"
    Risk      = "低"
} | Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8
Write-Host "  已导出: $csvPath"
Write-Host "  CSV 内容:"
Get-Content $csvPath | ForEach-Object { Write-Host "    $_" }
Write-Host ""

# 8.5 文件哈希
Write-Host "8.5 文件哈希（完整性校验）" -ForegroundColor Green
$hash = Get-FileHash -Path "$testDir\config.txt" -Algorithm SHA256
Write-Host "  文件: $($hash.Path)"
Write-Host "  SHA256: $($hash.Hash)"
Write-Host ""

# 清理测试文件
Remove-Item -Path $testDir -Recurse -Force -ErrorAction SilentlyContinue

# ============================================================
# 9. 错误处理
# ============================================================
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host "【9. 错误处理】" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host ""

# 9.1 try/catch/finally
Write-Host "9.1 try/catch/finally" -ForegroundColor Green
try {
    Write-Host "  尝试获取不存在的进程..."
    Get-Process -Name "NonExistentProcessXYZ" -ErrorAction Stop
    Write-Host "  进程存在"
} catch {
    Write-Host "  捕获到错误: $($_.Exception.Message)" -ForegroundColor Red
} finally {
    Write-Host "  finally 块：清理工作（总是执行）"
}
Write-Host ""

# 9.2 ErrorAction 参数
Write-Host "9.2 -ErrorAction 参数" -ForegroundColor Green
Write-Host "  SilentlyContinue（静默忽略）:"
$result = Get-Service -Name "NonExistentService" -ErrorAction SilentlyContinue
Write-Host "    结果: $(if ($result) { '找到' } else { '未找到（无报错）' })"

Write-Host "  Stop（遇错即停）:"
try {
    Get-Service -Name "NonExistentService" -ErrorAction Stop
} catch {
    Write-Host "    已捕获错误并停止" -ForegroundColor Yellow
}
Write-Host ""

# 9.3 $Error 变量
Write-Host "9.3 `$Error 变量（最近错误）" -ForegroundColor Green
Write-Host "  会话错误总数: $($Error.Count)"
if ($Error.Count -gt 0) {
    Write-Host "  最近一条错误: $($Error[0].Exception.Message)"
}
Write-Host ""

# ============================================================
# 10. 对象操作综合示例
# ============================================================
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host "【10. 对象操作综合示例】" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host ""

Write-Host "10.1 进程安全检查：查找可疑进程（路径不在系统目录）" -ForegroundColor Green
Write-Host "  (以下为模拟数据，实际环境使用 Get-Process)"
Write-Host ""

# 模拟进程数据
$mockProcesses = @(
    [PSCustomObject]@{Name="notepad"; Id=1001; Path="C:\Windows\System32\notepad.exe"; CPU=0.5},
    [PSCustomObject]@{Name="powershell"; Id=2002; Path="C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"; CPU=2.3},
    [PSCustomObject]@{Name="suspicious"; Id=3003; Path="C:\Temp\suspicious.exe"; CPU=50.1},
    [PSCustomObject]@{Name="chrome"; Id=4004; Path="C:\Program Files\Google\Chrome\Application\chrome.exe"; CPU=15.7},
    [PSCustomObject]@{Name="miner"; Id=5005; Path="C:\Users\Public\miner.exe"; CPU=99.9}
)

# 筛选 CPU 高的进程
Write-Host "  高 CPU 进程 (>10%):"
$mockProcesses | Where-Object { $_.CPU -gt 10 } |
    Sort-Object CPU -Descending |
    Select-Object Name, Id, CPU |
    Format-Table -AutoSize | Out-String | ForEach-Object { Write-Host "    $_" }

# 筛选可疑路径（不在 Windows 或 Program Files 下）
Write-Host "  可疑路径进程（非系统目录）:"
$mockProcesses | Where-Object {
    $_.Path -notlike "C:\Windows\*" -and
    $_.Path -notlike "C:\Program Files*"
} | Select-Object Name, Path |
    Format-Table -AutoSize | Out-String | ForEach-Object { Write-Host "    $_" }

Write-Host ""

# 10.2 自定义对象输出
Write-Host "10.2 自定义安全报告对象" -ForegroundColor Green
$securityReport = [PSCustomObject]@{
    ReportID     = "SR-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    ComputerName = $env:COMPUTERNAME
    GeneratedBy  = $env:USERNAME
    GeneratedAt  = Get-Date
    TotalChecks  = 10
    PassedChecks = 8
    FailedChecks = 2
    RiskLevel    = "中"
    Recommendations = @("启用 SMB 签名", "禁用不必要的服务")
}

$securityReport | Format-List
Write-Host ""

# ============================================================
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  所有示例执行完毕" -ForegroundColor Cyan
Write-Host "  脚本涵盖：变量、数组、哈希表、管道、条件、循环、" -ForegroundColor Cyan
Write-Host "  函数、文件操作、错误处理、对象操作" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
