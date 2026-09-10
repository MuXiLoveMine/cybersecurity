# Python 语言基础

> 本文档系统介绍 Python 编程语言的核心知识，从基础语法到常用库，配合 python 目录中的代码示例，帮助快速掌握 Python 脚本开发能力，为安全工具开发和自动化测试奠定基础。

---

## 目录

- [第一章：Python 概述](#第一章python-概述)
- [第二章：基础语法](#第二章基础语法)
- [第三章：数据类型](#第三章数据类型)
- [第四章：列表操作](#第四章列表操作)
- [第五章：字典操作](#第五章字典操作)
- [第六章：字符串操作](#第六章字符串操作)
- [第七章：条件判断与循环](#第七章条件判断与循环)
- [第八章：函数](#第八章函数)
- [第九章：文件操作](#第九章文件操作)
- [第十章：模块与包](#第十章模块与包)
- [第十一章：正则表达式（re 模块）](#第十一章正则表达式re-模块)
- [第十二章：网络请求（requests 库）](#第十二章网络请求requests-库)
- [第十三章：异常处理](#第十三章异常处理)
- [第十四章：简单脚本编写](#第十四章简单脚本编写)
- [附录：代码示例索引](#附录代码示例索引)

---

## 第一章：Python 概述

### 1.1 什么是 Python

Python 是一种高级、解释型、通用的编程语言，由 Guido van Rossum 于 1991 年首次发布。Python 以简洁清晰的语法和丰富的标准库著称，被广泛用于 Web 开发、数据科学、人工智能、自动化运维和网络安全等领域。

**Python 的特点**：

| 特点 | 说明 |
|------|------|
| **语法简洁** | 缩进代替花括号，代码可读性高 |
| **解释执行** | 不需要编译，逐行解释运行 |
| **跨平台** | 支持 Windows、Linux、macOS 等 |
| **丰富的库** | 标准库 + PyPI 海量第三方库 |
| **面向对象** | 支持面向对象编程 |
| **动态类型** | 变量类型运行时确定 |

### 1.2 Python 版本

- **Python 2**：已于 2020 年停止维护，不再推荐使用
- **Python 3**：当前主流版本，最新版本为 3.12+

本教程基于 **Python 3**。

### 1.3 安装与运行

```bash
# 检查 Python 版本
python3 --version
python --version    # Windows

# 交互式运行（REPL）
python3
>>> print("Hello")

# 运行脚本
python3 script.py
```

### 1.4 第一个 Python 程序

```python
# hello.py
print("Hello, World!")
```

---

## 第二章：基础语法

### 2.1 变量与命名

```python
# 变量定义（不需要声明类型）
name = "张三"
age = 25
height = 1.75
is_student = True

# 变量命名规则
# - 由字母、数字、下划线组成
# - 不能以数字开头
# - 区分大小写
# - 不能使用关键字

# 多变量赋值
a = b = c = 10
x, y, z = 1, 2, 3

# 查看变量类型
print(type(name))    # <class 'str'>
print(type(age))     # <class 'int'>
```

### 2.2 注释

```python
# 这是单行注释

"""
这是多行注释
可以写很多行
通常用于函数/类的文档字符串
"""
```

### 2.3 输入输出

```python
# 输出
print("Hello")
print("姓名:", name, "年龄:", age)
print(f"姓名: {name}, 年龄: {age}")    # f-string（推荐）
print("姓名: %s, 年龄: %d" % (name, age))  # 格式化（旧风格）
print("姓名: {}, 年龄: {}".format(name, age))  # format 方法

# 输入
name = input("请输入你的名字：")    # 返回字符串
age = int(input("请输入年龄："))     # 需要手动转类型
```

### 2.4 缩进

Python 使用缩进来表示代码块（代替其他语言的花括号），通常用 4 个空格：

```python
if age >= 18:
    print("成年")      # 缩进 4 空格
    print("可以投票")
else:
    print("未成年")
```

### 2.5 运算符

#### 算术运算符

| 运算符 | 说明 | 示例 |
|--------|------|------|
| `+` | 加 | `3 + 2 = 5` |
| `-` | 减 | `3 - 2 = 1` |
| `*` | 乘 | `3 * 2 = 6` |
| `/` | 除（浮点） | `7 / 2 = 3.5` |
| `//` | 整除 | `7 // 2 = 3` |
| `%` | 取余 | `7 % 2 = 1` |
| `**` | 幂 | `3 ** 2 = 9` |

#### 比较运算符

| 运算符 | 说明 |
|--------|------|
| `==` | 等于 |
| `!=` | 不等于 |
| `>` | 大于 |
| `<` | 小于 |
| `>=` | 大于等于 |
| `<=` | 小于等于 |

#### 逻辑运算符

| 运算符 | 说明 |
|--------|------|
| `and` | 与（两边都为真才为真） |
| `or` | 或（一边为真就为真） |
| `not` | 非（取反） |

#### 位运算符

| 运算符 | 说明 |
|--------|------|
| `&` | 按位与 |
| `\|` | 按位或 |
| `^` | 按位异或 |
| `~` | 按位取反 |
| `<<` | 左移 |
| `>>` | 右移 |

#### 赋值运算符

| 运算符 | 示例 | 等价于 |
|--------|------|--------|
| `=` | `a = 5` | - |
| `+=` | `a += 3` | `a = a + 3` |
| `-=` | `a -= 3` | `a = a - 3` |
| `*=` | `a *= 3` | `a = a * 3` |
| `/=` | `a /= 3` | `a = a / 3` |

---

## 第三章：数据类型

### 3.1 基本数据类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `int` | 整数 | `10`, `-5`, `0x1A` |
| `float` | 浮点数 | `3.14`, `1.5e2` |
| `bool` | 布尔值 | `True`, `False` |
| `str` | 字符串 | `"hello"`, `'world'` |
| `list` | 列表 | `[1, 2, 3]` |
| `tuple` | 元组 | `(1, 2, 3)` |
| `dict` | 字典 | `{"name": "张三"}` |
| `set` | 集合 | `{1, 2, 3}` |
| `NoneType` | 空值 | `None` |

### 3.2 类型转换

```python
# 转整数
int("123")       # 123
int(3.14)        # 3

# 转浮点数
float("3.14")    # 3.14
float(10)        # 10.0

# 转字符串
str(123)         # "123"
str(3.14)        # "3.14"

# 转布尔
bool(0)          # False
bool(1)          # True
bool("")         # False
bool("hello")    # True
bool([])         # False
```

### 3.3 类型判断

```python
x = 10
print(type(x))           # <class 'int'>
print(isinstance(x, int))    # True
print(isinstance(x, (int, float)))  # True（判断是否为多种类型之一）
```

---

## 第四章：列表操作

### 4.1 列表定义

列表（List）是有序、可变、可重复的元素集合。

```python
# 创建列表
fruits = ["apple", "banana", "cherry"]
numbers = [1, 2, 3, 4, 5]
mixed = [1, "hello", 3.14, True]
empty = []    # 空列表
```

### 4.2 访问元素

```python
fruits = ["apple", "banana", "cherry", "date"]

# 通过索引访问（从 0 开始）
print(fruits[0])     # apple
print(fruits[2])     # cherry

# 负索引（从右往左）
print(fruits[-1])    # date
print(fruits[-2])    # cherry

# 切片（左闭右开）
print(fruits[1:3])   # ['banana', 'cherry']
print(fruits[:2])    # ['apple', 'banana']
print(fruits[2:])    # ['cherry', 'date']
print(fruits[::2])   # ['apple', 'cherry']（步长 2）
print(fruits[::-1])  # ['date', 'cherry', 'banana', 'apple']（反转）
```

### 4.3 列表操作

```python
fruits = ["apple", "banana"]

# 添加元素
fruits.append("cherry")       # 末尾添加: ['apple', 'banana', 'cherry']
fruits.insert(1, "orange")    # 指定位置插入: ['apple', 'orange', 'banana', 'cherry']
fruits.extend(["date", "fig"])  # 合并另一个列表

# 删除元素
fruits.remove("banana")       # 删除指定值
del fruits[0]                 # 删除指定索引
last = fruits.pop()           # 弹出最后一个元素
fruits.pop(1)                 # 弹出指定索引元素

# 修改
fruits[0] = "grape"

# 查找
print(fruits.index("cherry"))    # 返回索引，找不到报错
print("apple" in fruits)         # 判断是否存在（返回 True/False）
print(fruits.count("apple"))     # 统计出现次数

# 长度
print(len(fruits))

# 排序
fruits.sort()                 # 升序排序（修改原列表）
fruits.sort(reverse=True)     # 降序排序
sorted_fruits = sorted(fruits)   # 返回新列表，不修改原列表

# 反转
fruits.reverse()

# 清空
fruits.clear()
```

### 4.4 遍历列表

```python
fruits = ["apple", "banana", "cherry"]

# 方式一：遍历元素
for fruit in fruits:
    print(fruit)

# 方式二：带索引遍历
for i, fruit in enumerate(fruits):
    print(f"{i}: {fruit}")

# 方式三：通过索引
for i in range(len(fruits)):
    print(fruits[i])
```

### 4.5 列表推导式

```python
# 快速生成列表
squares = [x**2 for x in range(10)]        # [0, 1, 4, 9, 16, ..., 81]
evens = [x for x in range(10) if x % 2 == 0]  # [0, 2, 4, 6, 8]

# 等价于
squares = []
for x in range(10):
    squares.append(x**2)
```

### 4.6 其他常用操作

```python
# 列表拼接
list1 = [1, 2, 3]
list2 = [4, 5, 6]
list3 = list1 + list2    # [1, 2, 3, 4, 5, 6]

# 复制
list_copy = list1.copy()
list_copy = list1[:]
list_copy = list(list1)

# 最大值、最小值、求和
nums = [3, 1, 4, 1, 5, 9, 2, 6]
print(max(nums))    # 9
print(min(nums))    # 1
print(sum(nums))    # 31
```

---

## 第五章：字典操作

### 5.1 字典定义

字典（Dict）是无序的键值对集合，键必须唯一且不可变（字符串、数字、元组）。

```python
# 创建字典
person = {
    "name": "张三",
    "age": 25,
    "city": "北京"
}

empty = {}    # 空字典
```

### 5.2 访问字典

```python
person = {"name": "张三", "age": 25, "city": "北京"}

# 方式一：键索引（键不存在会报错）
print(person["name"])      # 张三

# 方式二：get 方法（键不存在返回默认值，推荐）
print(person.get("age"))          # 25
print(person.get("gender", "未知"))  # 未知（键不存在返回默认值）

# 所有键 / 值 / 键值对
print(person.keys())       # dict_keys(['name', 'age', 'city'])
print(person.values())     # dict_values(['张三', 25, '北京'])
print(person.items())      # dict_items([('name', '张三'), ...])
```

### 5.3 字典操作

```python
person = {"name": "张三", "age": 25}

# 添加/修改
person["city"] = "北京"     # 添加新键
person["age"] = 26          # 修改已有键

# 批量更新
person.update({"job": "工程师", "city": "上海"})

# 删除
del person["age"]           # 删除指定键
age = person.pop("age")     # 弹出指定键
person.popitem()            # 弹出最后一个键值对

# 判断键是否存在
print("name" in person)     # True
print("gender" in person)   # False

# 长度
print(len(person))

# 清空
person.clear()
```

### 5.4 遍历字典

```python
person = {"name": "张三", "age": 25, "city": "北京"}

# 遍历键
for key in person:
    print(key, person[key])

# 遍历键值对（推荐）
for key, value in person.items():
    print(f"{key}: {value}")

# 遍历值
for value in person.values():
    print(value)
```

### 5.5 字典推导式

```python
# 快速生成字典
squares = {x: x**2 for x in range(5)}
# {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# 带条件
even_squares = {x: x**2 for x in range(10) if x % 2 == 0}
```

---

## 第六章：字符串操作

### 6.1 字符串定义

```python
# 单引号、双引号都可以
s1 = 'hello'
s2 = "world"

# 三引号（多行字符串）
s3 = """
第一行
第二行
第三行
"""

# 原始字符串（不转义）
path = r"C:\Users\name\Desktop"   # \ 不被当作转义符
```

### 6.2 字符串拼接与格式化

```python
name = "张三"
age = 25

# 加号拼接
s = "姓名：" + name + "，年龄：" + str(age)

# f-string（推荐，Python 3.6+）
s = f"姓名：{name}，年龄：{age}"
s = f"明年年龄：{age + 1}"    # 可以包含表达式

# % 格式化（旧风格）
s = "姓名：%s，年龄：%d" % (name, age)

# format 方法
s = "姓名：{}，年龄：{}".format(name, age)
s = "姓名：{0}，年龄：{1}".format(name, age)
s = "姓名：{n}，年龄：{a}".format(n=name, a=age)
```

### 6.3 常用字符串方法

```python
s = "Hello World"

# 大小写转换
print(s.upper())       # HELLO WORLD
print(s.lower())       # hello world
print(s.title())       # Hello World
print(s.capitalize())  # Hello world
print(s.swapcase())    # hELLO wORLD

# 去除空白
s2 = "  hello  "
print(s2.strip())      # "hello"（去除两端）
print(s2.lstrip())     # "hello  "（去除左端）
print(s2.rstrip())     # "  hello"（去除右端）

# 查找
print(s.find("World"))   # 6（返回索引，找不到返回 -1）
print(s.index("World"))  # 6（找不到报错）
print(s.count("l"))      # 3（出现次数）
print(s.startswith("He"))   # True
print(s.endswith("ld"))     # True

# 替换
print(s.replace("World", "Python"))   # Hello Python
print(s.replace("l", "L"))             # HeLLo WorLd

# 分割与连接
s3 = "apple,banana,cherry"
print(s3.split(","))     # ['apple', 'banana', 'cherry']
print(s3.split(",", 1))  # ['apple', 'banana,cherry']（分割 1 次）

fruits = ["apple", "banana", "cherry"]
print("-".join(fruits))  # apple-banana-cherry

# 判断
s4 = "12345"
print(s4.isdigit())     # True（是否全为数字）
print(s4.isalpha())     # False（是否全为字母）
print(s4.isalnum())     # True（是否全为字母或数字）
print(s4.isspace())     # False（是否全为空白）

# 填充对齐
s5 = "hello"
print(s5.center(10))    # "  hello   "（居中）
print(s5.ljust(10))     # "hello     "（左对齐）
print(s5.rjust(10, "0"))  # "00000hello"（右对齐，补0）
```

### 6.4 字符串切片

字符串和列表一样支持切片操作：

```python
s = "Hello World"
print(s[0])       # H
print(s[-1])      # d
print(s[0:5])     # Hello
print(s[6:])      # World
print(s[::2])     # HloWrd
print(s[::-1])    # dlroW olleH（反转）
```

---

## 第七章：条件判断与循环

### 7.1 if 条件判断

```python
age = 20

if age >= 18:
    print("成年")
    print("可以投票")
elif age >= 13:
    print("青少年")
else:
    print("儿童")

# 多条件
score = 85
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 60:
    grade = "C"
else:
    grade = "D"

# 三目表达式
result = "及格" if score >= 60 else "不及格"

# and / or / not
if age >= 18 and score >= 60:
    print("符合条件")
```

### 7.2 for 循环

```python
# 遍历列表
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)

# 带索引
for i, fruit in enumerate(fruits):
    print(f"{i}: {fruit}")

# range 函数
for i in range(5):        # 0, 1, 2, 3, 4
    print(i)

for i in range(2, 6):     # 2, 3, 4, 5
    print(i)

for i in range(0, 10, 2): # 0, 2, 4, 6, 8
    print(i)

# 遍历字典
person = {"name": "张三", "age": 25}
for key, value in person.items():
    print(f"{key}: {value}")

# 遍历字符串
for char in "hello":
    print(char)
```

### 7.3 while 循环

```python
# 基本用法
count = 0
while count < 5:
    print(count)
    count += 1

# 猜数字（示例）
import random
target = random.randint(1, 100)
while True:
    guess = int(input("猜一个数字："))
    if guess < target:
        print("太小了")
    elif guess > target:
        print("太大了")
    else:
        print("猜对了！")
        break
```

### 7.4 循环控制

```python
# break：跳出整个循环
for i in range(10):
    if i == 5:
        break
    print(i)  # 0, 1, 2, 3, 4

# continue：跳过本次循环
for i in range(10):
    if i % 2 == 0:
        continue
    print(i)  # 1, 3, 5, 7, 9

# else：循环正常结束时执行（break 跳出不执行）
for i in range(5):
    if i == 10:
        break
else:
    print("循环正常结束")
```

---

## 第八章：函数

### 8.1 函数定义

```python
# 基本函数
def greet():
    print("Hello!")

greet()    # 调用
```

### 8.2 函数参数

```python
# 位置参数
def add(a, b):
    return a + b

result = add(3, 5)

# 默认参数
def greet(name, greeting="Hello"):
    print(f"{greeting}, {name}!")

greet("张三")              # Hello, 张三!
greet("李四", "早上好")     # 早上好, 李四!

# 关键字参数
greet(name="王五", greeting="你好")

# 可变参数（收集为元组）
def sum_all(*args):
    total = 0
    for num in args:
        total += num
    return total

print(sum_all(1, 2, 3, 4, 5))

# 关键字可变参数（收集为字典）
def print_info(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")

print_info(name="张三", age=25, city="北京")
```

### 8.3 返回值

```python
# 单个返回值
def add(a, b):
    return a + b

# 多个返回值（元组）
def divide(a, b):
    quotient = a // b
    remainder = a % b
    return quotient, remainder

q, r = divide(10, 3)    # q=3, r=1

# 无 return 或 return 无值，返回 None
def do_nothing():
    pass

print(do_nothing())    # None
```

### 8.4 作用域

```python
x = 10    # 全局变量

def func():
    y = 20    # 局部变量
    global x    # 声明使用全局变量
    x = 15
    print(x, y)

func()
print(x)
```

### 8.5 lambda 匿名函数

```python
# 简单函数用 lambda
square = lambda x: x ** 2
print(square(5))    # 25

add = lambda a, b: a + b

# 常用场景：排序、map、filter
fruits = ["apple", "banana", "cherry"]
fruits.sort(key=lambda x: len(x))    # 按长度排序
```

### 8.6 装饰器（进阶）

```python
# 装饰器是函数的函数，用于增强函数功能
def timer(func):
    def wrapper(*args, **kwargs):
        import time
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__} 耗时: {time.time() - start:.4f}s")
        return result
    return wrapper

@timer
def slow_func():
    import time
    time.sleep(1)

slow_func()
```

---

## 第九章：文件操作

### 9.1 文件读写

```python
# 读取文件（推荐 with 方式，自动关闭）
with open("file.txt", "r", encoding="utf-8") as f:
    content = f.read()          # 读取全部内容
    lines = f.readlines()       # 读取所有行到列表
    line = f.readline()         # 读取一行

# 写入文件（覆盖）
with open("output.txt", "w", encoding="utf-8") as f:
    f.write("Hello\n")
    f.write("World\n")
    lines = ["第一行\n", "第二行\n"]
    f.writelines(lines)

# 追加写入
with open("log.txt", "a", encoding="utf-8") as f:
    f.write("新的一行\n")
```

### 9.2 文件打开模式

| 模式 | 说明 |
|------|------|
| `r` | 只读（默认） |
| `w` | 写入（覆盖，不存在则创建） |
| `a` | 追加（不存在则创建） |
| `r+` | 读写（文件必须存在） |
| `w+` | 读写（覆盖） |
| `x` | 创建新文件（已存在则报错） |
| `rb` | 二进制只读 |
| `wb` | 二进制写入 |

### 9.3 目录操作

```python
import os

# 获取当前目录
print(os.getcwd())

# 切换目录
os.chdir("/path/to/dir")

# 列出目录内容
print(os.listdir("."))

# 创建目录
os.mkdir("new_dir")              # 创建单级目录
os.makedirs("a/b/c", exist_ok=True)  # 创建多级目录

# 删除
os.remove("file.txt")            # 删除文件
os.rmdir("empty_dir")            # 删除空目录

# 判断
print(os.path.exists("file.txt"))  # 是否存在
print(os.path.isfile("file.txt"))  # 是否为文件
print(os.path.isdir("dir"))        # 是否为目录

# 路径操作
path = "/home/user/docs/file.txt"
print(os.path.basename(path))   # file.txt
print(os.path.dirname(path))    # /home/user/docs
print(os.path.join("a", "b"))   # a/b
print(os.path.splitext(path))   # ('/home/user/docs/file', '.txt')
print(os.path.getsize(path))    # 文件大小（字节）
```

### 9.4 glob 匹配文件

```python
import glob

# 匹配当前目录的所有 .txt 文件
txt_files = glob.glob("*.txt")

# 递归匹配
py_files = glob.glob("**/*.py", recursive=True)
```

---

## 第十章：模块与包

### 10.1 导入模块

```python
# 导入整个模块
import math
print(math.pi)
print(math.sqrt(16))

# 导入特定函数
from math import pi, sqrt
print(pi)
print(sqrt(16))

# 导入并起别名
import math as m
print(m.pi)

# 导入所有（不推荐）
from math import *
```

### 10.2 常用标准库

| 模块 | 功能 |
|------|------|
| `math` | 数学函数 |
| `random` | 随机数 |
| `datetime` | 日期时间 |
| `os` | 操作系统接口 |
| `sys` | 系统相关 |
| `json` | JSON 处理 |
| `re` | 正则表达式 |
| `requests` | HTTP 请求（第三方） |
| `time` | 时间相关 |
| `collections` | 高级数据结构 |

### 10.3 创建自己的模块

创建 `mymodule.py`：

```python
# mymodule.py
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

PI = 3.14159
```

在另一个文件中使用：

```python
import mymodule
print(mymodule.add(1, 2))

from mymodule import add, PI
print(add(3, 4))
print(PI)
```

---

## 第十一章：正则表达式（re 模块）

### 11.1 常用函数

```python
import re

# 匹配：从字符串开头匹配
result = re.match(r"\d+", "123abc")
if result:
    print(result.group())    # 123

# 搜索：查找第一个匹配
result = re.search(r"\d+", "abc123def")
if result:
    print(result.group())    # 123

# 查找所有匹配
results = re.findall(r"\d+", "abc123def456ghi")
print(results)    # ['123', '456']

# 替换
result = re.sub(r"\d+", "NUM", "abc123def456")
print(result)     # abcNUMdefNUM

# 分割
result = re.split(r"[,-]", "a,b-c,d")
print(result)     # ['a', 'b', 'c', 'd']

# 编译正则（重复使用时更高效）
pattern = re.compile(r"\d+")
pattern.findall("abc123")
```

### 11.2 常用正则语法

| 语法 | 说明 |
|------|------|
| `.` | 任意字符（除换行） |
| `\d` | 数字 `[0-9]` |
| `\w` | 单词字符 `[a-zA-Z0-9_]` |
| `\s` | 空白字符 |
| `^` | 行首 |
| `$` | 行尾 |
| `*` | 0 次或多次 |
| `+` | 1 次或多次 |
| `?` | 0 次或 1 次 |
| `{n}` | 恰好 n 次 |
| `{n,m}` | n 到 m 次 |
| `[abc]` | 匹配 a/b/c 任一 |
| `[^abc]` | 不匹配 a/b/c |
| `a|b` | a 或 b |
| `()` | 分组捕获 |
| `\b` | 单词边界 |

### 11.3 分组

```python
# 提取分组
text = "姓名: 张三, 年龄: 25"
pattern = r"姓名: (\w+), 年龄: (\d+)"
result = re.search(pattern, text)
if result:
    print(result.group(0))    # 姓名: 张三, 年龄: 25（全部）
    print(result.group(1))    # 张三
    print(result.group(2))    # 25
    print(result.groups())    # ('张三', '25')

# 命名分组
pattern = r"姓名: (?P<name>\w+), 年龄: (?P<age>\d+)"
result = re.search(pattern, text)
if result:
    print(result.group("name"))   # 张三
    print(result.group("age"))    # 25
```

### 11.4 标志位

| 标志 | 说明 |
|------|------|
| `re.IGNORECASE` / `re.I` | 忽略大小写 |
| `re.MULTILINE` / `re.M` | 多行模式，^ 和 $ 匹配每行 |
| `re.DOTALL` / `re.S` | `.` 也匹配换行符 |
| `re.VERBOSE` / `re.X` | 忽略空白和注释（正则可写多行） |

---

## 第十二章：网络请求（requests 库）

### 12.1 安装

```bash
pip install requests
```

### 12.2 基本请求

```python
import requests

# GET 请求
response = requests.get("https://httpbin.org/get")

# 响应内容
print(response.status_code)    # 状态码：200
print(response.text)           # 文本内容
print(response.json())         # JSON 解析（返回字典）
print(response.headers)        # 响应头
print(response.url)            # 请求的 URL

# 带参数的 GET
params = {"key1": "value1", "key2": "value2"}
response = requests.get("https://httpbin.org/get", params=params)

# POST 请求（表单数据）
data = {"username": "admin", "password": "123456"}
response = requests.post("https://httpbin.org/post", data=data)

# POST JSON
json_data = {"name": "张三", "age": 25}
response = requests.post("https://httpbin.org/post", json=json_data)
```

### 12.3 请求头与 Cookie

```python
# 自定义请求头
headers = {
    "User-Agent": "MyBot/1.0",
    "Authorization": "Bearer token123"
}
response = requests.get("https://httpbin.org/headers", headers=headers)

# Cookie
cookies = {"session": "abc123"}
response = requests.get("https://httpbin.org/cookies", cookies=cookies)

# Session（保持会话，自动处理 Cookie）
session = requests.Session()
session.post("https://example.com/login", data={"user": "admin", "pass": "123"})
response = session.get("https://example.com/dashboard")  # 自动带上登录 cookie
```

### 12.4 其他请求方式

```python
requests.put(url, data=data)       # PUT 请求
requests.delete(url)               # DELETE 请求
requests.head(url)                 # HEAD 请求
requests.patch(url, data=data)     # PATCH 请求
```

### 12.5 超时与异常处理

```python
try:
    response = requests.get("https://httpbin.org/get", timeout=5)
    response.raise_for_status()     # 状态码非 2xx 抛出异常
except requests.exceptions.Timeout:
    print("请求超时")
except requests.exceptions.ConnectionError:
    print("连接失败")
except requests.exceptions.HTTPError as e:
    print(f"HTTP 错误: {e}")
except requests.exceptions.RequestException as e:
    print(f"请求异常: {e}")
```

### 12.6 文件上传与下载

```python
# 文件上传
files = {"file": open("test.txt", "rb")}
response = requests.post("https://httpbin.org/post", files=files)

# 文件下载
url = "https://example.com/file.zip"
response = requests.get(url)
with open("file.zip", "wb") as f:
    f.write(response.content)
```

---

## 第十三章：异常处理

### 13.1 try-except

```python
try:
    num = int(input("请输入一个数字："))
    result = 10 / num
    print(f"结果：{result}")
except ValueError:
    print("输入的不是数字")
except ZeroDivisionError:
    print("不能除以零")
except Exception as e:
    print(f"发生了其他错误：{e}")
```

### 13.2 try-except-else-finally

```python
try:
    f = open("file.txt", "r")
    content = f.read()
except FileNotFoundError:
    print("文件不存在")
else:
    print("文件读取成功")
    print(content)
    f.close()
finally:
    print("无论成功失败都会执行")
```

### 13.3 抛出异常

```python
def divide(a, b):
    if b == 0:
        raise ValueError("除数不能为零")
    return a / b

try:
    divide(10, 0)
except ValueError as e:
    print(f"错误: {e}")
```

### 13.4 自定义异常

```python
class MyError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

try:
    raise MyError("自定义错误")
except MyError as e:
    print(f"捕获到自定义异常: {e}")
```

---

## 第十四章：简单脚本编写

### 14.1 端口扫描脚本

```python
import socket
import sys

def port_scan(host, start_port, end_port):
    print(f"开始扫描 {host} 的端口 {start_port}-{end_port}...")
    for port in range(start_port, end_port + 1):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex((host, port))
        if result == 0:
            print(f"端口 {port} 开放")
        sock.close()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(f"用法: {sys.argv[0]} <主机> <起始端口> <结束端口>")
        sys.exit(1)
    port_scan(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
```

### 14.2 目录爆破脚本

```python
import requests
import sys

def dir_brute(url, wordlist):
    with open(wordlist, "r") as f:
        paths = [line.strip() for line in f if line.strip()]
    for path in paths:
        full_url = f"{url.rstrip('/')}/{path}"
        try:
            response = requests.get(full_url, timeout=5, allow_redirects=False)
            if response.status_code == 200:
                print(f"[+] 找到: {full_url} (200)")
            elif response.status_code == 403:
                print(f"[*] 禁止访问: {full_url} (403)")
        except requests.exceptions.RequestException:
            pass

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"用法: {sys.argv[0]} <URL> <字典文件>")
        sys.exit(1)
    dir_brute(sys.argv[1], sys.argv[2])
```

### 14.3 简单的 Web 爬虫

```python
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def crawl(url, depth=2):
    visited = set()
    queue = [(url, 0)]

    while queue:
        current_url, current_depth = queue.pop(0)
        if current_url in visited or current_depth > depth:
            continue

        visited.add(current_url)
        print(f"[深度 {current_depth}] {current_url}")

        try:
            response = requests.get(current_url, timeout=5)
            soup = BeautifulSoup(response.text, "html.parser")

            for link in soup.find_all("a", href=True):
                full_url = urljoin(current_url, link["href"])
                if full_url.startswith("http") and full_url not in visited:
                    queue.append((full_url, current_depth + 1))
        except Exception:
            pass
```

---

## 附录：代码示例索引

所有示例代码保存在 `python/` 目录下：

| 文件名 | 对应章节 | 内容说明 |
|--------|---------|---------|
| `01_hello.py` | 第一章 | 第一个 Python 程序 |
| `02_variables.py` | 第二、三章 | 变量与数据类型 |
| `03_list.py` | 第四章 | 列表操作 |
| `04_dict.py` | 第五章 | 字典操作 |
| `05_string.py` | 第六章 | 字符串操作 |
| `06_control_flow.py` | 第七章 | 条件判断与循环 |
| `07_functions.py` | 第八章 | 函数定义与使用 |
| `08_file_ops.py` | 第九章 | 文件与目录操作 |
| `09_regex.py` | 第十一章 | 正则表达式 |
| `10_requests.py` | 第十二章 | requests 网络请求 |
| `11_exceptions.py` | 第十三章 | 异常处理 |
| `port_scanner.py` | 第十四章 | 端口扫描脚本 |
| `dir_bruter.py` | 第十四章 | 目录爆破脚本 |
| `web_crawler.py` | 第十四章 | 简单 Web 爬虫 |

---

> **延伸学习**：Python 是网络安全领域最常用的编程语言之一，掌握 Python 后可以编写各种安全工具（扫描器、爬虫、漏洞利用脚本等）。推荐进一步学习 `requests`、`scapy`、`pwntools` 等安全相关库。
