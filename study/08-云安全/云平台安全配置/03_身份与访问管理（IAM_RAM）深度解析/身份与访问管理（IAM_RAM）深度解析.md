# 身份与访问管理（IAM/RAM）深度解析

### 3.1 权限模型对比

| 概念 | AWS IAM | 阿里云 RAM | 说明 |
|------|---------|------------|------|
| 策略评估逻辑 | 显式拒绝 > 显式允许 > 默认拒绝 | 相同 | 所有策略聚合评估 |
| 策略类型 | 托管策略、内联策略 | 系统策略、自定义策略 | 策略复用方式 |
| 权限边界 | Permissions Boundary | 权限边界（部分支持） | 限制最大权限 |
| 资源级权限 | 大多数服务支持 | 多数服务支持 | 精细到资源的权限 |
| 条件策略 | 丰富的条件键 | 丰富的条件键 | 基于条件的授权 |

### 3.2 常见权限错误

#### 错误 1：权限过大的管理员策略
```json
// 错误示例：给普通用户完全管理员权限
{
    "Effect": "Allow",
    "Action": "*",
    "Resource": "*"
}
```
**正确做法**：只授予需要的具体服务权限。

#### 错误 2：资源通配符
```json
// 错误示例：允许操作所有存储桶
{
    "Effect": "Allow",
    "Action": "s3:*",
    "Resource": "*"
}
```
**正确做法**：指定具体的资源 ARN。

#### 错误 3：角色信任策略过宽
```json
// 错误示例：允许所有人扮演角色
{
    "Effect": "Allow",
    "Principal": {
        "AWS": "*"
    },
    "Action": "sts:AssumeRole"
}
```
**正确做法**：只允许信任的账户或服务扮演角色。

### 3.3 最小权限原则实践

**实施步骤**：
1. **列出所需操作**：明确用户/角色需要执行的具体操作
2. **映射到 API**：将操作映射到具体的云服务 API
3. **确定资源范围**：明确操作涉及的具体资源
4. **添加条件限制**：如 IP 限制、时间限制、MFA 要求
5. **定期审计**：使用 Access Advisor 等工具检查权限使用情况
6. **及时回收**：移除不再使用的权限

**示例：S3 只读权限策略**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "S3ReadOnlySpecificBucket",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:ListBucket",
                "s3:GetBucketLocation"
            ],
            "Resource": [
                "arn:aws:s3:::my-app-data",
                "arn:aws:s3:::my-app-data/*"
            ],
            "Condition": {
                "IpAddress": {
                    "aws:SourceIp": "10.0.0.0/8"
                },
                "Bool": {
                    "aws:MultiFactorAuthPresent": "true"
                }
            }
        }
    ]
}
```

---

---

