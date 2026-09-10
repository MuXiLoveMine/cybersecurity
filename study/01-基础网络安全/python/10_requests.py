# 10_requests.py
# requests 网络请求库
# 需要先安装: pip install requests

import requests

# 测试接口
BASE_URL = "https://httpbin.org"

# ===== GET 请求 =====
print("===== GET 请求 =====")

response = requests.get(f"{BASE_URL}/get")
print(f"状态码: {response.status_code}")
print(f"URL: {response.url}")
print(f"响应头 Content-Type: {response.headers.get('Content-Type')}")
print(f"JSON 响应: {response.json()}")

# 带参数的 GET
print("\n===== 带参数的 GET =====")
params = {"name": "张三", "age": 25}
response = requests.get(f"{BASE_URL}/get", params=params)
print(f"请求 URL: {response.url}")
data = response.json()
print(f"返回的参数: {data.get('args')}")

# ===== POST 请求 =====
print("\n===== POST 请求（表单） =====")

data = {"username": "admin", "password": "123456"}
response = requests.post(f"{BASE_URL}/post", data=data)
result = response.json()
print(f"表单数据: {result.get('form')}")

print("\n===== POST 请求（JSON） =====")

json_data = {"name": "张三", "age": 25, "skills": ["Python", "Java"]}
response = requests.post(f"{BASE_URL}/post", json=json_data)
result = response.json()
print(f"JSON 数据: {result.get('json')}")

# ===== 请求头 =====
print("\n===== 自定义请求头 =====")

headers = {
    "User-Agent": "MyPythonBot/1.0",
    "X-Custom-Header": "custom-value"
}
response = requests.get(f"{BASE_URL}/headers", headers=headers)
print(f"发送的请求头: {response.json().get('headers')}")

# ===== Cookie =====
print("\n===== Cookie =====")

cookies = {"session": "abc123456", "username": "testuser"}
response = requests.get(f"{BASE_URL}/cookies", cookies=cookies)
print(f"服务端收到的 Cookie: {response.json().get('cookies')}")

# ===== Session =====
print("\n===== Session 会话 =====")

session = requests.Session()

# 第一次请求，设置 cookie
response1 = session.get(f"{BASE_URL}/cookies/set?name=value1")
print(f"第一次请求 cookie: {response1.json().get('cookies')}")

# 第二次请求，自动带上 cookie
response2 = session.get(f"{BASE_URL}/cookies")
print(f"第二次请求 cookie: {response2.json().get('cookies')}")

# ===== 超时与异常 =====
print("\n===== 超时与异常处理 =====")

try:
    response = requests.get(f"{BASE_URL}/get", timeout=5)
    response.raise_for_status()  # 状态码非 2xx 抛出异常
    print("请求成功")
except requests.exceptions.Timeout:
    print("请求超时")
except requests.exceptions.ConnectionError:
    print("连接失败")
except requests.exceptions.HTTPError as e:
    print(f"HTTP 错误: {e}")
except requests.exceptions.RequestException as e:
    print(f"其他错误: {e}")

# ===== 文件下载 =====
print("\n===== 文件下载（示例） =====")
print("下载小图片...")
try:
    img_url = "https://httpbin.org/image/png"
    response = requests.get(img_url, timeout=10)
    with open("test_image.png", "wb") as f:
        f.write(response.content)
    print(f"下载完成，大小: {len(response.content)} 字节")
    import os
    os.remove("test_image.png")
    print("已删除测试图片")
except Exception as e:
    print(f"下载失败: {e}")
