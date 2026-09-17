# 特权访问管理（PAM）

### 2.1 PAM 概念与必要性

**PAM（Privileged Access Management）** 是对高权限账户的发现、监控、控制和审计的系统性方案。

**为什么需要 PAM**：
- 特权账户是攻击者的首要目标（"皇冠上的宝石"）
- 内部威胁：管理员过度权限和滥用
- 合规要求（SOX、PCI-DSS、GDPR、等保2.0）
- 横向移动的跳板：一旦特权账户失陷，整个域/云环境沦陷

### 2.2 PAM 核心功能

```
┌────────────────────────────────────────────────────────┐
│                   PAM 核心功能                          │
├────────────────┬────────────────┬─────────────────────┤
│  特权账户发现   │  密码保险库     │  会话录制与审计     │
│  & 登记        │  & 自动轮换     │                    │
├────────────────┼────────────────┼─────────────────────┤
│  即时访问(JIT) │  最小权限       │  审批流程           │
│  & 临时凭证    │  & 角色控制     │  & 工作流          │
└────────────────┴────────────────┴─────────────────────┘
```

#### 特权账户发现与登记

```python
# 特权账户发现示例（扫描域环境中的高权账户）
# 依赖: pip install ldap3

from ldap3 import Server, Connection, ALL

def discover_privileged_accounts(ldap_server, bind_dn, password, base_dn):
    server = Server(ldap_server, get_info=ALL)
    conn = Connection(server, user=bind_dn, password=password, auto_bind=True)

    privileged_groups = [
        "Domain Admins", "Enterprise Admins", "Schema Admins",
        "Administrators", "Account Operators", "Server Operators",
        "Backup Operators", "Print Operators"
    ]

    findings = []
    for group_name in privileged_groups:
        cn = f"CN={group_name},CN=Users,{base_dn}"
        conn.search(cn, '(objectClass=group)', attributes=['member'])
        if conn.entries:
            for entry in conn.entries:
                members = entry.member.values if entry.member else []
                findings.append({'group': group_name, 'members': members})
                print(f"[+] {group_name}: {len(members)} member(s)")
    return findings
```

#### 密码保险库与自动轮换

**密码保险库**：集中存储特权账户密码，密码使用强加密保管，使用后自动轮换。

```
# 密码轮换策略
- 长期特权账户：每次使用后立即轮换
- 服务账户密码：每30-90天轮换
- 紧急访问账户（Break-Glass）：每次使用后轮换并通知
- API密钥：定期轮换 + 过期策略

# PAM 会话流程
1. 管理员请求访问 → 审批流程
2. 审批通过后 → PAM 检出密码并注入会话通道
3. 管理员通过 PAM 代理连接目标系统（密码不暴露给管理员）
4. 会话全程录制
5. 会话结束后 → PAM 自动轮换目标系统密码
```

#### 会话录制与审计

- **实时监控**：安全团队实时查看活跃会话
- **录制回放**：完整记录键盘输入和屏幕输出
- **关键字告警**：检测危险命令（rm -rf、format、shutdown）
- **行为基线**：建立正常行为模式，偏离时告警

#### 即时访问（JIT）

**JIT（Just-in-Time Access）**：按需授予临时权限，使用后自动回收。

```
传统模式（常驻权限）：
  管理员 → 拥有持续的管理员权限 → 风险高

JIT 模式（临时权限）：
  管理员 → 申请权限 → 审批 → 获得2小时临时权限 → 自动回收
```

#### 最小权限与审批流程

```
# 特权访问审批工作流
┌────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ 申请者 │───→ │ 直属经理 │───→ │ 安全团队  │───→ │ 自动审批  │
│ 提交   │     │ 审批     │     │ 审批      │     │ 策略引擎  │
│ 请求   │     │          │     │           │     │           │
└────────┘     └──────────┘     └──────────┘     └──────────┘
                                                      │
                                            ┌──────────▼───────────┐
                                            │  授予临时权限（TTL）  │
                                            │  启动会话录制         │
                                            │  通知 SOC             │
                                            └──────────────────────┘
```

### 2.3 PAM 产品对比

| 产品 | 优势 | 适用场景 |
|------|------|---------|
| **CyberArk** | 功能最全，企业级标杆，深度AD集成 | 大型企业，复杂合规需求 |
| **BeyondTrust** | 远程访问强，支持云和IoT | 跨混合环境，远程运维 |
| **Delinea**（原Thycotic） | 部署快，UI友好，性价比高 | 中型企业，快速落地 |
| **Teleport** | 开源友好，SSH/Web/DB统一，零信任原生 | DevOps/SRE团队，云原生 |
| **HashiCorp Vault** | 基础设施即代码，API密钥管理强 | 开发团队，动态密钥 |

### 2.4 PAM 实施路线图

```
阶段1（0-3月）：发现与盘点
  ├── 盘点所有特权账户（域管/云管/数据库/网络设备/应用）
  ├── 识别过度权限和僵尸账户
  └── 建立特权账户资产台账

阶段2（3-6月）：核心部署
  ├── 部署密码保险库
  ├── 接入核心系统（域控/数据库/关键服务器）
  ├── 实施密码自动轮换
  └── 启用会话录制

阶段3（6-12月）：深化与优化
  ├── 实施 JIT 临时权限
  ├── 建立审批工作流
  ├── 集成 SIEM/SOC
  └── 覆盖云环境和 API 密钥

阶段4（12月+）：持续运营
  ├── 定期权限审查
  ├── 行为分析与异常检测
  ├── 自动化策略调优
  └── 合规报告生成
```

### 2.5 云环境 PAM

**AWS IAM 特权访问**：

```bash
# AWS IAM 临时凭证（JIT 模式）
# 使用 STS AssumeRole 获取临时凭证
aws sts assume-role \
  --role-arn "arn:aws:iam::123456789012:role/PrivilegedRole" \
  --role-session-name "admin-session" \
  --duration-seconds 3600  # 最长1小时

# IAM Access Analyzer 检测过度权限
aws accessanalyzer create-analyzer \
  --analyzer-name production-analyzer \
  --type ACCOUNT

# Session Policies 实现权限降级
aws sts assume-role \
  --role-arn "arn:aws:iam::123456789012:role/Role" \
  --policy '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":"s3:Get*","Resource":"*"}]}'
```

**Azure PIM（Privileged Identity Management）**：

```bash
# 启用角色（JIT）
az role assignment create \
  --assignee user@example.com \
  --role "Virtual Machine Contributor" \
  --scope /subscriptions/{sub-id}/resourceGroups/{rg} \
  --condition "@RequestTimeWithin('P1H')"  # 1小时内有效

# 查看 PIM 活动日志
az rest --method get \
  --url "https://management.azure.com/providers/Microsoft.Authorization/roleManagementPolicies?api-version=2020-10-01"
```

---

---

## 📋 内容审核与补充建议

> 针对「特权访问管理（PAM）」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

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
