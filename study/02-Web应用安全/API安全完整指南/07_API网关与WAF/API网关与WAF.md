# API网关与WAF

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

---

## 📋 内容审核与补充建议

> 针对「API网关与WAF」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

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
