-- ============================================================
-- 06_string.lua - 字符串操作：拼接、长度、查找、子串、分割、替换、格式化、大小写转换
-- 运行方式: lua 06_string.lua 或 luajit 06_string.lua
-- ============================================================

-- ---------- 1. 字符串基础 ----------
print("========== 字符串基础 ==========")

-- 字符串定义
local s1 = "双引号字符串"
local s2 = '单引号字符串'
local s3 = [[长多行字符串
可以包含换行
和 "引号"
]]

print(s1)
print(s2)
print(s3)

-- 转义字符
print("转义字符示例:")
print("  换行符: 第一行\n第二行")
print("  制表符: 列1\t列2\t列3")
print("  反斜杠: \\\\")
print("  引号: \"双引号\" '单引号'")

print()

-- ---------- 2. 字符串拼接 ----------
print("========== 字符串拼接 ==========")

-- 使用 .. 运算符
local a = "Hello"
local b = "Lua"
local c = a .. ", " .. b .. "!"
print("拼接结果:", c)

-- 数字会自动转为字符串
local num = 123
print("字符串+数字: " .. num)
print("多个数字: " .. 1 .. 2 .. 3)   --> 123

-- 注意：.. 运算符优先级较低，表达式需要括号
print("计算: " .. (1 + 2))   --> 计算: 3

-- table.concat 拼接数组元素（效率更高）
local parts = {"a", "b", "c", "d", "e"}
local result = table.concat(parts, "-")
print("table.concat:", result)

print()

-- ---------- 3. 字符串长度 ----------
print("========== 字符串长度 ==========")

-- 使用 # 运算符
local s = "Hello, Lua!"
print("字符串:", s)
print("长度:", #s)

-- 空字符串
print("空字符串长度:", #"")

-- 中文字符（每个 UTF-8 中文字符占 3 个字节）
local zh = "你好"
print("中文字符串:", zh)
print("字节长度:", #zh)   --> 6（两个中文字，每个3字节）

print()

-- ---------- 4. 大小写转换 ----------
print("========== 大小写转换 ==========")

local s = "Hello, Lua World!"
print("原字符串:", s)
print("全大写:", string.upper(s))
print("全小写:", string.lower(s))

-- 注意：只对 ASCII 字母有效，中文不受影响
local zh = "你好 Hello"
print("中文+英文:", zh)
print("upper:", string.upper(zh))

print()

-- ---------- 5. 子串 string.sub ----------
print("========== 子串 string.sub ==========")

local s = "Hello, Lua World!"
print("原字符串:", s)

-- string.sub(s, i, j) - 截取 s 中从 i 到 j 的子串
-- 索引从 1 开始
print("第1到5个字符:", string.sub(s, 1, 5))       --> Hello
print("第8到10个字符:", string.sub(s, 8, 10))     --> Lua

-- 省略 j 则截取到末尾
print("从第8个到末尾:", string.sub(s, 8))          --> Lua World!

-- 负数索引表示从末尾倒数
print("最后6个字符:", string.sub(s, -6, -1))      --> World!
print("最后一个字符:", string.sub(s, -1))          --> !
print("倒数第6到末尾:", string.sub(s, -6))         --> World!

-- 超出范围会自动截断
print("超出范围:", string.sub(s, 1, 100))         --> 整个字符串
print("起始为负:", string.sub(s, -100, 5))        --> Hello

print()

-- ---------- 6. 查找 string.find ----------
print("========== 查找 string.find ==========")

local s = "Hello, Lua World! Lua is great!"

-- string.find(s, pattern [, init [, plain]])
-- 返回：起始位置, 结束位置
-- 找不到返回 nil
local start, stop = string.find(s, "Lua")
print("查找 'Lua':", start, stop)   --> 8, 10

-- 从指定位置开始查找
local start2, stop2 = string.find(s, "Lua", 11)
print("从位置11查找 'Lua':", start2, stop2)   --> 19, 21

-- 找不到返回 nil
local not_found = string.find(s, "Python")
print("查找 'Python':", not_found)   --> nil

-- plain 模式：关闭模式匹配，纯文本查找
-- 当查找的内容包含特殊字符时很有用
local s2 = "a.b.c"
print("查找 '.' (模式):", string.find(s2, "."))      --> 1, 1 (.匹配任意字符)
print("查找 '.' (纯文本):", string.find(s2, ".", 1, true))  --> 2, 2

-- 判断是否包含子串
local function contains(s, substr)
    return string.find(s, substr, 1, true) ~= nil
end
print("包含 'Lua' 吗?", contains(s, "Lua"))   --> true
print("包含 'Java' 吗?", contains(s, "Java"))  --> false

print()

-- ---------- 7. 替换 string.gsub ----------
print("========== 替换 string.gsub ==========")

local s = "Hello World Hello Lua"

-- string.gsub(s, pattern, repl [, n])
-- 返回：替换后的字符串, 替换次数
local result, count = string.gsub(s, "Hello", "Hi")
print("替换 'Hello' 为 'Hi':", result)
print("替换次数:", count)

-- 指定替换次数
local result2 = string.gsub(s, "Hello", "Hey", 1)   -- 只替换第一个
print("只替换第一个:", result2)

-- 替换为空（删除）
local result3 = string.gsub(s, " ", "")   -- 删除所有空格
print("删除空格:", result3)

print()

-- ---------- 8. 格式化 string.format ----------
print("========== 格式化 string.format ==========")

-- 类似 C 语言的 sprintf
local name = "Alice"
local age = 25
local pi = math.pi

-- %s 字符串, %d 整数, %f 浮点数
print(string.format("姓名: %s, 年龄: %d", name, age))
print(string.format("圆周率: %f", pi))

-- 控制小数位数
print(string.format("保留2位小数: %.2f", pi))
print(string.format("保留4位小数: %.4f", pi))

-- 宽度与对齐
print(string.format("右对齐: [%10s]", name))
print(string.format("左对齐: [%-10s]", name))
print(string.format("补零: %05d", age))
print(string.format("十六进制: 0x%X", 255))

-- 各种格式说明符
print("\n格式说明符示例：")
print(string.format("  %%c (字符): %c", 65))         --> A
print(string.format("  %%d (十进制): %d", 123))       --> 123
print(string.format("  %%x (十六进制): %x", 255))     --> ff
print(string.format("  %%o (八进制): %o", 255))       --> 377
print(string.format("  %%f (浮点数): %f", 3.14))      --> 3.140000
print(string.format("  %%e (科学计数): %e", 1000))    --> 1.000000e+003
print(string.format("  %%s (字符串): %s", "hello"))   --> hello
print(string.format("  %%q (安全引用): %q", 'a"b'))   --> "a\"b"

print()

-- ---------- 9. 其他字符串函数 ----------
print("========== 其他字符串函数 ==========")

-- string.rep - 重复字符串
print("string.rep('*', 10):", string.rep("*", 10))
print("string.rep('ha', 5):", string.rep("ha", 5))

-- string.reverse - 反转字符串
print("string.reverse('abcde'):", string.reverse("abcde"))

-- string.byte - 字符转 ASCII 码
print("string.byte('A'):", string.byte("A"))         --> 65
print("string.byte('abc', 2):", string.byte("abc", 2))  --> 98

-- string.char - ASCII 码转字符
print("string.char(65, 66, 67):", string.char(65, 66, 67))  --> ABC

-- string.len - 字符串长度（与 # 运算符相同）
print("string.len('hello'):", string.len("hello"))   --> 5

print()

-- ---------- 10. 字符串分割 ----------
print("========== 字符串分割 ==========")

-- Lua 没有内置的 split 函数，需要自己实现
-- 方式1：使用 string.gmatch
local function split(str, sep)
    sep = sep or ","
    local result = {}
    for word in string.gmatch(str, "[^" .. sep .. "]+") do
        table.insert(result, word)
    end
    return result
end

local csv = "apple,banana,orange,grape"
local fruits = split(csv, ",")
print("分割 CSV:", table.concat(fruits, " | "))

local path = "/usr/local/bin/lua"
local parts = split(path, "/")
print("分割路径:", table.concat(parts, " | "))

-- 方式2：使用 string.find 实现（更精确）
local function split2(str, sep)
    sep = sep or ","
    local result = {}
    local pos = 1
    while true do
        local start, stop = string.find(str, sep, pos, true)
        if not start then
            table.insert(result, string.sub(str, pos))
            break
        end
        table.insert(result, string.sub(str, pos, start - 1))
        pos = stop + 1
    end
    return result
end

local test = "a,,b,c"
local r1 = split(test, ",")    -- 会跳过空字符串
local r2 = split2(test, ",")   -- 保留空字符串
print("split('a,,b,c'):", table.concat(r1, "|"))
print("split2('a,,b,c'):", table.concat(r2, "|"))

print()

-- ---------- 11. 字符串判断 ----------
print("========== 字符串判断 ==========")

-- 判断是否以某字符串开头
local function starts_with(str, prefix)
    return string.sub(str, 1, #prefix) == prefix
end
print("'hello.lua' 以 'hello' 开头:", starts_with("hello.lua", "hello"))
print("'hello.lua' 以 'world' 开头:", starts_with("hello.lua", "world"))

-- 判断是否以某字符串结尾
local function ends_with(str, suffix)
    return string.sub(str, -#suffix) == suffix
end
print("'hello.lua' 以 '.lua' 结尾:", ends_with("hello.lua", ".lua"))
print("'hello.lua' 以 '.py' 结尾:", ends_with("hello.lua", ".py"))

-- 判断是否为空字符串
local function is_empty(str)
    return str == nil or str == ""
end
print("'' 为空:", is_empty(""))
print("'abc' 为空:", is_empty("abc"))

print()
print("========== 示例结束 ==========")
