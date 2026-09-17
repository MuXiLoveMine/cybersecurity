# ============================================================
# Ruby 哈希（Hash）：创建、增删改查、遍历、嵌套哈希、符号作为 key
# 运行方式：ruby 05_hash.rb
# ============================================================

# ---------- 1. 哈希创建 ----------
puts "========== 1. 哈希创建 =========="

# 符号作为 key（推荐，Ruby 1.9+ 的新语法）
user = { name: "张三", age: 25, email: "zhangsan@example.com" }
puts "符号 key 哈希：#{user.inspect}"

# 传统语法（hashrocket =>），可使用任意类型的 key
user_old = { :name => "李四", :age => 30 }
puts "传统语法哈希：#{user_old.inspect}"

# 字符串作为 key
user_str = { "name" => "王五", "age" => 28 }
puts "字符串 key 哈希：#{user_str.inspect}"

# 空哈希
empty_hash = {}
empty_hash2 = Hash.new
puts "空哈希：#{empty_hash.inspect}"

# 指定默认值的哈希
default_hash = Hash.new(0)    # 不存在的 key 返回 0 而不是 nil
default_hash[:a] += 1
puts "带默认值的哈希：#{default_hash.inspect}"
puts "不存在的 key :b = #{default_hash[:b]}"

# ---------- 2. 访问元素 ----------
puts "\n========== 2. 访问元素 =========="

user = { name: "张三", age: 25, email: "zhangsan@example.com" }
puts "哈希：#{user.inspect}"

puts "user[:name] = #{user[:name]}"
puts "user[:age] = #{user[:age]}"
puts "user[:email] = #{user[:email]}"

# 不存在的 key 返回 nil
puts "user[:phone] = #{user[:phone].inspect}（不存在的 key）"

# fetch 方法（更安全，可指定默认值）
puts "user.fetch(:name) = #{user.fetch(:name)}"
puts "user.fetch(:phone, '无') = #{user.fetch(:phone, '无')}"
puts "user.fetch(:phone) { |k| \"键 #{k} 不存在\" } = #{user.fetch(:phone) { |k| "键 #{k} 不存在" }}"

# dig 方法（安全访问嵌套哈希，Ruby 2.3+）
data = { user: { profile: { name: "Alice" } } }
puts "data.dig(:user, :profile, :name) = #{data.dig(:user, :profile, :name)}"
puts "data.dig(:user, :profile, :phone) = #{data.dig(:user, :profile, :phone).inspect}"
puts "data.dig(:a, :b, :c) = #{data.dig(:a, :b, :c).inspect}（深层不存在返回 nil）"

# ---------- 3. 添加和修改 ----------
puts "\n========== 3. 添加和修改 =========="

user = { name: "张三", age: 25 }
puts "原始哈希：#{user.inspect}"

# 添加新键值对
user[:email] = "zhangsan@example.com"
puts "添加 email 后：#{user.inspect}"

# 修改已有键的值
user[:age] = 26
puts "修改 age 后：#{user.inspect}"

# store 方法（等同于 []=）
user.store(:phone, "13800138000")
puts "store 添加 phone 后：#{user.inspect}"

# merge 合并（不修改原哈希）
new_user = user.merge({ role: "admin", active: true })
puts "merge 后新哈希：#{new_user.inspect}"
puts "原哈希不变：#{user.inspect}"

# merge! 合并（修改原哈希）
user.merge!({ role: "user", city: "北京" })
puts "merge! 后原哈希：#{user.inspect}"

# ---------- 4. 删除元素 ----------
puts "\n========== 4. 删除元素 =========="

user = { name: "张三", age: 25, email: "zhangsan@example.com", city: "北京" }
puts "原始哈希：#{user.inspect}"

# delete 删除指定 key
removed = user.delete(:city)
puts "delete(:city) 删除的值：#{removed}"
puts "删除后：#{user.inspect}"

# delete_if 按条件删除
user.delete_if { |key, value| value.nil? }
puts "delete_if 删除 nil 值后：#{user.inspect}"

# select! / keep_if 保留满足条件的
user[:tmp] = "临时数据"
puts "添加 tmp 后：#{user.inspect}"
user.keep_if { |k, v| k.to_s.length > 3 }
puts "keep_if 保留 key 长度>3 的：#{user.inspect}"

# clear 清空
user.clear
puts "clear 后：#{user.inspect}"

# ---------- 5. 遍历哈希 ----------
puts "\n========== 5. 遍历哈希 =========="

user = { name: "张三", age: 25, email: "zhangsan@example.com" }

# each（最常用）
puts "each 遍历："
user.each do |key, value|
  puts "  #{key} => #{value}"
end

# each_pair（each 的别名）
puts "\neach_pair 遍历："
user.each_pair { |k, v| puts "  #{k} = #{v}" }

# each_key（只遍历 key）
puts "\neach_key 遍历："
user.each_key { |k| puts "  key: #{k}" }

# each_value（只遍历 value）
puts "\neach_value 遍历："
user.each_value { |v| puts "  value: #{v}" }

# ---------- 6. keys、values 和其他查询 ----------
puts "\n========== 6. keys、values 和查询方法 =========="

user = { name: "张三", age: 25, email: "zhangsan@example.com" }
puts "哈希：#{user.inspect}"

puts "keys：#{user.keys.inspect}"
puts "values：#{user.values.inspect}"
puts "length / size：#{user.length} / #{user.size}"
puts "empty?：#{user.empty?}"

# has_key? / key? / include? / member?
puts "has_key?(:name)：#{user.has_key?(:name)}"
puts "key?(:phone)：#{user.key?(:phone)}"
puts "include?(:age)：#{user.include?(:age)}"

# has_value? / value?
puts "has_value?('张三')：#{user.has_value?('张三')}"
puts "value?(100)：#{user.value?(100)}"

# key（根据值找 key）
puts "key('张三')：#{user.key('张三')}"

# ---------- 7. 嵌套哈希 ----------
puts "\n========== 7. 嵌套哈希 =========="

# 多层嵌套的哈希
company = {
  name: "示例科技",
  address: "北京市朝阳区",
  departments: {
    tech: {
      manager: "李工",
      employees: 20
    },
    sales: {
      manager: "王经理",
      employees: 15
    },
    hr: {
      manager: "张主管",
      employees: 5
    }
  }
}

puts "公司名：#{company[:name]}"
puts "技术部经理：#{company[:departments][:tech][:manager]}"
puts "销售部员工数：#{company[:departments][:sales][:employees]}"

# 遍历嵌套哈希
puts "\n各部门信息："
company[:departments].each do |dept_key, dept_info|
  puts "  #{dept_key} 部门：经理 #{dept_info[:manager]}，员工 #{dept_info[:employees]} 人"
end

# 安全访问深层嵌套（dig 方法）
puts "\n使用 dig 安全访问："
puts "技术部经理：#{company.dig(:departments, :tech, :manager)}"
puts "不存在的路径：#{company.dig(:departments, :finance, :manager).inspect}"

# ---------- 8. 哈希转换 ----------
puts "\n========== 8. 哈希转换 =========="

user = { name: "张三", age: 25 }

# 转数组
arr = user.to_a
puts "to_a：#{arr.inspect}"

# keys 转数组 / values 转数组
puts "keys.to_a：#{user.keys.to_a.inspect}"
puts "values.to_a：#{user.values.to_a.inspect}"

# invert（key 和 value 互换）
puts "invert：#{user.invert.inspect}"

# ---------- 9. select / reject ----------
puts "\n========== 9. select / reject =========="

scores = { 数学: 95, 语文: 82, 英语: 78, 物理: 90, 化学: 65 }
puts "成绩：#{scores.inspect}"

# select 筛选
high_scores = scores.select { |subject, score| score >= 90 }
puts "90 分以上：#{high_scores.inspect}"

# reject 排除
passed = scores.reject { |subject, score| score < 60 }
puts "及格科目：#{passed.inspect}"

# ---------- 10. 符号作为 key 的优势 ----------
puts "\n========== 10. 符号作为 key 的优势 =========="

# 1. 比较速度快（符号是单例，比较对象 ID 即可）
puts ":name.object_id == :name.object_id：#{:name.object_id == :name.object_id}"
puts "\"name\".object_id == \"name\".object_id：#{"name".object_id == "name".object_id}"

# 2. 内存占用小（相同符号只有一个对象）
# 3. 语法简洁（Ruby 1.9+ 的 key: value 语法）

# 注意：字符串 key 和符号 key 是不同的！
hash = { name: "符号key", "name" => "字符串key" }
puts "\n混合 key 的哈希：#{hash.inspect}"
puts "hash[:name] = #{hash[:name]}"
puts "hash['name'] = #{hash['name']}"

# ---------- 11. 安全领域的哈希示例 ----------
puts "\n========== 11. 安全场景示例 =========="

# 模拟漏洞扫描结果
scan_result = {
  target: "example.com",
  scan_time: "2024-01-15 10:30:00",
  summary: {
    total: 15,
    critical: 2,
    high: 5,
    medium: 5,
    low: 3
  },
  vulnerabilities: [
    { id: "CVE-2024-0001", severity: "critical", cvss: 9.8, description: "SQL注入漏洞" },
    { id: "CVE-2024-0002", severity: "high", cvss: 7.5, description: "XSS跨站脚本" },
    { id: "CVE-2024-0003", severity: "medium", cvss: 5.3, description: "信息泄露" }
  ]
}

puts "扫描目标：#{scan_result[:target]}"
puts "扫描时间：#{scan_result[:scan_time]}"
puts "漏洞总数：#{scan_result[:summary][:total]}"
puts "严重漏洞：#{scan_result[:summary][:critical]}"
puts "高危漏洞：#{scan_result[:summary][:high]}"

puts "\n漏洞详情："
scan_result[:vulnerabilities].each do |vuln|
  puts "  [#{vuln[:severity].upcase}] #{vuln[:id]} - #{vuln[:description]} (CVSS: #{vuln[:cvss]})"
end

# 模拟请求头哈希
headers = {
  "User-Agent" => "Mozilla/5.0",
  "Accept" => "text/html",
  "Authorization" => "Bearer token123",
  "Content-Type" => "application/json"
}

puts "\nHTTP 请求头："
headers.each { |k, v| puts "  #{k}: #{v}" }

# 模拟端口服务映射
port_services = {
  21 => "FTP",
  22 => "SSH",
  23 => "Telnet",
  25 => "SMTP",
  53 => "DNS",
  80 => "HTTP",
  110 => "POP3",
  143 => "IMAP",
  443 => "HTTPS",
  3306 => "MySQL",
  3389 => "RDP",
  5432 => "PostgreSQL",
  6379 => "Redis",
  8080 => "HTTP-Proxy"
}

open_ports = [22, 80, 443, 3306, 8080]
puts "\n开放端口对应的服务："
open_ports.each do |port|
  service = port_services.fetch(port, "未知服务")
  puts "  端口 #{port} -> #{service}"
end

puts "\n========== 示例运行结束 =========="
