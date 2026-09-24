# open

> **分类**：文件操作
> **说明**：打开文件，返回文件对象

---

## 语法

```c
open(file, mode="r", buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None)
```

## 参数说明

- file: 文件路径字符串
- mode: 打开模式（r/w/a/x/b/t/+）
- encoding: 编码方式（如 utf-8）
- errors: 编码错误处理方式

## 示例代码

```python
# 读取文件
with open("file.txt", "r", encoding="utf-8") as f:
    content = f.read()

# 逐行读取
with open("file.txt", "r") as f:
    for line in f:
        print(line.strip())

# 写入文件
with open("output.txt", "w", encoding="utf-8") as f:
    f.write("Hello, World!\n")
    f.write("第二行")

# 追加写入
with open("log.txt", "a") as f:
    f.write("新的一行\n")

# 二进制模式
with open("image.png", "rb") as f:
    data = f.read()

# 读写模式
with open("data.txt", "r+") as f:
    content = f.read()
    f.seek(0)
    f.write("新内容")
    f.truncate()
```
