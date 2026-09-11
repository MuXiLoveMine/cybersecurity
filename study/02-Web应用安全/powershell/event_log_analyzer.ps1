<#
.SYNOPSIS
    Windows 安全事件日志分析工具 - PowerShell 安全实战
.DESCRIPTION
    分析 Windows 安全事件日志，检测登录失败、暴力破解等异常行为
    重点检测 Event ID 4624（登录成功）和 4625（登录失败）
.NOTES
    仅用于安全学习和授权测试，需要管理员权限运行
.EXAMPLE
    .\event_log_analyzer.ps1 -Hours 24
    .\event_log_analyzer.ps1 -Hours 1 -Export report.csv
#>

param(
    [int]$Hours = 24,
    [string]$Export
)

Write-Host @"
========================================
  Windows 安全事件日志分析器
  需要管理员权限运行
  仅用于安全学习和授权测试
========================================
"@ -ForegroundColor Cyan

# 检查管理员权限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[!] 警告: 未以管理员身份运行，可能无法读取安全日志" -ForegroundColor Yellow
}

$startTime = (Get-Date).AddHours(-$Hours)
Write-Host "[*] 分析时间范围: 最近 $Hours 小时" -ForegroundColor Yellow
Write-Host "[*] 开始时间: $startTime`n" -ForegroundColor Green

# 获取登录失败事件 (Event ID 4625)
Write-Host "===== 登录失败事件 (4625) =====" -ForegroundColor Cyan
try {
    $failedLogins = Get-WinEvent -FilterHashtable @{
        LogName='Security'
        Id=4625
        StartTime=$startTime
    } -ErrorAction Stop

    Write-Host "[*] 登录失败事件总数: $($failedLogins.Count)`n" -ForegroundColor Yellow

    if ($failedLogins.Count -gt 0) {
        # 解析事件
        $failedData = @()
        foreach ($event in $failedLogins) {
            $xml = [xml]$event.ToXml()
            $ns = New-Object System.Xml.XmlNamespaceManager($xml.NameTable)
            $ns.AddNamespace("ev", "http://schemas.microsoft.com/win/2004/08/events/event")

            $targetUser = $xml.SelectSingleNode("//ev:Data[@Name='TargetUserName']", $ns)
            $sourceUser = $xml.SelectSingleNode("//ev:Data[@Name='SubjectUserName']", $ns)
            $logonType = $xml.SelectSingleNode("//ev:Data[@Name='LogonType']", $ns)
            $sourceIp = $xml.SelectSingleNode("//ev:Data[@Name='IpAddress']", $ns)

            $failedData += [PSCustomObject]@{
                TimeCreated = $event.TimeCreated
                TargetUser  = if($targetUser){$targetUser.'#text'}else{""}
                SourceUser  = if($sourceUser){$sourceUser.'#text'}else{""}
                LogonType   = if($logonType){$logonType.'#text'}else{""}
                SourceIP    = if($sourceIp){$sourceIp.'#text'}else{""}
            }
        }

        # 按源 IP 统计（暴力破解检测）
        Write-Host "--- 按源 IP 统计（前 10）---" -ForegroundColor Yellow
        $failedData | Group-Object SourceIP |
            Sort-Object Count -Descending |
            Select-Object -First 10 |
            ForEach-Object {
                Write-Host "  $($_.Name): $($_.Count) 次" -ForegroundColor Red
            }

        # 按目标用户统计
        Write-Host "`n--- 按目标用户统计（前 10）---" -ForegroundColor Yellow
        $failedData | Group-Object TargetUser |
            Sort-Object Count -Descending |
            Select-Object -First 10 |
            ForEach-Object {
                Write-Host "  $($_.Name): $($_.Count) 次" -ForegroundColor Red
            }

        # 暴力破解检测（同一 IP 失败超过 10 次）
        Write-Host "`n--- 暴力破解检测 ---" -ForegroundColor Yellow
        $bruteForce = $failedData | Group-Object SourceIP | Where-Object { $_.Count -ge 10 }
        if ($bruteForce) {
            foreach ($bf in $bruteForce) {
                $users = ($bf.Group | Select-Object -ExpandProperty TargetUser -Unique) -join ', '
                $timeRange = "$($bf.Group[0].TimeCreated) ~ $($bf.Group[-1].TimeCreated)"
                Write-Host "  [!] 疑似暴力破解 IP: $($bf.Name)" -ForegroundColor Red
                Write-Host "      失败次数: $($bf.Count)" -ForegroundColor White
                Write-Host "      尝试用户: $users" -ForegroundColor White
                Write-Host "      时间范围: $timeRange" -ForegroundColor White
            }
        } else {
            Write-Host "  [+] 未检测到暴力破解行为" -ForegroundColor Green
        }

        # 显示最近的失败登录
        Write-Host "`n--- 最近的登录失败（前 20 条）---" -ForegroundColor Yellow
        $failedData | Select-Object -First 20 | Format-Table TimeCreated, TargetUser, SourceIP, LogonType -AutoSize
    }
} catch {
    Write-Host "[!] 无法读取登录失败事件: $($_.Exception.Message)" -ForegroundColor Red
}

# 获取登录成功事件 (Event ID 4624)
Write-Host "`n===== 登录成功事件 (4624) =====" -ForegroundColor Cyan
try {
    $successLogins = Get-WinEvent -FilterHashtable @{
        LogName='Security'
        Id=4624
        StartTime=$startTime
    } -ErrorAction Stop -MaxEvents 100

    Write-Host "[*] 登录成功事件（最多 100 条）`n" -ForegroundColor Yellow

    $successData = @()
    foreach ($event in $successLogins) {
        $xml = [xml]$event.ToXml()
        $ns = New-Object System.Xml.XmlNamespaceManager($xml.NameTable)
        $ns.AddNamespace("ev", "http://schemas.microsoft.com/win/2004/08/events/event")

        $targetUser = $xml.SelectSingleNode("//ev:Data[@Name='TargetUserName']", $ns)
        $logonType = $xml.SelectSingleNode("//ev:Data[@Name='LogonType']", $ns)
        $sourceIp = $xml.SelectSingleNode("//ev:Data[@Name='IpAddress']", $ns)

        # 过滤系统账户
        $user = if($targetUser){$targetUser.'#text'}else{""}
        if ($user -and $user -ne "-" -and $user -notmatch "^(SYSTEM|UMFD-|DWM-|LOCAL SERVICE|NETWORK SERVICE|ANONYMOUS LOGON)") {
            $successData += [PSCustomObject]@{
                TimeCreated = $event.TimeCreated
                TargetUser  = $user
                LogonType   = if($logonType){$logonType.'#text'}else{""}
                SourceIP    = if($sourceIp){$sourceIp.'#text'}else{""}
            }
        }
    }

    if ($successData.Count -gt 0) {
        Write-Host "--- 最近的登录成功 ---" -ForegroundColor Yellow
        $successData | Select-Object -First 20 | Format-Table TimeCreated, TargetUser, SourceIP, LogonType -AutoSize
    } else {
        Write-Host "  [*] 未检测到用户登录成功事件" -ForegroundColor DarkGray
    }
} catch {
    Write-Host "[!] 无法读取登录成功事件: $($_.Exception.Message)" -ForegroundColor Red
}

# 导出报告
if ($Export) {
    $report = @{
        AnalysisTime = Get-Date
        TimeRange = "$Hours hours"
        FailedLogins = $failedData
        SuccessfulLogins = $successData
    }
    $report | ConvertTo-Csv -NoTypeInformation | Out-File $Export -Encoding UTF8
    Write-Host "`n[*] 报告已导出到: $Export" -ForegroundColor Green
}

Write-Host "`n===== 分析完成 =====" -ForegroundColor Cyan
