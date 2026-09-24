# Web安全最佳实践

### 9.1 SQL注入防御

```python
# 正确的做法：使用参数化查询
import sqlite3

# ✅ 安全写法
conn = sqlite3.connect('test.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

# ❌ 危险写法
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

### 9.2 XSS防御

```python
# 输出编码
import html

def safe_output(user_input):
    """对用户输入进行HTML实体编码"""
    return html.escape(user_input)

# Content-Security-Policy头
csp_header = "default-src 'self'; script-src 'self'; style-src 'self'"
```

### 9.3 SSRF防御

```python
import ipaddress
import socket

def is_internal_ip(hostname):
    """检查IP是否为内网地址"""
    try:
        ip = socket.gethostbyname(hostname)
        addr = ipaddress.ip_address(ip)
        return addr.is_private or addr.is_loopback or addr.is_link_local
    except:
        return True  # 解析失败视为危险

# 请求前验证目标地址
def safe_request(url):
    parsed = urllib.parse.urlparse(url)
    if is_internal_ip(parsed.hostname):
        raise ValueError("禁止访问内网地址")
    # 仅允许http/https协议
    if parsed.scheme not in ('http', 'https'):
        raise ValueError("不允许的协议")
```

### 9.4 文件上传防御

```python
import os
import magic  # python-magic

def safe_upload(file, upload_dir):
    """安全的文件上传处理"""
    # 1. 白名单检查后缀
    allowed_extensions = {'.jpg', '.png', '.gif'}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        raise ValueError("不允许的文件类型")
    
    # 2. 检查文件内容（Magic Number）
    file_content = file.read()
    file_type = magic.from_buffer(file_content, mime=True)
    if file_type not in ('image/jpeg', 'image/png', 'image/gif'):
        raise ValueError("文件内容与类型不匹配")
    
    # 3. 重命名文件
    import uuid
    safe_name = str(uuid.uuid4()) + ext
    
    # 4. 存储到非Web可访问目录
    save_path = os.path.join(upload_dir, safe_name)
    with open(save_path, 'wb') as f:
        f.write(file_content)
    
    return safe_name
```

---

---

