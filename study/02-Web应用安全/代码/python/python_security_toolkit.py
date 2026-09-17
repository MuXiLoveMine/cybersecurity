#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python Web安全工具集 - 综合Web安全扫描工具包

本工具集集成了以下安全检测功能：
1. SQL注入扫描器（基于错误/基于时间/基于布尔）
2. XSS检测器（反射型/存储型/DOM型）
3. 目录暴力破解工具（支持字典文件）
4. HTTP头安全检查器（CSP/HSTS/X-Frame-Options等）
5. 子域名枚举器（多数据源）
6. 多线程端口扫描器
7. Web漏洞报告生成器

使用方法：
    python python_security_toolkit.py --help
    python python_security_toolkit.py sqli -u "http://example.com/page?id=1"
    python python_security_toolkit.py xss -u "http://example.com/search?q=test"
    python python_security_toolkit.py dirbrute -u "http://example.com/" -w wordlist.txt
    python python_security_toolkit.py headers -u "http://example.com/"
    python python_security_toolkit.py subdomain -d example.com
    python python_security_toolkit.py portscan -H 127.0.0.1 -p 1-1000
    python python_security_toolkit.py report -u "http://example.com/" --all

免责声明：仅用于授权的安全测试，未经授权扫描目标网站属于违法行为。
"""

import os
import re
import sys
import time
import json
import random
import string
import hashlib
import argparse
import socket
import threading
import subprocess
from urllib.parse import urlparse, urljoin, urlencode, parse_qs, quote
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


# ============================================================================
# 全局配置与常量
# ============================================================================

class Config:
    """全局配置类"""
    # 请求超时（秒）
    TIMEOUT = 10
    # 最大重试次数
    MAX_RETRIES = 3
    # 并发线程数
    MAX_THREADS = 10
    # 默认User-Agent
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    # 常用HTTP方法
    HTTP_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'HEAD']
    # HTTP响应码含义映射
    STATUS_CODES = {
        200: 'OK',
        301: '永久重定向',
        302: '临时重定向',
        400: '错误请求',
        401: '未授权',
        403: '禁止访问',
        404: '未找到',
        500: '服务器内部错误',
        502: '网关错误',
        503: '服务不可用',
    }


class Colors:
    """终端输出颜色"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_info(msg):
    """打印信息"""
    print(f"{Colors.BLUE}[INFO]{Colors.END} {msg}")

def print_success(msg):
    """打印成功"""
    print(f"{Colors.GREEN}[成功]{Colors.END} {msg}")

def print_warning(msg):
    """打印警告"""
    print(f"{Colors.YELLOW}[警告]{Colors.END} {msg}")

def print_error(msg):
    """打印错误"""
    print(f"{Colors.RED}[错误]{Colors.END} {msg}")

def print_vuln(msg):
    """打印漏洞"""
    print(f"{Colors.RED + Colors.BOLD}[漏洞]{Colors.END} {msg}")


def create_session(retries: int = Config.MAX_RETRIES) -> requests.Session:
    """
    创建带重试机制的requests会话

    Args:
        retries: 最大重试次数

    Returns:
        requests.Session对象
    """
    session = requests.Session()
    retry = Retry(
        total=retries,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update({'User-Agent': Config.USER_AGENT})
    return session


# ============================================================================
# 模块1：SQL注入扫描器
# ============================================================================

class SQLInjectionScanner:
    """
    SQL注入扫描器

    支持三种检测模式：
    - 基于错误的注入检测
    - 基于时间的盲注检测
    - 基于布尔的盲注检测
    """

    # SQL注入测试payload
    ERROR_PAYLOADS = [
        "'", '"', "')", '")', "'; --", '"; --', "' --", '" --',
        "' OR '1'='1", '" OR "1"="1', "' OR '1'='1' --",
        "' UNION SELECT NULL,NULL --", "1' AND '1'='1", "1 AND 1=1",
        "1' AND SLEEP(5)--", "admin'--", "admin' OR '1'='1'--",
        "' OR 1=1#", "1; SELECT 1--", "' OR ''='", "1) OR (1=1",
    ]

    # 基于错误的数据库特征字符串
    ERROR_SIGNATURES = {
        'MySQL': [
            r'SQL syntax.*MySQL', r'Warning.*mysql_', r'MySQLSyntaxErrorException',
            r'valid MySQL result', r'check the manual that corresponds to your MySQL',
            r'com\.mysql\.jdbc', r'sqlalchemy\.exc\.ProgrammingError',
        ],
        'PostgreSQL': [
            r'PostgreSQL.*ERROR', r'Warning.*\Wpg_', r'valid PostgreSQL result',
            r'Npgsql\.', r'PSQLException', r'org\.postgresql\.util',
            r'ERROR:  syntax error at or near',
        ],
        'Microsoft SQL Server': [
            r'Driver.* SQL[\-\_\ ]*Server', r'OLE DB.* SQL Server', r'\bSQL Server[^&lt;&quot;]+Driver',
            r'SQLServer', r'sqlserver', r'SQLSTATE.*SQL Server',
            r'Unclosed quotation mark after the character string',
        ],
        'Oracle': [
            r'\bORA-\d{4,5}', r'Oracle error', r'Oracle.*Driver',
            r'quoted string not properly terminated',
            r'java\.sql\.SQLException.*Oracle',
        ],
        'SQLite': [
            r'SQLite/JDBCDriver', r'SQLite\.Exception', r'sqlite3\.OperationalError',
            r'SQLITE_ERROR', r'sqlite\.OperationalError',
        ],
        'IBM DB2': [
            r'CLI Driver.*DB2', r'DB2 SQL error', r'\bdb2_\w+\(',
            r'SQLCODE=\d', r'SQLSTATE=',
        ],
    }

    # 布尔注入测试payload对
    BOOLEAN_PAYLOADS = [
        ("1 AND 1=1", "1 AND 1=2"),
        ("1' AND '1'='1", "1' AND '1'='2"),
        ("1\" AND \"1\"=\"1", "1\" AND \"1\"=\"2"),
        ("1) AND (1=1", "1) AND (1=2"),
        ("1 AND 1=1--", "1 AND 1=2--"),
    ]

    # 时间盲注payload
    TIME_PAYLOADS = [
        "1' AND SLEEP(5)-- -",
        "1\" AND SLEEP(5)-- -",
        "1 AND SLEEP(5)-- -",
        "1); WAITFOR DELAY '0:0:5'--",
        "1' AND pg_sleep(5)-- -",
        "1' OR SLEEP(5)-- -",
        "1' AND (SELECT * FROM (SELECT(SLEEP(5)))a)-- -",
    ]

    def __init__(self, target_url: str, params: Dict = None, **kwargs):
        """
        初始化SQL注入扫描器

        Args:
            target_url: 目标URL
            params: 要测试的参数
            kwargs: 额外配置（timeout/cookies/headers等）
        """
        self.target_url = target_url
        self.params = params or {}
        self.timeout = kwargs.get('timeout', Config.TIMEOUT)
        self.cookies = kwargs.get('cookies', {})
        self.headers = kwargs.get('headers', {})
        self.session = create_session()
        self.results = []
        self.vulnerable = False

        # 解析URL参数
        parsed = urlparse(target_url)
        if parsed.query:
            existing_params = parse_qs(parsed.query)
            for k, v in existing_params.items():
                if k not in self.params:
                    self.params[k] = v[0] if isinstance(v, list) else v

    def _send_request(self, method: str, url: str, data: Dict = None) -> Optional[requests.Response]:
        """
        发送HTTP请求

        Args:
            method: HTTP方法
            url: 目标URL
            data: POST数据

        Returns:
            requests.Response对象或None
        """
        try:
            if method.upper() == 'GET':
                response = self.session.get(
                    url, params=data, timeout=self.timeout,
                    cookies=self.cookies, headers=self.headers,
                    allow_redirects=False, verify=False
                )
            else:
                response = self.session.post(
                    url, data=data, timeout=self.timeout,
                    cookies=self.cookies, headers=self.headers,
                    allow_redirects=False, verify=False
                )
            return response
        except requests.RequestException as e:
            return None

    def detect_error_based(self) -> List[Dict]:
        """
        基于错误的SQL注入检测

        通过注入特殊字符触发数据库错误，从响应内容中匹配数据库特征字符串。

        Returns:
            发现的漏洞列表
        """
        print_info("开始基于错误的SQL注入检测...")
        findings = []

        for param_name, param_value in self.params.items():
            for payload in self.ERROR_PAYLOADS:
                test_params = self.params.copy()
                test_params[param_name] = str(param_value) + payload

                # 构造测试URL
                test_url = self.target_url.split('?')[0]
                response = self._send_request('GET', test_url, test_params)

                if response is None:
                    continue

                response_text = response.text

                # 检查是否包含数据库错误特征
                for db_type, signatures in self.ERROR_SIGNATURES.items():
                    for sig in signatures:
                        if re.search(sig, response_text, re.IGNORECASE):
                            finding = {
                                'type': 'SQL注入 - 基于错误',
                                'parameter': param_name,
                                'payload': f"{param_value}{payload}",
                                'db_type': db_type,
                                'evidence': sig,
                                'url': response.url,
                            }
                            findings.append(finding)
                            print_vuln(f"发现SQL注入漏洞 - 参数: {param_name}, "
                                       f"数据库: {db_type}, Payload: {param_value}{payload}")
                            self.vulnerable = True
                            break
                    if self.vulnerable:
                        break
                if self.vulnerable:
                    break

        if not findings:
            print_info("基于错误的SQL注入检测完成，未发现漏洞")
        return findings

    def detect_time_based(self) -> List[Dict]:
        """
        基于时间的盲注检测

        通过注入SLEEP/WAITFOR等延迟函数，根据响应时间判断是否存在注入。

        Returns:
            发现的漏洞列表
        """
        print_info("开始基于时间的盲注检测...")
        findings = []

        # 延迟阈值（秒）
        delay_threshold = 4

        for param_name, param_value in self.params.items():
            for payload in self.TIME_PAYLOADS:
                test_params = self.params.copy()
                test_params[param_name] = str(param_value) + payload

                test_url = self.target_url.split('?')[0]

                # 先发送正常请求获取基准时间
                normal_params = self.params.copy()
                start_time = time.time()
                self._send_request('GET', test_url, normal_params)
                normal_time = time.time() - start_time

                # 发送带延迟的payload
                start_time = time.time()
                response = self._send_request('GET', test_url, test_params)
                elapsed_time = time.time() - start_time

                if elapsed_time > normal_time + delay_threshold:
                    finding = {
                        'type': 'SQL注入 - 基于时间',
                        'parameter': param_name,
                        'payload': f"{param_value}{payload}",
                        'normal_time': f"{normal_time:.2f}s",
                        'delay_time': f"{elapsed_time:.2f}s",
                        'url': test_url,
                    }
                    findings.append(finding)
                    print_vuln(f"发现时间盲注漏洞 - 参数: {param_name}, "
                               f"正常响应: {normal_time:.2f}s, "
                               f"延迟响应: {elapsed_time:.2f}s")
                    self.vulnerable = True
                    break

        if not findings:
            print_info("基于时间的盲注检测完成，未发现漏洞")
        return findings

    def detect_boolean_based(self) -> List[Dict]:
        """
        基于布尔的盲注检测

        通过注入布尔条件（AND 1=1 vs AND 1=2）比较响应差异来判断注入点。

        Returns:
            发现的漏洞列表
        """
        print_info("开始基于布尔的盲注检测...")
        findings = []

        for param_name, param_value in self.params.items():
            for true_payload, false_payload in self.BOOLEAN_PAYLOADS:
                test_url = self.target_url.split('?')[0]

                # 发送TRUE条件请求
                true_params = self.params.copy()
                true_params[param_name] = str(param_value) + " " + true_payload
                true_response = self._send_request('GET', test_url, true_params)

                # 发送FALSE条件请求
                false_params = self.params.copy()
                false_params[param_name] = str(param_value) + " " + false_payload
                false_response = self._send_request('GET', test_url, false_params)

                if true_response is None or false_response is None:
                    continue

                # 比较响应差异
                true_len = len(true_response.text)
                false_len = len(false_response.text)
                true_hash = hashlib.md5(true_response.text.encode()).hexdigest()
                false_hash = hashlib.md5(false_response.text.encode()).hexdigest()

                # TRUE条件与原始响应相似，FALSE条件不同 -> 可能存在注入
                if true_hash != false_hash and abs(true_len - false_len) > 0:
                    # 二次确认：原始响应应与TRUE条件接近
                    original_params = self.params.copy()
                    original_response = self._send_request('GET', test_url, original_params)
                    if original_response:
                        orig_hash = hashlib.md5(original_response.text.encode()).hexdigest()
                        if orig_hash == true_hash or abs(len(original_response.text) - true_len) < 10:
                            finding = {
                                'type': 'SQL注入 - 基于布尔',
                                'parameter': param_name,
                                'true_payload': f"{param_value} {true_payload}",
                                'false_payload': f"{param_value} {false_payload}",
                                'true_response_length': true_len,
                                'false_response_length': false_len,
                                'url': test_url,
                            }
                            findings.append(finding)
                            print_vuln(f"发现布尔盲注漏洞 - 参数: {param_name}, "
                                       f"TRUE响应: {true_len}字节, "
                                       f"FALSE响应: {false_len}字节")
                            self.vulnerable = True
                            break

        if not findings:
            print_info("基于布尔的盲注检测完成，未发现漏洞")
        return findings

    def scan(self) -> Dict:
        """
        执行完整的SQL注入扫描

        Returns:
            扫描结果字典
        """
        print_info(f"开始SQL注入扫描: {self.target_url}")
        print_info(f"检测参数: {list(self.params.keys())}")

        all_findings = []
        all_findings.extend(self.detect_error_based())
        all_findings.extend(self.detect_boolean_based())
        all_findings.extend(self.detect_time_based())

        result = {
            'target': self.target_url,
            'parameters_tested': list(self.params.keys()),
            'vulnerable': self.vulnerable,
            'findings_count': len(all_findings),
            'findings': all_findings,
            'timestamp': datetime.now().isoformat(),
        }

        self.results = result
        return result


# ============================================================================
# 模块2：XSS检测器
# ============================================================================

class XSSDetector:
    """
    XSS（跨站脚本）检测器

    支持检测：
    - 反射型XSS
    - 存储型XSS
    - DOM型XSS
    """

    # XSS测试payload
    REFLECTED_PAYLOADS = [
        '<script>alert(1)</script>',
        '<ScRiPt>alert(1)</ScRiPt>',
        '<img src=x onerror=alert(1)>',
        '<svg onload=alert(1)>',
        '<body onload=alert(1)>',
        '"><script>alert(1)</script>',
        "'><script>alert(1)</script>",
        '<iframe src="javascript:alert(1)">',
        '<details open ontoggle=alert(1)>',
        '<marquee onstart=alert(1)>',
        'javascript:alert(1)',
        '<input onfocus=alert(1) autofocus>',
        '<select onfocus=alert(1) autofocus>',
        '<textarea onfocus=alert(1) autofocus>',
        '<keygen onfocus=alert(1) autofocus>',
        '<video src=x onerror=alert(1)>',
        '<audio src=x onerror=alert(1)>',
        '<a href="javascript:alert(1)">click</a>',
        '"><img src=x onerror=alert(1)>',
        "<script>document.write('XSS_MARKER')</script>",
    ]

    # DOM XSS关键JavaScript函数（可能存在DOM XSS漏洞）
    DOM_SINKS = [
        'document.write', 'document.writeln', 'document.domain',
        'eval(', 'setTimeout(', 'setInterval(',
        'innerHTML', 'outerHTML', 'insertAdjacentHTML',
        'document.location', 'location.href', 'location.hash',
        'location.search', 'location.replace',
        'element.src', 'element.href', 'element.action',
        'document.cookie', 'window.name', 'postMessage',
        'execCommand(', 'window.open(',
    ]

    # DOM XSS常见source
    DOM_SOURCES = [
        'location.hash', 'location.search', 'location.href',
        'location.pathname', 'document.URL', 'document.URLUnencoded',
        'document.referrer', 'document.cookie', 'window.name',
        'postMessage', 'localStorage', 'sessionStorage',
    ]

    # 存储型XSS常用测试标记
    STORED_MARKER_PREFIX = "XSS_TEST_"

    def __init__(self, target_url: str, params: Dict = None, **kwargs):
        """
        初始化XSS检测器

        Args:
            target_url: 目标URL
            params: 要测试的参数
            kwargs: 额外配置
        """
        self.target_url = target_url
        self.params = params or {}
        self.timeout = kwargs.get('timeout', Config.TIMEOUT)
        self.cookies = kwargs.get('cookies', {})
        self.headers = kwargs.get('headers', {})
        self.session = create_session()
        self.vulnerable = False
        self.results = []

        # 解析URL参数
        parsed = urlparse(target_url)
        if parsed.query:
            existing_params = parse_qs(parsed.query)
            for k, v in existing_params.items():
                if k not in self.params:
                    self.params[k] = v[0] if isinstance(v, list) else v

    def detect_reflected_xss(self) -> List[Dict]:
        """
        检测反射型XSS

        通过在参数中注入XSS payload，检查响应中是否原样返回payload。

        Returns:
            发现的漏洞列表
        """
        print_info("开始反射型XSS检测...")
        findings = []

        for param_name, param_value in self.params.items():
            for payload in self.REFLECTED_PAYLOADS:
                test_params = self.params.copy()
                test_params[param_name] = payload

                test_url = self.target_url.split('?')[0]
                try:
                    response = self.session.get(
                        test_url, params=test_params,
                        timeout=self.timeout, cookies=self.cookies,
                        headers=self.headers, allow_redirects=False, verify=False
                    )
                except requests.RequestException:
                    continue

                if response is None:
                    continue

                # 检查payload是否被反射到响应中
                if payload in response.text:
                    # 进一步检查HTML上下文
                    escaped = self._check_escaping(payload, response.text)
                    if not escaped:
                        finding = {
                            'type': 'XSS - 反射型',
                            'parameter': param_name,
                            'payload': payload,
                            'evidence': 'Payload在响应中未转义',
                            'url': response.url,
                            'response_snippet': self._extract_context(payload, response.text),
                        }
                        findings.append(finding)
                        print_vuln(f"发现反射型XSS - 参数: {param_name}, Payload: {payload}")
                        self.vulnerable = True
                        break

        if not findings:
            print_info("反射型XSS检测完成，未发现漏洞")
        return findings

    def detect_stored_xss(self, post_url: str = None, view_url: str = None,
                          param_name: str = None) -> List[Dict]:
        """
        检测存储型XSS

        在输入处提交XSS payload，然后在输出页面检查payload是否被存储和执行。

        Args:
            post_url: 提交数据的URL
            view_url: 查看数据的URL
            param_name: 要注入的参数名

        Returns:
            发现的漏洞列表
        """
        print_info("开始存储型XSS检测...")
        findings = []

        post_url = post_url or self.target_url
        view_url = view_url or self.target_url

        # 生成唯一标记
        marker_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        marker = f"{self.STORED_MARKER_PREFIX}{marker_id}"

        payloads = [
            f'<script>alert("{marker}")</script>',
            f'<img src=x onerror=alert("{marker}")>',
            f'<svg onload=alert("{marker}")>',
        ]

        for payload in payloads:
            try:
                # 提交payload
                post_data = {param_name or 'comment': payload} if param_name else {'comment': payload}
                self.session.post(
                    post_url, data=post_data,
                    timeout=self.timeout, cookies=self.cookies,
                    headers=self.headers, verify=False
                )

                # 访问查看页面
                response = self.session.get(
                    view_url, timeout=self.timeout,
                    cookies=self.cookies, headers=self.headers, verify=False
                )

                if marker in response.text:
                    escaped = self._check_escaping(payload, response.text)
                    if not escaped:
                        finding = {
                            'type': 'XSS - 存储型',
                            'parameter': param_name or 'comment',
                            'payload': payload,
                            'marker': marker,
                            'evidence': 'Payload被存储且未转义',
                            'post_url': post_url,
                            'view_url': view_url,
                        }
                        findings.append(finding)
                        print_vuln(f"发现存储型XSS - 标记: {marker}, Payload: {payload}")
                        self.vulnerable = True
                        break
            except requests.RequestException:
                continue

        if not findings:
            print_info("存储型XSS检测完成，未发现漏洞")
        return findings

    def detect_dom_xss(self) -> List[Dict]:
        """
        检测DOM型XSS

        通过分析JavaScript代码中是否存在危险的DOM操作（source -> sink）。

        Returns:
            发现的漏洞列表
        """
        print_info("开始DOM型XSS检测...")
        findings = []

        try:
            response = self.session.get(
                self.target_url, timeout=self.timeout,
                cookies=self.cookies, headers=self.headers, verify=False
            )
            page_content = response.text
        except requests.RequestException:
            print_error("无法获取目标页面")
            return findings

        # 提取所有<script>标签内容
        script_pattern = re.compile(r'<script[^>]*>(.*?)</script>', re.DOTALL | re.IGNORECASE)
        scripts = script_pattern.findall(page_content)

        # 提取外部JS文件
        src_pattern = re.compile(r'<script[^>]+src=["\']([^"\']+)["\']', re.IGNORECASE)
        external_scripts = src_pattern.findall(page_content)

        # 检查每个脚本中的source->sink模式
        all_scripts = scripts[:]
        for ext_src in external_scripts:
            ext_url = urljoin(self.target_url, ext_src)
            try:
                ext_response = self.session.get(ext_url, timeout=self.timeout, verify=False)
                all_scripts.append(ext_response.text)
            except requests.RequestException:
                continue

        for script_content in all_scripts:
            # 查找DOM source
            found_sources = []
            for source in self.DOM_SOURCES:
                if source in script_content:
                    found_sources.append(source)

            # 查找DOM sink
            found_sinks = []
            for sink in self.DOM_SINKS:
                if sink in script_content:
                    found_sinks.append(sink)

            # 如果同时存在source和sink，可能存在DOM XSS
            if found_sources and found_sinks:
                # 提取相关代码片段
                snippet = self._extract_code_snippet(script_content, found_sources + found_sinks)
                finding = {
                    'type': 'XSS - DOM型',
                    'sources': found_sources,
                    'sinks': found_sinks,
                    'evidence': '检测到危险的DOM source->sink数据流',
                    'url': self.target_url,
                    'code_snippet': snippet,
                }
                findings.append(finding)
                print_vuln(f"发现潜在DOM型XSS - Sources: {found_sources}, Sinks: {found_sinks}")
                self.vulnerable = True

        if not findings:
            print_info("DOM型XSS检测完成，未发现漏洞")
        return findings

    def _check_escaping(self, payload: str, response_text: str) -> bool:
        """
        检查payload是否被转义

        Args:
            payload: 原始payload
            response_text: HTTP响应文本

        Returns:
            True表示已转义，False表示未转义
        """
        # 检查HTML实体编码
        escaped_chars = ['&lt;', '&gt;', '&quot;', '&#x27;', '&#39;', '&amp;']
        for char in escaped_chars:
            if char in response_text and char not in payload:
                # payload中的< >等被转义了
                raw_payload_check = payload.replace('<', '&lt;').replace('>', '&gt;')
                if raw_payload_check in response_text:
                    return True
        return False

    def _extract_context(self, payload: str, text: str, context_len: int = 100) -> str:
        """提取payload在响应中的上下文"""
        idx = text.find(payload)
        if idx == -1:
            return ""
        start = max(0, idx - context_len)
        end = min(len(text), idx + len(payload) + context_len)
        return text[start:end]

    def _extract_code_snippet(self, content: str, keywords: List[str], max_len: int = 200) -> str:
        """从脚本内容中提取关键代码片段"""
        for keyword in keywords:
            idx = content.find(keyword)
            if idx != -1:
                start = max(0, idx - 50)
                end = min(len(content), idx + max_len)
                return content[start:end]
        return ""

    def scan(self) -> Dict:
        """执行完整的XSS扫描"""
        print_info(f"开始XSS扫描: {self.target_url}")
        print_info(f"检测参数: {list(self.params.keys())}")

        all_findings = []
        all_findings.extend(self.detect_reflected_xss())
        all_findings.extend(self.detect_dom_xss())

        result = {
            'target': self.target_url,
            'parameters_tested': list(self.params.keys()),
            'vulnerable': self.vulnerable,
            'findings_count': len(all_findings),
            'findings': all_findings,
            'timestamp': datetime.now().isoformat(),
        }

        self.results = result
        return result


# ============================================================================
# 模块3：目录暴力破解工具
# ============================================================================

class DirectoryBruteForcer:
    """
    目录暴力破解工具

    通过字典文件对目标网站进行目录和文件枚举。
    支持自定义扩展名、并发请求和状态码过滤。
    """

    # 内置常用路径字典
    BUILTIN_WORDLIST = [
        'admin', 'administrator', 'login', 'wp-admin', 'wp-login.php',
        'admin.php', 'admin/', 'admin/login', 'backend', 'dashboard',
        'config', 'configuration', 'backup', 'backup.zip', 'backup.sql',
        'db', 'database', 'sql', '.git', '.git/config', '.svn',
        '.env', '.htaccess', '.htpasswd', 'web.config', 'robots.txt',
        'sitemap.xml', 'crossdomain.xml', 'server-status', 'phpinfo.php',
        'info.php', 'test.php', 'phpmyadmin', 'phpmyadmin/', 'pma',
        'phpmyadmin/index.php', 'swagger', 'swagger-ui', 'api-docs',
        'api/', 'api/v1/', 'api/v2/', 'graphql', 'graphiql',
        'uploads', 'upload', 'files', 'temp', 'tmp', 'logs', 'log',
        'debug', 'console', 'shell', 'cmd', 'exec', 'system',
        'install', 'setup', 'old', 'new', 'beta', 'test', 'dev',
        'development', 'staging', 'production', 'src', 'source',
        'include', 'includes', 'lib', 'libs', 'vendor', 'node_modules',
        'composer.json', 'package.json', 'Dockerfile', 'docker-compose.yml',
        'flag.txt', 'flag', 'secret', 'key', 'token', 'password',
        'passwd', 'shadow', 'id_rsa', '.ssh', '.ssh/id_rsa',
        'WEB-INF/web.xml', 'META-INF/', 'META-INF/MANIFEST.MF',
    ]

    # 常见文件扩展名
    COMMON_EXTENSIONS = ['', '.php', '.html', '.htm', '.asp', '.aspx',
                         '.jsp', '.txt', '.bak', '.old', '.zip', '.tar.gz',
                         '.sql', '.xml', '.json', '.js', '.css']

    def __init__(self, target_url: str, wordlist_path: str = None, **kwargs):
        """
        初始化目录暴力破解工具

        Args:
            target_url: 目标URL
            wordlist_path: 字典文件路径
            kwargs: 额外配置
        """
        self.target_url = target_url.rstrip('/')
        self.wordlist = self._load_wordlist(wordlist_path)
        self.extensions = kwargs.get('extensions', [''])
        self.threads = kwargs.get('threads', Config.MAX_THREADS)
        self.timeout = kwargs.get('timeout', Config.TIMEOUT)
        self.cookies = kwargs.get('cookies', {})
        self.headers = kwargs.get('headers', {})
        self.session = create_session()
        self.results = []
        self.found_paths = []

        # 禁用SSL警告
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def _load_wordlist(self, wordlist_path: str) -> List[str]:
        """加载字典文件"""
        if wordlist_path and os.path.exists(wordlist_path):
            with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
                words = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            print_info(f"已加载字典文件: {wordlist_path} ({len(words)}条)")
            return words
        else:
            print_info("使用内置字典")
            return self.BUILTIN_WORDLIST

    def _check_path(self, path: str) -> Optional[Dict]:
        """
        检查单个路径

        Args:
            path: 要检查的路径

        Returns:
            结果字典或None
        """
        url = f"{self.target_url}/{path.lstrip('/')}"
        try:
            response = self.session.get(
                url, timeout=self.timeout,
                cookies=self.cookies, headers=self.headers,
                allow_redirects=False, verify=False
            )

            status_code = response.status_code
            content_length = len(response.content)

            # 过滤掉404
            if status_code == 404:
                return None

            result = {
                'url': url,
                'status_code': status_code,
                'status_text': Config.STATUS_CODES.get(status_code, '未知'),
                'content_length': content_length,
                'path': path,
            }

            # 特殊状态码处理
            if status_code in [200, 301, 302, 401, 403]:
                if status_code == 200:
                    print_success(f"[{status_code}] {url} ({content_length} bytes)")
                elif status_code in [301, 302]:
                    location = response.headers.get('Location', '')
                    print_success(f"[{status_code}] {url} -> {location}")
                    result['redirect_to'] = location
                elif status_code == 401:
                    print_warning(f"[{status_code}] {url} (需要认证)")
                elif status_code == 403:
                    print_warning(f"[{status_code}] {url} (禁止访问)")

                return result
            return None

        except requests.RequestException:
            return None
        except Exception as e:
            return None

    def brute_force(self) -> List[Dict]:
        """
        执行目录暴力破解

        Returns:
            发现的路径列表
        """
        print_info(f"开始目录暴力破解: {self.target_url}")
        print_info(f"字典大小: {len(self.wordlist)}, 扩展名: {self.extensions}")
        print_info(f"线程数: {self.threads}")

        # 生成所有要测试的路径
        all_paths = []
        for word in self.wordlist:
            for ext in self.extensions:
                path = f"{word}{ext}"
                all_paths.append(path)

        print_info(f"总测试路径数: {len(all_paths)}")

        # 使用线程池并发请求
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {executor.submit(self._check_path, path): path for path in all_paths}

            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        self.found_paths.append(result)
                except Exception:
                    continue

        # 按状态码排序
        self.found_paths.sort(key=lambda x: x['status_code'])

        print_info(f"扫描完成，发现 {len(self.found_paths)} 个路径")

        self.results = self.found_paths
        return self.found_paths

    def scan(self) -> Dict:
        """执行扫描"""
        found = self.brute_force()
        return {
            'target': self.target_url,
            'wordlist_size': len(self.wordlist),
            'paths_found': len(found),
            'findings': found,
            'timestamp': datetime.now().isoformat(),
        }


# ============================================================================
# 模块4：HTTP头安全检查器
# ============================================================================

class HTTPHeaderChecker:
    """
    HTTP头安全检查器

    检查HTTP响应头的安全配置，包括：
    - Content-Security-Policy (CSP)
    - Strict-Transport-Security (HSTS)
    - X-Frame-Options
    - X-Content-Type-Options
    - X-XSS-Protection
    - Referrer-Policy
    - Permissions-Policy
    """

    # 需要检查的安全头
    SECURITY_HEADERS = {
        'Content-Security-Policy': {
            'description': '内容安全策略 - 防止XSS和数据注入攻击',
            'severity': '高危',
            'recommendation': '设置严格的CSP策略，限制脚本/样式/图片等资源来源',
        },
        'Strict-Transport-Security': {
            'description': 'HTTP严格传输安全 - 强制使用HTTPS',
            'severity': '高危',
            'recommendation': '设置HSTS头: max-age=63072000; includeSubDomains; preload',
        },
        'X-Frame-Options': {
            'description': '防止点击劫持 - 控制页面是否可被iframe嵌入',
            'severity': '中危',
            'recommendation': '设置为 DENY 或 SAMEORIGIN',
        },
        'X-Content-Type-Options': {
            'description': '防止MIME类型嗅探',
            'severity': '中危',
            'recommendation': '设置为 nosniff',
        },
        'X-XSS-Protection': {
            'description': '浏览器XSS过滤器（已弃用但仍建议检查）',
            'severity': '低危',
            'recommendation': '设置为 1; mode=block（注: 现代浏览器已使用CSP替代）',
        },
        'Referrer-Policy': {
            'description': '控制Referrer信息泄露',
            'severity': '中危',
            'recommendation': '设置为 no-referrer 或 strict-origin-when-cross-origin',
        },
        'Permissions-Policy': {
            'description': '功能策略 - 控制浏览器功能访问权限',
            'severity': '低危',
            'recommendation': '设置Permissions-Policy限制摄像头/麦克风/地理位置等',
        },
        'Cross-Origin-Opener-Policy': {
            'description': '跨域 opener 策略 - 防止跨域窗口操作',
            'severity': '低危',
            'recommendation': '设置为 same-origin',
        },
        'Cross-Origin-Embedder-Policy': {
            'description': '跨域嵌入策略',
            'severity': '低危',
            'recommendation': '设置为 require-corp',
        },
        'Cross-Origin-Resource-Policy': {
            'description': '跨域资源策略',
            'severity': '低危',
            'recommendation': '设置为 same-origin 或 same-site',
        },
    }

    # 信息泄露头
    INFO_LEAK_HEADERS = {
        'Server': '服务器版本信息泄露',
        'X-Powered-By': '后端技术栈信息泄露',
        'X-AspNet-Version': 'ASP.NET版本信息泄露',
        'X-Generator': '生成器信息泄露',
        'Via': '代理服务器信息泄露',
        'X-Cache': '缓存服务器信息泄露',
        'X-Runtime': '运行时信息泄露',
        'X-Version': '版本信息泄露',
        'Set-Cookie': 'Cookie安全属性检查',
    }

    def __init__(self, target_url: str, **kwargs):
        """初始化HTTP头安全检查器"""
        self.target_url = target_url
        self.timeout = kwargs.get('timeout', Config.TIMEOUT)
        self.session = create_session()
        self.results = []

    def check_security_headers(self, headers: Dict) -> List[Dict]:
        """
        检查安全响应头

        Args:
            headers: HTTP响应头字典

        Returns:
            检查结果列表
        """
        findings = []

        # 检查缺失的安全头
        for header, info in self.SECURITY_HEADERS.items():
            if header.lower() not in {k.lower() for k in headers.keys()}:
                finding = {
                    'type': '缺失安全头',
                    'header': header,
                    'description': info['description'],
                    'severity': info['severity'],
                    'recommendation': info['recommendation'],
                    'status': '缺失',
                }
                findings.append(finding)
                print_warning(f"缺失安全头: {header} ({info['severity']}) - {info['description']}")
            else:
                # 头存在，检查其值是否安全
                header_value = self._get_header_ci(headers, header)
                finding = {
                    'type': '安全头配置',
                    'header': header,
                    'value': header_value,
                    'description': info['description'],
                    'severity': '信息',
                    'status': '已设置',
                    'recommendation': info['recommendation'],
                }
                findings.append(finding)
                print_success(f"安全头已设置: {header}")

        return findings

    def check_info_leak_headers(self, headers: Dict) -> List[Dict]:
        """
        检查信息泄露头

        Args:
            headers: HTTP响应头字典

        Returns:
            检查结果列表
        """
        findings = []

        for header, description in self.INFO_LEAK_HEADERS.items():
            header_value = self._get_header_ci(headers, header)
            if header_value:
                if header == 'Set-Cookie':
                    # 检查Cookie安全属性
                    cookie_findings = self._check_cookie_security(header_value)
                    findings.extend(cookie_findings)
                else:
                    finding = {
                        'type': '信息泄露',
                        'header': header,
                        'value': header_value,
                        'description': description,
                        'severity': '低危',
                        'recommendation': f'隐藏或移除 {header} 响应头',
                    }
                    findings.append(finding)
                    print_warning(f"信息泄露: {header} = {header_value}")

        return findings

    def _check_cookie_security(self, cookie_header: str) -> List[Dict]:
        """
        检查Cookie安全属性

        Args:
            cookie_header: Set-Cookie头值

        Returns:
            检查结果列表
        """
        findings = []
        issues = []

        if 'HttpOnly' not in cookie_header:
            issues.append('缺少HttpOnly属性（可能导致XSS窃取Cookie）')
        if 'Secure' not in cookie_header:
            issues.append('缺少Secure属性（Cookie可能通过HTTP传输）')
        if 'SameSite' not in cookie_header:
            issues.append('缺少SameSite属性（可能导致CSRF攻击）')

        if issues:
            finding = {
                'type': 'Cookie安全问题',
                'header': 'Set-Cookie',
                'value': cookie_header[:100] + '...' if len(cookie_header) > 100 else cookie_header,
                'issues': issues,
                'severity': '中危',
                'recommendation': '设置HttpOnly、Secure和SameSite=Strict/Lax属性',
            }
            findings.append(finding)
            for issue in issues:
                print_warning(f"Cookie安全问题: {issue}")

        return findings

    def _get_header_ci(self, headers: Dict, name: str) -> Optional[str]:
        """不区分大小写获取HTTP头"""
        for key, value in headers.items():
            if key.lower() == name.lower():
                return value
        return None

    def check_csp_details(self, csp_value: str) -> Dict:
        """
        深入分析CSP策略配置

        Args:
            csp_value: CSP头值

        Returns:
            CSP分析结果
        """
        analysis = {
            'csp_value': csp_value,
            'directives': {},
            'issues': [],
            'score': 0,
        }

        directives = csp_value.split(';')
        for directive in directives:
            parts = directive.strip().split()
            if not parts:
                continue
            dir_name = parts[0]
            dir_values = parts[1:]
            analysis['directives'][dir_name] = dir_values

            # 检查危险配置
            if dir_name == 'default-src' and '*' in dir_values:
                analysis['issues'].append(f"default-src使用通配符'*'，CSP几乎无效")
            if 'unsafe-inline' in dir_values:
                analysis['issues'].append(f"{dir_name}包含'unsafe-inline'，削弱了XSS防护")
            if 'unsafe-eval' in dir_values:
                analysis['issues'].append(f"{dir_name}包含'unsafe-eval'，允许eval()使用")

        # CSP评分
        score = 100
        for issue in analysis['issues']:
            score -= 20
        analysis['score'] = max(0, score)

        if analysis['issues']:
            for issue in analysis['issues']:
                print_warning(f"CSP问题: {issue}")
        else:
            print_success("CSP策略配置良好")

        return analysis

    def scan(self) -> Dict:
        """执行HTTP头安全扫描"""
        print_info(f"开始HTTP头安全检查: {self.target_url}")

        try:
            response = self.session.get(
                self.target_url, timeout=self.timeout,
                allow_redirects=True, verify=False
            )
            headers = dict(response.headers)
        except requests.RequestException as e:
            print_error(f"请求失败: {e}")
            return {'error': str(e)}

        # 检查安全头
        security_findings = self.check_security_headers(headers)

        # 检查信息泄露
        leak_findings = self.check_info_leak_headers(headers)

        # 深入分析CSP
        csp_value = self._get_header_ci(headers, 'Content-Security-Policy')
        csp_analysis = self.check_csp_details(csp_value) if csp_value else None

        all_findings = security_findings + leak_findings

        result = {
            'target': self.target_url,
            'total_headers': len(headers),
            'security_headers_present': sum(1 for f in security_findings if f['status'] == '已设置'),
            'security_headers_missing': sum(1 for f in security_findings if f['status'] == '缺失'),
            'info_leak_headers': len(leak_findings),
            'csp_analysis': csp_analysis,
            'findings': all_findings,
            'timestamp': datetime.now().isoformat(),
        }

        self.results = result
        return result


# ============================================================================
# 模块5：子域名枚举器
# ============================================================================

class SubdomainEnumerator:
    """
    子域名枚举器

    通过多种数据源和技术进行子域名发现：
    - DNS暴力枚举
    - 搜索引擎查询
    - 证书透明度日志
    - 在线API服务
    """

    # 常用子域名字典
    COMMON_SUBDOMAINS = [
        'www', 'mail', 'ftp', 'localhost', 'smtp', 'pop', 'imap',
        'blog', 'forum', 'shop', 'store', 'api', 'dev', 'staging',
        'test', 'qa', 'prod', 'admin', 'portal', 'secure', 'vpn',
        'remote', 'gateway', 'cloud', 'app', 'mobile', 'm',
        'static', 'assets', 'cdn', 'images', 'img', 'media',
        'docs', 'wiki', 'help', 'support', 'status', 'monitor',
        'git', 'svn', 'gitlab', 'jenkins', 'ci', 'build',
        'db', 'database', 'redis', 'elastic', 'search',
        'auth', 'sso', 'oauth', 'identity', 'account',
        'ns1', 'ns2', 'ns3', 'ns4', 'dns1', 'dns2',
        'webmail', 'owa', 'exchange', 'autodiscover',
        'internal', 'intranet', 'extranet', 'office',
        'backup', 'bak', 'old', 'new', 'beta', 'alpha',
        'demo', 'sandbox', 'preview', 'stage', 'uat',
        'analytics', 'tracking', 'log', 'logs', 'syslog',
        'mx', 'mx1', 'mx2', 'relay', 'postoffice',
        'cpanel', 'plesk', 'webmin', 'directadmin',
        'en', 'cn', 'jp', 'us', 'eu', 'asia',
        'news', 'press', 'info', 'about', 'contact',
        'download', 'dl', 'files', 'upload', 'uploads',
        'secure', 'ssl', 'tls', 'cert', 'ca',
        'proxy', 'lb', 'haproxy', 'nginx', 'varnish',
        'grafana', 'prometheus', 'kibana', 'dashboard',
    ]

    # 证书透明度日志API
    CT_APIS = [
        'https://crt.sh/?q=%25.{domain}&output=json',
        'https://api.certspotter.com/v1/issuances?domain={domain}&include_subdomains=true&expand=dns_names',
    ]

    def __init__(self, domain: str, **kwargs):
        """
        初始化子域名枚举器

        Args:
            domain: 目标域名
            kwargs: 额外配置
        """
        self.domain = domain
        self.threads = kwargs.get('threads', Config.MAX_THREADS)
        self.timeout = kwargs.get('timeout', Config.TIMEOUT)
        self.session = create_session()
        self.results = set()
        self.resolved = {}

    def dns_brute_force(self, wordlist: List[str] = None) -> List[str]:
        """
        DNS暴力枚举子域名

        Args:
            wordlist: 子域名字典

        Returns:
            发现的子域名列表
        """
        print_info("开始DNS暴力枚举...")
        wordlist = wordlist or self.COMMON_SUBDOMAINS
        found = []

        def resolve_subdomain(subdomain):
            full_domain = f"{subdomain}.{self.domain}"
            try:
                ip = socket.gethostbyname(full_domain)
                return (full_domain, ip)
            except socket.gaierror:
                return None
            except Exception:
                return None

        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {executor.submit(resolve_subdomain, word): word for word in wordlist}
            for future in as_completed(futures):
                result = future.result()
                if result:
                    full_domain, ip = result
                    found.append(full_domain)
                    self.resolved[full_domain] = ip
                    print_success(f"发现子域名: {full_domain} -> {ip}")

        print_info(f"DNS暴力枚举完成，发现 {len(found)} 个子域名")
        return found

    def query_certificate_transparency(self) -> List[str]:
        """
        通过证书透明度日志发现子域名

        Returns:
            发现的子域名列表
        """
        print_info("查询证书透明度日志...")
        found = []

        for api_url in self.CT_APIS:
            url = api_url.format(domain=self.domain)
            try:
                response = self.session.get(url, timeout=self.timeout)
                if response.status_code == 200:
                    data = response.json()

                    # crt.sh 格式
                    if isinstance(data, list):
                        for entry in data:
                            names = entry.get('name_value', '').split('\n')
                            for name in names:
                                name = name.strip().lower()
                                if name and self.domain in name:
                                    # 过滤通配符
                                    name = name.replace('*.', '')
                                    found.append(name)
                                    self.results.add(name)

                    # CertSpotter 格式
                    elif isinstance(data, dict) and 'results' in data:
                        for entry in data['results']:
                            dns_names = entry.get('dns_names', [])
                            for name in dns_names:
                                if self.domain in name:
                                    found.append(name)
                                    self.results.add(name)
                    break
            except Exception as e:
                continue

        # 去重
        found = list(set(found))
        for name in found:
            print_success(f"证书透明度发现: {name}")

        print_info(f"证书透明度查询完成，发现 {len(found)} 个子域名")
        return found

    def query_search_engines(self) -> List[str]:
        """
        通过搜索引擎发现子域名

        Returns:
            发现的子域名列表
        """
        print_info("查询搜索引擎...")
        found = set()

        # 构造搜索查询
        queries = [
            f'site:*.{self.domain}',
            f'site:*.{self.domain} -site:www.{self.domain}',
        ]

        # 模拟搜索引擎查询（实际使用时需对接搜索引擎API）
        # 这里使用Bing搜索作为示例
        for query in queries:
            try:
                # 实际实现需要对接搜索引擎API或使用爬虫
                # 这里仅作为框架示例
                search_url = f"https://www.bing.com/search?q={quote(query)}"
                response = self.session.get(search_url, timeout=self.timeout)
                if response.status_code == 200:
                    # 从搜索结果中提取子域名
                    subdomain_pattern = re.compile(
                        rf'([\w\-]+\.)*{re.escape(self.domain)}',
                        re.IGNORECASE
                    )
                    matches = subdomain_pattern.findall(response.text)
                    for match in matches:
                        full_match = match[0] if isinstance(match, tuple) else match
                        if full_match:
                            subdomain = f"{full_match}{self.domain}".strip('.')
                            found.add(subdomain)
            except Exception:
                continue

        for name in found:
            print_success(f"搜索引擎发现: {name}")
            self.results.add(name)

        print_info(f"搜索引擎查询完成，发现 {len(found)} 个子域名")
        return list(found)

    def enumerate(self, methods: List[str] = None) -> Dict:
        """
        执行完整的子域名枚举

        Args:
            methods: 使用的方法列表（dns/ct/search）

        Returns:
            枚举结果字典
        """
        methods = methods or ['dns', 'ct', 'search']
        print_info(f"开始子域名枚举: {self.domain}")

        all_found = set()

        if 'dns' in methods:
            dns_results = self.dns_brute_force()
            all_found.update(dns_results)

        if 'ct' in methods:
            ct_results = self.query_certificate_transparency()
            all_found.update(ct_results)

        if 'search' in methods:
            search_results = self.query_search_engines()
            all_found.update(search_results)

        # 排序
        all_found = sorted(all_found)

        # 尝试解析所有发现的子域名
        for subdomain in all_found:
            if subdomain not in self.resolved:
                try:
                    ip = socket.gethostbyname(subdomain)
                    self.resolved[subdomain] = ip
                except socket.gaierror:
                    self.resolved[subdomain] = '无法解析'

        result = {
            'domain': self.domain,
            'methods_used': methods,
            'subdomains_found': len(all_found),
            'subdomains': all_found,
            'resolved': self.resolved,
            'timestamp': datetime.now().isoformat(),
        }

        self.results = result
        return result


# ============================================================================
# 模块6：多线程端口扫描器
# ============================================================================

class PortScanner:
    """
    多线程端口扫描器

    支持TCP连接扫描、常见服务识别和并发扫描。
    """

    # 常用端口与服务映射
    COMMON_PORTS = {
        21: 'FTP',
        22: 'SSH',
        23: 'Telnet',
        25: 'SMTP',
        53: 'DNS',
        80: 'HTTP',
        110: 'POP3',
        143: 'IMAP',
        443: 'HTTPS',
        445: 'SMB',
        993: 'IMAPS',
        995: 'POP3S',
        1433: 'MSSQL',
        1521: 'Oracle',
        3306: 'MySQL',
        3389: 'RDP',
        5432: 'PostgreSQL',
        5900: 'VNC',
        6379: 'Redis',
        8080: 'HTTP-Alt',
        8443: 'HTTPS-Alt',
        9200: 'Elasticsearch',
        11211: 'Memcached',
        27017: 'MongoDB',
    }

    def __init__(self, host: str, **kwargs):
        """
        初始化端口扫描器

        Args:
            host: 目标主机
            kwargs: 额外配置
        """
        self.host = host
        self.threads = kwargs.get('threads', Config.MAX_THREADS)
        self.timeout = kwargs.get('timeout', 2)
        self.results = []
        self.open_ports = []
        self.scan_lock = threading.Lock()

    def parse_port_range(self, port_str: str) -> List[int]:
        """
        解析端口范围字符串

        Args:
            port_str: 端口范围字符串，如 "80,443,1000-2000"

        Returns:
            端口列表
        """
        ports = []
        for part in port_str.split(','):
            part = part.strip()
            if '-' in part:
                start, end = part.split('-')
                ports.extend(range(int(start), int(end) + 1))
            else:
                ports.append(int(part))
        return sorted(set(ports))

    def scan_port(self, port: int) -> Optional[Dict]:
        """
        扫描单个端口

        Args:
            port: 端口号

        Returns:
            扫描结果字典或None
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.host, port))

            if result == 0:
                # 端口开放，尝试获取服务信息
                service = self.COMMON_PORTS.get(port, '未知')
                banner = self._grab_banner(port)

                scan_result = {
                    'port': port,
                    'state': 'open',
                    'service': service,
                    'banner': banner,
                }

                with self.scan_lock:
                    self.open_ports.append(scan_result)

                print_success(f"端口 {port}/tcp 开放 - {service}"
                              + (f" ({banner})" if banner else ""))

                sock.close()
                return scan_result
            else:
                sock.close()
                return None

        except socket.gaierror:
            print_error(f"无法解析主机: {self.host}")
            return None
        except Exception as e:
            return None

    def _grab_banner(self, port: int) -> str:
        """
        获取服务Banner

        Args:
            port: 端口号

        Returns:
            Banner字符串
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((self.host, port))

            # HTTP端口发送HTTP请求
            if port in [80, 8080, 8443, 443]:
                sock.send(b"GET / HTTP/1.0\r\nHost: " +
                          self.host.encode() + b"\r\n\r\n")
            else:
                # 其他端口等待Banner
                pass

            banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
            sock.close()

            # 截取第一行
            if banner:
                return banner.split('\n')[0][:100]
            return ""

        except Exception:
            return ""

    def scan(self, ports: List[int] = None, port_range: str = None) -> Dict:
        """
        执行端口扫描

        Args:
            ports: 端口列表
            port_range: 端口范围字符串

        Returns:
            扫描结果字典
        """
        if port_range:
            ports = self.parse_port_range(port_range)
        elif ports is None:
            ports = list(self.COMMON_PORTS.keys())

        print_info(f"开始端口扫描: {self.host}")
        print_info(f"扫描端口数: {len(ports)}, 线程数: {self.threads}")

        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {executor.submit(self.scan_port, port): port for port in ports}
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception:
                    continue

        self.open_ports.sort(key=lambda x: x['port'])
        print_info(f"端口扫描完成，发现 {len(self.open_ports)} 个开放端口")

        result = {
            'host': self.host,
            'ports_scanned': len(ports),
            'open_ports': len(self.open_ports),
            'findings': self.open_ports,
            'timestamp': datetime.now().isoformat(),
        }

        self.results = result
        return result


# ============================================================================
# 模块7：Web漏洞报告生成器
# ============================================================================

class VulnerabilityReportGenerator:
    """
    Web漏洞报告生成器

    将各扫描工具的结果汇总，生成结构化的漏洞报告。
    支持JSON和HTML格式输出。
    """

    # 漏洞严重程度分级
    SEVERITY_LEVELS = {
        '严重': 4,
        '高危': 3,
        '中危': 2,
        '低危': 1,
        '信息': 0,
    }

    def __init__(self, target_url: str = None):
        """
        初始化报告生成器

        Args:
            target_url: 目标URL
        """
        self.target_url = target_url
        self.scan_results = []
        self.report_data = {}

    def add_scan_result(self, tool_name: str, result: Dict):
        """
        添加扫描结果

        Args:
            tool_name: 工具名称
            result: 扫描结果字典
        """
        self.scan_results.append({
            'tool': tool_name,
            'result': result,
            'timestamp': datetime.now().isoformat(),
        })

    def run_all_scans(self, target_url: str) -> Dict:
        """
        运行所有扫描工具并生成综合报告

        Args:
            target_url: 目标URL

        Returns:
            综合报告字典
        """
        self.target_url = target_url
        print_info(f"开始对 {target_url} 执行综合安全扫描")

        # 1. SQL注入扫描
        try:
            parsed = urlparse(target_url)
            params = {}
            if parsed.query:
                params = parse_qs(parsed.query)
                params = {k: v[0] if isinstance(v, list) else v for k, v in params.items()}
            else:
                params = {'id': '1'}

            sqli_scanner = SQLInjectionScanner(target_url, params)
            sqli_result = sqli_scanner.scan()
            self.add_scan_result('SQL注入扫描器', sqli_result)
        except Exception as e:
            print_error(f"SQL注入扫描失败: {e}")

        # 2. XSS扫描
        try:
            xss_detector = XSSDetector(target_url, params if 'params' in locals() else {'q': 'test'})
            xss_result = xss_detector.scan()
            self.add_scan_result('XSS检测器', xss_result)
        except Exception as e:
            print_error(f"XSS扫描失败: {e}")

        # 3. HTTP头安全检查
        try:
            header_checker = HTTPHeaderChecker(target_url)
            header_result = header_checker.scan()
            self.add_scan_result('HTTP头安全检查器', header_result)
        except Exception as e:
            print_error(f"HTTP头检查失败: {e}")

        # 4. 目录暴力破解（使用内置字典）
        try:
            dir_brute = DirectoryBruteForcer(target_url)
            dir_result = dir_brute.scan()
            self.add_scan_result('目录暴力破解', dir_result)
        except Exception as e:
            print_error(f"目录扫描失败: {e}")

        # 生成综合报告
        return self.generate_report()

    def generate_report(self) -> Dict:
        """
        生成漏洞报告

        Returns:
            报告字典
        """
        total_vulns = 0
        severity_count = {level: 0 for level in self.SEVERITY_LEVELS}
        all_findings = []

        for scan in self.scan_results:
            result = scan['result']
            findings = result.get('findings', [])

            for finding in findings:
                severity = finding.get('severity', '信息')
                if severity in severity_count:
                    severity_count[severity] += 1
                total_vulns += 1
                all_findings.append({
                    'tool': scan['tool'],
                    'finding': finding,
                    'timestamp': scan['timestamp'],
                })

        report = {
            'target': self.target_url,
            'scan_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'tools_used': [s['tool'] for s in self.scan_results],
            'total_vulnerabilities': total_vulns,
            'severity_summary': severity_count,
            'all_findings': all_findings,
            'scan_results': self.scan_results,
        }

        self.report_data = report
        return report

    def save_json_report(self, filepath: str = None) -> str:
        """
        保存JSON格式报告

        Args:
            filepath: 文件路径

        Returns:
            保存的文件路径
        """
        if not self.report_data:
            self.generate_report()

        if filepath is None:
            filepath = f"vulnerability_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.report_data, f, ensure_ascii=False, indent=2)

        print_success(f"JSON报告已保存: {filepath}")
        return filepath

    def save_html_report(self, filepath: str = None) -> str:
        """
        保存HTML格式报告

        Args:
            filepath: 文件路径

        Returns:
            保存的文件路径
        """
        if not self.report_data:
            self.generate_report()

        if filepath is None:
            filepath = f"vulnerability_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

        report = self.report_data

        # 生成HTML报告
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web安全扫描报告 - {report.get('target', '未知目标')}</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
        .summary {{ display: flex; gap: 15px; margin: 20px 0; flex-wrap: wrap; }}
        .card {{ background: white; padding: 15px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); min-width: 150px; }}
        .card h3 {{ margin: 0 0 10px 0; color: #2c3e50; }}
        .severity-critical {{ color: #c0392b; font-weight: bold; }}
        .severity-high {{ color: #e67e22; font-weight: bold; }}
        .severity-medium {{ color: #f39c12; font-weight: bold; }}
        .severity-low {{ color: #27ae60; font-weight: bold; }}
        .finding {{ background: white; margin: 10px 0; padding: 15px; border-radius: 5px; border-left: 4px solid #3498db; }}
        .finding h4 {{ margin: 0 0 10px 0; color: #2c3e50; }}
        .finding pre {{ background: #f8f9fa; padding: 10px; border-radius: 3px; overflow-x: auto; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; background: white; }}
        th, td {{ padding: 10px; border: 1px solid #ddd; text-align: left; }}
        th {{ background: #2c3e50; color: white; }}
        tr:nth-child(even) {{ background: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Web安全扫描报告</h1>
        <p>目标: {report.get('target', '未知')}</p>
        <p>扫描时间: {report.get('scan_date', '未知')}</p>
    </div>

    <div class="summary">
        <div class="card">
            <h3>总漏洞数</h3>
            <span style="font-size: 24px; font-weight: bold;">{report.get('total_vulnerabilities', 0)}</span>
        </div>
        <div class="card">
            <h3>严重</h3>
            <span class="severity-critical">{report.get('severity_summary', {}).get('严重', 0)}</span>
        </div>
        <div class="card">
            <h3>高危</h3>
            <span class="severity-high">{report.get('severity_summary', {}).get('高危', 0)}</span>
        </div>
        <div class="card">
            <h3>中危</h3>
            <span class="severity-medium">{report.get('severity_summary', {}).get('中危', 0)}</span>
        </div>
        <div class="card">
            <h3>低危</h3>
            <span class="severity-low">{report.get('severity_summary', {}).get('低危', 0)}</span>
        </div>
    </div>

    <h2>使用的扫描工具</h2>
    <ul>
"""

        for tool in report.get('tools_used', []):
            html += f"        <li>{tool}</li>\n"

        html += "    </ul>\n\n    <h2>详细发现</h2>\n"

        for finding in report.get('all_findings', []):
            f = finding.get('finding', {})
            html += f"""    <div class="finding">
        <h4>[{finding.get('tool', '')}] {f.get('type', '未知类型')}</h4>
        <pre>{json.dumps(f, ensure_ascii=False, indent=2)}</pre>
    </div>
"""

        html += """</body>
</html>"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)

        print_success(f"HTML报告已保存: {filepath}")
        return filepath

    def print_summary(self):
        """打印报告摘要"""
        if not self.report_data:
            self.generate_report()

        report = self.report_data
        print("\n" + "=" * 60)
        print(f"  Web安全扫描报告 - {report.get('target', '未知')}")
        print("=" * 60)
        print(f"  扫描时间: {report.get('scan_date', '未知')}")
        print(f"  使用工具: {', '.join(report.get('tools_used', []))}")
        print(f"  总漏洞数: {report.get('total_vulnerabilities', 0)}")
        print("-" * 60)
        for severity, count in report.get('severity_summary', {}).items():
            if count > 0:
                print(f"  {severity}: {count}")
        print("=" * 60 + "\n")


# ============================================================================
# 主函数与CLI接口
# ============================================================================

def main():
    """
    主函数 - CLI入口

    提供命令行界面，支持各工具的独立调用和综合扫描。
    """
    parser = argparse.ArgumentParser(
        description='Python Web安全工具集 - 综合Web安全扫描工具包',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s sqli -u "http://example.com/page?id=1"
  %(prog)s xss -u "http://example.com/search?q=test"
  %(prog)s dirbrute -u "http://example.com/" -w wordlist.txt
  %(prog)s headers -u "http://example.com/"
  %(prog)s subdomain -d example.com
  %(prog)s portscan -H 127.0.0.1 -p 1-1000
  %(prog)s report -u "http://example.com/" --all

免责声明: 仅用于授权的安全测试！
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # SQL注入扫描
    sqli_parser = subparsers.add_parser('sqli', help='SQL注入扫描')
    sqli_parser.add_argument('-u', '--url', required=True, help='目标URL')
    sqli_parser.add_argument('-p', '--params', help='参数（格式: key=value,key2=value2）')
    sqli_parser.add_argument('--timeout', type=int, default=Config.TIMEOUT, help='超时秒数')

    # XSS扫描
    xss_parser = subparsers.add_parser('xss', help='XSS检测')
    xss_parser.add_argument('-u', '--url', required=True, help='目标URL')
    xss_parser.add_argument('-p', '--params', help='参数（格式: key=value,key2=value2）')
    xss_parser.add_argument('--stored', action='store_true', help='检测存储型XSS')
    xss_parser.add_argument('--post-url', help='存储型XSS提交URL')
    xss_parser.add_argument('--view-url', help='存储型XSS查看URL')

    # 目录暴力破解
    dir_parser = subparsers.add_parser('dirbrute', help='目录暴力破解')
    dir_parser.add_argument('-u', '--url', required=True, help='目标URL')
    dir_parser.add_argument('-w', '--wordlist', help='字典文件路径')
    dir_parser.add_argument('-e', '--extensions', nargs='+', default=[''],
                            help='文件扩展名（如 .php .html）')
    dir_parser.add_argument('-t', '--threads', type=int, default=Config.MAX_THREADS, help='线程数')

    # HTTP头检查
    header_parser = subparsers.add_parser('headers', help='HTTP头安全检查')
    header_parser.add_argument('-u', '--url', required=True, help='目标URL')

    # 子域名枚举
    sub_parser = subparsers.add_parser('subdomain', help='子域名枚举')
    sub_parser.add_argument('-d', '--domain', required=True, help='目标域名')
    sub_parser.add_argument('-m', '--methods', nargs='+', default=['dns', 'ct', 'search'],
                            choices=['dns', 'ct', 'search'], help='使用的方法')
    sub_parser.add_argument('-t', '--threads', type=int, default=Config.MAX_THREADS, help='线程数')

    # 端口扫描
    port_parser = subparsers.add_parser('portscan', help='端口扫描')
    port_parser.add_argument('-H', '--host', required=True, help='目标主机')
    port_parser.add_argument('-p', '--ports', default='1-1000', help='端口范围（如 80,443,1000-2000）')
    port_parser.add_argument('-t', '--threads', type=int, default=Config.MAX_THREADS, help='线程数')

    # 综合报告
    report_parser = subparsers.add_parser('report', help='生成综合安全报告')
    report_parser.add_argument('-u', '--url', required=True, help='目标URL')
    report_parser.add_argument('--all', action='store_true', help='运行所有扫描')
    report_parser.add_argument('--json', help='JSON报告输出路径')
    report_parser.add_argument('--html', help='HTML报告输出路径')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # 禁用SSL警告
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # 解析参数
    def parse_params(param_str):
        if not param_str:
            return {}
        params = {}
        for pair in param_str.split(','):
            if '=' in pair:
                k, v = pair.split('=', 1)
                params[k] = v
        return params

    # 执行对应命令
    if args.command == 'sqli':
        scanner = SQLInjectionScanner(args.url, parse_params(args.params), timeout=args.timeout)
        result = scanner.scan()
        print(f"\n扫描结果: {'存在漏洞' if result['vulnerable'] else '未发现漏洞'}, "
              f"共 {result['findings_count']} 个发现")

    elif args.command == 'xss':
        detector = XSSDetector(args.url, parse_params(args.params))
        if args.stored:
            detector.detect_stored_xss(args.post_url, args.view_url)
        result = detector.scan()
        print(f"\n扫描结果: {'存在漏洞' if result['vulnerable'] else '未发现漏洞'}, "
              f"共 {result['findings_count']} 个发现")

    elif args.command == 'dirbrute':
        brute = DirectoryBruteForcer(args.url, args.wordlist,
                                     extensions=args.extensions, threads=args.threads)
        result = brute.scan()
        print(f"\n发现 {result['paths_found']} 个路径")

    elif args.command == 'headers':
        checker = HTTPHeaderChecker(args.url)
        result = checker.scan()
        print(f"\n安全头检查: {result['security_headers_present']} 个已设置, "
              f"{result['security_headers_missing']} 个缺失, "
              f"{result['info_leak_headers']} 个信息泄露")

    elif args.command == 'subdomain':
        enumerator = SubdomainEnumerator(args.domain, threads=args.threads)
        result = enumerator.enumerate(args.methods)
        print(f"\n发现 {result['subdomains_found']} 个子域名")

    elif args.command == 'portscan':
        scanner = PortScanner(args.host, threads=args.threads)
        result = scanner.scan(port_range=args.ports)
        print(f"\n扫描完成: {result['ports_scanned']} 个端口, "
              f"{result['open_ports']} 个开放")

    elif args.command == 'report':
        generator = VulnerabilityReportGenerator(args.url)
        report = generator.run_all_scans(args.url)
        generator.print_summary()

        if args.json:
            generator.save_json_report(args.json)
        if args.html:
            generator.save_html_report(args.html)

        # 默认保存报告
        if not args.json and not args.html:
            generator.save_json_report()
            generator.save_html_report()

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
