# -*- coding: utf-8 -*-
"""
=============================================================================
CTF夺旗赛实战案例
=============================================================================

安全声明：
    本文件仅用于CTF学习和教育目的。
    所有代码均为教学演示，使用模拟题目数据，不涉及真实系统或网络。
    未经授权对他人系统进行安全测试是违法行为，请务必在获得书面授权后
    进行安全评估工作。作者不对任何滥用本代码的行为负责。

功能概览：
    1. Web方向CTF - SQL注入、XSS、文件上传、反序列化、SSRF、模板注入
    2. PWN与逆向方向 - 栈溢出、格式化字符串、逆向分析、壳与加密
    3. 密码学方向 - 古典密码、现代密码、哈希分析、编码解码
    4. Misc方向 - 隐写术、流量分析、取证分析、杂项技巧
    5. CTF解题工具集 - 常用脚本、自动化工具有、Flag格式验证
    6. CTF比赛策略 - 解题思路、团队协作、时间管理

作者：CTF夺旗赛实战学习工具
版本：1.0.0
日期：2024-01-01
=============================================================================
"""

import os
import re
import sys
import json
import hashlib
import base64
import binascii
import struct
import string
import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from collections import defaultdict, Counter
from itertools import product


# ============================================================================
#  模拟题目数据区
# ============================================================================

# Web题目数据
模拟Web题目 = [
    {
        "题目名称": "Easy Login",
        "分值": 50,
        "分类": "Web",
        "描述": "一个简单的登录页面，看看能不能绕过？",
        "提示": ["SQL注入基础题", "试试经典的永真式"],
        "考点": "SQL注入 - 登录绕过",
    },
    {
        "题目名称": "Secret Note",
        "分值": 100,
        "分类": "Web",
        "描述": "管理员把flag存在私密笔记里了，你能读到吗？",
        "提示": ["IDOR漏洞", "注意查看请求中的用户ID"],
        "考点": "越权访问 (IDOR)",
    },
    {
        "题目名称": "Magic Upload",
        "分值": 150,
        "分类": "Web",
        "描述": "文件上传点，但似乎有过滤...",
        "提示": ["检查Content-Type验证", "试试图片马"],
        "考点": "文件上传绕过",
    },
    {
        "题目名称": "Unserialize Me",
        "分值": 200,
        "分类": "Web",
        "描述": "PHP反序列化，找到pop链了吗？",
        "提示": ["查看源码中的魔术方法", "__destruct / __wakeup"],
        "考点": "PHP反序列化漏洞",
    },
    {
        "题目名称": "SSTI Playground",
        "分值": 200,
        "分类": "Web",
        "描述": "一个模板沙盒，能突破吗？",
        "提示": ["Jinja2模板注入", "寻找可利用的类和方法"],
        "考点": "服务端模板注入 (SSTI)",
    },
]

# Crypto题目数据
模拟Crypto题目 = [
    {
        "题目名称": "凯撒的密码",
        "分值": 50,
        "分类": "Crypto",
        "描述": "经典的古典密码，试试所有位移？",
        "密文": "Zkwdpx brx uhdg wklv brx duh juhdw!",
        "提示": ["凯撒密码", "位移量是3"],
        "考点": "古典密码 - 凯撒密码",
    },
    {
        "题目名称": "奇怪的等式",
        "分值": 100,
        "分类": "Crypto",
        "描述": "异或加密，key只有一个字节？",
        "密文": "1b37373331363f78151b7f2b783431333d78397828372d363c78373e783a393b3736",
        "提示": ["单字节XOR", "频率分析"],
        "考点": "单字节异或",
    },
    {
        "题目名称": "Base家族",
        "分值": 75,
        "分类": "Crypto",
        "描述": "一层层的编码，能解出来吗？",
        "密文": "Vm0wd2QyUXlVWGxWV0d4V1YwZDRWMVl3VmxKWGVEQlTlWGRs",
        "提示": ["Base64多次编码", "试试解码5次"],
        "考点": "编码识别与解码",
    },
    {
        "题目名称": "RSA入门",
        "分值": 200,
        "分类": "Crypto",
        "描述": "给你n, e, c，能恢复明文吗？",
        "参数": {"n": 3233, "e": 17, "c": 2790},
        "提示": ["n很小，可以分解", "p=61, q=53"],
        "考点": "RSA基础 - 小n分解",
    },
]

# PWN题目数据
模拟PWN题目 = [
    {
        "题目名称": "ret2text",
        "分值": 100,
        "分类": "PWN",
        "描述": "最简单的栈溢出，直接跳转到后门函数",
        "提示": ["找到后门函数地址", "计算缓冲区到返回地址的偏移"],
        "考点": "栈溢出 - ret2text",
    },
    {
        "题目名称": "printf_me",
        "分值": 150,
        "分类": "PWN",
        "描述": "格式化字符串漏洞，能改什么？",
        "提示": ["%n写入任意地址", "修改GOT表"],
        "考点": "格式化字符串漏洞",
    },
    {
        "题目名称": "shellcode",
        "分值": 200,
        "分类": "PWN",
        "描述": "栈可执行，自己写shellcode吧",
        "提示": ["execve('/bin/sh', 0, 0)", "注意字节大小端"],
        "考点": "Shellcode编写",
    },
]

# Misc题目数据
模拟Misc题目 = [
    {
        "题目名称": "图片里的秘密",
        "分值": 50,
        "分类": "Misc",
        "描述": "一张普通的图片，里面藏了什么？",
        "提示": ["看看文件末尾", "strings 命令了解一下"],
        "考点": "文件隐写 - 尾部追加",
    },
    {
        "题目名称": "流量分析",
        "分值": 150,
        "分类": "Misc",
        "描述": "pcap文件里有flag，找找看",
        "提示": ["关注HTTP流", "flag格式是flag{...}"],
        "考点": "网络流量分析",
    },
    {
        "题目名称": "二维码迷局",
        "分值": 100,
        "分类": "Misc",
        "描述": "损坏的二维码，能修复吗？",
        "提示": ["二维码有三个定位角", "QR码容错机制"],
        "考点": "二维码隐写/修复",
    },
    {
        "题目名称": "键盘密码",
        "分值": 75,
        "分类": "Misc",
        "描述": "这些字母在键盘上是什么形状？",
        "密文": "qazwsxedcrfvtgb",
        "提示": ["看键盘布局", "字母组成的形状"],
        "考点": "键盘密码",
    },
]


# ============================================================================
#  案例1: Web方向CTF解题实战
# ============================================================================

class Web方向解题:
    """
    Web方向CTF解题实战

    功能:
    1. 常见Web漏洞题型与解题思路
    2. SQL注入解题流程
    3. 文件上传绕过总结
    4. 反序列化pop链构造
    5. SSRF利用方式
    """

    def Web题型总结(self):
        """Web方向常见题型"""
        print("\n" + "=" * 60)
        print("Web方向 CTF 常见题型")
        print("=" * 60)

        题型列表 = [
            ("SQL注入", "入门~困难", "登录绕过、UNION注入、盲注、堆叠注入、二次注入",
             "sqlmap, 手工注入技巧"),
            ("XSS", "入门~中等", "反射型、存储型、DOM型、CSP绕过",
             "XSS平台、Cookie窃取、键盘记录"),
            ("文件上传", "入门~中等", "前端绕过、MIME绕过、扩展名绕过、解析漏洞",
             "图片马、.htaccess、00截断"),
            ("文件包含", "中等~困难", "LFI本地包含、RFI远程包含、PHP伪协议",
             "php://filter、php://input、data://"),
            ("反序列化", "中等~困难", "PHP反序列化、Python pickle、Java反序列化",
             "POP链构造、魔术方法利用"),
            ("SSRF", "中等~困难", "服务端请求伪造、内网探测、协议利用",
             "file://、gopher://、dict://"),
            ("模板注入(SSTI)", "中等~困难", "Jinja2、Twig、Velocity模板注入",
             "沙箱逃逸、命令执行"),
            ("条件竞争", "中等", "文件上传竞争、支付逻辑、抽奖系统",
             "并发请求、竞态条件"),
            ("越权访问", "入门~中等", "水平越权、垂直越权、未授权访问",
             "IDOR、权限绕过"),
            ("CSRF", "入门", "跨站请求伪造、点击劫持",
             "诱导管理员、自动提交表单"),
        ]

        print(f"  {'题型':<15} {'难度':<10} {'考点':<30} {'工具/技巧'}")
        print(f"  {'-'*15} {'-'*10} {'-'*30} {'-'*20}")
        for 题型, 难度, 考点, 工具 in 题型列表:
            print(f"  {题型:<15} {难度:<10} {考点:<30} {工具}")

    def SQL注入解题流程(self):
        """SQL注入解题步骤"""
        print("\n" + "=" * 60)
        print("SQL注入解题流程")
        print("=" * 60)

        print("""
  【步骤1: 寻找注入点】
  - GET参数 / POST参数 / Cookie / HTTP头
  - 单引号/双引号测试：加 ' 看是否报错
  - 数字型测试：and 1=1 / and 1=2

  【步骤2: 判断注入类型】
  - 有报错信息 → 报错注入
  - 页面有回显 → UNION注入
  - 页面真假变化 → 布尔盲注
  - 无回显有延迟 → 时间盲注
  - 有堆叠查询 → 堆叠注入

  【步骤3: 获取数据】
  UNION注入流程:
  1. ORDER BY 猜列数
  2. UNION SELECT 1,2,3... 找显示位
  3. 查数据库名 (database())
  4. 查表名 (information_schema.tables)
  5. 查列名 (information_schema.columns)
  6. 脱库 (SELECT 字段 FROM 表)

  盲注流程:
  1. 猜库名长度
  2. 逐字符猜库名 (ASCII二分法)
  3. 猜表数量和表名
  4. 猜列名
  5. 逐行猜数据
        """)

        print("  【常用注入语句】")
        常用语句 = [
            ("数据库版本", "SELECT version()"),
            ("当前数据库", "SELECT database()"),
            ("当前用户", "SELECT user()"),
            ("所有数据库", "SELECT schema_name FROM information_schema.schemata"),
            ("数据库表名", "SELECT table_name FROM information_schema.tables WHERE table_schema=database()"),
            ("表的列名", "SELECT column_name FROM information_schema.columns WHERE table_name='表名'"),
            ("读取文件", "SELECT load_file('/etc/passwd')"),
            ("写入文件", "SELECT '内容' INTO OUTFILE '/tmp/shell.php'"),
        ]
        for 用途, 语句 in 常用语句:
            print(f"    {用途:<15}: {语句}")

    def 文件上传绕过总结(self):
        """文件上传绕过总结"""
        print("\n" + "=" * 60)
        print("文件上传绕过技巧总结")
        print("=" * 60)

        绕过方式 = [
            ("前端验证绕过", "抓包修改文件名/Content-Type", "Burp Suite"),
            ("大小写绕过", "shell.PhP / shell.pHp", "Windows不区分大小写"),
            ("双写绕过", "shell.pphphp → 过滤后 shell.php", "过滤不彻底"),
            ("空格/点绕过", "shell.php. / shell.php ", "Windows特性"),
            ("::$DATA绕过", "shell.php::$DATA", "Windows NTFS流"),
            ("00截断", "shell.php%00.jpg", "PHP<5.3.4"),
            (".htaccess", "上传.htaccess解析jpg为php", "Apache"),
            (".user.ini", "上传.user.ini + 图片马", "PHP CGI/FastCGI"),
            ("解析漏洞", "shell.php.jpg", "Apache/Nginx解析漏洞"),
            ("图片马", "GIF89a + 代码", "文件头检测绕过"),
        ]

        print(f"  {'绕过方式':<18} {'方法':<30} {'条件/工具'}")
        print(f"  {'-'*18} {'-'*30} {'-'*20}")
        for 方式, 方法, 条件 in 绕过方式:
            print(f"  {方式:<18} {方法:<30} {条件}")

    def SSRF利用方式(self):
        """SSRF利用方式"""
        print("\n" + "=" * 60)
        print("SSRF 利用方式")
        print("=" * 60)

        print("""
  【SSRF能做什么】
  1. 探测内网存活主机和端口
  2. 攻击内网服务 (Redis、MySQL、Memcached等)
  3. 读取本地文件 (file://协议)
  4. DoS攻击 (请求大文件)
  5. 云环境元数据获取 (AWS/GCP/Azure)
        """)

        协议利用 = [
            ("http://", "探测内网HTTP服务", "http://127.0.0.1:8080"),
            ("file://", "读取本地文件", "file:///etc/passwd"),
            ("gopher://", "构造任意TCP数据包", "gopher://127.0.0.1:6379/_..."),
            ("dict://", "探测Redis等服务", "dict://127.0.0.1:6379/INFO"),
            ("ftp://", "FTP服务探测", "ftp://127.0.0.1:21"),
            ("tftp://", "UDP服务探测", "tftp://127.0.0.1"),
        ]

        print("  【协议利用】")
        print(f"  {'协议':<12} {'用途':<20} {'示例'}")
        print(f"  {'-'*12} {'-'*20} {'-'*40}")
        for 协议, 用途, 示例 in 协议利用:
            print(f"  {协议:<12} {用途:<20} {示例}")

        print("""
  【云环境元数据】
  AWS: http://169.254.169.254/latest/meta-data/
  GCP: http://metadata.google.internal/computeMetadata/v1/
  Azure: http://169.254.169.254/metadata/instance

  【绕过方式】
  - IP进制转换: 十进制、八进制、十六进制
  - DNS重绑定: 域名解析在内外网间切换
  - 302跳转: 跟随重定向到内网
  - URL解析差异: 不同解析器的解析差异
        """)

    def SSTI模板注入(self):
        """SSTI模板注入"""
        print("\n" + "=" * 60)
        print("SSTI 模板注入")
        print("=" * 60)

        print("""
  【常见模板引擎】
  - Jinja2 (Python) - {{ ... }} {% ... %}
  - Twig (PHP) - {{ ... }} {% ... %}
  - Velocity (Java) - $... #...
  - Freemarker (Java) - ${...}
  - ERB (Ruby) - <%= ... %>
        """)

        print("  【Jinja2 SSTI 利用链】")
        print("""
  1. 确认注入点: {{ 7*7 }} → 49
  2. 获取基类: {{ ''.__class__.__mro__[1] }} → <class 'object'>
  3. 获取子类: {{ ''.__class__.__mro__[1].__subclasses__() }}
  4. 寻找可利用类 (Popen, subprocess, file, os等)
  5. 命令执行: 找到os模块，调用popen

  常用Payload:
  {{ config.items() }}  // 读取配置
  {{ ''.__class__.__bases__[0].__subclasses__()[40]('/etc/passwd').read() }}
  {{ cycler.__init__.__globals__.os.popen('id').read() }}
        """)

    def 运行全部(self):
        self.Web题型总结()
        self.SQL注入解题流程()
        self.文件上传绕过总结()
        self.SSRF利用方式()
        self.SSTI模板注入()


# ============================================================================
#  案例2: PWN与逆向方向实战
# ============================================================================

class PWN逆向解题:
    """
    PWN与逆向方向CTF实战

    功能:
    1. PWN常见题型
    2. 栈溢出利用链
    3. 格式化字符串漏洞
    4. 逆向分析技巧
    """

    def PWN题型总结(self):
        """PWN常见题型"""
        print("\n" + "=" * 60)
        print("PWN 常见题型总结")
        print("=" * 60)

        题型列表 = [
            ("栈溢出", "入门", "ret2text, ret2shellcode, ret2syscall, ret2libc",
             "缓冲区溢出覆盖返回地址"),
            ("格式化字符串", "入门~中等", "%x泄露, %n写入, GOT表覆盖",
             "printf类函数未控制格式字符串"),
            ("堆利用", "中等~困难", "UAF, Double Free, House of ...",
             "堆管理机制漏洞利用"),
            ("整数溢出", "中等", "有符号/无符号转换、整数溢出",
             "计算错误导致缓冲区溢出"),
            ("条件竞争", "中等", "TOCTOU竞态条件",
             "时间差导致的安全问题"),
            ("内核pwn", "困难", "内核驱动漏洞利用",
             "提权到ring 0"),
        ]

        print(f"  {'题型':<15} {'难度':<8} {'利用方式':<30} {'原理'}")
        print(f"  {'-'*15} {'-'*8} {'-'*30} {'-'*25}")
        for 题型, 难度, 利用, 原理 in 题型列表:
            print(f"  {题型:<15} {难度:<8} {利用:<30} {原理}")

    def 栈溢出利用链(self):
        """栈溢出利用链演进"""
        print("\n" + "=" * 60)
        print("栈溢出利用链演进")
        print("=" * 60)

        利用链 = [
            ("ret2text", "无任何保护",
             "直接跳转到程序中已有的后门函数",
             "payload = padding + p32(backdoor_addr)"),
            ("ret2shellcode", "NX disabled / 栈可执行",
             "在缓冲区中放置shellcode，跳过去执行",
             "payload = shellcode + padding + p32(buf_addr)"),
            ("ret2syscall", "有NX，无ASLR或有gadget",
             "控制寄存器，执行系统调用 (int 0x80 / syscall)",
             "payload = padding + pop eax + int 0x80 + ..."),
            ("ret2libc", "有NX，有ASLR",
             "泄露libc基址，调用system('/bin/sh')",
             "payload = padding + p32(plt_puts) + p32(main) + p32(got_puts)"),
            ("ROP", "有NX，有ASLR",
             "用gadget拼出任意代码执行效果",
             "payload = padding + rop_chain"),
            ("stack pivoting", "栈空间不足",
             "控制esp到可控区域，执行更长的ROP",
             "payload = leave_ret + new_stack_addr"),
        ]

        for i, (名称, 条件, 原理, payload) in enumerate(利用链, 1):
            print(f"\n  {i}. {名称}")
            print(f"     条件: {条件}")
            print(f"     原理: {原理}")
            print(f"     示例: {payload}")

        print("""
  【保护机制】
  - NX/DEP: 栈不可执行 → 需要ret2libc/ROP
  - ASLR: 地址随机化 → 需要泄露地址
  - Stack Canary: 栈保护 → 需要泄露canary
  - PIE: 程序基址随机化 → 需要泄露程序基址
  - RELRO: GOT表只读 → 不能覆盖GOT
        """)

    def 格式化字符串漏洞(self):
        """格式化字符串漏洞"""
        print("\n" + "=" * 60)
        print("格式化字符串漏洞")
        print("=" * 60)

        print("""
  【原理】
  printf/scanf等函数的格式字符串参数可控，
  可以读取/写入任意地址的内存。

  【格式符】
  %x / %p  - 读取栈上数据（16进制/指针）
  %s      - 读取字符串（将参数当作指针）
  %n      - 将已输出字符数写入对应地址
  %hn     - 写入2字节
  %hhn    - 写入1字节
  %$n     - 指定第n个参数
        """)

        print("  【利用步骤】")
        print("""
  1. 确定偏移: AAAA.%x.%x.%x... 找到AAAA在第几个位置
  2. 任意地址读: addr%偏移$s → 读取addr地址的内容
  3. 任意地址写: addr%numc%偏移$n → 写入num到addr
  4. GOT表覆盖: 把printf的GOT改成system的地址
  5. 下次调用printf时实际执行system
        """)

        print("  【常见用途】")
        print("    • 泄露栈地址 / canary / libc地址")
        print("    • 覆盖GOT表 (printf → system)")
        print("    • 修改关键变量的值")
        print("    • 配合其他漏洞扩大战果")

    def 逆向分析技巧(self):
        """逆向分析技巧"""
        print("\n" + "=" * 60)
        print("逆向分析技巧")
        print("=" * 60)

        print("""
  【常用工具】
  静态分析: IDA Pro, Ghidra, Binary Ninja, radare2
  动态调试: gdb, x64dbg, OllyDbg, WinDbg
  辅助工具: strings, file, binwalk, upx, die
        """)

        print("  【解题步骤】")
        print("""
  1. 信息收集
     - file: 查看文件类型、架构、位数
     - strings: 查找字符串（flag、提示、错误信息）
     - checksec: 查看保护机制

  2. 静态分析
     - 找到main函数，理清程序逻辑
     - 关注关键函数: 输入处理、加密、验证
     - 识别算法: 常见加密/编码/混淆

  3. 动态调试
     - 下断点，观察关键变量
     - 跟踪输入数据的流向
     - 理解加密/验证逻辑

  4. 编写exp
     - 找到漏洞点
     - 构造利用payload
     - 本地调试通过
     - 远程打靶拿flag
        """)

        print("  【常见算法识别】")
        算法特征 = [
            ("Base64", "有ABCDEFG...的表，3字节变4字节"),
            ("AES", "S盒、轮密钥、固定块大小"),
            ("RC4", "256字节的S盒初始化"),
            ("MD5/SHA", "固定的初始常量、四轮循环"),
            ("TEA/XTEA", "32轮、delta常量0x9E3779B9"),
            ("凯撒密码", "简单字符位移"),
            ("异或加密", "与key逐位异或"),
        ]
        for 算法, 特征 in 算法特征:
            print(f"    {算法:<12} {特征}")

    def 运行全部(self):
        self.PWN题型总结()
        self.栈溢出利用链()
        self.格式化字符串漏洞()
        self.逆向分析技巧()


# ============================================================================
#  案例3: 密码学方向实战
# ============================================================================

class 密码学解题:
    """
    密码学方向CTF实战

    功能:
    1. 古典密码解析
    2. 编码识别与转换
    3. 现代密码攻击
    4. 哈希分析
    """

    def 古典密码大全(self):
        """古典密码类型与解法"""
        print("\n" + "=" * 60)
        print("古典密码类型与解法")
        print("=" * 60)

        古典密码列表 = [
            ("凯撒密码", "字母位移固定位数", "位移3位",
             "爆破所有25种位移", "ROT13是特殊的凯撒(位移13)"),
            ("维吉尼亚密码", "使用密钥词，每位位移不同", "密钥: KEY",
             "Kasiski测试 / 弗里德曼测试找密钥长度", "多表替换密码"),
            ("栅栏密码", "按Z字形写，按行读取", "2栏/3栏",
             "尝试不同栏数", "又称Rail Fence"),
            ("摩斯密码", "点和划表示字母", ".... . .-.. .-.. ---",
             "在线摩斯解码器", "有/无线索电码、数字等变体"),
            ("培根密码", "A/B两种字符表示字母", "AABBB ABABA...",
             "5位一组替换字母", "有24字母和26字母版本"),
            ("猪圈密码", "符号表示字母", "特殊图形符号",
             "猪圈密码对照表", "又称共济会密码"),
            ("键盘密码", "键盘位置坐标/形状", "qazwsx",
             "观察键盘布局找规律", "常见的有坐标、形状等"),
            ("手机键盘密码", "老式手机键盘", "22 33",
             "按数字和次数对应字母", "2=ABC, 3=DEF..."),
            ("Atbash", "字母倒序映射 (A↔Z, B↔Y...)", "ZYXWVU...",
             "对称加密，加密解密一样", "希伯来文起源"),
            ("希尔密码", "矩阵乘法加密", "2x2/3x3矩阵",
             "已知明文攻击求逆矩阵", "线性代数基础"),
        ]

        print(f"  {'密码名称':<15} {'原理':<20} {'示例':<20} {'解法'}")
        print(f"  {'-'*15} {'-'*20} {'-'*20} {'-'*25}")
        for 名称, 原理, 示例, 解法 in 古典密码列表:
            print(f"  {名称:<15} {原理:<20} {示例:<20} {解法}")

    def 编码识别大全(self):
        """常见编码识别"""
        print("\n" + "=" * 60)
        print("常见编码识别与转换")
        print("=" * 60)

        编码列表 = [
            ("Base64", "大小写+数字+/=结尾", "aGVsbG8=", "长度是4的倍数"),
            ("Base32", "大写字母+数字2-7=结尾", "NBSWY3DP", "全大写，字符少"),
            ("Base16/Hex", "0-9 A-F", "68656C6C6F", "纯十六进制字符"),
            ("URL编码", "%XX格式", "hello%20world", "%号开头"),
            ("Unicode", "\\uXXXX或&#XXXX;", "\\u4f60\\u597d", "中文常用"),
            ("HTML实体", "&name;或&#num;", "&lt;&gt;&amp;", "HTML中常见"),
            ("摩斯密码", ".和-", ".... . .-.. .-.. ---", "点划分隔"),
            ("Brainfuck", "8种符号 > < + - . , [ ]", "++++++++[>++++++<-]>.", "混淆编程语言"),
            ("JJEncode", "$和_等符号", "$_=(_=$+\"\")[...]", "JS混淆"),
            ("AAEncode", "颜文字", "(^_^)  (￣▽￣)", "JS混淆"),
            ("猪圈密码", "特殊符号", "□ △ ○ 等", "图形符号"),
            ("当铺密码", "汉字笔画", "由 中 人 大...", "当铺用的数字密码"),
        ]

        print(f"  {'编码类型':<15} {'特征':<25} {'示例':<30} 备注")
        print(f"  {'-'*15} {'-'*25} {'-'*30} {'-'*15}")
        for 类型, 特征, 示例 in 编码列表:
            print(f"  {类型:<15} {特征:<25} {示例:<30}")

    def 凯撒密码解密器(self, 密文=""):
        """凯撒密码爆破"""
        print("\n" + "=" * 60)
        print("凯撒密码爆破工具")
        print("=" * 60)

        if not 密文:
            密文 = "Zkwdpx brx uhdg wklv brx duh juhdw!"

        print(f"\n  密文: {密文}")
        print(f"  尝试所有25种位移...\n")

        for 位移 in range(1, 26):
            明文 = ""
            for c in 密文:
                if c.isalpha():
                    基准 = ord('A') if c.isupper() else ord('a')
                    明文 += chr((ord(c) - 基准 - 位移) % 26 + 基准)
                else:
                    明文 += c
            标记 = " ← flag?" if "flag" in 明文.lower() or "ctf" in 明文.lower() else ""
            print(f"  ROT{位移:2d}: {明文}{标记}")

    def 单字节异或破解(self, 密文十六进制=""):
        """单字节XOR破解"""
        print("\n" + "=" * 60)
        print("单字节 XOR 破解")
        print("=" * 60)

        if not 密文十六进制:
            密文十六进制 = "1b37373331363f78151b7f2b783431333d78397828372d363c78373e783a393b3736"

        print(f"\n  密文(hex): {密文十六进制}")
        print(f"  尝试所有256个密钥...\n")

        try:
            密文字节 = bytes.fromhex(密文十六进制)
        except:
            print("  密文格式错误，请输入有效的十六进制字符串")
            return

        # 英文字符频率评分
        英文字符频率 = {
            'e': 12.7, 't': 9.1, 'a': 8.2, 'o': 7.5, 'i': 7.0,
            'n': 6.7, 's': 6.3, 'h': 6.1, 'r': 6.0, 'd': 4.3,
            'l': 4.0, 'c': 2.8, 'u': 2.8, 'm': 2.4, 'w': 2.4,
            ' ': 13.0
        }

        def 评分(文本):
            分数 = 0
            for b in 文本.lower():
                char = chr(b) if isinstance(b, int) else b
                分数 += 英文字符频率.get(char, 0)
            return 分数

        结果列表 = []
        for key in range(256):
            明文字节 = bytes([b ^ key for b in 密文字节])
            try:
                明文 = 明文字节.decode('ascii')
                分数值 = 评分(明文)
                结果列表.append((分数值, key, 明文))
            except:
                pass

        # 按分数排序，取前5
        结果列表.sort(reverse=True)
        print(f"  {'Key(hex)':<10} {'Key(dec)':<8} {'分数':<8} 明文")
        print(f"  {'-'*10} {'-'*8} {'-'*8} {'-'*40}")

        for 分数值, key, 明文 in 结果列表[:5]:
            显示 = 明文.replace('\n', ' ')[:50]
            print(f"  0x{key:02x}      {key:<8} {分数值:<8.1f} {显示}")

    def 现代密码攻击(self):
        """现代密码常见考点"""
        print("\n" + "=" * 60)
        print("现代密码 CTF 常见考点")
        print("=" * 60)

        RSA考点 = [
            ("小n分解", "n太小，可以直接分解为p和q", "yafu / factordb"),
            ("共模攻击", "同一n，不同e加密同一明文", "扩展欧几里得求m"),
            ("低加密指数", "e很小(e=3)，密文也小", "直接开e次方"),
            ("Wiener攻击", "e很大，d很小", "连分数分解求d"),
            ("Boneh-Durfee", "d < n^0.292", "格基规约"),
            ("p-q很近", "p和q相差不大", "Fermat分解"),
            ("p+q光滑", "p-1或q-1只有小因子", "Pollard's p-1算法"),
            ("随机数预测", "生成素数的PRNG可预测", "恢复随机数生成器状态"),
        ]

        print("  【RSA 常见攻击】")
        print(f"  {'攻击类型':<15} {'条件':<25} {'工具/方法'}")
        print(f"  {'-'*15} {'-'*25} {'-'*25}")
        for 类型, 条件, 方法 in RSA考点:
            print(f"  {类型:<15} {条件:<25} {方法}")

        对称密码考点 = [
            ("ECB模式", "相同明文块产生相同密文块", "字节翻转攻击"),
            ("CBC模式", "IV可控/密文可控", "Padding Oracle攻击"),
            ("CTR模式", "Nonce复用", "流密码重用攻击"),
            ("弱密钥", "密钥空间太小", "暴力破解"),
            ("已知明文", "知道部分明文", "恢复密钥/明文"),
        ]

        print("\n  【对称密码常见攻击】")
        print(f"  {'攻击类型':<15} {'条件':<25} {'攻击方式'}")
        print(f"  {'-'*15} {'-'*25} {'-'*25}")
        for 类型, 条件, 方法 in 对称密码考点:
            print(f"  {类型:<15} {条件:<25} {方法}")

    def 运行全部(self):
        self.古典密码大全()
        self.编码识别大全()
        self.凯撒密码解密器()
        self.单字节异或破解()
        self.现代密码攻击()


# ============================================================================
#  案例4: Misc方向实战
# ============================================================================

class Misc方向解题:
    """
    Misc方向CTF实战

    功能:
    1. 隐写术总结
    2. 流量分析
    3. 取证分析
    4. 杂项技巧
    """

    def 隐写术总结(self):
        """隐写术常见类型"""
        print("\n" + "=" * 60)
        print("隐写术 (Steganography) 总结")
        print("=" * 60)

        图片隐写 = [
            ("尾部追加", "文件末尾附加数据", "strings / binwalk / 010Editor", "简单"),
            ("LSB隐写", "最低有效位隐藏信息", "zsteg / stegsolve / Stegsolve", "中等"),
            ("调色板隐写", "调色板颜色中隐藏", "stegsolve 查看各通道", "中等"),
            ("盲水印", "不可见水印", "盲水印工具", "困难"),
            ("F5隐写", "JPEG DCT系数修改", "F5-steganography", "困难"),
            ("JPHide", "JPEG图片隐写", "jpseek/jphide", "中等"),
            ("Steghide", "需要密码的隐写", "steghide extract -sf img.jpg", "中等"),
        ]

        print("  【图片隐写】")
        print(f"  {'类型':<15} {'原理':<25} {'检测/提取工具':<30} {'难度'}")
        print(f"  {'-'*15} {'-'*25} {'-'*30} {'-'*6}")
        for 类型, 原理, 工具, 难度 in 图片隐写:
            print(f"  {类型:<15} {原理:<25} {工具:<30} {难度}")

        其他隐写 = [
            ("音频隐写", "音频LSB、频谱隐藏", "Audacity / Sonic Visualiser", "MP3/WAV格式"),
            ("视频隐写", "视频帧中隐藏", "ffmpeg / 逐帧分析", "容量大"),
            ("文本隐写", "空格/换行/字体大小", "零宽字符/Unicode隐写", "肉眼不可见"),
            ("ZIP隐写", "ZIP文件中藏文件", "binwalk / foremost", "压缩包嵌套"),
            ("文件合并", "图片+压缩包", "copy /b image.jpg+file.rar", "图片改zip"),
        ]

        print("\n  【其他隐写】")
        print(f"  {'类型':<12} {'原理':<20} {'工具':<30} 备注")
        print(f"  {'-'*12} {'-'*20} {'-'*30} {'-'*15}")
        for 类型, 原理, 工具, 备注 in 其他隐写:
            print(f"  {类型:<12} {原理:<20} {工具:<30} {备注}")

    def 流量分析技巧(self):
        """流量分析技巧"""
        print("\n" + "=" * 60)
        print("流量分析 (pcap) 技巧")
        print("=" * 60)

        print("""
  【常用工具】
  - Wireshark: 图形化流量分析
  - tshark: 命令行版Wireshark
  - tcpdump: 抓包工具
  - NetworkMiner: 自动提取文件
  - foremost/binwalk: 提取pcap中的文件
        """)

        print("  【解题步骤】")
        print("""
  1. 快速浏览
     - 统计协议分布 (Statistics → Protocol Hierarchy)
     - 查看端点和会话 (Statistics → Conversations)
     - 追踪HTTP流 (Follow → HTTP Stream)

  2. 关键词搜索
     - 搜索 "flag" / "CTF" / "key" / "password"
     - 搜索特定格式: flag{xxx}, CTF{xxx}
     - 搜索文件头: PNG(89504E47), ZIP(504B0304)

  3. 常见考点
     - HTTP: 上传/下载的文件、Cookie、POST数据
     - DNS: TXT记录中的隐藏数据
     - FTP: 传输的文件内容
     - USB: USB流量还原键盘输入/鼠标
     - ICMP: 数据部分隐藏信息
     - TLS: 导出密钥后解密流量
        """)

        print("  【Wireshark 常用过滤表达式】")
        过滤器 = [
            ("http", "只看HTTP流量"),
            ("http.request.method == POST", "HTTP POST请求"),
            ("dns", "DNS流量"),
            ("tcp.port == 8080", "特定端口TCP流量"),
            ("ip.addr == 192.168.1.1", "特定IP"),
            ('frame contains "flag"', "包含flag的数据包"),
            ("ftp-data", "FTP数据传输"),
            ("usb", "USB流量"),
        ]
        for 过滤, 说明 in 过滤器:
            print(f"    {过滤:<40} // {说明}")

    def 取证分析技巧(self):
        """取证分析技巧"""
        print("\n" + "=" * 60)
        print("取证分析技巧")
        print("=" * 60)

        取证类型 = [
            ("内存取证", "内存镜像分析", "volatility / volatility3",
             ["进程列表", "网络连接", "提取密码", "恶意软件分析"]),
            ("磁盘取证", "磁盘镜像分析", "FTK Imager / Autopsy",
             ["文件恢复", "浏览历史", "回收站", "注册表分析"]),
            ("日志分析", "系统/应用日志", "grep / awk / python脚本",
             ["登录记录", "操作记录", "攻击溯源", "时间线分析"]),
        ]

        for 类型, 描述, 工具, 考点 in 取证类型:
            print(f"\n  【{类型}】")
            print(f"    描述: {描述}")
            print(f"    工具: {工具}")
            print(f"    常见考点:")
            for k in 考点:
                print(f"      • {k}")

        print("""
  【Volatility 常用命令】
    python vol.py -f mem.raw imageinfo            // 获取系统信息
    python vol.py -f mem.raw --profile=Win7SP1x64 pslist  // 进程列表
    python vol.py -f mem.raw --profile=Win7SP1x64 netscan // 网络连接
    python vol.py -f mem.raw --profile=Win7SP1x64 hashdump // 密码哈希
    python vol.py -f mem.raw --profile=Win7SP1x64 cmdline  // 命令行参数
    python vol.py -f mem.raw --profile=Win7SP1x64 filescan // 文件列表
    python vol.py -f mem.raw --profile=Win7SP1x64 dumpfiles -D output // 提取文件
        """)

    def 杂项技巧(self):
        """杂项技巧"""
        print("\n" + "=" * 60)
        print("Misc 杂项技巧")
        print("=" * 60)

        杂项列表 = [
            ("二维码", "扫描二维码获取信息", "QRazyBox / CQR / 在线工具",
             "注意修复损坏的二维码"),
            ("表情包", "表情包中藏flag", "stegsolve / 010Editor",
             "注意图片尾部、多帧GIF"),
            ("乐谱密码", "音符对应字母", "在线乐谱分析",
             "A-G对应音符，还有其他变体"),
            ("盲文", "六点表示字母", "盲文对照表",
             "常见的有六点盲文"),
            ("手语/旗语", "手势/旗子表示字母", "手语旗语对照表",
             "图片题中常见"),
            ("数独/字谜", "逻辑游戏题", "求解器",
             "解出后提取flag"),
            ("压缩包爆破", "加密ZIP/RAR", "ARCHPR / fcrackzip",
             "弱密码、掩码爆破"),
            ("CRC碰撞", "CRC32碰撞", "crc32碰撞脚本",
             "短文本通过CRC32反推"),
        ]

        print(f"  {'类型':<15} {'描述':<20} {'工具/方法':<25} 备注")
        print(f"  {'-'*15} {'-'*20} {'-'*25} {'-'*20}")
        for 类型, 描述, 工具, 备注 in 杂项列表:
            print(f"  {类型:<15} {描述:<20} {工具:<25} {备注}")

    def 运行全部(self):
        self.隐写术总结()
        self.流量分析技巧()
        self.取证分析技巧()
        self.杂项技巧()


# ============================================================================
#  案例5: CTF解题工具集
# ============================================================================

class CTF工具集:
    """
    CTF常用工具集合

    功能:
    1. 编码转换工具
    2. 哈希检测
    3. Flag格式验证
    4. 常用转换脚本
    """

    def 编码转换工具(self):
        """各种编码转换"""
        print("\n" + "=" * 60)
        print("编码转换工具")
        print("=" * 60)

        测试文本 = "flag{w3lc0m3_t0_ctf_w0rld}"
        print(f"\n  原始文本: {测试文本}")
        print()

        # Base64
        b64 = base64.b64encode(测试文本.encode()).decode()
        print(f"  Base64 编码: {b64}")
        print(f"  Base64 解码: {base64.b64decode(b64).decode()}")

        # Base32
        b32 = base64.b32encode(测试文本.encode()).decode()
        print(f"  Base32 编码: {b32}")

        # Hex
        hex_str = 测试文本.encode().hex()
        print(f"  Hex 编码:    {hex_str}")

        # URL编码
        url_encoded = urllib.parse.quote(测试文本)
        print(f"  URL 编码:    {url_encoded}")

        # 二进制
        binary = ' '.join(format(ord(c), '08b') for c in 测试文本[:10])
        print(f"  二进制(前10): {binary}...")

        # 摩斯密码
        摩斯码表 = {
            'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
            'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
            'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
            'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
            'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
            'Z': '--..', '0': '-----', '1': '.----', '2': '..---',
            '3': '...--', '4': '....-', '5': '.....', '6': '-....',
            '7': '--...', '8': '---..', '9': '----.',
        }
        摩斯 = ' '.join(摩斯码表.get(c.upper(), c) for c in 测试文本[:10].upper() if c.isalnum())
        print(f"  摩斯密码(前10字母): {摩斯}...")

    def 哈希类型检测(self):
        """哈希类型检测"""
        print("\n" + "=" * 60)
        print("哈希类型检测")
        print("=" * 60)

        示例哈希 = [
            ("5f4dcc3b5aa765d61d8327deb882cf99", "32位hex → MD5"),
            ("5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8", "40位hex → SHA-1"),
            ("5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8", "64位hex → SHA-256"),
            ("$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewYGyJkeUeMGFfJi", "bcrypt ($2b$)"),
            ("$6$rounds=5000$salt$...", "SHA-512 crypt ($6$)"),
            ("{SHA}W6ph5Mm5Pz8GgiULbPgzG37mj9g=", "{SHA}前缀 → SHA-1 Base64"),
        ]

        print(f"\n  {'哈希值(前30位)':<32} {'类型判断'}")
        print(f"  {'-'*32} {'-'*30}")
        for 哈希值, 类型 in 示例哈希:
            print(f"  {哈希值[:32]:<32} {类型}")

        print("""
  【常见哈希格式】
  MD5       : 32 hex chars
  SHA-1     : 40 hex chars
  SHA-256   : 64 hex chars
  SHA-512   : 128 hex chars
  bcrypt    : $2a$ / $2b$ / $2y$ 开头
  NTLM      : 32 hex (类似MD5，但是NTLM)
  MySQL     : * 开头 + 40 hex
  Wordpress : $P$ / $H$ 开头 (phpass)
        """)

    def Flag格式验证(self):
        """Flag格式验证"""
        print("\n" + "=" * 60)
        print("Flag 格式验证")
        print("=" * 60)

        常见格式 = [
            ("flag{...}", "最常见格式"),
            ("CTF{...}", "CTF前缀"),
            ("picoCTF{...}", "PicoCTF比赛"),
            ("HTB{...}", "Hack The Box"),
            ("THM{...}", "TryHackMe"),
            ("FLAG{...}", "全大写"),
            ("hkcert24{...}", "比赛名+年份"),
        ]

        print("\n  常见Flag格式:")
        for 格式, 说明 in 常见格式:
            print(f"    {格式:<25} {说明}")

        # 验证示例
        测试Flag = [
            "flag{th1s_1s_4_t3st_fl4g}",
            "CTF{w3ll_d0ne_y0u_g0t_1t}",
            "not_a_flag",
            "flag{invalid_char?}",
        ]

        print("\n  Flag验证测试:")
        for flag in 测试Flag:
            # 基本格式检查
            有效 = bool(re.match(r'^[A-Za-z0-9_-]*\{[A-Za-z0-9_!@#$%^&*()\-+=,.?/:;]+\}$', flag))
            状态 = "✓ 格式正确" if 有效 else "✗ 格式可疑"
            print(f"    {flag:<40} {状态}")

    def 运行全部(self):
        self.编码转换工具()
        self.哈希类型检测()
        self.Flag格式验证()


# ============================================================================
#  案例6: CTF比赛策略与模拟
# ============================================================================

class CTF比赛策略:
    """
    CTF比赛策略

    功能:
    1. 解题思路与方法
    2. 团队协作
    3. 时间管理
    4. 模拟比赛环境
    """

    def 解题思路方法(self):
        """CTF通用解题思路"""
        print("\n" + "=" * 60)
        print("CTF 解题思路与方法")
        print("=" * 60)

        print("""
  【通用解题步骤】
  1. 信息收集
     - 仔细读题，理解题目描述
     - 查看附件，分析文件类型
     - 收集所有线索（题目名、提示、分值）

  2. 初步分析
     - Web: 先访问网站，查看源码，找参数
     - Pwn: checksec + file + 运行看看
     - Crypto: 分析加密算法，找弱点
     - Misc: strings + binwalk + file 三件套

  3. 确定方向
     - 根据考点选择工具和方法
     - 从简单的尝试开始
     - 记录所有尝试和结果

  4. 深入利用
     - 找到漏洞点
     - 构造payload
     - 本地测试
     - 远程打靶

  5. 拿flag验证
     - 提交flag
     - 记录解题过程（写writeup）
        """)

        print("  【卡题时怎么办】")
        print("""
    1. 重新读题，有没有漏掉的信息？
    2. 回到最基础的步骤检查
    3. 换个角度思考（有没有其他考点？）
    4. 看看其他题目，换换思路
    5. 和队友讨论
    6. 搜索相关知识点
    7. 休息一下，大脑后台处理
        """)

    def 团队协作建议(self):
        """团队协作建议"""
        print("\n" + "=" * 60)
        print("CTF 团队协作建议")
        print("=" * 60)

        print("""
  【团队分工建议（3人队）】
  队员A (Web手): 主攻Web、Misc
  队员B (Pwn手): 主攻Pwn、Reverse
  队员C (Crypto手): 主攻Crypto、Misc、杂项

  【协作工具】
  - 即时通讯: Discord / Slack / 飞书
  - 共享文档: Notion / 飞书文档 / Google Docs
  - 代码共享: GitHub Gist / Pastebin
  - 共享终端: tmate / tmux共享

  【协作原则】
  1. 并行解题，不要挤在同一道题
  2. 进展及时同步
  3. 有思路及时分享
  4. 卡题及时换人
  5. 最后半小时集中攻难题
        """)

    def 模拟比赛环境(self):
        """模拟CTF比赛环境"""
        print("\n" + "=" * 60)
        print("模拟 CTF 比赛")
        print("=" * 60)

        所有题目 = 模拟Web题目 + 模拟Crypto题目 + 模拟PWN题目 + 模拟Misc题目
        总分值 = sum(t["分值"] for t in 所有题目)

        print(f"\n  比赛名称: 模拟CTF练习赛")
        print(f"  题目总数: {len(所有题目)} 道")
        print(f"  总分值: {总分值} 分")
        print(f"  比赛时长: 48小时")
        print(f"  开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  结束时间: {(datetime.now() + timedelta(hours=48)).strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # 按分类统计
        分类统计 = defaultdict(lambda: {"数量": 0, "分值": 0})
        for t in 所有题目:
            分类统计[t["分类"]]["数量"] += 1
            分类统计[t["分类"]]["分值"] += t["分值"]

        print("  【题目分布】")
        print(f"  {'分类':<10} {'数量':<8} {'分值':<8}")
        print(f"  {'-'*10} {'-'*8} {'-'*8}")
        for 分类, 数据 in 分类统计.items():
            print(f"  {分类:<10} {数据['数量']:<8} {数据['分值']:<8}")

        print("\n  【题目列表】")
        print(f"  {'#':<4} {'题目名称':<25} {'分类':<10} {'分值':<6} 考点")
        print(f"  {'-'*4} {'-'*25} {'-'*10} {'-'*6} {'-'*30}")
        for i, t in enumerate(所有题目, 1):
            print(f"  {i:<4} {t['题目名称']:<25} {t['分类']:<10} {t['分值']:<6} {t['考点']}")

        print("""
  【建议解题顺序】
  1. 先做所有50分的入门题（热身）
  2. 再做100分的基础题
  3. 然后各方向挑自己擅长的做
  4. 最后攻坚高分难题

  祝你好运，玩得开心！ 🚩
        """)

    def 运行全部(self):
        self.解题思路方法()
        self.团队协作建议()
        self.模拟比赛环境()


# ============================================================================
#  主函数
# ============================================================================

def main():
    print("\n" + "=" * 70)
    print("CTF夺旗赛实战案例集")
    print("=" * 70)
    print("""
请选择要运行的实战案例:

  1. Web方向CTF解题实战
  2. PWN与逆向方向实战
  3. 密码学方向实战
  4. Misc方向实战
  5. CTF解题工具集
  6. CTF比赛策略与模拟
  7. 运行全部案例
  0. 退出
""")

    while True:
        try:
            choice = input("\n请输入选项 (0-7): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！祝你比赛顺利！🚩")
            break

        if choice == "0":
            print("再见！祝你比赛顺利！🚩")
            break
        elif choice == "1":
            web = Web方向解题()
            web.运行全部()
        elif choice == "2":
            pwn = PWN逆向解题()
            pwn.运行全部()
        elif choice == "3":
            crypto = 密码学解题()
            crypto.运行全部()
        elif choice == "4":
            misc = Misc方向解题()
            misc.运行全部()
        elif choice == "5":
            tools = CTF工具集()
            tools.运行全部()
        elif choice == "6":
            strategy = CTF比赛策略()
            strategy.运行全部()
        elif choice == "7":
            print("\n" + "=" * 70)
            print("正在运行全部实战案例...")
            print("=" * 70)

            web = Web方向解题()
            web.运行全部()

            pwn = PWN逆向解题()
            pwn.运行全部()

            crypto = 密码学解题()
            crypto.运行全部()

            misc = Misc方向解题()
            misc.运行全部()

            tools = CTF工具集()
            tools.运行全部()

            strategy = CTF比赛策略()
            strategy.运行全部()

            print("\n" + "=" * 70)
            print("所有案例运行完成！祝你CTF比赛取得好成绩！🚩")
            print("=" * 70)
        else:
            print("无效选项，请重新输入 (0-7)")

        print("\n" + "-" * 70)


if __name__ == "__main__":
    import urllib.parse
    main()
