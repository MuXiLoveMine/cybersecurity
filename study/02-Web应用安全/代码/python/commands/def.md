# def

> **分类**：函数定义
> **说明**：定义一个函数

---

## 语法

```c
def 函数名(参数列表):\n    函数体\n    [return 返回值]
```

## 参数说明

- 位置参数：按顺序传递
- 默认参数：有默认值的参数
- 关键字参数：按名称传递
- *args：可变位置参数（元组）
- **kwargs：可变关键字参数（字典）

## 示例代码

```python
# 基本函数
def greet(name):
    return f"Hello, {name}!"

print(greet("Alice"))  # "Hello, Alice!"

# 默认参数
def power(x, n=2):
    return x ** n

print(power(3))     # 9
print(power(3, 3))  # 27

# 可变参数
def sum_all(*args):
    return sum(args)

print(sum_all(1, 2, 3, 4))  # 10

# 关键字参数
def print_info(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")

print_info(name="Bob", age=25)

# 混合参数
def func(a, b, *args, c=10, **kwargs):
    print(a, b, args, c, kwargs)

func(1, 2, 3, 4, c=20, x=1, y=2)
# a=1, b=2, args=(3,4), c=20, kwargs={"x":1, "y":2}

# lambda 匿名函数
square = lambda x: x * x
print(square(5))  # 25

# 带类型提示（Python 3.5+）
def add(x: int, y: int) -> int:
    return x + y
```
