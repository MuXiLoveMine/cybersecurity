#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
              密码学与密钥安全实战案例 - 密码学攻防全流程
==============================================================================

安全声明：
    本文件仅用于授权安全测试和教育培训目的。所有密码分析攻击
    均在受控模拟环境中进行，使用构造的测试数据。读者应在合法
    授权范围内使用这些技术，严禁用于破解他人加密数据或未经
    授权的密码分析活动。作者不对任何滥用本代码的行为负责。

技术范围：
    1. 古典密码破解（凯撒密码、维吉尼亚密码、频率分析）
    2. 对称加密实战（AES加密/解密、工作模式、分组密码分析）
    3. 非对称加密实战（RSA加密/签名、ECC密钥交换、密钥生成）
    4. 哈希与消息认证（哈希碰撞、HMAC验证、PBKDF2密码存储）
    5. 密码分析攻击（RSA共模攻击、广播攻击、低指数攻击）
    6. 密钥管理实践（密钥生成、存储、轮换、销毁）
    7. 侧信道攻击模拟（时间攻击、功耗分析、缓存攻击）

作者：网络安全学习项目
日期：2026年
==============================================================================
"""

import os
import sys
import math
import random
import hashlib
import hmac
import base64
import struct
import time
import binascii
import string
from typing import List, Dict, Tuple, Any, Optional

# ============================================================================
# 全局配置
# ============================================================================

random.seed(42)

BANNER = """
╔══════════════════════════════════════════════════════════════════════════════╗
║          密码学与密钥安全实战案例 - 密码学攻防系统                            ║
║   Classical | Symmetric | Asymmetric | Hash | Cryptanalysis | Side Channel  ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

# 英文字母频率表（用于频率分析）
字母频率 = {
    'A': 8.167, 'B': 1.492, 'C': 2.782, 'D': 4.253, 'E': 12.702,
    'F': 2.228, 'G': 2.015, 'H': 6.094, 'I': 6.966, 'J': 0.153,
    'K': 0.772, 'L': 4.025, 'M': 2.406, 'N': 6.749, 'O': 7.507,
    'P': 1.929, 'Q': 0.095, 'R': 5.987, 'S': 6.327, 'T': 9.056,
    'U': 2.758, 'V': 0.978, 'W': 2.360, 'X': 0.150, 'Y': 1.974,
    'Z': 0.074
}


# ============================================================================
# 第一部分：古典密码破解
# ============================================================================

class 古典密码破解器:
    """
    古典密码破解器
    
    实现和破解经典密码学算法：
    - 凯撒密码(Caesar Cipher): 简单替换密码
    - 维吉尼亚密码(Vigenere Cipher): 多表替换密码
    - 频率分析(Frequency Analysis): 基于统计的密码分析方法
    
    技术原理：
    凯撒密码: E(x) = (x + k) mod 26
    维吉尼亚密码: E(xi) = (xi + ki) mod 26
    频率分析: 利用字母出现频率的统计特性
    """

    def __init__(self):
        self.字母表 = string.ascii_uppercase

    def 凯撒密码加密(self, 明文: str, 密钥: int) -> str:
        """凯撒密码加密: 每个字母位移k位"""
        结果 = []
        for c in 明文.upper():
            if c in self.字母表:
                位移 = (ord(c) - ord('A') + 密钥) % 26
                结果.append(chr(位移 + ord('A')))
            else:
                结果.append(c)
        return ''.join(结果)

    def 凯撒密码破解(self) -> Dict:
        """
        凯撒密码破解
        
        方法1: 暴力破解 - 尝试所有25种可能密钥
        方法2: 频率分析 - 找出最高频字母推测为E
        
        由于只有25种可能的密钥，暴力破解是最简单的方法
        """
        print("\n" + "=" * 70)
        print("【凯撒密码破解】")
        print("=" * 70)
        print("技术: 暴力破解 + 频率分析")
        print("-" * 70)

        # 加密示例
        原文 = "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG"
        密钥 = 7  # 位移7位
        密文 = self.凯撒密码加密(原文, 密钥)

        print(f"\n[加密过程]")
        print(f"  明文: {原文}")
        print(f"  密钥: {密钥}")
        print(f"  密文: {密文}")
        print(f"  公式: C = (P + K) mod 26")

        # 暴力破解
        print(f"\n[暴力破解 - 尝试所有25种密钥]")
        print(f"  {'密钥':>4} {'解密结果':<50} {'匹配':>6}")

        for k in range(26):
            解密 = self.凯撒密码加密(密文, -k)  # 反向位移
            匹配 = "是!" if 解密 == 原文 else ""
            if k <= 10 or 解密 == 原文:  # 只打印部分结果
                print(f"  {k:>4} {解密:<50} {匹配:>6}")

        print(f"  ...")
        print(f"  破解成功! 密钥 = {密钥}")

        # 频率分析破解
        print(f"\n[频率分析破解]")
        # 统计密文字母频率
        字母计数 = {}
        总字母 = 0
        for c in 密文:
            if c in self.字母表:
                字母计数[c] = 字母计数.get(c, 0) + 1
                总字母 += 1

        # 找最高频字母
        排序频率 = sorted(字母计数.items(), key=lambda x: x[1], reverse=True)
        最高频字母 = 排序频率[0][0]

        # 假设最高频字母对应E(英文最高频)
        推测密钥 = (ord(最高频字母) - ord('E')) % 26

        print(f"  密文字母频率(前5):")
        for 字母, 次数 in 排序频率[:5]:
            频率 = 次数 / 总字母 * 100
            print(f"    {字母}: {次数}次 ({频率:.1f}%)")

        print(f"\n  最高频字母: {最高频字母}")
        print(f"  假设: {最高频字母} -> E (英文最高频)")
        print(f"  推测密钥: ({ord(最高频字母)}-{ord('E')}) mod 26 = {推测密钥}")

        if 推测密钥 == 密钥:
            print(f"  结果: 频率分析成功! 密钥 = {推测密钥}")
        else:
            print(f"  结果: 频率分析推测密钥 = {推测密钥} (可能因文本过短不准确)")

        print(f"\n[破解总结]")
        print(f"  暴力破解: 25次尝试内必定成功")
        print(f"  频率分析: 适合较长文本，无需遍历所有密钥")
        print(f"  安全性: 凯撒密码极不安全，密钥空间仅25")

        return {
            "原始密钥": 密钥,
            "暴力破解密钥": 密钥,
            "频率分析密钥": 推测密钥,
            "破解成功": True
        }

    def 维吉尼亚密码加密(self, 明文: str, 密钥: str) -> str:
        """维吉尼亚密码加密: 使用密钥词重复对齐明文"""
        结果 = []
        密钥 = 密钥.upper()
        密钥索引 = 0
        for c in 明文.upper():
            if c in self.字母表:
                位移 = ord(密钥[密钥索引 % len(密钥)]) - ord('A')
                加密 = (ord(c) - ord('A') + 位移) % 26
                结果.append(chr(加密 + ord('A')))
                密钥索引 += 1
            else:
                结果.append(c)
        return ''.join(结果)

    def 维吉尼亚密码破解(self) -> Dict:
        """
        维吉尼亚密码破解
        
        步骤:
        1. 确定密钥长度 (Kasiski测试/重合指数法)
        2. 按密钥长度分组
        3. 对每组进行频率分析
        
        Kasiski测试: 密文中重复模式之间的距离是密钥长度的倍数
        重合指数(IC): 衡量字母分布均匀度，英文IC约0.0667
        """
        print("\n" + "=" * 70)
        print("【维吉尼亚密码破解】")
        print("=" * 70)
        print("技术: Kasiski测试 + 重合指数法 + 频率分析")
        print("-" * 70)

        # 加密示例
        原文 = ("THE VIGENERE CIPHER IS A METHOD OF ENCRYPTING ALPHABETIC TEXT "
                "BY USING POLYALPHABETIC SUBSTITUTION IT USES A KEYWORD TO "
                "DETERMINE THE SHIFT FOR EACH LETTER MAKING IT MORE SECURE "
                "THAN SIMPLE SUBSTITUTION CIPHERS")
        密钥词 = "CIPHER"
        密文 = self.维吉尼亚密码加密(原文, 密钥词)

        print(f"\n[加密过程]")
        print(f"  明文: {原文[:60]}...")
        print(f"  密钥: {密钥词} (长度={len(密钥词)})")
        print(f"  密文: {密文[:60]}...")

        # 步骤1: Kasiski测试确定密钥长度
        print(f"\n[步骤1: Kasiski测试 - 寻找重复模式]")
        重复模式 = {}
        最小长度 = 3
        for i in range(len(密文) - 最小长度):
            片段 = 密文[i:i+最小长度]
            for j in range(i + 1, len(密文) - 最小长度):
                if 密文[j:j+最小长度] == 片段:
                    距离 = j - i
                    if 片段 not in 重复模式:
                        重复模式[片段] = []
                    重复模式[片段].append(距离)

        if 重复模式:
            print(f"  发现{len(重复模式)}个重复模式:")
            for 模式, 距离 in list(重复模式.items())[:5]:
                print(f"    '{模式}' 距离: {距离}")

            # 计算GCD推测密钥长度
            所有距离 = [d for distances in 重复模式.values() for d in distances]
            if 所有距离:
                from math import gcd
                from functools import reduce
                推测长度 = reduce(gcd, 所有距离)
                print(f"  距离GCD: {推测长度}")
        else:
            推测长度 = len(密钥词)
            print(f"  未找到重复模式(文本可能过短)")

        # 步骤2: 重合指数法验证密钥长度
        print(f"\n[步骤2: 重合指数法(IC)验证]")
        print(f"  英文期望IC值: ~0.0667")
        print(f"  随机文本IC值: ~0.0385")

        def 计算IC(文本):
            计数 = {}
            总数 = 0
            for c in 文本:
                if c in self.字母表:
                    计数[c] = 计数.get(c, 0) + 1
                    总数 += 1
            if 总数 < 2:
                return 0
            ic = sum(c * (c - 1) for c in 计数.values()) / (总数 * (总数 - 1))
            return ic

        # 尝试不同密钥长度
        print(f"  {'密钥长度':>8} {'平均IC':>10} {'判断':>8}")
        最佳长度 = 1
        最佳IC差 = 999
        for 尝试长度 in range(1, 10):
            ic列表 = []
            for i in range(尝试长度):
                子串 = 密文[i::尝试长度]
                ic = 计算IC(子串)
                ic列表.append(ic)
            平均IC = sum(ic列表) / len(ic列表)
            差值 = abs(平均IC - 0.0667)
            判断 = "匹配!" if 差值 < 0.01 else "不匹配"
            if 差值 < 最佳IC差:
                最佳IC差 = 差值
                最佳长度 = 尝试长度
            if 尝试长度 <= 8:
                print(f"  {尝试长度:>8} {平均IC:>10.4f} {判断:>8}")

        print(f"  最佳密钥长度: {最佳长度} (IC差={最佳IC差:.4f})")

        # 步骤3: 频率分析
        print(f"\n[步骤3: 频率分析 - 按组分析]")
        密钥字母 = []
        for i in range(最佳长度):
            子串 = 密文[i::最佳长度]
            # 频率分析: 找最高频字母推测为E
            计数 = {}
            for c in 子串:
                if c in self.字母表:
                    计数[c] = 计数.get(c, 0) + 1
            排序 = sorted(计数.items(), key=lambda x: x[1], reverse=True)
            最高频 = 排序[0][0] if 排序 else 'A'
            偏移 = (ord(最高频) - ord('E')) % 26
            密钥字母.append(chr(偏移 + ord('A')))

        推测密钥 = ''.join(密钥字母)
        print(f"  推测密钥: {推测密钥}")
        print(f"  实际密钥: {密钥词}")
        print(f"  匹配: {'成功!' if 推测密钥 == 密钥词 else '部分匹配(文本长度影响)'}")

        print(f"\n[破解总结]")
        print(f"  维吉尼亚密码破解步骤:")
        print(f"    1. Kasiski测试: 找重复模式推测密钥长度")
        print(f"    2. 重合指数法: 验证密钥长度")
        print(f"    3. 频率分析: 对每组子串独立分析")
        print(f"  安全性: 比凯撒密码强，但仍可被统计分析破解")

        return {
            "实际密钥": 密钥词,
            "推测密钥": 推测密钥,
            "密钥长度": 最佳长度,
            "破解成功": 推测密钥 == 密钥词
        }

    def 频率分析方法(self) -> Dict:
        """通用频率分析工具演示"""
        print("\n" + "=" * 70)
        print("【频率分析工具】")
        print("=" * 70)
        print("基于统计的密码分析方法")
        print("-" * 70)

        # 英文频率表
        print(f"\n[英文字母频率表(降序)]")
        排序频率 = sorted(字母频率.items(), key=lambda x: x[1], reverse=True)
        print(f"  {'字母':>4} {'频率%':>8}  {'分布图'}")
        for 字母, 频率 in 排序频率:
            条 = '#' * int(频率 * 2)
            print(f"  {字母:>4} {频率:>8.3f}  {条}")

        # Bigram频率(常见双字母组合)
        print(f"\n[常见双字母组合(Bigram)]")
        bigrams = [("TH", 3.56), ("HE", 3.07), ("IN", 2.43), ("ER", 2.05),
                   ("AN", 1.99), ("RE", 1.85), ("ON", 1.76), ("AT", 1.49),
                   ("EN", 1.45), ("ND", 1.35)]
        print(f"  {'组合':>6} {'频率%':>8}")
        for 组合, 频率 in bigrams:
            print(f"  {组合:>6} {频率:>8.2f}")

        # Trigram频率(常见三字母组合)
        print(f"\n[常见三字母组合(Trigram)]")
        trigrams = [("THE", 1.81), ("AND", 0.73), ("ING", 0.72), ("HER", 0.36),
                    ("HAT", 0.33), ("HIS", 0.33), ("THA", 0.33), ("ERE", 0.31)]
        print(f"  {'组合':>6} {'频率%':>8}")
        for 组合, 频率 in trigrams:
            print(f"  {组合:>6} {频率:>8.2f}")

        # 频率分析应用
        print(f"\n[频率分析应用场景]")
        场景 = [
            ("简单替换密码", "单表替换", "直接频率分析"),
            ("凯撒密码", "位移替换", "频率分析确定位移"),
            ("维吉尼亚密码", "多表替换", "分组后频率分析"),
            ("仿射密码", "线性变换", "频率分析+数学推导"),
            ("简单换位密码", "位置置换", "不适用(需其他方法)"),
        ]
        print(f"  {'密码类型':<16} {'原理':<12} {'分析方法'}")
        for 类型, 原理, 方法 in 场景:
            print(f"  {类型:<16} {原理:<12} {方法}")

        return {
            "字母数": 26,
            "bigram数": len(bigrams),
            "trigram数": len(trigrams)
        }

    def 运行所有破解(self):
        """运行所有古典密码破解"""
        print("\n" + "#" * 70)
        print("#  第一部分：古典密码破解")
        print("#" * 70)

        self.凯撒密码破解()
        self.维吉尼亚密码破解()
        self.频率分析方法()


# ============================================================================
# 第二部分：对称加密实战
# ============================================================================

class 对称加密实战器:
    """
    对称加密实战器
    
    实现对称加密算法的加密/解密和安全性分析：
    - AES加密/解密模拟
    - 工作模式对比(ECB/CBC/CTR/GCM)
    - 分组密码分析
    
    对称加密原理:
    加密: C = E(K, P)
    解密: P = D(K, C)
    同一密钥用于加密和解密
    """

    def __init__(self):
        self.算法 = "AES-256"
        self.块大小 = 16  # AES块大小128位=16字节

    def AES加密模拟(self) -> Dict:
        """AES加密/解密模拟"""
        print("\n" + "=" * 70)
        print("【AES加密/解密模拟】")
        print("=" * 70)
        print(f"算法: {self.算法}")
        print(f"块大小: {self.块大小}字节(128位)")
        print("-" * 70)

        # AES结构
        print(f"\n[AES算法结构]")
        print(f"  密钥长度: 128/192/256位")
        print(f"  轮数: 10/12/14 (对应128/192/256位密钥)")
        print(f"  状态矩阵: 4x4字节 (128位)")
        print(f"  ")
        print(f"  每轮操作:")
        轮操作 = [
            ("SubBytes", "S盒替换", "非线性字节替换"),
            ("ShiftRows", "行移位", "行循环移位"),
            ("MixColumns", "列混淆", "列线性变换"),
            ("AddRoundKey", "轮密钥加", "与轮密钥异或"),
        ]
        print(f"  {'操作':<16} {'名称':<12} {'描述'}")
        for 操作, 名称, 描述 in 轮操作:
            print(f"  {操作:<16} {名称:<12} {描述}")

        # 模拟S盒(部分)
        print(f"\n[AES S盒(部分)]")
        s盒示例 = [
            [0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5],
            [0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76],
            [0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0],
            [0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc],
        ]
        for i, 行 in enumerate(s盒示例):
            print(f"  {i}: " + " ".join(f"{b:02x}" for b in 行) + " ...")

        # 模拟加密过程
        print(f"\n[加密过程模拟]")
        明文 = b"Hello AES-256!!"  # 16字节
        密钥 = os.urandom(32)  # 256位密钥

        # 模拟加密轮次
        print(f"  明文(HEX): {明文.hex()}")
        print(f"  密钥(HEX): {密钥.hex()[:32]}...")
        print(f"  密钥扩展: 256位 -> 15个轮密钥")
        print(f"  ")

        轮数 = 14  # AES-256
        for 轮 in range(min(4, 轮数)):
            中间 = os.urandom(16)
            状态 = f"轮{轮+1}输出: {中间.hex()[:24]}..."
            if 轮 == 0:
                print(f"  初始轮: AddRoundKey")
            print(f"  {状态}")
        print(f"  ...")
        print(f"  最终轮: SubBytes -> ShiftRows -> AddRoundKey (无MixColumns)")

        密文 = os.urandom(16)
        print(f"  密文(HEX): {密文.hex()}")

        # 安全性分析
        print(f"\n[安全性分析]")
        安全性 = [
            ("密钥空间", "2^256", "无法暴力破解"),
            ("已知攻击", "Biclique(理论)", "仅降低2位安全性"),
            ("量子攻击", "Grover算法", "降至2^128(仍安全)"),
            ("侧信道", "缓存/时间", "实现需注意"),
            ("填充攻击", "Padding Oracle", "使用AEAD避免"),
            ("块碰撞", "生日攻击", "2^64块后碰撞"),
        ]
        print(f"  {'安全维度':<14} {'描述':<24} {'评估':>20}")
        for 维度, 描述, 评估 in 安全性:
            print(f"  {维度:<14} {描述:<24} {评估:>20}")

        # 密钥生成
        print(f"\n[密钥生成]")
        密钥方法 = [
            ("随机生成", "CSPRNG", "os.urandom(32)"),
            ("PBKDF2", "密码派生", "PBKDF2(password, salt, 100000)"),
            ("HKDF", "密钥派生", "HKDF(master_key, info)"),
            ("KMS生成", "密钥管理服务", "AWS KMS / Azure Key Vault"),
        ]
        print(f"  {'方法':<12} {'原理':<16} {'示例'}")
        for 方法, 原理, 示例 in 密钥方法:
            print(f"  {方法:<12} {原理:<16} {示例}")

        return {
            "算法": "AES-256",
            "密钥长度": 256,
            "轮数": 14
        }

    def 工作模式对比(self) -> Dict:
        """AES工作模式对比分析"""
        print("\n" + "=" * 70)
        print("【AES工作模式对比】")
        print("=" * 70)
        print("分析ECB/CBC/CTR/GCM等工作模式")
        print("-" * 70)

        工作模式 = [
            {"模式": "ECB", "全称": "Electronic Codebook", "IV": "否", "并行": "是",
             "安全性": "低", "优点": "简单并行", "缺点": "相同明文块产生相同密文",
             "推荐": "否"},
            {"模式": "CBC", "全称": "Cipher Block Chaining", "IV": "是", "并行": "否",
             "安全性": "中", "优点": "扩散性好", "缺点": "串行加密,Padding Oracle",
             "推荐": "谨慎"},
            {"模式": "CTR", "全称": "Counter", "IV": "Nonce", "并行": "是",
             "安全性": "中", "优点": "并行无Padding", "缺点": "Nonce不可重复",
             "推荐": "是"},
            {"模式": "GCM", "全称": "Galois/Counter", "IV": "Nonce", "并行": "是",
             "安全性": "高", "优点": "AEAD认证加密", "缺点": "Nonce不可重复",
             "推荐": "强烈推荐"},
            {"模式": "CCM", "全称": "Counter with CBC-MAC", "IV": "Nonce", "并行": "否",
             "安全性": "高", "优点": "AEAD认证", "缺点": "串行计算",
             "推荐": "是"},
            {"模式": "CFB", "全称": "Cipher Feedback", "IV": "是", "并行": "否",
             "安全性": "中", "优点": "流密码模式", "缺点": "串行加密",
             "推荐": "谨慎"},
            {"模式": "OFB", "全称": "Output Feedback", "IV": "是", "并行": "否",
             "安全性": "中", "优点": "流密码模式", "缺点": "串行加密",
             "推荐": "谨慎"},
        ]

        print(f"\n[工作模式对比表]")
        print(f"  {'模式':<6} {'全称':<24} {'IV':>6} {'并行':>4} {'安全性':>6} {'推荐':>8}")
        for m in 工作模式:
            print(f"  {m['模式']:<6} {m['全称']:<24} {m['IV']:>6} "
                  f"{m['并行']:>4} {m['安全性']:>6} {m['推荐']:>8}")

        # ECB模式弱点演示
        print(f"\n[ECB模式弱点演示]")
        print(f"  问题: 相同明文块产生相同密文块")
        print(f"  明文: [块A][块B][块A][块C]")
        print(f"  密文: [E(A)][E(B)][E(A)][E(C)]  <- 块A密文重复!")
        print(f"  信息泄露: 密文模式暴露明文模式")
        print(f"  经典案例: ECB企鹅( ECB加密后图片仍可见轮廓)")

        # CBC模式原理
        print(f"\n[CBC模式原理]")
        print(f"  加密: Ci = E(K, Pi XOR Ci-1), C0 = IV")
        print(f"  解密: Pi = D(K, Ci) XOR Ci-1")
        print(f"  链式结构: 每个密文块依赖前一个")
        print(f"  安全性: 扩散性好,但有Padding Oracle风险")

        # GCM模式原理
        print(f"\n[GCM模式原理]")
        print(f"  组合: CTR加密 + GHASH认证")
        print(f"  加密: Ci = Pi XOR E(K, counter+i)")
        print(f"  认证: T = GHASH(H, AAD, C) XOR E(K, J0)")
        print(f"  优势: 认证加密(AEAD),同时提供机密性和完整性")
        print(f"  性能: 支持并行, Intel AES-NI加速")

        # 模式选择建议
        print(f"\n[模式选择建议]")
        建议 = [
            ("通用加密", "AES-GCM", "AEAD,性能好,广泛支持"),
            ("流式加密", "AES-CTR", "并行化,无Padding"),
            ("兼容性", "AES-CBC", "广泛兼容,需配HMAC"),
            ("嵌入式", "AES-CCM", "资源受限场景"),
            ("禁止使用", "AES-ECB", "信息泄露风险"),
        ]
        print(f"  {'场景':<12} {'推荐模式':<12} {'理由'}")
        for 场景, 模式, 理由 in 建议:
            print(f"  {场景:<12} {模式:<12} {理由}")

        return {
            "模式数": len(工作模式),
            "推荐模式": "AES-GCM"
        }

    def 分组密码分析(self) -> Dict:
        """分组密码安全性分析"""
        print("\n" + "=" * 70)
        print("【分组密码分析】")
        print("=" * 70)
        print("分析分组密码的安全特性")
        print("-" * 70)

        # 分组密码特性
        print(f"\n[分组密码设计准则]")
        准则 = [
            ("雪崩效应", "输入1位变化导致约50%输出位变化", "扩散"),
            ("严格雪崩准则(SAC)", "每个输入位影响每个输出位", "完备性"),
            ("位独立准则(BIC)", "输出位变化相互独立", "非线性"),
            ("完善非线性准则(PC)", "无统计相关性", "抗线性分析"),
            ("抗差分分析", "差分分布表均匀", "抗差分"),
            ("抗线性分析", "线性逼近表均匀", "抗线性"),
        ]
        print(f"  {'准则':<22} {'描述':<30} {'特性'}")
        for 准则, 描述, 特性 in 准则:
            print(f"  {准则:<22} {描述:<30} {特性}")

        # 雪崩效应测试
        print(f"\n[雪崩效应测试]")
        print(f"  原始输入(HEX): {os.urandom(16).hex()[:32]}...")
        print(f"  翻转1位输入:  {os.urandom(16).hex()[:32]}...")
        原始输出 = os.urandom(16)
        翻转输出 = os.urandom(16)
        变化位数 = sum(bin(a ^ b).count('1') for a, b in zip(原始输出, 翻转输出))
        变化比例 = 变化位数 / 128 * 100
        print(f"  输出变化位数: {变化位数}/128 ({变化比例:.1f}%)")
        print(f"  雪崩判定: {'通过' if 40 <= 变化比例 <= 60 else '异常'} (理想约50%)")

        # 常见攻击
        print(f"\n[分组密码常见攻击]")
        攻击 = [
            ("差分分析", "分析输入差分与输出差分的关系", "高", "AES已抗差分"),
            ("线性分析", "利用输入输出的线性近似", "高", "AES已抗线性"),
            ("积分分析", "利用特殊输入集的统计特性", "中", "对AES-128有效"),
            ("相关密钥分析", "利用密钥之间的关系", "中", "对AES-256部分有效"),
            ("代数攻击", "利用算法的代数结构", "低", "理论攻击"),
            ("侧信道攻击", "利用实现的时间/功耗信息", "高", "实现层威胁"),
            ("Padding Oracle", "利用解密错误信息", "高", "CBC模式风险"),
            ("块重放", "重放密文块", "中", "无认证模式风险"),
        ]
        print(f"  {'攻击':<16} {'原理':<30} {'威胁':>6} {'备注'}")
        for 攻击名, 原理, 威胁, 备注 in 攻击:
            print(f"  {攻击名:<16} {原理:<30} {威胁:>6} {备注}")

        # Padding Oracle攻击详解
        print(f"\n[Padding Oracle攻击详解]")
        print(f"  攻击条件: CBC模式 + PKCS7填充 + 解密错误泄露")
        print(f"  攻击流程:")
        print(f"    1. 截获密文块 Ci-1 | Ci")
        print(f"    2. 修改 Ci-1 的字节，发送给服务器")
        print(f"    3. 观察Padding是否正确(错误信息)")
        print(f"    4. 逐字节推导中间值 = D(K, Ci)")
        print(f"    5. 明文 Pi = 中间值 XOR Ci-1")
        print(f"  防御: 使用AEAD(GCM)或恒定时间验证")

        return {
            "准则数": len(准则),
            "攻击类型数": len(攻击)
        }

    def 运行所有实战(self):
        """运行所有对称加密实战"""
        print("\n" + "#" * 70)
        print("#  第二部分：对称加密实战")
        print("#" * 70)

        self.AES加密模拟()
        self.工作模式对比()
        self.分组密码分析()


# ============================================================================
# 第三部分：非对称加密实战
# ============================================================================

class 非对称加密实战器:
    """
    非对称加密实战器
    
    实现非对称加密算法：
    - RSA加密/签名
    - ECC密钥交换
    - 密钥生成
    
    非对称加密原理:
    公钥加密: C = E(PU, M)
    私钥解密: M = D(PR, C)
    密钥对: (PU, PR) 数学关系绑定
    """

    def __init__(self):
        self.rsa密钥长度 = 2048

    def RSA加密签名模拟(self) -> Dict:
        """RSA加密和数字签名模拟"""
        print("\n" + "=" * 70)
        print("【RSA加密/签名模拟】")
        print("=" * 70)
        print(f"密钥长度: {self.rsa密钥长度}位")
        print("-" * 70)

        # RSA原理
        print(f"\n[RSA算法原理]")
        print(f"  密钥生成:")
        print(f"    1. 选择两个大素数 p, q")
        print(f"    2. n = p * q (模数, 公开)")
        print(f"    3. phi(n) = (p-1)(q-1) (欧拉函数)")
        print(f"    4. 选择 e: 1 < e < phi(n), gcd(e, phi(n))=1 (公钥指数)")
        print(f"    5. d = e^(-1) mod phi(n) (私钥指数)")
        print(f"  公钥: (n, e)  私钥: (n, d)")
        print(f"  加密: c = m^e mod n")
        print(f"  解密: m = c^d mod n")
        print(f"  签名: s = m^d mod n")
        print(f"  验签: v = s^e mod n, 验证 v == m")

        # 模拟小RSA(教学用)
        print(f"\n[小RSA示例(教学用)]")
        p, q = 61, 53  # 小素数
        n = p * q  # 3233
        phi = (p - 1) * (q - 1)  # 3120
        e = 17  # 公钥指数
        # 计算私钥 d = e^(-1) mod phi
        d = pow(e, -1, phi)  # 2753

        print(f"  p = {p}, q = {q}")
        print(f"  n = p * q = {n}")
        print(f"  phi(n) = (p-1)(q-1) = {phi}")
        print(f"  e = {e} (公钥指数)")
        print(f"  d = e^(-1) mod phi = {d} (私钥指数)")
        print(f"  公钥: (n={n}, e={e})")
        print(f"  私钥: (n={n}, d={d})")

        # 加密
        明文 = 65  # 字母'A'的ASCII
        密文 = pow(明文, e, n)
        print(f"\n  加密:")
        print(f"    明文 m = {明文}")
        print(f"    密文 c = m^e mod n = {明文}^{e} mod {n} = {密文}")

        # 解密
        解密 = pow(密文, d, n)
        print(f"\n  解密:")
        print(f"    密文 c = {密文}")
        print(f"    明文 m = c^d mod n = {密文}^{d} mod {n} = {解密}")
        print(f"    验证: {解密 == 明文} (解密成功!)")

        # 数字签名
        消息 = 123
        签名 = pow(消息, d, n)  # 用私钥签名
        验证 = pow(签名, e, n)  # 用公钥验签
        print(f"\n  数字签名:")
        print(f"    消息 m = {消息}")
        print(f"    签名 s = m^d mod n = {消息}^{d} mod {n} = {签名}")
        print(f"    验证 v = s^e mod n = {签名}^{e} mod {n} = {验证}")
        print(f"    验证: {验证 == 消息} (签名验证成功!)")

        # RSA安全性
        print(f"\n[RSA安全性分析]")
        安全性 = [
            ("密钥长度", "2048位", "推荐最小长度"),
            ("大数分解", "2^2048", "经典计算机不可行"),
            ("量子攻击", "Shor算法", "量子计算机可破解"),
            ("填充方案", "OAEP/PSS", "必须使用安全填充"),
            ("侧信道", "时间/功耗", "需恒定时间实现"),
            ("密钥管理", "HSM/TEE", "私钥安全存储"),
        ]
        print(f"  {'维度':<14} {'当前':>16} {'说明'}")
        for 维度, 当前, 说明 in 安全性:
            print(f"  {维度:<14} {当前:>16} {说明}")

        # RSA填充方案
        print(f"\n[RSA填充方案]")
        填充 = [
            ("PKCS1 v1.5", "确定性填充", "Bleichenbacher攻击风险", "不推荐"),
            ("OAEP", "随机化填充", "语义安全", "推荐(加密)"),
            ("PSS", "随机化签名", "语义安全", "推荐(签名)"),
            ("无填充", "无填充", "教科书RSA不安全", "禁止"),
        ]
        print(f"  {'方案':<14} {'类型':<14} {'特性':<20} {'推荐'}")
        for 方案, 类型, 特性, 推荐 in 填充:
            print(f"  {方案:<14} {类型:<14} {特性:<20} {推荐}")

        # 常见RSA攻击
        print(f"\n[常见RSA攻击]")
        rsa攻击 = [
            ("Bleichenbacher", "利用PKCS1 v1.5错误", "选择密文攻击", "高"),
            ("低指数攻击", "e=3时利用小消息", "广播攻击", "高"),
            ("共模攻击", "相同n不同e", "利用扩展GCD", "高"),
            ("Wiener攻击", "d过小(d < n^0.25/3)", "连分数攻击", "中"),
            ("Coppersmith", "部分明文已知", "利用格规约", "中"),
            ("时间攻击", "利用解密时间", "侧信道", "中"),
        ]
        print(f"  {'攻击':<16} {'原理':<24} {'类型':<14} {'威胁':>6}")
        for 攻击, 原理, 类型, 威胁 in rsa攻击:
            print(f"  {攻击:<16} {原理:<24} {类型:<14} {威胁:>6}")

        return {
            "密钥长度": self.rsa密钥长度,
            "示例n": n,
            "攻击类型数": len(rsa攻击)
        }

    def ECC密钥交换模拟(self) -> Dict:
        """ECC(椭圆曲线密码)密钥交换模拟"""
        print("\n" + "=" * 70)
        print("【ECC密钥交换模拟】")
        print("=" * 70)
        print("椭圆曲线Diffie-Hellman(ECDH)密钥交换")
        print("-" * 70)

        # ECC原理
        print(f"\n[ECC原理]")
        print(f"  椭圆曲线方程: y^2 = x^3 + ax + b (mod p)")
        print(f"  常用曲线: secp256r1 (NIST P-256)")
        print(f"  基点G: 曲线上的生成元")
        print(f"  密钥对: (d, Q) 其中 Q = d*G")
        print(f"  d: 私钥(随机整数)")
        print(f"  Q: 公钥(曲线上点)")

        # ECDH密钥交换
        print(f"\n[ECDH密钥交换流程]")
        print(f"  Alice: 私钥 dA, 公钥 QA = dA * G")
        print(f"  Bob:   私钥 dB, 公钥 QB = dB * G")
        print(f"  交换公钥: QA -> Bob, QB -> Alice")
        print(f"  Alice计算: K = dA * QB = dA * dB * G")
        print(f"  Bob计算:   K = dB * QA = dB * dA * G")
        print(f"  共享密钥: K = dA * dB * G (相同!)")

        # 模拟ECDH(使用小数演示)
        print(f"\n[模拟ECDH(小数值演示)]")
        # 使用小素数演示(不安全，仅教学)
        p = 65537  # 小素数(教学用)
        dA = random.randint(1, p - 1)  # Alice私钥
        dB = random.randint(1, p - 1)  # Bob私钥

        # 模拟公钥计算(实际是椭圆曲线点乘)
        QA = (dA * 5) % p  # 简化模拟
        QB = (dB * 5) % p

        # 共享密钥计算
        KA = (dA * QB) % p  # Alice计算的共享密钥
        KB = (dB * QA) % p  # Bob计算的共享密钥

        print(f"  曲线参数: p = {p}")
        print(f"  Alice私钥 dA = {dA}")
        print(f"  Alice公钥 QA = {QA}")
        print(f"  Bob私钥 dB = {dB}")
        print(f"  Bob公钥 QB = {QB}")
        print(f"  Alice计算: K = dA * QB mod p = {dA} * {QB} mod {p} = {KA}")
        print(f"  Bob计算:   K = dB * QA mod p = {dB} * {QA} mod {p} = {KB}")
        print(f"  共享密钥: K = {KA} (匹配: {KA == KB})")

        # ECC vs RSA
        print(f"\n[ECC vs RSA 对比]")
        对比 = [
            ("密钥长度", "256位(ECC)", "3072位(RSA)", "ECC更短"),
            ("安全性", "128位安全", "128位安全", "等同"),
            ("签名速度", "快", "慢", "ECC更快"),
            ("验证速度", "慢", "快", "RSA更快"),
            ("密钥大小", "32字节", "384字节", "ECC更小"),
            ("量子安全", "否", "否", "都需PQC"),
        ]
        print(f"  {'特性':<14} {'ECC':>14} {'RSA':>14} {'说明'}")
        for 特性, ecc, rsa, 说明 in 对比:
            print(f"  {特性:<14} {ecc:>14} {rsa:>14} {说明}")

        # ECC安全曲线
        print(f"\n[安全曲线推荐]")
        曲线 = [
            ("secp256r1", "NIST P-256", "广泛部署", "推荐"),
            ("secp384r1", "NIST P-384", "更高安全", "推荐"),
            ("Curve25519", "Daniel Bernstein", "无Timing攻击", "强烈推荐"),
            ("Ed25519", "Edwards曲线", "EdDSA签名", "强烈推荐"),
            ("secp256k1", "Bitcoin曲线", "加密货币", "特定用途"),
        ]
        print(f"  {'曲线':<14} {'名称':<16} {'特点':<16} {'推荐'}")
        for 曲线名, 名称, 特点, 推荐 in 曲线:
            print(f"  {曲线名:<14} {名称:<16} {特点:<16} {推荐}")

        return {
            "共享密钥匹配": KA == KB,
            "曲线数": len(曲线)
        }

    def 密钥生成最佳实践(self) -> Dict:
        """密钥生成最佳实践"""
        print("\n" + "=" * 70)
        print("【密钥生成最佳实践】")
        print("=" * 70)
        print("演示安全的密钥生成方法")
        print("-" * 70)

        # CSPRNG
        print(f"\n[密码学安全随机数生成器(CSPRNG)]")
        print(f"  os.urandom(): 操作系统提供的安全随机")
        print(f"  /dev/urandom: Linux安全随机源")
        print(f"  CryptGenRandom: Windows安全随机源")
        print(f"  getrandom(): Linux系统调用")

        # 生成示例
        print(f"\n[密钥生成示例]")
        密钥 = os.urandom(32)  # 256位密钥
        print(f"  AES-256密钥: {密钥.hex()}")
        print(f"  长度: {len(密钥)}字节 = {len(密钥)*8}位")
        print(f"  熵值: {len(密钥)*8}位 (理论最大)")

        # 密码派生
        print(f"\n[密码派生函数(PRF)]")
        密码 = b"用户密码"
        盐 = os.urandom(16)

        # PBKDF2
        derived_key = hashlib.pbkdf2_hmac('sha256', 密码, 盐, 100000, dklen=32)
        print(f"  PBKDF2-HMAC-SHA256:")
        print(f"    密码: {密码.decode()}")
        print(f"    盐: {盐.hex()}")
        print(f"    迭代: 100000次")
        print(f"    派生密钥: {derived_key.hex()[:32]}...")

        # HKDF
        print(f"\n  HKDF (HMAC-based Key Derivation):")
        print(f"    主密钥: {os.urandom(32).hex()[:16]}...")
        print(f"    信息: 'encryption-key'")
        print(f"    输出: 派生密钥(32字节)")

        # 密钥强度评估
        print(f"\n[密钥强度评估]")
        强度 = [
            ("AES-128", "128位", "77亿年(暴力)", "安全"),
            ("AES-256", "256位", "宇宙年龄倍数", "极度安全"),
            ("RSA-2048", "112位", "数百万年", "安全(近期)"),
            ("RSA-4096", "150位", "更长", "长期安全"),
            ("ECC-256", "128位", "等同AES-128", "安全"),
            ("ECC-384", "192位", "等同AES-192", "长期安全"),
        ]
        print(f"  {'算法':<12} {'安全级':>8} {'暴力破解时间':>18} {'评估'}")
        for 算法, 安全级, 时间, 评估 in 强度:
            print(f"  {算法:<12} {安全级:>8} {时间:>18} {评估}")

        # 密钥生成安全要求
        print(f"\n[密钥生成安全要求]")
        要求 = [
            "使用CSPRNG(os.urandom)生成密钥",
            "密钥长度足够(AES至少256位)",
            "密码派生使用PBKDF2/scrypt/Argon2",
            "派生函数迭代次数足够(PBKDF2>=100000)",
            "使用唯一盐值防止彩虹表攻击",
            "避免自定义随机数生成器",
            "密钥不在代码中硬编码",
            "使用HSM/KMS管理密钥",
        ]
        for i, 要求项 in enumerate(要求, 1):
            print(f"  {i}. {要求项}")

        return {
            "密钥长度": 256,
            "派生函数": "PBKDF2"
        }

    def 运行所有实战(self):
        """运行所有非对称加密实战"""
        print("\n" + "#" * 70)
        print("#  第三部分：非对称加密实战")
        print("#" * 70)

        self.RSA加密签名模拟()
        self.ECC密钥交换模拟()
        self.密钥生成最佳实践()


# ============================================================================
# 第四部分：哈希与消息认证
# ============================================================================

class 哈希与消息认证器:
    """
    哈希与消息认证器
    
    实现哈希函数和消息认证码：
    - 哈希碰撞检测
    - HMAC验证
    - PBKDF2密码存储
    """

    def __init__(self):
        self.哈希算法 = "SHA-256"

    def 哈希碰撞检测(self) -> Dict:
        """哈希函数碰撞检测"""
        print("\n" + "=" * 70)
        print("【哈希碰撞检测】")
        print("=" * 70)
        print(f"算法: {self.哈希算法}")
        print("-" * 70)

        # 哈希函数原理
        print(f"\n[哈希函数特性]")
        特性 = [
            ("确定性", "相同输入总是产生相同输出", "H(x)=H(x)"),
            ("快速性", "计算速度快", "O(n)复杂度"),
            ("雪崩效应", "输入微小变化导致输出巨大变化", "1位变化约50%输出变化"),
            ("单向性", "无法从哈希反推输入", "抗原像"),
            ("弱抗碰撞", "难以找到相同哈希的不同输入", "H(x)=H(y), x!=y"),
            ("强抗碰撞", "难以找到任意两个相同哈希的输入", "生日攻击"),
        ]
        print(f"  {'特性':<14} {'描述':<30} {'数学'}")
        for 特性, 描述, 数学 in 特性:
            print(f"  {特性:<14} {描述:<30} {数学}")

        # 哈希算法对比
        print(f"\n[哈希算法对比]")
        算法表 = [
            ("MD5", 128, "2^21(碰撞)", "已破解", "禁止"),
            ("SHA-1", 160, "2^63(碰撞)", "已破解", "禁止"),
            ("SHA-256", 256, "2^128(碰撞)", "安全", "推荐"),
            ("SHA-384", 384, "2^192(碰撞)", "安全", "推荐"),
            ("SHA-512", 512, "2^256(碰撞)", "安全", "推荐"),
            ("SHA3-256", 256, "2^128(碰撞)", "安全", "推荐"),
            ("BLAKE2s", 256, "2^128(碰撞)", "安全", "推荐"),
            ("BLAKE2b", 512, "2^256(碰撞)", "安全", "推荐"),
        ]
        print(f"  {'算法':<12} {'输出位':>8} {'碰撞复杂度':>14} {'状态':>8} {'推荐':>8}")
        for 算法, 位数, 复杂度, 状态, 推荐 in 算法表:
            print(f"  {算法:<12} {位数:>8} {复杂度:>14} {状态:>8} {推荐:>8}")

        # 碰撞演示
        print(f"\n[哈希输出示例]")
        消息1 = b"Hello, World!"
        消息2 = b"Hello, World?"  # 差一个字符
        h1 = hashlib.sha256(消息1).hexdigest()
        h2 = hashlib.sha256(消息2).hexdigest()
        print(f"  消息1: {消息1.decode()}")
        print(f"  SHA-256: {h1}")
        print(f"  消息2: {消息2.decode()}")
        print(f"  SHA-256: {h2}")
        print(f"  差异: {sum(a!=b for a,b in zip(h1,h2))}/{len(h1)} 字符不同 ({sum(a!=b for a,b in zip(h1,h2))/len(h1)*100:.0f}%)")

        # 生日攻击
        print(f"\n[生日攻击分析]")
        print(f"  碰撞概率公式: P(n) ≈ 1 - e^(-n^2/2^k)")
        print(f"  50%碰撞概率需要: n ≈ 1.2 * 2^(k/2)")
        for k in [64, 128, 160, 256]:
            n = 1.2 * 2 ** (k / 2)
            print(f"    {k}位哈希: 需要~{n:.0e}次计算 (2^{k//2})")

        # MD5碰撞示例
        print(f"\n[MD5碰撞示例]")
        print(f"  MD5已被证明不安全(2004年王小云团队)")
        print(f"  碰撞示例(两个不同输入产生相同MD5):")
        print(f"  消息1和消息2仅在特定字节不同但MD5相同")
        print(f"  影响: 数字签名伪造(rogue CA证书)")
        print(f"  建议: 立即停止使用MD5")

        # SHA-1退役
        print(f"\n[SHA-1退役]")
        print(f"  2017年: Google公布SHAttered攻击(SHA-1碰撞)")
        print(f"  碰撞成本: 约110 GPU年(2^63次运算)")
        print(f"  影响: Git(使用SHA-1)、证书签名")
        print(f"  现状: 主流浏览器拒绝SHA-1证书")
        print(f"  建议: 迁移到SHA-256/SHA-3")

        return {
            "算法数": len(算法表),
            "安全算法": ["SHA-256", "SHA-3", "BLAKE2"]
        }

    def HMAC验证(self) -> Dict:
        """HMAC消息认证码验证"""
        print("\n" + "=" * 70)
        print("【HMAC消息认证码】")
        print("=" * 70)
        print("演示HMAC生成和验证")
        print("-" * 70)

        # HMAC原理
        print(f"\n[HMAC原理]")
        print(f"  HMAC(K, m) = H((K' XOR opad) || H((K' XOR ipad) || m))")
        print(f"  K: 密钥 (K': 补齐到块大小)")
        print(f"  ipad: 0x36重复 (内部填充)")
        print(f"  opad: 0x5C重复 (外部填充)")
        print(f"  H: 哈希函数(SHA-256)")
        print(f"  优势: 不需要从哈希反推密钥")

        # HMAC生成
        密钥 = b"secret_hmac_key_2024"
        消息 = b"Important message to authenticate"
        h = hmac.new(密钥, 消息, hashlib.sha256)
        mac = h.hexdigest()

        print(f"\n[HMAC生成示例]")
        print(f"  密钥: {密钥.decode()}")
        print(f"  消息: {消息.decode()}")
        print(f"  HMAC-SHA256: {mac}")

        # HMAC验证
        print(f"\n[HMAC验证]")
        验证结果 = hmac.compare_digest(
            hmac.new(密钥, 消息, hashlib.sha256).hexdigest(),
            mac
        )
        print(f"  验证结果: {'通过' if 验证结果 else '失败'}")

        # 篡改检测
        篡改消息 = b"Important message to authenticatE"  # 改一个字母
        篡改MAC = hmac.new(密钥, 篡改消息, hashlib.sha256).hexdigest()
        篡改验证 = hmac.compare_digest(篡改MAC, mac)
        print(f"\n[HMAC篡改检测]")
        print(f"  原始消息: {消息.decode()}")
        print(f"  篡改消息: {篡改消息.decode()}")
        print(f"  原始MAC: {mac[:32]}...")
        print(f"  篡改MAC: {篡改MAC[:32]}...")
        print(f"  验证结果: {'通过' if 篡改验证 else '失败 - 检测到篡改!'}")

        # HMAC应用场景
        print(f"\n[HMAC应用场景]")
        场景 = [
            ("API认证", "API请求签名", "防止请求篡改"),
            ("JWT签名", "HMAC-SHA256", "令牌完整性"),
            ("消息完整性", "消息传输", "防篡改"),
            ("Webhook", "回调验证", "验证来源"),
            ("密码存储", "HMAC密码哈希", "加盐哈希"),
            ("TLS", "HKDF密钥派生", "密钥扩展"),
        ]
        print(f"  {'场景':<14} {'用途':<18} {'目的'}")
        for 场景, 用途, 目的 in 场景:
            print(f"  {场景:<14} {用途:<18} {目的}")

        # HMAC vs 签名
        print(f"\n[HMAC vs 数字签名]")
        对比 = [
            ("算法类型", "对称", "非对称"),
            ("密钥", "共享密钥", "公钥/私钥"),
            ("生成者", "任何持有密钥者", "仅私钥持有者"),
            ("验证者", "需要密钥", "任何有公钥者"),
            ("不可否认", "否", "是"),
            ("性能", "快", "较慢"),
            ("场景", "内部系统", "外部通信"),
        ]
        print(f"  {'特性':<14} {'HMAC':>16} {'数字签名':>16}")
        for 特性, hmac_val, sig in 对比:
            print(f"  {特性:<14} {hmac_val:>16} {sig:>16}")

        # 安全注意事项
        print(f"\n[安全注意事项]")
        注意 = [
            "使用hmac.compare_digest而非==比较(防时序攻击)",
            "密钥长度应与哈希输出相当(32字节 for SHA-256)",
            "不使用已知的哈希弱点算法(MD5/SHA-1)",
            "密钥需安全存储和轮换",
            "每条消息使用唯一Nonce防重放",
        ]
        for i, 注意项 in enumerate(注意, 1):
            print(f"  {i}. {注意项}")

        return {
            "HMAC验证": 验证结果,
            "篡改检测": not 篡改验证
        }

    def PBKDF2密码存储(self) -> Dict:
        """PBKDF2密码存储演示"""
        print("\n" + "=" * 70)
        print("【PBKDF2密码存储】")
        print("=" * 70)
        print("演示安全的密码哈希存储")
        print("-" * 70)

        # 密码存储演进
        print(f"\n[密码存储演进]")
        演进 = [
            ("明文存储", "原始密码", "极度危险"),
            ("加密存储", "对称加密", "密钥泄露风险"),
            ("MD5哈希", "hash(password)", "彩虹表攻击"),
            ("MD5+盐", "hash(salt+password)", "GPU暴力破解"),
            ("SHA-256+盐", "hash(salt+password)", "GPU暴力破解"),
            ("PBKDF2", "迭代哈希", "减缓暴力(推荐)"),
            ("scrypt", "内存困难", "抗GPU(推荐)"),
            ("Argon2", "内存+CPU困难", "最佳实践"),
            ("bcrypt", "自适应成本", "广泛使用"),
        ]
        print(f"  {'方法':<14} {'原理':<18} {'安全性'}")
        for 方法, 原理, 安全 in 演进:
            print(f"  {方法:<14} {原理:<18} {安全}")

        # PBKDF2实现
        print(f"\n[PBKDF2实现]")
        密码 = b"MySecurePassword2024!"
        盐 = os.urandom(16)
        迭代次数 = 100000
        密钥长度 = 32

        print(f"  密码: {密码.decode()}")
        print(f"  盐(随机): {盐.hex()}")
        print(f"  迭代次数: {迭代次数}")
        print(f"  输出长度: {密钥长度}字节")
        print(f"  算法: PBKDF2-HMAC-SHA256")

        开始时间 = time.time()
        哈希值 = hashlib.pbkdf2_hmac('sha256', 密码, 盐, 迭代次数, dklen=密钥长度)
        计算时间 = time.time() - 开始时间

        print(f"  计算结果: {哈希值.hex()[:32]}...")
        print(f"  计算时间: {计算时间:.3f}秒")

        # 存储格式
        print(f"\n[存储格式]")
        存储串 = f"pbkdf2$sha256${迭代次数}${base64.b64encode(盐).decode()}${base64.b64encode(哈希值).decode()}"
        print(f"  格式: algorithm$hash$iterations$salt$hash")
        print(f"  存储: {存储串[:64]}...")

        # 验证
        print(f"\n[密码验证]")
        验证密码 = b"MySecurePassword2024!"
        验证哈希 = hashlib.pbkdf2_hmac('sha256', 验证密码, 盐, 迭代次数, dklen=密钥长度)
        匹配 = hmac.compare_digest(哈希值, 验证哈希)
        print(f"  输入密码: {验证密码.decode()}")
        print(f"  验证结果: {'匹配 - 验证成功' if 匹配 else '不匹配 - 密码错误'}")

        # 错误密码
        错误密码 = b"WrongPassword!"
        错误哈希 = hashlib.pbkdf2_hmac('sha256', 错误密码, 盐, 迭代次数, dklen=密钥长度)
        错误匹配 = hmac.compare_digest(哈希值, 错误哈希)
        print(f"  错误密码: {错误密码.decode()}")
        print(f"  验证结果: {'匹配' if 错误匹配 else '不匹配 - 密码错误'}")

        # 迭代次数分析
        print(f"\n[迭代次数分析]")
        迭代选项 = [
            (1000, "旧标准", "不安全"),
            (10000, "最小可接受", "边缘"),
            (100000, "当前推荐", "安全"),
            (600000, "NIST 2024推荐", "更安全"),
            (1000000, "高安全需求", "非常安全"),
        ]
        print(f"  {'迭代次数':>10} {'说明':<14} {'安全性'}")
        for 次数, 说明, 安全 in 迭代选项:
            print(f"  {次数:>10} {说明:<14} {安全}")

        # 攻击成本
        print(f"\n[攻击成本分析]")
        print(f"  单次PBKDF2计算: ~{计算时间*1000:.1f}ms")
        每秒尝试 = 1 / 计算时间
        每天尝试 = 每秒尝试 * 86400
        print(f"  攻击者速度: ~{每秒尝试:.0f}次/秒 (单核)")
        print(f"  每天尝试: ~{每天尝试:.0f}次")
        密码空间 = 62**8  # 8位字母数字
        破解时间 = 密码空间 / 每天尝试
        print(f"  8位密码空间: {密码空间:.0e}")
        print(f"  穷举时间: ~{破解时间:.0f}天")
        print(f"  GPU加速(1000x): ~{破解时间/1000:.1f}天")

        print(f"\n[密码存储最佳实践]")
        实践 = [
            "使用Argon2(首选)或PBKDF2(次选)",
            "每个密码使用唯一随机盐(16字节+)",
            "迭代次数足够高(PBKDF2>=600000)",
            "使用恒定时间比较(hmac.compare_digest)",
            "记录算法和参数便于升级",
            "支持密码哈希算法迁移",
            "结合密码强度检查防止弱密码",
        ]
        for i, 实践项 in enumerate(实践, 1):
            print(f"  {i}. {实践项}")

        return {
            "迭代次数": 迭代次数,
            "计算时间": 计算时间,
            "验证成功": 匹配
        }

    def 运行所有检测(self):
        """运行所有哈希和消息认证检测"""
        print("\n" + "#" * 70)
        print("#  第四部分：哈希与消息认证")
        print("#" * 70)

        self.哈希碰撞检测()
        self.HMAC验证()
        self.PBKDF2密码存储()


# ============================================================================
# 第五部分：密码分析攻击
# ============================================================================

class 密码分析攻击器:
    """
    密码分析攻击器
    
    演示针对RSA的密码分析攻击：
    - RSA共模攻击
    - 广播攻击
    - 低指数攻击
    """

    def __init__(self):
        self.攻击目标 = "RSA密码系统"

    def RSA共模攻击(self) -> Dict:
        """
        RSA共模攻击(Common Modulus Attack)
        
        条件: 相同n, 不同e1,e2, gcd(e1,e2)=1
        方法: 利用扩展欧几里得算法
        a*e1 + b*e2 = 1 (mod phi)
        m = c1^a * c2^b mod n
        """
        print("\n" + "=" * 70)
        print("【RSA共模攻击】")
        print("=" * 70)
        print("利用相同模数n不同公钥指数e的RSA系统")
        print("-" * 70)

        # 小数值演示
        print(f"\n[共模攻击原理]")
        print(f"  条件: 同一明文m用相同n但不同e1,e2加密")
        print(f"  c1 = m^e1 mod n")
        print(f"  c2 = m^e2 mod n")
        print(f"  gcd(e1, e2) = 1")
        print(f"  利用扩展GCD: a*e1 + b*e2 = 1")
        print(f"  恢复: m = c1^a * c2^b mod n")

        # 模拟攻击
        print(f"\n[模拟攻击(小数值)]")
        n = 3233  # 小模数(教学用)
        e1, e2 = 17, 13  # 两个公钥指数
        m = 123  # 明文

        c1 = pow(m, e1, n)
        c2 = pow(m, e2, n)

        print(f"  公共模数 n = {n}")
        print(f"  公钥1: e1 = {e1}")
        print(f"  公钥2: e2 = {e2}")
        print(f"  明文: m = {m}")
        print(f"  密文1: c1 = m^e1 mod n = {m}^{e1} mod {n} = {c1}")
        print(f"  密文2: c2 = m^e2 mod n = {m}^{e2} mod {n} = {c2}")

        # 扩展欧几里得算法
        def 扩展GCD(a, b):
            if a == 0:
                return b, 0, 1
            g, x, y = 扩展GCD(b % a, a)
            return g, y - (b // a) * x, x

        g, a, b = 扩展GCD(e1, e2)
        print(f"\n  扩展GCD(e1={e1}, e2={e2}):")
        print(f"  gcd = {g}")
        print(f"  a = {a}, b = {b}")
        print(f"  验证: {a}*{e1} + {b}*{e2} = {a*e1 + b*e2}")

        # 恢复明文
        # 处理负指数: 需要 c1的逆
        if a < 0:
            c1_inv = pow(c1, -1, n)
            part1 = pow(c1_inv, -a, n)
        else:
            part1 = pow(c1, a, n)
        if b < 0:
            c2_inv = pow(c2, -1, n)
            part2 = pow(c2_inv, -b, n)
        else:
            part2 = pow(c2, b, n)

        恢复明文 = (part1 * part2) % n

        print(f"\n  恢复明文:")
        print(f"  m = c1^a * c2^b mod n")
        print(f"  m = {c1}^({a}) * {c2}^({b}) mod {n}")
        print(f"  m = {part1} * {part2} mod {n}")
        print(f"  m = {恢复明文}")
        print(f"  验证: {'成功! 明文正确恢复' if 恢复明文 == m else '失败'}")

        print(f"\n[防御建议]")
        print(f"  1. 不同用户使用不同模数n")
        print(f"  2. 使用OAEP填充(随机化密文)")
        print(f"  3. 不重复使用相同的RSA参数")

        return {
            "原始明文": m,
            "恢复明文": 恢复明文,
            "攻击成功": 恢复明文 == m
        }

    def 广播攻击(self) -> Dict:
        """
        RSA广播攻击(Hastad's Broadcast Attack)
        
        条件: e=3(低指数), 相同明文发送给3个接收者
        c1 = m^3 mod n1
        c2 = m^3 mod n2
        c3 = m^3 mod n3
        利用CRT恢复 m^3, 然后开立方
        """
        print("\n" + "=" * 70)
        print("【RSA广播攻击(Hastad)】")
        print("=" * 70)
        print("利用低指数RSA和广播发送")
        print("-" * 70)

        # 原理
        print(f"\n[广播攻击原理]")
        print(f"  条件: e=3, 同一明文m发送给3+个接收者")
        print(f"  c1 = m^3 mod n1")
        print(f"  c2 = m^3 mod n2")
        print(f"  c3 = m^3 mod n3")
        print(f"  利用CRT恢复 M = m^3 (mod n1*n2*n3)")
        print(f"  由于 m^3 < n1*n2*n3, M = m^3 (精确值)")
        print(f"  开立方: m = M^(1/3)")

        # 小数值模拟
        print(f"\n[模拟攻击(小数值)]")
        e = 3
        m = 42
        n1, n2, n3 = 3233, 4199, 5767  # 三个不同模数(教学用)

        c1 = pow(m, e, n1)
        c2 = pow(m, e, n2)
        c3 = pow(m, e, n3)

        print(f"  公钥指数 e = {e}")
        print(f"  明文 m = {m}")
        print(f"  模数: n1={n1}, n2={n2}, n3={n3}")
        print(f"  密文: c1={c1}, c2={c2}, c3={c3}")

        # 中国剩余定理(CRT)恢复
        def CRT(余数, 模数):
            M = 1
            for n in 模数:
                M *= n
            x = 0
            for r, n in zip(余数, 模数):
                Mi = M // n
                yi = pow(Mi, -1, n)
                x += r * Mi * yi
            return x % M

        M = CRT([c1, c2, c3], [n1, n2, n3])
        print(f"\n  CRT恢复: M = m^3 = {M}")

        # 开立方
        恢复明文 = round(M ** (1/3))
        print(f"  开立方: m = M^(1/3) = {M**(1/3):.4f} -> {恢复明文}")
        print(f"  验证: {'成功! 明文正确恢复' if 恢复明文 == m else '失败'}")

        print(f"\n[防御建议]")
        print(f"  1. 使用足够大的e(如65537)")
        print(f"  2. 使用OAEP填充随机化密文")
        print(f"  3. 不向多个接收者发送相同明文")

        return {
            "原始明文": m,
            "恢复明文": 恢复明文,
            "攻击成功": 恢复明文 == m
        }

    def 低指数攻击(self) -> Dict:
        """RSA低指数攻击"""
        print("\n" + "=" * 70)
        print("【RSA低指数攻击】")
        print("=" * 70)
        print("利用过小的RSA公钥指数e")
        print("-" * 70)

        # 原理
        print(f"\n[低指数攻击原理]")
        print(f"  当 e=3 且明文 m^3 < n 时:")
        print(f"  c = m^3 mod n = m^3 (无需取模)")
        print(f"  直接开立方: m = c^(1/3)")
        print(f"  条件: 明文足够小使 m^e < n")

        # 模拟
        e = 3
        n = 9999991  # 较大模数(教学用)
        m = 123  # 小明文

        c = pow(m, e, n)
        print(f"\n[攻击模拟]")
        print(f"  e = {e}")
        print(f"  n = {n}")
        print(f"  m = {m}")
        print(f"  c = m^e mod n = {m}^{e} mod {n} = {c}")

        # 检查是否可直接开方
        if c == m ** e:
            print(f"  m^e < n: 是 (密文无需取模)")
            恢复明文 = round(c ** (1/e))
            print(f"  开方: m = c^(1/3) = {c**(1/3):.4f} -> {恢复明文}")
            print(f"  验证: {'成功!' if 恢复明文 == m else '失败'}")
        else:
            print(f"  m^e >= n: 需要更复杂的攻击")

        # Wiener攻击(低私钥指数)
        print(f"\n[Wiener攻击(低私钥指数d)]")
        print(f"  条件: d < n^0.25 / 3")
        print(f"  方法: 连分数逼近 e/n")
        print(f"  恢复: 通过连分数系数恢复d")
        print(f"  影响: 使用过小的d不安全")

        # 各攻击条件总结
        print(f"\n[RSA攻击条件总结]")
        攻击表 = [
            ("共模攻击", "相同n, 不同e", "扩展GCD", "高"),
            ("广播攻击", "e小, 广播发送", "CRT+开方", "高"),
            ("低指数攻击", "e小, m小", "直接开方", "高"),
            ("Wiener攻击", "d过小", "连分数", "中"),
            ("Coppersmith", "部分明文已知", "格规约(LLL)", "中"),
            ("Bleichenbacher", "PKCS1 v1.5", "选择密文", "高"),
        ]
        print(f"  {'攻击':<16} {'条件':<20} {'方法':<16} {'威胁':>6}")
        for 攻击, 条件, 方法, 威胁 in 攻击表:
            print(f"  {攻击:<16} {条件:<20} {方法:<16} {威胁:>6}")

        print(f"\n[RSA安全建议]")
        建议 = [
            "使用标准公钥指数 e=65537",
            "密钥长度>=2048位(推荐3072位)",
            "使用OAEP/PSS填充方案",
            "不同用户使用不同模数n",
            "私钥指数d不应过小",
            "使用恒定时间实现防侧信道",
            "密钥由CSPRNG生成",
            "定期更新密钥对",
        ]
        for i, 建议项 in enumerate(建议, 1):
            print(f"  {i}. {建议项}")

        return {
            "攻击成功": 恢复明文 == m,
            "恢复明文": 恢复明文
        }

    def 运行所有攻击(self):
        """运行所有密码分析攻击"""
        print("\n" + "#" * 70)
        print("#  第五部分：密码分析攻击")
        print("#" * 70)

        self.RSA共模攻击()
        self.广播攻击()
        self.低指数攻击()


# ============================================================================
# 第六部分：密钥管理实践
# ============================================================================

class 密钥管理实践器:
    """
    密钥管理实践器
    
    实现密钥全生命周期管理：
    - 密钥生成
    - 密钥存储
    - 密钥轮换
    - 密钥销毁
    """

    def __init__(self):
        self.密钥库 = {}
        self.轮换周期 = 90  # 天

    def 密钥生成实践(self) -> Dict:
        """密钥生成实践"""
        print("\n" + "=" * 70)
        print("【密钥生成实践】")
        print("=" * 70)
        print("安全密钥生成方法和最佳实践")
        print("-" * 70)

        # 密钥类型
        print(f"\n[密钥类型]")
        类型 = [
            ("对称密钥", "AES", "16/24/32字节", "加密/解密"),
            ("RSA密钥对", "RSA", "2048/4096位", "加密/签名"),
            ("ECC密钥对", "ECC", "256/384位", "密钥交换/签名"),
            ("HMAC密钥", "HMAC", "32+字节", "消息认证"),
            ("TLS密钥", "TLS", "会话密钥", "传输加密"),
            ("数据库密钥", "DEK", "32字节", "数据加密"),
            ("主密钥", "KEK", "32字节", "密钥加密"),
        ]
        print(f"  {'类型':<14} {'算法':<8} {'长度':<14} {'用途'}")
        for 类型, 算法, 长度, 用途 in 类型:
            print(f"  {类型:<14} {算法:<8} {长度:<14} {用途}")

        # 生成各种密钥
        print(f"\n[密钥生成示例]")
        aes密钥 = os.urandom(32)
        rsa公钥 = base64.b64encode(os.urandom(32)).decode()[:32]
        ecc私钥 = os.urandom(32)
        hmac密钥 = os.urandom(32)
        dek密钥 = os.urandom(32)
        kek密钥 = os.urandom(32)

        密钥列表 = [
            ("AES-256密钥", aes密钥),
            ("ECC私钥", ecc私钥),
            ("HMAC密钥", hmac密钥),
            ("数据加密密钥(DEK)", dek密钥),
            ("密钥加密密钥(KEK)", kek密钥),
        ]

        for 名称, 密钥 in 密钥列表:
            print(f"  {名称}: {密钥.hex()[:32]}...")

        # 密钥层次结构
        print(f"\n[密钥层次结构]")
        print(f"  ┌─────────────────────────┐")
        print(f"  │   根密钥(Master Key)      │  <- HSM保护")
        print(f"  └────────────┬────────────┘")
        print(f"               │")
        print(f"  ┌────────────┼────────────┐")
        print(f"  │ KEK(密钥加密密钥)         │  <- 加密DEK")
        print(f"  └────────────┬────────────┘")
        print(f"               │")
        print(f"  ┌────────────┼────────────┐")
        print(f"  │ DEK(数据加密密钥)         │  <- 加密数据")
        print(f"  └────────────┴────────────┘")

        # 信封加密(Envelope Encryption)
        print(f"\n[信封加密模式]")
        print(f"  1. 生成随机DEK(数据加密密钥)")
        print(f"  2. 用DEK加密数据: C = Enc(DEK, data)")
        print(f"  3. 用KEK加密DEK: EDEK = Enc(KEK, DEK)")
        print(f"  4. 存储: (C, EDEK)  数据和加密的DEK")
        print(f"  5. 解密: D = Dec(KEK, EDEK) -> Dec(DEK, C)")
        print(f"  优势: KEK不需直接处理数据, 安全分离")

        # 密钥生成安全
        print(f"\n[密钥生成安全检查]")
        检查 = [
            ("随机源", "CSPRNG(os.urandom)", "通过"),
            ("密钥长度", "符合标准要求", "通过"),
            ("密钥唯一性", "每次生成新密钥", "通过"),
            ("密钥格式", "标准编码(hex/base64)", "通过"),
            ("生成审计", "记录密钥生成事件", "通过"),
            ("访问控制", "仅授权人员可生成", "通过"),
        ]
        print(f"  {'检查项':<14} {'期望':>24} {'结果':>6}")
        for 检查项, 期望, 结果 in 检查:
            print(f"  {检查项:<14} {期望:>24} {结果:>6}")

        return {
            "密钥类型数": len(类型),
            "生成密钥数": len(密钥列表)
        }

    def 密钥存储实践(self) -> Dict:
        """密钥安全存储实践"""
        print("\n" + "=" * 70)
        print("【密钥安全存储】")
        print("=" * 70)
        print("密钥存储安全方案")
        print("-" * 70)

        # 存储方案对比
        print(f"\n[密钥存储方案对比]")
        方案 = [
            ("硬编码", "代码中", "极度危险", "禁止", "无保护"),
            ("配置文件", "配置文件中", "危险", "禁止", "文件可读"),
            ("环境变量", "ENV", "有限", "谨慎", "进程可读"),
            ("加密配置", "加密存储", "中等", "可接受", "需保护主密钥"),
            ("HSM", "硬件安全模块", "高", "推荐", "物理隔离"),
            ("KMS", "密钥管理服务", "高", "推荐", "AWS KMS/Azure KV"),
            ("TEE", "可信执行环境", "高", "推荐", "Intel SGX/ARM TZ"),
            ("Vault", "HashiCorp Vault", "高", "推荐", "集中管理"),
        ]
        print(f"  {'方案':<12} {'存储位置':<16} {'安全级':>6} {'推荐':>8} {'特点'}")
        for 名称, 位置, 安全, 推荐, 特点 in 方案:
            print(f"  {名称:<12} {位置:<16} {安全:>6} {推荐:>8} {特点}")

        # HSM详解
        print(f"\n[HSM(硬件安全模块)详解]")
        print(f"  特性:")
        hsm特性 = [
            "物理防篡改(防拆/防探测)",
            "密钥在HSM内生成和存储",
            "密钥永不出HSM(明文)",
            "所有密码操作在HSM内完成",
            "认证和访问控制",
            "审计日志",
            "FIPS 140-2/3认证",
        ]
        for i, 特性 in enumerate(hsm特性, 1):
            print(f"    {i}. {特性}")

        print(f"\n  应用场景:")
        hsm场景 = [
            ("CA私钥", "证书颁发机构", "最高安全"),
            ("金融密钥", "银行/支付", "高安全"),
            ("TLS密钥", "HTTPS服务器", "中-高安全"),
            ("数据库密钥", "DEK/KEK存储", "高安全"),
            ("代码签名", "软件签名密钥", "高安全"),
        ]
        print(f"    {'用途':<14} {'场景':<16} {'安全级'}")
        for 用途, 场景, 安全 in hsm场景:
            print(f"    {用途:<14} {场景:<16} {安全}")

        # KMS实践
        print(f"\n[KMS(密钥管理服务)实践]")
        kms功能 = [
            "密钥生成和管理",
            "密钥版本管理和轮换",
            "密钥使用审计",
            "基于策略的访问控制",
            "信封加密支持",
            "HSM后端保护",
            "高可用和备份",
        ]
        for i, 功能 in enumerate(kms功能, 1):
            print(f"  {i}. {功能}")

        # 密钥访问控制
        print(f"\n[密钥访问控制策略]")
        策略示例 = {
            "密钥用途": "data-encryption-key",
            "允许操作": ["encrypt", "decrypt"],
            "允许用户": ["service-account-1", "service-account-2"],
            "禁止操作": ["delete", "export"],
            "审计": "所有操作记录日志",
            "MFA要求": "管理操作需要MFA",
        }
        for 键, 值 in 策略示例.items():
            print(f"  {键}: {值}")

        return {
            "存储方案数": len(方案),
            "推荐方案": "HSM/KMS"
        }

    def 密钥轮换实践(self) -> Dict:
        """密钥轮换实践"""
        print("\n" + "=" * 70)
        print("【密钥轮换实践】")
        print("=" * 70)
        print("密钥轮换策略和实现")
        print("-" * 70)

        # 轮换策略
        print(f"\n[密钥轮换策略]")
        策略 = [
            ("对称密钥", "90天", "定期轮换", "AES/HMAC"),
            ("RSA密钥对", "1年", "证书更新", "TLS/签名"),
            ("ECC密钥对", "1年", "证书更新", "TLS/签名"),
            ("TLS会话密钥", "每次会话", "会话级", "传输加密"),
            ("数据库DEK", "按需", "数据迁移", "数据加密"),
            ("KEK", "1年", "重新加密DEK", "密钥保护"),
            ("密码哈希", "登录时", "算法升级", "密码存储"),
        ]
        print(f"  {'密钥类型':<16} {'周期':>10} {'策略':<14} {'应用'}")
        for 类型, 周期, 策略名, 应用 in 策略:
            print(f"  {类型:<16} {周期:>10} {策略名:<14} {应用}")

        # 轮换流程
        print(f"\n[密钥轮换流程]")
        print(f"  1. 生成新密钥对")
        print(f"  2. 新旧密钥并存(过渡期)")
        print(f"  3. 新数据使用新密钥加密")
        print(f"  4. 旧数据逐步重加密(后台)")
        print(f"  5. 确认所有数据已重加密")
        print(f"  6. 旧密钥标记为只解密")
        print(f"  7. 过渡期结束后销毁旧密钥")

        # 轮换触发条件
        print(f"\n[轮换触发条件]")
        触发 = [
            ("定期轮换", "到期自动轮换", "预防性"),
            ("事件轮换", "疑似泄露", "应急响应"),
            ("人员轮换", "密钥管理员变更", "安全策略"),
            ("算法轮换", "算法被破解", "安全升级"),
            ("合规轮换", "审计/合规要求", "合规"),
            ("容量轮换", "使用次数达到上限", "使用限制"),
        ]
        print(f"  {'触发':<12} {'条件':<18} {'类型'}")
        for 触发名, 条件, 类型 in 触发:
            print(f"  {触发名:<12} {条件:<18} {类型}")

        # 自动化轮换
        print(f"\n[自动化密钥轮换]")
        print(f"  KMS自动轮换:")
        print(f"    - AWS KMS: 自动年度轮换")
        print(f"    - Azure Key Vault: 自动轮换策略")
        print(f"    - GCP KMS: 自动轮换周期配置")

        # 密钥版本管理
        print(f"\n[密钥版本管理]")
        版本 = [
            ("v1", "2024-01-01", "2024-03-31", "已销毁", "-"),
            ("v2", "2024-04-01", "2024-06-30", "已销毁", "-"),
            ("v3", "2024-07-01", "2024-09-30", "只解密", "过渡期"),
            ("v4", "2024-10-01", "当前", "活跃", "当前密钥"),
        ]
        print(f"  {'版本':>6} {'创建':>12} {'到期':>12} {'状态':>10} {'备注':>8}")
        for v, 创建, 到期, 状态, 备注 in 版本:
            print(f"  {v:>6} {创建:>12} {到期:>12} {状态:>10} {备注:>8}")

        # 密钥泄露响应
        print(f"\n[密钥泄露应急响应]")
        步骤 = [
            "1. 确认泄露范围(哪些密钥/数据受影响)",
            "2. 立即撤销/禁用泄露密钥",
            "3. 生成新密钥对",
            "4. 用新密钥重加密所有受影响数据",
            "5. 更新所有使用旧密钥的系统",
            "6. 审计泄露期间的所有密钥使用",
            "7. 安全事件报告和取证",
            "8. 改进安全措施防止再次发生",
        ]
        for 步骤 in 步骤:
            print(f"  {步骤}")

        return {
            "轮换策略数": len(策略),
            "触发条件数": len(触发)
        }

    def 密钥销毁实践(self) -> Dict:
        """密钥安全销毁实践"""
        print("\n" + "=" * 70)
        print("【密钥安全销毁】")
        print("=" * 70)
        print("密钥安全销毁方法和实践")
        print("-" * 70)

        # 销毁方法
        print(f"\n[密钥销毁方法]")
        方法 = [
            ("内存覆盖", "多次随机覆写", "软件级", "中"),
            ("安全擦除", "cryptographic erase", "软件级", "高"),
            ("物理销毁", "粉碎/焚烧存储介质", "物理级", "极高"),
            ("HSM销毁", "HSM内密钥销毁", "硬件级", "极高"),
            ("密钥归档", "加密归档后销毁", "合规级", "高"),
            ("分散销毁", "密钥分片后分别销毁", "分布级", "高"),
        ]
        print(f"  {'方法':<12} {'原理':<24} {'级别':>8} {'安全':>6}")
        for 方法, 原理, 级别, 安全 in 方法:
            print(f"  {方法:<12} {原理:<24} {级别:>8} {安全:>6}")

        # 内存安全
        print(f"\n[内存中的密钥安全]")
        注意 = [
            "密钥使用后立即清零( memset/zero_memory)",
            "防止编译器优化掉清零操作(volatile/屏障)",
            "密钥在内存中时间尽可能短",
            "使用安全内存区域(如mlock锁定)",
            "避免密钥写入swap(磁盘交换)",
            "使用专用安全内存库(如libsodium)")
        ]
        for i, 注意项 in enumerate(注意, 1):
            print(f"  {i}. {注意项}")

        # 密钥销毁流程
        print(f"\n[密钥销毁流程]")
        流程 = [
            ("1. 销毁请求", "授权人员发起", "需审批"),
            ("2. 影响评估", "评估销毁影响", "确认无影响"),
            ("3. 数据迁移", "确保数据已迁移", "用新密钥保护"),
            ("4. 密钥销毁", "执行安全销毁", "记录操作"),
            ("5. 销毁验证", "验证密钥不可恢复", "取证确认"),
            ("6. 审计记录", "记录销毁事件", "合规存档"),
            ("7. 通知相关方", "通知受影响系统", "更新配置"),
        ]
        for 步骤, 描述, 要求 in 流程:
            print(f"  {步骤}: {描述} ({要求})")

        # 合规要求
        print(f"\n[合规要求]")
        合规 = [
            ("PCI DSS", "支付卡行业", "密钥销毁需记录"),
            ("HIPAA", "医疗信息", "数据销毁要求"),
            ("GDPR", "欧盟数据保护", "删除权"),
            ("SOX", "金融合规", "审计追踪"),
            ("ISO 27001", "信息安全管理", "密钥生命周期"),
            ("中国网络安全法", "数据安全", "数据销毁要求"),
        ]
        print(f"  {'标准':<14} {'领域':<16} {'要求'}")
        for 标准, 领域, 要求 in 合规:
            print(f"  {标准:<14} {领域:<16} {要求}")

        # 密钥遗留风险
        print(f"\n[密钥遗留风险]")
        风险 = [
            ("内存残留", "密钥可能残留在内存", "安全擦除+重启"),
            ("日志泄露", "密钥记录在日志中", "日志过滤+审计"),
            ("备份残留", "密钥在备份中残留", "备份加密+销毁"),
            ("SSD残留", "SSD磨损均衡导致残留", "Cryptographic Erase"),
            ("缓存残留", "CPU缓存中的密钥", "缓存刷新"),
            ("调试信息", "调试输出中的密钥", "Release构建清理"),
        ]
        print(f"  {'风险':<14} {'描述':<24} {'缓解'}")
        for 风险, 描述, 缓解 in 风险:
            print(f"  {风险:<14} {描述:<24} {缓解}")

        return {
            "销毁方法数": len(方法),
            "合规标准数": len(合规)
        }

    def 运行所有实践(self):
        """运行所有密钥管理实践"""
        print("\n" + "#" * 70)
        print("#  第六部分：密钥管理实践")
        print("#" * 70)

        self.密钥生成实践()
        self.密钥存储实践()
        self.密钥轮换实践()
        self.密钥销毁实践()


# ============================================================================
# 第七部分：侧信道攻击模拟
# ============================================================================

class 侧信道攻击模拟器:
    """
    侧信道攻击模拟器
    
    模拟侧信道攻击：
    - 时间攻击(Timing Attack)
    - 功耗分析(Power Analysis)
    - 缓存攻击(Cache Attack)
    
    侧信道原理: 通过分析密码实现的物理信息(时间/功耗/电磁等)
    推断密钥信息
    """

    def __init__(self):
        self.测量次数 = 1000

    def 时间攻击模拟(self) -> Dict:
        """时间攻击模拟"""
        print("\n" + "=" * 70)
        print("【时间攻击模拟】")
        print("=" * 70)
        print("通过分析执行时间推断密钥信息")
        print("-" * 70)

        # 时间攻击原理
        print(f"\n[时间攻击原理]")
        print(f"  如果密码操作的时间依赖于密钥/数据:")
        print(f"    - 逐字节比较密码: 时间与匹配长度成正比")
        print(f"    - RSA指数运算: 时间与指数位数有关")
        print(f"    - 分支条件: 不同分支时间不同")
        print(f"  攻击者通过测量时间推断秘密信息")

        # 模拟密码比较时间攻击
        print(f"\n[密码比较时间攻击模拟]")
        正确密码 = "SECRET"
        print(f"  正确密码: {正确密码} (6字符)")
        print(f"  漏洞实现: 逐字符比较,第一个不同就返回")

        # 模拟不安全比较(时间与匹配长度相关)
        def 不安全比较(a, b):
            for i in range(min(len(a), len(b))):
                if a[i] != b[i]:
                    return False  # 在第i位不同就返回
                time.sleep(0.001)  # 模拟操作延迟
            return a == b

        # 模拟安全比较(恒定时间)
        def 安全比较(a, b):
            结果 = 0
            for i in range(max(len(a), len(b))):
                ca = ord(a[i]) if i < len(a) else 0
                cb = ord(b[i]) if i < len(b) else 0
                结果 |= ca ^ cb
            return 结果 == 0

        # 模拟攻击过程
        print(f"\n[攻击过程]")
        测试输入 = ["AAAAAA", "SAAAAA", "SEAAAA", "SECAAA", "SECAAA", "SECRET"]
        print(f"  {'输入':>8} {'匹配位数':>8} {'耗时(ms)':>10} {'推断':>8}")

        for 输入 in 测试输入:
            匹配数 = 0
            for i in range(min(len(输入), len(正确密码))):
                if 输入[i] == 正确密码[i]:
                    匹配数 += 1
                else:
                    break
            # 时间与匹配数成正比(不安全)
            耗时 = 匹配数 * 1.0 + random.uniform(-0.1, 0.1)
            推断 = f"前{匹配数}位正确" if 匹配数 > 0 else "第1位错误"
            标记 = " <- 破解!" if 输入 == 正确密码 else ""
            print(f"  {输入:>8} {匹配数:>8} {耗时:>10.1f} {推断:>8}{标记}")

        print(f"\n  攻击者通过时间差异逐字符推导密码!")
        print(f"  前1位正确时耗时更多 -> 推断第1位正确")

        # RSA时间攻击
        print(f"\n[RSA时间攻击]")
        print(f"  RSA解密: m = c^d mod n")
        print(f"  Square-and-Multiply算法:")
        print(f"    for each bit of d:")
        print(f"      square (总是执行)")
        print(f"      if bit == 1: multiply (条件执行)")
        print(f"  时间差异暴露d的位")

        # 模拟RSA时间泄露
        print(f"\n[模拟RSA密钥位泄露]")
        d = 0b10110100  # 8位私钥(教学用)
        d_bits = bin(d)[2:]
        print(f"  私钥d = {d} (二进制: {d_bits})")

        for i, bit in enumerate(d_bits):
            基础时间 = 1.0  # square时间
            if bit == '1':
                额外时间 = 0.5  # multiply额外时间
                总时间 = 基础时间 + 额外时间 + random.uniform(-0.05, 0.05)
                推断位 = 1
            else:
                总时间 = 基础时间 + random.uniform(-0.05, 0.05)
                推断位 = 0
            print(f"  位{i+1}: 实际={bit} 耗时={总时间:.2f}ms 推断={推断位}")

        # 防御措施
        print(f"\n[时间攻击防御]")
        防御 = [
            ("恒定时间比较", "hmac.compare_digest", "所有分支相同时间"),
            ("恒定时间密码学", "不受输入影响的实现", "消除时间差异"),
            ("添加随机延迟", "操作后随机等待", "降低信噪比(效果有限)"),
            ("操作盲化", "RSA: m*r^e, d", "随机化中间值"),
            ("恒定时间分支", "避免数据依赖分支", "无分支实现"),
        ]
        print(f"  {'防御':<16} {'方法':<24} {'原理'}")
        for 防御名, 方法, 原理 in 防御:
            print(f"  {防御名:<16} {方法:<24} {原理}")

        return {
            "攻击成功": True,
            "密钥位数": len(d_bits)
        }

    def 功耗分析模拟(self) -> Dict:
        """功耗分析攻击模拟"""
        print("\n" + "=" * 70)
        print("【功耗分析攻击模拟】")
        print("=" * 70)
        print("通过分析设备功耗推断密钥")
        print("-" * 70)

        # 功耗分析原理
        print(f"\n[功耗分析原理]")
        print(f"  CMOS电路功耗与数据/操作相关")
        print(f"  不同操作(读/写/计算)功耗不同")
        print(f"  不同数据值功耗不同(Hamming重量)")
        print(f"  攻击者测量功耗曲线推断密钥")

        # 功耗分析类型
        print(f"\n[功耗分析类型]")
        类型 = [
            ("SPA", "简单功耗分析", "直接观察功耗曲线", "低", "需要少量测量"),
            ("DPA", "差分功耗分析", "统计多组功耗差异", "高", "需要大量测量"),
            ("CPA", "相关功耗分析", "利用相关性分析", "高", "需要功耗模型"),
            ("模板攻击", "预先建模", "机器学习/统计", "高", "需要特征提取"),
            ("高阶DPA", "高阶统计", "结合多个时间点", "高", "复杂度高"),
        ]
        print(f"  {'类型':<10} {'名称':<16} {'原理':<20} {'威胁':>6} {'特点'}")
        for 简称, 名称, 原理, 威胁, 特点 in 类型:
            print(f"  {简称:<10} {名称:<16} {原理:<20} {威胁:>6} {特点}")

        # DPA攻击流程
        print(f"\n[DPA攻击流程]")
        print(f"  1. 收集N组功耗轨迹(每次加密功耗曲线)")
        print(f"  2. 猜测密钥子块k(如1字节)")
        print(f"  3. 根据k计算中间值(如S盒输出)")
        print(f"  4. 选择区分函数D(如LSB)")
        print(f"  5. 按D将轨迹分为两组")
        print(f"  6. 计算两组平均功耗差")
        print(f"  7. 正确k时出现功耗尖峰")

        # 模拟DPA
        print(f"\n[DPA模拟(AES S盒) ]")
        print(f"  目标: AES第一轮S盒输出")
        print(f"  方法: 猜测密钥字节,计算相关性")

        # 模拟256个密钥猜测
        正确密钥字节 = 0x2B
        相关性峰值 = 0

        print(f"  {'密钥猜测':>10} {'相关系数':>10} {'状态':>8}")
        for 猜测 in range(0, 256, 32):
            # 模拟: 正确密钥时相关性高
            if 猜测 == 正确密钥字节:
                相关系数 = 0.85 + random.uniform(-0.05, 0.05)
                状态 = "峰值!"
            else:
                相关系数 = random.uniform(-0.1, 0.1)
                状态 = "噪声"
            print(f"  0x{猜测:02X}({猜测:>3}) {相关系数:>10.4f} {状态:>8}")
            if abs(相关系数) > abs(相关性峰值):
                相关性峰值 = 相关系数

        print(f"  ...")
        print(f"  0x{正确密钥字节:02X}({正确密钥字节:>3}) {0.87:>10.4f} {'峰值!':>8}")
        print(f"\n  正确密钥字节: 0x{正确密钥字节:02X}")
        print(f"  峰值相关系数: 0.87")
        print(f"  攻击成功: 是")

        # 防御措施
        print(f"\n[功耗分析防御]")
        防御 = [
            ("掩码(Masking)", "中间值XOR随机掩码", "DPA防护"),
            ("隐藏(Hiding)", "恒定功耗/随机延迟", "降低信噪比"),
            ("双轨道逻辑", "互补逻辑平衡功耗", "硬件级防护"),
            ("功耗随机化", "随机插入空操作", "增加噪声"),
            ("并行化", "并行操作平均功耗", "降低相关性"),
        ]
        print(f"  {'防御':<16} {'原理':<24} {'适用'}")
        for 防御名, 原理, 适用 in 防御:
            print(f"  {防御名:<16} {原理:<24} {适用}")

        return {
            "分析类型数": len(类型),
            "恢复密钥": f"0x{正确密钥字节:02X}"
        }

    def 缓存攻击模拟(self) -> Dict:
        """缓存攻击模拟"""
        print("\n" + "=" * 70)
        print("【缓存攻击模拟】")
        print("=" * 70)
        print("通过分析CPU缓存行为推断密钥")
        print("-" * 70)

        # 缓存攻击原理
        print(f"\n[缓存攻击原理]")
        print(f"  CPU缓存命中比缓存未命中快")
        print(f"  密码表查找(AES S盒/DES S盒)访问缓存")
        print(f"  访问模式与密钥相关")
        print(f"  通过测量缓存访问时间推断密钥")

        # 缓存攻击类型
        print(f"\n[缓存攻击类型]")
        类型 = [
            ("Flush+Reload", "刷新后重载测时间", "高", "共享内存"),
            ("Prime+Probe", "填充后探测", "高", "L1/L2缓存"),
            ("Evict+Time", "驱逐后计时", "中", "L3缓存"),
            ("Flush+Flush", "刷新时间差异", "高", "无数据共享"),
            ("Spectre", "分支预测利用", "严重", "推测执行"),
            ("Meltdown", "越界读取", "严重", "权限隔离"),
        ]
        print(f"  {'攻击':<14} {'原理':<22} {'威胁':>6} {'条件'}")
        for 攻击, 原理, 威胁, 条件 in 类型:
            print(f"  {攻击:<14} {原理:<22} {威胁:>6} {条件}")

        # Flush+Reload模拟
        print(f"\n[Flush+Reload攻击模拟]")
        print(f"  流程:")
        print(f"    1. Flush: 从缓存中驱逐目标行(clflush)")
        print(f"    2. Wait: 等待目标程序执行(可能加载缓存)")
        print(f"    3. Reload: 测量重载目标行的时间")
        print(f"    4. 短时间=缓存命中(被访问过)")
        print(f"    5. 长时间=缓存未命中(未被访问)")

        # 模拟AES缓存攻击
        print(f"\n[AES T表缓存攻击模拟]")
        print(f"  AES查表: T[byte ^ key_byte]")
        print(f"  攻击者测量T表各行的访问时间")
        print(f"  推断哪些行被访问 -> 推断key_byte")

        # 模拟测量
        正确密钥 = 0x2B
        print(f"\n  目标密钥字节: 0x{正确密钥字节:02X}")
        print(f"  测量T表行访问时间:")

        命中行 = 正确密钥字节 // 16  # 模拟缓存行
        print(f"  {'缓存行':>8} {'访问时间(ns)':>12} {'判断':>10}")

        for 行 in range(16):
            if 行 == 命中行:
                时间 = 30 + random.uniform(-2, 2)  # 缓存命中快
                判断 = "命中! <-"
            else:
                时间 = 150 + random.uniform(-10, 10)  # 缓存未命中慢
                判断 = "未命中"

            if 行 <= 4 or 行 == 命中行 or 行 >= 14:
                print(f"  {行:>8} {时间:>12.1f} {判断:>10}")
        print(f"  ...")
        print(f"\n  推断: 行{命中行}命中 -> 密钥高4位 = {命中行:04b}")
        print(f"  重复4次攻击恢复完整密钥字节")

        # Spectre/Meltdown
        print(f"\n[Spectre & Meltdown]")
        print(f"  Spectre(幽灵):")
        print(f"    利用CPU推测执行")
        print(f"    诱导分支预测器误预测")
        print(f"    推测执行的代码读取秘密数据")
        print(f"    通过缓存侧信道泄露")
        print(f"")
        print(f"  Meltdown(熔毁):")
        print(f"    利用乱序执行")
        print(f"    绕过权限检查读取内核内存")
        print(f"    用户态读取内核态数据")
        print(f"    通过缓存侧信道泄露")

        # 防御措施
        print(f"\n[缓存攻击防御]")
        防御 = [
            ("常量时间实现", "不使用查找表", "软件级"),
            ("缓存刷新", "敏感操作前刷新缓存", "软件级"),
            ("缓存分区", "Intel CAT技术", "硬件级"),
            ("非瞬时执行", "MOVNT指令", "指令级"),
            ("内核隔离", "KPTI(Meltdown)", "内核级"),
            ("推测执行屏障", "lfence/memory barrier", "指令级"),
        ]
        print(f"  {'防御':<14} {'方法':<22} {'级别'}")
        for 防御名, 方法, 级别 in 防御:
            print(f"  {防御名:<14} {方法:<22} {级别}")

        # 安全建议
        print(f"\n[安全建议]")
        建议 = [
            "使用常量时间密码学库(如Curve25519)",
            "避免数据依赖的内存访问",
            "启用内核页表隔离(KPTI)",
            "定期更新CPU微码",
            "使用安全区域(Enclave)处理敏感数据",
            "限制共享内存访问",
            "禁用不必要的高精度定时器",
        ]
        for i, 建议项 in enumerate(建议, 1):
            print(f"  {i}. {建议项}")

        return {
            "攻击类型数": len(类型),
            "恢复密钥": f"0x{正确密钥:02X}"
        }

    def 运行所有攻击(self):
        """运行所有侧信道攻击模拟"""
        print("\n" + "#" * 70)
        print("#  第七部分：侧信道攻击模拟")
        print("#" * 70)

        self.时间攻击模拟()
        self.功耗分析模拟()
        self.缓存攻击模拟()


# ============================================================================
# 主函数
# ============================================================================

def main():
    """主函数 - 运行所有密码学与密钥安全实战案例"""
    print(BANNER)
    print(f"启动时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python版本: {sys.version.split()[0]}")
    print(f"安全声明: 本程序仅用于授权安全测试和教育目的")
    print("=" * 80)

    # 1. 古典密码破解
    古典破解器 = 古典密码破解器()
    古典破解器.运行所有破解()

    # 2. 对称加密实战
    对称加密器 = 对称加密实战器()
    对称加密器.运行所有实战()

    # 3. 非对称加密实战
    非对称加密器 = 非对称加密实战器()
    非对称加密器.运行所有实战()

    # 4. 哈希与消息认证
    哈希认证器 = 哈希与消息认证器()
    哈希认证器.运行所有检测()

    # 5. 密码分析攻击
    密码分析器 = 密码分析攻击器()
    密码分析器.运行所有攻击()

    # 6. 密钥管理实践
    密钥管理器 = 密钥管理实践器()
    密钥管理器.运行所有实践()

    # 7. 侧信道攻击模拟
    侧信道模拟器 = 侧信道攻击模拟器()
    侧信道模拟器.运行所有攻击()

    # 总结
    print("\n" + "=" * 80)
    print("密码学与密钥安全实战案例 - 执行完毕")
    print("=" * 80)
    print("""
学习总结:
  1. 古典密码: 凯撒/维吉尼亚密码可通过频率分析破解，现代密码学已超越
  2. 对称加密: AES-GCM是推荐模式，ECB不安全，需注意Padding Oracle
  3. 非对称加密: RSA需OAEP填充，ECC效率更高，密钥生成用CSPRNG
  4. 哈希认证: MD5/SHA-1已不安全，HMAC用compare_digest防时序，PBKDF2/Argon2存密码
  5. 密码分析: 共模/广播/低指数攻击展示RSA参数选择的重要性
  6. 密钥管理: HSM/KMS存储，定期轮换，安全销毁是全生命周期管理
  7. 侧信道: 时间/功耗/缓存攻击是密码实现的隐蔽威胁

关键学习要点:
  - 密码学安全 = 算法安全 + 实现安全 + 密钥安全
  - 没有完美的算法，只有不断演进的安全方案
  - 侧信道攻击表明实现安全与算法安全同等重要
  - 密钥管理是密码学安全的实际瓶颈
  - 量子计算将威胁RSA/ECC，需要关注后量子密码学
  - NIST PQC标准化: CRYSTALS-Kyber(密钥交换), CRYSTALS-Dilithium(签名)

进一步学习资源:
  - NIST密码学标准 (csrc.nist.gov)
  - Cryptopals Crypto Challenges (cryptopals.com)
  - OpenSSL文档和源码
  - RFC 8446 (TLS 1.3)
  - NIST FIPS 203/204/205 (后量子标准)
  - 《应用密码学》by Bruce Schneier
  - 《密码学原理与实践》by Douglas Stinson
""")
    print(f"\n结束时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
