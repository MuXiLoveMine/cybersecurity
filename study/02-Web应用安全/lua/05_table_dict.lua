-- ============================================================
-- 05_table_dict.lua - table 作为字典：创建、增删改查、遍历、嵌套表、词频统计
-- 运行方式: lua 05_table_dict.lua 或 luajit 05_table_dict.lua
-- ============================================================

-- ---------- 1. 字典的创建 ----------
print("========== 字典的创建 ==========")

-- 方式1：直接初始化
local person = {
    name = "张三",
    age = 25,
    city = "北京",
    job = "程序员"
}
print("person.name:", person.name)

-- 方式2：创建空表后添加
local dict = {}
dict["key1"] = "value1"
dict.key2 = "value2"   -- 语法糖，等价于 dict["key2"]
print("dict.key1:", dict.key1)
print("dict.key2:", dict["key2"])

-- 键名含特殊字符时，必须用方括号语法
local special = {
    ["user-name"] = "Alice",
    ["123"] = "数字键"
}
print("special['user-name']:", special["user-name"])
print("special['123']:", special["123"])

-- 键可以是任意类型（除了 nil）
local mixed = {}
mixed[1] = "数字键"
mixed["name"] = "字符串键"
mixed[true] = "布尔键"
mixed[{}] = "table 键"   -- 用 table 作为键（不常用）
print("mixed[1]:", mixed[1])
print("mixed[true]:", mixed[true])

print()

-- ---------- 2. 访问与修改 ----------
print("========== 访问与修改 ==========")

local user = {
    name = "Bob",
    age = 30,
    email = "bob@example.com"
}

-- 访问（两种方式）
print("姓名:", user.name)          -- 点语法（键为有效标识符时）
print("邮箱:", user["email"])      -- 方括号语法（通用）

-- 访问不存在的键返回 nil
print("不存在的键:", user.phone)   --> nil

-- 修改
user.age = 31
print("修改后年龄:", user.age)

-- 新增
user.phone = "138-0000-0000"
print("新增电话:", user.phone)

-- 删除（赋值为 nil）
user.email = nil
print("删除 email 后:", user.email)  --> nil

print()

-- ---------- 3. 遍历字典（pairs） ----------
print("========== 遍历字典 ==========")

local config = {
    host = "localhost",
    port = 8080,
    timeout = 30,
    debug = true,
    log_level = "info"
}

-- 使用 pairs 遍历所有键值对
-- 注意：pairs 遍历顺序不固定！
print("pairs 遍历：")
for k, v in pairs(config) do
    print("  ", k, "=", v, "(" .. type(v) .. ")")
end

-- 只遍历键
print("\n所有键：")
for k in pairs(config) do
    print("  -", k)
end

-- 只遍历值
print("\n所有值：")
for _, v in pairs(config) do
    print("  -", v)
end

print()

-- ---------- 4. 字典的常用操作 ----------
print("========== 字典的常用操作 ==========")

-- 4.1 判断键是否存在
local function has_key(tbl, key)
    return tbl[key] ~= nil
end

local dict = {a = 1, b = 2, c = 3}
print("有键 'a' 吗?", has_key(dict, "a"))   --> true
print("有键 'z' 吗?", has_key(dict, "z"))   --> false

-- 注意：如果值可能是 nil，则不能用上面的方法
-- 更可靠的方法：使用 rawget 或 next
local function has_key_safe(tbl, key)
    return rawget(tbl, key) ~= nil or next(tbl, key) ~= nil
    -- 实际上 rawget 就够了，因为如果 key 存在但值为 nil，rawget 返回 nil
    -- 但 Lua 中值为 nil 的键等同于不存在
end

-- 4.2 获取键的数量（字典大小）
local function dict_size(tbl)
    local count = 0
    for _ in pairs(tbl) do
        count = count + 1
    end
    return count
end
print("字典大小:", dict_size(dict))   --> 3

-- 4.3 获取所有键的列表
local function keys(tbl)
    local result = {}
    for k in pairs(tbl) do
        table.insert(result, k)
    end
    return result
end
local ks = keys(dict)
print("所有键:", table.concat(ks, ", "))

-- 4.4 获取所有值的列表
local function values(tbl)
    local result = {}
    for _, v in pairs(tbl) do
        table.insert(result, v)
    end
    return result
end
local vs = values(dict)
print("所有值:", table.concat(vs, ", "))

-- 4.5 合并字典
local function merge(dest, src)
    for k, v in pairs(src) do
        dest[k] = v
    end
    return dest
end

local d1 = {a = 1, b = 2}
local d2 = {b = 3, c = 4}
merge(d1, d2)   -- d2 的值会覆盖 d1 中相同的键
print("合并后 d1.b =", d1.b, "d1.c =", d1.c)

print()

-- ---------- 5. 嵌套表 ----------
print("========== 嵌套表 ==========")

-- 多维数组（二维数组）
local matrix = {
    {1, 2, 3},
    {4, 5, 6},
    {7, 8, 9}
}
print("3x3 矩阵：")
for i = 1, #matrix do
    local row = {}
    for j = 1, #matrix[i] do
        table.insert(row, tostring(matrix[i][j]))
    end
    print("  " .. table.concat(row, " "))
end
print("matrix[2][3] =", matrix[2][3])

-- 嵌套字典
local company = {
    name = "Acme Corp",
    address = {
        street = "中关村大街1号",
        city = "北京",
        zip = "100000"
    },
    employees = {
        {name = "Alice", role = "工程师", salary = 15000},
        {name = "Bob", role = "设计师", salary = 12000},
        {name = "Charlie", role = "产品经理", salary = 18000}
    }
}

print("\n公司名称:", company.name)
print("公司地址:", company.address.city .. company.address.street)
print("员工数量:", #company.employees)
print("第一位员工:", company.employees[1].name)

-- 遍历员工
print("\n员工列表：")
for i, emp in ipairs(company.employees) do
    print(string.format("  %d. %s - %s (薪资: %d)", i, emp.name, emp.role, emp.salary))
end

print()

-- ---------- 6. 综合练习：词频统计 ----------
print("========== 综合练习：词频统计 ==========")

local text = "hello world hello lua world hello world lua lua lua"

-- 统计每个单词出现的次数
local word_count = {}
for word in string.gmatch(text, "%a+") do
    if word_count[word] then
        word_count[word] = word_count[word] + 1
    else
        word_count[word] = 1
    end
end

print("词频统计结果：")
for word, count in pairs(word_count) do
    print(string.format("  %-8s: %d 次", word, count))
end

-- 按出现次数排序
print("\n按次数排序：")
local words = {}
for word in pairs(word_count) do
    table.insert(words, word)
end
table.sort(words, function(a, b)
    return word_count[a] > word_count[b]
end)
for _, word in ipairs(words) do
    print(string.format("  %-8s: %d 次", word, word_count[word]))
end

print()

-- ---------- 7. 综合练习：电话簿 ----------
print("========== 综合练习：电话簿 ==========")

local phone_book = {
    ["张三"] = "138-0001-0001",
    ["李四"] = "138-0002-0002",
    ["王五"] = "138-0003-0003"
}

-- 添加联系人
phone_book["赵六"] = "138-0004-0004"

-- 查找
print("张三的电话:", phone_book["张三"])
print("未知的电话:", phone_book["无名氏"])   --> nil

-- 修改
phone_book["张三"] = "139-9999-9999"
print("张三的新电话:", phone_book["张三"])

-- 删除
phone_book["李四"] = nil
print("李四删除后:", phone_book["李四"] and "存在" or "不存在")

-- 遍历所有联系人
print("\n所有联系人：")
for name, phone in pairs(phone_book) do
    print(string.format("  %s: %s", name, phone))
end

print()
print("========== 示例结束 ==========")
