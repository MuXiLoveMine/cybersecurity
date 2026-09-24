# OWASP API Security Top 10 (2023) 详解

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

---

