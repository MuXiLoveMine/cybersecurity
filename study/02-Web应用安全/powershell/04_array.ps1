# ============================================================
# 04_array.ps1 - 数组创建、操作、遍历、常用方法
# 运行方式: powershell -ExecutionPolicy Bypass -File .\04_array.ps1
# ============================================================

Write-Host "=============================="
Write-Host "  1. 创建数组"
Write-Host "=============================="

# 方式一：逗号分隔
$arr1 = 1, 2, 3, 4, 5
Write-Host "逗号分隔: $arr1"

# 方式二：@() 语法
$arr2 = @("苹果", "香蕉", "橙子")
Write-Host "@() 语法: $arr2"

# 方式三：范围运算符
$arr3 = 1..10
Write-Host "范围运算符 1..10: $arr3"

# 方式四：空数组
$empty = @()
Write-Host "空数组长度: $($empty.Length)"

# 方式五：强类型数组
[int[]]$intArr = 1, 2, 3, 4, 5
[string[]]$strArr = "a", "b", "c"
Write-Host "强类型 int 数组: $intArr"
Write-Host "强类型 string 数组: $strArr"

# 方式六：单元素数组
$single = @(42)
Write-Host "单元素数组: $single (长度: $($single.Length))"

Write-Host ""
Write-Host "=============================="
Write-Host "  2. 访问数组元素"
Write-Host "=============================="

$fruits = @("苹果", "香蕉", "橙子", "葡萄", "西瓜")

Write-Host "水果数组: $fruits"
Write-Host "第一个元素 [0]: $($fruits[0])"
Write-Host "第三个元素 [2]: $($fruits[2])"
Write-Host "最后一个元素 [-1]: $($fruits[-1])"
Write-Host "倒数第二个 [-2]: $($fruits[-2])"
Write-Host "前三个 [0..2]: $($fruits[0..2] -join ', ')"
Write-Host "数组长度: $($fruits.Length)"
Write-Host "数组元素数 (Count): $($fruits.Count)"

Write-Host ""
Write-Host "=============================="
Write-Host "  3. 修改数组"
Write-Host "=============================="

$numbers = 1..5
Write-Host "原始数组: $numbers"

# 修改元素
$numbers[0] = 100
Write-Host "修改 [0] = 100 后: $numbers"

# 添加元素（数组是固定大小的，+= 实际是创建新数组）
$numbers += 6
Write-Host "添加元素 6 后: $numbers"

$numbers += 7, 8, 9
Write-Host "添加多个元素后: $numbers"

# 删除元素（通过重新赋值，排除要删除的元素）
$numbers = $numbers | Where-Object { $_ -ne 100 }
Write-Host "删除 100 后: $numbers"

# 删除指定位置的元素
$index = 2
$numbers = $numbers[0..($index - 1)] + $numbers[($index + 1)..($numbers.Length - 1)]
Write-Host "删除索引 2 的元素后: $numbers"

Write-Host ""
Write-Host "=============================="
Write-Host "  4. 数组遍历"
Write-Host "=============================="

$colors = @("红", "橙", "黄", "绿", "青", "蓝", "紫")

# 方式一：foreach
Write-Host "foreach 遍历:"
foreach ($color in $colors) {
    Write-Host "  $color"
}

# 方式二：for
Write-Host "for 遍历:"
for ($i = 0; $i -lt $colors.Length; $i++) {
    Write-Host "  [$i] $($colors[$i])"
}

# 方式三：ForEach-Object（管道）
Write-Host "ForEach-Object 遍历:"
$colors | ForEach-Object { Write-Host "  $_" }

# 方式四：foreach 方法（PowerShell 4.0+）
Write-Host "ForEach 方法遍历:"
$colors.ForEach({ Write-Host "  $_" })

Write-Host ""
Write-Host "=============================="
Write-Host "  5. 数组操作符"
Write-Host "=============================="

$arr = 1..10

# -contains / -notcontains
Write-Host "数组: $arr"
Write-Host "包含 5 吗? ($arr -contains 5): $($arr -contains 5)"
Write-Host "不包含 100 吗? ($arr -notcontains 100): $($arr -notcontains 100)"

# -in / -notin
Write-Host "5 在数组中吗? (5 -in $arr): $(5 -in $arr)"
Write-Host "100 不在数组中吗? (100 -notin $arr): $(100 -notin $arr)"

# 比较操作符（返回匹配的元素）
Write-Host ""
Write-Host "数组 -eq 5: $($arr -eq 5)"
Write-Host "数组 -ne 5: $($arr -ne 5)"
Write-Host "数组 -gt 7: $($arr -gt 7)"
Write-Host "数组 -lt 3: $($arr -lt 3)"

# 数组合并
$arr1 = 1, 2, 3
$arr2 = 4, 5, 6
$combined = $arr1 + $arr2
Write-Host ""
Write-Host "数组合并: $combined"

Write-Host ""
Write-Host "=============================="
Write-Host "  6. 数组常用方法"
Write-Host "=============================="

# 排序
$nums = 5, 2, 8, 1, 9, 3, 7, 4, 6, 0
Write-Host "原始数组: $nums"

# Sort-Object（管道方式，不改变原数组）
$sorted = $nums | Sort-Object
Write-Host "排序后 (升序): $sorted"

$descSorted = $nums | Sort-Object -Descending
Write-Host "排序后 (降序): $descSorted"

# 反转
$reversed = $nums[($nums.Length - 1)..0]
Write-Host "反转后: $reversed"

# 查找索引
$idx = [array]::IndexOf($nums, 8)
Write-Host "元素 8 的索引: $idx"

$lastIdx = [array]::LastIndexOf($nums, 3)
Write-Host "元素 3 最后出现的索引: $lastIdx"

# 克隆数组
$clone = $nums.Clone()
$clone[0] = 999
Write-Host "原数组: $nums"
Write-Host "克隆修改后: $clone"

Write-Host ""
Write-Host "=============================="
Write-Host "  7. 多维数组"
Write-Host "=============================="

# 二维数组（数组的数组）
$matrix = @(
    @(1, 2, 3),
    @(4, 5, 6),
    @(7, 8, 9)
)

Write-Host "3x3 矩阵:"
for ($i = 0; $i -lt $matrix.Length; $i++) {
    $row = $matrix[$i] -join " "
    Write-Host "  $row"
}

Write-Host "元素 [1][2] = $($matrix[1][2])"

# 真正的多维数组（.NET 方式）
$multi = New-Object 'int[,]' 2, 3
$multi[0, 0] = 1
$multi[0, 1] = 2
$multi[0, 2] = 3
$multi[1, 0] = 4
$multi[1, 1] = 5
$multi[1, 2] = 6

Write-Host ""
Write-Host ".NET 多维数组 [2,3]:"
for ($i = 0; $i -lt 2; $i++) {
    $row = for ($j = 0; $j -lt 3; $j++) { $multi[$i, $j] }
    Write-Host "  $($row -join ' ')"
}

Write-Host ""
Write-Host "=============================="
Write-Host "  8. 数组筛选与转换"
Write-Host "=============================="

$numbers = 1..20

# Where-Object 筛选
$evens = $numbers | Where-Object { $_ % 2 -eq 0 }
Write-Host "偶数: $evens"

$greaterThan10 = $numbers | Where-Object { $_ -gt 10 }
Write-Host "大于 10: $greaterThan10"

# ForEach-Object 转换
$squares = $numbers | ForEach-Object { $_ * $_ }
Write-Host "平方值: $squares"

# Select-Object 选择
$first5 = $numbers | Select-Object -First 5
$last3 = $numbers | Select-Object -Last 3
$unique = @(1, 2, 2, 3, 3, 3, 4, 5) | Select-Object -Unique
Write-Host "前 5 个: $first5"
Write-Host "后 3 个: $last3"
Write-Host "去重后: $unique"

Write-Host ""
Write-Host "=============================="
Write-Host "  9. ArrayList（动态数组）"
Write-Host "=============================="

# 普通数组是固定大小的，频繁增删建议用 ArrayList
$list = New-Object System.Collections.ArrayList
Write-Host "初始 ArrayList 容量: $($list.Capacity)"

# 添加元素
[void]$list.Add("苹果")
[void]$list.Add("香蕉")
[void]$list.Add("橙子")
Write-Host "添加后: $($list -join ', ')"

# 插入元素
$list.Insert(1, "葡萄")
Write-Host "在索引 1 插入葡萄后: $($list -join ', ')"

# 删除元素
$list.Remove("香蕉")
Write-Host "删除香蕉后: $($list -join ', ')"

$list.RemoveAt(0)
Write-Host "删除索引 0 后: $($list -join ', ')"

# 清空
$list.Clear()
Write-Host "清空后元素数: $($list.Count)"

Write-Host ""
Write-Host "=============================="
Write-Host "  10. 综合示例：冒泡排序"
Write-Host "=============================="

$arr = 5, 2, 9, 1, 5, 6, 3, 8, 7, 4
Write-Host "排序前: $arr"

$n = $arr.Length
for ($i = 0; $i -lt $n - 1; $i++) {
    for ($j = 0; $j -lt $n - 1 - $i; $j++) {
        if ($arr[$j] -gt $arr[$j + 1]) {
            $temp = $arr[$j]
            $arr[$j] = $arr[$j + 1]
            $arr[$j + 1] = $temp
        }
    }
}

Write-Host "排序后: $arr"

Write-Host ""
Write-Host "脚本执行完毕！"
