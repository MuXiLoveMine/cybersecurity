# -*- coding: utf-8 -*-
"""
身份认证与访问管理（IAM）演示代码
====================================
本脚本包含身份认证与访问控制的核心技术演示，涵盖：

1. 密码哈希验证（bcrypt / Argon2 / PBKDF2）
2. JWT Token 生成与验证
3. OAuth 2.0 授权码流程模拟
4. TOTP 基于时间的动态口令实现
5. RBAC 基于角色的访问控制示例

运行环境：Python 3.7+
依赖安装：
    pip install bcrypt argon2-cffi pyjwt cryptography

注意：本代码仅用于学习演示，生产环境请使用成熟的安全框架。
"""

import hashlib
import hmac
import base64
import time
import struct
import json
import secrets
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple

# ============================================================
# 第一部分：密码哈希验证
# ============================================================

class PasswordHasher:
    """
    密码哈希验证类
    支持多种密码哈希算法：加盐SHA256、PBKDF2、bcrypt、Argon2
    """

    def __init__(self):
        """初始化，尝试导入可选依赖"""
        self.bcrypt_available = False
        self.argon2_available = False

        try:
            import bcrypt
            self.bcrypt = bcrypt
            self.bcrypt_available = True
        except ImportError:
            print("[提示] bcrypt 未安装，跳过 bcrypt 演示")
            print("       安装命令: pip install bcrypt")

        try:
            from argon2 import PasswordHasher as Argon2Hasher
            from argon2.exceptions import VerifyMismatchError
            self.argon2 = Argon2Hasher(
                time_cost=3,        # 迭代次数
                memory_cost=65536,  # 内存使用(KB)，即64MB
                parallelism=4,      # 并行度
                hash_len=32,        # 哈希长度
                salt_len=16         # 盐长度
            )
            self.Argon2VerifyError = VerifyMismatchError
            self.argon2_available = True
        except ImportError:
            print("[提示] argon2-cffi 未安装，跳过 Argon2 演示")
            print("       安装命令: pip install argon2-cffi")

    # ---------- 方法1：加盐 SHA-256 ----------
    @staticmethod
    def hash_sha256_salt(password: str, salt: Optional[bytes] = None) -> Tuple[str, bytes]:
        """
        使用加盐 SHA-256 哈希密码

        参数:
            password: 明文密码
            salt: 盐值，为None则自动生成

        返回:
            (哈希值十六进制字符串, 盐值)
        """
        if salt is None:
            # 使用密码学安全的随机数生成盐（16字节）
            salt = secrets.token_bytes(16)

        # 将密码转为字节，与盐拼接后计算SHA-256
        password_bytes = password.encode('utf-8')
        hash_value = hashlib.sha256(salt + password_bytes).hexdigest()

        return hash_value, salt

    @staticmethod
    def verify_sha256_salt(password: str, stored_hash: str, salt: bytes) -> bool:
        """
        验证加盐 SHA-256 密码

        参数:
            password: 用户输入的明文密码
            stored_hash: 存储的哈希值
            salt: 存储的盐值

        返回:
            True 表示验证通过，False 表示失败
        """
        computed_hash, _ = PasswordHasher.hash_sha256_salt(password, salt)

        # 使用 hmac.compare_digest 进行常数时间比较，防止时序攻击
        # 普通的 == 比较会因为第一个不同字节就返回，导致时间差异可被利用
        return hmac.compare_digest(computed_hash, stored_hash)

    # ---------- 方法2：PBKDF2 ----------
    @staticmethod
    def hash_pbkdf2(password: str, salt: Optional[bytes] = None,
                    iterations: int = 100000) -> Tuple[str, bytes]:
        """
        使用 PBKDF2-HMAC-SHA256 哈希密码

        参数:
            password: 明文密码
            salt: 盐值，为None则自动生成
            iterations: 迭代次数，建议至少10万次

        返回:
            (哈希值十六进制字符串, 盐值)
        """
        if salt is None:
            salt = secrets.token_bytes(16)

        # 使用 PBKDF2 算法派生密钥
        # dkLen=32 表示输出32字节(256位)
        hash_value = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            iterations,
            dklen=32
        )

        return hash_value.hex(), salt

    @staticmethod
    def verify_pbkdf2(password: str, stored_hash: str, salt: bytes,
                      iterations: int = 100000) -> bool:
        """验证 PBKDF2 密码"""
        computed_hash, _ = PasswordHasher.hash_pbkdf2(password, salt, iterations)
        return hmac.compare_digest(computed_hash, stored_hash)

    # ---------- 方法3：bcrypt ----------
    def hash_bcrypt(self, password: str, cost_factor: int = 12) -> str:
        """
        使用 bcrypt 哈希密码

        参数:
            password: 明文密码
            cost_factor: 成本因子，值越大越慢，推荐12（约250ms）

        返回:
            bcrypt 哈希字符串（包含盐和版本信息）
        """
        if not self.bcrypt_available:
            raise NotImplementedError("bcrypt 库未安装")

        # bcrypt 自动生成盐并嵌入到结果中
        # 格式: $2b$12$salt_and_hash
        hashed = self.bcrypt.hashpw(
            password.encode('utf-8'),
            self.bcrypt.gensalt(cost_factor)
        )
        return hashed.decode('utf-8')

    def verify_bcrypt(self, password: str, stored_hash: str) -> bool:
        """验证 bcrypt 密码"""
        if not self.bcrypt_available:
            raise NotImplementedError("bcrypt 库未安装")

        try:
            return self.bcrypt.checkpw(
                password.encode('utf-8'),
                stored_hash.encode('utf-8')
            )
        except Exception:
            return False

    # ---------- 方法4：Argon2 ----------
    def hash_argon2(self, password: str) -> str:
        """
        使用 Argon2id 哈希密码（当前最推荐的算法）

        参数:
            password: 明文密码

        返回:
            Argon2 哈希字符串（包含所有参数和盐）
        """
        if not self.argon2_available:
            raise NotImplementedError("argon2-cffi 库未安装")

        return self.argon2.hash(password)

    def verify_argon2(self, password: str, stored_hash: str) -> bool:
        """验证 Argon2 密码"""
        if not self.argon2_available:
            raise NotImplementedError("argon2-cffi 库未安装")

        try:
            return self.argon2.verify(stored_hash, password)
        except self.Argon2VerifyError:
            return False
        except Exception:
            return False


def demo_password_hashing():
    """演示各种密码哈希算法"""
    print("=" * 60)
    print("【第一部分：密码哈希验证演示】")
    print("=" * 60)

    hasher = PasswordHasher()
    test_password = "MyStr0ngP@ssw0rd!"

    # 1. 加盐 SHA-256
    print("\n1. 加盐 SHA-256 哈希:")
    print("-" * 40)
    sha256_hash, salt = hasher.hash_sha256_salt(test_password)
    print(f"   明文密码: {test_password}")
    print(f"   盐(hex): {salt.hex()}")
    print(f"   哈希值: {sha256_hash}")
    print(f"   验证正确密码: {hasher.verify_sha256_salt(test_password, sha256_hash, salt)}")
    print(f"   验证错误密码: {hasher.verify_sha256_salt('wrongpass', sha256_hash, salt)}")

    # 2. PBKDF2
    print("\n2. PBKDF2-HMAC-SHA256 哈希:")
    print("-" * 40)
    pbkdf2_hash, pbkdf2_salt = hasher.hash_pbkdf2(test_password, iterations=100000)
    print(f"   明文密码: {test_password}")
    print(f"   盐(hex): {pbkdf2_salt.hex()}")
    print(f"   迭代次数: 100,000")
    print(f"   哈希值: {pbkdf2_hash}")
    print(f"   验证正确密码: {hasher.verify_pbkdf2(test_password, pbkdf2_hash, pbkdf2_salt)}")
    print(f"   验证错误密码: {hasher.verify_pbkdf2('wrongpass', pbkdf2_hash, pbkdf2_salt)}")

    # 3. bcrypt
    if hasher.bcrypt_available:
        print("\n3. bcrypt 哈希:")
        print("-" * 40)
        start_time = time.time()
        bcrypt_hash = hasher.hash_bcrypt(test_password, cost_factor=12)
        elapsed = time.time() - start_time
        print(f"   明文密码: {test_password}")
        print(f"   哈希值: {bcrypt_hash}")
        print(f"   计算耗时: {elapsed:.3f}秒")
        print(f"   验证正确密码: {hasher.verify_bcrypt(test_password, bcrypt_hash)}")
        print(f"   验证错误密码: {hasher.verify_bcrypt('wrongpass', bcrypt_hash)}")

    # 4. Argon2
    if hasher.argon2_available:
        print("\n4. Argon2id 哈希 (当前推荐):")
        print("-" * 40)
        start_time = time.time()
        argon2_hash = hasher.hash_argon2(test_password)
        elapsed = time.time() - start_time
        print(f"   明文密码: {test_password}")
        print(f"   哈希值: {argon2_hash}")
        print(f"   计算耗时: {elapsed:.3f}秒")
        print(f"   验证正确密码: {hasher.verify_argon2(test_password, argon2_hash)}")
        print(f"   验证错误密码: {hasher.verify_argon2('wrongpass', argon2_hash)}")

    print("\n💡 安全提示:")
    print("   - 永远不要存储明文密码")
    print("   - 使用慢哈希算法(bcrypt/Argon2)提高破解成本")
    print("   - 使用常数时间比较防止时序攻击")
    print("   - Argon2id 是当前最推荐的密码哈希算法")


# ============================================================
# 第二部分：JWT Token 生成与验证
# ============================================================

class JWTManager:
    """
    JWT (JSON Web Token) 管理器
    实现 JWT 的生成、验证和解码
    """

    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        """
        初始化 JWT 管理器

        参数:
            secret_key: 签名密钥（生产环境应使用强密钥并妥善保管）
            algorithm: 签名算法，默认HS256
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.pyjwt_available = False

        try:
            import jwt
            self.jwt = jwt
            self.pyjwt_available = True
        except ImportError:
            print("[提示] PyJWT 未安装，使用纯Python实现演示")
            print("       安装命令: pip install pyjwt")

    @staticmethod
    def _base64url_encode(data: bytes) -> str:
        """Base64URL 编码（JWT 使用的编码格式）"""
        return base64.urlsafe_b64encode(data).rstrip(b'=').decode('ascii')

    @staticmethod
    def _base64url_decode(data: str) -> bytes:
        """Base64URL 解码"""
        # 补齐 = 填充字符
        padding = 4 - len(data) % 4
        if padding != 4:
            data += '=' * padding
        return base64.urlsafe_b64decode(data)

    def generate_token_manual(self, payload: dict, expires_in: int = 3600) -> str:
        """
        手动实现 JWT 生成（用于学习原理）

        参数:
            payload: 载荷数据
            expires_in: 过期时间（秒）

        返回:
            JWT 字符串
        """
        # Header: 声明类型和算法
        header = {
            "alg": self.algorithm,
            "typ": "JWT"
        }

        # 添加过期时间和签发时间
        payload = payload.copy()
        now = int(time.time())
        payload["iat"] = now          # Issued At: 签发时间
        payload["exp"] = now + expires_in  # Expiration: 过期时间

        # Base64URL 编码 Header 和 Payload
        header_encoded = self._base64url_encode(
            json.dumps(header, separators=(',', ':')).encode('utf-8')
        )
        payload_encoded = self._base64url_encode(
            json.dumps(payload, separators=(',', ':')).encode('utf-8')
        )

        # 创建签名输入
        signing_input = f"{header_encoded}.{payload_encoded}".encode('utf-8')

        # 计算签名（HS256 = HMAC-SHA256）
        if self.algorithm == "HS256":
            signature = hmac.new(
                self.secret_key.encode('utf-8'),
                signing_input,
                hashlib.sha256
            ).digest()
        else:
            raise ValueError(f"不支持的算法: {self.algorithm}")

        signature_encoded = self._base64url_encode(signature)

        # 组合 JWT: header.payload.signature
        return f"{header_encoded}.{payload_encoded}.{signature_encoded}"

    def verify_token_manual(self, token: str) -> dict:
        """
        手动实现 JWT 验证（用于学习原理）

        参数:
            token: JWT 字符串

        返回:
            解码后的 payload 字典

        异常:
            ValueError: 验证失败时抛出
        """
        parts = token.split('.')
        if len(parts) != 3:
            raise ValueError("JWT 格式错误：应包含三个部分")

        header_encoded, payload_encoded, signature_encoded = parts

        # 重新计算签名
        signing_input = f"{header_encoded}.{payload_encoded}".encode('utf-8')
        if self.algorithm == "HS256":
            expected_signature = hmac.new(
                self.secret_key.encode('utf-8'),
                signing_input,
                hashlib.sha256
            ).digest()
        else:
            raise ValueError(f"不支持的算法: {self.algorithm}")

        # 验证签名（常数时间比较）
        actual_signature = self._base64url_decode(signature_encoded)
        if not hmac.compare_digest(expected_signature, actual_signature):
            raise ValueError("JWT 签名验证失败")

        # 解码 payload
        payload = json.loads(self._base64url_decode(payload_encoded))

        # 验证过期时间
        if "exp" in payload:
            if int(time.time()) > payload["exp"]:
                raise ValueError("JWT 已过期")

        return payload

    def generate_token(self, payload: dict, expires_in: int = 3600) -> str:
        """
        生成 JWT（优先使用 PyJWT 库）

        参数:
            payload: 载荷数据
            expires_in: 过期时间（秒）
        """
        if self.pyjwt_available:
            return self.jwt.encode(
                payload,
                self.secret_key,
                algorithm=self.algorithm
            )
        else:
            return self.generate_token_manual(payload, expires_in)

    def verify_token(self, token: str) -> dict:
        """
        验证 JWT 并返回 payload

        参数:
            token: JWT 字符串
        """
        if self.pyjwt_available:
            try:
                return self.jwt.decode(
                    token,
                    self.secret_key,
                    algorithms=[self.algorithm]
                )
            except self.jwt.ExpiredSignatureError:
                raise ValueError("JWT 已过期")
            except self.jwt.InvalidTokenError:
                raise ValueError("JWT 验证失败")
        else:
            return self.verify_token_manual(token)


def demo_jwt():
    """演示 JWT Token 的生成与验证"""
    print("\n" + "=" * 60)
    print("【第二部分：JWT Token 生成与验证演示】")
    print("=" * 60)

    # 生产环境密钥应从安全的密钥管理系统获取
    # 这里仅作演示
    secret_key = "my-super-secret-key-change-in-production-12345"
    jwt_mgr = JWTManager(secret_key)

    # 生成 Token
    print("\n1. 生成 JWT Token:")
    print("-" * 40)
    user_payload = {
        "sub": "user123",          # Subject: 用户唯一标识
        "name": "张三",             # 用户名
        "email": "zhangsan@example.com",  # 邮箱
        "role": "admin",           # 角色
        "dept": "IT部门"           # 部门
    }

    token = jwt_mgr.generate_token(user_payload, expires_in=3600)
    print(f"   载荷数据: {json.dumps(user_payload, ensure_ascii=False)}")
    print(f"   Token (前80字符): {token[:80]}...")
    print(f"   Token 长度: {len(token)} 字符")

    # 解析 Token 结构
    parts = token.split('.')
    print(f"\n   JWT 结构:")
    print(f"     Header (Base64URL): {parts[0][:50]}...")
    print(f"     Payload (Base64URL): {parts[1][:50]}...")
    print(f"     Signature (Base64URL): {parts[2][:50]}...")

    # 验证 Token
    print("\n2. 验证 JWT Token:")
    print("-" * 40)
    try:
        decoded = jwt_mgr.verify_token(token)
        print(f"   ✅ 验证成功")
        print(f"   用户ID: {decoded.get('sub')}")
        print(f"   用户名: {decoded.get('name')}")
        print(f"   角色: {decoded.get('role')}")
        print(f"   签发时间: {datetime.fromtimestamp(decoded['iat'])}")
        print(f"   过期时间: {datetime.fromtimestamp(decoded['exp'])}")
    except ValueError as e:
        print(f"   ❌ 验证失败: {e}")

    # 验证被篡改的 Token
    print("\n3. 测试被篡改的 Token:")
    print("-" * 40)
    tampered_token = token[:-5] + "AAAAA"  # 篡改签名
    try:
        jwt_mgr.verify_token(tampered_token)
        print("   ❌ 篡改验证通过（不应发生！）")
    except ValueError as e:
        print(f"   ✅ 篡改检测成功: {e}")

    print("\n💡 JWT 安全提示:")
    print("   - 始终验证签名，防止篡改")
    print("   - 设置合理的过期时间")
    print("   - 不要在 JWT 中存储敏感信息（Payload只是Base64编码，不是加密）")
    print("   - 使用 HTTPS 传输，防止令牌泄露")
    print("   - 考虑使用 Refresh Token 机制")


# ============================================================
# 第三部分：TOTP 基于时间的动态口令
# ============================================================

class TOTPAuthenticator:
    """
    TOTP (Time-based One-Time Password) 动态口令生成器
    基于 RFC 6238 标准实现，兼容 Google Authenticator 等应用
    """

    def __init__(self, secret: Optional[str] = None, digits: int = 6,
                 period: int = 30, algorithm: str = "sha1"):
        """
        初始化 TOTP 认证器

        参数:
            secret: Base32 编码的密钥，为None则自动生成
            digits: 验证码位数，默认6位
            period: 验证码有效期（秒），默认30秒
            algorithm: HMAC算法，默认SHA1（兼容Google Authenticator）
        """
        self.digits = digits
        self.period = period
        self.algorithm = algorithm

        if secret:
            self.secret = secret.upper().replace(' ', '')
        else:
            # 生成随机密钥（160位 = 20字节，对应32个Base32字符）
            random_bytes = secrets.token_bytes(20)
            self.secret = self._base32_encode(random_bytes)

    @staticmethod
    def _base32_encode(data: bytes) -> str:
        """Base32 编码（用于密钥存储和传输）"""
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
        bits = ''.join(format(byte, '08b') for byte in data)
        # 按5位分组
        chunks = [bits[i:i+5] for i in range(0, len(bits) - 4, 5)]
        # 处理最后不足5位的情况
        if len(bits) % 5 != 0:
            last_chunk = bits[-(len(bits) % 5):].ljust(5, '0')
            chunks.append(last_chunk)
        result = ''.join(alphabet[int(chunk, 2)] for chunk in chunks)
        # 添加填充
        padding = (8 - len(result) % 8) % 8
        return result + '=' * padding

    @staticmethod
    def _base32_decode(data: str) -> bytes:
        """Base32 解码"""
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
        data = data.upper().rstrip('=')
        bits = ''
        for char in data:
            if char in alphabet:
                bits += format(alphabet.index(char), '05b')
        # 按8位分组
        result_bytes = bytearray()
        for i in range(0, len(bits) - 7, 8):
            result_bytes.append(int(bits[i:i+8], 2))
        return bytes(result_bytes)

    def _get_hmac(self, key: bytes, counter: int) -> bytes:
        """计算 HMAC"""
        # 将计数器转为8字节大端序
        counter_bytes = struct.pack('>Q', counter)
        # 根据算法选择哈希函数
        hash_func = getattr(hashlib, self.algorithm)
        return hmac.new(key, counter_bytes, hash_func).digest()

    def _dynamic_truncation(self, hmac_result: bytes) -> int:
        """
        动态截断（Dynamic Truncation）
        从 HMAC 结果中提取一个4字节的整数
        """
        # 取最后一个字节的低4位作为偏移量
        offset = hmac_result[-1] & 0x0F
        # 从偏移位置取4字节
        binary_code = (
            ((hmac_result[offset] & 0x7F) << 24) |  # 最高位清零（符号位）
            ((hmac_result[offset + 1] & 0xFF) << 16) |
            ((hmac_result[offset + 2] & 0xFF) << 8) |
            (hmac_result[offset + 3] & 0xFF)
        )
        return binary_code

    def generate(self, timestamp: Optional[int] = None) -> str:
        """
        生成当前时间步的验证码

        参数:
            timestamp: Unix 时间戳，为None则使用当前时间

        返回:
            数字验证码字符串
        """
        if timestamp is None:
            timestamp = int(time.time())

        # 计算时间步长计数器
        counter = timestamp // self.period

        # 解码密钥
        key = self._base32_decode(self.secret)

        # 计算 HMAC
        hmac_result = self._get_hmac(key, counter)

        # 动态截断
        binary_code = self._dynamic_truncation(hmac_result)

        # 取模得到指定位数的验证码
        otp = binary_code % (10 ** self.digits)

        # 补齐前导零并返回
        return str(otp).zfill(self.digits)

    def verify(self, code: str, timestamp: Optional[int] = None,
               window: int = 1) -> bool:
        """
        验证验证码

        参数:
            code: 用户输入的验证码
            timestamp: 当前时间戳
            window: 允许的时间窗口（前后各window个时间步）

        返回:
            True 表示验证通过
        """
        if timestamp is None:
            timestamp = int(time.time())

        # 检查时间窗口内的所有可能值
        # window=1 表示检查当前、前一个、后一个时间步（共3个）
        for i in range(-window, window + 1):
            current_time = timestamp + i * self.period
            expected_code = self.generate(current_time)
            if hmac.compare_digest(code, expected_code):
                return True

        return False

    def get_provisioning_uri(self, account_name: str, issuer: str = "IAM Demo") -> str:
        """
        生成配置URI（用于生成二维码，可被Google Authenticator扫描）

        参数:
            account_name: 账户名（通常是邮箱）
            issuer: 发行者名称

        返回:
            otpauth:// 格式的 URI
        """
        import urllib.parse
        params = {
            'secret': self.secret,
            'issuer': issuer,
            'algorithm': self.algorithm.upper(),
            'digits': self.digits,
            'period': self.period
        }
        return f"otpauth://totp/{urllib.parse.quote(issuer)}:{urllib.parse.quote(account_name)}?" + \
               urllib.parse.urlencode(params)


def demo_totp():
    """演示 TOTP 动态口令"""
    print("\n" + "=" * 60)
    print("【第三部分：TOTP 基于时间的动态口令演示】")
    print("=" * 60)

    # 创建 TOTP 认证器（自动生成密钥）
    totp = TOTPAuthenticator(digits=6, period=30)

    print("\n1. TOTP 配置信息:")
    print("-" * 40)
    print(f"   密钥 (Base32): {totp.secret}")
    print(f"   验证码位数: {totp.digits}")
    print(f"   有效期: {totp.period} 秒")
    print(f"   算法: {totp.algorithm.upper()}")

    # 生成配置 URI（可用于生成二维码）
    uri = totp.get_provisioning_uri("user@example.com", "我的系统")
    print(f"   配置URI: {uri}")
    print(f"   (可将此URI生成二维码，用Google Authenticator扫描)")

    # 生成当前验证码
    print("\n2. 当前验证码:")
    print("-" * 40)
    current_code = totp.generate()
    current_time = datetime.now()
    print(f"   当前时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   当前验证码: {current_code[:3]} {current_code[3:]}")

    # 计算剩余时间
    time_remaining = totp.period - (int(time.time()) % totp.period)
    print(f"   剩余有效时间: {time_remaining} 秒")

    # 验证正确的验证码
    print("\n3. 验证码验证:")
    print("-" * 40)
    is_valid = totp.verify(current_code)
    print(f"   验证正确验证码: {'✅ 通过' if is_valid else '❌ 失败'}")

    # 验证错误的验证码
    is_valid = totp.verify("000000")
    print(f"   验证错误验证码(000000): {'✅ 通过' if is_valid else '❌ 失败'}")

    # 模拟时间偏移验证（窗口=1，即前后30秒内有效）
    past_code = totp.generate(int(time.time()) - 30)
    is_valid = totp.verify(past_code, window=1)
    print(f"   验证前一时间步验证码(window=1): {'✅ 通过' if is_valid else '❌ 失败'}")

    print("\n💡 TOTP 安全提示:")
    print("   - 密钥必须安全存储（泄露则验证码失效）")
    print("   - 设置合理的时间窗口（通常1-2个时间步）")
    print("   - 验证码只能使用一次，防止重放攻击")
    print("   - 建议配合账号锁定机制防止暴力破解")
    print("   - TOTP 无法防御钓鱼攻击（U2F/WebAuthn更安全）")


# ============================================================
# 第四部分：OAuth 2.0 授权码流程模拟
# ============================================================

class OAuth2Server:
    """
    OAuth 2.0 授权服务器模拟
    演示授权码模式（Authorization Code Grant）的完整流程
    """

    def __init__(self):
        """初始化授权服务器"""
        # 存储注册的客户端
        self.clients: Dict[str, dict] = {}
        # 存储授权码（一次性使用）
        self.authorization_codes: Dict[str, dict] = {}
        # 存储访问令牌
        self.access_tokens: Dict[str, dict] = {}
        # 存储用户信息
        self.users: Dict[str, dict] = {}
        # 存储刷新令牌
        self.refresh_tokens: Dict[str, dict] = {}

    def register_client(self, client_id: str, client_secret: str,
                        redirect_uri: str, name: str) -> None:
        """
        注册客户端应用

        参数:
            client_id: 客户端ID
            client_secret: 客户端密钥
            redirect_uri: 重定向URI
            name: 客户端名称
        """
        self.clients[client_id] = {
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "name": name
        }
        print(f"[授权服务器] 注册客户端: {name} (ID: {client_id})")

    def register_user(self, username: str, password: str, name: str, email: str) -> None:
        """注册用户"""
        self.users[username] = {
            "username": username,
            "password": password,  # 演示用明文，实际应用应使用哈希
            "name": name,
            "email": email
        }
        print(f"[授权服务器] 注册用户: {name} ({username})")

    def authorize(self, client_id: str, redirect_uri: str, scope: str,
                  username: str, password: str) -> Tuple[str, str]:
        """
        授权端点：用户认证并授权后，生成授权码

        参数:
            client_id: 客户端ID
            redirect_uri: 重定向URI
            scope: 请求的权限范围
            username: 用户名
            password: 密码

        返回:
            (重定向URI, 授权码)

        异常:
            ValueError: 认证或授权失败时抛出
        """
        print(f"\n  [授权端点] 收到授权请求")
        print(f"    客户端: {client_id}")
        print(f"    权限范围: {scope}")

        # 1. 验证客户端
        if client_id not in self.clients:
            raise ValueError("无效的客户端ID")

        client = self.clients[client_id]
        if client["redirect_uri"] != redirect_uri:
            raise ValueError("重定向URI不匹配")

        # 2. 用户认证
        if username not in self.users:
            raise ValueError("用户不存在")
        user = self.users[username]
        if user["password"] != password:
            raise ValueError("密码错误")

        print(f"    用户认证通过: {user['name']}")
        print(f"    (实际应用中此处会显示授权确认页面)")

        # 3. 生成授权码（一次性使用，有效期通常为10分钟）
        authorization_code = secrets.token_urlsafe(32)
        self.authorization_codes[authorization_code] = {
            "client_id": client_id,
            "username": username,
            "scope": scope,
            "redirect_uri": redirect_uri,
            "expires_at": time.time() + 600,  # 10分钟有效期
            "used": False
        }

        print(f"    生成授权码: {authorization_code[:20]}...")
        print(f"    授权码有效期: 10分钟")

        return redirect_uri, authorization_code

    def token(self, grant_type: str, code: str, redirect_uri: str,
              client_id: str, client_secret: str) -> dict:
        """
        令牌端点：用授权码换取访问令牌

        参数:
            grant_type: 授权类型（authorization_code）
            code: 授权码
            redirect_uri: 重定向URI
            client_id: 客户端ID
            client_secret: 客户端密钥

        返回:
            包含 access_token 等信息的字典
        """
        print(f"\n  [令牌端点] 收到令牌请求")
        print(f"    授权类型: {grant_type}")

        # 1. 验证客户端凭证
        if client_id not in self.clients:
            raise ValueError("无效的客户端ID")
        client = self.clients[client_id]
        if client["client_secret"] != client_secret:
            raise ValueError("客户端密钥错误")

        # 2. 验证授权类型
        if grant_type != "authorization_code":
            raise ValueError("不支持的授权类型")

        # 3. 验证授权码
        if code not in self.authorization_codes:
            raise ValueError("无效的授权码")

        code_data = self.authorization_codes[code]

        # 检查是否已使用（防止重放）
        if code_data["used"]:
            # 安全做法：如果授权码被重复使用，应该撤销相关令牌
            raise ValueError("授权码已使用")

        # 检查过期
        if time.time() > code_data["expires_at"]:
            del self.authorization_codes[code]
            raise ValueError("授权码已过期")

        # 检查重定向URI
        if code_data["redirect_uri"] != redirect_uri:
            raise ValueError("重定向URI不匹配")

        # 检查客户端ID
        if code_data["client_id"] != client_id:
            raise ValueError("客户端不匹配")

        # 标记授权码为已使用
        code_data["used"] = True

        # 4. 生成访问令牌
        access_token = secrets.token_urlsafe(32)
        refresh_token = secrets.token_urlsafe(32)
        expires_in = 3600  # 1小时

        self.access_tokens[access_token] = {
            "username": code_data["username"],
            "client_id": client_id,
            "scope": code_data["scope"],
            "expires_at": time.time() + expires_in,
            "refresh_token": refresh_token
        }

        self.refresh_tokens[refresh_token] = {
            "username": code_data["username"],
            "client_id": client_id,
            "scope": code_data["scope"],
            "access_token": access_token
        }

        print(f"    生成访问令牌: {access_token[:20]}...")
        print(f"    生成刷新令牌: {refresh_token[:20]}...")
        print(f"    令牌有效期: {expires_in} 秒")

        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": expires_in,
            "refresh_token": refresh_token,
            "scope": code_data["scope"]
        }

    def validate_token(self, access_token: str) -> dict:
        """
        资源服务器验证访问令牌

        参数:
            access_token: 访问令牌

        返回:
            令牌对应的用户信息
        """
        if access_token not in self.access_tokens:
            raise ValueError("无效的访问令牌")

        token_data = self.access_tokens[access_token]

        if time.time() > token_data["expires_at"]:
            del self.access_tokens[access_token]
            raise ValueError("访问令牌已过期")

        # 返回用户信息（不包含敏感数据）
        user = self.users[token_data["username"]]
        return {
            "username": user["username"],
            "name": user["name"],
            "email": user["email"],
            "scope": token_data["scope"]
        }


class OAuth2Client:
    """
    OAuth 2.0 客户端应用模拟
    """

    def __init__(self, client_id: str, client_secret: str,
                 redirect_uri: str, auth_server: OAuth2Server):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.auth_server = auth_server
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None

    def get_authorization_url(self, scope: str) -> str:
        """
        生成授权URL（实际应用中会重定向用户浏览器）
        """
        # 实际应用中还需要 state 参数防止 CSRF
        state = secrets.token_urlsafe(16)
        return f"https://auth.example.com/authorize?" \
               f"response_type=code" \
               f"&client_id={self.client_id}" \
               f"&redirect_uri={self.redirect_uri}" \
               f"&scope={scope}" \
               f"&state={state}"

    def handle_authorization_callback(self, code: str) -> dict:
        """
        处理授权回调，用授权码换取令牌
        """
        return self.auth_server.token(
            grant_type="authorization_code",
            code=code,
            redirect_uri=self.redirect_uri,
            client_id=self.client_id,
            client_secret=self.client_secret
        )

    def get_user_info(self) -> dict:
        """使用访问令牌获取用户信息"""
        if not self.access_token:
            raise ValueError("尚未获取访问令牌")
        return self.auth_server.validate_token(self.access_token)


def demo_oauth2():
    """演示 OAuth 2.0 授权码流程"""
    print("\n" + "=" * 60)
    print("【第四部分：OAuth 2.0 授权码流程模拟】")
    print("=" * 60)

    # 1. 初始化授权服务器
    print("\n步骤0：初始化系统")
    print("-" * 40)
    auth_server = OAuth2Server()

    # 注册用户
    auth_server.register_user(
        username="zhangsan",
        password="password123",
        name="张三",
        email="zhangsan@example.com"
    )

    # 注册客户端应用
    auth_server.register_client(
        client_id="my-app-client-id",
        client_secret="my-app-client-secret-12345",
        redirect_uri="https://myapp.example.com/callback",
        name="我的应用"
    )

    # 创建客户端
    client = OAuth2Client(
        client_id="my-app-client-id",
        client_secret="my-app-client-secret-12345",
        redirect_uri="https://myapp.example.com/callback",
        auth_server=auth_server
    )

    # 2. 用户访问客户端应用，点击登录
    print("\n步骤1：用户访问应用，点击'用XX账号登录'")
    print("-" * 40)
    auth_url = client.get_authorization_url(scope="read profile")
    print(f"   生成授权URL:")
    print(f"   {auth_url[:80]}...")
    print("   (用户浏览器重定向到授权服务器)")

    # 3. 用户在授权服务器登录并授权
    print("\n步骤2：用户在授权服务器登录并授权")
    print("-" * 40)
    print("   用户输入用户名密码...")

    try:
        redirect_uri, auth_code = auth_server.authorize(
            client_id="my-app-client-id",
            redirect_uri="https://myapp.example.com/callback",
            scope="read profile",
            username="zhangsan",
            password="password123"
        )
        print(f"   授权成功！")
        print(f"   重定向到: {redirect_uri}")
        print(f"   授权码: {auth_code[:30]}...")
    except ValueError as e:
        print(f"   授权失败: {e}")
        return

    # 4. 客户端用授权码换取令牌
    print("\n步骤3：客户端用授权码换取访问令牌")
    print("-" * 40)
    print("   (后端服务器向授权服务器发起请求，不经过浏览器)")

    try:
        token_response = client.handle_authorization_callback(auth_code)
        client.access_token = token_response["access_token"]
        client.refresh_token = token_response["refresh_token"]

        print(f"   令牌获取成功！")
        print(f"   Access Token: {token_response['access_token'][:30]}...")
        print(f"   Refresh Token: {token_response['refresh_token'][:30]}...")
        print(f"   有效期: {token_response['expires_in']} 秒")
        print(f"   权限范围: {token_response['scope']}")
    except ValueError as e:
        print(f"   令牌获取失败: {e}")
        return

    # 5. 客户端使用访问令牌访问资源
    print("\n步骤4：使用访问令牌访问受保护资源")
    print("-" * 40)
    try:
        user_info = client.get_user_info()
        print(f"   ✅ 资源访问成功")
        print(f"   用户名: {user_info['name']}")
        print(f"   邮箱: {user_info['email']}")
        print(f"   权限: {user_info['scope']}")
    except ValueError as e:
        print(f"   ❌ 资源访问失败: {e}")

    # 6. 测试重复使用授权码
    print("\n步骤5：测试授权码只能使用一次")
    print("-" * 40)
    try:
        client.handle_authorization_callback(auth_code)
        print("   ❌ 重复使用授权码成功（不安全！）")
    except ValueError as e:
        print(f"   ✅ 重复使用授权码被拒绝: {e}")

    print("\n💡 OAuth 2.0 安全提示:")
    print("   - 始终使用授权码模式，避免使用隐式模式")
    print("   - 使用 state 参数防止 CSRF 攻击")
    print("   - 授权码应一次性使用，短期有效")
    print("   - 使用 PKCE 增强移动端应用安全")
    print("   - 访问令牌应设置较短的有效期")
    print("   - 使用 HTTPS 防止令牌在传输中被窃取")


# ============================================================
# 第五部分：RBAC 基于角色的访问控制
# ============================================================

class RBACManager:
    """
    RBAC (Role-Based Access Control) 权限管理器
    实现基于角色的访问控制，支持角色继承和职责分离
    """

    def __init__(self):
        """初始化 RBAC 系统"""
        # 用户列表: {username: {name, email, ...}}
        self.users: Dict[str, dict] = {}
        # 角色列表: {role_name: {description, permissions: set, inherits: set}}
        self.roles: Dict[str, dict] = {}
        # 权限列表: {permission_name: description}
        self.permissions: Dict[str, str] = {}
        # 用户-角色分配: {username: set(role_names)}
        self.user_roles: Dict[str, Set[str]] = {}
        # 职责分离互斥角色对: [(role_a, role_b), ...]
        self.sod_pairs: List[Tuple[str, str]] = []

    # ---------- 权限管理 ----------
    def add_permission(self, name: str, description: str) -> None:
        """添加权限"""
        self.permissions[name] = description

    # ---------- 角色管理 ----------
    def add_role(self, name: str, description: str,
                 permissions: Optional[List[str]] = None,
                 inherits: Optional[List[str]] = None) -> None:
        """
        添加角色

        参数:
            name: 角色名称
            description: 角色描述
            permissions: 直接拥有的权限列表
            inherits: 继承的角色列表
        """
        if name in self.roles:
            raise ValueError(f"角色 '{name}' 已存在")

        # 验证权限都存在
        if permissions:
            for perm in permissions:
                if perm not in self.permissions:
                    raise ValueError(f"权限 '{perm}' 不存在")

        # 验证继承的角色都存在
        if inherits:
            for role in inherits:
                if role not in self.roles:
                    raise ValueError(f"继承角色 '{role}' 不存在")

        self.roles[name] = {
            "description": description,
            "permissions": set(permissions or []),
            "inherits": set(inherits or [])
        }

    def get_role_permissions(self, role_name: str) -> Set[str]:
        """
        获取角色的所有权限（包括继承的权限）
        使用递归收集所有继承的权限
        """
        if role_name not in self.roles:
            return set()

        role = self.roles[role_name]
        all_perms = set(role["permissions"])

        # 递归获取继承角色的权限
        for inherited_role in role["inherits"]:
            all_perms.update(self.get_role_permissions(inherited_role))

        return all_perms

    # ---------- 用户管理 ----------
    def add_user(self, username: str, name: str, email: str) -> None:
        """添加用户"""
        if username in self.users:
            raise ValueError(f"用户 '{username}' 已存在")
        self.users[username] = {"name": name, "email": email}
        self.user_roles[username] = set()

    def assign_role(self, username: str, role_name: str) -> None:
        """
        为用户分配角色

        会进行职责分离冲突检测
        """
        if username not in self.users:
            raise ValueError(f"用户 '{username}' 不存在")
        if role_name not in self.roles:
            raise ValueError(f"角色 '{role_name}' 不存在")

        # 检查职责分离冲突
        new_roles = self.user_roles[username] | {role_name}
        conflict = self._check_sod_conflict(new_roles)
        if conflict:
            raise ValueError(
                f"职责分离冲突：角色 '{conflict[0]}' 和 '{conflict[1]}' 互斥"
            )

        self.user_roles[username].add(role_name)

    def remove_role(self, username: str, role_name: str) -> None:
        """移除用户角色"""
        if username in self.user_roles and role_name in self.user_roles[username]:
            self.user_roles[username].remove(role_name)

    def get_user_roles(self, username: str) -> Set[str]:
        """获取用户的所有角色"""
        return self.user_roles.get(username, set())

    def get_user_permissions(self, username: str) -> Set[str]:
        """获取用户的所有权限（所有角色的权限之和）"""
        all_perms = set()
        for role in self.user_roles.get(username, set()):
            all_perms.update(self.get_role_permissions(role))
        return all_perms

    # ---------- 权限检查 ----------
    def check_permission(self, username: str, permission: str) -> bool:
        """
        检查用户是否拥有指定权限

        参数:
            username: 用户名
            permission: 权限名称

        返回:
            True 表示有权限
        """
        user_perms = self.get_user_permissions(username)
        return permission in user_perms

    def check_role(self, username: str, role_name: str) -> bool:
        """检查用户是否拥有指定角色"""
        return role_name in self.user_roles.get(username, set())

    # ---------- 职责分离 ----------
    def add_sod_pair(self, role_a: str, role_b: str) -> None:
        """
        添加互斥角色对（职责分离）

        同一个用户不能同时拥有这两个角色
        """
        if role_a not in self.roles or role_b not in self.roles:
            raise ValueError("角色不存在")
        self.sod_pairs.append((role_a, role_b))

    def _check_sod_conflict(self, roles: Set[str]) -> Optional[Tuple[str, str]]:
        """
        检查角色集合是否存在职责分离冲突

        返回:
            冲突的角色对，无冲突返回None
        """
        for role_a, role_b in self.sod_pairs:
            if role_a in roles and role_b in roles:
                return (role_a, role_b)
        return None

    # ---------- 审计 ----------
    def get_user_permission_report(self, username: str) -> str:
        """生成用户权限报告"""
        if username not in self.users:
            return f"用户 '{username}' 不存在"

        user = self.users[username]
        roles = self.get_user_roles(username)
        permissions = self.get_user_permissions(username)

        report = f"用户权限报告 - {user['name']} ({username})\n"
        report += "=" * 50 + "\n"
        report += f"邮箱: {user['email']}\n"
        report += f"角色 ({len(roles)}):\n"
        for role in sorted(roles):
            desc = self.roles[role]["description"]
            report += f"  - {role}: {desc}\n"
        report += f"\n权限 ({len(permissions)}):\n"
        for perm in sorted(permissions):
            desc = self.permissions[perm]
            report += f"  - {perm}: {desc}\n"

        return report


def demo_rbac():
    """演示 RBAC 基于角色的访问控制"""
    print("\n" + "=" * 60)
    print("【第五部分：RBAC 基于角色的访问控制演示】")
    print("=" * 60)

    # 1. 初始化 RBAC 系统
    rbac = RBACManager()

    # 2. 定义权限
    print("\n1. 定义系统权限:")
    print("-" * 40)
    permissions = [
        ("user:read", "查看用户信息"),
        ("user:create", "创建用户"),
        ("user:update", "修改用户"),
        ("user:delete", "删除用户"),
        ("order:read", "查看订单"),
        ("order:create", "创建订单"),
        ("order:approve", "审批订单"),
        ("finance:read", "查看财务报表"),
        ("finance:payment", "执行付款"),
        ("system:config", "系统配置"),
        ("system:audit", "审计日志"),
    ]
    for name, desc in permissions:
        rbac.add_permission(name, desc)
        print(f"   + {name}: {desc}")

    # 3. 定义角色（带继承关系）
    print("\n2. 定义角色与权限分配:")
    print("-" * 40)

    # 普通员工
    rbac.add_role(
        name="employee",
        description="普通员工",
        permissions=["user:read", "order:read", "order:create"]
    )
    print("   + employee (普通员工): 基础权限")

    # 部门经理（继承普通员工）
    rbac.add_role(
        name="manager",
        description="部门经理",
        permissions=["order:approve"],
        inherits=["employee"]
    )
    print("   + manager (部门经理): 继承employee + 订单审批")

    # HR专员
    rbac.add_role(
        name="hr_specialist",
        description="HR专员",
        permissions=["user:read", "user:create", "user:update"]
    )
    print("   + hr_specialist (HR专员): 用户管理")

    # 财务人员
    rbac.add_role(
        name="finance_staff",
        description="财务人员",
        permissions=["finance:read", "order:read"]
    )
    print("   + finance_staff (财务人员): 财务查看")

    # 财务主管（继承财务人员）
    rbac.add_role(
        name="finance_manager",
        description="财务主管",
        permissions=["finance:payment"],
        inherits=["finance_staff"]
    )
    print("   + finance_manager (财务主管): 继承finance_staff + 付款权限")

    # 系统管理员
    rbac.add_role(
        name="system_admin",
        description="系统管理员",
        permissions=["system:config", "user:read", "user:create",
                     "user:update", "user:delete"]
    )
    print("   + system_admin (系统管理员): 系统配置和用户管理")

    # 审计员
    rbac.add_role(
        name="auditor",
        description="审计员",
        permissions=["system:audit", "user:read", "order:read", "finance:read"]
    )
    print("   + auditor (审计员): 审计和只读权限")

    # 4. 设置职责分离
    print("\n3. 设置职责分离 (SoD):")
    print("-" * 40)
    rbac.add_sod_pair("finance_staff", "finance_manager")
    rbac.add_sod_pair("hr_specialist", "auditor")
    rbac.add_sod_pair("system_admin", "auditor")
    print("   ✗ finance_staff ↔ finance_manager (财务人员和财务主管互斥)")
    print("   ✗ hr_specialist ↔ auditor (HR和审计员互斥)")
    print("   ✗ system_admin ↔ auditor (管理员和审计员互斥)")

    # 5. 创建用户并分配角色
    print("\n4. 创建用户并分配角色:")
    print("-" * 40)

    # 普通员工
    rbac.add_user("zhangsan", "张三", "zhangsan@example.com")
    rbac.assign_role("zhangsan", "employee")
    print("   张三 → employee (普通员工)")

    # 部门经理
    rbac.add_user("lisi", "李四", "lisi@example.com")
    rbac.assign_role("lisi", "manager")
    print("   李四 → manager (部门经理)")

    # HR专员
    rbac.add_user("wangwu", "王五", "wangwu@example.com")
    rbac.assign_role("wangwu", "hr_specialist")
    print("   王五 → hr_specialist (HR专员)")

    # 财务主管
    rbac.add_user("zhaoliu", "赵六", "zhaoliu@example.com")
    rbac.assign_role("zhaoliu", "finance_manager")
    print("   赵六 → finance_manager (财务主管)")

    # 系统管理员
    rbac.add_user("admin", "系统管理员", "admin@example.com")
    rbac.assign_role("admin", "system_admin")
    print("   admin → system_admin (系统管理员)")

    # 审计员
    rbac.add_user("auditor1", "审计员", "auditor@example.com")
    rbac.assign_role("auditor1", "auditor")
    print("   审计员 → auditor (审计员)")

    # 6. 权限检查演示
    print("\n5. 权限检查演示:")
    print("-" * 40)

    test_cases = [
        ("zhangsan", "order:create", "张三创建订单"),
        ("zhangsan", "order:approve", "张三审批订单"),
        ("lisi", "order:approve", "李四审批订单"),
        ("lisi", "user:create", "李四创建用户"),
        ("wangwu", "user:create", "王五创建用户"),
        ("wangwu", "finance:read", "王五查看财务"),
        ("zhaoliu", "finance:payment", "赵六执行付款"),
        ("zhaoliu", "order:approve", "赵六审批订单"),
        ("admin", "system:config", "管理员系统配置"),
        ("auditor1", "system:audit", "审计员查看审计"),
        ("auditor1", "user:delete", "审计员删除用户"),
    ]

    for username, permission, desc in test_cases:
        has_perm = rbac.check_permission(username, permission)
        status = "✅ 允许" if has_perm else "❌ 拒绝"
        print(f"   {status} | {desc} ({permission})")

    # 7. 职责分离检测
    print("\n6. 职责分离检测:")
    print("-" * 40)
    try:
        rbac.assign_role("wangwu", "auditor")
        print("   ❌ HR专员分配审计员角色成功（不应发生！）")
    except ValueError as e:
        print(f"   ✅ 职责分离检测生效: {e}")

    # 8. 用户权限报告
    print("\n7. 用户权限报告示例:")
    print("-" * 40)
    print(rbac.get_user_permission_report("lisi"))

    print("\n💡 RBAC 实践提示:")
    print("   - 角色设计应基于岗位职责，而非个人")
    print("   - 使用角色继承减少重复定义")
    print("   - 实施职责分离防止舞弊")
    print("   - 定期审查角色权限，避免角色爆炸")
    print("   - 权限命名要规范，便于理解和管理")
    print("   - 对于复杂场景，可考虑 ABAC 或 RBAC+ABAC 混合模式")


# ============================================================
# 主程序入口
# ============================================================

def main():
    """主函数：依次运行所有演示"""
    print("\n" + "=" * 60)
    print("  身份认证与访问管理（IAM）演示代码")
    print("  Identity and Access Management Demo")
    print("=" * 60)
    print()

    # 运行所有演示
    demo_password_hashing()
    demo_jwt()
    demo_totp()
    demo_oauth2()
    demo_rbac()

    print("\n" + "=" * 60)
    print("  演示完成！")
    print("=" * 60)
    print()
    print("📚 学习建议:")
    print("  1. 仔细阅读每个模块的代码注释，理解原理")
    print("  2. 修改参数（如成本因子、过期时间）观察效果")
    print("  3. 尝试添加新功能（如刷新令牌、角色挖掘）")
    print("  4. 思考安全边界和潜在的攻击面")
    print("  5. 生产环境请使用成熟框架，不要自行造轮子")
    print()


if __name__ == "__main__":
    main()
