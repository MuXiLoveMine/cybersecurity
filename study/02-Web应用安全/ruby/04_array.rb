# ============================================================
# Ruby 数组（Array）：创建、增删改查、遍历、常用方法
# 运行方式：ruby 04_array.rb
# ============================================================

# ---------- 1. 数组创建 ----------
puts "========== 1. 数组创建 =========="

# 字面量方式（最常用）
arr1 = [1, 2, 3, 4, 5]
puts "数字数组：#{arr1.inspect}"

# 空数组
empty_arr = []
puts "空数组：#{empty_arr.inspect}"

# 数组可以包含不同类型的元素
mixed = [1, "hello", :sym, true, nil, 3.14]
puts "混合类型数组：#{mixed.inspect}"

# 使用 Array.new 创建
arr2 = Array.new(3)            # [nil, nil, nil]
puts "Array.new(3)：#{arr2.inspect}"

arr3 = Array.new(3, "default")
puts "Array.new(3, 'default')：#{arr3.inspect}"

arr4 = Array.new(3) { |i| i * 10 }
puts "Array.new(3) { |i| i*10 }：#{arr4.inspect}"

# 范围转数组
arr5 = (1..5).to_a
puts "(1..5).to_a：#{arr5.inspect}"

# %w 创建字符串数组（空格分隔）
words = %w(apple banana orange)
puts "%w(apple banana orange)：#{words.inspect}"

# %i 创建符号数组
symbols = %i(name age email)
puts "%i(name age email)：#{symbols.inspect}"

# ---------- 2. 访问元素 ----------
puts "\n========== 2. 访问元素 =========="

arr = [10, 20, 30, 40, 50]
puts "数组：#{arr.inspect}"

# 索引访问（从 0 开始）
puts "arr[0] = #{arr[0]}"
puts "arr[2] = #{arr[2]}"
puts "arr[4] = #{arr[4]}"

# 负数索引（从末尾开始，-1 是最后一个）
puts "arr[-1] = #{arr[-1]}（最后一个）"
puts "arr[-2] = #{arr[-2]}（倒数第二个）"

# 范围访问
puts "arr[1..3] = #{arr[1..3].inspect}（索引 1 到 3）"
puts "arr[1...3] = #{arr[1...3].inspect}（索引 1 到 2）"

# first 和 last
puts "arr.first = #{arr.first}"
puts "arr.last = #{arr.last}"
puts "arr.first(3) = #{arr.first(3).inspect}（前 3 个）"
puts "arr.last(2) = #{arr.last(2).inspect}（后 2 个）"

# fetch 方法（越界时可指定默认值或块）
puts "arr.fetch(2) = #{arr.fetch(2)}"
puts "arr.fetch(10, '默认值') = #{arr.fetch(10, '默认值')}"
puts "arr.fetch(10) { |i| \"索引#{i}不存在\" } = #{arr.fetch(10) { |i| "索引#{i}不存在" }}"

# ---------- 3. 添加元素 ----------
puts "\n========== 3. 添加元素 =========="

arr = [1, 2, 3]
puts "原始数组：#{arr.inspect}"

# push / << （末尾添加）
arr.push(4)
puts "push(4) 后：#{arr.inspect}"

arr << 5
puts "<< 5 后：#{arr.inspect}"

# unshift （开头添加）
arr.unshift(0)
puts "unshift(0) 后：#{arr.inspect}"

# insert （指定位置插入）
arr.insert(3, 99)
puts "insert(3, 99) 后：#{arr.inspect}"

# concat （合并数组）
arr.concat([100, 200])
puts "concat([100, 200]) 后：#{arr.inspect}"

# ---------- 4. 删除元素 ----------
puts "\n========== 4. 删除元素 =========="

arr = [1, 2, 3, 4, 5, 3, 6]
puts "原始数组：#{arr.inspect}"

# pop （删除末尾元素，返回被删元素）
removed = arr.pop
puts "pop 删除末尾：#{removed}，数组变为：#{arr.inspect}"

# shift （删除开头元素）
removed = arr.shift
puts "shift 删除开头：#{removed}，数组变为：#{arr.inspect}"

# delete （删除指定值的所有元素）
arr.delete(3)
puts "delete(3) 后：#{arr.inspect}"

# delete_at （删除指定索引的元素）
arr.delete_at(1)
puts "delete_at(1) 后：#{arr.inspect}"

# delete_if / reject! （按条件删除）
arr = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
arr.delete_if { |n| n.even? }
puts "delete_if 偶数后：#{arr.inspect}"

# compact （移除 nil）
arr = [1, nil, 2, nil, 3]
puts "有 nil 的数组：#{arr.inspect}"
puts "compact 后：#{arr.compact.inspect}"

# uniq （去重）
arr = [1, 2, 2, 3, 3, 3, 4]
puts "重复数组：#{arr.inspect}"
puts "uniq 后：#{arr.uniq.inspect}"

# ---------- 5. 修改元素 ----------
puts "\n========== 5. 修改元素 =========="

arr = [1, 2, 3, 4, 5]
puts "原始数组：#{arr.inspect}"

arr[0] = 10
puts "arr[0] = 10 后：#{arr.inspect}"

arr[-1] = 50
puts "arr[-1] = 50 后：#{arr.inspect}"

arr[1..2] = [20, 30]
puts "arr[1..2] = [20, 30] 后：#{arr.inspect}"

# fill 批量填充
arr = [1, 2, 3, 4, 5]
arr.fill(0)
puts "fill(0) 后：#{arr.inspect}"

# ---------- 6. 遍历数组 ----------
puts "\n========== 6. 遍历数组 =========="

arr = ["苹果", "香蕉", "橙子"]

# each （最常用）
puts "each 遍历："
arr.each do |fruit|
  puts "  水果：#{fruit}"
end

# each_with_index （带索引）
puts "\neach_with_index："
arr.each_with_index do |fruit, index|
  puts "  第 #{index + 1} 个：#{fruit}"
end

# reverse_each （反向遍历）
puts "\nreverse_each："
arr.reverse_each { |fruit| puts "  #{fruit}" }

# map / collect （转换每个元素，返回新数组）
numbers = [1, 2, 3]
puts "\nmap 转换："
doubled = numbers.map { |n| n * 2 }
puts "  原数组：#{numbers.inspect}"
puts "  map 后：#{doubled.inspect}"

# map! （修改原数组，! 表示破坏性方法）
numbers.map! { |n| n ** 2 }
puts "  map! 后原数组变为：#{numbers.inspect}"

# ---------- 7. 筛选与查询 ----------
puts "\n========== 7. 筛选与查询 =========="

numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
puts "数组：#{numbers.inspect}"

# select / find_all （选择满足条件的）
evens = numbers.select { |n| n.even? }
puts "select 偶数：#{evens.inspect}"

# reject （排除满足条件的）
odds = numbers.reject { |n| n.even? }
puts "reject 偶数（即奇数）：#{odds.inspect}"

# find / detect （找到第一个满足条件的）
first_even = numbers.find { |n| n.even? }
puts "find 第一个偶数：#{first_even}"

# include? （是否包含）
puts "include?(5)：#{numbers.include?(5)}"
puts "include?(100)：#{numbers.include?(100)}"

# any? （是否有任何一个满足）
puts "any? 大于 9：#{numbers.any? { |n| n > 9 }}"

# all? （是否全部满足）
puts "all? 大于 0：#{numbers.all? { |n| n > 0 }}"
puts "all? 大于 5：#{numbers.all? { |n| n > 5 }}"

# none? （没有一个满足）
puts "none? 小于 0：#{numbers.none? { |n| n < 0 }}"

# count （计数）
puts "count 偶数：#{numbers.count { |n| n.even? }}"

# ---------- 8. 排序与顺序 ----------
puts "\n========== 8. 排序与顺序 =========="

arr = [3, 1, 4, 1, 5, 9, 2, 6]
puts "原始数组：#{arr.inspect}"

# sort
puts "sort：#{arr.sort.inspect}"

# sort 自定义排序
sorted = arr.sort { |a, b| b <=> a }
puts "降序排序：#{sorted.inspect}"

# sort_by
words = ["apple", "pear", "banana", "kiwi"]
puts "按长度排序：#{words.sort_by { |w| w.length }.inspect}"

# reverse
puts "reverse：#{arr.reverse.inspect}"

# shuffle
puts "shuffle（打乱）：#{arr.shuffle.inspect}"

# ---------- 9. 数组运算 ----------
puts "\n========== 9. 数组运算 =========="

a = [1, 2, 3]
b = [3, 4, 5]

puts "a = #{a.inspect}"
puts "b = #{b.inspect}"
puts "a + b = #{(a + b).inspect}（拼接）"
puts "a - b = #{(a - b).inspect}（差集）"
puts "a & b = #{(a & b).inspect}（交集）"
puts "a | b = #{(a | b).inspect}（并集）"

# ---------- 10. 归约运算 ----------
puts "\n========== 10. 归约运算（reduce/inject）=========="

numbers = [1, 2, 3, 4, 5]
puts "数组：#{numbers.inspect}"

# reduce / inject 求和
sum = numbers.reduce(0) { |acc, n| acc + n }
puts "reduce 求和：#{sum}"

# 简写
sum = numbers.reduce(:+)
puts "reduce(:+) 求和：#{sum}"

# reduce 求乘积
product = numbers.reduce(:*)
puts "reduce(:*) 求积：#{product}"

# 拼接字符串
words = ["Hello", "Ruby", "World"]
result = words.reduce("") { |acc, word| acc + word + " " }
puts "reduce 拼接：#{result.strip}"

# ---------- 11. 其他常用方法 ----------
puts "\n========== 11. 其他常用方法 =========="

arr = [1, 2, 3, 4, 5]
puts "数组：#{arr.inspect}"

puts "length / size：#{arr.length} / #{arr.size}"
puts "empty?：#{arr.empty?}"
puts "sample（随机一个）：#{arr.sample}"
puts "sample(2)（随机两个）：#{arr.sample(2).inspect}"
puts "join(', ')：#{arr.join(', ')}"

# 扁平化
nested = [[1, 2], [3, 4], [5, [6, 7]]]
puts "嵌套数组：#{nested.inspect}"
puts "flatten：#{nested.flatten.inspect}"
puts "flatten(1)（只展开一层）：#{nested.flatten(1).inspect}"

# 组合（zip）
a = [1, 2, 3]
b = ["a", "b", "c"]
puts "a.zip(b)：#{a.zip(b).inspect}"

# ---------- 12. 安全领域的数组示例 ----------
puts "\n========== 12. 安全场景示例 =========="

# 模拟端口列表扫描
ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 3306, 3389, 8080]
puts "待扫描端口：#{ports.inspect}"

# 模拟开放端口
open_ports = ports.select { |p| [22, 80, 443, 3306].include?(p) }
puts "开放端口：#{open_ports.inspect}"

# 按服务分类
service_map = open_ports.map do |port|
  service = case port
            when 22 then "SSH"
            when 80 then "HTTP"
            when 443 then "HTTPS"
            when 3306 then "MySQL"
            else "未知"
            end
  { port: port, service: service }
end
puts "端口-服务映射："
service_map.each { |item| puts "  #{item[:port]} -> #{item[:service]}" }

# 模拟 CVE 列表排序
cves = [
  { id: "CVE-2024-0001", cvss: 9.8 },
  { id: "CVE-2024-0002", cvss: 5.3 },
  { id: "CVE-2024-0003", cvss: 7.5 },
  { id: "CVE-2024-0004", cvss: 10.0 }
]

# 按严重程度排序（高到低）
sorted_cves = cves.sort_by { |c| -c[:cvss] }
puts "\n按 CVSS 从高到低排序的 CVE："
sorted_cves.each { |c| puts "  #{c[:id]} - #{c[:cvss]}" }

# 统计高危数量
high_risk = cves.count { |c| c[:cvss] >= 7.0 }
puts "高危及以上漏洞数量：#{high_risk}"

puts "\n========== 示例运行结束 =========="
