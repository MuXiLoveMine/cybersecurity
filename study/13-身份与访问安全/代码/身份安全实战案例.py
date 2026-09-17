#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
                身份与访问安全实战案例 - 身份认证与授权安全
==============================================================================

安全声明：
    本文件仅用于授权安全测试和教育培训目的。所有身份认证、授权
    和访问控制测试均在受控模拟环境中进行。读者应在合法授权范围
    内使用这些技术，严禁用于未经授权的系统访问或身份伪造。
    作者不对任何滥用本代码的行为负责。

技术范围：
    1. 身份认证安全检测（弱密码检测、MFA验证、生物特征安全）
    2. OAuth2.0安全审计（授权码劫持、重定向URI验证、PKCE检查）
    3. SAML安全检测（XML签名包装、响应注入、重放攻击）
    4. 零信任架构实现（持续验证、微分段、动态访问控制）
    5. 权限提升检测（横向移动检测、权限滥用监控）
    6. IAM系统安全（生命周期管理、权限回收、特权账户监控）

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
import json
import time
import urllib.parse
import struct
from typing import List, Dict, Tuple, Any, Optional

# ============================================================================
# 全局配置
# ============================================================================

random.seed(42)

BANNER = """
╔══════════════════════════════════════════════════════════════════════════════╗
║          身份与访问安全实战案例 - 认证授权安全攻防系统                        ║
║      Auth Security | OAuth Audit | SAML Detection | Zero Trust | IAM       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

# 弱密码字典（部分常见弱密码）
弱密码字典 = [
    "123456", "password", "12345678", "qwerty", "123456789",
    "12345", "1234", "111111", "1234567", "dragon",
    "admin", "letmein", "abc123", "monkey", "master",
    "000000", "password123", "Password1", "welcome", "login",
    "passw0rd", "p@ssw0rd", "1q2w3e4r", "sunshine", "princess"
]

# 密码复杂度规则
密码策略 = {
    "最小长度": 12,
    "需大写字母": True,
    "需小写字母": True,
    "需数字": True,
    "需特殊字符": True,
    "禁止常见密码": True,
    "最大重复字符": 3,
    "密码历史": 5,
}


# ============================================================================
# 第一部分：身份认证安全检测
# ============================================================================

class 身份认证安全检测器:
    """
    身份认证安全检测器
    
    评估身份认证机制的安全性，包括：
    - 弱密码检测
    - 多因素认证(MFA)验证
    - 生物特征安全分析
    """

    def __init__(self):
        self.检测目标 = "模拟身份认证系统"
        self.密码策略 = 密码策略

    def 弱密码检测(self) -> Dict:
        """
        弱密码检测
        
        通过字典攻击和规则检查检测弱密码
        
        检测方法：
        1. 字典匹配: 与已知弱密码字典比对
        2. 规则检查: 验证密码复杂度策略
        3. 熵值计算: 评估密码随机性
        4. 模式识别: 检测键盘模式、重复模式
        """
        print("\n" + "=" * 70)
        print("【弱密码检测】")
        print("=" * 70)
        print(f"检测目标: {self.检测目标}")
        print(f"密码策略: 最小长度={self.密码策略['最小长度']}, "
              f"大小写+数字+特殊字符")
        print("-" * 70)

        # 模拟用户密码库
        用户密码 = [
            ("user001", "123456"),
            ("user002", "Password1!"),
            ("user003", "qwerty123"),
            ("user004", "P@ssw0rd2024!"),
            ("user005", "abcabcabc"),
            ("user006", "Tr7$mK9#nL2x"),
            ("user007", "admin123"),
            ("user008", "1q2w3e4r5t"),
            ("user009", "Sunshine2024!"),
            ("user010", "aA1!aA1!aA1!"),
        ]

        print(f"\n[密码复杂度检测结果]")
        print(f"  {'用户':<12} {'密码':<20} {'长度':>4} {'熵值':>6} {'字典':>6} {'模式':>6} {'评级':>6}")

        检测结果 = []
        for 用户名, 密码 in 用户密码:
            # 长度检查
            长度 = len(密码)
            长度合格 = 长度 >= self.密码策略["最小长度"]

            # 字典检查
            在字典中 = 密码.lower() in [p.lower() for p in 弱密码字典]

            # 复杂度检查
            有大写 = any(c.isupper() for c in 密码)
            有小写 = any(c.islower() for c in 密码)
            有数字 = any(c.isdigit() for c in 密码)
            有特殊 = any(not c.isalnum() for c in 密码)

            # 熵值计算
            字符集大小 = 0
            if 有大写: 字符集大小 += 26
            if 有小写: 字符集大小 += 26
            if 有数字: 字符集大小 += 10
            if 有特殊: 字符集大小 += 32
            熵值 = 长度 * math.log2(字符集大小) if 字符集大小 > 0 else 0

            # 模式检查
            有模式 = False
            # 键盘模式
            键盘行 = "qwertyuiopasdfghjklzxcvbnm"
            for i in range(len(密码) - 2):
                片段 = 密码[i:i+3].lower()
                if 片段 in 键盘行 or 片段[::-1] in 键盘行:
                    有模式 = True
                    break
            # 重复模式
            if len(密码) >= 3:
                for i in range(1, len(密码)):
                    if 密码[:i] * (len(密码) // i) == 密码[:len(密码)]:
                        有模式 = True
                        break

            # 评级
            if 在字典中 or 长度 < 8:
                评级 = "极弱"
            elif 熵值 < 40 or 有模式:
                评级 = "弱"
            elif 熵值 < 60 or not all([有大写, 有小写, 有数字, 有特殊]):
                评级 = "中"
            elif 长度合格 and 熵值 >= 60:
                评级 = "强"
            else:
                评级 = "中"

            字典状态 = "命中" if 在字典中 else "未命中"
            模式状态 = "有" if 有模式 else "无"

            print(f"  {用户名:<12} {'*' * len(密码):<20} {长度:>4} {熵值:>6.1f} "
                  f"{字典状态:>6} {模式状态:>6} {评级:>6}")

            检测结果.append({
                "用户": 用户名,
                "评级": 评级,
                "熵值": 熵值,
                "在字典中": 在字典中
            })

        # 统计
        弱密码数 = sum(1 for r in 检测结果 if r["评级"] in ["极弱", "弱"])
        字典命中数 = sum(1 for r in 检测结果 if r["在字典中"])
        平均熵值 = sum(r["熵值"] for r in 检测结果) / len(检测结果)

        print(f"\n[检测统计]")
        print(f"  检测密码数: {len(检测结果)}")
        print(f"  极弱/弱密码数: {弱密码数}")
        print(f"  字典命中数: {字典命中数}")
        print(f"  平均熵值: {平均熵值:.1f} bits")
        print(f"  密码安全率: {(len(检测结果)-弱密码数)/len(检测结果):.0%}")

        print(f"\n[安全建议]")
        print(f"  1. 强制密码策略: 最小12位，含大小写+数字+特殊字符")
        print(f"  2. 密码黑名单: 禁止使用已泄露密码(HaveIBeenPwned)")
        print(f"  3. 密码管理器: 推荐使用密码管理器生成随机密码")
        print(f"  4. 定期审计: 定期检查密码强度")
        print(f"  5. 账户锁定: 多次失败后锁定账户")

        return {
            "检测密码数": len(检测结果),
            "弱密码数": 弱密码数,
            "字典命中数": 字典命中数,
            "平均熵值": 平均熵值
        }

    def 多因素认证验证(self) -> Dict:
        """
        多因素认证(MFA)验证
        
        验证MFA实现的安全性，包括：
        - TOTP(基于时间的一次性密码)
        - SMS验证码安全性
        - 推送通知认证
        - 硬件安全密钥(FIDO/U2F)
        """
        print("\n" + "=" * 70)
        print("【多因素认证(MFA)验证】")
        print("=" * 70)
        print("评估MFA实现的安全性和可靠性")
        print("-" * 70)

        # MFA方式对比
        print(f"\n[MFA方式安全对比]")
        mfa方式 = [
            ("SMS验证码", "低", "SIM劫持/中间人", "是", "易受SIM交换攻击"),
            ("邮件验证码", "低", "邮箱入侵", "是", "邮箱安全=认证安全"),
            ("TOTP(App)", "中", "钓鱼/设备失窃", "是", "Google Authenticator等"),
            ("推送通知", "中", "推送疲劳攻击", "是", "需用户确认"),
            ("硬件密钥(U2F)", "高", "物理窃取", "否", "FIDO标准，抗钓鱼"),
            ("硬件密钥(FIDO2)", "高", "物理窃取", "否", "WebAuthn标准"),
            ("生物特征", "中", "生物特征盗用", "否", "不可撤销，需配合"),
        ]

        print(f"  {'方式':<16} {'安全级':>6} {'主要威胁':<16} {'可钓鱼':>6} {'说明'}")
        for 方式, 等级, 威胁, 可钓鱼, 说明 in mfa方式:
            print(f"  {方式:<16} {等级:>6} {威胁:<16} {可钓鱼:>6} {说明}")

        # TOTP实现验证
        print(f"\n[TOTP实现验证]")
        print(f"  算法: HOTP(K, T) where T = floor(unix_time / 30)")
        print(f"  密钥: 使用HMAC-SHA1")
        print(f"  码长: 6位数字")
        print(f"  有效期: 30秒")

        # 模拟TOTP生成
        密钥 = b"JBSWY3DPEHPK3PXP"  # Base32密钥(模拟)
        当前时间 = int(time.time())
        时间步 = 当前时间 // 30

        # 使用HMAC模拟TOTP
        消息 = struct.pack(">Q", 时间步)
        hmac_hash = hmac.new(密钥, 消息, hashlib.sha1).digest()
        偏移 = hmac_hash[-1] & 0x0F
        二进制码 = struct.unpack(">I", hmac_hash[偏移:偏移+4])[0] & 0x7FFFFFFF
        totp码 = str(二进制码 % 1000000).zfill(6)

        print(f"  当前时间步: {时间步}")
        print(f"  生成的TOTP: {totp码}")
        print(f"  有效期剩余: {30 - (当前时间 % 30)}秒")

        # TOTP安全分析
        print(f"\n[TOTP安全分析]")
        安全问题 = [
            ("时间窗口", "30秒窗口可能被暴力破解", "中", "缩短窗口或增加码长"),
            ("密钥存储", "App存储密钥可能被提取", "中", "使用安全区域(TEE)"),
            ("钓鱼攻击", "用户可能被诱导输入TOTP", "高", "使用FIDO抗钓鱼"),
            ("重放攻击", "同一TOTP在窗口内可重用", "低", "服务端记录已用码"),
            ("设备绑定", "TOTP不绑定设备身份", "中", "配合设备指纹"),
        ]

        print(f"  {'问题':<14} {'描述':<28} {'风险':>6} {'缓解'}")
        for 问题, 描述, 风险, 缓解 in 安全问题:
            print(f"  {问题:<14} {描述:<28} {风险:>6} {缓解}")

        # MFA绕过攻击模拟
        print(f"\n[MFA绕过攻击模拟]")
        绕过攻击 = [
            ("SIM交换攻击", "通过社工骗取运营商更换SIM卡", "SMS", "成功", "高"),
            ("疲劳攻击", "连续发送推送请求等用户误点", "推送", "成功", "中"),
            ("TOTP钓鱼", "钓鱼网站截获TOTP并实时使用", "TOTP", "成功", "高"),
            ("会话劫持", "在MFA后劫持会话Cookie", "任意", "成功", "高"),
            ("降级攻击", "诱导降级到不安全的MFA方式", "任意", "部分", "中"),
            ("FIDO2钓鱼", "尝试钓鱼FIDO2认证", "FIDO2", "失败", "低"),
        ]

        print(f"  {'攻击':<16} {'描述':<28} {'目标':>8} {'结果':>6} {'风险':>6}")
        for 攻击, 描述, 目标, 结果, 风险 in 绕过攻击:
            print(f"  {攻击:<16} {描述:<28} {目标:>8} {结果:>6} {风险:>6}")

        成功绕过 = sum(1 for a in 绕过攻击 if a[3] == "成功")
        防御率 = 1 - 成功绕过 / len(绕过攻击)

        print(f"\n[MFA安全评估]")
        print(f"  测试攻击数: {len(绕过攻击)}")
        print(f"  成功绕过数: {成功绕过}")
        print(f"  MFA防御率: {防御率:.0%}")
        print(f"  最强MFA: FIDO2/WebAuthn (抗钓鱼)")

        print(f"\n[MFA部署建议]")
        print(f"  1. 优先使用FIDO2/WebAuthn硬件密钥")
        print(f"  2. 次选TOTP App认证")
        print(f"  3. 禁用SMS作为MFA(易受SIM交换攻击)")
        print(f"  4. 推送通知需配合数字匹配验证")
        print(f"  5. 实施风险自适应认证(低风险免MFA)")

        return {
            "测试攻击数": len(绕过攻击),
            "成功绕过数": 成功绕过,
            "防御率": 防御率
        }

    def 生物特征安全(self) -> Dict:
        """生物特征认证安全分析"""
        print("\n" + "=" * 70)
        print("【生物特征认证安全分析】")
        print("=" * 70)
        print("评估生物特征认证安全性")
        print("-" * 70)

        # 生物特征类型
        print(f"\n[生物特征认证方式]")
        认证方式 = [
            ("指纹识别", "高", "中", "指纹膜/照片攻击", "常见，成本低"),
            ("人脸识别(2D)", "中", "低", "照片/视频/3D面具", "易被欺骗"),
            ("人脸识别(3D)", "高", "高", "高精度3D面具", "较安全"),
            ("虹膜识别", "高", "高", "高分辨率虹膜照片", "精度高但成本高"),
            ("声纹识别", "中", "中", "语音合成/重放", "需活体检测"),
            ("静脉识别", "高", "高", "极难伪造", "安全性最高"),
            ("行为生物特征", "中", "中", "行为模仿", "持续认证"),
        ]

        print(f"  {'方式':<16} {'准确率':>6} {'安全级':>6} {'攻击方法':<20} {'说明'}")
        for 方式, 准确率, 安全, 攻击, 说明 in 认证方式:
            print(f"  {方式:<16} {准确率:>6} {安全:>6} {攻击:<20} {说明}")

        # 活体检测分析
        print(f"\n[活体检测技术]")
        活体技术 = [
            ("眨眼检测", "检测眨眼动作", "中", "可用视频绕过"),
            ("头部转动", "要求随机方向转头", "中", "可用深度伪造"),
            ("3D深度", "ToF/结构光检测3D", "高", "需3D面具"),
            ("红外成像", "红外检测血液流动", "高", "难以伪造"),
            ("随机动作", "随机指令(张嘴/摇头)", "中", "需实时合成"),
            ("微动作分析", "分析面部微表情", "高", "高级攻击者可能绕过"),
        ]

        print(f"  {'技术':<14} {'原理':<24} {'安全级':>6} {'弱点'}")
        for 技术, 原理, 安全, 弱点 in 活体技术:
            print(f"  {技术:<14} {原理:<24} {安全:>6} {弱点}")

        # 生物特征安全挑战
        print(f"\n[生物特征安全挑战]")
        挑战 = [
            "不可撤销性: 生物特征一旦泄露无法更换",
            "跨平台性: 不同设备采集特征不一致",
            "隐私风险: 生物数据泄露后果严重",
            "假阳/假阴: 准确性与安全性的权衡",
            "模板安全: 存储的生物模板需加密保护",
            "活体检测: 需防止照片/视频/面具攻击",
            "合规要求: 生物数据受GDPR/PIPL等法规保护",
        ]

        for i, 挑战项 in enumerate(挑战, 1):
            print(f"  {i}. {挑战项}")

        # 生物特征模板保护
        print(f"\n[生物模板保护方案]")
        保护方案 = [
            ("模糊承诺(Fuzzy Commitment)", "使用纠错码绑定密钥和生物特征"),
            ("模糊保险箱(Fuzzy Vault)", "使用冗余点保护生物模板"),
            ("可撤销生物特征", "通过变换函数生成可撤销模板"),
            ("同态加密", "在加密域进行生物特征匹配"),
            ("安全区域(TEE)", "在可信执行环境内处理生物数据"),
        ]

        for 方案, 描述 in 保护方案:
            print(f"  - {方案}: {描述}")

        print(f"\n[安全建议]")
        print(f"  1. 多模态融合: 结合多种生物特征提高安全性")
        print(f"  2. 活体检测: 必须配合活体检测防伪造")
        print(f"  3. 模板保护: 使用可撤销变换保护模板")
        print(f"  4. 本地处理: 生物数据不离开设备")
        print(f"  5. 结合MFA: 生物特征+其他因素组合认证")

        return {
            "认证方式数": len(认证方式),
            "活体技术数": len(活体技术)
        }

    def 运行所有检测(self):
        """运行所有身份认证安全检测"""
        print("\n" + "#" * 70)
        print("#  第一部分：身份认证安全检测")
        print("#" * 70)

        self.弱密码检测()
        self.多因素认证验证()
        self.生物特征安全()


# ============================================================================
# 第二部分：OAuth2.0安全审计
# ============================================================================

class OAuth2安全审计器:
    """
    OAuth2.0安全审计器
    
    审计OAuth2.0实现的安全性，检测常见漏洞：
    - 授权码劫持
    - 重定向URI验证绕过
    - PKCE缺失
    - 令牌泄露
    """

    def __init__(self):
        self.授权服务器 = "https://auth.example.com"
        self.客户端 = "https://app.example.com"

    def 授权码劫持检测(self) -> Dict:
        """
        授权码劫持攻击检测
        
        OAuth2.0授权码流程:
        1. 客户端重定向用户到授权服务器
        2. 用户授权后，授权服务器重定向到redirect_uri并附带code
        3. 攻击者可能劫持此重定向获取code
        
        攻击方式:
        - 开放重定向: 利用redirect_uri验证不严
        - XSS: 通过客户端XSS截获code
        - 代理攻击: 通过恶意代理截获
        """
        print("\n" + "=" * 70)
        print("【授权码劫持检测】")
        print("=" * 70)
        print(f"授权服务器: {self.授权服务器}")
        print(f"客户端: {self.客户端}")
        print("-" * 70)

        # 模拟授权码流程
        print(f"\n[OAuth2.0授权码流程]")
        流程 = [
            ("1. 授权请求", "客户端 -> 授权服务器", "GET /authorize?response_type=code&client_id=xxx&redirect_uri=xxx"),
            ("2. 用户授权", "用户在授权服务器登录并同意", "授权服务器展示授权页面"),
            ("3. 授权码返回", "授权服务器 -> 客户端", "302 redirect_uri?code=AUTH_CODE"),
            ("4. 令牌交换", "客户端 -> 授权服务器", "POST /token {code, client_secret}"),
            ("5. 访问资源", "客户端 -> 资源服务器", "GET /api with Bearer token"),
        ]

        for 步骤, 方向, 内容 in 流程:
            print(f"  {步骤}")
            print(f"    方向: {方向}")
            print(f"    内容: {内容}")

        # 模拟授权码
        模拟码 = base64.b64encode(os.urandom(20)).decode()[:32]
        print(f"\n[模拟授权码]")
        print(f"  code: {模拟码}")
        print(f"  有效期: 10分钟")
        print(f"  使用次数: 1次(一次性)")

        # 劫持攻击场景
        print(f"\n[授权码劫持攻击场景]")
        攻击场景 = [
            ("开放重定向", "redirect_uri验证不严",
             "redirect_uri=https://app.com.evil.com", "高", True),
            ("URI配置错误", "通配符配置过于宽松",
             "redirect_uri=https://app.com/redirect", "中", True),
            ("XSS截获", "客户端存在XSS漏洞",
             "注入脚本读取location.hash中的code", "高", True),
            ("Referer泄露", "通过Referer头泄露",
             "外链请求带Referer含code", "中", True),
            ("日志泄露", "code被记录在服务器日志",
             "access_log含code参数", "中", True),
            ("浏览器历史", "code留在浏览器历史",
             "history中含redirect_uri?code=xxx", "低", True),
        ]

        print(f"  {'场景':<14} {'原理':<24} {'载荷示例':<32} {'风险':>6} {'可利用':>6}")
        for 场景, 原理, 载荷, 风险, 可利用 in 攻击场景:
            print(f"  {场景:<14} {原理:<24} {载荷:<32} {风险:>6} {'是' if 可利用 else '否':>6}")

        # 防护检查
        print(f"\n[防护机制检查]")
        检查项 = [
            ("redirect_uri精确匹配", "是", "通过", "仅允许精确匹配的URI"),
            ("state参数", "是", "通过", "CSRF防护"),
            ("PKCE", "是", "通过", "防止授权码截获"),
            ("code一次性使用", "是", "通过", "使用后立即失效"),
            ("code有效期", "10分钟", "通过", "短有效期"),
            ("HTTPS强制", "是", "通过", "传输加密"),
            ("Referer-Policy", "no-referrer", "通过", "防止Referer泄露"),
            ("CSP策略", "严格", "通过", "防XSS截获"),
        ]

        print(f"  {'检查项':<22} {'配置':>12} {'结果':>6} {'说明'}")
        for 检查, 配置, 结果, 说明 in 检查项:
            print(f"  {检查:<22} {str(配置):>12} {结果:>6} {说明}")

        print(f"\n[安全建议]")
        print(f"  1. redirect_uri精确匹配(不允许通配符)")
        print(f"  2. 强制使用PKCE (S256)")
        print(f"  3. 使用state参数防CSRF")
        print(f"  4. 授权码一次性使用+短有效期")
        print(f"  5. 全程HTTPS + HSTS")
        print(f"  6. 实施CSP防XSS")
        print(f"  7. 配置Referer-Policy: no-referrer")

        return {
            "攻击场景数": len(攻击场景),
            "防护检查数": len(检查项),
            "防护通过率": sum(1 for c in 检查项 if c[2] == "通过") / len(检查项)
        }

    def 重定向URI验证(self) -> Dict:
        """重定向URI验证绕过检测"""
        print("\n" + "=" * 70)
        print("【重定向URI验证绕过检测】")
        print("=" * 70)
        print("检测redirect_uri验证是否存在绕过")
        print("-" * 70)

        # 合法URI
        合法URI = "https://app.example.com/callback"

        # 绕过尝试
        绕过尝试 = [
            ("子域名绕过", "https://evil.app.example.com/callback"),
            ("路径绕过", "https://app.example.com/callback/../../../redirect"),
            ("查询参数绕过", "https://app.example.com/callback?next=https://evil.com"),
            ("片段绕过", "https://app.example.com/callback#https://evil.com"),
            ("@符号绕过", "https://app.example.com/callback@evil.com"),
            ("开放重定向", "https://app.example.com/redirect?url=https://evil.com"),
            ("协议绕过", "javascript://app.example.com/callback%0Aalert(1)"),
            ("编码绕过", "https://app.example.com/c%61llback"),
            ("点号绕过", "https://app.example.com/callback.evil.com"),
            ("端口绕过", "https://app.example.com:8080/callback"),
        ]

        print(f"\n[绕过尝试]")
        print(f"  合法URI: {合法URI}")
        print(f"  {'类型':<16} {'测试URI':<52} {'结果':>6}")

        拦截数 = 0
        for 类型, uri in 绕过尝试:
            # 模拟验证逻辑
            拦截 = True  # 默认拦截
            if "精确匹配" in str(self):
                拦截 = True

            结果 = "拦截" if 拦截 else "通过!"
            if 拦截:
                拦截数 += 1
            print(f"  {类型:<16} {uri:<52} {结果:>6}")

        拦截率 = 拦截数 / len(绕过尝试)

        print(f"\n[验证统计]")
        print(f"  测试URI数: {len(绕过尝试)}")
        print(f"  拦截数: {拦截数}")
        print(f"  拦截率: {拦截率:.0%}")
        print(f"  URI验证: {'安全' if 拦截率 == 1.0 else '存在绕过风险!'}")

        print(f"\n[最佳实践]")
        print(f"  1. 精确匹配: redirect_uri必须与注册完全一致")
        print(f"  2. 不允许通配符: 禁止*通配符")
        print(f"  3. 协议限制: 只允许https(生产环境)")
        print(f"  4. 路径规范化: 防止路径遍历绕过")
        print(f"  5. 注册制: 预注册所有合法redirect_uri")
        print(f"  6. 禁止localhost: 生产环境禁止localhost")

        return {
            "测试URI数": len(绕过尝试),
            "拦截率": 拦截率
        }

    def PKCE检查(self) -> Dict:
        """PKCE (Proof Key for Code Exchange) 安全检查"""
        print("\n" + "=" * 70)
        print("【PKCE安全检查】")
        print("=" * 70)
        print("检查PKCE实现是否正确")
        print("-" * 70)

        print(f"\n[PKCE原理]")
        print(f"  1. 客户端生成code_verifier (43-128字符随机串)")
        print(f"  2. 计算code_challenge = BASE64URL(SHA256(code_verifier))")
        print(f"  3. 授权请求携带code_challenge")
        print(f"  4. 令牌交换时携带code_verifier")
        print(f"  5. 服务器验证SHA256(code_verifier) == code_challenge")
        print(f"  防止授权码截获后被交换为令牌")

        # 模拟PKCE流程
        code_verifier = base64.urlsafe_b64encode(os.urandom(32)).decode().rstrip("=")
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode().rstrip("=")

        print(f"\n[PKCE流程模拟]")
        print(f"  code_verifier: {code_verifier[:40]}...")
        print(f"  code_challenge: {code_challenge[:40]}...")
        print(f"  challenge方法: S256")

        # 验证
        验证结果 = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode().rstrip("=")
        匹配 = 验证结果 == code_challenge

        print(f"  验证结果: {'匹配' if 匹配 else '不匹配'}")
        print(f"  PKCE验证: {'通过' if 匹配 else '失败'}")

        # PKCE安全检查
        print(f"\n[PKCE安全检查]")
        检查项 = [
            ("code_verifier长度", "43-128字符", len(code_verifier), "通过"),
            ("code_verifier随机性", "高熵随机串", "是", "通过"),
            ("challenge方法", "S256", "S256", "通过"),
            ("code_verifier传输", "仅令牌交换时", "是", "通过"),
            ("code_challenge传输", "授权请求时", "是", "通过"),
            ("HTTPS传输", "强制", "是", "通过"),
        ]

        print(f"  {'检查项':<24} {'期望':>14} {'实际':>14} {'结果':>6}")
        for 检查, 期望, 实际, 结果 in 检查项:
            print(f"  {检查:<24} {str(期望):>14} {str(实际):>14} {结果:>6}")

        # PKCE缺失风险
        print(f"\n[PKCE缺失风险分析]")
        print(f"  无PKCE场景:")
        print(f"    1. 攻击者截获授权码")
        print(f"    2. 攻击者用截获的code交换令牌")
        print(f"    3. 攻击者获得用户访问令牌")
        print(f"    4. 可访问用户受保护资源")

        print(f"\n  有PKCE场景:")
        print(f"    1. 攻击者截获授权码(含code_challenge)")
        print(f"    2. 攻击者尝试用code交换令牌")
        print(f"    3. 服务器要求提供code_verifier")
        print(f"    4. 攻击者无法生成正确的code_verifier")
        print(f"    5. 令牌交换失败，攻击被阻止")

        return {
            "检查项数": len(检查项),
            "通过率": 1.0,
            "PKCE验证": "通过"
        }

    def 运行所有审计(self):
        """运行所有OAuth2.0安全审计"""
        print("\n" + "#" * 70)
        print("#  第二部分：OAuth2.0安全审计")
        print("#" * 70)

        self.授权码劫持检测()
        self.重定向URI验证()
        self.PKCE检查()


# ============================================================================
# 第三部分：SAML安全检测
# ============================================================================

class SAML安全检测器:
    """
    SAML安全检测器
    
    检测SAML(安全断言标记语言)实现的安全问题：
    - XML签名包装攻击
    - SAML响应注入
    - 重放攻击
    """

    def __init__(self):
        self.IdP = "https://idp.example.com"
        self.SP = "https://sp.example.com"

    def XML签名包装攻击(self) -> Dict:
        """
        XML签名包装(XSW)攻击检测
        
        XSW攻击原理:
        1. 攻击者获取合法签名的SAML响应
        2. 修改XML结构，在签名外添加恶意断言
        3. 签名验证通过(签名内容未变)
        4. 但应用读取的是恶意断言(签名外的内容)
        
        这利用了XML签名验证和XML解析之间的不一致
        """
        print("\n" + "=" * 70)
        print("【XML签名包装(XSW)攻击检测】")
        print("=" * 70)
        print(f"IdP: {self.IdP}")
        print(f"SP: {self.SP}")
        print("-" * 70)

        # 模拟SAML响应
        print(f"\n[正常SAML响应结构]")
        正常响应 = """
<samlp:Response>
  <ds:Signature>
    <ds:SignedInfo>
      <ds:Reference URI="# assertion-id-123">
        <!-- 签名引用 assertion-id-123 -->
      </ds:Reference>
    </ds:SignedInfo>
    <ds:SignatureValue>...签名值...</ds:SignatureValue>
  </ds:Signature>
  <saml:Assertion ID="assertion-id-123">
    <saml:Subject>user@example.com</saml:Subject>
    <saml:AttributeStatement>
      <saml:Attribute Name="role">user</saml:Attribute>
    </saml:AttributeStatement>
  </saml:Assertion>
</samlp:Response>"""
        print(正常响应)

        # XSW攻击变体
        print(f"\n[XSW攻击变体]")
        xsw变体 = [
            ("XSW1", "在签名前插入恶意断言",
             "签名验证原始断言，但应用读取恶意断言", "高"),
            ("XSW2", "签名包装在恶意断言内",
             "签名引用原始断言，恶意断言在外层", "高"),
            ("XSW3", "复制断言并修改属性",
             "原始断言被签名，复制断言被应用", "高"),
            ("XSW4", "在Response元素外包装",
             "利用XML命名空间混淆", "中"),
            ("XSW5", "在Signature元素内插入",
             "利用签名处理顺序差异", "中"),
            ("XSW6", "利用注释注入",
             "XML注释改变解析结果", "中"),
            ("XSW7", "利用实体注入",
             "XML实体扩展改变文档结构", "中"),
            ("XSW8", "利用属性顺序",
             "属性顺序影响解析结果", "低"),
        ]

        print(f"  {'变体':<8} {'原理':<28} {'描述':<32} {'风险':>6}")
        for 变体, 原理, 描述, 风险 in xsw变体:
            print(f"  {变体:<8} {原理:<28} {描述:<32} {风险:>6}")

        # 模拟XSW1攻击
        print(f"\n[XSW1攻击示例]")
        攻击响应 = """
<samlp:Response>
  <saml:Assertion ID="evil-assertion">
    <saml:Subject>admin@example.com</saml:Subject>
    <saml:AttributeStatement>
      <saml:Attribute Name="role">admin</saml:Attribute>  <!-- 提权! -->
    </saml:AttributeStatement>
  </saml:Assertion>
  <ds:Signature>
    <!-- 签名仍然验证 assertion-id-123 -->
    <ds:Reference URI="#assertion-id-123">...</ds:Reference>
  </ds:Signature>
  <saml:Assertion ID="assertion-id-123">
    <!-- 原始断言(被签名但被忽略) -->
    <saml:Subject>user@example.com</saml:Subject>
  </saml:Assertion>
</samlp:Response>"""
        print(攻击响应)

        # 防护检查
        print(f"\n[XSW防护检查]")
        检查项 = [
            ("签名后验证", "先验证签名再读取内容", "是", "通过"),
            ("引用一致性", "验证签名的URI与读取的元素一致", "是", "通过"),
            ("唯一断言", "只允许一个被签名的断言", "是", "通过"),
            ("DOM规范化", "使用安全的XML解析器", "是", "通过"),
            ("签名位置", "验证签名在正确位置", "是", "通过"),
            ("ID唯一性", "确保XML ID唯一", "是", "通过"),
        ]

        print(f"  {'检查项':<20} {'期望':>28} {'实际':>6} {'结果':>6}")
        for 检查, 期望, 实际, 结果 in 检查项:
            print(f"  {检查:<20} {期望:>28} {实际:>6} {结果:>6}")

        # 安全建议
        print(f"\n[XSW防御建议]")
        print(f"  1. 使用安全的SAML库(如OneLogin/python-saml)")
        print(f"  2. 验证签名引用与读取元素一致")
        print(f"  3. 只接受签名断言中的属性")
        print(f"  4. 禁止未签名断言")
        print(f"  5. 使用XPath评估时注意上下文")
        print(f"  6. 定期测试XSW攻击变体")

        return {
            "XSW变体数": len(xsw变体),
            "检查项数": len(检查项),
            "防护通过率": 1.0
        }

    def SAML响应注入(self) -> Dict:
        """SAML响应注入攻击检测"""
        print("\n" + "=" * 70)
        print("【SAML响应注入攻击检测】")
        print("=" * 70)
        print("检测SAML响应注入漏洞")
        print("-" * 70)

        # 注入攻击类型
        print(f"\n[SAML响应注入类型]")
        注入类型 = [
            ("NameID注入", "修改NameID为其他用户身份",
             "user@example.com -> admin@example.com", "高"),
            ("属性注入", "添加/修改属性值",
             "role=user -> role=admin", "高"),
            ("条件注入", "修改条件(时间/受众)",
             "扩展有效期或更改Audience", "中"),
            ("Subject确认注入", "修改SubjectConfirmation",
             "更改Recipient/BadgeInResponseTo", "中"),
            ("Issuer注入", "修改Issuer URI",
             "伪造IdP身份", "高"),
            ("AuthnStatement注入", "修改认证声明",
             "更改认证上下文/时间", "中"),
        ]

        print(f"  {'类型':<22} {'描述':<24} {'示例':<36} {'风险':>6}")
        for 类型, 描述, 示例, 风险 in 注入类型:
            print(f"  {类型:<22} {描述:<24} {示例:<36} {风险:>6}")

        # XXE注入
        print(f"\n[XXE注入攻击]")
        print(f"  攻击载荷:")
        xxepayload = """<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<samlp:Response>
  <saml:Assertion>
    <saml:Subject>&xxe;</saml:Subject>
  </saml:Assertion>
</samlp:Response>"""
        print(xxepayload)

        print(f"\n  XXE影响:")
        影响 = [
            "文件读取: 读取服务器本地文件",
            "SSRF: 发起服务端请求",
            "DoS: 递归实体扩展(Billion Laughs)",
            "信息泄露: 读取配置文件/密钥",
        ]
        for i, 影响 in enumerate(影响, 1):
            print(f"    {i}. {影响}")

        # 防护措施
        print(f"\n[防护措施]")
        防护 = [
            "禁用XML外部实体: 解析器禁用DTD和外部实体",
            "输入验证: 验证SAML响应格式和内容",
            "签名验证: 严格验证SAML响应签名",
            "时间验证: 检查NotBefore/NotOnOrAfter",
            "受众验证: 验证AudienceRestriction",
            "条件验证: 验证所有Conditions",
            "使用安全库: 使用经过审计的SAML库",
        ]

        for i, 措施 in enumerate(防护, 1):
            print(f"  {i}. {措施}")

        return {
            "注入类型数": len(注入类型),
            "防护措施数": len(防护)
        }

    def 重放攻击检测(self) -> Dict:
        """SAML重放攻击检测"""
        print("\n" + "=" * 70)
        print("【SAML重放攻击检测】")
        print("=" * 70)
        print("检测SAML令牌重放攻击")
        print("-" * 70)

        # 重放攻击原理
        print(f"\n[重放攻击原理]")
        print(f"  1. 攻击者截获合法的SAML响应/断言")
        print(f"  2. 在有效期内重放给服务提供者")
        print(f"  3. SP验证签名通过")
        print(f"  4. 攻击者获得认证会话")

        # 重放防护机制
        print(f"\n[重放防护机制]")
        防护 = [
            ("NotOnOrAfter", "断言过期时间", "中", "过期后无法重放"),
            ("InResponseTo", "请求-响应配对", "高", "确保响应对应特定请求"),
            ("缓存检测", "记录已用断言ID", "高", "同一断言不可二次使用"),
            ("时间窗口", "严格时间偏差限制", "中", "缩短重放窗口"),
            ("绑定验证", "验证SAML绑定", "中", "确保正确绑定类型"),
            ("会话绑定", "断言绑定到会话", "高", "断言与特定会话关联"),
        ]

        print(f"  {'机制':<16} {'原理':<24} {'防护级':>6} {'说明'}")
        for 机制, 原理, 等级, 说明 in 防护:
            print(f"  {机制:<16} {原理:<24} {等级:>6} {说明}")

        # 模拟重放检测
        print(f"\n[重放检测模拟]")
        断言ID = "_" + base64.b64encode(os.urandom(16)).decode().rstrip("=")
        已用断言 = set()

        # 第一次使用(合法)
        print(f"  第一次使用(合法):")
        print(f"    断言ID: {断言ID}")
        print(f"    状态: {'已用' if 断言ID in 已用断言 else '新断言'}")
        print(f"    结果: 接受")
        已用断言.add(断言ID)

        # 第二次使用(重放)
        print(f"\n  第二次使用(重放):")
        print(f"    断言ID: {断言ID}")
        print(f"    状态: {'已用! 重放检测!' if 断言ID in 已用断言 else '新断言'}")
        print(f"    结果: 拒绝 - 检测到重放攻击")

        # InResponseTo验证
        print(f"\n[InResponseTo验证模拟]")
        请求ID = "_" + base64.b64encode(os.urandom(16)).decode().rstrip("=")
        响应ID = "_" + base64.b64encode(os.urandom(16)).decode().rstrip("=")

        print(f"  AuthnRequest ID: {请求ID}")
        print(f"  Response InResponseTo: {请求ID} (匹配)")
        print(f"  结果: 接受 - InResponseTo验证通过")

        # 伪造的InResponseTo
        伪造ID = "_" + base64.b64encode(os.urandom(16)).decode().rstrip("=")
        print(f"\n  AuthnRequest ID: {请求ID}")
        print(f"  Response InResponseTo: {伪造ID} (不匹配!)")
        print(f"  结果: 拒绝 - InResponseTo验证失败")

        return {
            "防护机制数": len(防护),
            "检测能力": "完整"
        }

    def 运行所有检测(self):
        """运行所有SAML安全检测"""
        print("\n" + "#" * 70)
        print("#  第三部分：SAML安全检测")
        print("#" * 70)

        self.XML签名包装攻击()
        self.SAML响应注入()
        self.重放攻击检测()


# ============================================================================
# 第四部分：零信任架构实现
# ============================================================================

class 零信任架构演示:
    """
    零信任架构实现演示
    
    零信任核心原则: "从不信任，始终验证"
    - 持续验证用户和设备身份
    - 最小权限访问控制
    - 微分段网络架构
    - 动态访问策略
    
    NIST 800-207零信任架构:
    - PE (Policy Engine): 策略引擎
    - PA (Policy Administrator): 策略管理员
    - PEP (Policy Enforcement Point): 策略执行点
    """

    def __init__(self):
        self.信任评分阈值 = 0.7
        self.验证频率 = "持续"

    def 持续验证(self) -> Dict:
        """
        持续验证机制
        
        零信任不同于传统边界安全，不一次性验证，
        而是持续评估信任级别
        """
        print("\n" + "=" * 70)
        print("【零信任 - 持续验证】")
        print("=" * 70)
        print("演示零信任持续验证机制")
        print("-" * 70)

        # 信任评分模型
        print(f"\n[信任评分模型]")
        评分维度 = [
            ("身份验证", 0.25, "MFA通过/密码强度/会话安全"),
            ("设备状态", 0.20, "设备合规性/补丁状态/安全软件"),
            ("网络位置", 0.15, "网络类型/地理位置/IP信誉"),
            ("行为分析", 0.20, "访问模式/异常检测/UEBA"),
            ("数据敏感度", 0.10, "被访问数据的安全等级"),
            ("时间因素", 0.10, "访问时间/频率/持续时间"),
        ]

        print(f"  {'维度':<14} {'权重':>6} {'评估因素'}")
        for 维度, 权重, 因素 in 评分维度:
            print(f"  {维度:<14} {权重:>6.0%} {因素}")

        # 模拟信任评分计算
        print(f"\n[信任评分计算示例]")
        用户场景 = [
            {"场景": "办公室正常访问", "身份": 0.95, "设备": 0.90, "网络": 0.95,
             "行为": 0.85, "数据": 0.70, "时间": 0.90},
            {"场景": "远程VPN访问", "身份": 0.90, "设备": 0.80, "网络": 0.70,
             "行为": 0.80, "数据": 0.70, "时间": 0.85},
            {"场景": "未知设备访问", "身份": 0.85, "设备": 0.30, "网络": 0.50,
             "行为": 0.40, "数据": 0.80, "时间": 0.50},
            {"场景": "异常行为访问", "身份": 0.90, "设备": 0.85, "网络": 0.80,
             "行为": 0.20, "数据": 0.90, "时间": 0.30},
        ]

        for 场景 in 用户场景:
            信任分 = (
                场景["身份"] * 0.25 +
                场景["设备"] * 0.20 +
                场景["网络"] * 0.15 +
                场景["行为"] * 0.20 +
                场景["数据"] * 0.10 +
                场景["时间"] * 0.10
            )

            决策 = "允许" if 信任分 >= 0.7 else ("需要MFA" if 信任分 >= 0.5 else "拒绝")
            风险等级 = "低" if 信任分 >= 0.7 else ("中" if 信任分 >= 0.5 else "高")

            print(f"\n  场景: {场景['场景']}")
            print(f"    身份={场景['身份']:.2f} 设备={场景['设备']:.2f} 网络={场景['网络']:.2f} "
                  f"行为={场景['行为']:.2f}")
            print(f"    信任评分: {信任分:.2f} (阈值: {self.信任评分阈值})")
            print(f"    风险等级: {风险等级}")
            print(f"    访问决策: {决策}")

        # 持续验证策略
        print(f"\n[持续验证策略]")
        策略 = [
            ("低风险(>0.7)", "30分钟", "MFA", "允许", "降低验证频率"),
            ("中风险(0.5-0.7)", "10分钟", "MFA+额外验证", "条件允许", "提高验证频率"),
            ("高风险(<0.5)", "实时", "MFA+审批", "拒绝/限制", "持续验证"),
        ]

        print(f"  {'风险级':>14} {'验证频率':>10} {'要求':>14} {'决策':>10} {'说明'}")
        for 风险, 频率, 要求, 决策, 说明 in 策略:
            print(f"  {风险:>14} {频率:>10} {要求:>14} {决策:>10} {说明}")

        return {
            "评分维度数": len(评分维度),
            "测试场景数": len(用户场景)
        }

    def 微分段实现(self) -> Dict:
        """微分段(Microsegmentation)实现"""
        print("\n" + "=" * 70)
        print("【零信任 - 微分段实现】")
        print("=" * 70)
        print("演示零信任网络微分段架构")
        print("-" * 70)

        # 传统vs零信任对比
        print(f"\n[传统边界安全 vs 零信任微分段]")
        对比 = [
            ("信任模型", "内部可信", "从不信任"),
            ("安全边界", "网络边界", "每个资源"),
            ("访问控制", "网络层", "应用层"),
            ("分段粒度", "VLAN/子网", "进程/容器"),
            ("策略执行", "防火墙", "PEP(策略执行点)"),
            ("默认策略", "允许", "拒绝"),
        ]

        print(f"  {'维度':<14} {'传统边界':>14} {'零信任':>14}")
        for 维度, 传统, 零信任 in 对比:
            print(f"  {维度:<14} {传统:>14} {零信任:>14}")

        # 微分段架构
        print(f"\n[微分段架构]")
        print(f"  ┌─────────────────────────────────────────┐")
        print(f"  │         零信任控制器 (PE/PA)             │")
        print(f"  │    策略引擎 + 策略管理员 + 信任评估      │")
        print(f"  └─────────────┬───────────────────────────┘")
        print(f"                │ 策略下发")
        print(f"  ┌─────────────┼───────────────────────────┐")
        print(f"  │ PEP        │ PEP        │ PEP           │")
        print(f"  │ (Web)      │ (API)      │ (DB)          │")
        print(f"  │ ┌───────┐  │ ┌───────┐  │ ┌───────┐    │")
        print(f"  │ │ 资源A  │  │ │ 资源B  │  │ │ 资源C │    │")
        print(f"  │ └───────┘  │ └───────┘  │ └───────┘    │")
        print(f"  └────────────┴───────────┴───────────────┘")

        # 分段策略
        print(f"\n[微分段策略示例]")
        策略 = [
            {"源": "用户组-研发", "目标": "应用-代码库", "端口": "443", "条件": "MFA+合规设备", "动作": "允许"},
            {"源": "用户组-研发", "目标": "应用-生产DB", "端口": "5432", "条件": "审批+MFA", "动作": "条件允许"},
            {"源": "用户组-市场", "目标": "应用-代码库", "端口": "*", "条件": "-", "动作": "拒绝"},
            {"源": "用户组-运维", "目标": "应用-生产DB", "端口": "5432", "条件": "MFA+审批+堡垒机", "动作": "允许"},
            {"源": "任意", "目标": "任意", "端口": "*", "条件": "-", "动作": "默认拒绝"},
        ]

        print(f"  {'源':<16} {'目标':<16} {'端口':>6} {'条件':<18} {'动作':>8}")
        for p in 策略:
            print(f"  {p['源']:<16} {p['目标']:<16} {p['端口']:>6} {p['条件']:<18} {p['动作']:>8}")

        # 微分段技术
        print(f"\n[微分段实现技术]")
        技术 = [
            ("基于主机Agent", "在每台主机部署Agent", "细粒度高", "Agent管理开销"),
            ("基于网络", "使用SDN/下一代防火墙", "无需Agent", "粒度有限"),
            ("基于身份", "基于用户身份的策略", "与位置无关", "需身份基础设施"),
            ("基于云", "云安全组/微分段", "云原生", "仅限云环境"),
            ("基于进程", "进程级访问控制", "最细粒度", "部署复杂"),
        ]

        print(f"  {'技术':<14} {'原理':<24} {'优势':<12} {'劣势'}")
        for 技术, 原理, 优势, 劣势 in 技术:
            print(f"  {技术:<14} {原理:<24} {优势:<12} {劣势}")

        return {
            "策略数": len(策略),
            "技术数": len(技术)
        }

    def 动态访问控制(self) -> Dict:
        """动态访问控制实现"""
        print("\n" + "=" * 70)
        print("【零信任 - 动态访问控制】")
        print("=" * 70)
        print("演示基于上下文的动态访问控制")
        print("-" * 70)

        # 动态策略引擎
        print(f"\n[动态访问控制流程]")
        print(f"  1. 用户发起访问请求")
        print(f"  2. PEP拦截请求，转发给PE")
        print(f"  3. PE收集上下文(身份/设备/网络/行为)")
        print(f"  4. PE计算信任评分")
        print(f"  5. PE基于策略+评分做出决策")
        print(f"  6. PA下发决策给PEP")
        print(f"  7. PEP执行决策(允许/拒绝/条件)")

        # 策略规则
        print(f"\n[动态策略规则]")
        规则 = [
            {"规则": "研发访问代码库", "条件": "工作日+办公室+MFA+合规设备",
             "动作": "允许", "有效期": "4小时"},
            {"规则": "研发访问代码库", "条件": "非工作日+远程+MFA+合规设备",
             "动作": "需要审批", "有效期": "2小时"},
            {"规则": "运维访问生产DB", "条件": "任何时间+堡垒机+审批+MFA",
             "动作": "允许", "有效期": "1小时"},
            {"规则": "运维访问生产DB", "条件": "无堡垒机",
             "动作": "拒绝", "有效期": "-"},
            {"规则": "任意访问管理后台", "条件": "非白名单IP",
             "动作": "拒绝", "有效期": "-"},
            {"规则": "异常行为检测", "条件": "UEBA评分<0.3",
             "动作": "即时撤销", "有效期": "-"},
        ]

        print(f"  {'规则':<22} {'条件':<32} {'动作':>8} {'有效期':>8}")
        for r in 规则:
            print(f"  {r['规则']:<22} {r['条件']:<32} {r['动作']:>8} {r['有效期']:>8}")

        # 动态响应模拟
        print(f"\n[动态响应模拟]")
        事件 = [
            ("用户登录", 0.85, "低", "允许", "4小时"),
            ("设备合规检查失败", 0.55, "中", "需要MFA", "1小时"),
            ("异常下载行为", 0.30, "高", "限制下载", "实时"),
            ("非工作时间访问", 0.60, "中", "需要审批", "2小时"),
            ("未知设备登录", 0.25, "高", "拒绝", "-"),
            ("UEBA触发告警", 0.15, "严重", "撤销会话", "即时"),
        ]

        print(f"  {'事件':<22} {'信任分':>8} {'风险':>6} {'动作':>10} {'持续':>8}")
        for 事件名, 分数, 风险, 动作, 持续 in 事件:
            print(f"  {事件名:<22} {分数:>8.2f} {风险:>6} {动作:>10} {持续:>8}")

        print(f"\n[ABAC vs RBAC]")
        print(f"  {'特性':<16} {'RBAC':>14} {'ABAC':>14}")
        对比 = [
            ("决策依据", "角色", "属性+上下文"),
            ("灵活性", "低", "高"),
            ("动态性", "静态", "动态"),
            ("粒度", "角色级", "属性级"),
            ("复杂度", "简单", "复杂"),
            ("零信任适配", "部分", "完全"),
        ]
        for 特性, rbac, abac in 对比:
            print(f"  {特性:<16} {rbac:>14} {abac:>14}")

        return {
            "规则数": len(规则),
            "事件数": len(事件)
        }

    def 运行所有演示(self):
        """运行所有零信任架构演示"""
        print("\n" + "#" * 70)
        print("#  第四部分：零信任架构实现")
        print("#" * 70)

        self.持续验证()
        self.微分段实现()
        self.动态访问控制()


# ============================================================================
# 第五部分：权限提升检测
# ============================================================================

class 权限提升检测器:
    """
    权限提升检测器
    
    检测权限提升和横向移动行为：
    - 横向移动检测
    - 权限滥用监控
    - 异常行为分析
    """

    def __init__(self):
        self.告警阈值 = 0.6

    def 横向移动检测(self) -> Dict:
        """横向移动行为检测"""
        print("\n" + "=" * 70)
        print("【横向移动检测】")
        print("=" * 70)
        print("检测攻击者在网络内的横向移动行为")
        print("-" * 70)

        # 横向移动技术
        print(f"\n[常见横向移动技术]")
        技术 = [
            ("Pass-the-Hash", "使用NTLM哈希认证", "Windows", "高"),
            ("Pass-the-Ticket", "使用Kerberos票据", "Windows", "高"),
            ("WMI远程执行", "通过WMI远程执行命令", "Windows", "中"),
            ("PsExec", "远程执行工具", "Windows", "中"),
            ("SSH密钥传播", "利用SSH密钥横向移动", "Linux", "中"),
            ("RDP横向移动", "通过远程桌面移动", "Windows", "中"),
            ("Kerberoasting", "提取Kerberos服务票据", "Windows", "高"),
            ("DCSync", "模拟域控同步凭据", "Windows", "严重"),
        ]

        print(f"  {'技术':<20} {'原理':<24} {'平台':>8} {'风险':>6}")
        for 技术, 原理, 平台, 风险 in 技术:
            print(f"  {技术:<20} {原理:<24} {平台:>8} {风险:>6}")

        # 检测规则
        print(f"\n[横向移动检测规则]")
        规则 = [
            {"规则": "非常规时间登录", "描述": "非工作时间登录多个系统", "权重": 0.15},
            {"规则": "新登录路径", "描述": "A->B->C从未出现过的路径", "权重": 0.20},
            {"规则": "凭据使用异常", "描述": "同一凭据多系统使用", "权重": 0.25},
            {"规则": "管理工具异常", "描述": "PsExec/WMI异常调用", "权重": 0.15},
            {"规则": "认证协议异常", "描述": "降级到NTLM等弱协议", "权重": 0.10},
            {"规则": "网络扫描行为", "描述": "端口/服务探测行为", "权重": 0.15},
        ]

        print(f"  {'规则':<18} {'描述':<32} {'权重':>6}")
        for r in 规则:
            print(f"  {r['规则']:<18} {r['描述']:<32} {r['权重']:>6.0%}")

        # 模拟检测
        print(f"\n[横向移动检测模拟]")
        事件序列 = [
            ("T+0min", "用户A登录系统1", 0.10, "正常"),
            ("T+5min", "用户A访问系统2", 0.15, "正常"),
            ("T+10min", "用户A访问系统3(首次)", 0.35, "关注"),
            ("T+15min", "用户A使用PsExec远程", 0.55, "告警"),
            ("T+20min", "用户A访问系统4(非常规时间)", 0.70, "告警"),
            ("T+25min", "用户A尝试DCSync", 0.95, "严重告警"),
        ]

        print(f"  {'时间':>8} {'事件':<32} {'风险分':>8} {'状态':>8}")
        for 时间, 事件, 风险, 状态 in 事件序列:
            标记 = " <==!" if 风险 > self.告警阈值 else ""
            print(f"  {时间:>8} {事件:<32} {风险:>8.2f} {状态:>8}{标记}")

        print(f"\n[检测结果]")
        print(f"  检测到横向移动: 是")
        print(f"  涉及系统: 4个")
        print(f"  涉及用户: 1个")
        print(f"  最高风险: 0.95 (DCSync)")
        print(f"  建议: 立即隔离用户A，调查凭据泄露")

        return {
            "技术数": len(技术),
            "规则数": len(规则),
            "检测到": True
        }

    def 权限滥用监控(self) -> Dict:
        """权限滥用行为监控"""
        print("\n" + "=" * 70)
        print("【权限滥用监控】")
        print("=" * 70)
        print("监控特权账户的权限滥用行为")
        print("-" * 70)

        # 权限滥用场景
        print(f"\n[权限滥用场景]")
        场景 = [
            ("数据批量导出", "大量下载敏感数据", "高", "DLP+审计"),
            ("权限变更", "未经审批修改权限", "高", "变更管理+审批"),
            ("配置修改", "修改安全配置削弱防护", "严重", "配置监控"),
            ("日志清除", "删除或篡改审计日志", "严重", "日志完整性"),
            ("账户创建", "创建后门账户", "严重", "账户监控"),
            ("远程执行", "在非授权系统远程执行", "中", "PEP+审计"),
            ("数据访问", "访问超出职责的数据", "高", "ABAC+审计"),
            ("工具使用", "使用非授权管理工具", "中", "工具白名单"),
        ]

        print(f"  {'场景':<16} {'描述':<28} {'风险':>6} {'监控方案'}")
        for 场景, 描述, 风险, 监控 in 场景:
            print(f"  {场景:<16} {描述:<28} {风险:>6} {监控}")

        # UEBA(用户实体行为分析)
        print(f"\n[UEBA行为基线]")
        行为基线 = [
            {"行为": "日均登录次数", "基线": "2-5次", "异常": ">10次", "风险": 0.3},
            {"行为": "日均访问系统数", "基线": "3-5个", "异常": ">10个", "风险": 0.25},
            {"行为": "数据下载量", "基线": "<100MB", "异常": ">1GB", "风险": 0.35},
            {"行为": "工作时间外活动", "基线": "<10%", "异常": ">30%", "风险": 0.20},
            {"行为": "权限使用频率", "基线": "低频", "异常": "突增", "风险": 0.30},
            {"行为": "失败认证次数", "基线": "<5次", "异常": ">20次", "风险": 0.15},
        ]

        print(f"  {'行为':<22} {'基线':<12} {'异常':<12} {'权重':>6}")
        for b in 行为基线:
            print(f"  {b['行为']:<22} {b['基线']:<12} {b['异常']:<12} {b['风险']:>6.0%}")

        # 模拟监控告警
        print(f"\n[实时监控告警]")
        告警 = [
            ("CRITICAL", "管理员批量导出用户数据", "admin@corp", "2.3GB", "立即"),
            ("HIGH", "非工作时间创建新账户", "admin@corp", "svc_backdoor", "5分钟"),
            ("HIGH", "修改防火墙规则开放端口", "netadmin", "端口1337", "5分钟"),
            ("MEDIUM", "异常频繁登录失败", "user123", "23次/分钟", "30分钟"),
            ("LOW", "访问超出职责范围数据", "user456", "财务数据", "1小时"),
        ]

        print(f"  {'级别':>10} {'事件':<28} {'账户':>14} {'详情':>14} {'响应':>8}")
        for 级别, 事件, 账户, 详情, 响应 in 告警:
            print(f"  {级别:>10} {事件:<28} {账户:>14} {详情:>14} {响应:>8}")

        return {
            "场景数": len(场景),
            "基线行为数": len(行为基线),
            "告警数": len(告警)
        }

    def 运行所有检测(self):
        """运行所有权限提升检测"""
        print("\n" + "#" * 70)
        print("#  第五部分：权限提升检测")
        print("#" * 70)

        self.横向移动检测()
        self.权限滥用监控()


# ============================================================================
# 第六部分：IAM系统安全
# ============================================================================

class IAM系统安全审计器:
    """
    IAM(身份与访问管理)系统安全审计器
    
    审计IAM系统的安全性：
    - 用户生命周期管理
    - 权限回收审计
    - 特权账户监控
    """

    def __init__(self):
        self.用户总数 = 5000

    def 用户生命周期管理(self) -> Dict:
        """用户生命周期安全审计"""
        print("\n" + "=" * 70)
        print("【用户生命周期安全审计】")
        print("=" * 70)
        print("审计用户从创建到注销的全生命周期安全")
        print("-" * 70)

        # 生命周期阶段
        print(f"\n[用户生命周期阶段]")
        阶段 = [
            ("入职/注册", "HR系统创建用户", "身份来源验证", "自动化配置"),
            ("权限分配", "分配初始权限", "最小权限原则", "角色分配"),
            ("角色变更", "晋升/调岗", "权限重新评估", "审批流程"),
            ("权限临时提升", "临时项目需要", "限时+审批", "自动回收"),
            ("休假/长期离开", "长假/外派", "权限暂时冻结", "恢复机制"),
            ("离职/注销", "离开组织", "权限全部回收", "数据留存"),
        ]

        print(f"  {'阶段':<14} {'触发事件':<16} {'安全控制':<18} {'自动化'}")
        for 阶段, 触发, 控制, 自动 in 阶段:
            print(f"  {阶段:<14} {触发:<16} {控制:<18} {自动}")

        # 审计检查
        print(f"\n[生命周期审计检查]")
        检查 = [
            ("孤儿账户", "离职用户账户仍活跃", 23, "严重"),
            ("权限累积", "调岗后旧权限未回收", 156, "高"),
            ("临时权限过期", "临时权限未自动回收", 89, "高"),
            ("休眠账户", "90天未登录的活跃账户", 312, "中"),
            ("权限冗余", "超出职责的权限", 234, "中"),
            ("共享账户", "多人共享的账户", 12, "高"),
            ("默认账户", "未改名的默认账户", 5, "严重"),
        ]

        print(f"  {'检查项':<16} {'描述':<28} {'数量':>6} {'严重性':>6}")
        for 项, 描述, 数量, 严重 in 检查:
            标记 = "!" if 严重 in ["严重", "高"] else ""
            print(f"  {项:<16} {描述:<28} {数量:>6} {严重:>6}{标记}")

        总问题 = sum(c[2] for c in 检查)
        严重问题 = sum(c[2] for c in 检查 if c[3] in ["严重", "高"])

        print(f"\n[审计总结]")
        print(f"  用户总数: {self.用户总数}")
        print(f"  问题总数: {总问题}")
        print(f"  严重/高问题: {严重问题}")
        print(f"  问题率: {总问题/self.用户总数:.1%}")
        print(f"  合规状态: {'不合规' if 严重问题 > 50 else '部分合规'}")

        print(f"\n[整改建议]")
        print(f"  1. 孤儿账户: 立即禁用离职用户账户")
        print(f"  2. 权限累积: 定期执行权限重新认证")
        print(f"  3. 临时权限: 实现自动过期回收")
        print(f"  4. 休眠账户: 90天未登录自动禁用")
        print(f"  5. 共享账户: 改为个人账户+审计")
        print(f"  6. 默认账户: 重命名+强密码+MFA")
        print(f"  7. 自动化: HR系统集成自动配置/回收")

        return {
            "用户总数": self.用户总数,
            "问题总数": 总问题,
            "严重问题数": 严重问题
        }

    def 权限回收审计(self) -> Dict:
        """权限回收审计"""
        print("\n" + "=" * 70)
        print("【权限回收审计】")
        print("=" * 70)
        print("审计离职/调岗用户的权限回收情况")
        print("-" * 70)

        # 模拟离职用户权限回收审计
        print(f"\n[离职用户权限回收审计]")
        离职用户 = [
            {"姓名": "张三", "离职日期": "2024-01-15", "账户状态": "已禁用",
             "权限回收": "已回收", "数据清理": "已清理", "合规": True},
            {"姓名": "李四", "离职日期": "2024-02-20", "账户状态": "已禁用",
             "权限回收": "部分回收", "数据清理": "未清理", "合规": False},
            {"姓名": "王五", "离职日期": "2024-03-10", "账户状态": "仍活跃",
             "权限回收": "未回收", "数据清理": "未清理", "合规": False},
            {"姓名": "赵六", "离职日期": "2024-04-05", "账户状态": "已禁用",
             "权限回收": "已回收", "数据清理": "已清理", "合规": True},
            {"姓名": "钱七", "离职日期": "2024-05-18", "账户状态": "已禁用",
             "权限回收": "已回收", "数据清理": "部分清理", "合规": False},
        ]

        print(f"  {'姓名':<8} {'离职日期':>12} {'账户状态':>10} {'权限回收':>10} {'数据清理':>10} {'合规':>6}")
        for 用户 in 离职用户:
            合规 = "是" if 用户["合规"] else "否"
            标记 = "" if 用户["合规"] else " <--"
            print(f"  {用户['姓名']:<8} {用户['离职日期']:>12} {用户['账户状态']:>10} "
                  f"{用户['权限回收']:>10} {用户['数据清理']:>10} {合规:>6}{标记}")

        合规数 = sum(1 for u in 离职用户 if u["合规"])
        回收率 = 合规数 / len(离职用户)

        print(f"\n[审计结果]")
        print(f"  离职用户数: {len(离职用户)}")
        print(f"  合规回收数: {合规数}")
        print(f"  回收合规率: {回收率:.0%}")
        print(f"  不合规案例: {len(离职用户) - 合规数}")
        print(f"  严重问题: 王五离职后账户仍活跃!")

        # 调岗用户权限审计
        print(f"\n[调岗用户权限审计]")
        调岗用户 = [
            {"姓名": "孙八", "原部门": "研发", "新部门": "运维",
             "旧权限": "代码库,测试环境", "新权限": "运维工具,生产监控",
             "旧权限状态": "已回收", "合规": True},
            {"姓名": "周九", "原部门": "财务", "新部门": "市场",
             "旧权限": "财务系统,报表数据", "新权限": "CRM,营销工具",
             "旧权限状态": "未回收", "合规": False},
            {"姓名": "吴十", "原部门": "运维", "新部门": "安全",
             "旧权限": "生产服务器,数据库", "新权限": "安全工具,日志系统",
             "旧权限状态": "部分回收", "合规": False},
        ]

        print(f"  {'姓名':<8} {'原部门':>6} {'新部门':>6} {'旧权限状态':>10} {'合规':>6}")
        for 用户 in 调岗用户:
            合规 = "是" if 用户["合规"] else "否"
            标记 = "" if 用户["合规"] else " <--"
            print(f"  {用户['姓名']:<8} {用户['原部门']:>6} {用户['新部门']:>6} "
                  f"{用户['旧权限状态']:>10} {合规:>6}{标记}")

        调岗合规数 = sum(1 for u in 调岗用户 if u["合规"])

        print(f"\n[调岗审计结果]")
        print(f"  调岗用户数: {len(调岗用户)}")
        print(f"  权限回收合规: {调岗合规数}/{len(调岗用户)}")
        print(f"  问题: 周九调岗后仍可访问财务系统!")

        print(f"\n[权限回收最佳实践]")
        print(f"  1. 自动化: HR系统集成触发自动权限回收")
        print(f"  2. 即时性: 离职通知后立即回收(不超过24小时)")
        print(f"  3. 完整性: 回收所有系统/应用的访问权限")
        print(f"  4. 数据处理: 清理个人数据/转移文件所有权")
        print(f"  5. 审计追踪: 记录权限回收操作和验证")
        print(f"  6. 定期审计: 每月审计离职/调岗用户权限")

        return {
            "离职用户数": len(离职用户),
            "回收合规率": 回收率,
            "调岗用户数": len(调岗用户)
        }

    def 特权账户监控(self) -> Dict:
        """特权账户安全监控"""
        print("\n" + "=" * 70)
        print("【特权账户安全监控】")
        print("=" * 70)
        print("监控和管理特权账户安全")
        print("-" * 70)

        # 特权账户类型
        print(f"\n[特权账户类型]")
        类型 = [
            ("域管理员", "Domain Admins", "最高权限", "严重", "严格限制"),
            ("企业管理员", "Enterprise Admins", "森林级权限", "严重", "严格限制"),
            ("本地管理员", "Local Admin", "本地最高权限", "高", "限制使用"),
            ("服务账户", "Service Account", "应用服务权限", "高", "最小化"),
            ("数据库管理员", "DBA", "数据库最高权限", "高", "审计监控"),
            ("云管理员", "Cloud Admin", "云平台管理权限", "严重", "MFA+审计"),
            ("根用户", "root", "系统最高权限", "严重", "避免直接使用"),
        ]

        print(f"  {'类型':<16} {'标识':<20} {'权限':<16} {'风险':>6} {'管理'}")
        for 类型, 标识, 权限, 风险, 管理 in 类型:
            print(f"  {类型:<16} {标识:<20} {权限:<16} {风险:>6} {管理}")

        # PAM(特权访问管理)
        print(f"\n[特权访问管理(PAM)架构]")
        print(f"  ┌──────────────────────────────────────────┐")
        print(f"  │           PAM控制器                      │")
        print(f"  │  凭据保险库 + 访问审批 + 会话录制         │")
        print(f"  └──────────────┬───────────────────────────┘")
        print(f"                 │")
        print(f"  ┌──────────────┼───────────────────────────┐")
        print(f"  │  ┌────────┐  │  ┌────────┐               │")
        print(f"  │  │管理员A  │──┼──│ 堡垒机 │──目标系统     │")
        print(f"  │  └────────┘  │  └────────┘               │")
        print(f"  │  ┌────────┐  │                            │")
        print(f"  │  │管理员B  │──┼──自动旋转密码              │")
        print(f"  │  └────────┘  │                            │")
        print(f"  └──────────────┴────────────────────────────┘")

        # PAM功能
        print(f"\n[PAM核心功能]")
        功能 = [
            ("凭据保险库", "特权密码集中存储加密", "密码不暴露给用户"),
            ("即时访问", "按需申请特权访问", "限时使用"),
            ("审批流程", "特权使用需审批", "多人授权"),
            ("会话录制", "记录特权操作过程", "完整审计"),
            ("密码轮换", "使用后自动更换密码", "防止密码累积"),
            ("行为监控", "实时监控特权行为", "异常告警"),
            ("双因素认证", "特权使用需MFA", "增强认证"),
            ("时间限制", "特权访问限时", "减少窗口"),
        ]

        print(f"  {'功能':<14} {'原理':<24} {'价值'}")
        for 功能, 原理, 价值 in 功能:
            print(f"  {功能:<14} {原理:<24} {价值}")

        # 特权账户监控指标
        print(f"\n[特权账户监控指标]")
        指标 = [
            ("特权账户数", "15", "10", "偏多"),
            ("MFA覆盖率", "85%", "100%", "需提升"),
            ("会话录制率", "92%", "100%", "需提升"),
            ("密码轮换率", "78%", "100%", "需改进"),
            ("审批合规率", "88%", "100%", "需改进"),
            ("异常告警数", "3/月", "<1/月", "需关注"),
        ]

        print(f"  {'指标':<16} {'当前':>8} {'目标':>8} {'状态'}")
        for 指标, 当前, 目标, 状态 in 指标:
            print(f"  {指标:<16} {当前:>8} {目标:>8} {状态}")

        # 告警模拟
        print(f"\n[特权账户告警示例]")
        告警 = [
            ("严重", "root直接登录生产服务器", "立即阻断"),
            ("高", "特权账户非工作时间使用", "需审批"),
            ("高", "特权密码轮换失败", "需处理"),
            ("中", "特权会话录制中断", "需检查"),
            ("中", "特权访问频次异常", "需审查"),
        ]

        print(f"  {'级别':>6} {'事件':<28} {'响应':>10}")
        for 级别, 事件, 响应 in 告警:
            print(f"  {级别:>6} {事件:<28} {响应:>10}")

        return {
            "特权类型数": len(类型),
            "PAM功能数": len(功能),
            "监控指标数": len(指标)
        }

    def 运行所有审计(self):
        """运行所有IAM系统安全审计"""
        print("\n" + "#" * 70)
        print("#  第六部分：IAM系统安全")
        print("#" * 70)

        self.用户生命周期管理()
        self.权限回收审计()
        self.特权账户监控()


# ============================================================================
# 主函数
# ============================================================================

def main():
    """主函数 - 运行所有身份与访问安全实战案例"""
    print(BANNER)
    print(f"启动时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python版本: {sys.version.split()[0]}")
    print(f"安全声明: 本程序仅用于授权安全测试和教育目的")
    print("=" * 80)

    # 1. 身份认证安全检测
    认证检测器 = 身份认证安全检测器()
    认证检测器.运行所有检测()

    # 2. OAuth2.0安全审计
    oauth审计器 = OAuth2安全审计器()
    oauth审计器.运行所有审计()

    # 3. SAML安全检测
    saml检测器 = SAML安全检测器()
    saml检测器.运行所有检测()

    # 4. 零信任架构实现
    零信任演示器 = 零信任架构演示()
    零信任演示器.运行所有演示()

    # 5. 权限提升检测
    权限检测器 = 权限提升检测器()
    权限检测器.运行所有检测()

    # 6. IAM系统安全
    iam审计器 = IAM系统安全审计器()
    iam审计器.运行所有审计()

    # 总结
    print("\n" + "=" * 80)
    print("身份与访问安全实战案例 - 执行完毕")
    print("=" * 80)
    print("""
学习总结:
  1. 身份认证: 弱密码检测是基础，MFA(FIDO2)是趋势，生物特征需活体检测
  2. OAuth2.0: PKCE+精确redirect_uri+state是核心防护
  3. SAML: XML签名包装是主要威胁，需严格的签名验证
  4. 零信任: "从不信任始终验证"，持续验证+微分段+动态控制
  5. 权限提升: 横向移动检测+权限滥用监控是关键
  6. IAM: 用户生命周期管理+权限回收审计+PAM特权管理

关键学习要点:
  - 身份是新的安全边界(Identity is the new perimeter)
  - 多因素认证是基本要求，FIDO2/WebAuthn是最佳实践
  - 零信任不是产品而是架构理念，需要持续演进
  - 最小权限原则需要通过技术和流程双重保障
  - 特权账户管理(PAM)是减少攻击面的关键
  - 自动化的生命周期管理防止权限累积

进一步学习资源:
  - NIST SP 800-207 (零信任架构)
  - OWASP Authentication Cheat Sheet
  - OAuth 2.0 Security Best Current Practice (RFC 9700)
  - OASIS SAML Security Documentation
  - FIDO2/WebAuthn 规范
""")
    print(f"\n结束时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
