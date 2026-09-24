# variable_lua

> **分类**：变量与类型
> **说明**：Lua 变量和数据类型

---

## 语法

```lua
local variable = value  -- 局部变量\nvariable = value       -- 全局变量
```

## 基本类型

nil / boolean / number / string / function / table / userdata / thread

## 特点

默认全局 / local 声明局部变量 / nil 表示空 / 数字都是 double / 字符串不可变

## 示例代码

```lua
-- 全局变量
name = "Alice"
age = 25

-- 局部变量（推荐使用）
local price = 9.99
local flag = true
local nothing = nil  -- nil 表示空

-- 类型检查
print(type("hello"))   -- string
print(type(42))        -- number
print(type(true))      -- boolean
print(type(nil))       -- nil
print(type({}))        -- table
print(type(print))     -- function

-- 数字（Lua 中都是双精度浮点数）
local a = 10
local b = 3.14
local c = 1.23e-5

-- 算术运算
print(10 + 5)    -- 15
print(10 - 5)    -- 5
print(10 * 5)    -- 50
print(10 / 3)    -- 3.333...
print(10 // 3)   -- 3（整数除法，Lua 5.3+）
print(10 % 3)    -- 1
print(2 ^ 10)    -- 1024（幂运算）

-- 字符串
local s = "Hello, Lua!"
print(#s)                  -- 长度
print(string.upper(s))     -- 大写
print(string.lower(s))     -- 小写
print(string.reverse(s))   -- 反转
print(string.sub(s, 1, 5)) -- "Hello"（索引从1开始）
print(s:sub(1, 5))         -- 面向对象式写法

-- 字符串拼接
local str = "Hello" .. " " .. "World"

-- 数字转字符串
local num = 42
local str_num = tostring(num)
print("数字: " .. num)  -- 自动转换

-- 字符串转数字
local n = tonumber("123")
local f = tonumber("3.14")

-- 布尔运算
-- 只有 nil 和 false 是假，其余都是真（包括 0 和 ""）
if 0 then print("0 是真") end
if "" then print("空字符串是真") end

-- 多变量赋值
local x, y, z = 1, 2, 3
local a, b = 10, 20
a, b = b, a  -- 交换变量

-- 可变长参数
local function sum(...)
    local args = {...}
    local total = 0
    for _, v in ipairs(args) do
        total = total + v
    end
    return total
end
```
