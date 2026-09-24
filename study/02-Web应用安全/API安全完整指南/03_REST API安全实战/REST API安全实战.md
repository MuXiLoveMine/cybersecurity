# REST API安全实战

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

---

