# for

> **分类**：循环语句
> **说明**：for 循环，遍历可迭代对象

---

## 语法

```c
for 变量 in 可迭代对象:\n    循环体
```

## 相关函数

- while: 条件循环
- break: 跳出循环
- continue: 跳过当前迭代
- else: 循环正常结束时执行

## 示例代码

```python
# 遍历列表
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)

# 带索引遍历
for i, fruit in enumerate(fruits):
    print(f"{i}: {fruit}")

# 遍历字典
person = {"name": "Alice", "age": 25}
for key in person:
    print(key)

for key, value in person.items():
    print(key, value)

# range 循环
for i in range(5):
    print(i)  # 0, 1, 2, 3, 4

# while 循环
count = 0
while count < 5:
    print(count)
    count += 1

# break 和 continue
for i in range(10):
    if i == 3:
        continue  # 跳过3
    if i == 7:
        break     # 到7就停止
    print(i)

# for...else
for i in range(5):
    if i == 10:
        break
else:
    print("循环正常结束（没有break）")

# 列表推导式
squares = [x*x for x in range(10)]
evens = [x for x in range(20) if x % 2 == 0]
matrix = [[i*j for j in range(3)] for i in range(3)]
```
