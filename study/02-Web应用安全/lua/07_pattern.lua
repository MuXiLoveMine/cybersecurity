-- ============================================================
-- 07_pattern.lua - Lua 模式匹配（相当于正则）：find/match/gmatch/gsub、模式语法、捕获组
-- 运行方式: lua 07_pattern.lua 或 luajit 07_pattern.lua
-- ============================================================

-- ---------- 1. 模式匹配函数 ----------
print("========== 模式匹配函数 ==========")

local s = "Hello 123 World 456 Lua 789"

-- 1.1 string.find - 查找匹配，返回起始和结束位置
print("--- string.find ---")
local start, stop = string.find(s, "%d+")   -- 查找数字
print("第一个数字的位置:", start, stop)
print("匹配的内容:", string.sub(s, start, stop))

-- 从指定位置开始查找
local start2, stop2 = string.find(s, "%d+", stop + 1)
print("第二个数字的位置:", start2, stop2)

-- 找不到返回 nil
local not_found = string.find(s, "xyz")
print("找不到:", not_found)

-- 1.2 string.match - 返回第一个匹配的子串
print("\n--- string.match ---")
local num = string.match(s, "%d+")
print("第一个数字:", num)

local word = string.match(s, "%a+")
print("第一个单词:", word)

-- 1.3 string.gmatch - 返回迭代器，遍历所有匹配
print("\n--- string.gmatch ---")
print("所有数字:")
for n in string.gmatch(s, "%d+") do
    print("  ", n)
end

print("所有单词:")
for w in string.gmatch(s, "%a+") do
    print("  ", w)
end

-- 1.4 string.gsub - 全局替换
print("\n--- string.gsub ---")
local result, count = string.gsub(s, "%d+", "#")
print("替换所有数字:", result)
print("替换次数:", count)

print()

-- ---------- 2. 字符类 ----------
print("========== 字符类 ==========")

local s = "Hello Lua 5.4! 你好 123 _abc"

print("原字符串:", s)
print()

-- .  - 任意字符
print(".  任意字符:", string.match(s, "H.llo"))

-- %a - 字母
print("%a - 字母:", string.match(s, "%a+"))

-- %d - 数字
print("%d - 数字:", string.match(s, "%d+"))

-- %w - 字母和数字（单词字符）
print("%w - 字母数字:", string.match(s, "%w+"))

-- %s - 空白字符（空格、制表符等）
print("%s - 空白:", string.match(s, "Lua%s+%d"))

-- %l - 小写字母
print("%l - 小写字母:", string.match(s, "%l+"))

-- %u - 大写字母
print("%u - 大写字母:", string.match(s, "%u+"))

-- %p - 标点符号
print("%p - 标点:", string.match(s, "%p"))

-- %x - 十六进制数字
print("%x - 十六进制:", string.match("0xFF", "%x+"))

-- 大写表示补集
print("\n补集：")
print("%D - 非数字:", string.match("123abc", "%D+"))
print("%A - 非字母:", string.match("abc123", "%A+"))

print()

-- ---------- 3. 模式修饰符 ----------
print("========== 模式修饰符 ==========")

-- +  匹配 1 次或多次（贪婪）
-- *  匹配 0 次或多次（贪婪）
-- -  匹配 0 次或多次（非贪婪/懒惰）
-- ?  匹配 0 次或 1 次

local s = "a123b456c"

print("原字符串:", s)
print()

print("+  (1次或多次, 贪婪):")
print("  %d+ 匹配:", string.match(s, "%d+"))   --> 123

print("*  (0次或多次, 贪婪):")
print("  %d* 在开头:", string.match(s, "%d*"))  --> 空（0次也匹配）
print("  a%d* :", string.match(s, "a%d*"))      --> a123

print("-  (0次或多次, 非贪婪):")
local html = "<div>hello</div>"
print("  贪婪 <.-> :", string.match(html, "<.->"))     --> <div>hello</div> （不对，.是贪婪？）
-- 实际上 Lua 的 . 本身不贪婪，修饰符才决定贪婪性
print("  贪婪 <.*> :", string.match(html, "<.*>"))     --> <div>hello</div> （匹配尽可能多）
print("  非贪婪 <.->:", string.match(html, "<.->"))    --> <div> （匹配尽可能少）

print("?  (0次或1次):")
print("  color 匹配 colour:", string.match("colour", "colou?r"))   --> colour
print("  color 匹配 color:", string.match("color", "colou?r"))     --> color

print()

-- ---------- 4. 锚点 ----------
print("========== 锚点 ==========")

-- ^  匹配字符串开头
-- $  匹配字符串结尾

print("^ 开头锚点：")
print("  'hello' 以 'h' 开头:", string.match("hello", "^h") ~= nil)
print("  'world' 以 'h' 开头:", string.match("world", "^h") ~= nil)

print("$ 结尾锚点：")
print("  'hello' 以 'o' 结尾:", string.match("hello", "o$") ~= nil)
print("  'world' 以 'o' 结尾:", string.match("world", "o$") ~= nil)

-- 同时使用 ^ 和 $ 进行完全匹配
local function is_number(str)
    return string.match(str, "^%d+$") ~= nil
end
print("完全匹配数字：")
print("  '123' 是数字:", is_number("123"))
print("  '12a3' 是数字:", is_number("12a3"))
print("  '12.3' 是数字:", is_number("12.3"))

print()

-- ---------- 5. 字符集 [] ----------
print("========== 字符集 ==========")

-- [abc]     匹配 a、b、c 中的任意一个
-- [a-z]     匹配 a 到 z 的任意小写字母
-- [0-9]     匹配 0 到 9 的任意数字
-- [^abc]    匹配除了 a、b、c 以外的任意字符（取反）

print("[aeiou] 匹配元音字母：")
local vowels = string.gmatch("hello world", "[aeiou]")
for v in vowels do
    io.write(v, " ")
end
print()

print("[a-z]+ 匹配小写单词：")
print("  ", string.match("Hello World", "[a-z]+"))

print("[0-9a-fA-F]+ 匹配十六进制：")
print("  ", string.match("0x1A3F", "[0-9a-fA-F]+"))

print("[^0-9] 匹配非数字：")
print("  ", string.match("123abc", "[^0-9]+"))

print("字符集取反：")
print("  [^abc] 匹配 'def':", string.match("def", "[^abc]+"))

print()

-- ---------- 6. 捕获组 ----------
print("========== 捕获组 ==========")

-- 用 () 捕获匹配的部分

-- 6.1 string.match 中的捕获
print("--- string.match 捕获 ---")
local email = "user@example.com"
local user, domain = string.match(email, "(.+)@(.+)")
print("邮箱:", email)
print("用户名:", user)
print("域名:", domain)

-- 提取日期
local date_str = "2024-01-15"
local year, month, day = string.match(date_str, "(%d+)-(%d+)-(%d+)")
print("日期:", date_str)
print("年:", year, "月:", month, "日:", day)

-- 提取 HTML 标签内容
local html = "<title>Hello Lua</title>"
local tag, content = string.match(html, "<(%w+)>(.*)</%1>")
print("HTML 标签:", tag)
print("标签内容:", content)

-- 6.2 string.gsub 中的捕获
print("\n--- string.gsub 捕获 ---")

-- %1, %2 表示第 1、第 2 个捕获组
local result = string.gsub("Hello World", "(%w+)", "<%1>")
print("单词加尖括号:", result)

-- 交换位置
local result2 = string.gsub("first last", "(%w+) (%w+)", "%2, %1")
print("交换姓名:", result2)

-- 电话号码格式化
local phone = "13800001234"
local formatted = string.gsub(phone, "(%d%d%d)(%d%d%d%d)(%d%d%d%d)", "%1-%2-%3")
print("电话格式化:", formatted)

-- 6.3 string.gmatch 中的捕获
print("\n--- string.gmatch 捕获 ---")

local text = "name=Alice age=25 city=Beijing"
print("键值对解析：")
for key, value in string.gmatch(text, "(%w+)=(%w+)") do
    print("  ", key, "=", value)
end

print()

-- ---------- 7. 平衡匹配 %b ----------
print("========== 平衡匹配 %b ==========")

-- %bxy 匹配成对的 x 和 y 之间的内容（包括 x 和 y）
-- 常用于匹配括号、引号等成对的结构

local s = "a (b (c) d) e"
print("原字符串:", s)

-- %b() 匹配平衡的括号
local matched = string.match(s, "%b()")
print("匹配平衡括号:", matched)   --> (b (c) d)

-- 匹配引号
local s2 = '他说："你好，Lua是"非常"有趣的语言"'
print("\n原字符串:", s2)
print("匹配引号:", string.match(s2, '%b""'))

-- 匹配 HTML 标签
local html = "<div><p>Hello</p></div>"
print("\nHTML:", html)
print("匹配标签:", string.match(html, "%b<>"))

print()

-- ---------- 8. 常用模式示例 ----------
print("========== 常用模式示例 ==========")

-- 8.1 邮箱验证
local function is_email(str)
    return string.match(str, "^[%w%.%-_]+@[%w%.%-]+%.%a+$") ~= nil
end
print("邮箱验证：")
print("  user@example.com:", is_email("user@example.com"))
print("  invalid-email:", is_email("invalid-email"))

-- 8.2 手机号码验证（中国）
local function is_phone(str)
    return string.match(str, "^1[3-9]%d%d%d%d%d%d%d%d%d$") ~= nil
end
print("\n手机号验证：")
print("  13812345678:", is_phone("13812345678"))
print("  12345678901:", is_phone("12345678901"))

-- 8.3 IP 地址验证（简化版）
local function is_ip(str)
    local a, b, c, d = string.match(str, "^(%d+)%.(%d+)%.(%d+)%.(%d+)$")
    if not a then return false end
    a, b, c, d = tonumber(a), tonumber(b), tonumber(c), tonumber(d)
    return a <= 255 and b <= 255 and c <= 255 and d <= 255
end
print("\nIP 地址验证：")
print("  192.168.1.1:", is_ip("192.168.1.1"))
print("  256.1.1.1:", is_ip("256.1.1.1"))

-- 8.4 URL 提取
local url = "https://www.example.com:8080/path/page.html?query=123"
print("\nURL 解析:", url)
local protocol, host, port, path = string.match(url, "^(%w+)://([^:/]+):?(%d*)(.*)")
print("  协议:", protocol)
print("  主机:", host)
print("  端口:", port ~= "" and port or "默认")
print("  路径:", path)

-- 8.5 提取所有 URL
local text = "访问 https://www.lua.org 和 http://example.com 了解更多"
print("\n提取所有 URL：")
for u in string.gmatch(text, "%w+://[%w%.%-/]+") do
    print("  ", u)
end

print()

-- ---------- 9. 实战：日志解析 ----------
print("========== 实战：日志解析 ==========")

-- 模拟 Nginx 日志
local log_line = '192.168.1.100 - - [15/Jan/2024:10:30:45 +0800] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0"'

local ip, time, method, path, status, size, ua = string.match(log_line,
    '(%S+) %S+ %S+ %[(.-)%] "(%w+) (%S+) %S+" (%d+) (%d+) %S+ "(.-)"'
)

print("日志解析结果：")
print("  IP:", ip)
print("  时间:", time)
print("  方法:", method)
print("  路径:", path)
print("  状态码:", status)
print("  响应大小:", size, "字节")
print("  User-Agent:", ua)

print()
print("========== 示例结束 ==========")
