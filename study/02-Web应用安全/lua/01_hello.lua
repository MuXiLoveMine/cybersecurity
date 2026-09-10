-- ============================================================
-- 01_hello.lua - Hello World、变量、数据类型、类型转换
-- 运行方式: lua 01_hello.lua 或 luajit 01_hello.lua
-- ============================================================

-- ---------- 1. Hello World ----------
print("========== Hello World ==========")
print("Hello, Lua!")
print("你好，Lua！")

-- 打印换行
print()

-- ---------- 2. 注释 ----------
-- 这是单行注释

--[[
    这是
    多行注释
    可以写很多行
]]

-- ---------- 3. 变量 ----------
print("========== 变量 ==========")

-- 全局变量（不推荐，尽量用 local）
global_name = "我是全局变量"

-- 局部变量（推荐）
local name = "Alice"
local age = 25
local is_student = true

print("姓名:", name)
print("年龄:", age)
print("是否学生:", is_student)

-- 多变量赋值
local a, b, c = 1, 2, 3
print("a =", a, "b =", b, "c =", c)

-- 变量交换（无需临时变量）
a, b = b, a
print("交换后: a =", a, "b =", b)

-- 未赋值的变量默认是 nil
local undefined_var
print("未赋值的变量:", undefined_var)  --> nil

print()

-- ---------- 4. 数据类型 ----------
print("========== 数据类型 ==========")

-- 4.1 nil（空值）
local nil_val = nil
print("nil 类型:", type(nil_val))

-- 4.2 boolean（布尔）
local bool_true = true
local bool_false = false
print("boolean 类型:", type(bool_true))

-- 注意：Lua 中只有 false 和 nil 为假，0 和空字符串都为真
print("0 为真吗?", 0 and "是" or "否")           --> 是
print('空字符串为真吗?', "" and "是" or "否")    --> 是
print("nil 为假吗?", nil and "真" or "假")       --> 假
print("false 为假吗?", false and "真" or "假")   --> 假

-- 4.3 number（数字，默认是双精度浮点数）
local num_int = 42
local num_float = 3.14
local num_hex = 0xFF        -- 十六进制
local num_sci = 1.5e3       -- 科学计数法
print("number 类型:", type(num_int))
print("整数:", num_int)
print("浮点数:", num_float)
print("十六进制 0xFF =", num_hex)
print("科学计数法 1.5e3 =", num_sci)

-- 4.4 string（字符串）
local str1 = "双引号字符串"
local str2 = '单引号字符串'
local str3 = [[
    多行字符串
    可以包含换行和 "引号"
    不需要转义
]]
print("string 类型:", type(str1))
print(str1)
print(str2)
print("多行字符串:", str3)

-- 字符串连接用 .. 运算符
local greeting = "Hello, " .. "Lua!"
print("字符串连接:", greeting)

-- 字符串长度用 # 运算符
print("字符串长度:", #"Hello, Lua!")

-- 4.5 table（表）
local tbl = {1, 2, 3, name = "Lua", version = "5.4"}
print("table 类型:", type(tbl))
print("table 数组部分长度:", #tbl)
print("table.name:", tbl.name)

-- 4.6 function（函数）
local func = function() return "hello" end
print("function 类型:", type(func))
print("function 类型:", type(print))  -- 内置函数也是 function 类型

-- 4.7 thread（协程）
local co = coroutine.create(function() end)
print("thread 类型:", type(co))

print()

-- ---------- 5. type() 函数 ----------
print("========== type() 函数 ==========")
print("type(nil) =", type(nil))
print("type(true) =", type(true))
print("type(42) =", type(42))
print('type("hello") =', type("hello"))
print("type({}) =", type({}))
print("type(print) =", type(print))

-- type() 总是返回字符串
print("type 返回值类型:", type(type(42)))  --> string

print()

-- ---------- 6. 类型转换 ----------
print("========== 类型转换 ==========")

-- 6.1 转字符串 tostring()
print("tostring(123) =", tostring(123))
print("tostring(true) =", tostring(true))
print("tostring(nil) =", tostring(nil))

-- 6.2 转数字 tonumber()
print('tonumber("123") =', tonumber("123"))
print('tonumber("3.14") =', tonumber("3.14"))
print('tonumber("FF", 16) =', tonumber("FF", 16))  -- 十六进制转十进制
print('tonumber("abc") =', tonumber("abc"))          -- 转换失败返回 nil

-- 6.3 字符串与数字自动转换（算术运算时）
print('"10" + 5 =', "10" + 5)        --> 15（字符串自动转数字）
print('"10" * "2" =', "10" * "2")    --> 20

-- 注意：连接运算不会自动转，需要显式转换
-- print("数字是: " .. 123)  -- 这也可以，因为 .. 会自动转数字为字符串
print("数字: " .. 123 .. " + " .. 456 .. " = " .. (123 + 456))

-- 6.4 布尔转换
-- 没有直接的 toboolean 函数，可以用条件表达式
local function toboolean(v)
    return v and true or false
end
print("toboolean(0) =", toboolean(0))
print("toboolean('') =", toboolean(''))
print("toboolean(nil) =", toboolean(nil))
print("toboolean(false) =", toboolean(false))

print()
print("========== 示例结束 ==========")
