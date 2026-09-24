# variable_ruby

> **分类**：变量与类型
> **说明**：Ruby 变量和数据类型

---

## 语法

```ruby
variable = value  # 直接赋值，自动类型推断
```

## 变量类型

局部变量 / 全局变量$ / 实例变量@ / 类变量@@ / 常量

## 常用类

String / Integer / Float / Array / Hash / Symbol / Boolean / NilClass

## 示例代码

```ruby
# 局部变量
name = "Alice"
age = 25
price = 9.99
active = true
nothing = nil

# 全局变量（$ 开头）
$global_var = "全局变量"

# 实例变量（@ 开头）
@instance_var = "实例变量"

# 类变量（@@ 开头）
@@class_var = "类变量"

# 常量（大写开头）
MAX_SIZE = 100
PI = 3.14159

# 类型检查
puts name.class      # String
puts age.class       # Integer
puts price.class     # Float
puts active.class    # TrueClass / FalseClass
puts nothing.class   # NilClass

# 类型转换
"123".to_i           # 123
456.to_s             # "456"
"3.14".to_f          # 3.14
1.to_f               # 1.0
:symbol.to_s         # "symbol"
"sym".to_sym         # :sym

# String
str = "Hello, Ruby!"
str.length           # 长度
str.upcase           # 大写
str.downcase         # 小写
str.reverse          # 反转
str[0]               # 第一个字符
str[0..4]            # "Hello"
str.include?("Ruby") # true
str.gsub("Ruby", "World")  # 替换
str.split(",")       # 分割

# Symbol
:hello
:"hello world"
:hello.to_s          # "hello"

# 数字
100 + 50             # 150
10 * 3               # 30
10 / 3               # 3（整数除法）
10.0 / 3             # 3.333...
10 % 3               # 1
2 ** 10              # 1024（幂）

# 特殊方法
nil.nil?             # true
"hello".nil?         # false
5.odd?               # true
6.even?              # true

# 类型判断
"hello".is_a?(String)  # true
5.kind_of?(Integer)    # true
[].respond_to?(:map)   # true
```
