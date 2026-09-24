# SAML联邦

### 2.1 SAML协议概述

**SAML (Security Assertion Markup Language)** 是基于XML的联邦认证标准，广泛用于企业身份联邦。

```text
SAML 2.0 核心概念

SAML断言 (Assertion):
  XML格式的认证和属性声明
  包含: 认证信息、属性信息、授权决策

SAML绑定 (Binding):
  断言的传输方式
  ├── HTTP-Redirect: URL重定向传递
  ├── HTTP-POST: HTTP POST传递
  ├── HTTP-Artifact: 间接引用传递
  └── SOAP: SOAP消息传递

SAML协议 (Protocol):
  请求-响应模式
  ├── AuthnRequest: 认证请求
  ├── Response: 认证响应(含断言)
  ├── LogoutRequest: 注销请求
  ├── LogoutResponse: 注销响应
  └── ArtifactResolve: Artifact解析

SAML配置文件 (Profile):
  特定使用场景的约束
  ├── Web Browser SSO: 浏览器单点登录
  ├── Single Logout: 单点注销
  ├── Name Identifier Management: 名称管理
  └── Attribute Query: 属性查询
```

### 2.2 SAML认证流程

```text
SAML SSO认证流程 (SP发起)

1. 用户访问SP
   用户 → SP: 访问受保护资源
   SP: 检查会话 → 无有效会话

2. SP生成AuthnRequest
   SP → 用户: 重定向到IdP (携带AuthnRequest)
   AuthnRequest包含:
   ├── SP的EntityID
   ├── AssertionConsumerService URL
   ├── 请求的NameIDFormat
   └── 请求的认证上下文

3. 用户在IdP认证
   用户 → IdP: 登录认证
   IdP: 验证凭据 → 生成SAML断言

4. IdP返回断言
   IdP → 用户: 重定向回SP (携带SAML Response)
   SAML Response包含:
   ├── 认证断言 (Authentication Statement)
   ├── 属性断言 (Attribute Statement)
   └── IdP签名

5. SP验证断言
   SP: 验证IdP签名 → 提取用户信息 → 建立会话

6. 用户访问资源
   SP → 用户: 返回受保护资源内容
```

```python
"""
SAML联邦实现示例
"""

import base64
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError
from datetime import datetime, timedelta
import hashlib
import hmac

class SAMLFederation:
    """SAML联邦实现"""

    # SAML命名空间
    NS = {
        'saml': 'urn:oasis:names:tc:SAML:2.0:assertion',
        'samlp': 'urn:oasis:names:tc:SAML:2.0:protocol',
        'ds': 'http://www.w3.org/2000/09/xmldsig#'
    }

    def __init__(self, entity_id, role='sp'):
        """
        :param entity_id: 实体ID (如 https://sp.example.com)
        :param role: 'sp' 或 'idp'
        """
        self.entity_id = entity_id
        self.role = role
        self.trusted_partners = {}  # entity_id → metadata

    def generate_authn_request(self, idp_entity_id, acs_url=None):
        """生成SAML AuthnRequest（SP端）"""
        request_id = self._generate_id()
        issue_instant = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

        if acs_url is None:
            acs_url = f"{self.entity_id}/saml/acs"

        authn_request = f"""<samlp:AuthnRequest 
    xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
    ID="{request_id}"
    Version="2.0"
    IssueInstant="{issue_instant}"
    Destination="{idp_entity_id}/saml/sso"
    ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
    AssertionConsumerServiceURL="{acs_url}">
    <saml:Issuer xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">
        {self.entity_id}
    </saml:Issuer>
    <samlp:NameIDPolicy 
        AllowCreate="true"
        Format="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"/>
    <samlp:RequestedAuthnContext 
        Comparison="minimum">
        <saml:AuthnContextClassRef>
            urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport
        </saml:AuthnContextClassRef>
    </samlp:RequestedAuthnContext>
</samlp:AuthnRequest>"""

        return {
            'request_xml': authn_request,
            'request_id': request_id,
            'encoded': self._encode_for_redirect(authn_request)
        }

    def generate_saml_response(self, request_id, user_info, sp_entity_id,
                                 acs_url, signing_key=None):
        """生成SAML Response（IdP端）"""
        response_id = self._generate_id()
        assertion_id = self._generate_id()
        issue_instant = datetime.utcnow()
        not_on_or_after = issue_instant + timedelta(minutes=5)
        not_before = issue_instant - timedelta(minutes=1)
        session_not_on_or_after = issue_instant + timedelta(hours=8)

        fmt = '%Y-%m-%dT%H:%M:%SZ'
        issue_str = issue_instant.strftime(fmt)
        noa_str = not_on_or_after.strftime(fmt)
        nb_str = not_before.strftime(fmt)
        snoa_str = session_not_on_or_after.strftime(fmt)

        user_id = user_info.get('email', user_info.get('id', 'unknown'))
        attributes = user_info.get('attributes', {})

        attr_xml = ''
        for name, value in attributes.items():
            attr_xml += f"""<saml:Attribute Name="{name}" 
    NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:basic">
    <saml:AttributeValue>{value}</saml:AttributeValue>
</saml:Attribute>"""

        saml_response = f"""<samlp:Response 
    xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
    ID="{response_id}"
    Version="2.0"
    IssueInstant="{issue_str}"
    Destination="{acs_url}"
    InResponseTo="{request_id}">
    <saml:Issuer xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">
        {self.entity_id}
    </saml:Issuer>
    <samlp:Status>
        <samlp:StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:Success"/>
    </samlp:Status>
    <saml:Assertion 
        xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
        ID="{assertion_id}"
        Version="2.0"
        IssueInstant="{issue_str}">
        <saml:Issuer>{self.entity_id}</saml:Issuer>
        <saml:Subject>
            <saml:NameID Format="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress">
                {user_id}
            </saml:NameID>
            <saml:SubjectConfirmation Method="urn:oasis:names:tc:SAML:2.0:cm:bearer">
                <saml:SubjectConfirmationData
                    NotOnOrAfter="{noa_str}"
                    Recipient="{acs_url}"
                    InResponseTo="{request_id}"/>
            </saml:SubjectConfirmation>
        </saml:Subject>
        <saml:Conditions
            NotBefore="{nb_str}"
            NotOnOrAfter="{noa_str}">
            <saml:AudienceRestriction>
                <saml:Audience>{sp_entity_id}</saml:Audience>
            </saml:AudienceRestriction>
        </saml:Conditions>
        <saml:AuthnStatement
            AuthnInstant="{issue_str}"
            SessionIndex="{assertion_id}"
            SessionNotOnOrAfter="{snoa_str}">
            <saml:AuthnContext>
                <saml:AuthnContextClassRef>
                    urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport
                </saml:AuthnContextClassRef>
            </saml:AuthnContext>
        </saml:AuthnStatement>
        <saml:AttributeStatement>
            {attr_xml}
        </saml:AttributeStatement>
    </saml:Assertion>
</samlp:Response>"""

        return {
            'response_xml': saml_response,
            'response_id': response_id,
            'assertion_id': assertion_id
        }

    def verify_saml_response(self, response_xml, trusted_idp_entity_id):
        """验证SAML Response（SP端）"""
        try:
            root = ET.fromstring(response_xml)

            # 验证Issuer
            issuer = root.find('.//{*}Issuer')
            if issuer is not None:
                if issuer.text != trusted_idp_entity_id:
                    return {'valid': False, 'reason': '不信任的IdP'}

            # 验证状态
            status = root.find('.//{*}StatusCode')
            if status is not None:
                if 'Success' not in status.get('Value', ''):
                    return {'valid': False, 'reason': 'IdP返回失败状态'}

            # 提取断言信息
            assertion = root.find('.//{*}Assertion')
            if assertion is None:
                return {'valid': False, 'reason': '无断言'}

            # 提取用户信息
            name_id = assertion.find('.//{*}NameID')
            user_id = name_id.text if name_id is not None else 'unknown'

            # 提取属性
            attributes = {}
            for attr in assertion.findall('.//{*}Attribute'):
                name = attr.get('Name')
                values = attr.findall('{*}AttributeValue')
                if values:
                    attributes[name] = values[0].text

            # 验证时间
            conditions = assertion.find('.//{*}Conditions')
            if conditions is not None:
                not_before = conditions.get('NotBefore')
                not_on_or_after = conditions.get('NotOnOrAfter')
                now = datetime.utcnow()
                if not_on_or_after:
                    noa = datetime.strptime(not_on_or_after, '%Y-%m-%dT%H:%M:%SZ')
                    if now > noa:
                        return {'valid': False, 'reason': '断言已过期'}

            return {
                'valid': True,
                'user_id': user_id,
                'attributes': attributes
            }

        except ParseError as e:
            return {'valid': False, 'reason': f'XML解析失败: {e}'}
        except Exception as e:
            return {'valid': False, 'reason': f'验证异常: {e}'}

    def add_trusted_partner(self, entity_id, metadata):
        """添加信任伙伴"""
        self.trusted_partners[entity_id] = metadata

    @staticmethod
    def _generate_id():
        import secrets
        return f"id_{secrets.token_hex(16)}"

    @staticmethod
    def _encode_for_redirect(xml):
        """Base64编码用于URL重定向"""
        return base64.b64encode(xml.encode('utf-8')).decode('utf-8')
```

### 2.3 SAML安全考量

```text
SAML安全风险与防御

风险1: XML签名包装 (XSW)
  ├── 攻击者修改SAML断言结构
  ├── 使签名验证覆盖错误部分
  ├── 防御: 严格验证签名覆盖范围
  └── 使用: Schema验证 + 签名位置检查

风险2: 重放攻击
  ├── 截获有效SAML断言并重放
  ├── 防御: 验证NotOnOrAfter + InResponseTo
  └── 记录已使用的断言ID

风险3: 中间人攻击
  ├── 拦截SAML消息
  ├── 防御: HTTPS传输 + 断言签名
  └── Destination验证

风险4: XXE注入
  ├── XML外部实体注入
  ├── 防御: 禁用外部实体解析
  └── 使用安全XML解析器

风险5: 令牌伪造
  ├── 伪造SAML断言
  ├── 防御: 验证IdP签名
  └── 验证证书信任链

风险6: 会话固定
  ├── 攻击者固定SP会话ID
  ├── 防御: 认证后生成新会话
  └── 会话绑定到用户身份

最佳实践:
├── 断言签名必须验证
├── 严格验证所有时间条件
├── 验证AudienceRestriction
├── 验证Recipient
├── 记录InResponseTo
├── 使用安全XML解析（禁XXE）
├── 断言有效期不超过5分钟
├── 使用HTTPS传输
└── 定期轮换签名证书
```

---

---

