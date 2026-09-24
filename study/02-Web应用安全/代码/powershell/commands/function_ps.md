# function_ps

> **分类**：函数
> **说明**：PowerShell 函数定义

---

## 语法

```powershell
function FunctionName($param1, $param2) { ... }
```

## 高级函数

function FuncName {\n  [CmdletBinding()]\n  param([Parameter(Mandatory=$true)][string]$Name)\n  process { ... }\n}

## 参数属性

Mandatory / Position / ValueFromPipeline / ValidateSet / ValidateRange

## 示例代码

```powershell
# 基本函数
function Add($a, $b) {
    return $a + $b
}
Add 2 3      # 5
Add -a 2 -b 3  # 命名参数

# 默认参数
function Greet($name = "World") {
    Write-Host "Hello, $name!"
}
Greet          # Hello, World!
Greet "Alice"  # Hello, Alice!

# 类型化参数
function Multiply([int]$a, [int]$b) {
    return $a * $b
}

# 高级函数（带 CmdletBinding）
function Get-EvenNumber {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true, ValueFromPipeline=$true)]
        [int[]]$Numbers
    )
    process {
        foreach ($n in $Numbers) {
            if ($n % 2 -eq 0) {
                $n
            }
        }
    }
}

# 管道输入
1..10 | Get-EvenNumber

# 参数验证
function Test-Age {
    param(
        [ValidateRange(0, 150)]
        [int]$Age
    )
    Write-Host "年龄: $Age"
}

function Get-Fruit {
    param(
        [ValidateSet("apple", "banana", "cherry")]
        [string]$Fruit
    )
    $Fruit
}

# 返回值
function Get-Numbers {
    1
    2
    3          # 所有输出都是返回值
    return 4   # return 也输出并退出
}
$result = Get-Numbers  # 返回数组 (1,2,3,4)

# 递归函数
function Get-Factorial {
    param([int]$n)
    if ($n -le 1) { return 1 }
    return $n * (Get-Factorial ($n - 1))
}
Get-Factorial 5  # 120
```
