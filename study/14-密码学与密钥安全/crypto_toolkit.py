# -*- coding: utf-8 -*-
"""
密码学工具集 (Crypto Toolkit)
================================

本工具集包含常见密码学算法的 Python 实现，用于学习和演示目的。
包含：古典密码、对称加密、非对称加密、哈希算法、消息认证、密钥交换等。

注意：本实现仅用于学习，请勿用于生产环境。
      生产环境请使用经过严格审计的密码学库（如 OpenSSL、cryptography 等）。

作者：密码学学习工具
版本：1.0
"""

import os
import sys
import math
import random
import hashlib
import base64
import string
import re
from typing import Tuple, List, Optional

# ============================================================================
# 第一部分：古典密码
# ============================================================================

class ClassicalCipher:
    """古典密码算法集合"""

    # ------------------------------------------------------------
    # 凯撒密码 (Caesar Cipher)
    # ------------------------------------------------------------
    @staticmethod
    def caesar_encrypt(plaintext: str, shift: int = 3) -> str:
        """
        凯撒密码加密

        原理：将每个字母向后移动固定位数
        公式：C = (P + shift) mod 26

        参数:
            plaintext: 明文字符串（只处理字母，其他字符保留）
            shift: 移位数（0-25）

        返回:
            密文字符串

        示例:
            >>> ClassicalCipher.caesar_encrypt("HELLO", 3)
            'KHOOR'
        """
        result = []
        shift = shift % 26  # 确保移位数在 0-25 之间

        for char in plaintext:
            if char.isupper():
                # 大写字母：A(65) - Z(90)
                shifted = ord(char) + shift
                if shifted > ord('Z'):
                    shifted -= 26
                result.append(chr(shifted))
            elif char.islower():
                # 小写字母：a(97) - z(122)
                shifted = ord(char) + shift
                if shifted > ord('z'):
                    shifted -= 26
                result.append(chr(shifted))
            else:
                # 非字母字符保留不变
                result.append(char)

        return ''.join(result)

    @staticmethod
    def caesar_decrypt(ciphertext: str, shift: int = 3) -> str:
        """
        凯撒密码解密

        原理：将每个字母向前移动固定位数（即加密的逆操作）
        公式：P = (C - shift) mod 26

        参数:
            ciphertext: 密文字符串
            shift: 移位数（与加密时相同）

        返回:
            明文字符串
        """
        # 解密就是反向移位，等价于 shift = 26 - shift
        return ClassicalCipher.caesar_encrypt(ciphertext, 26 - (shift % 26))

    @staticmethod
    def caesar_brute_force(ciphertext: str) -> List[Tuple[int, str]]:
        """
        凯撒密码暴力破解

        原理：凯撒密码只有 26 种可能的密钥，逐一尝试即可

        参数:
            ciphertext: 密文字符串

        返回:
            所有 26 种移位的结果列表 [(shift, plaintext), ...]
        """
        results = []
        for shift in range(26):
            plaintext = ClassicalCipher.caesar_decrypt(ciphertext, shift)
            results.append((shift, plaintext))
        return results

    # ------------------------------------------------------------
    # 维吉尼亚密码 (Vigenere Cipher)
    # ------------------------------------------------------------
    @staticmethod
    def vigenere_encrypt(plaintext: str, key: str) -> str:
        """
        维吉尼亚密码加密

        原理：多表替换密码，使用密钥词决定每一位的移位数
        第 i 位的移位数 = 密钥第 (i mod keylen) 位对应的字母位置

        参数:
            plaintext: 明文字符串
            key: 密钥词（只使用字母）

        返回:
            密文字符串

        示例:
            >>> ClassicalCipher.vigenere_encrypt("HELLO", "KEY")
            'RIJVS'
        """
        # 过滤密钥中的非字母字符，并转为大写
        key_letters = [c.upper() for c in key if c.isalpha()]
        if not key_letters:
            raise ValueError("密钥必须包含至少一个字母")

        key_len = len(key_letters)
        result = []
        key_index = 0

        for char in plaintext:
            if char.isalpha():
                # 计算当前密钥位的移位数
                shift = ord(key_letters[key_index % key_len]) - ord('A')

                if char.isupper():
                    shifted = ord(char) + shift
                    if shifted > ord('Z'):
                        shifted -= 26
                    result.append(chr(shifted))
                else:
                    shifted = ord(char.upper()) + shift
                    if shifted > ord('Z'):
                        shifted -= 26
                    result.append(chr(shifted).lower())

                key_index += 1
            else:
                # 非字母字符保留（不消耗密钥）
                result.append(char)

        return ''.join(result)

    @staticmethod
    def vigenere_decrypt(ciphertext: str, key: str) -> str:
        """
        维吉尼亚密码解密

        原理：加密的逆操作，每一位向前移动密钥对应的位数
        """
        # 将密钥转为"解密密钥"（每个字母的反向移位）
        key_letters = [c.upper() for c in key if c.isalpha()]
        decrypt_key = ''.join(
            chr(ord('A') + (26 - (ord(k) - ord('A'))) % 26)
            for k in key_letters
        )
        return ClassicalCipher.vigenere_encrypt(ciphertext, decrypt_key)

    # ------------------------------------------------------------
    # 频率分析（用于破解古典密码）
    # ------------------------------------------------------------
    @staticmethod
    def frequency_analysis(text: str) -> dict:
        """
        频率分析：统计文本中各字母出现的频率

        原理：自然语言中各字母的出现频率有固定分布
        英语字母频率（从高到低）：E, T, A, O, I, N, S, H, R, D, L, C, ...

        参数:
            text: 待分析的文本

        返回:
            字母频率字典 {字母: 频率百分比}
        """
        # 只统计字母
        letters = [c.upper() for c in text if c.isalpha()]
        total = len(letters)

        if total == 0:
            return {}

        freq = {}
        for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            freq[c] = (letters.count(c) / total) * 100

        return freq

    @staticmethod
    def english_freq() -> dict:
        """英语字母标准频率表（百分比）"""
        return {
            'E': 12.70, 'T': 9.06, 'A': 8.17, 'O': 7.51, 'I': 6.97,
            'N': 6.75, 'S': 6.33, 'H': 6.09, 'R': 5.99, 'D': 4.25,
            'L': 4.03, 'C': 2.78, 'U': 2.76, 'M': 2.41, 'W': 2.36,
            'F': 2.23, 'G': 2.02, 'Y': 1.97, 'P': 1.93, 'B': 1.49,
            'V': 0.98, 'K': 0.77, 'J': 0.15, 'X': 0.15, 'Q': 0.10,
            'Z': 0.07
        }


# ============================================================================
# 第二部分：对称加密算法
# ============================================================================

class SymmetricCipher:
    """对称加密算法集合"""

    # ------------------------------------------------------------
    # Base64 / Hex 编解码
    # ------------------------------------------------------------
    @staticmethod
    def bytes_to_hex(data: bytes) -> str:
        """字节流转十六进制字符串"""
        return data.hex()

    @staticmethod
    def hex_to_bytes(hex_str: str) -> bytes:
        """十六进制字符串转字节流"""
        return bytes.fromhex(hex_str)

    @staticmethod
    def bytes_to_base64(data: bytes) -> str:
        """字节流转 Base64 字符串"""
        return base64.b64encode(data).decode('utf-8')

    @staticmethod
    def base64_to_bytes(b64_str: str) -> bytes:
        """Base64 字符串转字节流"""
        return base64.b64decode(b64_str)

    # ------------------------------------------------------------
    # XOR 加密（最简对称加密，用于演示）
    # ------------------------------------------------------------
    @staticmethod
    def xor_encrypt(data: bytes, key: bytes) -> bytes:
        """
        XOR 加密（也可以解密，因为 XOR 是对称的）

        原理：明文与密钥逐字节异或
        安全性：极弱（密钥太短或重复时极易破解）
        用途：仅用于学习演示

        参数:
            data: 明文/密文字节流
            key: 密钥字节流（循环使用）

        返回:
            加密/解密后的字节流
        """
        if len(key) == 0:
            raise ValueError("密钥不能为空")

        result = bytearray(len(data))
        key_len = len(key)

        for i in range(len(data)):
            result[i] = data[i] ^ key[i % key_len]

        return bytes(result)

    # ------------------------------------------------------------
    # AES 简化版（使用 Python 标准库 hashlib 进行演示）
    # 实际项目中请使用 cryptography 或 PyCryptodome 库
    # ------------------------------------------------------------
    @staticmethod
    def aes_ecb_encrypt_simple(plaintext: bytes, key: bytes) -> bytes:
        """
        简化版 AES-ECB 加密演示

        注意：这不是真正的 AES 实现，而是使用 SHA-256 模拟的"伪加密"，
        仅用于演示 ECB 模式的概念。真正的 AES 实现非常复杂，
        建议使用 cryptography 等专业库。

        参数:
            plaintext: 明文字节流
            key: 密钥（16/24/32 字节对应 AES-128/192/256）

        返回:
            密文字节流
        """
        block_size = 16  # AES 块大小 16 字节

        # PKCS#7 填充
        padded = SymmetricCipher._pkcs7_pad(plaintext, block_size)

        # 简化的"加密"：每个块用密钥派生出的密钥流异或
        # （真实 AES 使用 S 盒、行移位、列混合、轮密钥加等操作）
        ciphertext = bytearray()

        for i in range(0, len(padded), block_size):
            block = padded[i:i + block_size]
            # 用块索引和密钥生成"伪轮密钥"
            # 真实 AES 有复杂的密钥扩展和多轮变换
            block_key = hashlib.sha256(key + i.to_bytes(4, 'big')).digest()[:block_size]
            encrypted_block = bytes(b ^ k for b, k in zip(block, block_key))
            ciphertext.extend(encrypted_block)

        return bytes(ciphertext)

    @staticmethod
    def aes_ecb_decrypt_simple(ciphertext: bytes, key: bytes) -> bytes:
        """简化版 AES-ECB 解密（与加密相同，因为是异或操作）"""
        block_size = 16

        if len(ciphertext) % block_size != 0:
            raise ValueError("密文长度不是块大小的整数倍")

        padded = bytearray()

        for i in range(0, len(ciphertext), block_size):
            block = ciphertext[i:i + block_size]
            block_key = hashlib.sha256(key + i.to_bytes(4, 'big')).digest()[:block_size]
            decrypted_block = bytes(b ^ k for b, k in zip(block, block_key))
            padded.extend(decrypted_block)

        # 去除 PKCS#7 填充
        plaintext = SymmetricCipher._pkcs7_unpad(bytes(padded), block_size)
        return plaintext

    @staticmethod
    def aes_cbc_encrypt_simple(plaintext: bytes, key: bytes, iv: bytes) -> bytes:
        """
        简化版 AES-CBC 加密演示

        CBC 模式：每个明文块先与前一个密文块异或，再加密
        第一个块使用初始化向量 IV

        参数:
            plaintext: 明文字节流
            key: 密钥
            iv: 初始化向量（16字节，必须随机且不可预测）

        返回:
            密文字节流
        """
        block_size = 16

        if len(iv) != block_size:
            raise ValueError(f"IV 长度必须为 {block_size} 字节")

        # PKCS#7 填充
        padded = SymmetricCipher._pkcs7_pad(plaintext, block_size)

        ciphertext = bytearray()
        previous_block = iv  # 前一个密文块，初始为 IV

        for i in range(0, len(padded), block_size):
            # 明文块与前一个密文块异或
            plain_block = padded[i:i + block_size]
            xor_block = bytes(p ^ c for p, c in zip(plain_block, previous_block))

            # "加密"（简化版）
            block_key = hashlib.sha256(key + i.to_bytes(4, 'big')).digest()[:block_size]
            encrypted_block = bytes(b ^ k for b, k in zip(xor_block, block_key))

            ciphertext.extend(encrypted_block)
            previous_block = encrypted_block

        return bytes(ciphertext)

    @staticmethod
    def aes_cbc_decrypt_simple(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
        """简化版 AES-CBC 解密"""
        block_size = 16

        if len(iv) != block_size:
            raise ValueError(f"IV 长度必须为 {block_size} 字节")
        if len(ciphertext) % block_size != 0:
            raise ValueError("密文长度不是块大小的整数倍")

        padded = bytearray()
        previous_block = iv

        for i in range(0, len(ciphertext), block_size):
            cipher_block = ciphertext[i:i + block_size]

            # "解密"（简化版）
            block_key = hashlib.sha256(key + i.to_bytes(4, 'big')).digest()[:block_size]
            xor_block = bytes(b ^ k for b, k in zip(cipher_block, block_key))

            # 与前一个密文块异或得到明文
            plain_block = bytes(x ^ p for x, p in zip(xor_block, previous_block))

            padded.extend(plain_block)
            previous_block = cipher_block

        # 去除填充
        plaintext = SymmetricCipher._pkcs7_unpad(bytes(padded), block_size)
        return plaintext

    @staticmethod
    def aes_ctr_encrypt_simple(plaintext: bytes, key: bytes, nonce: bytes) -> bytes:
        """
        简化版 AES-CTR 加密（解密相同）

        CTR 模式：用计数器生成密钥流，与明文异或
        加密和解密操作完全相同

        参数:
            plaintext: 明文字节流
            key: 密钥
            nonce: 随机数（必须唯一，不能重复）

        返回:
            密文字节流
        """
        block_size = 16
        ciphertext = bytearray()
        counter = 0

        for i in range(0, len(plaintext), block_size):
            # 构造计数器块：nonce + counter
            counter_block = nonce + counter.to_bytes(block_size - len(nonce), 'big')

            # 生成密钥流块
            keystream_block = hashlib.sha256(key + counter_block).digest()[:block_size]

            # 与明文异或
            plain_block = plaintext[i:i + block_size]
            encrypted_block = bytes(p ^ k for p, k in zip(plain_block, keystream_block))
            ciphertext.extend(encrypted_block)

            counter += 1

        return bytes(ciphertext)

    # ------------------------------------------------------------
    # 填充函数
    # ------------------------------------------------------------
    @staticmethod
    def _pkcs7_pad(data: bytes, block_size: int = 16) -> bytes:
        """
        PKCS#7 填充

        填充规则：
        - 需要填充 n 个字节，每个填充字节的值都是 n
        - 如果数据长度正好是块大小的整数倍，填充一整块（值全为 block_size）

        示例：
        块大小 16，数据长度 10 → 填充 6 个 0x06
        块大小 16，数据长度 16 → 填充 16 个 0x10
        """
        pad_len = block_size - (len(data) % block_size)
        padding = bytes([pad_len] * pad_len)
        return data + padding

    @staticmethod
    def _pkcs7_unpad(data: bytes, block_size: int = 16) -> bytes:
        """
        PKCS#7 去填充

        验证填充是否正确，然后去除填充
        """
        if len(data) == 0:
            raise ValueError("数据为空")
        if len(data) % block_size != 0:
            raise ValueError("数据长度不是块大小的整数倍")

        pad_len = data[-1]  # 最后一个字节是填充长度

        # 验证填充
        if pad_len == 0 or pad_len > block_size:
            raise ValueError("无效的 PKCS#7 填充")
        if data[-pad_len:] != bytes([pad_len] * pad_len):
            raise ValueError("无效的 PKCS7 填充")

        return data[:-pad_len]

    # ------------------------------------------------------------
    # 使用 cryptography 库的真实 AES 实现（可选）
    # ------------------------------------------------------------
    @staticmethod
    def aes_gcm_encrypt(plaintext: bytes, key: bytes, associated_data: bytes = b'') -> Tuple[bytes, bytes, bytes]:
        """
        AES-GCM 认证加密（需要安装 cryptography 库）

        GCM 模式同时提供加密和认证，是推荐的工作模式。

        参数:
            plaintext: 明文字节流
            key: 密钥（16/24/32 字节）
            associated_data: 关联数据（只认证不加密）

        返回:
            (nonce, ciphertext, tag) 三元组
            - nonce: 随机数（12字节）
            - ciphertext: 密文
            - tag: 认证标签（16字节）
        """
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        except ImportError:
            raise ImportError("请先安装 cryptography 库：pip install cryptography")

        aesgcm = AESGCM(key)
        nonce = os.urandom(12)  # GCM 推荐使用 12 字节 nonce
        ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data)
        # ciphertext 包含密文和 tag（tag 在最后 16 字节）
        tag = ciphertext[-16:]
        ciphertext = ciphertext[:-16]
        return nonce, ciphertext, tag

    @staticmethod
    def aes_gcm_decrypt(nonce: bytes, ciphertext: bytes, tag: bytes, key: bytes,
                        associated_data: bytes = b'') -> bytes:
        """
        AES-GCM 认证解密

        参数:
            nonce: 随机数
            ciphertext: 密文
            tag: 认证标签
            key: 密钥
            associated_data: 关联数据

        返回:
            明文字节流（认证失败会抛出异常）
        """
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        except ImportError:
            raise ImportError("请先安装 cryptography 库：pip install cryptography")

        aesgcm = AESGCM(key)
        # 合并密文和 tag
        data = ciphertext + tag
        plaintext = aesgcm.decrypt(nonce, data, associated_data)
        return plaintext


# ============================================================================
# 第三部分：非对称加密算法
# ============================================================================

class AsymmetricCipher:
    """非对称加密算法集合"""

    # ------------------------------------------------------------
    # 数学工具函数
    # ------------------------------------------------------------
    @staticmethod
    def is_prime(n: int, k: int = 5) -> bool:
        """
        Miller-Rabin 素性测试

        判断一个数是否为素数（概率性测试）

        参数:
            n: 待测试的数
            k: 测试轮数（越多越准确）

        返回:
            True 表示可能是素数，False 表示一定是合数
        """
        if n < 2:
            return False
        if n == 2 or n == 3:
            return True
        if n % 2 == 0:
            return False

        # 写成 n-1 = d * 2^s 的形式
        d = n - 1
        s = 0
        while d % 2 == 0:
            d //= 2
            s += 1

        # 进行 k 轮测试
        for _ in range(k):
            a = random.randrange(2, n - 1)
            x = pow(a, d, n)  # a^d mod n

            if x == 1 or x == n - 1:
                continue

            for _ in range(s - 1):
                x = pow(x, 2, n)
                if x == n - 1:
                    break
            else:
                # 没有通过测试，是合数
                return False

        return True

    @staticmethod
    def generate_prime(bits: int = 512) -> int:
        """
        生成指定位数的大素数

        参数:
            bits: 素数的二进制位数

        返回:
            大素数
        """
        while True:
            # 生成随机数（确保最高位为 1，保证位数正确；最低位为 1，保证是奇数）
            n = random.getrandbits(bits)
            n |= (1 << (bits - 1)) | 1  # 设置最高位和最低位

            if AsymmetricCipher.is_prime(n):
                return n

    @staticmethod
    def gcd(a: int, b: int) -> int:
        """计算最大公约数（欧几里得算法）"""
        while b:
            a, b = b, a % b
        return a

    @staticmethod
    def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
        """
        扩展欧几里得算法

        返回 (g, x, y)，满足 a*x + b*y = g = gcd(a, b)
        用于计算模逆元
        """
        if a == 0:
            return b, 0, 1

        g, x1, y1 = AsymmetricCipher.extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1

        return g, x, y

    @staticmethod
    def mod_inverse(e: int, n: int) -> int:
        """
        计算模逆元：求 d 使得 (e * d) mod n = 1

        使用扩展欧几里得算法
        """
        g, x, _ = AsymmetricCipher.extended_gcd(e, n)
        if g != 1:
            raise ValueError("模逆元不存在（e 和 n 不互质）")
        return x % n

    # ------------------------------------------------------------
    # RSA 算法
    # ------------------------------------------------------------
    @staticmethod
    def rsa_generate_keys(bits: int = 1024) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """
        RSA 密钥生成

        步骤：
        1. 选择两个大素数 p 和 q
        2. 计算 n = p * q
        3. 计算 φ(n) = (p-1) * (q-1)
        4. 选择 e，通常为 65537（0x10001）
        5. 计算 d = e^-1 mod φ(n)

        参数:
            bits: 密钥位数（n 的二进制位数）

        返回:
            (公钥, 私钥) 二元组
            公钥 = (e, n)
            私钥 = (d, n)
        """
        # 生成两个大素数，每个约 bits/2 位
        p = AsymmetricCipher.generate_prime(bits // 2)
        q = AsymmetricCipher.generate_prime(bits // 2)

        # 确保 p != q
        while p == q:
            q = AsymmetricCipher.generate_prime(bits // 2)

        n = p * q
        phi = (p - 1) * (q - 1)

        # 选择 e = 65537（常用值）
        e = 65537
        while AsymmetricCipher.gcd(e, phi) != 1:
            e -= 2  # 如果不互质，换一个

        # 计算 d
        d = AsymmetricCipher.mod_inverse(e, phi)

        public_key = (e, n)
        private_key = (d, n)

        return public_key, private_key

    @staticmethod
    def rsa_encrypt(message: int, public_key: Tuple[int, int]) -> int:
        """
        RSA 加密

        公式：C = M^e mod n

        参数:
            message: 明文消息（整数，必须小于 n）
            public_key: 公钥 (e, n)

        返回:
            密文（整数）
        """
        e, n = public_key
        if message >= n:
            raise ValueError("消息必须小于 n")
        return pow(message, e, n)

    @staticmethod
    def rsa_decrypt(ciphertext: int, private_key: Tuple[int, int]) -> int:
        """
        RSA 解密

        公式：M = C^d mod n

        参数:
            ciphertext: 密文（整数）
            private_key: 私钥 (d, n)

        返回:
            明文（整数）
        """
        d, n = private_key
        return pow(ciphertext, d, n)

    @staticmethod
    def rsa_sign(message_hash: int, private_key: Tuple[int, int]) -> int:
        """
        RSA 数字签名（简化版）

        原理：用私钥"加密"消息哈希
        公式：S = H^d mod n

        注意：实际使用需要填充方案（PKCS#1 v1.5 或 PSS）

        参数:
            message_hash: 消息的哈希值（整数）
            private_key: 私钥 (d, n)

        返回:
            签名（整数）
        """
        d, n = private_key
        if message_hash >= n:
            raise ValueError("哈希值必须小于 n")
        return pow(message_hash, d, n)

    @staticmethod
    def rsa_verify(message_hash: int, signature: int, public_key: Tuple[int, int]) -> bool:
        """
        RSA 签名验证

        原理：用公钥"解密"签名，与消息哈希比较
        公式：H' = S^e mod n，比较 H' == H

        参数:
            message_hash: 消息的哈希值（整数）
            signature: 签名（整数）
            public_key: 公钥 (e, n)

        返回:
            True 表示验证通过
        """
        e, n = public_key
        decrypted_hash = pow(signature, e, n)
        return decrypted_hash == message_hash

    # ------------------------------------------------------------
    # RSA 文本加密（带填充的简化版本）
    # ------------------------------------------------------------
    @staticmethod
    def rsa_encrypt_text(plaintext: str, public_key: Tuple[int, int]) -> str:
        """
        RSA 文本加密（简化版，带简单填充）

        注意：实际 RSA 加密应该使用 OAEP 填充方案，
        这里只是演示用途。

        参数:
            plaintext: 明文字符串
            public_key: 公钥 (e, n)

        返回:
            密文（十六进制字符串）
        """
        e, n = public_key
        # 计算 n 的字节数
        n_bytes = (n.bit_length() + 7) // 8

        # 将文本转为整数
        plain_bytes = plaintext.encode('utf-8')

        if len(plain_bytes) > n_bytes - 11:
            raise ValueError(f"消息太长，最多 {n_bytes - 11} 字节")

        # 简化填充（类似 PKCS#1 v1.5）
        pad_len = n_bytes - len(plain_bytes) - 3
        padding = b'\x00\x02' + bytes([random.randint(1, 255) for _ in range(pad_len)]) + b'\x00'
        padded = padding + plain_bytes

        # 转为整数加密
        message_int = int.from_bytes(padded, 'big')
        cipher_int = AsymmetricCipher.rsa_encrypt(message_int, public_key)

        # 转回十六进制字符串
        return hex(cipher_int)[2:]  # 去掉 0x 前缀

    @staticmethod
    def rsa_decrypt_text(ciphertext_hex: str, private_key: Tuple[int, int]) -> str:
        """
        RSA 文本解密（简化版）
        """
        d, n = private_key
        n_bytes = (n.bit_length() + 7) // 8

        # 十六进制转整数
        cipher_int = int(ciphertext_hex, 16)
        message_int = AsymmetricCipher.rsa_decrypt(cipher_int, private_key)

        # 转回字节
        padded = message_int.to_bytes(n_bytes, 'big')

        # 去除填充
        if padded[0] != 0 or padded[1] != 2:
            raise ValueError("解密失败：填充格式错误")

        # 找到 0x00 分隔符
        sep_idx = padded.find(b'\x00', 2)
        if sep_idx == -1:
            raise ValueError("解密失败：找不到填充结束符")

        plain_bytes = padded[sep_idx + 1:]
        return plain_bytes.decode('utf-8')


# ============================================================================
# 第四部分：哈希算法
# ============================================================================

class HashUtils:
    """哈希算法工具集合"""

    # ------------------------------------------------------------
    # 标准哈希算法（使用 hashlib）
    # ------------------------------------------------------------
    @staticmethod
    def md5(data: bytes) -> str:
        """计算 MD5 哈希值（十六进制字符串）"""
        return hashlib.md5(data).hexdigest()

    @staticmethod
    def sha1(data: bytes) -> str:
        """计算 SHA-1 哈希值（十六进制字符串）"""
        return hashlib.sha1(data).hexdigest()

    @staticmethod
    def sha256(data: bytes) -> str:
        """计算 SHA-256 哈希值（十六进制字符串）"""
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def sha512(data: bytes) -> str:
        """计算 SHA-512 哈希值（十六进制字符串）"""
        return hashlib.sha512(data).hexdigest()

    # ------------------------------------------------------------
    # SM3 哈希算法（简化模拟版）
    # 注意：这不是完整的 SM3 实现，而是用 SHA-256 模拟的演示版
    # 真实 SM3 实现请使用国密算法库
    # ------------------------------------------------------------
    @staticmethod
    def sm3_simple(data: bytes) -> str:
        """
        SM3 哈希算法（简化模拟版）

        注意：这只是使用 SHA-256 模拟的 SM3 演示，
        真实的 SM3 使用不同的初始值、常量和轮函数。
        生产环境请使用专业的国密算法库（如 gmssl）。

        参数:
            data: 输入字节流

        返回:
            256 位哈希值（十六进制字符串，64个字符）
        """
        # 真实 SM3 使用 Merkle-Damgård 结构，与 SHA-256 类似
        # 但初始值、常量、轮函数都不同
        # 这里用 SHA-256 模拟输出长度和基本结构
        return hashlib.sha256(data).hexdigest()

    # ------------------------------------------------------------
    # HMAC 消息认证码
    # ------------------------------------------------------------
    @staticmethod
    def hmac(key: bytes, message: bytes, hash_func: str = 'sha256') -> str:
        """
        计算 HMAC（基于哈希的消息认证码）

        公式：HMAC(K, m) = H((K ⊕ opad) || H((K ⊕ ipad) || m))

        参数:
            key: 密钥字节流
            message: 消息字节流
            hash_func: 哈希函数名称（md5, sha1, sha256, sha512）

        返回:
            HMAC 值（十六进制字符串）
        """
        return hashlib.new(hash_func, key + message).hexdigest()

    @staticmethod
    def hmac_manual(key: bytes, message: bytes, hash_func: str = 'sha256') -> str:
        """
        手动实现 HMAC（用于学习原理）

        完整实现 HMAC 的双层哈希结构
        """
        # 获取哈希函数
        h = hashlib.new(hash_func)
        block_size = h.block_size  # 哈希函数的块大小（字节）
        hash_len = h.digest_size   # 哈希输出长度

        # 密钥预处理
        if len(key) > block_size:
            # 如果密钥比块大，先哈希
            key = hashlib.new(hash_func, key).digest()
        elif len(key) < block_size:
            # 如果密钥比块小，补 0
            key = key + b'\x00' * (block_size - len(key))

        # ipad 和 opad
        ipad = bytes([0x36] * block_size)  # 内部填充：0x36 重复
        opad = bytes([0x5c] * block_size)  # 外部填充：0x5c 重复

        # 内层哈希：H( (K ⊕ ipad) || m )
        inner_key = bytes([k ^ i for k, i in zip(key, ipad)])
        inner_hash = hashlib.new(hash_func, inner_key + message).digest()

        # 外层哈希：H( (K ⊕ opad) || 内层哈希 )
        outer_key = bytes([k ^ o for k, o in zip(key, opad)])
        outer_hash = hashlib.new(hash_func, outer_key + inner_hash).hexdigest()

        return outer_hash

    # ------------------------------------------------------------
    # 密码哈希（加盐 + 慢哈希）
    # ------------------------------------------------------------
    @staticmethod
    def password_hash(password: str, salt: Optional[bytes] = None,
                      iterations: int = 100000) -> Tuple[str, bytes]:
        """
        安全的密码哈希（使用 PBKDF2-HMAC-SHA256）

        参数:
            password: 密码字符串
            salt: 盐值（不提供则随机生成）
            iterations: 迭代次数（越多越慢越安全）

        返回:
            (哈希值十六进制, 盐值) 二元组
        """
        if salt is None:
            salt = os.urandom(16)  # 16 字节随机盐

        password_bytes = password.encode('utf-8')
        dk = hashlib.pbkdf2_hmac('sha256', password_bytes, salt, iterations)

        return dk.hex(), salt

    @staticmethod
    def password_verify(password: str, hash_hex: str, salt: bytes,
                        iterations: int = 100000) -> bool:
        """
        密码验证

        重新计算哈希并与存储的哈希比较
        """
        computed_hash, _ = HashUtils.password_hash(password, salt, iterations)

        # 恒定时间比较，防止时序攻击
        if len(computed_hash) != len(hash_hex):
            return False

        result = 0
        for a, b in zip(computed_hash, hash_hex):
            result |= ord(a) ^ ord(b)

        return result == 0

    # ------------------------------------------------------------
    # 文件哈希
    # ------------------------------------------------------------
    @staticmethod
    def file_hash(filepath: str, hash_func: str = 'sha256',
                  chunk_size: int = 8192) -> str:
        """
        计算文件的哈希值

        分块读取大文件，避免内存溢出

        参数:
            filepath: 文件路径
            hash_func: 哈希函数名称
            chunk_size: 每次读取的字节数

        返回:
            哈希值（十六进制字符串）
        """
        h = hashlib.new(hash_func)
        with open(filepath, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()


# ============================================================================
# 第五部分：密钥交换
# ============================================================================

class KeyExchange:
    """密钥交换算法集合"""

    # ------------------------------------------------------------
    # Diffie-Hellman 密钥交换
    # ------------------------------------------------------------
    @staticmethod
    def dh_generate_params(bits: int = 512) -> Tuple[int, int]:
        """
        生成 DH 参数（p, g）

        参数:
            bits: 素数 p 的位数

        返回:
            (p, g) 公共参数
            - p: 大素数
            - g: 生成元
        """
        # 生成一个大素数 p
        p = AsymmetricCipher.generate_prime(bits)

        # 选择生成元 g（简化处理，选一个小的数）
        # 实际中 g 应该是模 p 的原根
        g = 2

        return p, g

    @staticmethod
    def dh_generate_keypair(p: int, g: int) -> Tuple[int, int]:
        """
        生成 DH 密钥对

        参数:
            p: 大素数（公共参数）
            g: 生成元（公共参数）

        返回:
            (私钥, 公钥) 二元组
            - 私钥：随机整数 a
            - 公钥：g^a mod p
        """
        # 私钥：随机整数（1 < a < p-1）
        private_key = random.randrange(2, p - 1)

        # 公钥：g^a mod p
        public_key = pow(g, private_key, p)

        return private_key, public_key

    @staticmethod
    def dh_compute_shared_secret(private_key: int, other_public_key: int, p: int) -> int:
        """
        计算共享密钥

        己方私钥 + 对方公钥 → 共享密钥
        s = other_public_key ^ private_key mod p

        双方计算结果相同（数学保证）
        """
        shared_secret = pow(other_public_key, private_key, p)
        return shared_secret

    @staticmethod
    def dh_demo():
        """
        DH 密钥交换完整演示

        展示 Alice 和 Bob 如何在不安全信道上协商共享密钥
        """
        print("=" * 60)
        print("Diffie-Hellman 密钥交换演示")
        print("=" * 60)

        # 步骤 1：双方约定公共参数（p, g）
        print("\n【步骤 1】约定公共参数")
        p, g = KeyExchange.dh_generate_params(256)  # 演示用小参数
        print(f"  p (大素数) = {p}")
        print(f"  g (生成元) = {g}")

        # 步骤 2：Alice 生成密钥对
        print("\n【步骤 2】Alice 生成密钥对")
        alice_private, alice_public = KeyExchange.dh_generate_keypair(p, g)
        print(f"  Alice 私钥 = {alice_private}")
        print(f"  Alice 公钥 = {alice_public}")

        # 步骤 3：Bob 生成密钥对
        print("\n【步骤 3】Bob 生成密钥对")
        bob_private, bob_public = KeyExchange.dh_generate_keypair(p, g)
        print(f"  Bob 私钥 = {bob_private}")
        print(f"  Bob 公钥 = {bob_public}")

        # 步骤 4：交换公钥
        print("\n【步骤 4】交换公钥（在不安全信道上传输）")
        print("  Alice 收到 Bob 的公钥")
        print("  Bob 收到 Alice 的公钥")

        # 步骤 5：各自计算共享密钥
        print("\n【步骤 5】各自计算共享密钥")
        alice_shared = KeyExchange.dh_compute_shared_secret(
            alice_private, bob_public, p
        )
        bob_shared = KeyExchange.dh_compute_shared_secret(
            bob_private, alice_public, p
        )

        print(f"  Alice 计算的共享密钥 = {alice_shared}")
        print(f"  Bob 计算的共享密钥 = {bob_shared}")
        print(f"  密钥是否相同: {alice_shared == bob_shared}")

        # 步骤 6：派生出对称密钥
        print("\n【步骤 6】从共享密钥派生出对称密钥（使用 SHA-256）")
        shared_key = hashlib.sha256(
            str(alice_shared).encode()
        ).digest()
        print(f"  派生的 256 位对称密钥 = {shared_key.hex()}")

        print("\n" + "=" * 60)
        print("演示完成！")
        print("=" * 60)


# ============================================================================
# 第六部分：密码强度检测
# ============================================================================

class PasswordStrength:
    """密码强度检测器"""

    # 常见弱密码列表（部分示例）
    COMMON_PASSWORDS = {
        'password', '123456', '123456789', 'qwerty', 'abc123',
        'password1', '12345678', 'password123', '1234567',
        'admin', 'letmein', 'welcome', 'monkey', 'dragon',
        'master', 'login', 'princess', 'sunshine', 'qwerty123',
        'iloveyou', 'trustno1', '000000', '111111', '123123'
    }

    @staticmethod
    def check_strength(password: str) -> dict:
        """
        检测密码强度

        参数:
            password: 密码字符串

        返回:
            密码强度评估字典，包含：
            - score: 分数（0-100）
            - level: 等级（很弱/弱/中等/强/很强）
            - details: 详细评估项
            - suggestions: 改进建议
        """
        score = 0
        details = []
        suggestions = []

        length = len(password)

        # 1. 长度评分
        if length < 6:
            details.append(f"长度: {length} 位 (太短)")
            suggestions.append("密码长度至少 8 位，推荐 12 位以上")
            score += 0
        elif length < 8:
            details.append(f"长度: {length} 位 (较短)")
            suggestions.append("建议增加到至少 8 位")
            score += 10
        elif length < 12:
            details.append(f"长度: {length} 位 (一般)")
            score += 25
        elif length < 16:
            details.append(f"长度: {length} 位 (较好)")
            score += 35
        else:
            details.append(f"长度: {length} 位 (很好)")
            score += 40

        # 2. 字符种类
        has_lower = bool(re.search(r'[a-z]', password))
        has_upper = bool(re.search(r'[A-Z]', password))
        has_digit = bool(re.search(r'[0-9]', password))
        has_special = bool(re.search(r'[^a-zA-Z0-9]', password))

        char_types = sum([has_lower, has_upper, has_digit, has_special])

        if char_types == 1:
            details.append("字符种类: 单一 (只有一种字符类型)")
            suggestions.append("混合使用大小写字母、数字和特殊符号")
            score += 0
        elif char_types == 2:
            details.append("字符种类: 较少 (两种字符类型)")
            suggestions.append("增加更多字符类型")
            score += 10
        elif char_types == 3:
            details.append("字符种类: 较多 (三种字符类型)")
            score += 20
        else:
            details.append("字符种类: 丰富 (四种字符类型)")
            score += 25

        # 3. 常见密码检查
        if password.lower() in PasswordStrength.COMMON_PASSWORDS:
            details.append("常见密码: 是 (非常危险！)")
            suggestions.append("不要使用常见密码")
            score = min(score, 10)
        else:
            details.append("常见密码: 否")
            score += 5

        # 4. 重复性检查
        if PasswordStrength._has_repeated_chars(password):
            details.append("重复字符: 存在")
            suggestions.append("避免使用重复的字符（如 aaaa、1111）")
            score -= 5

        # 5. 连续性检查
        if PasswordStrength._has_sequential_chars(password):
            details.append("连续字符: 存在")
            suggestions.append("避免使用连续的字母或数字（如 abc、123）")
            score -= 5

        # 6. 字典词检查
        if PasswordStrength._has_dictionary_word(password):
            details.append("字典单词: 包含常见单词")
            suggestions.append("避免使用完整的英文单词")
            score -= 5

        # 确保分数在 0-100 范围内
        score = max(0, min(100, score))

        # 等级评定
        if score < 20:
            level = "很弱"
        elif score < 40:
            level = "弱"
        elif score < 60:
            level = "中等"
        elif score < 80:
            level = "强"
        else:
            level = "很强"

        return {
            'score': score,
            'level': level,
            'details': details,
            'suggestions': suggestions
        }

    @staticmethod
    def _has_repeated_chars(password: str) -> bool:
        """检查是否有重复字符（3个以上相同）"""
        for i in range(len(password) - 2):
            if password[i] == password[i + 1] == password[i + 2]:
                return True
        return False

    @staticmethod
    def _has_sequential_chars(password: str) -> bool:
        """检查是否有连续字母或数字（3个以上）"""
        # 检查数字
        for i in range(len(password) - 2):
            if password[i:i + 3].isdigit():
                nums = [int(c) for c in password[i:i + 3]]
                if nums[1] - nums[0] == 1 and nums[2] - nums[1] == 1:
                    return True
                if nums[0] - nums[1] == 1 and nums[1] - nums[2] == 1:
                    return True

        # 检查字母
        lower_pass = password.lower()
        for i in range(len(lower_pass) - 2):
            if lower_pass[i:i + 3].isalpha():
                if (ord(lower_pass[i + 1]) - ord(lower_pass[i]) == 1 and
                        ord(lower_pass[i + 2]) - ord(lower_pass[i + 1]) == 1):
                    return True
                if (ord(lower_pass[i]) - ord(lower_pass[i + 1]) == 1 and
                        ord(lower_pass[i + 1]) - ord(lower_pass[i + 2]) == 1):
                    return True

        return False

    @staticmethod
    def _has_dictionary_word(password: str) -> bool:
        """检查是否包含常见字典单词（简化版）"""
        common_words = ['password', 'admin', 'hello', 'world', 'love',
                        'master', 'dragon', 'monkey', 'sunshine', 'princess',
                        'qwerty', 'abc', 'test', 'welcome', 'letmein']
        lower_pass = password.lower()
        for word in common_words:
            if word in lower_pass and len(word) >= 4:
                return True
        return False

    @staticmethod
    def generate_strong_password(length: int = 16) -> str:
        """
        生成强密码

        参数:
            length: 密码长度（至少 8 位）

        返回:
            强密码字符串
        """
        if length < 8:
            length = 8

        # 确保包含各种字符类型
        uppercase = string.ascii_uppercase
        lowercase = string.ascii_lowercase
        digits = string.digits
        special = '!@#$%^&*()_+-=[]{}|;:,.<>?'

        # 至少各选一个
        password_chars = [
            random.choice(uppercase),
            random.choice(lowercase),
            random.choice(digits),
            random.choice(special)
        ]

        # 剩余的随机选择
        all_chars = uppercase + lowercase + digits + special
        for _ in range(length - 4):
            password_chars.append(random.choice(all_chars))

        # 打乱顺序
        random.shuffle(password_chars)

        return ''.join(password_chars)

    @staticmethod
    def print_strength_report(password: str):
        """打印密码强度检测报告"""
        result = PasswordStrength.check_strength(password)

        print("=" * 50)
        print("密码强度检测报告")
        print("=" * 50)
        print(f"密码: {'*' * len(password)} ({len(password)} 位)")
        print(f"分数: {result['score']} / 100")
        print(f"等级: {result['level']}")
        print()
        print("详细评估:")
        for detail in result['details']:
            print(f"  - {detail}")

        if result['suggestions']:
            print()
            print("改进建议:")
            for i, suggestion in enumerate(result['suggestions'], 1):
                print(f"  {i}. {suggestion}")

        print("=" * 50)


# ============================================================================
# 第七部分：演示与测试
# ============================================================================

def demo_classical_cipher():
    """演示古典密码"""
    print("\n" + "=" * 60)
    print("古典密码演示")
    print("=" * 60)

    # 凯撒密码
    plaintext = "Hello, World!"
    shift = 3
    cipher = ClassicalCipher.caesar_encrypt(plaintext, shift)
    decrypted = ClassicalCipher.caesar_decrypt(cipher, shift)

    print(f"\n凯撒密码 (移位={shift}):")
    print(f"  明文: {plaintext}")
    print(f"  密文: {cipher}")
    print(f"  解密: {decrypted}")

    # 维吉尼亚密码
    key = "KEY"
    cipher_v = ClassicalCipher.vigenere_encrypt(plaintext, key)
    decrypted_v = ClassicalCipher.vigenere_decrypt(cipher_v, key)

    print(f"\n维吉尼亚密码 (密钥={key}):")
    print(f"  明文: {plaintext}")
    print(f"  密文: {cipher_v}")
    print(f"  解密: {decrypted_v}")


def demo_symmetric():
    """演示对称加密"""
    print("\n" + "=" * 60)
    print("对称加密演示")
    print("=" * 60)

    plaintext = b"Hello, Crypto World! This is a test message."
    key = hashlib.sha256(b"my_secret_key").digest()[:16]  # 16 字节密钥
    iv = os.urandom(16)
    nonce = os.urandom(8)

    print(f"\n明文: {plaintext.decode()}")
    print(f"密钥 (十六进制): {key.hex()}")

    # ECB 模式
    print("\n--- ECB 模式 ---")
    try:
        cipher_ecb = SymmetricCipher.aes_ecb_encrypt_simple(plaintext, key)
        decrypted_ecb = SymmetricCipher.aes_ecb_decrypt_simple(cipher_ecb, key)
        print(f"密文 (十六进制): {cipher_ecb.hex()[:64]}...")
        print(f"解密结果: {decrypted_ecb.decode()}")
        print(f"解密正确: {decrypted_ecb == plaintext}")
    except Exception as e:
        print(f"错误: {e}")

    # CBC 模式
    print("\n--- CBC 模式 ---")
    try:
        cipher_cbc = SymmetricCipher.aes_cbc_encrypt_simple(plaintext, key, iv)
        decrypted_cbc = SymmetricCipher.aes_cbc_decrypt_simple(cipher_cbc, key, iv)
        print(f"IV (十六进制): {iv.hex()}")
        print(f"密文 (十六进制): {cipher_cbc.hex()[:64]}...")
        print(f"解密结果: {decrypted_cbc.decode()}")
        print(f"解密正确: {decrypted_cbc == plaintext}")
    except Exception as e:
        print(f"错误: {e}")

    # CTR 模式
    print("\n--- CTR 模式 ---")
    try:
        cipher_ctr = SymmetricCipher.aes_ctr_encrypt_simple(plaintext, key, nonce)
        decrypted_ctr = SymmetricCipher.aes_ctr_encrypt_simple(cipher_ctr, key, nonce)
        print(f"Nonce (十六进制): {nonce.hex()}")
        print(f"密文 (十六进制): {cipher_ctr.hex()[:64]}...")
        print(f"解密结果: {decrypted_ctr.decode()}")
        print(f"解密正确: {decrypted_ctr == plaintext}")
    except Exception as e:
        print(f"错误: {e}")

    # Base64 / Hex
    print("\n--- 编解码 ---")
    b64 = SymmetricCipher.bytes_to_base64(plaintext)
    hex_str = SymmetricCipher.bytes_to_hex(plaintext)
    print(f"Base64: {b64}")
    print(f"Hex: {hex_str[:64]}...")


def demo_asymmetric():
    """演示非对称加密"""
    print("\n" + "=" * 60)
    print("非对称加密（RSA）演示")
    print("=" * 60)

    print("\n正在生成 RSA 密钥对（512 位，仅用于演示）...")
    public_key, private_key = AsymmetricCipher.rsa_generate_keys(512)

    e, n = public_key
    d, _ = private_key

    print(f"\n公钥 (e, n):")
    print(f"  e = {e}")
    print(f"  n = {str(n)[:50]}...")
    print(f"\n私钥 (d, n):")
    print(f"  d = {str(d)[:50]}...")

    # 数字加密
    message = 42
    print(f"\n--- RSA 数字加密 ---")
    print(f"明文（数字）: {message}")
    ciphertext = AsymmetricCipher.rsa_encrypt(message, public_key)
    print(f"密文（数字）: {str(ciphertext)[:50]}...")
    decrypted = AsymmetricCipher.rsa_decrypt(ciphertext, private_key)
    print(f"解密结果: {decrypted}")
    print(f"解密正确: {decrypted == message}")

    # 数字签名
    print(f"\n--- RSA 数字签名 ---")
    msg_hash = 123456789  # 模拟消息哈希
    print(f"消息哈希: {msg_hash}")
    signature = AsymmetricCipher.rsa_sign(msg_hash, private_key)
    print(f"签名: {str(signature)[:50]}...")
    verified = AsymmetricCipher.rsa_verify(msg_hash, signature, public_key)
    print(f"验证结果: {'通过' if verified else '失败'}")

    # 文本加密
    print(f"\n--- RSA 文本加密 ---")
    plaintext = "Hello RSA!"
    print(f"明文: {plaintext}")
    try:
        cipher_hex = AsymmetricCipher.rsa_encrypt_text(plaintext, public_key)
        print(f"密文（十六进制）: {cipher_hex[:64]}...")
        decrypted_text = AsymmetricCipher.rsa_decrypt_text(cipher_hex, private_key)
        print(f"解密结果: {decrypted_text}")
        print(f"解密正确: {decrypted_text == plaintext}")
    except Exception as e:
        print(f"错误: {e}")


def demo_hash():
    """演示哈希算法"""
    print("\n" + "=" * 60)
    print("哈希算法演示")
    print("=" * 60)

    data = b"Hello, Hash World!"
    print(f"\n输入数据: {data.decode()}")

    # 各种哈希
    print("\n--- 哈希值对比 ---")
    print(f"MD5:     {HashUtils.md5(data)} ({len(HashUtils.md5(data)) * 4} 位)")
    print(f"SHA-1:   {HashUtils.sha1(data)} ({len(HashUtils.sha1(data)) * 4} 位)")
    print(f"SHA-256: {HashUtils.sha256(data)} ({len(HashUtils.sha256(data)) * 4} 位)")
    print(f"SHA-512: {HashUtils.sha512(data)[:64]}... ({len(HashUtils.sha512(data)) * 4} 位)")
    print(f"SM3(模拟): {HashUtils.sm3_simple(data)} (256 位)")

    # 雪崩效应演示
    print("\n--- 雪崩效应演示 ---")
    data2 = b"Hello, Hash World?"  # 只改了最后一个字符
    print(f"原输入:   {data.decode()}")
    print(f"修改后:   {data2.decode()}")
    print(f"原哈希:   {HashUtils.sha256(data)}")
    print(f"修改后:   {HashUtils.sha256(data2)}")

    # 比较差异位数
    hash1 = bytes.fromhex(HashUtils.sha256(data))
    hash2 = bytes.fromhex(HashUtils.sha256(data2))
    diff_bits = sum(bin(a ^ b).count('1') for a, b in zip(hash1, hash2))
    print(f"差异位数: {diff_bits} / 256 (约 {diff_bits / 256 * 100:.1f}%)")

    # HMAC
    print("\n--- HMAC 演示 ---")
    key = b"my_secret_key"
    message = b"Hello, HMAC!"
    hmac_val = HashUtils.hmac_manual(key, message, 'sha256')
    print(f"密钥: {key.decode()}")
    print(f"消息: {message.decode()}")
    print(f"HMAC-SHA256: {hmac_val}")

    # 密码哈希
    print("\n--- 密码哈希演示 ---")
    password = "MyP@ssw0rd123"
    pwd_hash, salt = HashUtils.password_hash(password)
    print(f"密码: {'*' * len(password)}")
    print(f"盐值: {salt.hex()}")
    print(f"哈希: {pwd_hash}")

    # 验证正确密码
    is_valid = HashUtils.password_verify(password, pwd_hash, salt)
    print(f"验证正确密码: {'通过' if is_valid else '失败'}")

    # 验证错误密码
    is_valid_wrong = HashUtils.password_verify("wrong_password", pwd_hash, salt)
    print(f"验证错误密码: {'通过' if is_valid_wrong else '失败'}")


def demo_password_strength():
    """演示密码强度检测"""
    print("\n" + "=" * 60)
    print("密码强度检测演示")
    print("=" * 60)

    test_passwords = [
        "123456",
        "password",
        "abc123",
        "Password123",
        "P@ssw0rd!",
        "MyStr0ng!P@ss#2024",
    ]

    for pwd in test_passwords:
        result = PasswordStrength.check_strength(pwd)
        print(f"\n密码: {pwd:<20} 分数: {result['score']:>3}/100  等级: {result['level']}")

    # 生成强密码
    print("\n--- 生成强密码 ---")
    strong_pwd = PasswordStrength.generate_strong_password(16)
    result = PasswordStrength.check_strength(strong_pwd)
    print(f"生成的密码: {strong_pwd}")
    print(f"强度等级: {result['level']} (分数: {result['score']}/100)")


def main():
    """主函数：运行所有演示"""
    print("=" * 60)
    print("  密码学工具集 (Crypto Toolkit)")
    print("  版本: 1.0")
    print("  用途: 学习演示，请勿用于生产环境")
    print("=" * 60)

    try:
        # 古典密码演示
        demo_classical_cipher()

        # 对称加密演示
        demo_symmetric()

        # 非对称加密演示
        demo_asymmetric()

        # 哈希算法演示
        demo_hash()

        # DH 密钥交换演示
        KeyExchange.dh_demo()

        # 密码强度检测演示
        demo_password_strength()

    except KeyboardInterrupt:
        print("\n\n用户中断。")
    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("演示结束！")
    print("=" * 60)


# 脚本入口
if __name__ == "__main__":
    main()
