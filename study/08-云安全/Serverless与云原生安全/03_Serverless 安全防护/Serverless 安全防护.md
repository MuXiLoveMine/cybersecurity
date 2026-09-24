# Serverless 安全防护

### 3.1 最小权限函数

原则：每个函数只授予完成其单一职责所需的最小权限。

1. 为每个函数创建独立 IAM 角色
2. 权限限定到具体资源 ARN
3. 定期使用 CIEM 工具分析权限使用率，收敛未用权限
4. 避免函数间共享角色

### 3.2 依赖扫描

1. CI 流水线中集成 SCA 工具（Snyk / Dependabot / OSV）
2. 锁定依赖版本，使用 lockfile
3. 禁止使用已废弃或有恶意历史的包
4. 定期重建与更新依赖

### 3.3 API 网关防护

API 网关是 Serverless HTTP 应用的入口，承担关键防护：

```yaml
# AWS API Gateway + Lambda + WAF 示例
# 1. 启用认证（Cognito / Lambda Authorizer）
# 2. 限速
# 3. 接入 WAF
Resources:
  MyApi:
    Type: AWS::ApiGateway::RestApi
    Properties:
      Name: secure-serverless-api
  WebAcl:
    Type: AWS::WAFv2::WebACL
    Properties:
      DefaultAction:
        Allow: {}
      Rules:
        - Name: rate-limit
          Priority: 1
          Action:
            Block: {}
          VisibilityConfig:
            SampledRequestsEnabled: true
            CloudWatchMetricsEnabled: true
            MetricName: rate-limit
          RateBasedStatement:
            Limit: 100
            AggregateKeyType: IP
```

### 3.4 日志与监控

- 所有函数输出日志到 CloudWatch / SLS
- 启用函数层追踪（X-Ray / 链路追踪）
- 监控异常调用频率、错误率、执行时长
- 对异常事件（如非工作时间大量调用）自动告警

### 3.5 函数代码加固

1. 输入校验：所有事件输入视为不可信
2. 输出过滤：避免返回内部错误细节
3. 禁用危险操作：如 `eval`、`pickle.loads`
4. 使用内存中临时文件而非持久化存储
5. 函数执行超时设置合理上限

---

---

