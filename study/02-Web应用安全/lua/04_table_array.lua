-- ============================================================
-- 04_table_array.lua - table 作为数组：创建、增删改查、遍历、table 库函数
-- 运行方式: lua 04_table_array.lua 或 luajit 04_table_array.lua
-- ============================================================

-- ---------- 1. 数组的创建 ----------
print("========== 数组的创建 ==========")

-- 方式1：直接初始化
local arr1 = {"苹果", "香蕉", "橙子", "葡萄"}
print("arr1 长度:", #arr1)

-- 方式2：创建空表后添加
local arr2 = {}
arr2[1] = "a"
arr2[2] = "b"
arr2[3] = "c"
print("arr2 长度:", #arr2)

-- 注意：Lua 数组索引从 1 开始！
-- 如果索引不连续，# 运算符的结果可能不符合预期
local arr3 = {[1] = "a", [3] = "c"}
print("arr3 长度:", #arr3)   -- 结果不确定，因为有"洞"

-- 数字数组
local nums = {10, 20, 30, 40, 50}
print("nums 长度:", #nums)

print()

-- ---------- 2. 访问与修改 ----------
print("========== 访问与修改 ==========")

local fruits = {"苹果", "香蕉", "橙子", "葡萄", "西瓜"}

-- 通过索引访问（从 1 开始）
print("第1个:", fruits[1])
print("第3个:", fruits[3])
print("最后一个:", fruits[#fruits])

-- 修改元素
fruits[2] = "香蕉（改良版）"
print("修改后第2个:", fruits[2])

-- 添加到末尾
fruits[#fruits + 1] = "芒果"
print("添加后长度:", #fruits)
print("最后一个:", fruits[#fruits])

print()

-- ---------- 3. 遍历数组 ----------
print("========== 遍历数组 ==========")

local colors = {"红", "橙", "黄", "绿", "青", "蓝", "紫"}

-- 方式1：数值 for 循环
print("方式1 - 数值 for：")
for i = 1, #colors do
    print("  ", i, ":", colors[i])
end

-- 方式2：ipairs 迭代器
-- ipairs 从索引 1 开始，按顺序遍历，遇到 nil 停止
print("方式2 - ipairs：")
for i, v in ipairs(colors) do
    print("  ", i, ":", v)
end

-- 方式3：pairs 迭代器（不推荐用于纯数组，顺序不保证）
print("方式3 - pairs（顺序不固定）：")
for k, v in pairs(colors) do
    print("  ", k, ":", v)
end

print()

-- ---------- 4. table.insert ----------
print("========== table.insert ==========")

local arr = {"a", "b", "c"}
print("初始:", table.concat(arr, ", "))

-- 在末尾插入（默认）
table.insert(arr, "d")
print("末尾插入 d:", table.concat(arr, ", "))

-- 在指定位置插入
table.insert(arr, 2, "x")   -- 在位置 2 插入
print("位置2插入 x:", table.concat(arr, ", "))

table.insert(arr, 1, "first")
print("开头插入 first:", table.concat(arr, ", "))

print()

-- ---------- 5. table.remove ----------
print("========== table.remove ==========")

local arr = {"a", "b", "c", "d", "e"}
print("初始:", table.concat(arr, ", "))

-- 删除最后一个元素
local last = table.remove(arr)
print("删除最后一个:", last, "→", table.concat(arr, ", "))

-- 删除指定位置的元素
local removed = table.remove(arr, 2)
print("删除位置2:", removed, "→", table.concat(arr, ", "))

-- 删除第一个元素
local first = table.remove(arr, 1)
print("删除第一个:", first, "→", table.concat(arr, ", "))

print()

-- ---------- 6. table.sort ----------
print("========== table.sort ==========")

local nums = {5, 2, 9, 1, 7, 3, 8, 4, 6}
print("排序前:", table.concat(nums, ", "))

-- 默认升序排序
table.sort(nums)
print("升序排序:", table.concat(nums, ", "))

-- 自定义排序函数：降序
table.sort(nums, function(a, b)
    return a > b
end)
print("降序排序:", table.concat(nums, ", "))

-- 字符串排序
local words = {"banana", "apple", "cherry", "date"}
print("字符串排序前:", table.concat(words, ", "))
table.sort(words)
print("字符串排序后:", table.concat(words, ", "))

-- 复杂对象排序
local people = {
    {name = "Alice", age = 25},
    {name = "Bob", age = 30},
    {name = "Charlie", age = 20}
}
print("按年龄排序：")
table.sort(people, function(a, b)
    return a.age < b.age
end)
for _, p in ipairs(people) do
    print("  ", p.name, ":", p.age, "岁")
end

print()

-- ---------- 7. table.concat ----------
print("========== table.concat ==========")

local arr = {"Hello", "Lua", "World"}

-- 默认无分隔符
print("无分隔符:", table.concat(arr))

-- 指定分隔符
print("空格分隔:", table.concat(arr, " "))
print("逗号分隔:", table.concat(arr, ", "))
print("换行分隔:")
print(table.concat(arr, "\n"))

-- 指定起始和结束位置
print("第2到第3个:", table.concat(arr, "-", 2, 3))

print()

-- ---------- 8. 其他数组操作 ----------
print("========== 其他数组操作 ==========")

-- 8.1 查找元素（自己实现）
local function index_of(arr, value)
    for i, v in ipairs(arr) do
        if v == value then
            return i
        end
    end
    return nil
end

local letters = {"a", "b", "c", "d", "e"}
print("'c' 的索引:", index_of(letters, "c"))
print("'z' 的索引:", index_of(letters, "z"))  --> nil

-- 8.2 数组反转
local function reverse(arr)
    local result = {}
    for i = #arr, 1, -1 do
        table.insert(result, arr[i])
    end
    return result
end

local reversed = reverse({1, 2, 3, 4, 5})
print("反转数组:", table.concat(reversed, ", "))

-- 8.3 数组拷贝
local function copy(arr)
    local result = {}
    for i, v in ipairs(arr) do
        result[i] = v
    end
    return result
end

local original = {10, 20, 30}
local copied = copy(original)
copied[1] = 99
print("原数组:", table.concat(original, ", "))
print("拷贝后修改:", table.concat(copied, ", "))

-- 8.4 数组合并
local function merge(arr1, arr2)
    local result = copy(arr1)
    for _, v in ipairs(arr2) do
        table.insert(result, v)
    end
    return result
end

local merged = merge({1, 2, 3}, {4, 5, 6})
print("合并数组:", table.concat(merged, ", "))

print()

-- ---------- 9. 综合练习：栈和队列 ----------
print("========== 综合练习：栈和队列 ==========")

-- 栈（后进先出）- 用 table.insert/remove 在末尾操作
print("栈操作：")
local stack = {}
table.insert(stack, "A")   -- 入栈
table.insert(stack, "B")
table.insert(stack, "C")
print("栈内容:", table.concat(stack, " → "))
print("出栈:", table.remove(stack))
print("出栈:", table.remove(stack))
print("剩余:", table.concat(stack, " → "))

-- 队列（先进先出）- 末尾插入，开头删除
print("\n队列操作：")
local queue = {}
table.insert(queue, "任务1")
table.insert(queue, "任务2")
table.insert(queue, "任务3")
print("队列内容:", table.concat(queue, " → "))
print("出队:", table.remove(queue, 1))
print("出队:", table.remove(queue, 1))
print("剩余:", table.concat(queue, " → "))

print()
print("========== 示例结束 ==========")
