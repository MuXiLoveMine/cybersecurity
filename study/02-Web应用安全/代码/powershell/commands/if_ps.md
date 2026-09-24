# if_ps

> **分类**：条件与循环
> **说明**：条件判断和循环语句

---

## 语法

```powershell
if (condition) { ... } elseif (cond) { ... } else { ... }
```

## 比较运算符

-eq 等于 / -ne 不等于 / -gt 大于 / -lt 小于 / -ge 大于等于 / -le 小于等于\n-like 通配符匹配 / -match 正则匹配 / -in 包含于 / -contains 包含

## 逻辑运算符

-and / -or / -not / !

## 示例代码

```powershell
# if/elseif/else
$age = 18
if ($age -ge 18) {
    Write-Host "成年"
} elseif ($age -ge 6) {
    Write-Host "少年"
} else {
    Write-Host "儿童"
}

# 比较运算符
if ($a -eq $b) { "相等" }
if ($a -ne $b) { "不等" }
if ($a -gt 10) { "大于10" }
if ($a -lt 10) { "小于10" }

# 字符串匹配
if ($name -like "A*") { "以A开头" }
if ($email -match "^\w+@\w+\.\w+$") { "邮箱格式" }

# 包含判断
if ($fruit -in "apple","banana","cherry") { "是水果" }
if ($fruits -contains "apple") { "包含苹果" }

# 逻辑运算
if ($age -gt 18 -and $loggedIn) { "成年且已登录" }
if ($isAdmin -or $isModerator) { "有权限" }
if (-not $error) { "没有错误" }

# switch
$day = "Monday"
switch ($day) {
    "Monday"    { "星期一" }
    "Tuesday"   { "星期二" }
    default     { "其他" }
}

# for 循环
for ($i = 0; $i -lt 5; $i++) {
    Write-Host $i
}

# foreach 循环
$fruits | ForEach-Object {
    Write-Host $_
}

foreach ($fruit in $fruits) {
    Write-Host $fruit
}

# while 循环
$i = 0
while ($i -lt 5) {
    Write-Host $i
    $i++
}

# do...while
$i = 0
do {
    Write-Host $i
    $i++
} while ($i -lt 5)

# break / continue
for ($i = 0; $i -lt 10; $i++) {
    if ($i -eq 3) { continue }
    if ($i -eq 7) { break }
    Write-Host $i
}
```
