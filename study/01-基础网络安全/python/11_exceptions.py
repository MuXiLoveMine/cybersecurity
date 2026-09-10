# 11_exceptions.py
# 异常处理

# ===== 基本 try-except =====
print("===== 基本 try-except =====")

try:
    num = int("abc")
except ValueError:
    print("捕获到 ValueError：无法转换为整数")

# ===== 多种异常 =====
print("\n===== 多种异常 =====")

def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        print("错误：除数不能为零")
        return None
    except TypeError:
        print("错误：类型不匹配")
        return None

safe_divide(10, 0)
safe_divide(10, "2")
print(f"10 / 2 = {safe_divide(10, 2)}")

# ===== 捕获所有异常 =====
print("\n===== 捕获所有异常 =====")

try:
    x = 10
    y = 0
    result = x / y
except Exception as e:
    print(f"捕获到异常: {type(e).__name__}: {e}")

# ===== try-except-else =====
print("\n===== try-except-else =====")

try:
    num = int("123")
except ValueError:
    print("转换失败")
else:
    print(f"转换成功: {num}")

# ===== finally =====
print("\n===== finally =====")

def read_file_safe(filename):
    f = None
    try:
        f = open(filename, "r")
        content = f.read()
        return content
    except FileNotFoundError:
        print(f"文件不存在: {filename}")
        return None
    finally:
        if f:
            f.close()
            print("文件已关闭")

read_file_safe("nonexistent.txt")

# ===== 抛出异常 =====
print("\n===== 抛出异常 =====")

def check_age(age):
    if age < 0:
        raise ValueError("年龄不能为负数")
    if age > 150:
        raise ValueError("年龄不合理")
    return True

try:
    check_age(-5)
except ValueError as e:
    print(f"错误: {e}")

# ===== 自定义异常 =====
print("\n===== 自定义异常 =====")

class MyCustomError(Exception):
    """自定义异常类"""
    def __init__(self, message, code=0):
        self.message = message
        self.code = code
        super().__init__(self.message)

def custom_func(value):
    if value < 0:
        raise MyCustomError("值不能为负", code=1001)

try:
    custom_func(-1)
except MyCustomError as e:
    print(f"捕获自定义异常: {e.message} (code: {e.code})")

# ===== 常见异常类型 =====
print("\n===== 常见异常类型 =====")

exceptions = [
    ("ValueError", lambda: int("abc")),
    ("TypeError", lambda: "abc" + 123),
    ("IndexError", lambda: [1, 2, 3][10]),
    ("KeyError", lambda: {"a": 1}["b"]),
    ("ZeroDivisionError", lambda: 1 / 0),
    ("FileNotFoundError", lambda: open("nonexistent_file.txt")),
]

for name, func in exceptions:
    try:
        func()
    except Exception as e:
        print(f"  {name}: {type(e).__name__}")
