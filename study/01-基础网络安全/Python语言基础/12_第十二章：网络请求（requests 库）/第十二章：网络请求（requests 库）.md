# 第十二章：网络请求（requests 库）

### 12.1 安装

```bash
pip install requests
```

### 12.2 基本请求

```python
import requests

# GET 请求
response = requests.get("https://httpbin.org/get")

# 响应内容
print(response.status_code)    # 状态码：200
print(response.text)           # 文本内容
print(response.json())         # JSON 解析（返回字典）
print(response.headers)        # 响应头
print(response.url)            # 请求的 URL

# 带参数的 GET
params = {"key1": "value1", "key2": "value2"}
response = requests.get("https://httpbin.org/get", params=params)

# POST 请求（表单数据）
data = {"username": "admin", "password": "123456"}
response = requests.post("https://httpbin.org/post", data=data)

# POST JSON
json_data = {"name": "张三", "age": 25}
response = requests.post("https://httpbin.org/post", json=json_data)
```

### 12.3 请求头与 Cookie

```python
# 自定义请求头
headers = {
    "User-Agent": "MyBot/1.0",
    "Authorization": "Bearer token123"
}
response = requests.get("https://httpbin.org/headers", headers=headers)

# Cookie
cookies = {"session": "abc123"}
response = requests.get("https://httpbin.org/cookies", cookies=cookies)

# Session（保持会话，自动处理 Cookie）
session = requests.Session()
session.post("https://example.com/login", data={"user": "admin", "pass": "123"})
response = session.get("https://example.com/dashboard")  # 自动带上登录 cookie
```

### 12.4 其他请求方式

```python
requests.put(url, data=data)       # PUT 请求
requests.delete(url)               # DELETE 请求
requests.head(url)                 # HEAD 请求
requests.patch(url, data=data)     # PATCH 请求
```

### 12.5 超时与异常处理

```python
try:
    response = requests.get("https://httpbin.org/get", timeout=5)
    response.raise_for_status()     # 状态码非 2xx 抛出异常
except requests.exceptions.Timeout:
    print("请求超时")
except requests.exceptions.ConnectionError:
    print("连接失败")
except requests.exceptions.HTTPError as e:
    print(f"HTTP 错误: {e}")
except requests.exceptions.RequestException as e:
    print(f"请求异常: {e}")
```

### 12.6 文件上传与下载

```python
# 文件上传
files = {"file": open("test.txt", "rb")}
response = requests.post("https://httpbin.org/post", files=files)

# 文件下载
url = "https://example.com/file.zip"
response = requests.get(url)
with open("file.zip", "wb") as f:
    f.write(response.content)
```

---

---

