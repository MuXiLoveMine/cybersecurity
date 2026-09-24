# print

> **分类**：基础输出
> **说明**：输出指定内容到标准输出

---

## 语法

```c
print(*objects, sep=" ", end="\n", file=sys.stdout, flush=False)
```

## 参数说明

- *objects: 一个或多个输出对象
- sep: 分隔符，默认为空格
- end: 结尾字符，默认为换行符
- file: 输出文件对象，默认为标准输出

## 示例代码

```python
# 基本输出
print("Hello, World!")

# 多参数输出
print("Name:", "Alice", "Age:", 25)

# 自定义分隔符和结尾
print(1, 2, 3, sep="-", end="!\n")

# 输出到文件
with open("output.txt", "w") as f:
    print("Hello File", file=f)

# 格式化输出
name = "Bob"
print(f"Hello, {name}!")      # f-string
print("Hello, {}!".format(name))  # format
print("Hello, %s!" % name)        # % 格式化
```
