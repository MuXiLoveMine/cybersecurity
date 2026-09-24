# if/elif/else

> **分类**：条件语句
> **说明**：条件判断语句，根据条件执行不同代码块

---

## 语法

```c
if 条件1:\n    语句1\nelif 条件2:\n    语句2\nelse:\n    语句3
```

## 运算符

- == 相等
- != 不等
- > 大于
- < 小于
- >= 大于等于
- <= 小于等于
- and 与
- or 或
- not 非
- in 包含
- is 身份相同

## 示例代码

```python
# 基本 if/else
age = 18
if age >= 18:
    print("成年")
else:
    print("未成年")

# 多分支
score = 85
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 60:
    grade = "C"
else:
    grade = "D"

# 多条件
if age >= 18 and score >= 60:
    print("符合条件")

# 三元表达式
x = 10
result = "大于5" if x > 5 else "小于等于5"

# match/case (Python 3.10+)
status = "success"
match status:
    case "success":
        print("成功")
    case "error":
        print("错误")
    case _:
        print("其他")

# 真值判断
# 以下被视为 False: None, False, 0, 0.0, "", [], {}, set()
if []:
    print("不会执行")
```
