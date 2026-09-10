# ============================================================
# Ruby 字符串操作：拼接、插值、查找、分割、替换、格式化、正则方法
# 运行方式：ruby 06_string.rb
# ============================================================

# ---------- 1. 字符串创建 ----------
puts "========== 1. 字符串创建 =========="

# 双引号字符串（支持插值和转义字符）
str1 = "Hello, Ruby!"
puts "双引号：#{str1}"

# 单引号字符串（不支持插值，转义支持有限）
str2 = 'Hello, Ruby!'
puts "单引号：#{str2}"

# 单引号 vs 双引号的区别
name = "Ruby"
puts "双引号插值：Hello, #{name}!"
puts '单引号原样：Hello, #{name}!'

# 转义字符
puts "换行符：第一行\n第二行"
puts "制表符：列1\t列2\t列3"
puts "反斜杠：\\"
puts "双引号：\"quoted\""

# %Q / %q 语法（适合包含大量引号的字符串）
str3 = %Q{他说："你好，#{name}！"}
puts "%Q：#{str3}"

str4 = %q{他说："你好，Ruby！"}   # %q 不支持插值
puts "%q：#{str4}"

# heredoc 多行字符串
multiline = <<~EOF
  这是第一行
  这是第二行
  这是第三行
EOF
puts "heredoc 多行字符串："
puts multiline

# ---------- 2. 字符串拼接 ----------
puts "\n========== 2. 字符串拼接 =========="

# + 拼接（不修改原字符串）
a = "Hello"
b = "World"
result = a + ", " + b + "!"
puts "用 + 拼接：#{result}"
puts "原字符串 a 不变：#{a}"

# << 追加（修改原字符串，破坏性）
str = "Hello"
str << ", Ruby!"
puts "用 << 追加：#{str}"

# concat 方法
str = "Hello"
str.concat(" World")
puts "concat：#{str}"

# 多次拼接
puts "重复 3 次：#{"ab" * 3}"

# ---------- 3. 字符串插值 ----------
puts "\n========== 3. 字符串插值 =========="

# 基本插值
name = "张三"
age = 25
puts "我叫#{name}，今年#{age}岁。"

# 插值中可以执行表达式
puts "1 + 2 = #{1 + 2}"
puts "年龄的平方 = #{age ** 2}"

# 插值中调用方法
puts "姓名大写：#{name.upcase}"
puts "姓名长度：#{name.length}"

# 格式字符串
puts "格式：%.2f" % 3.14159
puts "格式：%05d" % 42
puts "格式：%s 今年 %d 岁" % ["李四", 30]

# sprintf
result = sprintf("姓名：%s，分数：%.1f", "王五", 95.5)
puts "sprintf：#{result}"

# ---------- 4. 字符串长度与空判断 ----------
puts "\n========== 4. 字符串长度与空判断 =========="

str = "Hello, Ruby!"
puts "字符串：#{str}"
puts "length / size：#{str.length} / #{str.size}"
puts "empty?：#{str.empty?}"

empty_str = ""
puts "空字符串 empty?：#{empty_str.empty?}"

# 只包含空白字符的判断
blank_str = "   "
puts "\"   \" empty?：#{blank_str.empty?}"
puts "\"   \" strip 后 empty?：#{blank_str.strip.empty?}"

# ---------- 5. 访问子串 ----------
puts "\n========== 5. 访问子串 =========="

str = "Hello, Ruby!"
puts "字符串：#{str}"

# 索引访问单个字符
puts "str[0] = #{str[0]}"
puts "str[7] = #{str[7]}"
puts "str[-1] = #{str[-1]}（最后一个字符）"
puts "str[-2] = #{str[-2]}（倒数第二个）"

# 范围访问子串
puts "str[0..4] = #{str[0..4]}（索引 0 到 4）"
puts "str[7...11] = #{str[7...11]}（索引 7 到 10）"
puts "str[7..-1] = #{str[7..-1]}（从索引 7 到末尾）"

# slice 方法
puts "str.slice(7, 4) = #{str.slice(7, 4)}（从索引7开始，长度4）"

# ---------- 6. 查找与包含 ----------
puts "\n========== 6. 查找与包含 =========="

str = "Hello, Ruby! Ruby is great."
puts "字符串：#{str}"

# include? 是否包含
puts "include?('Ruby')：#{str.include?('Ruby')}"
puts "include?('Python')：#{str.include?('Python')}"

# index 查找位置（第一次出现）
puts "index('Ruby')：#{str.index('Ruby')}"
puts "index('Ruby', 8)：#{str.index('Ruby', 8)}（从索引 8 开始找）"
puts "index('Python')：#{str.index('Python').inspect}（没找到返回 nil）"

# rindex 从右往左找
puts "rindex('Ruby')：#{str.rindex('Ruby')}（最后一次出现的位置）"

# start_with? / end_with?
puts "start_with?('Hello')：#{str.start_with?('Hello')}"
puts "end_with?('great.')：#{str.end_with?('great.')}"

# count 计数
puts "count('R')：#{str.count('R')}"
puts "count('aeiou')：#{str.count('aeiou')}（元音字母数量）"

# ---------- 7. 分割 ----------
puts "\n========== 7. 分割 =========="

# 按分隔符分割
csv = "苹果,香蕉,橙子,葡萄"
fruits = csv.split(",")
puts "split(',')：#{fruits.inspect}"

# 限制分割次数
data = "a,b,c,d,e"
parts = data.split(",", 3)
puts "split(',', 3)：#{parts.inspect}（只分割成 3 份）"

# 按空格分割（默认按空白字符分割）
sentence = "Hello   Ruby   World"
words = sentence.split
puts "split（默认按空白）：#{words.inspect}"

# 按换行分割
lines = "第一行\n第二行\n第三行"
puts "按换行分割：#{lines.lines.inspect}"

# each_line 逐行遍历
puts "each_line 遍历："
lines.each_line { |line| puts "  #{line.strip}" }

# ---------- 8. 替换 ----------
puts "\n========== 8. 替换 =========="

str = "Hello, Ruby! Ruby is fun."
puts "原字符串：#{str}"

# sub 替换第一个匹配
result = str.sub("Ruby", "World")
puts "sub('Ruby', 'World')：#{result}"

# gsub 全局替换
result = str.gsub("Ruby", "World")
puts "gsub('Ruby', 'World')：#{result}"

# 破坏性替换（带 !）
str2 = str.dup
str2.gsub!("Ruby", "Python")
puts "gsub! 后：#{str2}"

# 使用块进行替换
str3 = "abc123def456"
result = str3.gsub(/\d+/) { |match| match.to_i * 2 }
puts "gsub 块替换（数字翻倍）：#{result}"

# 哈希替换
replacements = { "a" => "4", "e" => "3", "i" => "1", "o" => "0" }
result = "Hello World".gsub(/[aeio]/, replacements)
puts "gsub 哈希替换（leet语）：#{result}"

# ---------- 9. 大小写转换 ----------
puts "\n========== 9. 大小写转换 =========="

str = "Hello, Ruby!"
puts "原字符串：#{str}"

puts "upcase：#{str.upcase}"
puts "downcase：#{str.downcase}"
puts "swapcase：#{str.swapcase}（大小写互换）"
puts "capitalize：#{str.capitalize}（首字母大写，其余小写）"

# ---------- 10. 去除空白 ----------
puts "\n========== 10. 去除空白 =========="

str = "   Hello, Ruby!   "
puts "原字符串：'#{str}'"

puts "strip：'#{str.strip}'（两端去除）"
puts "lstrip：'#{str.lstrip}'（左侧去除）"
puts "rstrip：'#{str.rstrip}'（右侧去除）"

# chomp 去除末尾换行
line = "hello\n"
puts "chomp：'#{line.chomp}'（去除末尾换行）"

# chop 去除最后一个字符
puts "chop：'#{str.chop}'（去除最后一个字符）"

# ---------- 11. 字符串与数组转换 ----------
puts "\n========== 11. 字符串与数组转换 =========="

# 字符串转字符数组
str = "Ruby"
chars = str.chars
puts "chars：#{chars.inspect}"

# 每个字符处理
result = str.each_char.map { |c| c + c }.join
puts "每个字符翻倍：#{result}"

# 字节
puts "bytes：#{str.bytes.inspect}"

# ---------- 12. 字符串与正则 ----------
puts "\n========== 12. 字符串与正则 =========="

email = "user@example.com"

# =~ 匹配操作符
puts "email =~ /@/：#{email =~ /@/}（匹配位置）"
puts "email =~ /#/：#{email =~ /#/}（不匹配返回 nil）"

# match 方法
match_data = /(\w+)@(\w+\.\w+)/.match(email)
if match_data
  puts "match 成功："
  puts "  完整匹配：#{match_data[0]}"
  puts "  用户名：#{match_data[1]}"
  puts "  域名：#{match_data[2]}"
end

# scan 扫描所有匹配
text = "邮箱：alice@example.com 和 bob@test.org"
emails = text.scan(/[\w.]+@[\w.]+/)
puts "scan 找到的邮箱：#{emails.inspect}"

# gsub 正则替换
phone = "138-1234-5678"
result = phone.gsub(/-/, "")
puts "gsub 去除横杠：#{result}"

# ---------- 13. 其他常用方法 ----------
puts "\n========== 13. 其他常用方法 =========="

str = "Hello"
puts "字符串：#{str}"

puts "reverse：#{str.reverse}"
puts "hex（十六进制转十进制）：#{"FF".hex}"
puts "oct（八进制转十进制）：#{"17".oct}"
puts "to_i：#{"123".to_i}"
puts "to_f：#{"3.14".to_f}"

# ljust / rjust / center（填充对齐）
puts "ljust(10, '-')：'#{"Hello".ljust(10, '-')}'"
puts "rjust(10, '-')：'#{"Hello".rjust(10, '-')}'"
puts "center(11, '-')：'#{"Hello".center(11, '-')}'"

# tr 字符替换
puts "tr('el', 'EL')：#{str.tr('el', 'EL')}"
puts "tr('a-z', 'A-Z')：#{'hello'.tr('a-z', 'A-Z')}"

# ---------- 14. 安全领域的字符串示例 ----------
puts "\n========== 14. 安全场景示例 =========="

# 1. URL 解析
url = "https://admin:password@example.com:8443/path/to/page?id=123&name=test#section"
puts "URL：#{url}"

# 提取协议
protocol = url.match(/^(\w+):\/\//)[1]
puts "协议：#{protocol}"

# 提取域名
domain = url.match(/:\/\/([^\/:]+)/)[1]
puts "域名：#{domain}"

# 2. Base64 编码解码
require 'base64'
original = "admin:password"
encoded = Base64.encode64(original)
puts "\nBase64 编码："
puts "  原始：#{original}"
puts "  编码：#{encoded.strip}"
puts "  解码：#{Base64.decode64(encoded)}"

# 3. Hex 编码
str = "Hello"
hex = str.each_byte.map { |b| "%02x" % b }.join
puts "\nHex 编码："
puts "  原始：#{str}"
puts "  Hex：#{hex}"

# 4. 模拟 payload 构造
target = "http://example.com/search"
payload = "<script>alert('XSS')</script>"
puts "\nXSS payload 构造："
puts "  目标：#{target}"
puts "  Payload：#{payload}"
puts "  完整 URL：#{target}?q=#{URI.encode_www_form_component(payload)}"

# 5. 敏感信息脱敏
email = "user@example.com"
masked_email = email.gsub(/(.{1}).+(@.+)/, '\1***\2')
puts "\n邮箱脱敏：#{email} -> #{masked_email}"

phone = "13812345678"
masked_phone = phone.gsub(/(\d{3})\d{4}(\d{4})/, '\1****\2')
puts "手机号脱敏：#{phone} -> #{masked_phone}"

puts "\n========== 示例运行结束 =========="
