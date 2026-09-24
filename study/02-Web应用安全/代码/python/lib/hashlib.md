# hashlib 模块

> Python 标准库，提供多种安全哈希算法，用于数据完整性校验、密码存储等。

---

## 一、导入与基本用法

```python
import hashlib
```

---

## 二、常用哈希算法

### 2.1 基本用法

```python
# MD5（不安全，仅用于非安全场景）
md5 = hashlib.md5()
md5.update(b'hello world')
print(md5.hexdigest())  # 5eb63bbbe01eeed093cb22bb8f5acdc3

# SHA-1（已不推荐用于安全场景）
sha1 = hashlib.sha1()
sha1.update(b'hello world')
print(sha1.hexdigest())

# SHA-256（推荐）
sha256 = hashlib.sha256()
sha256.update(b'hello world')
print(sha256.hexdigest())  # b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9

# SHA-512
sha512 = hashlib.sha512()
sha512.update(b'hello world')
print(sha512.hexdigest())

# SHA-224, SHA-384 也可用
print(hashlib.sha224(b'test').hexdigest())
print(hashlib.sha384(b'test').hexdigest())
```

### 2.2 便捷方式

```python
# 一行计算
md5_hash = hashlib.md5(b'hello').hexdigest()
sha256_hash = hashlib.sha256(b'hello').hexdigest()

# 多次 update
h = hashlib.sha256()
h.update(b'hello ')
h.update(b'world')
# 等价于 h.update(b'hello world')
print(h.hexdigest())

# 字节形式的哈希值
digest = hashlib.sha256(b'test').digest()     # 字节
hexdigest = hashlib.sha256(b'test').hexdigest()  # 十六进制字符串

# 哈希长度
print(hashlib.sha256().digest_size)   # 32 字节
print(hashlib.sha256().block_size)    # 64 字节
print(hashlib.sha256().name)          # 'sha256'
```

### 2.3 可用算法查询

```python
# 所有可用算法
print(hashlib.algorithms_available)

# 保证可用的算法
print(hashlib.algorithms_guaranteed)
# {'sha1', 'sha224', 'sha256', 'sha384', 'sha512', 'md5', ...}

# 按名称创建哈希对象
h = hashlib.new('sha256')
h.update(b'test')
print(h.hexdigest())
```

### 2.4 SHA-3 系列

```python
# SHA3-256
h = hashlib.sha3_256(b'test')
print(h.hexdigest())

# SHA3-512
h = hashlib.sha3_512(b'test')

# SHAKE-256（可变长度输出）
h = hashlib.shake_256(b'test')
print(h.digest(10))  # 10 字节输出
```

### 2.5 文件哈希计算

```python
def file_hash(filepath, algorithm='sha256'):
    """计算文件的哈希值"""
    h = hashlib.new(algorithm)
    
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(8192)  # 每次读 8KB
            if not chunk:
                break
            h.update(chunk)
    
    return h.hexdigest()

# 使用
print(file_hash('data.txt', 'md5'))
print(file_hash('data.txt', 'sha256'))
print(file_hash('data.txt', 'sha512'))

# 大文件内存友好的哈希计算
def large_file_hash(filepath, algorithm='sha256', buf_size=65536):
    h = hashlib.new(algorithm)
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(buf_size), b''):
            h.update(chunk)
    return h.hexdigest()
```

---

## 三、HMAC（哈希消息认证码）

```python
import hmac
import hashlib

# 基本用法
key = b'secret_key'
message = b'Hello, HMAC!'

# 使用 hashlib 算法名称
mac = hmac.new(key, message, hashlib.sha256)
print(mac.hexdigest())

# 或使用字符串指定算法
mac = hmac.new(key, message, 'sha256')

# 分步更新
mac = hmac.new(key, digestmod='sha256')
mac.update(b'Hello, ')
mac.update(b'HMAC!')
print(mac.hexdigest())

# 安全比较（防止时序攻击）
def verify_hmac(key, message, signature):
    """安全的 HMAC 验证"""
    mac = hmac.new(key, message, hashlib.sha256)
    expected = mac.digest()
    return hmac.compare_digest(expected, signature)

# 不要直接用 == 比较（可能存在时序攻击）
# if mac.digest() == signature:  # 不安全
```

---

## 四、安全相关使用案例

### 4.1 文件完整性校验

```python
import hashlib
import os

def calculate_checksums(directory, algorithm='sha256'):
    """计算目录中所有文件的校验和"""
    checksums = {}
    
    for root, dirs, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            rel_path = os.path.relpath(filepath, directory)
            
            try:
                h = hashlib.new(algorithm)
                with open(filepath, 'rb') as f:
                    while True:
                        chunk = f.read(8192)
                        if not chunk:
                            break
                        h.update(chunk)
                checksums[rel_path] = h.hexdigest()
            except (IOError, OSError) as e:
                checksums[rel_path] = f"ERROR: {e}"
    
    return checksums

def verify_integrity(directory, saved_checksums, algorithm='sha256'):
    """验证文件完整性"""
    current = calculate_checksums(directory, algorithm)
    changed = []
    
    for filepath, old_hash in saved_checksums.items():
        if filepath not in current:
            changed.append((filepath, 'DELETED', old_hash, None))
        elif current[filepath] != old_hash:
            changed.append((filepath, 'MODIFIED', old_hash, current[filepath]))
    
    for filepath in current:
        if filepath not in saved_checksums:
            changed.append((filepath, 'ADDED', None, current[filepath]))
    
    return changed
```

### 4.2 密码哈希（注意：hashlib 不适合直接哈希密码）

```python
import hashlib
import os
import secrets

# ===== 加盐哈希（比单纯哈希好，但仍不够） =====
def salted_hash(password, salt=None):
    """加盐的 SHA-256 哈希（不推荐用于密码）"""
    if salt is None:
        salt = os.urandom(16)
    elif isinstance(salt, str):
        salt = salt.encode()
    
    if isinstance(password, str):
        password = password.encode()
    
    h = hashlib.sha256()
    h.update(salt)
    h.update(password)
    
    return salt.hex() + ':' + h.hexdigest()

def verify_salted_hash(password, stored_hash):
    salt_hex, hash_hex = stored_hash.split(':')
    salt = bytes.fromhex(salt_hex)
    
    h = hashlib.sha256()
    h.update(salt)
    h.update(password.encode())
    
    return h.hexdigest() == hash_hex

# ===== 更好的选择：使用 bcrypt / scrypt / argon2 =====
# 标准库中的 pbkdf2_hmac（可用，但不是最优）
def pbkdf2_hash(password, iterations=100000):
    """使用 PBKDF2-HMAC-SHA256 哈希密码"""
    if isinstance(password, str):
        password = password.encode()
    
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac('sha256', password, salt, iterations)
    
    return f"pbkdf2_sha256${iterations}${salt.hex()}${dk.hex()}"

def verify_pbkdf2(password, stored_hash):
    """验证 PBKDF2 密码哈希"""
    algo, iterations, salt_hex, hash_hex = stored_hash.split('$')
    iterations = int(iterations)
    salt = bytes.fromhex(salt_hex)
    
    if isinstance(password, str):
        password = password.encode()
    
    dk = hashlib.pbkdf2_hmac('sha256', password, salt, iterations)
    
    # 使用恒定时间比较
    import hmac
    return hmac.compare_digest(dk.hex(), hash_hex)

"""
    重要提示：
    - MD5 和 SHA-1 不应用于密码哈希（太快，易暴力破解）
    - SHA-256/SHA-512 也不推荐直接用于密码
    - 推荐使用专门的密码哈希算法：
      * bcrypt (pip install bcrypt)
      * scrypt (hashlib.scrypt)
      * Argon2 (pip install argon2-cffi)
      * PBKDF2 (可用，但不如上面的)
"""
```

### 4.3 哈希长度扩展攻击演示

```python
import hashlib

"""
    哈希长度扩展攻击 (Hash Length Extension Attack)
    
    原理：对于 Merkle–Damgård 结构的哈希函数（MD5, SHA-1, SHA-256 等），
    知道 message 的哈希值和 message 的长度，可以计算出
    message || padding || append_data 的哈希值。
    
    影响：基于 secret + data 方式构造的签名可以被扩展攻击。
    防御：使用 HMAC 而不是直接拼接密钥。
"""

# 不安全的签名方式（易受长度扩展攻击）
def insecure_sign(key, data):
    """不安全：直接拼接密钥和数据"""
    return hashlib.sha256(key + data).hexdigest()

# 安全的签名方式
def secure_sign(key, data):
    """安全：使用 HMAC"""
    import hmac
    return hmac.new(key, data, hashlib.sha256).hexdigest()

# 验证
key = b'secret_key'
data = b'user=admin&id=1'

# 不安全：可被长度扩展攻击
bad_sig = insecure_sign(key, data)

# 安全：HMAC 不受长度扩展攻击影响
good_sig = secure_sign(key, data)
```

---

## 五、算法安全级别

| 算法 | 输出长度 | 安全级别 | 推荐用途 |
|------|---------|---------|---------|
| MD5 | 128 bit | ❌ 不安全 | 非安全场景的校验和 |
| SHA-1 | 160 bit | ❌ 不安全 | 旧系统兼容 |
| SHA-256 | 256 bit | ✅ 安全 | 数据完整性、数字签名 |
| SHA-512 | 512 bit | ✅ 安全 | 高安全需求 |
| SHA3-256 | 256 bit | ✅ 安全 | 新一代哈希 |
| SHA3-512 | 512 bit | ✅ 安全 | 新一代哈希 |

**密码哈希专用算法（推荐）：**
- bcrypt — 自适应密码哈希
- scrypt — 内存难函数
- Argon2 — 最新密码哈希标准（PHC 冠军）
- PBKDF2 — 标准库可用，可接受

---

## 六、常见问题

| 问题 | 解答 |
|------|------|
| 可以用 MD5/SHA 存密码吗？ | ❌ 不行，太快了，暴力破解容易 |
| 加盐的 SHA-256 存密码可以吗？ | ⚠️ 不太推荐，仍不够慢，建议用 bcrypt/argon2 |
| HMAC 和普通哈希有什么区别？ | HMAC 使用密钥，可验证消息来源和完整性 |
| 为什么用 hmac.compare_digest？ | 防止时序攻击（恒定时间比较） |
| 如何选择哈希算法？ | 一般用 SHA-256，密码用 bcrypt/argon2 |
