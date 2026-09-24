# range

> **分类**：序列生成
> **说明**：生成一个整数序列的不可变对象

---

## 语法

```c
range(stop) 或 range(start, stop[, step])
```

## 参数说明

- start: 起始值（包含），默认为0
- stop: 结束值（不包含）
- step: 步长，默认为1

## 示例代码

```python
# 0到9
for i in range(10):
    print(i)  # 0, 1, 2, ..., 9

# 指定起始和结束
for i in range(5, 10):
    print(i)  # 5, 6, 7, 8, 9

# 指定步长
for i in range(0, 10, 2):
    print(i)  # 0, 2, 4, 6, 8

# 倒序
for i in range(10, 0, -1):
    print(i)  # 10, 9, 8, ..., 1

# 转换为列表
nums = list(range(5))  # [0, 1, 2, 3, 4]
```
