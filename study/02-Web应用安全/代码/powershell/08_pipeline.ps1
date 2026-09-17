# ============================================================
# 08_pipeline.ps1 - 管道操作：Where-Object、ForEach-Object、Sort-Object 等
# 运行方式: powershell -ExecutionPolicy Bypass -File .\08_pipeline.ps1
# ============================================================

Write-Host "=============================="
Write-Host "  1. 管道基础"
Write-Host "=============================="

# PowerShell 管道传递的是对象，不是纯文本
Write-Host "简单管道示例：1..5 | ForEach-Object { $_ * 2 }"
1..5 | ForEach-Object { $_ * 2 } | ForEach-Object { Write-Host "  $_" }

# 管道链式调用
Write-Host "`n链式调用：获取数字 -> 筛选偶数 -> 平方 -> 求和"
$sum = 1..10 |
    Where-Object { $_ % 2 -eq 0 } |
    ForEach-Object { $_ * $_ } |
    Measure-Object -Sum |
    Select-Object -ExpandProperty Sum
Write-Host "  1-10 偶数的平方和: $sum"

Write-Host ""
Write-Host "=============================="
Write-Host "  2. Where-Object（筛选）"
Write-Host "=============================="

$numbers = 1..20

# 脚本块语法
$evens = $numbers | Where-Object { $_ % 2 -eq 0 }
Write-Host "1-20 的偶数: $evens"

# 简写语法（PowerShell 3.0+）
$greaterThan15 = $numbers | Where-Object { $_ -gt 15 }
Write-Host "大于 15 的数: $greaterThan15"

# 多条件筛选
$filtered = $numbers | Where-Object { $_ -gt 5 -and $_ -lt 15 -and $_ % 2 -eq 0 }
Write-Host "5-15 之间的偶数: $filtered"

# 使用属性筛选（示例：获取当前进程信息）
Write-Host "`n获取当前进程中占用内存大于 10MB 的进程（前 5 个）:"
Get-Process |
    Where-Object { $_.WorkingSet -gt 10MB } |
    Sort-Object WorkingSet -Descending |
    Select-Object -First 5 -Property ProcessName, Id, @{
        Name = "MemoryMB"
        Expression = { [math]::Round($_.WorkingSet / 1MB, 2) }
    } |
    Format-Table -AutoSize |
    Out-String |
    ForEach-Object { Write-Host "  $_" }

Write-Host ""
Write-Host "=============================="
Write-Host "  3. ForEach-Object（遍历处理）"
Write-Host "=============================="

# 基本用法
Write-Host "1-5 的平方:"
1..5 | ForEach-Object {
    $square = $_ * $_
    Write-Host "  $_^2 = $square"
}

# 使用 -Begin / -Process / -End
Write-Host "`n使用 Begin/Process/End 计算 1-10 之和:"
$total = 1..10 | ForEach-Object -Begin {
    $sum = 0
    Write-Host "  Begin: 初始化 sum = 0"
} -Process {
    $sum += $_
} -End {
    Write-Host "  End: 返回 sum = $sum"
    $sum
}
Write-Host "  最终结果: $total"

# 多重管道（对象在管道中流动）
Write-Host "`n数字 -> 平方 -> 转字符串 -> 拼接前缀:"
1..5 |
    ForEach-Object { $_ * $_ } |
    ForEach-Object { "num_$_" } |
    ForEach-Object { Write-Host "  $_" }

# 使用 $PSItem（$_ 的别名）
Write-Host "`n使用 `$PSItem:"
"a", "b", "c" | ForEach-Object { Write-Host "  $PSItem" }

Write-Host ""
Write-Host "=============================="
Write-Host "  4. Sort-Object（排序）"
Write-Host "=============================="

$numbers = 5, 2, 9, 1, 7, 3, 8, 4, 6, 0

# 默认升序
$sorted = $numbers | Sort-Object
Write-Host "原始: $numbers"
Write-Host "升序: $sorted"

# 降序
$desc = $numbers | Sort-Object -Descending
Write-Host "降序: $desc"

# 字符串排序
$words = @("banana", "apple", "cherry", "date", "elderberry")
$sortedWords = $words | Sort-Object
Write-Host "`n单词排序: $($sortedWords -join ', ')"

# 按长度排序
$byLength = $words | Sort-Object { $_.Length }
Write-Host "按长度排序: $($byLength -join ', ')"

# 多字段排序（使用自定义对象示例）
$people = @(
    [pscustomobject]@{ Name = "张三"; Age = 25; City = "北京" }
    [pscustomobject]@{ Name = "李四"; Age = 30; City = "上海" }
    [pscustomobject]@{ Name = "王五"; Age = 25; City = "广州" }
    [pscustomobject]@{ Name = "赵六"; Age = 28; City = "北京" }
    [pscustomobject]@{ Name = "钱七"; Age = 30; City = "北京" }
)

Write-Host "`n按年龄升序，再按城市排序:"
$people | Sort-Object Age, City | ForEach-Object {
    Write-Host "  $($_.Name), $($_.Age)岁, $($_.City)"
}

# 唯一值
$duplicates = 1, 2, 2, 3, 3, 3, 4, 5, 5
$unique = $duplicates | Sort-Object -Unique
Write-Host "`n原始: $duplicates"
Write-Host "去重排序: $unique"

Write-Host ""
Write-Host "=============================="
Write-Host "  5. Select-Object（选择）"
Write-Host "=============================="

# 选择属性（使用进程示例）
Write-Host "选择进程的特定属性（前 3 个）:"
Get-Process |
    Select-Object -First 3 -Property ProcessName, Id, CPU |
    Format-Table -AutoSize |
    Out-String |
    ForEach-Object { Write-Host "  $_" }

# 选择前 N 个
$top5 = 1..20 | Select-Object -First 5
Write-Host "前 5 个: $top5"

# 跳过前 N 个
$skip5 = 1..20 | Select-Object -Skip 5 -First 5
Write-Host "跳过 5 个，取接下来 5 个: $skip5"

# 最后 N 个
$last5 = 1..20 | Select-Object -Last 5
Write-Host "最后 5 个: $last5"

# 唯一值
$uniqueItems = @(1, 2, 2, 3, 3, 3) | Select-Object -Unique
Write-Host "唯一值: $uniqueItems"

# 计算属性
Write-Host "`n计算属性（数字及其平方、立方）:"
1..5 |
    Select-Object `
        @{ Name = "数字"; Expression = { $_ } },
        @{ Name = "平方"; Expression = { $_ * $_ } },
        @{ Name = "立方"; Expression = { $_ * $_ * $_ } } |
    Format-Table -AutoSize |
    Out-String |
    ForEach-Object { Write-Host "  $_" }

# 展开属性
$procs = Get-Process | Select-Object -First 3
Write-Host "`n展开属性（ExpandProperty）:"
$procNames = $procs | Select-Object -ExpandProperty ProcessName
Write-Host "  进程名数组: $($procNames -join ', ')"

Write-Host ""
Write-Host "=============================="
Write-Host "  6. Group-Object（分组）"
Write-Host "=============================="

# 按奇偶分组
$groups = 1..10 | Group-Object { $_ % 2 }
Write-Host "1-10 按奇偶分组:"
$groups | ForEach-Object {
    $label = if ($_.Name -eq "0") { "偶数" } else { "奇数" }
    Write-Host "  $label ($($_.Count) 个): $($_.Group -join ', ')"
}

# 按长度分组单词
$words = @("cat", "dog", "bird", "elephant", "fish", "ant", "tiger")
$lenGroups = $words | Group-Object { $_.Length }
Write-Host "`n单词按长度分组:"
$lenGroups | Sort-Object Name | ForEach-Object {
    Write-Host "  $($_.Name) 个字母 ($($_.Count) 个): $($_.Group -join ', ')"
}

# 按属性分组（自定义对象）
$people = @(
    [pscustomobject]@{ Name = "张三"; Department = "技术部" },
    [pscustomobject]@{ Name = "李四"; Department = "市场部" },
    [pscustomobject]@{ Name = "王五"; Department = "技术部" },
    [pscustomobject]@{ Name = "赵六"; Department = "人事部" },
    [pscustomobject]@{ Name = "钱七"; Department = "市场部" },
    [pscustomobject]@{ Name = "孙八"; Department = "技术部" }
)

Write-Host "`n员工按部门分组:"
$people | Group-Object Department | ForEach-Object {
    Write-Host "  $($_.Name): $($_.Count) 人 - $($_.Group.Name -join ', ')"
}

# 按扩展名分组文件（当前目录）
Write-Host "`n当前目录文件按扩展名分组:"
Get-ChildItem -Path $PSScriptRoot -File |
    Group-Object Extension |
    Sort-Object Count -Descending |
    ForEach-Object {
        Write-Host "  $($_.Name): $($_.Count) 个文件"
    }

Write-Host ""
Write-Host "=============================="
Write-Host "  7. Measure-Object（统计）"
Write-Host "=============================="

$numbers = 1..10

# 计数
$count = $numbers | Measure-Object | Select-Object -ExpandProperty Count
Write-Host "1-10 的数量: $count"

# 求和
$sum = $numbers | Measure-Object -Sum | Select-Object -ExpandProperty Sum
Write-Host "1-10 的和: $sum"

# 平均值
$avg = $numbers | Measure-Object -Average | Select-Object -ExpandProperty Average
Write-Host "1-10 的平均值: $avg"

# 最大值和最小值
$max = $numbers | Measure-Object -Maximum | Select-Object -ExpandProperty Maximum
$min = $numbers | Measure-Object -Minimum | Select-Object -ExpandProperty Minimum
Write-Host "1-10 的最大值: $max, 最小值: $min"

# 全部统计
$stats = $numbers | Measure-Object -Sum -Average -Maximum -Minimum
Write-Host "`n全部统计信息:"
Write-Host "  数量: $($stats.Count)"
Write-Host "  和: $($stats.Sum)"
Write-Host "  平均值: $($stats.Average)"
Write-Host "  最大值: $($stats.Maximum)"
Write-Host "  最小值: $($stats.Minimum)"

# 统计文本行数
$text = @"
第一行
第二行
第三行
第四行
第五行
"@
$lineCount = ($text -split "`n") | Measure-Object -Line | Select-Object -ExpandProperty Lines
Write-Host "`n文本行数: $lineCount"

# 统计字符数和单词数
$sampleText = "Hello PowerShell World"
$charCount = ($sampleText.ToCharArray() | Measure-Object).Count
$wordCount = ($sampleText -split "\s+" | Measure-Object).Count
Write-Host "字符数: $charCount, 单词数: $wordCount"

Write-Host ""
Write-Host "=============================="
Write-Host "  8. 管道对象传递"
Write-Host "=============================="

# 验证管道中传递的是对象
Write-Host "管道中传递对象的属性访问:"
1..3 | ForEach-Object {
    [pscustomobject]@{ Name = "项目$_"; Value = $_ * 10 }
} | ForEach-Object {
    Write-Host "  对象: Name=$($_.Name), Value=$($_.Value)"
}

# 管道绑定参数（ByValue 和 ByPropertyName）
function Get-Double {
    param(
        [Parameter(ValueFromPipeline=$true)]
        [int]$Number
    )
    process {
        $Number * 2
    }
}

Write-Host "`nValueFromPipeline 管道绑定:"
1..5 | Get-Double | ForEach-Object { Write-Host "  $_" }

# ByPropertyName 绑定
function Get-Greeting {
    param(
        [Parameter(ValueFromPipelineByPropertyName=$true)]
        [string]$Name
    )
    process {
        "Hello, $Name!"
    }
}

Write-Host "`nValueFromPipelineByPropertyName 管道绑定:"
@(
    [pscustomobject]@{ Name = "张三" }
    [pscustomobject]@{ Name = "李四" }
    [pscustomobject]@{ Name = "王五" }
) | Get-Greeting | ForEach-Object { Write-Host "  $_" }

Write-Host ""
Write-Host "=============================="
Write-Host "  9. 其他常用管道命令"
Write-Host "=============================="

# Tee-Object：保存到文件同时继续传递
Write-Host "Tee-Object 示例（输出到变量同时显示）:"
$result = 1..5 | Tee-Object -Variable saved | ForEach-Object { $_ * $_ }
Write-Host "  原始数据: $saved"
Write-Host "  处理结果: $result"

# Compare-Object：比较两个对象
$arr1 = 1, 2, 3, 4, 5
$arr2 = 3, 4, 5, 6, 7
$diff = Compare-Object $arr1 $arr2
Write-Host "`n比较数组 $arr1 和 $arr2:"
$diff | ForEach-Object {
    $side = if ($_.SideIndicator -eq "<=") { "仅在左边" } else { "仅在右边" }
    Write-Host "  $($_.InputObject): $side"
}

# Format-Table / Format-List
Write-Host "`nFormat-Table 输出:"
Get-ChildItem -Path $PSScriptRoot -Filter "*.ps1" |
    Select-Object Name, Length |
    Format-Table -AutoSize |
    Out-String |
    ForEach-Object { Write-Host "  $_" }

Write-Host ""
Write-Host "=============================="
Write-Host "  10. 综合示例：文件分析"
Write-Host "=============================="

$scriptPath = $PSScriptRoot

Write-Host "分析目录: $scriptPath"
Write-Host ""

# 获取所有 .ps1 文件
$files = Get-ChildItem -Path $scriptPath -Filter "*.ps1" -File

# 统计信息
$totalSize = ($files | Measure-Object Length -Sum).Sum
$avgSize = ($files | Measure-Object Length -Average).Average
$maxFile = $files | Sort-Object Length -Descending | Select-Object -First 1
$minFile = $files | Sort-Object Length | Select-Object -First 1

Write-Host "文件统计:"
Write-Host "  文件总数: $($files.Count)"
Write-Host "  总大小: $([math]::Round($totalSize / 1KB, 2)) KB"
Write-Host "  平均大小: $([math]::Round($avgSize / 1KB, 2)) KB"
Write-Host "  最大文件: $($maxFile.Name) ($([math]::Round($maxFile.Length / 1KB, 2)) KB)"
Write-Host "  最小文件: $($minFile.Name) ($([math]::Round($minFile.Length / 1KB, 2)) KB)"

# 按大小排序显示
Write-Host "`n按大小排序的文件列表:"
$files | Sort-Object Length -Descending | ForEach-Object {
    $sizeKB = [math]::Round($_.Length / 1KB, 2)
    Write-Host "  $($_.Name.PadRight(20)) $sizeKB KB"
}

Write-Host ""
Write-Host "脚本执行完毕！"
