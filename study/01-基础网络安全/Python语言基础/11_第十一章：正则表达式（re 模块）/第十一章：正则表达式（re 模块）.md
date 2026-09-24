# 第十一章：正则表达式（re 模块）

### 11.1 常用函数

```python
import re

# 匹配：从字符串开头匹配
result = re.match(r"\d+", "123abc")
if result:
    print(result.group())    # 123

# 搜索：查找第一个匹配
result = re.search(r"\d+", "abc123def")
if result:
    print(result.group())    # 123

# 查找所有匹配
results = re.findall(r"\d+", "abc123def456ghi")
print(results)    # ['123', '456']

# 替换
result = re.sub(r"\d+", "NUM", "abc123def456")
print(result)     # abcNUMdefNUM

# 分割
result = re.split(r"[,-]", "a,b-c,d")
print(result)     # ['a', 'b', 'c', 'd']

# 编译正则（重复使用时更高效）
pattern = re.compile(r"\d+")
pattern.findall("abc123")
```

### 11.2 常用正则语法

| 语法 | 说明 |
|------|------|
| `.` | 任意字符（除换行） |
| `\d` | 数字 `[0-9]` |
| `\w` | 单词字符 `[a-zA-Z0-9_]` |
| `\s` | 空白字符 |
| `^` | 行首 |
| `$` | 行尾 |
| `*` | 0 次或多次 |
| `+` | 1 次或多次 |
| `?` | 0 次或 1 次 |
| `{n}` | 恰好 n 次 |
| `{n,m}` | n 到 m 次 |
| `[abc]` | 匹配 a/b/c 任一 |
| `[^abc]` | 不匹配 a/b/c |
| `a|b` | a 或 b |
| `()` | 分组捕获 |
| `\b` | 单词边界 |

### 11.3 分组

```python
# 提取分组
text = "姓名: 张三, 年龄: 25"
pattern = r"姓名: (\w+), 年龄: (\d+)"
result = re.search(pattern, text)
if result:
    print(result.group(0))    # 姓名: 张三, 年龄: 25（全部）
    print(result.group(1))    # 张三
    print(result.group(2))    # 25
    print(result.groups())    # ('张三', '25')

# 命名分组
pattern = r"姓名: (?P<name>\w+), 年龄: (?P<age>\d+)"
result = re.search(pattern, text)
if result:
    print(result.group("name"))   # 张三
    print(result.group("age"))    # 25
```

### 11.4 标志位

| 标志 | 说明 |
|------|------|
| `re.IGNORECASE` / `re.I` | 忽略大小写 |
| `re.MULTILINE` / `re.M` | 多行模式，^ 和 $ 匹配每行 |
| `re.DOTALL` / `re.S` | `.` 也匹配换行符 |
| `re.VERBOSE` / `re.X` | 忽略空白和注释（正则可写多行） |

---

---

