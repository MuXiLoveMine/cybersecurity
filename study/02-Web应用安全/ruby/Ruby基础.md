# Ruby 语言基础

## 目录

1. [Ruby 语言简介](#ruby-语言简介)
2. [使用场景](#使用场景)
3. [环境安装](#环境安装)
4. [基础语法](#基础语法)
5. [运算符](#运算符)
6. [控制流](#控制流)
7. [方法（函数）](#方法函数)
8. [字符串操作](#字符串操作)
9. [数组（Array）](#数组array)
10. [哈希（Hash）](#哈希hash)
11. [符号（Symbol）](#符号symbol)
12. [面向对象](#面向对象)
13. [异常处理](#异常处理)
14. [文件操作](#文件操作)
15. [网络请求（Net::HTTP）](#网络请求nethttp)
16. [正则表达式（Regexp）](#正则表达式regexp)
17. [RubyGems 与 Bundler](#rubygems-与-bundler)
18. [Ruby 在安全领域的应用](#ruby-在安全领域的应用)

---

## Ruby 语言简介

### 历史

Ruby 是由日本程序员**松本行弘（Matz）**于 1995 年发布的一种动态编程语言。他的设计理念是：

> "让程序员感到幸福"（Make programmers happy）

Ruby 深受 Perl、Smalltalk、Eiffel、Ada 和 Lisp 等语言的影响，致力于创造一种语法优雅、表达力强的语言。

### 核心特点

- **动态类型（Dynamically Typed）**：变量不需要声明类型，类型在运行时确定
- **纯面向对象（Pure Object-Oriented）**：一切皆对象，甚至数字、nil 都是对象
- **解释型语言**：通过 Ruby 解释器直接执行，无需编译
- **垃圾回收（GC）**：自动内存管理
- **元编程能力**：可以在运行时动态修改类和对象
- **简洁优雅**：语法接近自然语言，代码可读性高

### 和安全的关系

Ruby 的动态特性和元编程能力既带来了便利，也引入了一些安全风险：

- **代码注入风险**：`eval`、`send` 等动态方法可能导致代码注入
- **对象注入**：反序列化不安全数据可能导致任意代码执行
- **字符串插值风险**：不当的字符串拼接可能导致 SQL 注入等问题
- **强大的表达力**：安全工具开发者可以用极少的代码实现复杂功能

---

## 使用场景

### 1. Web 开发（Ruby on Rails）

Ruby 最著名的应用场景是 **Ruby on Rails** 框架，它是一个全栈 MVC 框架，以"约定优于配置"著称。GitHub、Shopify、Basecamp、Airbnb 等知名网站早期都使用 Rails 开发。

### 2. 脚本自动化

Ruby 语法简洁，非常适合编写自动化脚本：

- 文件处理和批量操作
- 系统管理脚本
- 数据处理和转换
- CI/CD 流水线脚本

### 3. 安全工具

Ruby 在安全领域应用广泛，最著名的就是 **Metasploit 框架**完全用 Ruby 编写。其他安全相关应用：

- 漏洞利用脚本开发
- 渗透测试工具
- 安全扫描器
- 取证分析工具
- 快速 PoC 验证

---

## 环境安装

### Windows

1. 下载 RubyInstaller：https://rubyinstaller.org/
2. 安装时勾选 "Add Ruby executables to your PATH"
3. 安装完成后打开命令行验证：

```bash
ruby --version
gem --version
```

### macOS

```bash
# 使用 Homebrew 安装
brew install ruby

# 或使用 rbenv（推荐，可管理多个版本）
brew install rbenv
rbenv install 3.2.0
rbenv global 3.2.0
```

### Linux（Ubuntu/Debian）

```bash
sudo apt-get update
sudo apt-get install ruby-full
```

### RubyGems

RubyGems 是 Ruby 的包管理器，安装 Ruby 后默认自带。常用命令：

```bash
gem install <gem_name>    # 安装 gem
gem uninstall <gem_name>  # 卸载 gem
gem list                  # 列出已安装的 gem
gem update                # 更新所有 gem
```

### Bundler

Bundler 用于管理项目的 gem 依赖：

```bash
gem install bundler       # 安装 bundler

# 在项目中使用
bundle init               # 初始化 Gemfile
bundle install            # 安装 Gemfile 中的依赖
bundle exec <command>     # 在当前 bundle 环境中执行命令
```

---

## 基础语法

### 变量

Ruby 变量名以小写字母或下划线开头，使用蛇形命名法（snake_case）。

```ruby
name = "Alice"        # 局部变量
age = 25              # 局部变量
_user_id = 1001       # 局部变量

# 变量类型在运行时确定
x = 10                # Integer
x = "hello"           # 现在变成 String，无需类型声明
```

### 常量

常量以大写字母开头，通常使用全大写加下划线。

```ruby
PI = 3.14159
MAX_RETRIES = 3
DEFAULT_PORT = 8080
```

> 注意：Ruby 的常量实际上是可以重新赋值的，但会产生警告。约定上不应该修改常量。

### 数据类型

#### 数字（Numeric）

```ruby
# 整数
int_num = 42
big_num = 1_000_000     # 可以用下划线分隔，提高可读性

# 浮点数
float_num = 3.14
scientific = 1.5e3      # 1500.0

# 一切皆对象
5.times { puts "hello" }  # 5 是 Integer 对象，可以调用 times 方法
```

#### 字符串（String）

```ruby
str1 = "Hello, World!"    # 双引号字符串（支持插值）
str2 = 'Hello, World!'    # 单引号字符串（不支持插值和转义）
str3 = <<~HEREDOC         #  heredoc 语法，多行字符串
  这是多行字符串
  第二行内容
HEREDOC
```

#### 符号（Symbol）

符号是轻量级的、不可变的字符串表示，常用作哈希的键。

```ruby
:name                   # 符号
:user_id
:"special symbol"       # 含特殊字符的符号
```

#### nil

`nil` 是 Ruby 中的空值，表示"什么都没有"，它是 `NilClass` 的唯一实例。

```ruby
result = nil
result.nil?             # => true
```

#### 布尔值

Ruby 中有两个布尔值：`true` 和 `false`。注意：**只有 `nil` 和 `false` 被视为假，其他所有值（包括 0、空字符串、空数组）都为真**。

```ruby
false                   # 假
nil                     # 假
true                    # 真
0                       # 真（和很多语言不同！）
""                      # 真
[]                      # 真
```

---

## 运算符

### 算术运算符

```ruby
+     # 加法
-     # 减法
*     # 乘法
/     # 除法（整数相除结果为整数）
%     # 取模
**    # 幂运算

10 / 3      # => 3（整数除法）
10.0 / 3    # => 3.333...
2 ** 3      # => 8
```

### 比较运算符

```ruby
==    # 等于
!=    # 不等于
>     # 大于
<     # 小于
>=    # 大于等于
<=    # 小于等于
<=>   # 飞船运算符（-1 / 0 / 1）
===   #  case 等式（常用于 case 语句）
```

### 逻辑运算符

```ruby
&&    # 与（and）
||    # 或（or）
!     # 非（not）

and   # 低优先级版本的 &&
or    # 低优先级版本的 ||
not   # 低优先级版本的 !
```

### 赋值运算符

```ruby
=     # 简单赋值
+=    # 加后赋值
-=    # 减后赋值
*=    # 乘后赋值
/=    # 除后赋值
%=    # 取模后赋值
**=   # 幂后赋值

a ||= b   # 如果 a 为 nil 或 false，则将 b 赋值给 a（常用惯用法）
```

### 其他运算符

```ruby
..    #  inclusive 范围（1..5 包含 5）
...   #  exclusive 范围（1...5 不包含 5）
?:    # 三目运算符
```

---

## 控制流

### if / elsif / else

```ruby
if age >= 18
  puts "成年人"
elsif age >= 13
  puts "青少年"
else
  puts "儿童"
end
```

**if 修饰符**（单行写法）：

```ruby
puts "允许访问" if age >= 18
```

### unless

`unless` 是 `if not` 的反面，当条件为假时执行：

```ruby
unless logged_in?
  redirect_to login_path
end

# 修饰符写法
puts "错误：未登录" unless logged_in?
```

### 三目运算符

```ruby
status = age >= 18 ? "成年" : "未成年"
```

### for 循环

```ruby
for i in 1..5
  puts i
end
```

> 注意：Ruby 中更常用 `each` 迭代器而非 for 循环。

### while 循环

```ruby
i = 0
while i < 5
  puts i
  i += 1
end
```

### until 循环

`until` 是 `while not` 的反面：

```ruby
i = 0
until i >= 5
  puts i
  i += 1
end
```

### each 迭代器

Ruby 中最常用的遍历方式：

```ruby
# 遍历数组
[1, 2, 3].each do |item|
  puts item
end

# 单行块写法
[1, 2, 3].each { |item| puts item }

# 带索引
['a', 'b', 'c'].each_with_index do |item, index|
  puts "#{index}: #{item}"
end
```

### case 语句

```ruby
case score
when 90..100
  "优秀"
when 80...90
  "良好"
when 70...80
  "中等"
when 60...70
  "及格"
else
  "不及格"
end

# case 也可以不带参数，类似 if/elsif
case
when score >= 90
  "优秀"
when score >= 80
  "良好"
else
  "继续努力"
end
```

---

## 方法（函数）

### 方法定义

```ruby
def greet
  puts "Hello, World!"
end

greet   # 调用方法
```

### 参数与返回值

```ruby
def add(a, b)
  return a + b    # return 可省略，最后一行的值自动作为返回值
end

def multiply(a, b)
  a * b           # 省略 return
end

# 默认参数
def power(base, exponent = 2)
  base ** exponent
end

power(3)      # => 9
power(3, 3)   # => 27
```

### 可变参数（splat）

```ruby
def sum(*numbers)
  numbers.reduce(0, :+)
end

sum(1, 2, 3, 4)   # => 10

# 关键字参数
def create_user(name:, age:, role: "user")
  { name: name, age: age, role: role }
end

create_user(name: "Alice", age: 25)
create_user(name: "Bob", age: 30, role: "admin")
```

### 块（Block）

块是 Ruby 中非常重要的概念，是一段可以被方法执行的代码。

```ruby
# 使用 do...end 定义块（多行）
[1, 2, 3].each do |n|
  puts n * 2
end

# 使用花括号定义块（单行）
[1, 2, 3].each { |n| puts n * 2 }
```

### yield

`yield` 用于在方法内部执行传入的块：

```ruby
def my_method
  puts "方法开始"
  yield
  puts "方法结束"
end

my_method do
  puts "块中的代码"
end
# 输出：
# 方法开始
# 块中的代码
# 方法结束

# yield 可以传参
def greet(name)
  yield(name) if block_given?
  puts "你好，#{name}！"
end

greet("Alice") { |n| puts "欢迎，#{n}！" }
```

### lambda 和 Proc

```ruby
# lambda
my_lambda = lambda { |x| x * 2 }
my_lambda.call(5)    # => 10

# 简写语法
my_proc = ->(x) { x * 2 }
my_proc.call(5)      # => 10

# Proc
my_proc = Proc.new { |x| x * 2 }
my_proc.call(5)      # => 10
```

---

## 字符串操作

```ruby
str = "Hello, Ruby!"

# 长度
str.length                # => 12

# 拼接
"Hello" + " " + "World"   # => "Hello World"
"Hello" << " World"       # => "Hello World"（原地修改）

# 插值
name = "Alice"
"Hello, #{name}!"         # => "Hello, Alice!"（仅双引号）

# 查找
str.include?("Ruby")      # => true
str.index("Ruby")         # => 7

# 分割
"a,b,c".split(",")        # => ["a", "b", "c"]

# 替换
str.sub("Ruby", "World")  # => "Hello, World!"（只替换第一个）
str.gsub("l", "L")        # => "HeLLo, Ruby!"（全局替换）

# 大小写
str.upcase                # => "HELLO, RUBY!"
str.downcase              # => "hello, ruby!"
str.capitalize            # => "Hello, ruby!"

# 去除空白
"  hello  ".strip         # => "hello"

# 格式化
"%.2f" % 3.14159          # => "3.14"
sprintf("%05d", 42)       # => "00042"
```

---

## 数组（Array）

### 创建数组

```ruby
arr = [1, 2, 3, 4, 5]
empty = []
mixed = [1, "hello", :sym, true, nil]  # 数组可以包含不同类型

# 其他创建方式
Array.new(3)              # => [nil, nil, nil]
Array.new(3, "default")   # => ["default", "default", "default"]
(1..5).to_a               # => [1, 2, 3, 4, 5]
```

### 增删改查

```ruby
arr = [1, 2, 3]

# 访问
arr[0]          # => 1（索引从 0 开始）
arr[-1]         # => 3（负数索引从末尾开始）
arr.first       # => 1
arr.last        # => 3

# 添加
arr.push(4)     # => [1, 2, 3, 4]（末尾添加）
arr << 5        # => [1, 2, 3, 4, 5]（常用写法）
arr.unshift(0)  # => [0, 1, 2, 3, 4, 5]（开头添加）

# 删除
arr.pop         # => 5，删除末尾元素
arr.shift       # => 0，删除开头元素
arr.delete(2)   # => 2，删除指定值
arr.delete_at(0) # => 1，删除指定索引

# 修改
arr[0] = 10     # 修改指定位置
```

### 常用方法

```ruby
arr = [1, 2, 3, 4, 5]

arr.length      # => 5
arr.size        # => 5（别名）
arr.empty?      # => false
arr.include?(3) # => true

# 遍历
arr.each { |n| puts n }
arr.each_with_index { |n, i| puts "#{i}: #{n}" }
arr.reverse_each { |n| puts n }

# 转换
arr.map { |n| n * 2 }       # => [2, 4, 6, 8, 10]（不修改原数组）
arr.map! { |n| n * 2 }      # 修改原数组（! 表示破坏性方法）

# 筛选
arr.select { |n| n > 2 }    # => [3, 4, 5]
arr.reject { |n| n > 2 }    # => [1, 2]
arr.find { |n| n > 2 }      # => 3（第一个匹配的）

# 归约
arr.reduce(:+)              # => 15（求和）
arr.inject(0) { |sum, n| sum + n }  # => 15

# 排序
arr.sort                    # => [1, 2, 3, 4, 5]
arr.sort { |a, b| b <=> a } # => [5, 4, 3, 2, 1]

# 其他常用
arr.join(", ")              # => "1, 2, 3, 4, 5"
arr.flatten                 # 扁平化嵌套数组
arr.uniq                    # 去重
arr.compact                 # 移除 nil
arr.sample                  # 随机取一个元素
arr.shuffle                 # 打乱顺序
```

---

## 哈希（Hash）

### 创建哈希

```ruby
# 符号作为 key（推荐）
user = { name: "Alice", age: 25, email: "alice@example.com" }

# 字符串作为 key
user = { "name" => "Alice", "age" => 25 }

# 空哈希
empty = {}
empty = Hash.new
```

### 增删改查

```ruby
user = { name: "Alice", age: 25 }

# 访问
user[:name]           # => "Alice"
user[:email]          # => nil（不存在的 key 返回 nil）
user.fetch(:email, "未知")  # => "未知"（指定默认值）

# 添加/修改
user[:email] = "alice@example.com"  # 添加
user[:age] = 26                      # 修改

# 删除
user.delete(:age)      # => 26，删除指定 key
```

### 遍历

```ruby
user.each do |key, value|
  puts "#{key}: #{value}"
end

user.each_key { |k| puts k }
user.each_value { |v| puts v }
```

### 嵌套哈希

```ruby
users = {
  alice: { name: "Alice", age: 25, email: "alice@example.com" },
  bob:   { name: "Bob",   age: 30, email: "bob@example.com" }
}

users[:alice][:email]   # => "alice@example.com"
```

### 常用方法

```ruby
user = { name: "Alice", age: 25 }

user.keys               # => [:name, :age]
user.values             # => ["Alice", 25]
user.length             # => 2
user.empty?             # => false
user.has_key?(:name)    # => true
user.has_value?(25)     # => true

# 合并
user.merge({ role: "admin" })  # 合并两个哈希
user.merge!({ role: "admin" }) # 原地合并

# 转换
user.to_a              # 转为数组
```

---

## 符号（Symbol）

符号是 Ruby 中独特的类型，它是不可变的、轻量级的标识符。

```ruby
:name
:user_id
:"hello world"     # 含空格的符号

# 符号与字符串的转换
:name.to_s         # => "name"
"name".to_sym      # => :name
"name".intern      # => :name

# 符号是单例的，相同的符号指向同一个对象
:name.object_id == :name.object_id   # => true
"name".object_id == "name".object_id # => false（每次创建新对象）
```

符号最常用作哈希的键，因为：
- 比较速度快（只需比较对象 ID）
- 内存占用小（单例模式）

---

## 面向对象

Ruby 是纯面向对象语言，一切皆对象。

### 类与对象

```ruby
class Person
  # 构造方法
  def initialize(name, age)
    @name = name    # 实例变量，以 @ 开头
    @age = age
  end

  # 实例方法
  def greet
    "你好，我是#{@name}，今年#{@age}岁。"
  end

  # getter 方法
  def name
    @name
  end

  # setter 方法
  def name=(new_name)
    @name = new_name
  end
end

# 创建对象
person = Person.new("Alice", 25)
puts person.greet
puts person.name
person.name = "Alicia"
```

### 属性访问器

Ruby 提供了便捷的属性定义方式：

```ruby
class Person
  attr_accessor :name    # 同时生成 getter 和 setter
  attr_reader :age       # 只生成 getter
  attr_writer :email     # 只生成 setter

  def initialize(name, age)
    @name = name
    @age = age
  end
end
```

### 类变量和类方法

```ruby
class Person
  @@count = 0            # 类变量，以 @@ 开头

  def initialize(name)
    @name = name
    @@count += 1
  end

  # 类方法，以 self. 开头
  def self.count
    @@count
  end
end

Person.new("Alice")
Person.new("Bob")
Person.count            # => 2
```

### 继承

```ruby
class Animal
  def speak
    "动物叫了一声"
  end
end

class Dog < Animal      # 使用 < 表示继承
  def speak             # 方法重写
    "汪汪！"
  end

  def fetch
    "叼回了球"
  end
end

dog = Dog.new
dog.speak               # => "汪汪！"
```

### 模块（Module）与混入（Mixin）

模块是 Ruby 实现多继承的方式，不能被实例化，可以被类包含（include）。

```ruby
# 定义模块
module Swimmable
  def swim
    "我会游泳！"
  end
end

module Flyable
  def fly
    "我会飞！"
  end
end

class Duck
  include Swimmable     # 混入模块
  include Flyable
end

duck = Duck.new
duck.swim               # => "我会游泳！"
duck.fly                # => "我会飞！"
```

---

## 异常处理

```ruby
begin
  # 可能出错的代码
  result = 10 / 0
rescue ZeroDivisionError => e
  # 捕获特定异常
  puts "除以零错误：#{e.message}"
rescue => e
  # 捕获其他所有异常
  puts "发生错误：#{e.message}"
ensure
  # 无论是否异常都会执行（可选）
  puts "执行结束"
end

# 抛出异常
raise "发生了一个错误"
raise ArgumentError, "参数无效"

# 自定义异常
class MyCustomError < StandardError
end

raise MyCustomError, "自定义错误信息"
```

---

## 文件操作

```ruby
# 读取整个文件
content = File.read("file.txt")

# 逐行读取
File.foreach("file.txt") do |line|
  puts line
end

# 写入文件（覆盖）
File.write("file.txt", "Hello, World!")

# 追加写入
File.open("file.txt", "a") do |file|
  file.puts "追加一行"
end

# 使用 block 自动关闭文件
File.open("file.txt", "r") do |file|
  while line = file.gets
    puts line
  end
end

# 文件/目录操作
File.exist?("file.txt")     # 文件是否存在
File.directory?("path")     # 是否是目录
Dir.entries(".")            # 列出目录内容
Dir.mkdir("new_dir")        # 创建目录
File.delete("file.txt")     # 删除文件
FileUtils.copy("a", "b")    # 复制文件（需要 require 'fileutils'）
```

---

## 网络请求（Net::HTTP）

Ruby 标准库中包含 `Net::HTTP` 用于 HTTP 请求。

```ruby
require 'net/http'
require 'uri'
require 'json'

# GET 请求
uri = URI("https://api.example.com/users")
response = Net::HTTP.get(uri)
data = JSON.parse(response)

# POST 请求
uri = URI("https://api.example.com/users")
http = Net::HTTP.new(uri.host, uri.port)
http.use_ssl = true

request = Net::HTTP::Post.new(uri.path)
request["Content-Type"] = "application/json"
request.body = { name: "Alice", age: 25 }.to_json

response = http.request(request)
puts response.code
puts response.body

# 带自定义 Header 的 GET 请求
uri = URI("https://api.example.com/data")
http = Net::HTTP.new(uri.host, uri.port)
http.use_ssl = true

request = Net::HTTP::Get.new(uri.path)
request["Authorization"] = "Bearer token123"
request["User-Agent"] = "MyRubyClient/1.0"

response = http.request(request)
```

> 注意：生产环境中更常用第三方 gem，如 `httparty`、`faraday`、`rest-client` 等，使用更便捷。

---

## 正则表达式（Regexp）

Ruby 的正则表达式功能非常强大，继承自 Perl 的传统。

### 正则表达式字面量

```ruby
/pattern/
/pattern/i           # 不区分大小写
/pattern/m           # 多行模式
%r{pattern}          # 可选语法，适合包含 / 的模式
```

### 匹配

```ruby
# 匹配操作符 =~ 返回匹配位置，未匹配返回 nil
"hello@example.com" =~ /@/       # => 5
"hello" =~ /@/                   # => nil

# match 方法返回 MatchData 对象
match_data = /(\w+)@(\w+\.\w+)/.match("hello@example.com")
match_data[0]    # => "hello@example.com"（整个匹配）
match_data[1]    # => "hello"（第一个捕获组）
match_data[2]    # => "example.com"（第二个捕获组）

# 命名捕获组
/(?<user>\w+)@(?<domain>\w+\.\w+)/.match("hello@example.com")
# => #<MatchData "hello@example.com" user:"hello" domain:"example.com">
```

### 替换

```ruby
"Hello World".gsub(/o/, "0")     # => "Hell0 W0rld"
"Hello World".sub(/o/, "0")      # => "Hell0 World"（只替换第一个）

# 使用块进行替换
"abc123def".gsub(/\d+/) { |m| m.to_i * 2 }
# => "abc246def"
```

### 常用正则模式

```ruby
/^abc/              # 以 abc 开头
/abc$/              # 以 abc 结尾
/./                 # 任意单个字符（除换行）
/\d/                # 数字 [0-9]
/\D/                # 非数字
/\w/                # 单词字符 [a-zA-Z0-9_]
/\W/                # 非单词字符
/\s/                # 空白字符
/\S/                # 非空白字符
/*/                 # 零次或多次
/+/                 # 一次或多次
/?/                 # 零次或一次
/{n}/               # 恰好 n 次
/{n,}/              # 至少 n 次
/{n,m}/             # n 到 m 次
/[abc]/             # 字符类
/[^abc]/            # 否定字符类
/(abc)/             # 捕获组
/(?:abc)/           # 非捕获组
/a|b/               # 或
```

---

## RubyGems 与 Bundler

### RubyGems

RubyGems 是 Ruby 的包管理系统，gem 是打包好的 Ruby 库或应用。

```bash
# 安装 gem
gem install nokogiri
gem install rails -v 7.0.0

# 查看已安装的 gem
gem list
gem list rails

# 更新 gem
gem update rails
gem update --system        # 更新 RubyGems 本身

# 卸载 gem
gem uninstall nokogiri

# 搜索 gem
gem search http
```

### Bundler

Bundler 用于管理项目的 gem 依赖，确保团队使用相同版本的 gem。

**Gemfile 示例：**

```ruby
source 'https://rubygems.org'

gem 'rails', '~> 7.0'
gem 'pg'
gem 'devise'
gem 'nokogiri'

group :development, :test do
  gem 'rspec-rails'
  gem 'pry'
end

group :production do
  gem 'puma'
end
```

**常用命令：**

```bash
bundle install              # 安装所有依赖
bundle update               # 更新所有依赖
bundle update rails         # 更新特定 gem
bundle exec rspec           # 在当前环境中执行命令
bundle list                 # 列出已安装的 gem
bundle show rails           # 显示 gem 的安装路径
```

---

## Ruby 在安全领域的应用

### Metasploit 框架

**Metasploit** 是世界上最流行的渗透测试框架，完全由 Ruby 编写。它提供了：

- 数千个漏洞利用模块（exploits）
- 载荷（payloads）和 Shellcode
- 辅助模块（auxiliary）如扫描器、爆破工具
- 后渗透模块（post-exploitation）

Metasploit 的模块开发就是用 Ruby 编写的，掌握 Ruby 是自定义 Metasploit 模块的基础。

### 快速开发安全工具

Ruby 的简洁语法和丰富的标准库使其非常适合快速开发安全工具：

- **端口扫描器**：使用 `Socket` 和 `TCPSocket` 快速实现
- **Web 漏洞扫描器**：使用 `Net::HTTP` 和 `Nokogiri` 进行爬虫和检测
- **密码破解工具**：结合 `OpenSSL` 库实现哈希破解
- **取证分析脚本**：处理日志、文件系统分析

### 漏洞利用脚本

Ruby 可以方便地编写 PoC（概念验证）和漏洞利用脚本：

```ruby
# 简单的 PoC 示例结构
require 'net/http'
require 'uri'

target = URI("http://target.com/vuln")
payload = "' OR '1'='1"

http = Net::HTTP.new(target.host, target.port)
request = Net::HTTP::Get.new("#{target.path}?id=#{payload}")
response = http.request(request)

if response.body.include?("admin")
  puts "[+] SQL 注入漏洞存在！"
else
  puts "[-] 未发现漏洞"
end
```

### 常用安全相关 Gem

- **nokogiri**：HTML/XML 解析，用于爬虫和 XSS 检测
- **httparty / faraday**：更便捷的 HTTP 客户端
- **devise**：Rails 认证框架（安全地处理用户认证）
- **brakeman**：Rails 静态代码安全扫描器
- **bundler-audit**：检查 gem 依赖中的已知漏洞
- **metasploit-payloads**：Metasploit 载荷库

### 学习建议

对于安全从业者，掌握 Ruby 可以：

1. **理解 Metasploit**：阅读和编写 Metasploit 模块
2. **快速 PoC 开发**：快速验证漏洞是否存在
3. **自动化安全测试**：编写自动化扫描和测试脚本
4. **Web 安全审计**：审计 Ruby on Rails 应用的安全漏洞
5. **CTF 比赛**：快速编写解题脚本
