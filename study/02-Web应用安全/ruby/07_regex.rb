# ============================================================
# Ruby 正则表达式（Regexp）：匹配、捕获、替换、常用模式
# 运行方式：ruby 07_regex.rb
# ============================================================

# ---------- 1. 正则表达式创建 ----------
puts "========== 1. 正则表达式创建 =========="

# 字面量方式（最常用）
re1 = /ruby/
puts "正则：#{re1.inspect}，类型：#{re1.class}"

# 不区分大小写
re2 = /ruby/i
puts "不区分大小写：#{re2.inspect}"

# 多行模式（. 匹配换行符）
re3 = /hello.world/m
puts "多行模式：#{re3.inspect}"

# %r{} 语法（适合包含 / 的模式）
re4 = %r{http://example.com/path}
puts "%r{} 语法：#{re4.inspect}"

# Regexp.new 构造
re5 = Regexp.new("ruby", Regexp::IGNORECASE)
puts "Regexp.new：#{re5.inspect}"

# ---------- 2. 匹配操作 ----------
puts "\n========== 2. 匹配操作 =========="

# =~ 操作符（返回匹配位置，未匹配返回 nil）
str = "Hello, Ruby is great!"
puts "字符串：#{str}"
puts "str =~ /Ruby/ = #{str =~ /Ruby/}"
puts "str =~ /Python/ = #{str =~ /Python/.inspect}"
puts "/Ruby/ =~ str = #{/Ruby/ =~ str}"

# match? 方法（返回 true/false）
puts "\nmatch? 方法："
puts "str.match?(/Ruby/)：#{str.match?(/Ruby/)}"
puts "str.match?(/python/i)：#{str.match?(/python/i)}"

# match 方法（返回 MatchData 对象）
puts "\nmatch 方法："
result = /Ruby/.match(str)
puts "/Ruby/.match(str) = #{result.inspect}"

result = /Python/.match(str)
puts "/Python/.match(str) = #{result.inspect}"

# ---------- 3. 捕获组 ----------
puts "\n========== 3. 捕获组 =========="

email = "user@example.com"
puts "邮箱：#{email}"

# 普通捕获组
match_data = /(\w+)@(\w+\.\w+)/.match(email)
if match_data
  puts "匹配成功！"
  puts "  完整匹配 [0]：#{match_data[0]}"
  puts "  第1组 [1]（用户名）：#{match_data[1]}"
  puts "  第2组 [2]（域名）：#{match_data[2]}"
end

# 命名捕获组
puts "\n命名捕获组："
match_data = /(?<user>\w+)@(?<domain>\w+\.\w+)/.match(email)
if match_data
  puts "  user：#{match_data[:user]}"
  puts "  domain：#{match_data[:domain]}"
end

# 非捕获组 (?:...)
puts "\n非捕获组："
str = "颜色是：红色"
match_data = /颜色是：(?:红色|蓝色|绿色)/.match(str)
puts "  只有 0 组：#{match_data[0]}"
puts "  没有第 1 组：#{match_data[1].inspect}"

# 多个捕获组
puts "\nURL 解析："
url = "https://example.com:8080/path/page"
match_data = /(\w+):\/\/([^:\/]+):?(\d*)?(\/.*)?/.match(url)
if match_data
  puts "  协议：#{match_data[1]}"
  puts "  域名：#{match_data[2]}"
  puts "  端口：#{match_data[3]}"
  puts "  路径：#{match_data[4]}"
end

# ---------- 4. 替换 ----------
puts "\n========== 4. 替换 =========="

# sub 替换第一个匹配
str = "Hello Ruby! Ruby is great."
puts "原字符串：#{str}"
puts "sub 替换第一个：#{str.sub(/Ruby/, 'World')}"

# gsub 全局替换
puts "gsub 全局替换：#{str.gsub(/Ruby/, 'World')}"

# 使用捕获组引用
phone = "13812345678"
puts "\n手机号格式化："
puts phone.gsub(/(\d{3})(\d{4})(\d{4})/, '\1-\2-\3')

# 使用命名捕获组
str = "日期：2024-01-15"
result = str.gsub(/(?<year>\d{4})-(?<month>\d{2})-(?<day>\d{2})/, '\k<month>/\k<day>/\k<year>')
puts "日期格式转换：#{result}"

# 块替换
str = "abc123def456ghi"
result = str.gsub(/\d+/) { |m| m.to_i * 2 }
puts "块替换（数字翻倍）：#{result}"

# ---------- 5. 常用元字符 ----------
puts "\n========== 5. 常用元字符 =========="

puts "--- 字符类 ---"
puts "/[aeiou]/ 匹配元音字母："
"Hello Ruby World".scan(/[aeiou]/) { |m| print "  #{m}" }
puts ""

puts "/[0-9]/ 匹配数字："
"abc123def456".scan(/[0-9]/) { |m| print "  #{m}" }
puts ""

puts "/[a-zA-Z]/ 匹配字母："
"abc123XYZ".scan(/[a-zA-Z]/) { |m| print "  #{m}" }
puts ""

puts "/[^0-9]/ 匹配非数字（否定字符类）："
"abc123".scan(/[^0-9]/) { |m| print "  #{m}" }
puts ""

puts "\n--- 预定义字符类 ---"
puts "/\\d/ 数字（等价 [0-9]）：#{"abc123".scan(/\d/).inspect}"
puts "/\\D/ 非数字：#{"abc123".scan(/\D/).inspect}"
puts "/\\w/ 单词字符 [a-zA-Z0-9_]：#{"hello_ruby!".scan(/\w/).inspect}"
puts "/\\W/ 非单词字符：#{"hello_ruby!".scan(/\W/).inspect}"
puts "/\\s/ 空白字符：#{"a b\tc".scan(/\s/).inspect}"
puts "/\\S/ 非空白字符：#{"a b\tc".scan(/\S/).inspect}"

puts "\n--- 锚点 ---"
puts "/^hello/ 以 hello 开头：#{"hello world".match?(/^hello/)}"
puts "/world$/ 以 world 结尾：#{"hello world".match?(/world$/)}"
puts "/\\Ahello/ 字符串开头：#{"hello world".match?(/\Ahello/)}"
puts "/world\\z/ 字符串结尾：#{"hello world".match?(/world\z/)}"
puts "/\\bword\\b/ 单词边界：#{"a word here".match?(/\bword\b/)}"

puts "\n--- 量词 ---"
puts "/*/ 零次或多次："
puts "  /ab*c/ 匹配 'ac'：#{"ac".match?(/ab*c/)}"
puts "  /ab*c/ 匹配 'abbc'：#{"abbc".match?(/ab*c/)}"

puts "/+/ 一次或多次："
puts "  /ab+c/ 匹配 'ac'：#{"ac".match?(/ab+c/)}"
puts "  /ab+c/ 匹配 'abbc'：#{"abbc".match?(/ab+c/)}"

puts "/?/ 零次或一次："
puts "  /colou?r/ 匹配 'color'：#{"color".match?(/colou?r/)}"
puts "  /colou?r/ 匹配 'colour'：#{"colour".match?(/colou?r/)}"

puts "/{n}/ 恰好 n 次："
puts "  /\\d{3}/ 匹配 3 位数字：#{"123".match?(/^\d{3}$/)}"

puts "/{n,}/ 至少 n 次："
puts "  /\\d{2,}/ 匹配至少 2 位：#{"1".match?(/^\d{2,}$/)}"

puts "/{n,m}/ n 到 m 次："
puts "  /\\d{2,4}/ 匹配 2-4 位：#{"123".match?(/^\d{2,4}$/)}"

# ---------- 6. scan 扫描所有匹配 ----------
puts "\n========== 6. scan 扫描所有匹配 =========="

text = "联系方式：alice@example.com 和 bob@test.org，还有 carol@mail.cn"
puts "文本：#{text}"

# 提取所有邮箱
emails = text.scan(/[\w.]+@[\w.]+\.\w+/)
puts "提取到的邮箱：#{emails.inspect}"

# 带捕获组的 scan 返回数组的数组
email_parts = text.scan(/(\w+)@(\w+\.\w+)/)
puts "邮箱各部分：#{email_parts.inspect}"

# 提取所有数字
numbers = "订单号 12345，金额 999 元，数量 3 件".scan(/\d+/)
puts "提取数字：#{numbers.inspect}"

# ---------- 7. 贪婪与非贪婪 ----------
puts "\n========== 7. 贪婪与非贪婪匹配 =========="

html = "<div>Hello</div><div>World</div>"
puts "HTML：#{html}"

# 贪婪匹配（默认，尽可能长）
greedy = html.match(/<div>(.*)<\/div>/)[1]
puts "贪婪匹配：#{greedy}"

# 非贪婪匹配（加 ?，尽可能短）
non_greedy = html.match(/<div>(.*?)<\/div>/)[1]
puts "非贪婪匹配：#{non_greedy}"

# ---------- 8. 常用正则模式 ----------
puts "\n========== 8. 常用正则模式 =========="

# 邮箱
email_pattern = /\A[\w+\-.]+@[a-z\d\-]+(\.[a-z\d\-]+)*\.[a-z]+\z/i
test_emails = ["user@example.com", "user.name@test.org", "invalid-email", "@no.com"]
puts "邮箱验证："
test_emails.each { |e| puts "  #{e} -> #{e.match?(email_pattern) ? '有效' : '无效'}" }

# 手机号（中国大陆）
phone_pattern = /\A1[3-9]\d{9}\z/
test_phones = ["13812345678", "19988887777", "12345678901", "1381234"]
puts "\n手机号验证："
test_phones.each { |p| puts "  #{p} -> #{p.match?(phone_pattern) ? '有效' : '无效'}" }

# IP 地址（IPv4 简单版）
ip_pattern = /\A(\d{1,3}\.){3}\d{1,3}\z/
test_ips = ["192.168.1.1", "10.0.0.1", "256.1.1.1", "abc"]
puts "\nIP 地址验证（简单版）："
test_ips.each { |ip| puts "  #{ip} -> #{ip.match?(ip_pattern) ? '格式正确' : '格式错误'}" }

# URL
url_pattern = /\Ahttps?:\/\/[\w\-]+(\.[\w\-]+)+[/#?]?.*\z/
test_urls = ["https://example.com", "http://test.org/path?q=1", "ftp://invalid", "not-url"]
puts "\nURL 验证："
test_urls.each { |u| puts "  #{u} -> #{u.match?(url_pattern) ? '有效' : '无效'}" }

# 日期 YYYY-MM-DD
date_pattern = /\A\d{4}-\d{2}-\d{2}\z/
test_dates = ["2024-01-15", "2024/01/15", "2024-1-1", "12345"]
puts "\n日期格式验证："
test_dates.each { |d| puts "  #{d} -> #{d.match?(date_pattern) ? '正确' : '错误'}" }

# 身份证号（简单版）
id_pattern = /\A\d{17}[\dXx]\z/
test_ids = ["110101199001011234", "11010119900101123X", "1234567890123456789"]
puts "\n身份证号验证（简单版）："
test_ids.each { |id| puts "  #{id} -> #{id.match?(id_pattern) ? '格式正确' : '格式错误'}" }

# ---------- 9. 安全领域的正则示例 ----------
puts "\n========== 9. 安全场景示例 =========="

# 1. 检测 SQL 注入特征
sql_keywords = /('|--|;|union\s+select|drop\s+table|insert\s+into|delete\s+from|or\s+1=1|and\s+1=1)/i
test_inputs = [
  "正常用户名",
  "admin' --",
  "' OR '1'='1",
  "1; DROP TABLE users--",
  "admin"
]
puts "SQL 注入特征检测："
test_inputs.each do |input|
  has_injection = input.match?(sql_keywords)
  puts "  \"#{input}\" -> #{has_injection ? '有注入嫌疑' : '正常'}"
end

# 2. 检测 XSS 特征
xss_pattern = /(<script|javascript:|on\w+\s*=|alert\(|eval\(|document\.cookie)/i
test_xss = [
  "<script>alert('xss')</script>",
  "javascript:alert(1)",
  "<img src=x onerror=alert(1)>",
  "正常文本",
  "<a href='http://example.com'>链接</a>"
]
puts "\nXSS 特征检测："
test_xss.each do |input|
  has_xss = input.match?(xss_pattern)
  puts "  \"#{input[0..30]}...\" -> #{has_xss ? '有XSS嫌疑' : '正常'}"
end

# 3. 提取 HTTP 响应头信息
headers = <<~HEADERS
  HTTP/1.1 200 OK
  Date: Mon, 15 Jan 2024 10:00:00 GMT
  Server: Apache/2.4.41 (Ubuntu)
  X-Powered-By: PHP/7.4
  Content-Type: text/html; charset=UTF-8
  Set-Cookie: sessionid=abc123; path=/; HttpOnly
  Set-Cookie: csrftoken=xyz789; path=/
HEADERS

puts "\nHTTP 响应头解析："
# 提取 Server
server = headers.match(/^Server: (.+)$/)[1]
puts "  Server：#{server}"

# 提取所有 Set-Cookie
cookies = headers.scan(/^Set-Cookie: (.+)$/)
puts "  Cookies (#{cookies.length} 个)："
cookies.each { |c| puts "    #{c[0]}" }

# 提取状态码
status = headers.match(/^HTTP\/\d\.\d (\d+)/)[1]
puts "  状态码：#{status}"

# 4. 密码强度检测
def password_strength(password)
  score = 0
  score += 1 if password.length >= 8
  score += 1 if password.length >= 12
  score += 1 if password.match?(/[A-Z]/)
  score += 1 if password.match?(/[a-z]/)
  score += 1 if password.match?(/\d/)
  score += 1 if password.match?(/[^A-Za-z0-9]/)

  level = case score
          when 0..2 then "弱"
          when 3..4 then "中"
          when 5..6 then "强"
          end
  [score, level]
end

test_passwords = ["123456", "password", "Password123", "P@ssw0rd!2024", "abc"]
puts "\n密码强度检测："
test_passwords.each do |pw|
  score, level = password_strength(pw)
  puts "  \"#{pw}\" -> 得分 #{score}/6，强度：#{level}"
end

puts "\n========== 示例运行结束 =========="
