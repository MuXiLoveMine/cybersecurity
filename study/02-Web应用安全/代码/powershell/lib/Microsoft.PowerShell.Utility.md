# Microsoft.PowerShell.Utility - PowerShell 核心模块

> PowerShell 核心实用工具模块，提供最常用的命令。

---

## 一、基本输出与变量

### 1.1 输出命令

```powershell
# Write-Output - 输出到管道（默认）
Write-Output "Hello World"
"Hello World"  # 简写（隐式调用 Write-Output）

# Write-Host - 直接输出到控制台（不进入管道）
Write-Host "Hello World"
Write-Host " colored " -ForegroundColor Red -BackgroundColor White
Write-Host "no newline" -NoNewline

# Write-Verbose - 详细输出（需要 -Verbose 或 $VerbosePreference）
Write-Verbose "详细信息"

# Write-Debug - 调试输出
Write-Debug "调试信息"

# Write-Warning - 警告信息
Write-Warning "警告"

# Write-Error - 错误信息
Write-Error "错误信息"

# Write-Progress - 进度条
for ($i = 0; $i -le 100; $i += 10) {
    Write-Progress -Activity "处理中" -Status "$i% 完成" -PercentComplete $i
    Start-Sleep -Milliseconds 200
}
```

### 1.2 变量与环境

```powershell
# 变量赋值
$name = "Alice"
$age = 25
$list = 1, 2, 3, 4, 5
$dict = @{ key1 = "value1"; key2 = "value2" }

# 变量类型
[string]$str = "hello"
[int]$num = 42
[bool]$flag = $true

# 环境变量
$env:PATH
$env:USERNAME
$env:COMPUTERNAME
$env:TEMP

# 自动变量
$PWD           # 当前路径
$HOME          # 用户主目录
$PSVersionTable  # PowerShell 版本信息
$Error[0]      # 最近的错误
$LASTEXITCODE  # 上次外部程序的退出码
$PID           # 当前进程 ID
$args          # 脚本/函数的参数
$input         # 管道输入
$_ 或 $PSItem  # 当前管道对象
$null          # 空值

# 变量作用域
$global:var    # 全局作用域
$script:var    # 脚本作用域
$local:var     # 局部作用域
$private:var   # 私有作用域
```

---

## 二、常用 Cmdlet

### 2.1 对象操作

```powershell
# Select-Object - 选择属性
Get-Process | Select-Object Name, Id, CPU
Get-Process | Select-Object -First 5
Get-Process | Select-Object -Last 5
Get-Process | Select-Object -Unique
Get-Process | Select-Object -Property *, @{Name="MemMB"; Expression={$_.WS/1MB}}

# Where-Object - 过滤
Get-Process | Where-Object { $_.CPU -gt 100 }
Get-Process | Where-Object CPU -gt 100  # 简写
Get-Service | Where-Object Status -eq Running

# Sort-Object - 排序
Get-Process | Sort-Object CPU -Descending
Get-Process | Sort-Object Name
Get-ChildItem | Sort-Object Length -Descending

# Group-Object - 分组
Get-Process | Group-Object PriorityClass
Get-ChildItem | Group-Object Extension

# Measure-Object - 统计
Get-ChildItem | Measure-Object -Property Length -Sum -Average -Maximum -Minimum
1..100 | Measure-Object -Sum

# ForEach-Object - 遍历
1..5 | ForEach-Object { $_ * 2 }
Get-ChildItem | ForEach-Object { $_.Name }

# 简写
1..5 | % { $_ * 2 }          # % = ForEach-Object
Get-Process | ? { $_.CPU -gt 10 }  # ? = Where-Object
```

### 2.2 字符串操作

```powershell
# 字符串格式化
"Hello {0}, you are {1} years old" -f "Alice", 25

# 字符串方法
$str = "Hello World"
$str.ToUpper()       # HELLO WORLD
$str.ToLower()       # hello world
$str.Length          # 11
$str.Substring(0, 5) # Hello
$str.Replace("World", "PowerShell")
$str.Contains("Hello")
$str.StartsWith("He")
$str.EndsWith("ld")
$str.Split(" ")      # 分割成数组
$str.Trim()          # 去除首尾空白
$str.IndexOf("o")    # 4

# -replace 操作符（正则替换）
"hello world" -replace "world", "powershell"
"a1b2c3" -replace "\d", "X"     # aXbXcX
"abc123" -replace "(\w+)(\d+)", '$2$1'  # 123abc

# -match 操作符
"hello@world.com" -match "^[\w.-]+@[\w.-]+\.\w+$"
$matches[0]  # 匹配的内容

# -split / -join
"a,b,c" -split ","    # @("a", "b", "c")
@("a", "b", "c") -join ","  # "a,b,c"
```

### 2.3 数组与哈希表

```powershell
# 数组
$arr = 1, 2, 3, 4, 5
$arr[0]         # 第一个元素
$arr[-1]        # 最后一个元素
$arr[0..2]      # 前三个元素
$arr.Length     # 元素个数
$arr += 6       # 添加元素

# 数组方法
$arr = @(1, 2, 3)
$arr.Add(4)           # 添加（[System.Collections.ArrayList] 才支持）
$arr.Remove(2)        # 删除
$arr.Contains(3)      # 包含
$arr.IndexOf(3)       # 索引

# 哈希表（字典）
$dict = @{
    Name = "Alice"
    Age = 25
    City = "Beijing"
}

$dict.Name          # Alice
$dict["Name"]       # Alice
$dict.Keys          # 所有键
$dict.Values        # 所有值
$dict.Count         # 键值对数量

$dict.Add("Job", "Engineer")  # 添加
$dict.Remove("Age")           # 删除
$dict.ContainsKey("Name")     # 是否包含键

# 有序哈希表
$ordered = [ordered]@{
    First = 1
    Second = 2
    Third = 3
}
```

---

## 三、文件系统操作

### 3.1 文件与目录

```powershell
# Get-ChildItem - 列出目录
Get-ChildItem                    # 当前目录
Get-ChildItem -Path C:\          # 指定目录
Get-ChildItem -Recurse           # 递归
Get-ChildItem -File              # 只显示文件
Get-ChildItem -Directory         # 只显示目录
Get-ChildItem -Hidden            # 显示隐藏文件
Get-ChildItem -Filter *.txt      # 过滤
Get-ChildItem *.txt -Recurse     # 递归找 txt 文件

# 别名：dir, ls, gci

# New-Item - 创建文件/目录
New-Item -Path "test.txt" -ItemType File
New-Item -Path "mydir" -ItemType Directory
New-Item -Path "subdir/file.txt" -Force  # 强制创建（自动创建父目录）

# ni 别名

# Copy-Item - 复制
Copy-Item source.txt dest.txt
Copy-Item -Path srcdir -Destination destdir -Recurse
Copy-Item *.txt -Destination backup\

# copy, cp, cpi 别名

# Move-Item - 移动
Move-Item source.txt dest\
Move-Item *.txt backup\

# move, mv, mi 别名

# Remove-Item - 删除
Remove-Item file.txt
Remove-Item dir -Recurse    # 删除目录及其内容
Remove-Item *.txt
Remove-Item -Recurse -Force  # 强制删除（包括只读）

# del, rm, rmdir, ri 别名

# Rename-Item - 重命名
Rename-Item old.txt new.txt
Get-ChildItem *.txt | Rename-Item -NewName { $_.Name -replace '\.txt$', '.bak' }

# ren, rni 别名
```

### 3.2 文件内容

```powershell
# Get-Content - 读取文件
Get-Content file.txt
Get-Content file.txt -TotalCount 10    # 前 10 行
Get-Content file.txt -Tail 10          # 后 10 行
Get-Content file.txt -Wait             # 实时跟踪（类似 tail -f）
Get-Content file.txt -Encoding UTF8    # 指定编码

# cat, type, gc 别名

# Set-Content - 写入文件（覆盖）
Set-Content -Path file.txt -Value "Hello World"
Set-Content -Path file.txt -Value $lines -Encoding UTF8

# sc 别名

# Add-Content - 追加
Add-Content -Path file.txt -Value "new line"
Add-Content -Path file.txt -Value "line1", "line2"

# ac 别名

# Out-File - 输出到文件
Get-Process | Out-File -FilePath processes.txt
Get-Process | Out-File -FilePath processes.txt -Encoding UTF8 -Width 200

# Convert 相关
Import-Csv data.csv             # 导入 CSV
Export-Csv -Path data.csv       # 导出 CSV
Get-Content file.json | ConvertFrom-Json  # JSON 转对象
$obj | ConvertTo-Json           # 对象转 JSON
```

---

## 四、安全相关内容

### 4.1 执行策略

```powershell
<#
    PowerShell 执行策略：
    - Restricted   - 不允许运行脚本（默认 Windows 客户端）
    - AllSigned    - 所有脚本必须有签名
    - RemoteSigned - 本地脚本可运行，下载的脚本需签名（默认服务器）
    - Unrestricted - 所有脚本都能运行（不安全）
    - Bypass       - 不阻止，无警告
    - Undefined    - 未设置（继承更高级别的策略）
    
    作用域级别：
    - MachinePolicy  - 组策略（计算机）
    - UserPolicy     - 组策略（用户）
    - Process        - 当前进程
    - CurrentUser    - 当前用户
    - LocalMachine   - 本机
#>

# 查看执行策略
Get-ExecutionPolicy
Get-ExecutionPolicy -List

# 设置执行策略（需要管理员权限）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 临时修改（只影响当前进程）
powershell.exe -ExecutionPolicy Bypass -File script.ps1

# 注意：执行策略不是安全边界，只是保护措施
# 有很多绕过方式，例如：
# powershell -Command "..."  （命令不触发执行策略）
# Get-Content script.ps1 | Invoke-Expression
```

### 4.2 脚本安全最佳实践

```powershell
<#
    脚本安全建议：
    
    1. 使用 Set-StrictMode - 启用严格模式
    2. 参数验证 - 验证输入参数
    3. 避免使用 Invoke-Expression - 可能导致注入
    4. 正确引用路径 - 防止路径遍历
    5. 敏感信息处理 - 不要硬编码密码
    6. 错误信息脱敏 - 不泄露敏感信息
#>

# ===== 严格模式 =====
Set-StrictMode -Version Latest
# 强制变量声明、禁止调用不存在的属性等

# ===== 参数验证 =====
function Get-User {
    param(
        [Parameter(Mandatory=$true)]
        [ValidatePattern('^[a-zA-Z0-9_]+$')]
        [string]$Username
    )
    
    # 安全使用 $Username
    Get-LocalUser $Username
}

# ===== 避免 Invoke-Expression =====
# ❌ 危险：用户输入直接执行
$userInput = Read-Host "输入命令"
Invoke-Expression $userInput  # 命令注入！

# ✅ 安全：使用 & 调用命令
$cmd = "Get-Process"
& $cmd -Name "powershell"

# ===== 安全的文件路径 =====
function Get-SafeFile {
    param(
        [string]$Filename
    )
    
    $baseDir = "C:\safe\path\"
    
    # 1. 只取文件名（防止路径遍历）
    $safeFilename = Split-Path -Leaf $Filename
    
    # 2. 组合路径
    $fullPath = Join-Path -Path $baseDir -ChildPath $safeFilename
    
    # 3. 验证规范化路径在基础目录内
    $resolvedPath = Resolve-Path -Path $fullPath -ErrorAction SilentlyContinue
    if (-not $resolvedPath) {
        Write-Error "文件不存在"
        return
    }
    
    if ($resolvedPath.Path.StartsWith($baseDir)) {
        Get-Content $resolvedPath.Path
    } else {
        Write-Error "非法路径"
    }
}
```

### 4.3 凭证与敏感信息

```powershell
# ===== 安全处理凭证 =====

# Get-Credential - 交互式获取凭证
$cred = Get-Credential

# 安全字符串（加密存储）
$securePassword = Read-Host "输入密码" -AsSecureString

# 转换为明文凭证（仅内存中使用）
$ptr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
$plainPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($ptr)
[System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)

# 保存加密凭证到文件（只能在同一用户同一机器上解密）
$cred | Export-Clixml -Path credential.xml

# 导入
$cred = Import-Clixml -Path credential.xml

# 用于远程连接
Enter-PSSession -ComputerName server01 -Credential $cred

# ===== 敏感信息日志 =====
# 不要在日志中输出密码、Token 等
Write-Host "用户: $username, 密码: $password"  # ❌ 危险！
Write-Host "用户: $username, 密码: ***"        # ✅ 脱敏

# ConvertTo-SecureString
$password = "plaintext" | ConvertTo-SecureString -AsPlainText -Force
```

### 4.4 输入验证示例

```powershell
function Invoke-SafeScript {
    param(
        [Parameter(Mandatory=$true)]
        [ValidateLength(1, 50)]
        [ValidatePattern('^[a-zA-Z0-9_-]+$')]
        [string]$Name,
        
        [Parameter(Mandatory=$true)]
        [ValidateRange(1, 65535)]
        [int]$Port,
        
        [Parameter(Mandatory=$true)]
        [ValidateSet('Start', 'Stop', 'Restart')]
        [string]$Action
    )
    
    # 参数已经过验证，可以安全使用
    Write-Host "执行 $Action 操作，名称: $Name, 端口: $Port"
}

# 文件路径验证
function Test-SafePath {
    param(
        [string]$Path,
        [string]$BaseDir
    )
    
    # 规范化路径
    try {
        $fullPath = Resolve-Path -Path $Path -ErrorAction Stop
    } catch {
        return $false
    }
    
    # 检查是否在基础目录内
    return $fullPath.Path.StartsWith(
        (Resolve-Path $BaseDir).Path,
        [System.StringComparison]::OrdinalIgnoreCase
    )
}
```

---

## 五、其他常用模块

```powershell
# Microsoft.PowerShell.Management - 系统管理
Get-Service          # 获取服务
Get-Process          # 获取进程
Get-EventLog         # 事件日志
Get-ItemProperty     # 注册表
Restart-Computer     # 重启
Stop-Computer        # 关机

# Microsoft.PowerShell.Security - 安全
Get-ExecutionPolicy
Set-ExecutionPolicy
Get-Acl              # 获取访问控制列表
Set-Acl              # 设置访问控制列表
ConvertTo-SecureString
ConvertFrom-SecureString

# Microsoft.PowerShell.Diagnostics - 诊断
Get-WinEvent         # Windows 事件日志
Get-Counter          # 性能计数器

# Microsoft.WSMan.Management - 远程管理
Enable-PSRemoting
Enter-PSSession
Invoke-Command
```

---

## 六、常用别名速查

| 别名 | 完整名称 | 说明 |
|------|---------|------|
| `cd` | `Set-Location` | 切换目录 |
| `dir`, `ls` | `Get-ChildItem` | 列出目录 |
| `cat`, `type`, `gc` | `Get-Content` | 读取文件 |
| `cp`, `copy` | `Copy-Item` | 复制 |
| `mv`, `move` | `Move-Item` | 移动 |
| `rm`, `del`, `rmdir` | `Remove-Item` | 删除 |
| `echo`, `write` | `Write-Output` | 输出 |
| `%` | `ForEach-Object` | 遍历 |
| `?`, `where` | `Where-Object` | 过滤 |
| `sort` | `Sort-Object` | 排序 |
| `select` | `Select-Object` | 选择 |
| `sleep` | `Start-Sleep` | 等待 |
| `kill` | `Stop-Process` | 终止进程 |
| `ps` | `Get-Process` | 获取进程 |
