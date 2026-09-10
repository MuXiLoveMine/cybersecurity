# ============================================================
# 07_regex.ps1 - 正则表达式：-match、-replace、-split、Select-String
# 运行方式: powershell -ExecutionPolicy Bypass -File .\07_regex.ps1
# ============================================================

Write-Host "=============================="
Write-Host "  1. -match 基础匹配"
Write-Host "=============================="

$text = "Hello PowerShell 123 World"

# 基础匹配
Write-Host "文本: '$text'"
Write-Host "包含数字吗 (-match '\d'): $($text -match '\d')"
Write-Host "包含 'Power' 吗: $($text -match 'Power')"
Write-Host "以 'Hello' 开头吗: $($text -match '^Hello')"
Write-Host "以 'World' 结尾吗: $($text -match 'World$')"

# $Matches 自动变量
Write-Host "`n`$Matches 自动变量:"
if ($text -match 'PowerShell') {
    Write-Host "  匹配到: $($Matches[0])"
}

# 区分大小写匹配
$caseText = "Hello World"
Write-Host "`n区分大小写匹配:"
Write-Host "  -match 'world': $($caseText -match 'world')"
Write-Host "  -imatch 'world': $($caseText -imatch 'world')"
Write-Host "  -cmatch 'world': $($caseText -cmatch 'world')"
Write-Host "  -cmatch 'World': $($caseText -cmatch 'World')"

# -notmatch
Write-Host "`n-notmatch 不匹配:"
Write-Host "  'abc' -notmatch '\d': $($text -notmatch '\d')"

Write-Host ""
Write-Host "=============================="
Write-Host "  2. 捕获组"
Write-Host "=============================="

# 数字捕获组
$phone = "13812345678"
if ($phone -match "^(\d{3})(\d{4})(\d{4})$") {
    Write-Host "手机号: $phone"
    Write-Host "  前三位: $($Matches[1])"
    Write-Host "  中间四位: $($Matches[2])"
    Write-Host "  后四位: $($Matches[3])"
}

# 命名捕获组
$email = "zhangsan@example.com"
if ($email -match "^(?<user>\w+)@(?<domain>\w+\.\w+)$") {
    Write-Host "`n邮箱: $email"
    Write-Host "  用户名: $($Matches['user'])"
    Write-Host "  域名: $($Matches['domain'])"
}

# 日期解析
$dateStr = "2024-01-15"
if ($dateStr -match "(\d{4})-(\d{2})-(\d{2})") {
    Write-Host "`n日期: $dateStr"
    Write-Host "  年: $($Matches[1])"
    Write-Host "  月: $($Matches[2])"
    Write-Host "  日: $($Matches[3])"
}

Write-Host ""
Write-Host "=============================="
Write-Host "  3. -replace 替换"
Write-Host "=============================="

# 简单替换
$text = "Hello World"
$result = $text -replace "World", "PowerShell"
Write-Host "原始: $text"
Write-Host "替换: $result"

# 数字替换
$text2 = "abc123def456ghi789"
$result2 = $text2 -replace "\d", "*"
Write-Host "`n原始: $text2"
Write-Host "替换数字为 *: $result2"

# 捕获组替换
$dateStr2 = "2024-01-15"
$dateCn = $dateStr2 -replace "(\d{4})-(\d{2})-(\d{2})", '$1年$2月$3日'
Write-Host "`n日期: $dateStr2"
Write-Host "替换后: $dateCn"

# 交换位置
$name = "张三"
$swapped = "Zhang San" -replace "(\w+) (\w+)", '$2, $1'
Write-Host "`n英文名: Zhang San"
Write-Host "交换姓和名: $swapped"

# 移除空白
$spaced = "  Hello   World  "
$trimmed = $spaced -replace "^\s+|\s+$", ""
Write-Host "`n原始: '$spaced'"
Write-Host "去除两端空白: '$trimmed'"

# 多个空格变一个
$multiSpace = "Hello    World     !"
$singleSpace = $multiSpace -replace "\s+", " "
Write-Host "`n原始: '$multiSpace'"
Write-Host "合并空白: '$singleSpace'"

# 脚本块替换（PowerShell Core 7+ 支持更好，Windows PowerShell 有限支持）
$numText = "a1b2c3"
$result3 = $numText -replace "\d", { ([int]$_.Value * 2).ToString() }
Write-Host "`n原始: $numText"
Write-Host "数字乘 2: $result3"

Write-Host ""
Write-Host "=============================="
Write-Host "  4. -split 分割"
Write-Host "=============================="

# 按空白分割
$text = "one  two   three    four"
$words = $text -split "\s+"
Write-Host "原始: '$text'"
Write-Host "按空白分割: $($words -join ', ')"

# 按标点分割
$csv = "apple,banana;orange|grape"
$fruits = $csv -split "[,;|]"
Write-Host "`n原始: $csv"
Write-Host "按多种标点分割: $($fruits -join ', ')"

# 限制分割次数
$longStr = "a,b,c,d,e,f,g"
$limited = $longStr -split ",", 4
Write-Host "`n原始: $longStr"
Write-Host "分割为 4 段: $($limited -join ' | ')"

# 区分大小写分割
$caseStr = "AppleBananaCherry"
$caseSplit = $caseStr -csplit "[A-Z]"
Write-Host "`n原始: $caseStr"
Write-Host "按大写字母分割 (-csplit): $($caseSplit -join ', ')"

Write-Host ""
Write-Host "=============================="
Write-Host "  5. Select-String"
Write-Host "=============================="

# 在字符串数组中搜索
$lines = @(
    "2024-01-15 10:30:00 INFO 启动服务",
    "2024-01-15 10:30:05 WARN 内存使用率过高",
    "2024-01-15 10:30:10 ERROR 数据库连接失败",
    "2024-01-15 10:30:15 INFO 重试连接",
    "2024-01-15 10:30:20 ERROR 连接超时",
    "2024-01-15 10:30:25 INFO 服务恢复正常"
)

Write-Host "搜索包含 ERROR 的行:"
$errors = $lines | Select-String -Pattern "ERROR"
$errors | ForEach-Object { Write-Host "  $($_.Line)" }

# 显示匹配上下文
Write-Host "`n搜索 ERROR 并显示上下文（前 1 行，后 1 行）:"
$ctx = $lines | Select-String -Pattern "ERROR" -Context 1, 1
$ctx | ForEach-Object {
    Write-Host "  上下文前: $($_.Context.PreContext)"
    Write-Host "  匹配行: $($_.Line)"
    Write-Host "  上下文后: $($_.Context.PostContext)"
    Write-Host "  ---"
}

# 简单匹配
Write-Host "`n匹配数字（简单模式）:"
$lines | Select-String -Pattern "\d{2}:\d{2}:\d{2}" | ForEach-Object {
    Write-Host "  $($_.Line)"
}

Write-Host ""
Write-Host "=============================="
Write-Host "  6. 常用正则模式"
Write-Host "=============================="

$patterns = @(
    @{ Name = "邮箱"; Pattern = "^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$"; Test = "test@example.com" },
    @{ Name = "手机号"; Pattern = "^1[3-9]\d{9}$"; Test = "13812345678" },
    @{ Name = "IPv4"; Pattern = "^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"; Test = "192.168.1.1" },
    @{ Name = "身份证号"; Pattern = "^\d{17}[\dXx]$"; Test = "110101199001011234" },
    @{ Name = "URL"; Pattern = "^https?://"; Test = "https://www.example.com" },
    @{ Name = "中文字符"; Pattern = "^[\u4e00-\u9fa5]+$"; Test = "你好世界" },
    @{ Name = "正整数"; Pattern = "^[1-9]\d*$"; Test = "12345" },
    @{ Name = "日期 YYYY-MM-DD"; Pattern = "^\d{4}-\d{2}-\d{2}$"; Test = "2024-01-15" }
)

foreach ($p in $patterns) {
    $isMatch = $p.Test -match $p.Pattern
    Write-Host "  $($p.Name): '$($p.Test)' -> $isMatch"
}

Write-Host ""
Write-Host "=============================="
Write-Host "  7. 正则字符类与量词"
Write-Host "=============================="

Write-Host "字符类:"
Write-Host "  \d 数字: 'abc123' -match '\d+' = $('abc123' -match '\d+')"
Write-Host "  \D 非数字: 'abc123' -match '\D+' = $('abc123' -match '\D+')"
Write-Host "  \w 单词字符: 'hello@123' -match '\w+' = $($('hello@123' -match '\w+'); $Matches[0])"
Write-Host "  \W 非单词字符: 'hello@123' -match '\W+' = $($('hello@123' -match '\W+'); $Matches[0])"
Write-Host "  \s 空白字符: 'a b c' -match '\s' = $('a b c' -match '\s')"
Write-Host "  .  任意字符: 'abc' -match 'a.c' = $('abc' -match 'a.c')"

Write-Host "`n量词:"
Write-Host "  * 零或多次: 'aaa' -match 'ba*' = $('aaa' -match 'a*')"
Write-Host "  + 一或多次: 'aaa' -match 'a+' = $('aaa' -match 'a+')"
Write-Host "  ? 零或一次: 'color' -match 'colou?r' = $('color' -match 'colou?r')"
Write-Host "  {n} 恰好 n 次: 'aaaaa' -match 'a{3}' = $('aaaaa' -match 'a{3}')"
Write-Host "  {n,m} n 到 m 次: 'aaaaa' -match 'a{2,4}' = $('aaaaa' -match 'a{2,4}')"

Write-Host "`n位置:"
Write-Host "  ^ 行首: 'hello' -match '^hel' = $('hello' -match '^hel')"
Write-Host "  $ 行尾: 'hello' -match 'llo$' = $('hello' -match 'llo$')"
Write-Host "  \b 单词边界: 'hello world' -match '\bworld\b' = $('hello world' -match '\bworld\b')"

Write-Host ""
Write-Host "=============================="
Write-Host "  8. 贪婪与非贪婪"
Write-Host "=============================="

$html = "<div>Hello</div><div>World</div>"

# 贪婪匹配（默认）
$html -match "<div>.*</div>"
Write-Host "原始 HTML: $html"
Write-Host "贪婪匹配 <div>.*</div>: $($Matches[0])"

# 非贪婪匹配（加 ?）
$html -match "<div>.*?</div>"
Write-Host "非贪婪匹配 <div>.*?</div>: $($Matches[0])"

# 提取所有 div 内容
$divContents = [regex]::Matches($html, '<div>(.*?)</div>') | ForEach-Object { $_.Groups[1].Value }
Write-Host "所有 div 内容: $($divContents -join ', ')"

Write-Host ""
Write-Host "=============================="
Write-Host "  9. [regex] 类高级用法"
Write-Host "=============================="

# [regex]::Match
$text = "价格: 99.99 元"
$match = [regex]::Match($text, "\d+\.\d+")
Write-Host "文本: $text"
Write-Host "匹配到价格: $($match.Value)"
Write-Host "匹配位置: $($match.Index)"

# [regex]::Matches（所有匹配）
$text2 = "电话: 13812345678, 备用: 13987654321"
$matches2 = [regex]::Matches($text2, "1[3-9]\d{9}")
Write-Host "`n文本: $text2"
Write-Host "所有手机号:"
$matches2 | ForEach-Object { Write-Host "  $($_.Value)" }

# [regex]::Replace
$text3 = "a1b2c3d4"
$replaced = [regex]::Replace($text3, "\d", { param($m) ([int]$m.Value * 2).ToString() })
Write-Host "`n文本: $text3"
Write-Host "数字乘 2: $replaced"

# [regex]::Split
$text4 = "2024-01-15"
$parts = [regex]::Split($text4, "-")
Write-Host "`n日期: $text4"
Write-Host "分割: $($parts -join ', ')"

# 预编译正则
$ipRegex = [regex]::new("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
Write-Host "`n预编译正则验证 IP:"
Write-Host "  192.168.1.1: $($ipRegex.IsMatch('192.168.1.1'))"
Write-Host "  abc: $($ipRegex.IsMatch('abc'))"

Write-Host ""
Write-Host "=============================="
Write-Host "  10. 综合示例：日志分析"
Write-Host "=============================="

$logLines = @(
    "192.168.1.100 - - [15/Jan/2024:10:30:00 +0800] 'GET /index.html HTTP/1.1' 200 1234",
    "10.0.0.5 - - [15/Jan/2024:10:30:05 +0800] 'POST /api/login HTTP/1.1' 401 567",
    "192.168.1.100 - - [15/Jan/2024:10:30:10 +0800] 'GET /admin HTTP/1.1' 302 0",
    "172.16.0.20 - - [15/Jan/2024:10:30:15 +0800] 'GET /css/style.css HTTP/1.1' 200 8900",
    "10.0.0.5 - - [15/Jan/2024:10:30:20 +0800] 'POST /api/login HTTP/1.1' 200 1200",
    "192.168.1.50 - - [15/Jan/2024:10:30:25 +0800] 'GET /favicon.ico HTTP/1.1' 404 200"
)

# 提取所有 IP
$ips = $logLines | ForEach-Object {
    if ($_ -match "^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}") {
        $Matches[0]
    }
}
Write-Host "日志中的所有 IP: $($ips -join ', ')"

# 统计状态码
$statusCodes = $logLines | ForEach-Object {
    if ($_ -match "HTTP/1\.1' (\d{3})") {
        $Matches[1]
    }
} | Group-Object | ForEach-Object {
    "{0}: {1} 次" -f $_.Name, $_.Count
}
Write-Host "`n状态码统计:"
$statusCodes | ForEach-Object { Write-Host "  $_" }

# 找出 4xx 错误
Write-Host "`n4xx 错误请求:"
$logLines | Select-String -Pattern "HTTP/1\.1' 4\d{2}" | ForEach-Object {
    Write-Host "  $($_.Line)"
}

Write-Host ""
Write-Host "脚本执行完毕！"
