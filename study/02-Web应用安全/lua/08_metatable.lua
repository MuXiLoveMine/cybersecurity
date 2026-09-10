-- ============================================================
-- 08_metatable.lua - 元表与元方法：__index/__newindex/__add/__tostring 等
-- 运行方式: lua 08_metatable.lua 或 luajit 08_metatable.lua
-- ============================================================

-- ---------- 1. 元表基础 ----------
print("========== 元表基础 ==========")

-- 元表（Metatable）是一个普通的 table，用于定义另一个 table 的行为
-- 元方法（Metamethod）是元表中以 __ 开头的特殊键

-- 创建普通表
local t = {name = "Lua", version = "5.4"}

-- 创建元表
local mt = {}

-- 设置元表
setmetatable(t, mt)

-- 获取元表
print("获取元表:", getmetatable(t) == mt)   --> true

-- 也可以在创建时设置
local t2 = setmetatable({a = 1, b = 2}, {})
print("t2 有元表:", getmetatable(t2) ~= nil)

print()

-- ---------- 2. __tostring 元方法 ----------
print("========== __tostring ==========")

-- __tostring 定义 table 转字符串的行为
local person = {name = "张三", age = 25}

-- 没有 __tostring 时，tostring 返回类似 table: 0x...
print("默认 tostring:", tostring(person))

-- 设置 __tostring
local mt = {
    __tostring = function(t)
        return string.format("Person{name=%s, age=%d}", t.name, t.age)
    end
}
setmetatable(person, mt)

print("设置后 tostring:", tostring(person))
print("print 会自动调用:", person)   -- print 会自动调用 tostring

print()

-- ---------- 3. __index 元方法 ----------
print("========== __index ==========")

-- 当访问 table 中不存在的键时，会调用 __index 元方法
-- __index 可以是函数，也可以是另一个 table

-- 3.1 __index 是函数
local mt = {
    __index = function(t, key)
        -- t 是被访问的表，key 是被访问的键
        return "默认值: " .. key
    end
}

local t = setmetatable({a = 1, b = 2}, mt)
print("t.a =", t.a)       --> 1（存在，直接返回）
print("t.b =", t.b)       --> 2（存在，直接返回）
print("t.c =", t.c)       --> 默认值: c（不存在，调用 __index）
print("t.xyz =", t.xyz)   --> 默认值: xyz

-- 3.2 __index 是 table（实现继承/原型模式）
print("\n__index 是 table（继承）：")

-- 原型（父类）
local Animal = {
    species = "动物",
    speak = function()
        print("动物发出声音")
    end
}

-- 新对象
local Dog = {
    name = "旺财",
    breed = "金毛"
}

-- 设置元表，__index 指向 Animal
setmetatable(Dog, {__index = Animal})

print("Dog.name:", Dog.name)       --> 旺财（自身属性）
print("Dog.species:", Dog.species) --> 动物（从 Animal 继承）
Dog.speak()                        --> 动物发出声音（从 Animal 继承）

-- 修改自身属性不影响原型
Dog.species = "犬科"
print("Dog.species 修改后:", Dog.species)
print("Animal.species:", Animal.species)  -- 不变

-- 3.3 带默认值的表
print("\n带默认值的表：")
local function default_table(default)
    local mt = {__index = function() return default end}
    return setmetatable({}, mt)
end

local scores = default_table(0)
print("scores.math:", scores.math)     --> 0
print("scores.english:", scores.english) --> 0
scores.math = 95
print("scores.math 赋值后:", scores.math)

print()

-- ---------- 4. __newindex 元方法 ----------
print("========== __newindex ==========")

-- 当给 table 中不存在的键赋值时，会调用 __newindex 元方法

-- 4.1 只读表
print("只读表示例：")
local function read_only(t)
    local mt = {
        __index = t,
        __newindex = function(t, k, v)
            error("尝试修改只读表的键: " .. tostring(k), 2)
        end
    }
    return setmetatable({}, mt)
end

local config = read_only({
    host = "localhost",
    port = 8080
})

print("config.host:", config.host)
-- config.host = "127.0.0.1"  -- 这会报错

-- 4.2 跟踪赋值
print("\n跟踪赋值：")
local mt = {
    __newindex = function(t, key, value)
        print(string.format("  赋值: %s = %s", key, tostring(value)))
        rawset(t, key, value)   -- 使用 rawset 真正赋值，避免再次触发 __newindex
    end
}

local t = setmetatable({}, mt)
t.name = "Lua"
t.version = "5.4"
t.age = 30

print("t.name:", t.name)

print()

-- ---------- 5. 算术运算元方法 ----------
print("========== 算术运算元方法 ==========")

-- __add: +    __sub: -    __mul: *    __div: /
-- __mod: %    __pow: ^    __unm: -（负号）

-- 示例：向量加法
print("向量加法：")

local Vector = {}
Vector.mt = {}

function Vector.new(x, y)
    local v = {x = x, y = y}
    setmetatable(v, Vector.mt)
    return v
end

-- __add 元方法：向量相加
Vector.mt.__add = function(a, b)
    return Vector.new(a.x + b.x, a.y + b.y)
end

-- __sub 元方法：向量相减
Vector.mt.__sub = function(a, b)
    return Vector.new(a.x - b.x, a.y - b.y)
end

-- __mul 元方法：向量数乘
Vector.mt.__mul = function(v, scalar)
    return Vector.new(v.x * scalar, v.y * scalar)
end

-- __tostring 方便打印
Vector.mt.__tostring = function(v)
    return string.format("(%d, %d)", v.x, v.y)
end

local v1 = Vector.new(1, 2)
local v2 = Vector.new(3, 4)

print("v1 =", v1)
print("v2 =", v2)
print("v1 + v2 =", v1 + v2)
print("v1 - v2 =", v1 - v2)
print("v1 * 3 =", v1 * 3)

print()

-- ---------- 6. 关系运算元方法 ----------
print("========== 关系运算元方法 ==========")

-- __eq: ==    __lt: <    __le: <=
-- 注意：~= 由 __eq 取反，> 由 __lt 取反，>= 由 __le 取反

-- 示例：字符串长度比较
print("字符串长度比较：")

local function new_len_str(s)
    local obj = {value = s}
    setmetatable(obj, {
        __lt = function(a, b)
            return #a.value < #b.value
        end,
        __le = function(a, b)
            return #a.value <= #b.value
        end,
        __eq = function(a, b)
            return #a.value == #b.value
        end,
        __tostring = function(t)
            return t.value
        end
    })
    return obj
end

local a = new_len_str("apple")     -- 5
local b = new_len_str("banana")    -- 6
local c = new_len_str("grape")     -- 5

print("a =", a, "(长度 5)")
print("b =", b, "(长度 6)")
print("c =", c, "(长度 5)")
print("a < b:", a < b)       --> true
print("a <= c:", a <= c)     --> true
print("a == c:", a == c)     --> true（长度相等）
print("a > b:", a > b)       --> false

print()

-- ---------- 7. __call 元方法 ----------
print("========== __call ==========")

-- __call 让 table 可以像函数一样被调用

-- 示例：可调用的对象
local mt = {
    __call = function(t, ...)
        print("table 被调用了，参数:", ...)
        return "调用结果"
    end
}

local obj = setmetatable({name = "可调用对象"}, mt)
local result = obj("hello", 123)
print("返回值:", result)

-- 示例：类工厂模式
print("\n类工厂模式：")

local function create_class(base)
    local class = {}
    class.__index = class

    setmetatable(class, {
        __call = function(cls, ...)
            local obj = setmetatable({}, cls)
            if obj.init then
                obj:init(...)
            end
            return obj
        end,
        __index = base  -- 继承
    })

    return class
end

-- 创建 Animal 类
local Animal = create_class()
function Animal:init(name)
    self.name = name
end
function Animal:speak()
    print(self.name .. " 发出声音")
end

-- 创建 Dog 类，继承自 Animal
local Dog = create_class(Animal)
function Dog:speak()
    print(self.name .. " 汪汪叫")
end

-- 像函数一样调用类来创建实例
local dog = Dog("旺财")
dog:speak()   --> 旺财 汪汪叫

print()

-- ---------- 8. __len 元方法 ----------
print("========== __len ==========")

-- __len 定义 # 运算符的行为

local mt = {
    __len = function(t)
        local count = 0
        for _ in pairs(t) do
            count = count + 1
        end
        return count
    end
}

local t = setmetatable({a = 1, b = 2, c = 3}, mt)
print("字典的元素个数:", #t)   --> 3（如果没有 __len，# 对字典结果不确定）

print()

-- ---------- 9. __concat 元方法 ----------
print("========== __concat ==========")

-- __concat 定义 .. 运算符的行为

local mt = {
    __concat = function(a, b)
        -- 支持 table 和字符串连接
        if type(a) == "table" then
            return table.concat(a, ", ") .. b
        else
            return a .. table.concat(b, ", ")
        end
    end
}

local arr = setmetatable({"apple", "banana", "cherry"}, mt)
print("前缀: " .. arr)
print(arr .. " :后缀")

print()

-- ---------- 10. 综合示例：集合（Set） ----------
print("========== 综合示例：集合（Set） ==========")

local Set = {}
Set.mt = {}

-- 创建集合
function Set.new(tbl)
    local set = {}
    for _, v in ipairs(tbl or {}) do
        set[v] = true
    end
    setmetatable(set, Set.mt)
    return set
end

-- 并集
Set.mt.__add = function(a, b)
    local result = Set.new()
    for k in pairs(a) do result[k] = true end
    for k in pairs(b) do result[k] = true end
    return result
end

-- 交集
Set.mt.__mul = function(a, b)
    local result = Set.new()
    for k in pairs(a) do
        if b[k] then
            result[k] = true
        end
    end
    return result
end

-- 差集
Set.mt.__sub = function(a, b)
    local result = Set.new()
    for k in pairs(a) do
        if not b[k] then
            result[k] = true
        end
    end
    return result
end

-- 成员判断
function Set.contains(set, item)
    return set[item] == true
end

-- 集合大小
Set.mt.__len = function(set)
    local count = 0
    for _ in pairs(set) do
        count = count + 1
    end
    return count
end

-- 字符串表示
Set.mt.__tostring = function(set)
    local items = {}
    for k in pairs(set) do
        table.insert(items, tostring(k))
    end
    table.sort(items)
    return "{" .. table.concat(items, ", ") .. "}"
end

-- 测试
local s1 = Set.new({1, 2, 3, 4})
local s2 = Set.new({3, 4, 5, 6})

print("s1 =", s1)
print("s2 =", s2)
print("s1 大小:", #s1)
print("s1 包含 3:", Set.contains(s1, 3))
print("s1 包含 9:", Set.contains(s1, 9))
print("s1 + s2 (并集) =", s1 + s2)
print("s1 * s2 (交集) =", s1 * s2)
print("s1 - s2 (差集) =", s1 - s2)

print()
print("========== 示例结束 ==========")
