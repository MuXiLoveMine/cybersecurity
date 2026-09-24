# re 模块（正则表达式）

> Python 标准库，提供正则表达式操作，用于字符串匹配、查找、替换等。

---

## 一、导入与基本用法

```python
import re
```

---

## 二、常用函数

### 2.1 匹配与查找

```python
# match() - 从字符串开头匹配
result = re.match(r'\d+', '123abc')
print(result.group())  # '123'

result = re.match(r'\d+', 'abc123')
print(result)  # None（不是从开头开始）

# search() - 搜索整个字符串，找到第一个匹配
result = re.search(r'\d+', 'abc123def456')
print(result.group())  # '123'
print(result.start())  # 3
print(result.end())    # 6
print(result.span())   # (3, 6)

# findall() - 找到所有匹配，返回列表
results = re.findall(r'\d+', 'abc123def456ghi789')
print(results)  # ['123', '456', '789']

# finditer() - 找到所有匹配，返回迭代器
for match in re.finditer(r'\d+', 'abc123def456'):
    print(match.group(), match.span())

# fullmatch() - 整个字符串完全匹配
result = re.fullmatch(r'\d+', '12345')
print(result)  # <Match object>

result = re.fullmatch(r'\d+', '123abc')
print(result)  # None
```

### 2.2 替换与分割

```python
# sub() - 替换
result = re.sub(r'\d+', 'NUM', 'abc123def456')
print(result)  # abcNUMdefNUM

# 替换次数限制
result = re.sub(r'\d+', 'NUM', 'abc123def456', count=1)
print(result)  # abcNUMdef456

# 使用函数作为替换
def add_one(match):
    num = int(match.group())
    return str(num + 1)

result = re.sub(r'\d+', add_one, 'a1b2c3')
print(result)  # a2b3c4

# subn() - 替换并返回替换次数
result, count = re.subn(r'\d+', 'X', 'a1b2c3')
print(result)  # aXbXcX
print(count)   # 3

# split() - 分割
parts = re.split(r'[,-]', 'a,b-c,d')
print(parts)  # ['a', 'b', 'c', 'd']

# 分割并保留分隔符
parts = re.split(r'([,-])', 'a,b-c')
print(parts)  # ['a', ',', 'b', '-', 'c']

# 最大分割次数
parts = re.split(r',', 'a,b,c,d', maxsplit=2)
print(parts)  # ['a', 'b', 'c,d']
```

### 2.3 编译正则（性能优化）

```python
# 编译正则表达式（多次使用时性能更好）
pattern = re.compile(r'\d+')

# 使用编译后的对象
result = pattern.search('abc123')
results = pattern.findall('abc123def456')
result = pattern.sub('X', 'a1b2c3')

# 编译标志
pattern = re.compile(r'pattern', re.IGNORECASE | re.MULTILINE)

# 查看模式和标志
print(pattern.pattern)   # 正则字符串
print(pattern.flags)     # 标志位
print(pattern.groups)    # 捕获组数量
print(pattern.groupindex)  # 命名组字典
```

### 2.4 匹配对象 (Match)

```python
m = re.search(r'(\d+)-(\w+)', 'id: 123-abc')

# 获取匹配内容
print(m.group())       # '123-abc'（整个匹配）
print(m.group(0))      # 同上
print(m.group(1))      # '123'（第1个捕获组）
print(m.group(2))      # 'abc'（第2个捕获组）
print(m.groups())      # ('123', 'abc')（所有组）

# 命名组
m = re.search(r'(?P<num>\d+)-(?P<word>\w+)', '123-abc')
print(m.group('num'))   # '123'
print(m.group('word'))  # 'abc'
print(m.groupdict())    # {'num': '123', 'word': 'abc'}

# 位置信息
print(m.start())       # 起始位置
print(m.end())         # 结束位置
print(m.span())        # (start, end)
print(m.start(1))      # 第1组的起始位置
print(m.end(1))        # 第1组的结束位置

# 原始字符串
print(m.string)        # 被搜索的字符串
print(m.re)            # 正则对象
```

### 2.5 常用标志

```python
# re.IGNORECASE / re.I - 忽略大小写
re.search(r'abc', 'ABC', re.I)  # 匹配

# re.MULTILINE / re.M - 多行模式
# ^ 匹配每行开头，$ 匹配每行结尾
text = "line1\nline2\nline3"
re.findall(r'^line\d', text, re.M)  # ['line1', 'line2', 'line3']

# re.DOTALL / re.S - 点号匹配换行
re.search(r'a.b', 'a\nb', re.S)  # 匹配

# re.VERBOSE / re.X - 详细模式（忽略空白和注释）
pattern = re.compile(r'''
    \d+    # 数字
    -      # 连字符
    \w+    # 单词
''', re.VERBOSE)

# re.ASCII / re.A - ASCII 模式
# \w, \d 等只匹配 ASCII 字符

# 多个标志组合
re.search(r'pattern', text, re.I | re.M | re.S)
```

---

## 三、正则语法速查

### 3.1 字符类

```python
.          # 任意字符（除换行）
\d         # 数字 [0-9]
\D         # 非数字
\w         # 单词字符 [a-zA-Z0-9_]
\W         # 非单词字符
\s         # 空白字符 [ \t\n\r\f\v]
\S         # 非空白字符
[abc]      # 字符集：a 或 b 或 c
[^abc]     # 否定字符集：非 a/b/c
[a-z]      # 范围：a 到 z
[A-Za-z]   # 范围：大小写字母
[0-9]      # 数字
```

### 3.2 量词

```python
*          # 0次或多次
+          # 1次或多次
?          # 0次或1次
{n}        # 恰好 n 次
{n,}       # 至少 n 次
{n,m}      # n 到 m 次

*?         # 非贪婪：0次或多次，尽可能少
+?         # 非贪婪：1次或多次，尽可能少
??         # 非贪婪：0次或1次，尽可能少
{n,m}?     # 非贪婪版本
```

### 3.3 锚点

```python
^          # 字符串开头（多行模式下每行开头）
$          # 字符串结尾（多行模式下每行结尾）
\A         # 字符串开头（不受多行模式影响）
\Z         # 字符串结尾
\b         # 单词边界
\B         # 非单词边界
(?=...)    # 正向先行断言
(?!...)    # 负向先行断言
(?<=...)   # 正向后行断言
(?<!...)   # 负向后行断言
```

### 3.4 分组与引用

```python
(...)      # 捕获组
(?P<name>...)  # 命名捕获组
(?:...)    # 非捕获组
\1, \2     # 反向引用第 1、2 组
(?P=name)  # 引用命名组
(?#...)    # 注释
```

---

## 四、安全相关使用案例

### 4.1 输入验证

```python
import re

# 用户名验证
def validate_username(username):
    """验证用户名：3-20位，字母数字下划线"""
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return bool(re.fullmatch(pattern, username))

# 邮箱验证（简化版）
def validate_email(email):
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.fullmatch(pattern, email))

# URL 验证
def validate_url(url):
    """验证 URL 格式"""
    pattern = r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$'
    return bool(re.fullmatch(pattern, url))

# IP 地址验证 (IPv4)
def validate_ipv4(ip):
    """验证 IPv4 地址"""
    pattern = r'^((25[0-5]|2[0-4]\d|[01]?\d?\d)\.){3}(25[0-5]|2[0-4]\d|[01]?\d?\d)$'
    return bool(re.fullmatch(pattern, ip))

# 手机号验证（中国大陆）
def validate_phone(phone):
    """验证手机号"""
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.fullmatch(pattern, phone))

# 密码强度检测
def password_strength(password):
    """检查密码强度"""
    score = 0
    feedback = []
    
    if len(password) >= 8:
        score += 1
    else:
        feedback.append("密码至少 8 位")
    
    if re.search(r'[a-z]', password):
        score += 1
    else:
        feedback.append("需要小写字母")
    
    if re.search(r'[A-Z]', password):
        score += 1
    else:
        feedback.append("需要大写字母")
    
    if re.search(r'\d', password):
        score += 1
    else:
        feedback.append("需要数字")
    
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 1
    else:
        feedback.append("需要特殊字符")
    
    # 常见弱密码检测
    weak_patterns = [
        r'^(password|123456|qwerty|admin)$',
        r'^([a-z])\1{4,}$',  # 重复字符
        r'^(12345|abcde)$',   # 连续字符
    ]
    for p in weak_patterns:
        if re.match(p, password, re.I):
            score = 0
            feedback.append("常见弱密码")
            break
    
    rating = ['弱', '较弱', '中等', '较强', '强'][min(score, 4)]
    return score, rating, feedback
```

### 4.2 XSS 检测

```python
import re

def detect_xss(input_str):
    """检测潜在的 XSS 攻击"""
    patterns = [
        # 脚本标签
        r'<\s*script[^>]*>',
        r'<\s*/\s*script\s*>',
        
        # JavaScript URI
        r'javascript\s*:',
        r'vbscript\s*:',
        r'data\s*:\s*text/html',
        
        # 事件处理器
        r'on\w+\s*=',
        
        # 危险标签
        r'<\s*iframe[^>]*>',
        r'<\s*object[^>]*>',
        r'<\s*embed[^>]*>',
        r'<\s*svg[^>]*>',
        r'<\s*img[^>]+on\w+\s*=',
        
        # eval / Function
        r'eval\s*\(',
        r'new\s+Function\s*\(',
        
        # document.cookie
        r'document\s*\.\s*cookie',
    ]
    
    found = []
    for pattern in patterns:
        if re.search(pattern, input_str, re.IGNORECASE):
            found.append(pattern)
    
    return len(found) > 0, found
```

### 4.3 SQL 注入检测

```python
import re

def detect_sqli(input_str):
    """检测潜在的 SQL 注入"""
    patterns = [
        # 关键字
        r'\bunion\s+select\b',
        r'\bselect\s+.*\s+from\b',
        r'\binsert\s+into\b',
        r'\bdrop\s+table\b',
        r'\bdelete\s+from\b',
        r'\bupdate\s+.*\s+set\b',
        
        # 永真式
        r"'\s*or\s*'?\d+'?\s*=\s*'?\d+",
        r"\bor\b.*\b1\s*=\s*1\b",
        
        # 注释
        r"--",
        r"/\*.*\*/",
        r"#",
        
        # 函数
        r'\bsleep\s*\(',
        r'\bbenchmark\s*\(',
        r'\bload_file\s*\(',
        r'\binto\s+outfile\b',
        r'\bxp_cmdshell\b',
        
        # 单引号（粗略检测）
        r"'.*'.*'",
    ]
    
    found = []
    for pattern in patterns:
        if re.search(pattern, input_str, re.IGNORECASE):
            found.append(pattern)
    
    return len(found) > 0, found
```

### 4.4 命令注入检测

```python
import re

def detect_command_injection(input_str):
    """检测潜在的命令注入"""
    patterns = [
        # 命令分隔符
        r';',
        r'\|',          # 管道
        r'&&',          # 逻辑与
        r'\|\|',        # 逻辑或
        r'`',           # 反引号
        r'\$\([^)]+\)', # $() 命令替换
        r'\$\{[^}]+\}', # ${} 变量扩展
        
        # 危险命令
        r'\brm\s+-rf\b',
        r'\bcat\s+/etc/passwd\b',
        r'\bwhoami\b',
        r'\bid\b',
        r'\buname\s+-a\b',
        r'\bnc\s+.*-e\b',
        
        # 重定向
        r'>\s*/dev/',
        r'<\s*/dev/',
    ]
    
    found = []
    for pattern in patterns:
        if re.search(pattern, input_str):
            found.append(pattern)
    
    return len(found) > 0, found
```

---

## 五、正则安全注意事项

### 5.1 ReDoS（正则表达式拒绝服务）

```python
"""
    ReDoS: 正则表达式拒绝服务攻击
    原因：嵌套的量词 + 回溯导致指数级复杂度
    
    危险模式示例：
    (a+)+
    ([a-zA-Z]+)*
    (a|aa)+
    (a|a?)+
    (.*a){n}
    
    攻击：输入大量 'a' 字符，导致匹配时间爆炸
"""

# 危险的正则（易受 ReDoS）
dangerous_pattern = r'^(a+)+$'
# 输入 'aaaaaaaaaaaaaaaaaaaaaaaaaaaa!' 会导致大量回溯

# 安全的写法
safe_pattern = r'^a+$'
# 或使用 possessive quantifiers（Python re 不支持，可用第三方库）

"""
    防御方法：
    1. 避免嵌套量词
    2. 限制输入长度
    3. 设置超时
    4. 使用原子组（Python 需第三方库）
    5. 使用非回溯正则引擎（如 re2）
"""

# 设置超时的简单实现
import signal

def safe_match(pattern, text, timeout=1):
    """带超时的正则匹配（Unix 专用）"""
    def handler(signum, frame):
        raise TimeoutError("正则匹配超时")
    
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(timeout)
    try:
        result = re.match(pattern, text)
    finally:
        signal.alarm(0)
    
    return result
```

### 5.2 其他安全注意

```python
# 1. 用户输入作为正则模式时要转义
user_input = "file.txt"
escaped = re.escape(user_input)  # 转义特殊字符
pattern = re.compile(escaped)

# 2. 不要用正则解析 HTML/XML
# 错误：用正则提取 HTML 标签内容
# 正确：使用 BeautifulSoup, lxml 等解析库

# 3. 注意贪婪 vs 非贪婪
text = "<a>first</a><a>second</a>"
re.findall(r'<a>(.*)</a>', text)   # ['first</a><a>second'] （贪婪）
re.findall(r'<a>(.*?)</a>', text)  # ['first', 'second'] （非贪婪）

# 4. 验证用户输入用 fullmatch 而不是 search
# search 只需要部分匹配，可能被绕过
re.search(r'\d+', 'abc123def')   # 匹配（但整体不是纯数字）
re.fullmatch(r'\d+', 'abc123def') # None（正确）
```

---

## 六、性能优化

| 优化方法 | 说明 |
|---------|------|
| 预编译正则 | 多次使用时用 `re.compile()` |
| 避免回溯 | 减少嵌套量词，使用非贪婪匹配 |
| 限制输入长度 | 防止 ReDoS 攻击 |
| 使用字符集 | `[abc]` 比 `(a|b|c)` 快 |
| 锚点优化 | 尽量用 `^` 开头，让不匹配的快速失败 |
