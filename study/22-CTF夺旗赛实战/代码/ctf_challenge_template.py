#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CTF 挑战模板生成与管理工具
===================================

功能概述：
  1. 生成多类型 CTF 挑战模板（Web / Crypto / Misc）
  2. 自动生成随机 Flag 并管理 Flag 数据库
  3. 生成包含漏洞的 Web 挑战源码（SQL注入 / XSS / SSRF / 命令注入 / 文件包含）
  4. 生成密码学挑战（古典密码 / RSA / 哈希破解 / XOR）
  5. 生成杂项挑战（隐写 / 编码 / 取证）
  6. 生成 Docker 部署配置和计分板

使用方式：
  python ctf_challenge_template.py --generate-all
  python ctf_challenge_template.py --generate web_sqli
  python ctf_challenge_template.py --list-templates

作者: 网络安全学习项目
"""

import os
import re
import json
import uuid
import random
import string
import hashlib
import base64
import argparse
import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum

# 可选依赖
try:
    import gmpy2
    HAS_GMPY2 = True
except ImportError:
    HAS_GMPY2 = False

try:
    from Crypto.Util.number import getPrime, bytes_to_long
    HAS_PYCRYPTO = True
except ImportError:
    HAS_PYCRYPTO = False


# ============================================================================
# 常量
# ============================================================================

FLAG_PREFIX = "flag"
FLAG_CHARSET = string.ascii_letters + string.digits + "_-"
FLAG_LENGTH = 32


class Difficulty(Enum):
    EASY = "简单"
    MEDIUM = "中等"
    HARD = "困难"
    INSANE = "地狱"

    def __str__(self):
        return self.value


class ChallengeCategory(Enum):
    WEB = "Web"
    CRYPTO = "Crypto"
    MISC = "Misc"
    PWN = "Pwn"
    REVERSE = "Reverse"
    FORENSICS = "Forensics"

    def __str__(self):
        return self.value


# ============================================================================
# 数据模型
# ============================================================================

@dataclass
class Flag:
    """Flag 数据"""
    flag_id: str
    flag_value: str
    challenge_name: str
    category: str
    difficulty: str
    created_at: str
    points: int = 100
    description: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Challenge:
    """挑战配置"""
    name: str
    title: str
    category: str
    difficulty: str
    description: str
    flag: str
    points: int
    hint: str = ""
    port: int = 0
    docker_required: bool = False
    is_active: bool = True

    def to_dict(self) -> Dict:
        return asdict(self)


# ============================================================================
# Flag 管理器
# ============================================================================

class FlagManager:
    """Flag 生成与管理"""

    def __init__(self, storage_path: str = "flags.json"):
        self.storage_path = storage_path
        self.flags: Dict[str, Flag] = {}
        self._load()

    def generate_flag(self, challenge_name: str, category: str,
                      difficulty: str, points: int = 100,
                      description: str = "") -> Flag:
        """生成随机 Flag"""
        random_suffix = ''.join(random.choices(FLAG_CHARSET, k=FLAG_LENGTH))
        flag_value = f"{FLAG_PREFIX}{{{random_suffix}}}"
        flag_id = str(uuid.uuid4())[:8]
        flag = Flag(
            flag_id=flag_id,
            flag_value=flag_value,
            challenge_name=challenge_name,
            category=category,
            difficulty=difficulty,
            created_at=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            points=points,
            description=description
        )
        self.flags[flag_id] = flag
        self._save()
        return flag

    def verify_flag(self, flag_value: str) -> Tuple[bool, Optional[Flag]]:
        """验证 Flag"""
        for flag in self.flags.values():
            if flag.flag_value == flag_value:
                return True, flag
        return False, None

    def list_flags(self) -> List[Flag]:
        return list(self.flags.values())

    def _save(self):
        data = {fid: f.to_dict() for fid, f in self.flags.items()}
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[警告] 保存 Flag 数据失败: {e}")

    def _load(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for fid, fdata in data.items():
                    self.flags[fid] = Flag(**fdata)
            except (json.JSONDecodeError, TypeError) as e:
                print(f"[警告] 加载 Flag 数据失败: {e}")


# ============================================================================
# Web 挑战生成器
# ============================================================================

class WebChallengeGenerator:
    """Web 安全挑战生成器"""

    @staticmethod
    def generate_sqli_challenge(flag: Flag) -> Dict[str, str]:
        """SQL 注入挑战"""
        files = {}
        flag_val = flag.flag_value

        files['app.py'] = f'''# -*- coding: utf-8 -*-
"""
CTF Web 挑战 - SQL 注入基础
难度: 简单 | 漏洞: SQL注入（UNION）
Flag: {flag_val}
"""
from flask import Flask, request, render_template_string
import sqlite3, os

app = Flask(__name__)
app.secret_key = os.urandom(32)

def init_db():
    conn = sqlite3.connect(':memory:')
    c = conn.cursor()
    c.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)')
    c.execute('CREATE TABLE flag (id INTEGER PRIMARY KEY, flag TEXT)')
    c.execute("INSERT INTO users VALUES (1, 'admin', 'sup3rs3cr3tpwd')")
    c.execute("INSERT INTO users VALUES (2, 'guest', 'guest123')")
    c.execute("INSERT INTO flag VALUES (1, '{flag_val}')")
    conn.commit()
    return conn

db = init_db()

TPL = """
<!DOCTYPE html><html><head><title>SQL Injection</title></head><body>
<h1>登录系统</h1>
{{% if msg %}}<p>{{{{ msg }}}}</p>{{% endif %}}
<form method="POST">
<input type="text" name="username" placeholder="用户名"><br><br>
<input type="password" name="password" placeholder="密码"><br><br>
<button type="submit">登录</button>
</form>
{{% if result %}}<pre>{{{{ result }}}}</pre>{{% endif %}}
</body></html>
"""

@app.route('/', methods=['GET', 'POST'])
def login():
    msg, result = "", ""
    if request.method == 'POST':
        u = request.form.get('username', '')
        p = request.form.get('password', '')
        # SQL 注入漏洞
        q = f"SELECT * FROM users WHERE username='{{u}}' AND password='{{p}}'"
        try:
            cur = db.cursor()
            cur.execute(q)
            rows = cur.fetchall()
            if rows:
                msg = "登录成功: " + rows[0][1]
            else:
                msg = "用户名或密码错误"
        except Exception as e:
            msg = f"SQL错误: {{e}}"
            result = q
    return render_template_string(TPL, msg=msg, result=result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
'''

        files['Dockerfile'] = '''FROM python:3.9-slim
WORKDIR /app
COPY app.py .
RUN pip install flask --no-cache-dir
EXPOSE 5000
CMD ["python", "app.py"]
'''

        files['docker-compose.yml'] = f'''version: '3'
services:
  web-sqli:
    build: .
    ports:
      - "5001:5000"
    restart: unless-stopped
'''

        files['README.md'] = f'''# SQL 注入 CTF 挑战

## 基本信息
- **挑战名称**: {flag.challenge_name}
- **难度**: {flag.difficulty}
- **分类**: Web
- **分值**: {flag.points}

## 描述
一个登录系统存在 SQL 注入漏洞，请通过注入读取 flag 表。

## 提示
1. 尝试 `' OR 1=1 --` 绕过登录
2. 使用 UNION 注入: `' UNION SELECT 1,flag,3 FROM flag --`
3. Flag 格式: `flag{{...}}`

## Flag
`{flag_val}`
'''
        return files

    @staticmethod
    def generate_xss_challenge(flag: Flag) -> Dict[str, str]:
        """XSS 挑战"""
        files = {}
        flag_val = flag.flag_value

        files['app.py'] = f'''# -*- coding: utf-8 -*-
"""
CTF Web 挑战 - 反射型 XSS
难度: 简单 | 漏洞: XSS
Flag: {flag_val}
"""
from flask import Flask, request, render_template_string

app = Flask(__name__)
FLAG = "{flag_val}"

TPL = """
<!DOCTYPE html><html><head><title>XSS Challenge</title></head><body>
<h1>搜索页面</h1>
<form method="GET">
<input type="text" name="q" value="{{{{ query | safe }}}}" placeholder="搜索...">
<button type="submit">搜索</button>
</form>
{{% if query %}}<p>你搜索了: {{{{ query | safe }}}}</p>{{% endif %}}
{{% if is_admin %}}<div id="flag">{{{{ admin_flag }}}}</div>{{% endif %}}
<p><small>加 ?admin=true 查看管理员视角</small></p>
</body></html>
"""

@app.route('/')
def index():
    q = request.args.get('q', '')
    is_admin = request.args.get('admin') == 'true'
    return render_template_string(TPL, query=q, is_admin=is_admin,
                                  admin_flag=FLAG if is_admin else "")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
'''

        files['Dockerfile'] = '''FROM python:3.9-slim
WORKDIR /app
COPY app.py .
RUN pip install flask --no-cache-dir
EXPOSE 5000
CMD ["python", "app.py"]
'''

        files['docker-compose.yml'] = '''version: '3'
services:
  web-xss:
    build: .
    ports:
      - "5002:5000"
    restart: unless-stopped
'''

        files['README.md'] = f'''# XSS CTF 挑战

## 基本信息
- **挑战名称**: {flag.challenge_name}
- **难度**: {flag.difficulty}
- **分类**: Web
- **分值**: {flag.points}

## 描述
搜索页面存在反射型 XSS 漏洞，Flag 在管理员视角可见。

## 提示
1. 搜索框直接输出无过滤
2. 访问 `/?admin=true&q=test` 可以看到 Flag
3. 尝试 `<script>alert(1)</script>` 验证 XSS

## Flag
`{flag_val}`
'''
        return files

    @staticmethod
    def generate_ssrf_challenge(flag: Flag) -> Dict[str, str]:
        """SSRF 挑战"""
        files = {}
        flag_val = flag.flag_value

        files['app.py'] = f'''# -*- coding: utf-8 -*-
"""
CTF Web 挑战 - SSRF
难度: 中等 | 漏洞: SSRF
Flag: {flag_val}
"""
from flask import Flask, request, render_template_string, Response
import requests

app = Flask(__name__)
FLAG = "{flag_val}"

TPL = """
<!DOCTYPE html><html><head><title>Image Proxy</title></head><body>
<h1>图片代理服务</h1>
<form method="POST">
<input type="text" name="url" size="50" placeholder="http://example.com/image.jpg">
<button type="submit">获取</button>
</form>
{{% if message %}}<p>{{{{ message }}}}</p>{{% endif %}}
{{% if content %}}<hr><pre>{{{{ content }}}}</pre>{{% endif %}}
<p><small>内网服务: http://127.0.0.1:5000/flag</small></p>
</body></html>
"""

@app.route('/')
def index():
    return render_template_string(TPL, message="", content="")

@app.route('/fetch', methods=['POST'])
def fetch():
    url = request.form.get('url', '')
    if not url:
        return render_template_string(TPL, message="请输入URL", content="")
    try:
        resp = requests.get(url, timeout=5)
        ct = resp.headers.get('Content-Type', '')
        if 'image' in ct:
            return Response(resp.content, content_type=ct)
        return render_template_string(TPL, message=f"获取成功({ct})", content=resp.text[:2000])
    except Exception as e:
        return render_template_string(TPL, message=f"失败: {{e}}", content="")

@app.route('/flag')
def flag_endpoint():
    if request.remote_addr not in ('127.0.0.1', '::1'):
        return "Access Denied", 403
    return f"Flag: {{FLAG}}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
'''

        files['Dockerfile'] = '''FROM python:3.9-slim
WORKDIR /app
COPY app.py .
RUN pip install flask requests --no-cache-dir
EXPOSE 5000
CMD ["python", "app.py"]
'''

        files['docker-compose.yml'] = '''version: '3'
services:
  web-ssrf:
    build: .
    ports:
      - "5003:5000"
    restart: unless-stopped
'''

        files['README.md'] = f'''# SSRF CTF 挑战

## 基本信息
- **挑战名称**: {flag.challenge_name}
- **难度**: {flag.difficulty}
- **分类**: Web
- **分值**: {flag.points}

## 描述
图片代理服务存在 SSRF 漏洞，通过访问内网 `/flag` 获取 Flag。

## 提示
1. 在 URL 输入 `http://127.0.0.1:5000/flag`
2. `/flag` 仅允许 localhost 访问
3. SSRF 可以绕过 IP 限制

## Flag
`{flag_val}`
'''
        return files

    @staticmethod
    def generate_command_injection_challenge(flag: Flag) -> Dict[str, str]:
        """命令注入挑战"""
        files = {}
        flag_val = flag.flag_value

        files['app.py'] = f'''# -*- coding: utf-8 -*-
"""
CTF Web 挑战 - 命令注入
难度: 简单 | 漏洞: OS命令注入
Flag: {flag_val}
"""
from flask import Flask, request, render_template_string
import subprocess, os

app = Flask(__name__)
FLAG = "{flag_val}"
with open('/tmp/flag.txt', 'w') as f:
    f.write(FLAG)

TPL = """
<!DOCTYPE html><html><head><title>Ping Tool</title></head><body>
<h1>Ping 工具</h1>
<form method="POST">
<input type="text" name="ip" placeholder="8.8.8.8">
<button type="submit">Ping</button>
</form>
{{% if result %}}<pre>{{{{ result }}}}</pre>{{% endif %}}
<p><small>Flag 在 /tmp/flag.txt</small></p>
</body></html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    result = ""
    if request.method == 'POST':
        ip = request.form.get('ip', '')
        if ip:
            try:
                output = subprocess.check_output(
                    f"ping -c 3 {{ip}}", shell=True,
                    stderr=subprocess.STDOUT, timeout=10
                ).decode('utf-8', errors='replace')
                result = output
            except Exception as e:
                result = f"错误: {{e}}"
    return render_template_string(TPL, result=result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
'''

        files['Dockerfile'] = '''FROM python:3.9-slim
RUN apt-get update && apt-get install -y iputils-ping --no-install-recommends && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY app.py .
RUN pip install flask --no-cache-dir
EXPOSE 5000
CMD ["python", "app.py"]
'''

        files['docker-compose.yml'] = '''version: '3'
services:
  web-cmd:
    build: .
    ports:
      - "5004:5000"
    restart: unless-stopped
'''

        files['README.md'] = f'''# 命令注入 CTF 挑战

## 基本信息
- **挑战名称**: {flag.challenge_name}
- **难度**: {flag.difficulty}
- **分类**: Web
- **分值**: {flag.points}

## 描述
Ping 工具存在命令注入漏洞，Flag 在 `/tmp/flag.txt`。

## 提示
1. 输入 `127.0.0.1; cat /tmp/flag.txt`
2. 或 `127.0.0.1 && cat /tmp/flag.txt`
3. 或 `127.0.0.1 | cat /tmp/flag.txt`

## Flag
`{flag_val}`
'''
        return files

    @staticmethod
    def generate_file_inclusion_challenge(flag: Flag) -> Dict[str, str]:
        """文件包含挑战"""
        files = {}
        flag_val = flag.flag_value

        files['app.py'] = f'''# -*- coding: utf-8 -*-
"""
CTF Web 挑战 - 文件包含 (LFI)
难度: 中等 | 漏洞: 本地文件包含
Flag: {flag_val}
"""
from flask import Flask, request, render_template_string
import os

app = Flask(__name__)
FLAG = "{flag_val}"
with open('/etc/flag.conf', 'w') as f:
    f.write(FLAG)

TPL = """
<!DOCTYPE html><html><head><title>Page Loader</title></head><body>
<h1>页面加载器</h1>
<form method="GET">
<input type="text" name="page" value="home">
<button type="submit">加载</button>
</form>
{{% if content %}}<div>{{{{ content | safe }}}}</div>{{% endif %}}
{{% if error %}}<p style="color:red">{{{{ error }}}}</p>{{% endif %}}
</body></html>
"""

PAGES = {{
    'home': '<h2>首页</h2><p>欢迎</p>',
    'about': '<h2>关于</h2><p>测试网站</p>',
    'contact': '<h2>联系</h2><p>admin@example.com</p>'
}}

@app.route('/')
def index():
    page = request.args.get('page', 'home')
    if page in PAGES:
        return render_template_string(TPL, content=PAGES[page], error="")
    try:
        # 文件包含漏洞
        if os.path.exists(page):
            with open(page, 'r') as f:
                return render_template_string(TPL, content=f.read(), error="")
        return render_template_string(TPL, content="", error=f"页面不存在: {{page}}")
    except Exception as e:
        return render_template_string(TPL, content="", error=str(e))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
'''

        files['Dockerfile'] = '''FROM python:3.9-slim
WORKDIR /app
COPY app.py .
RUN pip install flask --no-cache-dir
EXPOSE 5000
CMD ["python", "app.py"]
'''

        files['docker-compose.yml'] = '''version: '3'
services:
  web-lfi:
    build: .
    ports:
      - "5005:5000"
    restart: unless-stopped
'''

        files['README.md'] = f'''# 文件包含 CTF 挑战

## 基本信息
- **挑战名称**: {flag.challenge_name}
- **难度**: {flag.difficulty}
- **分类**: Web
- **分值**: {flag.points}

## 描述
页面加载器存在 LFI 漏洞，Flag 在 `/etc/flag.conf`。

## 提示
1. page 参数输入 `../../../etc/flag.conf`
2. 先用 `../../../../etc/passwd` 验证 LFI

## Flag
`{flag_val}`
'''
        return files


# ============================================================================
# 密码学挑战生成器
# ============================================================================

class CryptoChallengeGenerator:
    """密码学挑战生成器"""

    @staticmethod
    def _caesar_encrypt(text: str, shift: int) -> str:
        """凯撒加密"""
        result = ""
        for char in text:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                result += chr((ord(char) - base + shift) % 26 + base)
            else:
                result += char
        return result

    @staticmethod
    def generate_caesar_cipher_challenge(flag: Flag) -> Dict[str, str]:
        """凯撒密码挑战"""
        shift = random.randint(1, 25)
        encrypted = CryptoChallengeGenerator._caesar_encrypt(flag.flag_value, shift)
        files = {}

        files['challenge.py'] = f'''# -*- coding: utf-8 -*-
"""
CTF Crypto 挑战 - 凯撒密码
难度: 简单 | 分类: 古典密码
"""
ciphertext = "{encrypted}"

def caesar_decrypt(text, shift):
    result = ""
    for c in text:
        if c.isalpha():
            base = ord('A') if c.isupper() else ord('a')
            result += chr((ord(c) - base - shift) % 26 + base)
        else:
            result += c
    return result

for i in range(26):
    d = caesar_decrypt(ciphertext, i)
    if "flag{{" in d:
        print(f"偏移 {{i}}: {{d}}")

# Flag: {flag.flag_value}
'''

        files['README.md'] = f'''# 凯撒密码 CTF 挑战

## 基本信息
- **挑战名称**: {flag.challenge_name}
- **难度**: {flag.difficulty}
- **分类**: Crypto
- **分值**: {flag.points}

## 密文
```
{encrypted}
```

## 提示
1. 凯撒密码，每个字母按固定偏移移动
2. 尝试 26 种偏移量
3. 频率分析可加速破解

## Flag
`{flag.flag_value}`
'''
        return files

    @staticmethod
    def generate_rsa_challenge(flag: Flag) -> Dict[str, str]:
        """RSA 小公钥指数挑战"""
        files = {}

        if HAS_PYCRYPTO:
            from Crypto.Util.number import getPrime, bytes_to_long
            e = 3
            p = getPrime(1024)
            q = getPrime(1024)
            n = p * q
            m = bytes_to_long(flag.flag_value.encode())
            c = pow(m, e, n)
        else:
            # 简化版：使用大整数
            n = random.getrandbits(2048)
            e = 3
            m = int.from_bytes(flag.flag_value.encode(), 'big')
            c = pow(m, e, n)

        files['challenge.py'] = f'''# -*- coding: utf-8 -*-
"""
CTF Crypto 挑战 - RSA 小公钥指数攻击
难度: 中等 | 分类: 公钥密码
当 e=3 且 m^3 < n 时，c = m^3，可直接开立方根。
"""
n = {n}
e = {e}
c = {c}

# 方法1: 直接开立方根
{"import gmpy2; m, exact = gmpy2.iroot(c, 3); print(f'Flag: {{bytes.fromhex(hex(int(m))[2:]).decode()}}')" if HAS_GMPY2 else "# 需要 gmpy2: pip install gmpy2\n# m, exact = iroot(c, 3)"}

# 方法2: 暴力 c + k*n
for k in range(10000):
    val = c + k * n
    # 近似开立方根
    m_approx = round(val ** (1/3))
    for delta in range(-5, 6):
        candidate = m_approx + delta
        if candidate ** 3 == val:
            try:
                flag = bytes.fromhex(hex(candidate)[2:]).decode()
                print(f"Flag (k={{k}}): {{flag}}")
            except:
                pass

# Flag: {flag.flag_value}
'''

        files['README.md'] = f'''# RSA 小公钥指数 CTF 挑战

## 基本信息
- **挑战名称**: {flag.challenge_name}
- **难度**: {flag.difficulty}
- **分类**: Crypto
- **分值**: {flag.points}

## RSA 参数
- n = {n}
- e = {e}
- c = {c}

## 提示
1. e=3 且 m^3 < n 时，c = m^3
2. 对 c 开立方根得到明文 m
3. 使用 gmpy2.iroot() 精确开根
4. 如 m^3 > n，尝试 c + k*n 再开根

## Flag
`{flag.flag_value}`
'''
        return files

    @staticmethod
    def generate_hash_crack_challenge(flag: Flag) -> Dict[str, str]:
        """哈希破解挑战"""
        md5_hash = hashlib.md5(flag.flag_value.encode()).hexdigest()
        sha256_hash = hashlib.sha256(flag.flag_value.encode()).hexdigest()
        files = {}

        files['challenge.py'] = f'''# -*- coding: utf-8 -*-
"""
CTF Crypto 挑战 - 哈希破解
难度: 简单 | 分类: 哈希
"""
import hashlib

md5_hash = "{md5_hash}"
sha256_hash = "{sha256_hash}"

# 提示: Flag 格式 flag{{32位字符}}
# 可以使用 hashcat 破解: hashcat -m 0 hash.txt -a 3 ?l?d?-_...
# 也可以编写 Python 暴力破解

print(f"MD5: {{md5_hash}}")
print(f"SHA256: {{sha256_hash}}")

# 验证函数
def verify(candidate):
    return hashlib.md5(candidate.encode()).hexdigest() == md5_hash

# Flag: {flag.flag_value}
'''

        files['README.md'] = f'''# 哈希破解 CTF 挑战

## 基本信息
- **挑战名称**: {flag.challenge_name}
- **难度**: {flag.difficulty}
- **分类**: Crypto
- **分值**: {flag.points}

## 哈希值
- MD5: `{md5_hash}`
- SHA256: `{sha256_hash}`

## 提示
1. Flag 格式: `flag{{32位随机字符}}`
2. 使用 hashcat: `hashcat -m 0 -a 3 hash.txt ?l?d?-_...`
3. 也可编写 Python 脚本破解

## Flag
`{flag.flag_value}`
'''
        return files

    @staticmethod
    def generate_xor_challenge(flag: Flag) -> Dict[str, str]:
        """XOR 加密挑战"""
        key_length = random.randint(8, 16)
        key = os.urandom(key_length)
        flag_bytes = flag.flag_value.encode('utf-8')
        encrypted = bytes(flag_bytes[i] ^ key[i % len(key)] for i in range(len(flag_bytes)))
        encrypted_hex = encrypted.hex()
        key_hex = key.hex()
        files = {}

        files['challenge.py'] = f'''# -*- coding: utf-8 -*-
"""
CTF Crypto 挑战 - XOR 加密
难度: 简单 | 分类: 对称加密
"""
ciphertext_hex = "{encrypted_hex}"
key_hex = "{key_hex}"

ciphertext = bytes.fromhex(ciphertext_hex)
key = bytes.fromhex(key_hex)

def xor_decrypt(ct, k):
    return bytes(ct[i] ^ k[i % len(k)] for i in range(len(ct)))

plaintext = xor_decrypt(ciphertext, key)
flag = plaintext.decode('utf-8')
print(f"Flag: {{flag}}")

# Flag: {flag.flag_value}
'''

        files['README.md'] = f'''# XOR 加密 CTF 挑战

## 基本信息
- **挑战名称**: {flag.challenge_name}
- **难度**: {flag.difficulty}
- **分类**: Crypto
- **分值**: {flag.points}

## 数据
- 密文 (hex): `{encrypted_hex}`
- 密钥 (hex): `{key_hex}`

## 提示
1. XOR 可逆：密文 ^ 密钥 = 明文
2. 密钥循环使用

## Flag
`{flag.flag_value}`
'''
        return files


# ============================================================================
# 杂项挑战生成器
# ============================================================================

class MiscChallengeGenerator:
    """杂项挑战生成器"""

    @staticmethod
    def generate_encoding_challenge(flag: Flag) -> Dict[str, str]:
        """多层编码挑战"""
        s1 = flag.flag_value.encode('utf-8')
        s2 = base64.b64encode(s1)
        s3 = s2.hex()
        s4 = base64.b64encode(s3.encode())
        s5 = s4.hex()
        files = {}

        files['challenge.py'] = f'''# -*- coding: utf-8 -*-
"""
CTF Misc 挑战 - 多层编码
难度: 简单 | 分类: 编码
"""
import base64

encoded = "{s5}"

def decode(data):
    # 1. Hex -> Base64
    s1 = bytes.fromhex(data).decode()
    # 2. Base64 -> Hex
    s2 = base64.b64decode(s1).decode()
    # 3. Hex -> Base64
    s3 = bytes.fromhex(s2).decode()
    # 4. Base64 -> Flag
    s4 = base64.b64decode(s3).decode()
    return s4

flag = decode(encoded)
print(f"Flag: {{flag}}")

# Flag: {flag.flag_value}
'''

        files['README.md'] = f'''# 多层编码 CTF 挑战

## 基本信息
- **挑战名称**: {flag.challenge_name}
- **难度**: {flag.difficulty}
- **分类**: Misc
- **分值**: {flag.points}

## 编码数据
```
{s5}
```

## 提示
1. Hex -> Base64 -> Hex -> Base64
2. 逐层解码直到可读

## Flag
`{flag.flag_value}`
'''
        return files

    @staticmethod
    def generate_steganography_challenge(flag: Flag) -> Dict[str, str]:
        """LSB 隐写术挑战"""
        files = {}

        files['challenge.py'] = '''# -*- coding: utf-8 -*-
"""
CTF Misc 挑战 - LSB 隐写术
难度: 中等 | 分类: 隐写
Flag: FLAG_PLACEHOLDER
"""
from PIL import Image
import sys

def extract_lsb(image_path):
    img = Image.open(image_path)
    pixels = list(img.getdata())
    bits = []
    for pixel in pixels:
        if isinstance(pixel, tuple):
            for ch in pixel[:3]:
                bits.append(ch & 1)
        else:
            bits.append(pixel & 1)
    msg = []
    for i in range(0, len(bits) - 7, 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | bits[i + j]
        if byte == 0:
            break
        msg.append(chr(byte))
    return ''.join(msg)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python challenge.py <图片路径>")
        print("也可使用 zsteg image.png 或 stegsolve")
        sys.exit(1)
    result = extract_lsb(sys.argv[1])
    print(f"隐藏信息: {result}")

# Flag: FLAG_PLACEHOLDER
'''.replace('FLAG_PLACEHOLDER', flag.flag_value)

        files['README.md'] = f'''# LSB 隐写术 CTF 挑战

## 基本信息
- **挑战名称**: {flag.challenge_name}
- **难度**: {flag.difficulty}
- **分类**: Misc
- **分值**: {flag.points}

## 描述
Flag 隐藏在图片最低有效位中。

## 提示
1. LSB 隐写编码在像素最低位
2. 工具: zsteg, stegsolve, PIL
3. 检查 RGB 和 Alpha 通道

## Flag
`{flag.flag_value}`
'''
        return files

    @staticmethod
    def generate_forensics_challenge(flag: Flag) -> Dict[str, str]:
        """取证挑战"""
        files = {}

        files['challenge.py'] = '''# -*- coding: utf-8 -*-
"""
CTF Misc 挑战 - 内存取证
难度: 中等 | 分类: Forensics
Flag: FLAG_PLACEHOLDER
"""
# 使用 Volatility 3 分析内存镜像
# vol -f memory.raw windows.info
# vol -f memory.raw windows.pslist
# vol -f memory.raw windows.cmdline
# vol -f memory.raw windows.netscan
# vol -f memory.raw windows.filescan | grep -i flag
# strings memory.raw | grep -i "flag{"

# Flag: FLAG_PLACEHOLDER
'''.replace('FLAG_PLACEHOLDER', flag.flag_value)

        files['README.md'] = f'''# 内存取证 CTF 挑战

## 基本信息
- **挑战名称**: {flag.challenge_name}
- **难度**: {flag.difficulty}
- **分类**: Misc / Forensics
- **分值**: {flag.points}

## 描述
从内存镜像提取 Flag。

## 提示
1. 使用 Volatility 3
2. `strings memory.raw | grep -i flag`
3. 检查命令行历史和网络连接

## Flag
`{flag.flag_value}`
'''
        return files


# ============================================================================
# 计分板生成器
# ============================================================================

class ScoreboardGenerator:
    """CTF 计分板生成器"""

    @staticmethod
    def generate_html(challenges: List[Challenge], title: str = "CTF 2026") -> str:
        """生成 HTML 计分板"""
        severity_colors = {"简单": "#53d769", "中等": "#fdcb6e", "困难": "#e17055", "地狱": "#d63031"}

        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>{title} - 计分板</title>
<style>
body {{ font-family: 'Microsoft YaHei', sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }}
h1 {{ text-align: center; color: #e94560; border-bottom: 2px solid #e94560; padding-bottom: 10px; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 15px; max-width: 1200px; margin: 0 auto; }}
.card {{ background: #16213e; border-radius: 10px; padding: 20px; border: 1px solid #0f3460; }}
.card:hover {{ border-color: #e94560; }}
.card .cat {{ color: #e94560; font-size: 0.85em; }}
.card .pts {{ float: right; color: #53d769; font-weight: bold; }}
.card .diff {{ display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 0.8em; margin-left: 10px; color: #000; }}
.card .title {{ font-size: 1.2em; margin: 8px 0; }}
.card .desc {{ color: #aaa; font-size: 0.9em; }}
.summary {{ text-align: center; margin: 20px 0; }}
.summary span {{ display: inline-block; margin: 0 15px; }}
.summary .count {{ font-size: 1.5em; color: #e94560; }}
</style>
</head>
<body>
<h1>{title}</h1>
<div class="summary">
<span><div class="count">{len(challenges)}</div>挑战总数</span>
<span><div class="count">{sum(c.points for c in challenges)}</div>总分值</span>
</div>
<div class="grid">
'''
        for ch in challenges:
            color = severity_colors.get(ch.difficulty, "#6c757d")
            html += f'''<div class="card">
<span class="cat">{ch.category}</span>
<span class="diff" style="background:{color}">{ch.difficulty}</span>
<span class="pts">{ch.points} pts</span>
<div class="title">{ch.title}</div>
<div class="desc">{ch.description}</div>
</div>
'''

        html += '''</div>
</body>
</html>'''
        return html

    @staticmethod
    def generate_ctfd_config(challenges: List[Challenge]) -> str:
        """生成 CTFd 兼容的挑战配置"""
        data = {
            'challenges': [
                {
                    'name': ch.title,
                    'category': ch.category,
                    'description': ch.description,
                    'value': ch.points,
                    'type': 'standard',
                    'state': 'visible' if ch.is_active else 'hidden',
                    'flag': ch.flag
                }
                for ch in challenges
            ]
        }
        return json.dumps(data, ensure_ascii=False, indent=2)


# ============================================================================
# 挑战管理器
# ============================================================================

class ChallengeManager:
    """CTF 挑战管理器"""

    TEMPLATES = {
        'web_sqli': {
            'name': 'SQL注入基础',
            'category': 'Web',
            'difficulty': '简单',
            'points': 100,
            'description': '登录系统存在 SQL 注入漏洞',
            'generator': WebChallengeGenerator.generate_sqli_challenge
        },
        'web_xss': {
            'name': 'XSS反射型跨站脚本',
            'category': 'Web',
            'difficulty': '简单',
            'points': 100,
            'description': '搜索页面存在反射型 XSS',
            'generator': WebChallengeGenerator.generate_xss_challenge
        },
        'web_ssrf': {
            'name': 'SSRF服务端请求伪造',
            'category': 'Web',
            'difficulty': '中等',
            'points': 200,
            'description': '图片代理服务存在 SSRF',
            'generator': WebChallengeGenerator.generate_ssrf_challenge
        },
        'web_cmd_injection': {
            'name': '命令注入',
            'category': 'Web',
            'difficulty': '简单',
            'points': 100,
            'description': 'Ping 工具存在命令注入',
            'generator': WebChallengeGenerator.generate_command_injection_challenge
        },
        'web_lfi': {
            'name': '文件包含漏洞',
            'category': 'Web',
            'difficulty': '中等',
            'points': 200,
            'description': '页面加载器存在 LFI',
            'generator': WebChallengeGenerator.generate_file_inclusion_challenge
        },
        'crypto_caesar': {
            'name': '凯撒密码',
            'category': 'Crypto',
            'difficulty': '简单',
            'points': 50,
            'description': '使用凯撒密码加密的密文',
            'generator': CryptoChallengeGenerator.generate_caesar_cipher_challenge
        },
        'crypto_rsa': {
            'name': 'RSA小公钥指数',
            'category': 'Crypto',
            'difficulty': '中等',
            'points': 200,
            'description': 'RSA 使用小公钥指数 e=3',
            'generator': CryptoChallengeGenerator.generate_rsa_challenge
        },
        'crypto_hash': {
            'name': '哈希破解',
            'category': 'Crypto',
            'difficulty': '简单',
            'points': 100,
            'description': 'Flag 被哈希加密',
            'generator': CryptoChallengeGenerator.generate_hash_crack_challenge
        },
        'crypto_xor': {
            'name': 'XOR加密',
            'category': 'Crypto',
            'difficulty': '简单',
            'points': 50,
            'description': 'Flag 被 XOR 加密',
            'generator': CryptoChallengeGenerator.generate_xor_challenge
        },
        'misc_encoding': {
            'name': '多层编码',
            'category': 'Misc',
            'difficulty': '简单',
            'points': 50,
            'description': 'Flag 经过多层编码',
            'generator': MiscChallengeGenerator.generate_encoding_challenge
        },
        'misc_stego': {
            'name': 'LSB隐写术',
            'category': 'Misc',
            'difficulty': '中等',
            'points': 200,
            'description': 'Flag 隐藏在图片 LSB 中',
            'generator': MiscChallengeGenerator.generate_steganography_challenge
        },
        'misc_forensics': {
            'name': '内存取证',
            'category': 'Misc',
            'difficulty': '中等',
            'points': 200,
            'description': '从内存镜像提取 Flag',
            'generator': MiscChallengeGenerator.generate_forensics_challenge
        },
    }

    def __init__(self, output_dir: str = "ctf_challenges"):
        self.output_dir = output_dir
        self.flag_manager = FlagManager(os.path.join(output_dir, 'flags.json'))
        self.challenges: List[Challenge] = []

    def generate_challenge(self, template_id: str, custom_name: str = None) -> bool:
        """生成单个挑战"""
        if template_id not in self.TEMPLATES:
            print(f"[错误] 未知模板: {template_id}")
            return False

        template = self.TEMPLATES[template_id]
        challenge_name = custom_name or template['name']

        flag = self.flag_manager.generate_flag(
            challenge_name=challenge_name,
            category=template['category'],
            difficulty=template['difficulty'],
            points=template['points'],
            description=template['description']
        )

        files = template['generator'](flag)

        challenge_dir = os.path.join(self.output_dir, template_id)
        os.makedirs(challenge_dir, exist_ok=True)

        for filename, content in files.items():
            file_path = os.path.join(challenge_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  [+] 生成: {file_path}")

        challenge = Challenge(
            name=template_id,
            title=challenge_name,
            category=template['category'],
            difficulty=template['difficulty'],
            description=template['description'],
            flag=flag.flag_value,
            points=template['points'],
            hint=f"查看 {challenge_dir}/README.md",
            docker_required=template['category'] == 'Web'
        )
        self.challenges.append(challenge)

        print(f"[+] 挑战完成: {challenge_name} (Flag: {flag.flag_value})")
        return True

    def generate_all(self):
        """生成所有挑战"""
        print("=" * 60)
        print("开始生成所有 CTF 挑战模板...")
        print("=" * 60)

        for template_id in self.TEMPLATES:
            self.generate_challenge(template_id)
            print()

        self.generate_scoreboard()

        print("=" * 60)
        print(f"完成！共 {len(self.challenges)} 个挑战")
        print(f"Flag 数据库: {os.path.join(self.output_dir, 'flags.json')}")
        print(f"计分板: {os.path.join(self.output_dir, 'scoreboard.html')}")
        print("=" * 60)

    def generate_scoreboard(self, title: str = "CTF 2026"):
        """生成计分板"""
        if not self.challenges:
            print("[警告] 无挑战数据，跳过计分板")
            return

        # HTML 计分板
        html = ScoreboardGenerator.generate_html(self.challenges, title)
        html_path = os.path.join(self.output_dir, 'scoreboard.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  [+] 计分板: {html_path}")

        # CTFd 配置
        ctfd_config = ScoreboardGenerator.generate_ctfd_config(self.challenges)
        ctfd_path = os.path.join(self.output_dir, 'challenges.json')
        with open(ctfd_path, 'w', encoding='utf-8') as f:
            f.write(ctfd_config)
        print(f"  [+] CTFd 配置: {ctfd_path}")

        # docker-compose
        compose = '''version: '3'
services:
  ctfd:
    image: ctfd/ctfd:latest
    ports:
      - "8000:8000"
    environment:
      - SECRET_KEY=change_this_secret
    volumes:
      - ./challenges.json:/opt/ctfd/challenges.json
    restart: unless-stopped
'''
        compose_path = os.path.join(self.output_dir, 'docker-compose.ctfd.yml')
        with open(compose_path, 'w', encoding='utf-8') as f:
            f.write(compose)
        print(f"  [+] Docker Compose: {compose_path}")

    def list_templates(self):
        """列出所有可用模板"""
        print("=" * 70)
        print(f"{'模板ID':<25} {'名称':<20} {'分类':<10} {'难度':<8} {'分值'}")
        print("=" * 70)
        for tid, tmpl in self.TEMPLATES.items():
            print(f"{tid:<25} {tmpl['name']:<20} {tmpl['category']:<10} {tmpl['difficulty']:<8} {tmpl['points']}")
        print("=" * 70)
        print(f"共 {len(self.TEMPLATES)} 个模板")


# ============================================================================
# 主函数
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='CTF 挑战模板生成与管理工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python ctf_challenge_template.py --list-templates
  python ctf_challenge_template.py --generate-all --output ./my_ctf
  python ctf_challenge_template.py --generate web_sqli --name "我的SQLi"
  python ctf_challenge_template.py --generate-scoreboard --title "MyCTF 2026"
  python ctf_challenge_template.py --verify "flag{xxxxx}"
"""
    )

    parser.add_argument('--list-templates', action='store_true', help='列出所有可用模板')
    parser.add_argument('--generate-all', action='store_true', help='生成所有挑战')
    parser.add_argument('--generate', metavar='TEMPLATE_ID', help='生成指定挑战')
    parser.add_argument('--name', help='自定义挑战名称')
    parser.add_argument('--output', '-o', default='ctf_challenges', help='输出目录')
    parser.add_argument('--generate-scoreboard', action='store_true', help='生成计分板')
    parser.add_argument('--title', default='CTF 2026', help='CTF 标题')
    parser.add_argument('--verify', metavar='FLAG', help='验证 Flag')

    args = parser.parse_args()

    if args.list_templates:
        ChallengeManager(args.output).list_templates()
        return

    if args.verify:
        manager = ChallengeManager(args.output)
        valid, flag = manager.flag_manager.verify_flag(args.verify)
        if valid:
            print(f"[+] Flag 验证成功!")
            print(f"    挑战: {flag.challenge_name}")
            print(f"    分类: {flag.category}")
            print(f"    难度: {flag.difficulty}")
            print(f"    分值: {flag.points}")
        else:
            print(f"[-] Flag 验证失败")
        return

    if args.generate_all:
        os.makedirs(args.output, exist_ok=True)
        ChallengeManager(args.output).generate_all()
        return

    if args.generate:
        os.makedirs(args.output, exist_ok=True)
        manager = ChallengeManager(args.output)
        manager.generate_challenge(args.generate, args.name)
        manager.generate_scoreboard(args.title)
        return

    if args.generate_scoreboard:
        manager = ChallengeManager(args.output)
        if os.path.exists(os.path.join(args.output, 'flags.json')):
            manager.flag_manager._load()
            for flag in manager.flag_manager.list_flags():
                ch = Challenge(
                    name=flag.challenge_name,
                    title=flag.challenge_name,
                    category=flag.category,
                    difficulty=flag.difficulty,
                    description=flag.description,
                    flag=flag.flag_value,
                    points=flag.points
                )
                manager.challenges.append(ch)
        if manager.challenges:
            manager.generate_scoreboard(args.title)
        else:
            print("[错误] 无挑战数据")
        return

    parser.print_help()


if __name__ == '__main__':
    main()
