# 07_functions.py
# 函数定义与使用

# ===== 基本函数 =====
print("===== 基本函数 =====")

def greet():
    """简单的问候函数"""
    print("Hello, World!")

greet()

# ===== 带参数的函数 =====
print("\n===== 带参数的函数 =====")

def greet_name(name):
    """向指定的人问候"""
    print(f"Hello, {name}!")

greet_name("张三")
greet_name("李四")

# ===== 带返回值的函数 =====
print("\n===== 带返回值的函数 =====")

def add(a, b):
    """两个数相加"""
    return a + b

result = add(3, 5)
print(f"3 + 5 = {result}")

# 多个返回值
def divide(a, b):
    """返回商和余数"""
    quotient = a // b
    remainder = a % b
    return quotient, remainder

q, r = divide(10, 3)
print(f"10 / 3 = {q} 余 {r}")

# ===== 默认参数 =====
print("\n===== 默认参数 =====")

def greet2(name, greeting="Hello"):
    """带默认问候语的函数"""
    print(f"{greeting}, {name}!")

greet2("张三")
greet2("李四", "早上好")
greet2("王五", greeting="晚上好")

# ===== 可变参数 =====
print("\n===== 可变参数 =====")

def sum_all(*args):
    """计算所有参数的和"""
    total = 0
    for num in args:
        total += num
    return total

print(f"sum_all(1, 2, 3) = {sum_all(1, 2, 3)}")
print(f"sum_all(1, 2, 3, 4, 5) = {sum_all(1, 2, 3, 4, 5)}")

# 关键字可变参数
def print_info(**kwargs):
    """打印所有关键字参数"""
    for key, value in kwargs.items():
        print(f"  {key}: {value}")

print("个人信息:")
print_info(name="张三", age=25, city="北京", job="工程师")

# ===== 作用域 =====
print("\n===== 作用域 =====")

global_var = "我是全局变量"

def test_scope():
    local_var = "我是局部变量"
    global global_var
    global_var = "全局变量被修改了"
    print(f"  函数内: {global_var}")
    print(f"  函数内: {local_var}")

test_scope()
print(f"函数外: {global_var}")
# print(local_var)  # 报错，局部变量外部不可见

# ===== lambda 匿名函数 =====
print("\n===== lambda 匿名函数 =====")

square = lambda x: x ** 2
print(f"square(5) = {square(5)}")

add2 = lambda a, b: a + b
print(f"add2(3, 4) = {add2(3, 4)}")

# lambda 用于排序
fruits = ["apple", "banana", "cherry", "date"]
fruits.sort(key=lambda x: len(x))
print("按长度排序:", fruits)

# ===== 递归函数 =====
print("\n===== 递归函数 =====")

def factorial(n):
    """计算阶乘"""
    if n <= 1:
        return 1
    return n * factorial(n - 1)

for i in range(6):
    print(f"  {i}! = {factorial(i)}")

def fibonacci(n):
    """斐波那契数列"""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

print("斐波那契前10项:", end=" ")
for i in range(10):
    print(fibonacci(i), end=" ")
print()

# ===== 装饰器（进阶） =====
print("\n===== 装饰器 =====")

import time

def timer(func):
    """计时装饰器"""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"  {func.__name__} 耗时: {elapsed:.6f}s")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(0.1)
    return "完成"

result = slow_function()
print(f"  结果: {result}")
