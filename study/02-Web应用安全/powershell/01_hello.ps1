# ============================================================
# 01_hello.ps1 - Hello World、变量、数据类型、输出
# 运行方式: powershell -ExecutionPolicy Bypass -File .\01_hello.ps1
# ============================================================

Write-Host "=============================="
Write-Host "  1. Hello World"
Write-Host "=============================="

# 最基本的输出方式
Write-Host "Hello, PowerShell!"

# Write-Output 输出到管道（可以被后续命令接收）
Write-Output "这是 Write-Output 的输出"

# 直接输出表达式（隐式输出）
"直接输出字符串"
1 + 1

Write-Host ""
Write-Host "=============================="
Write-Host "  2. 变量基础"
Write-Host "=============================="

# 变量以 $ 开头，不需要声明类型
$name = "张三"
$age = 25
$pi = 3.14159
$isActive = $true

Write-Host "姓名: $name"
Write-Host "年龄: $age"
Write-Host "圆周率: $pi"
Write-Host "是否激活: $isActive"

# 查看变量类型
Write-Host ""
Write-Host "变量类型:"
Write-Host "`$name 的类型: $($name.GetType().Name)"
Write-Host "`$age 的类型: $($age.GetType().Name)"
Write-Host "`$pi 的类型: $($pi.GetType().Name)"
Write-Host "`$isActive 的类型: $($isActive.GetType().Name)"

Write-Host ""
Write-Host "=============================="
Write-Host "  3. 强类型声明"
Write-Host "=============================="

# 使用 [类型] 前缀强制变量类型
[int]$number = 42
[string]$text = "Hello"
[bool]$flag = $false
[double]$price = 19.99
[datetime]$today = Get-Date

Write-Host "整数: $number (类型: $($number.GetType().Name))"
Write-Host "字符串: $text (类型: $($text.GetType().Name))"
Write-Host "布尔: $flag (类型: $($flag.GetType().Name))"
Write-Host "浮点数: $price (类型: $($price.GetType().Name))"
Write-Host "日期: $today (类型: $($today.GetType().Name))"

# 强类型变量不能赋值其他类型（会自动转换或报错）
# $number = "abc"    # 这行会报错，因为不能将字符串转为 int

Write-Host ""
Write-Host "=============================="
Write-Host "  4. 常用数据类型"
Write-Host "=============================="

# 字符串
$str1 = '单引号字符串: 不解析变量 $name'
$str2 = "双引号字符串: 解析变量 $name"
Write-Host $str1
Write-Host $str2

# 数字
$intNum = 100
$longNum = 9223372036854775807
$doubleNum = 3.14
$decimalNum = 19.99D
Write-Host "整数: $intNum"
Write-Host "长整数: $longNum"
Write-Host "双精度: $doubleNum"
Write-Host "十进制: $decimalNum"

# 布尔值
$t = $true
$f = $false
Write-Host "真: $t, 假: $f"

# 空值
$nullVar = $null
Write-Host "空值: $nullVar"
Write-Host "是否为空: $($null -eq $nullVar)"

# 数组
$colors = "红", "绿", "蓝"
Write-Host "数组: $colors"
Write-Host "数组第一个元素: $($colors[0])"

# 哈希表
$person = @{
    Name = "李四"
    Age = 30
    City = "上海"
}
Write-Host "哈希表: Name=$($person.Name), Age=$($person.Age)"

Write-Host ""
Write-Host "=============================="
Write-Host "  5. Write-Host 与 Write-Output 的区别"
Write-Host "=============================="

# Write-Host: 直接输出到控制台，不能被管道捕获
# Write-Output: 输出到管道，可以被后续命令使用

Write-Host "Write-Host 输出（直接到控制台）"
Write-Output "Write-Output 输出（到管道，可以被捕获）"

# 演示 Write-Output 可以被管道捕获
$result = Write-Output "这个输出会被变量捕获"
Write-Host "捕获的结果: $result"

Write-Host ""
Write-Host "=============================="
Write-Host "  6. 特殊变量"
Write-Host "=============================="

# 常用特殊变量
Write-Host "当前目录: $PWD"
Write-Host "主目录: $HOME"
Write-Host "进程 ID: $PID"
Write-Host "PowerShell 版本: $($PSVersionTable.PSVersion)"

# 环境变量
Write-Host "用户名: $env:USERNAME"
Write-Host "计算机名: $env:COMPUTERNAME"
Write-Host "系统根目录: $env:SystemRoot"

Write-Host ""
Write-Host "=============================="
Write-Host "  7. 类型转换"
Write-Host "=============================="

# 字符串转数字
$numStr = "123"
$num = [int]$numStr
Write-Host "字符串 '$numStr' 转整数: $num (类型: $($num.GetType().Name))"

# 数字转字符串
$num2 = 456
$str = [string]$num2
Write-Host "数字 $num2 转字符串: '$str' (类型: $($str.GetType().Name))"

# 字符串转日期
$dateStr = "2024-01-15"
$date = [datetime]$dateStr
Write-Host "字符串 '$dateStr' 转日期: $date (类型: $($date.GetType().Name))"

# 布尔转换
Write-Host "[bool]1 = $([bool]1)"
Write-Host "[bool]0 = $([bool]0)"
Write-Host "[bool]'hello' = $([bool]'hello')"
Write-Host "[bool]'' = $([bool]'')"

Write-Host ""
Write-Host "脚本执行完毕！"
