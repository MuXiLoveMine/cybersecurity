# try/except

> **分类**：异常处理
> **说明**：异常捕获和处理机制

---

## 语法

```c
try:\n    代码\nexcept 异常类型 as e:\n    处理\nelse:\n    无异常时执行\nfinally:\n    总是执行
```

## 示例代码

```python
# 基本异常捕获
try:
    result = 10 / 0
except ZeroDivisionError:
    print("不能除以零")

# 捕获多个异常
try:
    x = int(input("输入数字: "))
    result = 100 / x
except ValueError:
    print("请输入有效的数字")
except ZeroDivisionError:
    print("不能除以零")

# 捕获所有异常（获取异常信息）
try:
    risky_operation()
except Exception as e:
    print(f"发生错误: {e}")
    import traceback
    traceback.print_exc()  # 打印完整堆栈

# else 和 finally
try:
    f = open("file.txt", "r")
except FileNotFoundError:
    print("文件不存在")
else:
    # 没有异常时执行
    content = f.read()
    print("文件读取成功")
finally:
    # 总是执行（无论是否异常）
    if 'f' in locals():
        f.close()
    print("清理完成")

# 抛出异常
def validate_age(age):
    if age < 0:
        raise ValueError("年龄不能为负数")
    if age > 150:
        raise ValueError("年龄不合理")

# 自定义异常
class MyCustomError(Exception):
    pass

raise MyCustomError("自定义错误信息")
```
