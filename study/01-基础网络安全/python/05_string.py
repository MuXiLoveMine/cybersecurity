# 05_string.py
# 字符串操作

s = "Hello World"
print("原始字符串:", s)
print("长度:", len(s))

# ===== 索引与切片 =====
print("\n===== 索引与切片 =====")
print("s[0] =", s[0])
print("s[-1] =", s[-1])
print("s[0:5] =", s[0:5])
print("s[6:] =", s[6:])
print("s[::2] =", s[::2])
print("s[::-1] =", s[::-1])  # 反转

# ===== 大小写转换 =====
print("\n===== 大小写转换 =====")
print("upper():", s.upper())
print("lower():", s.lower())
print("title():", s.title())
print("capitalize():", s.capitalize())
print("swapcase():", s.swapcase())

# ===== 去除空白 =====
print("\n===== 去除空白 =====")
s2 = "  hello world  "
print(f"原始: '{s2}'")
print(f"strip(): '{s2.strip()}'")
print(f"lstrip(): '{s2.lstrip()}'")
print(f"rstrip(): '{s2.rstrip()}'")

# ===== 查找 =====
print("\n===== 查找 =====")
print("find('World'):", s.find("World"))     # 6
print("find('world'):", s.find("world"))     # -1（找不到）
print("index('World'):", s.index("World"))   # 6
print("count('l'):", s.count("l"))           # 3
print("startswith('He'):", s.startswith("He"))
print("endswith('ld'):", s.endswith("ld"))

# ===== 替换 =====
print("\n===== 替换 =====")
print("replace('World', 'Python'):", s.replace("World", "Python"))
print("replace('l', 'L'):", s.replace("l", "L"))
print("replace('l', 'L', 1):", s.replace("l", "L", 1))  # 只替换第一个

# ===== 分割与连接 =====
print("\n===== 分割与连接 =====")
s3 = "apple,banana,cherry,date"
parts = s3.split(",")
print("split(','):", parts)
print("split(',', 2):", s3.split(",", 2))  # 分割2次

fruits = ["apple", "banana", "cherry"]
print("join:", " - ".join(fruits))

# ===== 判断 =====
print("\n===== 判断 =====")
num_str = "12345"
print(f"'{num_str}'.isdigit():", num_str.isdigit())

alpha_str = "Hello"
print(f"'{alpha_str}'.isalpha():", alpha_str.isalpha())

alnum_str = "abc123"
print(f"'{alnum_str}'.isalnum():", alnum_str.isalnum())

space_str = "   "
print(f"'{space_str}'.isspace():", space_str.isspace())

# ===== 填充对齐 =====
print("\n===== 填充对齐 =====")
s4 = "hello"
print(f"center(11): '{s4.center(11)}'")
print(f"ljust(11): '{s4.ljust(11)}'")
print(f"rjust(11, '0'): '{s4.rjust(11, '0')}'")

# ===== 格式化 =====
print("\n===== 格式化 =====")
name = "张三"
age = 25

# f-string（推荐）
print(f"姓名: {name}, 年龄: {age}")
print(f"明年年龄: {age + 1}")
print(f"价格: {3.14159:.2f}")

# format 方法
print("姓名: {}, 年龄: {}".format(name, age))
print("姓名: {0}, 年龄: {1}, 再次: {0}".format(name, age))
print("姓名: {n}, 年龄: {a}".format(n=name, a=age))

# % 格式化（旧风格）
print("姓名: %s, 年龄: %d" % (name, age))

# ===== 字符串判断 =====
print("\n===== 包含判断 =====")
text = "Hello World"
print("'World' in text:", "World" in text)
print("'world' in text:", "world" in text)
print("'hello' not in text:", "hello" not in text)
