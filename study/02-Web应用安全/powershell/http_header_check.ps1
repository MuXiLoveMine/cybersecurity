<#
.SYNOPSIS
    HTTP 安全头检测工具 - PowerShell 安全实战
.DESCRIPTION
    检测网站的安全响应头配置，给出评分和修复建议
    检测 7 大安全头 + 信息泄露头 + Cookie 安全属性
.NOTES
    仅用于安全学习和授权测试
.EXAMPLE
    .\http_header_check.ps1 -Url https://example.com
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$Url
)

Write-Host @"
========================================
  HTTP 安全头检测工具 (PowerShell)
  仅用于安全学习和授权测试
========================================
"@ -ForegroundColor Cyan

# 忽略 SSL 证书错误
[System.Net.ServicePointManager]::ServerCertificateValidationCallback = { $true }
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# 安全头检查清单
$securityHeaders = @(
    @{ Name="X-Frame-Options";           Score=10; Risk="高"; Desc="防止点击劫持（Clickjacking）"; Fix="添加 X-Frame-Options: SAMEORIGIN" },
    @{ Name="X-Content-Type-Options";    Score=10; Risk="高"; Desc="防止 MIME 类型嗅探"; Fix="添加 X-Content-Type-Options: nosniff" },
    @{ Name="X-XSS-Protection";           Score=5;  Risk="中"; Desc="浏览器 XSS 过滤器"; Fix="添加 X-XSS-Protection: 1; mode=block" },
    @{ Name="Content-Security-Policy";   Score=15; Risk="高"; Desc="内容安全策略，防 XSS/数据注入"; Fix="配置 CSP 策略，限制脚本来源" },
    @{ Name="Strict-Transport-Security"; Score=10; Risk="高"; Desc="HSTS 强制 HTTPS"; Fix="添加 Strict-Transport-Security: max-age=31536000; includeSubDomains" },
    @{ Name="Referrer-Policy";           Score=5;  Risk="中"; Desc="控制 Referer 信息泄露"; Fix="添加 Referrer-Policy: no-referrer-when-downgrade" },
    @{ Name="Permissions-Policy";        Score=5;  Risk="低"; Desc="控制浏览器功能权限"; Fix="配置 Permissions-Policy 限制功能访问" }
)

# 信息泄露头检查
$leakHeaders = @(
    "Server", "X-Powered-By", "X-AspNet-Version",
    "X-AspNetMvc-Version", "Via", "X-Runtime"
)

try {
    Write-Host "[*] 目标: $Url" -ForegroundColor Yellow
    Write-Host "[*] 发送请求...`n" -ForegroundColor Green

    $response = Invoke-WebRequest -Uri $Url -Method Head -TimeoutSec 15 -UseBasicParsing -ErrorAction Stop

    $headers = $response.Headers
    $totalScore = 0
    $maxScore = 0
    $missing = @()
    $present = @()

    Write-Host "===== 安全响应头检查 =====" -ForegroundColor Cyan
    foreach ($h in $securityHeaders) {
        $maxScore += $h.Score
        $headerName = $h.Name
        $found = $false
        foreach ($key in $headers.Keys) {
            if ($key -ieq $headerName) {
                $found = $true
                $value = $headers[$key]
                $totalScore += $h.Score
                Write-Host "  [+] $headerName : $value" -ForegroundColor Green
                $present += [PSCustomObject]@{ Header=$headerName; Value=$value; Score=$h.Score }
                break
            }
        }
        if (-not $found) {
            Write-Host "  [-] $headerName : 缺失" -ForegroundColor Red -NoNewline
            Write-Host "  (风险: $($h.Risk) | $($h.Desc) | 建议: $($h.Fix))" -ForegroundColor DarkYellow
            $missing += [PSCustomObject]@{ Header=$headerName; Risk=$h.Risk; Desc=$h.Desc; Fix=$h.Fix }
        }
    }

    # 信息泄露检测
    Write-Host "`n===== 信息泄露检测 =====" -ForegroundColor Cyan
    $leakFound = @()
    foreach ($lh in $leakHeaders) {
        foreach ($key in $headers.Keys) {
            if ($key -ieq $lh) {
                $value = $headers[$key]
                Write-Host "  [!] $lh : $value" -ForegroundColor Red
                $leakFound += [PSCustomObject]@{ Header=$lh; Value=$value }
                $totalScore -= 5
                break
            }
        }
    }
    if ($leakFound.Count -eq 0) {
        Write-Host "  [+] 未检测到信息泄露头" -ForegroundColor Green
    }

    # Cookie 安全检测
    Write-Host "`n===== Cookie 安全检测 =====" -ForegroundColor Cyan
    $cookies = $response.Headers['Set-Cookie']
    if ($cookies) {
        foreach ($cookie in $cookies) {
            $hasSecure = $cookie -match ';\s*Secure'
            $hasHttpOnly = $cookie -match ';\s*HttpOnly'
            $hasSameSite = $cookie -match ';\s*SameSite'
            $cookieName = ($cookie -split '=')[0]
            Write-Host "  Cookie: $cookieName" -ForegroundColor White
            if (-not $hasSecure) { Write-Host "    [-] 缺少 Secure 属性" -ForegroundColor Red }
            if (-not $hasHttpOnly) { Write-Host "    [-] 缺少 HttpOnly 属性" -ForegroundColor Red }
            if (-not $hasSameSite) { Write-Host "    [-] 缺少 SameSite 属性" -ForegroundColor Yellow }
        }
    } else {
        Write-Host "  [*] 未设置 Cookie" -ForegroundColor DarkGray
    }

    # 评分
    $percentage = [math]::Floor($totalScore / $maxScore * 100)
    $grade = if ($percentage -ge 90) { "A" }
             elseif ($percentage -ge 80) { "B" }
             elseif ($percentage -ge 70) { "C" }
             elseif ($percentage -ge 60) { "D" }
             else { "F" }

    Write-Host "`n===== 安全评分 =====" -ForegroundColor Cyan
    Write-Host "  得分: $totalScore / $maxScore ($percentage%)" -ForegroundColor $(if($percentage -ge 70){'Green'}else{'Red'})
    Write-Host "  等级: $grade" -ForegroundColor $(if($percentage -ge 70){'Green'}else{'Red'})
    Write-Host "  已配置: $($present.Count) / $($securityHeaders.Count)" -ForegroundColor White
    Write-Host "  缺失: $($missing.Count)" -ForegroundColor $(if($missing.Count -gt 0){'Red'}else{'Green'})
    Write-Host "  信息泄露: $($leakFound.Count)" -ForegroundColor $(if($leakFound.Count -gt 0){'Red'}else{'Green'})

    Write-Host "`n===== 修复建议 =====" -ForegroundColor Cyan
    if ($missing.Count -gt 0) {
        foreach ($m in $missing) {
            Write-Host "  [$($m.Risk)] $($m.Header)" -ForegroundColor Yellow
            Write-Host "       $($m.Fix)" -ForegroundColor DarkGray
        }
    } else {
        Write-Host "  所有安全头已配置！" -ForegroundColor Green
    }

} catch {
    Write-Host "[!] 请求失败: $($_.Exception.Message)" -ForegroundColor Red
}
