# puts_print

> **分类**：输出
> **说明**：Ruby 输出方法

---

## 语法

```ruby
puts "text"  # 自动换行\nprint "text" # 不换行
```

## 输出方法

puts / print / p / printf / sprintf / puts.inspect

## 区别

puts: 换行，数组每个元素一行\nprint: 不换行\np: 输出 inspect 形式

## 示例代码

```ruby
# puts - 输出并换行
puts "Hello, World!"
puts 42
puts [1, 2, 3]  # 每个元素一行

# print - 输出不换行
print "输入: "
# gets.chomp  # 读取输入

# p - 输出 inspect 形式（调试用）
p "hello"     # "hello"
p [1, 2, 3]   # [1, 2, 3]
p({a: 1, b: 2}) # {:a=>1, :b=>2}

# printf - 格式化输出
printf("姓名: %s, 年龄: %d\n", "Alice", 25)
printf("PI = %.2f\n", 3.14159)

# sprintf - 格式化到字符串
s = sprintf("%.2f", 3.14159)

# 字符串插值
name = "Bob"
age = 30
puts "你好, #{name}, 今年 #{age} 岁"
puts "1 + 2 = #{1 + 2}"

# 其他输出方法
$stdout.puts "标准输出"
$stderr.puts "错误输出"

# pp - 漂亮打印（需要 require 'pp'）
require 'pp'
pp({name: "Alice", age: 25, city: "Beijing"})

# 输入
# name = gets.chomp  # 读取一行并去掉换行符
# num = gets.to_i    # 读取并转整数
```
