# Lua 语言基础

## 一、Lua 语言简介

### 1.1 历史
Lua 是由巴西里约热内卢天主教大学（PUC-Rio）的 Roberto Ierusalimschy、Waldemar Celes 和 Luiz Henrique de Figueiredo 于 1993 年开发的一种轻量级脚本语言。其设计目的是为了嵌入应用程序中，从而为应用程序提供灵活的扩展和定制功能。

### 1.2 特点
- **轻量级（Lightweight）**：Lua 标准库很小，编译后仅几百 KB，非常适合资源受限的环境。
- **高效（Efficient）**：Lua 拥有非常快的执行速度，LuaJIT（Just-In-Time 编译器）更是使其性能接近原生 C 代码。
- **嵌入式脚本语言（Embedded Scripting）**：Lua 被设计为可以方便地嵌入到其他语言（主要是 C/C++）编写的程序中使用。
- **C 绑定（C API）**：提供了丰富的 C API，可以方便地与 C/C++ 代码互操作。
- **可移植（Portable）**：Lua 用标准 C 编写，可以在所有主流平台上编译运行。
- **语法简洁**：语法简单优雅，学习曲线平缓。

### 1.3 使用场景

| 领域 | 代表应用 | 说明 |
|------|----------|------|
| **游戏开发** | World of Warcraft、Roblox、Garry's Mod、Angry Birds | 作为游戏逻辑脚本、UI 脚本、Mod 开发语言 |
| **嵌入式/网络** | Nginx/OpenResty、Redis、HAProxy | 在 Nginx 中编写 WAF、负载均衡逻辑；Redis 中执行原子操作脚本 |
| **安全工具扩展** | Wireshark、Nmap、WAF | 协议解析器、NSE 脚本、自定义 WAF 规则 |
| **桌面应用** | Adobe Photoshop Lightroom、WeSay | 插件和扩展机制 |
| **物联网/嵌入式** | NodeMCU、各种嵌入式设备 | 资源受限设备上的脚本控制 |

---

## 二、环境安装

### 2.1 安装 Lua

**Windows：**
```bash
# 方式一：使用 LuaForWindows（推荐，自带 LuaRocks 和常用库）
# 下载地址：https://github.com/rjpcomputing/luaforwindows/releases

# 方式二：使用 scoop
scoop install lua

# 方式三：使用 chocolatey
choco install lua
```

**Linux：**
```bash
# Ubuntu/Debian
sudo apt-get install lua5.4

# CentOS/RHEL
sudo yum install lua
```

**macOS：**
```bash
brew install lua
```

### 2.2 安装 LuaJIT

LuaJIT 是 Lua 的高性能 JIT 编译器，性能比标准 Lua 快数倍。

```bash
# Windows: 下载预编译二进制
# Linux:
sudo apt-get install luajit

# macOS:
brew install luajit
```

### 2.3 安装 LuaRocks

LuaRocks 是 Lua 的包管理器，类似于 Python 的 pip。

```bash
# Windows: LuaForWindows 已自带
# Linux:
sudo apt-get install luarocks

# 安装第三方库
luarocks install luasocket
luarocks install lpeg
```

### 2.4 验证安装

```bash
lua -v       # 查看 Lua 版本
luajit -v    # 查看 LuaJIT 版本
luarocks --version
```

---

## 三、基础语法

### 3.1 第一个程序

```lua
-- 这是单行注释
--[[
    这是
    多行注释
]]

print("Hello, Lua!")
```

运行方式：
```bash
lua 01_hello.lua
luajit 01_hello.lua
```

### 3.2 变量

Lua 中的变量默认是全局的，使用 `local` 关键字声明局部变量。

```lua
-- 全局变量
name = "Lua"

-- 局部变量（推荐尽量使用局部变量，作用域更小，访问更快）
local age = 30

-- 多变量赋值
local a, b, c = 1, 2, 3
```

> **注意**：Lua 中未赋值的变量默认值为 `nil`。

### 3.3 数据类型

Lua 有 8 种基本数据类型：

| 类型 | 说明 | 示例 |
|------|------|------|
| **nil** | 空值，表示无效值 | `local x = nil` |
| **boolean** | 布尔值 | `true`, `false` |
| **number** | 数字（双精度浮点数） | `10`, `3.14`, `0xFF` |
| **string** | 字符串 | `"hello"`, `'world'`, `[[多行]]` |
| **table** | 表（数组+字典的统一体） | `{1, 2, 3}`, `{key = "value"}` |
| **function** | 函数 | `function() end` |
| **userdata** | 用户数据（C 数据结构） | 由 C 扩展提供 |
| **thread** | 协程 | `coroutine.create()` |

使用 `type()` 函数获取值的类型：

```lua
print(type(nil))        --> nil
print(type(true))       --> boolean
print(type(42))         --> number
print(type("hello"))    --> string
print(type({}))         --> table
print(type(print))      --> function
```

### 3.4 变量作用域

```lua
-- 全局变量：整个程序可见
global_var = "I'm global"

function test_scope()
    -- 局部变量：仅在当前块内可见
    local local_var = "I'm local"
    print(local_var)    -- 可以访问
    print(global_var)   -- 可以访问
end

test_scope()
-- print(local_var)      -- 错误：无法访问局部变量
```

> **最佳实践**：尽量使用 `local` 声明变量，避免污染全局命名空间，同时局部变量的访问速度也更快。

---

## 四、运算符

### 4.1 算术运算符

```lua
+   -- 加法
-   -- 减法
*   -- 乘法
/   -- 除法（浮点数）
//  -- 整除（Lua 5.3+）
%   -- 取模
^   -- 幂运算
-   -- 负号
```

### 4.2 关系运算符

```lua
==  -- 等于
~=  -- 不等于
<   -- 小于
>   -- 大于
<=  -- 小于等于
>=  -- 大于等于
```

### 4.3 逻辑运算符

```lua
and -- 逻辑与
or  -- 逻辑或
not -- 逻辑非
```

> **注意**：Lua 中只有 `false` 和 `nil` 为假，其他所有值（包括 `0` 和空字符串 `""`）都为真。

### 4.4 其他运算符

```lua
..  -- 字符串连接
#   -- 长度运算符（获取字符串长度或数组长度）
```

### 4.5 运算符优先级（从高到低）

```
^
not  #  - (一元)
*  /  //  %
+  -
..
<  >  <=  >=  ~=  ==
and
or
```

---

## 五、控制流

### 5.1 if / elseif / else

```lua
local score = 85

if score >= 90 then
    print("优秀")
elseif score >= 80 then
    print("良好")
elseif score >= 60 then
    print("及格")
else
    print("不及格")
end
```

### 5.2 for 循环

**数值 for：**

```lua
-- for 变量 = 起始值, 结束值, 步长 do ... end
for i = 1, 10 do
    print(i)
end

-- 指定步长
for i = 10, 1, -1 do
    print(i)
end
```

**泛型 for：**

```lua
-- 遍历数组（ipairs：按数字索引顺序遍历，遇到 nil 停止）
local arr = {"a", "b", "c"}
for i, v in ipairs(arr) do
    print(i, v)
end

-- 遍历表（pairs：遍历所有键值对，顺序不固定）
local dict = {name = "Lua", age = 30}
for k, v in pairs(dict) do
    print(k, v)
end
```

### 5.3 while 循环

```lua
local i = 1
while i <= 10 do
    print(i)
    i = i + 1
end
```

### 5.4 repeat-until 循环

类似 do-while，条件在循环体之后判断，循环体至少执行一次。

```lua
local i = 1
repeat
    print(i)
    i = i + 1
until i > 10
```

### 5.5 break

`break` 用于跳出当前循环：

```lua
for i = 1, 10 do
    if i == 5 then
        break
    end
    print(i)
end
```

---

## 六、函数

### 6.1 函数定义

```lua
-- 基本定义
function add(a, b)
    return a + b
end

-- 等价于
local add = function(a, b)
    return a + b
end

-- 局部函数（推荐）
local function multiply(a, b)
    return a * b
end
```

### 6.2 多返回值

Lua 函数可以返回多个值：

```lua
function get_user_info()
    return "Alice", 25, "alice@example.com"
end

local name, age, email = get_user_info()
print(name, age, email)

-- 忽略某些返回值
local name2, _, email2 = get_user_info()  -- 用 _ 作为占位符
```

### 6.3 可变参数

使用 `...` 表示可变参数：

```lua
function sum(...)
    local total = 0
    local args = {...}   -- 将可变参数收集到表中
    for i = 1, #args do
        total = total + args[i]
    end
    return total
end

print(sum(1, 2, 3, 4, 5))   --> 15

-- 使用 select 获取参数数量和指定位置参数
function demo(...)
    print("参数个数:", select("#", ...))
    print("第2个参数:", select(2, ...))
end
```

### 6.4 闭包（Closure）

当一个函数内部定义了另一个函数，内部函数可以访问外部函数的局部变量，这种机制称为闭包。

```lua
function counter()
    local count = 0
    return function()
        count = count + 1
        return count
    end
end

local c = counter()
print(c())   --> 1
print(c())   --> 2
print(c())   --> 3
```

### 6.5 尾调用（Tail Call）

当函数的最后一个动作是调用另一个函数时，Lua 会进行尾调用优化，不会增加调用栈深度。

```lua
-- 尾递归实现阶乘
function factorial(n, acc)
    acc = acc or 1
    if n <= 1 then
        return acc
    end
    return factorial(n - 1, n * acc)  -- 尾调用
end

print(factorial(5))   --> 120
```

---

## 七、Table（表）

Table 是 Lua 中唯一的数据结构，既可以作为数组（列表），也可以作为字典（哈希表）。

### 7.1 Table 基础

```lua
-- 空表
local t = {}

-- 初始化
local person = {
    name = "Alice",
    age = 25,
    ["full name"] = "Alice Smith"   -- 键含空格时需用方括号
}

-- 访问
print(person.name)          --> Alice
print(person["age"])        --> 25
print(person["full name"])  --> Alice Smith

-- 修改
person.age = 26
person.city = "Beijing"     -- 新增字段
```

### 7.2 Table 作为数组

使用整数键（从 1 开始）的表可以当作数组使用：

```lua
local arr = {10, 20, 30, 40, 50}

-- 访问
print(arr[1])   --> 10 （注意：Lua 数组下标从 1 开始！）
print(#arr)     --> 5  （获取数组长度）

-- 遍历
for i = 1, #arr do
    print(arr[i])
end

-- 使用 ipairs 遍历（按数字索引顺序，遇到 nil 停止）
for i, v in ipairs(arr) do
    print(i, v)
end
```

> **重要**：Lua 的数组索引从 **1** 开始，而不是 0！

### 7.3 数组操作

```lua
local arr = {"a", "b", "c"}

-- 插入（默认在末尾）
table.insert(arr, "d")          -- arr = {"a", "b", "c", "d"}
table.insert(arr, 2, "x")       -- 在位置 2 插入: {"a", "x", "b", "c", "d"}

-- 删除
table.remove(arr)               -- 删除最后一个
table.remove(arr, 2)            -- 删除位置 2 的元素

-- 排序
table.sort(arr)                 -- 默认升序
table.sort(arr, function(a, b)  -- 自定义排序
    return a > b
end)

-- 连接
local str = table.concat(arr, ", ")  -- 用指定分隔符连接数组元素
```

### 7.4 Table 作为字典/哈希表

```lua
local dict = {
    name = "Lua",
    version = "5.4",
    creator = "PUC-Rio"
}

-- 访问
print(dict.name)        --> Lua
print(dict["version"])  --> 5.4

-- 新增/修改
dict.year = 1993
dict["name"] = "Lua 5.4"

-- 删除
dict.creator = nil

-- 遍历（pairs 遍历所有键值对，顺序不固定）
for k, v in pairs(dict) do
    print(k, v)
end
```

### 7.5 嵌套表

Table 可以任意嵌套：

```lua
local users = {
    {name = "Alice", age = 25},
    {name = "Bob", age = 30},
    {name = "Charlie", age = 35}
}

print(users[1].name)    --> Alice
```

---

## 八、字符串操作

### 8.1 字符串基础

```lua
local s1 = "hello"
local s2 = 'world'
local s3 = [[
    多行字符串
    可以包含换行
]]

-- 字符串连接
local s4 = s1 .. " " .. s2   --> hello world

-- 字符串长度
print(#s1)   --> 5

-- 类型转换
tostring(123)     --> "123"
tonumber("123")   --> 123
```

### 8.2 string 库

```lua
local s = "Hello, Lua World!"

-- 大小写转换
string.upper(s)   --> "HELLO, LUA WORLD!"
string.lower(s)   --> "hello, lua world!"

-- 子串（索引从 1 开始，负数表示从末尾倒数）
string.sub(s, 1, 5)     --> "Hello"
string.sub(s, -6, -1)   --> "World!"

-- 查找
string.find(s, "Lua")   --> 8, 10  （起始位置和结束位置）

-- 替换
string.gsub(s, "World", "LuaJIT")  --> "Hello, Lua LuaJIT!", 1

-- 格式化
string.format("name=%s, age=%d, pi=%.2f", "Alice", 25, math.pi)

-- 重复
string.rep("*", 10)   --> "**********"

-- 反转
string.reverse("abc")  --> "cba"

-- 字符/ASCII码转换
string.char(65)        --> "A"
string.byte("A")       --> 65
```

---

## 九、模式匹配（Pattern Matching）

Lua 没有内置正则表达式，而是使用自己的模式匹配系统，功能类似但语法更简洁。

### 9.1 常用函数

```lua
-- string.find: 查找匹配，返回起始和结束位置
local s = "Hello 123 World"
local start, stop = string.find(s, "%d+")
print(start, stop)   --> 7, 9

-- string.match: 返回第一个匹配的子串
local num = string.match(s, "%d+")
print(num)           --> 123

-- string.gmatch: 返回迭代器，遍历所有匹配
for word in string.gmatch("one two three", "%a+") do
    print(word)
end

-- string.gsub: 全局替换
local result, count = string.gsub("Hello World", "o", "0")
print(result, count)  --> Hell0 W0rld, 2
```

### 9.2 模式语法

| 字符类 | 说明 |
|--------|------|
| `.` | 匹配任意字符 |
| `%a` | 匹配字母 |
| `%d` | 匹配数字 |
| `%w` | 匹配字母和数字 |
| `%s` | 匹配空白字符 |
| `%l` | 匹配小写字母 |
| `%u` | 匹配大写字母 |
| `%p` | 匹配标点符号 |
| `%c` | 匹配控制字符 |
| `%x` | 匹配十六进制数字 |
| `%z` | 匹配空字符（\0） |

> 大写形式表示补集，如 `%A` 匹配非字母，`%D` 匹配非数字。

### 9.3 模式修饰符

| 修饰符 | 说明 |
|--------|------|
| `+` | 匹配 1 次或多次（贪婪） |
| `*` | 匹配 0 次或多次（贪婪） |
| `-` | 匹配 0 次或多次（非贪婪） |
| `?` | 匹配 0 次或 1 次 |

### 9.4 其他模式元素

| 元素 | 说明 |
|------|------|
| `^` | 匹配字符串开头 |
| `$` | 匹配字符串结尾 |
| `[]` | 字符集，如 `[a-z0-9]` |
| `()` | 捕获组 |
| `%bxy` | 平衡匹配（成对的 x 和 y），如 `%b()` 匹配括号内的内容 |

### 9.5 捕获组

```lua
-- 用 () 捕获匹配的部分
local email = "user@example.com"
local user, domain = string.match(email, "(.+)@(.+)")
print(user, domain)   --> user    example.com

-- 替换中使用捕获
local result = string.gsub("Hello World", "(%w+)", "<%1>")
print(result)   --> <Hello> <World>
```

---

## 十、元表（Metatable）与元方法

元表允许我们改变 table 的行为，类似于运算符重载。

### 10.1 基本概念

- **元表（Metatable）**：一个普通的 table，用于定义另一个 table 的行为。
- **元方法（Metamethod）**：元表中的特殊键（以 `__` 开头），对应特定的操作。

```lua
local t = {}
local mt = {}

-- 设置元表
setmetatable(t, mt)

-- 获取元表
getmetatable(t)   --> mt
```

### 10.2 常用元方法

| 元方法 | 对应操作 | 说明 |
|--------|----------|------|
| `__index` | 访问不存在的键 | 可以是 table 或函数 |
| `__newindex` | 给不存在的键赋值 | 可以是 table 或函数 |
| `__add` | `+` 运算符 | |
| `__sub` | `-` 运算符 | |
| `__mul` | `*` 运算符 | |
| `__div` | `/` 运算符 | |
| `__mod` | `%` 运算符 | |
| `__eq` | `==` 运算符 | |
| `__lt` | `<` 运算符 | |
| `__le` | `<=` 运算符 | |
| `__tostring` | `tostring()` | 转字符串表示 |
| `__call` | 像函数一样调用 table | |
| `__len` | `#` 运算符 | 获取长度 |
| `__concat` | `..` 运算符 | 字符串连接 |

### 10.3 `__index` 示例

```lua
local mt = {
    __index = function(t, key)
        return "default value for " .. key
    end
}

local t = setmetatable({name = "Lua"}, mt)
print(t.name)      --> Lua
print(t.unknown)   --> default value for unknown
```

### 10.4 `__add` 示例（运算符重载）

```lua
-- 向量加法
local Vector = {}
Vector.mt = {}

function Vector.new(x, y)
    local v = {x = x, y = y}
    setmetatable(v, Vector.mt)
    return v
end

Vector.mt.__add = function(a, b)
    return Vector.new(a.x + b.x, a.y + b.y)
end

Vector.mt.__tostring = function(v)
    return string.format("(%d, %d)", v.x, v.y)
end

local v1 = Vector.new(1, 2)
local v2 = Vector.new(3, 4)
local v3 = v1 + v2
print(v3)   --> (4, 6)
```

---

## 十一、模块与包

### 11.1 创建模块

```lua
-- mymodule.lua
local M = {}

function M.hello(name)
    return "Hello, " .. name
end

function M.add(a, b)
    return a + b
end

M.version = "1.0"

return M
```

### 11.2 使用模块

```lua
-- 加载模块
local mymodule = require("mymodule")

print(mymodule.hello("Lua"))   --> Hello, Lua
print(mymodule.add(1, 2))      --> 3
print(mymodule.version)        --> 1.0
```

> **说明**：
> - `require` 函数会搜索 Lua 路径（`package.path`）查找模块文件。
> - 模块只会被加载一次，多次 `require` 返回同一个对象。
> - 模块文件需要在 Lua 的搜索路径中，或通过 `package.path` 添加路径。

### 11.3 模块搜索路径

```lua
-- 查看当前搜索路径
print(package.path)

-- 添加自定义路径
package.path = "./?.lua;" .. package.path
```

---

## 十二、协程（Coroutine）

协程是 Lua 的一种协作式多线程机制，与线程不同，协程的切换由程序控制，而非操作系统。

### 12.1 基本操作

```lua
-- 创建协程
local co = coroutine.create(function()
    print("协程开始")
    coroutine.yield(1)       -- 挂起，返回值
    print("协程继续")
    coroutine.yield(2)
    print("协程结束")
    return 3
end)

-- 查看状态
print(coroutine.status(co))   --> suspended

-- 启动/恢复协程
local ok, val = coroutine.resume(co)   -- 协程开始
print(val)                             --> 1

coroutine.resume(co)                    -- 协程继续
coroutine.resume(co)                    -- 协程结束

print(coroutine.status(co))   --> dead
```

### 12.2 协程的状态

- **suspended**：挂起（初始状态和 yield 后）
- **running**：运行中
- **normal**：活跃但未运行（正在 resume 另一个协程）
- **dead**：死亡（执行完毕或出错）

### 12.3 生产者-消费者示例

```lua
-- 生产者
local function producer()
    for i = 1, 5 do
        coroutine.yield("item " .. i)
    end
end

-- 消费者
local co = coroutine.create(producer)
while true do
    local ok, item = coroutine.resume(co)
    if not ok or item == nil then
        break
    end
    print("消费:", item)
end
```

---

## 十三、文件 I/O

### 13.1 简单 I/O

```lua
-- 读取整个文件
local f = io.open("test.txt", "r")
if f then
    local content = f:read("*a")   -- 读取全部
    print(content)
    f:close()
end

-- 写入文件
local f = io.open("output.txt", "w")
if f then
    f:write("Hello, Lua!\n")
    f:write("Second line\n")
    f:close()
end

-- 追加写入
local f = io.open("log.txt", "a")
if f then
    f:write(os.date() .. " - log message\n")
    f:close()
end
```

### 13.2 读取模式

| 模式 | 说明 |
|------|------|
| `"*a"` | 读取整个文件 |
| `"*l"` | 读取一行（去掉换行符），默认模式 |
| `"*L"` | 读取一行（保留换行符） |
| `"*n"` | 读取一个数字 |
| `n` (数字) | 读取 n 个字符 |

### 13.3 逐行读取

```lua
for line in io.lines("test.txt") do
    print(line)
end
```

---

## 十四、Lua 与 C 交互简介

Lua 的一个重要特性是可以方便地与 C/C++ 代码互操作。

### 14.1 C 调用 Lua

```c
#include <lua.h>
#include <lauxlib.h>
#include <lualib.h>

int main() {
    lua_State *L = luaL_newstate();    // 创建 Lua 状态机
    luaL_openlibs(L);                   // 打开标准库

    luaL_dofile(L, "script.lua");       // 执行 Lua 脚本

    // 调用 Lua 函数
    lua_getglobal(L, "my_function");    // 获取函数
    lua_pushnumber(L, 10);              // 压入参数
    lua_pcall(L, 1, 1, 0);              // 调用：1个参数，1个返回值

    double result = lua_tonumber(L, -1); // 获取返回值
    lua_pop(L, 1);                       // 弹出返回值

    lua_close(L);                        // 关闭状态机
    return 0;
}
```

### 14.2 Lua 调用 C

```c
// C 函数
static int l_sin(lua_State *L) {
    double d = luaL_checknumber(L, 1);  // 获取第一个参数
    lua_pushnumber(L, sin(d));          // 压入返回值
    return 1;                           // 返回值个数
}

// 注册函数到 Lua
int luaopen_mylib(lua_State *L) {
    lua_register(L, "mysin", l_sin);
    return 0;
}
```

```lua
-- Lua 中使用
local mylib = require("mylib")
print(mysin(math.pi / 2))   --> 1.0
```

---

## 十五、Lua 在安全领域的应用

### 15.1 Nginx WAF（Web 应用防火墙）

OpenResty（Nginx + LuaJIT）是构建 WAF 的常用平台：

```lua
-- WAF 规则示例（简化版）
local function waf_check()
    local args = ngx.req.get_uri_args()
    for _, val in pairs(args) do
        if type(val) == "string" then
            -- 检测 SQL 注入
            if ngx.re.match(val, [['\s*(or|and)\s+['"]?\w+['"]?\s*=\s*['"]?\w+]], "io") then
                ngx.exit(403)
            end
            -- 检测 XSS
            if ngx.re.match(val, [[<\s*script]], "io") then
                ngx.exit(403)
            end
        end
    end
end

waf_check()
```

### 15.2 Redis 安全脚本

使用 Lua 脚本实现 Redis 原子操作，防止竞争条件：

```lua
-- 限流脚本：限制某个 key 的访问频率
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local window = tonumber(ARGV[2])

local current = redis.call('INCR', key)
if current == 1 then
    redis.call('EXPIRE', key, window)
end

if current > limit then
    return 0  -- 超过限制
else
    return 1  -- 允许访问
end
```

### 15.3 游戏安全

- **反作弊**：很多游戏使用 Lua 作为脚本语言，安全研究人员需要分析 Lua 脚本以发现和防范作弊。
- **Mod 安全**：审查玩家制作的 Lua Mod，防止恶意代码。
- **内存扫描**：通过扫描内存中的 Lua 状态机，检测游戏作弊。

### 15.4 逆向分析

- **Lua 字节码反编译**：分析被编译的 Lua 脚本（如游戏脚本、恶意软件中的 Lua 组件）。
- **混淆与脱壳**：Lua 脚本常被混淆保护，需要脱壳和反混淆分析。
- **动态调试**：Hook Lua 虚拟机的 API 来监控脚本执行。

### 15.5 安全工具扩展

- **Nmap NSE**：Nmap Scripting Engine 使用 Lua 编写各种扫描脚本。
- **Wireshark 协议解析**：使用 Lua 编写自定义协议解析器。
- **自定义安全工具**：利用 Lua 的轻量和嵌入特性，快速开发安全工具原型。

---

## 参考资源

- [Lua 官方网站](https://www.lua.org/)
- [Lua 5.4 参考手册](https://www.lua.org/manual/5.4/)
- [Programming in Lua（第四版）](https://www.lua.org/pil/)
- [OpenResty 官方网站](https://openresty.org/)
- [LuaJIT 官方网站](https://luajit.org/)
- [LuaRocks 包仓库](https://luarocks.org/)
