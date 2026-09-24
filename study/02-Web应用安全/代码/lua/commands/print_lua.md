# print_lua

> **分类**：输出
> **说明**：Lua 打印函数

---

## 语法

```lua
print(...)
```

## 输出函数

print / io.write / io.read / tostring

## 格式化

string.format 类似 printf

## 示例代码

```lua
-- 基本输出
print("Hello, World!")
print(42)
print(3.14, "abc", true)

-- 多参数输出（自动用 tab 分隔）
print("a", "b", "c")

-- io.write（不自动换行）
io.write("输入: ")
-- local input = io.read()

-- 格式化输出
local name = "Alice"
local age = 25
print(string.format("姓名: %s, 年龄: %d", name, age))
print(string.format("PI = %.2f", 3.14159))

-- 字符串拼接（用 .. 运算符）
print("你好, " .. name .. "!")

-- 转字符串
print(tostring(42))
print(tostring(true))

-- 表的打印（需要自定义）
local t = {1, 2, 3}
-- print(t)  -- 输出表地址，不是内容

-- 简单打印数组
for i, v in ipairs(t) do
    print(i, v)
end

-- io 操作
io.write("请输入: ")
local input = io.read()
print("你输入了: " .. input)

-- 错误输出
io.stderr:write("错误信息\n")
```
