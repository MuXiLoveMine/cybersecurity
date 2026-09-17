# API 安全网关

### 6.1 网关安全能力

```
API 安全网关架构:

客户端请求 → [API网关] → 后端服务
                │
    ┌───────────┼───────────┐
    │           │           │
认证鉴权     限流控制     请求过滤
├─ JWT验证   ├─ 令牌桶     ├─ WAF规则
├─ OAuth2    ├─ 滑动窗口   ├─ SQL注入防护
├─ API Key   ├─ 并发控制   ├─ XSS过滤
└─ 签名验证   └─ 熔断降级   └─ CSRF防护
    │
响应处理
├─ 数据脱敏
├─ 字段过滤
├─ 响应签名
└─ 日志审计
```

### 6.2 限流配置示例

```yaml
# API 限流策略配置 (Kong网关)

plugins:
  # IP级限流 - 防暴力破解
  - name: rate-limiting
    config:
      minute: 30           # 每IP每分钟30次
      hour: 500            # 每IP每小时500次
      policy: redis
      redis:
        host: redis.internal
        port: 6379
      fault_tolerant: true  # Redis宕机时降级为本地限流

  # 用户级限流 - 防滥用
  - name: rate-limiting
    route: user-api
    config:
      minute: 60           # 每用户每分钟60次
      limit_by: credential  # 按认证凭据限流
      policy: redis

  # 请求大小限制
  - name: request-size-limiting
    config:
      allowed_payload_size: 5  # 最大5MB

  # IP黑白名单
  - name: ip-restriction
    config:
      blacklist:
        - 10.0.0.0/8       # 禁止内网段(防SSRF)
```

```python
# 自定义限流中间件示例 (Python Flask)
from functools import wraps
from redis import Redis
from flask import request, jsonify

redis = Redis(host='redis.internal', port=6379, decode_responses=True)

def rate_limit(limit=100, window=60, key_func=None):
    """
    API 速率限制装饰器
    limit: 窗口内最大请求数
    window: 时间窗口(秒)
    key_func: 限流键函数(默认IP+用户)
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # 生成限流键
            if key_func:
                key = key_func()
            else:
                # 默认: IP + 用户Token
                ip = request.headers.get('X-Forwarded-For', 
                                        request.remote_addr)
                token = request.headers.get('Authorization', 'anonymous')
                key = f"rate_limit:{ip}:{token}"
            
            # 滑动窗口计数
            pipe = redis.pipeline()
            pipe.incr(key)
            pipe.expire(key, window)
            count, _ = pipe.execute()
            
            if count > limit:
                # 返回429 Too Many Requests
                return jsonify({
                    'error': 'Too Many Requests',
                    'message': f'请求频率超过限制: {limit}次/{window}秒',
                    'retry_after': window
                }), 429
            
            # 添加限流头
            response = f(*args, **kwargs)
            response.headers['X-RateLimit-Limit'] = str(limit)
            response.headers['X-RateLimit-Remaining'] = str(
                max(0, limit - count)
            )
            return response
        return wrapper
    return decorator

# 使用示例
@app.route('/api/v1/orders', methods=['GET'])
@auth_required
@rate_limit(limit=60, window=60)  # 每分钟60次
def list_orders():
    ...
```

### 6.3 API 数据脱敏

```python
# 动态数据脱敏中间件

class DataMasker:
    """
    响应数据动态脱敏
    根据用户角色和数据敏感级别，对API响应中的敏感字段进行脱敏
    """
    
    MASK_RULES = {
        'phone': lambda x: x[:3] + '****' + x[-4:] if len(x) >= 8 else '****',
        'email': lambda x: x[0] + '***@' + x.split('@')[1] if '@' in x else '***',
        'id_card': lambda x: x[:6] + '********' + x[-4:] if len(x) >= 18 else '****',
        'bank_card': lambda x: x[:4] + '********' + x[-4:] if len(x) >= 16 else '****',
        'name': lambda x: x[0] + '*' * (len(x) - 1) if len(x) > 1 else '*',
        'address': lambda x: x[:6] + '***' if len(x) > 6 else '***',
    }
    
    # 角色级别的脱敏策略
    ROLE_POLICIES = {
        'admin': {
            # 管理员可看到更多数据
            'phone': 'partial',     # 138****8000
            'email': 'partial',     # z***@example.com
            'id_card': 'masked',    # 110101********1234
        },
        'customer_service': {
            'phone': 'masked',      # 138****8000
            'email': 'masked',      # z***@example.com
            'id_card': 'hidden',    # ***
        },
        'external_partner': {
            'phone': 'hidden',      # ***
            'email': 'masked',      # z***@example.com
            'id_card': 'hidden',    # ***
        }
    }
    
    def mask_response(self, data, user_role, field_types):
        """
        根据用户角色对响应数据进行脱敏
        data: 原始数据
        user_role: 用户角色
        field_types: {字段名: 数据类型}
        """
        policy = self.ROLE_POLICIES.get(user_role, 
                                         self.ROLE_POLICIES['external_partner'])
        
        if isinstance(data, dict):
            masked = {}
            for key, value in data.items():
                field_type = field_types.get(key)
                if field_type and field_type in self.MASK_RULES:
                    action = policy.get(field_type, 'masked')
                    if action == 'hidden':
                        masked[key] = '***'
                    elif action == 'partial':
                        masked[key] = value  # 部分角色可看原始数据
                    else:  # masked
                        masked[key] = self.MASK_RULES[field_type](str(value))
                else:
                    masked[key] = value
            return masked
        elif isinstance(data, list):
            return [self.mask_response(item, user_role, field_types) 
                    for item in data]
        return data


# 使用示例 - API 响应中间件
@app.route('/api/v1/users/<int:user_id>')
@auth_required
def get_user(user_id):
    user = get_user_from_db(user_id)
    
    # 当前用户角色
    role = g.current_user.role
    
    # 字段类型映射
    field_types = {
        'phone': 'phone',
        'email': 'email',
        'id_card': 'id_card',
        'name': 'name',
        'address': 'address'
    }
    
    # 动态脱敏
    masker = DataMasker()
    masked_user = masker.mask_response(
        user.to_dict(), role, field_types
    )
    
    return jsonify(masked_user)
```

---

---

## 📋 内容审核与补充建议

> 针对「API 安全网关」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

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
