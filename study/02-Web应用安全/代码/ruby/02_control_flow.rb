# ============================================================
# Ruby 控制流：if/else/unless、for、while/until、each、case、三目运算符
# 运行方式：ruby 02_control_flow.rb
# ============================================================

# ---------- 1. if / elsif / else ----------
puts "========== 1. if / elsif / else =========="

age = 20

if age >= 18
  puts "成年人"
elsif age >= 13
  puts "青少年"
else
  puts "儿童"
end

# 多条件判断
score = 85
if score >= 90
  grade = "优秀"
elsif score >= 80
  grade = "良好"
elsif score >= 60
  grade = "及格"
else
  grade = "不及格"
end
puts "分数 #{score}，等级：#{grade}"

# if 修饰符（单行写法，Ruby 风格）
puts "成年了" if age >= 18

# ---------- 2. unless ----------
puts "\n========== 2. unless =========="

# unless 是 if not 的反义，条件为假时执行
logged_in = false

unless logged_in
  puts "请先登录"
end

# 等价于
if !logged_in
  puts "请先登录（if 写法）"
end

# unless 修饰符
puts "未授权访问" unless logged_in

# unless ... else （不推荐，可读性差，直接用 if 更好）
unless age < 18
  puts "成年"
else
  puts "未成年"
end

# ---------- 3. 三目运算符 ----------
puts "\n========== 3. 三目运算符 =========="

age = 20
status = age >= 18 ? "成年" : "未成年"
puts "年龄 #{age}：#{status}"

# 嵌套三目（谨慎使用，影响可读性）
score = 75
result = score >= 90 ? "优秀" : score >= 60 ? "及格" : "不及格"
puts "分数 #{score}：#{result}"

# ---------- 4. for 循环 ----------
puts "\n========== 4. for 循环 =========="

# 遍历范围
puts "for 遍历 1..5："
for i in 1..5
  puts "  i = #{i}"
end

# 遍历数组
fruits = ["苹果", "香蕉", "橙子"]
puts "\nfor 遍历数组："
for fruit in fruits
  puts "  水果：#{fruit}"
end

# 注意：Ruby 中更推荐使用 each 而非 for 循环
# for 循环会创建外部变量，可能导致意外

# ---------- 5. while 循环 ----------
puts "\n========== 5. while 循环 =========="

# 基本 while
i = 1
puts "while 循环（1 到 5）："
while i <= 5
  puts "  i = #{i}"
  i += 1
end

# while 修饰符
i = 1
puts "while 修饰符写法："
begin
  puts "  i = #{i}"
  i += 1
end while i <= 3

# ---------- 6. until 循环 ----------
puts "\n========== 6. until 循环 =========="

# until 是 while not 的反义
i = 1
puts "until 循环（到 5 停止）："
until i > 5
  puts "  i = #{i}"
  i += 1
end

# ---------- 7. each 迭代器（最常用！）----------
puts "\n========== 7. each 迭代器 =========="

# 数组 each
numbers = [1, 2, 3, 4, 5]
puts "数组 each 遍历："
numbers.each do |n|
  puts "  数字：#{n}"
end

# 单行块写法（花括号）
puts "\n单行块写法："
numbers.each { |n| puts "  数字 x 2 = #{n * 2}" }

# each_with_index（带索引）
puts "\neach_with_index："
fruits = ["苹果", "香蕉", "橙子"]
fruits.each_with_index do |fruit, index|
  puts "  第 #{index + 1} 个水果：#{fruit}"
end

# 范围 each
puts "\n范围 each："
(1..3).each { |i| puts "  第 #{i} 次" }

# times 方法（整数的迭代器）
puts "\n3.times："
3.times do |i|
  puts "  执行第 #{i + 1} 次"
end

# upto / downto
puts "\n1.upto(3)："
1.upto(3) { |i| puts "  #{i}" }

puts "\n3.downto(1)："
3.downto(1) { |i| puts "  #{i}" }

# ---------- 8. case 语句 ----------
puts "\n========== 8. case 语句 =========="

# 基本用法（值匹配）
score = 85
grade = case score
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
puts "分数 #{score}，等级：#{grade}"

# case 与类型匹配
puts "\ncase 类型匹配："
value = "hello"
type = case value
       when String
         "字符串"
       when Integer
         "整数"
       when Float
         "浮点数"
       when Array
         "数组"
       else
         "未知类型"
       end
puts "#{value.inspect} 的类型是：#{type}"

# case 不带参数（类似 if/elsif）
puts "\ncase 不带参数："
x = 15
result = case
         when x > 20
           "大于 20"
         when x > 10
           "大于 10"
         when x > 0
           "大于 0"
         else
           "小于等于 0"
         end
puts "x = #{x}，#{result}"

# case 与正则表达式
puts "\ncase 正则匹配："
email = "user@example.com"
case email
when /@gmail\.com$/
  puts "Gmail 邮箱"
when /@qq\.com$/
  puts "QQ 邮箱"
when /@/
  puts "其他邮箱"
else
  puts "不是邮箱格式"
end

# ---------- 9. 循环控制 ----------
puts "\n========== 9. 循环控制（break/next/redo）=========="

# break：跳出循环
puts "break 示例（遇到 3 停止）："
[1, 2, 3, 4, 5].each do |n|
  break if n == 3
  puts "  n = #{n}"
end

# next：跳过当前迭代
puts "\nnext 示例（跳过偶数）："
(1..5).each do |n|
  next if n.even?
  puts "  n = #{n}（奇数）"
end

# redo：重新开始当前迭代
puts "\nredo 示例（模拟重试）："
attempts = 0
[1].each do
  attempts += 1
  puts "  第 #{attempts} 次尝试"
  redo if attempts < 3
end

# ---------- 10. 安全领域的条件判断示例 ----------
puts "\n========== 10. 安全场景示例 =========="

# 模拟端口扫描结果判断
port = 8080
service = case port
          when 21
            "FTP"
          when 22
            "SSH"
          when 80, 8080, 8000
            "HTTP"
          when 443, 8443
            "HTTPS"
          when 3306
            "MySQL"
          else
            "未知服务"
          end
puts "端口 #{port} 对应的服务：#{service}"

# 模拟漏洞等级判断
cvss_score = 7.5
severity = case cvss_score
           when 9.0..10.0
             "严重 (Critical)"
           when 7.0...9.0
             "高危 (High)"
           when 4.0...7.0
             "中危 (Medium)"
           when 0.1...4.0
             "低危 (Low)"
           else
             "信息 (Info)"
           end
puts "CVSS 分数 #{cvss_score}，漏洞等级：#{severity}"

puts "\n========== 示例运行结束 =========="
