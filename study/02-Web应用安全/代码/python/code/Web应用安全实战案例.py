# -*- coding: utf-8 -*-
"""
=============================================================================
Web应用安全实战案例
=============================================================================

安全声明：
    本文件仅用于授权安全测试和教育目的。
    所有代码均为教学演示，使用模拟数据，不涉及真实网站或系统。
    未经授权对他人网站进行安全测试是违法行为，请务必在获得书面授权后
    进行安全评估工作。作者不对任何滥用本代码的行为负责。

功能概览：
    1. SQL注入攻击与防御 - UNION注入、布尔盲注、时间盲注原理与防御
    2. XSS跨站脚本攻击 - 反射型、存储型、DOM型XSS原理与防御
    3. CSRF跨站请求伪造 - 攻击原理、检测方法、防御措施
    4. 文件上传漏洞 - 绕过技巧、webshell原理、安全上传配置
    5. 命令注入攻击 - 命令拼接、绕过过滤、安全编码实践
    6. Web安全扫描器 - 综合漏洞检测工具

作者：Web应用安全学习工具
版本：1.0.0
日期：2024-01-01
=============================================================================
"""

import os
import re
import json
import hashlib
import base64
import urllib.parse
import random
import string
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from collections import defaultdict


# ============================================================================
#  模拟数据定义区
# ============================================================================

# 模拟HTTP请求日志
模拟HTTP请求日志 = [
    {
        "方法": "GET",
        "URL": "/news.php?id=1",
        "参数": {"id": "1"},
        "响应码": 200,
        "响应长度": 5120,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    },
    {
        "方法": "GET",
        "URL": "/search?q=test",
        "参数": {"q": "test"},
        "响应码": 200,
        "响应长度": 3072,
        "User-Agent": "Mozilla/5.0"
    },
    {
        "方法": "POST",
        "URL": "/login.php",
        "参数": {"username": "admin", "password": "123456"},
        "响应码": 302,
        "响应长度": 0,
        "User-Agent": "Mozilla/5.0"
    },
    {
        "方法": "GET",
        "URL": "/profile?user=john",
        "参数": {"user": "john"},
        "响应码": 200,
        "响应长度": 2048,
        "User-Agent": "Mozilla/5.0"
    },
    {
        "方法": "GET",
        "URL": "/download?file=report.pdf",
        "参数": {"file": "report.pdf"},
        "响应码": 200,
        "响应长度": 102400,
        "User-Agent": "Mozilla/5.0"
    },
    {
        "方法": "POST",
        "URL": "/upload.php",
        "参数": {"filename": "avatar.jpg"},
        "响应码": 200,
        "响应长度": 512,
        "User-Agent": "Mozilla/5.0"
    },
    {
        "方法": "GET",
        "URL": "/comment?name=guest&msg=hello",
        "参数": {"name": "guest", "msg": "hello"},
        "响应码": 200,
        "响应长度": 1024,
        "User-Agent": "Mozilla/5.0"
    },
    {
        "方法": "GET",
        "URL": "/admin/users?sort=id",
        "参数": {"sort": "id"},
        "响应码": 200,
        "响应长度": 4096,
        "User-Agent": "Mozilla/5.0"
    },
]

# 模拟数据库
模拟用户数据库 = [
    {"id": 1, "username": "admin", "password": "Admin@2024", "email": "admin@example.com", "role": "admin"},
    {"id": 2, "username": "manager", "password": "Mgr@2024", "email": "manager@example.com", "role": "manager"},
    {"id": 3, "username": "user1", "password": "User@123", "email": "user1@example.com", "role": "user"},
    {"id": 4, "username": "user2", "password": "Pass@456", "email": "user2@example.com", "role": "user"},
    {"id": 5, "username": "guest", "password": "Guest@789", "email": "guest@example.com", "role": "guest"},
]


# ============================================================================
#  案例1: SQL注入攻击与防御
# ============================================================================

class SQL注入演示:
    """SQL注入攻击与防御实战"""

    def __init__(self):
        self.用户数据 = 模拟用户数据库

    def 登录绕过演示(self):
        print("\n" + "=" * 60)
        print("SQL注入 - 登录绕过演示")
        print("=" * 60)
        print("\n  【场景】存在SQL注入的登录验证:")
        print("  [正常登录] 用户名: admin 密码: Admin@2024 -> 登录成功")
        print("  [注入绕过] 用户名: admin\'-- 密码: 任意 -> 登录成功(注入绕过)")
        print("  [永真式绕过] 用户名: \' OR \'1\'=\'1 -> 登录成功(永真式)")

    def UNION注入演示(self):
        print("\n" + "=" * 60)
        print("SQL注入 - UNION 查询注入")
        print("=" * 60)
        print("""
  【步骤】
  1. ORDER BY 猜列数
  2. UNION SELECT 找显示位
  3. 获取数据库名/版本
  4. 枚举表名 (information_schema.tables)
  5. 枚举列名 (information_schema.columns)
  6. 脱库获取数据
        """)
        print("  【模拟脱库结果】")
        for u in self.用户数据:
            print("    " + u["username"] + ":" + u["password"])

    def 盲注演示(self):
        print("\n" + "=" * 60)
        print("SQL注入 - 盲注")
        print("=" * 60)
        print("""
  布尔盲注: 根据页面真假变化逐位猜解数据
  时间盲注: 根据响应延迟判断条件真假

  工具: sqlmap 可自动化完成盲注过程
  防御: 参数化查询 / ORM / 输入验证
        """)

    def SQL注入防御(self):
        print("\n" + "=" * 60)
        print("SQL注入防御方法")
        print("=" * 60)
        print("""
  1. 参数化查询 (预编译语句) - 最有效
  2. ORM框架 (Django ORM, SQLAlchemy)
  3. 输入验证 (白名单优先)
  4. 最小权限原则
  5. WAF防护 (辅助)
        """)

    def 运行全部演示(self):
        self.登录绕过演示()
        self.UNION注入演示()
        self.盲注演示()
        self.SQL注入防御()


# ============================================================================
#  案例2: XSS跨站脚本攻击
# ============================================================================

class XSS攻击演示:
    """XSS跨站脚本攻击实战"""

    def 反射型XSS演示(self):
        print("\n" + "=" * 60)
        print("XSS - 反射型 (Reflected XSS)")
        print("=" * 60)
        print("""
  【原理】恶意脚本通过URL参数传递，服务器反射到页面
  【场景】搜索结果、错误页、参数回显
  【危害】Cookie窃取、会话劫持、钓鱼攻击
        """)

    def 存储型XSS演示(self):
        print("\n" + "=" * 60)
        print("XSS - 存储型 (Stored XSS)")
        print("=" * 60)
        print("""
  【原理】恶意脚本存储在数据库，所有访问者都触发
  【场景】评论区、留言板、用户资料
  【危害】持久化，蠕虫传播，影响所有用户
        """)

    def DOM型XSS演示(self):
        print("\n" + "=" * 60)
        print("XSS - DOM型 (DOM-based XSS)")
        print("=" * 60)
        print("""
  【原理】纯前端漏洞，JS直接操作DOM
  【危险函数】innerHTML, document.write(), eval(), location.hash
  【特点】不经过服务器，日志中可能没有痕迹
        """)

    def XSS防御方法(self):
        print("\n" + "=" * 60)
        print("XSS 防御方法")
        print("=" * 60)
        print("""
  1. 输出编码 (HTML转义) - 最基本
  2. HttpOnly Cookie - 防止Cookie窃取
  3. Content Security Policy (CSP) - 限制脚本来源
  4. 安全DOM操作 - textContent代替innerHTML
  5. 输入验证 - 白名单校验
        """)

    def 运行全部演示(self):
        self.反射型XSS演示()
        self.存储型XSS演示()
        self.DOM型XSS演示()
        self.XSS防御方法()


# ============================================================================
#  案例3: CSRF跨站请求伪造
# ============================================================================

class CSRF攻击演示:
    """CSRF跨站请求伪造实战"""

    def 攻击原理演示(self):
        print("\n" + "=" * 60)
        print("CSRF 攻击原理")
        print("=" * 60)
        print("""
  【原理】利用受害者已登录身份，诱导访问恶意网站
  恶意网站自动发请求，浏览器自动带Cookie
  服务器无法区分是用户主动还是被诱导

  【攻击条件】
  1. 受害者已登录 (有效Cookie)
  2. 关键操作只依赖Cookie认证
  3. 参数格式可预测
  4. 受害者访问了攻击者页面
        """)

    def 攻击场景演示(self):
        print("\n" + "=" * 60)
        print("CSRF 常见攻击场景")
        print("=" * 60)
        print("""
  • 修改用户密码 -> 接管账户
  • 转账操作 -> 资金损失
  • 添加管理员 -> 权限提升
  • 邮件转发设置 -> 信息泄露
  • 退出登录 -> 干扰服务
        """)

    def CSRF防御措施(self):
        print("\n" + "=" * 60)
        print("CSRF 防御措施")
        print("=" * 60)
        print("""
  1. CSRF Token (推荐) - 随机token验证
  2. SameSite Cookie - 限制第三方Cookie
  3. 验证Referer/Origin头 - 辅助防御
  4. 二次验证 - 敏感操作需密码/验证码
  5. 自定义请求头 - X-CSRF-Token
        """)

    def 运行全部演示(self):
        self.攻击原理演示()
        self.攻击场景演示()
        self.CSRF防御措施()


# ============================================================================
#  案例4: 文件上传漏洞
# ============================================================================

class 文件上传漏洞演示:
    """文件上传漏洞实战"""

    def 漏洞原理演示(self):
        print("\n" + "=" * 60)
        print("文件上传漏洞原理")
        print("=" * 60)
        print("""
  【原理】未正确验证文件类型/内容/位置，上传恶意脚本执行
  【危害】获取WebShell、挂马、覆盖系统文件、DoS

  【常见缺陷】
  1. 仅前端验证 (可抓包绕过)
  2. 仅检查扩展名 (大小写/双扩展绕过)
  3. 仅检查Content-Type (可修改)
  4. 仅检查文件头 (图片马)
  5. 文件重命名不当 (00截断)
  6. 上传路径可控 (路径遍历)
        """)

    def 绕过技巧演示(self):
        print("\n" + "=" * 60)
        print("文件上传绕过技巧")
        print("=" * 60)
        print("""
  扩展名绕过:
    shell.php / shell.phtml / shell.PhP
    shell.jpg.php / shell.php%00.jpg / shell.php.

  Content-Type绕过: 修改为 image/jpeg
  文件头绕过: GIF89a + PHP代码 (图片马)
  解析漏洞: Apache从右往左解析扩展名
        """)

    def WebShell演示(self):
        print("\n" + "=" * 60)
        print("WebShell 原理")
        print("=" * 60)
        print("""
  一句话木马:
  PHP: <?php eval($_POST['cmd']); ?>
  ASP: <% eval request("cmd") %>
  JSP: <% Runtime.getRuntime().exec(request.getParameter("cmd")); %>

  工具: 中国菜刀、蚁剑、冰蝎
  功能: 文件管理、虚拟终端、数据库管理
        """)

    def 安全上传配置(self):
        print("\n" + "=" * 60)
        print("文件上传安全配置")
        print("=" * 60)
        print("""
  1. 文件类型验证: 后端白名单 + 内容验证
  2. 文件重命名: 随机文件名，防止猜解
  3. 存储安全: Web根目录外，禁用执行权限
  4. 路径限制: 防止路径遍历
  5. 大小限制: 防DDoS
        """)

    def 运行全部演示(self):
        self.漏洞原理演示()
        self.绕过技巧演示()
        self.WebShell演示()
        self.安全上传配置()


# ============================================================================
#  案例5: 命令注入攻击
# ============================================================================

class 命令注入演示:
    """命令注入攻击实战"""

    def 漏洞原理演示(self):
        print("\n" + "=" * 60)
        print("命令注入攻击原理")
        print("=" * 60)
        print("""
  【原理】用户输入拼接到系统命令中执行
  【常见场景】ping工具、文件操作、系统管理功能
  【危害】执行任意系统命令，获取服务器权限
        """)

    def 注入符号大全(self):
        print("\n" + "=" * 60)
        print("命令注入符号")
        print("=" * 60)
        print("""
  ;     命令分隔符
  &&    逻辑与 (前成功才执行后)
  ||    逻辑或 (前失败才执行后)
  |     管道符
  &     后台执行
  $()   命令替换
  ``    反引号命令替换
  \n    换行分隔
        """)

    def 绕过过滤技巧(self):
        print("\n" + "=" * 60)
        print("命令注入绕过技巧")
        print("=" * 60)
        print("""
  空格绕过: ${IFS} / $IFS$9 / <> / {cmd,arg}
  关键字绕过: c""at / cat$() / ca\t / /bin/???
  无回显: 时间盲注 / DNS外带 / HTTP外带
        """)

    def 命令注入防御(self):
        print("\n" + "=" * 60)
        print("命令注入防御")
        print("=" * 60)
        print("""
  1. 避免调用系统命令 - 用内置函数替代
  2. 参数化调用 - 数组而非字符串拼接
  3. 输入验证 - 白名单校验
  4. 最小权限 - 低权限用户运行服务
  5. 禁用危险函数 - disable_functions
        """)

    def 运行全部演示(self):
        self.漏洞原理演示()
        self.注入符号大全()
        self.绕过过滤技巧()
        self.命令注入防御()


# ============================================================================
#  案例6: Web安全扫描器
# ============================================================================

class Web安全扫描器:
    """Web安全综合扫描器"""

    def __init__(self):
        self.目标URL = "http://test.example.com"
        self.扫描结果 = []

    def 扫描目标(self, 请求列表):
        print("\n" + "=" * 60)
        print("Web安全扫描器 - 目标: " + self.目标URL)
        print("=" * 60)
        print("\n  扫描目标数: " + str(len(请求列表)))
        print("  扫描模块: SQL注入、XSS、目录遍历、命令注入、信息泄露\n")

        for i, req in enumerate(请求列表, 1):
            print("  [" + str(i) + "/" + str(len(请求列表)) + "] " + req["URL"])
            for param in req["参数"].keys():
                if param in ["id", "uid", "page"]:
                    self.扫描结果.append({"类型":"SQL注入","参数":param,"风险":"高","描述":"参数可能存在SQL注入"})
                    print("    [!] 可能SQL注入: " + param)
                if param in ["q", "search", "name", "msg"]:
                    self.扫描结果.append({"类型":"XSS","参数":param,"风险":"中","描述":"参数可能存在反射XSS"})
                    print("    [!] 可能XSS: " + param)
                if param in ["file", "path", "filename"]:
                    self.扫描结果.append({"类型":"目录遍历","参数":param,"风险":"高","描述":"参数可能存在目录遍历"})
                    print("    [!] 可能目录遍历: " + param)
                if param in ["ip", "host", "cmd"]:
                    self.扫描结果.append({"类型":"命令注入","参数":param,"风险":"高","描述":"参数可能存在命令注入"})
                    print("    [!] 可能命令注入: " + param)

        self.扫描结果.append({"类型":"信息泄露","路径":"/.git/config","风险":"高","描述":"发现.git目录泄露"})
        print("    [*] 信息泄露检测... 发现.git目录泄露")
        self.生成报告()

    def 生成报告(self):
        print("\n" + "=" * 60)
        print("扫描报告")
        print("=" * 60)
        print("\n  发现漏洞: " + str(len(self.扫描结果)) + " 个\n")
        for i, item in enumerate(self.扫描结果, 1):
            位置 = item.get("参数", item.get("路径", "-"))
            print("  " + str(i) + ". [" + item["风险"] + "] " + item["类型"] + " - " + 位置)

    def 运行扫描(self):
        self.扫描目标(模拟HTTP请求日志)


# ============================================================================
#  主函数
# ============================================================================

def main():
    print("\n" + "=" * 70)
    print("Web应用安全实战案例集")
    print("=" * 70)
    print("""
请选择要运行的实战案例:
  1. SQL注入攻击与防御
  2. XSS跨站脚本攻击
  3. CSRF跨站请求伪造
  4. 文件上传漏洞
  5. 命令注入攻击
  6. Web安全综合扫描器
  7. 运行全部案例
  0. 退出
""")
    while True:
        try:
            choice = input("\n请输入选项 (0-7): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break
        if choice == "0":
            print("再见！")
            break
        elif choice == "1":
            SQL注入演示().运行全部演示()
        elif choice == "2":
            XSS攻击演示().运行全部演示()
        elif choice == "3":
            CSRF攻击演示().运行全部演示()
        elif choice == "4":
            文件上传漏洞演示().运行全部演示()
        elif choice == "5":
            命令注入演示().运行全部演示()
        elif choice == "6":
            Web安全扫描器().运行扫描()
        elif choice == "7":
            SQL注入演示().运行全部演示()
            XSS攻击演示().运行全部演示()
            CSRF攻击演示().运行全部演示()
            文件上传漏洞演示().运行全部演示()
            命令注入演示().运行全部演示()
            Web安全扫描器().运行扫描()
            print("\n所有案例运行完成！")
        else:
            print("无效选项，请重新输入 (0-7)")
        print("\n" + "-" * 70)

if __name__ == "__main__":
    main()
