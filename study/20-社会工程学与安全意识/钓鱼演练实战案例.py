#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钓鱼演练与安全意识实战案例
=====================================
本文件包含5个完整的社会工程学实战案例：

  1. 企业钓鱼邮件演练系统（GoPhish风格）
  2. OSINT信息收集工具集
  3. 钓鱼网站克隆与检测工具
  4. 安全意识培训评估系统
  5. 社会工程学攻击链分析器

用途: 仅用于授权安全测试和教育学习
作者: 网络安全学习项目
"""

import os
import re
import json
import time
import socket
import base64
import random
import hashlib
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import defaultdict
from urllib.request import Request, urlopen
from urllib.error import URLError
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


# ============================================================
# 案例1: 企业钓鱼演练系统
# ============================================================

class 钓鱼演练系统:
    """
    完整的企业钓鱼演练系统，模拟 GoPhish 功能

    功能:
    1. 目标人员管理（批量导入、分组）
    2. 钓鱼邮件模板设计
    3. 钓鱼网站（着陆页）创建
    4. 发送配置与批量发送
    5. 效果追踪（打开率、点击率、提交率）
    6. 报告生成
    """

    def __init__(self, 演练名称="2026年Q3安全意识测试"):
        self.演练名称 = 演练名称
        self.目标列表 = []
        self.邮件模板 = {}
        self.着陆页 = {}
        self.发送记录 = []
        self.统计 = {
            "发送总数": 0, "邮件打开": 0, "链接点击": 0,
            "数据提交": 0, "报告上报": 0,
        }

    # ---- 目标管理 ----

    def 添加目标(self, 姓名, 邮箱, 部门, 职位):
        """添加演练目标"""
        目标ID = hashlib.md5(邮箱.encode()).hexdigest()[:8]
        self.目标列表.append({
            "ID": 目标ID,
            "姓名": 姓名,
            "邮箱": 邮箱,
            "部门": 部门,
            "职位": 职位,
            "状态": "待发送",
            "打开时间": None,
            "点击时间": None,
            "提交时间": None,
            "报告时间": None,
        })
        return 目标ID

    def 批量导入目标(self, 目标数据):
        """批量导入目标列表"""
        for 目标 in 目标数据:
            self.添加目标(**目标)
        print(f"[+] 已导入 {len(目标数据)} 个目标")

    # ---- 邮件模板设计 ----

    def 创建邮件模板(self, 模板名称, 主题, 发件人, 正文HTML, 仿冒域名):
        """创建钓鱼邮件模板"""
        # 在邮件正文中嵌入追踪像素和唯一链接
        追踪像素 = '<img src="https://phish-demo.security-lab.com/track/open?target_id={{.ID}}" width="1" height="1" />'
        钓鱼链接 = f'<a href="https://phish-demo.security-lab.com/l/{{.ID}}">点击这里</a>'

        # 将模板中的占位符替换
        正文 = 正文HTML.replace("{{.Name}}", "{{.Name}}")
        正文 = 正文.replace("{{.Link}}", 钓鱼链接)
        正文 += 追踪像素

        self.邮件模板[模板名称] = {
            "主题": 主题,
            "发件人": 发件人,
            "仿冒域名": 仿冒域名,
            "正文HTML": 正文,
        }
        print(f"[+] 邮件模板 '{模板名称}' 创建完成")

    def 创建默认模板(self):
        """创建默认钓鱼邮件模板（多个场景）"""
        # 模板1: 密码过期
        self.创建邮件模板(
            "密码过期通知",
            "[紧急] 您的密码将在24小时内过期",
            "IT-Support@company.com",
            """<html><body>
<p>亲爱的 {{.Name}},</p>
<p>您的企业账户密码将在 <strong>24小时内过期</strong>。</p>
<p>为避免影响工作，请点击以下链接立即更新：</p>
<p>{{.Link}}</p>
<p>如果您不更新密码，您的账户将被暂时冻结。</p>
<p>IT支持团队</p>
</body></html>""",
            "company-security.net"
        )

        # 模板2: 文件共享
        self.创建邮件模板(
            "文件共享通知",
            "您有一份新文件需要查看",
            "noreply@share-docs.com",
            """<html><body>
<p>您好 {{.Name}},</p>
<p>有人与您共享了一份文档: <strong>2026年第三季度薪资调整方案.xlsx</strong></p>
<p>点击以下链接查看文档:</p>
<p>{{.Link}}</p>
<p>此链接将在7天后失效。</p>
</body></html>""",
            "share-docs-company.com"
        )

        # 模板3: 快递通知
        self.创建邮件模板(
            "快递通知",
            "您的包裹无法投递 - 请确认地址",
            "service@express-delivery.com",
            """<html><body>
<p>尊敬的 {{.Name}},</p>
<p>您的包裹因地址不详无法投递。</p>
<p>请点击以下链接确认您的收货地址:</p>
<p>{{.Link}}</p>
<p>包裹将重新安排投递。</p>
</body></html>""",
            "express-delivery-service.net"
        )

    # ---- 着陆页创建 ----

    def 创建着陆页(self, 页面名称, HTML模板, 数据收集字段):
        """创建钓鱼网站着陆页"""
        self.着陆页[页面名称] = {
            "HTML": HTML模板,
            "收集字段": 数据收集字段,
        }
        print(f"[+] 着陆页 '{页面名称}' 创建完成")

    def 创建默认着陆页(self):
        """创建默认登录页面"""
        登录页HTML = """<!DOCTYPE html>
<html>
<head><title>企业统一身份认证</title>
<style>
body { font-family: Arial; display: flex; justify-content: center; }
.login-box { width: 350px; padding: 30px; border: 1px solid #ddd; }
input { width: 100%; padding: 10px; margin: 5px 0; }
button { width: 100%; padding: 10px; background: #0078d4; color: white; }
</style></head>
<body>
<div class="login-box">
<h2>企业统一身份认证</h2>
<p>请输入您的凭据登录</p>
<form action="/submit" method="POST">
  <input type="text" name="username" placeholder="用户名" required>
  <input type="password" name="password" placeholder="密码" required>
  <button type="submit">登录</button>
</form>
</div>
</body></html>"""
        self.创建着陆页("企业登录页", 登录页HTML, ["username", "password"])

    # ---- 发送与追踪 ----

    def 发送钓鱼邮件(self, 模板名称):
        """模拟发送钓鱼邮件"""
        模板 = self.邮件模板.get(模板名称)
        if not 模板:
            print(f"[!] 模板 '{模板名称}' 不存在")
            return

        print(f"\n[*] 开始发送钓鱼邮件 (模板: {模板名称})")
        print(f"    主题: {模板['主题']}")
        print(f"    发件人: {模板['发件人']}")

        for 目标 in self.目标列表:
            # 生成唯一追踪ID
            追踪ID = 目标["ID"]
            邮件正文 = 模板["正文HTML"].replace("{{.Name}}", 目标["姓名"])
            邮件正文 = 邮件正文.replace("{{.ID}}", 追踪ID)

            # 记录发送
            self.发送记录.append({
                "目标ID": 追踪ID,
                "姓名": 目标["姓名"],
                "邮箱": 目标["邮箱"],
                "模板": 模板名称,
                "发送时间": datetime.now().isoformat(),
                "状态": "已发送",
            })
            目标["状态"] = "已发送"
            self.统计["发送总数"] += 1

        print(f"[+] 已向 {len(self.目标列表)} 个目标发送钓鱼邮件")

    def 模拟用户行为(self):
        """模拟目标用户的行为（打开/点击/提交/报告）"""
        print(f"\n[*] 模拟用户行为（随机生成）...")

        for 目标 in self.目标列表:
            # 随机决定用户行为
            打开概率 = random.random()
            点击概率 = random.random()
            提交概率 = random.random()
            报告概率 = random.random()

            # 模拟打开邮件（70%概率）
            if 打开概率 < 0.70:
                目标["打开时间"] = datetime.now() + timedelta(
                    seconds=random.randint(60, 3600))
                self.统计["邮件打开"] += 1

                # 模拟点击链接（打开邮件中的50%概率）
                if 点击概率 < 0.50:
                    目标["点击时间"] = 目标["打开时间"] + timedelta(
                        seconds=random.randint(10, 120))
                    self.统计["链接点击"] += 1

                    # 模拟提交数据（点击中的60%概率）
                    if 提交概率 < 0.60:
                        目标["提交时间"] = 目标["点击时间"] + timedelta(
                            seconds=random.randint(5, 60))
                        self.统计["数据提交"] += 1

            # 模拟报告钓鱼（20%概率）
            if 报告概率 < 0.20:
                目标["报告时间"] = datetime.now() + timedelta(
                    minutes=random.randint(1, 30))
                self.统计["报告上报"] += 1

        print(f"[+] 用户行为模拟完成")

    # ---- 报告生成 ----

    def 生成报告(self):
        """生成钓鱼演练报告"""
        print("\n" + "=" * 60)
        print(f"钓鱼演练报告: {self.演练名称}")
        print("=" * 60)

        总数 = self.统计["发送总数"]
        if 总数 == 0:
            print("  无数据")
            return

        打开率 = self.统计["邮件打开"] / 总数 * 100
        点击率 = self.统计["链接点击"] / 总数 * 100
        提交率 = self.统计["数据提交"] / 总数 * 100
        报告率 = self.统计["报告上报"] / 总数 * 100

        print(f"\n  演练统计:")
        print(f"  {'指标':<20} {'数值':<10} {'比率':<10}")
        print(f"  {'-'*40}")
        print(f"  {'发送总数':<20} {总数:<10} {'100%':<10}")
        print(f"  {'邮件打开':<20} {self.统计['邮件打开']:<10} {打开率:.1f}%")
        print(f"  {'链接点击':<20} {self.统计['链接点击']:<10} {点击率:.1f}%")
        print(f"  {'数据提交':<20} {self.统计['数据提交']:<10} {提交率:.1f}%")
        print(f"  {'报告上报':<20} {self.统计['报告上报']:<10} {报告率:.1f}%")

        # 风险评估
        print(f"\n  风险评估:")
        if 提交率 > 30:
            风险等级 = "极高风险"
            print(f"    风险等级: {风险等级}")
            print(f"    超过30%的用户提交了凭据 → 需要紧急安全培训")
        elif 提交率 > 15:
            风险等级 = "高风险"
            print(f"    风险等级: {风险等级}")
            print(f"    超过15%的用户提交了凭据 → 需要加强安全培训")
        elif 提交率 > 5:
            风险等级 = "中风险"
            print(f"    风险等级: {风险等级}")
            print(f"    超过5%的用户提交了凭据 → 需要针对性培训")
        else:
            风险等级 = "低风险"
            print(f"    风险等级: {风险等级}")
            print(f"    不足5%的用户提交了凭据 → 保持定期演练")

        # 部门分析
        print(f"\n  部门统计:")
        部门统计 = defaultdict(lambda: {"发送": 0, "打开": 0, "点击": 0, "提交": 0})
        for 目标 in self.目标列表:
            部门 = 目标["部门"]
            部门统计[部门]["发送"] += 1
            if 目标["打开时间"]:
                部门统计[部门]["打开"] += 1
            if 目标["点击时间"]:
                部门统计[部门]["点击"] += 1
            if 目标["提交时间"]:
                部门统计[部门]["提交"] += 1

        print(f"  {'部门':<15} {'发送':<8} {'打开':<8} {'点击':<8} {'提交':<8} {'提交率'}")
        print(f"  {'-'*55}")
        for 部门, 数据 in sorted(部门统计.items()):
            提交率 = 数据["提交"] / 数据["发送"] * 100 if 数据["发送"] > 0 else 0
            print(f"  {部门:<15} {数据['发送']:<8} {数据['打开']:<8} "
                  f"{数据['点击']:<8} {数据['提交']:<8} {提交率:.0f}%")

        # 改进建议
        print(f"\n  改进建议:")
        if 提交率 > 15:
            print(f"    [紧急] 立即组织全员安全意识培训")
            print(f"    [紧急] 对提交凭据的用户进行密码重置")
        if 报告率 < 10:
            print(f"    [重要] 加强钓鱼报告渠道宣传（当前报告率仅{报告率:.0f}%）")
        if 打开率 > 70:
            print(f"    [重要] 加强邮件识别培训（当前打开率{打开率:.0f}%）")
        print(f"    [建议] 每3个月进行一次钓鱼演练")
        print(f"    [建议] 针对高风险部门进行专项培训")
        print(f"    [建议] 建立安全意识积分制度")

    def 执行完整演练(self):
        """执行完整的钓鱼演练流程"""
        print("\n" + "=" * 60)
        print(f"钓鱼演练系统: {self.演练名称}")
        print("=" * 60)

        # 创建模板和着陆页
        self.创建默认模板()
        self.创建默认着陆页()

        # 添加目标
        目标数据 = [
            {"姓名": "张三", "邮箱": "zhangsan@company.com", "部门": "技术部", "职位": "工程师"},
            {"姓名": "李四", "邮箱": "lisi@company.com", "部门": "财务部", "职位": "主管"},
            {"姓名": "王五", "邮箱": "wangwu@company.com", "部门": "人事部", "职位": "专员"},
            {"姓名": "赵六", "邮箱": "zhaoliu@company.com", "部门": "市场部", "职位": "经理"},
            {"姓名": "孙七", "邮箱": "sunqi@company.com", "部门": "技术部", "职位": "架构师"},
            {"姓名": "周八", "邮箱": "zhouba@company.com", "部门": "财务部", "职位": "会计"},
            {"姓名": "吴九", "邮箱": "wujiu@company.com", "部门": "销售部", "职位": "销售"},
            {"姓名": "郑十", "邮箱": "zhengshi@company.com", "部门": "法务部", "职位": "律师"},
            {"姓名": "钱十一", "邮箱": "qian11@company.com", "部门": "市场部", "职位": "策划"},
            {"姓名": "孙十二", "邮箱": "sun12@company.com", "部门": "技术部", "职位": "测试"},
        ]
        self.批量导入目标(目标数据)

        # 发送邮件
        self.发送钓鱼邮件("密码过期通知")

        # 模拟用户行为
        self.模拟用户行为()

        # 生成报告
        self.生成报告()


# ============================================================
# 案例2: OSINT信息收集工具集
# ============================================================

class OSINT收集工具:
    """
    开源情报收集工具集

    功能:
    1. 域名信息收集（WHOIS/DNS/子域名）
    2. 邮箱信息收集
    3. 社交媒体信息收集
    4. 数据泄露检查
    5. 技术栈识别
    6. 报告生成
    """

    def __init__(self, 目标域名="target-company.com"):
        self.目标域名 = 目标域名
        self.情报 = {
            "域名信息": {},
            "子域名": [],
            "邮箱": [],
            "员工信息": [],
            "技术栈": {},
            "泄露检查": {},
        }

    def 收集域名信息(self):
        """收集域名WHOIS和DNS信息"""
        print(f"\n[*] 收集 {self.目标域名} 的域名信息...")

        # 模拟WHOIS查询
        模拟WHOIS = {
            "注册商": "Alibaba Cloud Computing Ltd.",
            "注册日期": "2015-03-15",
            "过期日期": "2027-03-15",
            "注册人组织": "Target Company Ltd.",
            "DNS服务器": ["ns1.target-company.com", "ns2.target-company.com"],
        }

        # DNS记录查询
        模拟DNS = {
            "A记录": ["103.235.46.39"],
            "MX记录": ["mail.target-company.com"],
            "TXT记录": ["v=spf1 include:_spf.mail.target-company.com ~all"],
            "NS记录": ["ns1.target-company.com", "ns2.target-company.com"],
            "CNAME": {"www": "target-company.com", "mail": "mail.target-company.com"},
        }

        self.情报["域名信息"] = {"WHOIS": 模拟WHOIS, "DNS": 模拟DNS}

        print(f"  [+] 注册商: {模拟WHOIS['注册商']}")
        print(f"  [+] 注册日期: {模拟WHOIS['注册日期']}")
        print(f"  [+] A记录: {模拟DNS['A记录']}")
        print(f"  [+] MX记录: {模拟DNS['MX记录']}")
        print(f"  [+] SPF记录: {模拟DNS['TXT记录']}")

    def 收集子域名(self):
        """收集子域名"""
        print(f"\n[*] 收集子域名...")

        # 模拟子域名收集
        子域名列表 = [
            "www.target-company.com",
            "mail.target-company.com",
            "vpn.target-company.com",
            "owa.target-company.com",
            "portal.target-company.com",
            "git.target-company.com",
            "ci.target-company.com",
            "api.target-company.com",
            "admin.target-company.com",
            "test.target-company.com",
            "staging.target-company.com",
            "docs.target-company.com",
        ]

        self.情报["子域名"] = 子域名列表
        print(f"  [+] 发现 {len(子域名列表)} 个子域名:")
        for 子域名 in 子域名列表:
            print(f"      - {子域名}")

    def 收集邮箱信息(self):
        """收集邮箱地址"""
        print(f"\n[*] 收集邮箱信息...")

        # 模拟邮箱格式发现
        邮箱列表 = [
            {"邮箱": "zhangsan@target-company.com", "姓名": "张三", "职位": "CTO"},
            {"邮箱": "lisi@target-company.com", "姓名": "李四", "职位": "IT经理"},
            {"邮箱": "wangwu@target-company.com", "姓名": "王五", "职位": "安全工程师"},
            {"邮箱": "zhaoliu@target-company.com", "姓名": "赵六", "职位": "开发主管"},
        ]

        self.情报["邮箱"] = 邮箱列表
        print(f"  [+] 发现 {len(邮箱列表)} 个邮箱:")
        for 信息 in 邮箱列表:
            print(f"      - {信息['邮箱']} ({信息['姓名']}, {信息['职位']})")

        print(f"  [*] 邮箱格式: 姓名拼音@target-company.com")

    def 识别技术栈(self):
        """识别目标网站技术栈"""
        print(f"\n[*] 识别技术栈...")

        模拟技术栈 = {
            "Web服务器": "Nginx 1.18.0",
            "后端语言": "Java (Spring Boot)",
            "前端框架": "Vue.js 3 + Element Plus",
            "数据库": "MySQL 8.0",
            "CMS": "自研",
            "CDN": "阿里云CDN",
            "WAF": "阿里云WAF",
            "SSL证书": "DigiCert OV",
            "分析工具": "百度统计",
        }

        self.情报["技术栈"] = 模拟技术栈
        print(f"  [+] 技术栈识别结果:")
        for 类别, 信息 in 模拟技术栈.items():
            print(f"      {类别}: {信息}")

    def 检查数据泄露(self):
        """检查数据泄露"""
        print(f"\n[*] 检查数据泄露...")

        # 模拟Have I Been Pwned查询
        泄露记录 = [
            {"邮箱": "zhangsan@target-company.com", "泄露源": "LinkedIn 2021数据泄露",
             "泄露类型": "邮箱+姓名+职位", "泄露时间": "2021-06"},
            {"邮箱": "lisi@target-company.com", "泄露源": "Adobe 2013数据泄露",
             "泄露类型": "邮箱+密码提示", "泄露时间": "2013-10"},
        ]

        self.情报["泄露检查"] = 泄露记录
        print(f"  [+] 发现 {len(泄露记录)} 条泄露记录:")
        for 记录 in 泄露记录:
            print(f"      - {记录['邮箱']}: {记录['泄露源']} ({记录['泄露时间']})")

    def 生成OSINT报告(self):
        """生成OSINT报告"""
        print("\n" + "=" * 60)
        print(f"OSINT信息收集报告: {self.目标域名}")
        print("=" * 60)

        print(f"\n  收集摘要:")
        print(f"    域名信息: {'已收集' if self.情报['域名信息'] else '无'}")
        print(f"    子域名: {len(self.情报['子域名'])} 个")
        print(f"    邮箱: {len(self.情报['邮箱'])} 个")
        print(f"    技术栈: {len(self.情报['技术栈'])} 项")
        print(f"    数据泄露: {len(self.情报['泄露检查'])} 条")

        # 钓鱼攻击建议
        print(f"\n  钓鱼攻击建议:")
        if self.情报["邮箱"]:
            print(f"    [*] 使用发现的邮箱作为钓鱼目标")
            print(f"    [*] 邮箱格式: 姓名拼音@target-company.com")
        if self.情报["技术栈"].get("CMS") == "自研":
            print(f"    [*] 目标使用自研CMS，可尝试通用漏洞")
        if self.情报["泄露检查"]:
            print(f"    [*] 发现数据泄露记录，可能已暴露凭据")
            print(f"    [*] 可尝试泄露的密码进行撞库攻击")

    def 执行完整收集(self):
        """执行完整的OSINT收集"""
        self.收集域名信息()
        self.收集子域名()
        self.收集邮箱信息()
        self.识别技术栈()
        self.检查数据泄露()
        self.生成OSINT报告()


# ============================================================
# 案例3: 钓鱼网站克隆与检测工具
# ============================================================

class 钓鱼网站检测器:
    """
    钓鱼网站检测与分析工具

    功能:
    1. URL安全分析
    2. 域名相似度检测（同形异义字/子域名欺骗）
    3. 页面特征分析（表单检测/SSL验证）
    4. 黑名单检查
    5. 综合风险评分
    """

    # 常见钓鱼关键词
    钓鱼关键词 = [
        "login", "signin", "verify", "update", "confirm", "secure",
        "account", "password", "unlock", "validate", "wallet",
        "bank", "paypal", "apple", "microsoft", "google",
        "密码", "登录", "验证", "确认", "更新", "解锁",
    ]

    # 可信域名白名单（部分）
    可信域名 = [
        "google.com", "microsoft.com", "apple.com", "amazon.com",
        "github.com", "linkedin.com", "twitter.com", "facebook.com",
        "taobao.com", "baidu.com", "qq.com", "alipay.com",
    ]

    def __init__(self):
        self.分析结果 = {}

    def 分析URL(self, url):
        """分析URL安全性"""
        print(f"\n[*] 分析URL: {url}")
        解析结果 = urlparse(url)
        域名 = 解析结果.netloc

        分析 = {
            "URL": url,
            "域名": 域名,
            "协议": 解析结果.scheme,
            "路径": 解析结果.path,
            "查询参数": parse_qs(解析结果.query),
        }

        # 检查1: HTTPS
        分析["HTTPS"] = 解析结果.scheme == "https"
        if not 分析["HTTPS"]:
            print(f"  [!] 警告: 使用HTTP明文传输")
            分析["风险项"] = 分析.get("风险项", [])
            分析["风险项"].append("使用HTTP而非HTTPS")

        # 检查2: 域名相似度
        相似域名 = self.检查域名相似度(域名)
        if 相似域名:
            print(f"  [!] 警告: 域名与可信域名相似: {相似域名}")
            分析["相似可信域名"] = 相似域名
            分析["风险项"] = 分析.get("风险项", [])
            分析["风险项"].append(f"域名与可信域名相似: {相似域名}")

        # 检查3: 子域名欺骗
        欺骗检测 = self.检查子域名欺骗(域名)
        if 欺骗检测:
            print(f"  [!] 警告: 可能存在子域名欺骗: {欺骗骗检测}")
            分析["子域名欺骗"] = 欺骗检测
            分析["风险项"] = 分析.get("风险项", [])
            分析["风险项"].append("子域名欺骗")

        # 检查4: URL中的钓鱼关键词
        关键词匹配 = [kw for kw in self.钓鱼关键词 if kw in url.lower()]
        if 关键词匹配:
            print(f"  [!] URL包含钓鱼关键词: {关键词匹配}")
            分析["钓鱼关键词"] = 关键词匹配

        # 检查5: IP地址作为域名
        if re.match(r'\d+\.\d+\.\d+\.\d+', 域名):
            print(f"  [!] 警告: 使用IP地址而非域名")
            分析["风险项"] = 分析.get("风险项", [])
            分析["风险项"].append("使用IP地址而非域名")

        # 检查6: URL长度
        if len(url) > 100:
            print(f"  [!] 警告: URL异常长 ({len(url)}字符)")
            分析["风险项"] = 分析.get("风险项", [])
            分析["风险项"].append("URL异常长")

        # 计算风险评分
        风险分 = 0
        if not 分析.get("HTTPS"):
            风险分 += 20
        if 分析.get("相似可信域名"):
            风险分 += 30
        if 分析.get("子域名欺骗"):
            风险分 += 25
        if 分析.get("钓鱼关键词"):
            风险分 += 15
        if re.match(r'\d+\.\d+\.\d+\.\d+', 域名):
            风险分 += 20
        if len(url) > 100:
            风险分 += 10

        分析["风险评分"] = 风险分
        if 风险分 >= 60:
            分析["风险等级"] = "极高风险"
        elif 风险分 >= 40:
            分析["风险等级"] = "高风险"
        elif 风险分 >= 20:
            分析["风险等级"] = "中风险"
        else:
            分析["风险等级"] = "低风险"

        print(f"\n  [结果] 风险评分: {风险分}/100 ({分析['风险等级']})")
        self.分析结果[url] = 分析
        return 分析

    def 检查域名相似度(self, 域名):
        """检查域名是否与可信域名相似（同形异义字检测）"""
        相似列表 = []

        # 同形异义字映射
        同形字 = {
            '0': 'o', '1': 'l', '3': 'e', '5': 's', '7': 't',
            '@': 'a', '$': 's', '!': 'i',
            'rn': 'm', 'vv': 'w', 'cl': 'd',
        }

        # 去除TLD后比较
        域名核心 = 域名.split('.')[0].lower()

        for 可信 in self.可信域名:
            可信核心 = 可信.split('.')[0]
            # 检查字符替换
            规范化 = 域名核心
            for 原字, 替字 in 同形字.items():
                规范化 = 规范化.replace(原字, 替字)

            if 规范化 == 可信核心 and 域名核心 != 可信核心:
                相似列表.append(f"{域名} → {可信}")

            # 检查添加/删除字符
            if abs(len(域名核心) - len(可信核心)) <= 2:
                差异 = 0
                for i, (a, b) in enumerate(zip(域名核心, 可信核心)):
                    if a != b:
                        差异 += 1
                if 差异 <= 2 and len(域名核心) != len(可信核心):
                    相似列表.append(f"{域名} → {可信}")

        return 相似列表

    def 检查子域名欺骗(self, 域名):
        """检查子域名欺骗"""
        欺骗列表 = []

        # 检查可信域名是否出现在子域名中
        for 可信 in self.可信域名:
            if 可信 in 域名 and not 域名.endswith(可信):
                # 可信域名出现在子域名但不是主域名
                欺骗列表.append(f"'{可信}' 出现在子域名中")
                break

        # 检查多级子域名（超过3级）
        子域级别 = len(域名.split('.'))
        if 子域级别 > 3:
            欺骗列表.append(f"子域名层级过多({子域级别}级)")

        return 欺骗列表

    def 批量分析(self, url列表):
        """批量分析URL"""
        print("\n" + "=" * 60)
        print("钓鱼网站检测器 - 批量分析")
        print("=" * 60)

        for url in url列表:
            self.分析URL(url)

        # 生成汇总报告
        print("\n" + "=" * 60)
        print("分析汇总报告")
        print("=" * 60)

        for url, 结果 in self.分析结果.items():
            等级 = 结果.get("风险等级", "未知")
            评分 = 结果.get("风险评分", 0)
            print(f"  [{等级}] ({评分}分) {url[:60]}...")

    def 执行检测示例(self):
        """执行检测示例"""
        测试URL列表 = [
            "https://www.google.com/login",  # 安全
            "http://login.microsoft.com.evil.com/verify",  # 子域名欺骗
            "https://paypa1.com/signin",  # 同形异义字
            "https://192.168.1.1/admin/login",  # IP地址
            "https://company-security.net/update?account=verify&urgent=true",  # 钓鱼关键词
            "https://mail.target-company.com.update-password.net/login",  # 子域名欺骗
        ]
        self.批量分析(测试URL列表)


# ============================================================
# 案例4: 安全意识培训评估系统
# ============================================================

class 安全意识评估系统:
    """
    安全意识培训评估系统

    功能:
    1. 知识测验题库
    2. 自动组卷与评分
    3. 能力维度评估
    4. 薄弱环节分析
    5. 个性化学习建议
    """

    # 知识题库
    题库 = [
        {
            "题目": "收到一封来自'IT部门'的邮件，要求你点击链接更新密码。你应该怎么做？",
            "选项": ["立即点击链接更新", "检查发件人邮箱地址，联系IT确认",
                      "忽略这封邮件", "转发给同事问问"],
            "正确答案": 1,
            "维度": "钓鱼识别",
            "难度": "简单",
        },
        {
            "题目": "以下哪个密码最安全？",
            "选项": ["12345678", "Qwerty2024!", "P@ssw0rd", "x9K$mP2#vL7nQ4!"],
            "正确答案": 3,
            "维度": "密码安全",
            "难度": "简单",
        },
        {
            "题目": "在使用公共WiFi时，以下哪种做法最安全？",
            "选项": ["直接进行网上银行操作", "使用VPN后再操作",
                      "只浏览网页不登录", "关闭防火墙提高网速"],
            "正确答案": 1,
            "维度": "网络安全",
            "难度": "中等",
        },
        {
            "题目": "同事说他用U盘从外面拷了些文件，要在你的电脑上打开。你应该？",
            "选项": ["直接帮他打开", "先杀毒再打开",
                      "拒绝在办公电脑使用外来U盘", "插上看文件大小再决定"],
            "正确答案": 2,
            "维度": "终端安全",
            "难度": "中等",
        },
        {
            "题目": "发现公司内网存在异常，正确做法是？",
            "选项": ["自己尝试修复", "立即上报安全团队",
                      "不管它，不是自己的事", "发到群里讨论"],
            "正确答案": 1,
            "维度": "安全意识",
            "难度": "简单",
        },
        {
            "题目": "关于个人信息保护，以下说法正确的是？",
            "选项": ["可以随意在社交媒体分享工作内容",
                      "工牌照片可以发朋友圈",
                      "不应在社交媒体暴露工牌、屏幕、文档",
                      "只发几张截图没关系"],
            "正确答案": 2,
            "维度": "隐私保护",
            "难度": "中等",
        },
        {
            "题目": "收到自称是领导的微信/钉钉消息要求转账，应该？",
            "选项": ["领导要求赶紧转", "通过其他渠道核实领导身份",
                      "拒绝但不报告", "先转一半试试"],
            "正确答案": 1,
            "维度": "社会工程学",
            "难度": "中等",
        },
        {
            "题目": "以下哪种行为可能导致数据泄露？",
            "选项": ["定期更新系统补丁", "使用强密码并定期更换",
                      "将客户数据通过个人邮箱发送", "开启两步验证"],
            "正确答案": 2,
            "维度": "数据安全",
            "难度": "简单",
        },
        {
            "题目": "发现使用的软件有漏洞公告但尚未修复，应该？",
            "选项": ["继续使用，等官方修复", "停止使用并寻找替代方案",
                      "自己在网上找补丁打", "在漏洞公告下评论"],
            "正确答案": 1,
            "维度": "漏洞管理",
            "难度": "困难",
        },
        {
            "题目": "处理含敏感信息的纸质文件时，应该？",
            "选项": ["直接扔垃圾桶", "撕成几片扔掉",
                      "使用碎纸机销毁", "留作草稿纸用"],
            "正确答案": 2,
            "维度": "数据安全",
            "难度": "简单",
        },
    ]

    def __init__(self, 参训者姓名="测试用户"):
        self.参训者 = 参训者姓名
        self.答题记录 = []
        self.维度得分 = defaultdict(lambda: {"正确": 0, "总数": 0})
        self.总分 = 0

    def 组卷(self, 题目数=10):
        """随机组卷"""
        random.shuffle(self.题库)
        return self.题库[:题目数]

    def 模拟答题(self, 正确率=0.6):
        """模拟参训者答题"""
        试卷 = self.组卷(len(self.题库))
        print(f"\n[*] 安全意识测验 - 参训者: {self.参训者}")
        print(f"    题目数量: {len(试卷)}")
        print(f"    模拟正确率: {正确率*100:.0f}%")

        for i, 题 in enumerate(试卷, 1):
            # 根据正确率随机决定是否答对
            是否正确 = random.random() < 正确率
            选择 = 题["正确答案"] if 是否正确 else random.choice(
                [j for j in range(len(题["选项"])) if j != 题["正确答案"]])

            self.答题记录.append({
                "题号": i,
                "题目": 题["题目"],
                "维度": 题["维度"],
                "选择": 选择,
                "正确答案": 题["正确答案"],
                "是否正确": 是否正确,
            })

            self.维度得分[题["维度"]]["总数"] += 1
            if 是否正确:
                self.维度得分[题["维度"]]["正确"] += 1

    def 生成评估报告(self):
        """生成评估报告"""
        print("\n" + "=" * 60)
        print(f"安全意识评估报告 - {self.参训者}")
        print("=" * 60)

        总题数 = len(self.答题记录)
        正确数 = sum(1 for r in self.答题记录 if r["是否正确"])
        self.总分 = 正确数 / 总题数 * 100 if 总题数 > 0 else 0

        print(f"\n  总分: {self.总分:.0f}/100 ({正确数}/{总题数}正确)")

        # 等级评定
        if self.总分 >= 90:
            等级 = "优秀"
        elif self.总分 >= 75:
            等级 = "良好"
        elif self.总分 >= 60:
            等级 = "及格"
        else:
            等级 = "不及格"
        print(f"  等级: {等级}")

        # 维度分析
        print(f"\n  能力维度分析:")
        print(f"  {'维度':<15} {'正确率':<10} {'评级'}")
        print(f"  {'-'*40}")

        for 维度, 得分 in sorted(self.维度得分.items()):
            正确率 = 得分["正确"] / 得分["总数"] * 100 if 得分["总数"] > 0 else 0
            if 正确率 >= 80:
                评级 = "强"
            elif 正确率 >= 60:
                评级 = "中"
            else:
                评级 = "弱"
            print(f"  {维度:<15} {正确率:.0f}%       {评级}")

        # 薄弱环节
        薄弱维度 = []
        for 维度, 得分 in self.维度得分.items():
            正确率 = 得分["正确"] / 得分["总数"] * 100 if 得分["总数"] > 0 else 0
            if 正确率 < 60:
                薄弱维度.append(维度)

        # 学习建议
        print(f"\n  个性化学习建议:")
        if self.总分 < 60:
            print(f"    [紧急] 安全意识不足，需要参加基础安全培训")
        if 薄弱维度:
            print(f"    [重点] 薄弱环节: {', '.join(薄弱维度)}")
            for 维度 in 薄弱维度:
                if 维度 == "钓鱼识别":
                    print(f"      → 完成钓鱼模拟训练")
                elif 维度 == "密码安全":
                    print(f"      → 学习密码安全最佳实践")
                elif 维度 == "社会工程学":
                    print(f"      → 学习社会工程学识别技巧")
                elif 维度 == "数据安全":
                    print(f"      → 学习数据分类分级与保护")
        if self.总分 >= 75:
            print(f"    [鼓励] 整体表现良好，可参加进阶安全课程")

    def 执行评估(self):
        """执行完整评估"""
        self.模拟答题(正确率=0.65)
        self.生成评估报告()


# ============================================================
# 案例5: 社会工程学攻击链分析器
# ============================================================

class 攻击链分析器:
    """
    社会工程学攻击链分析与可视化工具

    功能:
    1. 攻击链建模（侦察→投递→利用→持久化→行动）
    2. ATT&CK 映射
    3. 防御控制点分析
    4. 攻击成本与防御效费比分析
    """

    def __init__(self):
        self.攻击链 = []

    def 分析钓鱼攻击链(self):
        """分析典型钓鱼攻击链"""
        攻击阶段 = [
            {
                "阶段": "侦察",
                "ATT&CK": "T1591.002 - 收集受害者主机信息",
                "活动": ["LinkedIn收集员工信息", "GitHub搜索泄露凭据",
                         "公司网站收集技术信息", "DNS枚举子域名"],
                "攻击成本": "低（2-4小时）",
                "防御控制": ["限制社交媒体信息暴露", "GitHub凭据泄露监控"],
                "检测难度": "高",
            },
            {
                "阶段": "投递",
                "ATT&CK": "T1566.002 - 鱼叉钓鱼链接",
                "活动": ["注册相似域名", "创建钓鱼邮件",
                         "部署钓鱼网站", "发送鱼叉邮件"],
                "攻击成本": "中（4-8小时）",
                "防御控制": ["SPF/DKIM/DMARC", "邮件安全网关",
                         "域名相似度监控", "用户安全意识"],
                "检测难度": "中",
            },
            {
                "阶段": "利用",
                "ATT&CK": "T1059.001 - PowerShell",
                "活动": ["用户点击链接", "下载恶意Payload",
                         "PowerShell执行", "绕过AMSI"],
                "攻击成本": "低（自动化）",
                "防御控制": ["AMSI", "EDR", "PowerShell执行策略",
                         "攻击面减少(ASR)规则"],
                "检测难度": "中",
            },
            {
                "阶段": "持久化",
                "ATT&CK": "T1547.001 - 注册表Run键",
                "活动": ["注册表自启动", "创建计划任务",
                         "部署后门服务"],
                "攻击成本": "低",
                "防御控制": ["Sysmon监控注册表", "EDR行为检测",
                         "配置基线审计"],
                "检测难度": "低",
            },
            {
                "阶段": "命令与控制",
                "ATT&CK": "T1071.001 - Web协议",
                "活动": ["HTTPS Beacon通信", "数据外传",
                         "内网横向移动指令"],
                "攻击成本": "中",
                "防御控制": ["NDR网络流量分析", "防火墙出站策略",
                         "DNS监控", "TLS中间人检测"],
                "检测难度": "高",
            },
        ]

        self.攻击链 = 攻击阶段

    def 生成分析报告(self):
        """生成攻击链分析报告"""
        print("\n" + "=" * 60)
        print("社会工程学攻击链分析报告")
        print("=" * 60)

        print(f"\n  攻击链可视化:")
        链路 = " → ".join([阶段["阶段"] for 阶段 in self.攻击链])
        print(f"  {链路}")

        print(f"\n  各阶段分析:")
        for 阶段 in self.攻击链:
            print(f"\n  ── {阶段['阶段']} ──")
            print(f"    ATT&CK: {阶段['ATT&CK']}")
            print(f"    活动:")
            for 活动 in 阶段["活动"]:
                print(f"      • {活动}")
            print(f"    攻击成本: {阶段['攻击成本']}")
            print(f"    检测难度: {阶段['检测难度']}")
            print(f"    防御控制:")
            for 控制 in 阶段["防御控制"]:
                print(f"      ✓ {控制}")

        # 防御效费比分析
        print(f"\n  防御效费比分析:")
        print(f"  {'阶段':<10} {'检测难度':<10} {'最有效控制':<25} {'效费比'}")
        print(f"  {'-'*60}")
        for 阶段 in self.攻击链:
            最佳控制 = 阶段["防御控制"][0] if 阶段["防御控制"] else "无"
            效费比 = "高" if 阶段["检测难度"] == "低" else "中" if 阶段["检测难度"] == "中" else "低"
            print(f"  {阶段['阶段']:<10} {阶段['检测难度']:<10} {最佳控制:<25} {效费比}")

        # 关键结论
        print(f"\n  关键结论:")
        print(f"    1. 投递阶段是最佳拦截点（邮件安全网关+用户意识）")
        print(f"    2. 利用阶段的AMSI/EDR是第二道防线")
        print(f"    3. C2阶段检测难度最高，需要NDR+SIEM联动")
        print(f"    4. 用户安全意识是效费比最高的防御措施")
        print(f"    5. 建议在侦察阶段加强OSINT监控和泄露检测")


# ============================================================
# 主程序
# ============================================================

def 主菜单():
    """主菜单"""
    print("""
╔══════════════════════════════════════════════╗
║        社会工程学与安全意识实战案例              ║
╠══════════════════════════════════════════════╣
║  1. 企业钓鱼演练系统                           ║
║  2. OSINT信息收集工具                          ║
║  3. 钓鱼网站检测器                             ║
║  4. 安全意识评估系统                           ║
║  5. 攻击链分析器                               ║
║  6. 执行全部案例                               ║
║  0. 退出                                       ║
╚══════════════════════════════════════════════╝
    """)
    return input("请选择 [0-6]: ").strip()


def 主程序():
    """主程序入口"""
    while True:
        选择 = 主菜单()

        if 选择 == "1":
            演练 = 钓鱼演练系统("2026年Q3安全意识测试")
            演练.执行完整演练()

        elif 选择 == "2":
            osint = OSINT收集工具("target-company.com")
            osint.执行完整收集()

        elif 选择 == "3":
            检测器 = 钓鱼网站检测器()
            检测器.执行检测示例()

        elif 选择 == "4":
            评估 = 安全意识评估系统("测试用户")
            评估.执行评估()

        elif 选择 == "5":
            分析器 = 攻击链分析器()
            分析器.分析钓鱼攻击链()
            分析器.生成分析报告()

        elif 选择 == "6":
            print("\n" + "=" * 60)
            print("执行全部案例")
            print("=" * 60)

            案例1 = 钓鱼演练系统("2026年Q3安全意识测试")
            案例1.执行完整演练()

            案例2 = OSINT收集工具("target-company.com")
            案例2.执行完整收集()

            案例3 = 钓鱼网站检测器()
            案例3.执行检测示例()

            案例4 = 安全意识评估系统("测试用户")
            案例4.执行评估()

            案例5 = 攻击链分析器()
            案例5.分析钓鱼攻击链()
            案例5.生成分析报告()

            print("\n" + "=" * 60)
            print("全部案例执行完成")
            print("=" * 60)

        elif 选择 == "0":
            print("退出程序")
            break


if __name__ == "__main__":
    主程序()
