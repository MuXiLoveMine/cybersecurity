-- ============================================================
-- 03_functions.lua - 函数：定义、多返回值、可变参数、局部函数、闭包、尾调用
-- 运行方式: lua 03_functions.lua 或 luajit 03_functions.lua
-- ============================================================

-- ---------- 1. 函数定义 ----------
print("========== 函数定义 ==========")

-- 1.1 标准函数定义
function greet(name)
    return "Hello, " .. name .. "!"
end
print(greet("Lua"))

-- 1.2 函数是一等公民，可以赋值给变量
local add = function(a, b)
    return a + b
end
print("add(1, 2) =", add(1, 2))

-- 1.3 局部函数（推荐，避免污染全局）
local function multiply(a, b)
    return a * b
end
print("multiply(3, 4) =", multiply(3, 4))

-- 1.4 无参数、无返回值的函数
local function say_hello()
    print("你好！")
end
say_hello()

-- 1.5 参数可以有默认值（通过 or 实现）
local function welcome(name)
    name = name or "访客"   -- 如果 name 为 nil，则使用默认值
    return "欢迎，" .. name
end
print(welcome("张三"))
print(welcome())          -- 使用默认值

print()

-- ---------- 2. 多返回值 ----------
print("========== 多返回值 ==========")

-- 函数可以返回多个值，用逗号分隔
local function get_user_info()
    return "Alice", 25, "alice@example.com"
end

-- 接收所有返回值
local name, age, email = get_user_info()
print("姓名:", name)
print("年龄:", age)
print("邮箱:", email)

-- 只接收部分返回值
local name2 = get_user_info()
print("只接收第一个:", name2)

-- 用 _ 忽略不需要的返回值（约定俗成）
local name3, _, email3 = get_user_info()
print("姓名:", name3, "邮箱:", email3)

-- 多余的变量会被赋值为 nil
local n1, n2, n3, n4 = get_user_info()
print("n4（多余）:", n4)   --> nil

-- 在表达式中调用函数，只有第一个返回值生效
print("字符串拼接: " .. get_user_info())   --> 只拼第一个返回值

-- 用括号包裹函数调用，强制只取第一个返回值
print("强制单返回:", (get_user_info()))

-- 返回值示例：除法，返回商和余数
local function divmod(a, b)
    return math.floor(a / b), a % b
end
local q, r = divmod(17, 5)
print("17 / 5 = 商", q, "余数", r)

print()

-- ---------- 3. 可变参数 ----------
print("========== 可变参数 ==========")

-- 使用 ... 表示可变参数
local function sum(...)
    local total = 0
    local args = {...}       -- 将可变参数收集到 table 中
    for i = 1, #args do
        total = total + args[i]
    end
    return total
end

print("sum(1, 2, 3) =", sum(1, 2, 3))
print("sum(1, 2, 3, 4, 5) =", sum(1, 2, 3, 4, 5))
print("sum() =", sum())   --> 0

-- 使用 select 函数处理可变参数
-- select('#', ...) 返回参数个数
-- select(n, ...) 返回从第 n 个开始的所有参数
local function demo_select(...)
    print("参数个数:", select("#", ...))
    print("第2个及以后:", select(2, ...))
end
demo_select("a", "b", "c", "d")

-- 带固定参数 + 可变参数
local function format_str(pattern, ...)
    return string.format(pattern, ...)
end
print(format_str("姓名:%s 年龄:%d", "Bob", 30))

print()

-- ---------- 4. 局部函数 ----------
print("========== 局部函数 ==========")

-- 使用 local function 定义局部函数
-- 局部函数只在当前作用域内可见
local function local_func()
    print("我是局部函数")
end
local_func()

-- 递归局部函数需要先声明再定义（或使用 local function 语法）
-- 正确方式1：local function
local function factorial(n)
    if n <= 1 then
        return 1
    end
    return n * factorial(n - 1)
end
print("factorial(5) =", factorial(5))

-- 正确方式2：先声明变量
local fib
fib = function(n)
    if n <= 2 then
        return 1
    end
    return fib(n - 1) + fib(n - 2)
end
print("fib(10) =", fib(10))

print()

-- ---------- 5. 闭包（Closure） ----------
print("========== 闭包 ==========")

-- 当一个函数内部定义了另一个函数，内部函数可以访问外部函数的局部变量
-- 这种机制称为闭包

-- 示例1：计数器
local function make_counter()
    local count = 0            -- 外部函数的局部变量
    return function()          -- 返回内部函数（闭包）
        count = count + 1
        return count
    end
end

local counter1 = make_counter()
print("counter1:", counter1())   --> 1
print("counter1:", counter1())   --> 2
print("counter1:", counter1())   --> 3

-- 每个闭包有独立的变量环境
local counter2 = make_counter()
print("counter2:", counter2())   --> 1（独立的 count）
print("counter1:", counter1())   --> 4（不受 counter2 影响）

-- 示例2：带参数的闭包
local function make_multiplier(n)
    return function(x)
        return x * n
    end
end

local double = make_multiplier(2)
local triple = make_multiplier(3)
print("double(5) =", double(5))     --> 10
print("triple(5) =", triple(5))     --> 15

-- 示例3：多个闭包共享同一个外部变量
local function create_account(initial_balance)
    local balance = initial_balance
    return {
        deposit = function(amount)
            balance = balance + amount
            return balance
        end,
        withdraw = function(amount)
            if amount <= balance then
                balance = balance - amount
                return balance
            else
                return nil, "余额不足"
            end
        end,
        get_balance = function()
            return balance
        end
    }
end

local acc = create_account(1000)
print("初始余额:", acc.get_balance())
print("存款 500:", acc.deposit(500))
print("取款 300:", acc.withdraw(300))
print("当前余额:", acc.get_balance())
local ok, err = acc.withdraw(2000)
print("取款 2000:", ok or err)   --> 余额不足

print()

-- ---------- 6. 尾调用（Tail Call） ----------
print("========== 尾调用 ==========")

-- 当函数的最后一个动作是调用另一个函数时，Lua 会进行尾调用优化
-- 不会增加调用栈深度，可以用来实现无限递归而不栈溢出

-- 普通递归（会栈溢出）
-- function bad_recursion(n)
--     if n == 0 then return end
--     bad_recursion(n - 1)
-- end

-- 尾递归实现阶乘（用累加器）
local function tail_factorial(n, acc)
    acc = acc or 1
    if n <= 1 then
        return acc
    end
    return tail_factorial(n - 1, n * acc)  -- 最后一个动作是函数调用
end
print("tail_factorial(5) =", tail_factorial(5))
print("tail_factorial(10) =", tail_factorial(10))

-- 尾递归实现斐波那契
local function tail_fib(n, a, b)
    a = a or 0
    b = b or 1
    if n == 0 then
        return a
    end
    return tail_fib(n - 1, b, a + b)
end
print("tail_fib(10) =", tail_fib(10))

print()

-- ---------- 7. 函数作为参数和返回值 ----------
print("========== 高阶函数 ==========")

-- 函数作为参数
local function apply(func, x, y)
    return func(x, y)
end

print("apply(add, 3, 4) =", apply(add, 3, 4))
print("apply(multiply, 3, 4) =", apply(multiply, 3, 4))

-- 匿名函数作为参数
local result = apply(function(a, b) return a ^ b end, 2, 10)
print("apply(匿名函数, 2, 10) =", result)

-- table 排序（自定义比较函数）
local nums = {5, 2, 8, 1, 9}
table.sort(nums, function(a, b)
    return a > b   -- 降序
end)
print("降序排序:", table.concat(nums, ", "))

print()
print("========== 示例结束 ==========")
