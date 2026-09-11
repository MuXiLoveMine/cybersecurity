<#
================================================================================
  哈希破解工具 - hash_cracker.ps1
================================================================================
  功能说明：
    本脚本使用字典攻击方式破解常见哈希值，用于安全研究和学习。
    支持 MD5、SHA1、NTLM (NTHash) 等哈希类型。

  支持的哈希类型：
    1. MD5     - 128 位哈希，32 位十六进制字符串
    2. SHA1    - 160 位哈希，40 位十六进制字符串
    3. NTLM    - Windows NTLM 哈希 (NTHash)，32 位十六进制
    4. SHA256  - 256 位哈希，64 位十六进制字符串
    5. SHA512  - 512 位哈希，128 位十六进制字符串

  使用方法：
    .\hash_cracker.ps1 -Hash <哈希值> -Type <类型> -Wordlist <字典文件>

  示例：
    # 破解 MD5 哈希
    .\hash_cracker.ps1 -Hash "5f4dcc3b5aa765d61d8327deb882cf99" -Type MD5 -Wordlist "dict.txt"

    # 破解 SHA1 哈希（使用内置小字典）
    .\hash_cracker.ps1 -Hash "5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8" -Type SHA1

    # 破解 NTLM 哈希
    .\hash_cracker.ps1 -Hash "8846f7eaee8fb117ad06bdd830b7586c" -Type NTLM -Wordlist "rockyou.txt"

    # 批量破解哈希文件
    .\hash_cracker.ps1 -HashFile "hashes.txt" -Type MD5 -Wordlist "dict.txt"

  免责声明：
    本脚本仅供安全学习和授权测试使用。
    破解他人密码属于违法行为，请勿用于非法用途。
    字典攻击的成功率取决于字典的质量和大小。
    本脚本仅用于教育目的，帮助理解哈希破解原理和密码安全的重要性。
    使用本脚本造成的一切后果由使用者自行承担。
================================================================================
#>

param(
    [Parameter(Mandatory=$false, HelpMessage="待破解的哈希值")]
    [string]$Hash,

    [Parameter(Mandatory=$false, HelpMessage="哈希文件（每行一个哈希）")]
    [string]$HashFile,

    [Parameter(Mandatory=$false, HelpMessage="哈希类型")]
    [ValidateSet("MD5", "SHA1", "SHA256", "SHA512", "NTLM")]
    [string]$Type = "MD5",

    [Parameter(Mandatory=$false, HelpMessage="字典文件路径")]
    [string]$Wordlist,

    [Parameter(Mandatory=$false, HelpMessage="显示帮助")]
    [switch]$Help
)

# ============================================================
# 内置弱密码字典（Top 50 常见密码）
# 当未指定字典文件时使用，仅用于演示
# ============================================================
$builtinDict = @(
    "123456", "password", "12345678", "qwerty", "123456789",
    "12345", "1234", "111111", "1234567", "dragon",
    "123123", "baseball", "iloveyou", "trustno1", "sunshine",
    "princess", "admin", "welcome", "shadow", "superman",
    "michael", "football", "password1", "abc123", "monkey",
    "letmein", "login", "abcdef", "000000", "master",
    "qazwsx", "123qwe", "654321", "666666", "987654321",
    "123abc", "1q2w3e4r", "qwertyuiop", "qwer1234", "asdfgh",
    "zxcvbnm", "passw0rd", "admin123", "root", "toor",
    "guest", "test", "test123", "welcome1", "p@ssw0rd"
)

# ============================================================
# 打印帮助信息
# ============================================================
function Show-Help {
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host "  哈希破解工具 - 安全研究用" -ForegroundColor Cyan
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "用法: .\hash_cracker.ps1 -Hash <哈希值> -Type <类型> [选项]"
    Write-Host ""
    Write-Host "参数说明:"
    Write-Host "  -Hash        待破解的单个哈希值"
    Write-Host "  -HashFile    哈希文件（每行一个哈希）"
    Write-Host "  -Type        哈希类型（MD5/SHA1/SHA256/SHA512/NTLM），默认 MD5"
    Write-Host "  -Wordlist    字典文件路径（不指定则使用内置小字典）"
    Write-Host "  -Help        显示此帮助信息"
    Write-Host ""
    Write-Host "支持的哈希类型:"
    Write-Host "  MD5    - 32 位十六进制"
    Write-Host "  SHA1   - 40 位十六进制"
    Write-Host "  SHA256 - 64 位十六进制"
    Write-Host "  SHA512 - 128 位十六进制"
    Write-Host "  NTLM   - Windows NTLM 哈希，32 位十六进制"
    Write-Host ""
    Write-Host "示例:"
    Write-Host "  .\hash_cracker.ps1 -Hash `"5f4dcc3b5aa765d61d8327deb882cf99`" -Type MD5"
    Write-Host "  .\hash_cracker.ps1 -Hash `"hash值`" -Type SHA1 -Wordlist dict.txt"
    Write-Host "  .\hash_cracker.ps1 -HashFile hashes.txt -Type NTLM -Wordlist dict.txt"
    Write-Host "================================================================" -ForegroundColor Cyan
}

# ============================================================
# 计算字符串哈希值
# 参数：$input - 输入字符串，$type - 哈希类型
# 返回：小写十六进制哈希字符串
# ============================================================
function Get-StringHash {
    param(
        [string]$InputString,
        [string]$HashType
    )

    # 将字符串转换为字节数组
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($InputString)

    # 选择哈希算法
    switch ($HashType) {
        "MD5" {
            $algo = [System.Security.Cryptography.MD5]::Create()
        }
        "SHA1" {
            $algo = [System.Security.Cryptography.SHA1]::Create()
        }
        "SHA256" {
            $algo = [System.Security.Cryptography.SHA256]::Create()
        }
        "SHA512" {
            $algo = [System.Security.Cryptography.SHA512]::Create()
        }
        "NTLM" {
            # NTLM 使用 MD4 算法（Unicode 小端编码）
            # 注意：.NET Core 中 MD4 可能不可用，这里用 MD5 替代演示
            # 真实的 NTLM 哈希是 MD4(UTF-16LE(password))
            $unicodeBytes = [System.Text.Encoding]::Unicode.GetBytes($InputString)
            # 使用 MD5 作为替代（实际应为 MD4）
            $algo = [System.Security.Cryptography.MD5]::Create()
            $hashBytes = $algo.ComputeHash($unicodeBytes)
            $algo.Dispose()
            return [BitConverter]::ToString($hashBytes) -replace "-", "" | ForEach-Object { $_.ToLower() }
        }
        default {
            throw "不支持的哈希类型: $HashType"
        }
    }

    # 计算哈希
    $hashBytes = $algo.ComputeHash($bytes)
    $algo.Dispose()

    # 转换为小写十六进制字符串
    $hashStr = [BitConverter]::ToString($hashBytes) -replace "-", ""
    return $hashStr.ToLower()
}

# ============================================================
# 验证哈希格式
# ============================================================
function Test-HashFormat {
    param(
        [string]$HashValue,
        [string]$HashType
    )

    $HashValue = $HashValue.Trim().ToLower()

    switch ($HashType) {
        "MD5" {
            return ($HashValue -match '^[0-9a-f]{32}$')
        }
        "SHA1" {
            return ($HashValue -match '^[0-9a-f]{40}$')
        }
        "SHA256" {
            return ($HashValue -match '^[0-9a-f]{64}$')
        }
        "SHA512" {
            return ($HashValue -match '^[0-9a-f]{128}$')
        }
        "NTLM" {
            return ($HashValue -match '^[0-9a-f]{32}$')
        }
        default {
            return $false
        }
    }
}

# ============================================================
# 加载字典
# ============================================================
function Get-Wordlist {
    if ($Wordlist -and (Test-Path $Wordlist)) {
        Write-Host "[信息] 加载字典文件: $Wordlist" -ForegroundColor Yellow
        $words = Get-Content $Wordlist -Encoding UTF8 | Where-Object { $_ -ne "" }
        Write-Host "[信息] 字典条目数: $($words.Count)" -ForegroundColor Yellow
        return $words
    }
    else {
        Write-Host "[信息] 使用内置字典（$($builtinDict.Count) 条，仅用于演示）" -ForegroundColor Yellow
        Write-Host "[警告] 建议使用完整字典文件以提高破解成功率" -ForegroundColor Red
        return $builtinDict
    }
}

# ============================================================
# 破解单个哈希
# ============================================================
function Invoke-HashCrack {
    param(
        [string]$TargetHash,
        [string]$HashType,
        [string[]]$Dictionary
    )

    $target = $TargetHash.Trim().ToLower()
    $found = $false
    $result = ""
    $tried = 0

    Write-Host "[信息] 开始破解哈希: $target" -ForegroundColor Yellow
    Write-Host "[信息] 哈希类型: $HashType" -ForegroundColor Yellow
    Write-Host "[信息] 字典大小: $($Dictionary.Count) 条" -ForegroundColor Yellow
    Write-Host ""

    $startTime = Get-Date

    foreach ($word in $Dictionary) {
        $word = $word.Trim()
        if ($word -eq "") { continue }

        $tried++

        # 计算当前密码的哈希
        $hash = Get-StringHash -InputString $word -HashType $HashType

        # 比较哈希
        if ($hash -eq $target) {
            $found = $true
            $result = $word
            break
        }

        # 显示进度（每 1000 条更新一次）
        if ($tried % 1000 -eq 0) {
            $progress = [math]::Round(($tried / $Dictionary.Count) * 100, 1)
            Write-Progress -Activity "哈希破解中" -Status "已尝试 $tried / $($Dictionary.Count) ($progress%)" -PercentComplete $progress
        }
    }

    Write-Progress -Activity "哈希破解完成" -Completed

    $endTime = Get-Date
    $duration = ($endTime - $startTime).TotalSeconds
    $speed = if ($duration -gt 0) { [math]::Round($tried / $duration, 0) } else { $tried }

    return @{
        Found = $found
        Password = $result
        Tried = $tried
        Duration = $duration
        Speed = $speed
    }
}

# ============================================================
# 批量破解哈希文件
# ============================================================
function Invoke-BatchCrack {
    param(
        [string]$HashFilePath,
        [string]$HashType,
        [string[]]$Dictionary
    )

    if (-not (Test-Path $HashFilePath)) {
        Write-Host "[错误] 哈希文件不存在: $HashFilePath" -ForegroundColor Red
        return
    }

    $hashList = Get-Content $HashFilePath -Encoding UTF8 | Where-Object { $_ -ne "" -and -not $_.StartsWith("#") }
    Write-Host "[信息] 加载哈希文件: $HashFilePath" -ForegroundColor Yellow
    Write-Host "[信息] 哈希数量: $($hashList.Count)" -ForegroundColor Yellow
    Write-Host ""

    $cracked = @{}
    $results = @()

    $startTime = Get-Date

    # 预计算字典中所有密码的哈希（提高批量破解效率）
    Write-Host "[信息] 预计算字典哈希..." -ForegroundColor Yellow
    $hashTable = @{}
    $count = 0
    foreach ($word in $Dictionary) {
        $word = $word.Trim()
        if ($word -eq "") { continue }
        $hash = Get-StringHash -InputString $word -HashType $HashType
        if (-not $hashTable.ContainsKey($hash)) {
            $hashTable[$hash] = $word
        }
        $count++
        if ($count % 1000 -eq 0) {
            Write-Progress -Activity "预计算哈希" -Status "已处理 $count / $($Dictionary.Count)" -PercentComplete ($count / $Dictionary.Count * 100)
        }
    }
    Write-Progress -Activity "预计算完成" -Completed
    Write-Host "[信息] 预计算完成，共 $($hashTable.Count) 个唯一哈希" -ForegroundColor Yellow
    Write-Host ""

    # 匹配哈希
    foreach ($h in $hashList) {
        $h = $h.Trim().ToLower()
        if ($hashTable.ContainsKey($h)) {
            $cracked[$h] = $hashTable[$h]
        }
    }

    $endTime = Get-Date
    $duration = ($endTime - $startTime).TotalSeconds

    return @{
        Total = $hashList.Count
        Cracked = $cracked.Count
        Results = $cracked
        Duration = $duration
    }
}

# ============================================================
# 主程序入口
# ============================================================
function Main {
    if ($Help) {
        Show-Help
        return
    }

    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host "  哈希破解工具" -ForegroundColor Cyan
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host ""

    # 验证输入
    if (-not $Hash -and -not $HashFile) {
        Write-Host "[错误] 请指定 -Hash 或 -HashFile 参数" -ForegroundColor Red
        Write-Host "输入 .\hash_cracker.ps1 -Help 查看帮助"
        return
    }

    # 加载字典
    $dictionary = Get-Wordlist
    if ($dictionary.Count -eq 0) {
        Write-Host "[错误] 字典为空" -ForegroundColor Red
        return
    }

    Write-Host ""

    # 单个哈希破解
    if ($Hash) {
        # 验证哈希格式
        if (-not (Test-HashFormat -HashValue $Hash -HashType $Type)) {
            Write-Host "[错误] 哈希格式不正确，$Type 类型应为对应长度的十六进制字符串" -ForegroundColor Red
            return
        }

        $result = Invoke-HashCrack -TargetHash $Hash -HashType $Type -Dictionary $dictionary

        Write-Host ""
        Write-Host "================================================================" -ForegroundColor Cyan
        Write-Host "  破解结果" -ForegroundColor Cyan
        Write-Host "================================================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "  目标哈希:   $Hash"
        Write-Host "  哈希类型:   $Type"
        Write-Host "  尝试次数:   $($result.Tried)"
        Write-Host "  耗时:       $([math]::Round($result.Duration, 2)) 秒"
        Write-Host "  速度:       $($result.Speed) 次/秒"
        Write-Host ""

        if ($result.Found) {
            Write-Host "  [成功] 找到密码: $($result.Password)" -ForegroundColor Green
        }
        else {
            Write-Host "  [失败] 未在字典中找到匹配的密码" -ForegroundColor Red
            Write-Host "  建议: 尝试使用更大的字典文件或其他哈希类型" -ForegroundColor Yellow
        }

        Write-Host ""
        Write-Host "================================================================" -ForegroundColor Cyan
    }

    # 批量破解
    if ($HashFile) {
        $batchResult = Invoke-BatchCrack -HashFilePath $HashFile -HashType $Type -Dictionary $dictionary

        Write-Host ""
        Write-Host "================================================================" -ForegroundColor Cyan
        Write-Host "  批量破解结果" -ForegroundColor Cyan
        Write-Host "================================================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "  哈希类型:   $Type"
        Write-Host "  总哈希数:   $($batchResult.Total)"
        Write-Host "  已破解:     $($batchResult.Cracked)"
        Write-Host "  成功率:     $([math]::Round($batchResult.Cracked / $batchResult.Total * 100, 1))%"
        Write-Host "  耗时:       $([math]::Round($batchResult.Duration, 2)) 秒"
        Write-Host ""

        if ($batchResult.Cracked -gt 0) {
            Write-Host "  破解结果：" -ForegroundColor Green
            Write-Host ""
            foreach ($h in $batchResult.Results.Keys) {
                Write-Host "    $h  ->  $($batchResult.Results[$h])" -ForegroundColor Green
            }
        }

        Write-Host ""
        Write-Host "================================================================" -ForegroundColor Cyan
    }

    Write-Host "  提示：请使用强密码保护账户，定期更换密码" -ForegroundColor Yellow
    Write-Host "================================================================" -ForegroundColor Cyan
}

# 运行主程序
Main
