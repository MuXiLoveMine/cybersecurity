# table_lua

> **分类**：表（Table）
> **说明**：Lua 唯一的数据结构，既是数组也是字典

---

## 语法

```lua
local t = {key = value, ...}  -- 字典\nlocal arr = {1, 2, 3}     -- 数组
```

## 数组操作

table.insert / table.remove / table.concat / table.sort / # 获取长度

## 字典操作

t[key] 访问 / pairs 遍历 / next 取下一个

## 示例代码

```lua
-- ===== 数组（列表） =====
local fruits = {"apple", "banana", "cherry"}

-- 访问（索引从 1 开始！）
print(fruits[1])       -- "apple"
print(#fruits)         -- 3（长度）

-- 添加
fruits[4] = "orange"
table.insert(fruits, "grape")       -- 末尾添加
table.insert(fruits, 2, "mango")    -- 在位置2插入

-- 删除
table.remove(fruits)                -- 删除最后一个
table.remove(fruits, 2)             -- 删除第2个

-- 拼接
print(table.concat(fruits, ", "))   -- "apple, banana, cherry"

-- 排序
table.sort(fruits)

-- 遍历数组（ipairs，顺序遍历，遇 nil 停止）
for i, v in ipairs(fruits) do
    print(i, v)
end

-- ===== 字典（哈希表） =====
local person = {
    name = "Alice",
    age = 25,
    city = "Beijing"
}

-- 访问
print(person.name)       -- "Alice"
print(person["age"])     -- 25

-- 修改/添加
person.email = "alice@test.com"
person["phone"] = "1234567890"

-- 删除
person.city = nil

-- 遍历字典（pairs，无序，遍历所有键值对）
for k, v in pairs(person) do
    print(k, v)
end

-- 判断键是否存在
if person.name ~= nil then
    print("name 存在")
end

-- ===== 混合表 =====
local mixed = {
    "apple", "banana",     -- 数组部分（键 1, 2）
    name = "Alice",        -- 哈希部分
    age = 25
}

-- ===== 表的操作 =====
local t = {a = 1, b = 2, c = 3}

-- 获取所有键（自定义函数）
local function keys(tbl)
    local ks = {}
    for k in pairs(tbl) do
        table.insert(ks, k)
    end
    return ks
end

-- 表的浅拷贝
local function shallow_copy(orig)
    local copy = {}
    for k, v in pairs(orig) do
        copy[k] = v
    end
    return copy
end

-- ===== 元表 (metatable) =====
local mt = {
    __add = function(a, b)
        return a.value + b.value
    end,
    __index = function(t, k)
        return "默认值"
    end
}

local obj = setmetatable({value = 10}, mt)
print(obj.value)    -- 10
print(obj.unknown)  -- "默认值"（__index）

local obj2 = setmetatable({value = 20}, mt)
print(obj + obj2)   -- 30（__add）
```
