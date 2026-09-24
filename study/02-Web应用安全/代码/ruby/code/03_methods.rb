# ============================================================
# Ruby 方法：定义、参数、返回值、可变参数、块（block）、yield、lambda、proc
# 运行方式：ruby 03_methods.rb
# ============================================================

# ---------- 1. 方法定义与调用 ----------
puts "========== 1. 方法定义与调用 =========="

# 基本方法定义
def greet
  puts "Hello, Ruby!"
end

greet    # 调用方法
greet()  # 括号可省略

# ---------- 2. 参数与返回值 ----------
puts "\n========== 2. 参数与返回值 =========="

# 带参数的方法
def add(a, b)
  return a + b    # return 显式返回
end
puts "add(3, 5) = #{add(3, 5)}"

# Ruby 方法默认返回最后一行的值（可省略 return）
def multiply(a, b)
  a * b           # 隐式返回
end
puts "multiply(3, 5) = #{multiply(3, 5)}"

# 返回多个值（实际返回数组）
def min_max(arr)
  return arr.min, arr.max
end
result = min_max([3, 1, 4, 1, 5, 9])
puts "min_max 返回：#{result.inspect}"
min, max = min_max([3, 1, 4, 1, 5, 9])
puts "最小值 = #{min}，最大值 = #{max}"

# ---------- 3. 默认参数 ----------
puts "\n========== 3. 默认参数 =========="

def power(base, exponent = 2)
  base ** exponent
end

puts "power(3) = #{power(3)}（默认指数 2）"
puts "power(3, 3) = #{power(3, 3)}"
puts "power(2, 10) = #{power(2, 10)}"

# ---------- 4. 可变参数（splat 运算符 *）----------
puts "\n========== 4. 可变参数（splat）=========="

# 使用 * 接收任意数量的参数，封装为数组
def sum(*numbers)
  total = 0
  numbers.each { |n| total += n }
  total
end

puts "sum(1, 2, 3) = #{sum(1, 2, 3)}"
puts "sum(1, 2, 3, 4, 5) = #{sum(1, 2, 3, 4, 5)}"
puts "sum(100) = #{sum(100)}"
puts "sum() = #{sum()}"

# splat 也可以在参数中间
def greet_with(greeting, *names, suffix)
  names.each { |name| puts "  #{greeting}, #{name}#{suffix}" }
end

puts "可变参数示例："
greet_with("你好", "张三", "李四", "王五", "！")

# ---------- 5. 关键字参数 ----------
puts "\n========== 5. 关键字参数 =========="

def create_user(name:, age:, role: "user")
  { name: name, age: age, role: role }
end

user1 = create_user(name: "张三", age: 25)
puts "用户 1：#{user1.inspect}"

user2 = create_user(name: "李四", age: 30, role: "admin")
puts "用户 2：#{user2.inspect}"

# 关键字参数必须显式指定参数名，顺序可以任意
user3 = create_user(age: 22, name: "王五")
puts "用户 3：#{user3.inspect}"

# ---------- 6. 块（Block）----------
puts "\n========== 6. 块（Block）=========="

# 块是 Ruby 中非常重要的概念，是一段可传递的代码
# 两种写法：do...end（多行）和 {}（单行）

# 数组的 each 方法接受一个块
puts "数组 each 接受块："
[1, 2, 3].each do |n|
  puts "  #{n} 的平方 = #{n * n}"
end

# 单行块
puts "\n单行块："
[1, 2, 3].each { |n| puts "  #{n} x 2 = #{n * 2}" }

# ---------- 7. yield ----------
puts "\n========== 7. yield =========="

# 使用 yield 在方法内部执行传入的块
def my_method
  puts "  [方法开始]"
  yield if block_given?   # 如果有块传入就执行
  puts "  [方法结束]"
end

puts "调用方法并传入块："
my_method do
  puts "  这是块中的代码"
end

puts "\n不传块调用："
my_method

# yield 传参给块
puts "\nyield 传参："
def greet_by_name(name)
  puts "  方法：准备问候 #{name}"
  yield(name) if block_given?
end

greet_by_name("Ruby") do |n|
  puts "  块中：Hello, #{n}!"
end

# yield 多个参数
puts "\nyield 多个参数："
def calc(a, b)
  puts "  计算 #{a} 和 #{b}"
  result = yield(a, b)
  puts "  结果：#{result}"
end

calc(10, 5) { |x, y| x + y }
calc(10, 5) { |x, y| x * y }

# ---------- 8. block_given? ----------
puts "\n========== 8. block_given? =========="

# 判断是否有块传入
def optional_block
  if block_given?
    yield
    puts "  块已执行"
  else
    puts "  没有传入块"
  end
end

puts "传块："
optional_block { puts "  我是块" }

puts "不传块："
optional_block

# ---------- 9. Lambda ----------
puts "\n========== 9. Lambda =========="

# lambda 是一种将块封装为对象的方式
# 语法 1：lambda { ... }
my_lambda = lambda { |x| x * 2 }
puts "lambda.call(5) = #{my_lambda.call(5)}"

# 语法 2：-> params { ... }（stabby lambda，更常用）
square = ->(x) { x * x }
puts "square.call(6) = #{square.call(6)}"

# 其他调用方式
puts "square[7] = #{square[7]}"
puts "square.(8) = #{square.(8)}"

# lambda 检查参数数量
begin
  square.call(1, 2)    # 报错：参数数量不对
rescue ArgumentError => e
  puts "lambda 严格检查参数：#{e.message}"
end

# ---------- 10. Proc ----------
puts "\n========== 10. Proc =========="

# Proc 和 lambda 类似，但更宽松
my_proc = Proc.new { |x, y| puts "  Proc 收到：#{x.inspect}, #{y.inspect}" }

puts "Proc 不严格检查参数："
my_proc.call(1)               # 缺少的参数为 nil
my_proc.call(1, 2, 3)         # 多余的参数被忽略

# Proc 和 lambda 的另一个区别：return 行为
puts "\nProc 和 lambda 的 return 区别："

def test_lambda
  l = -> { return "从 lambda 返回" }
  l.call
  "方法正常结束"
end
puts "lambda 测试：#{test_lambda}"

def test_proc
  p = Proc.new { return "从 Proc 返回（直接跳出方法）" }
  p.call
  "方法正常结束"
end
puts "Proc 测试：#{test_proc}"

# ---------- 11. 方法作为块传递 ----------
puts "\n========== 11. 方法作为块传递（&:方法名）=========="

# &:to_i 是 Ruby 中的常用惯用法
numbers = ["1", "2", "3"]
result = numbers.map(&:to_i)
puts "\"1\",\"2\",\"3\" map(&:to_i) = #{result.inspect}"

words = ["hello", "world", "ruby"]
puts "upcase 后：#{words.map(&:upcase).inspect}"

# ---------- 12. 安全领域的方法示例 ----------
puts "\n========== 12. 安全场景示例 =========="

# 模拟端口扫描函数
def port_scan(host, ports = [80, 443, 22, 3306])
  puts "  开始扫描 #{host}..."
  open_ports = []
  ports.each do |port|
    # 模拟检测（实际场景中使用 Socket）
    open = [80, 443].include?(port)  # 假设 80 和 443 是开放的
    status = open ? "开放" : "关闭"
    puts "    端口 #{port}：#{status}"
    open_ports << port if open
    yield(port, open) if block_given?
  end
  open_ports
end

puts "端口扫描示例："
open_ports = port_scan("192.168.1.1") do |port, is_open|
  puts "    [回调] 端口 #{port} 检测完成，状态：#{is_open ? 'OPEN' : 'CLOSED'}"
end
puts "  开放端口：#{open_ports.inspect}"

# 模拟带选项的安全检查函数
def security_check(target, deep: false, timeout: 30, &block)
  puts "  安全检查目标：#{target}"
  puts "  深度扫描：#{deep ? '开启' : '关闭'}"
  puts "  超时时间：#{timeout}秒"
  
  vulnerabilities = []
  vulnerabilities << "SQL注入" if deep
  vulnerabilities << "XSS"
  vulnerabilities << "敏感信息泄露"
  
  vulnerabilities.each do |vuln|
    block.call(vuln, "中危") if block
  end
  
  vulnerabilities
end

puts "\n安全检查示例："
vulns = security_check("example.com", deep: true) do |vuln, severity|
  puts "    发现漏洞：#{vuln}（#{severity}）"
end
puts "  共发现 #{vulns.length} 个漏洞"

puts "\n========== 示例运行结束 =========="
