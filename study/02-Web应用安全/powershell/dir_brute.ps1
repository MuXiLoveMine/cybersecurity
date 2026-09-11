<#
.SYNOPSIS
    Web 目录爆破工具 - PowerShell 安全实战
.DESCRIPTION
    基于 Invoke-WebRequest 的 Web 目录/文件扫描工具
    内置常见路径字典，支持自定义字典和扩展名
.NOTES
    仅用于安全学习和授权测试，禁止非法用途
.EXAMPLE
    .\dir_brute.ps1 -Url http://example.com
    .\dir_brute.ps1 -Url http://example.com -Wordlist custom.txt -Extensions php,bak,html
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$Url,

    [string]$Wordlist,

    [string[]]$Extensions = @("", ".php", ".html", ".bak", ".txt", ".zip"),

    [int]$Threads = 20,

    [int]$Timeout = 10
)

Write-Host @"
========================================
  Web 目录爆破工具 (PowerShell)
  仅用于安全学习和授权测试
========================================
"@ -ForegroundColor Cyan

# 内置常见路径字典
$builtInDict = @(
    "admin", "administrator", "login", "manage", "manager", "backend",
    "backup", "config", "test", "debug", "tmp", "temp",
    "api", "v1", "v2", "swagger", "graphql",
    ".git", ".svn", ".env", ".htaccess", "web.config",
    "phpinfo", "phpmyadmin", "pma", "adminer",
    "wp-admin", "wp-content", "wp-login.php",
    "upload", "uploads", "files", "download",
    "shell", "cmd", "system", "exec",
    "data", "database", "db", "sql",
    "logs", "log", "access.log", "error.log",
    "robots.txt", "sitemap.xml", "crossdomain.xml",
    "README", "CHANGELOG", "LICENSE",
    "install", "setup", "configure",
    "old", "new", "dev", "stage", "production",
    "include", "includes", "lib", "src",
    "static", "public", "assets", "js", "css",
    "favicon.ico", "index.php", "index.html"
)

# 加载字典
if ($Wordlist -and (Test-Path $Wordlist)) {
    $dict = Get-Content $Wordlist | Where-Object { $_.Trim() -ne "" -and $_ -notmatch "^#" }
    Write-Host "[*] 已加载自定义字典: $($dict.Count) 条" -ForegroundColor Yellow
} else {
    $dict = $builtInDict
    Write-Host "[*] 使用内置字典: $($dict.Count) 条" -ForegroundColor Yellow
}

# 构建完整 URL 列表
$urls = @()
foreach ($word in $dict) {
    foreach ($ext in $Extensions) {
        $path = "$word$ext"
        $urls += "$($Url.TrimEnd('/'))/$path"
    }
}

Write-Host "[*] 目标: $Url" -ForegroundColor Yellow
Write-Host "[*] 总请求数: $($urls.Count)" -ForegroundColor Yellow
Write-Host "[*] 开始扫描...`n" -ForegroundColor Green

# 忽略 SSL 证书错误
[System.Net.ServicePointManager]::ServerCertificateValidationCallback = { $true }
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$results = @()
$count = 0

foreach ($targetUrl in $urls) {
    $count++
    try {
        $response = Invoke-WebRequest -Uri $targetUrl -Method Head -TimeoutSec $Timeout `
            -UseBasicParsing -ErrorAction Stop -MaximumRedirection 0

        $status = [int]$response.StatusCode
        $length = $response.RawContentLength

        # 200/301/302/401/403 都值得关注
        if ($status -in @(200, 301, 302, 401, 403)) {
            $statusColor = switch ($status) {
                200 { "Green" }
                301 { "Cyan" }
                302 { "Cyan" }
                401 { "Yellow" }
                403 { "Yellow" }
                default { "White" }
            }
            Write-Host "  [$status] $targetUrl  ($length bytes)" -ForegroundColor $statusColor
            $results += [PSCustomObject]@{
                Url        = $targetUrl
                StatusCode = $status
                Length     = $length
            }
        }
    } catch {
        $status = $_.Exception.Response.StatusCode.value__
        if ($status -in @(200, 301, 302, 401, 403)) {
            $length = 0
            try {
                $length = $_.Exception.Response.ContentLength
            } catch {}
            Write-Host "  [$status] $targetUrl" -ForegroundColor Yellow
            $results += [PSCustomObject]@{
                Url        = $targetUrl
                StatusCode = $status
                Length     = $length
            }
        }
    }

    if ($count % 50 -eq 0) {
        $progress = [math]::Floor($count / $urls.Count * 100)
        Write-Progress -Activity "目录爆破" -Status "$count / $($urls.Count) ($progress%)" -PercentComplete $progress
    }
}

Write-Progress -Activity "目录爆破" -Completed
Write-Host "`n===== 扫描结果 =====" -ForegroundColor Cyan
Write-Host "总请求: $($urls.Count)" -ForegroundColor White
Write-Host "发现路径: $($results.Count)" -ForegroundColor Green

if ($results.Count -gt 0) {
    $results | Format-Table -AutoSize
    $results | Export-Csv -Path "dir_brute_$(Get-Date -Format 'yyyyMMdd_HHmmss').csv" -NoTypeInformation
    Write-Host "`n结果已保存到 CSV 文件" -ForegroundColor Green
}
