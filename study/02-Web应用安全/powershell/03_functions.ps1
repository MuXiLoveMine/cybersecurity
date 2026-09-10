# ============================================================
# 03_functions.ps1 - 函数定义、参数、返回值、高级函数
# 运行方式: powershell -ExecutionPolicy Bypass -File .\03_functions.ps1
# ============================================================

Write-Host "=============================="
Write-Host "  1. 基本函数定义"
Write-Host "=============================="

# 简单函数
function Get-Greeting {
    param($name)
    return "Hello, $name!"
}

# 调用函数
$result = Get-Greeting -name "PowerShell"
Write-Host $result

# 不带 param 的简单函数（不推荐，但可用）
function Say-Hello {
    "Hello World!"
}

Write-Host (Say-Hello)

Write-Host ""
Write-Host "=============================="
Write-Host "  2. 函数参数"
Write-Host "=============================="

# 带默认值的参数
function Get-UserInfo {
    param(
        [string]$Name = "匿名用户",
        [int]$Age = 18,
        [string]$City = "北京"
    )

    Write-Host "姓名: $Name"
    Write-Host "年龄: $Age"
    Write-Host "城市: $City"
}

Write-Host "--- 调用（指定全部参数） ---"
Get-UserInfo -Name "张三" -Age 25 -City "上海"

Write-Host "--- 调用（使用默认值） ---"
Get-UserInfo -Name "李四"

Write-Host "--- 调用（不指定任何参数） ---"
Get-UserInfo

Write-Host ""
Write-Host "=============================="
Write-Host "  3. 返回值"
Write-Host "=============================="

# PowerShell 中所有未被捕获的输出都是返回值
function Add-Numbers {
    param($a, $b)
    $a + $b          # 隐式返回
}

$sum = Add-Numbers -a 3 -b 5
Write-Host "3 + 5 = $sum"

# 使用 return 显式返回（同时终止函数）
function Get-Absolute {
    param([int]$num)
    if ($num -ge 0) {
        return $num
    }
    return -$num
}

Write-Host "|5| = $(Get-Absolute -num 5)"
Write-Host "|-7| = $(Get-Absolute -num -7)"

# 返回多个值（数组形式）
function Get-Dimensions {
    param([int]$width, [int]$height)
    $area = $width * $height
    $perimeter = 2 * ($width + $height)
    return $area, $perimeter
}

$area, $perimeter = Get-Dimensions -width 5 -height 3
Write-Host "矩形 5x3: 面积=$area, 周长=$perimeter"

Write-Host ""
Write-Host "=============================="
Write-Host "  4. 参数验证"
Write-Host "=============================="

function New-Person {
    param(
        [Parameter(Mandatory=$true)]
        [ValidateLength(2, 20)]
        [string]$Name,

        [ValidateRange(1, 120)]
        [int]$Age = 18,

        [ValidateSet("男", "女", "其他")]
        [string]$Gender = "男",

        [ValidatePattern("^\w+@\w+\.\w+$")]
        [string]$Email = "test@example.com"
    )

    Write-Host "创建用户: $Name"
    Write-Host "  年龄: $Age"
    Write-Host "  性别: $Gender"
    Write-Host "  邮箱: $Email"
}

Write-Host "--- 合法调用 ---"
New-Person -Name "王五" -Age 30 -Gender "男" -Email "wangwu@test.com"

# 以下调用会报错（取消注释测试）
# New-Person -Name "A" -Age 30           # 名字太短
# New-Person -Name "测试" -Age 200       # 年龄超出范围
# New-Person -Name "测试" -Gender "未知"  # 性别不在允许列表中

Write-Host ""
Write-Host "=============================="
Write-Host "  5. 高级函数 [CmdletBinding()]"
Write-Host "=============================="

# 使用 CmdletBinding 获得通用参数支持：-Verbose, -Debug, -WhatIf 等
function Invoke-Test {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$Target
    )

    Write-Verbose "开始处理目标: $Target"
    Write-Debug "调试信息: 正在检查 $Target"
    Write-Host "处理中: $Target"
    Write-Verbose "处理完成: $Target"
}

Write-Host "--- 普通调用（无 verbose） ---"
Invoke-Test -Target "Server01"

Write-Host ""
Write-Host "--- 带 -Verbose 调用 ---"
Invoke-Test -Target "Server02" -Verbose

# -Debug 会暂停等待确认（注释掉避免阻塞）
# Invoke-Test -Target "Server03" -Debug

Write-Host ""
Write-Host "=============================="
Write-Host "  6. 管道输入"
Write-Host "=============================="

# 简单管道输入（ValueFromPipeline）
function Get-Square {
    param(
        [Parameter(ValueFromPipeline=$true)]
        [int]$Number
    )
    process {
        $Number * $Number
    }
}

Write-Host "管道输入 1..5 求平方:"
1..5 | Get-Square | ForEach-Object { Write-Host "  $_" }

# 按属性名绑定管道输入（ValueFromPipelineByPropertyName）
function Get-FullName {
    param(
        [Parameter(ValueFromPipelineByPropertyName=$true)]
        [string]$FirstName,

        [Parameter(ValueFromPipelineByPropertyName=$true)]
        [string]$LastName
    )
    process {
        "$FirstName $LastName"
    }
}

Write-Host ""
Write-Host "按属性名绑定管道输入:"
$people = @(
    @{ FirstName = "张"; LastName = "三" }
    @{ FirstName = "李"; LastName = "四" }
    @{ FirstName = "王"; LastName = "五" }
) | ForEach-Object { [pscustomobject]$_ }

$people | Get-FullName | ForEach-Object { Write-Host "  $_" }

Write-Host ""
Write-Host "=============================="
Write-Host "  7. Begin / Process / End 块"
Write-Host "=============================="

# 管道函数的三个块：
# Begin: 管道开始前执行一次
# Process: 每个管道对象执行一次
# End: 管道结束后执行一次
function Get-Sum {
    [CmdletBinding()]
    param(
        [Parameter(ValueFromPipeline=$true)]
        [int]$Number
    )
    begin {
        Write-Host "Begin: 初始化总和为 0"
        $sum = 0
    }
    process {
        Write-Host "Process: 加上 $Number"
        $sum += $Number
    }
    end {
        Write-Host "End: 返回总和 $sum"
        return $sum
    }
}

Write-Host "计算 1..5 的和:"
$total = 1..5 | Get-Sum
Write-Host "总和: $total"

Write-Host ""
Write-Host "=============================="
Write-Host "  8. 参数集（Parameter Sets）"
Write-Host "=============================="

function Get-Info {
    [CmdletBinding(DefaultParameterSetName="ByName")]
    param(
        [Parameter(Mandatory=$true, ParameterSetName="ByName")]
        [string]$Name,

        [Parameter(Mandatory=$true, ParameterSetName="ById")]
        [int]$Id
    )

    if ($PSCmdlet.ParameterSetName -eq "ByName") {
        Write-Host "按名称查询: $Name"
    }
    else {
        Write-Host "按 ID 查询: $Id"
    }
}

Write-Host "使用 Name 参数集:"
Get-Info -Name "张三"

Write-Host "使用 ID 参数集:"
Get-Info -Id 1001

# 不能同时使用两个参数集的参数（取消注释测试）
# Get-Info -Name "张三" -Id 1001

Write-Host ""
Write-Host "=============================="
Write-Host "  9. 函数别名"
Write-Host "=============================="

# 为函数创建别名
function Write-Hello {
    param([string]$Name = "World")
    Write-Host "Hello, $Name!"
}

Set-Alias -Name wh -Value Write-Hello

Write-Host "使用别名 wh 调用:"
wh -Name "PowerShell"

Write-Host ""
Write-Host "=============================="
Write-Host "  10. 递归函数"
Write-Host "=============================="

# 阶乘
function Get-Factorial {
    param([int]$n)
    if ($n -le 1) {
        return 1
    }
    return $n * (Get-Factorial -n ($n - 1))
}

Write-Host "阶乘计算:"
for ($i = 1; $i -le 7; $i++) {
    Write-Host "  $i! = $(Get-Factorial -n $i)"
}

# 斐波那契数列
function Get-Fibonacci {
    param([int]$n)
    if ($n -le 1) { return $n }
    return (Get-Fibonacci -n ($n - 1)) + (Get-Fibonacci -n ($n - 2))
}

Write-Host ""
Write-Host "斐波那契数列前 10 项:"
$fib = 0..9 | ForEach-Object { Get-Fibonacci -n $_ }
Write-Host "  $($fib -join ', ')"

Write-Host ""
Write-Host "脚本执行完毕！"
