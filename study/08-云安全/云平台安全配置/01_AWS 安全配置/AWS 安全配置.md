# AWS 安全配置

### 1.1 IAM（身份与访问管理）

#### 1.1.1 IAM 核心概念

| 概念 | 说明 |
|------|------|
| 用户（User） | 具有长期凭证的身份实体，代表人或应用 |
| 组（Group） | 用户的集合，便于批量授权 |
| 角色（Role） | 临时凭证的身份，可被用户/服务/账户扮演 |
| 策略（Policy） | JSON 格式的权限定义文档 |
| 访问密钥（Access Key） | 用于 API/CLI 访问的密钥对（Access Key ID + Secret Access Key） |

#### 1.1.2 IAM 策略结构

IAM 策略是 JSON 格式的文档，定义了允许或拒绝的操作。

**策略基本结构**：

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowS3ReadAccess",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::my-bucket",
                "arn:aws:s3:::my-bucket/*"
            ],
            "Condition": {
                "IpAddress": {
                    "aws:SourceIp": "192.168.1.0/24"
                }
            }
        }
    ]
}
```

**字段说明**：
- **Version**：策略语言版本，固定为 "2012-10-17"
- **Statement**：策略语句数组，可以有多条
- **Sid**：语句标识符（可选），用于描述策略目的
- **Effect**：效果，"Allow"（允许）或 "Deny"（拒绝）
- **Action**：操作列表，格式为 `服务:操作`，如 `s3:GetObject`
- **Resource**：资源列表，ARN 格式
- **Condition**：条件（可选），满足条件时策略才生效

#### 1.1.3 IAM 安全最佳实践

| 最佳实践 | 说明 | 配置方式 |
|----------|------|----------|
| 启用 MFA | 根账号和所有用户启用多因素认证 | IAM 控制台 → 用户 → 安全凭证 → 分配 MFA 设备 |
| 最小权限原则 | 只授予必要的最小权限 | 使用 AWS 托管策略或自定义精细策略 |
| 使用角色而非长期密钥 | 应用通过角色获取临时凭证 | EC2 实例配置文件、Lambda 执行角色 |
| 定期轮换密钥 | 访问密钥定期更换 | IAM 控制台或 API 轮换 |
| 密码策略 | 设置强密码策略 | IAM 账户设置 → 密码策略 |
| 最小化根账号使用 | 日常操作不使用根账号 | 创建管理员用户进行日常管理 |
| 权限边界 | 限制用户/角色的最大权限 | Permissions Boundary |
| 定期审计权限 | 检查是否有权限过大 | IAM Access Analyzer、Access Advisor |

#### 1.1.4 危险的 IAM 策略示例

**危险策略 1：完全管理员权限（绝对禁止给普通用户）**
```json
{
    "Effect": "Allow",
    "Action": "*",
    "Resource": "*"
}
```
**风险**：拥有所有 AWS 服务的完全访问权限，一旦泄露可造成毁灭性损失。

**危险策略 2：资源通配符 + 敏感操作**
```json
{
    "Effect": "Allow",
    "Action": "s3:*",
    "Resource": "*"
}
```
**风险**：可访问所有 S3 存储桶，包括其他账户的公开桶，可能导致数据泄露。

**危险策略 3：过宽的角色信任策略**
```json
{
    "Effect": "Allow",
    "Principal": {
        "AWS": "*"
    },
    "Action": "sts:AssumeRole"
}
```
**风险**：任何 AWS 账户都可以扮演该角色，严重的权限泄露风险。

---

### 1.2 S3（简单存储服务）安全配置

#### 1.2.1 S3 安全配置清单

| 配置项 | 安全要求 | 风险等级 |
|--------|----------|----------|
| 阻止公开访问 | 启用（Block all public access） | 高危 |
| 存储桶策略 | 最小权限，禁止 Principal: "*" | 高危 |
| ACL | 私有（Private） | 高危 |
| 服务端加密 | 启用（SSE-KMS 或 SSE-S3） | 中危 |
| 版本控制 | 启用 | 中危 |
| 访问日志 | 启用 | 中危 |
| MFA 删除 | 启用（可选） | 中危 |
| 对象锁定 | 按需启用（WORM） | 低危 |
| 传输加密 | 强制 HTTPS | 中危 |

#### 1.2.2 安全的存储桶策略示例

**示例 1：仅允许特定 VPC 访问**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowOnlyFromVPC",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::my-secure-bucket/*",
            "Condition": {
                "StringEquals": {
                    "aws:SourceVpc": "vpc-12345678"
                }
            }
        }
    ]
}
```

**示例 2：强制 HTTPS 传输**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "ForceSSLOnly",
            "Effect": "Deny",
            "Principal": "*",
            "Action": "s3:*",
            "Resource": [
                "arn:aws:s3:::my-secure-bucket",
                "arn:aws:s3:::my-secure-bucket/*"
            ],
            "Condition": {
                "Bool": {
                    "aws:SecureTransport": "false"
                }
            }
        }
    ]
}
```

**示例 3：限制特定 IP 访问**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowSpecificIP",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::my-secure-bucket/*",
            "Condition": {
                "IpAddress": {
                    "aws:SourceIp": "10.0.0.0/8"
                }
            }
        }
    ]
}
```

#### 1.2.3 S3 公开访问检测与修复

**检测公开存储桶的方法**：
1. AWS 控制台：S3 → 权限 → 阻止公开访问
2. AWS CLI：`aws s3api get-bucket-policy-status --bucket my-bucket`
3. 使用 S3 Access Analyzer
4. 使用 Prowler、Scout Suite 等审计工具

**修复步骤**：
1. 启用"阻止全部公开访问"（Block all public access）
2. 审查存储桶策略，移除公开访问权限
3. 审查 ACL，设置为私有
4. 启用访问日志，审计历史访问记录

---

### 1.3 EC2（弹性计算云）安全配置

#### 1.3.1 EC2 安全基线

| 配置项 | 安全要求 |
|--------|----------|
| 实例元数据服务 | 使用 IMDSv2（需要会话令牌） |
| 密钥对 | 使用强密钥，禁止共享 |
| IAM 角色 | 为实例分配角色，而非使用访问密钥 |
| 安全组 | 最小权限原则，限制入站访问 |
| 操作系统 | 及时安装安全补丁 |
| 安全软件 | 安装主机安全/HIDS |
| 远程访问 | 限制 SSH/RDP 来源 IP |
| 存储加密 | EBS 卷启用加密 |

#### 1.3.2 实例元数据服务（IMDS）安全

**IMDSv1 vs IMDSv2**：
- **IMDSv1**：直接 GET 请求即可获取元数据，存在 SSRF 利用风险
- **IMDSv2**：需要先 PUT 请求获取会话令牌，再使用令牌访问元数据

**启用 IMDSv2**：
```bash
# 修改实例为仅 IMDSv2
aws ec2 modify-instance-metadata-options \
    --instance-id i-1234567890abcdef0 \
    --http-tokens required \
    --http-endpoint enabled
```

**元数据服务可获取的敏感信息**：
- 实例角色的临时凭证（`/latest/meta-data/iam/security-credentials/role-name`）
- 实例 ID、IP、AMI ID
- 用户数据（User Data）
- 公有密钥

#### 1.3.3 EC2 安全加固清单

**操作系统加固**：
- 禁用 root 用户 SSH 登录
- 使用密钥认证，禁用密码登录
- 修改 SSH 默认端口（可选）
- 配置 fail2ban 防暴力破解
- 启用防火墙（iptables/ufw）
- 定期更新系统补丁

**应用加固**：
- Web 服务器配置 WAF
- 数据库禁止公网访问
- 敏感配置文件加密存储
- 日志集中收集

---

### 1.4 VPC（虚拟私有云）与安全组

#### 1.4.1 VPC 网络架构设计

```
                    Internet
                        │
                   Internet Gateway
                        │
          ┌─────────────┴─────────────┐
          │                           │
     公有子网 1a                  公有子网 1b
     (Bastion/NAT GW)            (Bastion/NAT GW)
          │                           │
    路由表（公有）              路由表（公有）
          │                           │
          └─────────────┬─────────────┘
                        │
          ┌─────────────┴─────────────┐
          │                           │
     私有子网 1a                  私有子网 1b
     (Web/应用服务器)            (Web/应用服务器)
          │                           │
    路由表（私有）              路由表（私有）
          │                           │
          └─────────────┬─────────────┘
                        │
          ┌─────────────┴─────────────┐
          │                           │
    数据子网 1a                  数据子网 1b
     (数据库)                     (数据库)
```

**设计原则**：
1. **多可用区部署**：提高可用性
2. **分层网络**：公有子网放对外服务，私有子网放内部服务，数据子网放数据库
3. **最小暴露原则**：尽量减少公网暴露的资源
4. **安全分层**：安全组 + NACL 多层防护

#### 1.4.2 安全组（Security Group）配置

**安全组特点**：
- 有状态（Stateful）：入站允许则出站自动允许响应
- 实例级别的防火墙
- 只支持 Allow 规则，不支持 Deny 规则
- 可配置多个安全组

**安全组最佳实践**：

| 最佳实践 | 说明 |
|----------|------|
| 最小权限 | 只开放必要的端口和来源 |
| 命名清晰 | 用有意义的名称，如 web-sg、db-sg |
| 按角色分组 | 同类角色的实例使用相同安全组 |
| 限制来源 | 尽量指定安全组或具体 IP，不用 0.0.0.0/0 |
| 禁止全开放 | 禁止 0.0.0.0/0 到所有端口 |
| 定期审计 | 定期审查安全组规则 |

**危险的安全组配置示例**：

| 危险配置 | 风险 | 正确做法 |
|----------|------|----------|
| 入站规则：0.0.0.0/0 到 22 端口 | SSH 暴露给全网，易被暴力破解 | 限制为公司 IP 或堡垒机 IP |
| 入站规则：0.0.0.0/0 到 3306 端口 | MySQL 数据库公网暴露 | 数据库放私有子网，来源设为应用安全组 |
| 入站规则：0.0.0.0/0 到所有端口 | 等于没有防火墙 | 按需开放必要端口 |
| 出站规则：全部允许 0.0.0.0/0 | 被入侵后可对外发起任意连接 | 根据需要限制出站 |

**安全的安全组配置示例**：

Web 服务器安全组（web-sg）：
| 方向 | 协议 | 端口 | 来源 | 说明 |
|------|------|------|------|------|
| 入站 | TCP | 80 | 0.0.0.0/0 | HTTP 访问 |
| 入站 | TCP | 443 | 0.0.0.0/0 | HTTPS 访问 |
| 入站 | TCP | 22 | 10.0.1.0/24 | 仅允许堡垒机网段 SSH |
| 出站 | 全部 | 全部 | 0.0.0.0/0 | 出站按需限制 |

数据库安全组（db-sg）：
| 方向 | 协议 | 端口 | 来源 | 说明 |
|------|------|------|------|------|
| 入站 | TCP | 3306 | web-sg | 仅允许 Web 安全组访问 |
| 出站 | 全部 | 全部 | 0.0.0.0/0 | 出站按需限制 |

#### 1.4.3 网络 ACL（NACL）

**NACL 特点**：
- 无状态（Stateless）：入站和出站规则独立
- 子网级别的防火墙
- 支持 Allow 和 Deny 规则
- 规则按编号顺序匹配

**安全组 vs NACL**：

| 对比项 | 安全组 | 网络 ACL |
|--------|--------|----------|
| 作用层级 | 实例级别 | 子网级别 |
| 状态 | 有状态 | 无状态 |
| 规则类型 | 仅 Allow | Allow + Deny |
| 规则顺序 | 不按顺序 | 按编号顺序 |
| 默认配置 | 全部拒绝入站，全部允许出站 | 全部允许 |

---

### 1.5 CloudTrail（日志审计）

#### 1.5.1 CloudTrail 概述

AWS CloudTrail 记录 AWS 账户的 API 调用活动，包括：
- 谁发起了调用（身份）
- 调用了什么 API
- 何时调用（时间）
- 从哪里调用（IP 地址）
- 调用结果（成功/失败）

#### 1.5.2 CloudTrail 安全配置

| 配置项 | 安全要求 | 说明 |
|--------|----------|------|
| 启用全局跟踪 | 启用所有区域 | 覆盖所有 AWS 区域的 API 调用 |
| 日志文件验证 | 启用 | 防止日志被篡改 |
| 多区域跟踪 | 启用 | 记录所有区域的活动 |
| 管理事件 | 启用 | 记录管理操作 |
| 数据事件 | 按需启用 | 记录 S3、Lambda 等数据操作 |
| S3 存储桶加密 | 启用 | 日志文件加密存储 |
| 日志完整性 | 启用 S3 对象锁定 | 防止日志被删除 |
| 集中式日志 | 集中到安全账户 | 统一管理和分析 |

#### 1.5.3 关键监控事件

需要重点监控的 CloudTrail 事件：

| 事件名 | 说明 | 风险等级 |
|--------|------|----------|
| ConsoleLogin | 控制台登录 | 高危（失败登录） |
| CreateUser / DeleteUser | IAM 用户变更 | 高危 |
| CreateAccessKey | 创建访问密钥 | 高危 |
| AssumeRole | 扮演角色 | 中危 |
| PutBucketPolicy | 修改存储桶策略 | 高危 |
| AuthorizeSecurityGroupIngress | 安全组添加入站规则 | 高危 |
| RunInstances | 启动实例 | 中危 |
| StopInstances / TerminateInstances | 停止/终止实例 | 高危 |
| CreateTrail / UpdateTrail / DeleteTrail | CloudTrail 配置变更 | 高危 |

---

---

## 📋 内容审核与补充建议

> 针对「AWS 安全配置」部分的内容审核结果：

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

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
