# array_hash_ruby

> **分类**：数组与哈希
> **说明**：Ruby 数组和哈希操作

---

## 语法

```ruby
arr = [item1, item2, ...]\nhash = { key1 => val1, key2 => val2 }
```

## 数组方法

push/pop/shift/unshift/slice/select/reject/map/reduce/sort/reverse/each/find/select

## 哈希方法

keys/values/has_key?/has_value?/fetch/merge/each/select/transform_values

## 示例代码

```ruby
# ===== 数组 =====
fruits = ["apple", "banana", "cherry"]

# 访问
fruits[0]            # "apple"
fruits.first         # "apple"
fruits.last          # "cherry"
fruits.length        # 3
fruits[0..1]         # ["apple", "banana"]

# 添加/删除
fruits.push("orange")     # 末尾添加
fruits << "grape"         # 末尾添加（运算符）
fruits.pop                # 末尾删除
fruits.unshift("mango")   # 开头添加
fruits.shift              # 开头删除

# 操作
fruits.include?("banana")  # 是否包含
fruits.index("banana")     # 索引
fruits.sort                # 排序
fruits.reverse             # 反转
fruits.uniq                # 去重
fruits.compact             # 移除 nil

# 遍历
fruits.each do |fruit|
  puts fruit
end

fruits.each_with_index do |fruit, i|
  puts "#{i}: #{fruit}"
end

# map/select/reject/reduce
nums = [1, 2, 3, 4, 5]
nums.map { |n| n * 2 }      # [2, 4, 6, 8, 10]
nums.select { |n| n.even? } # [2, 4]
nums.reject { |n| n.even? } # [1, 3, 5]
nums.reduce(:+)             # 15
nums.sum                    # 15
nums.find { |n| n > 3 }     # 4

# ===== 哈希 =====
person = {
  "name" => "Alice",
  "age" => 25,
  "city" => "Beijing"
}

# Symbol 作为键（更常见）
person = { name: "Alice", age: 25, city: "Beijing" }

# 访问
person[:name]         # "Alice"
person[:age]          # 25
person.fetch(:name)   # "Alice"
person.fetch(:email, "unknown@test.com")  # 带默认值

# 添加/修改
person[:email] = "alice@test.com"
person[:age] = 26

# 删除
person.delete(:city)

# 判断
person.has_key?(:name)   # true
person.has_value?(25)    # true
person.empty?            # false

# 遍历
person.each do |key, value|
  puts "#{key}: #{value}"
end

person.each_key { |k| puts k }
person.each_value { |v| puts v }

# keys/values
person.keys    # [:name, :age, :email]
person.values  # ["Alice", 26, "..."]

# 合并
defaults = { color: "red", size: "M" }
options = { size: "L" }
merged = defaults.merge(options)  # { color: "red", size: "L" }

# 过滤
person.select { |k, v| v.is_a?(String) }

# 其他
person.transform_values { |v| v.to_s.upcase }
person.slice(:name, :age)   # 只保留指定键
```
