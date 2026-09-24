# PowerShell 基础

## 目录
- [PowerShell 简介](#powershell-简介)
- [使用场景](#使用场景)
- [环境与版本](#环境与版本)
- [基础概念](#基础概念)
- [变量与数据类型](#变量与数据类型)
- [运算符](#运算符)
- [控制流](#控制流)
- [函数](#函数)
- [数组（Array）](#数组array)
- [哈希表（Hashtable）](#哈希表hashtable)
- [字符串操作](#字符串操作)
- [管道（Pipeline）](#管道pipeline)
- [模块与快照](#模块与快照)
- [正则表达式](#正则表达式)
- [文件操作](#文件操作)
- [网络请求](#网络请求)
- [WMI/CIM](#wmicim)
- [远程管理](#远程管理)
- [执行策略与安全](#执行策略与安全)
- [PowerShell 在安全领域的应用](#powershell-在安全领域的应用)

---

## PowerShell 简介

### 什么是 PowerShell

PowerShell 是微软开发的**跨平台任务自动化和配置管理框架**，由命令行 Shell 和脚本语言两部分组成。

### 历史与版本

| 版本 | 发布时间 | 说明 |
|------|---------|------|
| PowerShell 1.0 | 2006年 | 最初版本，仅支持 Windows XP/2003/Vista |
| PowerShell 2.0 | 2009年 | 集成到 Windows 7 / Server 2008 R2，引入远程管理 |
| PowerShell 3.0 | 2012年 | 集成到 Windows 8 / Server 2012 |
| PowerShell 4.0 | 2013年 | 集成到 Windows 8.1 / Server 2012 R2 |
| PowerShell 5.0/5.1 | 2016年 | Windows PowerShell 最终版本，集成到 Windows 10 |
| PowerShell 6.0 | 2018年 | 首个跨平台版本（基于 .NET Core），改名为 PowerShell Core |
| PowerShell 7.0+ | 2020年至今 | 跨平台，基于 .NET 5/6/7/8，性能大幅提升 |

### 核心特点

1. **面向对象的脚本语言**
   - 不同于传统 Shell 传递纯文本，PowerShell 在管道中传递的是** .NET 对象**
   - 可以直接访问对象的属性和方法，无需文本解析

2. **基于 .NET 框架**
   - Windows PowerShell 5.1 基于 .NET Framework
   - PowerShell 7+ 基于 .NET Core / .NET 5+
   - 可以直接调用 .NET 类库中的所有类型

3. **Windows 原生支持**
   - Windows 7 及以上系统预装
   - 深度集成 Windows 管理接口（WMI/CIM、COM、ADSI 等）
   - 支持管理 Active Directory、Exchange、Azure 等微软产品

4. **一致的命令设计**
   - 所有 Cmdlet 遵循 **动词-名词（Verb-Noun）** 命名规范
   - 常用动词：Get、Set、New、Remove、Start、Stop、Invoke、Out 等

5. **强大的管道机制**
   - 支持对象在命令间流动
   - 支持管道输入、管道输出、管道绑定

---

## 使用场景

### 1. 系统管理
- 用户和组管理
- 服务管理（启动/停止/配置服务）
- 进程管理
- 磁盘和文件系统管理
- 注册表操作
- 事件日志管理

### 2. 自动化运维
- 批量服务器配置
- 定时任务脚本
- 部署自动化
- 监控告警脚本
- 报表生成

### 3. 渗透测试（红队）
- **PowerShell Empire**：后渗透利用框架
- **PowerSploit**：PowerShell 攻击工具集
- **Nishang**：渗透测试 PowerShell 框架
- 无文件攻击（Fileless Attack）
- 凭证窃取（Mimikatz 的 PowerShell 实现）
- 横向移动
- 权限提升

### 4. 蓝队分析与防御
- 日志收集与分析
- 恶意软件检测
- 系统基线检查
- 入侵检测
- 取证调查
- 安全审计

### 5. Windows 安全
- 组策略配置
- 防火墙规则管理
- Windows Defender 配置
- 安全基线合规检查
- 补丁管理

---

## 环境与版本

### Windows PowerShell 5.1

- Windows 自带版本，路径：`C:\Windows\System32\WindowsPowerShell\v1.0\`
- 基于 .NET Framework 4.5+
- 仅支持 Windows
- 启动命令：`powershell.exe`

### PowerShell 7+（跨平台）

- 需手动安装，路径通常在 `C:\Program Files\PowerShell\7\`
- 基于 .NET Core / .NET 5+
- 支持 Windows、Linux、macOS
- 启动命令：`pwsh.exe`（Windows）或 `pwsh`（Linux/macOS）

### 查看版本

```powershell
$PSVersionTable
```

---

## 基础概念

### Cmdlet

Cmdlet（读作 "command-let"）是 PowerShell 的原生命令，遵循 **Verb-Noun** 命名规范。

```powershell
# 常用 Cmdlet 示例
Get-Process          # 获取进程列表
Get-Service          # 获取服务列表
Get-ChildItem        # 获取目录内容（类似 dir/ls）
Get-Content          # 读取文件内容（类似 type/cat）
Set-Content          # 写入文件内容
New-Item             # 创建新文件或目录
Remove-Item          # 删除文件或目录
Copy-Item            # 复制文件或目录
Move-Item            # 移动文件或目录
```

### 管道（Pipeline）

管道使用 `|` 符号，将前一个命令的输出对象传递给下一个命令。

```powershell
# 获取所有运行中的进程，按 CPU 降序排列，取前 5 个
Get-Process | Sort-Object CPU -Descending | Select-Object -First 5
```

### 对象

PowerShell 中一切皆对象。每个命令输出的都是 .NET 对象，可以直接访问其属性和方法。

```powershell
# 获取进程对象并访问属性
$proc = Get-Process notepad
$proc.ProcessName    # 进程名
$proc.Id             # 进程 ID
$proc.CPU            # CPU 使用率
$proc.Kill()         # 调用方法终止进程
```

### 别名（Alias）

PowerShell 为常用命令提供了别名，兼容 cmd 和 bash 的命令习惯。

```powershell
# 查看所有别名
Get-Alias

# 常用别名
# dir / ls  -> Get-ChildItem
# cd        -> Set-Location
# cat / type-> Get-Content
# echo      -> Write-Output
# kill      -> Stop-Process
# ps        -> Get-Process
```

---

## 变量与数据类型

### 变量声明

PowerShell 变量以 `$` 开头，不需要提前声明类型。

```powershell
$name = "PowerShell"
$age = 25
$pi = 3.14159
$isActive = $true
```

### 强类型声明

可以在变量前指定类型，实现强类型约束。

```powershell
[int]$number = 42
[string]$text = "Hello"
[bool]$flag = $false
[double]$price = 19.99
[datetime]$date = Get-Date
```

### 常用数据类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `[string]` | 字符串 | `"Hello World"` |
| `[int]` | 32位整数 | `42` |
| `[long]` | 64位整数 | `9223372036854775807` |
| `[double]` | 双精度浮点数 | `3.14` |
| `[bool]` | 布尔值 | `$true` / `$false` |
| `[array]` | 数组 | `@(1, 2, 3)` |
| `[hashtable]` | 哈希表 | `@{key="value"}` |
| `[datetime]` | 日期时间 | `Get-Date` |
| `[pscustomobject]` | 自定义对象 | `[pscustomobject]@{...}` |
| `[xml]` | XML 对象 | `[xml]"<root/>"` |

### 特殊变量

| 变量 | 说明 |
|------|------|
| `$_` / `$PSItem` | 管道中的当前对象 |
| `$args` | 未声明参数的数组 |
| `$error` | 错误记录数组 |
| `$PSVersionTable` | PowerShell 版本信息 |
| `$env:` | 环境变量驱动器（如 `$env:PATH`） |
| `$HOME` | 用户主目录 |
| `$PWD` | 当前工作目录 |
| `$null` | 空值 |
| `$true` / `$false` | 布尔常量 |

---

## 运算符

### 算术运算符

```powershell
+       # 加法
-       # 减法
*       # 乘法
/       # 除法
%       # 取模
++      # 自增
--      # 自减
+=      # 加等于
-=      # 减等于
*=      # 乘等于
/=      # 除等于
%=      # 取模等于
```

### 比较运算符

PowerShell 的比较运算符以 `-` 开头，而非传统的符号。

```powershell
-eq     # 等于 (equal)
-ne     # 不等于 (not equal)
-gt     # 大于 (greater than)
-ge     # 大于等于 (greater or equal)
-lt     # 小于 (less than)
-le     # 小于等于 (less or equal)

# 字符串比较（默认不区分大小写）
-ceq    # 区分大小写的等于
-cne    # 区分大小写的不等于
-ieq    # 不区分大小写的等于（默认行为）

# 包含判断
-contains       # 集合包含指定值
-notcontains    # 集合不包含指定值
-in             # 值在集合中
-notin          # 值不在集合中
```

### 逻辑运算符

```powershell
-and    # 逻辑与
-or     # 逻辑或
-xor    # 逻辑异或
-not    # 逻辑非
!       # 逻辑非（与 -not 相同）
```

### 字符串运算符

```powershell
+       # 字符串拼接
*       # 字符串重复（"a" * 3 = "aaa"）
-replace        # 替换（支持正则）
-ireplace       # 不区分大小写替换
-creplace       # 区分大小写替换
-split          # 分割（支持正则）
-isplit         # 不区分大小写分割
-csplit         # 区分大小写分割
-join           # 连接数组为字符串
```

### 正则匹配运算符

```powershell
-match          # 正则匹配（不区分大小写）
-notmatch       # 正则不匹配
-cmatch         # 区分大小写匹配
-cnotmatch      # 区分大小写不匹配
-imatch         # 不区分大小写匹配（默认）
-like           # 通配符匹配（* ? [ ]）
-notlike        # 通配符不匹配
-clike          # 区分大小写通配符匹配
```

### 类型运算符

```powershell
-is     # 判断类型
-isnot  # 判断不是某类型
-as     # 类型转换
```

---

## 控制流

### if / elseif / else

```powershell
if ($score -ge 90) {
    Write-Output "优秀"
}
elseif ($score -ge 80) {
    Write-Output "良好"
}
elseif ($score -ge 60) {
    Write-Output "及格"
}
else {
    Write-Output "不及格"
}
```

### switch

```powershell
switch ($day) {
    1 { "星期一" }
    2 { "星期二" }
    3 { "星期三" }
    4 { "星期四" }
    5 { "星期五" }
    default { "周末" }
}

# switch 支持多条件匹配
switch -Wildcard ($input) {
    "*.txt" { "文本文件" }
    "*.exe" { "可执行文件" }
    "*.ps1" { "脚本文件" }
}

# switch 支持正则
switch -Regex ($ip) {
    "^192\.168\." { "内网地址" }
    "^10\." { "内网地址" }
    "^172\.(1[6-9]|2[0-9]|3[01])\." { "内网地址" }
    default { "公网地址" }
}
```

### for 循环

```powershell
for ($i = 0; $i -lt 10; $i++) {
    Write-Output $i
}
```

### foreach 循环

```powershell
$colors = @("红", "绿", "蓝")
foreach ($color in $colors) {
    Write-Output $color
}
```

### while 循环

```powershell
$i = 0
while ($i -lt 5) {
    Write-Output $i
    $i++
}
```

### do-while / do-until

```powershell
# do-while：至少执行一次，条件为真时继续
$i = 0
do {
    Write-Output $i
    $i++
} while ($i -lt 5)

# do-until：至少执行一次，直到条件为真时停止
$i = 0
do {
    Write-Output $i
    $i++
} until ($i -ge 5)
```

### break / continue

```powershell
# break：跳出循环
for ($i = 0; $i -lt 10; $i++) {
    if ($i -eq 5) { break }
    Write-Output $i
}

# continue：跳过当前迭代，继续下一次
for ($i = 0; $i -lt 10; $i++) {
    if ($i % 2 -eq 0) { continue }
    Write-Output "$i 是奇数"
}
```

---

## 函数

### 基本函数定义

```powershell
function Get-Greeting {
    param($name)
    return "Hello, $name!"
}

# 调用
Get-Greeting -name "World"
```

### 参数声明

```powershell
function Test-Params {
    param(
        [string]$Name,
        [int]$Age = 18,
        [string]$City = "Beijing"
    )

    Write-Output "姓名: $Name, 年龄: $Age, 城市: $City"
}

# 调用
Test-Params -Name "张三" -Age 25
```

### 返回值

PowerShell 函数中所有未被捕获的输出都会成为返回值。

```powershell
function Add-Numbers {
    param($a, $b)
    $a + $b          # 隐式返回
    return $a + $b   # 显式返回（会终止函数执行）
}

# 返回多个值
function Get-UserInfo {
    $name = "张三"
    $age = 25
    return $name, $age   # 返回数组
}
```

### 高级函数 [CmdletBinding()]

使用 `[CmdletBinding()]` 可以使函数获得 Cmdlet 的高级功能，如 `-Verbose`、`-Debug`、`-WhatIf` 等通用参数。

```powershell
function Invoke-Something {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$Target
    )

    Write-Verbose "正在处理 $Target"
    Write-Output "处理完成: $Target"
}

# 调用时可以使用 -Verbose
Invoke-Something -Target "Server01" -Verbose
```

### 参数验证

```powershell
function New-User {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [ValidateLength(3, 20)]
        [string]$Username,

        [Parameter(Mandatory=$true)]
        [ValidateRange(18, 100)]
        [int]$Age,

        [ValidateSet("Admin", "User", "Guest")]
        [string]$Role = "User",

        [ValidatePattern("^\w+@\w+\.\w+$")]
        [string]$Email
    )

    Write-Output "创建用户: $Username ($Role)"
}
```

### 管道输入

```powershell
function Get-Square {
    param(
        [Parameter(ValueFromPipeline=$true)]
        [int]$Number
    )
    process {
        $Number * $Number
    }
}

# 管道调用
1..5 | Get-Square
```

---

## 数组（Array）

### 创建数组

```powershell
# 方式一：使用逗号分隔
$arr = 1, 2, 3, 4, 5

# 方式二：使用 @()
$arr = @(1, 2, 3)

# 方式三：范围运算符
$arr = 1..10

# 空数组
$empty = @()

# 强类型数组
[int[]]$numbers = 1, 2, 3
```

### 访问元素

```powershell
$arr[0]      # 第一个元素
$arr[-1]     # 最后一个元素
$arr[0..2]   # 前三个元素
$arr.Length  # 数组长度
$arr.Count   # 数组长度（同 Length）
```

### 增删改查

```powershell
# 添加元素（数组是固定大小的，添加实际上是创建新数组）
$arr += 6

# 修改元素
$arr[0] = 100

# 判断是否包含
$arr -contains 3

# 查找索引
$arr.IndexOf(3)
```

### 遍历数组

```powershell
# foreach 遍历
foreach ($item in $arr) {
    Write-Output $item
}

# for 遍历
for ($i = 0; $i -lt $arr.Length; $i++) {
    Write-Output $arr[$i]
}

# 管道遍历
$arr | ForEach-Object { Write-Output $_ }
```

### 常用方法

```powershell
$arr.Sort()          # 排序
$arr.Reverse()       # 反转
$arr.Clone()         # 克隆
[array]::IndexOf($arr, $value)   # 查找索引
[array]::Find($arr, [Predicate[int]]{ $args[0] -gt 5 })  # 查找
```

### 数组操作符

```powershell
# 连接
$combined = $arr1 + $arr2

# 包含
$arr -contains 5
$arr -notcontains 5

# 成员
5 -in $arr
5 -notin $arr

# 比较（返回匹配的元素）
$arr -eq 3
$arr -ne 3
$arr -gt 5
```

---

## 哈希表（Hashtable）

### 创建哈希表

```powershell
# 基本语法
$ht = @{
    Name = "张三"
    Age = 25
    City = "北京"
}

# 空哈希表
$empty = @{}
```

### 增删改查

```powershell
# 添加
$ht["Email"] = "zhangsan@example.com"
$ht.Add("Phone", "123456789")

# 获取
$ht["Name"]     # 索引方式
$ht.Name        # 属性方式

# 修改
$ht["Age"] = 26

# 删除
$ht.Remove("Phone")

# 判断是否存在
$ht.ContainsKey("Name")
$ht.ContainsValue("张三")

# 键和值的集合
$ht.Keys
$ht.Values
$ht.Count
```

### 遍历哈希表

```powershell
# 遍历键
foreach ($key in $ht.Keys) {
    Write-Output "$key : $($ht[$key])"
}

# 遍历键值对
foreach ($item in $ht.GetEnumerator()) {
    Write-Output "$($item.Key) : $($item.Value)"
}

# 管道遍历
$ht.GetEnumerator() | ForEach-Object {
    Write-Output "$($_.Key) : $($_.Value)"
}
```

### 嵌套哈希表

```powershell
$user = @{
    Name = "张三"
    Contact = @{
        Email = "zhangsan@example.com"
        Phone = "123456789"
        Address = @{
            City = "北京"
            Street = "某某街道"
        }
    }
}

# 访问嵌套属性
$user.Contact.Email
$user.Contact.Address.City
```

### 有序字典

普通哈希表不保证键的顺序，使用 `[ordered]` 可以创建有序字典。

```powershell
$ordered = [ordered]@{
    First = 1
    Second = 2
    Third = 3
}
```

### 计算属性（splatting）

哈希表可以用于参数传递（splatting 技术）。

```powershell
$params = @{
    Path = "C:\temp"
    Recurse = $true
    Filter = "*.txt"
}

Get-ChildItem @params
```

---

## 字符串操作

### 字符串定义

```powershell
# 单引号：不解析变量和转义字符
$single = 'Hello $name'    # 输出：Hello $name

# 双引号：解析变量和转义字符
$name = "World"
$double = "Hello $name"    # 输出：Hello World

# 多行字符串（Here-String）
$hereString = @"
这是第一行
这是第二行
变量会被解析: $name
"@

# 单引号 Here-String（不解析变量）
$hereSingle = @'
变量不会被解析: $name
'@
```

### 字符串拼接

```powershell
# + 号拼接
$full = $first + " " + $last

# 字符串插值
$full = "$first $last"

# -join 操作符
$parts = @("Hello", "World")
$joined = $parts -join " "

# 格式化
$formatted = "姓名: {0}, 年龄: {1}" -f $name, $age
```

### 字符串查找

```powershell
$str = "Hello World"

# 包含（不区分大小写）
$str -like "*World*"
$str -match "World"

# 区分大小写
$str -clike "*world*"   # $false
$str -cmatch "world"    # $false

# 查找位置
$str.IndexOf("World")     # 6
$str.LastIndexOf("o")     # 7
$str.StartsWith("Hello")  # $true
$str.EndsWith("d")        # $true
```

### 字符串替换

```powershell
$str = "Hello World"

# 简单替换
$str -replace "World", "PowerShell"

# 正则替换
"abc123def456" -replace "\d+", "#"    # abc#def#

# 区分大小写替换
$str -creplace "world", "PS"          # 不替换（区分大小写）
```

### 字符串分割

```powershell
# 简单分割
"a,b,c" -split ","     # @("a", "b", "c")

# 正则分割
"a  b   c" -split "\s+"   # @("a", "b", "c")

# 限制分割次数
"a,b,c,d" -split ",", 3   # @("a", "b", "c,d")
```

### 大小写转换

```powershell
$str.ToUpper()     # 转大写
$str.ToLower()     # 转小写
```

### 其他常用方法

```powershell
$str.Length                 # 长度
$str.Trim()                 # 去除两端空白
$str.TrimStart()            # 去除开头空白
$str.TrimEnd()              # 去除结尾空白
$str.PadLeft(20)            # 左侧填充
$str.PadRight(20)           # 右侧填充
$str.Substring(0, 5)        # 截取子串
$str.Split(",")             # 分割（字符串方法）
$str.Replace("a", "b")      # 替换（字符串方法，不支持正则）
$str.Contains("Hello")      # 包含（字符串方法，区分大小写）
```

---

## 管道（Pipeline）

### 管道基础

PowerShell 管道传递的是对象，而不是文本。

```powershell
# 获取占用 CPU 最多的 5 个进程
Get-Process | Sort-Object CPU -Descending | Select-Object -First 5

# 停止所有名为 notepad 的进程
Get-Process notepad | Stop-Process
```

### Where-Object（筛选）

```powershell
# 获取所有运行中的服务
Get-Service | Where-Object { $_.Status -eq "Running" }

# 简写语法（PowerShell 3.0+）
Get-Service | Where-Object Status -eq "Running"

# 多条件
Get-Process | Where-Object { $_.CPU -gt 10 -and $_.WorkingSet -gt 100MB }
```

### ForEach-Object（遍历）

```powershell
# 对每个管道对象执行操作
1..5 | ForEach-Object { $_ * $_ }

# 简写
1..5 | ForEach-Object { $result += $_ }

# Begin/Process/End 块
1..5 | ForEach-Object -Begin { $sum = 0 } -Process { $sum += $_ } -End { $sum }
```

### Sort-Object（排序）

```powershell
# 升序排序
Get-Process | Sort-Object CPU

# 降序排序
Get-Process | Sort-Object CPU -Descending

# 多字段排序
Get-ChildItem | Sort-Object Extension, Length -Descending

# 自定义排序
Get-ChildItem | Sort-Object { $_.Name.Length }
```

### Select-Object（选择）

```powershell
# 选择指定属性
Get-Process | Select-Object ProcessName, Id, CPU

# 选择前 N 个
Get-Process | Sort-Object CPU -Descending | Select-Object -First 5

# 跳过前 N 个
Get-Process | Select-Object -Skip 10

# 选择唯一值
1,2,2,3,3,3 | Select-Object -Unique

# 计算属性
Get-Process | Select-Object ProcessName, @{
    Name = "MemoryMB"
    Expression = { [math]::Round($_.WorkingSet / 1MB, 2) }
}

# 展开属性
Get-Process | Select-Object -ExpandProperty ProcessName
```

### Group-Object（分组）

```powershell
# 按扩展名分组文件
Get-ChildItem | Group-Object Extension

# 按状态分组服务
Get-Service | Group-Object Status
```

### Measure-Object（统计）

```powershell
# 统计数量
Get-ChildItem | Measure-Object

# 统计数值属性
Get-Process | Measure-Object CPU -Sum -Average -Maximum -Minimum

# 统计文本行数
Get-Content file.txt | Measure-Object -Line
```

---

## 模块与快照

### 模块基础

模块是 PowerShell 功能的打包单元，可以包含 Cmdlet、函数、变量等。

```powershell
# 查看已加载的模块
Get-Module

# 查看所有可用模块
Get-Module -ListAvailable

# 导入模块
Import-Module ActiveDirectory

# 移除模块
Remove-Module ActiveDirectory
```

### 安装模块（PowerShellGet）

```powershell
# 安装 PSGallery 中的模块
Install-Module -Name PSScriptAnalyzer

# 指定版本和作用域
Install-Module -Name PSScriptAnalyzer -RequiredVersion 1.20.0 -Scope CurrentUser

# 卸载模块
Uninstall-Module -Name PSScriptAnalyzer

# 更新模块
Update-Module -Name PSScriptAnalyzer
```

### PowerShell Gallery

PowerShell Gallery 是微软官方的 PowerShell 模块仓库，地址：https://www.powershellgallery.com/

```powershell
# 查找模块
Find-Module -Name *SQL*

# 查看模块详情
Find-Module -Name PSScriptAnalyzer | Format-List *
```

### 导出模块成员

```powershell
# 在模块中导出函数和变量
Export-ModuleMember -Function Get-Something, Set-Something
Export-ModuleMember -Variable MyVariable
```

---

## 正则表达式

### -match 运算符

```powershell
# 基础匹配
"abc123" -match "\d+"      # $true

# 匹配结果保存在 $Matches 自动变量中
"abc123" -match "\d+"
$Matches[0]    # 123

# 捕获组
"张三,25" -match "(\w+),(\d+)"
$Matches[1]    # 张三
$Matches[2]    # 25
```

### -replace 运算符

```powershell
# 简单替换
"abc123" -replace "\d+", "#"    # abc#

# 使用捕获组
"2024-01-15" -replace "(\d{4})-(\d{2})-(\d{2})", '$1年$2月$3日'
# 输出：2024年01月15日

# 脚本块替换（PowerShell 6.1+）
"abc123" -replace "\d+", { [int]$_.Value * 2 }
```

### -split 运算符

```powershell
# 正则分割
"a b  c   d" -split "\s+"      # @("a", "b", "c", "d")

# 限制分割次数
"a,b,c,d,e" -split ",", 3      # @("a", "b", "c,d,e")
```

### Select-String

在文件或文本中搜索匹配的内容。

```powershell
# 在文件中搜索
Select-String -Path "*.txt" -Pattern "error"

# 在管道中搜索
Get-Content log.txt | Select-String -Pattern "ERROR"

# 递归搜索
Get-ChildItem -Recurse *.log | Select-String -Pattern "exception"

# 显示上下文
Select-String -Path log.txt -Pattern "error" -Context 2, 3
```

### 常用正则模式

```powershell
# 邮箱
$pattern = "^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$"

# IP 地址（IPv4）
$pattern = "^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"

# URL
$pattern = "^https?://"

# 中文字符
$pattern = "[\u4e00-\u9fa5]"

# 手机号
$pattern = "^1[3-9]\d{9}$"

# 身份证号
$pattern = "^\d{17}[\dXx]$"
```

---

## 文件操作

### Get-ChildItem（列出目录内容）

```powershell
# 列出当前目录内容
Get-ChildItem
Get-ChildItem -Path C:\temp

# 递归列出
Get-ChildItem -Recurse

# 筛选文件
Get-ChildItem -Filter "*.txt"
Get-ChildItem -Include "*.txt", "*.log" -Recurse

# 只列出文件或目录
Get-ChildItem -File
Get-ChildItem -Directory

# 按大小排序
Get-ChildItem | Sort-Object Length -Descending
```

### Get-Content（读取文件）

```powershell
# 读取整个文件
Get-Content -Path file.txt

# 读取指定行数
Get-Content -Path file.txt -TotalCount 10    # 前 10 行
Get-Content -Path file.txt -Tail 10          # 最后 10 行

# 逐行读取（管道）
Get-Content file.txt | ForEach-Object {
    # 处理每一行
}

# 以原始字节读取
Get-Content -Path file.bin -Encoding Byte -Raw
```

### Set-Content / Add-Content（写入文件）

```powershell
# 覆盖写入
Set-Content -Path file.txt -Value "Hello World"

# 追加写入
Add-Content -Path file.txt -Value "追加的内容"

# 指定编码
Set-Content -Path file.txt -Value "中文内容" -Encoding UTF8
```

### Copy / Move / Remove-Item

```powershell
# 复制文件
Copy-Item -Path source.txt -Destination dest.txt

# 复制目录及其内容
Copy-Item -Path C:\source -Destination C:\dest -Recurse

# 移动文件
Move-Item -Path source.txt -Destination dest.txt

# 删除文件
Remove-Item -Path file.txt

# 强制删除（包括只读）
Remove-Item -Path file.txt -Force

# 递归删除目录
Remove-Item -Path C:\temp -Recurse -Force
```

### 其他文件操作

```powershell
# 创建目录
New-Item -ItemType Directory -Path C:\newdir

# 创建文件
New-Item -ItemType File -Path newfile.txt

# 检查文件是否存在
Test-Path -Path file.txt

# 获取文件信息
Get-Item -Path file.txt | Select-Object Name, Length, LastWriteTime

# 重命名
Rename-Item -Path old.txt -NewName new.txt
```

---

## 网络请求

### Invoke-WebRequest

发送 HTTP/HTTPS 请求，返回完整的响应对象。

```powershell
# GET 请求
$response = Invoke-WebRequest -Uri "https://api.example.com/data"
$response.Content          # 响应内容
$response.StatusCode       # 状态码
$response.Headers          # 响应头

# POST 请求（表单数据）
$body = @{
    username = "admin"
    password = "123456"
}
$response = Invoke-WebRequest -Uri "https://api.example.com/login" -Method Post -Body $body

# POST JSON 数据
$jsonBody = '{"name":"test","value":123}'
$response = Invoke-WebRequest -Uri "https://api.example.com/api" `
    -Method Post `
    -Body $jsonBody `
    -ContentType "application/json"

# 设置请求头
$headers = @{
    "Authorization" = "Bearer token123"
    "User-Agent" = "MyScript/1.0"
}
$response = Invoke-WebRequest -Uri $url -Headers $headers

# 下载文件
Invoke-WebRequest -Uri "https://example.com/file.zip" -OutFile "file.zip"
```

### Invoke-RestMethod

专门用于 REST API，自动解析 JSON/XML 响应为对象。

```powershell
# GET JSON 数据（自动解析）
$data = Invoke-RestMethod -Uri "https://api.example.com/users"
$data | ForEach-Object { $_.name }

# POST JSON
$body = @{
    name = "test"
    email = "test@example.com"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "https://api.example.com/users" `
    -Method Post `
    -Body $body `
    -ContentType "application/json"
```

### 其他网络 Cmdlet

```powershell
# 测试网络连接
Test-NetConnection -ComputerName example.com -Port 80

# 解析 DNS
Resolve-DnsName -Name example.com

# TCP 连接测试
Test-Connection -ComputerName example.com -Count 3
```

---

## WMI/CIM

### Get-WmiObject（旧版，已弃用）

```powershell
# 获取操作系统信息
Get-WmiObject -Class Win32_OperatingSystem

# 获取磁盘信息
Get-WmiObject -Class Win32_LogicalDisk

# 获取进程
Get-WmiObject -Class Win32_Process
```

### Get-CimInstance（推荐使用）

```powershell
# 获取操作系统信息
Get-CimInstance -ClassName Win32_OperatingSystem |
    Select-Object Caption, Version, BuildNumber

# 获取磁盘信息
Get-CimInstance -ClassName Win32_LogicalDisk -Filter "DriveType=3" |
    Select-Object DeviceID, @{
        Name = "SizeGB"
        Expression = { [math]::Round($_.Size / 1GB, 2) }
    }, @{
        Name = "FreeGB"
        Expression = { [math]::Round($_.FreeSpace / 1GB, 2) }
    }

# 获取内存信息
Get-CimInstance -ClassName Win32_PhysicalMemory |
    Measure-Object -Property Capacity -Sum

# 获取服务
Get-CimInstance -ClassName Win32_Service -Filter "State='Running'"
```

### 常用 WMI/CIM 类

| 类名 | 说明 |
|------|------|
| `Win32_OperatingSystem` | 操作系统信息 |
| `Win32_ComputerSystem` | 计算机系统信息 |
| `Win32_Processor` | CPU 信息 |
| `Win32_PhysicalMemory` | 物理内存信息 |
| `Win32_LogicalDisk` | 逻辑磁盘信息 |
| `Win32_Process` | 进程信息 |
| `Win32_Service` | 服务信息 |
| `Win32_NetworkAdapterConfiguration` | 网络配置信息 |
| `Win32_UserAccount` | 用户账户信息 |
| `Win32_Group` | 用户组信息 |
| `Win32_EventLog` | 事件日志 |

---

## 远程管理

### Enter-PSSession（交互式会话）

```powershell
# 建立远程会话
Enter-PSSession -ComputerName Server01

# 指定凭据
Enter-PSSession -ComputerName Server01 -Credential (Get-Credential)
```

### Invoke-Command（远程执行命令）

```powershell
# 在远程计算机上执行命令
Invoke-Command -ComputerName Server01 -ScriptBlock {
    Get-Process | Where-Object CPU -gt 10
}

# 指定凭据
$cred = Get-Credential
Invoke-Command -ComputerName Server01 -Credential $cred -ScriptBlock {
    Get-Service
}

# 多台计算机同时执行
Invoke-Command -ComputerName Server01, Server02, Server03 -ScriptBlock {
    hostname
}

# 传递本地变量到远程
$serviceName = "wuauserv"
Invoke-Command -ComputerName Server01 -ScriptBlock {
    Get-Service -Name $using:serviceName
}

# 从远程获取文件
Copy-Item -Path C:\remote\file.txt -Destination C:\local\ `
    -FromSession (New-PSSession -ComputerName Server01)
```

### New-PSSession（持久会话）

```powershell
# 创建持久会话
$session = New-PSSession -ComputerName Server01

# 使用会话执行命令
Invoke-Command -Session $session -ScriptBlock { Get-Process }

# 关闭会话
Remove-PSSession -Session $session
```

### WinRM 配置

远程管理依赖 WinRM 服务，需要先在目标计算机上启用。

```powershell
# 启用 WinRM（需管理员权限）
Enable-PSRemoting -Force

# 查看 WinRM 配置
winrm quickconfig
```

---

## 执行策略与安全

### 执行策略（Execution Policy）

执行策略控制 PowerShell 加载配置文件和运行脚本的条件。

```powershell
# 查看当前执行策略
Get-ExecutionPolicy

# 设置执行策略（需管理员权限）
Set-ExecutionPolicy RemoteSigned

# 查看所有作用域的执行策略
Get-ExecutionPolicy -List
```

### 执行策略级别

| 策略 | 说明 |
|------|------|
| `Restricted` | 默认设置，不允许运行任何脚本，只能交互使用 |
| `AllSigned` | 所有脚本必须经过受信任的发布者签名 |
| `RemoteSigned` | 本地脚本可以运行，从网络下载的脚本必须签名 |
| `Unrestricted` | 可以运行所有脚本，非本地脚本会有警告 |
| `Bypass` | 不阻止任何脚本，也没有警告 |
| `Undefined` | 未设置，继承父作用域的策略 |

### 作用域

| 作用域 | 说明 |
|--------|------|
| `MachinePolicy` | 组策略（计算机级别） |
| `UserPolicy` | 组策略（用户级别） |
| `Process` | 当前进程 |
| `CurrentUser` | 当前用户 |
| `LocalMachine` | 本地计算机 |

### 绕过执行策略的常见方式

> 注意：仅用于学习和授权测试，请勿用于非法用途。

```powershell
# 方式一：命令行指定执行策略（仅当前进程有效）
powershell.exe -ExecutionPolicy Bypass -File script.ps1

# 方式二：从标准输入读取
powershell.exe -Command - < script.ps1

# 方式三：Base64 编码
powershell.exe -EncodedCommand <Base64字符串>
```

### 约束语言模式（Constrained Language Mode）

约束语言模式限制了可使用的 .NET 类型和方法，是一种安全加固措施。

```powershell
# 查看当前语言模式
$ExecutionContext.SessionState.LanguageMode

# 设置约束语言模式（仅当前会话）
$ExecutionContext.SessionState.LanguageMode = "ConstrainedLanguage"
```

约束语言模式的限制：
- 只能使用允许的 .NET 类型
- 不支持 Add-Type
- 不支持 P/Invoke
- 限制使用 COM 对象
- 限制字符串转换为类型

### PowerShell 日志

```powershell
# 查看 PowerShell 日志路径
# Windows PowerShell: %UserProfile%\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine
# PowerShell 7+: %UserProfile%\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine

# 启用模块日志记录
# 组策略：Administrative Templates -> Windows Components -> Windows PowerShell
#  -> Turn on Module Logging
```

---

## PowerShell 在安全领域的应用

### 红队（渗透测试）

#### 1. 信息收集
```powershell
# 系统信息收集
Get-CimInstance Win32_OperatingSystem
Get-CimInstance Win32_ComputerSystem
Get-NetIPAddress
Get-NetRoute
arp -a

# 用户和组枚举
Get-LocalUser
Get-LocalGroup
net user
net localgroup administrators

# 进程和服务枚举
Get-Process
Get-Service
Get-CimInstance Win32_StartupCommand
```

#### 2. 凭证窃取
- **Mimikatz**：可以通过 PowerShell 反射加载（如 `Invoke-Mimikatz`）
- **PowerView**：域信息收集工具
- **SharpHound**：BloodHound 的 C# 版本，可通过 PowerShell 执行

#### 3. 横向移动
```powershell
# WMI 远程执行
Get-WmiObject -Class Win32_Process -ComputerName target -Credential $cred

# PsExec 风格
# 使用 psexec.py 或 Invoke-PsExec

# WinRM 远程执行
Invoke-Command -ComputerName target -ScriptBlock { ... }
```

#### 4. 权限提升
- Token 窃取
- 服务配置错误利用
- 计划任务提权
- 注册表劫持

#### 5. 知名工具和框架
- **PowerShell Empire**：后渗透利用框架
- **PowerSploit**：PowerShell 攻击脚本集合
- **Nishang**：渗透测试 PowerShell 工具集
- **Cobalt Strike**：商业渗透测试平台，支持 PowerShell payload
- **Metasploit**：支持生成 PowerShell 类型的 payload

### 蓝队（防御与分析）

#### 1. 日志分析
```powershell
# 查看 PowerShell 操作日志
Get-WinEvent -LogName "Microsoft-Windows-PowerShell/Operational"

# 查看安全日志中的 PowerShell 相关事件
Get-WinEvent -LogName Security | Where-Object { $_.Message -match "PowerShell" }

# 事件 ID 参考
# 4104: 远程命令执行（Script Block Logging）
# 4103: 管道执行细节
# 400: 引擎状态变更
```

#### 2. 系统基线检查
```powershell
# 检查执行策略
Get-ExecutionPolicy -List

# 检查已安装的模块
Get-Module -ListAvailable

# 检查启动项
Get-CimInstance Win32_StartupCommand

# 检查计划任务
Get-ScheduledTask

# 检查服务
Get-Service | Where-Object { $_.StartType -eq "Automatic" }
```

#### 3. 恶意脚本检测
- 检查脚本中的 Base64 编码
- 检测 `Invoke-Expression`（IEX）的使用
- 检测 `DownloadString`、`DownloadFile` 等下载函数
- 分析 PowerShell 日志中的异常命令
- 使用 AMSI（Antimalware Scan Interface）检测

#### 4. 应急响应
```powershell
# 收集进程信息
Get-Process | Select-Object Id, ProcessName, Path, Company | Export-Csv processes.csv

# 收集网络连接
Get-NetTCPConnection | Where-Object { $_.State -eq "Established" }

# 收集注册表启动项
Get-ItemProperty "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run"
Get-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"

# 收集最近修改的文件
Get-ChildItem -Path C:\ -Recurse -File |
    Where-Object { $_.LastWriteTime -gt (Get-Date).AddDays(-7) } |
    Sort-Object LastWriteTime -Descending
```

### 无文件攻击（Fileless Attack）

PowerShell 是无文件攻击的常用载体，特点：
- 不落地文件，完全在内存中执行
- 使用 `DownloadString` 下载并通过 `IEX` 执行
- 使用 Base64 编码逃避检测
- 使用反射加载 .NET 程序集
- 利用 Windows 原生工具（Living off the Land）

### 防御建议

1. **启用 PowerShell 日志**：启用 Script Block Logging 和 Module Logging
2. **设置合适的执行策略**：至少使用 `RemoteSigned`
3. **启用 AMSI**：反恶意软件扫描接口
4. **使用最新版本**：PowerShell 5.1 或 7+ 安全性更好
5. **约束语言模式**：在受限环境中使用 Constrained Language Mode
6. **定期审计**：检查可疑的 PowerShell 活动
7. **EDR 部署**：使用端点检测与响应工具

---

## 参考资源

- [PowerShell 官方文档](https://learn.microsoft.com/powershell/)
- [PowerShell Gallery](https://www.powershellgallery.com/)
- [PowerShell GitHub 仓库](https://github.com/PowerShell/PowerShell)
- [PowerShell 安全最佳实践](https://learn.microsoft.com/powershell/scripting/learn/security/security-best-practices)

---

## 学习资源与知识拓展

### 官方资源

- **PowerShell 官方文档**：各语言官网提供最权威的文档和教程
- **PowerShell 标准库参考**：官方标准库 API 文档

### 在线教程

- **菜鸟教程 PowerShell**：https://www.runoob.com/ — 中文入门教程
- **W3Schools**：https://www.w3schools.com/ — 交互式学习平台
- **MDN Web Docs**：https://developer.mozilla.org/ — Web 技术文档（适用于 JS/HTML/CSS）

### 安全编程资源

- **OWASP 速查表系列**：https://cheatsheetseries.owasp.org/ — 各种安全最佳实践
- **CWE 常见弱点枚举**：https://cwe.mitre.org/ — 软件弱点分类体系
- **安全开发指南**：各语言官方安全文档与最佳实践

### 安全工具与库

- 根据语言选择相应的安全库和工具（加密库、HTTP 库、网络库等）
- 关注 GitHub 上的安全开源项目与社区

### 练习平台

- **LeetCode**：https://leetcode.cn/ — 算法练习平台
- **Codewars**：https://www.codewars.com/ — 编程挑战网站
- **Hack The Box**：https://www.hackthebox.com/ — 安全靶场
- **TryHackMe**：https://tryhackme.com/ — 安全学习房间
- **Bugku**：https://ctf.bugku.com/ — 国内 CTF 平台
- **攻防世界**：https://adworld.xctf.org.cn/ — XCTF 竞赛平台

### 推荐书籍

- 《PowerShell程序设计》— 入门经典教材
- 《PowerShell高级编程》— 进阶学习指南
- 各类安全相关技术书籍

### 社区与资讯

- **GitHub**：https://github.com/ — 开源项目托管平台
- **Stack Overflow**：https://stackoverflow.com/ — 编程问答社区
- **FreeBuf**：https://www.freebuf.com/ — 安全资讯媒体
- **安全客**：https://www.anquanke.com/ — 安全技术媒体
- **先知社区**：https://xz.aliyun.com/ — 阿里云安全社区

### 学习路线建议

1. **入门阶段**（1-2月）：掌握基本语法、数据类型、控制流
2. **进阶阶段**（2-3月）：函数、面向对象、异常处理、标准库
3. **实战练习**（1-2月）：通过项目巩固知识
4. **安全方向**（持续）：了解语言相关的安全漏洞和防护
5. **持续学习**：关注社区、阅读源码、参与开源
