# 09_regex.py
# 正则表达式（re 模块）

import re

# ===== 基本匹配 =====
print("===== 基本匹配 =====")

# match：从开头匹配
result = re.match(r"\d+", "123abc")
if result:
    print(f"match 结果: {result.group()}")  # 123

# search：查找第一个匹配
result = re.search(r"\d+", "abc123def")
if result:
    print(f"search 结果: {result.group()}")  # 123

# findall：查找所有匹配
results = re.findall(r"\d+", "abc123def456ghi789")
print(f"findall 结果: {results}")

# ===== 替换 =====
print("\n===== 替换 =====")

text = "今天是 2024年1月15日，温度 25 度"
result = re.sub(r"\d+", "X", text)
print(f"替换数字: {result}")

result = re.sub(r"\s+", "-", text)
print(f"替换空白: {result}")

# ===== 分割 =====
print("\n===== 分割 =====")

text2 = "a,b;c.d e"
parts = re.split(r"[,;.\s]", text2)
print(f"多分隔符分割: {parts}")

# ===== 常用正则模式 =====
print("\n===== 常用正则模式 =====")

# 邮箱
email = "test@example.com"
if re.match(r"^[\w.-]+@[\w.-]+\.\w+$", email):
    print(f"{email} 是有效的邮箱")

# 手机号
phone = "13812345678"
if re.match(r"^1[3-9]\d{9}$", phone):
    print(f"{phone} 是有效的手机号")

# IP 地址
ip = "192.168.1.1"
if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip):
    print(f"{ip} 看起来像 IP 地址")

# URL
url = "https://www.example.com/path?query=1"
if re.match(r"^https?://[\w.-]+(/.*)?$", url):
    print(f"{url} 看起来像 URL")

# ===== 分组捕获 =====
print("\n===== 分组捕获 =====")

text = "姓名: 张三, 年龄: 25, 城市: 北京"
pattern = r"姓名: (\w+), 年龄: (\d+), 城市: (\w+)"
result = re.search(pattern, text)
if result:
    print(f"全部匹配: {result.group(0)}")
    print(f"姓名: {result.group(1)}")
    print(f"年龄: {result.group(2)}")
    print(f"城市: {result.group(3)}")
    print(f"元组: {result.groups()}")

# 命名分组
pattern2 = r"姓名: (?P<name>\w+), 年龄: (?P<age>\d+)"
result2 = re.search(pattern2, text)
if result2:
    print(f"命名分组 name: {result2.group('name')}")
    print(f"命名分组 age: {result2.group('age')}")

# ===== 编译正则 =====
print("\n===== 编译正则 =====")

# 预编译，重复使用更高效
phone_pattern = re.compile(r"^1[3-9]\d{9}$")

numbers = ["13812345678", "12345678901", "1391234567", "18900001111"]
for num in numbers:
    if phone_pattern.match(num):
        print(f"  {num}: 有效")
    else:
        print(f"  {num}: 无效")

# ===== 标志位 =====
print("\n===== 标志位 =====")

text = "Hello World"

# 忽略大小写
result = re.findall(r"o", text)
print(f"普通查找 o: {result}")

result = re.findall(r"o", text, re.IGNORECASE)
print(f"忽略大小写查找 o: {result}")

# 多行模式
text3 = "line1\nline2\nline3"
result = re.findall(r"^line\d", text3, re.MULTILINE)
print(f"多行模式匹配行首: {result}")
