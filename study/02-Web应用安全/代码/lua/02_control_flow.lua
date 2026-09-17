-- ============================================================
-- 02_control_flow.lua - 控制流：if/elseif/else、for、while、repeat-until、break
-- 运行方式: lua 02_control_flow.lua 或 luajit 02_control_flow.lua
-- ============================================================

-- ---------- 1. if / elseif / else ----------
print("========== if / elseif / else ==========")

local score = 85

if score >= 90 then
    print("分数", score, "：优秀")
elseif score >= 80 then
    print("分数", score, "：良好")
elseif score >= 60 then
    print("分数", score, "：及格")
else
    print("分数", score, "：不及格")
end

-- 多条件判断
local age = 20
local has_id = true

if age >= 18 and has_id then
    print("可以进入（成年且有证件）")
elseif age >= 18 and not has_id then
    print("请出示证件")
else
    print("未成年人禁止入内")
end

-- Lua 中 if 的条件判断：只有 false 和 nil 为假
local x = 0
if x then
    print("0 被视为真")   -- 会执行
end

local y = ""
if y then
    print("空字符串被视为真")  -- 会执行
end

local z = nil
if z then
    print("nil 被视为真")   -- 不会执行
else
    print("nil 被视为假")   -- 会执行
end

print()

-- ---------- 2. for 循环：数值 for ----------
print("========== for 循环：数值 for ==========")

-- 基本用法：for 变量 = 起始值, 结束值 do ... end
-- 默认步长为 1
print("1 到 5：")
for i = 1, 5 do
    print("  i =", i)
end

-- 指定步长
print("1 到 10，步长 2：")
for i = 1, 10, 2 do
    print("  i =", i)
end

-- 倒序
print("10 到 1，倒序：")
for i = 10, 1, -1 do
    print("  i =", i)
end

-- 步长为小数
print("0 到 1，步长 0.2：")
for i = 0, 1, 0.2 do
    print(string.format("  i = %.1f", i))
end

print()

-- ---------- 3. for 循环：泛型 for ----------
print("========== for 循环：泛型 for ==========")

-- 3.1 ipairs - 遍历数组（按数字索引顺序，从 1 开始，遇到 nil 停止）
local fruits = {"苹果", "香蕉", "橙子", "葡萄"}
print("ipairs 遍历数组：")
for i, v in ipairs(fruits) do
    print("  索引", i, "=", v)
end

-- 3.2 pairs - 遍历表（所有键值对，顺序不固定）
local person = {
    name = "张三",
    age = 25,
    city = "北京",
    job = "程序员"
}
print("pairs 遍历表：")
for k, v in pairs(person) do
    print("  ", k, "=", v)
end

-- 3.3 遍历字符串（使用 string.gmatch）
local str = "hello world"
print("gmatch 遍历单词：")
for word in string.gmatch(str, "%a+") do
    print("  单词:", word)
end

print()

-- ---------- 4. while 循环 ----------
print("========== while 循环 ==========")

print("while 1 到 5：")
local i = 1
while i <= 5 do
    print("  i =", i)
    i = i + 1
end

-- while 循环求阶乘
print("while 求 5 的阶乘：")
local n = 5
local fact = 1
local j = 1
while j <= n do
    fact = fact * j
    j = j + 1
end
print("  5! =", fact)

print()

-- ---------- 5. repeat-until 循环 ----------
print("========== repeat-until 循环 ==========")

-- 类似 do-while，循环体至少执行一次
print("repeat-until 1 到 5：")
local k = 1
repeat
    print("  k =", k)
    k = k + 1
until k > 5

-- 即使条件一开始就为假，循环体也会执行一次
print("repeat-until 条件初始为假：")
local m = 10
repeat
    print("  执行了一次，m =", m)
until m < 5   -- 条件一开始就假，但还是会执行一次

print()

-- ---------- 6. break ----------
print("========== break ==========")

-- break 跳出当前循环
print("for 循环中 break（遇到 5 停止）：")
for i = 1, 10 do
    if i == 5 then
        print("  遇到 5，break")
        break
    end
    print("  i =", i)
end

-- while 循环中 break
print("while 循环中 break：")
local count = 0
while true do   -- 无限循环
    count = count + 1
    if count > 3 then
        break   -- 用 break 退出
    end
    print("  count =", count)
end

print()

-- ---------- 7. goto（Lua 5.2+，较少使用） ----------
print("========== goto（可选了解） ==========")

print("goto 示例：")
local p = 1
::start_loop::   -- 标签
if p <= 3 then
    print("  p =", p)
    p = p + 1
    goto start_loop   -- 跳转到标签
end

print()
print("========== 综合练习 ==========")

-- 练习1：打印 1-100 中所有偶数
print("1-100 中的偶数（前10个）：")
local even_count = 0
for i = 1, 100 do
    if i % 2 == 0 then
        io.write(i, " ")
        even_count = even_count + 1
        if even_count >= 10 then
            break
        end
    end
end
print()

-- 练习2：九九乘法表
print("九九乘法表（前3行）：")
for i = 1, 3 do
    local line = ""
    for j = 1, i do
        line = line .. string.format("%dx%d=%-2d ", j, i, i * j)
    end
    print(line)
end

-- 练习3：斐波那契数列
print("斐波那契数列前10项：")
local a, b = 0, 1
for i = 1, 10 do
    io.write(a, " ")
    a, b = b, a + b
end
print()

print()
print("========== 示例结束 ==========")
