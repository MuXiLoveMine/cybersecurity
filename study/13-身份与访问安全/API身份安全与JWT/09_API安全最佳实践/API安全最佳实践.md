# API安全最佳实践

```text
API安全最佳实践清单

[认证与授权]
□ 使用OAuth 2.0 / JWT替代API Key/Basic Auth
□ JWT使用RS256/ES256非对称签名
□ 明确指定算法白名单（不允许alg=none）
□ 实施最小权限原则
□ 使用scope限制API访问范围
□ 高敏感操作需要MFA
□ 定期轮换API密钥和JWT密钥

[JWT安全]
□ 设置合理的过期时间（1小时）
□ 实施刷新令牌机制
□ 使用jti防止重放
□ 验证iss/aud/sub
□ 不在Payload中存储敏感信息
□ 使用HTTPS传输JWT
□ 安全存储JWT（HttpOnly Cookie）

[传输安全]
□ 强制使用HTTPS（TLS 1.2+）
□ 实施HSTS
□ 考虑mTLS用于服务间通信
□ 使用证书固定(Certificate Pinning)

[请求安全]
□ 实施速率限制
□ 输入验证和参数白名单
□ 请求大小限制
□ SQL注入防护（参数化查询）
□ XSS防护（输出编码）
□ CSRF防护（SameSite Cookie）

[API网关]
□ 统一入口管理
□ 认证授权前置
□ 请求路由和过滤
□ 速率限制和配额
□ API版本管理
□ 请求/响应日志
□ WAF集成

[监控与审计]
□ 记录所有API访问日志
□ 异常请求检测
□ 认证失败告警
□ 权限变更审计
□ 数据访问审计
□ 安全事件响应

[密钥管理]
□ 使用KMS管理密钥
□ 密钥分级管理
□ 定期轮换
□ 访问控制
□ 使用HSM保护根密钥
```

---

---

