# 02_variables.py
# 变量与数据类型

# ===== 变量定义 =====
name = "张三"
age = 25
height = 1.75
is_student = True

print(f"姓名: {name}, 类型: {type(name)}")
print(f"年龄: {age}, 类型: {type(age)}")
print(f"身高: {height}, 类型: {type(height)}")
print(f"是否学生: {is_student}, 类型: {type(is_student)}")

# 多变量赋值
a = b = c = 10
x, y, z = 1, 2, 3
print(f"a={a}, b={b}, c={c}")
print(f"x={x}, y={y}, z={z}")

# ===== 算术运算 =====
print("\n===== 算术运算 =====")
a, b = 10, 3
print(f"a = {a}, b = {b}")
print(f"加法: {a} + {b} = {a + b}")
print(f"减法: {a} - {b} = {a - b}")
print(f"乘法: {a} * {b} = {a * b}")
print(f"除法: {a} / {b} = {a / b}")
print(f"整除: {a} // {b} = {a // b}")
print(f"取余: {a} % {b} = {a % b}")
print(f"幂: {a} ** {b} = {a ** b}")

# ===== 位运算 =====
print("\n===== 位运算 =====")
x, y = 0b1010, 0b1100  # 10, 12
print(f"x = {x:04b} ({x})")
print(f"y = {y:04b} ({y})")
print(f"按位与 &: {x & y:04b} ({x & y})")
print(f"按位或 |: {x | y:04b} ({x | y})")
print(f"按位异或 ^: {x ^ y:04b} ({x ^ y})")
print(f"左移 << 1: {x << 1:04b} ({x << 1})")
print(f"右移 >> 1: {x >> 1:04b} ({x >> 1})")

# ===== 类型转换 =====
print("\n===== 类型转换 =====")
print(f"int('123') = {int('123')}")
print(f"float('3.14') = {float('3.14')}")
print(f"str(123) = '{str(123)}'")
print(f"bool(0) = {bool(0)}")
print(f"bool('hello') = {bool('hello')}")
print(f"bool([]) = {bool([])}")

# 判断类型
print(f"isinstance(age, int) = {isinstance(age, int)}")
print(f"isinstance(name, str) = {isinstance(name, str)}")
