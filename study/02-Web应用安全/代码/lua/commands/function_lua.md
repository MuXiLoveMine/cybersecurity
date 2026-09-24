# function_lua

> **分类**：函数与控制流
> **说明**：Lua 函数定义和控制流

---

## 语法

```lua
function funcName(param)\n  ...\nend
```

## 函数特性

多返回值 / 可变参数 / 匿名函数 / 闭包 / 函数作为值

## 控制流

if/elseif/else / while / repeat / for / for-in / break / goto

## 示例代码

```lua
-- ===== 函数 =====

-- 基本函数
function add(a, b)
    return a + b
end
print(add(2, 3))  -- 5

-- 多返回值
function min_max(arr)
    local min_val = arr[1]
    local max_val = arr[1]
    for _, v in ipairs(arr) do
        if v < min_val then min_val = v end
        if v > max_val then max_val = v end
    end
    return min_val, max_val
end
local min, max = min_max({3, 1, 4, 1, 5})

-- 可变参数
function sum(...)
    local total = 0
    for _, v in ipairs({...}) do
        total = total + v
    end
    return total
end
print(sum(1, 2, 3, 4, 5))  -- 15

-- 匿名函数
local double = function(x) return x * 2 end
print(double(5))  -- 10

-- 闭包
function create_counter()
    local count = 0
    return function()
        count = count + 1
        return count
    end
end

local counter = create_counter()
print(counter())  -- 1
print(counter())  -- 2
print(counter())  -- 3

-- ===== 控制流 =====

-- if/elseif/else
local age = 18
if age >= 18 then
    print("成年")
elseif age >= 6 then
    print("少年")
else
    print("儿童")
end

-- 逻辑运算符
-- and / or / not
-- Lua 中 and 和 or 是短路求值
local x = true and "hello"     -- "hello"
local y = false or "world"     -- "world"
local z = not false            -- true

-- 三元运算符模拟
local a = 10
local result = a > 5 and "大于5" or "小于等于5"

-- while 循环
local i = 0
while i < 5 do
    print(i)
    i = i + 1
end

-- repeat...until（至少执行一次，类似 do...while）
local j = 0
repeat
    print(j)
    j = j + 1
until j >= 5

-- 数值 for 循环
for i = 1, 5 do
    print(i)
end

-- 带步长
for i = 10, 0, -2 do
    print(i)  -- 10, 8, 6, 4, 2, 0
end

-- 泛型 for 循环
local arr = {"a", "b", "c"}
for i, v in ipairs(arr) do
    print(i, v)
end

local dict = {name = "Alice", age = 25}
for k, v in pairs(dict) do
    print(k, v)
end

-- break（只能用在循环内）
for i = 1, 10 do
    if i == 5 then
        break
    end
    print(i)
end

-- goto (Lua 5.2+)
-- ::label::
-- goto label
```
