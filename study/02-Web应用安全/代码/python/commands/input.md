# input

> **分类**：基础输入
> **说明**：从标准输入读取一行用户输入

---

## 语法

```c
input(prompt=None)
```

**返回值**：用户输入的字符串（去掉末尾换行符）

## 参数说明

- prompt: 可选的提示字符串，显示给用户

## 示例代码

```python
# 基本输入
name = input("请输入你的名字: ")
print(f"你好, {name}!")

# 输入数字（需要类型转换）
age = int(input("请输入年龄: "))
print(f"明年你 {age + 1} 岁")

# 输入多个值
x, y = map(int, input("输入两个数字: ").split())
print(f"和: {x + y}")

# 密码输入（不回显）
import getpass
password = getpass.getpass("输入密码: ")
```
