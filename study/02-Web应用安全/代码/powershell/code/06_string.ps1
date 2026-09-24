# ============================================================
# 06_string.ps1 - 字符串操作：拼接、插值、格式化、查找、分割、替换
# 运行方式: powershell -ExecutionPolicy Bypass -File .\06_string.ps1
# ============================================================

Write-Host "=============================="
Write-Host "  1. 字符串定义"
Write-Host "=============================="

# 单引号字符串：不解析变量和转义字符
$single = 'Hello World'
Write-Host "单引号: $single"

$singleVar = '变量 $name 不会被解析'
Write-Host $singleVar

# 双引号字符串：解析变量和转义字符
$name = "PowerShell"
$double = "Hello, $name!"
Write-Host "双引号: $double"

# 转义字符（使用反引号 `）
$escaped = "第一行`n第二行`t制表符"
Write-Host "转义字符:"
Write-Host $escaped

# Here-String（多行字符串）
$hereStr = @"
这是一个多行字符串
可以包含换行
也可以解析变量: $name
非常方便
"@
Write-Host "`nHere-String:"
Write-Host $hereStr

# 单引号 Here-String（不解析变量）
$hereSingle = @'
这是单引号 Here-String
变量 $name 不会被解析
'@
Write-Host "单引号 Here-String:"
Write-Host $hereSingle

Write-Host ""
Write-Host "=============================="
Write-Host "  2. 字符串拼接"
Write-Host "=============================="

$first = "张"
$last = "三"

# 方式一：+ 号拼接
$fullName1 = $first + $last
Write-Host "+ 号拼接: $fullName1"

# 方式二：字符串插值
$fullName2 = "$first$last"
Write-Host "字符串插值: $fullName2"

# 方式三：-join 操作符
$parts = @("Hello", "PowerShell", "World")
$joined = $parts -join " "
Write-Host "-join 拼接: $joined"

# 方式四：String.Format / -f 操作符
$formatted = "姓名: {0}, 年龄: {1}, 城市: {2}" -f "李四", 25, "上海"
Write-Host "-f 格式化: $formatted"

# 方式五：String.Concat
$concat = [string]::Concat("A", "B", "C")
Write-Host "Concat 方法: $concat"

Write-Host ""
Write-Host "=============================="
Write-Host "  3. 字符串插值高级用法"
Write-Host "=============================="

$person = @{
    Name = "王五"
    Age = 30
}

# 访问对象属性需要用 $()
$info = "姓名: $($person.Name), 年龄: $($person.Age)"
Write-Host "对象属性插值: $info"

# 表达式计算
$math = "1 + 1 = $(1 + 1)"
Write-Host "表达式插值: $math"

# 方法调用
$str = "hello"
$method = "转大写: $($str.ToUpper())"
Write-Host "方法插值: $method"

# 数组索引
$colors = @("红", "绿", "蓝")
$arrStr = "第二个颜色: $($colors[1])"
Write-Host "数组索引插值: $arrStr"

Write-Host ""
Write-Host "=============================="
Write-Host "  4. 字符串查找"
Write-Host "=============================="

$text = "Hello PowerShell World"

# -like 通配符匹配（不区分大小写）
Write-Host "文本: '$text'"
Write-Host "包含 'Power' 吗 (-like *Power*): $($text -like '*Power*')"
Write-Host "以 'Hello' 开头吗 (-like Hello*): $($text -like 'Hello*')"
Write-Host "以 'World' 结尾吗 (-like *World): $($text -like '*World')"

# -clike 区分大小写
Write-Host "区分大小写包含 'power' 吗: $($text -clike '*power*')"

# -match 正则匹配
Write-Host "`n-match 正则匹配 'Power': $($text -match 'Power')"

# IndexOf 查找位置
$pos = $text.IndexOf("Power")
Write-Host "'Power' 的位置 (IndexOf): $pos"

$lastPos = $text.LastIndexOf("o")
Write-Host "'o' 最后出现的位置: $lastPos"

# StartsWith / EndsWith
Write-Host "以 'Hello' 开头: $($text.StartsWith('Hello'))"
Write-Host "以 'world' 结尾 (区分大小写): $($text.EndsWith('world'))"
Write-Host "以 'World' 结尾: $($text.EndsWith('World'))"

# Contains 方法（区分大小写）
Write-Host "包含 'Shell' (方法): $($text.Contains('Shell'))"

Write-Host ""
Write-Host "=============================="
Write-Host "  5. 字符串替换"
Write-Host "=============================="

$text = "Hello World"

# -replace 运算符（支持正则，不区分大小写）
$replaced = $text -replace "World", "PowerShell"
Write-Host "原始: $text"
Write-Host "替换后: $replaced"

# 正则替换
$numStr = "abc123def456ghi789"
$numReplaced = $numStr -replace "\d+", "#"
Write-Host "`n原始: $numStr"
Write-Host "数字替换为 #: $numReplaced"

# 捕获组替换
$dateStr = "2024-01-15"
$dateCn = $dateStr -replace "(\d{4})-(\d{2})-(\d{2})", '$1年$2月$3日'
Write-Host "`n日期原始: $dateStr"
Write-Host "替换后: $dateCn"

# Replace 方法（不支持正则，区分大小写）
$simple = "Hello World Hello"
$simpleReplaced = $simple.Replace("Hello", "Hi")
Write-Host "`n原始: $simple"
Write-Host "Replace 方法替换: $simpleReplaced"

# 区分大小写替换 -creplace
$caseStr = "Hello HELLO hello"
$caseReplaced = $caseStr -creplace "hello", "Hi"
Write-Host "`n原始: $caseStr"
Write-Host "区分大小写替换 (-creplace): $caseReplaced"

Write-Host ""
Write-Host "=============================="
Write-Host "  6. 字符串分割"
Write-Host "=============================="

# 简单分割
$csv = "苹果,香蕉,橙子,葡萄,西瓜"
$fruits = $csv -split ","
Write-Host "原始: $csv"
Write-Host "分割后:"
$fruits | ForEach-Object { Write-Host "  $_" }

# 正则分割
$spaceStr = "a  b   c    d"
$spaceArr = $spaceStr -split "\s+"
Write-Host "`n原始: '$spaceStr'"
Write-Host "正则分割 (\s+): $($spaceArr -join ', ')"

# 限制分割次数
$longStr = "a,b,c,d,e,f"
$limited = $longStr -split ",", 3
Write-Host "`n原始: $longStr"
Write-Host "分割为 3 段: $($limited -join ' | ')"

# Split 方法
$methodStr = "one;two;three"
$methodArr = $methodStr.Split(";")
Write-Host "`nSplit 方法: $($methodArr -join ', ')"

Write-Host ""
Write-Host "=============================="
Write-Host "  7. 大小写转换"
Write-Host "=============================="

$text = "Hello PowerShell"

Write-Host "原始: $text"
Write-Host "全部大写: $($text.ToUpper())"
Write-Host "全部小写: $($text.ToLower())"

# 首字母大写（需要手动实现）
$textLower = $text.ToLower()
$capitalized = $textLower[0].ToString().ToUpper() + $textLower.Substring(1)
Write-Host "首字母大写: $capitalized"

Write-Host ""
Write-Host "=============================="
Write-Host "  8. 字符串截取与填充"
Write-Host "=============================="

$text = "Hello PowerShell World"

Write-Host "原始: '$text'"
Write-Host "长度: $($text.Length)"

# Substring 截取
Write-Host "前 5 个字符: '$($text.Substring(0, 5))'"
Write-Host "从第 6 个开始: '$($text.Substring(6))'"
Write-Host "从第 6 个开始取 10 个: '$($text.Substring(6, 10))'"

# 填充
$num = "42"
Write-Host "左侧填充到 5 位: '$($num.PadLeft(5, '0'))'"
Write-Host "右侧填充到 10 位: '$($num.PadRight(10, '.'))'"

# 去除空白
$spaced = "   Hello World   "
Write-Host "`n带空格: '$spaced'"
Write-Host "Trim 两端: '$($spaced.Trim())'"
Write-Host "TrimStart: '$($spaced.TrimStart())'"
Write-Host "TrimEnd: '$($spaced.TrimEnd())'"

Write-Host ""
Write-Host "=============================="
Write-Host "  9. 字符串比较"
Write-Host "=============================="

$str1 = "Hello"
$str2 = "hello"
$str3 = "Hello"

# -eq / -ne（不区分大小写）
Write-Host "'$str1' -eq '$str2': $($str1 -eq $str2)"
Write-Host "'$str1' -ceq '$str2': $($str1 -ceq $str2)"
Write-Host "'$str1' -ieq '$str2': $($str1 -ieq $str2)"

# CompareTo
$cmp = $str1.CompareTo($str3)
Write-Host "'$str1'.CompareTo('$str3'): $cmp (0 表示相等)"

# 字符串方法 Equals（区分大小写）
Write-Host "'$str1'.Equals('$str2'): $($str1.Equals($str2))"
Write-Host "'$str1'.Equals('$str3'): $($str1.Equals($str3))"

# 不区分大小写比较
Write-Host "不区分大小写比较: $($str1.Equals($str2, [System.StringComparison]::OrdinalIgnoreCase))"

Write-Host ""
Write-Host "=============================="
Write-Host "  10. 字符串其他操作"
Write-Host "=============================="

# 字符串重复
$stars = "*" * 20
Write-Host "字符串重复 (* * 20):"
Write-Host $stars

# 判断空字符串
$emptyStr = ""
$nullStr = $null
$whiteSpace = "   "

Write-Host "'$emptyStr' 是空字符串吗: $([string]::IsNullOrEmpty($emptyStr))"
Write-Host "`$null 是空字符串吗: $([string]::IsNullOrEmpty($nullStr))"
Write-Host "'$whiteSpace' 是空白字符串吗: $([string]::IsNullOrWhiteSpace($whiteSpace))"

# 插入字符串
$text = "Hello World"
$inserted = $text.Insert(5, ", PowerShell")
Write-Host "`n插入字符串: $inserted"

# 删除字符串
$removed = $text.Remove(5)
Write-Host "删除索引 5 之后: $removed"

$removed2 = $text.Remove(0, 6)
Write-Host "删除前 6 个字符: $removed2"

# 字符数组
$chars = "PowerShell".ToCharArray()
Write-Host "`n字符数组: $($chars -join ', ')"

# 反转字符串
$charArray = "Hello".ToCharArray()
[array]::Reverse($charArray)
$reversed = -join $charArray
Write-Host "反转 'Hello': $reversed"

Write-Host ""
Write-Host "脚本执行完毕！"
