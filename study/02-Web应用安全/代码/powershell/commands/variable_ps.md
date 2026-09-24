# variable_ps

> **分类**：变量
> **说明**：PowerShell 变量以 $ 开头

---

## 语法

```powershell
$variableName = value
```

## 常用类型

string / int / double / bool / array / hashtable / PSObject

## 特殊变量

$_ 当前管道对象\n$PSVersionTable PS版本信息\n$HOME 用户主目录\n$PWD 当前目录\n$Args 函数参数\n$Error 错误集合\n$true/$false 布尔值

## 示例代码

```powershell
# 基本变量
$name = "Alice"
$age = 25
$price = 9.99
$isActive = $true

# 类型指定
[int]$number = 42
[string]$text = "hello"
[bool]$flag = $true

# 查看类型
$name.GetType().Name
$age | Get-Member

# 类型转换
$num = [int]"123"
$str = [string]456
$arr = [array](1, 2, 3)

# 数组
$fruits = @("apple", "banana", "cherry")
$nums = 1..10  # 1到10的数组

# 哈希表
$person = @{
    Name = "Alice"
    Age = 25
    City = "Beijing"
}

# 环境变量
$env:PATH
$env:USERNAME
$env:COMPUTERNAME

# 特殊变量
$PSVersionTable.PSVersion  # PS版本
$HOME                       # 用户目录
$PWD.Path                   # 当前目录
$Error[0]                   # 最近的错误
$true / $false              # 布尔值
$null                       # 空值

# 变量作用域
$global:var = "全局"
$script:var = "脚本"
$private:var = "私有"

# 常量
Set-Variable -Name "MAX_SIZE" -Value 100 -Option Constant

# 验证变量是否存在
Test-Path variable:name
```
