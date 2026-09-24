# str

> **分类**：字符串方法
> **说明**：字符串类型，提供丰富的文本处理方法

---

## 语法

```c
str(object="") 或直接使用字符串字面量
```

## 常用方法/属性

- upper() - 转大写
- lower() - 转小写
- strip() - 去除两端空白
- split(sep) - 分割为列表
- join(iterable) - 连接序列
- replace(old, new) - 替换
- find(sub) - 查找子串位置
- startswith(prefix) - 检查前缀
- endswith(suffix) - 检查后缀
- count(sub) - 统计出现次数
- format() - 格式化字符串

## 示例代码

```python
# 常用方法
s = "  Hello, World!  "

print(s.upper())        # "  HELLO, WORLD!  "
print(s.lower())        # "  hello, world!  "
print(s.strip())        # "Hello, World!"
print(s.replace("World", "Python"))  # "  Hello, Python!  "

# 分割与连接
parts = "a,b,c".split(",")  # ['a', 'b', 'c']
result = "-".join(parts)    # "a-b-c"

# 查找
text = "hello world"
print(text.find("world"))  # 6
print("hello" in text)     # True

# 格式化
name = "Alice"
print(f"Hello, {name}!")        # f-string
print("Hello, {}!".format(name)) # format
print("Hello, %s!" % name)       # %

# 字符串方法链式调用
s = "  Test String  "
result = s.strip().lower().replace(" ", "-")
# "test-string"
```
