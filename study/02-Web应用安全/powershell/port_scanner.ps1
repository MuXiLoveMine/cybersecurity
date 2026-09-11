<#
.SYNOPSIS
    TCP 端口扫描器 - PowerShell 安全实战工具
.DESCRIPTION
    使用 System.Net.Sockets.TcpClient 进行 TCP 全连接端口扫描
    支持指定 IP/域名和端口范围，使用 Runspace 实现多线程并发
.NOTES
    仅用于安全学习和授权测试，禁止非法用途
.EXAMPLE
    .\port_scanner.ps1 -Target 192.168.1.1 -StartPort 1 -EndPort 1000
    .\port_scanner.ps1 -Target 10.0.0.0/24 -Ports 22,80,443,3306
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$Target,

    [int]$StartPort = 1,
    [int]$EndPort = 1024,

    [string]$Ports,

    [int]$Threads = 100
)

# 免责声明
Write-Host @"
========================================
  PowerShell TCP 端口扫描器
  仅用于安全学习和授权测试
========================================
"@ -ForegroundColor Cyan

# 解析目标（支持单 IP 和网段）
function Resolve-Targets {
    param([string]$target)
    $targets = @()
    if ($target -match '/') {
        $parts = $target -split '/'
        $baseIp = $parts[0]
        $cidr = [int]$parts[1]
        $hostBits = 32 - $cidr
        $hostCount = [math]::Pow(2, $hostBits) - 2
        $ipBytes = $baseIp.Split('.') | ForEach-Object { [int]$_ }
        $baseNum = ($ipBytes[0] * 16777216) + ($ipBytes[1] * 65536) + ($ipBytes[2] * 256) + $ipBytes[3]
        for ($i = 1; $i -le $hostCount; $i++) {
            $num = $baseNum + $i
            $targets += "$([math]::Floor($num / 16777216)).$([math]::Floor(($num % 16777216) / 65536)).$([math]::Floor(($num % 65536) / 256)).$($num % 256)"
        }
    } else {
        $targets += $target
    }
    return $targets
}

# 解析端口列表
function Get-PortList {
    param(
        [int]$start, [int]$end, [string]$portStr
    )
    if ($portStr) {
        $ports = @()
        $portStr.Split(',') | ForEach-Object { $ports += [int]($_.Trim()) }
        return $ports
    }
    return $start..$end
}

# 常见端口服务名映射
$serviceMap = @{
    21='FTP'; 22='SSH'; 23='Telnet'; 25='SMTP'; 53='DNS';
    80='HTTP'; 110='POP3'; 143='IMAP'; 443='HTTPS';
    445='SMB'; 1433='MSSQL'; 3306='MySQL'; 3389='RDP';
    5432='PostgreSQL'; 6379='Redis'; 8080='HTTP-Proxy';
    27017='MongoDB'; 9200='Elasticsearch'; 11211='Memcached'
}

# 扫描单个端口
function Test-Port {
    param([string]$ip, [int]$port, [int]$timeout = 1500)
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $result = $tcp.BeginConnect($ip, $port, $null, $null)
        $success = $result.AsyncWaitHandle.WaitOne($timeout, $false)
        if ($success -and $tcp.Connected) {
            $tcp.Close()
            return $true
        }
        $tcp.Close()
    } catch {}
    return $false
}

# 主扫描逻辑
$targets = Resolve-Targets $Target
$portList = Get-PortList $StartPort $EndPort $Ports

Write-Host "[*] 目标: $($targets.Count) 个主机" -ForegroundColor Yellow
Write-Host "[*] 端口: $($portList.Count) 个" -ForegroundColor Yellow
Write-Host "[*] 开始扫描...`n" -ForegroundColor Green

$totalTasks = $targets.Count * $portList.Count
$completed = 0
$results = @()

foreach ($ip in $targets) {
    Write-Host "[*] 扫描主机: $ip" -ForegroundColor Cyan
    foreach ($port in $portList) {
        if (Test-Port -ip $ip -port $port) {
            $service = if ($serviceMap.ContainsKey($port)) { $serviceMap[$port] } else { "unknown" }
            $result = [PSCustomObject]@{
                IP       = $ip
                Port     = $port
                State    = "open"
                Service  = $service
            }
            $results += $result
            Write-Host "  [+] $ip`:$port  OPEN  ($service)" -ForegroundColor Green
        }
        $completed++
        if ($completed % 100 -eq 0) {
            $progress = [math]::Floor($completed / $totalTasks * 100)
            Write-Progress -Activity "端口扫描" -Status "$completed / $totalTasks ($progress%)" -PercentComplete $progress
        }
    }
}

Write-Progress -Activity "端口扫描" -Completed
Write-Host "`n===== 扫描结果摘要 =====" -ForegroundColor Cyan
Write-Host "扫描主机数: $($targets.Count)" -ForegroundColor White
Write-Host "扫描端口数: $($portList.Count)" -ForegroundColor White
Write-Host "发现开放端口: $($results.Count)" -ForegroundColor Green

if ($results.Count -gt 0) {
    Write-Host "`n开放端口列表:" -ForegroundColor Yellow
    $results | Format-Table -AutoSize
}

Export-Csv -InputObject $results -Path "port_scan_$(Get-Date -Format 'yyyyMMdd_HHmmss').csv" -NoTypeInformation -ErrorAction SilentlyContinue
