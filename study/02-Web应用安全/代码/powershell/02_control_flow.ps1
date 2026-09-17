# ============================================================
# 02_control_flow.ps1 - 控制流：条件判断与循环
# 运行方式: powershell -ExecutionPolicy Bypass -File .\02_control_flow.ps1
# ============================================================

Write-Host "=============================="
Write-Host "  1. if / elseif / else"
Write-Host "=============================="

$score = 85

if ($score -ge 90) {
    Write-Host "成绩: 优秀 (>= 90)"
}
elseif ($score -ge 80) {
    Write-Host "成绩: 良好 (>= 80)"
}
elseif ($score -ge 60) {
    Write-Host "成绩: 及格 (>= 60)"
}
else {
    Write-Host "成绩: 不及格 (< 60)"
}

# 多条件判断
$age = 25
$hasLicense = $true

if ($age -ge 18 -and $hasLicense) {
    Write-Host "可以开车（成年且有驾照）"
}
elseif ($age -ge 18 -and -not $hasLicense) {
    Write-Host "成年但没有驾照，不能开车"
}
else {
    Write-Host "未成年，不能开车"
}

Write-Host ""
Write-Host "=============================="
Write-Host "  2. switch 语句"
Write-Host "=============================="

$day = 3

switch ($day) {
    1 { Write-Host "星期一" }
    2 { Write-Host "星期二" }
    3 { Write-Host "星期三" }
    4 { Write-Host "星期四" }
    5 { Write-Host "星期五" }
    6 { Write-Host "星期六" }
    7 { Write-Host "星期日" }
    default { Write-Host "无效的日期" }
}

# switch 支持多值匹配
Write-Host ""
Write-Host "switch 多值匹配（水果颜色）:"
$fruits = @("苹果", "香蕉", "葡萄", "橙子")

switch ($fruits) {
    "苹果" { Write-Host "  苹果是红色的" }
    "香蕉" { Write-Host "  香蕉是黄色的" }
    "葡萄" { Write-Host "  葡萄是紫色的" }
    default { Write-Host "  未知水果: $_" }
}

# switch -Wildcard（通配符匹配）
Write-Host ""
Write-Host "switch -Wildcard:"
$file = "document.pdf"

switch -Wildcard ($file) {
    "*.txt" { Write-Host "  文本文件" }
    "*.pdf" { Write-Host "  PDF 文件" }
    "*.ps1" { Write-Host "  PowerShell 脚本" }
    "*.exe" { Write-Host "  可执行文件" }
}

# switch -Regex（正则匹配）
Write-Host ""
Write-Host "switch -Regex（IP 地址判断）:"
$ip = "192.168.1.100"

switch -Regex ($ip) {
    "^192\.168\." { Write-Host "  $ip 是 C 类内网地址" }
    "^10\." { Write-Host "  $ip 是 A 类内网地址" }
    "^172\.(1[6-9]|2[0-9]|3[01])\." { Write-Host "  $ip 是 B 类内网地址" }
    "^127\." { Write-Host "  $ip 是回环地址" }
    default { Write-Host "  $ip 是公网地址" }
}

Write-Host ""
Write-Host "=============================="
Write-Host "  3. for 循环"
Write-Host "=============================="

# 基础 for 循环
Write-Host "for 循环输出 1 到 5:"
for ($i = 1; $i -le 5; $i++) {
    Write-Host "  $i"
}

# 倒序循环
Write-Host "倒序输出 5 到 1:"
for ($i = 5; $i -ge 1; $i--) {
    Write-Host "  $i"
}

# 步长为 2
Write-Host "1 到 10 的奇数:"
for ($i = 1; $i -le 10; $i += 2) {
    Write-Host "  $i"
}

Write-Host ""
Write-Host "=============================="
Write-Host "  4. foreach 循环"
Write-Host "=============================="

# 遍历数组
$colors = @("红", "橙", "黄", "绿", "青", "蓝", "紫")
Write-Host "遍历颜色数组:"
foreach ($color in $colors) {
    Write-Host "  $color"
}

# 遍历数字范围
Write-Host "1..5 范围:"
foreach ($num in 1..5) {
    Write-Host "  数字: $num, 平方: $($num * $num)"
}

Write-Host ""
Write-Host "=============================="
Write-Host "  5. while 循环"
Write-Host "=============================="

# while 循环：先判断条件，再执行
$i = 1
Write-Host "while 循环 (1 到 5):"
while ($i -le 5) {
    Write-Host "  i = $i"
    $i++
}

# while 可能一次都不执行
$j = 10
Write-Host "while 循环 (j=10, 条件 j -le 5，不会执行):"
while ($j -le 5) {
    Write-Host "  j = $j"
    $j++
}
Write-Host "  （循环体未执行）"

Write-Host ""
Write-Host "=============================="
Write-Host "  6. do-while 循环"
Write-Host "=============================="

# do-while：先执行一次，再判断条件
$i = 1
Write-Host "do-while 循环 (1 到 5):"
do {
    Write-Host "  i = $i"
    $i++
} while ($i -le 5)

# do-while 至少执行一次
$j = 10
Write-Host "do-while 循环 (j=10, 条件 j -le 5，仍会执行一次):"
do {
    Write-Host "  j = $j (执行了一次)"
    $j++
} while ($j -le 5)

Write-Host ""
Write-Host "=============================="
Write-Host "  7. do-until 循环"
Write-Host "=============================="

# do-until：执行直到条件为真时停止
$i = 1
Write-Host "do-until 循环 (直到 i > 5 停止):"
do {
    Write-Host "  i = $i"
    $i++
} until ($i -gt 5)

Write-Host ""
Write-Host "=============================="
Write-Host "  8. break 和 continue"
Write-Host "=============================="

# break：跳出整个循环
Write-Host "break 示例 (遇到 5 跳出):"
for ($i = 1; $i -le 10; $i++) {
    if ($i -eq 5) {
        Write-Host "  遇到 $i，跳出循环"
        break
    }
    Write-Host "  i = $i"
}

# continue：跳过当前迭代，继续下一次
Write-Host ""
Write-Host "continue 示例 (跳过偶数):"
for ($i = 1; $i -le 10; $i++) {
    if ($i % 2 -eq 0) {
        continue
    }
    Write-Host "  奇数: $i"
}

# 嵌套循环中的 break
Write-Host ""
Write-Host "嵌套循环 break 示例:"
:outer for ($i = 1; $i -le 3; $i++) {
    for ($j = 1; $j -le 3; $j++) {
        if ($i -eq 2 -and $j -eq 2) {
            Write-Host "  遇到 i=$i, j=$j，跳出外层循环"
            break outer
        }
        Write-Host "  i=$i, j=$j"
    }
}

Write-Host ""
Write-Host "=============================="
Write-Host "  9. 综合示例：九九乘法表"
Write-Host "=============================="

for ($i = 1; $i -le 9; $i++) {
    $line = ""
    for ($j = 1; $j -le $i; $j++) {
        $line += "{0}x{1}={2}`t" -f $j, $i, ($i * $j)
    }
    Write-Host $line
}

Write-Host ""
Write-Host "脚本执行完毕！"
