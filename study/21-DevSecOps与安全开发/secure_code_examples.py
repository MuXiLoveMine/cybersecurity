#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全编码模式示例库

本模块展示常见安全漏洞的安全编码模式，包括：
  - 输入验证
  - 输出编码
  - 参数化查询
  - 安全密码哈希
  - 安全文件操作
  - 安全随机数生成
  - 错误处理（不泄露信息）

每个示例包含不安全实现和安全实现的对比说明。
"""

import hashlib
import hmac
import json
import logging
import os
import re
import secrets
import sqlite3
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# 配置日志（不泄露敏感信息到日志中）
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# =============================================================================
# 1. 输入验证 (Input Validation)
# =============================================================================

class InputValidator:
    """安全输入验证工具集"""

    # 白名单字符集
    USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_\u4e00-\u9fa5]{3,32}$")
    EMAIL_PATTERN = re.compile(
        r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    )
    PHONE_PATTERN = re.compile(r"^1[3-9]\d{9}$")
    ID_CARD_PATTERN = re.compile(
        r"^[1-9]\d{5}(?:19|20)\d{2}(?:0[1-9]|1[0-2])"
        r"(?:0[1-9]|[12]\d|3[01])\d{3}[\dXx]$"
    )
    URL_PATTERN = re.compile(
        r"^https?://[a-zA-Z0-9\-._~:/?#\[\]@!$&'()*+,;=]+$"
    )

    # 允许的协议（防止javascript:/data:等）
    ALLOWED_URL_SCHEMES = {"http", "https"}

    # 最大输入长度
    MAX_INPUT_LENGTH = 4096
    MAX_FILENAME_LENGTH = 255

    @classmethod
    def validate_username(cls, username: str) -> Tuple[bool, str]:
        """验证用户名"""
        if not username:
            return False, "用户名不能为空"
        if len(username) > 32:
            return False, "用户名长度不能超过32个字符"
        if not cls.USERNAME_PATTERN.match(username):
            return False, "用户名只能包含字母、数字、下划线和中文"
        return True, "验证通过"

    @classmethod
    def validate_email(cls, email: str) -> Tuple[bool, str]:
        """验证邮箱地址"""
        if not email or len(email) > 254:
            return False, "邮箱地址无效"
        if not cls.EMAIL_PATTERN.match(email):
            return False, "邮箱格式不正确"
        return True, "验证通过"

    @classmethod
    def validate_phone(cls, phone: str) -> Tuple[bool, str]:
        """验证手机号"""
        if not phone:
            return False, "手机号不能为空"
        if not cls.PHONE_PATTERN.match(phone):
            return False, "手机号格式不正确"
        return True, "验证通过"

    @classmethod
    def validate_integer(cls, value: str, min_val: int = 0,
                         max_val: int = 2**31 - 1) -> Tuple[bool, str, Optional[int]]:
        """验证整数输入"""
        try:
            num = int(value)
        except (ValueError, TypeError):
            return False, "请输入有效的整数", None
        if num < min_val or num > max_val:
            return False, f"数值必须在 {min_val} 到 {max_val} 之间", None
        return True, "验证通过", num

    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """安全地清理文件名，防止路径遍历"""
        if not filename:
            raise ValueError("文件名不能为空")
        if len(filename) > cls.MAX_FILENAME_LENGTH:
            raise ValueError("文件名过长")
        # 移除路径分隔符和特殊字符
        filename = os.path.basename(filename)
        filename = re.sub(r"[^\w.\-]", "_", filename)
        # 防止隐藏文件
        if filename.startswith("."):
            filename = "_" + filename
        return filename

    @classmethod
    def validate_url(cls, url: str) -> Tuple[bool, str]:
        """验证URL（防止SSRF和XSS）"""
        if not url or len(url) > cls.MAX_INPUT_LENGTH:
            return False, "URL无效"
        if not cls.URL_PATTERN.match(url):
            return False, "URL格式不正确"
        # 检查协议
        scheme = url.split("://")[0].lower()
        if scheme not in cls.ALLOWED_URL_SCHEMES:
            return False, f"不允许的协议: {scheme}"
        return True, "验证通过"

    @classmethod
    def sanitize_html_input(cls, text: str) -> str:
        """清理HTML输入，移除危险标签"""
        if not text:
            return ""
        if len(text) > cls.MAX_INPUT_LENGTH:
            raise ValueError("输入过长")
        # 移除HTML标签
        clean = re.sub(r"<[^>]+>", "", text)
        # 移除事件处理器
        clean = re.sub(
            r"javascript:|on\w+\s*=|data:", "", clean, flags=re.IGNORECASE
        )
        return clean.strip()


# =============================================================================
# 2. 输出编码 (Output Encoding)
# =============================================================================

class OutputEncoder:
    """安全输出编码工具集"""

    @staticmethod
    def encode_html(text: str) -> str:
        """HTML编码，防止XSS"""
        if not text:
            return ""
        html_escape_map = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#x27;",
            "/": "&#x2F;",
        }
        return "".join(html_escape_map.get(c, c) for c in text)

    @staticmethod
    def encode_html_attribute(text: str) -> str:
        """HTML属性编码"""
        if not text:
            return ""
        encoded = []
        for char in text:
            if ord(char) < 128:
                encoded.append(
                    f"&#x{ord(char):x};" if not char.isalnum() else char
                )
            else:
                encoded.append(f"&#x{ord(char):x};")
        return "".join(encoded)

    @staticmethod
    def encode_javascript(text: str) -> str:
        """JavaScript编码，防止DOM XSS"""
        if not text:
            return ""
        js_escape_map = {
            "\\": "\\u005C",
            "'": "\\u0027",
            '"': "\\u0022",
            "<": "\\u003C",
            ">": "\\u003E",
            "&": "\\u0026",
            "=": "\\u003D",
            ";": "\\u003B",
            "\n": "\\u000A",
            "\r": "\\u000D",
            "/": "\\u002F",
        }
        return "".join(js_escape_map.get(c, c) for c in text)

    @staticmethod
    def encode_url(text: str) -> str:
        """URL编码"""
        from urllib.parse import quote
        return quote(text, safe="")

    @staticmethod
    def encode_sql_string(text: str) -> str:
        """SQL字符串转义（应优先使用参数化查询）"""
        return text.replace("'", "''")


# =============================================================================
# 3. 参数化查询 (Parameterized Queries)
# =============================================================================

class SecureDatabase:
    """安全数据库操作（使用参数化查询）"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now')),
                    role TEXT DEFAULT 'user'
                )
            """)
            conn.commit()

    # ---- 不安全示例 ----
    # def get_user_insecure(self, username):
    #     # 不安全：直接拼接SQL，存在SQL注入风险
    #     sql = f"SELECT * FROM users WHERE username = '{username}'"
    #     cursor = self.conn.execute(sql)
    #     return cursor.fetchone()

    def get_user(self, username: str) -> Optional[Dict]:
        """安全：使用参数化查询"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT id, username, email, role FROM users WHERE username = ?",
                (username,),
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def create_user(self, username: str, email: str,
                    password_hash: str, salt: str) -> int:
        """安全创建用户"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """INSERT INTO users (username, email, password_hash, salt)
                   VALUES (?, ?, ?, ?)""",
                (username, email, password_hash, salt),
            )
            conn.commit()
            return cursor.lastrowid

    def search_users(self, keyword: str, limit: int = 20) -> List[Dict]:
        """安全搜索用户"""
        # 验证输入
        valid, msg, limit_val = InputValidator.validate_integer(
            str(limit), 1, 100
        )
        if not valid:
            limit_val = 20

        # 安全的LIKE查询
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """SELECT id, username, email FROM users
                   WHERE username LIKE ? ESCAPE '\\'
                   LIMIT ?""",
                (f"%{keyword}%", limit_val),
            )
            return [dict(row) for row in cursor.fetchall()]

    def update_user_role(self, user_id: int, role: str) -> bool:
        """安全更新用户角色"""
        # 验证角色值（白名单）
        allowed_roles = {"user", "admin", "moderator", "readonly"}
        if role not in allowed_roles:
            raise ValueError(f"无效的角色: {role}")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "UPDATE users SET role = ? WHERE id = ?",
                (role, user_id),
            )
            conn.commit()
            return cursor.rowcount > 0


# =============================================================================
# 4. 安全密码哈希 (Secure Password Hashing)
# =============================================================================

class SecurePasswordHasher:
    """安全密码哈希（使用Argon2/PBKDF2/bcrypt）"""

    # Argon2参数
    ARGON2_TIME_COST = 3        # 迭代次数
    ARGON2_MEMORY_COST = 65536  # 64MB
    ARGON2_PARALLELISM = 4
    ARGON2_HASH_LEN = 32
    ARGON2_SALT_LEN = 16

    # PBKDF2参数
    PBKDF2_ITERATIONS = 600000
    PBKDF2_HASH_LEN = 32
    PBKDF2_SALT_LEN = 16

    @classmethod
    def hash_password_argon2(cls, password: str) -> str:
        """
        使用Argon2id哈希密码（推荐）

        Argon2是密码哈希竞赛的获胜者，设计用于抵抗
        GPU/ASIC攻击，支持时间-内存权衡。
        """
        try:
            from argon2 import PasswordHasher, Type
            ph = PasswordHasher(
                time_cost=cls.ARGON2_TIME_COST,
                memory_cost=cls.ARGON2_MEMORY_COST,
                parallelism=cls.ARGON2_PARALLELISM,
                hash_len=cls.ARGON2_HASH_LEN,
                salt_len=cls.ARGON2_SALT_LEN,
                type=Type.ID,
            )
            return ph.hash(password)
        except ImportError:
            # 如果argon2-cffi不可用，回退到PBKDF2
            return cls.hash_password_pbkdf2(password)

    @classmethod
    def verify_password_argon2(cls, hashed: str, password: str) -> bool:
        """验证Argon2哈希"""
        try:
            from argon2 import PasswordHasher, Type
            from argon2.exceptions import VerifyMismatchError
            ph = PasswordHasher(type=Type.ID)
            try:
                ph.verify(hashed, password)
                return True
            except VerifyMismatchError:
                return False
        except ImportError:
            return cls.verify_password_pbkdf2(hashed, password)

    @classmethod
    def hash_password_pbkdf2(cls, password: str) -> str:
        """
        使用PBKDF2-HMAC-SHA256哈希密码

        使用标准库实现，不依赖外部库。
        """
        salt = secrets.token_bytes(cls.PBKDF2_SALT_LEN)
        dk = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            cls.PBKDF2_ITERATIONS,
            cls.PBKDF2_HASH_LEN,
        )
        return f"pbkdf2_sha256${cls.PBKDF2_ITERATIONS}${salt.hex()}${dk.hex()}"

    @classmethod
    def verify_password_pbkdf2(cls, hashed: str, password: str) -> bool:
        """验证PBKDF2哈希"""
        try:
            algorithm, iterations, salt_hex, hash_hex = hashed.split("$")
            if algorithm != "pbkdf2_sha256":
                return False
            salt = bytes.fromhex(salt_hex)
            stored_hash = bytes.fromhex(hash_hex)
            computed_hash = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                salt,
                int(iterations),
                len(stored_hash),
            )
            # 使用恒定时间比较防止时序攻击
            return hmac.compare_digest(stored_hash, computed_hash)
        except (ValueError, AttributeError):
            return False

    @classmethod
    def hash_password_bcrypt(cls, password: str) -> str:
        """使用bcrypt哈希密码"""
        try:
            import bcrypt
            salt = bcrypt.gensalt(rounds=12)
            return bcrypt.hashpw(password.encode("utf-8"), salt).decode()
        except ImportError:
            return cls.hash_password_pbkdf2(password)

    @classmethod
    def verify_password_bcrypt(cls, hashed: str, password: str) -> bool:
        """验证bcrypt哈希"""
        try:
            import bcrypt
            return bcrypt.checkpw(
                password.encode("utf-8"), hashed.encode()
            )
        except ImportError:
            return cls.verify_password_pbkdf2(hashed, password)

    @classmethod
    def generate_password_reset_token(cls) -> str:
        """生成密码重置令牌"""
        return secrets.token_urlsafe(32)

    @classmethod
    def needs_rehash(cls, hashed: str) -> bool:
        """检查密码哈希是否需要更新（参数升级）"""
        if hashed.startswith("pbkdf2_sha256$"):
            parts = hashed.split("$")
            if len(parts) >= 2:
                try:
                    iterations = int(parts[1])
                    return iterations < cls.PBKDF2_ITERATIONS
                except ValueError:
                    pass
        return False


# =============================================================================
# 5. 安全文件操作 (Secure File Operations)
# =============================================================================

class SecureFileHandler:
    """安全文件操作工具集"""

    ALLOWED_EXTENSIONS = {".txt", ".pdf", ".jpg", ".png", ".csv", ".json"}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR = Path("uploads")

    @classmethod
    def safe_read_file(cls, file_path: str, base_dir: str = ".") -> bytes:
        """
        安全读取文件

        防止路径遍历攻击。
        """
        base = Path(base_dir).resolve()
        # 解析绝对路径，防止符号链接和相对路径绕过
        target = (base / file_path).resolve()

        # 验证目标路径在base目录内
        try:
            target.relative_to(base)
        except ValueError:
            raise ValueError(f"路径遍历检测: {file_path}")

        if not target.is_file():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        return target.read_bytes()

    @classmethod
    def safe_write_file(cls, filename: str, content: bytes,
                        base_dir: str = ".") -> str:
        """
        安全写入文件

        验证文件名、路径和大小。
        """
        # 清理文件名
        safe_name = InputValidator.sanitize_filename(filename)

        # 验证扩展名
        ext = Path(safe_name).suffix.lower()
        if ext not in cls.ALLOWED_EXTENSIONS:
            raise ValueError(f"不允许的文件类型: {ext}")

        # 验证文件大小
        if len(content) > cls.MAX_FILE_SIZE:
            raise ValueError("文件过大")

        # 构造安全路径
        base = Path(base_dir).resolve()
        target = (base / safe_name).resolve()

        # 验证路径安全
        try:
            target.relative_to(base)
        except ValueError:
            raise ValueError("路径遍历检测")

        # 确保父目录存在
        target.parent.mkdir(parents=True, exist_ok=True)

        # 使用原子写入
        temp_path = target.with_suffix(target.suffix + ".tmp")
        try:
            temp_path.write_bytes(content)
            temp_path.replace(target)  # 原子操作
        except Exception:
            if temp_path.exists():
                temp_path.unlink()
            raise

        return str(target)

    @classmethod
    def safe_file_upload(cls, upload_data: bytes, original_filename: str,
                         user_id: int) -> Dict:
        """
        安全文件上传

        实现完整的安全文件上传流程。
        """
        # 1. 验证文件大小
        if len(upload_data) > cls.MAX_FILE_SIZE:
            raise ValueError("文件过大")

        # 2. 清理文件名
        safe_name = InputValidator.sanitize_filename(original_filename)

        # 3. 验证扩展名
        ext = Path(safe_name).suffix.lower()
        if ext not in cls.ALLOWED_EXTENSIONS:
            raise ValueError(f"不允许的文件类型: {ext}")

        # 4. 生成唯一存储名（防止冲突和信息泄露）
        stored_name = f"{user_id}_{secrets.token_hex(8)}{ext}"

        # 5. 创建用户目录
        user_dir = cls.UPLOAD_DIR / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)

        # 6. 安全路径验证
        target = (user_dir / stored_name).resolve()
        try:
            target.relative_to(user_dir.resolve())
        except ValueError:
            raise ValueError("路径遍历检测")

        # 7. 验证文件内容（Magic Number检查）
        magic_numbers = {
            b"\xff\xd8\xff": ".jpg",
            b"\x89PNG": ".png",
            b"%PDF": ".pdf",
        }
        actual_type = None
        for magic, expected_ext in magic_numbers.items():
            if upload_data.startswith(magic):
                actual_type = expected_ext
                break
        if actual_type and actual_type != ext:
            raise ValueError("文件内容与扩展名不匹配")

        # 8. 写入文件
        target.write_bytes(upload_data)

        return {
            "original_name": safe_name,
            "stored_name": stored_name,
            "path": str(target),
            "size": len(upload_data),
            "type": ext,
        }

    @classmethod
    def safe_delete_file(cls, file_path: str, base_dir: str = ".") -> bool:
        """安全删除文件"""
        base = Path(base_dir).resolve()
        target = (base / file_path).resolve()

        try:
            target.relative_to(base)
        except ValueError:
            raise ValueError("路径遍历检测")

        if not target.is_file():
            return False

        target.unlink()
        return True


# =============================================================================
# 6. 安全随机数生成 (Secure Random Number Generation)
# =============================================================================

class SecureRandom:
    """安全随机数生成工具集"""

    @staticmethod
    def generate_token(length: int = 32) -> str:
        """
        生成安全随机令牌

        使用secrets模块（基于操作系统CSPRNG）
        """
        return secrets.token_urlsafe(length)

    @staticmethod
    def generate_hex(length: int = 32) -> str:
        """生成十六进制随机字符串"""
        return secrets.token_hex(length)

    @staticmethod
    def generate_password(length: int = 16,
                          include_symbols: bool = True) -> str:
        """生成强随机密码"""
        import string
        alphabet = string.ascii_letters + string.digits
        if include_symbols:
            alphabet += "!@#$%^&*-_=+"

        # 确保至少包含每种字符类型
        password = [
            secrets.choice(string.ascii_lowercase),
            secrets.choice(string.ascii_uppercase),
            secrets.choice(string.digits),
        ]
        if include_symbols:
            password.append(secrets.choice("!@#$%^&*-_=+"))

        # 填充剩余长度
        for _ in range(length - len(password)):
            password.append(secrets.choice(alphabet))

        # 安全洗牌
        import random
        # 使用secrets来选择交换位置（random.shuffle不安全）
        for i in range(len(password) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            password[i], password[j] = password[j], password[i]

        return "".join(password)

    @staticmethod
    def generate_api_key() -> str:
        """生成API密钥"""
        prefix = "sk"
        key = secrets.token_urlsafe(32)
        return f"{prefix}_{key}"

    @staticmethod
    def generate_otp_secret() -> str:
        """生成TOTP密钥（Base32编码）"""
        import base64
        secret = secrets.token_bytes(20)
        return base64.b32encode(secret).decode("utf-8")

    @staticmethod
    def generate_uuid() -> str:
        """生成UUID v4"""
        import uuid
        return str(uuid.uuid4())

    @staticmethod
    def constant_time_compare(a: str, b: str) -> bool:
        """
        恒定时间比较

        防止时序攻击，用于比较令牌/哈希值。
        """
        return hmac.compare_digest(a.encode(), b.encode())


# =============================================================================
# 7. 安全错误处理 (Secure Error Handling)
# =============================================================================

class SecureErrorHandler:
    """
    安全错误处理

    原则：
    1. 不向用户泄露系统内部信息
    2. 记录详细错误到日志（不含敏感数据）
    3. 使用通用错误消息面向用户
    4. 使用错误ID关联日志和用户消息
    """

    # 通用错误消息（不泄露内部信息）
    GENERIC_ERROR_MESSAGE = "服务器处理请求时发生错误，请联系管理员。"
    GENERIC_AUTH_ERROR = "用户名或密码错误。"
    GENERIC_NOT_FOUND = "请求的资源不存在。"
    GENERIC_FORBIDDEN = "您没有权限执行此操作。"

    @classmethod
    def handle_database_error(cls, error: Exception) -> Dict:
        """安全处理数据库错误"""
        error_id = SecureRandom.generate_hex(8)
        logger.error(
            f"[ErrorID:{error_id}] 数据库错误: {type(error).__name__}",
            exc_info=True,
        )
        # 检查是否为唯一约束冲突
        if "UNIQUE constraint failed" in str(error):
            return {
                "success": False,
                "error": "该数据已存在，请勿重复提交。",
                "error_id": error_id,
            }
        # 其他数据库错误不暴露细节
        return {
            "success": False,
            "error": cls.GENERIC_ERROR_MESSAGE,
            "error_id": error_id,
        }

    @classmethod
    def handle_file_error(cls, error: Exception) -> Dict:
        """安全处理文件操作错误"""
        error_id = SecureRandom.generate_hex(8)
        logger.error(
            f"[ErrorID:{error_id}] 文件操作错误: {type(error).__name__}",
            exc_info=True,
        )
        if isinstance(error, FileNotFoundError):
            return {
                "success": False,
                "error": cls.GENERIC_NOT_FOUND,
                "error_id": error_id,
            }
        if isinstance(error, PermissionError):
            return {
                "success": False,
                "error": cls.GENERIC_FORBIDDEN,
                "error_id": error_id,
            }
        return {
            "success": False,
            "error": cls.GENERIC_ERROR_MESSAGE,
            "error_id": error_id,
        }

    @classmethod
    def handle_auth_error(cls, error: Exception) -> Dict:
        """安全处理认证错误"""
        error_id = SecureRandom.generate_hex(8)
        logger.warning(
            f"[ErrorID:{error_id}] 认证失败: {type(error).__name__}",
        )
        # 认证错误始终返回相同的消息（防止用户枚举）
        return {
            "success": False,
            "error": cls.GENERIC_AUTH_ERROR,
            "error_id": error_id,
        }

    @classmethod
    def safe_api_response(cls, func):
        """API安全响应装饰器"""
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return {"success": True, "data": result}
            except ValueError as e:
                error_id = SecureRandom.generate_hex(8)
                logger.warning(
                    f"[ErrorID:{error_id}] 输入验证失败: {e}"
                )
                return {
                    "success": False,
                    "error": str(e),
                    "error_id": error_id,
                }
            except PermissionError as e:
                error_id = SecureRandom.generate_hex(8)
                logger.warning(
                    f"[ErrorID:{error_id}] 权限错误: {e}"
                )
                return {
                    "success": False,
                    "error": cls.GENERIC_FORBIDDEN,
                    "error_id": error_id,
                }
            except Exception as e:
                error_id = SecureRandom.generate_hex(8)
                logger.error(
                    f"[ErrorID:{error_id}] 未预期错误: "
                    f"{type(e).__name__}: {e}",
                    exc_info=True,
                )
                return {
                    "success": False,
                    "error": cls.GENERIC_ERROR_MESSAGE,
                    "error_id": error_id,
                }
        return wrapper


# =============================================================================
# 8. 安全命令执行 (Secure Command Execution)
# =============================================================================

class SecureCommandExecutor:
    """安全命令执行工具集"""

    # 允许的命令白名单
    ALLOWED_COMMANDS = {
        "ping": {
            "binary": "/bin/ping",
            "max_args": 2,
            "allowed_flags": {"-c", "-W"},
            "requires_value": {"-c", "-W"},
        },
        "nslookup": {
            "binary": "/usr/bin/nslookup",
            "max_args": 1,
            "allowed_flags": set(),
            "requires_value": set(),
        },
    }

    @classmethod
    def execute_command(cls, command: str, args: List[str],
                        timeout: int = 30) -> Tuple[bool, str]:
        """
        安全执行命令

        使用白名单验证命令和参数，避免命令注入。
        """
        if command not in cls.ALLOWED_COMMANDS:
            raise ValueError(f"不允许的命令: {command}")

        config = cls.ALLOWED_COMMANDS[command]
        binary = config["binary"]

        # 验证参数数量
        if len(args) > config["max_args"]:
            raise ValueError("参数过多")

        # 验证参数格式（只允许字母数字和点）
        validated_args = []
        for arg in args:
            if not re.match(r"^[a-zA-Z0-9.\-]+$", arg):
                raise ValueError(f"参数包含非法字符: {arg}")
            validated_args.append(arg)

        # 使用列表形式传递参数（不经过shell，防止注入）
        try:
            result = subprocess.run(
                [binary] + validated_args,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return result.returncode == 0, result.stdout
        except subprocess.TimeoutExpired:
            raise TimeoutError(f"命令执行超时（{timeout}秒）")
        except FileNotFoundError:
            raise FileNotFoundError(f"命令不存在: {binary}")

    @classmethod
    def safe_subprocess_example(cls) -> str:
        """
        安全的子进程调用示例

        不安全示例（命令注入风险）：
        subprocess.call(f"nslookup {user_input}", shell=True)

        安全示例：
        使用列表参数，不使用shell=True
        """
        user_input = "example.com"  # 模拟用户输入

        # 安全：使用列表参数
        result = subprocess.run(
            ["nslookup", user_input],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.stdout


# =============================================================================
# 演示主函数
# =============================================================================

def demo_input_validation():
    """演示输入验证"""
    print("=" * 60)
    print("1. 输入验证演示")
    print("=" * 60)

    # 用户名验证
    for username in ["alice", "admin'; DROP TABLE--", "测试用户123", "a"]:
        valid, msg = InputValidator.validate_username(username)
        print(f"  用户名 '{username}': {'通过' if valid else '拒绝'} - {msg}")

    # 邮箱验证
    for email in ["user@example.com", "invalid", "a@b.c"]:
        valid, msg = InputValidator.validate_email(email)
        print(f"  邮箱 '{email}': {'通过' if valid else '拒绝'} - {msg}")

    # 文件名清理
    for filename in ["../../../etc/passwd", "file.txt", "normal.pdf"]:
        try:
            safe = InputValidator.sanitize_filename(filename)
            print(f"  文件名 '{filename}' -> '{safe}'")
        except ValueError as e:
            print(f"  文件名 '{filename}' -> 错误: {e}")


def demo_output_encoding():
    """演示输出编码"""
    print("\n" + "=" * 60)
    print("2. 输出编码演示")
    print("=" * 60)

    xss_payload = "<script>alert('XSS')</script>"
    print(f"  原始: {xss_payload}")
    print(f"  HTML编码: {OutputEncoder.encode_html(xss_payload)}")
    print(f"  JS编码: {OutputEncoder.encode_javascript(xss_payload)}")
    print(f"  URL编码: {OutputEncoder.encode_url(xss_payload)}")


def demo_parameterized_query():
    """演示参数化查询"""
    print("\n" + "=" * 60)
    print("3. 参数化查询演示")
    print("=" * 60)

    db = SecureDatabase(":memory:")

    # 创建用户
    db.create_user("alice", "alice@example.com",
                   SecurePasswordHasher.hash_password_pbkdf2("pass123"),
                   "salt123")
    db.create_user("bob", "bob@example.com",
                   SecurePasswordHasher.hash_password_pbkdf2("pass456"),
                   "salt456")

    # 安全查询（尝试SQL注入会被安全处理）
    print("  查询用户 'alice':", db.get_user("alice"))
    print("  查询注入 ' OR '1'='1:", db.get_user("' OR '1'='1"))
    print("  搜索用户 'li':", db.search_users("li"))


def demo_password_hashing():
    """演示密码哈希"""
    print("\n" + "=" * 60)
    print("4. 安全密码哈希演示")
    print("=" * 60)

    password = "MySecurePassword123!"
    hashed = SecurePasswordHasher.hash_password_pbkdf2(password)
    print(f"  密码: {password}")
    print(f"  哈希: {hashed[:50]}...")
    print(f"  验证正确密码: {SecurePasswordHasher.verify_password_pbkdf2(hashed, password)}")
    print(f"  验证错误密码: {SecurePasswordHasher.verify_password_pbkdf2(hashed, 'wrong')}")

    print(f"  生成的随机密码: {SecureRandom.generate_password()}")
    print(f"  生成的API密钥: {SecureRandom.generate_api_key()}")
    print(f"  生成的令牌: {SecureRandom.generate_token()}")


def demo_secure_file_ops():
    """演示安全文件操作"""
    print("\n" + "=" * 60)
    print("5. 安全文件操作演示")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmpdir:
        # 安全写入
        path = SecureFileHandler.safe_write_file(
            "test.txt", b"Hello World", tmpdir
        )
        print(f"  写入文件: {path}")

        # 安全读取
        content = SecureFileHandler.safe_read_file("test.txt", tmpdir)
        print(f"  读取内容: {content}")

        # 路径遍历检测
        try:
            SecureFileHandler.safe_read_file("../../../etc/passwd", tmpdir)
        except ValueError as e:
            print(f"  路径遍历被阻止: {e}")


def demo_error_handling():
    """演示安全错误处理"""
    print("\n" + "=" * 60)
    print("6. 安全错误处理演示")
    print("=" * 60)

    # 模拟数据库错误
    error = sqlite3.IntegrityError("UNIQUE constraint failed: users.username")
    result = SecureErrorHandler.handle_database_error(error)
    print(f"  数据库错误响应: {result}")

    # 模拟认证错误
    error = Exception("User not found in database at line 42")
    result = SecureErrorHandler.handle_auth_error(error)
    print(f"  认证错误响应: {result}")


def demo_secure_command():
    """演示安全命令执行"""
    print("\n" + "=" * 60)
    print("7. 安全命令执行演示")
    print("=" * 60)

    # 允许的命令
    try:
        success, output = SecureCommandExecutor.execute_command(
            "nslookup", ["example.com"]
        )
        print(f"  执行 nslookup example.com: {'成功' if success else '失败'}")
        print(f"  输出前100字符: {output[:100]}")
    except Exception as e:
        print(f"  命令执行异常: {e}")

    # 拒绝的命令
    try:
        SecureCommandExecutor.execute_command("rm", ["-rf", "/"])
    except ValueError as e:
        print(f"  非法命令被拒绝: {e}")

    # 命令注入尝试
    try:
        SecureCommandExecutor.execute_command(
            "nslookup", ["example.com; rm -rf /"]
        )
    except ValueError as e:
        print(f"  命令注入被阻止: {e}")


def main():
    """主函数 - 运行所有演示"""
    print("=" * 60)
    print("安全编码模式示例库")
    print("Secure Coding Patterns Demonstration")
    print("=" * 60)

    demo_input_validation()
    demo_output_encoding()
    demo_parameterized_query()
    demo_password_hashing()
    demo_secure_file_ops()
    demo_error_handling()
    demo_secure_command()

    print("\n" + "=" * 60)
    print("所有演示完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
