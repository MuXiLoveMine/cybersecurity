# Python API安全测试脚本示例

以下脚本使用模拟数据和模拟API端点，仅用于安全学习和防御检测。

### 7.1 JWT安全检测脚本

```python
#!/usr/bin/env python3
"""
JWT安全检测工具
功能：分析JWT Token的安全配置
用途：API安全评估与自查
注意：使用模拟Token数据，不对真实系统测试
"""

import base64
import json
import hashlib
import hmac
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class JWTVulnerability:
    """JWT漏洞发现"""
    severity: str  # CRITICAL / HIGH / MEDIUM / LOW
    issue: str
    description: str
    recommendation: str


class JWTSecurityAnalyzer:
    """JWT安全分析器"""

    # 常见弱密钥（实际场景应使用更大的字典）
    COMMON_WEAK_KEYS = [
        "secret", "password", "123456", "admin", "key",
        "jwt_secret", "your-256-bit-secret", "supersecret",
        "changeme", "default", "test", "example",
    ]

    def __init__(self, token: str):
        self.token = token
        self.header: Dict = {}
        self.payload: Dict = {}
        self.signature: str = ""
        self.vulnerabilities: List[JWTVulnerability] = []
        self._parse()

    def _parse(self):
        """解析JWT Token"""
        parts = self.token.split('.')
        if len(parts) != 3:
            raise ValueError("Invalid JWT format")

        # Base64URL解码header和payload
        self.header = self._decode_base64url(parts[0])
        self.payload = self._decode_base64url(parts[1])
        self.signature = parts[2]

    @staticmethod
    def _decode_base64url(data: str) -> dict:
        """Base64URL解码"""
        padding = 4 - len(data) % 4
        if padding != 4:
            data += '=' * padding
        decoded = base64.urlsafe_b64decode(data)
        return json.loads(decoded)

    def analyze(self) -> List[JWTVulnerability]:
        """执行全面安全分析"""
        self._check_algorithm()
        self._check_expiration()
        self._check_sensitive_data()
        self._check_issuer_audience()
        self._check_weak_signature()
        return self.vulnerabilities

    def _check_algorithm(self):
        """检查签名算法安全性"""
        alg = self.header.get('alg', 'none')

        # none算法检查
        if alg.lower() == 'none':
            self.vulnerabilities.append(JWTVulnerability(
                severity="CRITICAL",
                issue="使用none算法",
                description=f"JWT使用 '{alg}' 算法，签名被完全移除，"
                            f"任何人都可以伪造Token",
                recommendation="使用HS256/RS256/ES256等安全算法"
            ))

        # 弱算法检查
        elif alg in ('HS256', 'HS384', 'HS512'):
            # 对称密钥算法需要检查密钥强度
            pass  # 在_weak_signature中检查

        # 推荐算法
        elif alg in ('RS256', 'RS384', 'RS512',
                      'ES256', 'ES384', 'ES512'):
            pass  # 非对称算法更安全

        # 未知算法
        else:
            self.vulnerabilities.append(JWTVulnerability(
                severity="HIGH",
                issue="未知签名算法",
                description=f"使用不常见的算法 '{alg}'",
                recommendation="使用标准算法RS256或ES256"
            ))

    def _check_expiration(self):
        """检查Token过期配置"""
        if 'exp' not in self.payload:
            self.vulnerabilities.append(JWTVulnerability(
                severity="HIGH",
                issue="无过期时间",
                description="JWT缺少exp声明，Token永不过期，"
                            "泄露后可被永久使用",
                recommendation="设置exp字段，Access Token建议15分钟过期"
            ))
        else:
            import time
            exp = self.payload['exp']
            now = int(time.time())
            remaining = exp - now
            if remaining > 86400:  # 超过24小时
                self.vulnerabilities.append(JWTVulnerability(
                    severity="MEDIUM",
                    issue="过期时间过长",
                    description=f"Token有效期剩余{remaining//3600}小时，"
                                f"时间过长增加泄露风险",
                    recommendation="Access Token有效期不超过15分钟"
                ))

    def _check_sensitive_data(self):
        """检查Payload中的敏感数据"""
        sensitive_keys = ['password', 'pwd', 'secret', 'key',
                         'token', 'credit_card', 'ssn', 'pin']
        for key in self.payload:
            for sensitive in sensitive_keys:
                if sensitive in key.lower():
                    self.vulnerabilities.append(JWTVulnerability(
                        severity="HIGH",
                        issue=f"Payload包含敏感字段: {key}",
                        description=f"JWT Payload中包含 '{key}' 字段，"
                                    f"Payload仅Base64编码未加密，"
                                    f"任何人可解码查看",
                        recommendation="不要在JWT中存储敏感数据，"
                                       f"仅存储用户标识"
                    ))

    def _check_issuer_audience(self):
        """检查Issuer和Audience"""
        if 'iss' not in self.payload:
            self.vulnerabilities.append(JWTVulnerability(
                severity="MEDIUM",
                issue="缺少iss声明",
                description="缺少issuer声明，无法验证Token来源",
                recommendation="设置iss字段标识签发方"
            ))

        if 'aud' not in self.payload:
            self.vulnerabilities.append(JWTVulnerability(
                severity="MEDIUM",
                issue="缺少aud声明",
                description="缺少audience声明，Token可被跨服务重用",
                recommendation="设置aud字段限制Token使用范围"
            ))

    def _check_weak_signature(self):
        """尝试弱密钥破解（仅用于安全测试）"""
        alg = self.header.get('alg', '')
        if not alg.startswith('HS'):
            return  # 仅对称算法可测试

        # 构建签名输入
        signing_input = self.token.rsplit('.', 1)[0]

        for key in self.COMMON_WEAK_KEYS:
            expected_sig = hmac.new(
                key.encode(),
                signing_input.encode(),
                getattr(hashlib, f'sha{alg[2:]}')
            ).digest()
            expected_b64 = base64.urlsafe_b64encode(
                expected_sig
            ).rstrip(b'=').decode()

            if hmac.compare_digest(expected_b64, self.signature):
                self.vulnerabilities.append(JWTVulnerability(
                    severity="CRITICAL",
                    issue=f"弱密钥可破解: '{key}'",
                    description=f"JWT签名密钥为常见弱密钥 '{key}'，"
                                f"可被轻易伪造",
                    recommendation="使用至少256位随机密钥"
                ))
                break

    def print_report(self):
        """打印安全报告"""
        print(f"\n{'='*60}")
        print(f"  JWT安全分析报告")
        print(f"{'='*60}\n")

        print(f"  Header:  {json.dumps(self.header, indent=4)}")
        print(f"  Payload: {json.dumps(self.payload, indent=4)}")
        print(f"  Signature: {self.signature[:20]}...")
        print()

        if not self.vulnerabilities:
            print("  [OK] 未发现明显安全问题。")
        else:
            severity_order = {"CRITICAL": 0, "HIGH": 1,
                              "MEDIUM": 2, "LOW": 3}
            self.vulnerabilities.sort(
                key=lambda v: severity_order.get(v.severity, 99))

            for i, vuln in enumerate(self.vulnerabilities, 1):
                icon = {"CRITICAL": "[!!!]", "HIGH": "[!!]",
                        "MEDIUM": "[!]", "LOW": "[i]"}[vuln.severity]
                print(f"  #{i} {icon} [{vuln.severity}] {vuln.issue}")
                print(f"     描述: {vuln.description}")
                print(f"     建议: {vuln.recommendation}")
                print()

        print(f"{'='*60}")


# 使用模拟Token进行演示
if __name__ == "__main__":
    print("=" * 60)
    print("  JWT安全检测工具 v1.0")
    print("  使用模拟Token数据 - 仅用于安全学习")
    print("=" * 60)

    # 模拟Token 1: 使用none算法（高危）
    mock_token_none = (
        base64.urlsafe_b64encode(
            json.dumps({"alg": "none", "typ": "JWT"}).encode()
        ).rstrip(b'=').decode()
        + "." +
        base64.urlsafe_b64encode(
            json.dumps({
                "sub": "1234567890",
                "name": "John Doe",
                "role": "admin",
                "password": "secret123",
                "iat": 1516239022
            }).encode()
        ).rstrip(b'=').decode()
        + "."
    )

    analyzer = JWTSecurityAnalyzer(mock_token_none)
    analyzer.analyze()
    analyzer.print_report()

    # 模拟Token 2: 使用弱密钥（高危）
    signing_input = (
        base64.urlsafe_b64encode(
            json.dumps({"alg": "HS256", "typ": "JWT"}).encode()
        ).rstrip(b'=').decode()
        + "." +
        base64.urlsafe_b64encode(
            json.dumps({"sub": "1234567890", "name": "Test"}).encode()
        ).rstrip(b'=').decode()
    )
    sig = hmac.new(b"secret", signing_input.encode(),
                   hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(sig).rstrip(b'=').decode()
    mock_token_weak = f"{signing_input}.{sig_b64}"

    analyzer2 = JWTSecurityAnalyzer(mock_token_weak)
    analyzer2.analyze()
    analyzer2.print_report()
```

### 7.2 API端点枚举脚本

```python
#!/usr/bin/env python3
"""
API端点枚举工具
功能：通过OpenAPI规范和路径模糊发现API端点
用途：API资产盘点与安全评估
注意：使用模拟端点数据，不对真实系统测试
"""

import json
from dataclasses import dataclass, field
from typing import List, Dict, Set


@dataclass
class APIEndpoint:
    """API端点信息"""
    method: str
    path: str
    requires_auth: bool = False
    parameters: List[str] = field(default_factory=list)
    description: str = ""


@dataclass
class EndpointFinding:
    """端点发现结果"""
    endpoint: APIEndpoint
    status_code: int
    accessible: bool
    security_note: str = ""


class APIEndpointEnumerator:
    """API端点枚举器"""

    # 常见API路径模式（模拟字典）
    COMMON_PATHS = [
        "/api/v1/users", "/api/v2/users", "/api/v1/admin",
        "/api/v1/auth/login", "/api/v1/auth/register",
        "/api/v1/auth/refresh", "/api/v1/auth/logout",
        "/api/v1/health", "/api/v1/status", "/api/v1/metrics",
        "/api/v1/debug", "/api/v1/config", "/api/v1/docs",
        "/api/v1/swagger.json", "/api/v1/openapi.json",
        "/api/v1/orders", "/api/v1/products", "/api/v1/payments",
        "/api/v1/internal/users", "/api/v1/internal/config",
        "/api/v1/staging/debug", "/api/v1/test/reset",
        "/api/v1/graphql", "/api/v1/upload", "/api/v1/export",
    ]

    HTTP_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']

    def __init__(self, base_url: str = "https://api.example.com"):
        self.base_url = base_url.rstrip('/')
        self.findings: List[EndpointFinding] = []
        self.openapi_spec: Dict = {}

    def parse_openapi(self, spec: dict):
        """解析OpenAPI规范文件"""
        self.openapi_spec = spec
        paths = spec.get('paths', {})
        for path, methods in paths.items():
            for method, details in methods.items():
                if method.upper() in self.HTTP_METHODS:
                    security = details.get('security', [])
                    params = [p['name'] for p in details.get('parameters', [])]
                    endpoint = APIEndpoint(
                        method=method.upper(),
                        path=path,
                        requires_auth=bool(security),
                        parameters=params,
                        description=details.get('summary', '')
                    )
                    self._simulate_access(endpoint)

    def enumerate_paths(self, paths: List[str] = None):
        """路径枚举发现"""
        paths = paths or self.COMMON_PATHS
        for path in paths:
            for method in self.HTTP_METHODS:
                endpoint = APIEndpoint(
                    method=method,
                    path=path,
                    requires_auth=False
                )
                self._simulate_access(endpoint)

    def _simulate_access(self, endpoint: APIEndpoint):
        """模拟访问端点（使用模拟数据）"""
        # 模拟响应状态码
        simulated_responses = self._get_simulated_response(endpoint)
        status_code, accessible, note = simulated_responses

        finding = EndpointFinding(
            endpoint=endpoint,
            status_code=status_code,
            accessible=accessible,
            security_note=note
        )
        self.findings.append(finding)

    def _get_simulated_response(self, endpoint: APIEndpoint) -> tuple:
        """返回模拟的响应状态码和安全备注"""
        # 模拟已知端点的响应
        known_endpoints = {
            ('GET', '/api/v1/health'): (200, True, "公开健康检查端点"),
            ('GET', '/api/v1/users'): (200, True, "需要认证 - 验证授权配置"),
            ('GET', '/api/v1/admin'): (403, False, "管理端点 - 需检查授权"),
            ('GET', '/api/v1/debug'): (200, True,
                "[!] 调试端点暴露 - 高危"),
            ('GET', '/api/v1/internal/config'): (200, True,
                "[!] 内部配置端点可访问 - 高危"),
            ('GET', '/api/v1/swagger.json'): (200, True,
                "[!] OpenAPI文档暴露 - 可能泄露API结构"),
            ('GET', '/api/v1/test/reset'): (200, True,
                "[!!!] 测试端点暴露 - 严重"),
            ('GET', '/api/v1/metrics'): (200, True,
                "[!] 指标端点暴露 - 可能泄露内部信息"),
            ('POST', '/api/v1/auth/login'): (200, True, "登录端点"),
        }

        key = (endpoint.method, endpoint.path)
        if key in known_endpoints:
            return known_endpoints[key] + (None,)[:0][:1]  # 返回三元组
        # 模拟未找到
        return (404, False, "")

    def analyze_security(self) -> List[Dict]:
        """分析端点安全状况"""
        security_issues = []

        for finding in self.findings:
            if not finding.accessible:
                continue

            # 检查未认证端点
            if not finding.endpoint.requires_auth and \
               finding.status_code == 200:
                # 排除健康检查等公开端点
                if '/health' not in finding.endpoint.path and \
                   '/auth/login' not in finding.endpoint.path:
                    security_issues.append({
                        'severity': 'HIGH',
                        'issue': f"未认证端点可访问: "
                                 f"{finding.endpoint.method} "
                                 f"{finding.endpoint.path}",
                        'note': finding.security_note,
                        'recommendation': "添加认证要求或限制网络访问"
                    })

            # 检查敏感端点
            sensitive_patterns = ['admin', 'debug', 'internal',
                                 'test', 'config', 'metrics']
            for pattern in sensitive_patterns:
                if pattern in finding.endpoint.path.lower():
                    security_issues.append({
                        'severity': 'CRITICAL'
                        if pattern in ('debug', 'test', 'internal')
                        else 'HIGH',
                        'issue': f"敏感端点暴露: "
                                 f"{finding.endpoint.method} "
                                 f"{finding.endpoint.path}",
                        'note': finding.security_note,
                        'recommendation': f"移除或限制'{pattern}'相关端点"
                    })
                    break

        return security_issues

    def print_report(self):
        """打印枚举报告"""
        print(f"\n{'='*70}")
        print(f"  API端点枚举报告")
        print(f"  目标: {self.base_url}")
        print(f"{'='*70}\n")

        accessible = [f for f in self.findings if f.accessible]
        blocked = [f for f in self.findings if not f.accessible]

        print(f"  发现端点统计:")
        print(f"    可访问: {len(accessible)}")
        print(f"    不可访问(404): {len(blocked)}")
        print(f"    总计探测: {len(self.findings)}")
        print()

        if accessible:
            print(f"{'='*70}")
            print(f"  可访问端点列表:")
            print(f"{'='*70}\n")
            for finding in accessible:
                auth_tag = "[AUTH]" if finding.endpoint.requires_auth \
                           else "[NO-AUTH]"
                print(f"  {finding.endpoint.method:7s} "
                      f"{finding.endpoint.path:40s} "
                      f"{finding.status_code} {auth_tag}")
                if finding.security_note:
                    print(f"          → {finding.security_note}")
            print()

        issues = self.analyze_security()
        if issues:
            print(f"{'='*70}")
            print(f"  安全问题:")
            print(f"{'='*70}\n")
            for issue in issues:
                icon = {"CRITICAL": "[!!!]", "HIGH": "[!!]",
                        "MEDIUM": "[!]", "LOW": "[i]"}.get(
                    issue['severity'], '[?]')
                print(f"  {icon} [{issue['severity']}] {issue['issue']}")
                if issue['note']:
                    print(f"           {issue['note']}")
                print(f"           建议: {issue['recommendation']}")
                print()

        print(f"{'='*70}")


if __name__ == "__main__":
    print("=" * 70)
    print("  API端点枚举工具 v1.0")
    print("  使用模拟数据 - 仅用于安全学习")
    print("=" * 70)

    enumerator = APIEndpointEnumerator("https://api.example.com")

    # 路径枚举
    enumerator.enumerate_paths()

    # 模拟OpenAPI解析
    mock_openapi = {
        "openapi": "3.0.3",
        "paths": {
            "/api/v2/users": {
                "get": {
                    "summary": "获取用户列表",
                    "security": [{"bearerAuth": []}],
                    "parameters": [
                        {"name": "page", "in": "query"},
                        {"name": "page_size", "in": "query"}
                    ]
                }
            }
        }
    }
    enumerator.parse_openapi(mock_openapi)

    enumerator.print_report()
```

### 7.3 BOLA漏洞检测脚本

```python
#!/usr/bin/env python3
"""
BOLA (Broken Object Level Authorization) 漏洞检测脚本
功能：检测API端点是否存在水平越权漏洞
原理：使用用户A的Token尝试访问用户B的资源
注意：使用模拟API，不对真实系统测试
"""

import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class Severity(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


@dataclass
class BOLAFinding:
    """BOLA漏洞发现"""
    severity: Severity
    endpoint: str
    method: str
    description: str
    evidence: str
    recommendation: str


class BOLADetector:
    """BOLA漏洞检测器"""

    def __init__(self):
        self.findings: List[BOLAFinding] = []

    def detect_idor(self, endpoint_template: str,
                    user_a_token: str, user_b_id: str,
                    response_status: int, response_body: str) -> bool:
        """
        检测IDOR/BOLA漏洞
        endpoint_template: 含{ID}占位符的端点模板
        user_a_token: 用户A的认证Token
        user_b_id: 用户B的资源ID
        response_status: 模拟响应状态码
        response_body: 模拟响应体
        """
        endpoint = endpoint_template.replace("{ID}", str(user_b_id))

        # 如果用户A用A的Token能访问B的资源 → BOLA
        if response_status == 200:
            # 检查响应中是否包含属于用户B的数据
            try:
                data = json.loads(response_body) if response_body else {}
            except json.JSONDecodeError:
                data = {}

            # 判断是否返回了其他用户的数据
            returned_user_id = data.get('user_id') or data.get('userId')
            if returned_user_id and str(returned_user_id) == str(user_b_id):
                self.findings.append(BOLAFinding(
                    severity=Severity.CRITICAL,
                    endpoint=endpoint,
                    method="GET",
                    description=f"用户A的Token可访问用户B(ID={user_b_id})"
                                f"的资源，返回了用户B的私有数据",
                    evidence=f"Status: {response_status}, "
                              f"Response: {response_body[:100]}...",
                    recommendation="在查询资源时增加user_id归属校验: "
                                   "WHERE id = ? AND user_id = current_user_id"
                ))
                return True

        return False

    def detect_batch_idor(self, endpoint_template: str,
                          user_a_token: str,
                          target_ids: List[str],
                          simulate_responses: Dict[str, tuple]) -> List[str]:
        """批量检测IDOR - 枚举多个资源ID"""
        vulnerable_ids = []

        for target_id in target_ids:
            endpoint = endpoint_template.replace("{ID}", target_id)
            # 从模拟响应中获取结果
            if target_id in simulate_responses:
                status, body = simulate_responses[target_id]
                if self.detect_idor(endpoint, user_a_token,
                                     target_id, status, body):
                    vulnerable_ids.append(target_id)

        return vulnerable_ids

    def detect_method_tampering(self, endpoint: str,
                                user_a_token: str,
                                responses: Dict[str, tuple]) -> List[str]:
        """检测HTTP方法篡改导致的越权"""
        vulnerable_methods = []

        for method in ['GET', 'PUT', 'PATCH', 'DELETE']:
            if method in responses:
                status, body = responses[method]
                # 用户A可以修改/删除用户B的资源
                if method in ('PUT', 'PATCH', 'DELETE') and status in (200, 204):
                    self.findings.append(BOLAFinding(
                        severity=Severity.CRITICAL,
                        endpoint=endpoint,
                        method=method,
                        description=f"用户A可通过{method}方法操作用户B的资源",
                        evidence=f"Status: {status}",
                        recommendation=f"在{method}处理中增加归属校验"
                    ))
                    vulnerable_methods.append(method)

        return vulnerable_methods

    def print_report(self):
        """打印BOLA检测报告"""
        print(f"\n{'='*70}")
        print(f"  BOLA漏洞检测报告")
        print(f"{'='*70}\n")

        if not self.findings:
            print("  [OK] 未检测到BOLA漏洞。")
            print("  所有测试端点均正确验证了资源归属。")
            print(f"\n{'='*70}")
            return

        severity_order = {Severity.CRITICAL: 0, Severity.HIGH: 1,
                         Severity.MEDIUM: 2, Severity.LOW: 3}
        self.findings.sort(key=lambda f: severity_order.get(f.severity, 99))

        stats = {}
        for f in self.findings:
            stats[f.severity.value] = stats.get(f.severity.value, 0) + 1

        print(f"  发现统计: {dict(stats)}")
        print(f"{'='*70}\n")

        for i, finding in enumerate(self.findings, 1):
            icon = {Severity.CRITICAL: "[!!!]", Severity.HIGH: "[!!]",
                    Severity.MEDIUM: "[!]", Severity.LOW: "[i]",
                    Severity.INFO: "[i]"}.get(finding.severity, "[?]")
            print(f"  #{i} {icon} [{finding.severity.value}]")
            print(f"     端点: {finding.method} {finding.endpoint}")
            print(f"     描述: {finding.description}")
            print(f"     证据: {finding.evidence}")
            print(f"     建议: {finding.recommendation}")
            print()

        print(f"{'='*70}")
        print(f"  防御建议汇总:")
        print(f"{'='*70}")
        print("""
  1. 所有资源查询必须包含归属校验:
     SELECT * FROM resource WHERE id = ? AND owner_id = current_user_id

  2. 使用UUID替代自增ID增加枚举难度

  3. 实现集中式授权中间件，避免每个端点单独实现

  4. 使用ABAC(基于属性的访问控制)实现细粒度授权

  5. 定期运行BOLA自动化检测脚本
""")


# 模拟API响应数据
MOCK_API_RESPONSES = {
    # 用户A尝试访问订单（模拟返回其他用户订单数据 → BOLA）
    "order_5001": (200, '{"id": 5001, "user_id": 123, "total": 99.99}'),
    "order_5002": (200, '{"id": 5002, "user_id": 456, "total": 199.99}'),
    "order_5003": (200, '{"id": 5003, "user_id": 789, "total": 299.99}'),
    "order_5004": (403, '{"error": "Forbidden"}'),  # 安全的端点
    "order_5005": (404, '{"error": "Not Found"}'),
}

# 模拟方法篡改响应
MOCK_METHOD_RESPONSES = {
    "GET":    (200, '{"id": 5001, "user_id": 456}'),
    "PUT":    (200, '{"status": "updated"}'),       # 越权修改成功
    "DELETE": (204, ''),                             # 越权删除成功
}


if __name__ == "__main__":
    print("=" * 70)
    print("  BOLA漏洞检测工具 v1.0")
    print("  使用模拟API数据 - 仅用于安全学习")
    print("=" * 70)

    detector = BOLADetector()

    # 模拟场景: 用户A(token_A)尝试访问用户B的订单
    user_a_token = "mock_token_user_A"
    target_order_ids = ["5001", "5002", "5003", "5004", "5005"]

    print(f"\n  场景1: IDOR检测 - 枚举订单ID")
    print(f"  用户A Token: {user_a_token[:20]}...")
    print(f"  目标订单ID: {target_order_ids}")

    vulnerable = detector.detect_batch_idor(
        endpoint_template="/api/v2/orders/{ID}",
        user_a_token=user_a_token,
        target_ids=target_order_ids,
        simulate_responses=MOCK_API_RESPONSES
    )
    if vulnerable:
        print(f"  [!] 发现 {len(vulnerable)} 个可越权访问的订单ID")

    # 场景2: HTTP方法篡改
    print(f"\n  场景2: HTTP方法篡改检测")
    detector.detect_method_tampering(
        endpoint="/api/v2/orders/5001",
        user_a_token=user_a_token,
        responses=MOCK_METHOD_RESPONSES
    )

    # 输出报告
    detector.print_report()
```

---

---

## 📋 内容审核与补充建议

> 针对「Python API安全测试脚本示例」部分的内容审核结果：

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 📖 参考资料
- ⚠️ 缺少参考资料/延伸阅读

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客
