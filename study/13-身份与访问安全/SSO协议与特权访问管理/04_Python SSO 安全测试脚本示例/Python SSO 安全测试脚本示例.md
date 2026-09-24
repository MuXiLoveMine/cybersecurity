# Python SSO 安全测试脚本示例

### 4.1 JWT 安全检测脚本

```python
"""
JWT 安全检测脚本
检测项：弱签名算法、密钥泄露、claims 验证缺失、敏感信息泄露
依赖: pip install pyjwt cryptography requests
"""

import jwt
import json
import base64
import requests
from datetime import datetime


class JWTSafetyChecker:
    def __init__(self, token):
        self.token = token
        self.header = None
        self.payload = None
        self._decode_unsafe()

    def _decode_unsafe(self):
        """不验证签名地解码（仅用于安全检查）"""
        try:
            parts = self.token.split('.')
            self.header = json.loads(base64.urlsafe_b64decode(parts[0] + '=='))
            self.payload = json.loads(base64.urlsafe_b64decode(parts[1] + '=='))
        except Exception as e:
            print(f"[!] Failed to decode JWT: {e}")

    def check_algorithm(self):
        """检查签名算法安全性"""
        alg = self.header.get('alg', 'none')
        risks = []
        if alg.lower() == 'none':
            risks.append(('CRITICAL', 'alg=none，无签名，可伪造任意内容'))
        if alg.lower() == 'hs256':
            risks.append(('WARNING', 'HS256 对称算法，若密钥泄露可伪造 token'))
        if alg.lower() in ('rs256', 'es256'):
            risks.append(('INFO', f'{alg} 非对称算法，安全性较好'))
        return risks

    def check_alg_confusion(self, public_key):
        """检测 alg 混淆攻击（RS256→HS256）"""
        try:
            # 尝试用公钥作为 HMAC 密钥验证
            jwt.decode(self.token, key=public_key, algorithms=['HS256'])
            return [('CRITICAL', 'alg 混淆攻击成功！RS256→HS256 可伪造 token')]
        except jwt.InvalidSignatureError:
            return [('OK', 'alg 混淆攻击不可行')]
        except Exception:
            return [('OK', 'alg 混淆攻击不可行')]

    def check_claims(self):
        """检查关键 claims 是否存在且合理"""
        risks = []
        required = ['iss', 'sub', 'aud', 'exp', 'iat']
        for claim in required:
            if claim not in self.payload:
                risks.append(('WARNING', f'缺少 {claim} claim'))

        exp = self.payload.get('exp')
        if exp:
            if exp > datetime.now().timestamp() + 86400:
                risks.append(('WARNING', 'exp 过长（>24h），增加 token 泄露风险窗口'))
            if exp < datetime.now().timestamp():
                risks.append(('INFO', 'token 已过期'))
        return risks

    def check_sensitive_data(self):
        """检查是否包含敏感数据"""
        sensitive_keys = ['password', 'secret', 'ssn', 'credit_card', 'api_key']
        risks = []
        for key, value in self.payload.items():
            if any(s in key.lower() for s in sensitive_keys):
                risks.append(('CRITICAL', f'Payload 包含敏感字段: {key}'))
        return risks

    def try_default_secrets(self):
        """尝试常见弱密钥"""
        common_secrets = [
            'secret', 'password', '123456', 'jwt_secret',
            'your-256-bit-secret', 'default', 'changeme'
        ]
        risks = []
        alg = self.header.get('alg', '')
        if alg.startswith('HS'):
            for secret in common_secrets:
                try:
                    jwt.decode(self.token, key=secret, algorithms=[alg])
                    risks.append(('CRITICAL', f'弱密钥爆破成功: {secret}'))
                    break
                except jwt.InvalidTokenError:
                    continue
            if not risks:
                risks.append(('OK', '常见弱密钥不可用'))
        return risks

    def run_all_checks(self, public_key=None):
        """运行所有检查"""
        print(f"[*] JWT Header: {json.dumps(self.header)}")
        print(f"[*] JWT Payload: {json.dumps(self.payload)}\n")

        all_checks = [
            ('Algorithm Security', self.check_algorithm()),
            ('Claims Validation', self.check_claims()),
            ('Sensitive Data', self.check_sensitive_data()),
            ('Default Secrets', self.try_default_secrets()),
        ]
        if public_key:
            all_checks.append(('Alg Confusion', self.check_alg_confusion(public_key)))

        for name, results in all_checks:
            print(f"[*] {name}:")
            for level, msg in results:
                print(f"    [{level}] {msg}")
            print()


if __name__ == '__main__':
    # 示例 JWT（仅用于测试）
    test_token = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJpc3MiOiJ0ZXN0LmlvIiwic3ViIjoiMTIzNDUiLCJhdWQiOiJteS1hcHAiLCJ"
        "leHAiOjk5OTk5OTk5OTksImlhdCI6MTU5OTk5OTk5OX0."
        "weak_signature_here"
    )
    checker = JWTSafetyChecker(test_token)
    checker.run_all_checks()
```

### 4.2 SAML 断言解析与验证脚本

```python
"""
SAML 断言解析与安全验证脚本
检测项：签名验证、时间窗口、受众、XXE、XSW
依赖: pip install lxml signxml python3-saml
"""

from lxml import etree
from signxml import XMLVerifier
from datetime import datetime, timezone
import re


class SAMLChecker:
    def __init__(self, saml_response_xml):
        """saml_response_xml: SAML Response 的 XML 字符串"""
        # 安全解析（禁用 DTD 和外部实体，防 XXE）
        parser = etree.XMLParser(
            no_network=True,
            resolve_entities=False,
            dtd_validation=False,
            huge_tree=False
        )
        self.root = etree.fromstring(saml_response_xml.encode(), parser=parser)
        self.ns = {'saml': 'urn:oasis:names:tc:SAML:2.0:assertion',
                   'samlp': 'urn:oasis:names:tc:SAML:2.0:protocol',
                   'ds': 'http://www.w3.org/2000/09/xmldsig#'}

    def check_xxe(self):
        """检测 XXE 风险（已通过安全解析器消除）"""
        risks = []
        xml_text = etree.tostring(self.root).decode()
        if '<!DOCTYPE' in xml_text or '<!ENTITY' in xml_text:
            risks.append(('WARNING', '检测到 DTD/Entity，已安全过滤'))
        else:
            risks.append(('OK', '无 DTD/Entity，XXE 风险低'))
        return risks

    def check_signature(self, idp_cert):
        """验证 SAML 断言签名"""
        risks = []
        try:
            XMLVerifier().verify(self.root, x509_cert=idp_cert)
            risks.append(('OK', '签名验证通过'))
        except Exception as e:
            risks.append(('CRITICAL', f'签名验证失败: {e}'))
        return risks

    def check_conditions(self, expected_audience):
        """检查 Conditions 时间窗口和受众"""
        risks = []
        conditions = self.root.find('.//saml:Conditions', self.ns)
        if conditions is not None:
            not_before = conditions.get('NotBefore')
            not_on_or_after = conditions.get('NotOnOrAfter')
            now = datetime.now(timezone.utc)

            if not_before:
                nb = datetime.fromisoformat(not_before.replace('Z', '+00:00'))
                if now < nb:
                    risks.append(('WARNING', f'NotBefore 在未来: {not_before}'))

            if not_on_or_after:
                exp = datetime.fromisoformat(not_on_or_after.replace('Z', '+00:00'))
                if now > exp:
                    risks.append(('WARNING', f'断言已过期: {not_on_or_after}'))
                window = (exp - nb).total_seconds() if not_before else 0
                if window > 300:
                    risks.append(('WARNING', f'时间窗口过大: {window}s'))
            audience_restriction = conditions.find('.//saml:Audience', self.ns)
            if audience_restriction is not None:
                audience = audience_restriction.text
                if audience != expected_audience:
                    risks.append(('CRITICAL', f'受众不匹配: {audience}'))
                else:
                    risks.append(('OK', f'受众验证通过: {audience}'))
            else:
                risks.append(('WARNING', '缺少 AudienceRestriction'))
        else:
            risks.append(('CRITICAL', '缺少 Conditions 元素'))
        return risks

    def check_xsw(self):
        """检测 XML 签名包装攻击可能性"""
        risks = []
        assertions = self.root.findall('.//saml:Assertion', self.ns)
        if len(assertions) > 1:
            risks.append(('CRITICAL', f'检测到多个 Assertion（{len(assertions)}个），可能存在 XSW'))
        signatures = self.root.findall('.//ds:Signature', self.ns)
        for sig in signatures:
            ref = sig.find('.//ds:Reference', self.ns)
            if ref is not None:
                uri = ref.get('URI', '')
                if not uri or uri == '':
                    risks.append(('WARNING', '签名 Reference URI 为空，可能存在 XSW'))
        return risks

    def extract_claims(self):
        """提取断言中的属性声明"""
        claims = {}
        attrs = self.root.findall('.//saml:Attribute', self.ns)
        for attr in attrs:
            name = attr.get('Name')
            values = [v.text for v in attr.findall('.//saml:AttributeValue', self.ns)]
            claims[name] = values
        name_id = self.root.find('.//saml:NameID', self.ns)
        if name_id is not None:
            claims['NameID'] = name_id.text
        return claims

    def run_all_checks(self, idp_cert=None, expected_audience=None):
        """运行所有检查"""
        all_checks = [
            ('XXE Protection', self.check_xxe()),
            ('XSW Detection', self.check_xsw()),
        ]
        if idp_cert:
            all_checks.append(('Signature', self.check_signature(idp_cert)))
        if expected_audience:
            all_checks.append(('Conditions', self.check_conditions(expected_audience)))

        for name, results in all_checks:
            print(f"[*] {name}:")
            for level, msg in results:
                print(f"    [{level}] {msg}")
            print()

        claims = self.extract_claims()
        print(f"[*] Extracted Claims: {claims}")


if __name__ == '__main__':
    # 示例用法
    sample_saml = """
    <samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol">
      <saml:Assertion xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" ID="_abc123">
        <saml:Issuer>https://idp.example.com</saml:Issuer>
        <saml:Subject>
          <saml:NameID>user@example.com</saml:NameID>
        </saml:Subject>
        <saml:Conditions NotBefore="2026-09-12T10:00:00Z" NotOnOrAfter="2026-09-12T10:05:00Z">
          <saml:AudienceRestriction>
            <saml:Audience>https://sp.example.com</saml:Audience>
          </saml:AudienceRestriction>
        </saml:Conditions>
      </saml:Assertion>
    </samlp:Response>
    """
    checker = SAMLChecker(sample_saml)
    checker.run_all_checks(expected_audience='https://sp.example.com')
```

---

---

