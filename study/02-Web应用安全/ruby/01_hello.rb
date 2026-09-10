# ============================================================
# Ruby 基础入门：Hello World、变量、数据类型、运算符
# 运行方式：ruby 01_hello.rb
# ============================================================

# ---------- 1. Hello World ----------
puts "========== 1. Hello World =========="

# puts 输出并换行
puts "Hello, Ruby!"
puts "欢迎学习 Ruby 语言"

# print 输出不换行
print "Hello, "
print "World!"
puts ""   # 输出空行换行

# p 输出 inspect 结果（调试用，会显示类型信息）
p "Hello"      # => "Hello"
p 123          # => 123

# ---------- 2. 变量 ----------
puts "\n========== 2. 变量 =========="

# 局部变量：小写字母或下划线开头，使用蛇形命名法
name = "张三"
age = 25
_user_id = 1001

puts "姓名：#{name}"
puts "年龄：#{age}"
puts "用户ID：#{_user_id}"

# Ruby 是动态类型语言，变量类型可以随时改变
x = 10          # 整数
puts "x = #{x}，类型：#{x.class}"
x = "hello"     # 字符串
puts "x = #{x}，类型：#{x.class}"
x = 3.14        # 浮点数
puts "x = #{x}，类型：#{x.class}"

# 常量：大写字母开头
PI = 3.14159
MAX_RETRIES = 3
puts "PI = #{PI}"
puts "最大重试次数 = #{MAX_RETRIES}"

# ---------- 3. 数据类型 ----------
puts "\n========== 3. 数据类型 =========="

# --- 数字（Numeric）---
puts "\n--- 数字 ---"
int_num = 42
float_num = 3.14
big_num = 1_000_000    # 下划线只是为了可读性，不影响值

puts "整数：#{int_num}，类型：#{int_num.class}"
puts "浮点数：#{float_num}，类型：#{float_num.class}"
puts "大数字：#{big_num}"

# Ruby 中一切皆对象，数字也可以调用方法
puts "5 的 3 次方：#{5 ** 3}"
puts "5 次循环："
3.times { |i| puts "  第 #{i + 1} 次" }

# --- 字符串（String）---
puts "\n--- 字符串 ---"
str1 = "双引号字符串"
str2 = '单引号字符串'

puts str1
puts str2

# 双引号支持字符串插值
name = "Ruby"
puts "Hello, #{name}!"     # 插值
puts 'Hello, #{name}!'     # 单引号不支持插值，原样输出

# 多行字符串（heredoc）
multiline = <<~TEXT
  这是第一行
  这是第二行
  这是第三行
TEXT
puts "多行字符串：\n#{multiline}"

# --- 符号（Symbol）---
puts "\n--- 符号 ---"
:name
:user_id
:"特殊符号"

puts ":name 的类型：#{:name.class}"
puts ":name 转字符串：#{:name.to_s}"
puts "\"name\" 转符号：#{"name".to_sym}"

# 符号是单例的，相同符号指向同一个对象
puts ":name 对象 ID：#{:name.object_id}"
puts ":name 对象 ID：#{:name.object_id}（和上面相同）"

# --- nil ---
puts "\n--- nil ---"
result = nil
puts "result = #{result.inspect}"
puts "result 是 nil 吗？#{result.nil?}"

# --- 布尔值 ---
puts "\n--- 布尔值 ---"
puts "true 的类型：#{true.class}"
puts "false 的类型：#{false.class}"

# 重要：Ruby 中只有 nil 和 false 为假，其他都为真
# 包括 0、空字符串、空数组都为真！
puts "0 为真吗？#{!!0}"           # => true
puts "空字符串为真吗？#{!!""}"     # => true
puts "空数组为真吗？#{!![]}"       # => true
puts "nil 为真吗？#{!!nil}"        # => false
puts "false 为真吗？#{!!false}"    # => false

# ---------- 4. 运算符 ----------
puts "\n========== 4. 运算符 =========="

a = 10
b = 3

# 算术运算符
puts "a + b = #{a + b}"
puts "a - b = #{a - b}"
puts "a * b = #{a * b}"
puts "a / b = #{a / b}（整数除法）"
puts "a.to_f / b = #{a.to_f / b}（浮点除法）"
puts "a % b = #{a % b}（取模）"
puts "a ** b = #{a ** b}（幂运算）"

# 比较运算符
puts "\n--- 比较运算符 ---"
puts "a == b：#{a == b}"
puts "a != b：#{a != b}"
puts "a > b：#{a > b}"
puts "a < b：#{a < b}"
puts "a >= 10：#{a >= 10}"
puts "a <= 10：#{a <= 10}"
puts "a <=> b：#{a <=> b}（飞船运算符，a大返回1）"

# 逻辑运算符
puts "\n--- 逻辑运算符 ---"
x = true
y = false
puts "x && y = #{x && y}"
puts "x || y = #{x || y}"
puts "!x = #{!x}"

# ||= 惯用法：如果变量为 nil 或 false，则赋值
value = nil
value ||= "默认值"
puts "value ||= 默认值 后：#{value}"

value = "已有值"
value ||= "默认值"
puts "已有值时 value ||= 默认值 后：#{value}"

# 字符串拼接
puts "\n--- 字符串拼接 ---"
str = "Hello"
puts str + ", World!"
puts str << " Ruby"    # << 会修改原字符串
puts "现在 str = #{str}"

# 范围运算符
puts "\n--- 范围运算符 ---"
puts "(1..5).to_a = #{(1..5).to_a}（包含5）"
puts "(1...5).to_a = #{(1...5).to_a}（不包含5）"

puts "\n========== 示例运行结束 =========="
