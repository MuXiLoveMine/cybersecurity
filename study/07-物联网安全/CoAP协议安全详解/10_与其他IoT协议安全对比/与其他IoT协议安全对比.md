# 与其他IoT协议安全对比

### 10.1 协议安全对比表

| 安全特性 | CoAP | MQTT | HTTP | AMQP |
|---------|------|------|------|------|
| 传输层 | UDP | TCP | TCP | TCP |
| 加密 | DTLS | TLS | TLS | TLS |
| 认证 | DTLS/OSCORE | TLS/用户名密码 | TLS/Basic/Digest | TLS/SASL |
| 消息完整性 | DTLS MAC | TLS MAC | TLS MAC | TLS MAC |
| 防重放 | DTLS序号 | TLS序号 | TLS序号 | TLS序号 |
| 端到端安全 | OSCORE | 无(需应用层) | 无(需应用层) | 无 |
| 多播安全 | OSCORE | 不支持 | 不支持 | 不支持 |
| 轻量级 | 是(最小) | 中等 | 否 | 否 |
| 资源发现 | /.well-known/core | 无标准 | /.well-known | 无标准 |

### 10.2 安全建议总结

```
CoAP安全最佳实践:

1. 始终使用DTLS
   - 最低: PSK-DTLS (适用于受限设备)
   - 推荐: RPK-DTLS (适用于中等设备)
   - 最佳: X.509-DTLS (适用于有PKI的环境)

2. 启用OSCORE
   - 在有代理的环境中
   - 需要端到端加密时
   - 多播通信场景

3. 实现访问控制
   - 基于资源的ACL
   - 最小权限原则
   - 敏感资源单独保护

4. 防重放保护
   - 利用DTLS序号
   - CoAP层Message ID窗口
   - Token随机化

5. 资源发现保护
   - 限制/.well-known/core的访问
   - 不暴露敏感资源路径
   - 使用过滤的资源列表

6. 防DoS措施
   - DTLS HelloVerifyRequest
   - 连接速率限制
   - 资源配额管理

7. 固件更新安全
   - 使用CoAP块传输
   - 固件签名验证
   - 版本回滚保护
```

---

---

