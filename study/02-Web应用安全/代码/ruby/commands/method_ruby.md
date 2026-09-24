# method_ruby

> **分类**：方法与控制流
> **说明**：Ruby 方法定义和控制流

---

## 语法

```ruby
def method_name(param)\n  ...\nend
```

## 方法特性

默认参数 / 可变参数 / 关键字参数 / 块 yield / 别名

## 控制流

if/else/unless/while/until/for/case/break/next

## 示例代码

```ruby
# 基本方法
def greet(name)
  "Hello, #{name}!"
end
puts greet("Alice")

# 默认参数
def greet(name = "World")
  "Hello, #{name}!"
end
puts greet
puts greet("Bob")

# 可变参数
def sum(*numbers)
  numbers.reduce(0, :+)
end
puts sum(1, 2, 3, 4, 5)  # 15

# 关键字参数
def create_user(name:, age:, city: "Beijing")
  { name: name, age: age, city: city }
end
create_user(name: "Alice", age: 25)

# 返回值（最后一个表达式就是返回值）
def add(a, b)
  a + b  # 不需要 return
end

# 多个返回值
def min_max(arr)
  [arr.min, arr.max]
end
min, max = min_max([3, 1, 4, 1, 5])

# ===== 块 (block) =====
def my_method
  puts "方法开始"
  yield if block_given?
  puts "方法结束"
end

my_method do
  puts "块中的代码"
end

# 带参数的 yield
def greet_yield
  yield("Alice")
  yield("Bob")
end

greet_yield { |name| puts "Hello, #{name}!" }

# each 就是 yield 的应用
[1, 2, 3].each { |n| puts n }

# ===== 控制流 =====
age = 18

if age >= 18
  puts "成年"
elsif age >= 6
  puts "少年"
else
  puts "儿童"
end

# unless（if 的反义）
puts "未成年" unless age >= 18

# 三元运算符
status = age >= 18 ? "成年" : "未成年"

# case/when
day = "Monday"
case day
when "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"
  puts "工作日"
when "Saturday", "Sunday"
  puts "周末"
else
  puts "无效"
end

# case 用类型
x = 100
case x
when String then puts "字符串"
when Integer then puts "整数"
when Float then puts "浮点数"
end

# 循环
i = 0
while i < 5
  puts i
  i += 1
end

# until（while 的反义）
i = 0
until i >= 5
  puts i
  i += 1
end

# for 循环（不常用，each 更 Ruby）
for fruit in ["apple", "banana"] do
  puts fruit
end

# times
5.times { puts "hello" }

# upto / downto
1.upto(5) { |i| puts i }
5.downto(1) { |i| puts i }

# break / next
[1, 2, 3, 4, 5].each do |n|
  next if n == 3  # 跳过3
  break if n == 7 # 到7停止
  puts n
end
```
